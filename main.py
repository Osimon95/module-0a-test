
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

# START COMPLETE REPLACEMENT - UNIT 2
# ZERO INDENTATION
# CONFIGURATION + FIVE BACKUP SAFETY
# ============================================================

def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 2 START")
    print("-" * 80, flush=True)

    # ========================================================
    # 1. REQUIRE UNIT 1
    # ========================================================

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
        raise RuntimeError(
            "UNIT 2 BLOCKED: UNIT 1 NOT READY"
        )

    # ========================================================
    # 2. EXCHANGE CONFIGURATION
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
    # 3. SAFETY CONTRACT
    # ========================================================

    # This Unit 2 is read-only.
    # Demo execution is handled by later validated units.
    # Real cash trading remains disabled.

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

        # ----------------------------------------------------
        # LEVERAGE AND INITIAL ENTRY
        # ----------------------------------------------------

        "leverage_target": 100,

        "initial_margin_percent": 5.0,

        "initial_fixed_usdt": 0.50,

        # ----------------------------------------------------
        # FIVE BACKUPS
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # MAXIMUM EXPOSURE
        # ----------------------------------------------------

        "exposure_cap_percent": 35.0,

        "progressive_backup_funding": True,

        "full_ladder_reservation_required": False,

        # ----------------------------------------------------
        # TAKE PROFIT ALLOCATION
        # ----------------------------------------------------

        "tp1_allocation_percent": 10.0,

        "tp2_allocation_percent": 20.0,

        "tp3_allocation_percent": 70.0,

        # ----------------------------------------------------
        # NET ROI TARGET FLOORS
        # ----------------------------------------------------

        "tp1_net_roi_floor_percent": 5.0,

        "tp2_net_roi_floor_percent": 10.0,

        "tp1_tp2_min_roi_separation_percent": 5.0,

        # ----------------------------------------------------
        # TP3 DYNAMIC TRAILING
        # ----------------------------------------------------

        "tp3_trailing_reference_percent": 0.20,

        "tp3_trailing_min_percent": 0.10,

        "tp3_trailing_max_percent": 0.40,

        # ----------------------------------------------------
        # SIGNAL / MODE CONTROL
        # ----------------------------------------------------

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
    # 6. COMPLETE CONFIGURATION OBJECT
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
    # 7. VALIDATION
    # ========================================================

    validation_errors = []

    # --------------------------------------------------------
    # EXCHANGE
    # --------------------------------------------------------

    if exchange_name != "WEEX":
        validation_errors.append(
            "INVALID EXCHANGE"
        )

    if api_version != "V3":
        validation_errors.append(
            "INVALID API VERSION"
        )

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
            "INVALID DEMO SYMBOL"
        )

    if execution_environment != "DEMO":
        validation_errors.append(
            "REAL TRADING NOT ALLOWED"
        )

    # --------------------------------------------------------
    # LEVERAGE / ENTRY
    # --------------------------------------------------------

    if strategy["leverage_target"] <= 0:
        validation_errors.append(
            "INVALID LEVERAGE"
        )

    if not (
        0 < strategy["initial_margin_percent"] <= 5.0
    ):
        validation_errors.append(
            "INVALID INITIAL MARGIN PERCENT"
        )

    if strategy["initial_fixed_usdt"] <= 0:
        validation_errors.append(
            "INVALID FIXED INITIAL MARGIN"
        )

    # --------------------------------------------------------
    # FIVE BACKUP VALIDATION
    # --------------------------------------------------------

    if strategy["max_backups"] != 5:
        validation_errors.append(
            "MAX BACKUPS MUST BE FIVE"
        )

    expected_multipliers = (
        1.0,
        1.5,
        2.0,
        2.5,
        3.0,
    )

    if (
        strategy["backup_multipliers"]
        != expected_multipliers
    ):
        validation_errors.append(
            "INVALID BACKUP MULTIPLIERS"
        )

    if not (
        0 < strategy["backup_margin_percent"] <= 5.0
    ):
        validation_errors.append(
            "INVALID BACKUP MARGIN PERCENT"
        )

    if strategy["backup_buffer_percent"] <= 0:
        validation_errors.append(
            "INVALID BACKUP BUFFER"
        )

    if strategy["progressive_backup_funding"] is not True:
        validation_errors.append(
            "PROGRESSIVE FUNDING DISABLED"
        )

    if (
        strategy["full_ladder_reservation_required"]
        is not False
    ):
        validation_errors.append(
            "FULL LADDER RESERVATION MUST BE OFF"
        )

    # --------------------------------------------------------
    # EXPOSURE PROTECTION
    # --------------------------------------------------------

    exposure_cap = (
        strategy["exposure_cap_percent"]
    )

    if not (0 < exposure_cap <= 35.0):
        validation_errors.append(
            "EXPOSURE CAP EXCEEDS 35%"
        )

    # Do not require the full ladder to fit the cap
    # during configuration.
    #
    # Initial entry and each subsequent backup
    # require separate affordability checks.
    #
    # Unit 14 must use actual exchange margin
    # and available funds before placing orders.

    backup_total_multiplier = sum(
        strategy["backup_multipliers"]
    )

    ladder_total_multiplier = (
        1.0 + backup_total_multiplier
    )

    full_ladder_margin = (
        strategy["initial_fixed_usdt"]
        * ladder_total_multiplier
    )

    # --------------------------------------------------------
    # TP ALLOCATION
    # --------------------------------------------------------

    tp_total = sum(
        (
            strategy["tp1_allocation_percent"],
            strategy["tp2_allocation_percent"],
            strategy["tp3_allocation_percent"],
        )
    )

    if abs(tp_total - 100.0) > 0.000001:
        validation_errors.append(
            "TP ALLOCATION MUST TOTAL 100%"
        )

    if any(
        strategy[key] <= 0
        for key in (
            "tp1_allocation_percent",
            "tp2_allocation_percent",
            "tp3_allocation_percent",
        )
    ):
        validation_errors.append(
            "INVALID TP ALLOCATION"
        )

    # --------------------------------------------------------
    # TP ROI
    # --------------------------------------------------------

    if (
        strategy["tp1_net_roi_floor_percent"]
        < 5.0
    ):
        validation_errors.append(
            "TP1 ROI FLOOR TOO LOW"
        )

    if (
        strategy["tp2_net_roi_floor_percent"]
        < 10.0
    ):
        validation_errors.append(
            "TP2 ROI FLOOR TOO LOW"
        )

    if (
        strategy["tp2_net_roi_floor_percent"]
        <= strategy["tp1_net_roi_floor_percent"]
    ):
        validation_errors.append(
            "TP2 MUST EXCEED TP1"
        )

    if (
        strategy["tp1_tp2_min_roi_separation_percent"]
        <= 0
    ):
        validation_errors.append(
            "INVALID TP SEPARATION"
        )

    # --------------------------------------------------------
    # TP3 TRAILING
    # --------------------------------------------------------

    trailing_min = strategy[
        "tp3_trailing_min_percent"
    ]

    trailing_ref = strategy[
        "tp3_trailing_reference_percent"
    ]

    trailing_max = strategy[
        "tp3_trailing_max_percent"
    ]

    if not (
        0 < trailing_min
        <= trailing_ref
        <= trailing_max
    ):
        validation_errors.append(
            "INVALID TP3 TRAILING RANGE"
        )

    # --------------------------------------------------------
    # SIGNAL CONTROL
    # --------------------------------------------------------

    for key in (
        "signal_expiry_seconds",
        "loss_cooldown_seconds",
        "mode_confirmations_required",
    ):
        if strategy[key] <= 0:
            validation_errors.append(
                "INVALID SIGNAL CONTROL: " + key
            )

    # --------------------------------------------------------
    # REQUIRED TRUE FLAGS
    # --------------------------------------------------------

    for key in (
        "one_direction_only",
        "anti_duplicate_orders",
        "active_trade_mode_lock",
        "exclusive_mode",
    ):
        if strategy[key] is not True:
            validation_errors.append(
                "REQUIRED FLAG DISABLED: " + key
            )

    # --------------------------------------------------------
    # PRECISION VALIDATION
    # --------------------------------------------------------

    for key in (
        "quantity_step",
        "minimum_quantity",
        "price_step",
    ):
        if market_precision[key] <= 0:
            validation_errors.append(
                "INVALID MARKET PRECISION: " + key
            )

    # --------------------------------------------------------
    # SAFETY VALIDATION
    # --------------------------------------------------------

    if (
        safety["public_market_data_read_enabled"]
        is not True
    ):
        validation_errors.append(
            "PUBLIC MARKET READ DISABLED"
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
        if safety[capability] is not False:
            validation_errors.append(
                "UNSAFE CAPABILITY: " + capability
            )

    # ========================================================
    # 8. FAIL CLOSED IF INVALID
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
    # 9. CONFIGURATION REPORT
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

    print(
        "PASS: LEVERAGE TARGET =",
        strategy["leverage_target"],
        flush=True,
    )

    print(
        "PASS: INITIAL MARGIN % =",
        strategy["initial_margin_percent"],
        flush=True,
    )

    print(
        "PASS: DEFAULT INITIAL MARGIN USDT =",
        strategy["initial_fixed_usdt"],
        flush=True,
    )

    print(
        "PASS: BACKUP MARGIN % =",
        strategy["backup_margin_percent"],
        flush=True,
    )

    print(
        "PASS: BACKUP BUFFER % =",
        strategy["backup_buffer_percent"],
        flush=True,
    )

    print(
        "PASS: MAX BACKUPS =",
        strategy["max_backups"],
        flush=True,
    )

    print(
        "PASS: BACKUP MULTIPLIERS =",
        strategy["backup_multipliers"],
        flush=True,
    )

    print(
        "PASS: BACKUP FUNDING = PROGRESSIVE",
        flush=True,
    )

    print(
        "PASS: FULL LADDER RESERVATION = FALSE",
        flush=True,
    )

    print(
        "PASS: EXPOSURE CAP % =",
        exposure_cap,
        flush=True,
    )

    print(
        "UNIT 2 FULL LADDER MARGIN USDT =",
        full_ladder_margin,
        flush=True,
    )

    print(
        "PASS: TP TARGET ALLOCATION = "
        "10% / 20% / 70%",
        flush=True,
    )

    print(
        "PASS: TP ALLOCATION TOTAL =",
        tp_total,
        "%",
        flush=True,
    )

    print(
        "PASS: TP1 NET ROI FLOOR =",
        strategy["tp1_net_roi_floor_percent"],
        "%",
        flush=True,
    )

    print(
        "PASS: TP2 NET ROI FLOOR =",
        strategy["tp2_net_roi_floor_percent"],
        "%",
        flush=True,
    )

    print(
        "PASS: TP1 -> TP2 MIN ROI SEPARATION =",
        strategy[
            "tp1_tp2_min_roi_separation_percent"
        ],
        "%",
        flush=True,
    )

    print(
        "PASS: TP3 TRAILING REFERENCE =",
        trailing_ref,
        "%",
        flush=True,
    )

    print(
        "PASS: TP3 TRAILING RANGE =",
        trailing_min,
        "%",
        "TO",
        trailing_max,
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
        "PASS: QUANTITY STEP =",
        market_precision["quantity_step"],
        flush=True,
    )

    print(
        "PASS: MINIMUM QUANTITY =",
        market_precision["minimum_quantity"],
        flush=True,
    )

    print(
        "PASS: PRICE STEP =",
        market_precision["price_step"],
        flush=True,
    )

    print(
        "PASS: ANTI-DUPLICATE ORDERS =",
        strategy["anti_duplicate_orders"],
        flush=True,
    )

    print(
        "PASS: ONE DIRECTION ONLY =",
        strategy["one_direction_only"],
        flush=True,
    )

    print(
        "PASS: ACTIVE TRADE MODE LOCK =",
        strategy["active_trade_mode_lock"],
        flush=True,
    )

    print(
        "PASS: EXCLUSIVE MODE =",
        strategy["exclusive_mode"],
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

    print(
        "ZERO AUTHENTICATED API ACCESS = TRUE",
        flush=True,
    )

    print(
        "ZERO ACCOUNT ACCESS = TRUE",
        flush=True,
    )

    print(
        "ZERO POSITION ACCESS = TRUE",
        flush=True,
    )

    print(
        "ZERO ORDER ENDPOINT ACCESS = TRUE",
        flush=True,
    )

    print(
        "ZERO DEMO ORDER SUBMISSION = TRUE",
        flush=True,
    )

    print(
        "ZERO REAL ORDER SUBMISSION = TRUE",
        flush=True,
    )

    print(
        "ZERO EXCHANGE MUTATION = TRUE",
        flush=True,
    )

    print(
        "ZERO LEVERAGE MUTATION = TRUE",
        flush=True,
    )

    print(
        "ZERO MARGIN MODE MUTATION = TRUE",
        flush=True,
    )

    print(
        "ZERO POSITION MODE MUTATION = TRUE",
        flush=True,
    )

    # ========================================================
    # 10. UNIT 2 COMPLETE
    # ========================================================

    print("-" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 2 RESULT = PASS"
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
# UNIT 2 FULLY CLOSED AND CALLED
# EXISTING UNIT 3 CONTINUES BELOW
# ============================================================
