
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
