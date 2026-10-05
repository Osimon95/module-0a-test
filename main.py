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
