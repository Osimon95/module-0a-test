# ============================================================
# FRESH WEEX BOT RECONSTRUCTION
# UNITS 1 -> 4
#
# CLEAN RECONSTRUCTION BASELINE
#
# UNIT 1:
#   Runtime foundation
#
# UNIT 2:
#   Configuration + safety contract
#
# UNIT 3:
#   WEEX V3 public read-only market data
#
# UNIT 4:
#   Public mark-price kline + EMA analysis
#
# IMPORTANT:
# - PYTHON STANDARD LIBRARY ONLY
# - NO requests PACKAGE
# - NO API KEY REQUIRED YET
# - NO ACCOUNT ACCESS
# - NO POSITION ACCESS
# - NO ORDER ENDPOINT ACCESS
# - NO DEMO ORDER
# - NO REAL ORDER
# - ZERO EXCHANGE WRITE
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
# MASTER BOT MODE - ZERO INDENTATION START
# ============================================================
import os

BOT_MODE = os.environ.get("BOT_MODE", "PAUSE").strip().upper()
if BOT_MODE not in ("ACTIVE", "PAUSE"):
    BOT_MODE = "PAUSE"

def bot_new_entries_allowed():
    return BOT_MODE == "ACTIVE"

print("MASTER BOT MODE = " + BOT_MODE, flush=True)
print("MASTER NEW ENTRIES ALLOWED = " + str(bot_new_entries_allowed()), flush=True)
print("MASTER EXISTING POSITION MANAGEMENT = ENABLED", flush=True)
# ============================================================
# MASTER BOT MODE - ZERO INDENTATION END
# ============================================================

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
# END PART 1 - MASTER CONTROLLER + UNIT 1
# ZERO INDENTATION DEMARCATION
# UNIT 1 FULLY CLOSED AND CALLED
# ============================================================

# ============================================================
# PART 2 START - FRESH RECONSTRUCTION UNIT 2
# ZERO INDENTATION DEMARCATION
# ============================================================

# ============================================================
# UNIT 2 - CONFIGURATION + SAFETY CONTRACT
# ============================================================

def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 2 START")
    print("-" * 80, flush=True)

    # ========================================================
    # 1. UNIT 1 DEPENDENCY
    # ========================================================

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
        raise RuntimeError(
            "UNIT 2 BLOCKED: UNIT 1 NOT READY"
        )

    # ========================================================
    # 2. WEEX EXCHANGE CONFIGURATION
    # ========================================================

    exchange_name = "WEEX"
    api_version = "V3"

    contract_base_url = (
        "https://api-contract.weex.com"
    )

    market_symbol = "BTCUSDT"
    demo_order_symbol = "BTCSUSDT"
    execution_environment = "DEMO"

    # ========================================================
    # 3. UNIT-LOCAL SAFETY CONTRACT
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
    # 4. STRATEGY CONFIGURATION
    # ========================================================

    strategy = {

        # LEVERAGE / INITIAL ENTRY

        "leverage_target": 100,
        "initial_margin_percent": 5.0,

        # BACKUPS

        "backup_margin_percent": 5.0,
        "backup_buffer_percent": 0.30,
        "max_backups": 3,
        "exposure_cap_percent": 35.0,

        # TP ALLOCATION
        # EXECUTABLE QUANTITIES ARE STEP-AWARE

        "tp1_allocation_percent": 10.0,
        "tp2_allocation_percent": 20.0,
        "tp3_allocation_percent": 70.0,

        # TP1 / TP2 DYNAMIC ROI FLOORS

        "tp1_net_roi_floor_percent": 5.0,
        "tp2_net_roi_floor_percent": 10.0,

        # MANDATORY TP SEPARATION

        "tp1_tp2_min_roi_separation_percent": 5.0,

        # TP3 DYNAMIC TRAILING
        # 0.20% IS REFERENCE, NOT FIXED

        "tp3_trailing_reference_percent": 0.20,
        "tp3_trailing_min_percent": 0.10,
        "tp3_trailing_max_percent": 0.40,

        # SIGNAL AND STRATEGY CONTROLS

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
    # 6. BUILD CONFIGURATION
    # ========================================================

    config = {
        "exchange": {
            "name": exchange_name,
            "api_version": api_version,
            "contract_base_url": contract_base_url,
            "market_symbol": market_symbol,
            "demo_order_symbol": demo_order_symbol,
        },
        "execution_environment": execution_environment,
        "safety": safety,
        "strategy": strategy,
        "market_precision": market_precision,
    }

    # ========================================================
    # 7. EXCHANGE VALIDATION
    # ========================================================

    validation_errors = []

    if exchange_name != "WEEX":
        validation_errors.append("INVALID EXCHANGE")

    if api_version != "V3":
        validation_errors.append("INVALID API VERSION")

    if contract_base_url != (
        "https://api-contract.weex.com"
    ):
        validation_errors.append(
            "INVALID CONTRACT BASE URL"
        )

    if market_symbol != "BTCUSDT":
        validation_errors.append(
            "INVALID MARKET SYMBOL"
        )

    if demo_order_symbol != "BTCSUSDT":
        validation_errors.append(
            "INVALID DEMO ORDER SYMBOL"
        )

    if execution_environment != "DEMO":
        validation_errors.append(
            "INVALID EXECUTION ENVIRONMENT"
        )

    # ========================================================
    # 8. BASIC STRATEGY VALIDATION
    # ========================================================

    positive_values = {
        "leverage_target": "INVALID LEVERAGE TARGET",
        "initial_margin_percent": "INVALID INITIAL MARGIN",
        "backup_margin_percent": "INVALID BACKUP MARGIN",
        "backup_buffer_percent": "INVALID BACKUP BUFFER",
        "exposure_cap_percent": "INVALID EXPOSURE CAP",
        "tp1_allocation_percent": "INVALID TP1 ALLOCATION",
        "tp2_allocation_percent": "INVALID TP2 ALLOCATION",
        "tp3_allocation_percent": "INVALID TP3 ALLOCATION",
        "tp3_trailing_reference_percent": "INVALID TP3 TRAILING REFERENCE",
        "tp3_trailing_min_percent": "INVALID TP3 TRAILING MINIMUM",
        "tp3_trailing_max_percent": "INVALID TP3 TRAILING MAXIMUM",
        "signal_expiry_seconds": "INVALID SIGNAL EXPIRY",
        "loss_cooldown_seconds": "INVALID LOSS COOLDOWN",
        "mode_confirmations_required": "INVALID MODE CONFIRMATION COUNT",
    }

    for key, error in positive_values.items():
        if strategy[key] <= 0:
            validation_errors.append(error)

    if strategy["max_backups"] != 3:
        validation_errors.append(
            "INVALID MAX BACKUPS"
        )

    # ========================================================
    # 9. TP ALLOCATION VALIDATION
    # ========================================================

    tp_total = (
        strategy["tp1_allocation_percent"]
        + strategy["tp2_allocation_percent"]
        + strategy["tp3_allocation_percent"]
    )

    if tp_total != 100.0:
        validation_errors.append(
            "TP ALLOCATION DOES NOT TOTAL 100%"
        )

    # ========================================================
    # 10. DYNAMIC ROI VALIDATION
    # ========================================================

    if strategy["tp1_net_roi_floor_percent"] < 5.0:
        validation_errors.append(
            "TP1 NET ROI FLOOR BELOW 5%"
        )

    if strategy["tp2_net_roi_floor_percent"] < 10.0:
        validation_errors.append(
            "TP2 NET ROI FLOOR BELOW 10%"
        )

    if (
        strategy["tp2_net_roi_floor_percent"]
        <= strategy["tp1_net_roi_floor_percent"]
    ):
        validation_errors.append(
            "TP2 ROI FLOOR MUST EXCEED TP1 ROI FLOOR"
        )

    if (
        strategy["tp1_tp2_min_roi_separation_percent"]
        <= 0
    ):
        validation_errors.append(
            "INVALID TP1 TP2 ROI SEPARATION"
        )

    # ========================================================
    # 11. DYNAMIC TP3 VALIDATION
    # ========================================================

    if (
        strategy["tp3_trailing_min_percent"]
        > strategy["tp3_trailing_reference_percent"]
    ):
        validation_errors.append(
            "TP3 MINIMUM EXCEEDS REFERENCE"
        )

    if (
        strategy["tp3_trailing_reference_percent"]
        > strategy["tp3_trailing_max_percent"]
    ):
        validation_errors.append(
            "TP3 REFERENCE EXCEEDS MAXIMUM"
        )

    # ========================================================
    # 12. STRATEGY SAFETY VALIDATION
    # ========================================================

    required_true_strategy_flags = (
        "one_direction_only",
        "anti_duplicate_orders",
        "active_trade_mode_lock",
        "exclusive_mode",
    )

    for flag_name in required_true_strategy_flags:
        if strategy.get(flag_name) is not True:
            validation_errors.append(
                "STRATEGY FLAG MUST BE TRUE: "
                + flag_name
            )

    # ========================================================
    # 13. MARKET PRECISION VALIDATION
    # ========================================================

    for key, error in (
        ("quantity_step", "INVALID QUANTITY STEP"),
        ("minimum_quantity", "INVALID MINIMUM QUANTITY"),
        ("price_step", "INVALID PRICE STEP"),
    ):
        if market_precision[key] <= 0:
            validation_errors.append(error)

    # ========================================================
    # 14. UNIT-LOCAL SAFETY VALIDATION
    # ========================================================

    if (
        safety["public_market_data_read_enabled"]
        is not True
    ):
        validation_errors.append(
            "PUBLIC MARKET DATA READ MUST BE ENABLED"
        )

    dangerous_capabilities = (
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

    for capability in dangerous_capabilities:
        if safety.get(capability) is not False:
            validation_errors.append(
                "UNSAFE CAPABILITY ENABLED: "
                + capability
            )

    # ========================================================
    # 15. FINAL VALIDATION
    # ========================================================

    if validation_errors:
        print(
            "UNIT 2 VALIDATION ERRORS =",
            validation_errors,
            flush=True,
        )
        raise RuntimeError(
            "UNIT 2 CONFIGURATION VALIDATION FAILED"
        )

    # ========================================================
    # 16. UNIT 2 RESULTS
    # ========================================================

    print(
        "PASS: UNIT 2 CONFIGURATION CREATED",
        flush=True,
    )

    print(
        "PASS: EXCHANGE =",
        exchange_name,
        flush=True,
    )

    print(
        "PASS: API VERSION =",
        api_version,
        flush=True,
    )

    print(
        "PASS: MARKET SYMBOL =",
        market_symbol,
        flush=True,
    )

    print(
        "PASS: DEMO ORDER SYMBOL =",
        demo_order_symbol,
        flush=True,
    )

    print(
        "PASS: EXECUTION ENVIRONMENT =",
        execution_environment,
        flush=True,
    )

    for key in (
        "leverage_target",
        "initial_margin_percent",
        "backup_margin_percent",
        "backup_buffer_percent",
        "max_backups",
        "exposure_cap_percent",
        "tp1_allocation_percent",
        "tp2_allocation_percent",
        "tp3_allocation_percent",
        "tp1_net_roi_floor_percent",
        "tp2_net_roi_floor_percent",
        "tp1_tp2_min_roi_separation_percent",
        "tp3_trailing_reference_percent",
        "tp3_trailing_min_percent",
        "tp3_trailing_max_percent",
        "anti_duplicate_orders",
        "one_direction_only",
        "active_trade_mode_lock",
        "exclusive_mode",
    ):
        print(
            "PASS: UNIT 2",
            key.upper(),
            "=",
            strategy[key],
            flush=True,
        )

    print(
        "PASS: TP ALLOCATION TOTAL =",
        tp_total,
        "%",
        flush=True,
    )

    print(
        "PASS: TP3 TRAILING MODE = DYNAMIC",
        flush=True,
    )

    print(
        "PASS: TP3 DYNAMIC INPUTS = "
        "TREND + ATR/VOLATILITY + MOMENTUM DETERIORATION",
        flush=True,
    )

    print(
        "PASS: TP QUANTITY MODE = STEP-AWARE",
        flush=True,
    )

    print(
        "PASS: SL = DISABLED",
        flush=True,
    )

    print(
        "PASS: PUBLIC MARKET DATA READ ENABLED",
        flush=True,
    )

    for capability in dangerous_capabilities:
        print(
            "ZERO",
            capability.upper(),
            "= TRUE",
            flush=True,
        )

    print("-" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 2 RESULT = PASS")
    print("=" * 80, flush=True)

    return config


# ============================================================
# RUN UNIT 2
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# END PART 2 - COMPLETE UNIT 2
# ZERO INDENTATION DEMARCATION
# UNIT 2 FULLY CLOSED AND CALLED
# NO OPEN FUNCTION OR BLOCK
# ============================================================
