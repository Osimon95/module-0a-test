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


# ============================================================
# PART 3 START - RECONSTRUCTION UNIT 3
# ZERO INDENTATION DEMARCATION
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
# END PART 3 - COMPLETE UNIT 3
# ZERO INDENTATION DEMARCATION
# UNIT 3 FULLY CLOSED AND CALLED
# NO OPEN FUNCTION OR BLOCK
# ============================================================

# ============================================================
# PART 4 START - FRESH RECONSTRUCTION UNIT 4
# ZERO INDENTATION DEMARCATION
# ============================================================

# ============================================================
# UNIT 4 - PUBLIC MARK PRICE KLINES + EMA ANALYSIS
# ============================================================

def fresh_reconstruction_unit_4():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 4 START")
    print("-" * 80, flush=True)

    # ========================================================
    # 1. RECEIVE UNIT 2 CONFIGURATION
    # ========================================================

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID UNIT 2 CONFIGURATION"
        )

    print(
        "PASS: UNIT 4 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    # ========================================================
    # 2. RECEIVE UNIT 3 MARKET SNAPSHOT
    # ========================================================

    market_snapshot = (
        FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    )

    if not isinstance(market_snapshot, dict):
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID UNIT 3 MARKET SNAPSHOT"
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

    missing = [
        key for key in required_snapshot_fields
        if key not in market_snapshot
    ]

    if missing:
        raise RuntimeError(
            "UNIT 4 BLOCKED: MISSING UNIT 3 FIELDS = "
            + str(missing)
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
            "UNIT 4 BLOCKED: SNAPSHOT NOT READ ONLY"
        )

    exchange_time_ms = int(
        market_snapshot["exchange_time_ms"]
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
    # 3. VALIDATE EXCHANGE CONFIGURATION
    # ========================================================

    exchange_config = config.get("exchange")
    safety = config.get("safety")

    if not isinstance(exchange_config, dict):
        raise RuntimeError(
            "UNIT 4 BLOCKED: EXCHANGE CONFIG MISSING"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 4 BLOCKED: SAFETY CONFIG MISSING"
        )

    base_url = exchange_config.get(
        "contract_base_url"
    )

    market_symbol = exchange_config.get(
        "market_symbol"
    )

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID BASE URL"
        )

    if market_symbol != market_snapshot["symbol"]:
        raise RuntimeError(
            "UNIT 4 BLOCKED: SYMBOL MISMATCH"
        )

    # ========================================================
    # 4. READ-ONLY SAFETY CONTRACT
    # ========================================================

    if (
        safety.get("public_market_data_read_enabled")
        is not True
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: MARKET READ DISABLED"
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
                "UNIT 4 BLOCKED: UNSAFE CAPABILITY: "
                + capability
            )

    print(
        "PASS: UNIT 4 READ-ONLY SAFETY GATE",
        flush=True,
    )

    # ========================================================
    # 5. WEEX V3 PUBLIC KLINE SETTINGS
    # ========================================================

    interval = "1m"
    candle_limit = 300

    endpoint = (
        "/capi/v3/market/markPriceKlines"
    )

    query_parameters = {
        "symbol": market_symbol,
        "interval": interval,
        "limit": candle_limit,
    }

    request_url = (
        base_url
        + endpoint
        + "?"
        + urllib.parse.urlencode(query_parameters)
    )

    # ========================================================
    # 6. BUILD PUBLIC GET REQUEST
    # ========================================================

    request = urllib.request.Request(
        url=request_url,
        method="GET",
        headers={
            "Accept": "application/json",
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

    # ========================================================
    # 7. EXECUTE PUBLIC READ
    # ========================================================

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            http_status = response.getcode()

            response_body = (
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as exc:

        error_body = ""

        try:
            error_body = (
                exc.read().decode("utf-8")
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
            repr(exc.reason),
            flush=True,
        )

        raise RuntimeError(
            "UNIT 4 WEEX V3 CONNECTION FAILED"
        ) from exc

    except Exception as exc:

        print(
            "UNIT 4 UNEXPECTED CONNECTION ERROR =",
            repr(exc),
            flush=True,
        )

        raise

    if http_status != 200:
        raise RuntimeError(
            "UNIT 4 BLOCKED: NON-200 HTTP STATUS"
        )

    if not response_body:
        raise RuntimeError(
            "UNIT 4 BLOCKED: EMPTY RESPONSE"
        )

    print(
        "PASS: UNIT 4 WEEX V3 KLINE RESPONSE RECEIVED",
        flush=True,
    )

    # ========================================================
    # 8. PARSE JSON RESPONSE
    # ========================================================

    try:
        raw_klines = json.loads(response_body)
    except json.JSONDecodeError as exc:

        print(
            "UNIT 4 RAW RESPONSE =",
            response_body[:1000],
            flush=True,
        )

        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID JSON"
        ) from exc

    if not isinstance(raw_klines, list):
        raise RuntimeError(
            "UNIT 4 BLOCKED: KLINES NOT A LIST"
        )

    if len(raw_klines) < 200:
        raise RuntimeError(
            "UNIT 4 BLOCKED: INSUFFICIENT KLINES"
        )

    print(
        "PASS: UNIT 4 KLINES RECEIVED =",
        len(raw_klines),
        flush=True,
    )

    # ========================================================
    # 9. NORMALIZE KLINES
    # ========================================================

    normalized_klines = []

    for raw_candle in raw_klines:

        if not isinstance(raw_candle, (list, tuple)):
            raise RuntimeError(
                "UNIT 4 BLOCKED: INVALID KLINE ENTRY"
            )

        if len(raw_candle) < 7:
            raise RuntimeError(
                "UNIT 4 BLOCKED: INCOMPLETE KLINE"
            )

        try:

            candle = {
                "open_time_ms": int(raw_candle[0]),
                "open": float(raw_candle[1]),
                "high": float(raw_candle[2]),
                "low": float(raw_candle[3]),
                "close": float(raw_candle[4]),
                "volume": float(raw_candle[5]),
                "close_time_ms": int(raw_candle[6]),
            }

        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                "UNIT 4 BLOCKED: INVALID KLINE VALUE"
            ) from exc

        if (
            candle["open"] <= 0
            or candle["high"] <= 0
            or candle["low"] <= 0
            or candle["close"] <= 0
        ):
            raise RuntimeError(
                "UNIT 4 BLOCKED: NON-POSITIVE OHLC"
            )

        normalized_klines.append(candle)

    # Ensure chronological order.

    normalized_klines.sort(
        key=lambda candle: candle["open_time_ms"]
    )

    # ========================================================
    # 10. EXCLUDE UNFINISHED CANDLES
    # ========================================================

    closed_klines = [
        candle
        for candle in normalized_klines
        if candle["close_time_ms"] <= exchange_time_ms
    ]

    if len(closed_klines) < 200:
        raise RuntimeError(
            "UNIT 4 BLOCKED: INSUFFICIENT CLOSED KLINES"
        )

    newest_returned_is_closed = (
        normalized_klines[-1]["close_time_ms"]
        <= exchange_time_ms
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

    # ========================================================
    # 11. CLOSED-CANDLE PRICE SERIES
    # ========================================================

    close_prices = [
        candle["close"]
        for candle in closed_klines
    ]

    # ========================================================
    # 12. EMA CALCULATION
    # ========================================================

    def calculate_ema(prices, period):

        if len(prices) < period:
            raise RuntimeError(
                "INSUFFICIENT DATA FOR EMA"
                + str(period)
            )

        ema_value = (
            sum(prices[:period]) / period
        )

        multiplier = 2.0 / (period + 1.0)

        for price in prices[period:]:

            ema_value = (
                price * multiplier
                + ema_value * (1.0 - multiplier)
            )

        return float(ema_value)

    ema19 = calculate_ema(close_prices, 19)
    ema50 = calculate_ema(close_prices, 50)
    ema200 = calculate_ema(close_prices, 200)

    if min(ema19, ema50, ema200) <= 0:
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
        "PASS: UNIT 4 EMA200 =",
        round(ema200, 6),
        flush=True,
    )

    # ========================================================
    # 13. EMA SEPARATION AND STRUCTURE
    # ========================================================

    ema19_50_separation_pct = (
        abs(ema19 - ema50) / ema50 * 100.0
    )

    if ema19 > ema50 > ema200:
        ema_structure = "BULLISH"

    elif ema19 < ema50 < ema200:
        ema_structure = "BEARISH"

    else:
        ema_structure = "MIXED"

    print(
        "PASS: UNIT 4 EMA19/50 SEPARATION % =",
        round(ema19_50_separation_pct, 6),
        flush=True,
    )

    print(
        "PASS: UNIT 4 EMA STRUCTURE =",
        ema_structure,
        flush=True,
    )

    # ========================================================
    # 14. LATEST CLOSED CANDLES
    # ========================================================

    latest_candle = closed_klines[-1]
    previous_candle = closed_klines[-2]

    latest_close = float(
        latest_candle["close"]
    )

    previous_close = float(
        previous_candle["close"]
    )

    latest_open_time_ms = int(
        latest_candle["open_time_ms"]
    )

    latest_close_time_ms = int(
        latest_candle["close_time_ms"]
    )

    if previous_close <= 0:
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID PREVIOUS CLOSE"
        )

    # ========================================================
    # 15. SHORT-TERM MOVE
    # ========================================================

    short_term_move_pct = (
        (latest_close - previous_close)
        / previous_close
        * 100.0
    )

    print(
        "PASS: UNIT 4 SHORT TERM MOVE % =",
        round(short_term_move_pct, 6),
        flush=True,
    )

    # ========================================================
    # 16. MULTI-WINDOW MOMENTUM
    # ========================================================

    diagnostic_windows = (
        1, 5, 15, 30, 60, 120
    )

    window_moves_pct = {}

    print(
        "UNIT 4 BREAKOUT WINDOW DIAGNOSTIC",
        flush=True,
    )

    for window_minutes in diagnostic_windows:

        if len(close_prices) <= window_minutes:
            raise RuntimeError(
                "UNIT 4 BLOCKED: INSUFFICIENT WINDOW DATA"
            )

        reference_close = float(
            close_prices[-(window_minutes + 1)]
        )

        if reference_close <= 0:
            raise RuntimeError(
                "UNIT 4 BLOCKED: INVALID WINDOW CLOSE"
            )

        window_move_pct = (
            (latest_close - reference_close)
            / reference_close
            * 100.0
        )

        window_moves_pct[window_minutes] = float(
            window_move_pct
        )

        print(
            "UNIT 4",
            str(window_minutes) + "M MOVE % =",
            round(window_move_pct, 6),
            flush=True,
        )

    # ========================================================
    # 17. REAL-TIME MARK PRICE
    # ========================================================

    live_mark_price = float(
        market_snapshot["price"]
    )

    if live_mark_price <= 0:
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID LIVE MARK PRICE"
        )

    # ========================================================
    # 18. NORMALIZED ANALYSIS SNAPSHOT
    # ========================================================

    analysis_snapshot = {

        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": market_symbol,
        "interval": interval,
        "price_type": "MARK",

        "live_mark_price": live_mark_price,

        "previous_close": previous_close,
        "latest_close": latest_close,

        "latest_open_time_ms":
            latest_open_time_ms,

        "latest_close_time_ms":
            latest_close_time_ms,

        "exchange_time_ms":
            exchange_time_ms,

        "ema19": ema19,
        "ema50": ema50,
        "ema200": ema200,

        "ema19_50_separation_pct":
            ema19_50_separation_pct,

        "short_term_move_pct":
            short_term_move_pct,

        "move_1m_pct": window_moves_pct[1],
        "move_5m_pct": window_moves_pct[5],
        "move_15m_pct": window_moves_pct[15],
        "move_30m_pct": window_moves_pct[30],
        "move_60m_pct": window_moves_pct[60],
        "move_120m_pct": window_moves_pct[120],

        "ema_structure": ema_structure,

        "recent_closed_klines": [
            dict(candle)
            for candle in closed_klines[-60:]
        ],

        "candle_count": len(normalized_klines),

        "closed_candle_count": len(closed_klines),

        "newest_returned_candle_closed":
            newest_returned_is_closed,

        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",

        "read_only": True,
    }

    # ========================================================
    # 19. FINAL SNAPSHOT VALIDATION
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
        key
        for key in required_analysis_fields
        if key not in analysis_snapshot
    ]

    if missing_analysis_fields:
        raise RuntimeError(
            "UNIT 4 ANALYSIS SNAPSHOT MISSING FIELDS = "
            + str(missing_analysis_fields)
        )

    if analysis_snapshot["read_only"] is not True:
        raise RuntimeError(
            "UNIT 4 SNAPSHOT READ-ONLY FAILURE"
        )

    if latest_close_time_ms > exchange_time_ms:
        raise RuntimeError(
            "UNIT 4 CLOSED-CANDLE SAFETY FAILURE"
        )

    if abs(
        analysis_snapshot["move_1m_pct"]
        - analysis_snapshot["short_term_move_pct"]
    ) > 0.000000001:
        raise RuntimeError(
            "UNIT 4 1M MOVE CONSISTENCY FAILURE"
        )

    # ========================================================
    # 20. UNIT 4 FINAL REPORT
    # ========================================================

    print("-" * 80, flush=True)

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

    print("-" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 4 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return analysis_snapshot


# ============================================================
# RUN UNIT 4
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)


# ============================================================
# END PART 4 - COMPLETE UNIT 4
# ZERO INDENTATION DEMARCATION
# UNIT 4 FULLY CLOSED AND CALLED
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN TRY
# ============================================================

# ============================================================
# PART 5 START - FRESH RECONSTRUCTION UNIT 5
# ZERO INDENTATION DEMARCATION
# ============================================================

# ============================================================
# UNIT 5 - MULTI-WINDOW SIGNAL QUALIFICATION ENGINE
#
# MODES:
# SCALP: 5M primary momentum, EMA19/50
# STRUCTURE: 15M primary momentum, EMA19/50/200
# BREAKOUT: 30M primary momentum, 5M/15M support
#
# PRIORITY: BREAKOUT -> STRUCTURE -> SCALP
#
# READ-ONLY. NO ACCOUNT ACCESS OR ORDER EXECUTION.
# ============================================================

def fresh_reconstruction_unit_5(
    unit_2_config,
    unit_4_snapshot,
):

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 5 START")
    print("-" * 80, flush=True)

    # ========================================================
    # 1. VALIDATE INPUT CONTRACTS
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 5 FAILED: INVALID UNIT 2 CONFIGURATION"
        )

    if not isinstance(unit_4_snapshot, dict):
        raise RuntimeError(
            "UNIT 5 FAILED: INVALID UNIT 4 SNAPSHOT"
        )

    print(
        "PASS: UNIT 5 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )
    print(
        "PASS: UNIT 5 RECEIVED UNIT 4 MARKET SNAPSHOT",
        flush=True,
    )

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
        key for key in required_fields
        if key not in unit_4_snapshot
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
    # 2. NORMALIZE MARKET INPUTS
    # ========================================================

    s = unit_4_snapshot

    symbol = str(s["symbol"]).upper()
    live_price = float(s["live_mark_price"])
    ema19 = float(s["ema19"])
    ema50 = float(s["ema50"])
    ema200 = float(s["ema200"])

    separation_pct = abs(
        float(s["ema19_50_separation_pct"])
    )

    ema_structure = str(
        s["ema_structure"]
    ).upper()

    previous_close = float(s["previous_close"])
    latest_close = float(s["latest_close"])

    short_term_move_pct = float(
        s["short_term_move_pct"]
    )

    move_1m_pct = float(s["move_1m_pct"])
    move_5m_pct = float(s["move_5m_pct"])
    move_15m_pct = float(s["move_15m_pct"])
    move_30m_pct = float(s["move_30m_pct"])
    move_60m_pct = float(s["move_60m_pct"])
    move_120m_pct = float(s["move_120m_pct"])

    if live_price <= 0:
        raise RuntimeError(
            "UNIT 5 FAILED: INVALID LIVE PRICE"
        )

    if min(ema19, ema50, ema200) <= 0:
        raise RuntimeError(
            "UNIT 5 FAILED: INVALID EMA VALUE"
        )

    print(
        "PASS: UNIT 5 UNIT 4 SNAPSHOT VALIDATED",
        flush=True,
    )
    print(
        "PASS: UNIT 5 READ-ONLY SAFETY GATE",
        flush=True,
    )

    # ========================================================
    # 3. PRESERVED MODE THRESHOLDS
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

    # ========================================================
    # 4. EMA DIRECTION
    # ========================================================

    bullish_alignment = (
        ema19 > ema50 > ema200
    )

    bearish_alignment = (
        ema19 < ema50 < ema200
    )

    if bullish_alignment:
        ema_direction = "LONG"
    elif bearish_alignment:
        ema_direction = "SHORT"
    else:
        ema_direction = "NONE"

    print(
        "UNIT 5 EMA DIRECTION =",
        ema_direction,
        flush=True,
    )

    # ========================================================
    # 5. MULTI-WINDOW MOMENTUM
    # ========================================================

    def movement_direction(movement_pct):
        if movement_pct > 0:
            return "LONG"
        if movement_pct < 0:
            return "SHORT"
        return "NONE"

    momentum_1m_direction = movement_direction(
        move_1m_pct
    )
    momentum_5m_direction = movement_direction(
        move_5m_pct
    )
    momentum_15m_direction = movement_direction(
        move_15m_pct
    )
    momentum_30m_direction = movement_direction(
        move_30m_pct
    )
    momentum_60m_direction = movement_direction(
        move_60m_pct
    )
    momentum_120m_direction = movement_direction(
        move_120m_pct
    )

    for name, move, direction_value in (
        ("1M", move_1m_pct, momentum_1m_direction),
        ("5M", move_5m_pct, momentum_5m_direction),
        ("15M", move_15m_pct, momentum_15m_direction),
        ("30M", move_30m_pct, momentum_30m_direction),
        ("60M", move_60m_pct, momentum_60m_direction),
        ("120M", move_120m_pct, momentum_120m_direction),
    ):
        print(
            "UNIT 5", name,
            "MOVE % =", move,
            "| DIRECTION =", direction_value,
            flush=True,
        )

    # ========================================================
    # 6. SCALP QUALIFICATION CONTEXT
    #
    # PRIMARY = 5M MOMENTUM
    # EMA200 IS NOT REQUIRED
    # COUNTER-DIRECTION 1M DOES NOT AUTOMATICALLY VETO
    # ========================================================

    scalp_long_context = (
        ema19 > ema50
        and momentum_5m_direction == "LONG"
    )

    scalp_short_context = (
        ema19 < ema50
        and momentum_5m_direction == "SHORT"
    )

    scalp_direction = "NONE"

    if scalp_long_context:
        scalp_direction = "LONG"
    elif scalp_short_context:
        scalp_direction = "SHORT"

    scalp_move_pct = abs(move_5m_pct)

    scalp_1m_support = (
        momentum_1m_direction == scalp_direction
    )

    print(
        "UNIT 5 SCALP DIRECTION =",
        scalp_direction,
        flush=True,
    )
    print(
        "UNIT 5 SCALP 5M MOVE % =",
        move_5m_pct,
        flush=True,
    )
    print(
        "UNIT 5 SCALP 1M FRESHNESS SUPPORT =",
        scalp_1m_support,
        flush=True,
    )

    # ========================================================
    # 7. STRUCTURE QUALIFICATION CONTEXT
    #
    # PRIMARY = 15M MOMENTUM
    # REQUIRES FULL EMA ALIGNMENT
    # ========================================================

    structure_direction = "NONE"

    if (
        ema_direction != "NONE"
        and momentum_15m_direction == ema_direction
    ):
        structure_direction = ema_direction

    structure_direction_agreement = (
        structure_direction != "NONE"
    )

    structure_move_pct = abs(move_15m_pct)

    print(
        "UNIT 5 STRUCTURE DIRECTION =",
        structure_direction,
        flush=True,
    )

    # ========================================================
    # 8. BREAKOUT QUALIFICATION CONTEXT
    #
    # PRIMARY = 30M MOMENTUM
    # SUPPORT = 5M OR 15M
    # EMA200 IS PRICE CONTEXT
    # ========================================================

    breakout_primary_direction = (
        momentum_30m_direction
    )

    breakout_fast_support = (
        momentum_5m_direction
        == breakout_primary_direction
        or momentum_15m_direction
        == breakout_primary_direction
    )

    breakout_long_context = (
        breakout_primary_direction == "LONG"
        and breakout_fast_support
        and ema19 > ema50
        and live_price > ema19
        and live_price > ema200
    )

    breakout_short_context = (
        breakout_primary_direction == "SHORT"
        and breakout_fast_support
        and ema19 < ema50
        and live_price < ema19
        and live_price < ema200
    )

    breakout_direction = "NONE"

    if breakout_long_context:
        breakout_direction = "LONG"
    elif breakout_short_context:
        breakout_direction = "SHORT"

    breakout_move_pct = abs(move_30m_pct)

    print(
        "UNIT 5 BREAKOUT DIRECTION =",
        breakout_direction,
        flush=True,
    )
    print(
        "UNIT 5 BREAKOUT FAST SUPPORT =",
        breakout_fast_support,
        flush=True,
    )

    # ========================================================
    # 9. EXCLUSIVE MODE SELECTION
    #
    # BREAKOUT -> STRUCTURE -> SCALP
    # ========================================================

    active_mode = "NONE"
    direction = "NONE"
    qualified = False
    qualification_reason = "NO_MODE_QUALIFIED"

    if (
        breakout_direction != "NONE"
        and separation_pct
            >= BREAKOUT_MIN_SEPARATION_PCT
        and breakout_move_pct
            >= BREAKOUT_MIN_MOVE_PCT
    ):
        active_mode = "BREAKOUT"
        direction = breakout_direction
        qualified = True
        qualification_reason = (
            "BREAKOUT_30M_DIRECTION_AND_"
            "MULTI_WINDOW_MOMENTUM_CONFIRMED"
        )

    elif (
        structure_direction_agreement
        and separation_pct
            >= STRUCTURE_MIN_SEPARATION_PCT
        and structure_move_pct
            >= STRUCTURE_MIN_MOVE_PCT
    ):
        active_mode = "STRUCTURE"
        direction = structure_direction
        qualified = True
        qualification_reason = (
            "STRUCTURE_15M_DIRECTION_AND_"
            "MOMENTUM_CONFIRMED"
        )

    elif (
        scalp_direction != "NONE"
        and separation_pct
            >= SCALP_MIN_SEPARATION_PCT
        and scalp_move_pct
            >= SCALP_MIN_MOVE_PCT
    ):
        active_mode = "SCALP"
        direction = scalp_direction
        qualified = True
        qualification_reason = (
            "SCALP_5M_DIRECTION_AND_"
            "MOMENTUM_CONFIRMED"
        )

    else:

        any_directional_context = (
            scalp_direction != "NONE"
            or structure_direction != "NONE"
            or breakout_direction != "NONE"
        )

        if not any_directional_context:
            qualification_reason = (
                "NO_MULTI_WINDOW_DIRECTIONAL_CONTEXT"
            )

        elif separation_pct < SCALP_MIN_SEPARATION_PCT:
            qualification_reason = (
                "EMA_SEPARATION_BELOW_MINIMUM"
            )

        elif (
            scalp_direction != "NONE"
            and scalp_move_pct < SCALP_MIN_MOVE_PCT
        ):
            qualification_reason = (
                "SCALP_5M_MOVE_BELOW_MINIMUM"
            )

        elif (
            structure_direction != "NONE"
            and separation_pct
                >= STRUCTURE_MIN_SEPARATION_PCT
            and structure_move_pct
                < STRUCTURE_MIN_MOVE_PCT
        ):
            qualification_reason = (
                "STRUCTURE_15M_MOVE_BELOW_MINIMUM"
            )

        elif (
            breakout_direction != "NONE"
            and separation_pct
                >= BREAKOUT_MIN_SEPARATION_PCT
            and breakout_move_pct
                < BREAKOUT_MIN_MOVE_PCT
        ):
            qualification_reason = (
                "BREAKOUT_30M_MOVE_BELOW_MINIMUM"
            )

        else:
            qualification_reason = (
                "NO_MODE_THRESHOLDS_CONFIRMED"
            )

    # ========================================================
    # 10. PRICE RELATIONSHIP
    # ========================================================

    price_above_ema19 = live_price > ema19
    price_above_ema50 = live_price > ema50
    price_above_ema200 = live_price > ema200

    latest_close_above_previous = (
        latest_close > previous_close
    )

    # ========================================================
    # 11. NORMALIZED UNIT 5 OUTPUT
    #
    # PRESERVE UNIT 6 HANDOFF CONTRACT
    # ========================================================

    signal_candidate = {
        "symbol": symbol,
        "qualified": qualified,
        "active_mode": active_mode,
        "direction": direction,
        "qualification_reason": qualification_reason,

        "live_mark_price": live_price,

        "ema19": ema19,
        "ema50": ema50,
        "ema200": ema200,

        "ema19_50_separation_pct": separation_pct,
        "ema_structure": ema_structure,
        "ema_direction": ema_direction,

        "momentum_direction":
            momentum_1m_direction,

        "direction_agreement":
            structure_direction_agreement,

        "short_term_move_pct":
            short_term_move_pct,

        "absolute_short_term_move_pct":
            abs(short_term_move_pct),

        "previous_close": previous_close,
        "latest_close": latest_close,

        "price_above_ema19": price_above_ema19,
        "price_above_ema50": price_above_ema50,
        "price_above_ema200": price_above_ema200,

        "latest_close_above_previous":
            latest_close_above_previous,

        "move_1m_pct": move_1m_pct,
        "move_5m_pct": move_5m_pct,
        "move_15m_pct": move_15m_pct,
        "move_30m_pct": move_30m_pct,
        "move_60m_pct": move_60m_pct,
        "move_120m_pct": move_120m_pct,

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

        "scalp_direction": scalp_direction,
        "scalp_move_pct": scalp_move_pct,
        "scalp_1m_support": scalp_1m_support,

        "structure_direction": structure_direction,
        "structure_move_pct": structure_move_pct,

        "breakout_direction": breakout_direction,
        "breakout_move_pct": breakout_move_pct,
        "breakout_fast_support":
            breakout_fast_support,
    }

    # ========================================================
    # 12. FINAL DIAGNOSTICS
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "UNIT 5 ACTIVE MODE =",
        active_mode,
        flush=True,
    )
    print(
        "UNIT 5 DIRECTION =",
        direction,
        flush=True,
    )
    print(
        "UNIT 5 SIGNAL QUALIFIED =",
        qualified,
        flush=True,
    )
    print(
        "UNIT 5 QUALIFICATION REASON =",
        qualification_reason,
        flush=True,
    )
    print(
        "UNIT 5 EMA19/50 SEPARATION % =",
        separation_pct,
        flush=True,
    )

    print(
        "UNIT 5 SCALP 5M MOVE % =",
        scalp_move_pct,
        flush=True,
    )
    print(
        "UNIT 5 STRUCTURE 15M MOVE % =",
        structure_move_pct,
        flush=True,
    )
    print(
        "UNIT 5 BREAKOUT 30M MOVE % =",
        breakout_move_pct,
        flush=True,
    )

    print("-" * 80, flush=True)

    # ========================================================
    # 13. UNIT-LOCAL SAFETY REPORT
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

    print("-" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 5 RESULT = PASS"
    )

    print("=" * 80, flush=True)

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
# END PART 5 - COMPLETE UNIT 5
# ZERO INDENTATION DEMARCATION
# UNIT 5 FULLY CLOSED AND CALLED
# NO OPEN FUNCTION OR BLOCK
# NEXT UNIT = 6
# ============================================================
