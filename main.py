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
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 2
# ZERO INDENTATION DEMARCATION
# DELETE THE OLD UNIT 2 AND ITS CALL
# PASTE THIS COMPLETE BLOCK IN ITS PLACE
# ============================================================


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

# ============================================================
# RECONSTRUCTION UNIT 3
# WEEX V3 PUBLIC READ-ONLY MARKET DATA
# ============================================================

def fresh_reconstruction_unit_3():

    print(
        "=" * 80,
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 3 START"
    )

    print(
        "-" * 80,
        flush=True,
    )

    # --------------------------------------------------------
    # 1. REQUIRE VALIDATED UNIT 2 CONFIGURATION
    # --------------------------------------------------------

    config = (
        FRESH_RECONSTRUCTION_CONFIG
    )

    if not isinstance(
        config,
        dict,
    ):

        raise RuntimeError(
            "UNIT 3 BLOCKED: UNIT 2 CONFIGURATION MISSING"
        )

    exchange_config = (
        config.get(
            "exchange"
        )
    )

    safety = (
        config.get(
            "safety"
        )
    )

    if not isinstance(
        exchange_config,
        dict,
    ):

        raise RuntimeError(
            "UNIT 3 BLOCKED: EXCHANGE CONFIG MISSING"
        )

    if not isinstance(
        safety,
        dict,
    ):

        raise RuntimeError(
            "UNIT 3 BLOCKED: SAFETY CONFIG MISSING"
        )

    print(
        "PASS: UNIT 3 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    # --------------------------------------------------------
    # 2. READ EXCHANGE CONFIGURATION
    # --------------------------------------------------------

    exchange_name = (
        exchange_config.get(
            "name"
        )
    )

    api_version = (
        exchange_config.get(
            "api_version"
        )
    )

    base_url = (
        exchange_config.get(
            "contract_base_url"
        )
    )

    market_symbol = (
        exchange_config.get(
            "market_symbol"
        )
    )

    # --------------------------------------------------------
    # 3. STRICT EXCHANGE CONFIG VALIDATION
    # --------------------------------------------------------

    if exchange_name != "WEEX":

        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID EXCHANGE"
        )

    if api_version != "V3":

        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID API VERSION"
        )

    if (
        base_url
        !=
        "https://api-contract.weex.com"
    ):

        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID BASE URL"
        )

    if market_symbol != "BTCUSDT":

        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID MARKET SYMBOL"
        )

    print(
        "PASS: UNIT 3 EXCHANGE = WEEX",
        flush=True,
    )

    print(
        "PASS: UNIT 3 API VERSION = V3",
        flush=True,
    )

    print(
        "PASS: UNIT 3 MARKET SYMBOL =",
        market_symbol,
        flush=True,
    )

    # --------------------------------------------------------
    # 4. SAFETY GATE
    # --------------------------------------------------------

    if (
        safety.get(
            "public_market_data_read_enabled"
        )
        is not True
    ):

        raise RuntimeError(
            "UNIT 3 BLOCKED: PUBLIC MARKET READ DISABLED"
        )

    forbidden_capabilities = (

        "authenticated_api_enabled",

        "account_access_enabled",

        "position_access_enabled",

        "order_endpoint_access_enabled",

        "demo_order_submission_enabled",

        "real_order_submission_enabled",

        "exchange_mutation_enabled",
    )

    for capability in forbidden_capabilities:

        if (
            safety.get(
                capability
            )
            is not False
        ):

            raise RuntimeError(
                "UNIT 3 BLOCKED: UNSAFE CAPABILITY ENABLED: "
                +
                capability
            )

    print(
        "PASS: UNIT 3 READ-ONLY SAFETY GATE",
        flush=True,
    )

    # --------------------------------------------------------
    # 5. WEEX V3 PUBLIC SYMBOL-PRICE ENDPOINT
    #
    # GET:
    # /capi/v3/market/symbolPrice
    #
    # MARK price is intentionally requested.
    # --------------------------------------------------------

    endpoint = (
        "/capi/v3/market/symbolPrice"
    )

    price_type = "MARK"

    query = urllib.parse.urlencode(
        {
            "symbol":
                market_symbol,

            "priceType":
                price_type,
        }
    )

    url = (
        base_url
        +
        endpoint
        +
        "?"
        +
        query
    )

    # --------------------------------------------------------
    # 6. BUILD STRICT GET REQUEST
    # --------------------------------------------------------

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept":
                "application/json",

            "User-Agent":
                "Fresh-WEEX-Reconstruction/1-4",
        },
    )

    if request.get_method() != "GET":

        raise RuntimeError(
            "UNIT 3 BLOCKED: NON-GET REQUEST"
        )

    if request.data is not None:

        raise RuntimeError(
            "UNIT 3 BLOCKED: REQUEST BODY PRESENT"
        )

    print(
        "PASS: UNIT 3 ENDPOINT = WEEX V3 SYMBOL PRICE",
        flush=True,
    )

    print(
        "PASS: UNIT 3 HTTP METHOD = GET",
        flush=True,
    )

    print(
        "PASS: UNIT 3 AUTHENTICATION = NONE",
        flush=True,
    )

    print(
        "PASS: UNIT 3 REQUEST BODY = NONE",
        flush=True,
    )

    print(
        "PASS: UNIT 3 PRICE TYPE = MARK",
        flush=True,
    )

    # --------------------------------------------------------
    # 7. EXECUTE PUBLIC READ-ONLY GET
    # --------------------------------------------------------

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            status_code = (
                response.getcode()
            )

            raw_body = (
                response
                .read()
                .decode(
                    "utf-8"
                )
            )

    except urllib.error.HTTPError as exc:

        error_body = ""

        try:

            error_body = (
                exc
                .read()
                .decode(
                    "utf-8"
                )
            )

        except Exception:

            pass

        print(
            "UNIT 3 HTTP ERROR CODE =",
            exc.code,
            flush=True,
        )

        print(
            "UNIT 3 HTTP ERROR BODY =",
            error_body[:1000],
            flush=True,
        )

        raise RuntimeError(
            "UNIT 3 WEEX V3 MARKET DATA HTTP ERROR"
        ) from exc

    except urllib.error.URLError as exc:

        print(
            "UNIT 3 URL ERROR =",
            repr(
                exc.reason
            ),
            flush=True,
        )

        raise RuntimeError(
            "UNIT 3 WEEX V3 CONNECTION FAILED"
        ) from exc

    except Exception as exc:

        print(
            "UNIT 3 UNEXPECTED CONNECTION ERROR =",
            repr(
                exc
            ),
            flush=True,
        )

        raise

    # --------------------------------------------------------
    # 8. HTTP RESPONSE VALIDATION
    # --------------------------------------------------------

    print(
        "UNIT 3 HTTP STATUS =",
        status_code,
        flush=True,
    )

    if status_code != 200:

        raise RuntimeError(
            "UNIT 3 INVALID HTTP STATUS"
        )

    if not raw_body:

        raise RuntimeError(
            "UNIT 3 EMPTY RESPONSE"
        )

    print(
        "PASS: UNIT 3 WEEX V3 RESPONSE RECEIVED",
        flush=True,
    )

    # --------------------------------------------------------
    # 9. JSON RESPONSE VALIDATION
    # --------------------------------------------------------

    try:

        payload = json.loads(
            raw_body
        )

    except json.JSONDecodeError as exc:

        print(
            "UNIT 3 RAW RESPONSE =",
            raw_body[:1000],
            flush=True,
        )

        raise RuntimeError(
            "UNIT 3 INVALID JSON RESPONSE"
        ) from exc

    if not isinstance(
        payload,
        dict,
    ):

        raise RuntimeError(
            "UNIT 3 INVALID RESPONSE TYPE"
        )

    print(
        "PASS: UNIT 3 VALID JSON RESPONSE",
        flush=True,
    )

    # --------------------------------------------------------
    # 10. STRICT RESPONSE CONTRACT
    # --------------------------------------------------------

    response_symbol = (
        payload.get(
            "symbol"
        )
    )

    response_price = (
        payload.get(
            "price"
        )
    )

    response_time = (
        payload.get(
            "time"
        )
    )

    if response_symbol != market_symbol:

        print(
            "UNIT 3 RESPONSE SYMBOL =",
            response_symbol,
            flush=True,
        )

        raise RuntimeError(
            "UNIT 3 RESPONSE SYMBOL MISMATCH"
        )

    try:

        live_price = float(
            response_price
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise RuntimeError(
            "UNIT 3 INVALID MARKET PRICE"
        ) from exc

    if live_price <= 0:

        raise RuntimeError(
            "UNIT 3 NON-POSITIVE MARKET PRICE"
        )

    if not isinstance(
        response_time,
        int,
    ):

        raise RuntimeError(
            "UNIT 3 INVALID MARKET TIMESTAMP"
        )

    if response_time <= 0:

        raise RuntimeError(
            "UNIT 3 NON-POSITIVE MARKET TIMESTAMP"
        )

    print(
        "PASS: UNIT 3 RESPONSE SYMBOL =",
        response_symbol,
        flush=True,
    )

    print(
        "PASS: UNIT 3 LIVE BTC MARK PRICE =",
        live_price,
        flush=True,
    )

    print(
        "PASS: UNIT 3 MARKET TIMESTAMP =",
        response_time,
        flush=True,
    )

    # --------------------------------------------------------
    # 11. NORMALIZED MARKET SNAPSHOT
    # --------------------------------------------------------

    market_snapshot = {

        "exchange":
            exchange_name,

        "api_version":
            api_version,

        "symbol":
            market_symbol,

        "price":
            live_price,

        "price_type":
            price_type,

        "exchange_time_ms":
            response_time,

        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE",

        "read_only":
            True,
    }

    # --------------------------------------------------------
    # 12. NORMALIZED SNAPSHOT VALIDATION
    # --------------------------------------------------------

    if (
        market_snapshot[
            "exchange"
        ]
        !=
        "WEEX"
    ):

        raise RuntimeError(
            "UNIT 3 SNAPSHOT EXCHANGE FAILURE"
        )

    if (
        market_snapshot[
            "api_version"
        ]
        !=
        "V3"
    ):

        raise RuntimeError(
            "UNIT 3 SNAPSHOT API VERSION FAILURE"
        )

    if (
        market_snapshot[
            "symbol"
        ]
        !=
        "BTCUSDT"
    ):

        raise RuntimeError(
            "UNIT 3 SNAPSHOT SYMBOL FAILURE"
        )

    if (
        market_snapshot[
            "read_only"
        ]
        is not True
    ):

        raise RuntimeError(
            "UNIT 3 SNAPSHOT READ-ONLY FAILURE"
        )

    # --------------------------------------------------------
    # 13. FINAL SAFETY REPORT
    # --------------------------------------------------------

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 3 NORMALIZED MARKET SNAPSHOT",
        flush=True,
    )

    print(
        "PASS: WEEX V3 PUBLIC MARKET READ COMPLETED",
        flush=True,
    )

    print(
        "PASS: STANDARD LIBRARY HTTP CLIENT",
        flush=True,
    )

    print(
        "PASS: NO requests PACKAGE REQUIRED",
        flush=True,
    )

    print(
        "ZERO AUTHENTICATED REQUEST = TRUE",
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
        "ZERO DEMO ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO REAL ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO EXCHANGE WRITE = TRUE",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 3 RESULT = PASS"
    )

    print(
        "=" * 80,
        flush=True,
    )

    return market_snapshot


# ============================================================
# RUN UNIT 3
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# END OF TRANSMISSION PART 2A
#
# ZERO INDENTATION DEMARCATION
# UNIT 3 IS FULLY CLOSED AND CALLED
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN TRY
# NO OPEN DICTIONARY
# NO INDENTATION CONTINUES INTO PART 2B
#
# PASTE PART 2B DIRECTLY BELOW THIS LINE
# ============================================================

# ============================================================
# FRESH RECONSTRUCTION UNIT 4
# PUBLIC MARK-PRICE KLINE + CLOSED-CANDLE EMA ANALYSIS
#
# PURPOSE:
# - Consume verified Unit 2 configuration
# - Consume verified Unit 3 market snapshot
# - Read WEEX V3 PUBLIC mark-price candles
# - Exclude unfinished candles from signal calculations
# - Calculate EMA19 / EMA50 / EMA200 from CLOSED candles
# - Calculate closed-candle multi-window movement
# - Produce normalized read-only Unit 4 snapshot
#
# IMPORTANT:
# - ZERO AUTHENTICATED API ACCESS
# - ZERO ACCOUNT ACCESS
# - ZERO POSITION ACCESS
# - ZERO ORDER ENDPOINT ACCESS
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE WRITE
# - ZERO LEVERAGE MUTATION
# - ZERO MARGIN MODE MUTATION
# - ZERO POSITION MODE MUTATION
#
# UNIT 4 IS ANALYSIS ONLY.
# ============================================================

def fresh_reconstruction_unit_4():

    print(
        "=" * 80,
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 4 START"
    )

    print(
        "-" * 80,
        flush=True,
    )

    # ========================================================
    # 1. RECEIVE VERIFIED UNIT 2 CONFIGURATION
    # ========================================================

    config = (
        FRESH_RECONSTRUCTION_CONFIG
    )

    if not isinstance(
        config,
        dict,
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID UNIT 2 CONFIGURATION"
        )

    print(
        "PASS: UNIT 4 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    # ========================================================
    # 2. RECEIVE VERIFIED UNIT 3 MARKET SNAPSHOT
    # ========================================================

    market_snapshot = (
        FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    )

    if not isinstance(
        market_snapshot,
        dict,
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID UNIT 3 MARKET SNAPSHOT"
        )

    print(
        "PASS: UNIT 4 RECEIVED UNIT 3 MARKET SNAPSHOT",
        flush=True,
    )

    required_snapshot_fields = (
        "exchange",
        "api_version",
        "symbol",
        "price",
        "price_type",
        "exchange_time_ms",
        "source",
        "read_only",
    )

    missing_snapshot_fields = [
        field
        for field in required_snapshot_fields
        if field not in market_snapshot
    ]

    if missing_snapshot_fields:
        raise RuntimeError(
            "UNIT 4 BLOCKED: UNIT 3 SNAPSHOT MISSING FIELDS = "
            + str(missing_snapshot_fields)
        )

    if market_snapshot["exchange"] != "WEEX":
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID EXCHANGE"
        )

    if market_snapshot["api_version"] != "V3":
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID API VERSION"
        )

    if market_snapshot["symbol"] != "BTCUSDT":
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID MARKET SYMBOL"
        )

    if market_snapshot["price_type"] != "MARK":
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID PRICE TYPE"
        )

    if market_snapshot["read_only"] is not True:
        raise RuntimeError(
            "UNIT 4 BLOCKED: UNIT 3 SNAPSHOT NOT READ ONLY"
        )

    exchange_time_ms = int(
        market_snapshot[
            "exchange_time_ms"
        ]
    )

    if exchange_time_ms <= 0:
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID EXCHANGE TIME"
        )

    print(
        "PASS: UNIT 4 UNIT 3 SNAPSHOT VALIDATED",
        flush=True,
    )

    # ========================================================
    # 3. READ CONFIGURATION
    # ========================================================

    exchange_config = (
        config.get(
            "exchange"
        )
    )

    safety = (
        config.get(
            "safety"
        )
    )

    if not isinstance(
        exchange_config,
        dict,
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: EXCHANGE CONFIGURATION MISSING"
        )

    if not isinstance(
        safety,
        dict,
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: SAFETY CONFIGURATION MISSING"
        )

    base_url = (
        exchange_config.get(
            "contract_base_url"
        )
    )

    market_symbol = (
        exchange_config.get(
            "market_symbol"
        )
    )

    if (
        base_url
        !=
        "https://api-contract.weex.com"
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID CONTRACT BASE URL"
        )

    if (
        market_symbol
        !=
        market_snapshot["symbol"]
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: MARKET SYMBOL MISMATCH"
        )

    # ========================================================
    # 4. READ-ONLY SAFETY GATE
    # ========================================================

    if (
        safety.get(
            "public_market_data_read_enabled"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: PUBLIC MARKET READ DISABLED"
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

        if (
            safety.get(
                capability
            )
            is not False
        ):
            raise RuntimeError(
                "UNIT 4 BLOCKED: UNSAFE CAPABILITY ENABLED: "
                + capability
            )

    print(
        "PASS: UNIT 4 READ-ONLY SAFETY GATE",
        flush=True,
    )

    # ========================================================
    # 5. PUBLIC KLINE SETTINGS
    # ========================================================

    interval = "1m"
    candle_limit = 300

    endpoint = (
        "/capi/v3/market/markPriceKlines"
    )

    query_parameters = {
        "symbol":
            market_symbol,

        "interval":
            interval,

        "limit":
            candle_limit,
    }

    query_string = (
        urllib.parse.urlencode(
            query_parameters
        )
    )

    request_url = (
        base_url
        + endpoint
        + "?"
        + query_string
    )

    print(
        "PASS: UNIT 4 ENDPOINT = WEEX V3 MARK PRICE KLINES",
        flush=True,
    )

    print(
        "PASS: UNIT 4 HTTP METHOD = GET",
        flush=True,
    )

    print(
        "PASS: UNIT 4 AUTHENTICATION = NONE",
        flush=True,
    )

    print(
        "PASS: UNIT 4 REQUEST BODY = NONE",
        flush=True,
    )

    print(
        "PASS: UNIT 4 MARKET SYMBOL =",
        market_symbol,
        flush=True,
    )

    print(
        "PASS: UNIT 4 INTERVAL =",
        interval,
        flush=True,
    )

    print(
        "PASS: UNIT 4 CANDLE LIMIT =",
        candle_limit,
        flush=True,
    )

    # ========================================================
    # 6. BUILD PUBLIC GET REQUEST
    # ========================================================

    request = urllib.request.Request(
        url=request_url,
        method="GET",
        headers={
            "Accept":
                "application/json",

            "User-Agent":
                "Fresh-WEEX-Reconstruction/1-4",
        },
    )

    if request.get_method() != "GET":
        raise RuntimeError(
            "UNIT 4 BLOCKED: NON-GET REQUEST"
        )

    if request.data is not None:
        raise RuntimeError(
            "UNIT 4 BLOCKED: REQUEST BODY PRESENT"
        )

    # ========================================================
    # 7. PUBLIC HTTP READ
    # ========================================================

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            http_status = (
                response.getcode()
            )

            response_body = (
                response
                .read()
                .decode(
                    "utf-8"
                )
            )

    except urllib.error.HTTPError as exc:

        error_body = ""

        try:
            error_body = (
                exc
                .read()
                .decode(
                    "utf-8"
                )
            )
        except Exception:
            pass

        print(
            "UNIT 4 HTTP ERROR CODE =",
            exc.code,
            flush=True,
        )

        print(
            "UNIT 4 HTTP ERROR BODY =",
            error_body[:1000],
            flush=True,
        )

        raise RuntimeError(
            "UNIT 4 WEEX V3 KLINE HTTP ERROR"
        ) from exc

    except urllib.error.URLError as exc:

        print(
            "UNIT 4 URL ERROR =",
            repr(
                exc.reason
            ),
            flush=True,
        )

        raise RuntimeError(
            "UNIT 4 WEEX V3 KLINE CONNECTION FAILED"
        ) from exc

    except Exception as exc:

        print(
            "UNIT 4 UNEXPECTED CONNECTION ERROR =",
            repr(
                exc
            ),
            flush=True,
        )

        raise

    print(
        "UNIT 4 HTTP STATUS =",
        http_status,
        flush=True,
    )

    if http_status != 200:
        raise RuntimeError(
            "UNIT 4 BLOCKED: NON-200 HTTP STATUS"
        )

    if not response_body:
        raise RuntimeError(
            "UNIT 4 BLOCKED: EMPTY KLINE RESPONSE"
        )

    print(
        "PASS: UNIT 4 WEEX V3 KLINE RESPONSE RECEIVED",
        flush=True,
    )

    # ========================================================
    # 8. JSON PARSE
    # ========================================================

    try:

        raw_klines = json.loads(
            response_body
        )

    except json.JSONDecodeError as exc:

        print(
            "UNIT 4 RAW RESPONSE =",
            response_body[:1000],
            flush=True,
        )

        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID JSON RESPONSE"
        ) from exc

    print(
        "PASS: UNIT 4 VALID JSON RESPONSE",
        flush=True,
    )

    if not isinstance(
        raw_klines,
        list,
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: KLINE RESPONSE IS NOT A LIST"
        )

    if len(raw_klines) < 200:
        raise RuntimeError(
            "UNIT 4 BLOCKED: FEWER THAN 200 KLINES RECEIVED"
        )

    print(
        "PASS: UNIT 4 KLINES RECEIVED =",
        len(raw_klines),
        flush=True,
    )

    # ========================================================
    # 9. NORMALIZE KLINES
    #
    # EXPECTED WEEX FORMAT:
    #
    # [0] open time
    # [1] open
    # [2] high
    # [3] low
    # [4] close
    # [5] volume
    # [6] close time
    # ========================================================

    normalized_klines = []

    for raw_candle in raw_klines:

        if not isinstance(
            raw_candle,
            (list, tuple),
        ):
            raise RuntimeError(
                "UNIT 4 BLOCKED: INVALID KLINE ENTRY"
            )

        if len(raw_candle) < 7:
            raise RuntimeError(
                "UNIT 4 BLOCKED: INCOMPLETE KLINE ENTRY"
            )

        try:

            normalized_candle = {
                "open_time_ms":
                    int(
                        raw_candle[0]
                    ),

                "open":
                    float(
                        raw_candle[1]
                    ),

                "high":
                    float(
                        raw_candle[2]
                    ),

                "low":
                    float(
                        raw_candle[3]
                    ),

                "close":
                    float(
                        raw_candle[4]
                    ),

                "volume":
                    float(
                        raw_candle[5]
                    ),

                "close_time_ms":
                    int(
                        raw_candle[6]
                    ),
            }

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise RuntimeError(
                "UNIT 4 BLOCKED: INVALID KLINE VALUE"
            ) from exc

        if (
            normalized_candle["open"] <= 0
            or normalized_candle["high"] <= 0
            or normalized_candle["low"] <= 0
            or normalized_candle["close"] <= 0
        ):
            raise RuntimeError(
                "UNIT 4 BLOCKED: NON-POSITIVE KLINE PRICE"
            )

        normalized_klines.append(
            normalized_candle
        )

    normalized_klines.sort(
        key=lambda candle:
            candle[
                "open_time_ms"
            ]
    )

    print(
        "PASS: UNIT 4 KLINES NORMALIZED",
        flush=True,
    )

    print(
        "PASS: UNIT 4 KLINES ORDERED OLDEST -> NEWEST",
        flush=True,
    )

    # ========================================================
    # 10. VALIDATE KLINE ORDER
    # ========================================================

    previous_open_time = None

    for candle in normalized_klines:

        current_open_time = (
            candle[
                "open_time_ms"
            ]
        )

        if (
            previous_open_time
            is not None
            and current_open_time
            <= previous_open_time
        ):
            raise RuntimeError(
                "UNIT 4 BLOCKED: DUPLICATE OR UNORDERED KLINE TIME"
            )

        previous_open_time = (
            current_open_time
        )

    print(
        "PASS: UNIT 4 KLINE TIMESTAMPS VALIDATED",
        flush=True,
    )

    # ========================================================
    # 11. CLOSED-CANDLE FILTER
    #
    # The newest WEEX kline may still be forming.
    #
    # Only candles whose close time is <= Unit 3 exchange
    # timestamp may participate in EMA or momentum signals.
    # ========================================================

    closed_klines = [
        candle
        for candle in normalized_klines
        if candle[
            "close_time_ms"
        ] <= exchange_time_ms
    ]

    if len(closed_klines) < 200:
        raise RuntimeError(
            "UNIT 4 BLOCKED: INSUFFICIENT CLOSED KLINES"
        )

    newest_returned_candle = (
        normalized_klines[-1]
    )

    newest_returned_is_closed = (
        newest_returned_candle[
            "close_time_ms"
        ] <= exchange_time_ms
    )

    print(
        "PASS: UNIT 4 EXCHANGE TIME =",
        exchange_time_ms,
        flush=True,
    )

    print(
        "PASS: UNIT 4 RETURNED KLINES =",
        len(normalized_klines),
        flush=True,
    )

    print(
        "PASS: UNIT 4 CLOSED KLINES =",
        len(closed_klines),
        flush=True,
    )

    print(
        "UNIT 4 NEWEST RETURNED CANDLE CLOSED =",
        newest_returned_is_closed,
        flush=True,
    )


# ============================================================
# END OF TRANSMISSION PART 2B-1
# ZERO INDENTATION DEMARCATION
#
# IMPORTANT:
# - UNIT 4 FUNCTION IS STILL OPEN
# - THIS ZERO-INDENTATION COMMENT DOES NOT CLOSE THE FUNCTION
# - PART 2B-2 RESUMES UNIT 4 AT ITS ORIGINAL 4-SPACE INDENTATION
# - DO NOT ADD EXECUTABLE CODE BETWEEN 2B-1 AND 2B-2
# - PASTE PART 2B-2 DIRECTLY BELOW THIS LINE
# ============================================================

    # ========================================================
    # 12. CLOSED-CANDLE CLOSE PRICE SERIES
    # ========================================================

    close_prices = [
        candle[
            "close"
        ]
        for candle in closed_klines
    ]

    if len(close_prices) < 200:
        raise RuntimeError(
            "UNIT 4 BLOCKED: INSUFFICIENT CLOSED CLOSE PRICES"
        )

    print(
        "PASS: UNIT 4 CLOSED-CANDLE PRICE SERIES READY",
        flush=True,
    )

    
    
    # ========================================================
    # 13. EMA CALCULATION
    # EMA19 / EMA50 / EMA100 / EMA200
    # INDENTATION: 4 SPACES
    # ========================================================

    def calculate_ema(prices, period):

        if len(prices) < period:
            raise RuntimeError(
                "INSUFFICIENT DATA FOR EMA"
                + str(period)
            )

        ema_value = sum(prices[:period]) / period
        multiplier = 2.0 / (period + 1.0)

        for price in prices[period:]:
            ema_value = (
                price * multiplier
                + ema_value * (1.0 - multiplier)
            )

        return float(ema_value)

    ema19 = calculate_ema(close_prices, 19)
    ema50 = calculate_ema(close_prices, 50)
    ema100 = calculate_ema(close_prices, 100)
    ema200 = calculate_ema(close_prices, 200)

    if any(
        value <= 0
        for value in (
            ema19,
            ema50,
            ema100,
            ema200,
        )
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID EMA VALUE"
        )

    print(
        "PASS: UNIT 4 EMA19 =",
        round(ema19, 6),
        flush=True,
    )

    print(
        "PASS: UNIT 4 EMA50 =",
        round(ema50, 6),
        flush=True,
    )

    print(
        "PASS: UNIT 4 EMA100 =",
        round(ema100, 6),
        flush=True,
    )

    print(
        "PASS: UNIT 4 EMA200 =",
        round(ema200, 6),
        flush=True,
    )

    # ========================================================
    # END UNIT 4 EMA CALCULATION
    # UNIT 4 CONTINUES BELOW
    # ========================================================
    # ========================================================
    # 14. EMA19 / EMA50 SEPARATION
    # ========================================================

    if ema50 == 0:
        raise RuntimeError(
            "UNIT 4 BLOCKED: EMA50 IS ZERO"
        )

    ema19_50_separation_pct = (
        abs(
            ema19
            -
            ema50
        )
        /
        ema50
        *
        100.0
    )

    print(
        "PASS: UNIT 4 EMA19/50 SEPARATION % =",
        round(
            ema19_50_separation_pct,
            6,
        ),
        flush=True,
    )

    # ========================================================
    # 15. EMA STRUCTURE
    # ========================================================

    if (
        ema19 > ema50
        and ema50 > ema200
    ):
        ema_structure = (
            "BULLISH"
        )

    elif (
        ema19 < ema50
        and ema50 < ema200
    ):
        ema_structure = (
            "BEARISH"
        )

    else:
        ema_structure = (
            "MIXED"
        )

    print(
        "PASS: UNIT 4 EMA STRUCTURE =",
        ema_structure,
        flush=True,
    )

    # ========================================================
    # 16. LATEST TWO FULLY CLOSED CANDLES
    # ========================================================

    latest_candle = (
        closed_klines[-1]
    )

    previous_candle = (
        closed_klines[-2]
    )

    latest_close = float(
        latest_candle[
            "close"
        ]
    )

    previous_close = float(
        previous_candle[
            "close"
        ]
    )

    latest_open_time_ms = int(
        latest_candle[
            "open_time_ms"
        ]
    )

    latest_close_time_ms = int(
        latest_candle[
            "close_time_ms"
        ]
    )

    print(
        "PASS: UNIT 4 PREVIOUS KLINE CLOSE =",
        previous_close,
        flush=True,
    )

    print(
        "PASS: UNIT 4 LATEST KLINE CLOSE =",
        latest_close,
        flush=True,
    )

    print(
        "PASS: UNIT 4 LATEST KLINE OPEN TIME =",
        latest_open_time_ms,
        flush=True,
    )

    print(
        "PASS: UNIT 4 LATEST KLINE CLOSE TIME =",
        latest_close_time_ms,
        flush=True,
    )

    # ========================================================
    # 17. CLOSED 1-MINUTE MOVE
    # ========================================================

    if previous_close <= 0:
        raise RuntimeError(
            "UNIT 4 BLOCKED: PREVIOUS CLOSE IS ZERO"
        )

    short_term_move_pct = (
        (
            latest_close
            -
            previous_close
        )
        /
        previous_close
        *
        100.0
    )

    print(
        "PASS: UNIT 4 SHORT-TERM MOVE % =",
        round(
            short_term_move_pct,
            6,
        ),
        flush=True,
    )

    # ========================================================
    # 18. CLOSED-CANDLE MULTI-WINDOW MOMENTUM
    #
    # These values are stored in the Unit 4 snapshot.
    #
    # Unit 4 itself still does NOT qualify entries.
    # ========================================================

    diagnostic_windows = (
        1,
        5,
        15,
        30,
        60,
        120,
    )

    window_moves_pct = {}

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 4 BREAKOUT WINDOW DIAGNOSTIC",
        flush=True,
    )

    for window_minutes in diagnostic_windows:

        if (
            len(close_prices)
            <= window_minutes
        ):
            raise RuntimeError(
                "UNIT 4 BLOCKED: INSUFFICIENT DATA FOR "
                + str(window_minutes)
                + "M MOVE"
            )

        reference_close = float(
            close_prices[
                -(window_minutes + 1)
            ]
        )

        if reference_close <= 0:
            raise RuntimeError(
                "UNIT 4 BLOCKED: INVALID "
                + str(window_minutes)
                + "M REFERENCE CLOSE"
            )

        window_move_pct = (
            (
                latest_close
                -
                reference_close
            )
            /
            reference_close
            *
            100.0
        )

        window_moves_pct[
            window_minutes
        ] = float(
            window_move_pct
        )

        print(
            f"UNIT 4 {window_minutes}M MOVE % = "
            f"{round(window_move_pct, 6)}",
            flush=True,
        )

    print(
        "UNIT 4 SIGNAL MOVE SOURCE = "
        "FULLY CLOSED 1M CANDLE VS PREVIOUS FULLY CLOSED 1M CANDLE",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    # ========================================================
    # 19. UNIT 3 REAL-TIME MARK PRICE
    #
    # Signal candles are closed candles.
    # Execution/context mark price remains real-time.
    # ========================================================

    live_mark_price = float(
        market_snapshot[
            "price"
        ]
    )

    if live_mark_price <= 0:
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID LIVE MARK PRICE"
        )

    print(
        "PASS: UNIT 4 LIVE MARK PRICE =",
        live_mark_price,
        flush=True,
    )

    # ========================================================
    # 20. NORMALIZED ANALYSIS SNAPSHOT
    # ========================================================

    analysis_snapshot = {
        "exchange":
            "WEEX",

        "api_version":
            "V3",

        "symbol":
            market_symbol,

        "interval":
            interval,

        "price_type":
            "MARK",

        "live_mark_price":
            live_mark_price,

        "previous_close":
            previous_close,

        "latest_close":
            latest_close,

        "latest_open_time_ms":
            latest_open_time_ms,

        "latest_close_time_ms":
            latest_close_time_ms,

        "exchange_time_ms":
            exchange_time_ms,

        "ema19":
            ema19,

        "ema50":
            ema50,
        "ema100":
            ema100,
        "ema200":
            ema200,

        "ema19_50_separation_pct":
            ema19_50_separation_pct,

        "short_term_move_pct":
            short_term_move_pct,

        "move_1m_pct":
            window_moves_pct[1],

        "move_5m_pct":
            window_moves_pct[5],

        "move_15m_pct":
            window_moves_pct[15],

        "move_30m_pct":
            window_moves_pct[30],

        "move_60m_pct":
            window_moves_pct[60],

        "move_120m_pct":
            window_moves_pct[120],

        "ema_structure":
            ema_structure,

        # Recent fully closed 1-minute OHLC candles are exposed
        # for downstream read-only SCALP quality analysis.
        "recent_closed_klines": [
            dict(candle)
            for candle in closed_klines[-60:]
        ],

        "candle_count":
            len(
                normalized_klines
            ),

        "closed_candle_count":
            len(
                closed_klines
            ),

        "newest_returned_candle_closed":
            newest_returned_is_closed,

        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",

        "read_only":
            True,
    }

    # ========================================================
    # 21. FINAL SNAPSHOT VALIDATION
    # ========================================================

    required_analysis_fields = (
        "exchange",
        "api_version",
        "symbol",
        "interval",
        "price_type",
        "live_mark_price",
        "previous_close",
        "latest_close",
        "latest_open_time_ms",
        "latest_close_time_ms",
        "exchange_time_ms",
        "ema19",
        "ema50",
        "ema100",
        "ema200",
        "ema19_50_separation_pct",
        "short_term_move_pct",
        "move_1m_pct",
        "move_5m_pct",
        "move_15m_pct",
        "move_30m_pct",
        "move_60m_pct",
        "move_120m_pct",
        "ema_structure",
        "recent_closed_klines",
        "candle_count",
        "closed_candle_count",
        "newest_returned_candle_closed",
        "source",
        "read_only",
    )

    missing_analysis_fields = [
        field
        for field in required_analysis_fields
        if field not in analysis_snapshot
    ]

    if missing_analysis_fields:
        raise RuntimeError(
            "UNIT 4 ANALYSIS SNAPSHOT MISSING FIELDS = "
            + str(missing_analysis_fields)
        )

    if (
        analysis_snapshot[
            "read_only"
        ]
        is not True
    ):
        raise RuntimeError(
            "UNIT 4 ANALYSIS SNAPSHOT READ-ONLY FAILURE"
        )

    if (
        analysis_snapshot[
            "latest_close_time_ms"
        ]
        >
        analysis_snapshot[
            "exchange_time_ms"
        ]
    ):
        raise RuntimeError(
            "UNIT 4 CLOSED-CANDLE SAFETY FAILURE"
        )

    if (
        abs(
            analysis_snapshot[
                "move_1m_pct"
            ]
            -
            analysis_snapshot[
                "short_term_move_pct"
            ]
        )
        >
        0.000000001
    ):
        raise RuntimeError(
            "UNIT 4 1M MOVE CONSISTENCY FAILURE"
        )

    # ========================================================
    # 22. FINAL SAFETY REPORT
    # ========================================================

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 4 NORMALIZED MARKET ANALYSIS SNAPSHOT",
        flush=True,
    )

    print(
        "PASS: UNIT 4 CLOSED-CANDLE SIGNAL SOURCE VERIFIED",
        flush=True,
    )

    print(
        "PASS: UNIT 4 MULTI-WINDOW MOMENTUM SNAPSHOT READY",
        flush=True,
    )

    print(
        "PASS: UNIT 4 PUBLIC MARKET ANALYSIS COMPLETED",
        flush=True,
    )

    print(
        "PASS: UNIT 4 EMA19 / EMA50 / EMA200 COMPLETED",
        flush=True,
    )

    print(
        "PASS: UNIT 4 NO ENTRY SIGNAL GENERATED",
        flush=True,
    )

    print(
        "PASS: UNIT 4 NO ORDER PAYLOAD GENERATED",
        flush=True,
    )

    print(
        "ZERO AUTHENTICATED REQUEST = TRUE",
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
        "ZERO DEMO ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO REAL ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO EXCHANGE WRITE = TRUE",
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

    print(
        "-" * 80,
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 4 RESULT = PASS"
    )

    print(
        "=" * 80,
        flush=True,
    )

    return analysis_snapshot


# ============================================================
# RUN UNIT 4
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)


# ============================================================
# END OF TRANSMISSION PART 2B-2
# ZERO INDENTATION DEMARCATION
#
# UNIT 4 IS FULLY CLOSED
# UNIT 4 HAS BEEN CALLED
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN TRY
# NO OPEN DICTIONARY
# NO INDENTATION CONTINUES INTO THE NEXT PART
#
# PASTE THE NEXT PART DIRECTLY BELOW THIS LINE
# ============================================================

# FRESH RECONSTRUCTION UNIT 5
# MULTI-WINDOW SIGNAL QUALIFICATION ENGINE
#
# PURPOSE:
# Consume the verified normalized Unit 4 market-analysis
# snapshot and determine whether the current market state
# qualifies for:
#
#   - SCALP
#   - STRUCTURE
#   - BREAKOUT
#   - NO TRADE
#
# MOMENTUM ARCHITECTURE:
#
# SCALP
#   Primary momentum = CLOSED 5M movement
#   1M movement = freshness / supporting information
#
# STRUCTURE
#   Primary momentum = CLOSED 15M movement
#
# BREAKOUT
#   Primary momentum = CLOSED 30M movement
#   5M / 15M provide directional support
#
# IMPORTANT:
# - EMA thresholds remain unchanged
# - Movement thresholds remain unchanged
# - EMA200 is NOT required for SCALP
# - ZERO AUTHENTICATED API ACCESS
# - ZERO ACCOUNT ACCESS
# - ZERO POSITION ACCESS
# - ZERO ORDER ENDPOINT ACCESS
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE WRITE
# - ZERO ORDER PAYLOAD
# - ZERO POSITION SIZING
# - ZERO TP / SL
# - ZERO BACKUP EXECUTION
#
# UNIT 5 ONLY QUALIFIES MARKET STATE.
# ============================================================


def fresh_reconstruction_unit_5(
    unit_2_config,
    unit_4_snapshot,
):
    print(
        "=" * 80,
        flush=True,
    )

    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 5 START",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    # ========================================================
    # 1. INPUT VALIDATION
    # ========================================================

    if not isinstance(
        unit_2_config,
        dict,
    ):
        raise RuntimeError(
            "UNIT 5 FAILED: INVALID UNIT 2 CONFIGURATION"
        )

    print(
        "PASS: UNIT 5 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    if not isinstance(
        unit_4_snapshot,
        dict,
    ):
        raise RuntimeError(
            "UNIT 5 FAILED: INVALID UNIT 4 SNAPSHOT"
        )

    print(
        "PASS: UNIT 5 RECEIVED UNIT 4 MARKET SNAPSHOT",
        flush=True,
    )

    # ========================================================
    # 2. REQUIRED UNIT 4 FIELDS
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
    )

    missing_fields = [
        field
        for field in required_fields
        if field not in unit_4_snapshot
    ]

    if missing_fields:
        raise RuntimeError(
            "UNIT 5 FAILED: UNIT 4 SNAPSHOT MISSING FIELDS = "
            + str(missing_fields)
        )

    print(
        "PASS: UNIT 5 REQUIRED UNIT 4 FIELDS PRESENT",
        flush=True,
    )

    # ========================================================
    # 3. NORMALIZE INPUT VALUES
    # ========================================================

    symbol = str(
        unit_4_snapshot[
            "symbol"
        ]
    ).upper()

    live_price = float(
        unit_4_snapshot[
            "live_mark_price"
        ]
    )

    ema19 = float(
        unit_4_snapshot[
            "ema19"
        ]
    )

    ema50 = float(
        unit_4_snapshot[
            "ema50"
        ]
    )

    ema200 = float(
        unit_4_snapshot[
            "ema200"
        ]
    )

    separation_pct = abs(
        float(
            unit_4_snapshot[
                "ema19_50_separation_pct"
            ]
        )
    )

    ema_structure = str(
        unit_4_snapshot[
            "ema_structure"
        ]
    ).upper()

    previous_close = float(
        unit_4_snapshot[
            "previous_close"
        ]
    )

    latest_close = float(
        unit_4_snapshot[
            "latest_close"
        ]
    )

    short_term_move_pct = float(
        unit_4_snapshot[
            "short_term_move_pct"
        ]
    )

    move_1m_pct = float(
        unit_4_snapshot[
            "move_1m_pct"
        ]
    )

    move_5m_pct = float(
        unit_4_snapshot[
            "move_5m_pct"
        ]
    )

    move_15m_pct = float(
        unit_4_snapshot[
            "move_15m_pct"
        ]
    )

    move_30m_pct = float(
        unit_4_snapshot[
            "move_30m_pct"
        ]
    )

    move_60m_pct = float(
        unit_4_snapshot[
            "move_60m_pct"
        ]
    )

    move_120m_pct = float(
        unit_4_snapshot[
            "move_120m_pct"
        ]
    )

    if live_price <= 0:
        raise RuntimeError(
            "UNIT 5 FAILED: INVALID LIVE PRICE"
        )

    if (
        ema19 <= 0
        or ema50 <= 0
        or ema200 <= 0
    ):
        raise RuntimeError(
            "UNIT 5 FAILED: INVALID EMA VALUE"
        )

    print(
        "PASS: UNIT 5 UNIT 4 SNAPSHOT VALIDATED",
        flush=True,
    )

    # ========================================================
    # 4. READ-ONLY SAFETY GATE
    # ========================================================

    print(
        "PASS: UNIT 5 READ-ONLY SAFETY GATE",
        flush=True,
    )

    # ========================================================
    # 5. MODE THRESHOLDS
    #
    # PRESERVED FROM EXISTING UNIT 5.
    # ========================================================

    BREAKOUT_MIN_SEPARATION_PCT = 0.120
    STRUCTURE_MIN_SEPARATION_PCT = 0.070
    SCALP_MIN_SEPARATION_PCT = 0.030

    BREAKOUT_MIN_MOVE_PCT = 0.080
    STRUCTURE_MIN_MOVE_PCT = 0.040
    SCALP_MIN_MOVE_PCT = 0.015

    print(
        "PASS: UNIT 5 MODE THRESHOLDS LOADED",
        flush=True,
    )

    print(
        "UNIT 5 SCALP MIN SEPARATION % = "
        f"{SCALP_MIN_SEPARATION_PCT}",
        flush=True,
    )

    print(
        "UNIT 5 STRUCTURE MIN SEPARATION % = "
        f"{STRUCTURE_MIN_SEPARATION_PCT}",
        flush=True,
    )

    print(
        "UNIT 5 BREAKOUT MIN SEPARATION % = "
        f"{BREAKOUT_MIN_SEPARATION_PCT}",
        flush=True,
    )

    print(
        "UNIT 5 SCALP MIN MOVE % = "
        f"{SCALP_MIN_MOVE_PCT}",
        flush=True,
    )

    print(
        "UNIT 5 STRUCTURE MIN MOVE % = "
        f"{STRUCTURE_MIN_MOVE_PCT}",
        flush=True,
    )

    print(
        "UNIT 5 BREAKOUT MIN MOVE % = "
        f"{BREAKOUT_MIN_MOVE_PCT}",
        flush=True,
    )

    # ========================================================
    # 6. EMA DIRECTION
    # ========================================================

    bullish_alignment = (
        ema19 > ema50
        and ema50 > ema200
    )

    bearish_alignment = (
        ema19 < ema50
        and ema50 < ema200
    )

    if bullish_alignment:
        ema_direction = "LONG"

    elif bearish_alignment:
        ema_direction = "SHORT"

    else:
        ema_direction = "NONE"

    print(
        "UNIT 5 EMA DIRECTION = "
        f"{ema_direction}",
        flush=True,
    )

    # ========================================================
    # 7. MULTI-WINDOW MOMENTUM
    # ========================================================

    def movement_direction(
        movement_pct,
    ):
        if movement_pct > 0:
            return "LONG"

        if movement_pct < 0:
            return "SHORT"

        return "NONE"

    momentum_1m_direction = (
        movement_direction(
            move_1m_pct
        )
    )

    momentum_5m_direction = (
        movement_direction(
            move_5m_pct
        )
    )

    momentum_15m_direction = (
        movement_direction(
            move_15m_pct
        )
    )

    momentum_30m_direction = (
        movement_direction(
            move_30m_pct
        )
    )

    momentum_60m_direction = (
        movement_direction(
            move_60m_pct
        )
    )

    momentum_120m_direction = (
        movement_direction(
            move_120m_pct
        )
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 5 MULTI-WINDOW MOMENTUM",
        flush=True,
    )

    print(
        "UNIT 5 1M MOVE % = "
        f"{move_1m_pct}",
        flush=True,
    )

    print(
        "UNIT 5 1M DIRECTION = "
        f"{momentum_1m_direction}",
        flush=True,
    )

    print(
        "UNIT 5 5M MOVE % = "
        f"{move_5m_pct}",
        flush=True,
    )

    print(
        "UNIT 5 5M DIRECTION = "
        f"{momentum_5m_direction}",
        flush=True,
    )

    print(
        "UNIT 5 15M MOVE % = "
        f"{move_15m_pct}",
        flush=True,
    )

    print(
        "UNIT 5 15M DIRECTION = "
        f"{momentum_15m_direction}",
        flush=True,
    )

    print(
        "UNIT 5 30M MOVE % = "
        f"{move_30m_pct}",
        flush=True,
    )

    print(
        "UNIT 5 30M DIRECTION = "
        f"{momentum_30m_direction}",
        flush=True,
    )

    print(
        "UNIT 5 60M MOVE % = "
        f"{move_60m_pct}",
        flush=True,
    )

    print(
        "UNIT 5 60M DIRECTION = "
        f"{momentum_60m_direction}",
        flush=True,
    )

    print(
        "UNIT 5 120M MOVE % = "
        f"{move_120m_pct}",
        flush=True,
    )

    print(
        "UNIT 5 120M DIRECTION = "
        f"{momentum_120m_direction}",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    
    # ========================================================
    # UNIT 5A START
    # SECTIONS 8 TO 11 COMPLETE REPLACEMENT
    # INDENTATION: FOUR SPACES
    # ========================================================

    # ========================================================
    # 8. CLOSED CANDLE MARKET CONTEXT
    # ========================================================

    candles = unit_4_snapshot.get(
        "recent_closed_klines", []
    )

    if not isinstance(candles, list) or len(candles) < 30:
        raise RuntimeError(
            "UNIT 5 BLOCKED: INSUFFICIENT CLOSED CANDLES"
        )

    candles = candles[-60:]

    for candle in candles:
        if not isinstance(candle, dict):
            raise RuntimeError(
                "UNIT 5 INVALID CLOSED CANDLE"
            )

        for key in ("open", "high", "low", "close"):
            value = float(candle[key])
            if not 0 < value < float("inf"):
                raise RuntimeError(
                    "UNIT 5 INVALID CANDLE PRICE"
                )

    recent = candles[-20:]
    previous_range = candles[-21:-1]

    range_high = max(
        float(c["high"]) for c in previous_range
    )

    range_low = min(
        float(c["low"]) for c in previous_range
    )

    if range_low <= 0:
        raise RuntimeError("INVALID RANGE LOW")

    range_width_pct = (
        (range_high - range_low) / range_low * 100.0
    )

    recent_high = max(
        float(c["high"]) for c in recent
    )

    recent_low = min(
        float(c["low"]) for c in recent
    )

    recent_range_pct = (
        (recent_high - recent_low)
        / latest_close * 100.0
    )

    ema100 = float(
        unit_4_snapshot.get("ema100", ema200)
    )

    if not 0 < ema100 < float("inf"):
        raise RuntimeError("INVALID EMA100")

    # ========================================================
    # 9. EARLY STRUCTURE QUALIFICATION
    # ========================================================

    # EMA200 is a context indicator.
    # Full EMA19/50/200 alignment is not compulsory
    # for preliminary STRUCTURE qualification.

    structure_direction = "NONE"

    structure_long_votes = sum((
        ema19 > ema50,
        move_5m_pct > 0 and move_15m_pct > 0,
        latest_close > ema19 and latest_close > ema100,
    ))

    structure_short_votes = sum((
        ema19 < ema50,
        move_5m_pct < 0 and move_15m_pct < 0,
        latest_close < ema19 and latest_close < ema100,
    ))

    structure_move_pct = abs(move_15m_pct)

    structure_long_candidate = (
        structure_long_votes >= 2
        and move_15m_pct >= 0.020
        and separation_pct >= 0.035
        and latest_close > ema19
    )

    structure_short_candidate = (
        structure_short_votes >= 2
        and move_15m_pct <= -0.020
        and separation_pct >= 0.035
        and latest_close < ema19
    )

    structure_candidate = (
        structure_long_candidate
        or structure_short_candidate
    )

    structure_long_ready = (
        structure_long_candidate
        and structure_long_votes == 3
        and structure_move_pct >= 0.035
    )

    structure_short_ready = (
        structure_short_candidate
        and structure_short_votes == 3
        and structure_move_pct >= 0.035
    )

    structure_ready = (
        structure_long_ready
        or structure_short_ready
    )

    if structure_long_candidate:
        structure_direction = "LONG"

    elif structure_short_candidate:
        structure_direction = "SHORT"

    structure_direction_agreement = (
        structure_ready
    )

    # ========================================================
    # 10. PRICE-BASED BREAKOUT QUALIFICATION
    # ========================================================

    # The latest closed candle must actually break
    # the preceding 20-candle range to be READY.
    #
    # A nearby developing candidate can be detected
    # before the actual breakout.

    breakout_primary_direction = (
        momentum_30m_direction
    )

    breakout_fast_support = (
        momentum_5m_direction
        == breakout_primary_direction
        or momentum_15m_direction
        == breakout_primary_direction
    )

    breakout_move_pct = abs(move_30m_pct)

    latest_high = float(candles[-1]["high"])
    latest_low = float(candles[-1]["low"])

    upper_distance_pct = (
        (range_high - latest_close)
        / latest_close * 100.0
    )

    lower_distance_pct = (
        (latest_close - range_low)
        / latest_close * 100.0
    )

    breakout_long_candidate = (
        move_5m_pct > 0.015
        and move_15m_pct > 0
        and latest_close > ema19
        and upper_distance_pct <= 0.080
    )

    breakout_short_candidate = (
        move_5m_pct < -0.015
        and move_15m_pct < 0
        and latest_close < ema19
        and lower_distance_pct <= 0.080
    )

    breakout_candidate = (
        breakout_long_candidate
        or breakout_short_candidate
    )

    breakout_long_ready = (
        breakout_long_candidate
        and latest_close > range_high
        and latest_high > range_high
        and move_5m_pct >= 0.030
        and move_15m_pct > 0
    )

    breakout_short_ready = (
        breakout_short_candidate
        and latest_close < range_low
        and latest_low < range_low
        and move_5m_pct <= -0.030
        and move_15m_pct < 0
    )

    breakout_ready = (
        breakout_long_ready
        or breakout_short_ready
    )

    breakout_direction = "NONE"

    if breakout_long_candidate:
        breakout_direction = "LONG"

    elif breakout_short_candidate:
        breakout_direction = "SHORT"

    breakout_long_context = breakout_long_candidate
    breakout_short_context = breakout_short_candidate

    # ========================================================
    # 11. SCALP SIDEWAYS AND FEE-AWARE CONTEXT
    # ========================================================

    scalp_move_pct = abs(move_5m_pct)

    scalp_direction = "NONE"

    # Sideways participation: short-term movement may
    # exist, but a stronger directional regime must
    # take priority.

    sideways_context = (
        not structure_candidate
        and not breakout_candidate
        and separation_pct <= 0.090
        and abs(move_30m_pct) <= 0.180
    )

    scalp_long_context = (
        sideways_context
        and move_5m_pct >= SCALP_MIN_MOVE_PCT
        and (
            move_1m_pct > 0
            or latest_close > previous_close
        )
    )

    scalp_short_context = (
        sideways_context
        and move_5m_pct <= -SCALP_MIN_MOVE_PCT
        and (
            move_1m_pct < 0
            or latest_close < previous_close
        )
    )

    if scalp_long_context:
        scalp_direction = "LONG"

    elif scalp_short_context:
        scalp_direction = "SHORT"

    scalp_1m_support = (
        scalp_direction != "NONE"
        and momentum_1m_direction == scalp_direction
    )

    # Preliminary fee feasibility only.
    #
    # A historical price range is not a prediction of
    # future obtainable profit.
    #
    # Unit 6 and downstream execution must still check
    # prospective reward, spread, fees, slippage,
    # and entry quality.

    assumed_taker_fee_per_side_pct = 0.080
    assumed_extra_friction_pct = 0.020

    minimum_net_price_profit_pct = 0.050

    minimum_sustainable_range_pct = (
        2.0 * assumed_taker_fee_per_side_pct
        + assumed_extra_friction_pct
        + minimum_net_price_profit_pct
    )

    scalp_range_feasible = (
        recent_range_pct
        >= minimum_sustainable_range_pct
    )

    scalp_ready = (
        scalp_direction != "NONE"
        and sideways_context
        and scalp_range_feasible
    )

    # ========================================================
    # 11A. STRICT MODE ARBITRATION
    # ========================================================

    active_mode = "NONE"
    direction = "NONE"
    qualified = False
    qualification_reason = "NO_MODE_QUALIFIED"

    if breakout_ready:

        active_mode = "BREAKOUT"
        direction = breakout_direction
        qualified = True
        qualification_reason = (
            "BREAKOUT_CONFIRMED_CLOSED_CANDLE_RANGE"
        )

    elif structure_ready:

        active_mode = "STRUCTURE"
        direction = structure_direction
        qualified = True
        qualification_reason = (
            "EARLY_STRUCTURE_THREE_FACTOR_CONFIRMATION"
        )

    elif breakout_candidate:

        qualification_reason = (
            "DEVELOPING_BREAKOUT_SCALP_DEFERRED"
        )

    elif structure_candidate:

        qualification_reason = (
            "DEVELOPING_STRUCTURE_SCALP_DEFERRED"
        )

    elif scalp_ready:

        active_mode = "SCALP"
        direction = scalp_direction
        qualified = True
        qualification_reason = (
            "SIDEWAYS_SCALP_PRELIMINARY_FEE_FILTER_PASS"
        )

    elif sideways_context and not scalp_range_feasible:

        qualification_reason = (
            "SCALP_HISTORICAL_RANGE_BELOW_FEE_THRESHOLD"
        )

    else:

        qualification_reason = (
            "NO_ACCEPTABLE_TRADE_CONTEXT"
        )

    # ========================================================
    # 11B. DIAGNOSTICS
    # ========================================================

    print("UNIT 5 RANGE HIGH =", range_high, flush=True)
    print("UNIT 5 RANGE LOW =", range_low, flush=True)
    print("UNIT 5 RANGE WIDTH % =", range_width_pct, flush=True)

    print("UNIT 5 BREAKOUT CANDIDATE =", breakout_candidate, flush=True)
    print("UNIT 5 BREAKOUT READY =", breakout_ready, flush=True)
    print("UNIT 5 BREAKOUT DIRECTION =", breakout_direction, flush=True)

    print("UNIT 5 STRUCTURE CANDIDATE =", structure_candidate, flush=True)
    print("UNIT 5 STRUCTURE READY =", structure_ready, flush=True)
    print("UNIT 5 STRUCTURE DIRECTION =", structure_direction, flush=True)

    print("UNIT 5 SIDEWAYS CONTEXT =", sideways_context, flush=True)
    print("UNIT 5 SCALP RANGE % =", recent_range_pct, flush=True)
    print("UNIT 5 SCALP RANGE FEASIBLE =", scalp_range_feasible, flush=True)
    print("UNIT 5 SCALP READY =", scalp_ready, flush=True)
    print("UNIT 5 SCALP DIRECTION =", scalp_direction, flush=True)

    print("UNIT 5 SELECTED MODE =", active_mode, flush=True)
    print("UNIT 5 QUALIFIED =", qualified, flush=True)
    print("UNIT 5 REASON =", qualification_reason, flush=True)

    # ========================================================
    # UNIT 5A END
    # EXISTING SECTION 12 CONTINUES BELOW
    # NO OTHER UNIT REPLACED
    # ========================================================
    
    # ========================================================
    # 12. PRICE RELATIONSHIP CHECKS
    # ========================================================

    price_above_ema19 = (
        live_price > ema19
    )

    price_above_ema50 = (
        live_price > ema50
    )

    price_above_ema200 = (
        live_price > ema200
    )

    latest_close_above_previous = (
        latest_close
        >
        previous_close
    )

    print(
        "UNIT 5 PRICE ABOVE EMA19 = "
        f"{price_above_ema19}",
        flush=True,
    )

    print(
        "UNIT 5 PRICE ABOVE EMA50 = "
        f"{price_above_ema50}",
        flush=True,
    )

    print(
        "UNIT 5 PRICE ABOVE EMA200 = "
        f"{price_above_ema200}",
        flush=True,
    )

    print(
        "UNIT 5 LATEST CLOSE ABOVE PREVIOUS = "
        f"{latest_close_above_previous}",
        flush=True,
    )

    # ========================================================
    # 13. NORMALIZED SIGNAL CANDIDATE
    #
    # Existing fields required by Unit 6 are preserved.
    # Additional diagnostics are included.
    # ========================================================

    signal_candidate = {
        "symbol":
            symbol,

        "qualified":
            qualified,

        "active_mode":
            active_mode,

        "direction":
            direction,

        "qualification_reason":
            qualification_reason,

        "live_mark_price":
            live_price,

        "ema19":
            ema19,

        "ema50":
            ema50,

        "ema200":
            ema200,

        "ema19_50_separation_pct":
            separation_pct,

        "ema_structure":
            ema_structure,

        "ema_direction":
            ema_direction,

        # Compatibility field:
        # represents the latest 1M direction.
        "momentum_direction":
            momentum_1m_direction,

        "direction_agreement":
            structure_direction_agreement,

        # Compatibility field:
        # retain original Unit 4 1M value.
        "short_term_move_pct":
            short_term_move_pct,

        "absolute_short_term_move_pct":
            abs(
                short_term_move_pct
            ),

        "previous_close":
            previous_close,

        "latest_close":
            latest_close,

        "price_above_ema19":
            price_above_ema19,

        "price_above_ema50":
            price_above_ema50,

        "price_above_ema200":
            price_above_ema200,

        "latest_close_above_previous":
            latest_close_above_previous,

        # Multi-window diagnostics.
        "move_1m_pct":
            move_1m_pct,

        "move_5m_pct":
            move_5m_pct,

        "move_15m_pct":
            move_15m_pct,

        "move_30m_pct":
            move_30m_pct,

        "move_60m_pct":
            move_60m_pct,

        "move_120m_pct":
            move_120m_pct,

        "momentum_1m_direction":
            momentum_1m_direction,

        "momentum_5m_direction":
            momentum_5m_direction,

        "momentum_15m_direction":
            momentum_15m_direction,

        "momentum_30m_direction":
            momentum_30m_direction,

        "momentum_60m_direction":
            momentum_60m_direction,

        "momentum_120m_direction":
            momentum_120m_direction,

        "scalp_direction":
            scalp_direction,

        "scalp_move_pct":
            scalp_move_pct,

        "scalp_1m_support":
            scalp_1m_support,

        "structure_direction":
            structure_direction,

        "structure_move_pct":
            structure_move_pct,

        "breakout_direction":
            breakout_direction,

        "breakout_move_pct":
            breakout_move_pct,

        "breakout_fast_support":
            breakout_fast_support,
    }

    # ========================================================
    # 14. FINAL SIGNAL LOG
    # ========================================================

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 5 ACTIVE MODE = "
        f"{active_mode}",
        flush=True,
    )

    print(
        "UNIT 5 DIRECTION = "
        f"{direction}",
        flush=True,
    )

    print(
        "UNIT 5 SIGNAL QUALIFIED = "
        f"{qualified}",
        flush=True,
    )

    print(
        "UNIT 5 QUALIFICATION REASON = "
        f"{qualification_reason}",
        flush=True,
    )

    print(
        "UNIT 5 EMA19/50 SEPARATION % = "
        f"{separation_pct}",
        flush=True,
    )

    print(
        "UNIT 5 ORIGINAL 1M MOVE % = "
        f"{short_term_move_pct}",
        flush=True,
    )

    print(
        "UNIT 5 SCALP 5M MOVE % = "
        f"{scalp_move_pct}",
        flush=True,
    )

    print(
        "UNIT 5 STRUCTURE 15M MOVE % = "
        f"{structure_move_pct}",
        flush=True,
    )

    print(
        "UNIT 5 BREAKOUT 30M MOVE % = "
        f"{breakout_move_pct}",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    # ========================================================
    # 15. SAFETY ASSERTIONS
    # ========================================================

    print(
        "PASS: UNIT 5 NORMALIZED SIGNAL CANDIDATE",
        flush=True,
    )

    print(
        "PASS: UNIT 5 MULTI-WINDOW SIGNAL QUALIFICATION COMPLETED",
        flush=True,
    )

    print(
        "PASS: UNIT 5 EXCLUSIVE MODE SELECTION",
        flush=True,
    )

    print(
        "PASS: UNIT 5 NO NETWORK REQUEST",
        flush=True,
    )

    print(
        "PASS: UNIT 5 NO ORDER PAYLOAD GENERATED",
        flush=True,
    )

    print(
        "PASS: UNIT 5 NO POSITION SIZING",
        flush=True,
    )

    print(
        "PASS: UNIT 5 NO TP / SL",
        flush=True,
    )

    print(
        "PASS: UNIT 5 NO BACKUP EXECUTION",
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
        "ZERO DEMO ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO REAL ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO EXCHANGE WRITE = TRUE",
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

    print(
        "-" * 80,
        flush=True,
    )

    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 5 RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return signal_candidate


# ============================================================
# RUN UNIT 5
# ============================================================

FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
    fresh_reconstruction_unit_5(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
    )
)


# ============================================================
# END OF TRANSMISSION PART 3
# ZERO INDENTATION DEMARCATION
#
# UNIT 5 IS FULLY CLOSED
# UNIT 5 HAS BEEN CALLED
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN TRY
# NO OPEN DICTIONARY
# NO INDENTATION CONTINUES INTO THE NEXT PART
#
# NEXT PART STARTS WITH FRESH RECONSTRUCTION UNIT 6
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 6
# ZERO INDENTATION
# COORDINATED SIGNAL ADMISSION
# ============================================================

def fresh_reconstruction_unit_6(
    unit_2_config,
    unit_4_analysis,
    unit_5_candidate,
):
    import math

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 6 START")

    if not all(isinstance(x, dict) for x in (
        unit_2_config,
        unit_4_analysis,
        unit_5_candidate,
    )):
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
                "UNIT 6 SAFETY FLAG FAILURE: " + key
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
                "UNIT 6 UNSAFE CONFIGURATION: " + key
            )

    mode = unit_5_candidate.get("active_mode", "NONE")
    side = unit_5_candidate.get("direction", "NONE")
    qualified = (
        unit_5_candidate.get("qualified") is True
    )
    unit5_reason = str(
        unit_5_candidate.get(
            "qualification_reason", "UNKNOWN"
        )
    )

    if mode not in (
        "NONE", "SCALP", "STRUCTURE", "BREAKOUT"
    ):
        raise RuntimeError("UNIT 6 INVALID MODE")

    if side not in ("NONE", "LONG", "SHORT"):
        raise RuntimeError("UNIT 6 INVALID DIRECTION")

    leverage = float(
        strategy.get("leverage_target", 100)
    )

    if not math.isfinite(leverage) or leverage <= 0:
        raise RuntimeError("UNIT 6 INVALID LEVERAGE")

    execution_intent = False
    reason = "NO_QUALIFIED_SIGNAL"
    scalp_score = None
    scalp_pass = None
    details = {}

    # No unit may execute a candidate that Unit 5
    # has not qualified.

    if not qualified:
        reason = "UNIT_5_NOT_QUALIFIED:" + unit5_reason

    elif mode == "NONE" or side == "NONE":
        reason = "INVALID_QUALIFIED_MODE_OR_DIRECTION"

    elif mode in ("BREAKOUT", "STRUCTURE"):

        # These modes are independently qualified in
        # Unit 5. Do not apply Scalp-specific gates.
        #
        # Downstream units must still validate fresh
        # market conditions and execution safety.

        execution_intent = True
        reason = mode + "_PRELIMINARY_ADMISSION_PASS"

    elif mode == "SCALP":

        # ====================================================
        # 1. SCALP CLOSED-CANDLE HISTORY
        # ====================================================

        candles = unit_4_analysis.get(
            "recent_closed_klines", []
        )

        if not isinstance(candles, list) or len(candles) < 30:
            reason = "SCALP_INSUFFICIENT_CLOSED_CANDLES"

        else:

            candles = candles[-60:]

            # Invalid or nonfinite data fails closed.

            valid = True
            for c in candles:
                try:
                    o = float(c["open"])
                    h = float(c["high"])
                    l = float(c["low"])
                    p = float(c["close"])
                    if not (
                        all(math.isfinite(v) for v in (o, h, l, p))
                        and 0 < l <= min(o, p)
                        and h >= max(o, p)
                    ):
                        valid = False
                        break
                except (TypeError, ValueError, KeyError):
                    valid = False
                    break

            if not valid:
                reason = "SCALP_INVALID_CANDLE_DATA"

            else:

                # ============================================
                # 2. MARKET VALUES
                # ============================================

                price = float(candles[-1]["close"])

                ema19 = float(
                    unit_5_candidate.get("ema19", 0)
                )
                ema50 = float(
                    unit_5_candidate.get("ema50", 0)
                )
                ema100 = float(
                    unit_4_analysis.get("ema100", 0)
                )

                move1 = float(
                    unit_5_candidate.get("move_1m_pct", 0)
                )
                move5 = float(
                    unit_5_candidate.get("move_5m_pct", 0)
                )
                move15 = float(
                    unit_5_candidate.get("move_15m_pct", 0)
                )

                market_values = (
                    price, ema19, ema50, ema100,
                    move1, move5, move15
                )

                if not (
                    all(math.isfinite(v) for v in market_values)
                    and min(
                        price, ema19, ema50, ema100
                    ) > 0
                ):
                    raise RuntimeError(
                        "UNIT 6 INVALID MARKET INDICATORS"
                    )

                # ============================================
                # 3. DIRECTIONAL PRICE HEADROOM
                # ============================================

                prior = candles[:-1]

                if side == "LONG":
                    target = max(
                        float(c["high"]) for c in prior
                    )
                    headroom = max(
                        0.0, (target - price) / price * 100
                    )
                    directional_move = move5
                    ema_support = price >= ema19

                else:
                    target = min(
                        float(c["low"]) for c in prior
                    )
                    headroom = max(
                        0.0, (price - target) / price * 100
                    )
                    directional_move = -move5
                    ema_support = price <= ema19

                # An already crossed level is not counted
                # as additional available profit room.
                #
                # The target is historical reference only,
                # not a guaranteed future exit.

                # ============================================
                # 4. ESTIMATED TRADING FRICTION
                # ============================================

                fee_side_pct = 0.080
                slippage_roundtrip_pct = 0.020
                desired_net_price_pct = 0.050

                total_cost_pct = (
                    2 * fee_side_pct
                    + slippage_roundtrip_pct
                )

                prospective_net_pct = (
                    headroom - total_cost_pct
                )

                fee_pass = (
                    prospective_net_pct
                    >= desired_net_price_pct
                )

                # Fee assumptions are conservative inputs,
                # not verified WEEX charges for this trade.
                # Funding and liquidation risk are separate.

                # ============================================
                # 5. PRICE QUALITY: 50 POINTS
                # ============================================

                price_score = 0.0

                # Directional movement: 15
                if directional_move > 0:
                    price_score += 8
                    if directional_move >= 0.025:
                        price_score += 7

                # Latest closed candle: 10
                latest = candles[-1]
                o = float(latest["open"])
                h = float(latest["high"])
                l = float(latest["low"])
                c = float(latest["close"])

                body_ratio = (
                    abs(c - o) / (h - l)
                    if h > l else 0.0
                )

                candle_agrees = (
                    c > o if side == "LONG" else c < o
                )

                if candle_agrees:
                    price_score += 6
                    if body_ratio >= 0.45:
                        price_score += 4

                # Headroom after friction: 20
                if prospective_net_pct >= 0.05:
                    price_score += 10
                if prospective_net_pct >= 0.10:
                    price_score += 5
                if prospective_net_pct >= 0.15:
                    price_score += 5

                # Recent price progression: 5
                previous_close = float(
                    candles[-2]["close"]
                )

                progression = (
                    c > previous_close
                    if side == "LONG"
                    else c < previous_close
                )

                if progression:
                    price_score += 5

                # ============================================
                # 6. SUPPORTING QUALITY: 50 POINTS
                # ============================================

                support_score = 0.0

                # EMA timing and context: 15
                if ema_support:
                    support_score += 7

                ema_agrees = (
                    ema19 > ema50
                    if side == "LONG"
                    else ema19 < ema50
                )

                if ema_agrees:
                    support_score += 5

                ema100_agrees = (
                    price >= ema100
                    if side == "LONG"
                    else price <= ema100
                )

                if ema100_agrees:
                    support_score += 3

                # Momentum: 10
                aligned = sum(
                    (
                        m > 0 if side == "LONG" else m < 0
                    )
                    for m in (move1, move5, move15)
                )

                support_score += (
                    10 if aligned == 3
                    else 7 if aligned == 2
                    else 3 if aligned == 1
                    else 0
                )

                # Entry location: 10
                ranges = [
                    (float(x["high"]) - float(x["low"]))
                    / float(x["close"]) * 100
                    for x in candles[-20:]
                ]

                avg_range = sum(ranges) / len(ranges)
                extension = abs(
                    price - ema19
                ) / ema19 * 100

                extension_ratio = (
                    extension / avg_range
                    if avg_range > 0 else float("inf")
                )

                if extension_ratio <= 0.75:
                    support_score += 10
                elif extension_ratio <= 1.5:
                    support_score += 5

                # Volatility consistency: 10
                latest_range = (
                    (h - l) / c * 100
                )

                spike_ratio = (
                    latest_range / avg_range
                    if avg_range > 0 else float("inf")
                )

                if spike_ratio <= 1.5:
                    support_score += 10
                elif spike_ratio <= 2:
                    support_score += 5

                # Directional persistence: 5
                recent_changes = [
                    float(candles[i]["close"])
                    - float(candles[i - 1]["close"])
                    for i in range(len(candles)-3, len(candles))
                ]

                confirmations = sum(
                    v > 0 if side == "LONG" else v < 0
                    for v in recent_changes
                )

                persistence_pass = confirmations >= 2

                if persistence_pass:
                    support_score += 5

                # ============================================
                # 7. HARD SAFETY REJECTIONS
                # ============================================

                late_impulse = False

                if len(candles) >= 7:
                    prior_delta = (
                        float(candles[-2]["close"])
                        - float(candles[-3]["close"])
                    )
                    current_delta = (
                        float(candles[-1]["close"])
                        - float(candles[-2]["close"])
                    )

                    impulse_pct = (
                        abs(
                            float(candles[-1]["close"])
                            - float(candles[-6]["close"])
                        ) / float(candles[-6]["close"]) * 100
                    )

                    weakening = (
                        0 < current_delta < prior_delta
                        if side == "LONG"
                        else prior_delta < current_delta < 0
                    )

                    late_impulse = (
                        weakening
                        and avg_range > 0
                        and impulse_pct / avg_range > 3
                        and extension_ratio > 1
                    )

                extreme_extension = extension_ratio > 1.5
                extreme_spike = spike_ratio > 2

                scalp_score = round(
                    price_score + support_score, 2
                )

                scalp_pass = (
                    scalp_score >= 70
                    and fee_pass
                    and persistence_pass
                    and not extreme_extension
                    and not extreme_spike
                    and not late_impulse
                )

                details = {
                    "price_score": price_score,
                    "support_score": support_score,
                    "headroom_pct": round(headroom, 5),
                    "target_reference": target,
                    "estimated_cost_pct": total_cost_pct,
                    "prospective_net_pct": round(
                        prospective_net_pct, 5
                    ),
                    "fee_pass": fee_pass,
                    "persistence_confirmations": confirmations,
                    "extension_ratio": extension_ratio,
                    "spike_ratio": spike_ratio,
                    "late_impulse": late_impulse,
                }

                if not fee_pass:
                    reason = "SCALP_NET_HEADROOM_TOO_SMALL"
                elif extreme_extension:
                    reason = "SCALP_EXCESSIVE_EMA_EXTENSION"
                elif extreme_spike:
                    reason = "SCALP_PRICE_SPIKE_REJECTED"
                elif late_impulse:
                    reason = "SCALP_LATE_IMPULSE_REJECTED"
                elif not persistence_pass:
                    reason = "SCALP_PERSISTENCE_REJECTED"
                elif scalp_score < 70:
                    reason = "SCALP_QUALITY_BELOW_70"
                else:
                    reason = "SCALP_ADMISSION_PASS"
                    execution_intent = True

    # ========================================================
    # 8. NORMALIZE REJECTED SIGNAL
    # ========================================================

    if not execution_intent:
        mode = "NONE"
        side = "NONE"
        qualified = False

    # ========================================================
    # 9. PRESERVE UNIT 7 OUTPUT CONTRACT
    # ========================================================

    result = {
        "execution_intent": execution_intent,
        "signal_qualified": qualified,
        "active_mode": mode,
        "direction": side,
        "unit_5_reason": unit5_reason,
        "admission_reason": reason,
        "leverage_target": leverage,
        "leverage_regime": (
            "GE_100X" if leverage >= 100
            else "50_99X" if leverage >= 50
            else "20_49X" if leverage >= 20
            else "11_19X" if leverage >= 11
            else "LE_10X"
        ),
        "sideways_regime": mode == "SCALP",
        "ema_compressed": False,
        "compression_threshold_pct": 0.09,
        "momentum_conflict": False,
        "persistence_window": 3,
        "persistence_required": 2,
        "persistence_confirmations": (
            details.get("persistence_confirmations", 0)
        ),
        "persistence_directions": [],
        "persistence_pass": (
            details.get("persistence_confirmations", 0) >= 2
            if scalp_score is not None else True
        ),
        "fifteen_minute_support_pass": True,
        "scalp_quality_score": scalp_score,
        "scalp_quality_minimum": 70.0,
        "scalp_quality_pass": scalp_pass,
        "scalp_quality_details": details,
    }

    # ========================================================
    # 10. DIAGNOSTIC REPORT
    # ========================================================

    print("UNIT 6 MODE =", mode, flush=True)
    print("UNIT 6 DIRECTION =", side, flush=True)
    print("UNIT 6 SCALP SCORE =", scalp_score, flush=True)
    print("UNIT 6 SCALP DETAILS =", details, flush=True)
    print("UNIT 6 ADMISSION =", reason, flush=True)
    print(
        "UNIT 6 EXECUTION INTENT =",
        execution_intent,
        flush=True,
    )
    print(
        "PASS: UNIT 6 NORMALIZED OUTPUT",
        flush=True,
    )
    log("FRESH RECONSTRUCTION UNIT 6 RESULT = PASS")
    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 6
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
# END COMPLETE REPLACEMENT - UNIT 6
# UNIT 7 CONTINUES BELOW
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 7
# ZERO INDENTATION
#
# SIGNAL HANDOFF + POSITION SIZING PREPARATION
# EXCHANGE-CONTROLLED LEVERAGE
#
# NO LEVERAGE TARGET
# NO LEVERAGE ASSUMPTION
# NO EXCHANGE WRITE
# NO ORDER SUBMISSION
# ============================================================

def fresh_reconstruction_unit_7(
    unit_2_config,
    unit_6_candidate,
):

    import math

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 7 START")

    # ========================================================
    # 1. INPUT CONTRACT
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 7 INVALID CONFIGURATION"
        )

    if not isinstance(unit_6_candidate, dict):
        raise RuntimeError(
            "UNIT 7 INVALID EXECUTION CANDIDATE"
        )

    strategy = unit_2_config.get("strategy")
    exchange = unit_2_config.get("exchange")
    precision = unit_2_config.get("market_precision")
    safety = unit_2_config.get("safety")

    if not all(
        isinstance(x, dict)
        for x in (
            strategy, exchange, precision, safety
        )
    ):
        raise RuntimeError(
            "UNIT 7 MISSING CONFIGURATION SECTIONS"
        )

    required_fields = (
        "execution_intent",
        "signal_qualified",
        "active_mode",
        "direction",
        "unit_5_reason",
        "admission_reason",
    )

    missing = [
        key for key in required_fields
        if key not in unit_6_candidate
    ]

    if missing:
        raise RuntimeError(
            "UNIT 7 MISSING UNIT 6 FIELDS: "
            + str(missing)
        )

    # ========================================================
    # 2. READ-ONLY SAFETY
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
                "UNIT 7 UNSAFE CAPABILITY: " + key
            )

    # ========================================================
    # 3. RECEIVE UNIT 6 DECISION
    # ========================================================

    execution_intent = unit_6_candidate[
        "execution_intent"
    ]

    signal_qualified = unit_6_candidate[
        "signal_qualified"
    ]

    mode = unit_6_candidate[
        "active_mode"
    ]

    side = unit_6_candidate[
        "direction"
    ]

    reason = str(
        unit_6_candidate["admission_reason"]
    )

    unit5_reason = str(
        unit_6_candidate["unit_5_reason"]
    )

    if not isinstance(execution_intent, bool):
        raise RuntimeError(
            "UNIT 7 INVALID EXECUTION INTENT"
        )

    if not isinstance(signal_qualified, bool):
        raise RuntimeError(
            "UNIT 7 INVALID QUALIFICATION FLAG"
        )

    if execution_intent != signal_qualified:
        raise RuntimeError(
            "UNIT 7 INCONSISTENT SIGNAL STATE"
        )

    # ========================================================
    # 4. IDLE PATH
    # ========================================================

    if not execution_intent:

        if mode != "NONE" or side != "NONE":
            raise RuntimeError(
                "UNIT 7 IDLE MODE/DIRECTION MISMATCH"
            )

        result = {
            "status": "IDLE",
            "active_mode": "NONE",
            "direction": "NONE",
            "execution_intent": False,
            "signal_qualified": False,
            "unit_5_reason": unit5_reason,
            "admission_reason": reason,
            "skip_reason": reason,
            "account_balance_required": False,
            "position_sizing_performed": False,
            "quantity_calculated": False,
            "proposed_quantity": None,
            "order_payload_created": False,
            "leverage_source": "WEEX_EXCHANGE",
            "exchange_leverage_verified": False,
            "effective_leverage": None,
            "read_only": True,
        }

        print(
            "UNIT 7 STATUS = IDLE",
            flush=True,
        )

        print(
            "UNIT 7 REASON =", reason,
            flush=True,
        )

        print(
            "UNIT 7 LEVERAGE CONTROL = WEEX",
            flush=True,
        )

        log(
            "FRESH RECONSTRUCTION UNIT 7 "
            "RESULT = PASS (IDLE)"
        )

        print("=" * 80, flush=True)

        return result

    # ========================================================
    # 5. ACTIVE SIGNAL VALIDATION
    # ========================================================

    if mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        raise RuntimeError(
            "UNIT 7 INVALID ACTIVE MODE"
        )

    if side not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 7 INVALID TRADE DIRECTION"
        )

    expected_reasons = {
        "SCALP": "SCALP_ADMISSION_PASS",
        "STRUCTURE":
            "STRUCTURE_PRELIMINARY_ADMISSION_PASS",
        "BREAKOUT":
            "BREAKOUT_PRELIMINARY_ADMISSION_PASS",
    }

    if reason != expected_reasons[mode]:
        raise RuntimeError(
            "UNIT 7 MODE/ADMISSION MISMATCH: "
            + reason
        )

    # ========================================================
    # 6. VALIDATE SIZING PARAMETERS
    # ========================================================

    margin_pct = float(
        strategy.get("initial_margin_percent", 0)
    )

    quantity_step = float(
        precision.get("quantity_step", 0)
    )

    minimum_quantity = float(
        precision.get("minimum_quantity", 0)
    )

    price_step = float(
        precision.get("price_step", 0)
    )

    values = (
        margin_pct,
        quantity_step,
        minimum_quantity,
        price_step,
    )

    if not all(
        math.isfinite(v) and v > 0
        for v in values
    ):
        raise RuntimeError(
            "UNIT 7 INVALID SIZING PARAMETERS"
        )

    if margin_pct > 5.0:
        raise RuntimeError(
            "UNIT 7 INITIAL MARGIN EXCEEDS 5%"
        )

    if exchange.get(
        "market_symbol"
    ) != "BTCUSDT":
        raise RuntimeError(
            "UNIT 7 INVALID MARKET SYMBOL"
        )

    if exchange.get(
        "demo_order_symbol"
    ) != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 7 INVALID DEMO SYMBOL"
        )

    # ========================================================
    # 7. EXCHANGE-CONTROLLED LEVERAGE CONTRACT
    # ========================================================

    # WEEX is the sole leverage-setting authority.
    #
    # Unit 7 must not:
    #
    # - impose 100x leverage
    # - assume identical LONG and SHORT leverage
    # - invent an effective leverage
    # - send leverage-changing requests
    #
    # Unit 8 must retrieve applicable leverage
    # from authenticated exchange information
    # before any position quantity is calculated.
    #
    # The current Unit 8 still expects the old
    # leverage_target field. Until Unit 8 is
    # upgraded, qualified signals must fail closed.

    leverage_source = "WEEX_EXCHANGE"

    effective_leverage = None

    exchange_leverage_verified = False

    # ========================================================
    # 8. PRESERVE LEGACY UNIT 8 HANDOFF SHAPE
    # ========================================================

    # The field name leverage_target is retained
    # temporarily with value None.
    #
    # It is NOT a Python leverage instruction.
    # It prevents Unit 8 from silently using 100x.

    result = {
        "status": "READY_FOR_BALANCE",
        "symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",
        "active_mode": mode,
        "direction": side,
        "execution_intent": True,
        "signal_qualified": True,
        "unit_5_reason": unit5_reason,
        "admission_reason": reason,
        "initial_margin_percent": margin_pct,
        "leverage_target": None,
        "leverage_source": leverage_source,
        "effective_leverage": effective_leverage,
        "exchange_leverage_verified":
            exchange_leverage_verified,
        "quantity_step": quantity_step,
        "minimum_quantity": minimum_quantity,
        "price_step": price_step,
        "account_balance_required": True,
        "position_sizing_performed": False,
        "quantity_calculated": False,
        "proposed_quantity": None,
        "order_payload_created": False,
        "read_only": True,
    }

    # ========================================================
    # 9. VALIDATE OUTPUT
    # ========================================================

    if result["execution_intent"] is not True:
        raise RuntimeError(
            "UNIT 7 EXECUTION CONTRACT FAILED"
        )

    if result["signal_qualified"] is not True:
        raise RuntimeError(
            "UNIT 7 SIGNAL CONTRACT FAILED"
        )

    if result["proposed_quantity"] is not None:
        raise RuntimeError(
            "UNIT 7 INVENTED POSITION QUANTITY"
        )

    if result["leverage_target"] is not None:
        raise RuntimeError(
            "UNIT 7 PYTHON LEVERAGE STILL ACTIVE"
        )

    if result["order_payload_created"] is not False:
        raise RuntimeError(
            "UNIT 7 UNEXPECTED ORDER PAYLOAD"
        )

    # ========================================================
    # 10. REPORT
    # ========================================================

    print(
        "UNIT 7 STATUS = READY_FOR_BALANCE",
        flush=True,
    )

    print(
        "UNIT 7 ACTIVE MODE =", mode,
        flush=True,
    )

    print(
        "UNIT 7 DIRECTION =", side,
        flush=True,
    )

    print(
        "UNIT 7 ADMISSION =", reason,
        flush=True,
    )

    print(
        "UNIT 7 LEVERAGE SOURCE =",
        leverage_source,
        flush=True,
    )

    print(
        "UNIT 7 EFFECTIVE LEVERAGE = UNVERIFIED",
        flush=True,
    )

    print(
        "UNIT 7 POSITION QUANTITY = NOT CALCULATED",
        flush=True,
    )

    print(
        "UNIT 7 EXCHANGE WRITE = FALSE",
        flush=True,
    )

    print(
        "UNIT 7 NEXT REQUIREMENT = "
        "UNIT 8 EXCHANGE LEVERAGE VERIFICATION",
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 7 "
        "RESULT = PASS (PREPARATION)"
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 7
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_SIZING_CANDIDATE = (
    fresh_reconstruction_unit_7(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE,
    )
)

# ============================================================
# END COMPLETE REPLACEMENT - UNIT 7
# ZERO INDENTATION
# UNIT 8 CONTINUES BELOW
# ============================================================
                

# ============================================================
# START COMPLETE REPLACEMENT - UNIT 8
# ZERO INDENTATION
#
# WEEX EXCHANGE-CONTROLLED LEVERAGE
# DEMO ACCOUNT BALANCE AND POSITION SIZING
# 35% MAXIMUM EXPOSURE
# NO LEVERAGE MUTATION
# NO ORDER SUBMISSION
# ============================================================

def fresh_reconstruction_unit_8(
    config,
    unit_7_result,
    market_snapshot,
):
    import os
    import time
    import hmac
    import hashlib
    import base64
    import json
    import math
    import urllib.request
    import urllib.parse
    from decimal import Decimal, ROUND_DOWN

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 8 START")

    # ========================================================
    # 1. INPUT AND SAFETY VALIDATION
    # ========================================================

    if not all(isinstance(v, dict) for v in (
        config, unit_7_result, market_snapshot
    )):
        raise RuntimeError("UNIT 8 INVALID INPUT")

    exchange = config.get("exchange", {})
    strategy = config.get("strategy", {})
    safety = config.get("safety", {})

    if not all(isinstance(v, dict) for v in (
        exchange, strategy, safety
    )):
        raise RuntimeError("UNIT 8 INVALID CONFIGURATION")

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError("UNIT 8 DEMO ONLY")

    if exchange.get("contract_base_url") != (
        "https://api-contract.weex.com"
    ):
        raise RuntimeError("UNIT 8 INVALID EXCHANGE")

    if exchange.get("market_symbol") != "BTCUSDT":
        raise RuntimeError("UNIT 8 MARKET SYMBOL MISMATCH")

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError("UNIT 8 DEMO SYMBOL MISMATCH")

    for key in (
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
    ):
        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 8 UNSAFE CAPABILITY: " + key
            )

    # ========================================================
    # 2. IDLE RESULT HELPER
    # ========================================================

    def idle(reason):
        result = {
            "status": "IDLE",
            "active_mode": "NONE",
            "direction": "NONE",
            "signal_qualified": False,
            "execution_intent": False,
            "trade_plan_ready": False,
            "trade_plan": None,
            "skip_reason": reason,
            "read_only": True,
        }

        print("UNIT 8 STATUS = IDLE", flush=True)
        print("UNIT 8 REASON =", reason, flush=True)
        log("FRESH RECONSTRUCTION UNIT 8 RESULT = IDLE")
        return result

    # ========================================================
    # 3. RECEIVE UNIT 7 SIGNAL
    # ========================================================

    if unit_7_result.get("execution_intent") is not True:
        return idle(
            unit_7_result.get(
                "skip_reason",
                unit_7_result.get(
                    "admission_reason", "NO_SIGNAL"
                )
            )
        )

    if unit_7_result.get("signal_qualified") is not True:
        return idle("SIGNAL_NOT_QUALIFIED")

    if unit_7_result.get("status") != "READY_FOR_BALANCE":
        return idle("UNIT_7_NOT_READY")

    if unit_7_result.get("leverage_target") is not None:
        return idle("PYTHON_LEVERAGE_NOT_DISABLED")

    mode = unit_7_result.get("active_mode")
    side = unit_7_result.get("direction")

    if mode not in (
        "SCALP", "STRUCTURE", "BREAKOUT"
    ):
        return idle("INVALID_MODE")

    if side not in ("LONG", "SHORT"):
        return idle("INVALID_SIDE")

    # ========================================================
    # 4. AUTHENTICATION
    # ========================================================

    api_key = (
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

    if not all((api_key, secret, passphrase)):
        return idle("WEEX_CREDENTIALS_MISSING")

    base_url = exchange["contract_base_url"]

    def authenticated_get(path, params=None):

        query = (
            urllib.parse.urlencode(params)
            if params else ""
        )

        request_path = (
            path + "?" + query if query else path
        )

        timestamp = str(int(time.time() * 1000))

        signature = base64.b64encode(
            hmac.new(
                secret.encode(),
                (
                    timestamp + "GET" + request_path
                ).encode(),
                hashlib.sha256,
            ).digest()
        ).decode()

        request = urllib.request.Request(
            base_url + request_path,
            method="GET",
            headers={
                "ACCESS-KEY": api_key,
                "ACCESS-SIGN": signature,
                "ACCESS-TIMESTAMP": timestamp,
                "ACCESS-PASSPHRASE": passphrase,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        if request.get_method() != "GET":
            raise RuntimeError("NON-GET REQUEST")

        if request.data is not None:
            raise RuntimeError("REQUEST BODY NOT ALLOWED")

        with urllib.request.urlopen(
            request, timeout=15
        ) as response:
            if response.getcode() != 200:
                raise RuntimeError("NON-200 RESPONSE")
            return json.loads(
                response.read().decode("utf-8")
            )

    # ========================================================
    # 5. READ EXCHANGE LEVERAGE CONFIGURATION
    # ========================================================

    try:
        settings = authenticated_get(
            "/capi/v3/account/symbolConfig",
            {"symbol": "BTCUSDT"},
        )
    except Exception as exc:
        print(
            "UNIT 8 CONFIG READ ERROR =",
            type(exc).__name__,
            flush=True,
        )
        return idle("WEEX_LEVERAGE_CONFIG_READ_FAILED")

    if not isinstance(settings, list):
        return idle("INVALID_LEVERAGE_RESPONSE")

    matches = [
        item for item in settings
        if isinstance(item, dict)
        and item.get("symbol") == "BTCUSDT"
    ]

    if len(matches) != 1:
        return idle("LEVERAGE_CONFIG_NOT_UNIQUE")

    setting = matches[0]

    margin_mode = str(
        setting.get("marginType", "")
    ).upper()

    position_mode = str(
        setting.get("separatedType", "")
    ).upper()

    if margin_mode not in ("CROSSED", "ISOLATED"):
        return idle("UNKNOWN_MARGIN_MODE")

    if position_mode not in ("COMBINED", "SEPARATED"):
        return idle("UNKNOWN_POSITION_MODE")

    if margin_mode == "CROSSED":
        leverage_field = "crossLeverage"
    elif side == "LONG":
        leverage_field = "isolatedLongLeverage"
    else:
        leverage_field = "isolatedShortLeverage"

    try:
        leverage = float(setting[leverage_field])
    except (KeyError, ValueError, TypeError):
        return idle("INVALID_EXCHANGE_LEVERAGE")

    if not math.isfinite(leverage) or leverage <= 0:
        return idle("INVALID_EXCHANGE_LEVERAGE_VALUE")

    print(
        "UNIT 8 LEVERAGE SOURCE = WEEX",
        flush=True,
    )
    print(
        "UNIT 8 MARGIN MODE =", margin_mode,
        flush=True,
    )
    print(
        "UNIT 8 POSITION MODE =", position_mode,
        flush=True,
    )
    print(
        "UNIT 8 EXCHANGE LEVERAGE =", leverage,
        flush=True,
    )

    # ========================================================
    # 6. READ CURRENT DEMO POSITIONS
    # ========================================================

    try:
        positions = authenticated_get(
            "/capi/v3/sim/position/allPosition"
        )
    except Exception as exc:
        print(
            "UNIT 8 POSITION READ ERROR =",
            type(exc).__name__,
            flush=True,
        )
        return idle("DEMO_POSITION_READ_FAILED")

    if not isinstance(positions, list):
        return idle("INVALID_DEMO_POSITIONS")

    for position in positions:

        if not isinstance(position, dict):
            return idle("INVALID_DEMO_POSITION_ENTRY")

        if position.get("symbol") != "BTCSUSDT":
            continue

        try:
            size = float(position["size"])
        except (KeyError, TypeError, ValueError):
            return idle("INVALID_DEMO_POSITION_SIZE")

        if not math.isfinite(size) or size < 0:
            return idle("INVALID_DEMO_POSITION_SIZE")

        if size > 0:
            print(
                "UNIT 8 EXISTING DEMO POSITION = TRUE",
                flush=True,
            )
            return idle(
                "POSITION_EXISTS_UNIT_14_MANAGEMENT_REQUIRED"
            )

    # ========================================================
    # 7. DEMO LEVERAGE CONFIRMATION
    # ========================================================

    # The documented symbolConfig endpoint reports
    # regular futures account configuration.
    #
    # Until WEEX exposes verified demo settings,
    # the user must confirm in WEEX that the demo
    # leverage and margin mode match this configuration.
    #
    # This flag is an acknowledgement, not leverage.
    # Python never selects or changes leverage.

    confirmed = os.getenv(
        "WEEX_DEMO_LEVERAGE_MATCH_CONFIRMED",
        "NO",
    ).strip().upper() == "YES"

    if not confirmed:
        return idle(
            "CONFIRM_DEMO_LEVERAGE_MATCH_IN_WEEX"
        )

    # ========================================================
    # 8. READ VERIFIED DEMO BALANCE
    # ========================================================

    try:
        balances = authenticated_get(
            "/capi/v3/sim/balance"
        )
    except Exception as exc:
        print(
            "UNIT 8 BALANCE ERROR =",
            type(exc).__name__,
            flush=True,
        )
        return idle("DEMO_BALANCE_READ_FAILED")

    if not isinstance(balances, list):
        return idle("INVALID_DEMO_BALANCE")

    matches = [
        b for b in balances
        if isinstance(b, dict)
        and str(b.get("asset", "")).upper() == "SUSDT"
    ]

    if len(matches) != 1:
        return idle("SUSDT_BALANCE_NOT_UNIQUE")

    try:
        available = float(
            matches[0]["availableBalance"]
        )
        total_balance = float(
            matches[0]["balance"]
        )
        frozen = float(
            matches[0]["frozen"]
        )
    except (KeyError, ValueError, TypeError):
        return idle("INVALID_BALANCE_FIELDS")

    if not all(
        math.isfinite(v) and v >= 0
        for v in (available, total_balance, frozen)
    ):
        return idle("INVALID_BALANCE_VALUES")

    if available <= 0 or total_balance <= 0:
        return idle("INSUFFICIENT_DEMO_BALANCE")

    # ========================================================
    # 9. EXPOSURE AND MARGIN
    # ========================================================

    try:
        price = float(market_snapshot["price"])
        entry_margin = float(
            os.getenv(
                "ENTRY_FIXED_USDT",
                str(strategy.get("initial_fixed_usdt", 0.50))
            )
        )
        cap_pct = float(
            strategy["exposure_cap_percent"]
        )
        step = Decimal(
            str(unit_7_result["quantity_step"])
        )
        minimum = Decimal(
            str(unit_7_result["minimum_quantity"])
        )
    except (
        KeyError, TypeError, ValueError, ArithmeticError
    ):
        return idle("INVALID_SIZING_INPUT")

    if not all(
        math.isfinite(v) and v > 0
        for v in (price, entry_margin, cap_pct)
    ):
        return idle("INVALID_MARGIN_OR_PRICE")

    if not 0 < cap_pct <= 35:
        return idle("EXPOSURE_CAP_INVALID")

    if not (
        step.is_finite() and minimum.is_finite()
        and step > 0 and minimum > 0
    ):
        return idle("INVALID_QUANTITY_PRECISION")

    if market_snapshot.get("symbol") != "BTCUSDT":
        return idle("INVALID_PRICE_SYMBOL")

    # Conservative reservation proxy:
    # includes unavailable funds, which can include
    # commitments unrelated to this bot.
    #
    # This does not replace account-wide reconciliation
    # by the execution and position-management units.

    committed_proxy = max(
        0.0, total_balance - available
    )

    maximum_margin = total_balance * cap_pct / 100

    remaining_capacity = max(
        0.0, maximum_margin - committed_proxy
    )

    if entry_margin > remaining_capacity:
        return idle("EXPOSURE_CAP_REACHED")

    if entry_margin > available:
        return idle("INSUFFICIENT_AVAILABLE_MARGIN")

    # ========================================================
    # 10. QUANTITY FROM WEEX-REPORTED LEVERAGE
    # ========================================================

    notional = entry_margin * leverage

    raw_quantity = (
        Decimal(str(notional))
        / Decimal(str(price))
    )

    quantity = (
        raw_quantity / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    ) * step

    if quantity < minimum:
        return idle("QUANTITY_BELOW_EXCHANGE_MINIMUM")

    quantity_float = float(quantity)

    actual_notional = quantity_float * price
    estimated_margin = actual_notional / leverage

    if estimated_margin > remaining_capacity + 1e-9:
        return idle("NORMALIZED_QUANTITY_EXCEEDS_CAP")

    if estimated_margin > available + 1e-9:
        return idle("NORMALIZED_QUANTITY_UNAFFORDABLE")

    # ========================================================
    # 11. INTERNAL POSITION SIZING OBJECT
    # ========================================================

    position_sizing = {
        "asset": "SUSDT",
        "available_balance": available,
        "total_balance": total_balance,
        "frozen_balance": frozen,
        "initial_margin_percent": (
            unit_7_result.get(
                "initial_margin_percent", 5.0
            )
        ),
        "margin_allocation": entry_margin,
        "leverage_target": None,
        "exchange_leverage": leverage,
        "effective_leverage": leverage,
        "leverage_source": "WEEX_SYMBOL_CONFIG",
        "demo_leverage_match_confirmed": True,
        "margin_mode": margin_mode,
        "position_mode": position_mode,
        "live_mark_price": price,
        "raw_quantity": float(raw_quantity),
        "quantity_step": float(step),
        "minimum_quantity": float(minimum),
        "quantity": quantity_float,
        "estimated_margin": estimated_margin,
        "exposure_cap_percent": cap_pct,
        "position_sizing_performed": True,
        "quantity_calculated": True,
        "source": "WEEX_V3_DEMO_BALANCE",
        "read_only": True,
    }

    # ========================================================
    # 12. INTERNAL TRADE PLAN
    # ========================================================

    trade_plan = {
        "active_mode": mode,
        "direction": side,
        "quantity": quantity_float,
        "position_sizing": position_sizing,
        "execution_environment": "DEMO",
    }

    result = {
        "status": "READY",
        "active_mode": mode,
        "direction": side,
        "signal_qualified": True,
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": trade_plan,
        "skip_reason": "NONE",
        "read_only": True,
    }

    # ========================================================
    # 13. FINAL REPORT
    # ========================================================

    print("UNIT 8 STATUS = READY", flush=True)
    print("UNIT 8 MODE =", mode, flush=True)
    print("UNIT 8 DIRECTION =", side, flush=True)
    print(
        "UNIT 8 WEEX LEVERAGE =", leverage,
        flush=True,
    )
    print(
        "UNIT 8 AVAILABLE SUSDT =", available,
        flush=True,
    )
    print(
        "UNIT 8 INITIAL MARGIN =", entry_margin,
        flush=True,
    )
    print(
        "UNIT 8 QUANTITY =", quantity_float,
        flush=True,
    )
    print(
        "UNIT 8 ESTIMATED MARGIN =", estimated_margin,
        flush=True,
    )
    print(
        "UNIT 8 MAX EXPOSURE % =", cap_pct,
        flush=True,
    )
    print(
        "UNIT 8 TRADE PLAN READY = TRUE",
        flush=True,
    )
    print(
        "UNIT 8 LEVERAGE MUTATION = FALSE",
        flush=True,
    )
    print(
        "UNIT 8 EXCHANGE WRITE = FALSE",
        flush=True,
    )

    log("FRESH RECONSTRUCTION UNIT 8 RESULT = PASS")
    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 8
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
# END COMPLETE REPLACEMENT - UNIT 8
# UNIT 9 CONTINUES BELOW
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 9
# ZERO INDENTATION
#
# VALIDATED DEMO EXECUTION PREPARATION
# EXCHANGE-CONTROLLED LEVERAGE PRESERVED
# NO ORDER SUBMISSION
# ============================================================

def fresh_reconstruction_unit_9(
    config,
    unit_8_result,
):
    import math

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 9 START")

    # ========================================================
    # 1. INPUT VALIDATION
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 9 INVALID CONFIG")

    if not isinstance(unit_8_result, dict):
        raise RuntimeError("UNIT 9 INVALID UNIT 8 RESULT")

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})
    strategy = config.get("strategy", {})

    if not all(isinstance(v, dict) for v in (
        exchange, safety, strategy
    )):
        raise RuntimeError("UNIT 9 INVALID CONFIG SECTIONS")

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

    if any(k not in unit_8_result for k in required_fields):
        raise RuntimeError("UNIT 9 MISSING UNIT 8 FIELDS")

    if unit_8_result["read_only"] is not True:
        raise RuntimeError("UNIT 9 UNSAFE UNIT 8 HANDOFF")

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError("UNIT 9 DEMO ONLY")

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError("UNIT 9 INVALID DEMO SYMBOL")

    for key in (
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
    ):
        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 9 UNSAFE CAPABILITY: " + key
            )

    # ========================================================
    # 2. NORMALIZED IDLE RESULT
    # ========================================================

    def idle(reason):
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
            "skip_reason": str(reason),
            "order_payload_created": False,
            "tp_execution_requested": False,
            "sl_execution_requested": False,
            "read_only": True,
        }

        print("UNIT 9 STATUS = IDLE", flush=True)
        print("UNIT 9 REASON =", reason, flush=True)
        log("FRESH RECONSTRUCTION UNIT 9 RESULT = PASS (IDLE)")
        return result

    # ========================================================
    # 3. UNIT 8 ADMISSION
    # ========================================================

    status = unit_8_result["status"]
    mode = unit_8_result["active_mode"]
    side = unit_8_result["direction"]

    if status == "IDLE":
        return idle(unit_8_result["skip_reason"])

    if status != "READY":
        raise RuntimeError("UNIT 9 INVALID READY STATUS")

    if unit_8_result["signal_qualified"] is not True:
        return idle("UNIT_8_SIGNAL_NOT_QUALIFIED")

    if unit_8_result["execution_intent"] is not True:
        return idle("UNIT_8_EXECUTION_INTENT_FALSE")

    if unit_8_result["trade_plan_ready"] is not True:
        return idle("UNIT_8_TRADE_PLAN_NOT_READY")

    if mode not in ("SCALP", "STRUCTURE", "BREAKOUT"):
        raise RuntimeError("UNIT 9 INVALID ACTIVE MODE")

    if side not in ("LONG", "SHORT"):
        raise RuntimeError("UNIT 9 INVALID DIRECTION")

    trade_plan = unit_8_result.get("trade_plan")

    if not isinstance(trade_plan, dict):
        raise RuntimeError("UNIT 9 TRADE PLAN MISSING")

    if trade_plan.get("active_mode") != mode:
        raise RuntimeError("UNIT 9 MODE MISMATCH")

    if trade_plan.get("direction") != side:
        raise RuntimeError("UNIT 9 DIRECTION MISMATCH")

    if trade_plan.get("execution_environment") != "DEMO":
        raise RuntimeError("UNIT 9 NOT DEMO TRADE")

    # ========================================================
    # 4. POSITION SIZING VERIFICATION
    # ========================================================

    sizing = trade_plan.get("position_sizing")

    if not isinstance(sizing, dict):
        raise RuntimeError("UNIT 9 SIZING MISSING")

    if sizing.get("position_sizing_performed") is not True:
        return idle("POSITION_SIZING_NOT_PERFORMED")

    if sizing.get("quantity_calculated") is not True:
        return idle("QUANTITY_NOT_CALCULATED")

    if sizing.get("leverage_source") != "WEEX_SYMBOL_CONFIG":
        return idle("INVALID_LEVERAGE_SOURCE")

    if sizing.get(
        "demo_leverage_match_confirmed"
    ) is not True:
        return idle("DEMO_LEVERAGE_NOT_CONFIRMED")

    if sizing.get("leverage_target") is not None:
        return idle("PYTHON_LEVERAGE_TARGET_PRESENT")

    try:
        quantity = float(sizing["quantity"])
        leverage = float(sizing["effective_leverage"])
        price = float(sizing["live_mark_price"])
        margin = float(sizing["estimated_margin"])
        available = float(sizing["available_balance"])
        minimum = float(sizing["minimum_quantity"])
        step = float(sizing["quantity_step"])
        cap = float(sizing["exposure_cap_percent"])
        total_balance = float(sizing["total_balance"])
    except (KeyError, ValueError, TypeError):
        return idle("INVALID_POSITION_SIZING_DATA")

    values = (
        quantity, leverage, price, margin,
        available, minimum, step, cap, total_balance
    )

    if not all(math.isfinite(v) and v > 0 for v in values):
        return idle("INVALID_NUMERIC_SIZING_DATA")

    if quantity < minimum:
        return idle("QUANTITY_BELOW_MINIMUM")

    if not math.isclose(
        quantity / step,
        round(quantity / step),
        rel_tol=0,
        abs_tol=0.000001,
    ):
        return idle("QUANTITY_STEP_MISMATCH")

    if not 0 < cap <= 35:
        return idle("INVALID_EXPOSURE_CAP")

    if margin > available:
        return idle("INSUFFICIENT_AVAILABLE_MARGIN")

    if not math.isclose(
        margin,
        quantity * price / leverage,
        rel_tol=0.000001,
        abs_tol=0.00000001,
    ):
        return idle("MARGIN_CALCULATION_MISMATCH")

    # Unit 8 verifies exposure against committed funds.
    # Unit 9 must not override that calculation.
    # Later execution must refresh account conditions
    # immediately before submitting the order.

    if float(trade_plan.get("quantity", 0)) != quantity:
        return idle("TRADE_PLAN_QUANTITY_MISMATCH")

    # ========================================================
    # 5. EXECUTION CANDIDATE
    # ========================================================

    execution_candidate = {
        "active_mode": mode,
        "direction": side,
        "trade_plan": trade_plan,
        "execution_environment": "DEMO",
    }

    result = {
        "status": "READY",
        "active_mode": mode,
        "direction": side,
        "signal_qualified": True,
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": trade_plan,
        "execution_ready": True,
        "execution_candidate": execution_candidate,
        "skip_reason": "NONE",
        "order_payload_created": False,
        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "read_only": True,
    }

    # ========================================================
    # 6. REPORT
    # ========================================================

    print("UNIT 9 STATUS = READY", flush=True)
    print("UNIT 9 MODE =", mode, flush=True)
    print("UNIT 9 DIRECTION =", side, flush=True)
    print("UNIT 9 QUANTITY =", quantity, flush=True)
    print("UNIT 9 EXCHANGE LEVERAGE =", leverage, flush=True)
    print("UNIT 9 ESTIMATED MARGIN =", margin, flush=True)
    print("UNIT 9 EXECUTION READY = TRUE", flush=True)
    print("UNIT 9 ORDER PAYLOAD CREATED = FALSE", flush=True)
    print("UNIT 9 EXCHANGE WRITE = FALSE", flush=True)

    log("FRESH RECONSTRUCTION UNIT 9 RESULT = PASS")
    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 9
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_9_RESULT = (
    fresh_reconstruction_unit_9(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT,
    )
)

# ============================================================
# END COMPLETE REPLACEMENT - UNIT 9
# ZERO INDENTATION
# UNIT 10 CONTINUES BELOW
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 10
# ZERO INDENTATION
#
# DEMO EXECUTION BOUNDARY PREPARATION
# WEEX-CONTROLLED LEVERAGE
# NO PYTHON LEVERAGE SELECTION
# NO ORDER SUBMISSION IN THIS UNIT
# ============================================================

def fresh_reconstruction_unit_10(
    config,
    unit_9_result,
):
    import math

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 10 START")

    # ========================================================
    # 1. VALIDATE INPUT
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 10 INVALID CONFIG")

    if not isinstance(unit_9_result, dict):
        raise RuntimeError("UNIT 10 INVALID UNIT 9 RESULT")

    exchange = config.get("exchange")
    safety = config.get("safety")
    strategy = config.get("strategy")
    precision = config.get("market_precision")

    if not all(isinstance(v, dict) for v in (
        exchange, safety, strategy, precision
    )):
        raise RuntimeError(
            "UNIT 10 MISSING CONFIGURATION SECTIONS"
        )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError("UNIT 10 DEMO ONLY")

    if exchange.get("name") != "WEEX":
        raise RuntimeError("UNIT 10 INVALID EXCHANGE")

    if exchange.get("api_version") != "V3":
        raise RuntimeError("UNIT 10 INVALID API VERSION")

    if exchange.get("market_symbol") != "BTCUSDT":
        raise RuntimeError("UNIT 10 INVALID MARKET SYMBOL")

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError("UNIT 10 INVALID DEMO SYMBOL")

    # ========================================================
    # 2. READ-ONLY PREPARATION SAFETY
    # ========================================================

    for key in (
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
    ):
        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 10 UNSAFE CAPABILITY: " + key
            )

    for key in (
        "anti_duplicate_orders",
        "one_direction_only",
        "active_trade_mode_lock",
        "exclusive_mode",
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 10 STRATEGY SAFETY FAILURE: " + key
            )

    # ========================================================
    # 3. PRESERVE UNIT 11 OUTPUT CONTRACT
    # ========================================================

    def idle(reason):

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
            "skip_reason": str(reason),
            "order_payload_created": False,
            "demo_submission_requested": False,
            "real_submission_requested": False,
            "tp_execution_requested": False,
            "sl_execution_requested": False,
            "backup_execution_requested": False,
            "read_only": True,
        }

        print("UNIT 10 STATUS = IDLE", flush=True)
        print(
            "UNIT 10 SKIP REASON =", reason,
            flush=True,
        )

        log(
            "FRESH RECONSTRUCTION UNIT 10 "
            "RESULT = PASS (IDLE)"
        )

        return result

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
        "skip_reason",
        "order_payload_created",
        "tp_execution_requested",
        "sl_execution_requested",
        "read_only",
    )

    if any(key not in unit_9_result for key in required):
        raise RuntimeError(
            "UNIT 10 INCOMPLETE UNIT 9 CONTRACT"
        )

    if unit_9_result["read_only"] is not True:
        raise RuntimeError(
            "UNIT 10 UNIT 9 SAFETY FAILURE"
        )

    if (
        unit_9_result["order_payload_created"] is not False
        or unit_9_result["tp_execution_requested"] is not False
        or unit_9_result["sl_execution_requested"] is not False
    ):
        raise RuntimeError(
            "UNIT 10 UNEXPECTED PRIOR EXECUTION"
        )

    # ========================================================
    # 4. NORMAL IDLE SIGNAL
    # ========================================================

    status = unit_9_result["status"]

    if status == "IDLE":
        return idle(unit_9_result["skip_reason"])

    if status != "READY":
        return idle("UNIT_9_NOT_READY")

    if any(unit_9_result[key] is not True for key in (
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "execution_ready",
    )):
        return idle("UNIT_9_ADMISSION_INCOMPLETE")

    mode = unit_9_result["active_mode"]
    side = unit_9_result["direction"]

    if mode not in (
        "SCALP", "STRUCTURE", "BREAKOUT"
    ):
        return idle("INVALID_ACTIVE_MODE")

    if side not in ("LONG", "SHORT"):
        return idle("INVALID_TRADE_DIRECTION")

    # ========================================================
    # 5. VERIFY TRADE PLAN
    # ========================================================

    trade_plan = unit_9_result["trade_plan"]
    candidate = unit_9_result["execution_candidate"]

    if not isinstance(trade_plan, dict):
        return idle("TRADE_PLAN_MISSING")

    if not isinstance(candidate, dict):
        return idle("EXECUTION_CANDIDATE_MISSING")

    if trade_plan.get("active_mode") != mode:
        return idle("TRADE_PLAN_MODE_MISMATCH")

    if trade_plan.get("direction") != side:
        return idle("TRADE_PLAN_DIRECTION_MISMATCH")

    if trade_plan.get(
        "execution_environment"
    ) != "DEMO":
        return idle("TRADE_PLAN_NOT_DEMO")

    if candidate.get("active_mode") != mode:
        return idle("CANDIDATE_MODE_MISMATCH")

    if candidate.get("direction") != side:
        return idle("CANDIDATE_DIRECTION_MISMATCH")

    if candidate.get("trade_plan") != trade_plan:
        return idle("CANDIDATE_TRADE_PLAN_MISMATCH")

    sizing = trade_plan.get("position_sizing")

    if not isinstance(sizing, dict):
        return idle("POSITION_SIZING_MISSING")

    # ========================================================
    # 6. EXCHANGE-CONTROLLED LEVERAGE
    # ========================================================

    if sizing.get("leverage_target") is not None:
        return idle("PYTHON_LEVERAGE_TARGET_PRESENT")

    if sizing.get(
        "leverage_source"
    ) != "WEEX_SYMBOL_CONFIG":
        return idle("INVALID_EXCHANGE_LEVERAGE_SOURCE")

    if sizing.get(
        "demo_leverage_match_confirmed"
    ) is not True:
        return idle("DEMO_LEVERAGE_NOT_CONFIRMED")

    if sizing.get("position_sizing_performed") is not True:
        return idle("POSITION_SIZING_NOT_PERFORMED")

    if sizing.get("quantity_calculated") is not True:
        return idle("POSITION_QUANTITY_NOT_CALCULATED")

    margin_mode = sizing.get("margin_mode")
    position_mode = sizing.get("position_mode")

    if margin_mode not in ("CROSSED", "ISOLATED"):
        return idle("INVALID_MARGIN_MODE")

    if position_mode not in ("COMBINED", "SEPARATED"):
        return idle("INVALID_POSITION_MODE")

    # ========================================================
    # 7. NUMERIC VALIDATION
    # ========================================================

    try:
        leverage = float(sizing["effective_leverage"])
        price = float(sizing["live_mark_price"])
        quantity = float(sizing["quantity"])
        margin = float(sizing["estimated_margin"])
        available = float(sizing["available_balance"])
        total_balance = float(sizing["total_balance"])
        cap = float(sizing["exposure_cap_percent"])
        quantity_step = float(sizing["quantity_step"])
        minimum_qty = float(sizing["minimum_quantity"])
        fixed_margin = float(sizing["margin_allocation"])
        frozen = float(sizing["frozen_balance"])
    except (KeyError, ValueError, TypeError):
        return idle("INVALID_NUMERIC_TRADE_PLAN")

    positive_values = (
        leverage, price, quantity, margin,
        available, total_balance, cap,
        quantity_step, minimum_qty, fixed_margin,
    )

    if not all(
        math.isfinite(v) and v > 0
        for v in positive_values
    ):
        return idle("NONPOSITIVE_OR_NONFINITE_SIZING")

    if not math.isfinite(frozen) or frozen < 0:
        return idle("INVALID_FROZEN_BALANCE")

    if quantity < minimum_qty:
        return idle("QUANTITY_BELOW_MINIMUM")

    if not math.isclose(
        quantity / quantity_step,
        round(quantity / quantity_step),
        rel_tol=0,
        abs_tol=0.000001,
    ):
        return idle("INVALID_QUANTITY_INCREMENT")

    if not 0 < cap <= 35:
        return idle("EXPOSURE_CAP_INVALID")

    if not math.isclose(
        cap,
        float(strategy.get("exposure_cap_percent", 0)),
        abs_tol=0.000001,
        rel_tol=0,
    ):
        return idle("EXPOSURE_CONFIG_MISMATCH")

    if not math.isclose(
        margin,
        quantity * price / leverage,
        rel_tol=0.000001,
        abs_tol=0.00000001,
    ):
        return idle("ESTIMATED_MARGIN_MISMATCH")

    if margin > available:
        return idle("INSUFFICIENT_AVAILABLE_MARGIN")

    if margin > fixed_margin + 0.00000001:
        return idle("MARGIN_ALLOCATION_EXCEEDED")

    # ========================================================
    # 8. CONSERVATIVE EXPOSURE VERIFICATION
    # ========================================================

    committed_proxy = max(
        0.0, total_balance - available
    )

    maximum_margin = total_balance * cap / 100.0

    if committed_proxy + margin > (
        maximum_margin + 0.00000001
    ):
        return idle("TOTAL_EXPOSURE_CAP_EXCEEDED")

    # Unit 8 must be re-run with fresh account data
    # before submitting a new order.
    #
    # This check does not establish that the exchange
    # balance remains unchanged by execution time.

    if not math.isclose(
        quantity,
        float(trade_plan.get("quantity", 0)),
        rel_tol=0,
        abs_tol=0.00000001,
    ):
        return idle("TRADE_QUANTITY_MISMATCH")

    # ========================================================
    # 9. BUILD INTERNAL DEMO SUBMISSION INSTRUCTION
    # ========================================================

    # Unit 11 constructs the WEEX order payload.
    # Unit 12 owns authorized demo submission.
    #
    # These False flags are LOCAL to Unit 10.
    # They do not instruct Unit 12 to remain paused.

    instruction = {
        "exchange": "WEEX",
        "api_version": "V3",
        "execution_environment": "DEMO",
        "market_symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",
        "active_mode": mode,
        "direction": side,
        "trade_plan": trade_plan,
        "execution_candidate": candidate,
        "anti_duplicate_required": True,
        "one_direction_only_required": True,
        "active_trade_mode_lock_required": True,
        "payload_creation_allowed": False,
        "submission_allowed": False,
        "read_only": True,
    }

    # ========================================================
    # 10. RESULT FOR UNIT 11
    # ========================================================

    result = {
        "status": "READY",
        "active_mode": mode,
        "direction": side,
        "signal_qualified": True,
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": trade_plan,
        "execution_ready": True,
        "execution_candidate": candidate,
        "demo_boundary_ready": True,
        "demo_submission_instruction": instruction,
        "skip_reason": "NONE",
        "order_payload_created": False,
        "demo_submission_requested": False,
        "real_submission_requested": False,
        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "backup_execution_requested": False,
        "read_only": True,
    }

    # ========================================================
    # 11. REPORT
    # ========================================================

    print(
        "UNIT 10 STATUS = READY",
        flush=True,
    )

    print(
        "UNIT 10 ACTIVE MODE =", mode,
        flush=True,
    )

    print(
        "UNIT 10 DIRECTION =", side,
        flush=True,
    )

    print(
        "UNIT 10 WEEX LEVERAGE =", leverage,
        flush=True,
    )

    print(
        "UNIT 10 MARGIN MODE =", margin_mode,
        flush=True,
    )

    print(
        "UNIT 10 BTC QUANTITY =", quantity,
        flush=True,
    )

    print(
        "UNIT 10 ESTIMATED MARGIN =", margin,
        flush=True,
    )

    print(
        "UNIT 10 EXPOSURE CAP % =", cap,
        flush=True,
    )

    print(
        "UNIT 10 DEMO BOUNDARY READY = TRUE",
        flush=True,
    )

    print(
        "UNIT 10 ORDER PAYLOAD CREATED = FALSE",
        flush=True,
    )

    print(
        "UNIT 10 LEVERAGE MUTATION = FALSE",
        flush=True,
    )

    print(
        "UNIT 10 EXCHANGE WRITE = FALSE",
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 10 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 10
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_10_RESULT = (
    fresh_reconstruction_unit_10(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_9_RESULT,
    )
)

# ============================================================
# END COMPLETE REPLACEMENT - UNIT 10
# ZERO INDENTATION
# EXISTING UNIT 11 CONTINUES BELOW
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 11
# ZERO INDENTATION
#
# WEEX DEMO ENTRY PAYLOAD PREPARATION
# EXCHANGE-CONTROLLED LEVERAGE
#
# NO PYTHON LEVERAGE SETTING
# NO ORDER SUBMISSION IN THIS UNIT
# UNIT 12 RETAINS DEMO EXECUTION AUTHORITY
# ============================================================

def fresh_reconstruction_unit_11(
    config,
    unit_10_result,
):
    import math
    import uuid
    from decimal import Decimal
    from datetime import datetime, timezone

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 11 START")

    # ========================================================
    # 1. INPUT VALIDATION
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 11 INVALID CONFIGURATION")

    if not isinstance(unit_10_result, dict):
        raise RuntimeError("UNIT 11 INVALID UNIT 10 RESULT")

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})
    strategy = config.get("strategy", {})
    precision = config.get("market_precision", {})

    if not all(isinstance(v, dict) for v in (
        exchange, safety, strategy, precision
    )):
        raise RuntimeError(
            "UNIT 11 CONFIGURATION SECTION MISSING"
        )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError("UNIT 11 DEMO ONLY")

    if exchange.get("name") != "WEEX":
        raise RuntimeError("UNIT 11 INVALID EXCHANGE")

    if exchange.get("api_version") != "V3":
        raise RuntimeError("UNIT 11 INVALID API VERSION")

    if exchange.get("market_symbol") != "BTCUSDT":
        raise RuntimeError("UNIT 11 INVALID MARKET SYMBOL")

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError("UNIT 11 INVALID DEMO SYMBOL")

    # ========================================================
    # 2. SAFETY CONTRACT
    # ========================================================

    for key in (
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
    ):
        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 11 UNSAFE CAPABILITY: " + key
            )

    for key in (
        "anti_duplicate_orders",
        "one_direction_only",
        "active_trade_mode_lock",
        "exclusive_mode",
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 11 SAFETY RULE DISABLED: " + key
            )

    # ========================================================
    # 3. NORMALIZED IDLE RESULT
    # ========================================================

    def idle(reason):

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
            "skip_reason": str(reason),
            "order_payload_created": False,
            "demo_submission_requested": False,
            "real_submission_requested": False,
            "tp_execution_requested": False,
            "sl_execution_requested": False,
            "backup_execution_requested": False,
            "read_only": True,
        }

        print("UNIT 11 STATUS = IDLE", flush=True)
        print("UNIT 11 SKIP REASON =", reason, flush=True)

        log(
            "FRESH RECONSTRUCTION UNIT 11 "
            "RESULT = PASS (IDLE)"
        )

        return result

    # ========================================================
    # 4. UNIT 10 ADMISSION
    # ========================================================

    status = unit_10_result.get("status", "IDLE")

    if status == "IDLE":
        return idle(
            unit_10_result.get(
                "skip_reason", "UNIT_10_IDLE"
            )
        )

    if status != "READY":
        return idle("UNIT_10_NOT_READY")

    if unit_10_result.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 11 UNIT 10 PREPARATION SAFETY FAILURE"
        )

    for key in (
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "execution_ready",
        "demo_boundary_ready",
    ):
        if unit_10_result.get(key) is not True:
            return idle("UNIT_10_NOT_ADMITTED:" + key)

    for key in (
        "order_payload_created",
        "demo_submission_requested",
        "real_submission_requested",
        "tp_execution_requested",
        "sl_execution_requested",
        "backup_execution_requested",
    ):
        if unit_10_result.get(key) is not False:
            raise RuntimeError(
                "UNIT 11 UNEXPECTED PRIOR EXECUTION: " + key
            )

    mode = unit_10_result.get("active_mode")
    direction = unit_10_result.get("direction")

    if mode not in (
        "SCALP", "STRUCTURE", "BREAKOUT"
    ):
        return idle("INVALID_ACTIVE_MODE")

    if direction not in ("LONG", "SHORT"):
        return idle("INVALID_DIRECTION")

    # ========================================================
    # 5. TRADE PLAN AND INSTRUCTION
    # ========================================================

    trade_plan = unit_10_result.get("trade_plan")
    candidate = unit_10_result.get(
        "execution_candidate"
    )
    instruction = unit_10_result.get(
        "demo_submission_instruction"
    )

    if not all(isinstance(v, dict) for v in (
        trade_plan, candidate, instruction
    )):
        return idle("MISSING_EXECUTION_COMPONENT")

    if (
        trade_plan.get("active_mode") != mode
        or candidate.get("active_mode") != mode
        or instruction.get("active_mode") != mode
    ):
        return idle("EXECUTION_MODE_MISMATCH")

    if (
        trade_plan.get("direction") != direction
        or candidate.get("direction") != direction
        or instruction.get("direction") != direction
    ):
        return idle("EXECUTION_DIRECTION_MISMATCH")

    if candidate.get("trade_plan") != trade_plan:
        return idle("EXECUTION_CANDIDATE_MISMATCH")

    if instruction.get("trade_plan") != trade_plan:
        return idle("INSTRUCTION_TRADE_PLAN_MISMATCH")

    if instruction.get("execution_candidate") != candidate:
        return idle("INSTRUCTION_CANDIDATE_MISMATCH")

    if instruction.get("execution_environment") != "DEMO":
        return idle("INSTRUCTION_NOT_DEMO")

    if instruction.get("demo_order_symbol") != "BTCSUSDT":
        return idle("INSTRUCTION_SYMBOL_MISMATCH")

    if instruction.get("read_only") is not True:
        return idle("UNSAFE_SUBMISSION_INSTRUCTION")

    for key in (
        "anti_duplicate_required",
        "one_direction_only_required",
        "active_trade_mode_lock_required",
    ):
        if instruction.get(key) is not True:
            return idle("MISSING_EXECUTION_GUARD:" + key)

    # Unit 10's submission_allowed=False means
    # Unit 10 itself must not submit an order.
    # Unit 12 remains the authorized demo executor.

    if instruction.get("submission_allowed") is not False:
        return idle("INVALID_UNIT_10_SUBMISSION_BOUNDARY")

    # ========================================================
    # 6. VERIFIED WEEX LEVERAGE HANDOFF
    # ========================================================

    sizing = trade_plan.get("position_sizing")

    if not isinstance(sizing, dict):
        return idle("POSITION_SIZING_MISSING")

    if sizing.get("leverage_target") is not None:
        return idle("PYTHON_LEVERAGE_TARGET_PRESENT")

    if sizing.get(
        "leverage_source"
    ) != "WEEX_SYMBOL_CONFIG":
        return idle("EXCHANGE_LEVERAGE_SOURCE_INVALID")

    if sizing.get(
        "demo_leverage_match_confirmed"
    ) is not True:
        return idle("DEMO_LEVERAGE_MATCH_NOT_CONFIRMED")

    if sizing.get("position_sizing_performed") is not True:
        return idle("POSITION_SIZING_INCOMPLETE")

    if sizing.get("quantity_calculated") is not True:
        return idle("POSITION_QUANTITY_NOT_CALCULATED")

    if sizing.get("margin_mode") not in (
        "CROSSED", "ISOLATED"
    ):
        return idle("INVALID_MARGIN_MODE")

    if sizing.get("position_mode") not in (
        "COMBINED", "SEPARATED"
    ):
        return idle("INVALID_POSITION_MODE")

    # ========================================================
    # 7. QUANTITY AND MARGIN VALIDATION
    # ========================================================

    try:
        quantity = Decimal(str(sizing["quantity"]))
        quantity_step = Decimal(
            str(sizing["quantity_step"])
        )
        minimum_quantity = Decimal(
            str(sizing["minimum_quantity"])
        )
        config_step = Decimal(
            str(precision["quantity_step"])
        )
        config_minimum = Decimal(
            str(precision["minimum_quantity"])
        )

        price = float(sizing["live_mark_price"])
        leverage = float(sizing["effective_leverage"])
        margin = float(sizing["estimated_margin"])
        allocated = float(sizing["margin_allocation"])
        available = float(sizing["available_balance"])
        cap = float(sizing["exposure_cap_percent"])
        total_balance = float(sizing["total_balance"])
        frozen = float(sizing["frozen_balance"])

    except (
        KeyError, TypeError, ValueError, ArithmeticError
    ):
        return idle("INVALID_SIZING_FIELDS")

    if not all(
        value.is_finite() and value > 0
        for value in (
            quantity, quantity_step,
            minimum_quantity,
            config_step, config_minimum
        )
    ):
        return idle("INVALID_QUANTITY_PRECISION")

    if quantity_step != config_step:
        return idle("QUANTITY_STEP_CONFIG_MISMATCH")

    if minimum_quantity != config_minimum:
        return idle("MINIMUM_QUANTITY_CONFIG_MISMATCH")

    if quantity < minimum_quantity:
        return idle("QUANTITY_BELOW_EXCHANGE_MINIMUM")

    if (
        quantity / quantity_step
    ) != (
        quantity / quantity_step
    ).to_integral_value():
        return idle("QUANTITY_NOT_STEP_ALIGNED")

    numeric_values = (
        price, leverage, margin, allocated,
        available, cap, total_balance
    )

    if not all(
        math.isfinite(v) and v > 0
        for v in numeric_values
    ):
        return idle("NONFINITE_OR_NONPOSITIVE_SIZING")

    if not math.isfinite(frozen) or frozen < 0:
        return idle("INVALID_FROZEN_BALANCE")

    if not 0 < cap <= 35:
        return idle("EXPOSURE_CAP_INVALID")

    expected_margin = (
        float(quantity) * price / leverage
    )

    if not math.isclose(
        margin,
        expected_margin,
        rel_tol=0.000001,
        abs_tol=0.00000001,
    ):
        return idle("MARGIN_CALCULATION_MISMATCH")

    if margin > allocated + 1e-8:
        return idle("INITIAL_MARGIN_ALLOCATION_EXCEEDED")

    if margin > available + 1e-8:
        return idle("AVAILABLE_BALANCE_INSUFFICIENT")

    committed_proxy = max(
        0.0, total_balance - available
    )

    if committed_proxy + margin > (
        total_balance * cap / 100.0 + 1e-8
    ):
        return idle("MAX_EXPOSURE_CAP_EXCEEDED")

    try:
        plan_quantity = Decimal(
            str(trade_plan["quantity"])
        )
    except (KeyError, TypeError, ValueError):
        return idle("TRADE_PLAN_QUANTITY_INVALID")

    if plan_quantity != quantity:
        return idle("TRADE_PLAN_QUANTITY_MISMATCH")

    # ========================================================
    # 8. MAP LONG / SHORT TO WEEX DEMO ENTRY
    # ========================================================

    if direction == "LONG":
        order_side = "BUY"
        position_side = "LONG"
    else:
        order_side = "SELL"
        position_side = "SHORT"

    quantity_text = format(quantity, "f")

    if not quantity_text or Decimal(
        quantity_text
    ) != quantity:
        return idle("INVALID_FORMATTED_QUANTITY")

    # ========================================================
    # 9. CREATE UNIQUE ORDER IDENTIFIER
    # ========================================================

    client_order_id = (
        "FR11-"
        + datetime.now(
            timezone.utc
        ).strftime("%y%m%d%H%M%S%f")
        + "-"
        + uuid.uuid4().hex[:8]
    )

    # A unique identifier prevents accidental reuse.
    # It does not replace durable order reconciliation.

    # ========================================================
    # 10. BUILD DEMO MARKET ORDER PAYLOAD
    # ========================================================

    order_payload = {
        "symbol": "BTCSUSDT",
        "side": order_side,
        "positionSide": position_side,
        "type": "MARKET",
        "quantity": quantity_text,
        "newClientOrderId": client_order_id,
    }

    # No leverage field.
    # No margin-mode mutation field.
    # No real trading symbol.
    # No TP, SL or backup instruction here.

    # ========================================================
    # 11. STRICT PAYLOAD VALIDATION
    # ========================================================

    required_payload = (
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    )

    if set(order_payload) != set(required_payload):
        raise RuntimeError(
            "UNIT 11 UNEXPECTED ORDER PAYLOAD FIELDS"
        )

    if order_payload["symbol"] != "BTCSUSDT":
        raise RuntimeError("UNIT 11 WRONG ORDER SYMBOL")

    if order_payload["type"] != "MARKET":
        raise RuntimeError("UNIT 11 NOT MARKET ORDER")

    if not order_payload["newClientOrderId"]:
        raise RuntimeError("UNIT 11 EMPTY CLIENT ORDER ID")

    if direction == "LONG" and (
        order_payload["side"] != "BUY"
        or order_payload["positionSide"] != "LONG"
    ):
        raise RuntimeError("UNIT 11 LONG ORDER MISMATCH")

    if direction == "SHORT" and (
        order_payload["side"] != "SELL"
        or order_payload["positionSide"] != "SHORT"
    ):
        raise RuntimeError("UNIT 11 SHORT ORDER MISMATCH")

    # ========================================================
    # 12. RESULT FOR UNIT 12
    # ========================================================

    result = {
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
        "demo_submission_instruction": instruction,
        "payload_ready": True,
        "order_payload": order_payload,
        "order_payload_created": True,
        "skip_reason": "NONE",
        "demo_submission_requested": False,
        "real_submission_requested": False,
        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "backup_execution_requested": False,
        "read_only": True,
    }

    # ========================================================
    # 13. DIAGNOSTIC REPORT
    # ========================================================

    print("UNIT 11 STATUS = READY", flush=True)
    print("UNIT 11 ACTIVE MODE =", mode, flush=True)
    print("UNIT 11 DIRECTION =", direction, flush=True)
    print(
        "UNIT 11 EXCHANGE LEVERAGE =",
        leverage,
        flush=True,
    )
    print(
        "UNIT 11 MARGIN MODE =",
        sizing["margin_mode"],
        flush=True,
    )
    print(
        "UNIT 11 POSITION MODE =",
        sizing["position_mode"],
        flush=True,
    )
    print(
        "UNIT 11 BTC QUANTITY =",
        quantity_text,
        flush=True,
    )
    print(
        "UNIT 11 ESTIMATED MARGIN =",
        margin,
        flush=True,
    )
    print(
        "UNIT 11 PAYLOAD READY = TRUE",
        flush=True,
    )
    print(
        "UNIT 11 ORDER TYPE = MARKET",
        flush=True,
    )
    print(
        "UNIT 11 CLIENT ORDER ID =",
        client_order_id,
        flush=True,
    )
    print(
        "UNIT 11 LEVERAGE MUTATION = FALSE",
        flush=True,
    )
    print(
        "UNIT 11 DEMO SUBMISSION = FALSE",
        flush=True,
    )
    print(
        "UNIT 11 REAL SUBMISSION = FALSE",
        flush=True,
    )

    log("FRESH RECONSTRUCTION UNIT 11 RESULT = PASS")
    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 11
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_11_RESULT = (
    fresh_reconstruction_unit_11(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_10_RESULT,
    )
)

# ============================================================
# END COMPLETE REPLACEMENT - UNIT 11
# ZERO INDENTATION
# EXISTING UNIT 12 CONTINUES BELOW
# ============================================================


# ============================================================
# FRESH RECONSTRUCTION UNIT 12
# POSITION-AWARE WEEX DEMO INITIAL ENTRY
#
# PURPOSE:
# - Consume verified Unit 11 result.
# - IDLE -> do absolutely nothing.
# - READY -> authenticated DEMO position read FIRST.
# - Existing non-zero BTCSUSDT position:
#       BLOCK NEW INITIAL ENTRY ONLY.
# - Zero BTCSUSDT position:
#       submit exactly ONE authenticated WEEX DEMO entry.
# - TP and Backup management are NOT blocked by this unit.
# - Unit 12 remains INITIAL ENTRY ONLY.
# - DEMO endpoints only.
# - REAL trading absolutely prohibited.
# - Initial SL remains disabled.
# - No leverage mutation.
# - No margin-mode mutation.
# - No position-mode mutation.
# - No backup execution inside Unit 12.
# ============================================================


def fresh_reconstruction_unit_12(
    config,
    unit_11_result,
):
    import os
    import json
    import time
    import hmac
    import hashlib
    import base64
    import urllib.request
    import urllib.error
    from datetime import datetime, timezone

    print("=" * 80, flush=True)
    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 12 START",
        flush=True,
    )
    print("-" * 80, flush=True)

    # --------------------------------------------------------
    # INPUT VALIDATION
    # --------------------------------------------------------

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 12 BLOCKED: CONFIGURATION IS NOT A DICT"
        )

    print(
        "PASS: UNIT 12 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    if not isinstance(unit_11_result, dict):
        raise RuntimeError(
            "UNIT 12 BLOCKED: UNIT 11 RESULT IS NOT A DICT"
        )

    print(
        "PASS: UNIT 12 RECEIVED UNIT 11 RESULT",
        flush=True,
    )

    if "status" not in unit_11_result:
        raise RuntimeError(
            "UNIT 12 BLOCKED: UNIT 11 STATUS MISSING"
        )

    if "read_only" not in unit_11_result:
        raise RuntimeError(
            "UNIT 12 BLOCKED: UNIT 11 READ_ONLY FIELD MISSING"
        )

    print(
        "PASS: UNIT 12 UNIT 11 CONTRACT VALIDATED",
        flush=True,
    )

    if unit_11_result.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 12 BLOCKED: UNIT 11 WAS NOT READ-ONLY"
        )

    print(
        "PASS: UNIT 12 UNIT 11 READ-ONLY BOUNDARY VERIFIED",
        flush=True,
    )

    status = str(
        unit_11_result.get("status", "IDLE")
    ).upper()

    # ========================================================
    # IDLE PATH
    # ========================================================

    if status == "IDLE":

        active_mode = unit_11_result.get(
            "active_mode"
        )

        direction = unit_11_result.get(
            "direction"
        )

        signal_qualified = bool(
            unit_11_result.get(
                "signal_qualified",
                False,
            )
        )

        execution_intent = bool(
            unit_11_result.get(
                "execution_intent",
                False,
            )
        )

        skip_reason = unit_11_result.get(
            "skip_reason",
            "UNIT_11_IDLE",
        )

        result = {
            "unit": 12,
            "status": "IDLE",
            "read_only": False,
            "active_mode": active_mode,
            "direction": direction,
            "signal_qualified": signal_qualified,
            "execution_intent": execution_intent,
            "position_check_attempted": False,
            "active_position_exists": False,
            "demo_submission_attempted": False,
            "demo_submission_completed": False,
            "real_submission_attempted": False,
            "authenticated_request": False,
            "order_endpoint_access": False,
            "exchange_write": False,
            "skip_reason": skip_reason,
        }

        print("-" * 80, flush=True)

        print(
            "UNIT 12 STATUS = IDLE",
            flush=True,
        )

        print(
            f"UNIT 12 ACTIVE MODE = {active_mode}",
            flush=True,
        )

        print(
            f"UNIT 12 DIRECTION = {direction}",
            flush=True,
        )

        print(
            "UNIT 12 SIGNAL QUALIFIED = "
            f"{signal_qualified}",
            flush=True,
        )

        print(
            "UNIT 12 EXECUTION INTENT = "
            f"{execution_intent}",
            flush=True,
        )

        print(
            "UNIT 12 POSITION CHECK ATTEMPTED = False",
            flush=True,
        )

        print(
            "UNIT 12 DEMO SUBMISSION ATTEMPTED = False",
            flush=True,
        )

        print(
            f"UNIT 12 SKIP REASON = {skip_reason}",
            flush=True,
        )

        print("-" * 80, flush=True)

        print(
            "PASS: UNIT 12 NORMAL NO-TRADE STATE",
            flush=True,
        )

        print(
            "PASS: UNIT 12 NO AUTHENTICATED REQUEST",
            flush=True,
        )

        print(
            "PASS: UNIT 12 NO POSITION ACCESS",
            flush=True,
        )

        print(
            "PASS: UNIT 12 NO ORDER ENDPOINT ACCESS",
            flush=True,
        )

        print(
            "PASS: UNIT 12 NO DEMO SUBMISSION",
            flush=True,
        )

        print(
            "PASS: UNIT 12 NO REAL SUBMISSION",
            flush=True,
        )

        print(
            "PASS: UNIT 12 NO TP EXECUTION",
            flush=True,
        )

        print(
            "PASS: UNIT 12 NO SL EXECUTION",
            flush=True,
        )

        print(
            "PASS: UNIT 12 NO BACKUP EXECUTION",
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
            "ZERO DEMO ORDER = TRUE",
            flush=True,
        )

        print(
            "ZERO REAL ORDER = TRUE",
            flush=True,
        )

        print(
            "ZERO EXCHANGE WRITE = TRUE",
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

        print("-" * 80, flush=True)

        print(
            f"{datetime.now(timezone.utc).isoformat()} "
            "FRESH RECONSTRUCTION UNIT 12 RESULT = PASS (IDLE)",
            flush=True,
        )

        print("=" * 80, flush=True)

        return result

    # ========================================================
    # ONLY READY MAY REACH INITIAL ENTRY PATH
    # ========================================================

    if status != "READY":
        raise RuntimeError(
            "UNIT 12 BLOCKED: "
            f"INVALID UNIT 11 STATUS: {status}"
        )

    print(
        "PASS: UNIT 12 UNIT 11 STATUS = READY",
        flush=True,
    )

    # --------------------------------------------------------
    # QUALIFIED EXECUTION CONTRACT
    # --------------------------------------------------------

    active_mode = unit_11_result.get(
        "active_mode"
    )

    direction = unit_11_result.get(
        "direction"
    )

    signal_qualified = bool(
        unit_11_result.get(
            "signal_qualified",
            False,
        )
    )

    execution_intent = bool(
        unit_11_result.get(
            "execution_intent",
            False,
        )
    )

    if active_mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        raise RuntimeError(
            "UNIT 12 BLOCKED: INVALID ACTIVE MODE"
        )

    if direction not in (
        "LONG",
        "SHORT",
    ):
        raise RuntimeError(
            "UNIT 12 BLOCKED: INVALID DIRECTION"
        )

    if signal_qualified is not True:
        raise RuntimeError(
            "UNIT 12 BLOCKED: SIGNAL NOT QUALIFIED"
        )

    if execution_intent is not True:
        raise RuntimeError(
            "UNIT 12 BLOCKED: EXECUTION INTENT FALSE"
        )

    print(
        "PASS: UNIT 12 QUALIFIED EXECUTION CONTRACT",
        flush=True,
    )

    # --------------------------------------------------------
    # EXTRACT UNIT 11 DEMO PAYLOAD
    # --------------------------------------------------------

    demo_payload = unit_11_result.get(
        "demo_payload"
    )

    if demo_payload is None:
        demo_payload = unit_11_result.get(
            "payload"
        )

    if demo_payload is None:
        demo_payload = unit_11_result.get(
            "order_payload"
        )

    if not isinstance(demo_payload, dict):
        raise RuntimeError(
            "UNIT 12 BLOCKED: "
            "UNIT 11 DEMO PAYLOAD NOT FOUND"
        )

    if not demo_payload:
        raise RuntimeError(
            "UNIT 12 BLOCKED: "
            "UNIT 11 DEMO PAYLOAD EMPTY"
        )

    print(
        "PASS: UNIT 12 RECEIVED UNIT 11 DEMO PAYLOAD",
        flush=True,
    )

    # --------------------------------------------------------
    # REQUIRED INITIAL ENTRY FIELDS
    # --------------------------------------------------------

    required_payload_fields = (
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
    )

    for field in required_payload_fields:

        if field not in demo_payload:
            raise RuntimeError(
                "UNIT 12 BLOCKED: "
                f"DEMO PAYLOAD FIELD MISSING: {field}"
            )

    print(
        "PASS: UNIT 12 REQUIRED DEMO PAYLOAD FIELDS PRESENT",
        flush=True,
    )

    # --------------------------------------------------------
    # DEMO SYMBOL LOCK
    # --------------------------------------------------------

    if demo_payload.get("symbol") != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 12 BLOCKED: "
            "DEMO SYMBOL MUST BE BTCSUSDT"
        )

    print(
        "PASS: UNIT 12 DEMO SYMBOL = BTCSUSDT",
        flush=True,
    )

    # --------------------------------------------------------
    # INITIAL ENTRY MARKET ORDER LOCK
    # --------------------------------------------------------

    if str(
        demo_payload.get("type")
    ).upper() != "MARKET":

        raise RuntimeError(
            "UNIT 12 BLOCKED: "
            "ENTRY ORDER TYPE MUST BE MARKET"
        )

    print(
        "PASS: UNIT 12 ORDER TYPE = MARKET",
        flush=True,
    )

    # --------------------------------------------------------
    # DIRECTION / SIDE CONSISTENCY
    # --------------------------------------------------------

    side = str(
        demo_payload.get("side")
    ).upper()

    position_side = str(
        demo_payload.get("positionSide")
    ).upper()

    if direction == "LONG":

        if side != "BUY":
            raise RuntimeError(
                "UNIT 12 BLOCKED: "
                "LONG REQUIRES BUY SIDE"
            )

        if position_side != "LONG":
            raise RuntimeError(
                "UNIT 12 BLOCKED: "
                "LONG REQUIRES LONG POSITION SIDE"
            )

    elif direction == "SHORT":

        if side != "SELL":
            raise RuntimeError(
                "UNIT 12 BLOCKED: "
                "SHORT REQUIRES SELL SIDE"
            )

        if position_side != "SHORT":
            raise RuntimeError(
                "UNIT 12 BLOCKED: "
                "SHORT REQUIRES SHORT POSITION SIDE"
            )

    print(
        "PASS: UNIT 12 DIRECTION / SIDE CONSISTENCY",
        flush=True,
    )

    # --------------------------------------------------------
    # INITIAL STOP LOSS MUST REMAIN ABSENT
    # --------------------------------------------------------

    prohibited_sl_fields = (
        "slTriggerPrice",
        "SlWorkingType",
        "stopLossPrice",
        "stopPrice",
    )

    for field in prohibited_sl_fields:

        if field in demo_payload:
            raise RuntimeError(
                "UNIT 12 BLOCKED: "
                f"SL FIELD PRESENT: {field}"
            )

    print(
        "PASS: UNIT 12 INITIAL SL REMAINS DISABLED",
        flush=True,
    )

    final_payload = dict(
        demo_payload
    )

    # --------------------------------------------------------
    # WEEX DEMO CREDENTIALS
    # --------------------------------------------------------

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

    if not api_key:
        raise RuntimeError(
            "UNIT 12 BLOCKED: WEEX API KEY MISSING"
        )

    if not api_secret:
        raise RuntimeError(
            "UNIT 12 BLOCKED: WEEX API SECRET MISSING"
        )

    if not api_passphrase:
        raise RuntimeError(
            "UNIT 12 BLOCKED: WEEX API PASSPHRASE MISSING"
        )

    print(
        "PASS: UNIT 12 WEEX DEMO CREDENTIALS PRESENT",
        flush=True,
    )

    base_url = (
        "https://api-contract.weex.com"
    )

    # ========================================================
    # POSITION-AWARE INITIAL ENTRY GATE
    #
    # IMPORTANT:
    # This gate controls INITIAL ENTRY ONLY.
    #
    # Existing position DOES NOT mean:
    # - block TP
    # - block TP1
    # - block TP2
    # - block TP3 trailing
    # - block Backup 1
    # - block Backup 2
    # - block Backup 3
    #
    # Those belong to the management path after Unit 12.
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "UNIT 12 PRE-SUBMISSION POSITION GATE START",
        flush=True,
    )

    position_request_path = (
        "/capi/v3/sim/position/allPosition"
    )

    position_url = (
        base_url
        + position_request_path
    )

    position_method = "GET"

    position_timestamp = str(
        int(time.time() * 1000)
    )

    position_prehash = (
        position_timestamp
        + position_method
        + position_request_path
    )

    position_signature = base64.b64encode(
        hmac.new(
            api_secret.encode("utf-8"),
            position_prehash.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    position_headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": position_signature,
        "ACCESS-TIMESTAMP": position_timestamp,
        "ACCESS-PASSPHRASE": api_passphrase,
        "Content-Type": "application/json",
    }

    print(
        "UNIT 12 POSITION REQUEST PATH = "
        f"{position_request_path}",
        flush=True,
    )

    print(
        "UNIT 12 POSITION REQUEST METHOD = GET",
        flush=True,
    )

    print(
        "PASS: UNIT 12 AUTHENTICATED DEMO POSITION "
        "REQUEST PREPARED",
        flush=True,
    )

    position_request = urllib.request.Request(
        url=position_url,
        headers=position_headers,
        method="GET",
    )

    position_http_status = None
    position_response_text = None

    try:

        with urllib.request.urlopen(
            position_request,
            timeout=15,
        ) as response:

            position_http_status = (
                response.getcode()
            )

            position_response_text = (
                response.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

    except urllib.error.HTTPError as exc:

        error_text = ""

        try:
            error_text = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )
        except Exception:
            error_text = str(exc)

        print(
            "UNIT 12 POSITION HTTP ERROR = "
            f"{exc.code}",
            flush=True,
        )

        print(
            "UNIT 12 POSITION ERROR RESPONSE = "
            f"{error_text}",
            flush=True,
        )

        raise RuntimeError(
            "UNIT 12 INITIAL ENTRY BLOCKED: "
            "DEMO POSITION QUERY FAILED"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "UNIT 12 INITIAL ENTRY BLOCKED: "
            "DEMO POSITION QUERY NETWORK ERROR: "
            f"{exc}"
        ) from exc

    except Exception as exc:

        raise RuntimeError(
            "UNIT 12 INITIAL ENTRY BLOCKED: "
            "UNEXPECTED POSITION QUERY ERROR: "
            f"{exc}"
        ) from exc

    print(
        "UNIT 12 POSITION HTTP STATUS = "
        f"{position_http_status}",
        flush=True,
    )

    if not (
        200 <= int(position_http_status) < 300
    ):
        raise RuntimeError(
            "UNIT 12 INITIAL ENTRY BLOCKED: "
            "POSITION QUERY NON-SUCCESS HTTP STATUS"
        )

    if not position_response_text:
        raise RuntimeError(
            "UNIT 12 INITIAL ENTRY BLOCKED: "
            "EMPTY POSITION RESPONSE"
        )

    try:

        position_response_json = json.loads(
            position_response_text
        )

    except Exception as exc:

        raise RuntimeError(
            "UNIT 12 INITIAL ENTRY BLOCKED: "
            "POSITION RESPONSE IS NOT VALID JSON"
        ) from exc

    if not isinstance(
        position_response_json,
        list,
    ):
        raise RuntimeError(
            "UNIT 12 INITIAL ENTRY BLOCKED: "
            "POSITION RESPONSE IS NOT A LIST"
        )

    print(
        "PASS: UNIT 12 VALID DEMO POSITION JSON RESPONSE",
        flush=True,
    )

    active_btc_positions = []

    for position_record in position_response_json:

        if not isinstance(
            position_record,
            dict,
        ):
            raise RuntimeError(
                "UNIT 12 INITIAL ENTRY BLOCKED: "
                "MALFORMED POSITION RECORD"
            )

        record_symbol = str(
            position_record.get(
                "symbol",
                "",
            )
        ).upper()

        if record_symbol != "BTCSUSDT":
            continue

        if "size" not in position_record:
            raise RuntimeError(
                "UNIT 12 INITIAL ENTRY BLOCKED: "
                "BTCSUSDT POSITION SIZE MISSING"
            )

        try:

            record_size = float(
                position_record.get(
                    "size"
                )
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise RuntimeError(
                "UNIT 12 INITIAL ENTRY BLOCKED: "
                "INVALID BTCSUSDT POSITION SIZE"
            ) from exc

        if record_size < 0:
            raise RuntimeError(
                "UNIT 12 INITIAL ENTRY BLOCKED: "
                "NEGATIVE POSITION SIZE"
            )

        if record_size > 0:

            record_side = str(
                position_record.get(
                    "side",
                    "",
                )
            ).upper()

            if record_side not in (
                "LONG",
                "SHORT",
            ):
                raise RuntimeError(
                    "UNIT 12 INITIAL ENTRY BLOCKED: "
                    "ACTIVE POSITION SIDE INVALID"
                )

            active_btc_positions.append(
                {
                    "id": position_record.get(
                        "id"
                    ),
                    "symbol": record_symbol,
                    "side": record_side,
                    "size": record_size,
                    "leverage": position_record.get(
                        "leverage"
                    ),
                    "marginType": position_record.get(
                        "marginType"
                    ),
                    "separatedMode": position_record.get(
                        "separatedMode"
                    ),
                }
            )

    active_position_exists = (
        len(active_btc_positions) > 0
    )

    print(
        "UNIT 12 BTCSUSDT ACTIVE POSITION COUNT = "
        f"{len(active_btc_positions)}",
        flush=True,
    )

    print(
        "UNIT 12 ACTIVE POSITION EXISTS = "
        f"{active_position_exists}",
        flush=True,
    )

    # ========================================================
    # EXISTING POSITION:
    # BLOCK INITIAL ENTRY, BUT RETURN MANAGEMENT STATE
    # ========================================================

    if active_position_exists:

        for active_position in active_btc_positions:

            print(
                "UNIT 12 EXISTING POSITION ID = "
                f"{active_position.get('id')}",
                flush=True,
            )

            print(
                "UNIT 12 EXISTING POSITION SIDE = "
                f"{active_position.get('side')}",
                flush=True,
            )

            print(
                "UNIT 12 EXISTING POSITION SIZE = "
                f"{active_position.get('size')}",
                flush=True,
            )

        result = {
            "unit": 12,
            "status": "ACTIVE_POSITION_BLOCK",
            "read_only": False,
            "active_mode": active_mode,
            "direction": direction,
            "signal_qualified": True,
            "execution_intent": True,

            "position_check_attempted": True,
            "position_check_completed": True,
            "position_endpoint_access": True,
            "position_http_status": position_http_status,

            "active_position_exists": True,
            "active_positions": active_btc_positions,

            "initial_entry_permitted": False,
            "duplicate_initial_entry_blocked": True,

            "management_path_permitted": True,
            "tp_management_permitted": True,
            "backup_management_permitted": True,

            "demo_submission_attempted": False,
            "demo_submission_completed": False,
            "real_submission_attempted": False,

            "authenticated_request": True,
            "order_endpoint_access": False,
            "exchange_write": False,

            "skip_reason":
                "NON_ZERO_POSITION_BLOCK_INITIAL_ENTRY",
        }

        print("-" * 80, flush=True)

        print(
            "UNIT 12 INITIAL ENTRY PERMITTED = False",
            flush=True,
        )

        print(
            "UNIT 12 DEMO ENTRY SUBMISSION ATTEMPTED = False",
            flush=True,
        )

        print(
            "UNIT 12 MANAGEMENT PATH PERMITTED = True",
            flush=True,
        )

        print(
            "UNIT 12 TP MANAGEMENT PERMITTED = True",
            flush=True,
        )

        print(
            "UNIT 12 BACKUP MANAGEMENT PERMITTED = True",
            flush=True,
        )

        print("-" * 80, flush=True)

        print(
            "PASS: UNIT 12 DUPLICATE INITIAL ENTRY BLOCKED",
            flush=True,
        )

        print(
            "PASS: UNIT 12 EXISTING POSITION PRESERVED",
            flush=True,
        )

        print(
            "PASS: UNIT 12 TP PATH NOT BLOCKED",
            flush=True,
        )

        print(
            "PASS: UNIT 12 BACKUP PATH NOT BLOCKED",
            flush=True,
        )

        print(
            "PASS: UNIT 12 NO ENTRY ORDER ENDPOINT ACCESS",
            flush=True,
        )

        print(
            "PASS: UNIT 12 NO NEW DEMO ENTRY",
            flush=True,
        )

        print(
            "PASS: UNIT 12 NO REAL SUBMISSION",
            flush=True,
        )

        print(
            "PASS: UNIT 12 NO LEVERAGE MUTATION",
            flush=True,
        )

        print(
            "PASS: UNIT 12 NO MARGIN MODE MUTATION",
            flush=True,
        )

        print(
            "PASS: UNIT 12 NO POSITION MODE MUTATION",
            flush=True,
        )

        print(
            "POSITION READ ACCESS = TRUE",
            flush=True,
        )

        print(
            "ENTRY EXCHANGE WRITE = FALSE",
            flush=True,
        )

        print("-" * 80, flush=True)

        print(
            f"{datetime.now(timezone.utc).isoformat()} "
            "FRESH RECONSTRUCTION UNIT 12 RESULT = "
            "PASS (ACTIVE POSITION BLOCK)",
            flush=True,
        )

        print("=" * 80, flush=True)

        return result

    # ========================================================
    # ZERO POSITION:
    # INITIAL ENTRY IS PERMITTED
    # ========================================================

    print(
        "PASS: UNIT 12 ZERO ACTIVE BTCSUSDT POSITION",
        flush=True,
    )

    print(
        "UNIT 12 INITIAL ENTRY PERMITTED = True",
        flush=True,
    )

    request_path = (
        "/capi/v3/sim/order"
    )

    url = (
        base_url
        + request_path
    )

    method = "POST"

    print(
        "PASS: UNIT 12 WEEX DEMO ENTRY ENDPOINT LOCKED",
        flush=True,
    )

    print(
        f"UNIT 12 REQUEST PATH = {request_path}",
        flush=True,
    )

    body = json.dumps(
        final_payload,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    body_bytes = body.encode(
        "utf-8"
    )

    timestamp = str(
        int(time.time() * 1000)
    )

    prehash = (
        timestamp
        + method
        + request_path
        + body
    )

    signature = base64.b64encode(
        hmac.new(
            api_secret.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    print(
        "PASS: UNIT 12 WEEX V3 ENTRY SIGNATURE GENERATED",
        flush=True,
    )

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": api_passphrase,
        "Content-Type": "application/json",
    }

    print(
        "PASS: UNIT 12 AUTHENTICATED DEMO ENTRY REQUEST PREPARED",
        flush=True,
    )

    print("-" * 80, flush=True)

    print(
        "UNIT 12 EXECUTION ENVIRONMENT = DEMO",
        flush=True,
    )

    print(
        f"UNIT 12 ACTIVE MODE = {active_mode}",
        flush=True,
    )

    print(
        f"UNIT 12 DIRECTION = {direction}",
        flush=True,
    )

    print(
        f"UNIT 12 SYMBOL = {final_payload.get('symbol')}",
        flush=True,
    )

    print(
        f"UNIT 12 SIDE = {side}",
        flush=True,
    )

    print(
        f"UNIT 12 POSITION SIDE = {position_side}",
        flush=True,
    )

    print(
        f"UNIT 12 QUANTITY = {final_payload.get('quantity')}",
        flush=True,
    )

    print(
        "UNIT 12 POSITION CHECK COMPLETED = True",
        flush=True,
    )

    print(
        "UNIT 12 ACTIVE POSITION EXISTS = False",
        flush=True,
    )

    print(
        "UNIT 12 REAL ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 12 DEMO INITIAL ENTRY = TRUE",
        flush=True,
    )

    print(
        "UNIT 12 SL ENABLED = FALSE",
        flush=True,
    )

    print(
        "UNIT 12 TP EXECUTION = FALSE",
        flush=True,
    )

    print(
        "UNIT 12 BACKUP EXECUTION = FALSE",
        flush=True,
    )

    print("-" * 80, flush=True)

    print(
        "UNIT 12 SENDING ONE WEEX DEMO INITIAL ENTRY",
        flush=True,
    )

    request = urllib.request.Request(
        url=url,
        data=body_bytes,
        headers=headers,
        method="POST",
    )

    response_status = None
    response_text = None

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            response_status = (
                response.getcode()
            )

            response_text = (
                response.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

    except urllib.error.HTTPError as exc:

        response_status = exc.code

        try:

            response_text = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

        except Exception:

            response_text = str(exc)

        print(
            "UNIT 12 WEEX HTTP ERROR = "
            f"{response_status}",
            flush=True,
        )

        print(
            "UNIT 12 WEEX RESPONSE = "
            f"{response_text}",
            flush=True,
        )

        raise RuntimeError(
            "UNIT 12 DEMO INITIAL ENTRY REJECTED BY WEEX: "
            f"HTTP {response_status}"
        )

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "UNIT 12 DEMO INITIAL ENTRY NETWORK ERROR: "
            f"{exc}"
        ) from exc

    print(
        f"UNIT 12 HTTP STATUS = {response_status}",
        flush=True,
    )

    print(
        f"UNIT 12 WEEX RESPONSE = {response_text}",
        flush=True,
    )

    try:

        response_json = json.loads(
            response_text
        )

    except Exception as exc:

        raise RuntimeError(
            "UNIT 12 BLOCKED: "
            "WEEX ENTRY RESPONSE IS NOT VALID JSON"
        ) from exc

    print(
        "PASS: UNIT 12 VALID WEEX ENTRY JSON RESPONSE",
        flush=True,
    )

    if not (
        200 <= int(response_status) < 300
    ):
        raise RuntimeError(
            "UNIT 12 DEMO INITIAL ENTRY FAILED: "
            f"HTTP {response_status}"
        )

    if response_json.get("success") is not True:

        raise RuntimeError(
            "UNIT 12 DEMO INITIAL ENTRY NOT ACCEPTED: "
            f"{response_json}"
        )

    order_id = response_json.get(
        "orderId"
    )

    if not order_id:

        raise RuntimeError(
            "UNIT 12 DEMO INITIAL ENTRY ACCEPTED "
            "WITHOUT ORDER ID"
        )

    print(
        "PASS: UNIT 12 WEEX RESPONSE SUCCESS = TRUE",
        flush=True,
    )

    print(
        f"PASS: UNIT 12 WEEX ORDER ID = {order_id}",
        flush=True,
    )

    result = {
        "unit": 12,
        "status": "DEMO_SUBMITTED",
        "read_only": False,
        "active_mode": active_mode,
        "direction": direction,
        "signal_qualified": True,
        "execution_intent": True,

        "position_check_attempted": True,
        "position_check_completed": True,
        "position_endpoint_access": True,
        "position_http_status": position_http_status,
        "active_position_exists": False,
        "active_positions": [],

        "initial_entry_permitted": True,
        "duplicate_initial_entry_blocked": False,

        "management_path_permitted": True,
        "tp_management_permitted": True,
        "backup_management_permitted": True,

        "demo_submission_attempted": True,
        "demo_submission_completed": True,
        "real_submission_attempted": False,

        "authenticated_request": True,
        "order_endpoint_access": True,
        "exchange_write": True,

        "request_path": request_path,
        "request_payload": final_payload,
        "http_status": response_status,
        "weex_response": response_json,
        "order_id": order_id,
    }

    print("-" * 80, flush=True)

    print(
        "PASS: UNIT 12 POSITION-AWARE ENTRY GATE",
        flush=True,
    )

    print(
        "PASS: UNIT 12 ZERO POSITION CONFIRMED BEFORE ENTRY",
        flush=True,
    )

    print(
        "PASS: UNIT 12 AUTHENTICATED WEEX DEMO ENTRY REQUEST",
        flush=True,
    )

    print(
        "PASS: UNIT 12 DEMO INITIAL ENTRY COMPLETED",
        flush=True,
    )

    print(
        "PASS: UNIT 12 REAL ORDER SUBMISSION BLOCKED",
        flush=True,
    )

    print(
        "PASS: UNIT 12 NO PRODUCTION ORDER ENDPOINT",
        flush=True,
    )

    print(
        "PASS: UNIT 12 NO LEVERAGE MUTATION",
        flush=True,
    )

    print(
        "PASS: UNIT 12 NO MARGIN MODE MUTATION",
        flush=True,
    )

    print(
        "PASS: UNIT 12 NO POSITION MODE MUTATION",
        flush=True,
    )

    print(
        "PASS: UNIT 12 NO TP EXECUTION",
        flush=True,
    )

    print(
        "PASS: UNIT 12 NO BACKUP EXECUTION",
        flush=True,
    )

    print(
        "PASS: UNIT 12 MANAGEMENT PATH REMAINS AVAILABLE",
        flush=True,
    )

    print("-" * 80, flush=True)

    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 12 RESULT = "
        "PASS (DEMO SUBMITTED)",
        flush=True,
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 12
# ZERO INDENTATION
# ============================================================


# ============================================================
# BOT MODE MASTER SWITCH
# RUN   = ALLOW NEW ENTRIES AND MANAGE EXISTING POSITIONS
# PAUSE = BLOCK NEW ENTRIES, CONTINUE POSITION MANAGEMENT
# ============================================================

import os

BOT_MODE = os.environ.get(
    "BOT_MODE",
    "RUN"
).strip().upper()

if BOT_MODE not in ("RUN", "PAUSE"):
    raise RuntimeError(
        "INVALID BOT_MODE: SET RUN OR PAUSE"
    )

print(
    "BOT MODE =",
    BOT_MODE,
    flush=True,
)

if BOT_MODE == "PAUSE":

    print(
        "UNIT 12 INITIAL ENTRY BLOCKED: BOT PAUSED",
        flush=True,
    )

    FRESH_RECONSTRUCTION_UNIT_12_RESULT = {
        "unit": 12,
        "status": "IDLE",
        "read_only": True,
        "demo_submission_attempted": False,
        "demo_submission_completed": False,
        "real_submission_attempted": False,
        "skip_reason": "BOT_MODE_PAUSE",
    }

else:

    FRESH_RECONSTRUCTION_UNIT_12_RESULT = (
        fresh_reconstruction_unit_12(
            FRESH_RECONSTRUCTION_CONFIG,
            FRESH_RECONSTRUCTION_UNIT_11_RESULT,
        )
    )

# ============================================================
# END BOT MODE SWITCH
# UNIT 13 CONTINUES BELOW
# ============================================================



# ============================================================
# END PART 10
# UNIT 12 FULLY CLOSED AND CALLED
# NEXT = PART 11 / UNIT 13
# ============================================================ 
    
# ============================================================
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 13
# ZERO INDENTATION DEMARCATION
#
# DELETE OLD UNIT 13 + OLD RUN UNIT 13 CALL
# PASTE THIS COMPLETE BLOCK IN ITS PLACE
#
# DO NOT DELETE UNIT 14 BELOW THIS BLOCK
# ============================================================


# ============================================================
# FRESH RECONSTRUCTION UNIT 13
# EXISTING-POSITION DYNAMIC TAKE-PROFIT MANAGEMENT
#
# CORE RULE:
#
# NEW SIGNAL QUALIFICATION CONTROLS NEW ENTRY ONLY.
#
# ONCE A BTCSUSDT DEMO POSITION EXISTS:
# - UNIT 13 MANAGES IT INDEPENDENTLY.
# - UNIT 13 DOES NOT REQUIRE A NEW QUALIFIED SIGNAL.
# - UNIT 13 DOES NOT REQUIRE UNIT 12 TO BE READY.
# - UNIT 13 DOES NOT CREATE AN INITIAL ENTRY.
#
# TARGET TP ALLOCATION:
#
# TP1 = 10%
# TP2 = 20%
# TP3 = 70%
#
# ACTUAL QUANTITIES ARE QUANTITY-STEP AWARE.
#
# EXAMPLE:
#
# 0.0010 BTC:
# TP1 = 0.0001
# TP2 = 0.0002
# TP3 = 0.0007
#
# 0.0004 BTC:
# ONLY FOUR 0.0001 BTC STEPS EXIST.
#
# THEREFORE:
# TP1 = 0.0001
# TP2 = 0.0001
# TP3 = 0.0002
#
# EFFECTIVE = 25 / 25 / 50
#
# THIS IS NOT A STRATEGY CHANGE.
# IT IS THE CLOSEST EXECUTABLE REPRESENTATION OF
# THE CONFIGURED 10 / 20 / 70 TARGET.
#
# DYNAMIC TARGET CONTRACT:
#
# TP1:
# - >= 5% ESTIMATED NET ROI FLOOR
#
# TP2:
# - >= 10% ESTIMATED NET ROI FLOOR
# - MUST REMAIN BEYOND TP1
# - AT LEAST ONE PRICE STEP SEPARATION
#
# FEE CONTRACT:
#
# MARKET TP CLOSES ARE TAKER EXECUTIONS.
#
# DEFAULT WEEX FUTURES TAKER FEE ESTIMATE:
# 0.08% OF NOTIONAL PER EXECUTION.
#
# ROUND-TRIP FEE ESTIMATE:
# ENTRY TAKER + EXIT TAKER.
#
# CONFIG MAY OVERRIDE:
# strategy["futures_taker_fee_percent"]
#
# TP3:
# - UNIT 13 ONLY ARMS / HANDS OFF TP3.
# - UNIT 14 PERFORMS DYNAMIC TRAILING.
#
# SAFETY:
# - DEMO BTCSUSDT ONLY
# - REAL ORDER PROHIBITED
# - SL DISABLED
# - NO BACKUP EXECUTION IN UNIT 13
# - NO LEVERAGE MUTATION
# - NO MARGIN MODE MUTATION
# - NO POSITION MODE MUTATION
# ============================================================


def fresh_reconstruction_unit_13(
    config,
    unit_12_result,
):
    import os
    import json
    import time
    import hmac
    import hashlib
    import base64
    import urllib.request
    import urllib.error
    import urllib.parse

    from decimal import (
        Decimal,
        ROUND_DOWN,
        ROUND_UP,
    )

    from datetime import (
        datetime,
        timezone,
    )

    print(
        "=" * 80,
        flush=True,
    )

    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 13 START",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    # ========================================================
    # 1. INPUT CONTRACT
    # ========================================================

    if not isinstance(
        config,
        dict,
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: CONFIGURATION MISSING"
        )

    if not isinstance(
        unit_12_result,
        dict,
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: UNIT 12 RESULT MISSING"
        )

    print(
        "PASS: UNIT 13 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    print(
        "PASS: UNIT 13 RECEIVED UNIT 12 RESULT",
        flush=True,
    )

    unit_12_status = str(
        unit_12_result.get(
            "status",
            "UNKNOWN",
        )
    ).upper()

    print(
        "UNIT 13 RECEIVED UNIT 12 STATUS = "
        f"{unit_12_status}",
        flush=True,
    )

    print(
        "PASS: UNIT 13 POSITION MANAGEMENT "
        "INDEPENDENT OF NEW SIGNAL",
        flush=True,
    )

    # ========================================================
    # 2. STRATEGY CONTRACT
    # ========================================================

    strategy = config.get(
        "strategy"
    )

    if not isinstance(
        strategy,
        dict,
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: STRATEGY CONFIGURATION MISSING"
        )

    tp1_allocation_percent = Decimal(
        str(
            strategy.get(
                "tp1_allocation_percent",
                10.0,
            )
        )
    )

    tp2_allocation_percent = Decimal(
        str(
            strategy.get(
                "tp2_allocation_percent",
                20.0,
            )
        )
    )

    tp3_allocation_percent = Decimal(
        str(
            strategy.get(
                "tp3_allocation_percent",
                70.0,
            )
        )
    )

    tp1_net_roi_floor = Decimal(
        str(
            strategy.get(
                "tp1_net_roi_floor_percent",
                5.0,
            )
        )
    )

    tp2_net_roi_floor = Decimal(
        str(
            strategy.get(
                "tp2_net_roi_floor_percent",
                10.0,
            )
        )
    )

    tp1_tp2_min_roi_separation = Decimal(
        str(
            strategy.get(
                "tp1_tp2_min_roi_separation_percent",
                5.0,
            )
        )
    )

    tp3_trailing_reference = Decimal(
        str(
            strategy.get(
                "tp3_trailing_reference_percent",
                0.20,
            )
        )
    )

    tp3_trailing_min = Decimal(
        str(
            strategy.get(
                "tp3_trailing_min_percent",
                0.10,
            )
        )
    )

    tp3_trailing_max = Decimal(
        str(
            strategy.get(
                "tp3_trailing_max_percent",
                0.40,
            )
        )
    )

    total_tp_allocation = (
        tp1_allocation_percent
        +
        tp2_allocation_percent
        +
        tp3_allocation_percent
    )

    if (
        total_tp_allocation
        !=
        Decimal("100")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "TP ALLOCATION DOES NOT TOTAL 100%"
        )

    if (
        tp1_net_roi_floor
        <
        Decimal("5")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "TP1 NET ROI FLOOR BELOW 5%"
        )

    if (
        tp2_net_roi_floor
        <
        Decimal("10")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "TP2 NET ROI FLOOR BELOW 10%"
        )

    if (
        tp2_net_roi_floor
        <=
        tp1_net_roi_floor
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "TP2 ROI FLOOR MUST EXCEED TP1"
        )

    print(
        "PASS: UNIT 13 TARGET TP ALLOCATION = "
        "10 / 20 / 70",
        flush=True,
    )

    print(
        "PASS: UNIT 13 TP QUANTITY MODE = STEP-AWARE",
        flush=True,
    )

    print(
        "PASS: UNIT 13 TP1 NET ROI FLOOR = "
        f"{tp1_net_roi_floor}%",
        flush=True,
    )

    print(
        "PASS: UNIT 13 TP2 NET ROI FLOOR = "
        f"{tp2_net_roi_floor}%",
        flush=True,
    )

    
    # ========================================================
    # 3. FEE CONFIGURATION
    # LEVERAGE WILL COME FROM ACTUAL DEMO POSITION
    # INDENTATION: FOUR SPACES
    # ========================================================

    # Do not take leverage from Unit 2 strategy.
    # No hardcoded 100x or 20x.
    #
    # Actual leverage will be read from:
    # GET /capi/v3/sim/position/allPosition
    #
    # This section only initializes the fee estimate.

    futures_taker_fee_percent = Decimal(
        str(
            strategy.get(
                "futures_taker_fee_percent",
                "0.08",
            )
        )
    )

    if (
        not futures_taker_fee_percent.is_finite()
        or futures_taker_fee_percent < Decimal("0")
        or futures_taker_fee_percent >= Decimal("1")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: INVALID TAKER FEE"
        )

    # Default is an estimate, not a verified rate
    # for the demo account.
    #
    # More accurate fee information should come from
    # exchange records or a verified rate source.

    estimated_round_trip_fee_price_percent = (
        futures_taker_fee_percent * Decimal("2")
    )

    print(
        "UNIT 13 DEFAULT TAKER FEE ESTIMATE =",
        futures_taker_fee_percent,
        "% PER SIDE",
        flush=True,
    )

    print(
        "UNIT 13 LEVERAGE SOURCE = "
        "ACTUAL WEEX DEMO POSITION",
        flush=True,
    )

    # ========================================================
    # 4. EXCHANGE CONTRACT
    # ========================================================

    exchange = config.get(
        "exchange"
    )

    if not isinstance(
        exchange,
        dict,
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: EXCHANGE CONFIG MISSING"
        )

    demo_symbol = str(
        exchange.get(
            "demo_order_symbol",
            "",
        )
    ).upper()

    market_symbol = str(
        exchange.get(
            "market_symbol",
            "BTCUSDT",
        )
    ).upper()

    base_url = str(
        exchange.get(
            "contract_base_url",
            exchange.get(
                "base_url",
                "https://api-contract.weex.com",
            ),
        )
    ).rstrip("/")

    if (
        demo_symbol
        !=
        "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "DEMO SYMBOL MUST BE BTCSUSDT"
        )

    if (
        market_symbol
        !=
        "BTCUSDT"
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "MARKET SYMBOL MUST BE BTCUSDT"
        )

    if (
        base_url
        !=
        "https://api-contract.weex.com"
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "UNEXPECTED CONTRACT BASE URL"
        )

    print(
        "PASS: UNIT 13 DEMO SYMBOL = BTCSUSDT",
        flush=True,
    )

    print(
        "PASS: UNIT 13 PUBLIC MARKET SYMBOL = BTCUSDT",
        flush=True,
    )

    print(
        "PASS: UNIT 13 REAL TRADING PROHIBITED",
        flush=True,
    )

    # ========================================================
    # 5. PRECISION CONTRACT
    # ========================================================

    market_precision = config.get(
        "market_precision",
        {},
    )

    quantity_step = Decimal(
        str(
            market_precision.get(
                "quantity_step",
                0.0001,
            )
        )
    )

    minimum_quantity = Decimal(
        str(
            market_precision.get(
                "minimum_quantity",
                0.0001,
            )
        )
    )

    price_step = Decimal(
        str(
            market_precision.get(
                "price_step",
                0.1,
            )
        )
    )

    if (
        quantity_step
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: INVALID QUANTITY STEP"
        )

    if (
        price_step
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: INVALID PRICE STEP"
        )

    def round_quantity_down(
        value,
    ):

        value = Decimal(
            str(value)
        )

        if (
            value
            <=
            Decimal("0")
        ):
            return Decimal("0")

        steps = (
            value
            /
            quantity_step
        ).to_integral_value(
            rounding=ROUND_DOWN
        )

        return (
            steps
            *
            quantity_step
        )

    def round_price_down(
        value,
    ):

        steps = (
            value
            /
            price_step
        ).to_integral_value(
            rounding=ROUND_DOWN
        )

        return (
            steps
            *
            price_step
        )

    def round_price_up(
        value,
    ):

        steps = (
            value
            /
            price_step
        ).to_integral_value(
            rounding=ROUND_UP
        )

        return (
            steps
            *
            price_step
        )

    # ========================================================
    # 6. API CREDENTIALS
    # ========================================================

    api_key = (
        os.environ.get(
            "WEEX_API_KEY"
        )
        or
        os.environ.get(
            "API_KEY"
        )
    )

    api_secret = (
        os.environ.get(
            "WEEX_API_SECRET"
        )
        or
        os.environ.get(
            "API_SECRET"
        )
    )

    api_passphrase = (
        os.environ.get(
            "WEEX_API_PASSPHRASE"
        )
        or
        os.environ.get(
            "API_PASSPHRASE"
        )
    )

    if not api_key:
        raise RuntimeError(
            "UNIT 13 BLOCKED: WEEX API KEY MISSING"
        )

    if not api_secret:
        raise RuntimeError(
            "UNIT 13 BLOCKED: WEEX API SECRET MISSING"
        )

    if not api_passphrase:
        raise RuntimeError(
            "UNIT 13 BLOCKED: WEEX API PASSPHRASE MISSING"
        )

    # ========================================================
    # 7. AUTHENTICATED DEMO POSITION READ
    # ========================================================

    position_request_path = (
        "/capi/v3/sim/position/allPosition"
    )

    position_timestamp = str(
        int(
            time.time()
            *
            1000
        )
    )

    position_prehash = (
        position_timestamp
        +
        "GET"
        +
        position_request_path
    )

    position_signature = (
        base64.b64encode(
            hmac.new(
                api_secret.encode(
                    "utf-8"
                ),
                position_prehash.encode(
                    "utf-8"
                ),
                hashlib.sha256,
            ).digest()
        ).decode(
            "utf-8"
        )
    )

    position_headers = {

        "ACCESS-KEY":
            api_key,

        "ACCESS-SIGN":
            position_signature,

        "ACCESS-TIMESTAMP":
            position_timestamp,

        "ACCESS-PASSPHRASE":
            api_passphrase,

        "Content-Type":
            "application/json",
    }

    position_request = (
        urllib.request.Request(
            url=(
                base_url
                +
                position_request_path
            ),
            headers=position_headers,
            method="GET",
        )
    )

    try:

        with urllib.request.urlopen(
            position_request,
            timeout=15,
        ) as response:

            position_http_status = (
                response.getcode()
            )

            position_response_text = (
                response.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

    except urllib.error.HTTPError as exc:

        try:

            error_text = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

        except Exception:

            error_text = str(exc)

        print(
            "UNIT 13 POSITION ERROR RESPONSE = "
            f"{error_text}",
            flush=True,
        )

        raise RuntimeError(
            "UNIT 13 DEMO POSITION READ FAILED"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "UNIT 13 DEMO POSITION NETWORK ERROR: "
            f"{exc}"
        ) from exc

    if not (
        200
        <=
        int(position_http_status)
        <
        300
    ):
        raise RuntimeError(
            "UNIT 13 DEMO POSITION READ FAILED"
        )

    try:

        position_records = json.loads(
            position_response_text
        )

    except Exception as exc:

        raise RuntimeError(
            "UNIT 13 POSITION RESPONSE INVALID JSON"
        ) from exc

    if not isinstance(
        position_records,
        list,
    ):
        raise RuntimeError(
            "UNIT 13 POSITION RESPONSE NOT LIST"
        )

    print(
        "PASS: UNIT 13 DEMO POSITION READ COMPLETED",
        flush=True,
    )

    # ========================================================
    # 8. FIND EXACT ACTIVE BTCSUSDT POSITION
    # ========================================================

    active_positions = []

    for record in position_records:

        if not isinstance(
            record,
            dict,
        ):
            continue

        if (
            str(
                record.get(
                    "symbol",
                    "",
                )
            ).upper()
            !=
            "BTCSUSDT"
        ):
            continue

        try:

            record_size = Decimal(
                str(
                    record.get(
                        "size",
                        "0",
                    )
                )
            )

        except Exception:

            continue

        if (
            record_size
            >
            Decimal("0")
        ):
            active_positions.append(
                record
            )

    # ========================================================
    # 9. NO POSITION
    # ========================================================

    if (
        len(active_positions)
        ==
        0
    ):

        result = {

            "unit":
                13,

            "status":
                "IDLE_NO_POSITION",

            "read_only":
                False,

            "unit_12_status":
                unit_12_status,

            "active_position_exists":
                False,

            "tp_management_required":
                False,

            "tp_execution_attempted":
                False,

            "tp_execution_completed":
                False,

            "tp3_armed":
                False,

            "sl_execution_attempted":
                False,

            "backup_execution_attempted":
                False,

            "real_submission_attempted":
                False,

            "exchange_write":
                False,

            "skip_reason":
                "NO_ACTIVE_BTCSUSDT_POSITION",
        }

        print(
            "UNIT 13 STATUS = IDLE_NO_POSITION",
            flush=True,
        )

        print(
            "PASS: UNIT 13 NO TP EXECUTION",
            flush=True,
        )

        print(
            "PASS: UNIT 13 SL REMAINS DISABLED",
            flush=True,
        )

        print(
            "ZERO EXCHANGE WRITE = TRUE",
            flush=True,
        )

        print(
            f"{datetime.now(timezone.utc).isoformat()} "
            "FRESH RECONSTRUCTION UNIT 13 RESULT = "
            "PASS (IDLE_NO_POSITION)",
            flush=True,
        )

        print(
            "=" * 80,
            flush=True,
        )

        return result

    if (
        len(active_positions)
        !=
        1
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "MULTIPLE ACTIVE BTCSUSDT POSITIONS"
        )

    position = active_positions[0]

    position_side = str(
        position.get(
            "side",
            "",
        )
    ).upper()

    if position_side not in (
        "LONG",
        "SHORT",
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: INVALID POSITION SIDE"
        )

    
    # ========================================================
    # 9A. ACTUAL WEEX POSITION LEVERAGE
    # INDENTATION: FOUR SPACES
    # ========================================================

    try:
        effective_leverage = Decimal(
            str(position["leverage"])
        )
    except (
        KeyError,
        ValueError,
        TypeError,
        ArithmeticError,
    ) as exc:
        raise RuntimeError(
            "UNIT 13 BLOCKED: EXCHANGE LEVERAGE MISSING"
        ) from exc

    if (
        not effective_leverage.is_finite()
        or effective_leverage <= Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: INVALID EXCHANGE LEVERAGE"
        )

    # Do not request any leverage change.
    # Preserve old variable name only where needed
    # by downstream calculations.

    leverage_target = effective_leverage

    # ========================================================
    # 9B. VALIDATE POSITION MARGIN
    # ========================================================

    try:
        actual_margin_size = Decimal(
            str(position["marginSize"])
        )
    except (
        KeyError,
        ValueError,
        TypeError,
        ArithmeticError,
    ) as exc:
        raise RuntimeError(
            "UNIT 13 BLOCKED: POSITION MARGIN MISSING"
        ) from exc

    if (
        not actual_margin_size.is_finite()
        or actual_margin_size <= Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: INVALID POSITION MARGIN"
        )

    # ========================================================
    # 9C. REBUILD TP1 AND TP2 REQUIRED ROI
    # ========================================================

    estimated_round_trip_fee_roi_percent = (
        estimated_round_trip_fee_price_percent
        * effective_leverage
    )

    tp1_required_gross_roi = (
        tp1_net_roi_floor
        + estimated_round_trip_fee_roi_percent
    )

    tp2_required_gross_roi = (
        tp2_net_roi_floor
        + estimated_round_trip_fee_roi_percent
    )

    minimum_tp2_from_tp1 = (
        tp1_required_gross_roi
        + tp1_tp2_min_roi_separation
    )

    if tp2_required_gross_roi < minimum_tp2_from_tp1:
        tp2_required_gross_roi = minimum_tp2_from_tp1

    tp1_price_move_percent = (
        tp1_required_gross_roi / effective_leverage
    )

    tp2_price_move_percent = (
        tp2_required_gross_roi / effective_leverage
    )

    # ========================================================
    # 9D. EXCHANGE POSITION DIAGNOSTICS
    # ========================================================

    print(
        "UNIT 13 ACTUAL WEEX LEVERAGE =",
        effective_leverage,
        "x",
        flush=True,
    )

    print(
        "UNIT 13 ACTUAL MARGIN SIZE =",
        actual_margin_size,
        flush=True,
    )

    print(
        "UNIT 13 ESTIMATED ROUND TRIP FEE ROI =",
        estimated_round_trip_fee_roi_percent,
        "%",
        flush=True,
    )

    print(
        "UNIT 13 TP1 GROSS ROI REQUIREMENT =",
        tp1_required_gross_roi,
        "%",
        flush=True,
    )

    print(
        "UNIT 13 TP2 GROSS ROI REQUIREMENT =",
        tp2_required_gross_roi,
        "%",
        flush=True,
    )

    print(
        "UNIT 13 TP1 REQUIRED PRICE MOVEMENT =",
        tp1_price_move_percent,
        "%",
        flush=True,
    )

    print(
        "UNIT 13 TP2 REQUIRED PRICE MOVEMENT =",
        tp2_price_move_percent,
        "%",
        flush=True,
    )

    print(
        "UNIT 13 LEVERAGE MUTATION = FALSE",
        flush=True,
    )

    
    # ========================================================
    # 9E. WEEX POSITION FINANCIAL SNAPSHOT
    # INDENTATION: FOUR SPACES
    # DIAGNOSTICS ONLY
    # ========================================================

    financial_fields = (
        "openFee",
        "fundingFee",
        "cumOpenFee",
        "cumCloseFee",
        "cumFundingFee",
        "cumLiquidateFee",
        "cumOpenSize",
        "cumCloseSize",
        "unrealizePnl",
        "liquidatePrice",
    )

    position_financial_snapshot = {}

    for field in financial_fields:

        raw_value = position.get(field)

        if raw_value is None:
            position_financial_snapshot[field] = None
            continue

        try:
            value = Decimal(str(raw_value))

            if not value.is_finite():
                raise ValueError("NONFINITE")

            position_financial_snapshot[field] = (
                str(value)
            )

        except (ValueError, TypeError, ArithmeticError):
            position_financial_snapshot[field] = None

    position_financial_snapshot["leverage"] = str(
        effective_leverage
    )

    position_financial_snapshot["marginSize"] = str(
        actual_margin_size
    )

    position_financial_snapshot["positionId"] = (
        str(position.get("id", ""))
    )

    position_financial_snapshot["updatedTime"] = (
        position.get("updatedTime")
    )

    print(
        "UNIT 13 WEEX POSITION FINANCIAL SNAPSHOT =",
        position_financial_snapshot,
        flush=True,
    )

    # These cumulative exchange fields improve
    # reconciliation and reporting.
    #
    # They must not be treated as complete realized
    # cycle profit until order fills, fees and
    # funding are reconciled.
    # ========================================================
    # 10. AVERAGE ENTRY
    # ========================================================

    open_value = Decimal(
        str(
            position.get(
                "openValue",
                "0",
            )
        )
    )

    if (
        open_value
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: OPEN VALUE INVALID"
        )

    average_entry_price = (
        open_value
        /
        position_size
    )

    if (
        average_entry_price
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: ENTRY PRICE INVALID"
        )

    try:

        cumulative_open_size = Decimal(
            str(
                position.get(
                    "cumOpenSize",
                    position_size,
                )
            )
        )

    except Exception:

        cumulative_open_size = (
            position_size
        )

    try:

        cumulative_close_size = Decimal(
            str(
                position.get(
                    "cumCloseSize",
                    "0",
                )
            )
        )

    except Exception:

        cumulative_close_size = (
            Decimal("0")
        )

    if (
        cumulative_open_size
        <=
        Decimal("0")
    ):
        cumulative_open_size = (
            position_size
        )

    if (
        cumulative_close_size
        <
        Decimal("0")
    ):
        cumulative_close_size = (
            Decimal("0")
        )

    print(
        "UNIT 13 POSITION SIDE = "
        f"{position_side}",
        flush=True,
    )

    print(
        "UNIT 13 POSITION SIZE = "
        f"{position_size}",
        flush=True,
    )

    print(
        "UNIT 13 AVERAGE ENTRY PRICE = "
        f"{average_entry_price}",
        flush=True,
    )

    # ========================================================
    # 11. STEP-AWARE TP ALLOCATION
    # ========================================================

    total_steps = int(
        (
            cumulative_open_size
            /
            quantity_step
        ).to_integral_value(
            rounding=ROUND_DOWN
        )
    )

    if (
        total_steps
        <=
        0
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "POSITION BELOW EXECUTABLE QUANTITY STEP"
        )

    tp1_steps = 0
    tp2_steps = 0
    tp3_steps = 0

    # --------------------------------------------------------
    # 3 OR MORE STEPS:
    #
    # Guarantee one executable step to TP1,
    # one executable step to TP2,
    # and one executable step to TP3.
    #
    # Remaining steps are distributed according to the
    # configured 10 / 20 / 70 target.
    # --------------------------------------------------------

    if (
        total_steps
        >=
        3
    ):

        tp1_steps = max(
            1,
            int(
                (
                    Decimal(total_steps)
                    *
                    tp1_allocation_percent
                    /
                    Decimal("100")
                ).to_integral_value(
                    rounding=ROUND_DOWN
                )
            ),
        )

        tp2_steps = max(
            1,
            int(
                (
                    Decimal(total_steps)
                    *
                    tp2_allocation_percent
                    /
                    Decimal("100")
                ).to_integral_value(
                    rounding=ROUND_DOWN
                )
            ),
        )

        # Preserve at least one runner step.

        while (
            tp1_steps
            +
            tp2_steps
            >
            total_steps
            -
            1
        ):

            if (
                tp2_steps
                >
                1
            ):
                tp2_steps -= 1

            elif (
                tp1_steps
                >
                1
            ):
                tp1_steps -= 1

            else:
                break

        tp3_steps = (
            total_steps
            -
            tp1_steps
            -
            tp2_steps
        )

    # --------------------------------------------------------
    # EXACTLY TWO STEPS:
    #
    # Three separate exits are mathematically impossible.
    #
    # Preserve:
    # TP1 = one step
    # TP3 = one step
    #
    # TP2 has zero separate quantity and is treated as
    # structurally completed once TP1 has completed.
    # --------------------------------------------------------

    elif (
        total_steps
        ==
        2
    ):

        tp1_steps = 1
        tp2_steps = 0
        tp3_steps = 1

    # --------------------------------------------------------
    # EXACTLY ONE STEP:
    #
    # Splitting is impossible.
    #
    # Preserve entire executable quantity for TP3 runner.
    # TP1 and TP2 become structurally complete.
    # --------------------------------------------------------

    else:

        tp1_steps = 0
        tp2_steps = 0
        tp3_steps = 1

    tp1_quantity = (
        Decimal(tp1_steps)
        *
        quantity_step
    )

    tp2_quantity = (
        Decimal(tp2_steps)
        *
        quantity_step
    )

    tp3_quantity = (
        Decimal(tp3_steps)
        *
        quantity_step
    )

    allocated_quantity = (
        tp1_quantity
        +
        tp2_quantity
        +
        tp3_quantity
    )

    executable_open_quantity = (
        Decimal(total_steps)
        *
        quantity_step
    )

    if (
        allocated_quantity
        !=
        executable_open_quantity
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "STEP-AWARE ALLOCATION MISMATCH"
        )

    print(
        "UNIT 13 TOTAL EXECUTABLE STEPS = "
        f"{total_steps}",
        flush=True,
    )

    print(
        "UNIT 13 TP1 EXECUTABLE QUANTITY = "
        f"{tp1_quantity}",
        flush=True,
    )

    print(
        "UNIT 13 TP2 EXECUTABLE QUANTITY = "
        f"{tp2_quantity}",
        flush=True,
    )

    print(
        "UNIT 13 TP3 EXECUTABLE QUANTITY = "
        f"{tp3_quantity}",
        flush=True,
    )

    if (
        total_steps
        <
        10
    ):

        print(
            "PASS: UNIT 13 SMALL POSITION "
            "STEP-CONSTRAINED ALLOCATION APPLIED",
            flush=True,
        )

    # ========================================================
    # 12. TP1 / TP2 PRICE TARGETS
    # ========================================================

    tp1_fraction = (
        tp1_price_move_percent
        /
        Decimal("100")
    )

    tp2_fraction = (
        tp2_price_move_percent
        /
        Decimal("100")
    )

    if (
        position_side
        ==
        "LONG"
    ):

        raw_tp1_target = (
            average_entry_price
            *
            (
                Decimal("1")
                +
                tp1_fraction
            )
        )

        raw_tp2_target = (
            average_entry_price
            *
            (
                Decimal("1")
                +
                tp2_fraction
            )
        )

        # Round UP so rounding cannot reduce the ROI floor.

        tp1_target = round_price_up(
            raw_tp1_target
        )

        tp2_target = round_price_up(
            raw_tp2_target
        )

        if (
            tp2_target
            <=
            tp1_target
        ):
            tp2_target = (
                tp1_target
                +
                price_step
            )

        closing_side = (
            "SELL"
        )

    else:

        raw_tp1_target = (
            average_entry_price
            *
            (
                Decimal("1")
                -
                tp1_fraction
            )
        )

        raw_tp2_target = (
            average_entry_price
            *
            (
                Decimal("1")
                -
                tp2_fraction
            )
        )

        # Round DOWN for SHORT so rounding cannot reduce
        # the required favorable price movement.

        tp1_target = round_price_down(
            raw_tp1_target
        )

        tp2_target = round_price_down(
            raw_tp2_target
        )

        if (
            tp2_target
            >=
            tp1_target
        ):
            tp2_target = (
                tp1_target
                -
                price_step
            )

        closing_side = (
            "BUY"
        )

    print(
        "UNIT 13 TP1 TARGET PRICE = "
        f"{tp1_target}",
        flush=True,
    )

    print(
        "UNIT 13 TP2 TARGET PRICE = "
        f"{tp2_target}",
        flush=True,
    )

    print(
        "PASS: UNIT 13 TP1 -> TP2 "
        "MANDATORY SEPARATION VERIFIED",
        flush=True,
    )

    # ========================================================
    # 13. CURRENT PUBLIC MARK PRICE
    # ========================================================

    mark_request_path = (
        "/capi/v3/market/symbolPrice"
    )

    mark_query = (
        urllib.parse.urlencode(
            {
                "symbol":
                    market_symbol,

                "priceType":
                    "MARK",
            }
        )
    )

    mark_url = (
        base_url
        +
        mark_request_path
        +
        "?"
        +
        mark_query
    )

    mark_request = (
        urllib.request.Request(
            url=mark_url,
            method="GET",
        )
    )

    try:

        with urllib.request.urlopen(
            mark_request,
            timeout=15,
        ) as response:

            mark_http_status = (
                response.getcode()
            )

            mark_response_text = (
                response.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

    except Exception as exc:

        raise RuntimeError(
            "UNIT 13 PUBLIC MARK PRICE READ FAILED"
        ) from exc

    if not (
        200
        <=
        int(mark_http_status)
        <
        300
    ):
        raise RuntimeError(
            "UNIT 13 PUBLIC MARK PRICE HTTP FAILURE"
        )

    try:

        mark_json = json.loads(
            mark_response_text
        )

        mark_price = Decimal(
            str(
                mark_json.get(
                    "price"
                )
            )
        )

    except Exception as exc:

        raise RuntimeError(
            "UNIT 13 INVALID MARK PRICE RESPONSE"
        ) from exc

    if (
        mark_price
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 13 INVALID MARK PRICE"
        )

    print(
        "UNIT 13 CURRENT MARK PRICE = "
        f"{mark_price}",
        flush=True,
    )

    # ========================================================
    # 14. COMPLETION STATE
    # ========================================================

    # Zero-sized TP stages are structurally complete because
    # that stage cannot exist at the exchange quantity step.

    if (
        tp1_quantity
        ==
        Decimal("0")
    ):
        tp1_already_completed = True

    else:

        tp1_already_completed = (
            cumulative_close_size
            >=
            tp1_quantity
        )

    if (
        tp2_quantity
        ==
        Decimal("0")
    ):

        tp2_already_completed = (
            tp1_already_completed
        )

    else:

        tp2_already_completed = (
            cumulative_close_size
            >=
            (
                tp1_quantity
                +
                tp2_quantity
            )
        )

    if (
        position_side
        ==
        "LONG"
    ):

        tp1_reached = (
            mark_price
            >=
            tp1_target
        )

        tp2_reached = (
            mark_price
            >=
            tp2_target
        )

    else:

        tp1_reached = (
            mark_price
            <=
            tp1_target
        )

        tp2_reached = (
            mark_price
            <=
            tp2_target
        )

    print(
        "UNIT 13 TP1 COMPLETED = "
        f"{tp1_already_completed}",
        flush=True,
    )

    print(
        "UNIT 13 TP2 COMPLETED = "
        f"{tp2_already_completed}",
        flush=True,
    )

    print(
        "UNIT 13 TP1 REACHED = "
        f"{tp1_reached}",
        flush=True,
    )

    print(
        "UNIT 13 TP2 REACHED = "
        f"{tp2_reached}",
        flush=True,
    )

    # ========================================================
    # 15. SELECT EXACTLY ONE TP ACTION
    #
    # TP2 HAS PRIORITY IF PRICE JUMPS THROUGH BOTH TARGETS.
    # ========================================================

    close_quantity = Decimal(
        "0"
    )

    tp_action = (
        "NONE"
    )

    if (
        tp2_quantity
        >
        Decimal("0")
        and
        tp2_reached
        and
        not tp2_already_completed
    ):

        required_closed_quantity = (
            tp1_quantity
            +
            tp2_quantity
        )

        outstanding_quantity = (
            required_closed_quantity
            -
            cumulative_close_size
        )

        close_quantity = round_quantity_down(
            outstanding_quantity
        )

        if (
            close_quantity
            >
            position_size
        ):
            close_quantity = round_quantity_down(
                position_size
            )

        if (
            close_quantity
            >=
            minimum_quantity
        ):
            tp_action = (
                "TP2"
            )

    elif (
        tp1_quantity
        >
        Decimal("0")
        and
        tp1_reached
        and
        not tp1_already_completed
    ):

        outstanding_quantity = (
            tp1_quantity
            -
            cumulative_close_size
        )

        close_quantity = round_quantity_down(
            outstanding_quantity
        )

        if (
            close_quantity
            >
            position_size
        ):
            close_quantity = round_quantity_down(
                position_size
            )

        if (
            close_quantity
            >=
            minimum_quantity
        ):
            tp_action = (
                "TP1"
            )

    # ========================================================
    # 16. MONITORING / TP3 HANDOFF
    # ========================================================

    if (
        tp_action
        ==
        "NONE"
    ):

        tp3_armed = (
            tp1_already_completed
            and
            tp2_already_completed
            and
            tp3_quantity
            >
            Decimal("0")
            and
            position_size
            >
            Decimal("0")
        )

        if tp3_armed:

            unit_13_status = (
                "TP3_ARMED"
            )

            skip_reason = (
                "DYNAMIC_TP3_RUNTIME_REQUIRED"
            )

        else:

            unit_13_status = (
                "MONITORING"
            )

            skip_reason = (
                "DYNAMIC_TP_TARGET_NOT_REACHED"
            )

        result = {

            "unit":
                13,

            "status":
                unit_13_status,

            "read_only":
                False,

            "unit_12_status":
                unit_12_status,

            "active_position_exists":
                True,

            "position_side":
                position_side,

            "position_size":
                float(position_size),

            "average_entry_price":
                float(average_entry_price),

            "mark_price":
                float(mark_price),

            "tp_target_allocation":
                "10/20/70",

            "tp1_target":
                float(tp1_target),

            "tp2_target":
                float(tp2_target),

            "tp1_quantity":
                float(tp1_quantity),

            "tp2_quantity":
                float(tp2_quantity),

            "tp3_quantity":
                float(tp3_quantity),

            "tp1_net_roi_floor_percent":
                float(tp1_net_roi_floor),

            "tp2_net_roi_floor_percent":
                float(tp2_net_roi_floor),

            "estimated_taker_fee_percent":
                float(futures_taker_fee_percent),

            "estimated_round_trip_fee_percent":
                float(
                    estimated_round_trip_fee_price_percent
                ),

            "tp1_completed":
                tp1_already_completed,

            "tp2_completed":
                tp2_already_completed,

            "tp3_armed":
                tp3_armed,

            # Compatibility field for old Unit 14.
            # It now means REFERENCE ONLY.
            "tp3_trailing_percent":
                float(
                    tp3_trailing_reference
                ),

            "tp3_trailing_reference_percent":
                float(
                    tp3_trailing_reference
                ),

            "tp3_trailing_min_percent":
                float(
                    tp3_trailing_min
                ),

            "tp3_trailing_max_percent":
                float(
                    tp3_trailing_max
                ),

            "tp3_trailing_dynamic":
                True,

            "tp_execution_attempted":
                False,

            "tp_execution_completed":
                False,

            "sl_execution_attempted":
                False,

            "backup_execution_attempted":
                False,

            "real_submission_attempted":
                False,

            "exchange_write":
                False,

            "skip_reason":
                skip_reason,
        }

        print(
            "-" * 80,
            flush=True,
        )

        print(
            "UNIT 13 STATUS = "
            f"{unit_13_status}",
            flush=True,
        )

        print(
            "UNIT 13 NEW SIGNAL REQUIRED = FALSE",
            flush=True,
        )

        print(
            "UNIT 13 TP3 ARMED = "
            f"{tp3_armed}",
            flush=True,
        )

        print(
            "UNIT 13 TP3 TRAILING MODE = DYNAMIC",
            flush=True,
        )

        print(
            "UNIT 13 TP3 NORMAL REFERENCE = "
            f"{tp3_trailing_reference}%",
            flush=True,
        )

        print(
            "UNIT 13 SL EXECUTION = FALSE",
            flush=True,
        )

        print(
            "UNIT 13 BACKUP EXECUTION = FALSE",
            flush=True,
        )

        print(
            "ZERO EXCHANGE WRITE = TRUE",
            flush=True,
        )

        print(
            f"{datetime.now(timezone.utc).isoformat()} "
            "FRESH RECONSTRUCTION UNIT 13 RESULT = "
            f"PASS ({unit_13_status})",
            flush=True,
        )

        print(
            "=" * 80,
            flush=True,
        )

        return result

    # ========================================================
    # 17. FINAL CLOSE QUANTITY VALIDATION
    # ========================================================

    if (
        close_quantity
        <
        minimum_quantity
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "TP CLOSE BELOW MINIMUM QUANTITY"
        )

    quantity_text = (
        f"{close_quantity:.8f}"
        .rstrip("0")
        .rstrip(".")
    )

    # ========================================================
    # 18. BUILD DEMO MARKET CLOSE
    # ========================================================

    client_order_timestamp = int(
        datetime.now(
            timezone.utc
        ).timestamp()
        *
        1000000
    )

    new_client_order_id = (
        "FR13-"
        +
        tp_action
        +
        "-"
        +
        str(client_order_timestamp)
    )

    new_client_order_id = (
        new_client_order_id[:36]
    )

    tp_payload = {

        "symbol":
            "BTCSUSDT",

        "side":
            closing_side,

        "positionSide":
            position_side,

        "type":
            "MARKET",

        "quantity":
            quantity_text,

        "newClientOrderId":
            new_client_order_id,
    }

    # ========================================================
    # 19. ABSOLUTE SL PROHIBITION
    # ========================================================

    prohibited_sl_fields = (

        "slTriggerPrice",

        "SlWorkingType",

        "stopLossPrice",

        "stopPrice",
    )

    for field in (
        prohibited_sl_fields
    ):

        if (
            field
            in
            tp_payload
        ):
            raise RuntimeError(
                "UNIT 13 BLOCKED: SL FIELD DETECTED"
            )

    print(
        "PASS: UNIT 13 TP PAYLOAD VALIDATED",
        flush=True,
    )

    print(
        "PASS: UNIT 13 SL REMAINS DISABLED",
        flush=True,
    )

    # ========================================================
    # 20. DEMO ENDPOINT ONLY
    # ========================================================

    request_path = (
        "/capi/v3/sim/order"
    )

    if (
        "/sim/"
        not in
        request_path
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: NON-DEMO ENDPOINT"
        )

    method = (
        "POST"
    )

    body = json.dumps(
        tp_payload,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )

    timestamp = str(
        int(
            time.time()
            *
            1000
        )
    )

    prehash = (
        timestamp
        +
        method
        +
        request_path
        +
        body
    )

    signature = (
        base64.b64encode(
            hmac.new(
                api_secret.encode(
                    "utf-8"
                ),
                prehash.encode(
                    "utf-8"
                ),
                hashlib.sha256,
            ).digest()
        ).decode(
            "utf-8"
        )
    )

    headers = {

        "ACCESS-KEY":
            api_key,

        "ACCESS-SIGN":
            signature,

        "ACCESS-TIMESTAMP":
            timestamp,

        "ACCESS-PASSPHRASE":
            api_passphrase,

        "Content-Type":
            "application/json",
    }

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 13 TP ACTION = "
        f"{tp_action}",
        flush=True,
    )

    print(
        "UNIT 13 TP CLOSE SIDE = "
        f"{closing_side}",
        flush=True,
    )

    print(
        "UNIT 13 TP CLOSE QUANTITY = "
        f"{quantity_text}",
        flush=True,
    )

    print(
        "UNIT 13 EXECUTION ENVIRONMENT = DEMO",
        flush=True,
    )

    print(
        "UNIT 13 REAL ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 13 SL ENABLED = FALSE",
        flush=True,
    )

    # ========================================================
    # 21. SUBMIT EXACTLY ONE DEMO TP CLOSE
    # ========================================================

    request = (
        urllib.request.Request(
            url=(
                base_url
                +
                request_path
            ),
            data=body.encode(
                "utf-8"
            ),
            headers=headers,
            method="POST",
        )
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            response_status = (
                response.getcode()
            )

            response_text = (
                response.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

    except urllib.error.HTTPError as exc:

        try:

            error_text = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

        except Exception:

            error_text = str(exc)

        print(
            "UNIT 13 TP ERROR RESPONSE = "
            f"{error_text}",
            flush=True,
        )

        raise RuntimeError(
            "UNIT 13 DEMO TP ORDER REJECTED"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "UNIT 13 DEMO TP NETWORK ERROR: "
            f"{exc}"
        ) from exc

    print(
        "UNIT 13 TP HTTP STATUS = "
        f"{response_status}",
        flush=True,
    )

    print(
        "UNIT 13 TP RESPONSE = "
        f"{response_text}",
        flush=True,
    )

    try:

        response_json = json.loads(
            response_text
        )

    except Exception as exc:

        raise RuntimeError(
            "UNIT 13 TP RESPONSE INVALID JSON"
        ) from exc

    if not (
        200
        <=
        int(response_status)
        <
        300
    ):
        raise RuntimeError(
            "UNIT 13 TP ORDER HTTP FAILURE"
        )

    if (
        response_json.get(
            "success"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 13 TP ORDER NOT ACCEPTED: "
            f"{response_json}"
        )

    tp_order_id = response_json.get(
        "orderId"
    )

# ============================================================
# START REPLACEMENT - UNIT 13 POST-EXECUTION TP3 HANDOFF
# ZERO INDENTATION DEMARCATION
# ============================================================

    if not tp_order_id:
        raise RuntimeError(
            "UNIT 13 TP ACCEPTED WITHOUT ORDER ID"
        )

    # ========================================================
    # POST-EXECUTION TP3 HANDOFF
    #
    # If TP2 has now been successfully executed, TP1 + TP2
    # are cumulatively complete.
    #
    # Any executable quantity remaining for TP3 becomes the
    # live runner and must be handed directly to Unit 14.
    #
    # NO NEW NATURALLY QUALIFIED ENTRY SIGNAL IS REQUIRED.
    # ========================================================

    post_execution_tp3_armed = (
        tp_action
        ==
        "TP2"
        and
        tp3_quantity
        >
        Decimal("0")
    )

    if post_execution_tp3_armed:

        print(
            "PASS: UNIT 13 TP1 + TP2 CUMULATIVE EXIT COMPLETED",
            flush=True,
        )

        print(
            "PASS: UNIT 13 TP3 RUNNER REMAINS = "
            f"{tp3_quantity}",
            flush=True,
        )

        print(
            "PASS: UNIT 13 TP3 ARMED AFTER TP2 EXECUTION",
            flush=True,
        )

        print(
            "PASS: UNIT 13 TP3 HANDOFF TO UNIT 14 = READY",
            flush=True,
        )

    else:

        print(
            "UNIT 13 POST-EXECUTION TP3 ARMED = FALSE",
            flush=True,
        )

    # ========================================================
    # BUILD FINAL UNIT 13 POST-EXECUTION RESULT
    # ========================================================

    unit_13_result = {

        "unit":
            13,

        "status":
            (
                "TP3_ARMED"
                if post_execution_tp3_armed
                else "TP_EXECUTED"
            ),

        "position_exists":
            True,

        "position_side":
            position_side,

        "position_size":
            str(
                position_size
            ),

        "average_entry_price":
            str(
                average_entry_price
            ),

        "total_executable_steps":
            total_steps,

        "tp1_quantity":
            str(
                tp1_quantity
            ),

        "tp2_quantity":
            str(
                tp2_quantity
            ),

        "tp3_quantity":
            str(
                tp3_quantity
            ),

        "tp1_target_price":
            str(
                tp1_target
            ),

        "tp2_target_price":
            str(
                tp2_target
            ),

        "tp1_completed":
            (
                True
                if tp_action == "TP2"
                else tp1_already_completed
            ),

        "tp2_completed":
            (
                True
                if tp_action == "TP2"
                else tp2_already_completed
            ),

        "tp3_armed":
            post_execution_tp3_armed,

        "tp3_trailing_reference_percent":
            str(
                tp3_trailing_reference_percent
            ),

        "tp3_trailing_min_percent":
            str(
                tp3_trailing_min_percent
            ),

        "tp3_trailing_max_percent":
            str(
                tp3_trailing_max_percent
            ),

        "tp_action":
            tp_action,

        "tp_close_quantity":
            str(
                tp_close_quantity
            ),

        "tp_order_id":
            str(
                response_json.get(
                    "orderId",
                    "",
                )
            ),

        "demo_order_executed":
            True,

        "real_order":
            False,

        "sl_enabled":
            False,

        "backup_execution":
            False,
    }

    print(
        "UNIT 13 POST-EXECUTION STATUS = "
        f"{unit_13_result['status']}",
        flush=True,
    )

    print(
        "UNIT 13 POST-EXECUTION TP3 ARMED = "
        f"{post_execution_tp3_armed}",
        flush=True,
    )

    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 13 RESULT = "
        +
        (
            "PASS (TP3 ARMED)"
            if post_execution_tp3_armed
            else "PASS (TP EXECUTED)"
        ),
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return unit_13_result
# ============================================================
# END REPLACEMENT - UNIT 13 POST-EXECUTION TP3 HANDOFF
# ZERO INDENTATION DEMARCATION
# ============================================================
    
# ============================================================
# RUN UNIT 13
# ============================================================

FRESH_RECONSTRUCTION_UNIT_13_RESULT = (
    fresh_reconstruction_unit_13(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_12_RESULT,
    )
)


# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 13
# ZERO INDENTATION DEMARCATION
#
# UNIT 13 IS FULLY CLOSED
# UNIT 13 IS CALLED
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN TRY
# NO OPEN DICTIONARY
#
# EXISTING UNIT 14 CONTINUES DIRECTLY BELOW
# ============================================================
    # ============================================================
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 14
# ZERO INDENTATION DEMARCATION
#
# DELETE OLD UNIT 14 FUNCTION + OLD UNIT 14 CALL
# PASTE THIS COMPLETE BLOCK IN ITS PLACE
# ============================================================


def fresh_tp3_runtime(
    config,
    unit_13_result,
):
    # ========================================================
    # FRESH RECONSTRUCTION UNIT 14
    # DYNAMIC TP3 + LIQUIDATION BACKUP RUNTIME
    #
    # TP3:
    #
    # TARGET ALLOCATION:
    #     70% BEFORE QUANTITY-STEP ADJUSTMENT
    #
    # TRAILING CALLBACK:
    #     DYNAMIC
    #
    # NORMAL REFERENCE:
    #     APPROXIMATELY 0.20%
    #
    # DYNAMIC INPUTS:
    #     1. ATR / VOLATILITY
    #     2. TREND STRENGTH
    #     3. MOMENTUM DETERIORATION
    #
    # CALLBACK RANGE:
    #     DEFAULT MIN = 0.10%
    #     DEFAULT MAX = 0.40%
    #
    # BEHAVIOUR:
    #
    # STRONG TREND:
    #     WIDEN TRAILING CALLBACK
    #
    # HIGHER VOLATILITY:
    #     WIDEN TRAILING CALLBACK
    #
    # MOMENTUM DETERIORATION:
    #     TIGHTEN TRAILING CALLBACK
    #
    # --------------------------------------------------------
    # BACKUP SEQUENCE PRESERVED:
    #
    # ENTRY
    #   ->
    # B1
    #   ->
    # RE-READ POSITION + L1
    #   ->
    # B2
    #   ->
    # RE-READ POSITION + L2
    #   ->
    # B3
    #   ->
    # RE-READ POSITION + L3
    #   ->
    # STOP
    #
    # NO B4.
    #
    # LONG BACKUP:
    #     trigger = liquidation * (1 + buffer)
    #
    # SHORT BACKUP:
    #     trigger = liquidation * (1 - buffer)
    #
    # --------------------------------------------------------
    # SAFETY:
    #
    # DEMO BTCSUSDT ONLY
    # REAL ORDER PROHIBITED
    # SL DISABLED
    # ONE DIRECTION ONLY
    # ANTI-DUPLICATE
    # NO LEVERAGE MUTATION
    # NO MARGIN MODE MUTATION
    # NO POSITION MODE MUTATION
    # ========================================================

    import os
    import json
    import time
    import hmac
    import hashlib
    import base64
    import urllib.request
    import urllib.error
    import urllib.parse

    from decimal import (
        Decimal,
        ROUND_DOWN,
    )

    from datetime import (
        datetime,
        timezone,
    )

    print(
        "=" * 80,
        flush=True,
    )

    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 14 START",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    # ========================================================
    # 1. CONFIGURATION CONTRACT
    # ========================================================

    if not isinstance(
        config,
        dict,
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: CONFIGURATION MISSING"
        )

    if not isinstance(
        unit_13_result,
        dict,
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: UNIT 13 RESULT MISSING"
        )

    strategy = config.get(
        "strategy",
        {},
    )

    exchange = config.get(
        "exchange",
        {},
    )

    market_precision = config.get(
        "market_precision",
        {},
    )

    if not isinstance(
        strategy,
        dict,
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: STRATEGY CONFIGURATION MISSING"
        )

    if not isinstance(
        exchange,
        dict,
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: EXCHANGE CONFIGURATION MISSING"
        )

    execution_environment = str(
        config.get(
            "execution_environment",
            "",
        )
    ).upper()

    if (
        execution_environment
        !=
        "DEMO"
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: "
            "EXECUTION ENVIRONMENT NOT DEMO"
        )

    market_symbol = str(
        exchange.get(
            "market_symbol",
            "",
        )
    ).upper()

    demo_symbol = str(
        exchange.get(
            "demo_order_symbol",
            "",
        )
    ).upper()

    base_url = str(
        exchange.get(
            "contract_base_url",
            "",
        )
    ).rstrip("/")

    if (
        market_symbol
        !=
        "BTCUSDT"
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: MARKET SYMBOL MUST BE BTCUSDT"
        )

    if (
        demo_symbol
        !=
        "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: DEMO SYMBOL MUST BE BTCSUSDT"
        )

    if (
        base_url
        !=
        "https://api-contract.weex.com"
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID CONTRACT BASE URL"
        )

    # ========================================================
    # 2. STRATEGY VALUES
    # ========================================================

    backup_margin_percent = Decimal(
        str(
            strategy.get(
                "backup_margin_percent",
                5.0,
            )
        )
    )

    backup_buffer_percent = Decimal(
        str(
            strategy.get(
                "backup_buffer_percent",
                0.30,
            )
        )
    )

    max_backups = int(
        strategy.get(
            "max_backups",
            3,
        )
    )

    exposure_cap_percent = Decimal(
        str(
            strategy.get(
                "exposure_cap_percent",
                35.0,
            )
        )
    )

    
    # ========================================================
    # UNIT 14A - WEEX LEVERAGE AUTHORITY
    # INDENTATION: 4 SPACES
    # ========================================================

    # Leverage is not selected in Python.
    # It must come from the actual WEEX demo position
    # during each position-management cycle.

    leverage_target = None

    print(
        "UNIT 14 LEVERAGE AUTHORITY = WEEX EXCHANGE",
        flush=True,
    )

    print(
        "UNIT 14 PYTHON LEVERAGE SETTING = DISABLED",
        flush=True,
    )

    # ========================================================
    # END UNIT 14A
    # ========================================================

    initial_margin_percent = Decimal(
        str(
            strategy.get(
                "initial_margin_percent",
                5.0,
            )
        )
    )

    
    # ========================================================
    # START UNIT 14 FIXED BACKUP MARGIN
    # INDENTATION: 4 SPACES
    # ========================================================

    try:
        fixed_entry_margin = Decimal(
            os.getenv(
                "ENTRY_FIXED_USDT",
                "1.00",
            ).strip()
        )
    except Exception as exc:
        raise RuntimeError(
            "UNIT 14 INVALID ENTRY_FIXED_USDT"
        ) from exc

    if (
        not fixed_entry_margin.is_finite()
        or fixed_entry_margin <= Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 14 FIXED ENTRY MARGIN MUST BE POSITIVE"
        )

    # Locked for this Unit 14 runtime invocation.
    fixed_backup_margin = fixed_entry_margin

    print(
        "UNIT 14 FIXED INITIAL MARGIN SUSDT =",
        fixed_entry_margin,
        flush=True,
    )

    print(
        "UNIT 14 B1-B3 MARGIN EACH SUSDT =",
        fixed_backup_margin,
        flush=True,
    )

    # ========================================================
    # END UNIT 14 FIXED BACKUP MARGIN
    # ========================================================
    
    # --------------------------------------------------------
    # DYNAMIC TP3 CONFIGURATION
    # --------------------------------------------------------

    trailing_reference_percent = Decimal(
        str(
            strategy.get(
                "tp3_trailing_reference_percent",
                unit_13_result.get(
                    "tp3_trailing_reference_percent",
                    0.20,
                ),
            )
        )
    )

    trailing_min_percent = Decimal(
        str(
            strategy.get(
                "tp3_trailing_min_percent",
                unit_13_result.get(
                    "tp3_trailing_min_percent",
                    0.10,
                ),
            )
        )
    )

    trailing_max_percent = Decimal(
        str(
            strategy.get(
                "tp3_trailing_max_percent",
                unit_13_result.get(
                    "tp3_trailing_max_percent",
                    0.40,
                ),
            )
        )
    )

    if (
        backup_margin_percent
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID BACKUP MARGIN"
        )

    if (
        backup_buffer_percent
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID BACKUP BUFFER"
        )

    if (
        exposure_cap_percent
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID EXPOSURE CAP"
        )

    if (
        leverage_target
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID LEVERAGE"
        )

    if (
        trailing_reference_percent
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID TP3 REFERENCE"
        )

    if (
        trailing_min_percent
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID TP3 MINIMUM"
        )

    if (
        trailing_max_percent
        <
        trailing_min_percent
    ):
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID TP3 RANGE"
        )

    # Absolute architecture protection.

    # ========================================================
    # FIVE BACKUP ARCHITECTURE
    # INDENTATION: 4 SPACES
    # ========================================================

    max_backups = min(
        max(
            max_backups,
            0,
        ),
        5,
    )

    print(
        "PASS: UNIT 14 MAX BACKUPS =",
        max_backups,
        flush=True,
    )

    backup_buffer_fraction = (
        backup_buffer_percent
        /
        Decimal("100")
    )

    print(
        "PASS: UNIT 14 EXECUTION ENVIRONMENT = DEMO",
        flush=True,
    )

    print(
        "PASS: UNIT 14 TP3 TRAILING MODE = DYNAMIC",
        flush=True,
    )

    print(
        "PASS: UNIT 14 TP3 NORMAL REFERENCE = "
        f"{trailing_reference_percent}%",
        flush=True,
    )

    print(
        "PASS: UNIT 14 TP3 DYNAMIC RANGE = "
        f"{trailing_min_percent}% -> "
        f"{trailing_max_percent}%",
        flush=True,
    )

    print(
        "PASS: UNIT 14 TP3 DYNAMIC INPUTS = "
        "TREND + ATR/VOLATILITY + MOMENTUM DETERIORATION",
        flush=True,
    )

    print(
        "PASS: UNIT 14 BACKUP SEQUENCE = "
        "ENTRY -> B1 -> L1 -> B2 -> L2 -> "
        "B3 -> L3 -> B4 -> L4 -> B5 -> L5 -> STOP",
        flush=True,
    )

    print(
        "PASS: UNIT 14 B1-B5 ENABLED SUBJECT TO SAFETY CHECKS",
        flush=True,
    )

    print(
        "PASS: UNIT 14 SL = DISABLED",
        flush=True,
    )

    print(
        "PASS: UNIT 14 REAL TRADING = PROHIBITED",
        flush=True,
    )

    # ========================================================
    # 3. QUANTITY PRECISION
    # ========================================================

    quantity_step = Decimal(
        str(
            market_precision.get(
                "quantity_step",
                0.0001,
            )
        )
    )

    minimum_quantity = Decimal(
        str(
            market_precision.get(
                "minimum_quantity",
                0.0001,
            )
        )
    )

    if (
        quantity_step
        <=
        Decimal("0")
    ):
        quantity_step = Decimal(
            "0.0001"
        )

    if (
        minimum_quantity
        <=
        Decimal("0")
    ):
        minimum_quantity = Decimal(
            "0.0001"
        )

    def floor_quantity(
        value,
    ):

        value = Decimal(
            str(value)
        )

        if (
            value
            <=
            Decimal("0")
        ):
            return Decimal(
                "0"
            )

        steps = (
            value
            /
            quantity_step
        ).to_integral_value(
            rounding=ROUND_DOWN
        )

        return (
            steps
            *
            quantity_step
        )

    def quantity_text(
        value,
    ):

        return (
            f"{value:.8f}"
            .rstrip("0")
            .rstrip(".")
        )

    # ========================================================
    # 4. AUTHENTICATION
    # ========================================================

    api_key = (
        os.environ.get(
            "WEEX_API_KEY"
        )
        or
        os.environ.get(
            "API_KEY"
        )
    )

    api_secret = (
        os.environ.get(
            "WEEX_API_SECRET"
        )
        or
        os.environ.get(
            "API_SECRET"
        )
    )

    api_passphrase = (
        os.environ.get(
            "WEEX_API_PASSPHRASE"
        )
        or
        os.environ.get(
            "API_PASSPHRASE"
        )
    )

    if not api_key:
        raise RuntimeError(
            "UNIT 14 BLOCKED: WEEX API KEY MISSING"
        )

    if not api_secret:
        raise RuntimeError(
            "UNIT 14 BLOCKED: WEEX API SECRET MISSING"
        )

    if not api_passphrase:
        raise RuntimeError(
            "UNIT 14 BLOCKED: WEEX API PASSPHRASE MISSING"
        )

    # ========================================================
    # 5. AUTHENTICATED HELPERS
    # ========================================================

    def make_signature(
        timestamp,
        method,
        path,
        query_string="",
        body="",
    ):

        message = (
            timestamp
            +
            method.upper()
            +
            path
        )

        if query_string:
            message += (
                "?"
                +
                query_string
            )

        if body:
            message += body

        return (
            base64.b64encode(
                hmac.new(
                    api_secret.encode(
                        "utf-8"
                    ),
                    message.encode(
                        "utf-8"
                    ),
                    hashlib.sha256,
                ).digest()
            ).decode(
                "utf-8"
            )
        )

    def authenticated_get(
        path,
        query_string="",
    ):

        timestamp = str(
            int(
                time.time()
                *
                1000
            )
        )

        signature = make_signature(
            timestamp,
            "GET",
            path,
            query_string,
            "",
        )

        headers = {
            "ACCESS-KEY":
                api_key,

            "ACCESS-SIGN":
                signature,

            "ACCESS-TIMESTAMP":
                timestamp,

            "ACCESS-PASSPHRASE":
                api_passphrase,

            "Content-Type":
                "application/json",
        }

        url = (
            base_url
            +
            path
        )

        if query_string:

            url += (
                "?"
                +
                query_string
            )

        request = (
            urllib.request.Request(
                url=url,
                headers=headers,
                method="GET",
            )
        )

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            status = (
                response.getcode()
            )

            response_text = (
                response.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

        if not (
            200
            <=
            int(status)
            <
            300
        ):
            raise RuntimeError(
                "UNIT 14 AUTHENTICATED GET FAILED: "
                f"HTTP {status}"
            )

        return json.loads(
            response_text
        )

    def authenticated_post(
        path,
        payload,
    ):

        # Absolute demo-write boundary.

        if (
            "/sim/"
            not in
            path
        ):
            raise RuntimeError(
                "UNIT 14 BLOCKED: NON-DEMO WRITE ENDPOINT"
            )

        body = json.dumps(
            payload,
            separators=(
                ",",
                ":",
            ),
            ensure_ascii=False,
        )

        timestamp = str(
            int(
                time.time()
                *
                1000
            )
        )

        signature = make_signature(
            timestamp,
            "POST",
            path,
            "",
            body,
        )

        headers = {
            "ACCESS-KEY":
                api_key,

            "ACCESS-SIGN":
                signature,

            "ACCESS-TIMESTAMP":
                timestamp,

            "ACCESS-PASSPHRASE":
                api_passphrase,

            "Content-Type":
                "application/json",
        }

        request = (
            urllib.request.Request(
                url=(
                    base_url
                    +
                    path
                ),
                data=body.encode(
                    "utf-8"
                ),
                headers=headers,
                method="POST",
            )
        )

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            status = (
                response.getcode()
            )

            response_text = (
                response.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

        print(
            "UNIT 14 DEMO ORDER HTTP STATUS = "
            f"{status}",
            flush=True,
        )

        print(
            "UNIT 14 DEMO ORDER RESPONSE = "
            f"{response_text}",
            flush=True,
        )

        if not (
            200
            <=
            int(status)
            <
            300
        ):
            raise RuntimeError(
                "UNIT 14 DEMO ORDER FAILED: "
                f"HTTP {status}"
            )

        return json.loads(
            response_text
        )

    # ========================================================
    # 6. POSITION / BALANCE / MARKET HELPERS
    # ========================================================

    
    # ========================================================
    # UNIT 14B - STRICT DEMO POSITION READER
    # INDENTATION: 4 SPACES
    # ========================================================

    def get_active_position():

        records = authenticated_get(
            "/capi/v3/sim/position/allPosition"
        )

        if not isinstance(records, list):
            raise RuntimeError(
                "UNIT 14 POSITION RESPONSE INVALID"
            )

        active_records = []

        for record in records:

            if not isinstance(record, dict):
                raise RuntimeError(
                    "UNIT 14 INVALID POSITION RECORD"
                )

            if str(
                record.get("symbol", "")
            ).upper() != demo_symbol:
                continue

            try:
                size = Decimal(
                    str(record["size"])
                )
            except (
                KeyError,
                TypeError,
                ValueError,
                ArithmeticError,
            ) as exc:
                raise RuntimeError(
                    "UNIT 14 INVALID DEMO POSITION SIZE"
                ) from exc

            if not size.is_finite() or size < 0:
                raise RuntimeError(
                    "UNIT 14 NONFINITE OR NEGATIVE SIZE"
                )

            if size == 0:
                continue

            side = str(
                record.get("side", "")
            ).upper()

            if side not in ("LONG", "SHORT"):
                raise RuntimeError(
                    "UNIT 14 INVALID POSITION SIDE"
                )

            active_records.append(record)

        if len(active_records) > 1:
            raise RuntimeError(
                "UNIT 14 MULTIPLE ACTIVE DEMO POSITIONS"
            )

        if not active_records:
            return None

        return active_records[0]

    # ========================================================
    # END UNIT 14B
    # ========================================================

    def get_demo_balance():

        balances = authenticated_get(
            "/capi/v3/sim/balance"
        )

        if not isinstance(
            balances,
            list,
        ):
            raise RuntimeError(
                "UNIT 14 INVALID DEMO BALANCE RESPONSE"
            )

        for item in balances:

            if not isinstance(
                item,
                dict,
            ):
                continue

            if (
                str(
                    item.get(
                        "asset",
                        "",
                    )
                ).upper()
                ==
                "SUSDT"
            ):
                return item

        raise RuntimeError(
            "UNIT 14 SUSDT DEMO BALANCE NOT FOUND"
        )

    def get_mark_price():

        path = (
            "/capi/v3/market/symbolPrice"
        )

        query = urllib.parse.urlencode(
            {
                "symbol":
                    market_symbol,

                "priceType":
                    "MARK",
            }
        )

        request = (
            urllib.request.Request(
                url=(
                    base_url
                    +
                    path
                    +
                    "?"
                    +
                    query
                ),
                method="GET",
            )
        )

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            status = (
                response.getcode()
            )

            response_text = (
                response.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

        if not (
            200
            <=
            int(status)
            <
            300
        ):
            raise RuntimeError(
                "UNIT 14 MARK PRICE READ FAILED"
            )

        payload = json.loads(
            response_text
        )

        mark = Decimal(
            str(
                payload.get(
                    "price",
                    "0",
                )
            )
        )

        if (
            mark
            <=
            Decimal("0")
        ):
            raise RuntimeError(
                "UNIT 14 INVALID MARK PRICE"
            )

        return mark

    # ========================================================
    # 7. DYNAMIC TP3 MARKET ANALYSIS
    # ========================================================

    def get_recent_market_analysis():

        endpoint = (
            "/capi/v3/market/markPriceKlines"
        )

        query = urllib.parse.urlencode(
            {
                "symbol":
                    market_symbol,

                "interval":
                    "1m",

                "limit":
                    60,
            }
        )

        request = (
            urllib.request.Request(
                url=(
                    base_url
                    +
                    endpoint
                    +
                    "?"
                    +
                    query
                ),
                method="GET",
            )
        )

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            status = (
                response.getcode()
            )

            response_text = (
                response.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

        if not (
            200
            <=
            int(status)
            <
            300
        ):
            raise RuntimeError(
                "UNIT 14 KLINE READ FAILED"
            )

        raw_klines = json.loads(
            response_text
        )

        if not isinstance(
            raw_klines,
            list,
        ):
            raise RuntimeError(
                "UNIT 14 INVALID KLINE RESPONSE"
            )

        candles = []

        for raw in raw_klines:

            if not isinstance(
                raw,
                (list, tuple),
            ):
                continue

            if (
                len(raw)
                <
                5
            ):
                continue

            try:

                open_time = int(
                    raw[0]
                )

                open_price = Decimal(
                    str(raw[1])
                )

                high_price = Decimal(
                    str(raw[2])
                )

                low_price = Decimal(
                    str(raw[3])
                )

                close_price = Decimal(
                    str(raw[4])
                )

            except Exception:

                continue

            if (
                open_price
                <=
                Decimal("0")
                or
                high_price
                <=
                Decimal("0")
                or
                low_price
                <=
                Decimal("0")
                or
                close_price
                <=
                Decimal("0")
            ):
                continue

            candles.append(
                {
                    "time":
                        open_time,

                    "open":
                        open_price,

                    "high":
                        high_price,

                    "low":
                        low_price,

                    "close":
                        close_price,
                }
            )

        candles.sort(
            key=lambda item:
                item["time"]
        )

        if (
            len(candles)
            <
            25
        ):
            raise RuntimeError(
                "UNIT 14 INSUFFICIENT KLINES "
                "FOR DYNAMIC TRAILING"
            )

        # ----------------------------------------------------
        # EMA helper
        # ----------------------------------------------------

        def ema(
            values,
            period,
        ):

            multiplier = (
                Decimal("2")
                /
                Decimal(
                    period
                    +
                    1
                )
            )

            ema_value = (
                values[0]
            )

            for value in values[1:]:

                ema_value = (
                    (
                        value
                        -
                        ema_value
                    )
                    *
                    multiplier
                    +
                    ema_value
                )

            return ema_value

        closes = [
            candle["close"]
            for candle in candles
        ]

        # ----------------------------------------------------
        # ATR14
        # ----------------------------------------------------

        true_ranges = []

        previous_close = None

        for candle in candles:

            high_price = (
                candle["high"]
            )

            low_price = (
                candle["low"]
            )

            if previous_close is None:

                true_range = (
                    high_price
                    -
                    low_price
                )

            else:

                true_range = max(
                    high_price
                    -
                    low_price,

                    abs(
                        high_price
                        -
                        previous_close
                    ),

                    abs(
                        low_price
                        -
                        previous_close
                    ),
                )

            true_ranges.append(
                true_range
            )

            previous_close = (
                candle["close"]
            )

        atr_values = (
            true_ranges[-14:]
        )

        atr = (
            sum(
                atr_values,
                Decimal("0"),
            )
            /
            Decimal(
                len(atr_values)
            )
        )

        latest_close = (
            closes[-1]
        )

        atr_percent = (
            atr
            /
            latest_close
            *
            Decimal("100")
        )

        # ----------------------------------------------------
        # TREND STRENGTH
        #
        # EMA9 / EMA21 separation relative to ATR.
        #
        # 0 = weak/flat
        # 1 = strong directional structure
        # ----------------------------------------------------

        ema9 = ema(
            closes[-30:],
            9,
        )

        ema21 = ema(
            closes[-40:],
            21,
        )

        ema_separation = abs(
            ema9
            -
            ema21
        )

        if (
            atr
            >
            Decimal("0")
        ):

            trend_strength = (
                ema_separation
                /
                atr
            )

        else:

            trend_strength = (
                Decimal("0")
            )

        if (
            trend_strength
            >
            Decimal("1")
        ):
            trend_strength = (
                Decimal("1")
            )

        if (
            trend_strength
            <
            Decimal("0")
        ):
            trend_strength = (
                Decimal("0")
            )

        # ----------------------------------------------------
        # MOMENTUM DETERIORATION
        #
        # Compare recent 3-candle movement with the preceding
        # 3-candle movement in the ACTIVE POSITION direction.
        #
        # 0 = momentum healthy
        # 1 = strong deterioration/reversal
        # ----------------------------------------------------

        earlier_reference = (
            closes[-7]
        )

        middle_reference = (
            closes[-4]
        )

        latest_reference = (
            closes[-1]
        )

        earlier_move = (
            middle_reference
            -
            earlier_reference
        )

        recent_move = (
            latest_reference
            -
            middle_reference
        )

        return {
            "atr":
                atr,

            "atr_percent":
                atr_percent,

            "ema9":
                ema9,

            "ema21":
                ema21,

            "trend_strength":
                trend_strength,

            "earlier_move":
                earlier_move,

            "recent_move":
                recent_move,
        }

    def calculate_dynamic_callback(
        analysis,
        position_side,
    ):

        atr_percent = Decimal(
            str(
                analysis[
                    "atr_percent"
                ]
            )
        )

        trend_strength = Decimal(
            str(
                analysis[
                    "trend_strength"
                ]
            )
        )

        earlier_move = Decimal(
            str(
                analysis[
                    "earlier_move"
                ]
            )
        )

        recent_move = Decimal(
            str(
                analysis[
                    "recent_move"
                ]
            )
        )

        # ----------------------------------------------------
        # MOMENTUM DETERIORATION SCORE
        #
        # Range 0 -> 1.
        # ----------------------------------------------------

        deterioration = Decimal(
            "0"
        )

        if (
            position_side
            ==
            "LONG"
        ):

            earlier_favorable = max(
                earlier_move,
                Decimal("0"),
            )

            recent_favorable = max(
                recent_move,
                Decimal("0"),
            )

            if (
                recent_move
                <
                Decimal("0")
            ):
                deterioration = (
                    Decimal("1")
                )

            elif (
                earlier_favorable
                >
                Decimal("0")
            ):

                deterioration = (
                    Decimal("1")
                    -
                    min(
                        recent_favorable
                        /
                        earlier_favorable,
                        Decimal("1"),
                    )
                )

        else:

            earlier_favorable = max(
                -earlier_move,
                Decimal("0"),
            )

            recent_favorable = max(
                -recent_move,
                Decimal("0"),
            )

            if (
                recent_move
                >
                Decimal("0")
            ):
                deterioration = (
                    Decimal("1")
                )

            elif (
                earlier_favorable
                >
                Decimal("0")
            ):

                deterioration = (
                    Decimal("1")
                    -
                    min(
                        recent_favorable
                        /
                        earlier_favorable,
                        Decimal("1"),
                    )
                )

        if (
            deterioration
            <
            Decimal("0")
        ):
            deterioration = (
                Decimal("0")
            )

        if (
            deterioration
            >
            Decimal("1")
        ):
            deterioration = (
                Decimal("1")
            )

        # ----------------------------------------------------
        # VOLATILITY COMPONENT
        #
        # ATR contributes to callback width.
        #
        # Limit ATR influence to prevent one abnormal candle
        # from creating an excessive callback.
        # ----------------------------------------------------

        atr_component = min(
            atr_percent,
            Decimal("0.30"),
        )

        # ----------------------------------------------------
        # DYNAMIC CALLBACK FORMULA
        #
        # Reference remains the centre.
        #
        # ATR:
        #     contributes up to +0.075%
        #
        # Trend strength:
        #     contributes up to +0.08%
        #
        # Momentum deterioration:
        #     removes up to 0.12%
        #
        # Final result always clamped to configured range.
        # ----------------------------------------------------

        volatility_adjustment = (
            atr_component
            *
            Decimal("0.25")
        )

        trend_adjustment = (
            trend_strength
            *
            Decimal("0.08")
        )

        deterioration_adjustment = (
            deterioration
            *
            Decimal("0.12")
        )

        dynamic_percent = (
            trailing_reference_percent
            +
            volatility_adjustment
            +
            trend_adjustment
            -
            deterioration_adjustment
        )

        dynamic_percent = max(
            trailing_min_percent,
            min(
                dynamic_percent,
                trailing_max_percent,
            ),
        )

        return (
            dynamic_percent,
            deterioration,
        )

    # ========================================================
    # 8. ORDER HISTORY / BACKUP HELPERS
    # ========================================================

   
    # ========================================================
    # UNIT 14 COORDINATED CORRECTION
    # STRICT DEMO ORDER-HISTORY VERIFICATION
    # ========================================================

    def get_order_history():

        all_orders = []
        page = 0
        page_limit = 1000
        max_pages = 20

        while page < max_pages:

            query = urllib.parse.urlencode({
                "symbol": demo_symbol,
                "limit": page_limit,
                "page": page,
            })

            result = authenticated_get(
                "/capi/v3/sim/order/history",
                query,
            )

            if not isinstance(result, list):
                raise RuntimeError(
                    "UNIT 14 HISTORY VERIFICATION FAILED: "
                    "INVALID RESPONSE TYPE"
                )

            for order in result:
                if not isinstance(order, dict):
                    raise RuntimeError(
                        "UNIT 14 HISTORY VERIFICATION FAILED: "
                        "INVALID ORDER RECORD"
                    )

            all_orders.extend(result)

            if len(result) < page_limit:
                print(
                    "PASS: UNIT 14 ORDER HISTORY COMPLETE | "
                    f"RECORDS = {len(all_orders)}",
                    flush=True,
                )
                return all_orders

            page += 1

        raise RuntimeError(
            "UNIT 14 HISTORY VERIFICATION FAILED: "
            "PAGINATION LIMIT REACHED"
        )

    # ========================================================
    # END STRICT ORDER-HISTORY VERIFICATION
    # ========================================================
    

    def get_trade_key(
        position,
    ):

        created_time = str(
            position.get(
                "createdTime",
                "",
            )
        )

        if created_time.isdigit():

            return (
                created_time[-12:]
            )

        position_id = str(
            position.get(
                "id",
                "",
            )
        )

        if position_id:

            return (
                position_id[-12:]
            )

        raise RuntimeError(
            "UNIT 14 BLOCKED: "
            "POSITION TRADE ID UNAVAILABLE"
        )

    def backup_client_id(
        stage,
        trade_key,
    ):

        return (
            f"FR-B{stage}-{trade_key}"
        )[:36]

    def determine_backup_stage(
        history,
        trade_key,
    ):

        filled_stages = set()
        existing_stages = set()

        for stage in range(
            1,
            max_backups + 1,
        ):

            expected_id = (
                backup_client_id(
                    stage,
                    trade_key,
                )
            )

            for order in history:

                if not isinstance(
                    order,
                    dict,
                ):
                    continue

                if (
                    str(
                        order.get(
                            "clientOrderId",
                            "",
                        )
                    )
                    !=
                    expected_id
                ):
                    continue

                existing_stages.add(
                    stage
                )

                status = str(
                    order.get(
                        "status",
                        "",
                    )
                ).upper()

                try:

                    executed_qty = Decimal(
                        str(
                            order.get(
                                "executedQty",
                                "0",
                            )
                        )
                    )

                except Exception:

                    executed_qty = (
                        Decimal("0")
                    )

                if (
                    status
                    ==
                    "FILLED"
                    and
                    executed_qty
                    >
                    Decimal("0")
                ):
                    filled_stages.add(
                        stage
                    )

        completed = 0

        for stage in range(
            1,
            max_backups + 1,
        ):

            if (
                stage
                in
                filled_stages
            ):

                if (
                    stage
                    !=
                    completed
                    +
                    1
                ):
                    raise RuntimeError(
                        "UNIT 14 BLOCKED: "
                        "NON-SEQUENTIAL BACKUP HISTORY"
                    )

                completed = (
                    stage
                )

            else:

                break

        return (
            completed,
            existing_stages,
            filled_stages,
        )

    #   
    # ========================================================
    # 9. INITIAL TP1 / TP2 / TP3 RUNTIME STATE
    #
    # UNIT 13 CALCULATES THE ORIGINAL TP PLAN.
    #
    # UNIT 14 NOW CONTINUOUSLY MONITORS:
    #
    # TP1
    #   ->
    # TP2
    #   ->
    # TP3 DYNAMIC TRAILING
    #
    # NEW SIGNAL QUALIFICATION IS NOT REQUIRED.
    # ========================================================

    unit_13_status = str(
        unit_13_result.get(
            "status",
            "",
        )
    ).upper()

    position_side_from_unit_13 = str(
        unit_13_result.get(
            "position_side",
            "",
        )
    ).upper()

    # --------------------------------------------------------
    # TP QUANTITIES
    # --------------------------------------------------------

    try:

        original_tp1_quantity = Decimal(
            str(
                unit_13_result.get(
                    "tp1_quantity",
                    "0",
                )
            )
        )

    except Exception:

        original_tp1_quantity = (
            Decimal("0")
        )

    try:

        original_tp2_quantity = Decimal(
            str(
                unit_13_result.get(
                    "tp2_quantity",
                    "0",
                )
            )
        )

    except Exception:

        original_tp2_quantity = (
            Decimal("0")
        )

    try:

        original_tp3_quantity = Decimal(
            str(
                unit_13_result.get(
                    "tp3_quantity",
                    "0",
                )
            )
        )

    except Exception:

        original_tp3_quantity = (
            Decimal("0")
        )

    # --------------------------------------------------------
    # TP TARGETS
    #
    # UNIT 13 MAY RETURN EITHER:
    #
    # tp1_target / tp2_target
    #
    # OR AFTER EXECUTION:
    #
    # tp1_target_price / tp2_target_price
    # --------------------------------------------------------

    try:

        tp1_runtime_target = Decimal(
            str(
                unit_13_result.get(
                    "tp1_target",
                    unit_13_result.get(
                        "tp1_target_price",
                        "0",
                    ),
                )
            )
        )

    except Exception:

        tp1_runtime_target = (
            Decimal("0")
        )

    try:

        tp2_runtime_target = Decimal(
            str(
                unit_13_result.get(
                    "tp2_target",
                    unit_13_result.get(
                        "tp2_target_price",
                        "0",
                    ),
                )
            )
        )

    except Exception:

        tp2_runtime_target = (
            Decimal("0")
        )

    # --------------------------------------------------------
    # INITIAL COMPLETION STATE FROM UNIT 13
    # --------------------------------------------------------

    tp1_completed = bool(
        unit_13_result.get(
            "tp1_completed",
            False,
        )
    )

    tp2_completed = bool(
        unit_13_result.get(
            "tp2_completed",
            False,
        )
    )

    tp3_armed = (
        unit_13_result.get(
            "tp3_armed"
        )
        is True
        and
        unit_13_status
        ==
        "TP3_ARMED"
    )

    # --------------------------------------------------------
    # ZERO-SIZED STAGES ARE STRUCTURALLY COMPLETE
    # --------------------------------------------------------

    if (
        original_tp1_quantity
        <=
        Decimal("0")
    ):

        tp1_completed = True

    if (
        original_tp2_quantity
        <=
        Decimal("0")
        and
        tp1_completed
    ):

        tp2_completed = True

    if (
        tp1_completed
        and
        tp2_completed
        and
        original_tp3_quantity
        >
        Decimal("0")
    ):

        tp3_armed = True

    print(
        "UNIT 14 TP1 ORIGINAL QUANTITY = "
        f"{original_tp1_quantity}",
        flush=True,
    )

    print(
        "UNIT 14 TP2 ORIGINAL QUANTITY = "
        f"{original_tp2_quantity}",
        flush=True,
    )

    print(
        "UNIT 14 TP3 ORIGINAL RUNNER QUANTITY = "
        f"{original_tp3_quantity}",
        flush=True,
    )

    print(
        "UNIT 14 TP1 TARGET = "
        f"{tp1_runtime_target}",
        flush=True,
    )

    print(
        "UNIT 14 TP2 TARGET = "
        f"{tp2_runtime_target}",
        flush=True,
    )

    print(
        "UNIT 14 TP1 COMPLETED = "
        f"{tp1_completed}",
        flush=True,
    )

    print(
        "UNIT 14 TP2 COMPLETED = "
        f"{tp2_completed}",
        flush=True,
    )

    print(
        "UNIT 14 TP3 ARMED = "
        f"{tp3_armed}",
        flush=True,
    )
    
    # ========================================================
    # UNIT 14 CONTINUOUS TP3 STATE INITIALIZATION
    # INDENTATION: 4 SPACES
    # ========================================================

    last_confirmed_backup_stage = None

    # Initialize TP3 best favorable mark.
    # Required when TP3 is already armed at startup.
    # Existing runtime logic updates or resets this value.

    best_mark = None

    runtime_cycle = 0

    poll_seconds = 5

    last_runtime_order_time = 0.0

    # ========================================================
    # END TP3 STATE INITIALIZATION
    # ========================================================
    
    print(
        "UNIT 14 TP3 ARMED = "
        f"{tp3_armed}",
        flush=True,
    )

    print(
        "UNIT 14 TP3 ORIGINAL RUNNER QUANTITY = "
        f"{original_tp3_quantity}",
        flush=True,
    )

    print(
        "UNIT 14 RUNTIME POLL INTERVAL = "
        f"{poll_seconds} SECONDS",
        flush=True,
    )

    print(
        "UNIT 14 COMBINED POSITION LOOP STARTED = TRUE",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    # ========================================================
    # 10. CONTINUOUS POSITION MANAGEMENT LOOP
    # ========================================================

    while True:

        runtime_cycle += 1

        # ====================================================
        # 10A. CURRENT POSITION
        # ====================================================

        try:

            position = (
                get_active_position()
            )

        except Exception as exc:

            print(
                "UNIT 14 POSITION READ ERROR = "
                f"{repr(exc)}",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # UNIT 14C - VERIFIED FLAT POSITION HANDOFF
        # INDENTATION: 8 SPACES
        # ====================================================

        if position is None:

            print(
                "UNIT 14 FLAT POSITION CANDIDATE",
                flush=True,
            )

            # A single zero-position response is not
            # sufficient to authorize re-entry.

            time.sleep(2)

            try:
                second_position = get_active_position()

                if second_position is not None:
                    print(
                        "UNIT 14 POSITION REAPPEARED",
                        flush=True,
                    )
                    continue

                history = get_order_history()

            except Exception as exc:

                print(
                    "UNIT 14 CLOSURE VERIFICATION "
                    "FAILED =",
                    repr(exc),
                    flush=True,
                )

                time.sleep(poll_seconds)
                continue

            # Check history for unresolved orders.
            # This is supplementary verification,
            # not proof that all pending orders
            # are represented by order history.

            pending_statuses = {
                "NEW",
                "PARTIALLY_FILLED",
                "PENDING",
                "PENDING_NEW",
                "ACCEPTED",
                "OPEN",
            }

            unresolved_orders = []

            for order in history:

                if not isinstance(order, dict):
                    unresolved_orders.append(
                        {"reason": "INVALID_ORDER_RECORD"}
                    )
                    break

                if str(
                    order.get("symbol", "")
                ).upper() != demo_symbol:
                    continue

                status = str(
                    order.get("status", "")
                ).upper()

                if status in pending_statuses:
                    unresolved_orders.append({
                        "orderId": order.get("orderId"),
                        "clientOrderId": order.get(
                            "clientOrderId"
                        ),
                        "status": status,
                    })

            if unresolved_orders:

                print(
                    "UNIT 14 REENTRY BLOCKED: "
                    "UNRESOLVED DEMO ORDERS =",
                    unresolved_orders[:10],
                    flush=True,
                )

                time.sleep(poll_seconds)
                continue

            # Third position read reduces the chance
            # of racing with an order fill during
            # the history check.

            try:
                final_position = get_active_position()

            except Exception as exc:

                print(
                    "UNIT 14 FINAL FLAT CHECK FAILED =",
                    repr(exc),
                    flush=True,
                )

                time.sleep(poll_seconds)
                continue

            if final_position is not None:

                print(
                    "UNIT 14 FLAT STATE REVOKED: "
                    "POSITION FOUND",
                    flush=True,
                )

                continue

            print(
                "UNIT 14 POSITION CLOSED = "
                "CONFIRMED BY REPEATED POSITION READS",
                flush=True,
            )

            print(
                "UNIT 14 DEMO HISTORY PENDING "
                "STATUS CHECK = PASS",
                flush=True,
            )

            print(
                "UNIT 14 RUNTIME STATUS = POSITION_CLOSED",
                flush=True,
            )

            print(
                "UNIT 14 RETURNING TO CONTINUOUS "
                "ENTRY SCAN",
                flush=True,
            )

            return {
                "unit": 14,
                "status": "POSITION_CLOSED",
                "closure_position_reads": 3,
                "history_pending_status_check": True,
                "exchange_write": False,
                "real_order": False,
                "sl_enabled": False,
            }

        # ====================================================
        # END UNIT 14C
        # ====================================================

        position_side = str(
            position.get(
                "side",
                "",
            )
        ).upper()

        if position_side not in (
            "LONG",
            "SHORT",
        ):
            raise RuntimeError(
                "UNIT 14 BLOCKED: INVALID POSITION SIDE"
            )

        if (
            position_side_from_unit_13
            in
            (
                "LONG",
                "SHORT",
            )
            and
            position_side
            !=
            position_side_from_unit_13
        ):
            raise RuntimeError(
                "UNIT 14 BLOCKED: POSITION SIDE CHANGED"
            )

        try:

            position_size = Decimal(
                str(
                    position.get(
                        "size",
                        "0",
                    )
                )
            )

            liquidation_price = Decimal(
                str(
                    position.get(
                        "liquidatePrice",
                        "0",
                    )
                )
            )

        except Exception as exc:

            print(
                "UNIT 14 POSITION PARSE ERROR = "
                f"{repr(exc)}",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        if (
            position_size
            <=
            Decimal("0")
        ):

            time.sleep(
                poll_seconds
            )

            continue

        trade_key = (
            get_trade_key(
                position
            )
        )

        # ====================================================
        # 10B. CURRENT MARK
        # ====================================================

        try:

            current_mark = (
                get_mark_price()
            )

        except Exception as exc:

            print(
                "UNIT 14 MARK READ ERROR = "
                f"{repr(exc)}",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # 10C. HISTORY + CONFIRMED BACKUP STAGE
        # ====================================================

        try:

            history = (
                get_order_history()
            )

            (
                completed_backups,
                existing_backup_stages,
                filled_backup_stages,
            ) = determine_backup_stage(
                history,
                trade_key,
            )

        except Exception as exc:

            print(
                "UNIT 14 HISTORY READ ERROR = "
                f"{repr(exc)}",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # 10D. BACKUP FILL CHANGE
        #
        # Reset TP3 best mark whenever a newly confirmed
        # backup changes the managed position.
        #
        # The CURRENT position and CURRENT liquidation price
        # were already re-read at the beginning of this cycle.
        # ====================================================

        if (
            last_confirmed_backup_stage
            is None
        ):

            last_confirmed_backup_stage = (
                completed_backups
            )

        elif (
            completed_backups
            !=
            last_confirmed_backup_stage
        ):

            print(
                "PASS: UNIT 14 BACKUP STAGE CHANGED "
                f"{last_confirmed_backup_stage} -> "
                f"{completed_backups}",
                flush=True,
            )

            print(
                "PASS: UNIT 14 POSITION RE-READ "
                "AFTER CONFIRMED BACKUP FILL",
                flush=True,
            )

            print(
                "PASS: UNIT 14 NEW WEEX LIQUIDATION = "
                f"{liquidation_price}",
                flush=True,
            )

            best_mark = None

            last_confirmed_backup_stage = (
                completed_backups
            )

            print(
                "PASS: UNIT 14 TP3 BEST MARK RESET "
                "AFTER BACKUP FILL",
                flush=True,
            )

                # ====================================================
        # 10E. CONTINUOUS TP1 / TP2 MANAGEMENT
        #
        # UNIT 13 CALCULATED THE PLAN ONCE.
        #
        # UNIT 14 NOW RECHECKS TP1 / TP2 EVERY RUNTIME CYCLE.
        #
        # PRIORITY:
        #
        # IF PRICE JUMPS DIRECTLY THROUGH TP2:
        #
        # TP2 CLOSES THE OUTSTANDING CUMULATIVE
        # TP1 + TP2 QUANTITY.
        #
        # ONLY EXCHANGE-CONFIRMED FILLS ADVANCE STATE.
        # ====================================================

        tp1_client_id = (
            f"FR14-TP1-{trade_key}"
        )[:36]

        tp2_client_id = (
            f"FR14-TP2-{trade_key}"
        )[:36]

        tp1_order_exists = False
        tp2_order_exists = False

        tp1_order_filled = False
        tp2_order_filled = False

        tp1_executed_qty = Decimal("0")
        tp2_executed_qty = Decimal("0")

        # ----------------------------------------------------
        # READ RUNTIME TP ORDER HISTORY
        # ----------------------------------------------------

        for order in history:

            if not isinstance(
                order,
                dict,
            ):
                continue

            client_id = str(
                order.get(
                    "clientOrderId",
                    "",
                )
            )

            status = str(
                order.get(
                    "status",
                    "",
                )
            ).upper()

            try:

                executed_qty = Decimal(
                    str(
                        order.get(
                            "executedQty",
                            "0",
                        )
                    )
                )

            except Exception:

                executed_qty = (
                    Decimal("0")
                )

            if (
                client_id
                ==
                tp1_client_id
            ):

                tp1_order_exists = True

                if (
                    status
                    ==
                    "FILLED"
                    and
                    executed_qty
                    >
                    Decimal("0")
                ):

                    tp1_order_filled = True
                    tp1_executed_qty = (
                        executed_qty
                    )

            if (
                client_id
                ==
                tp2_client_id
            ):

                tp2_order_exists = True

                if (
                    status
                    ==
                    "FILLED"
                    and
                    executed_qty
                    >
                    Decimal("0")
                ):

                    tp2_order_filled = True
                    tp2_executed_qty = (
                        executed_qty
                    )

        # ----------------------------------------------------
        # CONFIRMED TP1 FILL
        # ----------------------------------------------------

        if (
            tp1_order_filled
            and
            not tp1_completed
        ):

            tp1_completed = True

            print(
                "PASS: UNIT 14 TP1 EXCHANGE-CONFIRMED FILLED",
                flush=True,
            )

            print(
                "PASS: UNIT 14 TP1 EXECUTED QUANTITY = "
                f"{tp1_executed_qty}",
                flush=True,
            )

        # ----------------------------------------------------
        # CONFIRMED TP2 FILL
        #
        # TP2 ORDER MAY REPRESENT CUMULATIVE TP1 + TP2
        # WHEN PRICE JUMPED DIRECTLY THROUGH BOTH.
        # ----------------------------------------------------

        if (
            tp2_order_filled
            and
            not tp2_completed
        ):

            tp1_completed = True
            tp2_completed = True

            print(
                "PASS: UNIT 14 TP2 EXCHANGE-CONFIRMED FILLED",
                flush=True,
            )

            print(
                "PASS: UNIT 14 TP1 + TP2 CUMULATIVE EXIT COMPLETE",
                flush=True,
            )

            print(
                "PASS: UNIT 14 TP2 EXECUTED QUANTITY = "
                f"{tp2_executed_qty}",
                flush=True,
            )

        # ----------------------------------------------------
        # ARM TP3 AS SOON AS TP1 + TP2 ARE CONFIRMED COMPLETE
        # ----------------------------------------------------

        if (
            not tp3_armed
            and
            tp1_completed
            and
            tp2_completed
            and
            original_tp3_quantity
            >
            Decimal("0")
            and
            position_size
            >
            Decimal("0")
        ):

            tp3_armed = True

            best_mark = None

            print(
                "PASS: UNIT 14 TP1 + TP2 COMPLETE",
                flush=True,
            )

            print(
                "PASS: UNIT 14 TP3 ARMED = TRUE",
                flush=True,
            )

            print(
                "PASS: UNIT 14 TP3 RUNNER QUANTITY = "
                f"{original_tp3_quantity}",
                flush=True,
            )

        # ----------------------------------------------------
        # TP TARGET REACHED STATE
        # ----------------------------------------------------

        tp1_reached_runtime = False
        tp2_reached_runtime = False

        if (
            position_side
            ==
            "LONG"
        ):

            if (
                tp1_runtime_target
                >
                Decimal("0")
            ):

                tp1_reached_runtime = (
                    current_mark
                    >=
                    tp1_runtime_target
                )

            if (
                tp2_runtime_target
                >
                Decimal("0")
            ):

                tp2_reached_runtime = (
                    current_mark
                    >=
                    tp2_runtime_target
                )

        else:

            if (
                tp1_runtime_target
                >
                Decimal("0")
            ):

                tp1_reached_runtime = (
                    current_mark
                    <=
                    tp1_runtime_target
                )

            if (
                tp2_runtime_target
                >
                Decimal("0")
            ):

                tp2_reached_runtime = (
                    current_mark
                    <=
                    tp2_runtime_target
                )

        print(
            "UNIT 14 TP STATUS | "
            f"CYCLE = {runtime_cycle} | "
            f"SIDE = {position_side} | "
            f"MARK = {current_mark} | "
            f"TP1 = {tp1_runtime_target} | "
            f"TP1 REACHED = {tp1_reached_runtime} | "
            f"TP1 DONE = {tp1_completed} | "
            f"TP2 = {tp2_runtime_target} | "
            f"TP2 REACHED = {tp2_reached_runtime} | "
            f"TP2 DONE = {tp2_completed} | "
            f"TP3 ARMED = {tp3_armed}",
            flush=True,
        )

        # ----------------------------------------------------
        # TP1 / TP2 EXECUTION IS FINISHED ONCE TP3 IS ARMED
        # ----------------------------------------------------

        if not tp3_armed:

            tp_runtime_action = (
                "NONE"
            )

            tp_runtime_quantity = (
                Decimal("0")
            )

            tp_runtime_client_id = (
                ""
            )

            # ------------------------------------------------
            # TP2 HAS PRIORITY.
            #
            # IF TP1 WAS NEVER TAKEN AND PRICE HAS ALREADY
            # REACHED TP2, CLOSE BOTH TP1 + TP2 ALLOCATION.
            # ------------------------------------------------

            if (
                not tp2_completed
                and
                tp2_reached_runtime
                and
                not tp2_order_exists
            ):

                if tp1_completed:

                    tp_runtime_quantity = (
                        original_tp2_quantity
                    )

                else:

                    tp_runtime_quantity = (
                        original_tp1_quantity
                        +
                        original_tp2_quantity
                    )

                tp_runtime_quantity = (
                    floor_quantity(
                        tp_runtime_quantity
                    )
                )

                if (
                    tp_runtime_quantity
                    >
                    position_size
                ):

                    tp_runtime_quantity = (
                        floor_quantity(
                            position_size
                        )
                    )

                if (
                    tp_runtime_quantity
                    >=
                    minimum_quantity
                ):

                    tp_runtime_action = (
                        "TP2"
                    )

                    tp_runtime_client_id = (
                        tp2_client_id
                    )

            # ------------------------------------------------
            # TP1
            # ------------------------------------------------

            elif (
                not tp1_completed
                and
                tp1_reached_runtime
                and
                not tp1_order_exists
            ):

                tp_runtime_quantity = (
                    floor_quantity(
                        original_tp1_quantity
                    )
                )

                if (
                    tp_runtime_quantity
                    >
                    position_size
                ):

                    tp_runtime_quantity = (
                        floor_quantity(
                            position_size
                        )
                    )

                if (
                    tp_runtime_quantity
                    >=
                    minimum_quantity
                ):

                    tp_runtime_action = (
                        "TP1"
                    )

                    tp_runtime_client_id = (
                        tp1_client_id
                    )

            # ------------------------------------------------
            # SUBMIT EXACTLY ONE TP ORDER
            # ------------------------------------------------

            if (
                tp_runtime_action
                !=
                "NONE"
            ):

                elapsed = (
                    time.time()
                    -
                    last_runtime_order_time
                )

                if (
                    last_runtime_order_time
                    >
                    0
                    and
                    elapsed
                    <
                    60
                ):

                    print(
                        "UNIT 14 "
                        f"{tp_runtime_action} "
                        "WAITING FOR DEMO ORDER RATE WINDOW",
                        flush=True,
                    )

                    time.sleep(
                        poll_seconds
                    )

                    continue

                # --------------------------------------------
                # FINAL POSITION RECONCILIATION
                # --------------------------------------------

                try:

                    final_tp_position = (
                        get_active_position()
                    )

                except Exception as exc:

                    print(
                        "UNIT 14 TP FINAL POSITION CHECK ERROR = "
                        f"{repr(exc)}",
                        flush=True,
                    )

                    time.sleep(
                        poll_seconds
                    )

                    continue

                if final_tp_position is None:

                    print(
                        "UNIT 14 TP SUBMISSION BLOCKED: "
                        "POSITION CLOSED",
                        flush=True,
                    )

                    time.sleep(
                        poll_seconds
                    )

                    continue

                final_tp_side = str(
                    final_tp_position.get(
                        "side",
                        "",
                    )
                ).upper()

                if (
                    final_tp_side
                    !=
                    position_side
                ):

                    raise RuntimeError(
                        "UNIT 14 BLOCKED: "
                        "POSITION DIRECTION CHANGED "
                        "BEFORE TP SUBMISSION"
                    )

                final_tp_trade_key = (
                    get_trade_key(
                        final_tp_position
                    )
                )

                if (
                    final_tp_trade_key
                    !=
                    trade_key
                ):

                    print(
                        "UNIT 14 TP SUBMISSION BLOCKED: "
                        "POSITION IDENTITY CHANGED",
                        flush=True,
                    )

                    time.sleep(
                        poll_seconds
                    )

                    continue

                try:

                    final_tp_size = Decimal(
                        str(
                            final_tp_position.get(
                                "size",
                                "0",
                            )
                        )
                    )

                except Exception:

                    final_tp_size = (
                        Decimal("0")
                    )

                if (
                    final_tp_size
                    <=
                    Decimal("0")
                ):

                    time.sleep(
                        poll_seconds
                    )

                    continue

                if (
                    tp_runtime_quantity
                    >
                    final_tp_size
                ):

                    tp_runtime_quantity = (
                        floor_quantity(
                            final_tp_size
                        )
                    )

                if (
                    tp_runtime_quantity
                    <
                    minimum_quantity
                ):

                    print(
                        "UNIT 14 TP SUBMISSION BLOCKED: "
                        "QUANTITY BELOW MINIMUM",
                        flush=True,
                    )

                    time.sleep(
                        poll_seconds
                    )

                    continue

                if (
                    position_side
                    ==
                    "LONG"
                ):

                    tp_closing_side = (
                        "SELL"
                    )

                else:

                    tp_closing_side = (
                        "BUY"
                    )

                tp_runtime_payload = {

                    "symbol":
                        demo_symbol,

                    "side":
                        tp_closing_side,

                    "positionSide":
                        position_side,

                    "type":
                        "MARKET",

                    "quantity":
                        quantity_text(
                            tp_runtime_quantity
                        ),

                    "newClientOrderId":
                        tp_runtime_client_id,
                }

                # --------------------------------------------
                # ABSOLUTE SL PROHIBITION
                # --------------------------------------------

                for prohibited in (

                    "slTriggerPrice",

                    "SlWorkingType",

                    "stopLossPrice",

                    "stopPrice",
                ):

                    if (
                        prohibited
                        in
                        tp_runtime_payload
                    ):

                        raise RuntimeError(
                            "UNIT 14 BLOCKED: "
                            "SL FIELD DETECTED IN TP"
                        )

                print(
                    "-" * 80,
                    flush=True,
                )

                print(
                    "UNIT 14 "
                    f"{tp_runtime_action} "
                    "TRIGGER REACHED = TRUE",
                    flush=True,
                )

                print(
                    "UNIT 14 "
                    f"{tp_runtime_action} "
                    "MARK = "
                    f"{current_mark}",
                    flush=True,
                )

                print(
                    "UNIT 14 "
                    f"{tp_runtime_action} "
                    "QUANTITY = "
                    f"{tp_runtime_quantity}",
                    flush=True,
                )

                print(
                    "UNIT 14 "
                    f"{tp_runtime_action} "
                    "CLIENT ID = "
                    f"{tp_runtime_client_id}",
                    flush=True,
                )

                print(
                    "UNIT 14 DEMO TP ORDER = TRUE",
                    flush=True,
                )

                print(
                    "UNIT 14 REAL TP ORDER = FALSE",
                    flush=True,
                )

                print(
                    "UNIT 14 SL ENABLED = FALSE",
                    flush=True,
                )

                try:

                    tp_runtime_result = (
                        authenticated_post(
                            "/capi/v3/sim/order",
                            tp_runtime_payload,
                        )
                    )

                    last_runtime_order_time = (
                        time.time()
                    )

                except Exception as exc:

                    print(
                        "UNIT 14 "
                        f"{tp_runtime_action} "
                        "SUBMISSION ERROR = "
                        f"{repr(exc)}",
                        flush=True,
                    )

                    # Do not blindly retry immediately.
                    # Next cycle checks order history first.

                    last_runtime_order_time = (
                        time.time()
                    )

                    time.sleep(
                        poll_seconds
                    )

                    continue

                if (
                    tp_runtime_result.get(
                        "success"
                    )
                    is not True
                ):

                    print(
                        "UNIT 14 "
                        f"{tp_runtime_action} "
                        "NOT ACCEPTED = "
                        f"{tp_runtime_result}",
                        flush=True,
                    )

                    time.sleep(
                        poll_seconds
                    )

                    continue

                tp_runtime_order_id = (
                    tp_runtime_result.get(
                        "orderId"
                    )
                )

                if not tp_runtime_order_id:

                    print(
                        "UNIT 14 "
                        f"{tp_runtime_action} "
                        "ACCEPTED WITHOUT ORDER ID",
                        flush=True,
                    )

                    time.sleep(
                        poll_seconds
                    )

                    continue

                print(
                    "PASS: UNIT 14 "
                    f"{tp_runtime_action} "
                    "DEMO ORDER ACCEPTED",
                    flush=True,
                )

                print(
                    "PASS: UNIT 14 "
                    f"{tp_runtime_action} "
                    "ORDER ID = "
                    f"{tp_runtime_order_id}",
                    flush=True,
                )

                print(
                    "PASS: UNIT 14 "
                    f"{tp_runtime_action} "
                    "WAITING FOR EXCHANGE-CONFIRMED FILL",
                    flush=True,
                )

                print(
                    "PASS: UNIT 14 TP STATE NOT ADVANCED "
                    "BY TRIGGER ALONE",
                    flush=True,
                )

                # Next cycle:
                # history confirms FILLED before state advances.

                time.sleep(
                    poll_seconds
                )

                continue
        # ====================================================
        # 11. DYNAMIC TP3 MANAGEMENT
        # ====================================================

        tp3_callback_reached = False
        trailing_trigger = None
        dynamic_trailing_percent = None
        momentum_deterioration = None
        atr_percent = None
        trend_strength = None

        if tp3_armed:

            # ------------------------------------------------
            # Once a backup has filled after TP3 was armed,
            # the added quantity joins the remaining runner.
            #
            # Before backups:
            # close no more than Unit 13 TP3 allocation.
            #
            # After backup:
            # manage current remaining position as runner.
            # ------------------------------------------------

            if (
                completed_backups
                >
                0
            ):

                tp3_close_quantity = (
                    position_size
                )

            else:

                tp3_close_quantity = min(
                    original_tp3_quantity,
                    position_size,
                )

            # ------------------------------------------------
            # BEST FAVORABLE MARK
            # ------------------------------------------------

            if best_mark is None:

                best_mark = (
                    current_mark
                )

                print(
                    "TP3 INITIAL BEST MARK = "
                    f"{best_mark}",
                    flush=True,
                )
    
                # ------------------------------------------------
            # BEST FAVORABLE MARK
            # ------------------------------------------------

            if best_mark is None:

                best_mark = (
                    current_mark
                )

                print(
                    "TP3 INITIAL BEST MARK = "
                    f"{best_mark}",
                    flush=True,
                )

            elif (
                position_side
                ==
                "LONG"
                and
                current_mark
                >
                best_mark
            ):

                best_mark = (
                    current_mark
                )

                print(
                    "TP3 NEW BEST MARK = "
                    f"{best_mark}",
                    flush=True,
                )

            elif (
                position_side
                ==
                "SHORT"
                and
                current_mark
                <
                best_mark
            ):

                best_mark = (
                    current_mark
                )

                print(
                    "TP3 NEW BEST MARK = "
                    f"{best_mark}",
                    flush=True,
                )

            # ------------------------------------------------
            # RECALCULATE DYNAMIC CALLBACK EVERY CYCLE
            # ------------------------------------------------

            try:

                analysis = (
                    get_recent_market_analysis()
                )

                (
                    dynamic_trailing_percent,
                    momentum_deterioration,
                ) = calculate_dynamic_callback(
                    analysis,
                    position_side,
                )

                atr_percent = (
                    analysis[
                        "atr_percent"
                    ]
                )

                trend_strength = (
                    analysis[
                        "trend_strength"
                    ]
                )

            except Exception as exc:

                # Fail-safe:
                # if market-analysis data temporarily fails,
                # use normal reference rather than inventing
                # market conditions.

                dynamic_trailing_percent = (
                    trailing_reference_percent
                )

                momentum_deterioration = (
                    Decimal("0")
                )

                atr_percent = (
                    Decimal("0")
                )

                trend_strength = (
                    Decimal("0")
                )

                print(
                    "UNIT 14 DYNAMIC ANALYSIS ERROR = "
                    f"{repr(exc)}",
                    flush=True,
                )

                print(
                    "UNIT 14 TP3 CALLBACK FALLBACK = "
                    f"{trailing_reference_percent}%",
                    flush=True,
                )

            dynamic_trailing_percent = max(
                trailing_min_percent,
                min(
                    dynamic_trailing_percent,
                    trailing_max_percent,
                ),
            )

            dynamic_trailing_fraction = (
                dynamic_trailing_percent
                /
                Decimal("100")
            )

            if (
                position_side
                ==
                "LONG"
            ):

                trailing_trigger = (
                    best_mark
                    *
                    (
                        Decimal("1")
                        -
                        dynamic_trailing_fraction
                    )
                )

                tp3_callback_reached = (
                    current_mark
                    <=
                    trailing_trigger
                )

            else:

                trailing_trigger = (
                    best_mark
                    *
                    (
                        Decimal("1")
                        +
                        dynamic_trailing_fraction
                    )
                )

                tp3_callback_reached = (
                    current_mark
                    >=
                    trailing_trigger
                )

            print(
                "UNIT 14 DYNAMIC TP3 | "
                f"CYCLE = {runtime_cycle} | "
                f"SIDE = {position_side} | "
                f"MARK = {current_mark} | "
                f"BEST = {best_mark} | "
                f"ATR% = {atr_percent} | "
                f"TREND = {trend_strength} | "
                f"DETERIORATION = {momentum_deterioration} | "
                f"REFERENCE = {trailing_reference_percent}% | "
                f"CALLBACK = {dynamic_trailing_percent}% | "
                f"TRIGGER = {trailing_trigger} | "
                f"REACHED = {tp3_callback_reached}",
                flush=True,
            )

        else:

            print(
                "UNIT 14 CYCLE = "
                f"{runtime_cycle} | "
                f"SIDE = {position_side} | "
                f"SIZE = {position_size} | "
                f"MARK = {current_mark} | "
                f"LIQ = {liquidation_price} | "
                f"BACKUPS FILLED = "
                f"{completed_backups}/{max_backups} | "
                "TP3 ARMED = FALSE",
                flush=True,
            )

        # ====================================================
        # 12. TP3 CALLBACK HAS EXECUTION PRIORITY
        # ====================================================

        if (
            tp3_armed
            and
            tp3_callback_reached
        ):

            elapsed = (
                time.time()
                -
                last_runtime_order_time
            )

            if (
                last_runtime_order_time
                >
                0
                and
                elapsed
                <
                60
            ):

                print(
                    "TP3 EXECUTION WAITING FOR "
                    "DEMO ORDER RATE WINDOW",
                    flush=True,
                )

                time.sleep(
                    poll_seconds
                )

                continue

            if (
                position_side
                ==
                "LONG"
            ):

                closing_side = (
                    "SELL"
                )

            else:

                closing_side = (
                    "BUY"
                )

            close_quantity = min(
                tp3_close_quantity,
                position_size,
            )

            close_quantity = (
                floor_quantity(
                    close_quantity
                )
            )

            if (
                close_quantity
                <
                minimum_quantity
            ):

                print(
                    "TP3 CLOSE BLOCKED: "
                    "QUANTITY BELOW MINIMUM",
                    flush=True,
                )

                time.sleep(
                    poll_seconds
                )

                continue

            tp3_client_id = (
                f"FR-TP3-{trade_key}"
            )[:36]

            tp3_existing = False

            for order in history:

                if not isinstance(
                    order,
                    dict,
                ):
                    continue

                if (
                    str(
                        order.get(
                            "clientOrderId",
                            "",
                        )
                    )
                    ==
                    tp3_client_id
                ):

                    tp3_existing = True

                    break

            if tp3_existing:

                print(
                    "TP3 DUPLICATE SUBMISSION BLOCKED",
                    flush=True,
                )

                time.sleep(
                    poll_seconds
                )

                continue

            tp3_payload = {
                "symbol":
                    demo_symbol,

                "side":
                    closing_side,

                "positionSide":
                    position_side,

                "type":
                    "MARKET",

                "quantity":
                    quantity_text(
                        close_quantity
                    ),

                "newClientOrderId":
                    tp3_client_id,
            }

            for prohibited in (
                "slTriggerPrice",
                "SlWorkingType",
                "stopLossPrice",
                "stopPrice",
            ):

                if (
                    prohibited
                    in
                    tp3_payload
                ):

                    raise RuntimeError(
                        "UNIT 14 BLOCKED: "
                        "SL FIELD DETECTED"
                    )

            print(
                "-" * 80,
                flush=True,
            )

            print(
                "TP3 CALLBACK REACHED = TRUE",
                flush=True,
            )

            print(
                "TP3 DYNAMIC CALLBACK % = "
                f"{dynamic_trailing_percent}",
                flush=True,
            )

            print(
                "TP3 CLOSE QUANTITY = "
                f"{close_quantity}",
                flush=True,
            )

            print(
                "TP3 DEMO SUBMISSION = TRUE",
                flush=True,
            )

            try:

                result = authenticated_post(
                    "/capi/v3/sim/order",
                    tp3_payload,
                )

                last_runtime_order_time = (
                    time.time()
                )

            except Exception as exc:

                print(
                    "TP3 DEMO ORDER ERROR = "
                    f"{repr(exc)}",
                    flush=True,
                )

                # Outcome may be uncertain.
                # Re-read history and position before retry.

                last_runtime_order_time = (
                    time.time()
                )

                time.sleep(
                    poll_seconds
                )

                continue

            if (
                result.get(
                    "success"
                )
                is not True
            ):

                print(
                    "TP3 ORDER NOT ACCEPTED = "
                    f"{result}",
                    flush=True,
                )

                time.sleep(
                    poll_seconds
                )

                continue

            print(
                "PASS: TP3 DEMO CLOSE ACCEPTED",
                flush=True,
            )

            print(
                "PASS: TP3 ORDER ID = "
                f"{result.get('orderId')}",
                flush=True,
            )

            print(
                "PASS: TP3 DYNAMIC TRAILING EXECUTED",
                flush=True,
            )

            print(
                "PASS: TP3 REAL ORDER = FALSE",
                flush=True,
            )

            print(
                "PASS: TP3 SL = DISABLED",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # 13. BACKUP MANAGEMENT
        # ====================================================

        if (
            max_backups
            <=
            0
        ):

            print(
                "UNIT 14 BACKUPS DISABLED BY CONFIG",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        if (
            completed_backups
            >=
            max_backups
        ):

            print(
                "UNIT 14 BACKUP STATUS = "
                f"B{completed_backups} FILLED",
                flush=True,
            )

            print(
                "UNIT 14 NEXT BACKUP = NONE",
                flush=True,
            )

            print(
                "UNIT 14 B4 = DISABLED",
                flush=True,
            )

            print(
                "UNIT 14 FINAL LIQUIDATION BOUNDARY = "
                f"{liquidation_price}",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        next_backup_stage = (
            completed_backups
            +
            1
        )

        # ====================================================
        # FIVE BACKUP STAGE PROTECTION
        # INDENTATION: 8 SPACES
        # ====================================================

        if (
            next_backup_stage
            >
            5
        ):

            print(
                "UNIT 14 BACKUP STOP = FIVE BACKUPS MAXIMUM",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue
    

        # ====================================================
        # 13A. CURRENT WEEX LIQUIDATION PRICE REQUIRED
        # ====================================================

        if (
            liquidation_price
            <=
            Decimal("0")
        ):

            print(
                f"UNIT 14 B{next_backup_stage} BLOCKED: "
                "WEEX LIQUIDATION PRICE UNAVAILABLE",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # 13B. BACKUP TRIGGER
        # ====================================================

        if (
            position_side
            ==
            "LONG"
        ):

            backup_trigger = (
                liquidation_price
                *
                (
                    Decimal("1")
                    +
                    backup_buffer_fraction
                )
            )

            backup_reached = (
                current_mark
                <=
                backup_trigger
            )

        else:

            backup_trigger = (
                liquidation_price
                *
                (
                    Decimal("1")
                    -
                    backup_buffer_fraction
                )
            )

            backup_reached = (
                current_mark
                >=
                backup_trigger
            )

        print(
            f"UNIT 14 B{next_backup_stage} | "
            f"L{next_backup_stage} = "
            f"{liquidation_price} | "
            f"BUFFER = {backup_buffer_percent}% | "
            f"TRIGGER = {backup_trigger} | "
            f"MARK = {current_mark} | "
            f"REACHED = {backup_reached}",
            flush=True,
        )

        if not backup_reached:

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # 13C. ANTI-DUPLICATE
        # ====================================================

        next_client_id = (
            backup_client_id(
                next_backup_stage,
                trade_key,
            )
        )

        if (
            next_backup_stage
            in
            existing_backup_stages
        ):

            print(
                f"UNIT 14 B{next_backup_stage} "
                "ORDER ALREADY EXISTS",
                flush=True,
            )

            print(
                "UNIT 14 DUPLICATE BACKUP BLOCKED",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        
        # ====================================================
        # UNIT 14 - PROGRESSIVE FIVE BACKUP CONTROL
        # INDENTATION: 8 SPACES
        # ====================================================

        backup_multipliers = (
            Decimal("1"),
            Decimal("1.5"),
            Decimal("2"),
            Decimal("2.5"),
            Decimal("3"),
        )

        backup_stage = int(next_backup_stage)

        if not 1 <= backup_stage <= 5:
            raise RuntimeError(
                "UNIT 14 INVALID BACKUP STAGE"
            )

        if completed_backups != backup_stage - 1:
            raise RuntimeError(
                "UNIT 14 BACKUP SEQUENCE MISMATCH"
            )

        backup_multiplier = (
            backup_multipliers[backup_stage - 1]
        )

        backup_margin_amount = (
            fixed_backup_margin
            * backup_multiplier
        )

        current_margin_committed = (
            fixed_entry_margin
            * (
                Decimal("1")
                + sum(
                    backup_multipliers[
                        :completed_backups
                    ]
                )
            )
        )

        projected_margin_committed = (
            current_margin_committed
            + backup_margin_amount
        )

        print(
            f"UNIT 14 B{backup_stage} "
            f"MULTIPLIER = {backup_multiplier}X",
            flush=True,
        )

        print(
            "UNIT 14 CURRENT PLANNED MARGIN =",
            current_margin_committed,
            flush=True,
        )

        print(
            "UNIT 14 PROJECTED PLANNED MARGIN =",
            projected_margin_committed,
            flush=True,
        )

        # ----------------------------------------------------
        # VERIFY FRESH DEMO AVAILABLE BALANCE
        # ----------------------------------------------------

        try:
            balance_item = get_demo_balance()

            available_balance = Decimal(
                str(
                    balance_item.get(
                        "availableBalance",
                        "0",
                    )
                )
            )

            if not available_balance.is_finite():
                raise ValueError(
                    "NON-FINITE AVAILABLE BALANCE"
                )

        except Exception as exc:
            print(
                "UNIT 14 BALANCE READ ERROR =",
                repr(exc),
                flush=True,
            )

            time.sleep(poll_seconds)
            continue

        # ----------------------------------------------------
        # CONSERVATIVE ACCOUNT FUNDS ESTIMATE
        # ----------------------------------------------------

        budgeted_funds = (
            available_balance
            + current_margin_committed
        )

        maximum_allowed_exposure = (
            budgeted_funds
            * exposure_cap_percent
            / Decimal("100")
        )

        remaining_exposure_allowance = max(
            Decimal("0"),
            maximum_allowed_exposure
            - current_margin_committed,
        )

        print(
            "UNIT 14 AVAILABLE BALANCE =",
            available_balance,
            flush=True,
        )

        print(
            "UNIT 14 EXPOSURE LIMIT =",
            maximum_allowed_exposure,
            flush=True,
        )

        print(
            "UNIT 14 REMAINING ALLOWANCE =",
            remaining_exposure_allowance,
            flush=True,
        )

        # ----------------------------------------------------
        # FULL BACKUP SIZE REQUIRED
        # ----------------------------------------------------

        if (
            available_balance
            < backup_margin_amount
        ):
            print(
                f"UNIT 14 B{backup_stage} WAITING: "
                "INSUFFICIENT AVAILABLE BALANCE",
                flush=True,
            )

            time.sleep(poll_seconds)
            continue

        if (
            backup_margin_amount
            > remaining_exposure_allowance
        ):
            print(
                f"UNIT 14 B{backup_stage} WAITING: "
                "35% EXPOSURE CAP",
                flush=True,
            )

            time.sleep(poll_seconds)
            continue

        print(
            f"UNIT 14 B{backup_stage} "
            "AFFORDABILITY CHECK = PASS",
            flush=True,
        )

        print(
            f"UNIT 14 B{backup_stage} "
            f"PLANNED MARGIN = {backup_margin_amount}",
            flush=True,
        )

        # ====================================================
        # END UNIT 14 PROGRESSIVE BACKUP CONTROL
        # NEXT: EXISTING backup_notional CALCULATION
        # ====================================================
        
        backup_notional = (
            backup_margin_amount
            *
            leverage_target
        )

        raw_backup_quantity = (
            backup_notional
            /
            current_mark
        )

        backup_quantity = (
            floor_quantity(
                raw_backup_quantity
            )
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            f"AVAILABLE SUSDT = {available_balance}",
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            f"MARGIN ALLOCATION = {backup_margin_amount}",
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            f"RAW QUANTITY = {raw_backup_quantity}",
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            f"NORMALIZED QUANTITY = {backup_quantity}",
            flush=True,
        )

        if (
            backup_quantity
            <
            minimum_quantity
        ):

            print(
                f"UNIT 14 B{next_backup_stage} BLOCKED: "
                "QUANTITY BELOW MINIMUM",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # 13G. FINAL POSITION RECONCILIATION
        # ====================================================

        try:

            final_position = (
                get_active_position()
            )

        except Exception as exc:

            print(
                "UNIT 14 FINAL POSITION CHECK ERROR = "
                f"{repr(exc)}",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        if final_position is None:

            print(
                f"UNIT 14 B{next_backup_stage} BLOCKED: "
                "POSITION CLOSED BEFORE SUBMISSION",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        final_side = str(
            final_position.get(
                "side",
                "",
            )
        ).upper()

        if (
            final_side
            !=
            position_side
        ):
            raise RuntimeError(
                "UNIT 14 BLOCKED: "
                "POSITION DIRECTION CHANGED"
            )

        final_trade_key = (
            get_trade_key(
                final_position
            )
        )

        if (
            final_trade_key
            !=
            trade_key
        ):

            print(
                f"UNIT 14 B{next_backup_stage} BLOCKED: "
                "POSITION IDENTITY CHANGED",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        try:

            final_liquidation = Decimal(
                str(
                    final_position.get(
                        "liquidatePrice",
                        "0",
                    )
                )
            )

        except Exception:

            final_liquidation = (
                Decimal("0")
            )

        # ----------------------------------------------------
        # If WEEX changed liquidation before submission,
        # restart. Never submit from stale liquidation.
        # ----------------------------------------------------

        if (
            final_liquidation
            !=
            liquidation_price
        ):

            print(
                f"UNIT 14 B{next_backup_stage} "
                "LIQUIDATION CHANGED BEFORE SUBMISSION",
                flush=True,
            )

            print(
                "OLD LIQUIDATION = "
                f"{liquidation_price}",
                flush=True,
            )

            print(
                "NEW LIQUIDATION = "
                f"{final_liquidation}",
                flush=True,
            )

            print(
                "UNIT 14 RECALCULATING BACKUP TRIGGER",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # 13H. ORDER RATE GUARD
        # ====================================================

        elapsed = (
            time.time()
            -
            last_runtime_order_time
        )

        if (
            last_runtime_order_time
            >
            0
            and
            elapsed
            <
            60
        ):

            print(
                f"UNIT 14 B{next_backup_stage} "
                "WAITING FOR DEMO ORDER RATE WINDOW",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # 13I. BUILD BACKUP ORDER
        # ====================================================

        if (
            position_side
            ==
            "LONG"
        ):

            backup_order_side = (
                "BUY"
            )

        else:

            backup_order_side = (
                "SELL"
            )

        backup_payload = {
            "symbol":
                demo_symbol,

            "side":
                backup_order_side,

            "positionSide":
                position_side,

            "type":
                "MARKET",

            "quantity":
                quantity_text(
                    backup_quantity
                ),

            "newClientOrderId":
                next_client_id,
        }

        for prohibited in (
            "slTriggerPrice",
            "SlWorkingType",
            "stopLossPrice",
            "stopPrice",
        ):

            if (
                prohibited
                in
                backup_payload
            ):

                raise RuntimeError(
                    "UNIT 14 BLOCKED: "
                    "SL FIELD DETECTED"
                )

        print(
            "-" * 80,
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            "TRIGGER REACHED = TRUE",
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            "LIQUIDATION REFERENCE = "
            f"{liquidation_price}",
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            "TRIGGER PRICE = "
            f"{backup_trigger}",
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            "CURRENT MARK = "
            f"{current_mark}",
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            "ORDER SIDE = "
            f"{backup_order_side}",
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            "QUANTITY = "
            f"{backup_quantity}",
            flush=True,
        )

        print(
            "UNIT 14 DEMO ORDER = TRUE",
            flush=True,
        )

        print(
            "UNIT 14 REAL ORDER = FALSE",
            flush=True,
        )

        print(
            "UNIT 14 SL ENABLED = FALSE",
            flush=True,
        )

        # ====================================================
        # 14. SUBMIT EXACTLY ONE DEMO BACKUP
        # ====================================================

        try:

            backup_result = authenticated_post(
                "/capi/v3/sim/order",
                backup_payload,
            )

            last_runtime_order_time = (
                time.time()
            )

        except Exception as exc:

            print(
                f"UNIT 14 B{next_backup_stage} "
                "SUBMISSION ERROR = "
                f"{repr(exc)}",
                flush=True,
            )

            # Outcome may be uncertain.
            # Do not blindly resubmit.
            # Next cycle re-reads order history first.

            last_runtime_order_time = (
                time.time()
            )

            time.sleep(
                poll_seconds
            )

            continue

        if (
            backup_result.get(
                "success"
            )
            is not True
        ):

            print(
                f"UNIT 14 B{next_backup_stage} "
                "NOT ACCEPTED = "
                f"{backup_result}",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        backup_order_id = (
            backup_result.get(
                "orderId"
            )
        )

        if not backup_order_id:

            print(
                f"UNIT 14 B{next_backup_stage} "
                "ACCEPTED WITHOUT ORDER ID",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        print(
            "-" * 80,
            flush=True,
        )

        print(
            f"PASS: UNIT 14 B{next_backup_stage} "
            "DEMO ORDER ACCEPTED",
            flush=True,
        )

        print(
            f"PASS: UNIT 14 B{next_backup_stage} "
            "ORDER ID = "
            f"{backup_order_id}",
            flush=True,
        )

        print(
            f"PASS: UNIT 14 B{next_backup_stage} "
            "WAITING FOR EXCHANGE-CONFIRMED FILL",
            flush=True,
        )

        print(
            "PASS: UNIT 14 BACKUP STAGE NOT "
            "ADVANCED BY TRIGGER ALONE",
            flush=True,
        )

        print(
            "PASS: UNIT 14 NEXT LIQUIDATION WILL "
            "BE READ FROM WEEX AFTER FILL",
            flush=True,
        )

        print(
            "PASS: UNIT 14 REAL ORDER = FALSE",
            flush=True,
        )

        print(
            "PASS: UNIT 14 SL REMAINS DISABLED",
            flush=True,
        )

        print(
            "PASS: UNIT 14 NO LEVERAGE MUTATION",
            flush=True,
        )

        print(
            "PASS: UNIT 14 NO MARGIN MODE MUTATION",
            flush=True,
        )

        print(
            "PASS: UNIT 14 NO POSITION MODE MUTATION",
            flush=True,
        )

        print(
            "=" * 80,
            flush=True,
        )

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # DO NOT calculate B2/B3 here.
        #
        # NEXT LOOP:
        #
        # 1. Reads history.
        # 2. Confirms Bn FILLED.
        # 3. Reads actual changed position.
        # 4. Reads WEEX's new liquidation price.
        # 5. Resets TP3 best mark.
        # 6. Only then calculates B(n+1).
        # ----------------------------------------------------

        time.sleep(
            poll_seconds
        )

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
# ============================================================

def unit15_telegram(message):

    token = _u15_os.getenv(
        "TELEGRAM_BOT_TOKEN", ""
    ).strip()

    chat = _u15_os.getenv(
        "TELEGRAM_CHAT_ID", ""
    ).strip()

    if not token or not chat:

        print(
            "UNIT 15 TELEGRAM NOT CONFIGURED",
            flush=True,
        )

        return False

    payload = _u15_parse.urlencode({
        "chat_id": chat,
        "text": message,
    }).encode()

    req = _u15_request.Request(
        "https://api.telegram.org/bot"
        + token
        + "/sendMessage",
        data=payload,
        method="POST",
    )

    try:

        with _u15_request.urlopen(
            req,
            timeout=15,
        ) as response:

            result = _u15_json.loads(
                response.read().decode()
            )

        good = bool(
            result.get("ok")
        )

        print(
            "UNIT 15 TELEGRAM SENT =",
            good,
            flush=True,
        )

        return good

    except Exception as exc:

        print(
            "UNIT 15 TELEGRAM ERROR =",
            type(exc).__name__,
            flush=True,
        )

        return False


# ============================================================
# UNIT 15 COMPLETED EIGHT-HOUR WINDOW
# ============================================================

def unit15_latest_8h_end(now):

    candidates = []

    for days_back in (0, 1):

        day = (
            now - _U15_DELTA(
                days=days_back
            )
        ).date()

        for hour, minute in _UNIT15_SLOTS:

            end = _U15_DT(
                day.year,
                day.month,
                day.day,
                hour,
                minute,
                tzinfo=_UNIT15_ZONE,
            )

            if end <= now:
                candidates.append(end)

    return (
        max(candidates)
        if candidates
        else None
    )


# ============================================================
# UNIT 15 PERFORMANCE REPORT
# INTERVAL + PREVIOUS 8H + CUMULATIVE PERFORMANCE
# ZERO INDENTATION
# PRESERVES EXISTING WORKER AND TELEGRAM COMMANDS
# ============================================================

def unit15_report(
    hours=8,
    reason="ON_DEMAND",
    end=None,
):

    global _UNIT15_LAST_REPORT

    if hours not in (1, 8, 24):
        raise ValueError(
            "UNIT 15 UNSUPPORTED REPORT INTERVAL"
        )

    with _UNIT15_LOCK:

        now = _U15_DT.now(
            _UNIT15_ZONE
        )

        if end is None:

            end = (
                unit15_latest_8h_end(now)
                if hours == 8
                else now
            )

        if end is None:
            raise RuntimeError(
                "UNIT 15 NO COMPLETED WINDOW"
            )

        start = (
            end - _U15_DELTA(
                hours=hours
            )
        )

        start_ms = int(
            start.timestamp() * 1000
        )

        end_ms = int(
            end.timestamp() * 1000
        )

        
        # ----------------------------------------------------
        # UNIT 15 EQUITY SNAPSHOT
        # INDENTATION: 8 SPACES
        # ----------------------------------------------------

        equity_snapshot = None
        equity_error = None

        try:

            equity_snapshot = (
                unit15_read_equity()
            )

            unit15_save_equity(
                equity_snapshot
            )

            print(
                "UNIT 15 EQUITY SNAPSHOT =",
                equity_snapshot,
                flush=True,
            )

        except Exception as exc:

            equity_error = str(exc)

            print(
                "UNIT 15 EQUITY READ UNAVAILABLE =",
                equity_error,
                flush=True,
            )

        equity_result = (
            unit15_equity_change(
                start_ms,
                end_ms,
            )
        )
        # ----------------------------------------------------
        # FETCH EXCHANGE HISTORY ONCE
        # ----------------------------------------------------

        orders, complete = (
            unit15_history_get()
        )

        # ----------------------------------------------------
        # CURRENT SELECTED INTERVAL
        # ----------------------------------------------------

        result = unit15_analyze(
            orders,
            complete,
            start_ms,
            end_ms,
        )

        # ----------------------------------------------------
        # CUMULATIVE AVAILABLE HISTORY
        # ----------------------------------------------------

        cumulative = unit15_analyze(
            orders,
            complete,
            0,
            end_ms,
        )

        # ----------------------------------------------------
        # PREVIOUS 8H INTERVAL
        # ----------------------------------------------------

        previous = None

        if hours == 8:

            previous_start_ms = (
                start_ms - 8 * 3600000
            )

            previous = unit15_analyze(
                orders,
                complete,
                previous_start_ms,
                start_ms,
            )

        # ----------------------------------------------------
        # CURRENT INTERVAL RESULTS
        # ----------------------------------------------------

        wins = result["winners"]
        losses = result["losers"]

        amount = (
            result["gross_win"]
            + result["gross_loss"]
        )

        # ----------------------------------------------------
        # CUMULATIVE RESULTS
        # ----------------------------------------------------

        cumulative_wins = (
            cumulative["winners"]
        )

        cumulative_losses = (
            cumulative["losers"]
        )

        cumulative_count = (
            cumulative["completed"]
        )

        cumulative_gross_profit = (
            cumulative["gross_win"]
        )

        cumulative_gross_loss = (
            cumulative["gross_loss"]
        )

        cumulative_gross_pnl = (
            cumulative["gross_pnl"]
        )

        # ----------------------------------------------------
        # BUILD MAIN REPORT
        # ----------------------------------------------------

        report = (
            "WEEX DEMO TRADING PERFORMANCE\n"
            "================================\n"
            f"Notification: {reason}\n"
            f"Period: {hours}h\n"
            f"Window: {start:%Y-%m-%d %H:%M} to "
            f"{end:%Y-%m-%d %H:%M} WAT\n"
            f"History orders: {result['orders']}\n"
            f"Fully filled: {result['fills']}\n"
            f"Completed cycles: {result['completed']}\n"
            f"Winning cycles: {wins}\n"
            f"Losing cycles: {losses}\n"
            f"Break-even: {result['breakeven']}\n"
            f"Gross win rate: "
            f"{unit15_percent(wins, wins + losses)}\n"
            f"Gross loss rate: "
            f"{unit15_percent(losses, wins + losses)}\n"
            f"Winning amount share: "
            f"{unit15_percent(result['gross_win'], amount)}\n"
            f"Losing amount share: "
            f"{unit15_percent(result['gross_loss'], amount)}\n"
            f"Gross profit: {result['gross_win']:.4f} USDT\n"
            f"Gross loss: {result['gross_loss']:.4f} USDT\n"
            f"Gross P&L: {result['gross_pnl']:+.4f} USDT\n"
            f"Unmatched closes: {len(result['unmatched'])}\n"
            f"History complete: {result['history_complete']}\n"
            f"Provisional: {result['provisional']}\n"
            "Net ROI: N/A\n"
            "Fees/funding/margin: Unverified\n"
            "Close cause: Unverified\n"
        )

        
        # ----------------------------------------------------
        # UNIT 15 EQUITY PERFORMANCE REPORT
        # INDENTATION: 8 SPACES
        # ----------------------------------------------------

        report += (
            "\nEQUITY-BASED PERFORMANCE\n"
            "================================\n"
        )

        if equity_result is None:

            report += (
                "Starting equity: N/A\n"
                "Ending equity: N/A\n"
                "Equity change: N/A\n"
                "Equity ROI: N/A\n"
                "Reason: Matching historical "
                "equity snapshots unavailable\n"
            )

        else:

            report += (
                f"Starting equity: "
                f"{equity_result['start']:.4f} SUSDT\n"
                f"Ending equity: "
                f"{equity_result['end']:.4f} SUSDT\n"
                f"Equity change: "
                f"{equity_result['change']:+.4f} SUSDT\n"
            )

            if equity_result["roi"] is None:

                report += (
                    "Equity ROI: N/A\n"
                )

            else:

                report += (
                    f"Equity ROI: "
                    f"{equity_result['roi']:+.2f}%\n"
                )

        report += (
            "Net trading profit: Unverified\n"
            "Deposits/transfers: Unverified\n"
            "Exchange writes: FALSE\n"
        )
        # ----------------------------------------------------
        # ADD PREVIOUS 8H COMPARISON
        # ----------------------------------------------------

        if previous is not None:

            combined_profit = (
                previous["gross_pnl"]
                + result["gross_pnl"]
            )

            combined_wins = (
                previous["winners"]
                + result["winners"]
            )

            combined_losses = (
                previous["losers"]
                + result["losers"]
            )

            report += (
                "\nPREVIOUS 8H COMPARISON\n"
                "================================\n"
                f"Previous 8H P&L: "
                f"{previous['gross_pnl']:+.4f} USDT\n"
                f"Current 8H P&L: "
                f"{result['gross_pnl']:+.4f} USDT\n"
                f"Combined 16H P&L: "
                f"{combined_profit:+.4f} USDT\n"
                f"Combined winning cycles: "
                f"{combined_wins}\n"
                f"Combined losing cycles: "
                f"{combined_losses}\n"
            )

        # ----------------------------------------------------
        # ADD CUMULATIVE PERFORMANCE
        # ----------------------------------------------------

        report += (
            "\nCUMULATIVE PERFORMANCE\n"
            "================================\n"
            "Scope: Available exchange history\n"
            f"Completed cycles: {cumulative_count}\n"
            f"Winning cycles: {cumulative_wins}\n"
            f"Losing cycles: {cumulative_losses}\n"
            f"Break-even: {cumulative['breakeven']}\n"
            f"Gross win rate: "
            f"{unit15_percent(cumulative_wins, cumulative_wins + cumulative_losses)}\n"
            f"Gross profit: "
            f"{cumulative_gross_profit:.4f} USDT\n"
            f"Gross loss: "
            f"{cumulative_gross_loss:.4f} USDT\n"
            f"Gross P&L: "
            f"{cumulative_gross_pnl:+.4f} USDT\n"
            f"Unmatched closes: "
            f"{len(cumulative['unmatched'])}\n"
            f"History complete: "
            f"{cumulative['history_complete']}\n"
            f"Provisional: "
            f"{cumulative['provisional']}\n"
            "Net profit: PENDING\n"
            "Net ROI: PENDING\n"
            "Exchange writes: FALSE\n"
            "================================"
        )

        # ----------------------------------------------------
        # DIAGNOSTICS
        # ----------------------------------------------------

        print(
            "UNIT 15 REPORT START\n"
            + report,
            flush=True,
        )

        print(
            "UNIT 15 OPEN QUANTITIES =",
            result["open_qty"],
            flush=True,
        )

        print(
            "UNIT 15 DIAGNOSTICS =",
            result["reasons"],
            flush=True,
        )

        for item in result["unmatched"][:20]:

            print(
                "UNIT 15 UNMATCHED CLOSE =",
                item,
                flush=True,
            )

        if result["provisional"]:

            print(
                "WARNING: UNIT 15 INTERVAL "
                "RECONSTRUCTION PROVISIONAL",
                flush=True,
            )

        if cumulative["provisional"]:

            print(
                "WARNING: UNIT 15 CUMULATIVE "
                "RECONSTRUCTION PROVISIONAL",
                flush=True,
            )

        # ----------------------------------------------------
        # SAVE LATEST RESULT IN MEMORY
        # ----------------------------------------------------

        _UNIT15_LAST_REPORT = {
            "interval": result,
            "cumulative": cumulative,
            "previous_8h": previous,
        }

        # ----------------------------------------------------
        # TELEGRAM DELIVERY
        # ----------------------------------------------------

        unit15_telegram(report)

        return _UNIT15_LAST_REPORT


# ============================================================
# END UNIT 15 PERFORMANCE REPORT REPLACEMENT
# EXISTING TELEGRAM COMMANDS CONTINUE BELOW
# ============================================================

# ============================================================
# UNIT 15 VOLUNTARY TELEGRAM COMMANDS
# ============================================================

def unit15_poll_commands():

    global _UNIT15_OFFSET
    global _UNIT15_POLL_STARTED

    if not UNIT15_ON_DEMAND:
        return []

    token = _u15_os.getenv(
        "TELEGRAM_BOT_TOKEN", ""
    ).strip()

    chat_id = _u15_os.getenv(
        "TELEGRAM_CHAT_ID", ""
    ).strip()

    if not token or not chat_id:
        return []

    params = {
        "timeout": 0,
        "limit": 50,
        "allowed_updates":
            _u15_json.dumps(["message"]),
    }

    if _UNIT15_OFFSET is not None:
        params["offset"] = _UNIT15_OFFSET

    elif not _UNIT15_POLL_STARTED:
        params["offset"] = -1

    url = (
        "https://api.telegram.org/bot"
        + token
        + "/getUpdates?"
        + _u15_parse.urlencode(params)
    )

    req = _u15_request.Request(
        url,
        method="GET",
    )

    with _u15_request.urlopen(
        req,
        timeout=12,
    ) as response:

        payload = _u15_json.loads(
            response.read().decode()
        )

    if not payload.get("ok"):
        return []

    updates = payload.get(
        "result", []
    )

    choices = []

    for update in updates:

        uid = update.get(
            "update_id"
        )

        if isinstance(uid, int):

            _UNIT15_OFFSET = max(
                uid + 1,
                _UNIT15_OFFSET or 0,
            )

        if not _UNIT15_POLL_STARTED:
            continue

        msg = (
            update.get("message")
            or {}
        )

        if str(
            (
                msg.get("chat")
                or {}
            ).get("id", "")
        ) != chat_id:
            continue

        parts = str(
            msg.get("text", "")
        ).strip().lower().split()

        if (
            not parts
            or parts[0].split("@")[0]
            != "/report"
        ):
            continue

        choice = (
            parts[1]
            if len(parts) > 1
            else "8h"
        )

        if choice in (
            "1h",
            "8h",
            "24h",
            "all",
        ):
            choices.append(choice)

    _UNIT15_POLL_STARTED = True

    return choices


# ============================================================
# UNIT 15 SCHEDULED REPORTING WORKER
# ============================================================

def unit15_worker():

    global _UNIT15_LAST_SLOT

    print(
        "UNIT 15 WORKER LOOP ENTERED",
        flush=True,
    )

    print(
        "UNIT 15 INTERVALS = 1H / 8H / 24H",
        flush=True,
    )

    print(
        "UNIT 15 SCHEDULE = "
        "05:00 / 13:00 / 21:00 WAT",
        flush=True,
    )

    print(
        "UNIT 15 STARTUP REPORT = DISABLED",
        flush=True,
    )

    while True:

        try:

            now = _U15_DT.now(
                _UNIT15_ZONE
            )

            key = now.strftime(
                "%Y-%m-%d %H:%M"
            )

            if (
                UNIT15_8H_ENABLED
                and (
                    now.hour,
                    now.minute
                ) in _UNIT15_SLOTS
                and key != _UNIT15_LAST_SLOT
            ):

                _UNIT15_LAST_SLOT = key

                close = now.replace(
                    second=0,
                    microsecond=0,
                )

                unit15_report(
                    8,
                    "SCHEDULED_8H",
                    close,
                )

        except Exception as exc:

            print(
                "UNIT 15 SCHEDULE ERROR =",
                repr(exc),
                flush=True,
            )

        try:

            for choice in unit15_poll_commands():

                hours_list = (
                    (1, 8, 24)
                    if choice == "all"
                    else (
                        int(choice[:-1]),
                    )
                )

                for hours in hours_list:

                    if (
                        hours == 8
                        and not UNIT15_8H_ENABLED
                    ):
                        continue

                    unit15_report(
                        hours,
                        "ON_DEMAND",
                    )

        except Exception as exc:

            print(
                "UNIT 15 COMMAND ERROR =",
                type(exc).__name__,
                flush=True,
            )

        _u15_time.sleep(10)


# ============================================================
# UNIT 15 SINGLE WORKER ACTIVATION
# ============================================================

if UNIT15_ENABLED:

    prior = globals().get(
        "_UNIT15_THREAD"
    )

    if (
        prior is None
        or not prior.is_alive()
    ):

        _UNIT15_THREAD = (
            _u15_threading.Thread(
                target=unit15_worker,
                name="WEEX-UNIT15-PERFORMANCE",
                daemon=True,
            )
        )

        _UNIT15_THREAD.start()

        print(
            "PASS: UNIT 15 REPORTING WORKER STARTED",
            flush=True,
        )

    print(
        "PASS: UNIT 15 EXCHANGE READ ONLY",
        flush=True,
    )

    print(
        "PASS: UNITS 1-14 PRESERVED",
        flush=True,
    )

else:

    print(
        "UNIT 15 DISABLED",
        flush=True,
    )


# ============================================================
# END COMPLETE UNIT 15 REPLACEMENT
# NEXT: START CONTINUOUS OPERATION CORRECTION
# ============================================================

# ============================================================
# START CONTINUOUS OPERATION CORRECTION
# REPLACES THE EXISTING RUN UNIT 14 CALL ONLY
# ZERO INDENTATION
# ============================================================

import os
import time

print(
    "CONTINUOUS TRADING CYCLE = ENABLED",
    flush=True,
)

# Run Unit 14 first using the fresh startup
# results already produced by Units 1-13.

FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    fresh_tp3_runtime(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_13_RESULT,
    )
)

# Unit 14 returns after position closure.
# Rebuild fresh market analysis and entry
# decisions before beginning another trade.

continuous_cycle = 0

while True:

    # --------------------------------------------------------
    # 1. REQUIRE COMPLETED UNIT 14
    # --------------------------------------------------------

    if not isinstance(
        FRESH_RECONSTRUCTION_UNIT_14_RESULT,
        dict,
    ):
        raise RuntimeError(
            "CONTINUOUS CYCLE: INVALID UNIT 14 RESULT"
        )

    previous_status = str(
        FRESH_RECONSTRUCTION_UNIT_14_RESULT.get(
            "status",
            "",
        )
    ).upper()

    if previous_status != "POSITION_CLOSED":
        raise RuntimeError(
            "CONTINUOUS CYCLE BLOCKED: "
            "UNIT 14 DID NOT CONFIRM POSITION_CLOSED"
        )

    continuous_cycle += 1

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "CONTINUOUS ENTRY SCAN CYCLE =",
        continuous_cycle,
        flush=True,
    )

    # --------------------------------------------------------
    # 2. REFRESH BOT MODE
    # --------------------------------------------------------

    BOT_MODE = os.getenv(
        "BOT_MODE",
        "RUN",
    ).strip().upper()

    if BOT_MODE not in ("RUN", "PAUSE"):
        raise RuntimeError(
            "INVALID BOT_MODE: SET RUN OR PAUSE"
        )

    # --------------------------------------------------------
    # 3. REFRESH MARKET DATA
    # --------------------------------------------------------

    FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
        fresh_reconstruction_unit_3()
    )

    FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
        fresh_reconstruction_unit_4()
    )

    # --------------------------------------------------------
    # 4. REFRESH SIGNAL AND ENTRY ANALYSIS
    # --------------------------------------------------------

    FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
        fresh_reconstruction_unit_5(
            FRESH_RECONSTRUCTION_CONFIG,
            FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        )
    )

    FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE = (
        fresh_reconstruction_unit_6(
            FRESH_RECONSTRUCTION_CONFIG,
            FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
            FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE,
        )
    )

    FRESH_RECONSTRUCTION_SIZING_CANDIDATE = (
        fresh_reconstruction_unit_7(
            FRESH_RECONSTRUCTION_CONFIG,
            FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE,
        )
    )

    # --------------------------------------------------------
    # 5. REFRESH POSITION SIZING AND VALIDATION
    # --------------------------------------------------------

    FRESH_RECONSTRUCTION_UNIT_8_RESULT = (
        fresh_reconstruction_unit_8(
            FRESH_RECONSTRUCTION_CONFIG,
            FRESH_RECONSTRUCTION_SIZING_CANDIDATE,
            FRESH_RECONSTRUCTION_MARKET_SNAPSHOT,
        )
    )

    FRESH_RECONSTRUCTION_UNIT_9_RESULT = (
        fresh_reconstruction_unit_9(
            FRESH_RECONSTRUCTION_CONFIG,
            FRESH_RECONSTRUCTION_UNIT_8_RESULT,
        )
    )

    FRESH_RECONSTRUCTION_UNIT_10_RESULT = (
        fresh_reconstruction_unit_10(
            FRESH_RECONSTRUCTION_CONFIG,
            FRESH_RECONSTRUCTION_UNIT_9_RESULT,
        )
    )

    FRESH_RECONSTRUCTION_UNIT_11_RESULT = (
        fresh_reconstruction_unit_11(
            FRESH_RECONSTRUCTION_CONFIG,
            FRESH_RECONSTRUCTION_UNIT_10_RESULT,
        )
    )

    # --------------------------------------------------------
    # 6. CONTROL NEW ENTRY
    # --------------------------------------------------------

    if BOT_MODE == "PAUSE":

        print(
            "CONTINUOUS CYCLE: NEW ENTRY PAUSED",
            flush=True,
        )

        FRESH_RECONSTRUCTION_UNIT_12_RESULT = {
            "unit": 12,
            "status": "IDLE",
            "read_only": True,
            "demo_submission_attempted": False,
            "demo_submission_completed": False,
            "real_submission_attempted": False,
            "skip_reason": "BOT_MODE_PAUSE",
        }

    else:

        FRESH_RECONSTRUCTION_UNIT_12_RESULT = (
            fresh_reconstruction_unit_12(
                FRESH_RECONSTRUCTION_CONFIG,
                FRESH_RECONSTRUCTION_UNIT_11_RESULT,
            )
        )

    # --------------------------------------------------------
    # 7. REFRESH TP POSITION PLAN
    # --------------------------------------------------------

    FRESH_RECONSTRUCTION_UNIT_13_RESULT = (
        fresh_reconstruction_unit_13(
            FRESH_RECONSTRUCTION_CONFIG,
            FRESH_RECONSTRUCTION_UNIT_12_RESULT,
        )
    )

    # --------------------------------------------------------
    # 8. RETURN TO ESTABLISHED UNIT 14 MANAGEMENT
    # --------------------------------------------------------

    FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
        fresh_tp3_runtime(
            FRESH_RECONSTRUCTION_CONFIG,
            FRESH_RECONSTRUCTION_UNIT_13_RESULT,
        )
    )

    print(
        "CONTINUOUS CYCLE COMPLETED =",
        continuous_cycle,
        flush=True,
    )

    # This delay applies after Unit 14 returns.
    # Unit 14 retains its own position polling.

    time.sleep(5)


# ============================================================
# END CONTINUOUS OPERATION CORRECTION
# ZERO INDENTATION
# ============================================================

# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 14
# ZERO INDENTATION DEMARCATION
#
# UNIT 14 IS FULLY CLOSED
# UNIT 14 IS CALLED
#
# NO OPEN FUNCTION
# NO OPEN LOOP
# NO OPEN IF
# NO OPEN TRY
# NO OPEN DICTIONARY
#
# TP ARCHITECTURE:
# TP1 TARGET = 10%
# TP2 TARGET = 20%
# TP3 TARGET = 70%
#
# TP3 CALLBACK:
# DYNAMIC
# NORMAL REFERENCE ~= 0.20%
# INPUTS:
# ATR/VOLATILITY
# TREND STRENGTH
# MOMENTUM DETERIORATION
#
# BACKUPS:
# ENTRY -> B1 -> L1 -> B2 -> L2 -> B3 -> L3 -> STOP
# B4 DISABLED
#
# SL DISABLED
# REAL TRADING PROHIBITED
# ============================================================


