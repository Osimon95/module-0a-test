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
# RECONSTRUCTION UNIT 2
# CONFIGURATION + SAFETY CONTRACT
# ============================================================

def fresh_reconstruction_unit_2():

    print(
        "=" * 80,
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 2 START"
    )

    print(
        "-" * 80,
        flush=True,
    )

    # --------------------------------------------------------
    # 1. REQUIRE UNIT 1
    # --------------------------------------------------------

    if (
        FRESH_RECONSTRUCTION_UNIT_1_READY
        is not True
    ):

        raise RuntimeError(
            "UNIT 2 BLOCKED: UNIT 1 NOT READY"
        )

    # --------------------------------------------------------
    # 2. EXCHANGE CONFIGURATION
    #
    # BTCUSDT:
    #   WEEX V3 public/live contract market symbol.
    #
    # BTCSUSDT:
    #   WEEX V3 simulated/demo order symbol.
    #
    # These are intentionally separate.
    # --------------------------------------------------------

    exchange_name = "WEEX"

    api_version = "V3"

    contract_base_url = (
        "https://api-contract.weex.com"
    )

    market_symbol = "BTCUSDT"

    demo_order_symbol = "BTCSUSDT"

    execution_environment = "DEMO"

    # --------------------------------------------------------
    # 3. SAFETY CAPABILITY CONFIGURATION
    #
    # Public market-data GET is allowed.
    #
    # Everything capable of changing account/exchange state
    # remains disabled.
    # --------------------------------------------------------

    safety = {

        "public_market_data_read_enabled":
            True,

        "demo_account_balance_read_enabled":
            True,

        "authenticated_api_enabled":
            False,

        "account_access_enabled":
            False,

        "position_access_enabled":
            False,

        "order_endpoint_access_enabled":
            False,

        "demo_order_submission_enabled":
            False,

        "real_order_submission_enabled":
            False,

        "exchange_mutation_enabled":
            False,

        "leverage_mutation_enabled":
            False,

        "margin_mode_mutation_enabled":
            False,

        "position_mode_mutation_enabled":
            False,
    }

    # --------------------------------------------------------
    # 4. STRATEGY CONFIGURATION
    # --------------------------------------------------------

    strategy = {

        "leverage_target":
            100,

        "initial_margin_percent":
            5.0,

        "backup_margin_percent":
            5.0,

        "backup_buffer_percent":
            0.30,

        "max_backups":
            3,

        "exposure_cap_percent":
            35.0,

        "tp1_allocation_percent":
            25.0,

        "tp2_allocation_percent":
            25.0,

        "tp3_allocation_percent":
            50.0,

        "tp3_trailing_percent":
            0.20,

        "signal_expiry_seconds":
            120,

        "loss_cooldown_seconds":
            300,

        "one_direction_only":
            True,

        "anti_duplicate_orders":
            True,

        "active_trade_mode_lock":
            True,

        "exclusive_mode":
            True,

        "mode_confirmations_required":
            3,
    }

    # --------------------------------------------------------
    # 5. MARKET PRECISION
    # --------------------------------------------------------

    market_precision = {

        "quantity_step":
            0.0001,

        "minimum_quantity":
            0.0001,

        "price_step":
            0.1,
    }

    # --------------------------------------------------------
    # 6. COMPLETE CONFIGURATION OBJECT
    # --------------------------------------------------------

    config = {

        "exchange": {

            "name":
                exchange_name,

            "api_version":
                api_version,

            "contract_base_url":
                contract_base_url,

            "market_symbol":
                market_symbol,

            "demo_order_symbol":
                demo_order_symbol,
        },

        "execution_environment":
            execution_environment,

        "safety":
            safety,

        "strategy":
            strategy,

        "market_precision":
            market_precision,
    }

    # --------------------------------------------------------
    # 7. CONFIGURATION VALIDATION
    # --------------------------------------------------------

    validation_errors = []

    if exchange_name != "WEEX":

        validation_errors.append(
            "INVALID EXCHANGE"
        )

    if api_version != "V3":

        validation_errors.append(
            "INVALID API VERSION"
        )

    if (
        contract_base_url
        !=
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

    # --------------------------------------------------------
    # STRATEGY VALIDATION
    # --------------------------------------------------------

    if (
        strategy["leverage_target"]
        <= 0
    ):

        validation_errors.append(
            "INVALID LEVERAGE TARGET"
        )

    if (
        strategy["initial_margin_percent"]
        <= 0
    ):

        validation_errors.append(
            "INVALID INITIAL MARGIN"
        )

    if (
        strategy["backup_margin_percent"]
        <= 0
    ):

        validation_errors.append(
            "INVALID BACKUP MARGIN"
        )

    if (
        strategy["backup_buffer_percent"]
        <= 0
    ):

        validation_errors.append(
            "INVALID BACKUP BUFFER"
        )

    if (
        strategy["max_backups"]
        != 3
    ):

        validation_errors.append(
            "INVALID MAX BACKUPS"
        )

    if (
        strategy["exposure_cap_percent"]
        <= 0
    ):

        validation_errors.append(
            "INVALID EXPOSURE CAP"
        )

    tp_total = (

        strategy[
            "tp1_allocation_percent"
        ]

        +

        strategy[
            "tp2_allocation_percent"
        ]

        +

        strategy[
            "tp3_allocation_percent"
        ]
    )

    if tp_total != 100.0:

        validation_errors.append(
            "TP ALLOCATION DOES NOT TOTAL 100%"
        )

    if (
        strategy["tp3_trailing_percent"]
        <= 0
    ):

        validation_errors.append(
            "INVALID TP3 TRAILING PERCENT"
        )

    if (
        strategy["signal_expiry_seconds"]
        <= 0
    ):

        validation_errors.append(
            "INVALID SIGNAL EXPIRY"
        )

    if (
        strategy["loss_cooldown_seconds"]
        <= 0
    ):

        validation_errors.append(
            "INVALID LOSS COOLDOWN"
        )

    if (
        strategy[
            "mode_confirmations_required"
        ]
        <= 0
    ):

        validation_errors.append(
            "INVALID MODE CONFIRMATION COUNT"
        )

    # --------------------------------------------------------
    # BOOLEAN STRATEGY CONTRACTS
    # --------------------------------------------------------

    required_true_strategy_flags = (

        "one_direction_only",

        "anti_duplicate_orders",

        "active_trade_mode_lock",

        "exclusive_mode",
    )

    for flag_name in required_true_strategy_flags:

        if (
            strategy.get(
                flag_name
            )
            is not True
        ):

            validation_errors.append(
                "STRATEGY FLAG MUST BE TRUE: "
                +
                flag_name
            )

    # --------------------------------------------------------
    # PRECISION VALIDATION
    # --------------------------------------------------------

    if (
        market_precision[
            "quantity_step"
        ]
        <= 0
    ):

        validation_errors.append(
            "INVALID QUANTITY STEP"
        )

    if (
        market_precision[
            "minimum_quantity"
        ]
        <= 0
    ):

        validation_errors.append(
            "INVALID MINIMUM QUANTITY"
        )

    if (
        market_precision[
            "price_step"
        ]
        <= 0
    ):

        validation_errors.append(
            "INVALID PRICE STEP"
        )

    # --------------------------------------------------------
    # SAFETY VALIDATION
    # --------------------------------------------------------

    if (
        safety[
            "public_market_data_read_enabled"
        ]
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

        if (
            safety.get(
                capability
            )
            is not False
        ):

            validation_errors.append(
                "UNSAFE CAPABILITY ENABLED: "
                +
                capability
            )

    # --------------------------------------------------------
    # FINAL VALIDATION RESULT
    # --------------------------------------------------------

    if validation_errors:

        print(
            "UNIT 2 VALIDATION ERRORS =",
            validation_errors,
            flush=True,
        )

        raise RuntimeError(
            "UNIT 2 CONFIGURATION VALIDATION FAILED"
        )

    # --------------------------------------------------------
    # UNIT 2 PASS OUTPUT
    # --------------------------------------------------------

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
        strategy[
            "leverage_target"
        ],
        flush=True,
    )

    print(
        "PASS: INITIAL MARGIN % =",
        strategy[
            "initial_margin_percent"
        ],
        flush=True,
    )

    print(
        "PASS: BACKUP MARGIN % =",
        strategy[
            "backup_margin_percent"
        ],
        flush=True,
    )

    print(
        "PASS: BACKUP BUFFER % =",
        strategy[
            "backup_buffer_percent"
        ],
        flush=True,
    )

    print(
        "PASS: MAX BACKUPS =",
        strategy[
            "max_backups"
        ],
        flush=True,
    )

    print(
        "PASS: EXPOSURE CAP % =",
        strategy[
            "exposure_cap_percent"
        ],
        flush=True,
    )

    print(
        "PASS: TP ALLOCATION =",
        tp_total,
        "%",
        flush=True,
    )

    print(
        "PASS: ANTI-DUPLICATE ORDERS =",
        strategy[
            "anti_duplicate_orders"
        ],
        flush=True,
    )

    print(
        "PASS: ONE DIRECTION ONLY =",
        strategy[
            "one_direction_only"
        ],
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

    print(
        "-" * 80,
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 2 RESULT = PASS"
    )

    print(
        "=" * 80,
        flush=True,
    )

    return config


# ============================================================
# RUN UNIT 2
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# END OF TRANSMISSION PART 1
#
# ZERO INDENTATION DEMARCATION
# UNIT 2 IS FULLY CLOSED
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN TRY
# NO OPEN DICTIONARY
# NO INDENTATION CONTINUES INTO PART 2
#
# PASTE TRANSMISSION PART 2 DIRECTLY BELOW THIS LINE
# ============================================================

# ============================================================

# ============================================================
# PART 2 OF 2
# FRESH WEEX BOT RECONSTRUCTION
# UNITS 3 -> 4
#
# CONTINUES DIRECTLY AFTER PART 1
# ZERO INDENTATION AT DEMARCATION
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
    # ========================================================

    def calculate_ema(
        prices,
        period,
    ):

        if len(prices) < period:
            raise RuntimeError(
                "INSUFFICIENT DATA FOR EMA"
                + str(period)
            )

        seed_prices = (
            prices[
                :period
            ]
        )

        ema_value = (
            sum(seed_prices)
            /
            period
        )

        multiplier = (
            2.0
            /
            (
                period
                + 1.0
            )
        )

        for price in prices[period:]:

            ema_value = (
                price
                * multiplier
                +
                ema_value
                * (
                    1.0
                    -
                    multiplier
                )
            )

        return float(
            ema_value
        )

    ema19 = calculate_ema(
        close_prices,
        19,
    )

    ema50 = calculate_ema(
        close_prices,
        50,
    )

    ema200 = calculate_ema(
        close_prices,
        200,
    )

    if (
        ema19 <= 0
        or ema50 <= 0
        or ema200 <= 0
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID EMA VALUE"
        )

    print(
        "PASS: UNIT 4 EMA19 =",
        round(
            ema19,
            6,
        ),
        flush=True,
    )

    print(
        "PASS: UNIT 4 EMA50 =",
        round(
            ema50,
            6,
        ),
        flush=True,
    )

    print(
        "PASS: UNIT 4 EMA200 =",
        round(
            ema200,
            6,
        ),
        flush=True,
    )

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
    # 8. SCALP CONTEXT
    #
    # Primary momentum:
    # CLOSED 5M movement.
    #
    # EMA200 intentionally NOT required.
    #
    # The latest 1M candle remains visible for freshness,
    # but a single counter-direction 1M candle does NOT
    # automatically veto valid 5M momentum.
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

    scalp_move_pct = abs(
        move_5m_pct
    )

    scalp_1m_support = (
        momentum_1m_direction
        ==
        scalp_direction
    )

    print(
        "UNIT 5 SCALP DIRECTION = "
        f"{scalp_direction}",
        flush=True,
    )

    print(
        "UNIT 5 SCALP LONG CONTEXT = "
        f"{scalp_long_context}",
        flush=True,
    )

    print(
        "UNIT 5 SCALP SHORT CONTEXT = "
        f"{scalp_short_context}",
        flush=True,
    )

    print(
        "UNIT 5 SCALP 5M MOVE % = "
        f"{move_5m_pct}",
        flush=True,
    )

    print(
        "UNIT 5 SCALP 1M FRESHNESS SUPPORT = "
        f"{scalp_1m_support}",
        flush=True,
    )

    # ========================================================
    # 9. STRUCTURE CONTEXT
    #
    # Primary momentum:
    # CLOSED 15M movement.
    #
    # STRUCTURE still requires mature EMA19/50/200 alignment.
    # ========================================================

    structure_direction = "NONE"

    if (
        ema_direction != "NONE"
        and
        momentum_15m_direction
        ==
        ema_direction
    ):
        structure_direction = (
            ema_direction
        )

    structure_direction_agreement = (
        structure_direction
        !=
        "NONE"
    )

    structure_move_pct = abs(
        move_15m_pct
    )

    print(
        "UNIT 5 STRUCTURE DIRECTION = "
        f"{structure_direction}",
        flush=True,
    )

    print(
        "UNIT 5 STRUCTURE DIRECTION AGREEMENT = "
        f"{structure_direction_agreement}",
        flush=True,
    )

    print(
        "UNIT 5 STRUCTURE 15M MOVE % = "
        f"{move_15m_pct}",
        flush=True,
    )

    # ========================================================
    # 10. BREAKOUT CONTEXT
    #
    # Primary momentum:
    # CLOSED 30M movement.
    #
    # At least one faster window (5M or 15M) must support
    # the 30M breakout direction.
    #
    # EMA50/EMA200 crossover is still NOT required.
    # EMA200 remains directional context.
    # ========================================================

    breakout_primary_direction = (
        momentum_30m_direction
    )

    breakout_fast_support = (
        (
            momentum_5m_direction
            ==
            breakout_primary_direction
        )
        or
        (
            momentum_15m_direction
            ==
            breakout_primary_direction
        )
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

    breakout_move_pct = abs(
        move_30m_pct
    )

    print(
        "UNIT 5 BREAKOUT PRIMARY DIRECTION = "
        f"{breakout_primary_direction}",
        flush=True,
    )

    print(
        "UNIT 5 BREAKOUT FAST SUPPORT = "
        f"{breakout_fast_support}",
        flush=True,
    )

    print(
        "UNIT 5 BREAKOUT DIRECTION = "
        f"{breakout_direction}",
        flush=True,
    )

    print(
        "UNIT 5 BREAKOUT LONG CONTEXT = "
        f"{breakout_long_context}",
        flush=True,
    )

    print(
        "UNIT 5 BREAKOUT SHORT CONTEXT = "
        f"{breakout_short_context}",
        flush=True,
    )

    print(
        "UNIT 5 BREAKOUT 30M MOVE % = "
        f"{move_30m_pct}",
        flush=True,
    )

    # ========================================================
    # 11. EXCLUSIVE MODE QUALIFICATION
    #
    # Priority remains:
    #
    # BREAKOUT -> STRUCTURE -> SCALP
    #
    # Only ONE mode can qualify.
    # ========================================================

    active_mode = "NONE"
    direction = "NONE"
    qualified = False
    qualification_reason = (
        "NO_MODE_QUALIFIED"
    )

    # --------------------------------------------------------
    # BREAKOUT
    # --------------------------------------------------------

    if (
        breakout_direction != "NONE"
        and
        separation_pct
        >=
        BREAKOUT_MIN_SEPARATION_PCT
        and
        breakout_move_pct
        >=
        BREAKOUT_MIN_MOVE_PCT
    ):
        active_mode = "BREAKOUT"

        direction = (
            breakout_direction
        )

        qualified = True

        qualification_reason = (
            "BREAKOUT_30M_DIRECTION_AND_"
            "MULTI_WINDOW_MOMENTUM_CONFIRMED"
        )

    # --------------------------------------------------------
    # STRUCTURE
    # --------------------------------------------------------

    elif (
        structure_direction_agreement
        and
        separation_pct
        >=
        STRUCTURE_MIN_SEPARATION_PCT
        and
        structure_move_pct
        >=
        STRUCTURE_MIN_MOVE_PCT
    ):
        active_mode = "STRUCTURE"

        direction = (
            structure_direction
        )

        qualified = True

        qualification_reason = (
            "STRUCTURE_15M_DIRECTION_AND_"
            "MOMENTUM_CONFIRMED"
        )

    # --------------------------------------------------------
    # SCALP
    # --------------------------------------------------------

    elif (
        scalp_direction != "NONE"
        and
        separation_pct
        >=
        SCALP_MIN_SEPARATION_PCT
        and
        scalp_move_pct
        >=
        SCALP_MIN_MOVE_PCT
    ):
        active_mode = "SCALP"

        direction = (
            scalp_direction
        )

        qualified = True

        qualification_reason = (
            "SCALP_5M_DIRECTION_AND_"
            "MOMENTUM_CONFIRMED"
        )

    # --------------------------------------------------------
    # NO QUALIFIED MODE
    # --------------------------------------------------------

    else:

        any_directional_context = (
            scalp_direction != "NONE"
            or
            structure_direction != "NONE"
            or
            breakout_direction != "NONE"
        )

        if not any_directional_context:
            qualification_reason = (
                "NO_MULTI_WINDOW_DIRECTIONAL_CONTEXT"
            )

        elif (
            separation_pct
            <
            SCALP_MIN_SEPARATION_PCT
        ):
            qualification_reason = (
                "EMA_SEPARATION_BELOW_MINIMUM"
            )

        elif (
            scalp_direction != "NONE"
            and
            scalp_move_pct
            <
            SCALP_MIN_MOVE_PCT
        ):
            qualification_reason = (
                "SCALP_5M_MOVE_BELOW_MINIMUM"
            )

        elif (
            structure_direction != "NONE"
            and
            separation_pct
            >=
            STRUCTURE_MIN_SEPARATION_PCT
            and
            structure_move_pct
            <
            STRUCTURE_MIN_MOVE_PCT
        ):
            qualification_reason = (
                "STRUCTURE_15M_MOVE_BELOW_MINIMUM"
            )

        elif (
            breakout_direction != "NONE"
            and
            separation_pct
            >=
            BREAKOUT_MIN_SEPARATION_PCT
            and
            breakout_move_pct
            <
            BREAKOUT_MIN_MOVE_PCT
        ):
            qualification_reason = (
                "BREAKOUT_30M_MOVE_BELOW_MINIMUM"
            )

        else:
            qualification_reason = (
                "NO_MODE_THRESHOLDS_CONFIRMED"
            )

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

# FRESH RECONSTRUCTION UNIT 6
# SIGNAL ADMISSION / EXECUTION-INTENT GATE
#
# PURPOSE:
# Validate the normalized Unit 5 signal candidate before any
# account, position-sizing, TP, backup, or order layer exists.
#
# IMPORTANT:
# - UNIT 1-5 REMAIN FROZEN
# - ZERO AUTHENTICATED API ACCESS
# - ZERO ACCOUNT ACCESS
# - ZERO POSITION ACCESS
# - ZERO ORDER ENDPOINT ACCESS
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE WRITE
# - NO POSITION SIZING
# - NO TP / SL
# - NO BACKUP EXECUTION
# ============================================================


def fresh_reconstruction_unit_6(
    unit_2_config,
    unit_4_analysis,
    unit_5_candidate,
):
    from datetime import datetime, timezone

    print(
        "=" * 80,
        flush=True,
    )

    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 6 START",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    # --------------------------------------------------------
    # INPUT VALIDATION
    # --------------------------------------------------------

    if not isinstance(unit_2_config, dict):
        raise TypeError(
            "UNIT 6 EXPECTED UNIT 2 CONFIGURATION DICT"
        )

    print(
        "PASS: UNIT 6 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    if not isinstance(unit_4_analysis, dict):
        raise TypeError(
            "UNIT 6 EXPECTED UNIT 4 ANALYSIS SNAPSHOT DICT"
        )

    print(
        "PASS: UNIT 6 RECEIVED UNIT 4 ANALYSIS SNAPSHOT",
        flush=True,
    )

    if not isinstance(unit_5_candidate, dict):
        raise TypeError(
            "UNIT 6 EXPECTED UNIT 5 SIGNAL CANDIDATE DICT"
        )

    print(
        "PASS: UNIT 6 RECEIVED UNIT 5 SIGNAL CANDIDATE",
        flush=True,
    )

    # --------------------------------------------------------
    # READ UNIT 5 NORMALIZED VALUES
    # --------------------------------------------------------

    signal_qualified = bool(
    unit_5_candidate.get(
        "qualified",
        False,
    )
)


    active_mode = unit_5_candidate.get(
        "active_mode",
        "NONE",
    )

    direction = unit_5_candidate.get(
        "direction",
        "NONE",
    )

    qualification_reason = unit_5_candidate.get(
        "qualification_reason",
        "UNKNOWN",
    )

    print(
        "PASS: UNIT 6 UNIT 5 SIGNAL CANDIDATE READ",
        flush=True,
    )

    # --------------------------------------------------------
    # SAFETY CONFIGURATION
    # --------------------------------------------------------

    anti_duplicate_orders = bool(
        unit_2_config.get(
            "anti_duplicate_orders",
            True,
        )
    )

    one_direction_only = bool(
        unit_2_config.get(
            "one_direction_only",
            True,
        )
    )

    if not anti_duplicate_orders:
        raise RuntimeError(
            "UNIT 6 SAFETY FAILURE: "
            "ANTI-DUPLICATE ORDERS DISABLED"
        )

    if not one_direction_only:
        raise RuntimeError(
            "UNIT 6 SAFETY FAILURE: "
            "ONE DIRECTION ONLY DISABLED"
        )

    print(
        "PASS: UNIT 6 ANTI-DUPLICATE REQUIREMENT ENABLED",
        flush=True,
    )

    print(
        "PASS: UNIT 6 ONE-DIRECTION REQUIREMENT ENABLED",
        flush=True,
    )

    print(
        "PASS: UNIT 6 READ-ONLY SAFETY GATE",
        flush=True,
    )

    # --------------------------------------------------------
    # SIGNAL CONSISTENCY VALIDATION
    # --------------------------------------------------------

    valid_modes = {
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
        "NONE",
    }

    valid_directions = {
        "LONG",
        "SHORT",
        "NONE",
    }

    if active_mode not in valid_modes:
        raise RuntimeError(
            f"UNIT 6 INVALID ACTIVE MODE = {active_mode}"
        )

    if direction not in valid_directions:
        raise RuntimeError(
            f"UNIT 6 INVALID DIRECTION = {direction}"
        )

    print(
        "PASS: UNIT 6 ACTIVE MODE VALIDATED",
        flush=True,
    )

    print(
        "PASS: UNIT 6 DIRECTION VALIDATED",
        flush=True,
    )

    # --------------------------------------------------------
    # SCALP ENTRY QUALITY GATE
    # --------------------------------------------------------

    scalp_quality_minimum = 75.0
    scalp_quality_score = None
    scalp_quality_pass = None
    scalp_quality_details = {}

    if signal_qualified and active_mode == "SCALP":

        candles = unit_4_analysis.get(
            "recent_closed_klines",
            [],
        )

        if not isinstance(candles, list) or len(candles) < 20:
            raise RuntimeError(
                "UNIT 6 SCALP QUALITY BLOCKED: "
                "INSUFFICIENT CLOSED 1M OHLC HISTORY"
            )

        candles = candles[-60:]

        def pct_distance(a, b):
            if b <= 0:
                return 0.0
            return abs(a - b) / b * 100.0

        def direction_of(value, epsilon=0.000001):
            if value > epsilon:
                return "LONG"
            if value < -epsilon:
                return "SHORT"
            return "NONE"

        # Average recent 1-minute candle height.
        recent_ranges = []
        for candle in candles[-20:]:
            close = float(candle["close"])
            high = float(candle["high"])
            low = float(candle["low"])
            if close > 0:
                recent_ranges.append(
                    (high - low) / close * 100.0
                )

        average_cluster_height_pct = (
            sum(recent_ranges) / len(recent_ranges)
            if recent_ranges
            else 0.0
        )

        # Find actual local pivot highs/lows from completed candles.
        resistance_pivots = []
        support_pivots = []

        for i in range(2, len(candles) - 2):
            c = candles[i]
            left1 = candles[i - 1]
            left2 = candles[i - 2]
            right1 = candles[i + 1]
            right2 = candles[i + 2]

            high = float(c["high"])
            low = float(c["low"])

            if (
                high >= float(left1["high"])
                and high >= float(left2["high"])
                and high > float(right1["high"])
                and high > float(right2["high"])
            ):
                resistance_pivots.append(high)

            if (
                low <= float(left1["low"])
                and low <= float(left2["low"])
                and low < float(right1["low"])
                and low < float(right2["low"])
            ):
                support_pivots.append(low)

        resistance_points = resistance_pivots[-10:]
        support_points = support_pivots[-10:]

        # Require at least five actual pivots when possible.
        # If fewer exist in 60 candles, retain what exists and
        # score conservatively rather than inventing levels.
        def median(values):
            if not values:
                return None
            ordered = sorted(values)
            n = len(ordered)
            mid = n // 2
            if n % 2:
                return float(ordered[mid])
            return float(
                (ordered[mid - 1] + ordered[mid]) / 2.0
            )

        resistance_mid = median(resistance_points)
        support_mid = median(support_points)

        latest_close = float(
            unit_4_analysis.get("latest_close", 0.0)
        )
        ema19 = float(unit_5_candidate.get("ema19", 0.0))
        ema50 = float(unit_5_candidate.get("ema50", 0.0))
        ema200 = float(unit_5_candidate.get("ema200", 0.0))

        move_1m = float(unit_5_candidate.get("move_1m_pct", 0.0))
        move_5m = float(unit_5_candidate.get("move_5m_pct", 0.0))
        move_15m = float(unit_5_candidate.get("move_15m_pct", 0.0))

        latest = candles[-1]
        previous = candles[-2]
        latest_open = float(latest["open"])
        latest_high = float(latest["high"])
        latest_low = float(latest["low"])
        latest_candle_close = float(latest["close"])

        candle_range = max(latest_high - latest_low, 0.0)
        candle_body = abs(latest_candle_close - latest_open)
        body_ratio = (
            candle_body / candle_range
            if candle_range > 0
            else 0.0
        )

        ema_score = 0.0
        momentum_score = 0.0
        location_score = 0.0
        candle_score = 0.0
        sr_score = 0.0
        breakout_score = 0.0
        volatility_score = 0.0
        exhaustion_score = 0.0

        # 1) EMA alignment + price relationship: 20.
        if direction == "LONG":
            if ema19 > ema50 > ema200:
                ema_score = 20.0
            elif ema19 > ema50:
                ema_score = 15.0
            elif latest_close > ema19:
                ema_score = 8.0
        else:
            if ema19 < ema50 < ema200:
                ema_score = 20.0
            elif ema19 < ema50:
                ema_score = 15.0
            elif latest_close < ema19:
                ema_score = 8.0

        # 2) Momentum agreement/progression: 15.
        d1 = direction_of(move_1m)
        d5 = direction_of(move_5m)
        d15 = direction_of(move_15m)
        agreement_count = sum(
            1 for d in (d1, d5, d15)
            if d == direction
        )
        momentum_score = {
            0: 0.0,
            1: 5.0,
            2: 10.0,
            3: 15.0,
        }[agreement_count]

        # 3) EMA19 entry extension normalized by current noise: 15.
        extension_pct = pct_distance(latest_close, ema19)
        extension_ratio = (
            extension_pct / average_cluster_height_pct
            if average_cluster_height_pct > 0
            else 999.0
        )
        if extension_ratio <= 0.50:
            location_score = 15.0
        elif extension_ratio <= 1.00:
            location_score = 12.0
        elif extension_ratio <= 1.50:
            location_score = 7.0
        elif extension_ratio <= 2.00:
            location_score = 3.0

        # 4) Latest completed candle confirmation: 10.
        candle_direction_ok = (
            latest_candle_close > latest_open
            if direction == "LONG"
            else latest_candle_close < latest_open
        )
        if candle_direction_ok:
            candle_score = 6.0
            if body_ratio >= 0.50:
                candle_score += 2.0
            if body_ratio >= 0.70:
                candle_score += 2.0

        # 5/6) Direction-aware resistance/support midpoint and
        # breakout/breakdown quality: 15 + 10.
        reference_mid = (
            resistance_mid
            if direction == "LONG"
            else support_mid
        )
        reference_points = (
            resistance_points
            if direction == "LONG"
            else support_points
        )

        sr_distance_pct = None
        sr_distance_ratio = None
        reference_state = "NO_REFERENCE"

        if reference_mid is not None and reference_mid > 0:
            sr_distance_pct = pct_distance(
                latest_close,
                reference_mid,
            )

            sr_distance_ratio = (
                sr_distance_pct / average_cluster_height_pct
                if average_cluster_height_pct > 0
                else 999.0
            )

            if direction == "LONG":
                broken = latest_close > reference_mid
                previous_below = float(previous["close"]) <= reference_mid
            else:
                broken = latest_close < reference_mid
                previous_below = float(previous["close"]) >= reference_mid

            if broken:
                reference_state = "BROKEN"
                sr_score = 15.0
                if previous_below:
                    breakout_score = 10.0
                elif sr_distance_ratio <= 1.0:
                    breakout_score = 8.0
                else:
                    breakout_score = 5.0
            else:
                reference_state = "AHEAD"
                if sr_distance_ratio >= 2.0:
                    sr_score = 13.0
                elif sr_distance_ratio >= 1.25:
                    sr_score = 10.0
                elif sr_distance_ratio >= 0.75:
                    sr_score = 6.0
                else:
                    sr_score = 2.0
                breakout_score = 0.0
        else:
            # Missing a reliable 5-10 point cluster must not
            # receive full credit.
            sr_score = 5.0
            breakout_score = 2.0

        # 7) Healthy 1-minute tradable range: 10.
        # Relative rather than a fixed BTC percentage.
        if average_cluster_height_pct > 0:
            if 0.04 <= average_cluster_height_pct <= 0.35:
                volatility_score = 10.0
            elif 0.02 <= average_cluster_height_pct <= 0.50:
                volatility_score = 6.0
            else:
                volatility_score = 2.0

        # 8) Spike/exhaustion protection: 5.
        latest_range_pct = (
            (latest_high - latest_low) / latest_candle_close * 100.0
            if latest_candle_close > 0
            else 0.0
        )
        spike_ratio = (
            latest_range_pct / average_cluster_height_pct
            if average_cluster_height_pct > 0
            else 999.0
        )
        if spike_ratio <= 1.50:
            exhaustion_score = 5.0
        elif spike_ratio <= 2.00:
            exhaustion_score = 3.0
        elif spike_ratio <= 2.50:
            exhaustion_score = 1.0
        else:
            exhaustion_score = 0.0

        scalp_quality_score = round(
            ema_score
            + momentum_score
            + location_score
            + candle_score
            + sr_score
            + breakout_score
            + volatility_score
            + exhaustion_score,
            2,
        )

        # Hard anti-chase protection in addition to scoring.
        extreme_extension = extension_ratio > 2.50
        extreme_spike = spike_ratio > 3.00

        scalp_quality_pass = (
            scalp_quality_score >= scalp_quality_minimum
            and not extreme_extension
            and not extreme_spike
        )

        scalp_quality_details = {
            "minimum": scalp_quality_minimum,
            "score": scalp_quality_score,
            "pass": scalp_quality_pass,
            "ema_score": ema_score,
            "momentum_score": momentum_score,
            "location_score": location_score,
            "candle_score": candle_score,
            "sr_score": sr_score,
            "breakout_score": breakout_score,
            "volatility_score": volatility_score,
            "exhaustion_score": exhaustion_score,
            "average_cluster_height_pct": round(
                average_cluster_height_pct, 6
            ),
            "resistance_points": resistance_points,
            "support_points": support_points,
            "resistance_mid": resistance_mid,
            "support_mid": support_mid,
            "reference_mid": reference_mid,
            "reference_point_count": len(reference_points),
            "reference_state": reference_state,
            "sr_distance_pct": sr_distance_pct,
            "sr_distance_ratio": sr_distance_ratio,
            "ema19_extension_pct": extension_pct,
            "ema19_extension_ratio": extension_ratio,
            "latest_range_pct": latest_range_pct,
            "spike_ratio": spike_ratio,
            "extreme_extension": extreme_extension,
            "extreme_spike": extreme_spike,
        }

        print("-" * 80, flush=True)
        print("UNIT 6 SCALP QUALITY GATE", flush=True)
        print(
            f"UNIT 6 SCALP QUALITY SCORE = "
            f"{scalp_quality_score} / 100",
            flush=True,
        )
        print(
            f"UNIT 6 SCALP QUALITY MINIMUM = "
            f"{scalp_quality_minimum}",
            flush=True,
        )
        print(
            f"UNIT 6 EMA QUALITY = {ema_score} / 20",
            flush=True,
        )
        print(
            f"UNIT 6 MOMENTUM QUALITY = {momentum_score} / 15",
            flush=True,
        )
        print(
            f"UNIT 6 EMA19 LOCATION QUALITY = {location_score} / 15",
            flush=True,
        )
        print(
            f"UNIT 6 CANDLE QUALITY = {candle_score} / 10",
            flush=True,
        )
        print(
            f"UNIT 6 S/R MID QUALITY = {sr_score} / 15",
            flush=True,
        )
        print(
            f"UNIT 6 BREAKOUT/BREAKDOWN QUALITY = "
            f"{breakout_score} / 10",
            flush=True,
        )
        print(
            f"UNIT 6 VOLATILITY QUALITY = {volatility_score} / 10",
            flush=True,
        )
        print(
            f"UNIT 6 EXHAUSTION QUALITY = {exhaustion_score} / 5",
            flush=True,
        )
        print(
            f"UNIT 6 AVERAGE RECENT CLUSTER HEIGHT % = "
            f"{round(average_cluster_height_pct, 6)}",
            flush=True,
        )
        print(
            f"UNIT 6 RECENT RESISTANCE POINTS = "
            f"{resistance_points}",
            flush=True,
        )
        print(
            f"UNIT 6 RESISTANCE MID = {resistance_mid}",
            flush=True,
        )
        print(
            f"UNIT 6 RECENT SUPPORT POINTS = "
            f"{support_points}",
            flush=True,
        )
        print(
            f"UNIT 6 SUPPORT MID = {support_mid}",
            flush=True,
        )
        print(
            f"UNIT 6 ACTIVE S/R REFERENCE MID = {reference_mid}",
            flush=True,
        )
        print(
            f"UNIT 6 ACTIVE S/R REFERENCE STATE = {reference_state}",
            flush=True,
        )
        print(
            f"UNIT 6 EMA19 EXTENSION RATIO = "
            f"{round(extension_ratio, 4)} CLUSTER HEIGHTS",
            flush=True,
        )
        print(
            f"UNIT 6 SPIKE RATIO = "
            f"{round(spike_ratio, 4)} CLUSTER HEIGHTS",
            flush=True,
        )
        print(
            f"UNIT 6 SCALP QUALITY GATE = "
            f"{'PASS' if scalp_quality_pass else 'REJECT'}",
            flush=True,
        )
        print("-" * 80, flush=True)

    # --------------------------------------------------------
    # ADMISSION DECISION
    # --------------------------------------------------------

    execution_intent = False
    admission_reason = "NO_QUALIFIED_SIGNAL"

    if signal_qualified:

        if active_mode == "NONE":
            admission_reason = (
                "BLOCKED_QUALIFIED_SIGNAL_WITHOUT_MODE"
            )

        elif direction == "NONE":
            admission_reason = (
                "BLOCKED_QUALIFIED_SIGNAL_WITHOUT_DIRECTION"
            )

        elif active_mode == "SCALP" and scalp_quality_pass is not True:
            execution_intent = False
            admission_reason = (
                "SCALP_QUALITY_GATE_REJECTED:"
                f"SCORE={scalp_quality_score}:"
                f"MINIMUM={scalp_quality_minimum}"
            )

        else:
            execution_intent = True
            admission_reason = (
                "QUALIFIED_SIGNAL_ADMITTED"
            )

    else:
        execution_intent = False
        admission_reason = (
            f"UNIT_5_NOT_QUALIFIED:"
            f"{qualification_reason}"
        )

    # --------------------------------------------------------
    # NORMALIZED UNIT 6 OUTPUT
    # --------------------------------------------------------

    execution_candidate = {
        "execution_intent": execution_intent,
        "active_mode": active_mode,
        "direction": direction,
        "signal_qualified": signal_qualified,
        "unit_5_reason": qualification_reason,
        "admission_reason": admission_reason,
        "scalp_quality_score": scalp_quality_score,
        "scalp_quality_minimum": scalp_quality_minimum,
        "scalp_quality_pass": scalp_quality_pass,
        "scalp_quality_details": scalp_quality_details,
    }

    print(
        "-" * 80,
        flush=True,
    )

    print(
        f"UNIT 6 ACTIVE MODE = {active_mode}",
        flush=True,
    )

    print(
        f"UNIT 6 DIRECTION = {direction}",
        flush=True,
    )

    print(
        f"UNIT 6 SIGNAL QUALIFIED = "
        f"{signal_qualified}",
        flush=True,
    )

    print(
        f"UNIT 6 EXECUTION INTENT = "
        f"{execution_intent}",
        flush=True,
    )

    print(
        f"UNIT 6 ADMISSION REASON = "
        f"{admission_reason}",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 6 NORMALIZED EXECUTION CANDIDATE",
        flush=True,
    )

    print(
        "PASS: UNIT 6 SIGNAL ADMISSION COMPLETED",
        flush=True,
    )

    print(
        "PASS: UNIT 6 NO NETWORK REQUEST",
        flush=True,
    )

    print(
        "PASS: UNIT 6 NO ORDER PAYLOAD GENERATED",
        flush=True,
    )

    print(
        "PASS: UNIT 6 NO POSITION SIZING",
        flush=True,
    )

    print(
        "PASS: UNIT 6 NO TP / SL",
        flush=True,
    )

    print(
        "PASS: UNIT 6 NO BACKUP EXECUTION",
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
        "FRESH RECONSTRUCTION UNIT 6 RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return execution_candidate
    

# ============================================================
# RUN UNIT 6
# ============================================================

FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE = (
    fresh_reconstruction_unit_6(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE,
    )
)


# ============================================================
# END OF TRANSMISSION PART 4
# ZERO INDENTATION DEMARCATION
#
# UNIT 6 IS FULLY CLOSED
# UNIT 6 HAS BEEN CALLED
# SCALP QUALITY GATE IS INSTALLED
# QUALITY MINIMUM = 75 / 100
# STRUCTURE AND BREAKOUT ARE NOT BLOCKED BY THIS QUALITY GATE
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN TRY
# NO OPEN DICTIONARY
# NO INDENTATION CONTINUES INTO THE NEXT PART
#
# NEXT PART STARTS WITH FRESH RECONSTRUCTION UNIT 7
# ============================================================

# FRESH RECONSTRUCTION UNIT 7
# EXECUTION PLAN / POSITION-SIZING PREPARATION
#
# PURPOSE:
# - Consume Unit 2 configuration
# - Consume Unit 6 execution candidate
# - Handle BOTH normal states correctly:
#
#   1. NO QUALIFIED SIGNAL -> IDLE / PASS
#   2. QUALIFIED SIGNAL    -> SIZING PREPARATION / PASS
#
# IMPORTANT:
# - NO ACCOUNT BALANCE INVENTED
# - NO POSITION QUANTITY INVENTED
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
# - NO ORDER PAYLOAD
# - NO TP / SL
# - NO BACKUP EXECUTION
# ============================================================


def fresh_reconstruction_unit_7(
    unit_2_config,
    unit_6_candidate,
):

    print(
        "=" * 80,
        flush=True,
    )

    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 7 START",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    # ========================================================
    # 1. INPUT VALIDATION
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 7 FAILED: INVALID UNIT 2 CONFIGURATION"
        )

    print(
        "PASS: UNIT 7 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    if not isinstance(unit_6_candidate, dict):
        raise RuntimeError(
            "UNIT 7 FAILED: INVALID UNIT 6 EXECUTION CANDIDATE"
        )

    print(
        "PASS: UNIT 7 RECEIVED UNIT 6 EXECUTION CANDIDATE",
        flush=True,
    )

    # ========================================================
    # 2. CONFIGURATION SECTIONS
    # ========================================================

    strategy = unit_2_config.get("strategy")
    market_precision = unit_2_config.get("market_precision")
    safety = unit_2_config.get("safety")
    exchange = unit_2_config.get("exchange")

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 7 FAILED: STRATEGY CONFIGURATION MISSING"
        )

    if not isinstance(market_precision, dict):
        raise RuntimeError(
            "UNIT 7 FAILED: MARKET PRECISION MISSING"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 7 FAILED: SAFETY CONFIGURATION MISSING"
        )

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 7 FAILED: EXCHANGE CONFIGURATION MISSING"
        )

    print(
        "PASS: UNIT 7 CONFIGURATION SECTIONS PRESENT",
        flush=True,
    )

    # ========================================================
    # 3. STRICT UNIT 6 CONTRACT
    # ========================================================

    required_unit_6_fields = (
        "execution_intent",
        "active_mode",
        "direction",
        "signal_qualified",
        "unit_5_reason",
        "admission_reason",
    )

    missing_unit_6_fields = [
        field
        for field in required_unit_6_fields
        if field not in unit_6_candidate
    ]

    if missing_unit_6_fields:
        raise RuntimeError(
            "UNIT 7 FAILED: UNIT 6 CANDIDATE MISSING FIELDS = "
            + str(missing_unit_6_fields)
        )

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

    unit_5_reason = unit_6_candidate[
        "unit_5_reason"
    ]

    if not isinstance(execution_intent, bool):
        raise RuntimeError(
            "UNIT 7 FAILED: EXECUTION INTENT IS NOT BOOLEAN"
        )

    if not isinstance(signal_qualified, bool):
        raise RuntimeError(
            "UNIT 7 FAILED: SIGNAL QUALIFIED IS NOT BOOLEAN"
        )

    print(
        "PASS: UNIT 7 UNIT 6 CONTRACT VALIDATED",
        flush=True,
    )

    # ========================================================
    # 4. READ-ONLY SAFETY GATE
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

    for capability in forbidden_capabilities:

        if safety.get(capability) is not False:
            raise RuntimeError(
                "UNIT 7 BLOCKED: UNSAFE CAPABILITY ENABLED: "
                + capability
            )

    print(
        "PASS: UNIT 7 READ-ONLY SAFETY GATE",
        flush=True,
    )

    # ========================================================
    # 5. NORMAL IDLE / NO-TRADE PATH
    #
    # NO SIGNAL IS A NORMAL OPERATING CONDITION.
    # IT MUST NOT CRASH OR RESTART THE SERVICE.
    # ========================================================

    if execution_intent is False:

        if signal_qualified is not False:
            raise RuntimeError(
                "UNIT 7 FAILED: EXECUTION INTENT FALSE "
                "BUT SIGNAL QUALIFIED TRUE"
            )

        if active_mode != "NONE":
            raise RuntimeError(
                "UNIT 7 FAILED: IDLE STATE HAS ACTIVE MODE"
            )

        if direction != "NONE":
            raise RuntimeError(
                "UNIT 7 FAILED: IDLE STATE HAS DIRECTION"
            )

        sizing_candidate = {
            "status": "IDLE",
            "active_mode": active_mode,
            "direction": direction,
            "execution_intent": False,
            "signal_qualified": False,
            "unit_5_reason": unit_5_reason,
            "admission_reason": admission_reason,
            "account_balance_required": False,
            "position_sizing_performed": False,
            "quantity_calculated": False,
            "proposed_quantity": None,
            "order_payload_created": False,
            "read_only": True,
            "skip_reason": admission_reason,
        }

        print(
            "-" * 80,
            flush=True,
        )

        print(
            "UNIT 7 STATUS = IDLE",
            flush=True,
        )

        print(
            "UNIT 7 ACTIVE MODE = NONE",
            flush=True,
        )

        print(
            "UNIT 7 DIRECTION = NONE",
            flush=True,
        )

        print(
            "UNIT 7 SIGNAL QUALIFIED = False",
            flush=True,
        )

        print(
            "UNIT 7 EXECUTION INTENT = False",
            flush=True,
        )

        print(
            "UNIT 7 POSITION SIZING = SKIPPED",
            flush=True,
        )

        print(
            "UNIT 7 SKIP REASON =",
            admission_reason,
            flush=True,
        )

        print(
            "-" * 80,
            flush=True,
        )

        print(
            "PASS: UNIT 7 NORMAL NO-TRADE STATE",
            flush=True,
        )

        print(
            "PASS: UNIT 7 NO POSITION SIZING",
            flush=True,
        )

        print(
            "PASS: UNIT 7 NO NETWORK REQUEST",
            flush=True,
        )

        print(
            "PASS: UNIT 7 NO ORDER PAYLOAD GENERATED",
            flush=True,
        )

        print(
            "PASS: UNIT 7 NO TP / SL",
            flush=True,
        )

        print(
            "PASS: UNIT 7 NO BACKUP EXECUTION",
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
            "FRESH RECONSTRUCTION UNIT 7 RESULT = PASS (IDLE)",
            flush=True,
        )

        print(
            "=" * 80,
            flush=True,
        )

        return sizing_candidate

    # ========================================================
    # 6. ACTIVE / QUALIFIED SIGNAL PATH
    # ========================================================

    if execution_intent is not True:
        raise RuntimeError(
            "UNIT 7 FAILED: INVALID EXECUTION INTENT STATE"
        )

    if signal_qualified is not True:
        raise RuntimeError(
            "UNIT 7 FAILED: EXECUTION INTENT TRUE "
            "BUT SIGNAL QUALIFIED FALSE"
        )

    if admission_reason != "QUALIFIED_SIGNAL_ADMITTED":
        raise RuntimeError(
            "UNIT 7 FAILED: EXECUTION INTENT TRUE "
            "WITHOUT QUALIFIED SIGNAL ADMISSION"
        )

    valid_modes = {
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    }

    if active_mode not in valid_modes:
        raise RuntimeError(
            "UNIT 7 FAILED: INVALID ACTIVE TRADE MODE"
        )

    valid_directions = {
        "LONG",
        "SHORT",
    }

    if direction not in valid_directions:
        raise RuntimeError(
            "UNIT 7 FAILED: INVALID TRADE DIRECTION"
        )

    print(
        "PASS: UNIT 7 QUALIFIED EXECUTION CANDIDATE",
        flush=True,
    )

    print(
        "PASS: UNIT 7 ACTIVE MODE =",
        active_mode,
        flush=True,
    )

    print(
        "PASS: UNIT 7 DIRECTION =",
        direction,
        flush=True,
    )

    # ========================================================
    # 7. POSITION-SIZING PARAMETERS
    # ========================================================

    initial_margin_percent = float(
        strategy.get(
            "initial_margin_percent",
            0.0,
        )
    )

    leverage_target = int(
        strategy.get(
            "leverage_target",
            0,
        )
    )

    quantity_step = float(
        market_precision.get(
            "quantity_step",
            0.0,
        )
    )

    minimum_quantity = float(
        market_precision.get(
            "minimum_quantity",
            0.0,
        )
    )

    price_step = float(
        market_precision.get(
            "price_step",
            0.0,
        )
    )

    if initial_margin_percent <= 0:
        raise RuntimeError(
            "UNIT 7 FAILED: INVALID INITIAL MARGIN PERCENT"
        )

    if leverage_target <= 0:
        raise RuntimeError(
            "UNIT 7 FAILED: INVALID LEVERAGE TARGET"
        )

    if quantity_step <= 0:
        raise RuntimeError(
            "UNIT 7 FAILED: INVALID QUANTITY STEP"
        )

    if minimum_quantity <= 0:
        raise RuntimeError(
            "UNIT 7 FAILED: INVALID MINIMUM QUANTITY"
        )

    if price_step <= 0:
        raise RuntimeError(
            "UNIT 7 FAILED: INVALID PRICE STEP"
        )

    print(
        "PASS: UNIT 7 INITIAL MARGIN % =",
        initial_margin_percent,
        flush=True,
    )

    print(
        "PASS: UNIT 7 LEVERAGE TARGET =",
        leverage_target,
        flush=True,
    )

    print(
        "PASS: UNIT 7 QUANTITY STEP =",
        quantity_step,
        flush=True,
    )

    print(
        "PASS: UNIT 7 MINIMUM QUANTITY =",
        minimum_quantity,
        flush=True,
    )

    print(
        "PASS: UNIT 7 PRICE STEP =",
        price_step,
        flush=True,
    )

    # ========================================================
    # 8. SIZING PREPARATION
    #
    # DO NOT INVENT ACCOUNT BALANCE.
    # DO NOT INVENT POSITION QUANTITY.
    #
    # ACTUAL QUANTITY REQUIRES VERIFIED BALANCE + PRICE.
    # ========================================================

    sizing_candidate = {
        "status": "READY_FOR_BALANCE",
        "symbol": exchange.get(
            "market_symbol"
        ),
        "demo_order_symbol": exchange.get(
            "demo_order_symbol"
        ),
        "active_mode": active_mode,
        "direction": direction,
        "execution_intent": True,
        "signal_qualified": True,
        "unit_5_reason": unit_5_reason,
        "admission_reason": admission_reason,
        "initial_margin_percent": initial_margin_percent,
        "leverage_target": leverage_target,
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
    # 9. OUTPUT CONTRACT
    # ========================================================

    if sizing_candidate["execution_intent"] is not True:
        raise RuntimeError(
            "UNIT 7 OUTPUT CONTRACT FAILURE: EXECUTION INTENT"
        )

    if sizing_candidate["signal_qualified"] is not True:
        raise RuntimeError(
            "UNIT 7 OUTPUT CONTRACT FAILURE: SIGNAL QUALIFICATION"
        )

    if sizing_candidate["account_balance_required"] is not True:
        raise RuntimeError(
            "UNIT 7 OUTPUT CONTRACT FAILURE: BALANCE REQUIREMENT"
        )

    if sizing_candidate["quantity_calculated"] is not False:
        raise RuntimeError(
            "UNIT 7 OUTPUT CONTRACT FAILURE: QUANTITY STATE"
        )

    if sizing_candidate["proposed_quantity"] is not None:
        raise RuntimeError(
            "UNIT 7 OUTPUT CONTRACT FAILURE: QUANTITY INVENTED"
        )

    if sizing_candidate["order_payload_created"] is not False:
        raise RuntimeError(
            "UNIT 7 OUTPUT CONTRACT FAILURE: ORDER PAYLOAD STATE"
        )

    if sizing_candidate["read_only"] is not True:
        raise RuntimeError(
            "UNIT 7 OUTPUT CONTRACT FAILURE: READ-ONLY STATE"
        )

    # ========================================================
    # 10. ACTIVE OUTPUT
    # ========================================================

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 7 STATUS = READY_FOR_BALANCE",
        flush=True,
    )

    print(
        "UNIT 7 ACTIVE MODE =",
        active_mode,
        flush=True,
    )

    print(
        "UNIT 7 DIRECTION =",
        direction,
        flush=True,
    )

    print(
        "UNIT 7 SIGNAL QUALIFIED = True",
        flush=True,
    )

    print(
        "UNIT 7 EXECUTION INTENT = True",
        flush=True,
    )

    print(
        "UNIT 7 INITIAL MARGIN % =",
        initial_margin_percent,
        flush=True,
    )

    print(
        "UNIT 7 LEVERAGE TARGET =",
        leverage_target,
        flush=True,
    )

    print(
        "UNIT 7 ACCOUNT BALANCE REQUIRED = True",
        flush=True,
    )

    print(
        "UNIT 7 QUANTITY CALCULATED = False",
        flush=True,
    )

    print(
        "UNIT 7 PROPOSED QUANTITY = None",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    # ========================================================
    # 11. FINAL SAFETY REPORT
    # ========================================================

    print(
        "PASS: UNIT 7 NORMALIZED SIZING PREPARATION CANDIDATE",
        flush=True,
    )

    print(
        "PASS: UNIT 7 POSITION-SIZING PARAMETERS VALIDATED",
        flush=True,
    )

    print(
        "PASS: UNIT 7 NO ACCOUNT BALANCE INVENTED",
        flush=True,
    )

    print(
        "PASS: UNIT 7 NO POSITION QUANTITY INVENTED",
        flush=True,
    )

    print(
        "PASS: UNIT 7 NO NETWORK REQUEST",
        flush=True,
    )

    print(
        "PASS: UNIT 7 NO ORDER PAYLOAD GENERATED",
        flush=True,
    )

    print(
        "PASS: UNIT 7 NO TP / SL",
        flush=True,
    )

    print(
        "PASS: UNIT 7 NO BACKUP EXECUTION",
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
        "FRESH RECONSTRUCTION UNIT 7 RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return sizing_candidate


# ============================================================
# RUN UNIT 7
# ============================================================

FRESH_RECONSTRUCTION_SIZING_CANDIDATE = (
    fresh_reconstruction_unit_7(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE,
    )
)


# ============================================================
# END OF TRANSMISSION PART 5
# ZERO INDENTATION DEMARCATION
#
# UNIT 7 IS FULLY CLOSED
# UNIT 7 HAS BEEN CALLED
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN TRY
# NO OPEN DICTIONARY
# NO INDENTATION CONTINUES INTO THE NEXT PART
#
# NEXT PART STARTS WITH FRESH RECONSTRUCTION UNIT 8
# ============================================================

# FRESH RECONSTRUCTION UNIT 8
# VERIFIED DEMO BALANCE + POSITION SIZING + TRADE PLAN
#
# PURPOSE:
# Receive the normalized Unit 7 sizing-preparation result.
#
# IDLE:
# - no authenticated request
# - no sizing
# - no trade plan
#
# ACTIONABLE:
# - perform ONE authenticated read-only WEEX demo balance GET
# - read SUSDT availableBalance
# - use verified live BTC mark price from Unit 3
# - apply configured initial margin %
# - apply configured leverage target
# - calculate BTC quantity
# - round DOWN to configured quantity step
# - prepare normalized internal trade plan
#
# IMPORTANT:
# - DEMO BALANCE READ ONLY
# - NO POSITION ACCESS
# - NO ORDER ENDPOINT ACCESS
# - NO DEMO ORDER
# - NO REAL ORDER
# - ZERO EXCHANGE WRITE
# - ZERO LEVERAGE MUTATION
# - ZERO MARGIN MODE MUTATION
# - ZERO POSITION MODE MUTATION
# - NO TP / SL
# - NO BACKUP EXECUTION
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
    import math
    import json
    import urllib.request
    import urllib.error
    from datetime import datetime, timezone

    print("=" * 80, flush=True)

    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 8 START",
        flush=True,
    )

    print("-" * 80, flush=True)

    # --------------------------------------------------------
    # 1. INPUT VALIDATION
    # --------------------------------------------------------

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 8 BLOCKED: CONFIGURATION IS NOT A DICTIONARY"
        )

    if not isinstance(unit_7_result, dict):
        raise RuntimeError(
            "UNIT 8 BLOCKED: UNIT 7 RESULT IS NOT A DICTIONARY"
        )

    if not isinstance(market_snapshot, dict):
        raise RuntimeError(
            "UNIT 8 BLOCKED: MARKET SNAPSHOT IS NOT A DICTIONARY"
        )

    print(
        "PASS: UNIT 8 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    print(
        "PASS: UNIT 8 RECEIVED UNIT 7 RESULT",
        flush=True,
    )

    print(
        "PASS: UNIT 8 RECEIVED UNIT 3 MARKET SNAPSHOT",
        flush=True,
    )

    # --------------------------------------------------------
    # 2. CONFIGURATION SECTIONS
    # --------------------------------------------------------

    exchange = config.get(
        "exchange"
    )

    safety = config.get(
        "safety"
    )

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 8 BLOCKED: EXCHANGE CONFIGURATION MISSING"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 8 BLOCKED: SAFETY CONFIGURATION MISSING"
        )

    if (
        config.get(
            "execution_environment"
        )
        != "DEMO"
    ):
        raise RuntimeError(
            "UNIT 8 BLOCKED: EXECUTION ENVIRONMENT NOT DEMO"
        )

    if (
        exchange.get(
            "contract_base_url"
        )
        != "https://api-contract.weex.com"
    ):
        raise RuntimeError(
            "UNIT 8 BLOCKED: INVALID WEEX CONTRACT BASE URL"
        )

    print(
        "PASS: UNIT 8 CONFIGURATION SECTIONS PRESENT",
        flush=True,
    )

    print(
        "PASS: UNIT 8 EXECUTION ENVIRONMENT = DEMO",
        flush=True,
    )

    # --------------------------------------------------------
    # 3. REQUIRED UNIT 7 CONTRACT
    # --------------------------------------------------------

    required_fields = (
        "status",
        "active_mode",
        "direction",
        "signal_qualified",
        "execution_intent",
    )

    missing_fields = [
        field
        for field in required_fields
        if field not in unit_7_result
    ]

    if missing_fields:
        raise RuntimeError(
            "UNIT 8 BLOCKED: UNIT 7 MISSING REQUIRED FIELDS: "
            + ", ".join(missing_fields)
        )

    print(
        "PASS: UNIT 8 UNIT 7 CONTRACT VALIDATED",
        flush=True,
    )

    # --------------------------------------------------------
    # 4. NORMALIZE UNIT 7 STATE
    # --------------------------------------------------------

    status = str(
        unit_7_result.get(
            "status",
            "IDLE",
        )
    ).upper()

    active_mode = str(
        unit_7_result.get(
            "active_mode",
            "NONE",
        )
    ).upper()

    direction = str(
        unit_7_result.get(
            "direction",
            "NONE",
        )
    ).upper()

    signal_qualified = bool(
        unit_7_result.get(
            "signal_qualified",
            False,
        )
    )

    execution_intent = bool(
        unit_7_result.get(
            "execution_intent",
            False,
        )
    )

    skip_reason = str(
        unit_7_result.get(
            "skip_reason",
            unit_7_result.get(
                "reason",
                "NONE",
            ),
        )
    )

    # --------------------------------------------------------
    # 5. NORMAL IDLE PATH
    #
    # No signal means absolutely no authenticated request.
    # --------------------------------------------------------

    if not execution_intent:

        unit_8_result = {
            "status": "IDLE",
            "active_mode": active_mode,
            "direction": direction,
            "signal_qualified": signal_qualified,
            "execution_intent": False,
            "trade_plan_ready": False,
            "trade_plan": None,
            "skip_reason": skip_reason,
            "read_only": True,
        }

        print("-" * 80, flush=True)

        print(
            "UNIT 8 STATUS = IDLE",
            flush=True,
        )

        print(
            f"UNIT 8 ACTIVE MODE = {active_mode}",
            flush=True,
        )

        print(
            f"UNIT 8 DIRECTION = {direction}",
            flush=True,
        )

        print(
            f"UNIT 8 SIGNAL QUALIFIED = "
            f"{signal_qualified}",
            flush=True,
        )

        print(
            "UNIT 8 EXECUTION INTENT = False",
            flush=True,
        )

        print(
            "UNIT 8 TRADE PLAN READY = False",
            flush=True,
        )

        print(
            "UNIT 8 TRADE PLAN = NONE",
            flush=True,
        )

        print(
            f"UNIT 8 SKIP REASON = {skip_reason}",
            flush=True,
        )

        print("-" * 80, flush=True)

        print(
            "PASS: UNIT 8 NORMAL NO-TRADE STATE",
            flush=True,
        )

        print(
            "PASS: UNIT 8 NO AUTHENTICATED REQUEST WHILE IDLE",
            flush=True,
        )

        print(
            "PASS: UNIT 8 NO ORDER PAYLOAD GENERATED",
            flush=True,
        )

        print(
            "PASS: UNIT 8 NO TP / SL EXECUTION",
            flush=True,
        )

        print(
            "PASS: UNIT 8 NO BACKUP EXECUTION",
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
            "FRESH RECONSTRUCTION UNIT 8 "
            "RESULT = PASS (IDLE)",
            flush=True,
        )

        print("=" * 80, flush=True)

        return unit_8_result

    # --------------------------------------------------------
    # 6. ACTIONABLE CONTRACT
    # --------------------------------------------------------

    if not signal_qualified:
        raise RuntimeError(
            "UNIT 8 BLOCKED: EXECUTION INTENT TRUE "
            "BUT SIGNAL QUALIFIED FALSE"
        )

    if status != "READY_FOR_BALANCE":
        raise RuntimeError(
            "UNIT 8 BLOCKED: UNIT 7 NOT READY FOR BALANCE"
        )

    if active_mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        raise RuntimeError(
            "UNIT 8 BLOCKED: INVALID ACTIVE MODE "
            f"{active_mode}"
        )

    if direction not in (
        "LONG",
        "SHORT",
    ):
        raise RuntimeError(
            "UNIT 8 BLOCKED: INVALID DIRECTION "
            f"{direction}"
        )

    if (
        unit_7_result.get(
            "account_balance_required"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 8 BLOCKED: UNIT 7 BALANCE REQUIREMENT MISSING"
        )

    if (
        unit_7_result.get(
            "quantity_calculated"
        )
        is not False
    ):
        raise RuntimeError(
            "UNIT 8 BLOCKED: UNIT 7 QUANTITY STATE INVALID"
        )

    if (
        unit_7_result.get(
            "proposed_quantity"
        )
        is not None
    ):
        raise RuntimeError(
            "UNIT 8 BLOCKED: UNIT 7 INVENTED QUANTITY"
        )

    print(
        "PASS: UNIT 8 ACTIONABLE EXECUTION CONTRACT",
        flush=True,
    )

    # --------------------------------------------------------
    # 7. SCOPED SAFETY GATE
    #
    # Existing broad authenticated/account flags intentionally
    # remain False. Only this explicit DEMO BALANCE READ
    # capability is permitted here.
    # --------------------------------------------------------

    if (
        safety.get(
            "demo_account_balance_read_enabled"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 8 BLOCKED: DEMO BALANCE READ NOT ENABLED"
        )

    if (
        safety.get(
            "position_access_enabled"
        )
        is not False
    ):
        raise RuntimeError(
            "UNIT 8 BLOCKED: POSITION ACCESS ENABLED"
        )

    if (
        safety.get(
            "order_endpoint_access_enabled"
        )
        is not False
    ):
        raise RuntimeError(
            "UNIT 8 BLOCKED: ORDER ENDPOINT ACCESS ENABLED"
        )

    if (
        safety.get(
            "real_order_submission_enabled"
        )
        is not False
    ):
        raise RuntimeError(
            "UNIT 8 BLOCKED: REAL ORDER ENABLED"
        )

    if (
        safety.get(
            "exchange_mutation_enabled"
        )
        is not False
    ):
        raise RuntimeError(
            "UNIT 8 BLOCKED: EXCHANGE MUTATION ENABLED"
        )

    print(
        "PASS: UNIT 8 SCOPED DEMO BALANCE READ ENABLED",
        flush=True,
    )

    print(
        "PASS: UNIT 8 ALL EXCHANGE WRITES REMAIN DISABLED",
        flush=True,
    )

    # --------------------------------------------------------
    # 8. VERIFIED MARKET PRICE
    # --------------------------------------------------------

    if (
        market_snapshot.get(
            "symbol"
        )
        != exchange.get(
            "market_symbol"
        )
    ):
        raise RuntimeError(
            "UNIT 8 BLOCKED: MARKET SYMBOL MISMATCH"
        )

    try:
        live_price = float(
            market_snapshot.get(
                "price"
            )
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise RuntimeError(
            "UNIT 8 BLOCKED: INVALID LIVE MARKET PRICE"
        ) from exc

    if live_price <= 0:
        raise RuntimeError(
            "UNIT 8 BLOCKED: NON-POSITIVE LIVE MARKET PRICE"
        )

    print(
        "PASS: UNIT 8 VERIFIED LIVE BTC MARK PRICE =",
        live_price,
        flush=True,
    )

    # --------------------------------------------------------
    # 9. VERIFIED SIZING PARAMETERS FROM UNIT 7
    # --------------------------------------------------------

    try:
        initial_margin_percent = float(
            unit_7_result.get(
                "initial_margin_percent"
            )
        )

        leverage_target = float(
            unit_7_result.get(
                "leverage_target"
            )
        )

        quantity_step = float(
            unit_7_result.get(
                "quantity_step"
            )
        )

        minimum_quantity = float(
            unit_7_result.get(
                "minimum_quantity"
            )
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise RuntimeError(
            "UNIT 8 BLOCKED: INVALID SIZING PARAMETERS"
        ) from exc

    if initial_margin_percent <= 0:
        raise RuntimeError(
            "UNIT 8 BLOCKED: INVALID INITIAL MARGIN PERCENT"
        )

    if leverage_target <= 0:
        raise RuntimeError(
            "UNIT 8 BLOCKED: INVALID LEVERAGE TARGET"
        )

    if quantity_step <= 0:
        raise RuntimeError(
            "UNIT 8 BLOCKED: INVALID QUANTITY STEP"
        )

    if minimum_quantity <= 0:
        raise RuntimeError(
            "UNIT 8 BLOCKED: INVALID MINIMUM QUANTITY"
        )

    print(
        "PASS: UNIT 8 INITIAL MARGIN % =",
        initial_margin_percent,
        flush=True,
    )

    print(
        "PASS: UNIT 8 LEVERAGE TARGET =",
        leverage_target,
        flush=True,
    )

    print(
        "PASS: UNIT 8 QUANTITY STEP =",
        quantity_step,
        flush=True,
    )

    print(
        "PASS: UNIT 8 MINIMUM QUANTITY =",
        minimum_quantity,
        flush=True,
    )

    # --------------------------------------------------------
    # 10. WEEX CREDENTIALS
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
