
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
# START UNIT 2
# ZERO INDENTATION
# WEEX CONFIGURATION AND SAFETY CONTRACT
# ORIGINAL 22525-LINE MODEL BASELINE
# ============================================================


def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 2 START")

    # ========================================================
    # 1. UNIT 1 HANDOVER
    # ========================================================

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
        raise RuntimeError(
            "UNIT 2 BLOCKED: UNIT 1 NOT READY"
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
    # 3. ORIGINAL SAFETY CONTRACT
    #
    # This is Unit 2's read-only configuration.
    # Later execution units retain their existing
    # authenticated WEEX demo execution mechanism.
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
    # 4. ORIGINAL STRATEGY CONFIGURATION
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

        # TAKE-PROFIT ALLOCATION
        "tp1_allocation_percent": 10.0,
        "tp2_allocation_percent": 20.0,
        "tp3_allocation_percent": 70.0,

        # NET ROI TARGETS
        "tp1_net_roi_floor_percent": 5.0,
        "tp2_net_roi_floor_percent": 10.0,
        "tp1_tp2_min_roi_separation_percent": 5.0,

        # TP3 DYNAMIC TRAILING
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
    # 6. ORIGINAL CONFIGURATION OUTPUT
    # ========================================================

    config = {
        "exchange": exchange,
        "execution_environment": execution_environment,
        "safety": safety,
        "strategy": strategy,
        "market_precision": market_precision,
    }

    # ========================================================
    # 7. VALIDATION
    # ========================================================

    errors = []

    def check(condition, label):
        if condition:
            print("PASS: UNIT 2 " + label, flush=True)
        else:
            errors.append(label)
            print("FAIL: UNIT 2 " + label, flush=True)

    check(
        exchange["name"] == "WEEX"
        and exchange["api_version"] == "V3"
        and exchange["contract_base_url"]
        == "https://api-contract.weex.com",
        "WEEX V3 CONFIGURATION"
    )

    check(
        exchange["market_symbol"] == "BTCUSDT"
        and exchange["demo_order_symbol"] == "BTCSUSDT",
        "MARKET AND DEMO SYMBOLS"
    )

    check(
        execution_environment == "DEMO",
        "DEMO EXECUTION ENVIRONMENT"
    )

    check(
        strategy["leverage_target"] > 0,
        "LEVERAGE TARGET"
    )

    check(
        0 < strategy["initial_margin_percent"] <= 5.0
        and strategy["initial_fixed_usdt"] > 0,
        "INITIAL ENTRY CONFIGURATION"
    )

    check(
        strategy["max_backups"] == 5
        and strategy["backup_multipliers"]
        == (1.0, 1.5, 2.0, 2.5, 3.0)
        and 0 < strategy["backup_margin_percent"] <= 5.0
        and strategy["backup_buffer_percent"] > 0,
        "FIVE BACKUP CONFIGURATION"
    )

    check(
        strategy["progressive_backup_funding"] is True
        and strategy["full_ladder_reservation_required"]
        is False,
        "PROGRESSIVE BACKUP FUNDING"
    )

    check(
        0 < strategy["exposure_cap_percent"] <= 35.0,
        "MAXIMUM EXPOSURE 35%"
    )

    full_ladder_multiplier = (
        1.0 + sum(strategy["backup_multipliers"])
    )

    full_ladder_margin = (
        strategy["initial_fixed_usdt"]
        * full_ladder_multiplier
    )

    tp_total = sum(
        strategy[key]
        for key in (
            "tp1_allocation_percent",
            "tp2_allocation_percent",
            "tp3_allocation_percent",
        )
    )

    check(
        abs(tp_total - 100.0) < 0.000001
        and all(
            strategy[key] > 0
            for key in (
                "tp1_allocation_percent",
                "tp2_allocation_percent",
                "tp3_allocation_percent",
            )
        ),
        "TP ALLOCATION 10/20/70"
    )

    check(
        strategy["tp1_net_roi_floor_percent"] >= 5.0
        and strategy["tp2_net_roi_floor_percent"] >= 10.0
        and strategy["tp2_net_roi_floor_percent"]
        > strategy["tp1_net_roi_floor_percent"]
        and strategy[
            "tp1_tp2_min_roi_separation_percent"
        ] > 0,
        "TP NET ROI TARGETS"
    )

    check(
        0 < strategy["tp3_trailing_min_percent"]
        <= strategy["tp3_trailing_reference_percent"]
        <= strategy["tp3_trailing_max_percent"],
        "TP3 DYNAMIC TRAILING RANGE"
    )

    check(
        all(
            strategy[key] > 0
            for key in (
                "signal_expiry_seconds",
                "loss_cooldown_seconds",
                "mode_confirmations_required",
            )
        ),
        "SIGNAL CONTROL"
    )

    check(
        all(
            strategy[key] is True
            for key in (
                "one_direction_only",
                "anti_duplicate_orders",
                "active_trade_mode_lock",
                "exclusive_mode",
            )
        ),
        "POSITION PROTECTION"
    )

    check(
        all(
            market_precision[key] > 0
            for key in (
                "quantity_step",
                "minimum_quantity",
                "price_step",
            )
        ),
        "MARKET PRECISION"
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

    check(
        safety["public_market_data_read_enabled"]
        is True
        and all(
            safety[key] is False
            for key in forbidden_capabilities
        ),
        "ORIGINAL UNIT 2 SAFETY CONTRACT"
    )

    # ========================================================
    # 8. CONFIGURATION RESULTS
    # ========================================================

    if errors:
        raise RuntimeError(
            "UNIT 2 VALIDATION FAILED: "
            + ", ".join(errors)
        )

    print("-" * 80, flush=True)

    print(
        "UNIT 2 INITIAL MARGIN USDT =",
        strategy["initial_fixed_usdt"],
        flush=True
    )

    print(
        "UNIT 2 MAX BACKUPS =",
        strategy["max_backups"],
        flush=True
    )

    print(
        "UNIT 2 BACKUP MULTIPLIERS =",
        strategy["backup_multipliers"],
        flush=True
    )

    print(
        "UNIT 2 FULL LADDER MARGIN USDT =",
        full_ladder_margin,
        flush=True
    )

    print(
        "UNIT 2 EXPOSURE CAP =",
        strategy["exposure_cap_percent"],
        flush=True
    )

    print(
        "UNIT 2 TP ALLOCATION = 10/20/70",
        flush=True
    )

    print(
        "UNIT 2 REAL ORDER SUBMISSION = DISABLED",
        flush=True
    )

    print(
        "UNIT 2 EXCHANGE WRITE = NONE",
        flush=True
    )

    log("FRESH RECONSTRUCTION UNIT 2 RESULT = PASS")

    print("=" * 80, flush=True)

    return config


# ============================================================
# UNIT 2 EXECUTION AND UNIT 3 HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# END UNIT 2
# ZERO INDENTATION
# UNIT 3 CONTINUES BELOW
# ============================================================
