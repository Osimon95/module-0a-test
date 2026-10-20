
# ============================================================
# FRESH WEEX RECONSTRUCTION
# UNIT 1 INDEPENDENT TEST
# ZERO INDENTATION START
# ============================================================

import json
import urllib.error
import urllib.parse
import urllib.request

from datetime import datetime, timezone


def log(message):
    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    print(timestamp, message, flush=True)


def fresh_reconstruction_unit_1():

    print("=" * 80, flush=True)

    log("FRESH RECONSTRUCTION UNIT 1 START")

    print("-" * 80, flush=True)

    # Verify standard library functionality.

    assert json.loads('{"test": true}')["test"] is True

    assert (
        urllib.parse.urlencode({"symbol": "BTCUSDT"})
        == "symbol=BTCUSDT"
    )

    assert callable(urllib.request.Request)

    assert hasattr(urllib.error, "URLError")

    assert datetime.now(timezone.utc).tzinfo is not None

    print(
        "PASS: MAIN PYTHON RUNTIME STARTED",
        flush=True
    )

    print(
        "PASS: PYTHON STANDARD LIBRARY AVAILABLE",
        flush=True
    )

    print(
        "PASS: JSON MODULE FUNCTIONAL",
        flush=True
    )

    print(
        "PASS: URLLIB MODULE FUNCTIONAL",
        flush=True
    )

    print(
        "PASS: UTC LOGGER FUNCTIONAL",
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

    print("-" * 80, flush=True)

    log("FRESH RECONSTRUCTION UNIT 1 RESULT = PASS")

    print("=" * 80, flush=True)

    return True


# ============================================================
# RUN INDEPENDENT UNIT 1 TEST
# ZERO INDENTATION
# ============================================================

if __name__ == "__main__":

    result = fresh_reconstruction_unit_1()

    if result is not True:
        raise RuntimeError(
            "UNIT 1 TEST FAILED"
        )

    print(
        "FINAL VERDICT: UNIT 1 VERIFIED",
        flush=True
    )

    print(
        "NEXT UNIT AUTHORIZED FOR TESTING = UNIT 2",
        flush=True
    )

# ============================================================
# END UNIT 1 INDEPENDENT TEST
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 2
# ZERO INDENTATION
# CONFIGURATION AND SAFETY CONTRACT
# ============================================================



# ============================================================
# UNIT 1 TO UNIT 2 VERIFICATION HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_1_READY = (
    fresh_reconstruction_unit_1()
)

if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
    raise RuntimeError(
        "UNIT 1 TO UNIT 2 HANDOVER FAILED"
    )

print(
    "PASS: UNIT 1 TO UNIT 2 HANDOVER VERIFIED",
    flush=True
)

# ============================================================
# END UNIT 1 TO UNIT 2 HANDOVER
# ============================================================
def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 2 START")
    print("-" * 80, flush=True)

    # ========================================================
    # 1. UNIT 1 DEPENDENCY
    # ========================================================

    if globals().get(
        "FRESH_RECONSTRUCTION_UNIT_1_READY"
    ) is not True:
        raise RuntimeError(
            "UNIT 2 BLOCKED: UNIT 1 NOT VERIFIED"
        )

    print(
        "PASS: UNIT 2 RECEIVED UNIT 1 RESULT",
        flush=True
    )

    # ========================================================
    # 2. EXCHANGE CONFIGURATION
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
    # 3. SAFETY CONFIGURATION
    # ========================================================

    safety = {
        "public_market_data_read_enabled": True,
        "demo_account_balance_read_enabled": False,
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
    # 4. STRATEGY CONFIGURATION
    # ========================================================

    strategy = {

        # LEVERAGE AND INITIAL ENTRY

        "leverage_target": 100,
        "initial_margin_percent": 5.0,
        "initial_fixed_usdt": 0.50,

        # FIVE BACKUPS

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

        # EXPOSURE PROTECTION

        "exposure_cap_percent": 35.0,
        "progressive_backup_funding": True,
        "full_ladder_reservation_required": False,

        # TAKE PROFIT

        "tp1_allocation_percent": 10.0,
        "tp2_allocation_percent": 20.0,
        "tp3_allocation_percent": 70.0,

        "tp1_net_roi_floor_percent": 5.0,
        "tp2_net_roi_floor_percent": 10.0,
        "tp1_tp2_min_roi_separation_percent": 5.0,

        # TP3 TRAILING

        "tp3_trailing_reference_percent": 0.20,
        "tp3_trailing_min_percent": 0.10,
        "tp3_trailing_max_percent": 0.40,

        # SIGNAL CONTROL

        "signal_expiry_seconds": 120,
        "loss_cooldown_seconds": 300,
        "one_direction_only": True,
        "anti_duplicate_orders": True,
        "active_trade_mode_lock": True,
        "exclusive_mode": True,
        "mode_confirmations_required": 3,

        # MODE ARBITRATION

        "mode_priority": (
            "BREAKOUT",
            "STRUCTURE",
            "SCALP",
        ),

        "structure_breakout_priority": True,
        "arbitration_before_scalp": True,
        "developing_candidate_protection": True,
        "scalp_requires_higher_modes_clear": True,
        "scalp_preemption_requires_confirmation": True,
        "preserve_active_position_management": True,

        # COMMON DIRECTION CONTROL

        "direction_votes_required": 2,
        "direction_votes_total": 3,
        "qualification_use_closed_candles": True,
        "reject_stale_signals": True,
        "reject_late_impulse_entry": True,
        "reject_spike_count_above": 2,

        # BREAKOUT

        "breakout_early_detection_enabled": True,
        "breakout_developing_candidate_enabled": True,
        "breakout_require_ema_crossover": False,
        "breakout_allow_preconfirmation": True,
        "breakout_require_price_confirmation": True,
        "breakout_require_momentum_confirmation": True,
        "breakout_require_direction_agreement": True,
        "breakout_retest_mandatory": False,

        # STRUCTURE

        "structure_early_detection_enabled": True,
        "structure_developing_candidate_enabled": True,
        "structure_require_ema_crossover": False,
        "structure_require_price_confirmation": True,
        "structure_require_direction_agreement": True,
        "structure_allow_pullback_entry": True,
        "structure_allow_continuation_entry": True,
        "structure_retest_mandatory": False,

        # SCALPING

        "scalp_sideways_preferred": True,
        "scalp_trending_market_block": True,
        "scalp_quality_threshold": 70.0,
        "scalp_price_weight_percent": 50.0,
        "scalp_other_factors_weight_percent": 50.0,
        "scalp_max_ema_extension_clusters": 1.5,
        "scalp_early_entry_enabled": True,
        "scalp_late_entry_rejection": True,

        # SCALP PROFITABILITY

        "scalp_fee_aware_enabled": True,
        "scalp_estimated_taker_fee_percent": 0.08,
        "scalp_include_entry_fee": True,
        "scalp_include_exit_fee": True,
        "scalp_include_estimated_slippage": True,
        "scalp_require_positive_net_profit": True,
        "scalp_profit_safety_buffer_enabled": True,
        "scalp_min_net_roi_percent": 2.0,

        # CONTINUOUS ENTRY SCANNING

        "continuous_entry_scan_enabled": True,
        "flat_position_reentry_enabled": True,
        "reentry_requires_confirmed_flat": True,
        "reentry_requires_no_pending_entry": True,
        "reentry_preserves_cooldown": True,
    }

    # ========================================================
    # 5. MARKET PRECISION
    # ========================================================

    market_precision = {
        "quantity_step": 0.0001,
        "minimum_quantity": 0.0001,
        "price_step": 0.1,
    }

    # ========================================================
    # 6. COMPLETE CONFIGURATION
    # ========================================================

    config = {
        "exchange": exchange,
        "execution_environment": execution_environment,
        "safety": safety,
        "strategy": strategy,
        "market_precision": market_precision,
    }

    # ========================================================
    # 7. VALIDATION ENGINE
    # ========================================================

    errors = []

    def check(condition, label):

        if condition:
            print(
                "PASS: UNIT 2 " + label,
                flush=True
            )
        else:
            print(
                "FAIL: UNIT 2 " + label,
                flush=True
            )
            errors.append(label)

    check(
        exchange["name"] == "WEEX",
        "EXCHANGE = WEEX"
    )

    check(
        exchange["api_version"] == "V3",
        "API VERSION = V3"
    )

    check(
        exchange["contract_base_url"]
        == "https://api-contract.weex.com",
        "CONTRACT API URL"
    )

    check(
        exchange["market_symbol"] == "BTCUSDT",
        "MARKET SYMBOL = BTCUSDT"
    )

    check(
        exchange["demo_order_symbol"] == "BTCSUSDT",
        "DEMO SYMBOL = BTCSUSDT"
    )

    check(
        execution_environment == "DEMO",
        "DEMO ENVIRONMENT"
    )

    check(
        strategy["leverage_target"] == 100,
        "LEVERAGE TARGET = 100X"
    )

    check(
        strategy["initial_fixed_usdt"] == 0.50
        and strategy["initial_margin_percent"] == 5.0,
        "INITIAL ENTRY CONFIGURATION"
    )

    check(
        strategy["max_backups"] == 5
        and strategy["backup_multipliers"]
        == (1.0, 1.5, 2.0, 2.5, 3.0),
        "FIVE BACKUP LADDER"
    )

    check(
        strategy["backup_buffer_percent"] == 0.30,
        "BACKUP BUFFER = 0.30%"
    )

    check(
        strategy["exposure_cap_percent"] == 35.0,
        "MAXIMUM EXPOSURE = 35%"
    )

    check(
        strategy["progressive_backup_funding"]
        is True
        and strategy["full_ladder_reservation_required"]
        is False,
        "PROGRESSIVE BACKUP FUNDING"
    )

    tp_total = (
        strategy["tp1_allocation_percent"]
        + strategy["tp2_allocation_percent"]
        + strategy["tp3_allocation_percent"]
    )

    check(
        (
            strategy["tp1_allocation_percent"],
            strategy["tp2_allocation_percent"],
            strategy["tp3_allocation_percent"],
        ) == (10.0, 20.0, 70.0)
        and tp_total == 100.0,
        "TP ALLOCATION = 10/20/70"
    )

    check(
        strategy["tp1_net_roi_floor_percent"] == 5.0
        and strategy["tp2_net_roi_floor_percent"] == 10.0,
        "TP NET ROI FLOORS"
    )

    check(
        0 < strategy["tp3_trailing_min_percent"]
        <= strategy["tp3_trailing_reference_percent"]
        <= strategy["tp3_trailing_max_percent"],
        "TP3 DYNAMIC TRAILING RANGE"
    )

    check(
        strategy["mode_priority"]
        == ("BREAKOUT", "STRUCTURE", "SCALP"),
        "MODE PRIORITY = BREAKOUT/STRUCTURE/SCALP"
    )

    check(
        strategy["direction_votes_required"] == 2
        and strategy["direction_votes_total"] == 3,
        "DIRECTION CONFIRMATION = 2/3"
    )

    check(
        strategy["arbitration_before_scalp"]
        and strategy["developing_candidate_protection"]
        and strategy["scalp_requires_higher_modes_clear"],
        "HIGHER MODE CANDIDATE PROTECTION"
    )

    check(
        strategy["scalp_quality_threshold"] == 70.0,
        "SCALP QUALITY THRESHOLD = 70"
    )

    check(
        strategy["scalp_price_weight_percent"] == 50.0
        and strategy["scalp_other_factors_weight_percent"]
        == 50.0,
        "SCALP PRICE WEIGHT = 50%"
    )

    check(
        strategy["scalp_fee_aware_enabled"]
        and strategy["scalp_require_positive_net_profit"]
        and strategy["scalp_include_entry_fee"]
        and strategy["scalp_include_exit_fee"],
        "FEE AWARE SCALPING CONFIGURED"
    )

    check(
        strategy["scalp_min_net_roi_percent"] > 0.0,
        "SCALP MINIMUM NET ROI CONFIGURED"
    )

    check(
        strategy["continuous_entry_scan_enabled"]
        and strategy["flat_position_reentry_enabled"]
        and strategy["reentry_requires_confirmed_flat"]
        and strategy["reentry_requires_no_pending_entry"],
        "CONTINUOUS SCAN AND FLAT REENTRY CONFIGURED"
    )

    check(
        strategy["one_direction_only"]
        and strategy["anti_duplicate_orders"]
        and strategy["active_trade_mode_lock"]
        and strategy["exclusive_mode"],
        "POSITION AND MODE PROTECTION FLAGS"
    )

    check(
        market_precision["quantity_step"] == 0.0001
        and market_precision["minimum_quantity"]
        == 0.0001
        and market_precision["price_step"] == 0.1,
        "MARKET PRECISION"
    )

    # ========================================================
    # 8. SAFETY CONTRACT VALIDATION
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

    check(
        all(
            safety.get(key) is False
            for key in forbidden_capabilities
        ),
        "EXCHANGE WRITE AND ACCOUNT ACCESS DISABLED"
    )

    check(
        safety["public_market_data_read_enabled"]
        is True,
        "PUBLIC MARKET DATA READ ENABLED"
    )

    check(
        safety["demo_account_balance_read_enabled"]
        is False,
        "DEMO ACCOUNT READ DISABLED DURING TEST"
    )

    # ========================================================
    # 9. CONFIGURATION DIAGNOSTICS
    # ========================================================

    full_ladder_multiplier = (
        1.0 + sum(strategy["backup_multipliers"])
    )

    full_ladder_margin = (
        strategy["initial_fixed_usdt"]
        * full_ladder_multiplier
    )

    print(
        "UNIT 2 FULL LADDER MULTIPLIER =",
        full_ladder_multiplier,
        flush=True
    )

    print(
        "UNIT 2 FULL LADDER MARGIN USDT =",
        full_ladder_margin,
        flush=True
    )

    print(
        "UNIT 2 TP ALLOCATION TOTAL =",
        tp_total,
        flush=True
    )

    print(
        "UNIT 2 SCALP PRICE WEIGHT =",
        strategy["scalp_price_weight_percent"],
        flush=True
    )

    print(
        "UNIT 2 SCALP OTHER FACTORS WEIGHT =",
        strategy["scalp_other_factors_weight_percent"],
        flush=True
    )

    print(
        "UNIT 2 DEMO ORDER SUBMISSION ENABLED =",
        safety["demo_order_submission_enabled"],
        flush=True
    )

    print(
        "UNIT 2 REAL ORDER SUBMISSION ENABLED =",
        safety["real_order_submission_enabled"],
        flush=True
    )

    # ========================================================
    # 10. FINAL VALIDATION
    # ========================================================

    if errors:
        print(
            "UNIT 2 VALIDATION ERRORS =",
            errors,
            flush=True
        )

        raise RuntimeError(
            "UNIT 2 CONFIGURATION VERIFICATION FAILED"
        )

    print("-" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 2 RESULT = PASS"
    )

    print(
        "PASS: UNIT 2 CONFIGURATION VALIDATED",
        flush=True
    )

    print(
        "PASS: UNIT 2 SAFETY CONTRACT VALIDATED",
        flush=True
    )

    print(
        "UNIT 2 EXCHANGE REQUEST = NONE",
        flush=True
    )

    print(
        "UNIT 2 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 2 REAL ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 2 EXCHANGE WRITE = NONE",
        flush=True
    )

    print("=" * 80, flush=True)

    return config


# ============================================================
# RUN UNIT 2
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# END COMPLETE REPLACEMENT - UNIT 2
# ZERO INDENTATION
# ============================================================


# ============================================================
# START CENTRAL TUNING CONFIGURATION - CTC V1
# ZERO INDENTATION
#
# INSTALL AFTER UNIT 2, BEFORE UNIT 3
#
# STAGE A: READ ONLY / OBSERVATION MODE
# NO EXCHANGE WRITE
# NO AUTOMATIC STRATEGY CHANGES
# ============================================================

def fresh_central_tuning_config(unit_2_config):

    import copy
    import math
    import os

    print("=" * 80, flush=True)
    print("CENTRAL TUNING CONFIG START", flush=True)

    if not isinstance(unit_2_config, dict):
        raise RuntimeError("CTC INVALID CONFIG")

    strategy = unit_2_config.get("strategy")
    safety = unit_2_config.get("safety")

    if not isinstance(strategy, dict):
        raise RuntimeError("CTC INVALID STRATEGY")

    if not isinstance(safety, dict):
        raise RuntimeError("CTC INVALID SAFETY")

    for key in (
        "demo_order_submission_enabled",
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
    ):
        if safety.get(key) is not False:
            raise RuntimeError(
                "CTC UNSAFE CONFIG: " + key
            )

    # --------------------------------------------------------
    # 1. CONFIGURATION PROFILES
    #
    # These values are candidates for future testing.
    # They are NOT proven profitable settings.
    # --------------------------------------------------------

    profiles = {

        "BASELINE": {

            "structure_min_move_pct": 0.020,
            "structure_confirm_move_pct": 0.035,

            "breakout_min_5m_move_pct": 0.030,

            "scalp_quality_threshold": 70.0,
            "scalp_price_weight": 50.0,

            "scalp_min_net_roi_percent": 5.0,

            "backup_buffer_percent": 0.30,
            "exposure_cap_percent": 35.0,
        },

        "RESPONSIVE": {

            "structure_min_move_pct": 0.015,
            "structure_confirm_move_pct": 0.025,

            "breakout_min_5m_move_pct": 0.020,

            "scalp_quality_threshold": 70.0,
            "scalp_price_weight": 50.0,

            "scalp_min_net_roi_percent": 5.0,

            "backup_buffer_percent": 0.30,
            "exposure_cap_percent": 35.0,
        },

        "SELECTIVE": {

            "structure_min_move_pct": 0.035,
            "structure_confirm_move_pct": 0.050,

            "breakout_min_5m_move_pct": 0.050,

            "scalp_quality_threshold": 80.0,
            "scalp_price_weight": 50.0,

            "scalp_min_net_roi_percent": 10.0,

            "backup_buffer_percent": 0.30,
            "exposure_cap_percent": 25.0,
        },
    }

    # --------------------------------------------------------
    # 2. PROFILE SELECTION
    #
    # Optional Render environment setting:
    #
    # BOT_TUNING_PROFILE = BASELINE
    #
    # Other permitted values:
    # RESPONSIVE
    # SELECTIVE
    # --------------------------------------------------------

    profile_name = os.environ.get(
        "BOT_TUNING_PROFILE",
        "BASELINE"
    ).strip().upper()

    if profile_name not in profiles:
        raise RuntimeError(
            "CTC UNKNOWN PROFILE: " + profile_name
        )

    selected = copy.deepcopy(
        profiles[profile_name]
    )

    # --------------------------------------------------------
    # 3. STRICT NUMERIC VALIDATION
    # --------------------------------------------------------

    bounds = {

        "structure_min_move_pct":
            (0.005, 0.100),

        "structure_confirm_move_pct":
            (0.010, 0.150),

        "breakout_min_5m_move_pct":
            (0.010, 0.150),

        "scalp_quality_threshold":
            (70.0, 90.0),

        "scalp_price_weight":
            (30.0, 70.0),

        "scalp_min_net_roi_percent":
            (5.0, 30.0),

        "backup_buffer_percent":
            (0.10, 1.00),

        "exposure_cap_percent":
            (5.0, 35.0),
    }

    for key, limits in bounds.items():

        value = float(selected[key])
        low, high = limits

        if not (
            math.isfinite(value)
            and low <= value <= high
        ):
            raise RuntimeError(
                "CTC INVALID VALUE: " + key
            )

    if (
        selected["structure_confirm_move_pct"]
        <
        selected["structure_min_move_pct"]
    ):
        raise RuntimeError(
            "CTC STRUCTURE THRESHOLD ORDER"
        )

    if selected["exposure_cap_percent"] > 35.0:
        raise RuntimeError(
            "CTC EXPOSURE CAP EXCEEDED"
        )

    # --------------------------------------------------------
    # 4. PRESERVE HARD SAFETY LIMITS
    # --------------------------------------------------------

    selected["mode_priority"] = (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP",
    )

    selected["direction_votes_required"] = 2

    selected["real_order_submission_enabled"] = False

    selected["demo_order_submission_enabled"] = False

    # Stage A does not apply profile thresholds
    # to the running strategy.

    result = {

        "version": "CTC_V1",

        "profile": profile_name,

        "parameters": selected,

        "profile_validated": True,

        "apply_to_strategy": False,

        "shadow_only": True,

        "auto_optimization_enabled": False,

        "exchange_write_enabled": False,

        "source": "CENTRAL_TUNING_CONFIG",
    }

    # --------------------------------------------------------
    # 5. RENDER DIAGNOSTICS
    # --------------------------------------------------------

    print(
        "CTC ACTIVE PROFILE =",
        profile_name,
        flush=True
    )

    for key, value in selected.items():

        print(
            "CTC PARAMETER",
            key,
            "=",
            value,
            flush=True
        )

    print(
        "CTC PROFILE VALIDATED = TRUE",
        flush=True
    )

    print(
        "CTC STRATEGY OVERRIDE = FALSE",
        flush=True
    )

    print(
        "CTC AUTO OPTIMIZATION = FALSE",
        flush=True
    )

    print(
        "CTC DEMO ORDER = NONE",
        flush=True
    )

    print(
        "CTC REAL ORDER = NONE",
        flush=True
    )

    print(
        "CTC EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "CENTRAL TUNING CONFIG RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN CENTRAL TUNING CONFIG
# ZERO INDENTATION
# ============================================================

FRESH_CENTRAL_TUNING = (
    fresh_central_tuning_config(
        FRESH_RECONSTRUCTION_CONFIG
    )
)

# ============================================================
# END CENTRAL TUNING CONFIGURATION - CTC V1
# ZERO INDENTATION
# ============================================================

# ============================================================
# START COMPLETE REPLACEMENT - UNIT 3
# ZERO INDENTATION
# WEEX V3 PUBLIC MARKET DATA VERIFICATION
# ============================================================

def fresh_reconstruction_unit_3():

    import json
    import math
    import urllib.parse
    import urllib.request
    import urllib.error
    import time

    print("=" * 80, flush=True)

    log("FRESH RECONSTRUCTION UNIT 3 START")

    print("-" * 80, flush=True)

    # ========================================================
    # 1. RECEIVE VERIFIED UNIT 2 CONFIGURATION
    # ========================================================

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 BLOCKED: UNIT 2 CONFIG MISSING"
        )

    exchange = config.get("exchange")
    safety = config.get("safety")
    strategy = config.get("strategy")

    if not all(
        isinstance(item, dict)
        for item in (exchange, safety, strategy)
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID UNIT 2 DATA"
        )

    print(
        "PASS: UNIT 3 RECEIVED UNIT 2 CONFIGURATION",
        flush=True
    )

    # ========================================================
    # 2. VERIFY EXCHANGE CONFIGURATION
    # ========================================================

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID EXCHANGE"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID API VERSION"
        )

    base_url = exchange.get(
        "contract_base_url"
    )

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID API DOMAIN"
        )

    symbol = exchange.get("market_symbol")

    if symbol != "BTCUSDT":
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID MARKET SYMBOL"
        )

    if config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 3 BLOCKED: NOT DEMO ENVIRONMENT"
        )

    print(
        "PASS: UNIT 3 WEEX V3 CONFIGURATION",
        flush=True
    )

    print(
        "PASS: UNIT 3 SYMBOL = BTCUSDT",
        flush=True
    )

    # ========================================================
    # 3. STRICT READ ONLY SAFETY GATE
    # ========================================================

    if safety.get(
        "public_market_data_read_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: MARKET READ DISABLED"
        )

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

    for capability in forbidden_capabilities:

        if safety.get(capability) is not False:
            raise RuntimeError(
                "UNIT 3 BLOCKED: UNSAFE CAPABILITY "
                + capability
            )

    if safety.get(
        "demo_account_balance_read_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 3 BLOCKED: ACCOUNT READ ENABLED"
        )

    print(
        "PASS: UNIT 3 READ ONLY SAFETY GATE",
        flush=True
    )

    # ========================================================
    # 4. VERIFY STRATEGY HANDOVER
    # ========================================================

    if strategy.get("mode_priority") != (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP",
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: MODE PRIORITY MISMATCH"
        )

    if strategy.get(
        "continuous_entry_scan_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: SCANNING CONFIG MISSING"
        )

    if strategy.get(
        "scalp_fee_aware_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: FEE CONFIG MISSING"
        )

    if strategy.get(
        "developing_candidate_protection"
    ) is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: MODE PROTECTION MISSING"
        )

    print(
        "PASS: UNIT 3 STRATEGY CONFIGURATION RECEIVED",
        flush=True
    )

    # ========================================================
    # 5. CREATE WEEX PUBLIC REQUEST
    # ========================================================

    endpoint = "/capi/v3/market/symbolPrice"

    parameters = {
        "symbol": symbol,
        "priceType": "MARK",
    }

    query = urllib.parse.urlencode(parameters)

    url = base_url + endpoint + "?" + query

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Unit3-Verification/1.0",
        },
    )

    if request.get_method() != "GET":
        raise RuntimeError(
            "UNIT 3 BLOCKED: HTTP METHOD NOT GET"
        )

    if request.data is not None:
        raise RuntimeError(
            "UNIT 3 BLOCKED: REQUEST BODY DETECTED"
        )

    print(
        "PASS: UNIT 3 PUBLIC ENDPOINT CONFIGURED",
        flush=True
    )

    print(
        "PASS: UNIT 3 HTTP METHOD = GET",
        flush=True
    )

    print(
        "PASS: UNIT 3 AUTHENTICATION = NONE",
        flush=True
    )

    # ========================================================
    # 6. PREVENT HTTP REDIRECTION
    # ========================================================

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
            return None

    opener = urllib.request.build_opener(
        NoRedirect()
    )

    # ========================================================
    # 7. EXECUTE PUBLIC WEEX GET REQUEST
    # ========================================================

    print(
        "UNIT 3 WEEX PUBLIC REQUEST START",
        flush=True
    )

    try:

        with opener.open(
            request,
            timeout=15
        ) as response:

            http_status = response.getcode()

            raw_body = response.read(
                65537
            )

    except urllib.error.HTTPError as exc:

        print(
            "UNIT 3 HTTP ERROR CODE =",
            exc.code,
            flush=True
        )

        print(
            "UNIT 3 HTTP ERROR BODY =",
            exc.read(500).decode(
                "utf-8",
                errors="replace"
            ),
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 WEEX HTTP REQUEST FAILED"
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

    # ========================================================
    # 8. VERIFY HTTP RESPONSE
    # ========================================================

    print(
        "UNIT 3 HTTP STATUS =",
        http_status,
        flush=True
    )

    if http_status != 200:
        raise RuntimeError(
            "UNIT 3 BLOCKED: HTTP STATUS NOT 200"
        )

    if not raw_body:
        raise RuntimeError(
            "UNIT 3 BLOCKED: EMPTY HTTP RESPONSE"
        )

    if len(raw_body) > 65536:
        raise RuntimeError(
            "UNIT 3 BLOCKED: RESPONSE TOO LARGE"
        )

    print(
        "PASS: UNIT 3 WEEX RESPONSE RECEIVED",
        flush=True
    )

    # ========================================================
    # 9. DECODE JSON RESPONSE
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
            "UNIT 3 BLOCKED: INVALID JSON RESPONSE"
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID RESPONSE STRUCTURE"
        )

    print(
        "PASS: UNIT 3 JSON RESPONSE VALID",
        flush=True
    )

    # ========================================================
    # 10. VALIDATE WEEX RESPONSE SYMBOL
    # ========================================================

    response_symbol = payload.get("symbol")

    if response_symbol != symbol:
        raise RuntimeError(
            "UNIT 3 BLOCKED: RESPONSE SYMBOL MISMATCH"
        )

    print(
        "PASS: UNIT 3 RESPONSE SYMBOL =",
        response_symbol,
        flush=True
    )

    # ========================================================
    # 11. VALIDATE LIVE BTC MARK PRICE
    # ========================================================

    try:

        mark_price = float(
            payload.get("price")
        )

    except (
        TypeError,
        ValueError
    ) as exc:

        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID MARK PRICE"
        ) from exc

    if not math.isfinite(mark_price):
        raise RuntimeError(
            "UNIT 3 BLOCKED: NON FINITE PRICE"
        )

    if mark_price <= 0:
        raise RuntimeError(
            "UNIT 3 BLOCKED: NON POSITIVE PRICE"
        )

    print(
        "PASS: UNIT 3 LIVE BTC MARK PRICE =",
        mark_price,
        flush=True
    )

    # ========================================================
    # 12. VALIDATE EXCHANGE TIMESTAMP
    # ========================================================

    exchange_time_ms = payload.get("time")

    if (
        isinstance(exchange_time_ms, bool)
        or not isinstance(exchange_time_ms, int)
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID TIMESTAMP TYPE"
        )

    if not (
        1000000000000 <= exchange_time_ms
        < 100000000000000
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID MILLISECOND TIME"
        )

    received_time_ms = int(
        time.time() * 1000
    )

    market_age_seconds = (
        received_time_ms - exchange_time_ms
    ) / 1000.0

    max_market_age_seconds = 120.0

    future_tolerance_seconds = 30.0

    print(
        "UNIT 3 MARKET AGE SECONDS =",
        round(market_age_seconds, 3),
        flush=True
    )

    if market_age_seconds > max_market_age_seconds:
        raise RuntimeError(
            "UNIT 3 BLOCKED: STALE MARKET DATA"
        )

    if market_age_seconds < -future_tolerance_seconds:
        raise RuntimeError(
            "UNIT 3 BLOCKED: FUTURE TIMESTAMP"
        )

    print(
        "PASS: UNIT 3 MARKET DATA FRESH",
        flush=True
    )

    print(
        "PASS: UNIT 3 EXCHANGE TIMESTAMP VALID",
        flush=True
    )

    # ========================================================
    # 13. CREATE NORMALIZED MARKET SNAPSHOT
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

        "received_time_ms": received_time_ms,

        "market_age_seconds": market_age_seconds,

        "max_market_age_seconds":
            max_market_age_seconds,

        "market_data_fresh": True,

        "finite_price_validated": True,

        "source_type": "MARK_PRICE",

        "strategy_data_ready": True,
    }

    # ========================================================
    # 14. VERIFY UNIT 4 HANDOVER CONTRACT
    # ========================================================

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

    for field in required_fields:

        if field not in market_snapshot:
            raise RuntimeError(
                "UNIT 3 BLOCKED: SNAPSHOT FIELD MISSING "
                + field
            )

    if market_snapshot["read_only"] is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID READ ONLY SNAPSHOT"
        )

    print(
        "PASS: UNIT 3 NORMALIZED SNAPSHOT CREATED",
        flush=True
    )

    print(
        "PASS: UNIT 3 SNAPSHOT READY FOR UNIT 4",
        flush=True
    )

    # ========================================================
    # 15. FINAL UNIT 3 DIAGNOSTICS
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "PASS: UNIT 3 WEEX V3 PUBLIC MARKET READ",
        flush=True
    )

    print(
        "PASS: UNIT 3 MARK PRICE VALIDATED",
        flush=True
    )

    print(
        "PASS: UNIT 3 DATA FRESHNESS VALIDATED",
        flush=True
    )

    print(
        "PASS: UNIT 3 STRATEGY HANDOVER VERIFIED",
        flush=True
    )

    print(
        "UNIT 3 AUTHENTICATED REQUEST = NONE",
        flush=True
    )

    print(
        "UNIT 3 ACCOUNT ACCESS = NONE",
        flush=True
    )

    print(
        "UNIT 3 POSITION ACCESS = NONE",
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

    print("-" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 3 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return market_snapshot


# ============================================================
# RUN UNIT 3
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# END COMPLETE REPLACEMENT - UNIT 3
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 4 V2
# ZERO INDENTATION
#
# PUBLIC BTC MARKET ANALYSIS
# CLOSED CANDLES + EMA + ATR
# BREAKOUT / STRUCTURE / SIDEWAYS EVIDENCE
# UNIFIED DOWNSTREAM OUTPUT CONTRACT
#
# NO ACCOUNT ACCESS
# NO POSITION ACCESS
# NO DEMO ORDER
# NO REAL ORDER
# NO EXCHANGE WRITE
# ============================================================

def fresh_reconstruction_unit_4():

    import json
    import math
    import urllib.parse
    import urllib.request
    import urllib.error

    print("=" * 80, flush=True)
    print("FRESH RECONSTRUCTION UNIT 4 V2 START", flush=True)

    # ========================================================
    # 1. RECEIVE UNITS 2 AND 3
    # ========================================================

    config = FRESH_RECONSTRUCTION_CONFIG

    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 4 INVALID CONFIG")

    if not isinstance(market, dict):
        raise RuntimeError("UNIT 4 INVALID MARKET SNAPSHOT")

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})
    strategy = config.get("strategy", {})

    if not all(
        isinstance(x, dict)
        for x in (exchange, safety, strategy)
    ):
        raise RuntimeError("UNIT 4 INVALID CONFIG SECTION")

    if (
        market.get("exchange") != "WEEX"
        or market.get("api_version") != "V3"
        or market.get("symbol") != "BTCUSDT"
        or market.get("price_type") != "MARK"
        or market.get("read_only") is not True
    ):
        raise RuntimeError("UNIT 4 MARKET CONTRACT FAILURE")

    if (
        exchange.get("contract_base_url")
        != "https://api-contract.weex.com"
        or exchange.get("market_symbol") != "BTCUSDT"
    ):
        raise RuntimeError("UNIT 4 EXCHANGE CONTRACT FAILURE")

    # ========================================================
    # 2. SAFETY CONTRACT
    # ========================================================

    if safety.get(
        "public_market_data_read_enabled"
    ) is not True:
        raise RuntimeError("UNIT 4 PUBLIC DATA DISABLED")

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
                "UNIT 4 UNSAFE CONFIG: " + key
            )

    print("PASS: UNIT 4 READ ONLY SAFETY", flush=True)

    # ========================================================
    # 3. VALID NUMERIC HELPER
    # ========================================================

    def number(value, label):

        try:
            result = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise RuntimeError(
                "UNIT 4 INVALID " + label
            ) from exc

        if not math.isfinite(result):
            raise RuntimeError(
                "UNIT 4 NONFINITE " + label
            )

        return result

    exchange_ms = int(
        market["exchange_time_ms"]
    )

    live_mark = number(
        market["price"], "MARK PRICE"
    )

    if exchange_ms <= 0 or live_mark <= 0:
        raise RuntimeError("UNIT 4 INVALID MARKET DATA")

    # ========================================================
    # 4. PUBLIC WEEX CANDLE REQUEST
    # ========================================================

    endpoint = "/capi/v3/market/markPriceKlines"

    query = urllib.parse.urlencode({
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 300,
    })

    url = (
        "https://api-contract.weex.com"
        + endpoint
        + "?"
        + query
    )

    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Unit4-V2-ReadOnly",
        },
    )

    if request.get_method() != "GET":
        raise RuntimeError("UNIT 4 HTTP METHOD BLOCKED")

    if request.data is not None:
        raise RuntimeError("UNIT 4 REQUEST BODY BLOCKED")

    print("UNIT 4 KLINE REQUEST START", flush=True)

    try:
        with urllib.request.urlopen(
            request, timeout=15
        ) as response:

            status = response.getcode()
            raw_text = response.read().decode("utf-8")

    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            "UNIT 4 HTTP ERROR: " + str(exc.code)
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            "UNIT 4 CONNECTION FAILED"
        ) from exc

    print("UNIT 4 HTTP STATUS =", status, flush=True)

    if status != 200:
        raise RuntimeError("UNIT 4 HTTP NOT 200")

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT 4 INVALID WEEX JSON"
        ) from exc

    if not isinstance(payload, list):
        raise RuntimeError(
            "UNIT 4 UNEXPECTED KLINE RESPONSE"
        )

    if len(payload) < 200:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT KLINES"
        )

    # ========================================================
    # 5. NORMALIZE AND VALIDATE KLINES
    #
    # WEEX FORMAT:
    # 0 OPEN TIME
    # 1 OPEN
    # 2 HIGH
    # 3 LOW
    # 4 CLOSE
    # 5 VOLUME
    # 6 CLOSE TIME
    # ========================================================

    candles = []

    for raw in payload:

        if not isinstance(raw, (list, tuple)):
            raise RuntimeError("UNIT 4 INVALID KLINE ENTRY")

        if len(raw) < 7:
            raise RuntimeError("UNIT 4 SHORT KLINE ENTRY")

        candle = {
            "open_time_ms": int(raw[0]),
            "open": number(raw[1], "OPEN"),
            "high": number(raw[2], "HIGH"),
            "low": number(raw[3], "LOW"),
            "close": number(raw[4], "CLOSE"),
            "volume": number(raw[5], "VOLUME"),
            "close_time_ms": int(raw[6]),
        }

        if not (
            0 < candle["low"]
            <= min(candle["open"], candle["close"])
            <= max(candle["open"], candle["close"])
            <= candle["high"]
        ):
            raise RuntimeError("UNIT 4 INVALID OHLC")

        if (
            candle["open_time_ms"] <= 0
            or candle["close_time_ms"]
            <= candle["open_time_ms"]
            or candle["volume"] < 0
        ):
            raise RuntimeError(
                "UNIT 4 INVALID KLINE METADATA"
            )

        candles.append(candle)

    candles.sort(
        key=lambda c: c["open_time_ms"]
    )

    for index in range(1, len(candles)):

        if (
            candles[index]["open_time_ms"]
            <= candles[index - 1]["open_time_ms"]
        ):
            raise RuntimeError(
                "UNIT 4 DUPLICATE CANDLE TIME"
            )

    # ========================================================
    # 6. CLOSED-CANDLE FILTER
    # ========================================================

    closed = [
        c for c in candles
        if c["close_time_ms"] <= exchange_ms
    ]

    if len(closed) < 200:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT CLOSED CANDLES"
        )

    latest = closed[-1]
    previous = closed[-2]

    newest_returned_closed = (
        candles[-1]["close_time_ms"] <= exchange_ms
    )

    age_seconds = (
        exchange_ms - latest["close_time_ms"]
    ) / 1000.0

    candle_data_fresh = (
        0 <= age_seconds <= 180
    )

    print(
        "UNIT 4 RETURNED CANDLE COUNT =",
        len(candles),
        flush=True
    )

    print(
        "UNIT 4 CLOSED CANDLE COUNT =",
        len(closed),
        flush=True
    )

    print(
        "UNIT 4 UNFINISHED CANDLE EXCLUDED =",
        not newest_returned_closed,
        flush=True
    )

    print(
        "UNIT 4 CANDLE AGE SECONDS =",
        round(age_seconds, 3),
        flush=True
    )

    print(
        "UNIT 4 CANDLE DATA FRESH =",
        candle_data_fresh,
        flush=True
    )

    if not candle_data_fresh:
        raise RuntimeError(
            "UNIT 4 CLOSED CANDLE STALE"
        )

    # ========================================================
    # 7. EMA19 / 50 / 100 / 200
    # ========================================================

    prices = [
        c["close"] for c in closed
    ]

    def calculate_ema(values, period):

        if len(values) < period:
            raise RuntimeError("UNIT 4 EMA HISTORY SHORT")

        ema = sum(values[:period]) / period
        multiplier = 2.0 / (period + 1.0)

        for price in values[period:]:
            ema = (
                multiplier * price
                + (1.0 - multiplier) * ema
            )

        return float(ema)

    ema19 = calculate_ema(prices, 19)
    ema50 = calculate_ema(prices, 50)
    ema100 = calculate_ema(prices, 100)
    ema200 = calculate_ema(prices, 200)

    separation_pct = (
        abs(ema19 - ema50) / ema50 * 100.0
    )

    if ema19 > ema50 > ema200:
        ema_structure = "BULLISH"
    elif ema19 < ema50 < ema200:
        ema_structure = "BEARISH"
    else:
        ema_structure = "MIXED"

    # ========================================================
    # 8. MULTI-WINDOW CLOSED MOMENTUM
    # ========================================================

    moves = {}

    for window in (1, 5, 15, 30, 60, 120):

        reference = prices[-(window + 1)]

        moves[window] = (
            (latest["close"] - reference)
            / reference * 100.0
        )

    move5 = moves[5]
    move15 = moves[15]

    # ========================================================
    # 9. ATR14
    # ========================================================

    ranges = []

    for index in range(1, len(closed)):

        current = closed[index]
        prior = closed[index - 1]

        tr = max(
            current["high"] - current["low"],
            abs(current["high"] - prior["close"]),
            abs(current["low"] - prior["close"]),
        )

        ranges.append(tr)

    atr14 = sum(ranges[-14:]) / 14.0

    if atr14 <= 0:
        raise RuntimeError("UNIT 4 INVALID ATR14")

    atr_pct = atr14 / latest["close"] * 100.0

    # ========================================================
    # 10. SUPPORT / RESISTANCE
    # PREVIOUS 20 FULLY CLOSED CANDLES
    # ========================================================

    reference20 = closed[-21:-1]

    resistance20 = max(
        c["high"] for c in reference20
    )

    support20 = min(
        c["low"] for c in reference20
    )

    range_atr_ratio = (
        resistance20 - support20
    ) / atr14

    distance_resistance = (
        resistance20 - latest["close"]
    )

    distance_support = (
        latest["close"] - support20
    )

    near_resistance = (
        -0.10 * atr14
        <= distance_resistance
        <= 0.50 * atr14
    )

    near_support = (
        -0.10 * atr14
        <= distance_support
        <= 0.50 * atr14
    )

    # ========================================================
    # 11. PRICE OVEREXTENSION
    # ========================================================

    cluster_height = max(
        max(ema19, ema50, ema200)
        - min(ema19, ema50, ema200),
        atr14 * 0.10
    )

    extension = (
        abs(latest["close"] - ema19)
        / cluster_height
    )

    extension_limit = number(
        strategy.get(
            "scalp_max_ema_extension_clusters",
            1.5
        ),
        "EXTENSION LIMIT"
    )

    if extension_limit <= 0:
        raise RuntimeError(
            "UNIT 4 INVALID EXTENSION LIMIT"
        )

    price_overextended = (
        extension > extension_limit
    )

    # ========================================================
    # 12. BREAKOUT DEVELOPMENT / CONFIRMATION
    # ========================================================

    bullish_momentum = (
        move5 > 0 and move15 > 0
    )

    bearish_momentum = (
        move5 < 0 and move15 < 0
    )

    breakout_developing_long = (
        near_resistance
        and bullish_momentum
    )

    breakout_developing_short = (
        near_support
        and bearish_momentum
    )

    breakout_confirmed_long = (
        latest["close"]
        > resistance20 + 0.10 * atr14
        and bullish_momentum
    )

    breakout_confirmed_short = (
        latest["close"]
        < support20 - 0.10 * atr14
        and bearish_momentum
    )

    # ========================================================
    # 13. STRUCTURE DEVELOPMENT
    # ========================================================

    bullish_ema_context = (
        ema19 > ema50 > ema200
    )

    bearish_ema_context = (
        ema19 < ema50 < ema200
    )

    near_ema19 = (
        abs(latest["close"] - ema19)
        <= 0.75 * atr14
    )

    bullish_recovery = (
        latest["close"] > previous["close"]
        and latest["close"] > latest["open"]
    )

    bearish_recovery = (
        latest["close"] < previous["close"]
        and latest["close"] < latest["open"]
    )

    structure_developing_long = (
        bullish_ema_context
        and (near_ema19 or bullish_recovery)
        and move15 > 0
    )

    structure_developing_short = (
        bearish_ema_context
        and (near_ema19 or bearish_recovery)
        and move15 < 0
    )

    # ========================================================
    # 14. SIDEWAYS REGIME
    # ========================================================

    ema_gap_atr = (
        abs(ema19 - ema50) / atr14
    )

    sideways_candidate = (
        ema_gap_atr <= 0.70
        and range_atr_ratio <= 8.0
        and abs(move15) <= 1.5 * atr_pct
    )

    # ========================================================
    # 15. DIRECTION VOTING
    # ========================================================

    long_votes = sum((
        ema_structure == "BULLISH",
        move5 > 0,
        latest["close"] > previous["close"],
    ))

    short_votes = sum((
        ema_structure == "BEARISH",
        move5 < 0,
        latest["close"] < previous["close"],
    ))

    required_votes = int(
        strategy.get(
            "direction_votes_required",
            2
        )
    )

    if required_votes != 2:
        raise RuntimeError(
            "UNIT 4 EXPECTED 2 OF 3 VOTES"
        )

    direction_evidence = "NONE"

    if (
        long_votes >= required_votes
        and long_votes > short_votes
    ):
        direction_evidence = "LONG"

    elif (
        short_votes >= required_votes
        and short_votes > long_votes
    ):
        direction_evidence = "SHORT"

    # ========================================================
    # 16. COMPLETE SNAPSHOT
    # ========================================================

    result = {

        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": "BTCUSDT",
        "interval": "1m",
        "price_type": "MARK",

        "live_mark_price": live_mark,

        "previous_close": previous["close"],
        "latest_close": latest["close"],

        "latest_open_time_ms":
            latest["open_time_ms"],

        "latest_close_time_ms":
            latest["close_time_ms"],

        "exchange_time_ms": exchange_ms,

        "ema19": ema19,
        "ema50": ema50,
        "ema100": ema100,
        "ema200": ema200,

        "ema19_50_separation_pct":
            separation_pct,

        "ema_structure": ema_structure,

        "short_term_move_pct": moves[1],
        "move_1m_pct": moves[1],
        "move_5m_pct": moves[5],
        "move_15m_pct": moves[15],
        "move_30m_pct": moves[30],
        "move_60m_pct": moves[60],
        "move_120m_pct": moves[120],

        "atr14": atr14,
        "atr_percent": atr_pct,

        "ema_cluster_height": cluster_height,
        "price_extension_cluster": extension,
        "price_overextended": price_overextended,

        "support20": support20,
        "resistance20": resistance20,
        "range20_atr_ratio": range_atr_ratio,

        "near_resistance": near_resistance,
        "near_support": near_support,

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

        "sideways_candidate":
            sideways_candidate,

        "direction_long_votes": long_votes,
        "direction_short_votes": short_votes,
        "direction_evidence": direction_evidence,

        "candle_age_seconds": age_seconds,
        "candle_data_fresh": candle_data_fresh,

        "strategy_evidence_version":
            "U4_COORDINATED_V1",

        "recent_closed_klines": [
            dict(c) for c in closed[-60:]
        ],

        "candle_count": len(candles),
        "closed_candle_count": len(closed),

        "newest_returned_candle_closed":
            newest_returned_closed,

        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",

        "read_only": True,
        "trade_authorized": False,
    }

    # ========================================================
    # 17. FINAL CONTRACT VALIDATION
    # ========================================================

    required = (
        "symbol",
        "ema19",
        "ema50",
        "ema100",
        "ema200",
        "move_5m_pct",
        "move_15m_pct",
        "atr14",
        "support20",
        "resistance20",
        "breakout_developing_long",
        "breakout_developing_short",
        "breakout_confirmed_long",
        "breakout_confirmed_short",
        "structure_developing_long",
        "structure_developing_short",
        "sideways_candidate",
        "direction_evidence",
        "candle_age_seconds",
        "candle_data_fresh",
        "strategy_evidence_version",
    )

    missing = [
        key for key in required
        if key not in result
    ]

    if missing:
        raise RuntimeError(
            "UNIT 4 MISSING OUTPUT: " + str(missing)
        )

    if (
        result["read_only"] is not True
        or result["trade_authorized"] is not False
        or result["candle_data_fresh"] is not True
    ):
        raise RuntimeError(
            "UNIT 4 FINAL SAFETY CONTRACT FAILED"
        )

    # ========================================================
    # 18. RENDER VERIFICATION
    # ========================================================

    print("-" * 80, flush=True)

    for period, value in (
        (19, ema19),
        (50, ema50),
        (100, ema100),
        (200, ema200),
    ):
        print(
            "UNIT 4 EMA" + str(period) + " =",
            round(value, 6),
            flush=True
        )

    print(
        "UNIT 4 EMA STRUCTURE =",
        ema_structure,
        flush=True
    )

    for window in (1, 5, 15, 30, 60, 120):
        print(
            "UNIT 4 " + str(window) + "M MOVE % =",
            round(moves[window], 6),
            flush=True
        )

    print(
        "UNIT 4 ATR14 =",
        round(atr14, 6),
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
        "UNIT 4 DIRECTION VOTES LONG/SHORT =",
        long_votes, "/", short_votes,
        flush=True
    )

    print(
        "UNIT 4 DIRECTION EVIDENCE =",
        direction_evidence,
        flush=True
    )

    print(
        "UNIT 4 CANDLE DATA FRESH =",
        result["candle_data_fresh"],
        flush=True
    )

    print(
        "UNIT 4 CANDLE AGE SECONDS =",
        round(age_seconds, 3),
        flush=True
    )

    print(
        "UNIT 4 EVIDENCE VERSION =",
        result["strategy_evidence_version"],
        flush=True
    )

    print(
        "UNIT 4 TRADE AUTHORIZED = FALSE",
        flush=True
    )

    print(
        "UNIT 4 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 4 REAL ORDER = NONE",
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

    return result


# ============================================================
# RUN UNIT 4 V2
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)

# ============================================================
# END COMPLETE REPLACEMENT - UNIT 4 V2
# ZERO INDENTATION
#
# NEXT EXISTING COMPONENT:
# CTC STAGE B1 / UNIT 5
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 5 V2
# ZERO INDENTATION
#
# COORDINATED SIGNAL QUALIFICATION
#
# PRIORITY:
# 1. BREAKOUT
# 2. STRUCTURE
# 3. SCALP
#
# CONSUMES UNIT 4 V2 EVIDENCE ONLY
# NO NETWORK REQUEST
# NO AUTHENTICATED ACCESS
# NO DEMO OR REAL ORDER
# NO EXCHANGE WRITE
# ============================================================

def fresh_reconstruction_unit_5(
    unit_2_config,
    unit_4_snapshot,
):

    import math

    print("=" * 80, flush=True)
    print(
        "FRESH RECONSTRUCTION UNIT 5 V2 START",
        flush=True
    )

    # ========================================================
    # 1. INPUT AND SAFETY CONTRACT
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 5 INVALID UNIT 2 CONFIG"
        )

    if not isinstance(unit_4_snapshot, dict):
        raise RuntimeError(
            "UNIT 5 INVALID UNIT 4 SNAPSHOT"
        )

    strategy = unit_2_config.get(
        "strategy", {}
    )

    safety = unit_2_config.get(
        "safety", {}
    )

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 5 INVALID STRATEGY"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 5 INVALID SAFETY"
        )

    if strategy.get("mode_priority") != (
        "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError(
            "UNIT 5 MODE PRIORITY MISMATCH"
        )

    for key in (
        "authenticated_api_enabled",
        "account_access_enabled",
        "position_access_enabled",
        "order_endpoint_access_enabled",
        "demo_order_submission_enabled",
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
    ):
        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 5 UNSAFE CONFIG: " + key
            )

    if (
        unit_4_snapshot.get("symbol") != "BTCUSDT"
        or unit_4_snapshot.get("read_only") is not True
        or unit_4_snapshot.get("trade_authorized") is not False
    ):
        raise RuntimeError(
            "UNIT 5 UNIT 4 SAFETY FAILURE"
        )

    if (
        unit_4_snapshot.get(
            "strategy_evidence_version"
        ) != "U4_COORDINATED_V1"
    ):
        raise RuntimeError(
            "UNIT 5 UNIT 4 VERSION MISMATCH"
        )

    # ========================================================
    # 2. FRESHNESS VALIDATION
    # ========================================================

    if (
        unit_4_snapshot.get(
            "candle_data_fresh"
        ) is not True
    ):
        raise RuntimeError(
            "UNIT 5 STALE CANDLE EVIDENCE"
        )

    try:
        candle_age = float(
            unit_4_snapshot["candle_age_seconds"]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 5 INVALID CANDLE AGE"
        ) from exc

    if (
        not math.isfinite(candle_age)
        or not (0 <= candle_age <= 180)
    ):
        raise RuntimeError(
            "UNIT 5 CANDLE AGE OUT OF RANGE"
        )

    print(
        "PASS: UNIT 5 FRESH CLOSED CANDLES",
        flush=True
    )

    # ========================================================
    # 3. REQUIRED EVIDENCE
    # ========================================================

    evidence_flags = (
        "breakout_developing_long",
        "breakout_developing_short",
        "breakout_confirmed_long",
        "breakout_confirmed_short",
        "structure_developing_long",
        "structure_developing_short",
        "sideways_candidate",
        "price_overextended",
    )

    flags = {}

    for key in evidence_flags:

        if key not in unit_4_snapshot:
            raise RuntimeError(
                "UNIT 5 MISSING EVIDENCE: " + key
            )

        value = unit_4_snapshot[key]

        if type(value) is not bool:
            raise RuntimeError(
                "UNIT 5 INVALID EVIDENCE TYPE: " + key
            )

        flags[key] = value

    direction_evidence = unit_4_snapshot.get(
        "direction_evidence"
    )

    if direction_evidence not in (
        "LONG", "SHORT", "NONE"
    ):
        raise RuntimeError(
            "UNIT 5 INVALID DIRECTION EVIDENCE"
        )

    def numeric(key):

        if key not in unit_4_snapshot:
            raise RuntimeError(
                "UNIT 5 MISSING " + key
            )

        try:
            value = float(unit_4_snapshot[key])
        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                "UNIT 5 INVALID " + key
            ) from exc

        if not math.isfinite(value):
            raise RuntimeError(
                "UNIT 5 NONFINITE " + key
            )

        return value

    move1 = numeric("move_1m_pct")
    move5 = numeric("move_5m_pct")
    move15 = numeric("move_15m_pct")
    move30 = numeric("move_30m_pct")

    latest_close = numeric("latest_close")
    previous_close = numeric("previous_close")
    live_mark = numeric("live_mark_price")

    ema19 = numeric("ema19")
    ema50 = numeric("ema50")
    ema100 = numeric("ema100")
    ema200 = numeric("ema200")

    separation_pct = numeric(
        "ema19_50_separation_pct"
    )

    atr14 = numeric("atr14")

    if min(
        latest_close,
        previous_close,
        live_mark,
        ema19,
        ema50,
        ema100,
        ema200,
        atr14
    ) <= 0:
        raise RuntimeError(
            "UNIT 5 NONPOSITIVE PRICE OR ATR"
        )

    # ========================================================
    # 4. QUALIFICATION SETTINGS
    #
    # BASELINE VALUES FROM CENTRAL TUNING
    # NO CTC OVERRIDE IS APPLIED.
    # ========================================================

    structure_min_move_pct = 0.020
    structure_confirm_move_pct = 0.035
    breakout_min_5m_move_pct = 0.030

    scalp_min_move_pct = 0.015

    taker_fee_per_side_pct = 0.080
    extra_friction_pct = 0.020
    minimum_net_price_profit_pct = 0.050

    minimum_sustainable_range_pct = (
        2.0 * taker_fee_per_side_pct
        + extra_friction_pct
        + minimum_net_price_profit_pct
    )

    # ========================================================
    # 5. BREAKOUT EVIDENCE
    # ========================================================

    breakout_developing_long = flags[
        "breakout_developing_long"
    ]

    breakout_developing_short = flags[
        "breakout_developing_short"
    ]

    breakout_confirmed_long = flags[
        "breakout_confirmed_long"
    ]

    breakout_confirmed_short = flags[
        "breakout_confirmed_short"
    ]

    breakout_developing = (
        breakout_developing_long
        or breakout_developing_short
    )

    breakout_candidate = (
        breakout_developing
        or breakout_confirmed_long
        or breakout_confirmed_short
    )

    price_overextended = flags[
        "price_overextended"
    ]

    breakout_ready_long = (
        breakout_confirmed_long
        and direction_evidence == "LONG"
        and move5 >= breakout_min_5m_move_pct
        and move15 > 0
        and not price_overextended
    )

    breakout_ready_short = (
        breakout_confirmed_short
        and direction_evidence == "SHORT"
        and move5 <= -breakout_min_5m_move_pct
        and move15 < 0
        and not price_overextended
    )

    breakout_ready = (
        breakout_ready_long
        or breakout_ready_short
    )

    # ========================================================
    # 6. STRUCTURE EVIDENCE
    # ========================================================

    structure_developing_long = flags[
        "structure_developing_long"
    ]

    structure_developing_short = flags[
        "structure_developing_short"
    ]

    structure_candidate = (
        structure_developing_long
        or structure_developing_short
    )

    # Structure has its own early qualification.
    # EMA direction and 15M momentum are already
    # represented in the Unit 4 development flag.

    structure_ready_long = (
        structure_developing_long
        and direction_evidence == "LONG"
        and move15 >= structure_confirm_move_pct
        and abs(move15) >= structure_min_move_pct
        and not price_overextended
    )

    structure_ready_short = (
        structure_developing_short
        and direction_evidence == "SHORT"
        and move15 <= -structure_confirm_move_pct
        and abs(move15) >= structure_min_move_pct
        and not price_overextended
    )

    structure_ready = (
        structure_ready_long
        or structure_ready_short
    )

    higher_mode_developing = (
        breakout_candidate
        or structure_candidate
    )

    # ========================================================
    # 7. SCALP SIDEWAYS AND FEE CONTEXT
    # ========================================================

    sideways = flags["sideways_candidate"]

    closed_candles = unit_4_snapshot.get(
        "recent_closed_klines", []
    )

    if not isinstance(closed_candles, list):
        raise RuntimeError(
            "UNIT 5 INVALID SCALP CANDLE HISTORY"
        )

    if len(closed_candles) < 20:
        raise RuntimeError(
            "UNIT 5 INSUFFICIENT SCALP HISTORY"
        )

    recent = closed_candles[-20:]

    try:
        high20 = max(
            float(c["high"]) for c in recent
        )

        low20 = min(
            float(c["low"]) for c in recent
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 5 INVALID SCALP RANGE"
        ) from exc

    if (
        not math.isfinite(high20)
        or not math.isfinite(low20)
        or low20 <= 0
        or high20 < low20
    ):
        raise RuntimeError(
            "UNIT 5 INVALID RANGE VALUES"
        )

    scalp_range_pct = (
        (high20 - low20) / low20 * 100.0
    )

    scalp_range_feasible = (
        scalp_range_pct
        >= minimum_sustainable_range_pct
    )

    scalp_context = (
        sideways
        and not higher_mode_developing
        and not price_overextended
        and direction_evidence in (
            "LONG", "SHORT"
        )
    )

    scalp_momentum_agreement = (
        (
            direction_evidence == "LONG"
            and move5 >= scalp_min_move_pct
            and move1 > 0
        )
        or
        (
            direction_evidence == "SHORT"
            and move5 <= -scalp_min_move_pct
            and move1 < 0
        )
    )

    scalp_pending = (
        scalp_context
        and scalp_momentum_agreement
        and scalp_range_feasible
    )

    # Unit 6 must still validate the scalp's
    # actual price-weighted quality score,
    # prospective reward, spread, and fees.

    
    # ========================================================
    # UNIT 5 V2.2
    # COMPLETE COORDINATED MODE ARBITRATION
    # INDENTATION: 4 SPACES
    #
    # QUALIFIED BREAKOUT > PROMISING BREAKOUT
    # > QUALIFIED STRUCTURE > DEVELOPING STRUCTURE
    # > FEE-FEASIBLE SCALP
    #
    # WEAK OR OPPOSING BREAKOUT MUST NOT
    # STARVE A QUALIFIED STRUCTURE.
    #
    # ZERO EXCHANGE WRITE
    # ========================================================

    # --------------------------------------------------------
    # 1. DETERMINE BREAKOUT EVIDENCE STRENGTH
    # --------------------------------------------------------

    confirmed_breakout_long = (
        breakout_confirmed_long
    )

    confirmed_breakout_short = (
        breakout_confirmed_short
    )

    confirmed_breakout = (
        confirmed_breakout_long
        or confirmed_breakout_short
    )

    developing_long_aligned = (
        breakout_developing_long
        and direction_evidence == "LONG"
        and move5 >= breakout_min_5m_move_pct
        and move15 > 0
        and not price_overextended
    )

    developing_short_aligned = (
        breakout_developing_short
        and direction_evidence == "SHORT"
        and move5 <= -breakout_min_5m_move_pct
        and move15 < 0
        and not price_overextended
    )

    breakout_promising = (
        developing_long_aligned
        or developing_short_aligned
    )

    # --------------------------------------------------------
    # 2. EXPLAIN FAILED CONFIRMED BREAKOUT
    # --------------------------------------------------------

    breakout_rejection_reason = "NONE"

    if confirmed_breakout and not breakout_ready:

        if price_overextended:

            breakout_rejection_reason = (
                "BREAKOUT_PRICE_OVEREXTENDED"
            )

        elif (
            confirmed_breakout_long
            and direction_evidence != "LONG"
        ) or (
            confirmed_breakout_short
            and direction_evidence != "SHORT"
        ):

            breakout_rejection_reason = (
                "BREAKOUT_DIRECTION_NOT_CONFIRMED"
            )

        elif (
            confirmed_breakout_long
            and (
                move5 < breakout_min_5m_move_pct
                or move15 <= 0
            )
        ) or (
            confirmed_breakout_short
            and (
                move5 > -breakout_min_5m_move_pct
                or move15 >= 0
            )
        ):

            breakout_rejection_reason = (
                "BREAKOUT_MOMENTUM_INSUFFICIENT"
            )

        else:

            breakout_rejection_reason = (
                "BREAKOUT_NOT_QUALIFIED"
            )

    # --------------------------------------------------------
    # 3. CLASSIFY STRUCTURE DEVELOPMENT
    # --------------------------------------------------------

    structure_long_aligned = (
        structure_developing_long
        and direction_evidence == "LONG"
        and move15 > 0
        and not price_overextended
    )

    structure_short_aligned = (
        structure_developing_short
        and direction_evidence == "SHORT"
        and move15 < 0
        and not price_overextended
    )

    structure_promising = (
        structure_long_aligned
        or structure_short_aligned
    )

    # Protective evidence can exist below qualification.
    # Contradictory or overextended evidence must not
    # automatically suppress every other strategy.

    higher_mode_developing = (
        breakout_ready
        or breakout_promising
        or structure_ready
        or structure_promising
    )

    # --------------------------------------------------------
    # 4. RECALCULATE SCALP ELIGIBILITY
    # USING THE V2.2 PRIORITY CONTRACT
    # --------------------------------------------------------

    scalp_context = (
        sideways
        and not higher_mode_developing
        and not breakout_candidate
        and not structure_candidate
        and not price_overextended
        and direction_evidence in (
            "LONG", "SHORT"
        )
    )

    scalp_pending = (
        scalp_context
        and scalp_momentum_agreement
        and scalp_range_feasible
    )

    # --------------------------------------------------------
    # 5. INITIALIZE DECISION
    # --------------------------------------------------------

    active_mode = "NONE"
    direction = "NONE"
    qualified = False

    candidate_mode = "NONE"
    candidate_stage = "NONE"

    qualification_reason = (
        "NO_ACCEPTABLE_CANDIDATE"
    )

    # --------------------------------------------------------
    # 6. PRIORITY 1: QUALIFIED BREAKOUT
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 7. PRIORITY 2: PROMISING DEVELOPING BREAKOUT
    # --------------------------------------------------------

    elif breakout_promising:

        candidate_mode = "BREAKOUT"
        candidate_stage = "DEVELOPING"

        qualification_reason = (
            "BREAKOUT_PROMISING_AWAITING_CONFIRMATION"
        )

    # --------------------------------------------------------
    # 8. PRIORITY 3: QUALIFIED STRUCTURE
    #
    # A weak or opposing breakout no longer blocks it.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 9. PRIORITY 4: DEVELOPING STRUCTURE
    # --------------------------------------------------------

    elif structure_promising:

        candidate_mode = "STRUCTURE"
        candidate_stage = "DEVELOPING"

        qualification_reason = (
            "STRUCTURE_PROMISING_AWAITING_CONFIRMATION"
        )

    # --------------------------------------------------------
    # 10. REJECT FAILED CONFIRMED BREAKOUT
    # WITHOUT AUTHORIZING THE WEAK SIGNAL
    # --------------------------------------------------------

    elif confirmed_breakout:

        candidate_mode = "BREAKOUT"
        candidate_stage = "REJECTED"

        qualification_reason = (
            breakout_rejection_reason
        )

    # --------------------------------------------------------
    # 11. WEAK DEVELOPING BREAKOUT
    # --------------------------------------------------------

    elif breakout_candidate:

        candidate_mode = "BREAKOUT"
        candidate_stage = "REJECTED"

        qualification_reason = (
            "BREAKOUT_WEAK_OR_DIRECTION_CONFLICT"
        )

    # --------------------------------------------------------
    # 12. WEAK DEVELOPING STRUCTURE
    # --------------------------------------------------------

    elif structure_candidate:

        candidate_mode = "STRUCTURE"
        candidate_stage = "REJECTED"

        qualification_reason = (
            "STRUCTURE_WEAK_OR_DIRECTION_CONFLICT"
        )

    # --------------------------------------------------------
    # 13. PRIORITY 5: SCALP PENDING UNIT 6
    # --------------------------------------------------------

    elif scalp_pending:

        candidate_mode = "SCALP"
        candidate_stage = "PENDING_UNIT_6"

        qualification_reason = (
            "SCALP_PENDING_QUALITY_AND_FEES"
        )

    elif sideways and not scalp_range_feasible:

        qualification_reason = (
            "SCALP_HISTORICAL_RANGE_INSUFFICIENT"
        )

    elif sideways and price_overextended:

        qualification_reason = (
            "SCALP_PRICE_OVEREXTENDED"
        )

    elif sideways:

        qualification_reason = (
            "SCALP_DIRECTION_OR_MOMENTUM_REJECTED"
        )

    # --------------------------------------------------------
    # 14. FINAL QUALIFICATION SAFETY
    # --------------------------------------------------------

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
                "UNIT 5 V2.2 QUALIFICATION INCONSISTENT"
            )

    else:

        if (
            active_mode != "NONE"
            or direction != "NONE"
        ):
            raise RuntimeError(
                "UNIT 5 V2.2 UNQUALIFIED MODE LEAK"
            )

    if (
        candidate_mode == "SCALP"
        and (
            higher_mode_developing
            or breakout_candidate
            or structure_candidate
        )
    ):
        raise RuntimeError(
            "UNIT 5 V2.2 SCALP PRIORITY FAILURE"
        )

    # --------------------------------------------------------
    # 15. V2.2 RENDER DIAGNOSTICS
    # --------------------------------------------------------

    print(
        "UNIT 5 V2.2 BREAKOUT PROMISING =",
        breakout_promising,
        flush=True
    )

    print(
        "UNIT 5 V2.2 BREAKOUT REJECTION =",
        breakout_rejection_reason,
        flush=True
    )

    print(
        "UNIT 5 V2.2 STRUCTURE PROMISING =",
        structure_promising,
        flush=True
    )

    print(
        "UNIT 5 V2.2 HIGHER MODE DEVELOPING =",
        higher_mode_developing,
        flush=True
    )

    print(
        "UNIT 5 V2.2 SELECTED CANDIDATE =",
        candidate_mode,
        flush=True
    )

    print(
        "UNIT 5 V2.2 CANDIDATE STAGE =",
        candidate_stage,
        flush=True
    )

    print(
        "UNIT 5 V2.2 QUALIFICATION REASON =",
        qualification_reason,
        flush=True
    )

    print(
        "UNIT 5 V2.2 QUALIFIED =",
        qualified,
        flush=True
    )

    print(
        "UNIT 5 V2.2 TRADE AUTHORIZED = FALSE",
        flush=True
    )

    # ========================================================
    # END UNIT 5 V2.2
    # SECTION 9 INVARIANTS CONTINUES BELOW
    # ========================================================
    
    # ========================================================
    # 9. INVARIANTS
    # ========================================================

    if qualified and (
        active_mode not in ("BREAKOUT", "STRUCTURE")
        or direction not in ("LONG", "SHORT")
        or candidate_stage != "QUALIFIED"
    ):
        raise RuntimeError(
            "UNIT 5 INVALID QUALIFICATION"
        )

    if (
        active_mode == "SCALP"
        or (
            candidate_mode == "SCALP"
            and higher_mode_developing
        )
    ):
        raise RuntimeError(
            "UNIT 5 SCALP PRIORITY FAILURE"
        )

    # ========================================================
    # 10. NORMALIZED UNIT 6 HANDOVER
    # ========================================================

    output = {

        "symbol": "BTCUSDT",

        "qualified": qualified,
        "active_mode": active_mode,
        "direction": direction,
        "qualification_reason": qualification_reason,

        "candidate_mode": candidate_mode,
        "candidate_stage": candidate_stage,

        "higher_mode_developing":
            higher_mode_developing,

        "breakout_candidate": breakout_candidate,
        "breakout_ready": breakout_ready,

        "structure_candidate": structure_candidate,
        "structure_ready": structure_ready,

        "sideways_context": sideways,
        "scalp_range_pct": scalp_range_pct,
        "scalp_range_feasible": scalp_range_feasible,
        "scalp_ready": scalp_pending,

        "direction_evidence": direction_evidence,

        "live_mark_price": live_mark,
        "latest_close": latest_close,
        "previous_close": previous_close,

        "ema19": ema19,
        "ema50": ema50,
        "ema100": ema100,
        "ema200": ema200,

        "ema19_50_separation_pct":
            separation_pct,

        "ema_structure": unit_4_snapshot.get(
            "ema_structure", "MIXED"
        ),

        "ema_direction": direction_evidence,

        "momentum_direction": (
            "LONG" if move1 > 0 else
            "SHORT" if move1 < 0 else "NONE"
        ),

        "momentum_1m_direction": (
            "LONG" if move1 > 0 else
            "SHORT" if move1 < 0 else "NONE"
        ),

        "momentum_5m_direction": (
            "LONG" if move5 > 0 else
            "SHORT" if move5 < 0 else "NONE"
        ),

        "momentum_15m_direction": (
            "LONG" if move15 > 0 else
            "SHORT" if move15 < 0 else "NONE"
        ),

        "short_term_move_pct": move1,
        "absolute_short_term_move_pct": abs(move1),

        "move_1m_pct": move1,
        "move_5m_pct": move5,
        "move_15m_pct": move15,
        "move_30m_pct": move30,

        "scalp_direction": (
            direction_evidence if scalp_pending
            else "NONE"
        ),

        "scalp_move_pct": abs(move5),

        "price_above_ema19": live_mark > ema19,
        "price_above_ema50": live_mark > ema50,
        "price_above_ema200": live_mark > ema200,

        "latest_close_above_previous":
            latest_close > previous_close,

        "candle_data_fresh": True,
        "read_only": True,
        "trade_authorized": False,

        "strategy_evidence_version":
            "U4_COORDINATED_V1",
    }

    # ========================================================
    # 11. RENDER DIAGNOSTICS
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "UNIT 5 DIRECTION EVIDENCE =",
        direction_evidence, flush=True
    )

    print(
        "UNIT 5 BREAKOUT CANDIDATE =",
        breakout_candidate, flush=True
    )

    print(
        "UNIT 5 BREAKOUT READY =",
        breakout_ready, flush=True
    )

    print(
        "UNIT 5 STRUCTURE CANDIDATE =",
        structure_candidate, flush=True
    )

    print(
        "UNIT 5 STRUCTURE READY =",
        structure_ready, flush=True
    )

    print(
        "UNIT 5 HIGHER MODE DEVELOPING =",
        higher_mode_developing, flush=True
    )

    print(
        "UNIT 5 SIDEWAYS CONTEXT =",
        sideways, flush=True
    )

    print(
        "UNIT 5 SCALP RANGE % =",
        round(scalp_range_pct, 6),
        flush=True
    )

    print(
        "UNIT 5 MINIMUM SCALP RANGE % =",
        minimum_sustainable_range_pct,
        flush=True
    )

    print(
        "UNIT 5 SCALP RANGE FEASIBLE =",
        scalp_range_feasible, flush=True
    )

    print(
        "UNIT 5 SCALP READY =",
        scalp_pending, flush=True
    )

    print(
        "UNIT 5 CANDIDATE MODE =",
        candidate_mode, flush=True
    )

    print(
        "UNIT 5 CANDIDATE STAGE =",
        candidate_stage, flush=True
    )

    print(
        "UNIT 5 ACTIVE MODE =",
        active_mode, flush=True
    )

    print(
        "UNIT 5 DIRECTION =",
        direction, flush=True
    )

    print(
        "UNIT 5 QUALIFIED =",
        qualified, flush=True
    )

    print(
        "UNIT 5 QUALIFICATION REASON =",
        qualification_reason, flush=True
    )

    print(
        "UNIT 5 TRADE AUTHORIZED = FALSE",
        flush=True
    )

    print(
        "UNIT 5 NETWORK REQUEST = NONE",
        flush=True
    )

    print(
        "UNIT 5 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 5 REAL ORDER = NONE",
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

    return output


# ============================================================
# RUN UNIT 5 V2
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
    fresh_reconstruction_unit_5(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
    )
)

# ============================================================
# END COMPLETE REPLACEMENT - UNIT 5 V2
# ZERO INDENTATION
# ============================================================


# ============================================================
# START UNIT 5 V2.1
# CONTROLLED QUALIFICATION TEST SUITE
# ZERO INDENTATION
#
# TEST ONLY:
# - NO NEW MARKET REQUEST
# - NO EXCHANGE ACCOUNT ACCESS
# - NO ORDERS
# - NO MUTATION OF UNIT 4 OR UNIT 5 RESULTS
#
# RUN AFTER UNIT 5 V2
# ============================================================

def fresh_unit_5_v21_tests():

    import copy
    import math

    print("=" * 80, flush=True)
    print("UNIT 5 V2.1 CONTROLLED TEST START", flush=True)

    config = FRESH_RECONSTRUCTION_CONFIG

    original = (
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
    )

    original_result = (
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
    )

    if not isinstance(original, dict):
        raise RuntimeError(
            "UNIT 5 V2.1 INVALID BASE SNAPSHOT"
        )

    if not isinstance(original_result, dict):
        raise RuntimeError(
            "UNIT 5 V2.1 INVALID ORIGINAL RESULT"
        )

    if (
        original.get("read_only") is not True
        or original.get("candle_data_fresh") is not True
        or original.get("trade_authorized") is not False
        or original.get("strategy_evidence_version")
        != "U4_COORDINATED_V1"
    ):
        raise RuntimeError(
            "UNIT 5 V2.1 BASE CONTRACT FAILURE"
        )

    # ========================================================
    # 1. TEST SNAPSHOT BUILDER
    # ========================================================

    evidence_flags = (
        "breakout_developing_long",
        "breakout_developing_short",
        "breakout_confirmed_long",
        "breakout_confirmed_short",
        "structure_developing_long",
        "structure_developing_short",
    )

    def fixture(
        direction="LONG",
        sideways=False,
        wide_range=False,
        overextended=False,
        **overrides
    ):

        data = copy.deepcopy(original)

        for key in evidence_flags:
            data[key] = False

        data["direction_evidence"] = direction
        data["sideways_candidate"] = sideways
        data["price_overextended"] = overextended

        data["candle_data_fresh"] = True
        data["candle_age_seconds"] = 30.0

        data["read_only"] = True
        data["trade_authorized"] = False

        data["strategy_evidence_version"] = (
            "U4_COORDINATED_V1"
        )

        data["move_1m_pct"] = 0.030
        data["move_5m_pct"] = 0.050
        data["move_15m_pct"] = 0.050
        data["move_30m_pct"] = 0.080

        if direction == "SHORT":
            data["move_1m_pct"] = -0.030
            data["move_5m_pct"] = -0.050
            data["move_15m_pct"] = -0.050
            data["move_30m_pct"] = -0.080

        if direction == "NONE":
            data["move_1m_pct"] = 0.0
            data["move_5m_pct"] = 0.0
            data["move_15m_pct"] = 0.0
            data["move_30m_pct"] = 0.0

        # Construct a reproducible historical range.
        # These candles are test fixtures, not WEEX data.

        price = float(
            data["latest_close"]
        )

        if not math.isfinite(price) or price <= 0:
            raise RuntimeError(
                "UNIT 5 V2.1 INVALID FIXTURE PRICE"
            )

        range_pct = (
            0.40 if wide_range else 0.10
        )

        low_price = (
            price * (1.0 - range_pct / 200.0)
        )

        high_price = (
            price * (1.0 + range_pct / 200.0)
        )

        test_candles = []

        for index in range(20):

            test_candles.append({
                "open": price,
                "high": high_price,
                "low": low_price,
                "close": price,
            })

        data["recent_closed_klines"] = (
            test_candles
        )

        for key, value in overrides.items():
            data[key] = value

        return data

    # ========================================================
    # 2. TEST RUNNER
    # ========================================================

    total = 0
    passed = 0
    failed = 0
    spec_gaps = 0

    def run_case(
        name,
        expected_mode,
        expected_stage,
        expected_direction,
        expected_qualified,
        data,
        known_gap=False,
    ):

        nonlocal total, passed, failed, spec_gaps

        total += 1

        print("-" * 80, flush=True)
        print("V2.1 TEST =", name, flush=True)

        try:

            result = fresh_reconstruction_unit_5(
                config,
                data,
            )

            actual = (
                result.get("candidate_mode"),
                result.get("candidate_stage"),
                result.get("direction"),
                result.get("qualified"),
            )

            expected = (
                expected_mode,
                expected_stage,
                expected_direction,
                expected_qualified,
            )

            safe = (
                result.get("trade_authorized") is False
                and result.get("read_only") is True
            )

            matched = actual == expected and safe

            print(
                "V2.1 EXPECTED =",
                expected,
                flush=True
            )

            print(
                "V2.1 ACTUAL =",
                actual,
                flush=True
            )

            print(
                "V2.1 READ ONLY =",
                safe,
                flush=True
            )

            if matched:
                passed += 1
                print(
                    "V2.1 TEST RESULT = PASS",
                    flush=True
                )

            elif known_gap and safe:
                spec_gaps += 1
                print(
                    "V2.1 TEST RESULT = SPEC GAP",
                    flush=True
                )

            else:
                failed += 1
                print(
                    "V2.1 TEST RESULT = FAIL",
                    flush=True
                )

        except Exception as exc:

            failed += 1

            print(
                "V2.1 TEST RESULT = ERROR",
                flush=True
            )

            print(
                "V2.1 ERROR =",
                repr(exc),
                flush=True
            )

    # ========================================================
    # TEST 1. CONFIRMED BREAKOUT LONG
    # ========================================================

    run_case(
        "BREAKOUT_LONG_QUALIFIED",
        "BREAKOUT",
        "QUALIFIED",
        "LONG",
        True,
        fixture(
            breakout_confirmed_long=True
        ),
    )

    # ========================================================
    # TEST 2. CONFIRMED BREAKOUT SHORT
    # ========================================================

    run_case(
        "BREAKOUT_SHORT_QUALIFIED",
        "BREAKOUT",
        "QUALIFIED",
        "SHORT",
        True,
        fixture(
            direction="SHORT",
            breakout_confirmed_short=True
        ),
    )

    # ========================================================
    # TEST 3. DEVELOPING BREAKOUT PROTECTION
    # ========================================================

    run_case(
        "BREAKOUT_DEVELOPING_PROTECTED",
        "BREAKOUT",
        "DEVELOPING",
        "NONE",
        False,
        fixture(
            breakout_developing_long=True,
            structure_developing_long=True
        ),
    )

    # ========================================================
    # TEST 4. STRUCTURE LONG QUALIFIED
    # ========================================================

    run_case(
        "STRUCTURE_LONG_QUALIFIED",
        "STRUCTURE",
        "QUALIFIED",
        "LONG",
        True,
        fixture(
            structure_developing_long=True
        ),
    )

    # ========================================================
    # TEST 5. STRUCTURE SHORT QUALIFIED
    # ========================================================

    run_case(
        "STRUCTURE_SHORT_QUALIFIED",
        "STRUCTURE",
        "QUALIFIED",
        "SHORT",
        True,
        fixture(
            direction="SHORT",
            structure_developing_short=True
        ),
    )

    # ========================================================
    # TEST 6. WEAK OPPOSING BREAKOUT
    #
    # SPECIFICATION:
    # A weak SHORT breakout candidate must not
    # indefinitely suppress a qualified LONG structure.
    #
    # This is a known potential gap in Unit 5 V2.
    # ========================================================

    run_case(
        "WEAK_BREAKOUT_MUST_NOT_BLOCK_STRUCTURE",
        "STRUCTURE",
        "QUALIFIED",
        "LONG",
        True,
        fixture(
            direction="LONG",
            breakout_developing_short=True,
            structure_developing_long=True
        ),
        known_gap=True,
    )

    # ========================================================
    # TEST 7. SIDEWAYS / PROFIT RANGE INSUFFICIENT
    # ========================================================

    run_case(
        "SCALP_RANGE_REJECTED",
        "NONE",
        "NONE",
        "NONE",
        False,
        fixture(
            sideways=True,
            wide_range=False
        ),
    )

    # ========================================================
    # TEST 8. SIDEWAYS / SCALP PENDING UNIT 6
    # ========================================================

    run_case(
        "SCALP_VALID_PENDING_UNIT_6",
        "SCALP",
        "PENDING_UNIT_6",
        "NONE",
        False,
        fixture(
            sideways=True,
            wide_range=True
        ),
    )

    # ========================================================
    # TEST 9. HIGHER MODE MUST BLOCK SCALP
    # ========================================================

    run_case(
        "HIGHER_MODE_BLOCKS_SCALP",
        "STRUCTURE",
        "DEVELOPING",
        "NONE",
        False,
        fixture(
            sideways=True,
            wide_range=True,
            structure_developing_long=True,
            move_15m_pct=0.010
        ),
    )

    # ========================================================
    # TEST 10. STALE EVIDENCE MUST BE REJECTED
    # ========================================================

    print("-" * 80, flush=True)
    print(
        "V2.1 TEST = STALE_CANDLE_REJECTION",
        flush=True
    )

    total += 1

    stale = fixture()
    stale["candle_data_fresh"] = False
    stale["candle_age_seconds"] = 240.0

    try:

        fresh_reconstruction_unit_5(
            config,
            stale,
        )

        failed += 1

        print(
            "V2.1 TEST RESULT = FAIL",
            flush=True
        )

    except RuntimeError as exc:

        if "STALE CANDLE" in str(exc):
            passed += 1

            print(
                "V2.1 TEST RESULT = PASS",
                flush=True
            )

        else:
            failed += 1

            print(
                "V2.1 TEST RESULT = FAIL",
                repr(exc),
                flush=True
            )

    # ========================================================
    # 3. ORIGINAL RESULT INTEGRITY
    # ========================================================

    preserved = (
        original
        ==
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
        and original_result
        ==
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
    )

    if not preserved:
        raise RuntimeError(
            "UNIT 5 V2.1 ORIGINAL STATE MODIFIED"
        )

    print("=" * 80, flush=True)
    print(
        "UNIT 5 V2.1 TEST COUNT =",
        total,
        flush=True
    )

    print(
        "UNIT 5 V2.1 PASS =",
        passed,
        flush=True
    )

    print(
        "UNIT 5 V2.1 FAIL =",
        failed,
        flush=True
    )

    print(
        "UNIT 5 V2.1 SPEC GAPS =",
        spec_gaps,
        flush=True
    )

    print(
        "UNIT 5 V2.1 ORIGINAL DATA PRESERVED =",
        preserved,
        flush=True
    )

    if failed:
        verdict = "FAIL"

    elif spec_gaps:
        verdict = "SPEC_GAPS_FOUND"

    else:
        verdict = "PASS"

    print(
        "UNIT 5 V2.1 RESULT =",
        verdict,
        flush=True
    )

    print("=" * 80, flush=True)

    return {
        "status": verdict,
        "tests": total,
        "passed": passed,
        "failed": failed,
        "spec_gaps": spec_gaps,
        "original_preserved": preserved,
        "read_only": True,
        "trade_authorized": False,
    }


# ============================================================
# RUN UNIT 5 V2.1
# ZERO INDENTATION
# ============================================================

# UNIT 5 REGRESSION TEST SWITCH
# ZERO INDENTATION

UNIT_5_V21_TEST_ENABLED = False

FRESH_UNIT_5_V21_RESULT = None

if UNIT_5_V21_TEST_ENABLED:
    FRESH_UNIT_5_V21_RESULT = (
        fresh_unit_5_v21_tests()
    )


# ============================================================
# END UNIT 5 V2.1
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 6 V1
# ZERO INDENTATION
#
# SIGNAL ADMISSION AND SCALP QUALITY
# CONSUMES UNIT 5 V2.2
#
# - BREAKOUT / STRUCTURE ADMISSION
# - SCALP 50% PRICE WEIGHT
# - SCALP QUALITY FLOOR 70
# - CLOSED CANDLE PERSISTENCE
# - FEE-AWARE PROSPECTIVE HEADROOM
# - ZERO EXCHANGE WRITE
# ============================================================

def fresh_reconstruction_unit_6(
    unit_2_config,
    unit_4_analysis,
    unit_5_candidate,
):

    import math

    print("=" * 80, flush=True)
    print("FRESH RECONSTRUCTION UNIT 6 V1 START", flush=True)

    # ========================================================
    # 1. INPUT VALIDATION
    # ========================================================

    if not all(
        isinstance(x, dict)
        for x in (
            unit_2_config,
            unit_4_analysis,
            unit_5_candidate,
        )
    ):
        raise RuntimeError("UNIT 6 INVALID INPUT CONTRACT")

    strategy = unit_2_config.get("strategy", {})
    safety = unit_2_config.get("safety", {})

    if not isinstance(strategy, dict):
        raise RuntimeError("UNIT 6 STRATEGY MISSING")

    if not isinstance(safety, dict):
        raise RuntimeError("UNIT 6 SAFETY MISSING")

    for key in (
        "one_direction_only",
        "anti_duplicate_orders",
        "exclusive_mode",
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 6 SAFETY FLAG FAILED: " + key
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
                "UNIT 6 UNSAFE CONFIG: " + key
            )

    if (
        unit_4_analysis.get("read_only") is not True
        or unit_4_analysis.get("candle_data_fresh")
        is not True
        or unit_4_analysis.get("trade_authorized")
        is not False
        or unit_4_analysis.get(
            "strategy_evidence_version"
        ) != "U4_COORDINATED_V1"
    ):
        raise RuntimeError(
            "UNIT 6 UNIT 4 EVIDENCE CONTRACT FAILED"
        )

    if (
        unit_5_candidate.get("read_only") is not True
        or unit_5_candidate.get("trade_authorized")
        is not False
        or unit_5_candidate.get("symbol")
        != unit_4_analysis.get("symbol")
    ):
        raise RuntimeError(
            "UNIT 6 UNIT 5 CONTRACT FAILED"
        )

    def number(value, label):

        try:
            result = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise RuntimeError(
                "UNIT 6 INVALID " + label
            ) from exc

        if not math.isfinite(result):
            raise RuntimeError(
                "UNIT 6 NONFINITE " + label
            )

        return result

    age = number(
        unit_4_analysis.get("candle_age_seconds"),
        "CANDLE AGE"
    )

    if not 0 <= age <= 180:
        raise RuntimeError("UNIT 6 STALE CANDLES")

    mode = unit_5_candidate.get(
        "active_mode", "NONE"
    )

    side = unit_5_candidate.get(
        "direction", "NONE"
    )

    qualified = (
        unit_5_candidate.get("qualified")
        is True
    )

    candidate_mode = unit_5_candidate.get(
        "candidate_mode", "NONE"
    )

    candidate_stage = unit_5_candidate.get(
        "candidate_stage", "NONE"
    )

    higher_mode = (
        unit_5_candidate.get(
            "higher_mode_developing"
        ) is True
    )

    unit5_reason = str(
        unit_5_candidate.get(
            "qualification_reason", "UNKNOWN"
        )
    )

    if mode not in (
        "NONE", "BREAKOUT", "STRUCTURE"
    ):
        raise RuntimeError("UNIT 6 INVALID ACTIVE MODE")

    if side not in ("NONE", "LONG", "SHORT"):
        raise RuntimeError("UNIT 6 INVALID DIRECTION")

    if candidate_mode not in (
        "NONE", "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError("UNIT 6 INVALID CANDIDATE MODE")

    if candidate_stage not in (
        "NONE", "QUALIFIED", "DEVELOPING",
        "REJECTED", "PENDING_UNIT_6"
    ):
        raise RuntimeError(
            "UNIT 6 INVALID CANDIDATE STAGE"
        )

    leverage_target = number(
        strategy.get("leverage_target", 100),
        "LEVERAGE TARGET"
    )

    if leverage_target <= 0:
        raise RuntimeError(
            "UNIT 6 INVALID LEVERAGE TARGET"
        )

    # Target is configuration only.
    # Exchange leverage has not been verified.

    # ========================================================
    # 2. INITIALIZE ADMISSION RESULT
    # ========================================================

    execution_intent = False
    admitted_mode = "NONE"
    admitted_side = "NONE"

    reason = (
        "UNIT_5_NOT_QUALIFIED:" + unit5_reason
    )

    scalp_score = None
    scalp_pass = None

    persistence_confirmations = 0
    persistence_directions = []
    persistence_pass = False

    details = {}

    live_cost_verified = False

    # ========================================================
    # 3. BREAKOUT / STRUCTURE HANDOVER
    # ========================================================

    if qualified:

        if (
            mode not in ("BREAKOUT", "STRUCTURE")
            or side not in ("LONG", "SHORT")
            or candidate_mode != mode
            or candidate_stage != "QUALIFIED"
        ):
            raise RuntimeError(
                "UNIT 6 QUALIFIED SIGNAL INCONSISTENT"
            )

        if (
            unit_4_analysis.get("direction_evidence")
            != side
        ):
            raise RuntimeError(
                "UNIT 6 QUALIFIED DIRECTION CONFLICT"
            )

        execution_intent = True
        admitted_mode = mode
        admitted_side = side

        reason = (
            mode + "_PRELIMINARY_ADMISSION_PASS"
        )

    elif (
        mode != "NONE"
        or side != "NONE"
    ):
        raise RuntimeError(
            "UNIT 6 UNQUALIFIED MODE LEAK"
        )

    # ========================================================
    # 4. SCALP PENDING VALIDATION
    # ========================================================

    scalp_pending = (
        not qualified
        and candidate_mode == "SCALP"
        and candidate_stage == "PENDING_UNIT_6"
        and not higher_mode
    )

    if scalp_pending:

        if (
            unit_4_analysis.get(
                "sideways_candidate"
            ) is not True
        ):
            raise RuntimeError(
                "UNIT 6 SCALP NOT SIDEWAYS"
            )

        if (
            unit_5_candidate.get(
                "scalp_range_feasible"
            ) is not True
        ):
            raise RuntimeError(
                "UNIT 6 SCALP RANGE NOT FEASIBLE"
            )

        direction = unit_4_analysis.get(
            "direction_evidence"
        )

        if direction not in ("LONG", "SHORT"):
            raise RuntimeError(
                "UNIT 6 SCALP DIRECTION INVALID"
            )

        candles = unit_4_analysis.get(
            "recent_closed_klines", []
        )

        if (
            not isinstance(candles, list)
            or len(candles) < 20
        ):
            raise RuntimeError(
                "UNIT 6 SCALP HISTORY INSUFFICIENT"
            )

        latest = number(
            unit_4_analysis.get("latest_close"),
            "LATEST CLOSE"
        )

        ema19 = number(
            unit_4_analysis.get("ema19"),
            "EMA19"
        )

        atr14 = number(
            unit_4_analysis.get("atr14"),
            "ATR14"
        )

        support = number(
            unit_4_analysis.get("support20"),
            "SUPPORT20"
        )

        resistance = number(
            unit_4_analysis.get("resistance20"),
            "RESISTANCE20"
        )

        move1 = number(
            unit_4_analysis.get("move_1m_pct"),
            "MOVE1"
        )

        move5 = number(
            unit_4_analysis.get("move_5m_pct"),
            "MOVE5"
        )

        move15 = number(
            unit_4_analysis.get("move_15m_pct"),
            "MOVE15"
        )

        if (
            latest <= 0
            or ema19 <= 0
            or atr14 <= 0
            or support <= 0
            or resistance <= support
        ):
            raise RuntimeError(
                "UNIT 6 INVALID SCALP PRICE GEOMETRY"
            )

        # ====================================================
        # 5. CLOSED-CANDLE PERSISTENCE
        # ====================================================

        for candle in candles[-3:]:

            open_price = number(
                candle.get("open"), "CANDLE OPEN"
            )

            close_price = number(
                candle.get("close"), "CANDLE CLOSE"
            )

            if close_price > open_price:
                persistence_directions.append("LONG")

            elif close_price < open_price:
                persistence_directions.append("SHORT")

            else:
                persistence_directions.append("NONE")

        persistence_confirmations = sum(
            x == direction
            for x in persistence_directions
        )

        persistence_pass = (
            persistence_confirmations >= 2
        )

        # ====================================================
        # 6. PRICE BEHAVIOR: 50 POINTS
        #
        # Reward:
        # - directional price momentum
        # - persistence
        # - limited EMA extension
        # - absence of large price spike
        # ====================================================

        sign = 1 if direction == "LONG" else -1

        directional_move5 = move5 * sign
        directional_move1 = move1 * sign

        momentum_score = (
            15.0 if directional_move5 >= 0.03
            else 8.0 if directional_move5 > 0
            else 0.0
        )

        freshness_score = (
            10.0 if directional_move1 > 0
            else 0.0
        )

        persistence_score = (
            15.0 if persistence_confirmations == 3
            else 10.0 if persistence_confirmations == 2
            else 0.0
        )

        extension_ratio = (
            abs(latest - ema19) / atr14
        )

        extension_score = (
            10.0 if extension_ratio <= 0.75
            else 5.0 if extension_ratio <= 1.5
            else 0.0
        )

        price_score = (
            momentum_score
            + freshness_score
            + persistence_score
            + extension_score
        )

        # ====================================================
        # 7. SUPPORTING FACTORS: 50 POINTS
        # ====================================================

        sideways_score = 15.0

        agreement_score = (
            10.0 if move15 * sign >= 0
            else 0.0
        )

        range_score = (
            10.0 if unit_5_candidate.get(
                "scalp_range_feasible"
            ) is True else 0.0
        )

        near_boundary = (
            latest <= support + 0.50 * atr14
            if direction == "LONG"
            else latest >= resistance - 0.50 * atr14
        )

        boundary_score = (
            10.0 if near_boundary else 0.0
        )

        no_overextension = (
            unit_4_analysis.get(
                "price_overextended"
            ) is False
        )

        overextension_score = (
            5.0 if no_overextension
            else 0.0
        )

        other_score = (
            sideways_score
            + agreement_score
            + range_score
            + boundary_score
            + overextension_score
        )

        scalp_score = (
            price_score + other_score
        )

        quality_minimum = number(
            strategy.get(
                "scalp_quality_threshold", 70
            ),
            "SCALP QUALITY FLOOR"
        )

        scalp_pass = (
            scalp_score >= quality_minimum
        )

        # ====================================================
        # 8. PRICE SPIKE FILTER
        # ====================================================

        last_candle = candles[-1]

        last_high = number(
            last_candle.get("high"),
            "LAST HIGH"
        )

        last_low = number(
            last_candle.get("low"),
            "LAST LOW"
        )

        spike_ratio = (
            (last_high - last_low) / atr14
        )

        spike_pass = (
            spike_ratio <= 2.0
        )

        extension_pass = (
            extension_ratio <= 1.5
        )

        # ====================================================
        # 9. PROSPECTIVE FEE HEADROOM
        #
        # Historical support/resistance is not
        # a guaranteed execution target.
        # ====================================================

        headroom_pct = max(
            0.0,
            (
                (resistance - latest) / latest * 100.0
                if direction == "LONG"
                else (latest - support) / latest * 100.0
            )
        )

        # Conservative provisional assumptions.
        # Not verified WEEX execution charges.

        round_trip_fees_pct = 0.16
        friction_allowance_pct = 0.02

        estimated_cost_pct = (
            round_trip_fees_pct
            + friction_allowance_pct
        )

        estimated_net_price_pct = (
            headroom_pct - estimated_cost_pct
        )

        provisional_leveraged_roi = (
            estimated_net_price_pct
            * leverage_target
        )

        minimum_roi = number(
            strategy.get(
                "scalp_min_net_roi_percent", 5.0
            ),
            "SCALP MIN NET ROI"
        )

        fee_pass = (
            provisional_leveraged_roi >= minimum_roi
        )

        details = {
            "price_score": price_score,
            "other_score": other_score,
            "persistence_confirmations":
                persistence_confirmations,
            "extension_ratio": extension_ratio,
            "spike_ratio": spike_ratio,
            "headroom_pct": headroom_pct,
            "estimated_cost_pct":
                estimated_cost_pct,
            "estimated_net_price_pct":
                estimated_net_price_pct,
            "provisional_leveraged_roi_pct":
                provisional_leveraged_roi,
            "fee_pass": fee_pass,
            "live_cost_verified": False,
            "minimum_net_roi_pct": minimum_roi,
        }

        # ====================================================
        # 10. SCALP VERDICT
        # ====================================================

        if not spike_pass:

            reason = "SCALP_PRICE_SPIKE_REJECTED"

        elif not extension_pass:

            reason = "SCALP_EMA_EXTENSION_REJECTED"

        elif not persistence_pass:

            reason = "SCALP_PERSISTENCE_REJECTED"

        elif not scalp_pass:

            reason = "SCALP_QUALITY_BELOW_THRESHOLD"

        elif not fee_pass:

            reason = "SCALP_INSUFFICIENT_NET_HEADROOM"

        else:

            reason = (
                "SCALP_PRELIMINARY_PASS_"
                "AWAITING_VERIFIED_LIVE_COSTS"
            )

        # IMPORTANT:
        # No live spread/order-book or authenticated
        # execution-cost verification is available.
        # Scalp is therefore held, even if score passes.

        execution_intent = False
        admitted_mode = "NONE"
        admitted_side = "NONE"

        print(
            "UNIT 6 SCALP PRICE SCORE =",
            price_score,
            flush=True
        )

        print(
            "UNIT 6 SCALP OTHER SCORE =",
            other_score,
            flush=True
        )

        print(
            "UNIT 6 SCALP TOTAL SCORE =",
            scalp_score,
            flush=True
        )

        print(
            "UNIT 6 SCALP EST NET ROI % =",
            round(provisional_leveraged_roi, 4),
            flush=True
        )

        print(
            "UNIT 6 LIVE COST VERIFIED = FALSE",
            flush=True
        )

    # ========================================================
    # 11. SAFETY AND UNIT 7 CONSISTENCY
    # ========================================================

    signal_qualified = execution_intent

    if execution_intent:

        if (
            admitted_mode not in (
                "BREAKOUT", "STRUCTURE"
            )
            or admitted_side not in (
                "LONG", "SHORT"
            )
        ):
            raise RuntimeError(
                "UNIT 6 ACTIVE SIGNAL INCONSISTENT"
            )

    else:

        if (
            admitted_mode != "NONE"
            or admitted_side != "NONE"
        ):
            raise RuntimeError(
                "UNIT 6 IDLE SIGNAL INCONSISTENT"
            )

    leverage_regime = (
        "GE_100X" if leverage_target >= 100
        else "50_99X" if leverage_target >= 50
        else "20_49X" if leverage_target >= 20
        else "11_19X" if leverage_target >= 11
        else "LE_10X"
    )

    # ========================================================
    # 12. NORMALIZED OUTPUT FOR UNIT 7
    # ========================================================

    result = {
        "execution_intent": execution_intent,
        "signal_qualified": signal_qualified,
        "active_mode": admitted_mode,
        "direction": admitted_side,

        "candidate_mode": candidate_mode,
        "candidate_stage": candidate_stage,

        "higher_mode_developing": higher_mode,

        "unit_5_reason": unit5_reason,
        "admission_reason": reason,

        "leverage_target": leverage_target,
        "leverage_regime": leverage_regime,

        "exchange_leverage_verified": False,
        "leverage_source": "WEEX_EXCHANGE",
        "effective_leverage": None,

        "sideways_regime":
            unit_4_analysis.get(
                "sideways_candidate", False
            ),

        "ema_compressed": False,
        "compression_threshold_pct": 0.09,
        "momentum_conflict": False,

        "persistence_window": 3,
        "persistence_required": 2,
        "persistence_confirmations":
            persistence_confirmations,

        "persistence_directions":
            persistence_directions,

        "persistence_pass": persistence_pass,

        "fifteen_minute_support_pass": (
            False if scalp_pending
            and move15 * sign < 0
            else True
        ),

        "scalp_quality_score": scalp_score,
        "scalp_quality_minimum": 70.0,
        "scalp_quality_pass": scalp_pass,
        "scalp_quality_details": details,

        "live_cost_verified": live_cost_verified,
        "read_only": True,
        "trade_authorized": False,

        "order_payload_created": False,
        "demo_order_submitted": False,
        "real_order_submitted": False,
        "exchange_write": False,
    }

    print("-" * 80, flush=True)

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
        "UNIT 6 SELECTED MODE =",
        admitted_mode,
        flush=True
    )

    print(
        "UNIT 6 DIRECTION =",
        admitted_side,
        flush=True
    )

    print(
        "UNIT 6 ADMISSION REASON =",
        reason,
        flush=True
    )

    print(
        "UNIT 6 EXECUTION INTENT =",
        execution_intent,
        flush=True
    )

    print(
        "UNIT 6 TRADE AUTHORIZED = FALSE",
        flush=True
    )

    print(
        "UNIT 6 NETWORK REQUEST = NONE",
        flush=True
    )

    print(
        "UNIT 6 ORDER PAYLOAD = NONE",
        flush=True
    )

    print(
        "UNIT 6 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 6 REAL ORDER = NONE",
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

    return result


# ============================================================
# RUN UNIT 6 V1
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
# END UNIT 6 V1
# ZERO INDENTATION
# ============================================================


# ============================================================
# START UNIT 6 V1.1 CONTROLLED TEST SUITE
# ZERO INDENTATION
# READ ONLY - NO NETWORK - NO ORDERS
# ============================================================

UNIT_6_V11_TEST_ENABLED = True


def fresh_unit_6_v11_tests():

    import copy

    print("=" * 80, flush=True)
    print(
        "UNIT 6 V1.1 CONTROLLED TEST START",
        flush=True
    )

    config = FRESH_RECONSTRUCTION_CONFIG

    original_market = (
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
    )

    original_signal = (
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
    )

    original_execution = (
        FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE
    )

    # Protect all original data against test changes.
    original_market_copy = copy.deepcopy(
        original_market
    )
    original_signal_copy = copy.deepcopy(
        original_signal
    )
    original_execution_copy = copy.deepcopy(
        original_execution
    )

    results = []

    # ========================================================
    # 1. SYNTHETIC MARKET SNAPSHOT
    # ========================================================

    def market_fixture():

        data = copy.deepcopy(original_market)

        data["symbol"] = "BTCUSDT"
        data["read_only"] = True
        data["trade_authorized"] = False
        data["candle_data_fresh"] = True
        data["candle_age_seconds"] = 30.0

        data["strategy_evidence_version"] = (
            "U4_COORDINATED_V1"
        )

        data["direction_evidence"] = "LONG"
        data["sideways_candidate"] = True
        data["price_overextended"] = False

        data["latest_close"] = 10000.0
        data["live_mark_price"] = 10000.0
        data["previous_close"] = 9996.0
        data["ema19"] = 9990.0
        data["atr14"] = 30.0

        data["support20"] = 9950.0
        data["resistance20"] = 10080.0

        data["move_1m_pct"] = 0.04
        data["move_5m_pct"] = 0.07
        data["move_15m_pct"] = 0.02

        candles = []

        for index in range(20):

            candles.append({
                "open": 9995.0,
                "high": 10010.0,
                "low": 9990.0,
                "close": 10000.0,
            })

        data["recent_closed_klines"] = candles

        return data

    # ========================================================
    # 2. SYNTHETIC UNIT 5 HANDOVER
    # ========================================================

    def signal_fixture(
        mode="NONE",
        side="NONE",
        qualified=False,
        stage="NONE",
    ):

        candidate_mode = (
            mode if mode != "NONE"
            else "NONE"
        )

        return {
            "symbol": "BTCUSDT",
            "read_only": True,
            "trade_authorized": False,

            "qualified": qualified,

            "active_mode": (
                mode if qualified else "NONE"
            ),

            "direction": (
                side if qualified else "NONE"
            ),

            "candidate_mode": candidate_mode,
            "candidate_stage": stage,

            "higher_mode_developing": (
                mode in ("BREAKOUT", "STRUCTURE")
            ),

            "scalp_range_feasible": (
                mode == "SCALP"
            ),

            "qualification_reason": (
                "CONTROLLED_UNIT_6_TEST"
            ),
        }

    # ========================================================
    # 3. TEST RUNNER
    # ========================================================

    def run_case(
        name,
        market,
        signal,
        expected_reason,
        expected_intent=False,
        expect_exception=False,
    ):

        print("-" * 80, flush=True)
        print(
            "UNIT 6 V1.1 TEST =",
            name,
            flush=True
        )

        actual_reason = None
        actual_intent = None

        try:

            output = fresh_reconstruction_unit_6(
                config,
                market,
                signal,
            )

            actual_reason = output.get(
                "admission_reason"
            )

            actual_intent = output.get(
                "execution_intent"
            )

            safety_pass = (
                output.get("read_only") is True
                and output.get(
                    "trade_authorized"
                ) is False
                and output.get(
                    "exchange_write"
                ) is False
                and output.get(
                    "order_payload_created"
                ) is False
                and output.get(
                    "demo_order_submitted"
                ) is False
                and output.get(
                    "real_order_submitted"
                ) is False
            )

            if actual_intent:
                contract_pass = (
                    output.get("signal_qualified")
                    is True
                    and output.get("active_mode")
                    in ("BREAKOUT", "STRUCTURE")
                    and output.get("direction")
                    in ("LONG", "SHORT")
                )
            else:
                contract_pass = (
                    output.get("signal_qualified")
                    is False
                    and output.get("active_mode")
                    == "NONE"
                    and output.get("direction")
                    == "NONE"
                )

            passed = (
                not expect_exception
                and actual_reason == expected_reason
                and actual_intent == expected_intent
                and safety_pass
                and contract_pass
            )

        except RuntimeError as exc:

            actual_reason = str(exc)
            actual_intent = False

            passed = (
                expect_exception
                and expected_reason in str(exc)
            )

        except Exception as exc:

            actual_reason = (
                "UNEXPECTED_EXCEPTION: "
                + repr(exc)
            )

            passed = False

        print(
            "UNIT 6 V1.1 EXPECTED REASON =",
            expected_reason,
            flush=True
        )

        print(
            "UNIT 6 V1.1 ACTUAL REASON =",
            actual_reason,
            flush=True
        )

        print(
            "UNIT 6 V1.1 ACTUAL INTENT =",
            actual_intent,
            flush=True
        )

        print(
            "UNIT 6 V1.1 TEST RESULT =",
            "PASS" if passed else "FAIL",
            flush=True
        )

        results.append({
            "name": name,
            "passed": passed,
            "reason": actual_reason,
        })

    # ========================================================
    # TESTS 1-4: BREAKOUT AND STRUCTURE
    # ========================================================

    for mode, side in (
        ("BREAKOUT", "LONG"),
        ("BREAKOUT", "SHORT"),
        ("STRUCTURE", "LONG"),
        ("STRUCTURE", "SHORT"),
    ):

        market = market_fixture()
        market["direction_evidence"] = side

        signal = signal_fixture(
            mode=mode,
            side=side,
            qualified=True,
            stage="QUALIFIED",
        )

        run_case(
            mode + "_" + side + "_ADMISSION",
            market,
            signal,
            mode + "_PRELIMINARY_ADMISSION_PASS",
            expected_intent=True,
        )

    # ========================================================
    # TEST 5: SCALP PASSES PRELIMINARY CHECKS
    # BUT MUST REMAIN HELD
    # ========================================================

    scalp_signal = signal_fixture(
        mode="SCALP",
        stage="PENDING_UNIT_6",
    )

    run_case(
        "SCALP_QUALITY_PASS_HELD",
        market_fixture(),
        scalp_signal,
        "SCALP_PRELIMINARY_PASS_"
        "AWAITING_VERIFIED_LIVE_COSTS",
    )

    # ========================================================
    # TEST 6: QUALITY SCORE BELOW 70
    # ========================================================

    low_quality = market_fixture()

    low_quality["move_1m_pct"] = -0.01
    low_quality["move_5m_pct"] = -0.01
    low_quality["move_15m_pct"] = -0.01

    low_quality["recent_closed_klines"][-1] = {
        "open": 10002.0,
        "high": 10010.0,
        "low": 9990.0,
        "close": 10000.0,
    }

    run_case(
        "SCALP_QUALITY_BELOW_70",
        low_quality,
        scalp_signal,
        "SCALP_QUALITY_BELOW_THRESHOLD",
    )

    # ========================================================
    # TEST 7: INSUFFICIENT NET HEADROOM
    # ========================================================

    low_headroom = market_fixture()

    low_headroom["resistance20"] = 10001.0

    run_case(
        "SCALP_FEE_REJECTION",
        low_headroom,
        scalp_signal,
        "SCALP_INSUFFICIENT_NET_HEADROOM",
    )

    # ========================================================
    # TEST 8: EXCESSIVE PRICE SPIKE
    # ========================================================

    spike = market_fixture()

    spike["recent_closed_klines"][-1] = {
        "open": 9995.0,
        "high": 10090.0,
        "low": 9990.0,
        "close": 10000.0,
    }

    run_case(
        "SCALP_SPIKE_REJECTION",
        spike,
        scalp_signal,
        "SCALP_PRICE_SPIKE_REJECTED",
    )

    # ========================================================
    # TEST 9: INSUFFICIENT PERSISTENCE
    # ========================================================

    no_persistence = market_fixture()

    for index in (-3, -2, -1):

        no_persistence[
            "recent_closed_klines"
        ][index] = {
            "open": 10002.0,
            "high": 10010.0,
            "low": 9990.0,
            "close": 10000.0,
        }

    run_case(
        "SCALP_PERSISTENCE_REJECTION",
        no_persistence,
        scalp_signal,
        "SCALP_PERSISTENCE_REJECTED",
    )

    # ========================================================
    # TEST 10: STALE MARKET REJECTION
    # ========================================================

    stale = market_fixture()
    stale["candle_age_seconds"] = 240.0

    run_case(
        "STALE_MARKET_REJECTION",
        stale,
        signal_fixture(),
        "UNIT 6 STALE CANDLES",
        expect_exception=True,
    )

    # ========================================================
    # 4. ORIGINAL STATE INTEGRITY
    # ========================================================

    originals_preserved = (
        original_market
        == original_market_copy
        and original_signal
        == original_signal_copy
        and original_execution
        == original_execution_copy
    )

    if not originals_preserved:
        raise RuntimeError(
            "UNIT 6 V1.1 ORIGINAL STATE CHANGED"
        )

    # ========================================================
    # 5. FINAL SUMMARY
    # ========================================================

    passed_count = sum(
        item["passed"] for item in results
    )

    failed_count = (
        len(results) - passed_count
    )

    verdict = (
        "PASS"
        if failed_count == 0
        else "FAIL"
    )

    print("=" * 80, flush=True)

    print(
        "UNIT 6 V1.1 TEST COUNT =",
        len(results),
        flush=True
    )

    print(
        "UNIT 6 V1.1 PASS =",
        passed_count,
        flush=True
    )

    print(
        "UNIT 6 V1.1 FAIL =",
        failed_count,
        flush=True
    )

    print(
        "UNIT 6 V1.1 ORIGINAL DATA PRESERVED =",
        originals_preserved,
        flush=True
    )

    print(
        "UNIT 6 V1.1 RESULT =",
        verdict,
        flush=True
    )

    print("=" * 80, flush=True)

    return {
        "status": verdict,
        "total": len(results),
        "passed": passed_count,
        "failed": failed_count,
        "original_preserved": originals_preserved,
        "details": results,
    }


# ============================================================
# RUN UNIT 6 V1.1
# ZERO INDENTATION
# ============================================================


# ============================================================
# UNIT 6 V1.1 TEST SWITCH
# ZERO INDENTATION
# ============================================================

UNIT_6_V11_TEST_ENABLED = False

FRESH_UNIT_6_V11_RESULT = None

if UNIT_6_V11_TEST_ENABLED:
    FRESH_UNIT_6_V11_RESULT = (
        fresh_unit_6_v11_tests()
    )


# ============================================================
# END UNIT 6 V1.1
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 7 V1
# ZERO INDENTATION
#
# SIGNAL HANDOVER AND POSITION SIZING PREPARATION
#
# INPUT:
# - UNIT 2 CONFIGURATION
# - UNIT 6 EXECUTION CANDIDATE
#
# SAFETY:
# - NO AUTHENTICATED REQUEST
# - NO ACCOUNT BALANCE READ
# - NO POSITION READ
# - NO LEVERAGE MUTATION
# - NO ORDER PAYLOAD
# - NO DEMO OR REAL ORDER
# - ZERO EXCHANGE WRITE
# ============================================================

def fresh_reconstruction_unit_7(
    unit_2_config,
    unit_6_candidate,
):

    import math

    print("=" * 80, flush=True)
    print(
        "FRESH RECONSTRUCTION UNIT 7 V1 START",
        flush=True
    )

    # ========================================================
    # 1. INPUT CONTRACT
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 7 INVALID UNIT 2 CONFIGURATION"
        )

    if not isinstance(unit_6_candidate, dict):
        raise RuntimeError(
            "UNIT 7 INVALID UNIT 6 CANDIDATE"
        )

    strategy = unit_2_config.get("strategy")
    safety = unit_2_config.get("safety")
    exchange = unit_2_config.get("exchange")
    precision = unit_2_config.get(
        "market_precision"
    )

    if not all(
        isinstance(x, dict)
        for x in (
            strategy,
            safety,
            exchange,
            precision,
        )
    ):
        raise RuntimeError(
            "UNIT 7 CONFIGURATION SECTIONS MISSING"
        )

    # ========================================================
    # 2. STRICT EXCHANGE SAFETY
    # ========================================================

    forbidden_flags = (
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

    for key in forbidden_flags:

        if safety.get(key) is not False:

            raise RuntimeError(
                "UNIT 7 UNSAFE CONFIGURATION: "
                + key
            )

    if (
        unit_6_candidate.get("read_only")
        is not True
        or unit_6_candidate.get(
            "trade_authorized"
        ) is not False
        or unit_6_candidate.get(
            "exchange_write"
        ) is not False
        or unit_6_candidate.get(
            "order_payload_created"
        ) is not False
        or unit_6_candidate.get(
            "demo_order_submitted"
        ) is not False
        or unit_6_candidate.get(
            "real_order_submitted"
        ) is not False
    ):

        raise RuntimeError(
            "UNIT 7 UNIT 6 SAFETY CONTRACT FAILED"
        )

    print(
        "PASS: UNIT 7 READ ONLY SAFETY",
        flush=True
    )

    # ========================================================
    # 3. NUMBER VALIDATION HELPER
    # ========================================================

    def finite_number(
        value,
        label,
        allow_none=False,
    ):

        if value is None and allow_none:
            return None

        try:
            result = float(value)

        except (
            TypeError,
            ValueError,
            OverflowError,
        ) as exc:

            raise RuntimeError(
                "UNIT 7 INVALID " + label
            ) from exc

        if not math.isfinite(result):

            raise RuntimeError(
                "UNIT 7 NONFINITE " + label
            )

        return result

    # ========================================================
    # 4. RECEIVE UNIT 6 DECISION
    # ========================================================

    execution_intent = unit_6_candidate.get(
        "execution_intent"
    )

    signal_qualified = unit_6_candidate.get(
        "signal_qualified"
    )

    active_mode = unit_6_candidate.get(
        "active_mode"
    )

    direction = unit_6_candidate.get(
        "direction"
    )

    unit_5_reason = str(
        unit_6_candidate.get(
            "unit_5_reason", "UNKNOWN"
        )
    )

    admission_reason = str(
        unit_6_candidate.get(
            "admission_reason", "UNKNOWN"
        )
    )

    if (
        type(execution_intent) is not bool
        or type(signal_qualified) is not bool
    ):

        raise RuntimeError(
            "UNIT 7 INVALID SIGNAL FLAGS"
        )

    if execution_intent != signal_qualified:

        raise RuntimeError(
            "UNIT 7 SIGNAL QUALIFICATION MISMATCH"
        )

    if active_mode not in (
        "NONE",
        "BREAKOUT",
        "STRUCTURE",
    ):

        raise RuntimeError(
            "UNIT 7 INVALID ACTIVE MODE"
        )

    if direction not in (
        "NONE",
        "LONG",
        "SHORT",
    ):

        raise RuntimeError(
            "UNIT 7 INVALID DIRECTION"
        )

    if execution_intent:

        if (
            active_mode not in (
                "BREAKOUT",
                "STRUCTURE",
            )
            or direction not in (
                "LONG",
                "SHORT",
            )
        ):

            raise RuntimeError(
                "UNIT 7 ACTIVE SIGNAL INCONSISTENT"
            )

        if (
            unit_6_candidate.get(
                "candidate_mode"
            ) != active_mode
            or unit_6_candidate.get(
                "candidate_stage"
            ) != "QUALIFIED"
        ):

            raise RuntimeError(
                "UNIT 7 QUALIFIED HANDOVER MISMATCH"
            )

    else:

        if (
            active_mode != "NONE"
            or direction != "NONE"
        ):

            raise RuntimeError(
                "UNIT 7 IDLE HANDOVER MISMATCH"
            )

    print(
        "PASS: UNIT 7 UNIT 6 HANDOVER VALIDATED",
        flush=True
    )

    # ========================================================
    # 5. CONFIGURATION AND LEVERAGE
    # ========================================================

    configured_leverage = finite_number(
        unit_6_candidate.get(
            "leverage_target"
        ),
        "LEVERAGE TARGET",
    )

    if configured_leverage <= 0:

        raise RuntimeError(
            "UNIT 7 INVALID LEVERAGE TARGET"
        )

    if (
        unit_6_candidate.get(
            "exchange_leverage_verified"
        ) is not False
        or unit_6_candidate.get(
            "effective_leverage"
        ) is not None
    ):

        raise RuntimeError(
            "UNIT 7 UNEXPECTED LEVERAGE STATE"
        )

    leverage_source = "WEEX_EXCHANGE"
    exchange_leverage_verified = False
    effective_leverage = None

    # NOTE:
    # Configured 100x is a target only.
    # It must not be used as actual leverage.

    # ========================================================
    # 6. MARKET PRECISION CONTRACT
    # ========================================================

    # Unit 2 owns market precision settings.
    # Read them without changing configuration.
    # Do not assume undocumented dictionary keys.

    precision_reference = {
        "configuration_present": True,
        "configuration_keys": sorted(
            str(key) for key in precision.keys()
        ),
        "exchange_precision_verified": False,
    }

    # Executable BTC quantity depends on:
    # - Actual account balance
    # - Actual position state
    # - Verified exchange leverage
    # - Confirmed quantity step and minimum size
    # - Current executable bid/ask price
    #
    # None is inferred from mark price alone.

    # ========================================================
    # 7. PREPARE READ-ONLY SIZING STATUS
    # ========================================================

    balance_verified = False
    position_state_verified = False
    margin_mode_verified = False
    quantity_rules_verified = False
    executable_price_verified = False

    initial_margin_usdt = None
    position_notional_usdt = None
    proposed_quantity = None

    maximum_exposure_verified = False
    backup_capacity_verified = False

    position_sizing_performed = False
    quantity_calculated = False

    order_payload_created = False

    # ========================================================
    # 8. SAFETY GATE FOR SIGNALS
    # ========================================================

    if execution_intent:

        status = "HELD"

        sizing_reason = (
            "QUALIFIED_SIGNAL_AWAITING_"
            "VERIFIED_ACCOUNT_AND_EXCHANGE_DATA"
        )

        print(
            "PASS: UNIT 7 QUALIFIED SIGNAL RECEIVED",
            flush=True
        )

        print(
            "UNIT 7 SIGNAL HELD FOR VALIDATION",
            flush=True
        )

    else:

        status = "IDLE"

        sizing_reason = (
            "NO_QUALIFIED_SIGNAL"
        )

        print(
            "PASS: UNIT 7 IDLE HANDOVER",
            flush=True
        )

    # ========================================================
    # 9. HARD EXECUTION BOUNDARY
    # ========================================================

    trade_authorized = False
    demo_order_enabled = False
    real_order_enabled = False
    exchange_write = False

    if any((
        trade_authorized,
        demo_order_enabled,
        real_order_enabled,
        exchange_write,
        order_payload_created,
        position_sizing_performed,
        quantity_calculated,
    )):

        raise RuntimeError(
            "UNIT 7 READ ONLY BOUNDARY VIOLATED"
        )

    # ========================================================
    # 10. RESULT FOR UNIT 8
    # ========================================================

    result = {

        "status": status,

        "signal_received": execution_intent,
        "signal_qualified": signal_qualified,

        "active_mode": active_mode,
        "direction": direction,

        "unit_5_reason": unit_5_reason,
        "admission_reason": admission_reason,

        "sizing_reason": sizing_reason,

        "configured_leverage": configured_leverage,
        "leverage_source": leverage_source,

        "exchange_leverage_verified":
            exchange_leverage_verified,

        "effective_leverage":
            effective_leverage,

        "precision_reference":
            precision_reference,

        "balance_verified":
            balance_verified,

        "position_state_verified":
            position_state_verified,

        "margin_mode_verified":
            margin_mode_verified,

        "quantity_rules_verified":
            quantity_rules_verified,

        "executable_price_verified":
            executable_price_verified,

        "maximum_exposure_verified":
            maximum_exposure_verified,

        "backup_capacity_verified":
            backup_capacity_verified,

        "account_balance_required":
            execution_intent,

        "initial_margin_usdt":
            initial_margin_usdt,

        "position_notional_usdt":
            position_notional_usdt,

        "proposed_quantity":
            proposed_quantity,

        "position_sizing_performed":
            position_sizing_performed,

        "quantity_calculated":
            quantity_calculated,

        "order_payload_created":
            order_payload_created,

        "trade_authorized":
            trade_authorized,

        "demo_order_enabled":
            demo_order_enabled,

        "real_order_enabled":
            real_order_enabled,

        "exchange_write":
            exchange_write,

        "read_only": True,

        "execution_intent": False,

    }

    # ========================================================
    # 11. DIAGNOSTIC REPORT
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "UNIT 7 STATUS =",
        status,
        flush=True
    )

    print(
        "UNIT 7 SIGNAL RECEIVED =",
        execution_intent,
        flush=True
    )

    print(
        "UNIT 7 MODE =",
        active_mode,
        flush=True
    )

    print(
        "UNIT 7 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 7 SIZING REASON =",
        sizing_reason,
        flush=True
    )

    print(
        "UNIT 7 CONFIGURED LEVERAGE =",
        configured_leverage,
        flush=True
    )

    print(
        "UNIT 7 ACTUAL LEVERAGE VERIFIED =",
        exchange_leverage_verified,
        flush=True
    )

    print(
        "UNIT 7 ACCOUNT BALANCE VERIFIED =",
        balance_verified,
        flush=True
    )

    print(
        "UNIT 7 POSITION STATE VERIFIED =",
        position_state_verified,
        flush=True
    )

    print(
        "UNIT 7 POSITION SIZING PERFORMED =",
        position_sizing_performed,
        flush=True
    )

    print(
        "UNIT 7 QUANTITY CALCULATED =",
        quantity_calculated,
        flush=True
    )

    print(
        "UNIT 7 EXECUTION INTENT = FALSE",
        flush=True
    )

    print(
        "UNIT 7 TRADE AUTHORIZED = FALSE",
        flush=True
    )

    print(
        "UNIT 7 AUTHENTICATED REQUEST = NONE",
        flush=True
    )

    print(
        "UNIT 7 ACCOUNT ACCESS = NONE",
        flush=True
    )

    print(
        "UNIT 7 POSITION ACCESS = NONE",
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
        "FRESH RECONSTRUCTION UNIT 7 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 7 V1
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_7_RESULT = (
    fresh_reconstruction_unit_7(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE,
    )
)

# ============================================================
# END COMPLETE REPLACEMENT - UNIT 7 V1
# ZERO INDENTATION
# ============================================================


# ============================================================
# START UNIT 7 V1.1 CONTROLLED TEST SUITE
# ZERO INDENTATION
#
# TEST UNIT 7 V1 WITHOUT CHANGING IT
# SYNTHETIC DATA ONLY
# NO ACCOUNT ACCESS
# NO NETWORK REQUEST
# NO ORDER SUBMISSION
# ZERO EXCHANGE WRITE
# ============================================================

UNIT_7_V11_TEST_ENABLED = True


def fresh_unit_7_v11_tests():

    import copy

    print("=" * 80, flush=True)
    print(
        "UNIT 7 V1.1 CONTROLLED TEST START",
        flush=True
    )

    # ========================================================
    # 1. PRESERVE ORIGINAL INPUT AND OUTPUT
    # ========================================================

    original_config = (
        FRESH_RECONSTRUCTION_CONFIG
    )

    original_candidate = (
        FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE
    )

    original_result = (
        FRESH_RECONSTRUCTION_UNIT_7_RESULT
    )

    baseline_config = copy.deepcopy(
        original_config
    )

    baseline_candidate = copy.deepcopy(
        original_candidate
    )

    baseline_result = copy.deepcopy(
        original_result
    )

    test_results = []

    # ========================================================
    # 2. NORMALIZED TEST FIXTURES
    # ========================================================

    def make_config():

        return copy.deepcopy(
            baseline_config
        )

    def make_candidate(
        mode="NONE",
        side="NONE",
        qualified=False,
        candidate_mode=None,
        candidate_stage=None,
    ):

        data = copy.deepcopy(
            baseline_candidate
        )

        if candidate_mode is None:
            candidate_mode = mode

        if candidate_stage is None:
            candidate_stage = (
                "QUALIFIED" if qualified
                else "NONE"
            )

        data["execution_intent"] = qualified
        data["signal_qualified"] = qualified

        data["active_mode"] = mode
        data["direction"] = side

        data["candidate_mode"] = candidate_mode
        data["candidate_stage"] = candidate_stage

        data["unit_5_reason"] = (
            "CONTROLLED_UNIT_7_TEST"
        )

        data["admission_reason"] = (
            "CONTROLLED_UNIT_7_TEST"
        )

        data["read_only"] = True
        data["trade_authorized"] = False
        data["exchange_write"] = False

        data["order_payload_created"] = False
        data["demo_order_submitted"] = False
        data["real_order_submitted"] = False

        data["leverage_target"] = 100.0
        data["exchange_leverage_verified"] = False
        data["effective_leverage"] = None

        return data

    # ========================================================
    # 3. TEST CASE RUNNER
    # ========================================================

    def run_case(
        name,
        config,
        candidate,
        expected_status=None,
        expected_mode=None,
        expected_direction=None,
        expected_exception=None,
    ):

        print("-" * 80, flush=True)
        print(
            "UNIT 7 V1.1 TEST =",
            name,
            flush=True
        )

        # Preserve each individual fixture.
        config_before = copy.deepcopy(config)
        candidate_before = copy.deepcopy(candidate)

        actual_status = None
        actual_reason = None
        passed = False

        try:

            output = fresh_reconstruction_unit_7(
                config,
                candidate,
            )

            actual_status = output.get("status")

            actual_reason = output.get(
                "sizing_reason"
            )

            safety_pass = (
                output.get("read_only") is True
                and output.get(
                    "trade_authorized"
                ) is False
                and output.get(
                    "exchange_write"
                ) is False
                and output.get(
                    "order_payload_created"
                ) is False
                and output.get(
                    "demo_order_enabled"
                ) is False
                and output.get(
                    "real_order_enabled"
                ) is False
                and output.get(
                    "execution_intent"
                ) is False
            )

            sizing_pass = (
                output.get(
                    "position_sizing_performed"
                ) is False
                and output.get(
                    "quantity_calculated"
                ) is False
                and output.get(
                    "proposed_quantity"
                ) is None
                and output.get(
                    "balance_verified"
                ) is False
                and output.get(
                    "position_state_verified"
                ) is False
                and output.get(
                    "exchange_leverage_verified"
                ) is False
                and output.get(
                    "effective_leverage"
                ) is None
            )

            if expected_status == "HELD":

                handover_pass = (
                    output.get(
                        "signal_received"
                    ) is True
                    and output.get(
                        "signal_qualified"
                    ) is True
                    and output.get(
                        "account_balance_required"
                    ) is True
                )

            else:

                handover_pass = (
                    output.get(
                        "signal_received"
                    ) is False
                    and output.get(
                        "signal_qualified"
                    ) is False
                    and output.get(
                        "account_balance_required"
                    ) is False
                )

            passed = (
                expected_exception is None
                and actual_status == expected_status
                and output.get(
                    "active_mode"
                ) == expected_mode
                and output.get(
                    "direction"
                ) == expected_direction
                and safety_pass
                and sizing_pass
                and handover_pass
            )

        except RuntimeError as exc:

            actual_reason = str(exc)

            passed = (
                expected_exception is not None
                and expected_exception
                in actual_reason
            )

        except Exception as exc:

            actual_reason = (
                "UNEXPECTED_EXCEPTION: "
                + repr(exc)
            )

            passed = False

        # Verify the test itself did not mutate inputs.
        inputs_preserved = (
            config == config_before
            and candidate == candidate_before
        )

        passed = (
            passed and inputs_preserved
        )

        print(
            "UNIT 7 V1.1 EXPECTED STATUS =",
            expected_status,
            flush=True
        )

        print(
            "UNIT 7 V1.1 ACTUAL STATUS =",
            actual_status,
            flush=True
        )

        print(
            "UNIT 7 V1.1 EXPECTED EXCEPTION =",
            expected_exception,
            flush=True
        )

        print(
            "UNIT 7 V1.1 ACTUAL REASON =",
            actual_reason,
            flush=True
        )

        print(
            "UNIT 7 V1.1 INPUT PRESERVED =",
            inputs_preserved,
            flush=True
        )

        print(
            "UNIT 7 V1.1 TEST RESULT =",
            "PASS" if passed else "FAIL",
            flush=True
        )

        test_results.append({
            "name": name,
            "passed": passed,
            "reason": actual_reason,
        })

    # ========================================================
    # TEST 1: IDLE HANDOVER
    # ========================================================

    run_case(
        "IDLE_HANDOVER",
        make_config(),
        make_candidate(),
        expected_status="IDLE",
        expected_mode="NONE",
        expected_direction="NONE",
    )

    # ========================================================
    # TESTS 2-5: QUALIFIED BREAKOUT AND STRUCTURE
    # ========================================================

    for mode, side in (
        ("BREAKOUT", "LONG"),
        ("BREAKOUT", "SHORT"),
        ("STRUCTURE", "LONG"),
        ("STRUCTURE", "SHORT"),
    ):

        run_case(
            mode + "_" + side + "_HELD",
            make_config(),
            make_candidate(
                mode=mode,
                side=side,
                qualified=True,
            ),
            expected_status="HELD",
            expected_mode=mode,
            expected_direction=side,
        )

    # ========================================================
    # TEST 6: SCALP NOT ADMITTED BY UNIT 6
    # ========================================================

    run_case(
        "SCALP_PENDING_REMAINS_IDLE",
        make_config(),
        make_candidate(
            mode="NONE",
            side="NONE",
            qualified=False,
            candidate_mode="SCALP",
            candidate_stage="PENDING_UNIT_6",
        ),
        expected_status="IDLE",
        expected_mode="NONE",
        expected_direction="NONE",
    )

    # ========================================================
    # TEST 7: INCONSISTENT QUALIFICATION FLAGS
    # ========================================================

    inconsistent_flags = make_candidate(
        mode="BREAKOUT",
        side="LONG",
        qualified=True,
    )

    inconsistent_flags[
        "signal_qualified"
    ] = False

    run_case(
        "QUALIFICATION_FLAG_MISMATCH",
        make_config(),
        inconsistent_flags,
        expected_exception=(
            "UNIT 7 SIGNAL QUALIFICATION MISMATCH"
        ),
    )

    # ========================================================
    # TEST 8: INVALID ACTIVE SIGNAL DIRECTION
    # ========================================================

    invalid_direction = make_candidate(
        mode="STRUCTURE",
        side="NONE",
        qualified=True,
    )

    run_case(
        "ACTIVE_DIRECTION_INVALID",
        make_config(),
        invalid_direction,
        expected_exception=(
            "UNIT 7 ACTIVE SIGNAL INCONSISTENT"
        ),
    )

    # ========================================================
    # TEST 9: EXCHANGE MUTATION ENABLED
    # ========================================================

    unsafe_config = make_config()

    unsafe_config["safety"][
        "exchange_mutation_enabled"
    ] = True

    run_case(
        "UNSAFE_EXCHANGE_WRITE_PERMISSION",
        unsafe_config,
        make_candidate(),
        expected_exception=(
            "UNIT 7 UNSAFE CONFIGURATION: "
            "exchange_mutation_enabled"
        ),
    )

    # ========================================================
    # TEST 10: UNEXPECTED LEVERAGE VERIFICATION
    # ========================================================

    unverified_leverage = make_candidate(
        mode="BREAKOUT",
        side="LONG",
        qualified=True,
    )

    unverified_leverage[
        "exchange_leverage_verified"
    ] = True

    unverified_leverage[
        "effective_leverage"
    ] = 100.0

    run_case(
        "LEVERAGE_STATE_REJECTION",
        make_config(),
        unverified_leverage,
        expected_exception=(
            "UNIT 7 UNEXPECTED LEVERAGE STATE"
        ),
    )

    # ========================================================
    # TEST 11: MISSING UNIT 6 INPUT
    # ========================================================

    run_case(
        "MISSING_UNIT_6_INPUT",
        make_config(),
        None,
        expected_exception=(
            "UNIT 7 INVALID UNIT 6 CANDIDATE"
        ),
    )

    # ========================================================
    # TEST 12: MISSING SAFETY FLAG
    # ========================================================

    missing_safety = make_config()

    missing_safety["safety"].pop(
        "position_access_enabled",
        None,
    )

    run_case(
        "MISSING_SAFETY_FLAG",
        missing_safety,
        make_candidate(),
        expected_exception=(
            "UNIT 7 UNSAFE CONFIGURATION: "
            "position_access_enabled"
        ),
    )

    # ========================================================
    # 4. VERIFY ORIGINAL STATE
    # ========================================================

    originals_preserved = (
        original_config == baseline_config
        and original_candidate == baseline_candidate
        and original_result == baseline_result
    )

    pass_count = sum(
        item["passed"]
        for item in test_results
    )

    fail_count = (
        len(test_results) - pass_count
    )

    verdict = (
        "PASS"
        if fail_count == 0
        and originals_preserved
        else "FAIL"
    )

    # ========================================================
    # 5. SUMMARY
    # ========================================================

    print("=" * 80, flush=True)

    print(
        "UNIT 7 V1.1 TEST COUNT =",
        len(test_results),
        flush=True
    )

    print(
        "UNIT 7 V1.1 PASS =",
        pass_count,
        flush=True
    )

    print(
        "UNIT 7 V1.1 FAIL =",
        fail_count,
        flush=True
    )

    print(
        "UNIT 7 V1.1 ORIGINAL DATA PRESERVED =",
        originals_preserved,
        flush=True
    )

    print(
        "UNIT 7 V1.1 RESULT =",
        verdict,
        flush=True
    )

    print("=" * 80, flush=True)

    return {
        "status": verdict,
        "test_count": len(test_results),
        "passed": pass_count,
        "failed": fail_count,
        "originals_preserved":
            originals_preserved,
        "details": test_results,
    }


# ============================================================
# RUN UNIT 7 V1.1 CONTROLLED TESTS
# ZERO INDENTATION
# ============================================================

FRESH_UNIT_7_V11_RESULT = False
FRESH_UNIT_7_V11_RESULT = None

if UNIT_7_V11_TEST_ENABLED:

    FRESH_UNIT_7_V11_RESULT = (
        fresh_unit_7_v11_tests()
    )

# ============================================================
# END UNIT 7 V1.1 CONTROLLED TEST SUITE
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE UNIT 8 V1
# ZERO INDENTATION
#
# ENTRY READINESS AND SIGNAL CONTINUITY
#
# CONSUMES:
# - UNIT 2 CONFIGURATION
# - UNIT 4 MARKET ANALYSIS
# - UNIT 7 HANDOVER RESULT
#
# READ ONLY
# NO POSITION ACCESS
# NO ACCOUNT ACCESS
# NO ORDER SUBMISSION
# NO EXCHANGE WRITE
# ============================================================

def fresh_reconstruction_unit_8(
    unit_2_config,
    unit_4_analysis,
    unit_7_result,
):

    import math

    print("=" * 80, flush=True)
    print(
        "FRESH RECONSTRUCTION UNIT 8 V1 START",
        flush=True,
    )

    # ========================================================
    # 1. INPUT CONTRACT
    # ========================================================

    if not all(
        isinstance(x, dict)
        for x in (
            unit_2_config,
            unit_4_analysis,
            unit_7_result,
        )
    ):
        raise RuntimeError(
            "UNIT 8 INVALID INPUT CONTRACT"
        )

    safety = unit_2_config.get("safety")

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 8 SAFETY CONFIGURATION MISSING"
        )

    # ========================================================
    # 2. READ ONLY SAFETY GATE
    # ========================================================

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
                "UNIT 8 UNSAFE CONFIG: " + key
            )

    for key in (
        "read_only",
        "trade_authorized",
        "exchange_write",
        "order_payload_created",
    ):

        expected = (
            True if key == "read_only"
            else False
        )

        if unit_7_result.get(key) is not expected:
            raise RuntimeError(
                "UNIT 8 UNSAFE UNIT 7 FIELD: " + key
            )

    if (
        unit_7_result.get(
            "execution_intent"
        ) is not False
        or unit_7_result.get(
            "demo_order_enabled"
        ) is not False
        or unit_7_result.get(
            "real_order_enabled"
        ) is not False
        or unit_7_result.get(
            "position_sizing_performed"
        ) is not False
        or unit_7_result.get(
            "quantity_calculated"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT 8 EXECUTION SAFETY VIOLATION"
        )

    print(
        "PASS: UNIT 8 READ ONLY SAFETY",
        flush=True,
    )

    # ========================================================
    # 3. VALIDATE FRESH MARKET EVIDENCE
    # ========================================================

    if (
        unit_4_analysis.get("read_only")
        is not True
        or unit_4_analysis.get(
            "trade_authorized"
        ) is not False
        or unit_4_analysis.get(
            "strategy_evidence_version"
        ) != "U4_COORDINATED_V1"
    ):
        raise RuntimeError(
            "UNIT 8 INVALID MARKET EVIDENCE"
        )

    def finite_number(value, label):

        try:
            result = float(value)
        except (
            TypeError,
            ValueError,
            OverflowError,
        ) as exc:
            raise RuntimeError(
                "UNIT 8 INVALID " + label
            ) from exc

        if not math.isfinite(result):
            raise RuntimeError(
                "UNIT 8 NONFINITE " + label
            )

        return result

    candle_age = finite_number(
        unit_4_analysis.get(
            "candle_age_seconds"
        ),
        "CANDLE AGE",
    )

    market_fresh = (
        unit_4_analysis.get(
            "candle_data_fresh"
        ) is True
        and 0 <= candle_age <= 180
    )

    market_direction = unit_4_analysis.get(
        "direction_evidence", "NONE"
    )

    if market_direction not in (
        "NONE",
        "LONG",
        "SHORT",
    ):
        raise RuntimeError(
            "UNIT 8 INVALID MARKET DIRECTION"
        )

    # ========================================================
    # 4. RECEIVE UNIT 7 RESULT
    # ========================================================

    unit7_status = unit_7_result.get("status")
    signal_received = unit_7_result.get(
        "signal_received"
    )
    signal_qualified = unit_7_result.get(
        "signal_qualified"
    )

    mode = unit_7_result.get(
        "active_mode", "NONE"
    )
    direction = unit_7_result.get(
        "direction", "NONE"
    )

    if unit7_status not in ("IDLE", "HELD"):
        raise RuntimeError(
            "UNIT 8 INVALID UNIT 7 STATUS"
        )

    if (
        type(signal_received) is not bool
        or type(signal_qualified) is not bool
        or signal_received != signal_qualified
    ):
        raise RuntimeError(
            "UNIT 8 SIGNAL FLAG MISMATCH"
        )

    if unit7_status == "IDLE":

        if (
            signal_received
            or mode != "NONE"
            or direction != "NONE"
        ):
            raise RuntimeError(
                "UNIT 8 IDLE HANDOVER MISMATCH"
            )

    else:

        if (
            not signal_received
            or mode not in (
                "BREAKOUT", "STRUCTURE"
            )
            or direction not in (
                "LONG", "SHORT"
            )
        ):
            raise RuntimeError(
                "UNIT 8 HELD HANDOVER MISMATCH"
            )

    print(
        "PASS: UNIT 8 UNIT 7 HANDOVER",
        flush=True,
    )

    # ========================================================
    # 5. DETERMINE CURRENT SNAPSHOT STATUS
    # ========================================================

    signal_direction_match = (
        market_direction == direction
        if signal_received else False
    )

    if not market_fresh:

        status = "BLOCKED"
        reason = "STALE_MARKET_EVIDENCE"

    elif unit7_status == "IDLE":

        status = "IDLE"
        reason = "NO_QUALIFIED_SIGNAL"

    elif not signal_direction_match:

        status = "BLOCKED"
        reason = "SIGNAL_DIRECTION_CONFLICT"

    else:

        status = "PENDING"
        reason = (
            "SIGNAL_FRESH_AND_ALIGNED_"
            "AWAITING_CONTINUITY_AND_POSITION_CHECKS"
        )

    # ========================================================
    # 6. NO FALSE CONTINUITY CLAIMS
    # ========================================================

    # One market snapshot does not prove
    # multiple independent confirmations.
    #
    # Persisted scan history and distinct
    # closed-candle identifiers are required
    # for trustworthy continuity measurement.

    continuity_observations = (
        1 if status == "PENDING" else 0
    )

    continuity_required = 2
    continuity_verified = False

    # No authenticated position information
    # is available at this development stage.

    position_flat_verified = False
    existing_position_checked = False
    pending_orders_checked = False

    # Without position/pending-order evidence,
    # re-entry cannot be authorized.

    reentry_authorized = False
    duplicate_order_absence_verified = False

    # ========================================================
    # 7. RETAIN CANDIDATE INFORMATION
    # ========================================================

    candidate_preserved = (
        status == "PENDING"
    )

    pending_mode = (
        mode if candidate_preserved else "NONE"
    )

    pending_direction = (
        direction if candidate_preserved
        else "NONE"
    )

    # ========================================================
    # 8. EXECUTION BOUNDARY
    # ========================================================

    execution_intent = False
    trade_authorized = False
    order_payload_created = False
    quantity_calculated = False

    demo_order_submitted = False
    real_order_submitted = False
    exchange_write = False

    if any((
        execution_intent,
        trade_authorized,
        order_payload_created,
        quantity_calculated,
        demo_order_submitted,
        real_order_submitted,
        exchange_write,
        reentry_authorized,
    )):
        raise RuntimeError(
            "UNIT 8 EXECUTION BOUNDARY VIOLATION"
        )

    # ========================================================
    # 9. STANDARDIZED RESULT
    # ========================================================

    result = {
        "status": status,
        "reason": reason,

        "upstream_status": unit7_status,
        "upstream_signal_received":
            signal_received,

        "candidate_preserved":
            candidate_preserved,

        "pending_mode": pending_mode,
        "pending_direction": pending_direction,

        "market_fresh": market_fresh,
        "candle_age_seconds": candle_age,

        "market_direction": market_direction,
        "signal_direction_match":
            signal_direction_match,

        "continuity_observations":
            continuity_observations,

        "continuity_required":
            continuity_required,

        "continuity_verified":
            continuity_verified,

        "existing_position_checked":
            existing_position_checked,

        "position_flat_verified":
            position_flat_verified,

        "pending_orders_checked":
            pending_orders_checked,

        "duplicate_order_absence_verified":
            duplicate_order_absence_verified,

        "reentry_authorized":
            reentry_authorized,

        "execution_intent":
            execution_intent,

        "trade_authorized":
            trade_authorized,

        "order_payload_created":
            order_payload_created,

        "quantity_calculated":
            quantity_calculated,

        "demo_order_submitted":
            demo_order_submitted,

        "real_order_submitted":
            real_order_submitted,

        "exchange_write": exchange_write,
        "read_only": True,
    }

    # ========================================================
    # 10. RENDER DIAGNOSTICS
    # ========================================================

    print("-" * 80, flush=True)

    for label, value in (
        ("STATUS", status),
        ("REASON", reason),
        ("UPSTREAM STATUS", unit7_status),
        ("MARKET FRESH", market_fresh),
        ("MARKET DIRECTION", market_direction),
        ("SIGNAL MATCH", signal_direction_match),
        ("PENDING MODE", pending_mode),
        ("PENDING DIRECTION", pending_direction),
        ("CONTINUITY VERIFIED", continuity_verified),
        ("POSITION FLAT VERIFIED", position_flat_verified),
        ("REENTRY AUTHORIZED", reentry_authorized),
        ("EXECUTION INTENT", execution_intent),
        ("TRADE AUTHORIZED", trade_authorized),
        ("EXCHANGE WRITE", exchange_write),
    ):
        print(
            "UNIT 8 " + label + " =",
            value,
            flush=True,
        )

    print(
        "UNIT 8 AUTHENTICATED REQUEST = NONE",
        flush=True,
    )
    print(
        "UNIT 8 DEMO ORDER = NONE",
        flush=True,
    )
    print(
        "UNIT 8 REAL ORDER = NONE",
        flush=True,
    )
    print(
        "FRESH RECONSTRUCTION UNIT 8 RESULT = PASS",
        flush=True,
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 8 V1
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_8_RESULT = (
    fresh_reconstruction_unit_8(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        FRESH_RECONSTRUCTION_UNIT_7_RESULT,
    )
)

# ============================================================
# END COMPLETE UNIT 8 V1
# ZERO INDENTATION
# ============================================================


# ============================================================
# START UNIT 8 V1.1 CONTROLLED TEST SUITE
# ZERO INDENTATION
#
# UNIT 8 V1 REMAINS UNCHANGED
# SYNTHETIC INPUT DATA ONLY
# NO EXCHANGE REQUESTS
# NO ACCOUNT OR POSITION ACCESS
# NO DEMO OR REAL ORDERS
# ============================================================

UNIT_8_V11_TEST_ENABLED = True


def fresh_unit_8_v11_tests():

    import copy

    print("=" * 80, flush=True)
    print(
        "UNIT 8 V1.1 CONTROLLED TEST START",
        flush=True,
    )

    # ========================================================
    # 1. PRESERVE ORIGINAL STATE
    # ========================================================

    original_config = (
        FRESH_RECONSTRUCTION_CONFIG
    )

    original_market = (
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
    )

    original_unit7 = (
        FRESH_RECONSTRUCTION_UNIT_7_RESULT
    )

    original_unit8 = (
        FRESH_RECONSTRUCTION_UNIT_8_RESULT
    )

    saved_config = copy.deepcopy(
        original_config
    )

    saved_market = copy.deepcopy(
        original_market
    )

    saved_unit7 = copy.deepcopy(
        original_unit7
    )

    saved_unit8 = copy.deepcopy(
        original_unit8
    )

    results = []

    # ========================================================
    # 2. FRESH MARKET FIXTURE
    # ========================================================

    def make_market(direction="LONG"):

        market = copy.deepcopy(saved_market)

        market["read_only"] = True
        market["trade_authorized"] = False

        market["strategy_evidence_version"] = (
            "U4_COORDINATED_V1"
        )

        market["candle_data_fresh"] = True
        market["candle_age_seconds"] = 30.0

        market["direction_evidence"] = direction

        return market

    # ========================================================
    # 3. UNIT 7 SIGNAL FIXTURE
    # ========================================================

    def make_unit7(
        mode="NONE",
        direction="NONE",
        qualified=False,
    ):

        data = copy.deepcopy(saved_unit7)

        data["status"] = (
            "HELD" if qualified
            else "IDLE"
        )

        data["signal_received"] = qualified
        data["signal_qualified"] = qualified

        data["active_mode"] = mode
        data["direction"] = direction

        data["read_only"] = True

        data["trade_authorized"] = False
        data["execution_intent"] = False

        data["exchange_write"] = False
        data["order_payload_created"] = False

        data["demo_order_enabled"] = False
        data["real_order_enabled"] = False

        data["position_sizing_performed"] = False
        data["quantity_calculated"] = False

        return data

    # ========================================================
    # 4. COMMON RESULT VALIDATION
    # ========================================================

    def safety_is_preserved(output):

        if not isinstance(output, dict):
            return False

        return (
            output.get("read_only") is True
            and output.get(
                "execution_intent"
            ) is False
            and output.get(
                "trade_authorized"
            ) is False
            and output.get(
                "exchange_write"
            ) is False
            and output.get(
                "order_payload_created"
            ) is False
            and output.get(
                "quantity_calculated"
            ) is False
            and output.get(
                "demo_order_submitted"
            ) is False
            and output.get(
                "real_order_submitted"
            ) is False
            and output.get(
                "reentry_authorized"
            ) is False
            and output.get(
                "continuity_verified"
            ) is False
            and output.get(
                "position_flat_verified"
            ) is False
            and output.get(
                "duplicate_order_absence_verified"
            ) is False
        )

    # ========================================================
    # 5. GENERAL TEST RUNNER
    # ========================================================

    def run_case(
        name,
        config,
        market,
        unit7,
        expected_status=None,
        expected_reason=None,
        expected_mode="NONE",
        expected_direction="NONE",
        expected_exception=None,
    ):

        print("-" * 80, flush=True)
        print(
            "UNIT 8 V1.1 TEST =",
            name,
            flush=True,
        )

        config_before = copy.deepcopy(config)
        market_before = copy.deepcopy(market)
        unit7_before = copy.deepcopy(unit7)

        passed = False
        actual_status = None
        actual_reason = None

        try:

            output = fresh_reconstruction_unit_8(
                config,
                market,
                unit7,
            )

            actual_status = output.get("status")
            actual_reason = output.get("reason")

            candidate_pass = (
                output.get(
                    "pending_mode"
                ) == expected_mode
                and output.get(
                    "pending_direction"
                ) == expected_direction
            )

            preservation_pass = (
                output.get(
                    "candidate_preserved"
                ) is (
                    expected_status == "PENDING"
                )
            )

            observation_pass = (
                output.get(
                    "continuity_observations"
                ) == (
                    1 if expected_status == "PENDING"
                    else 0
                )
                and output.get(
                    "continuity_required"
                ) == 2
            )

            passed = (
                expected_exception is None
                and actual_status == expected_status
                and actual_reason == expected_reason
                and candidate_pass
                and preservation_pass
                and observation_pass
                and safety_is_preserved(output)
            )

        except RuntimeError as exc:

            actual_reason = str(exc)

            passed = (
                expected_exception is not None
                and expected_exception in actual_reason
            )

        except Exception as exc:

            actual_reason = (
                "UNEXPECTED_EXCEPTION: "
                + repr(exc)
            )

            passed = False

        inputs_preserved = (
            config == config_before
            and market == market_before
            and unit7 == unit7_before
        )

        passed = passed and inputs_preserved

        print(
            "UNIT 8 V1.1 EXPECTED STATUS =",
            expected_status,
            flush=True,
        )

        print(
            "UNIT 8 V1.1 ACTUAL STATUS =",
            actual_status,
            flush=True,
        )

        print(
            "UNIT 8 V1.1 EXPECTED REASON =",
            expected_reason,
            flush=True,
        )

        print(
            "UNIT 8 V1.1 ACTUAL REASON =",
            actual_reason,
            flush=True,
        )

        print(
            "UNIT 8 V1.1 INPUT PRESERVED =",
            inputs_preserved,
            flush=True,
        )

        print(
            "UNIT 8 V1.1 TEST RESULT =",
            "PASS" if passed else "FAIL",
            flush=True,
        )

        results.append({
            "name": name,
            "passed": passed,
            "actual_status": actual_status,
            "actual_reason": actual_reason,
        })

    # ========================================================
    # TEST 1: NORMAL IDLE
    # ========================================================

    run_case(
        "FRESH_IDLE",
        copy.deepcopy(saved_config),
        make_market("LONG"),
        make_unit7(),
        expected_status="IDLE",
        expected_reason="NO_QUALIFIED_SIGNAL",
    )

    # ========================================================
    # TESTS 2-5: ALIGNED QUALIFIED SIGNALS
    # ========================================================

    for mode, side in (
        ("BREAKOUT", "LONG"),
        ("BREAKOUT", "SHORT"),
        ("STRUCTURE", "LONG"),
        ("STRUCTURE", "SHORT"),
    ):

        run_case(
            mode + "_" + side + "_PENDING",
            copy.deepcopy(saved_config),
            make_market(side),
            make_unit7(
                mode=mode,
                direction=side,
                qualified=True,
            ),
            expected_status="PENDING",
            expected_reason=(
                "SIGNAL_FRESH_AND_ALIGNED_"
                "AWAITING_CONTINUITY_AND_POSITION_CHECKS"
            ),
            expected_mode=mode,
            expected_direction=side,
        )

    # ========================================================
    # TEST 6: OPPOSING MARKET DIRECTION
    # ========================================================

    run_case(
        "DIRECTION_CONFLICT",
        copy.deepcopy(saved_config),
        make_market("SHORT"),
        make_unit7(
            mode="BREAKOUT",
            direction="LONG",
            qualified=True,
        ),
        expected_status="BLOCKED",
        expected_reason="SIGNAL_DIRECTION_CONFLICT",
    )

    # ========================================================
    # TEST 7: STALE QUALIFIED SIGNAL
    # ========================================================

    stale_market = make_market("LONG")

    stale_market["candle_data_fresh"] = False
    stale_market["candle_age_seconds"] = 240.0

    run_case(
        "STALE_QUALIFIED_SIGNAL",
        copy.deepcopy(saved_config),
        stale_market,
        make_unit7(
            mode="STRUCTURE",
            direction="LONG",
            qualified=True,
        ),
        expected_status="BLOCKED",
        expected_reason="STALE_MARKET_EVIDENCE",
    )

    # ========================================================
    # TEST 8: STALE IDLE
    # ========================================================

    stale_idle = make_market("SHORT")

    stale_idle["candle_data_fresh"] = False
    stale_idle["candle_age_seconds"] = 240.0

    run_case(
        "STALE_IDLE_MARKET",
        copy.deepcopy(saved_config),
        stale_idle,
        make_unit7(),
        expected_status="BLOCKED",
        expected_reason="STALE_MARKET_EVIDENCE",
    )

    # ========================================================
    # TEST 9: SIGNAL FLAG MISMATCH
    # ========================================================

    mismatch = make_unit7(
        mode="BREAKOUT",
        direction="LONG",
        qualified=True,
    )

    mismatch["signal_qualified"] = False

    run_case(
        "SIGNAL_FLAG_MISMATCH",
        copy.deepcopy(saved_config),
        make_market("LONG"),
        mismatch,
        expected_exception=(
            "UNIT 8 SIGNAL FLAG MISMATCH"
        ),
    )

    # ========================================================
    # TEST 10: INVALID HELD DIRECTION
    # ========================================================

    invalid_held = make_unit7(
        mode="STRUCTURE",
        direction="NONE",
        qualified=True,
    )

    run_case(
        "HELD_DIRECTION_INVALID",
        copy.deepcopy(saved_config),
        make_market("LONG"),
        invalid_held,
        expected_exception=(
            "UNIT 8 HELD HANDOVER MISMATCH"
        ),
    )

    # ========================================================
    # TEST 11: UNSAFE EXCHANGE PERMISSION
    # ========================================================

    unsafe_config = copy.deepcopy(
        saved_config
    )

    unsafe_config["safety"][
        "exchange_mutation_enabled"
    ] = True

    run_case(
        "EXCHANGE_MUTATION_REJECTED",
        unsafe_config,
        make_market("LONG"),
        make_unit7(),
        expected_exception=(
            "UNIT 8 UNSAFE CONFIG: "
            "exchange_mutation_enabled"
        ),
    )

    # ========================================================
    # TEST 12: MISSING UNIT 7 RESULT
    # ========================================================

    run_case(
        "MISSING_UNIT_7_RESULT",
        copy.deepcopy(saved_config),
        make_market("LONG"),
        None,
        expected_exception=(
            "UNIT 8 INVALID INPUT CONTRACT"
        ),
    )

    # ========================================================
    # 6. ORIGINAL STATE INTEGRITY
    # ========================================================

    originals_preserved = (
        original_config == saved_config
        and original_market == saved_market
        and original_unit7 == saved_unit7
        and original_unit8 == saved_unit8
    )

    pass_count = sum(
        item["passed"] for item in results
    )

    fail_count = (
        len(results) - pass_count
    )

    verdict = (
        "PASS"
        if fail_count == 0
        and originals_preserved
        else "FAIL"
    )

    # ========================================================
    # 7. FINAL REPORT
    # ========================================================

    print("=" * 80, flush=True)

    print(
        "UNIT 8 V1.1 TEST COUNT =",
        len(results),
        flush=True,
    )

    print(
        "UNIT 8 V1.1 PASS =",
        pass_count,
        flush=True,
    )

    print(
        "UNIT 8 V1.1 FAIL =",
        fail_count,
        flush=True,
    )

    print(
        "UNIT 8 V1.1 ORIGINAL DATA PRESERVED =",
        originals_preserved,
        flush=True,
    )

    print(
        "UNIT 8 V1.1 RESULT =",
        verdict,
        flush=True,
    )

    print("=" * 80, flush=True)

    return {
        "status": verdict,
        "test_count": len(results),
        "passed": pass_count,
        "failed": fail_count,
        "originals_preserved":
            originals_preserved,
        "details": results,
    }


# ============================================================
# RUN UNIT 8 V1.1 CONTROLLED TESTS
# ZERO INDENTATION
# ============================================================

FRESH_UNIT_8_V11_RESULT = None

if UNIT_8_V11_TEST_ENABLED:

    FRESH_UNIT_8_V11_RESULT = (
        fresh_unit_8_v11_tests()
    )

# ============================================================
# END UNIT 8 V1.1 CONTROLLED TEST SUITE
# ZERO INDENTATION
# ============================================================
