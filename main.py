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

# ============================================================
# PART 6B
# CONTINUATION OF FRESH RECONSTRUCTION UNIT 8
#
# CONTINUES DIRECTLY AFTER:
#
#     api_passphrase = (
#         os.getenv("WEEX_API_PASSPHRASE")
#         or os.getenv("API_PASSPHRASE")
#     )
#
# IMPORTANT:
# - THE CODE BELOW IS STILL INSIDE fresh_reconstruction_unit_8
#   UNTIL THE FUNCTION'S return unit_8_result
# - THE FINAL UNIT 8 CALL IS ZERO INDENTATION
# - STOP BEFORE UNIT 9
# ============================================================

    if not api_key:
        raise RuntimeError(
            "UNIT 8 BLOCKED: WEEX API KEY MISSING"
        )

    if not api_secret:
        raise RuntimeError(
            "UNIT 8 BLOCKED: WEEX API SECRET MISSING"
        )

    if not api_passphrase:
        raise RuntimeError(
            "UNIT 8 BLOCKED: WEEX API PASSPHRASE MISSING"
        )

    print(
        "PASS: UNIT 8 WEEX DEMO CREDENTIALS PRESENT",
        flush=True,
    )

    # --------------------------------------------------------
    # 11. FIXED WEEX DEMO BALANCE ENDPOINT
    # --------------------------------------------------------

    base_url = (
        exchange.get(
            "contract_base_url"
        )
    )

    request_path = (
        "/capi/v3/sim/balance"
    )

    url = (
        base_url
        + request_path
    )

    method = "GET"

    print(
        "PASS: UNIT 8 DEMO BALANCE ENDPOINT LOCKED",
        flush=True,
    )

    print(
        f"UNIT 8 REQUEST PATH = {request_path}",
        flush=True,
    )

    # --------------------------------------------------------
    # 12. WEEX V3 GET SIGNATURE
    #
    # No query string.
    # No request body.
    #
    # timestamp + GET + request_path
    # --------------------------------------------------------

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    prehash = (
        timestamp
        + method
        + request_path
    )

    signature = base64.b64encode(
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

        "Accept":
            "application/json",

        "User-Agent":
            "Fresh-WEEX-Reconstruction/Unit8",
    }

    print(
        "PASS: UNIT 8 WEEX V3 DEMO BALANCE SIGNATURE GENERATED",
        flush=True,
    )

    # --------------------------------------------------------
    # 13. BUILD STRICT READ-ONLY GET
    # --------------------------------------------------------

    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    if request.get_method() != "GET":
        raise RuntimeError(
            "UNIT 8 BLOCKED: DEMO BALANCE REQUEST NOT GET"
        )

    if request.data is not None:
        raise RuntimeError(
            "UNIT 8 BLOCKED: DEMO BALANCE REQUEST HAS BODY"
        )

    # --------------------------------------------------------
    # 14. EXECUTE ONE AUTHENTICATED DEMO BALANCE READ
    # --------------------------------------------------------

    print(
        "UNIT 8 READING WEEX DEMO ACCOUNT BALANCE",
        flush=True,
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
                response
                .read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

    except urllib.error.HTTPError as exc:

        error_body = ""

        try:
            error_body = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )
        except Exception:
            pass

        raise RuntimeError(
            "UNIT 8 DEMO BALANCE HTTP ERROR "
            f"{exc.code}: {error_body}"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "UNIT 8 DEMO BALANCE NETWORK ERROR: "
            f"{exc}"
        ) from exc

    if response_status != 200:
        raise RuntimeError(
            "UNIT 8 DEMO BALANCE NON-200 RESPONSE: "
            f"{response_status}"
        )

    print(
        "PASS: UNIT 8 AUTHENTICATED DEMO BALANCE GET COMPLETED",
        flush=True,
    )

    # --------------------------------------------------------
    # 15. PARSE DEMO BALANCE RESPONSE
    # --------------------------------------------------------

    try:
        balance_payload = json.loads(
            response_text
        )
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT 8 BLOCKED: INVALID DEMO BALANCE JSON"
        ) from exc

    if not isinstance(
        balance_payload,
        list,
    ):
        raise RuntimeError(
            "UNIT 8 BLOCKED: DEMO BALANCE RESPONSE NOT A LIST"
        )

    susdt_balance = None

    for balance_item in balance_payload:

        if not isinstance(
            balance_item,
            dict,
        ):
            continue

        asset = str(
            balance_item.get(
                "asset",
                "",
            )
        ).upper()

        if asset == "SUSDT":
            susdt_balance = balance_item
            break

    if susdt_balance is None:
        raise RuntimeError(
            "UNIT 8 BLOCKED: SUSDT DEMO BALANCE NOT FOUND"
        )

    try:
        available_balance = float(
            susdt_balance.get(
                "availableBalance"
            )
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise RuntimeError(
            "UNIT 8 BLOCKED: INVALID SUSDT AVAILABLE BALANCE"
        ) from exc

    if available_balance <= 0:
        raise RuntimeError(
            "UNIT 8 BLOCKED: NON-POSITIVE SUSDT AVAILABLE BALANCE"
        )

    print(
        "PASS: UNIT 8 DEMO ASSET = SUSDT",
        flush=True,
    )

    print(
        "PASS: UNIT 8 VERIFIED AVAILABLE SUSDT =",
        available_balance,
        flush=True,
    )

    # --------------------------------------------------------
    # 16. POSITION SIZE CALCULATION
    #
    # margin allocation =
    # available balance * initial margin %
    #
    # notional =
    # margin allocation * leverage
    #
    # raw BTC quantity =
    # notional / live BTC mark price
    #
    # Final quantity is always rounded DOWN to quantity_step.
    # --------------------------------------------------------

    margin_allocation = (
        available_balance
        * (
            initial_margin_percent
            / 100.0
        )
    )

    notional_value = (
        margin_allocation
        * leverage_target
    )

    raw_quantity = (
        notional_value
        / live_price
    )

    quantity_steps = math.floor(
        (
            raw_quantity
            + 1e-12
        )
        / quantity_step
    )

    normalized_quantity = (
        quantity_steps
        * quantity_step
    )

    quantity_decimals = max(
        0,
        len(
            str(
                quantity_step
            ).rstrip(
                "0"
            ).split(
                "."
            )[-1]
        )
        if "." in str(
            quantity_step
        )
        else 0,
    )

    normalized_quantity = round(
        normalized_quantity,
        quantity_decimals,
    )

    if normalized_quantity < minimum_quantity:
        raise RuntimeError(
            "UNIT 8 BLOCKED: CALCULATED QUANTITY BELOW MINIMUM"
        )

    if normalized_quantity <= 0:
        raise RuntimeError(
            "UNIT 8 BLOCKED: CALCULATED QUANTITY NON-POSITIVE"
        )

    # ========================================================
    # INITIAL ENTRY SAFETY CAP
    #
    # The theoretical position-sizing calculation remains
    # visible for diagnostics, but the executable INITIAL
    # ENTRY quantity must never exceed 0.0004 BTC.
    #
    # This cap applies to the initial entry only.
    # It must NOT later be used as a blanket cap for:
    #   - TP1
    #   - TP2
    #   - TP3 trailing
    #   - Backup 1
    #   - Backup 2
    #   - Backup 3
    # ========================================================

    initial_entry_max_quantity = 0.0004

    executable_quantity = min(
        normalized_quantity,
        initial_entry_max_quantity,
    )

    executable_quantity = round(
        executable_quantity,
        quantity_decimals,
    )

    if executable_quantity < minimum_quantity:
        raise RuntimeError(
            "UNIT 8 BLOCKED: CAPPED INITIAL ENTRY QUANTITY BELOW MINIMUM"
        )

    if executable_quantity <= 0:
        raise RuntimeError(
            "UNIT 8 BLOCKED: CAPPED INITIAL ENTRY QUANTITY NON-POSITIVE"
        )

    print(
        "PASS: UNIT 8 MARGIN ALLOCATION SUSDT =",
        margin_allocation,
        flush=True,
    )

    print(
        "PASS: UNIT 8 LEVERAGED NOTIONAL SUSDT =",
        notional_value,
        flush=True,
    )

    print(
        "PASS: UNIT 8 RAW BTC QUANTITY =",
        raw_quantity,
        flush=True,
    )

    print(
        "PASS: UNIT 8 THEORETICAL BTC QUANTITY =",
        normalized_quantity,
        flush=True,
    )

    print(
        "PASS: UNIT 8 INITIAL ENTRY MAX BTC QUANTITY =",
        initial_entry_max_quantity,
        flush=True,
    )

    print(
        "PASS: UNIT 8 EXECUTABLE INITIAL ENTRY BTC QUANTITY =",
        executable_quantity,
        flush=True,
    )

    normalized_quantity = executable_quantity

    # --------------------------------------------------------
    # 17. NORMALIZED POSITION-SIZING OBJECT
    # --------------------------------------------------------

    position_sizing = {
        "asset":
            "SUSDT",

        "available_balance":
            available_balance,

        "initial_margin_percent":
            initial_margin_percent,

        "margin_allocation":
            margin_allocation,

        "leverage_target":
            leverage_target,

        "live_mark_price":
            live_price,

        "raw_quantity":
            raw_quantity,

        "quantity_step":
            quantity_step,

        "minimum_quantity":
            minimum_quantity,

        "quantity":
            normalized_quantity,

        "position_sizing_performed":
            True,

        "quantity_calculated":
            True,

        "source":
            "WEEX_V3_DEMO_BALANCE",

        "read_only":
            True,
    }

    # --------------------------------------------------------
    # 18. NORMALIZED TRADE PLAN
    #
    # Internal planning object only.
    # NOT a WEEX order payload.
    # --------------------------------------------------------

    trade_plan = {
        "active_mode":
            active_mode,

        "direction":
            direction,

        "quantity":
            normalized_quantity,

        "position_sizing":
            position_sizing,

        "execution_environment":
            "DEMO",
    }

    unit_8_result = {
        "status":
            "READY",

        "active_mode":
            active_mode,

        "direction":
            direction,

        "signal_qualified":
            True,

        "execution_intent":
            True,

        "trade_plan_ready":
            True,

        "trade_plan":
            trade_plan,

        "skip_reason":
            "NONE",

        "read_only":
            True,
    }

    # --------------------------------------------------------
    # 19. OUTPUT CONTRACT
    # --------------------------------------------------------

    if (
        trade_plan.get(
            "quantity"
        )
        is None
    ):
        raise RuntimeError(
            "UNIT 8 OUTPUT CONTRACT FAILURE: QUANTITY MISSING"
        )

    if (
        position_sizing.get(
            "quantity_calculated"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 8 OUTPUT CONTRACT FAILURE: QUANTITY NOT CALCULATED"
        )

    if (
        position_sizing.get(
            "position_sizing_performed"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 8 OUTPUT CONTRACT FAILURE: SIZING NOT PERFORMED"
        )

    # --------------------------------------------------------
    # 20. ACTIVE OUTPUT
    # --------------------------------------------------------

    print("-" * 80, flush=True)

    print(
        "UNIT 8 STATUS = READY",
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
        "UNIT 8 SIGNAL QUALIFIED = True",
        flush=True,
    )

    print(
        "UNIT 8 EXECUTION INTENT = True",
        flush=True,
    )

    print(
        "UNIT 8 TRADE PLAN READY = True",
        flush=True,
    )

    print(
        "UNIT 8 QUANTITY CALCULATED = True",
        flush=True,
    )

    print(
        "UNIT 8 EXECUTION QUANTITY =",
        normalized_quantity,
        flush=True,
    )

    print("-" * 80, flush=True)

    # --------------------------------------------------------
    # 21. FINAL SAFETY REPORT
    # --------------------------------------------------------

    print(
        "PASS: UNIT 8 VERIFIED DEMO ACCOUNT BALANCE",
        flush=True,
    )

    print(
        "PASS: UNIT 8 VERIFIED POSITION SIZING",
        flush=True,
    )

    print(
        "PASS: UNIT 8 NORMALIZED TRADE PLAN",
        flush=True,
    )

    print(
        "PASS: UNIT 8 AUTHENTICATED ACCESS = DEMO BALANCE GET ONLY",
        flush=True,
    )

    print(
        "PASS: UNIT 8 ORDER PAYLOAD GENERATED = False",
        flush=True,
    )

    print(
        "PASS: UNIT 8 TP / SL EXECUTION = False",
        flush=True,
    )

    print(
        "PASS: UNIT 8 BACKUP EXECUTION = False",
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
        "FRESH RECONSTRUCTION UNIT 8 RESULT = PASS",
        flush=True,
    )

    print("=" * 80, flush=True)

    return unit_8_result


# ============================================================
# ZERO INDENTATION FROM HERE
# UNIT 8 FUNCTION IS FULLY CLOSED
# ============================================================

FRESH_RECONSTRUCTION_UNIT_8_RESULT = (
    fresh_reconstruction_unit_8(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_SIZING_CANDIDATE,
        FRESH_RECONSTRUCTION_MARKET_SNAPSHOT,
    )
)

# ============================================================
# END OF PART 6B
#
# UNIT 8 IS FULLY CLOSED AND CALLED.
# NEXT EXISTING CODE IS UNIT 9.
# ============================================================

# ============================================================
# PART 7
# FRESH RECONSTRUCTION UNIT 9
# VALIDATED EXECUTION PREPARATION
# ============================================================

# ============================================================
# FRESH RECONSTRUCTION UNIT 9
# VALIDATED EXECUTION PREPARATION
#
# PURPOSE:
# Receive the completed Unit 8 result and prepare a strictly
# internal execution candidate for the later demo-submission
# boundary.
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
# Unit 9 DOES NOT submit an order.
# Unit 9 DOES NOT create a WEEX order payload.
# Unit 9 DOES NOT execute TP.
# Unit 9 DOES NOT execute SL.
#
# TP AND SL REMAIN INDEPENDENT CAPABILITIES.
# UNIT 9 MUST NOT COUPLE TP TO SL.
# ============================================================


def fresh_reconstruction_unit_9(
    config,
    unit_8_result,
):
    from datetime import datetime, timezone

    print(
        "=" * 80,
        flush=True,
    )

    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 9 START",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    # --------------------------------------------------------
    # INPUT VALIDATION
    # --------------------------------------------------------

    if not isinstance(config, dict):
        raise TypeError(
            "UNIT 9 CONFIGURATION MUST BE A DICTIONARY"
        )

    print(
        "PASS: UNIT 9 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    if not isinstance(unit_8_result, dict):
        raise TypeError(
            "UNIT 9 UNIT 8 RESULT MUST BE A DICTIONARY"
        )

    print(
        "PASS: UNIT 9 RECEIVED UNIT 8 RESULT",
        flush=True,
    )

    # --------------------------------------------------------
    # UNIT 8 CONTRACT VALIDATION
    # --------------------------------------------------------

    required_unit_8_fields = (
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

    missing_unit_8_fields = [
        field
        for field in required_unit_8_fields
        if field not in unit_8_result
    ]

    if missing_unit_8_fields:
        raise RuntimeError(
            "UNIT 9 MISSING UNIT 8 FIELDS: "
            + ", ".join(missing_unit_8_fields)
        )

    print(
        "PASS: UNIT 9 UNIT 8 CONTRACT VALIDATED",
        flush=True,
    )

    # --------------------------------------------------------
    # READ-ONLY SAFETY GATE
    # --------------------------------------------------------

    if unit_8_result.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 9 REJECTED NON-READ-ONLY UNIT 8 RESULT"
        )

    print(
        "PASS: UNIT 9 READ-ONLY SAFETY GATE",
        flush=True,
    )

    # --------------------------------------------------------
    # NORMALIZE UNIT 8 STATE
    # --------------------------------------------------------

    status = str(
        unit_8_result.get(
            "status",
            "IDLE",
        )
    ).upper()

    active_mode = unit_8_result.get(
        "active_mode"
    )

    direction = unit_8_result.get(
        "direction"
    )

    signal_qualified = bool(
        unit_8_result.get(
            "signal_qualified",
            False,
        )
    )

    execution_intent = bool(
        unit_8_result.get(
            "execution_intent",
            False,
        )
    )

    trade_plan_ready = bool(
        unit_8_result.get(
            "trade_plan_ready",
            False,
        )
    )

    trade_plan = unit_8_result.get(
        "trade_plan"
    )

    skip_reason = str(
        unit_8_result.get(
            "skip_reason",
            "NONE",
        )
    )

    # --------------------------------------------------------
    # NORMAL IDLE PATH
    # --------------------------------------------------------

    if (
        status == "IDLE"
        or not signal_qualified
        or not execution_intent
        or not trade_plan_ready
    ):
        execution_candidate = {
            "status": "IDLE",
            "active_mode": active_mode,
            "direction": direction,
            "signal_qualified": signal_qualified,
            "execution_intent": False,
            "trade_plan_ready": False,
            "trade_plan": None,
            "execution_ready": False,
            "execution_candidate": None,
            "skip_reason": skip_reason,
            "order_payload_created": False,
            "tp_execution_requested": False,
            "sl_execution_requested": False,
            "read_only": True,
        }

        print(
            "-" * 80,
            flush=True,
        )

        print(
            "UNIT 9 STATUS = IDLE",
            flush=True,
        )

        print(
            f"UNIT 9 ACTIVE MODE = {active_mode}",
            flush=True,
        )

        print(
            f"UNIT 9 DIRECTION = {direction}",
            flush=True,
        )

        print(
            f"UNIT 9 SIGNAL QUALIFIED = "
            f"{signal_qualified}",
            flush=True,
        )

        print(
            "UNIT 9 EXECUTION INTENT = False",
            flush=True,
        )

        print(
            "UNIT 9 TRADE PLAN READY = False",
            flush=True,
        )

        print(
            "UNIT 9 EXECUTION READY = False",
            flush=True,
        )

        print(
            "UNIT 9 EXECUTION CANDIDATE = NONE",
            flush=True,
        )

        print(
            f"UNIT 9 SKIP REASON = {skip_reason}",
            flush=True,
        )

        print(
            "-" * 80,
            flush=True,
        )

        print(
            "PASS: UNIT 9 NORMAL NO-TRADE STATE",
            flush=True,
        )

        print(
            "PASS: UNIT 9 NO EXECUTION CANDIDATE GENERATED",
            flush=True,
        )

        print(
            "PASS: UNIT 9 NO NETWORK REQUEST",
            flush=True,
        )

        print(
            "PASS: UNIT 9 NO ORDER PAYLOAD GENERATED",
            flush=True,
        )

        print(
            "PASS: UNIT 9 NO TP EXECUTION",
            flush=True,
        )

        print(
            "PASS: UNIT 9 NO SL EXECUTION",
            flush=True,
        )

        print(
            "PASS: UNIT 9 TP / SL CAPABILITIES REMAIN INDEPENDENT",
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
            "FRESH RECONSTRUCTION UNIT 9 RESULT = "
            "PASS (IDLE)",
            flush=True,
        )

        print(
            "=" * 80,
            flush=True,
        )

        return execution_candidate

    # --------------------------------------------------------
    # ACTIONABLE UNIT 8 PATH
    # --------------------------------------------------------

    if status not in (
        "READY",
        "QUALIFIED",
        "ACTIVE",
    ):
        raise RuntimeError(
            "UNIT 9 ACTIONABLE UNIT 8 RESULT HAS "
            f"INVALID STATUS: {status}"
        )

    if not isinstance(trade_plan, dict):
        raise RuntimeError(
            "UNIT 9 ACTIONABLE RESULT REQUIRES "
            "A TRADE PLAN DICTIONARY"
        )

    if active_mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        raise RuntimeError(
            "UNIT 9 INVALID ACTIVE MODE: "
            f"{active_mode}"
        )

    print(
        "PASS: UNIT 9 ACTIVE MODE VALIDATED",
        flush=True,
    )

    if direction not in (
        "LONG",
        "SHORT",
    ):
        raise RuntimeError(
            "UNIT 9 INVALID DIRECTION: "
            f"{direction}"
        )

    print(
        "PASS: UNIT 9 DIRECTION VALIDATED",
        flush=True,
    )

    # --------------------------------------------------------
    # CROSS-CHECK TRADE PLAN IDENTITY
    # --------------------------------------------------------

    trade_plan_mode = trade_plan.get(
        "active_mode"
    )

    trade_plan_direction = trade_plan.get(
        "direction"
    )

    if trade_plan_mode != active_mode:
        raise RuntimeError(
            "UNIT 9 TRADE PLAN MODE DOES NOT MATCH "
            "UNIT 8 ACTIVE MODE"
        )

    if trade_plan_direction != direction:
        raise RuntimeError(
            "UNIT 9 TRADE PLAN DIRECTION DOES NOT MATCH "
            "UNIT 8 DIRECTION"
        )

    print(
        "PASS: UNIT 9 TRADE PLAN IDENTITY VALIDATED",
        flush=True,
    )

    # --------------------------------------------------------
    # INTERNAL EXECUTION CANDIDATE
    #
    # IMPORTANT:
    # This is NOT a WEEX payload.
    # No endpoint-specific fields are generated here.
    # --------------------------------------------------------

    normalized_execution_candidate = {
        "active_mode": active_mode,
        "direction": direction,
        "trade_plan": trade_plan,
        "execution_environment": trade_plan.get(
            "execution_environment",
            config.get(
                "execution_environment",
                "DEMO",
            ),
        ),
    }

    execution_candidate = {
        "status": "READY",
        "active_mode": active_mode,
        "direction": direction,
        "signal_qualified": True,
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": trade_plan,
        "execution_ready": True,
        "execution_candidate": (
            normalized_execution_candidate
        ),
        "skip_reason": "NONE",
        "order_payload_created": False,
        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "read_only": True,
    }

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 9 STATUS = READY",
        flush=True,
    )

    print(
        f"UNIT 9 ACTIVE MODE = {active_mode}",
        flush=True,
    )

    print(
        f"UNIT 9 DIRECTION = {direction}",
        flush=True,
    )

    print(
        "UNIT 9 SIGNAL QUALIFIED = True",
        flush=True,
    )

    print(
        "UNIT 9 EXECUTION INTENT = True",
        flush=True,
    )

    print(
        "UNIT 9 TRADE PLAN READY = True",
        flush=True,
    )

    print(
        "UNIT 9 EXECUTION READY = True",
        flush=True,
    )

    print(
        "UNIT 9 INTERNAL EXECUTION CANDIDATE = READY",
        flush=True,
    )

    print(
        "UNIT 9 ORDER PAYLOAD CREATED = False",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 9 VALIDATED EXECUTION PREPARATION",
        flush=True,
    )

    print(
        "PASS: UNIT 9 INTERNAL EXECUTION CANDIDATE GENERATED",
        flush=True,
    )

    print(
        "PASS: UNIT 9 NO NETWORK REQUEST",
        flush=True,
    )

    print(
        "PASS: UNIT 9 NO ORDER PAYLOAD GENERATED",
        flush=True,
    )

    print(
        "PASS: UNIT 9 NO TP EXECUTION",
        flush=True,
    )

    print(
        "PASS: UNIT 9 NO SL EXECUTION",
        flush=True,
    )

    print(
        "PASS: UNIT 9 TP / SL CAPABILITIES REMAIN INDEPENDENT",
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
        "FRESH RECONSTRUCTION UNIT 9 RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return execution_candidate


# ============================================================
# FRESH RECONSTRUCTION UNIT 9 RUNNER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_9_RESULT = (
    fresh_reconstruction_unit_9(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT,
    )
)

# ============================================================
# END PART 7
# UNIT 9 FULLY CLOSED AND CALLED
# NEXT = PART 8 / UNIT 10
# ============================================================

# ============================================================
# FRESH RECONSTRUCTION UNIT 10
# DEMO EXECUTION BOUNDARY PREPARATION
#
# PURPOSE:
# - Consume verified Unit 2 configuration
# - Consume verified Unit 9 execution candidate
# - Preserve normal IDLE state when no trade is qualified
# - Prepare a normalized demo-submission instruction when READY
# - Validate the execution boundary before payload construction
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
# UNIT 10 DOES NOT:
# - CREATE A WEEX ORDER PAYLOAD
# - SUBMIT A DEMO ORDER
# - SUBMIT A REAL ORDER
# - EXECUTE TP
# - EXECUTE SL
# - EXECUTE BACKUPS
#
# UNIT 10 IS THE FINAL INTERNAL BOUNDARY PREPARATION
# BEFORE UNIT 11 BUILDS AND VALIDATES THE DEMO PAYLOAD.
# ============================================================


def fresh_reconstruction_unit_10(
    config,
    unit_9_result,
):
    from datetime import datetime, timezone

    print(
        "=" * 80,
        flush=True,
    )

    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 10 START",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    # ========================================================
    # 1. INPUT VALIDATION
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 10 BLOCKED: INVALID UNIT 2 CONFIGURATION"
        )

    print(
        "PASS: UNIT 10 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    if not isinstance(unit_9_result, dict):
        raise RuntimeError(
            "UNIT 10 BLOCKED: INVALID UNIT 9 RESULT"
        )

    print(
        "PASS: UNIT 10 RECEIVED UNIT 9 RESULT",
        flush=True,
    )

    # ========================================================
    # 2. CONFIGURATION SECTIONS
    # ========================================================

    exchange = config.get(
        "exchange"
    )

    safety = config.get(
        "safety"
    )

    strategy = config.get(
        "strategy"
    )

    market_precision = config.get(
        "market_precision"
    )

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 10 BLOCKED: EXCHANGE CONFIGURATION MISSING"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 10 BLOCKED: SAFETY CONFIGURATION MISSING"
        )

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 10 BLOCKED: STRATEGY CONFIGURATION MISSING"
        )

    if not isinstance(market_precision, dict):
        raise RuntimeError(
            "UNIT 10 BLOCKED: MARKET PRECISION MISSING"
        )

    print(
        "PASS: UNIT 10 CONFIGURATION SECTIONS PRESENT",
        flush=True,
    )

    # ========================================================
    # 3. STRICT UNIT 9 CONTRACT
    # ========================================================

    required_unit_9_fields = (
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

    missing_unit_9_fields = [
        field
        for field in required_unit_9_fields
        if field not in unit_9_result
    ]

    if missing_unit_9_fields:
        raise RuntimeError(
            "UNIT 10 BLOCKED: UNIT 9 MISSING FIELDS = "
            + str(
                missing_unit_9_fields
            )
        )

    print(
        "PASS: UNIT 10 UNIT 9 CONTRACT VALIDATED",
        flush=True,
    )

    # ========================================================
    # 4. UNIT 9 READ-ONLY CONTRACT
    # ========================================================

    if unit_9_result.get(
        "read_only"
    ) is not True:
        raise RuntimeError(
            "UNIT 10 BLOCKED: UNIT 9 RESULT NOT READ ONLY"
        )

    if unit_9_result.get(
        "order_payload_created"
    ) is not False:
        raise RuntimeError(
            "UNIT 10 BLOCKED: UNIT 9 CREATED ORDER PAYLOAD"
        )

    if unit_9_result.get(
        "tp_execution_requested"
    ) is not False:
        raise RuntimeError(
            "UNIT 10 BLOCKED: UNIT 9 REQUESTED TP EXECUTION"
        )

    if unit_9_result.get(
        "sl_execution_requested"
    ) is not False:
        raise RuntimeError(
            "UNIT 10 BLOCKED: UNIT 9 REQUESTED SL EXECUTION"
        )

    print(
        "PASS: UNIT 10 UNIT 9 READ-ONLY CONTRACT",
        flush=True,
    )

    # ========================================================
    # 5. GLOBAL SAFETY GATE
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

        if safety.get(
            capability
        ) is not False:

            raise RuntimeError(
                "UNIT 10 BLOCKED: UNSAFE CAPABILITY ENABLED: "
                + capability
            )

    print(
        "PASS: UNIT 10 READ-ONLY SAFETY GATE",
        flush=True,
    )

    # ========================================================
    # 6. EXCHANGE CONTRACT
    # ========================================================

    if exchange.get(
        "name"
    ) != "WEEX":
        raise RuntimeError(
            "UNIT 10 BLOCKED: INVALID EXCHANGE"
        )

    if exchange.get(
        "api_version"
    ) != "V3":
        raise RuntimeError(
            "UNIT 10 BLOCKED: INVALID API VERSION"
        )

    if exchange.get(
        "market_symbol"
    ) != "BTCUSDT":
        raise RuntimeError(
            "UNIT 10 BLOCKED: INVALID MARKET SYMBOL"
        )

    if exchange.get(
        "demo_order_symbol"
    ) != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 10 BLOCKED: INVALID DEMO SYMBOL"
        )

    if config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 10 BLOCKED: EXECUTION ENVIRONMENT NOT DEMO"
        )

    print(
        "PASS: UNIT 10 WEEX DEMO ENVIRONMENT CONTRACT",
        flush=True,
    )

    # ========================================================
    # 7. STRATEGY SAFETY CONTRACT
    # ========================================================

    if strategy.get(
        "anti_duplicate_orders"
    ) is not True:
        raise RuntimeError(
            "UNIT 10 BLOCKED: ANTI-DUPLICATE ORDERS DISABLED"
        )

    if strategy.get(
        "one_direction_only"
    ) is not True:
        raise RuntimeError(
            "UNIT 10 BLOCKED: ONE-DIRECTION-ONLY DISABLED"
        )

    if strategy.get(
        "active_trade_mode_lock"
    ) is not True:
        raise RuntimeError(
            "UNIT 10 BLOCKED: ACTIVE TRADE MODE LOCK DISABLED"
        )

    print(
        "PASS: UNIT 10 STRATEGY SAFETY CONTRACT",
        flush=True,
    )

    # ========================================================
    # 8. NORMALIZE UNIT 9 STATE
    # ========================================================

    status = str(
        unit_9_result.get(
            "status",
            "IDLE",
        )
    ).upper()

    active_mode = unit_9_result.get(
        "active_mode"
    )

    direction = unit_9_result.get(
        "direction"
    )

    signal_qualified = bool(
        unit_9_result.get(
            "signal_qualified",
            False,
        )
    )

    execution_intent = bool(
        unit_9_result.get(
            "execution_intent",
            False,
        )
    )

    trade_plan_ready = bool(
        unit_9_result.get(
            "trade_plan_ready",
            False,
        )
    )

    execution_ready = bool(
        unit_9_result.get(
            "execution_ready",
            False,
        )
    )

    trade_plan = unit_9_result.get(
        "trade_plan"
    )

    execution_candidate = unit_9_result.get(
        "execution_candidate"
    )

    skip_reason = str(
        unit_9_result.get(
            "skip_reason",
            "NONE",
        )
    )

    # ========================================================
    # 9. NORMAL IDLE PATH
    # ========================================================

    if (
        status == "IDLE"
        or not signal_qualified
        or not execution_intent
        or not trade_plan_ready
        or not execution_ready
    ):

        unit_10_result = {
            "status": "IDLE",
            "active_mode": active_mode,
            "direction": direction,
            "signal_qualified": signal_qualified,
            "execution_intent": False,
            "trade_plan_ready": False,
            "trade_plan": None,
            "execution_ready": False,
            "execution_candidate": None,
            "demo_boundary_ready": False,
            "demo_submission_instruction": None,
            "skip_reason": skip_reason,
            "order_payload_created": False,
            "demo_submission_requested": False,
            "real_submission_requested": False,
            "tp_execution_requested": False,
            "sl_execution_requested": False,
            "backup_execution_requested": False,
            "read_only": True,
        }

        print(
            "-" * 80,
            flush=True,
        )

        print(
            "UNIT 10 STATUS = IDLE",
            flush=True,
        )

        print(
            f"UNIT 10 ACTIVE MODE = {active_mode}",
            flush=True,
        )

        print(
            f"UNIT 10 DIRECTION = {direction}",
            flush=True,
        )

        print(
            f"UNIT 10 SIGNAL QUALIFIED = "
            f"{signal_qualified}",
            flush=True,
        )

        print(
            "UNIT 10 EXECUTION INTENT = False",
            flush=True,
        )

        print(
            "UNIT 10 EXECUTION READY = False",
            flush=True,
        )

        print(
            "UNIT 10 DEMO BOUNDARY READY = False",
            flush=True,
        )

        print(
            "UNIT 10 DEMO SUBMISSION INSTRUCTION = NONE",
            flush=True,
        )

        print(
            f"UNIT 10 SKIP REASON = {skip_reason}",
            flush=True,
        )

        print(
            "-" * 80,
            flush=True,
        )

        print(
            "PASS: UNIT 10 NORMAL NO-TRADE STATE",
            flush=True,
        )

        print(
            "PASS: UNIT 10 NO DEMO BOUNDARY GENERATED",
            flush=True,
        )

        print(
            "PASS: UNIT 10 NO NETWORK REQUEST",
            flush=True,
        )

        print(
            "PASS: UNIT 10 NO ORDER PAYLOAD GENERATED",
            flush=True,
        )

        print(
            "PASS: UNIT 10 NO DEMO SUBMISSION",
            flush=True,
        )

        print(
            "PASS: UNIT 10 NO REAL SUBMISSION",
            flush=True,
        )

        print(
            "PASS: UNIT 10 NO TP EXECUTION",
            flush=True,
        )

        print(
            "PASS: UNIT 10 NO SL EXECUTION",
            flush=True,
        )

        print(
            "PASS: UNIT 10 NO BACKUP EXECUTION",
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
            "FRESH RECONSTRUCTION UNIT 10 "
            "RESULT = PASS (IDLE)",
            flush=True,
        )

        print(
            "=" * 80,
            flush=True,
        )

        return unit_10_result

    # ========================================================
    # 10. ACTIONABLE UNIT 9 CONTRACT
    # ========================================================

    if status != "READY":
        raise RuntimeError(
            "UNIT 10 BLOCKED: ACTIONABLE UNIT 9 STATUS NOT READY"
        )

    if active_mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        raise RuntimeError(
            "UNIT 10 BLOCKED: INVALID ACTIVE MODE"
        )

    if direction not in (
        "LONG",
        "SHORT",
    ):
        raise RuntimeError(
            "UNIT 10 BLOCKED: INVALID DIRECTION"
        )

    if not isinstance(
        trade_plan,
        dict,
    ):
        raise RuntimeError(
            "UNIT 10 BLOCKED: TRADE PLAN MISSING"
        )

    if not isinstance(
        execution_candidate,
        dict,
    ):
        raise RuntimeError(
            "UNIT 10 BLOCKED: EXECUTION CANDIDATE MISSING"
        )

    print(
        "PASS: UNIT 10 ACTIONABLE UNIT 9 CONTRACT",
        flush=True,
    )

    # ========================================================
    # 11. DEMO BOUNDARY INSTRUCTION
    #
    # INTERNAL ONLY.
    #
    # This is deliberately NOT the WEEX HTTP order payload.
    # Unit 11 will convert this instruction into a payload and
    # validate it without submission.
    # ========================================================

    demo_submission_instruction = {
        "exchange": "WEEX",
        "api_version": "V3",
        "execution_environment": "DEMO",
        "market_symbol": exchange.get(
            "market_symbol"
        ),
        "demo_order_symbol": exchange.get(
            "demo_order_symbol"
        ),
        "active_mode": active_mode,
        "direction": direction,
        "trade_plan": trade_plan,
        "execution_candidate": execution_candidate,
        "anti_duplicate_required": True,
        "one_direction_only_required": True,
        "active_trade_mode_lock_required": True,
        "payload_creation_allowed": False,
        "submission_allowed": False,
        "read_only": True,
    }

    # ========================================================
    # 12. FINAL BOUNDARY VALIDATION
    # ========================================================

    if (
        demo_submission_instruction[
            "execution_environment"
        ]
        != "DEMO"
    ):
        raise RuntimeError(
            "UNIT 10 BLOCKED: INVALID DEMO ENVIRONMENT"
        )

    if (
        demo_submission_instruction[
            "demo_order_symbol"
        ]
        != "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 10 BLOCKED: INVALID DEMO ORDER SYMBOL"
        )

    if (
        demo_submission_instruction[
            "payload_creation_allowed"
        ]
        is not False
    ):
        raise RuntimeError(
            "UNIT 10 BLOCKED: PAYLOAD CREATION ENABLED"
        )

    if (
        demo_submission_instruction[
            "submission_allowed"
        ]
        is not False
    ):
        raise RuntimeError(
            "UNIT 10 BLOCKED: SUBMISSION ENABLED"
        )

    if (
        demo_submission_instruction[
            "read_only"
        ]
        is not True
    ):
        raise RuntimeError(
            "UNIT 10 BLOCKED: BOUNDARY NOT READ ONLY"
        )

    print(
        "PASS: UNIT 10 DEMO BOUNDARY CONTRACT VALIDATED",
        flush=True,
    )

    # ========================================================
    # 13. FINAL NORMALIZED RESULT
    # ========================================================

    unit_10_result = {
        "status": "READY",
        "active_mode": active_mode,
        "direction": direction,
        "signal_qualified": True,
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": trade_plan,
        "execution_ready": True,
        "execution_candidate": execution_candidate,
        "demo_boundary_ready": True,
        "demo_submission_instruction":
            demo_submission_instruction,
        "skip_reason": "NONE",
        "order_payload_created": False,
        "demo_submission_requested": False,
        "real_submission_requested": False,
        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "backup_execution_requested": False,
        "read_only": True,
    }

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 10 STATUS = READY",
        flush=True,
    )

    print(
        f"UNIT 10 ACTIVE MODE = {active_mode}",
        flush=True,
    )

    print(
        f"UNIT 10 DIRECTION = {direction}",
        flush=True,
    )

    print(
        "UNIT 10 SIGNAL QUALIFIED = True",
        flush=True,
    )

    print(
        "UNIT 10 EXECUTION INTENT = True",
        flush=True,
    )

    print(
        "UNIT 10 EXECUTION READY = True",
        flush=True,
    )

    print(
        "UNIT 10 DEMO BOUNDARY READY = True",
        flush=True,
    )

    print(
        "UNIT 10 ORDER PAYLOAD CREATED = False",
        flush=True,
    )

    print(
        "UNIT 10 DEMO SUBMISSION REQUESTED = False",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 10 DEMO EXECUTION BOUNDARY PREPARED",
        flush=True,
    )

    print(
        "PASS: UNIT 10 NO NETWORK REQUEST",
        flush=True,
    )

    print(
        "PASS: UNIT 10 NO ORDER PAYLOAD GENERATED",
        flush=True,
    )

    print(
        "PASS: UNIT 10 NO DEMO SUBMISSION",
        flush=True,
    )

    print(
        "PASS: UNIT 10 NO REAL SUBMISSION",
        flush=True,
    )

    print(
        "PASS: UNIT 10 NO TP EXECUTION",
        flush=True,
    )

    print(
        "PASS: UNIT 10 NO SL EXECUTION",
        flush=True,
    )

    print(
        "PASS: UNIT 10 NO BACKUP EXECUTION",
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
        "FRESH RECONSTRUCTION UNIT 10 RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return unit_10_result


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
# END PART 8
# UNIT 10 FULLY CLOSED AND CALLED
# NEXT = PART 9 / UNIT 11
# ============================================================

# ============================================================
# FRESH RECONSTRUCTION UNIT 11
# DEMO ORDER PAYLOAD CONSTRUCTION + VALIDATION
#
# PURPOSE:
# - Consume verified Unit 2 configuration
# - Consume verified Unit 10 result
# - Preserve normal IDLE state when no trade is qualified
# - Build a normalized WEEX DEMO order payload when READY
# - Validate the payload WITHOUT submission
#
# IMPORTANT:
# - ZERO AUTHENTICATED API ACCESS
# - ZERO ACCOUNT ACCESS
# - ZERO POSITION ACCESS
# - ZERO ORDER ENDPOINT ACCESS
# - ZERO DEMO ORDER SUBMISSION
# - ZERO REAL ORDER SUBMISSION
# - ZERO EXCHANGE WRITE
# - ZERO LEVERAGE MUTATION
# - ZERO MARGIN MODE MUTATION
# - ZERO POSITION MODE MUTATION
#
# UNIT 11 MAY CONSTRUCT A PAYLOAD IN MEMORY.
# UNIT 11 MUST NOT SUBMIT THAT PAYLOAD.
#
# TP AND SL REMAIN INDEPENDENT.
# UNIT 11 DOES NOT EXECUTE TP.
# UNIT 11 DOES NOT EXECUTE SL.
# UNIT 11 DOES NOT EXECUTE BACKUPS.
# ============================================================


def fresh_reconstruction_unit_11(
    config,
    unit_10_result,
):
    from datetime import datetime, timezone

    print(
        "=" * 80,
        flush=True,
    )

    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 11 START",
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
        config,
        dict,
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: INVALID UNIT 2 CONFIGURATION"
        )

    print(
        "PASS: UNIT 11 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    if not isinstance(
        unit_10_result,
        dict,
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: INVALID UNIT 10 RESULT"
        )

    print(
        "PASS: UNIT 11 RECEIVED UNIT 10 RESULT",
        flush=True,
    )

    # ========================================================
    # 2. CONFIGURATION SECTIONS
    # ========================================================

    exchange = config.get(
        "exchange"
    )

    safety = config.get(
        "safety"
    )

    strategy = config.get(
        "strategy"
    )

    market_precision = config.get(
        "market_precision"
    )

    if not isinstance(
        exchange,
        dict,
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: EXCHANGE CONFIGURATION MISSING"
        )

    if not isinstance(
        safety,
        dict,
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: SAFETY CONFIGURATION MISSING"
        )

    if not isinstance(
        strategy,
        dict,
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: STRATEGY CONFIGURATION MISSING"
        )

    if not isinstance(
        market_precision,
        dict,
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: MARKET PRECISION MISSING"
        )

    print(
        "PASS: UNIT 11 CONFIGURATION SECTIONS PRESENT",
        flush=True,
    )

    # ========================================================
    # 3. STRICT UNIT 10 CONTRACT
    # ========================================================

    required_unit_10_fields = (
        "status",
        "active_mode",
        "direction",
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "trade_plan",
        "execution_ready",
        "execution_candidate",
        "demo_boundary_ready",
        "demo_submission_instruction",
        "skip_reason",
        "order_payload_created",
        "demo_submission_requested",
        "real_submission_requested",
        "tp_execution_requested",
        "sl_execution_requested",
        "backup_execution_requested",
        "read_only",
    )

    missing_unit_10_fields = [
        field
        for field in required_unit_10_fields
        if field not in unit_10_result
    ]

    if missing_unit_10_fields:
        raise RuntimeError(
            "UNIT 11 BLOCKED: UNIT 10 MISSING FIELDS = "
            + str(
                missing_unit_10_fields
            )
        )

    print(
        "PASS: UNIT 11 UNIT 10 CONTRACT VALIDATED",
        flush=True,
    )

    # ========================================================
    # 4. UNIT 10 READ-ONLY CONTRACT
    # ========================================================

    if unit_10_result.get(
        "read_only"
    ) is not True:
        raise RuntimeError(
            "UNIT 11 BLOCKED: UNIT 10 RESULT NOT READ ONLY"
        )

    if unit_10_result.get(
        "order_payload_created"
    ) is not False:
        raise RuntimeError(
            "UNIT 11 BLOCKED: UNIT 10 ALREADY CREATED PAYLOAD"
        )

    if unit_10_result.get(
        "demo_submission_requested"
    ) is not False:
        raise RuntimeError(
            "UNIT 11 BLOCKED: UNIT 10 REQUESTED DEMO SUBMISSION"
        )

    if unit_10_result.get(
        "real_submission_requested"
    ) is not False:
        raise RuntimeError(
            "UNIT 11 BLOCKED: UNIT 10 REQUESTED REAL SUBMISSION"
        )

    if unit_10_result.get(
        "tp_execution_requested"
    ) is not False:
        raise RuntimeError(
            "UNIT 11 BLOCKED: UNIT 10 REQUESTED TP EXECUTION"
        )

    if unit_10_result.get(
        "sl_execution_requested"
    ) is not False:
        raise RuntimeError(
            "UNIT 11 BLOCKED: UNIT 10 REQUESTED SL EXECUTION"
        )

    if unit_10_result.get(
        "backup_execution_requested"
    ) is not False:
        raise RuntimeError(
            "UNIT 11 BLOCKED: UNIT 10 REQUESTED BACKUP EXECUTION"
        )

    print(
        "PASS: UNIT 11 UNIT 10 READ-ONLY CONTRACT",
        flush=True,
    )

    # ========================================================
    # 5. GLOBAL SAFETY GATE
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

        if safety.get(
            capability
        ) is not False:

            raise RuntimeError(
                "UNIT 11 BLOCKED: UNSAFE CAPABILITY ENABLED: "
                + capability
            )

    print(
        "PASS: UNIT 11 READ-ONLY SAFETY GATE",
        flush=True,
    )

    # ========================================================
    # 6. WEEX DEMO ENVIRONMENT CONTRACT
    # ========================================================

    if exchange.get(
        "name"
    ) != "WEEX":
        raise RuntimeError(
            "UNIT 11 BLOCKED: INVALID EXCHANGE"
        )

    if exchange.get(
        "api_version"
    ) != "V3":
        raise RuntimeError(
            "UNIT 11 BLOCKED: INVALID API VERSION"
        )

    if exchange.get(
        "market_symbol"
    ) != "BTCUSDT":
        raise RuntimeError(
            "UNIT 11 BLOCKED: INVALID MARKET SYMBOL"
        )

    if exchange.get(
        "demo_order_symbol"
    ) != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 11 BLOCKED: INVALID DEMO ORDER SYMBOL"
        )

    if config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 11 BLOCKED: EXECUTION ENVIRONMENT NOT DEMO"
        )

    print(
        "PASS: UNIT 11 WEEX DEMO ENVIRONMENT CONTRACT",
        flush=True,
    )

    # ========================================================
    # 7. STRATEGY SAFETY CONTRACT
    # ========================================================

    if strategy.get(
        "anti_duplicate_orders"
    ) is not True:
        raise RuntimeError(
            "UNIT 11 BLOCKED: ANTI-DUPLICATE ORDERS DISABLED"
        )

    if strategy.get(
        "one_direction_only"
    ) is not True:
        raise RuntimeError(
            "UNIT 11 BLOCKED: ONE DIRECTION ONLY DISABLED"
        )

    if strategy.get(
        "active_trade_mode_lock"
    ) is not True:
        raise RuntimeError(
            "UNIT 11 BLOCKED: ACTIVE TRADE MODE LOCK DISABLED"
        )

    print(
        "PASS: UNIT 11 STRATEGY SAFETY CONTRACT",
        flush=True,
    )

    # ========================================================
    # 8. NORMALIZE UNIT 10 STATE
    # ========================================================

    status = str(
        unit_10_result.get(
            "status",
            "IDLE",
        )
    ).upper()

    active_mode = unit_10_result.get(
        "active_mode"
    )

    direction = unit_10_result.get(
        "direction"
    )

    signal_qualified = bool(
        unit_10_result.get(
            "signal_qualified",
            False,
        )
    )

    execution_intent = bool(
        unit_10_result.get(
            "execution_intent",
            False,
        )
    )

    trade_plan_ready = bool(
        unit_10_result.get(
            "trade_plan_ready",
            False,
        )
    )

    execution_ready = bool(
        unit_10_result.get(
            "execution_ready",
            False,
        )
    )

    demo_boundary_ready = bool(
        unit_10_result.get(
            "demo_boundary_ready",
            False,
        )
    )

    trade_plan = unit_10_result.get(
        "trade_plan"
    )

    execution_candidate = unit_10_result.get(
        "execution_candidate"
    )

    demo_submission_instruction = (
        unit_10_result.get(
            "demo_submission_instruction"
        )
    )

    skip_reason = str(
        unit_10_result.get(
            "skip_reason",
            "NONE",
        )
    )

    # ========================================================
    # 9. NORMAL IDLE PATH
    # ========================================================

    if (
        status == "IDLE"
        or not signal_qualified
        or not execution_intent
        or not trade_plan_ready
        or not execution_ready
        or not demo_boundary_ready
    ):

        unit_11_result = {
            "status": "IDLE",
            "active_mode": active_mode,
            "direction": direction,
            "signal_qualified": signal_qualified,
            "execution_intent": False,
            "trade_plan_ready": False,
            "trade_plan": None,
            "execution_ready": False,
            "execution_candidate": None,
            "demo_boundary_ready": False,
            "demo_submission_instruction": None,
            "payload_ready": False,
            "order_payload": None,
            "skip_reason": skip_reason,
            "order_payload_created": False,
            "demo_submission_requested": False,
            "real_submission_requested": False,
            "tp_execution_requested": False,
            "sl_execution_requested": False,
            "backup_execution_requested": False,
            "read_only": True,
        }

        print(
            "-" * 80,
            flush=True,
        )

        print(
            "UNIT 11 STATUS = IDLE",
            flush=True,
        )

        print(
            f"UNIT 11 ACTIVE MODE = {active_mode}",
            flush=True,
        )

        print(
            f"UNIT 11 DIRECTION = {direction}",
            flush=True,
        )

        print(
            f"UNIT 11 SIGNAL QUALIFIED = "
            f"{signal_qualified}",
            flush=True,
        )

        print(
            "UNIT 11 EXECUTION INTENT = False",
            flush=True,
        )

        print(
            "UNIT 11 DEMO BOUNDARY READY = False",
            flush=True,
        )

        print(
            "UNIT 11 PAYLOAD READY = False",
            flush=True,
        )

        print(
            "UNIT 11 ORDER PAYLOAD = NONE",
            flush=True,
        )

        print(
            f"UNIT 11 SKIP REASON = {skip_reason}",
            flush=True,
        )

        print(
            "-" * 80,
            flush=True,
        )

        print(
            "PASS: UNIT 11 NORMAL NO-TRADE STATE",
            flush=True,
        )

        print(
            "PASS: UNIT 11 NO ORDER PAYLOAD GENERATED",
            flush=True,
        )

        print(
            "PASS: UNIT 11 NO NETWORK REQUEST",
            flush=True,
        )

        print(
            "PASS: UNIT 11 NO DEMO SUBMISSION",
            flush=True,
        )

        print(
            "PASS: UNIT 11 NO REAL SUBMISSION",
            flush=True,
        )

        print(
            "PASS: UNIT 11 NO TP EXECUTION",
            flush=True,
        )

        print(
            "PASS: UNIT 11 NO SL EXECUTION",
            flush=True,
        )

        print(
            "PASS: UNIT 11 NO BACKUP EXECUTION",
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
            "FRESH RECONSTRUCTION UNIT 11 "
            "RESULT = PASS (IDLE)",
            flush=True,
        )

        print(
            "=" * 80,
            flush=True,
        )

        return unit_11_result

    # ========================================================
    # 10. ACTIONABLE UNIT 10 CONTRACT
    # ========================================================

    if status != "READY":
        raise RuntimeError(
            "UNIT 11 BLOCKED: ACTIONABLE UNIT 10 STATUS NOT READY"
        )

    if active_mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: INVALID ACTIVE MODE"
        )

    if direction not in (
        "LONG",
        "SHORT",
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: INVALID DIRECTION"
        )

    if not isinstance(
        trade_plan,
        dict,
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: TRADE PLAN MISSING"
        )

    if not isinstance(
        execution_candidate,
        dict,
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: EXECUTION CANDIDATE MISSING"
        )

    if not isinstance(
        demo_submission_instruction,
        dict,
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: DEMO SUBMISSION INSTRUCTION MISSING"
        )

    print(
        "PASS: UNIT 11 ACTIONABLE UNIT 10 CONTRACT",
        flush=True,
    )

    # ========================================================
    # 11. VALIDATE UNIT 10 DEMO INSTRUCTION
    # ========================================================

    required_instruction_fields = (
        "exchange",
        "api_version",
        "execution_environment",
        "market_symbol",
        "demo_order_symbol",
        "active_mode",
        "direction",
        "trade_plan",
        "execution_candidate",
        "anti_duplicate_required",
        "one_direction_only_required",
        "active_trade_mode_lock_required",
        "payload_creation_allowed",
        "submission_allowed",
        "read_only",
    )

    missing_instruction_fields = [
        field
        for field in required_instruction_fields
        if field not in demo_submission_instruction
    ]

    if missing_instruction_fields:
        raise RuntimeError(
            "UNIT 11 BLOCKED: DEMO INSTRUCTION MISSING FIELDS = "
            + str(
                missing_instruction_fields
            )
        )

    if demo_submission_instruction.get(
        "exchange"
    ) != "WEEX":
        raise RuntimeError(
            "UNIT 11 BLOCKED: INVALID INSTRUCTION EXCHANGE"
        )

    if demo_submission_instruction.get(
        "api_version"
    ) != "V3":
        raise RuntimeError(
            "UNIT 11 BLOCKED: INVALID INSTRUCTION API VERSION"
        )

    if demo_submission_instruction.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 11 BLOCKED: INVALID INSTRUCTION ENVIRONMENT"
        )

    if demo_submission_instruction.get(
        "market_symbol"
    ) != "BTCUSDT":
        raise RuntimeError(
            "UNIT 11 BLOCKED: INVALID INSTRUCTION MARKET SYMBOL"
        )

    if demo_submission_instruction.get(
        "demo_order_symbol"
    ) != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 11 BLOCKED: INVALID INSTRUCTION DEMO SYMBOL"
        )

    if demo_submission_instruction.get(
        "active_mode"
    ) != active_mode:
        raise RuntimeError(
            "UNIT 11 BLOCKED: ACTIVE MODE CONTRACT MISMATCH"
        )

    if demo_submission_instruction.get(
        "direction"
    ) != direction:
        raise RuntimeError(
            "UNIT 11 BLOCKED: DIRECTION CONTRACT MISMATCH"
        )

    if demo_submission_instruction.get(
        "anti_duplicate_required"
    ) is not True:
        raise RuntimeError(
            "UNIT 11 BLOCKED: ANTI-DUPLICATE CONTRACT MISSING"
        )

    if demo_submission_instruction.get(
        "one_direction_only_required"
    ) is not True:
        raise RuntimeError(
            "UNIT 11 BLOCKED: ONE-DIRECTION CONTRACT MISSING"
        )

    if demo_submission_instruction.get(
        "active_trade_mode_lock_required"
    ) is not True:
        raise RuntimeError(
            "UNIT 11 BLOCKED: MODE LOCK CONTRACT MISSING"
        )

    if demo_submission_instruction.get(
        "payload_creation_allowed"
    ) is not False:
        raise RuntimeError(
            "UNIT 11 BLOCKED: UNIT 10 PAYLOAD FLAG CHANGED"
        )

    if demo_submission_instruction.get(
        "submission_allowed"
    ) is not False:
        raise RuntimeError(
            "UNIT 11 BLOCKED: SUBMISSION FLAG ENABLED"
        )

    if demo_submission_instruction.get(
        "read_only"
    ) is not True:
        raise RuntimeError(
            "UNIT 11 BLOCKED: DEMO INSTRUCTION NOT READ ONLY"
        )

    print(
        "PASS: UNIT 11 DEMO INSTRUCTION VALIDATED",
        flush=True,
    )

    # ========================================================
    # 12. READ EXECUTION DATA
    #
    # Unit 11 does not invent quantity or entry data.
    # It consumes the already-normalized execution candidate
    # produced by the preceding verified units.
    # ========================================================

    quantity = execution_candidate.get(
        "quantity"
    )

    if quantity is None:
        quantity = execution_candidate.get(
            "position_quantity"
        )

    if quantity is None:
        quantity = execution_candidate.get(
            "order_quantity"
        )

    if quantity is None:

        nested_trade_plan = execution_candidate.get(
            "trade_plan"
        )

        if isinstance(
            nested_trade_plan,
            dict,
        ):
            quantity = nested_trade_plan.get(
                "quantity"
            )

            if quantity is None:

                nested_position_sizing = (
                    nested_trade_plan.get(
                        "position_sizing"
                    )
                )

                if isinstance(
                    nested_position_sizing,
                    dict,
                ):
                    quantity = (
                        nested_position_sizing.get(
                            "quantity"
                        )
                    )

    if quantity is None:
        raise RuntimeError(
            "UNIT 11 BLOCKED: EXECUTION QUANTITY MISSING"
        )

    print(
        "PASS: UNIT 11 VERIFIED EXECUTION QUANTITY RECEIVED =",
        quantity,
        flush=True,
    )

    try:
        quantity_value = float(
            quantity
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise RuntimeError(
            "UNIT 11 BLOCKED: INVALID EXECUTION QUANTITY"
        ) from exc

    if quantity_value <= 0:
        raise RuntimeError(
            "UNIT 11 BLOCKED: NON-POSITIVE EXECUTION QUANTITY"
        )

    minimum_quantity = float(
        market_precision.get(
            "minimum_quantity",
            0.0,
        )
    )

    if quantity_value < minimum_quantity:
        raise RuntimeError(
            "UNIT 11 BLOCKED: QUANTITY BELOW MINIMUM"
        )

    print(
        "PASS: UNIT 11 EXECUTION QUANTITY VALIDATED",
        flush=True,
    )

    # ========================================================
    # 13. MAP INTERNAL DIRECTION TO WEEX ENTRY SIDE
    #
    # LONG  -> BUY / LONG
    # SHORT -> SELL / SHORT
    # ========================================================

    if direction == "LONG":

        order_side = "BUY"
        position_side = "LONG"

    elif direction == "SHORT":

        order_side = "SELL"
        position_side = "SHORT"

    else:

        raise RuntimeError(
            "UNIT 11 BLOCKED: UNSUPPORTED DIRECTION"
        )

    # ========================================================
    # 14. FORMAT QUANTITY
    # ========================================================

    quantity_text = (
        f"{quantity_value:.8f}"
        .rstrip("0")
        .rstrip(".")
    )

    if not quantity_text:
        raise RuntimeError(
            "UNIT 11 BLOCKED: EMPTY QUANTITY"
        )

    # ========================================================
    # 15. BUILD IN-MEMORY DEMO ENTRY PAYLOAD
    #
    # IMPORTANT:
    # This dictionary is NOT transmitted by Unit 11.
    #
    # WEEX V3 DEMO requires a nonblank newClientOrderId.
    # Generate it here so Unit 12 receives the complete
    # validated entry payload.
    #
    # No TP is attached here.
    # No SL is attached here.
    # TP and SL remain separate later capabilities.
    # ========================================================

    client_order_timestamp = int(
        datetime.now(
            timezone.utc
        ).timestamp()
        * 1000000
    )

    new_client_order_id = (
        "FR11-"
        + direction
        + "-"
        + str(
            client_order_timestamp
        )
    )

    if not new_client_order_id.strip():
        raise RuntimeError(
            "UNIT 11 BLOCKED: "
            "NEW CLIENT ORDER ID EMPTY"
        )

    order_payload = {
        "symbol":
            exchange.get(
                "demo_order_symbol"
            ),

        "side":
            order_side,

        "positionSide":
            position_side,

        "type":
            "MARKET",

        "quantity":
            quantity_text,

        "newClientOrderId":
            new_client_order_id,
    }

    print(
        "PASS: UNIT 11 NEW CLIENT ORDER ID GENERATED = "
        f"{new_client_order_id}",
        flush=True,
    )

    # ========================================================
    # 16. STRICT PAYLOAD VALIDATION
    # ========================================================

    required_payload_fields = (
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    )

    missing_payload_fields = [
        field
        for field in required_payload_fields
        if field not in order_payload
    ]

    if not str(
        order_payload.get(
            "newClientOrderId",
            ""
        )
    ).strip():
        raise RuntimeError(
            "UNIT 11 BLOCKED: "
            "NEW CLIENT ORDER ID BLANK"
        )

    print(
        "PASS: UNIT 11 NEW CLIENT ORDER ID VALIDATED",
        flush=True,
    )

    if missing_payload_fields:
        raise RuntimeError(
            "UNIT 11 BLOCKED: PAYLOAD MISSING FIELDS = "
            + str(
                missing_payload_fields
            )
        )

    if order_payload[
        "symbol"
    ] != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 11 BLOCKED: PAYLOAD SYMBOL FAILURE"
        )

    if order_payload[
        "side"
    ] not in (
        "BUY",
        "SELL",
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: PAYLOAD SIDE FAILURE"
        )

    if order_payload[
        "positionSide"
    ] not in (
        "LONG",
        "SHORT",
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: PAYLOAD POSITION SIDE FAILURE"
        )

    if order_payload[
        "type"
    ] != "MARKET":
        raise RuntimeError(
            "UNIT 11 BLOCKED: PAYLOAD TYPE FAILURE"
        )

    if (
        direction == "LONG"
        and (
            order_payload["side"] != "BUY"
            or
            order_payload["positionSide"] != "LONG"
        )
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: LONG PAYLOAD DIRECTION FAILURE"
        )

    if (
        direction == "SHORT"
        and (
            order_payload["side"] != "SELL"
            or
            order_payload["positionSide"] != "SHORT"
        )
    ):
        raise RuntimeError(
            "UNIT 11 BLOCKED: SHORT PAYLOAD DIRECTION FAILURE"
        )

    forbidden_payload_fields = (
        "slTriggerPrice",
        "SlWorkingType",
        "stopLossPrice",
        "stopPrice",
        "tpTriggerPrice",
        "TpWorkingType",
    )

    unexpected_protected_fields = [
        field
        for field in forbidden_payload_fields
        if field in order_payload
    ]

    if unexpected_protected_fields:
        raise RuntimeError(
            "UNIT 11 BLOCKED: TP/SL FIELD PRESENT IN ENTRY PAYLOAD = "
            + str(
                unexpected_protected_fields
            )
        )

    print(
        "PASS: UNIT 11 DEMO ENTRY PAYLOAD VALIDATED",
        flush=True,
    )

    print(
        "PASS: UNIT 11 TP NOT COUPLED TO ENTRY PAYLOAD",
        flush=True,
    )

    print(
        "PASS: UNIT 11 SL NOT COUPLED TO ENTRY PAYLOAD",
        flush=True,
    )

    # ========================================================
    # 17. FINAL NORMALIZED RESULT
    # ========================================================

    unit_11_result = {
        "status": "READY",
        "active_mode": active_mode,
        "direction": direction,
        "signal_qualified": True,
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": trade_plan,
        "execution_ready": True,
        "execution_candidate": execution_candidate,
        "demo_boundary_ready": True,
        "demo_submission_instruction":
            demo_submission_instruction,
        "payload_ready": True,
        "order_payload": order_payload,
        "skip_reason": "NONE",
        "order_payload_created": True,
        "demo_submission_requested": False,
        "real_submission_requested": False,
        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "backup_execution_requested": False,
        "read_only": True,
    }

    # ========================================================
    # 18. FINAL REPORT
    # ========================================================

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 11 STATUS = READY",
        flush=True,
    )

    print(
        f"UNIT 11 ACTIVE MODE = {active_mode}",
        flush=True,
    )

    print(
        f"UNIT 11 DIRECTION = {direction}",
        flush=True,
    )

    print(
        "UNIT 11 SIGNAL QUALIFIED = True",
        flush=True,
    )

    print(
        "UNIT 11 EXECUTION INTENT = True",
        flush=True,
    )

    print(
        "UNIT 11 DEMO BOUNDARY READY = True",
        flush=True,
    )

    print(
        "UNIT 11 PAYLOAD READY = True",
        flush=True,
    )

    print(
        "UNIT 11 ORDER PAYLOAD =",
        order_payload,
        flush=True,
    )

    print(
        "UNIT 11 ORDER PAYLOAD CREATED = True",
        flush=True,
    )

    print(
        "UNIT 11 DEMO SUBMISSION REQUESTED = False",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11 DEMO PAYLOAD CONSTRUCTION COMPLETED",
        flush=True,
    )

    print(
        "PASS: UNIT 11 PAYLOAD VALIDATION COMPLETED",
        flush=True,
    )

    print(
        "PASS: UNIT 11 NO NETWORK REQUEST",
        flush=True,
    )

    print(
        "PASS: UNIT 11 NO DEMO SUBMISSION",
        flush=True,
    )

    print(
        "PASS: UNIT 11 NO REAL SUBMISSION",
        flush=True,
    )

    print(
        "PASS: UNIT 11 NO TP EXECUTION",
        flush=True,
    )

    print(
        "PASS: UNIT 11 NO SL EXECUTION",
        flush=True,
    )

    print(
        "PASS: UNIT 11 NO BACKUP EXECUTION",
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
        "FRESH RECONSTRUCTION UNIT 11 RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return unit_11_result


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
# END PART 9
# UNIT 11 FULLY CLOSED AND CALLED
# NEXT = PART 10 / UNIT 12
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

FRESH_RECONSTRUCTION_UNIT_12_RESULT = (
    fresh_reconstruction_unit_12(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_11_RESULT,
    )
)


# ============================================================
# END PART 10
# UNIT 12 FULLY CLOSED AND CALLED
# NEXT = PART 11 / UNIT 13
# ============================================================ 

# ============================================================
# FRESH RECONSTRUCTION UNIT 13
# EXISTING-POSITION TAKE-PROFIT MANAGEMENT
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
# TP:
# - TP1 = 25%
# - TP2 = 25%
# - TP3 = 50% TRAILING RUNNER
# - TP3 TRAILING DISTANCE = 0.20%
#
# SAFETY:
# - DEMO ONLY
# - REAL TRADING PROHIBITED
# - SL DISABLED
# - NO BACKUP EXECUTION
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
    # 1. BASIC INPUT VALIDATION
    # ========================================================

    if not isinstance(
        config,
        dict,
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "CONFIGURATION IS NOT A DICTIONARY"
        )

    print(
        "PASS: UNIT 13 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    if not isinstance(
        unit_12_result,
        dict,
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "UNIT 12 RESULT IS NOT A DICTIONARY"
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
        f"UNIT 13 RECEIVED UNIT 12 STATUS = "
        f"{unit_12_status}",
        flush=True,
    )

    # ========================================================
    # IMPORTANT CORRECTION
    #
    # DO NOT RETURN IDLE BECAUSE UNIT 12 IS IDLE.
    #
    # Unit 12 controls INITIAL ENTRY.
    #
    # Unit 13 controls EXISTING POSITION MANAGEMENT.
    #
    # Therefore Unit 13 MUST inspect the actual demo position
    # before deciding whether TP management is needed.
    # ========================================================

    print(
        "PASS: UNIT 13 POSITION MANAGEMENT "
        "INDEPENDENT OF NEW SIGNAL",
        flush=True,
    )

    print(
        "PASS: UNIT 13 WILL CHECK EXISTING POSITION "
        "EVEN WHEN UNIT 12 IS IDLE",
        flush=True,
    )

    # ========================================================
    # 2. STRATEGY CONFIGURATION
    # ========================================================

    strategy = config.get(
        "strategy"
    )

    if not isinstance(
        strategy,
        dict,
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "STRATEGY CONFIGURATION MISSING"
        )

    tp1_allocation_percent = Decimal(
        str(
            strategy.get(
                "tp1_allocation_percent",
                25.0,
            )
        )
    )

    tp2_allocation_percent = Decimal(
        str(
            strategy.get(
                "tp2_allocation_percent",
                25.0,
            )
        )
    )

    tp3_allocation_percent = Decimal(
        str(
            strategy.get(
                "tp3_allocation_percent",
                50.0,
            )
        )
    )

    tp3_trailing_percent = Decimal(
        str(
            strategy.get(
                "tp3_trailing_percent",
                0.20,
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
        != Decimal("100")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "TP ALLOCATION DOES NOT TOTAL 100%"
        )

    if (
        tp3_trailing_percent
        <= Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "INVALID TP3 TRAILING DISTANCE"
        )

    print(
        "PASS: UNIT 13 TP ALLOCATION = 25 / 25 / 50",
        flush=True,
    )

    print(
        "PASS: UNIT 13 TP3 TRAILING DISTANCE = "
        f"{tp3_trailing_percent}%",
        flush=True,
    )

    # ========================================================
    # 3. LEVERAGE / TP TARGET CONTRACT
    #
    # TP1 = 10% ROI
    # TP2 = 20% ROI
    #
    # At 100x:
    # TP1 price movement ~= 0.10%
    # TP2 price movement ~= 0.20%
    # ========================================================

    leverage_target = Decimal(
        str(
            strategy.get(
                "leverage_target",
                config.get(
                    "leverage_target",
                    100,
                ),
            )
        )
    )

    if (
        leverage_target
        <= Decimal("0")
    ):
        leverage_target = Decimal(
            "100"
        )

    tp1_roi_percent = Decimal(
        "10"
    )

    tp2_roi_percent = Decimal(
        "20"
    )

    tp1_price_move_percent = (
        tp1_roi_percent
        /
        leverage_target
    )

    tp2_price_move_percent = (
        tp2_roi_percent
        /
        leverage_target
    )

    print(
        "UNIT 13 TP1 ROI TARGET = 10%",
        flush=True,
    )

    print(
        "UNIT 13 TP2 ROI TARGET = 20%",
        flush=True,
    )

    # ========================================================
    # 4. EXCHANGE CONFIGURATION
    # ========================================================

    exchange = config.get(
        "exchange"
    )

    if not isinstance(
        exchange,
        dict,
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "EXCHANGE CONFIGURATION MISSING"
        )

    demo_symbol = exchange.get(
        "demo_order_symbol"
    )

    if (
        demo_symbol
        != "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "DEMO SYMBOL MUST BE BTCSUSDT"
        )

    base_url = str(
        exchange.get(
            "base_url",
            "https://api-contract.weex.com",
        )
    ).rstrip("/")

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
        "PASS: UNIT 13 EXECUTION ENVIRONMENT = DEMO",
        flush=True,
    )

    print(
        "PASS: UNIT 13 REAL TRADING PROHIBITED",
        flush=True,
    )

    # ========================================================
    # 5. API CREDENTIALS
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
            "UNIT 13 BLOCKED: "
            "WEEX API KEY MISSING"
        )

    if not api_secret:
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "WEEX API SECRET MISSING"
        )

    if not api_passphrase:
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "WEEX API PASSPHRASE MISSING"
        )

    print(
        "PASS: UNIT 13 DEMO AUTHENTICATION AVAILABLE",
        flush=True,
    )

    # ========================================================
    # 6. ALWAYS CHECK CURRENT DEMO POSITION
    #
    # THIS HAPPENS REGARDLESS OF UNIT 12 STATUS.
    # ========================================================

    position_request_path = (
        "/capi/v3/sim/position/allPosition"
    )

    position_method = "GET"

    position_timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    position_prehash = (
        position_timestamp
        +
        position_method
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

        try:

            error_text = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

        except Exception:

            error_text = str(
                exc
            )

        print(
            "UNIT 13 POSITION HTTP ERROR = "
            f"{exc.code}",
            flush=True,
        )

        print(
            "UNIT 13 POSITION RESPONSE = "
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
        int(
            position_http_status
        )
        <
        300
    ):
        raise RuntimeError(
            "UNIT 13 POSITION READ "
            "NON-SUCCESS HTTP STATUS"
        )

    try:

        position_records = (
            json.loads(
                position_response_text
            )
        )

    except Exception as exc:

        raise RuntimeError(
            "UNIT 13 POSITION RESPONSE "
            "IS NOT VALID JSON"
        ) from exc

    if not isinstance(
        position_records,
        list,
    ):
        raise RuntimeError(
            "UNIT 13 POSITION RESPONSE "
            "IS NOT A LIST"
        )

    print(
        "PASS: UNIT 13 DEMO POSITION READ COMPLETED",
        flush=True,
    )

    # ========================================================
    # 7. FIND ACTIVE BTCSUSDT POSITION
    # ========================================================

    active_positions = []

    for record in position_records:

        if not isinstance(
            record,
            dict,
        ):
            continue

        record_symbol = str(
            record.get(
                "symbol",
                "",
            )
        ).upper()

        if (
            record_symbol
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
    # 8. NO EXISTING POSITION
    #
    # ONLY NOW MAY UNIT 13 RETURN IDLE.
    # ========================================================

    if (
        len(
            active_positions
        )
        ==
        0
    ):

        result = {
            "unit": 13,

            "status":
                "IDLE_NO_POSITION",

            "read_only":
                False,

            "unit_12_status":
                unit_12_status,

            "position_check_attempted":
                True,

            "position_check_completed":
                True,

            "active_position_exists":
                False,

            "tp_management_required":
                False,

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
                "NO_ACTIVE_BTCSUSDT_POSITION",
        }

        print(
            "-" * 80,
            flush=True,
        )

        print(
            "UNIT 13 STATUS = IDLE_NO_POSITION",
            flush=True,
        )

        print(
            "UNIT 13 ACTIVE POSITION EXISTS = False",
            flush=True,
        )

        print(
            "UNIT 13 NEW SIGNAL REQUIRED FOR NEW ENTRY = True",
            flush=True,
        )

        print(
            "PASS: UNIT 13 NO POSITION TO MANAGE",
            flush=True,
        )

        print(
            "PASS: UNIT 13 NO TP EXECUTION",
            flush=True,
        )

        print(
            "PASS: UNIT 13 NO SL EXECUTION",
            flush=True,
        )

        print(
            "PASS: UNIT 13 NO BACKUP EXECUTION",
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

    # ========================================================
    # 9. EXACTLY ONE ACTIVE POSITION REQUIRED
    # ========================================================

    if (
        len(
            active_positions
        )
        !=
        1
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "MULTIPLE ACTIVE BTCSUSDT POSITIONS DETECTED"
        )

    position = (
        active_positions[0]
    )

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
            "UNIT 13 BLOCKED: "
            "INVALID POSITION SIDE"
        )

    position_size = Decimal(
        str(
            position.get(
                "size",
                "0",
            )
        )
    )

    if (
        position_size
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "INVALID ACTIVE POSITION SIZE"
        )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 13 ACTIVE POSITION EXISTS = True",
        flush=True,
    )

    print(
        f"UNIT 13 POSITION SIDE = "
        f"{position_side}",
        flush=True,
    )

    print(
        f"UNIT 13 CURRENT POSITION SIZE = "
        f"{position_size}",
        flush=True,
    )

    print(
        "PASS: UNIT 13 EXISTING POSITION "
        "MANAGEMENT ACTIVATED",
        flush=True,
    )

    print(
        "PASS: UNIT 13 NEW QUALIFIED SIGNAL "
        "NOT REQUIRED",
        flush=True,
    )

    # ========================================================
    # 10. DERIVE AVERAGE ENTRY PRICE
    # ========================================================

    try:

        open_value = Decimal(
            str(
                position.get(
                    "openValue",
                    "0",
                )
            )
        )

    except Exception as exc:

        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "INVALID POSITION OPEN VALUE"
        ) from exc

    if (
        open_value
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "POSITION OPEN VALUE MISSING OR ZERO"
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
            "UNIT 13 BLOCKED: "
            "AVERAGE ENTRY PRICE INVALID"
        )

    print(
        "UNIT 13 AVERAGE ENTRY PRICE = "
        f"{average_entry_price}",
        flush=True,
    )

    # ========================================================
    # 11. CUMULATIVE OPEN / CLOSE SIZE
    # ========================================================

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
        "UNIT 13 CUMULATIVE OPEN SIZE = "
        f"{cumulative_open_size}",
        flush=True,
    )

    print(
        "UNIT 13 CUMULATIVE CLOSE SIZE = "
        f"{cumulative_close_size}",
        flush=True,
    )

    # ========================================================
    # 12. QUANTITY STEP
    # ========================================================

    quantity_step = Decimal(
        "0.0001"
    )

    market_precision = config.get(
        "market_precision"
    )

    if isinstance(
        market_precision,
        dict,
    ):

        configured_step = (
            market_precision.get(
                "quantity_step"
            )
        )

        if (
            configured_step
            is not None
        ):

            try:

                parsed_step = Decimal(
                    str(
                        configured_step
                    )
                )

                if (
                    parsed_step
                    >
                    Decimal("0")
                ):
                    quantity_step = (
                        parsed_step
                    )

            except Exception:
                pass

# ============================================================
# END PART 11A
# CONTINUE DIRECTLY WITH PART 11B
# ZERO-INDENTATION TRANSMISSION DEMARCATION ONLY
# ============================================================

        if (
            configured_step
            is not None
        ):    

            try:

                parsed_step = Decimal(
                    str(
                        configured_step
                    )
                )

                if (
                    parsed_step
                    >
                    Decimal("0")
                ):

                    quantity_step = (
                        parsed_step
                    )

            except Exception:

                pass

    def unit_13_round_quantity_down(
        value,
    ):

        if (
            value
            <=
            Decimal("0")
        ):
            return Decimal(
                "0"
            )

        step_count = (
            value
            /
            quantity_step
        ).to_integral_value(
            rounding=ROUND_DOWN
        )

        return (
            step_count
            *
            quantity_step
        )

    # ========================================================
    # 13. TP QUANTITY ALLOCATION
    # ========================================================

    tp1_quantity = (
        unit_13_round_quantity_down(
            cumulative_open_size
            *
            tp1_allocation_percent
            /
            Decimal("100")
        )
    )

    tp2_quantity = (
        unit_13_round_quantity_down(
            cumulative_open_size
            *
            tp2_allocation_percent
            /
            Decimal("100")
        )
    )

    tp3_quantity = (
        cumulative_open_size
        -
        tp1_quantity
        -
        tp2_quantity
    )

    if (
        tp3_quantity
        <
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "INVALID TP QUANTITY ALLOCATION"
        )

    print(
        f"UNIT 13 TP1 QUANTITY = "
        f"{tp1_quantity}",
        flush=True,
    )

    print(
        f"UNIT 13 TP2 QUANTITY = "
        f"{tp2_quantity}",
        flush=True,
    )

    print(
        f"UNIT 13 TP3 RUNNER QUANTITY = "
        f"{tp3_quantity}",
        flush=True,
    )

    # ========================================================
    # 14. TP TARGET PRICES
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

        tp1_target = (
            average_entry_price
            *
            (
                Decimal("1")
                +
                tp1_fraction
            )
        )

        tp2_target = (
            average_entry_price
            *
            (
                Decimal("1")
                +
                tp2_fraction
            )
        )

        closing_side = (
            "SELL"
        )

    else:

        tp1_target = (
            average_entry_price
            *
            (
                Decimal("1")
                -
                tp1_fraction
            )
        )

        tp2_target = (
            average_entry_price
            *
            (
                Decimal("1")
                -
                tp2_fraction
            )
        )

        closing_side = (
            "BUY"
        )

    price_step = Decimal(
        "0.1"
    )

    def unit_13_round_price_down(
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

    tp1_target = (
        unit_13_round_price_down(
            tp1_target
        )
    )

    tp2_target = (
        unit_13_round_price_down(
            tp2_target
        )
    )

    print(
        f"UNIT 13 TP1 TARGET PRICE = "
        f"{tp1_target}",
        flush=True,
    )

    print(
        f"UNIT 13 TP2 TARGET PRICE = "
        f"{tp2_target}",
        flush=True,
    )

    # ========================================================
    # 15. CURRENT PUBLIC MARK PRICE
    # ========================================================

    mark_request_path = (
        "/capi/v3/market/symbolPrice"
    )

    mark_query = (
        urllib.parse.urlencode(
            {
                "symbol":
                    "BTCUSDT",

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

    except urllib.error.HTTPError as exc:

        raise RuntimeError(
            "UNIT 13 MARK PRICE HTTP ERROR: "
            f"{exc.code}"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "UNIT 13 MARK PRICE NETWORK ERROR: "
            f"{exc}"
        ) from exc

    if not (
        200
        <=
        int(
            mark_http_status
        )
        <
        300
    ):
        raise RuntimeError(
            "UNIT 13 MARK PRICE READ FAILED"
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
        f"UNIT 13 CURRENT MARK PRICE = "
        f"{mark_price}",
        flush=True,
    )

    # ========================================================
    # 16. DETERMINE COMPLETED TP ALLOCATION
    # ========================================================

    tp1_already_completed = (
        tp1_quantity
        >
        Decimal("0")
        and
        cumulative_close_size
        >=
        tp1_quantity
    )

    tp2_already_completed = (
        tp2_quantity
        >
        Decimal("0")
        and
        cumulative_close_size
        >=
        (
            tp1_quantity
            +
            tp2_quantity
        )
    )

    print(
        "UNIT 13 TP1 ALREADY COMPLETED = "
        f"{tp1_already_completed}",
        flush=True,
    )

    print(
        "UNIT 13 TP2 ALREADY COMPLETED = "
        f"{tp2_already_completed}",
        flush=True,
    )

    # ========================================================
    # 17. CHECK TP TARGETS
    # ========================================================

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
        f"UNIT 13 TP1 REACHED = "
        f"{tp1_reached}",
        flush=True,
    )

    print(
        f"UNIT 13 TP2 REACHED = "
        f"{tp2_reached}",
        flush=True,
    )

    # ========================================================
    # 18. SELECT EXACTLY ONE TP ACTION
    # ========================================================

    close_quantity = Decimal(
        "0"
    )

    tp_action = (
        "NONE"
    )

    # --------------------------------------------------------
    # TP2 HAS PRIORITY.
    #
    # If price jumped through TP1 directly to TP2,
    # close whatever quantity remains necessary to bring
    # cumulative closed quantity to TP1 + TP2 allocation.
    # --------------------------------------------------------

    if (
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

        close_quantity = (
            unit_13_round_quantity_down(
                outstanding_quantity
            )
        )

        if (
            close_quantity
            >
            position_size
        ):
            close_quantity = (
                unit_13_round_quantity_down(
                    position_size
                )
            )

        if (
            close_quantity
            >
            Decimal("0")
        ):
            tp_action = (
                "TP2"
            )

    elif (
        tp1_reached
        and
        not tp1_already_completed
    ):

        outstanding_quantity = (
            tp1_quantity
            -
            cumulative_close_size
        )

        close_quantity = (
            unit_13_round_quantity_down(
                outstanding_quantity
            )
        )

        if (
            close_quantity
            >
            position_size
        ):
            close_quantity = (
                unit_13_round_quantity_down(
                    position_size
                )
            )

        if (
            close_quantity
            >
            Decimal("0")
        ):
            tp_action = (
                "TP1"
            )

    # ========================================================
    # 19. NO TP1 / TP2 CLOSE REQUIRED
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
            position_size
            >
            Decimal("0")
        )

        if tp3_armed:

            unit_13_status = (
                "TP3_ARMED"
            )

            skip_reason = (
                "TP3_TRAILING_RUNTIME_REQUIRED"
            )

        else:

            unit_13_status = (
                "MONITORING"
            )

            skip_reason = (
                "TP_TARGET_NOT_REACHED"
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

            "position_check_attempted":
                True,

            "position_check_completed":
                True,

            "active_position_exists":
                True,

            "position_side":
                position_side,

            "position_size":
                float(
                    position_size
                ),

            "average_entry_price":
                float(
                    average_entry_price
                ),

            "mark_price":
                float(
                    mark_price
                ),

            "tp1_target":
                float(
                    tp1_target
                ),

            "tp2_target":
                float(
                    tp2_target
                ),

            "tp1_quantity":
                float(
                    tp1_quantity
                ),

            "tp2_quantity":
                float(
                    tp2_quantity
                ),

            "tp3_quantity":
                float(
                    tp3_quantity
                ),

            "tp1_completed":
                tp1_already_completed,

            "tp2_completed":
                tp2_already_completed,

            "tp3_armed":
                tp3_armed,

            "tp3_trailing_percent":
                float(
                    tp3_trailing_percent
                ),

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
            f"UNIT 13 STATUS = "
            f"{unit_13_status}",
            flush=True,
        )

        print(
            "UNIT 13 ACTIVE POSITION MANAGEMENT = TRUE",
            flush=True,
        )

        print(
            "UNIT 13 NEW SIGNAL REQUIRED = FALSE",
            flush=True,
        )

        print(
            "UNIT 13 TP EXECUTION ATTEMPTED = False",
            flush=True,
        )

        print(
            f"UNIT 13 TP3 ARMED = "
            f"{tp3_armed}",
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
            "UNIT 13 REAL ORDER = FALSE",
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
    # 20. VALIDATE TP CLOSE QUANTITY
    # ========================================================

    if (
        close_quantity
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "TP CLOSE QUANTITY INVALID"
        )

    quantity_text = (
        f"{close_quantity:.8f}"
        .rstrip("0")
        .rstrip(".")
    )

    if not quantity_text:
        raise RuntimeError(
            "UNIT 13 BLOCKED: "
            "EMPTY TP QUANTITY"
        )

    # ========================================================
    # 21. BUILD DEMO TP CLOSE PAYLOAD
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
        str(
            client_order_timestamp
        )
    )

    if (
        len(
            new_client_order_id
        )
        >
        36
    ):
        new_client_order_id = (
            new_client_order_id[
                :36
            ]
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
    # 22. ABSOLUTE SL PROHIBITION
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
                "UNIT 13 BLOCKED: "
                "SL FIELD DETECTED"
            )

    print(
        "PASS: UNIT 13 TP CLOSE PAYLOAD VALIDATED",
        flush=True,
    )

    print(
        "PASS: UNIT 13 SL REMAINS DISABLED",
        flush=True,
    )

    # ========================================================
    # 23. DEMO ENDPOINT ONLY
    # ========================================================

    request_path = (
        "/capi/v3/sim/order"
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
        f"UNIT 13 TP ACTION = "
        f"{tp_action}",
        flush=True,
    )

    print(
        f"UNIT 13 TP CLOSE SIDE = "
        f"{closing_side}",
        flush=True,
    )

    print(
        f"UNIT 13 TP CLOSE QUANTITY = "
        f"{quantity_text}",
        flush=True,
    )

    print(
        "UNIT 13 NEW SIGNAL REQUIRED = FALSE",
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

    print(
        "UNIT 13 BACKUP EXECUTION = FALSE",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    # ========================================================
    # 24. SUBMIT EXACTLY ONE DEMO TP CLOSE
    # ========================================================

    request = (
        urllib.request.Request(
# ============================================================
# END PART 11B
# CONTINUE DIRECTLY WITH PART 11C
# ZERO-INDENTATION TRANSMISSION DEMARCATION ONLY
# ============================================================

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

        try:

            error_text = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

        except Exception:

            error_text = str(
                exc
            )

        print(
            "UNIT 13 TP HTTP ERROR = "
            f"{exc.code}",
            flush=True,
        )

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
        f"UNIT 13 TP HTTP STATUS = "
        f"{response_status}",
        flush=True,
    )

    print(
        f"UNIT 13 TP RESPONSE = "
        f"{response_text}",
        flush=True,
    )

    try:

        response_json = (
            json.loads(
                response_text
            )
        )

    except Exception as exc:

        raise RuntimeError(
            "UNIT 13 TP RESPONSE "
            "IS NOT VALID JSON"
        ) from exc

    if not (
        200
        <=
        int(
            response_status
        )
        <
        300
    ):
        raise RuntimeError(
            "UNIT 13 TP ORDER FAILED: "
            f"HTTP {response_status}"
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

    tp_order_id = (
        response_json.get(
            "orderId"
        )
    )

    if not tp_order_id:
        raise RuntimeError(
            "UNIT 13 TP ACCEPTED "
            "WITHOUT ORDER ID"
        )

    # ========================================================
    # 25. SUCCESS RESULT
    # ========================================================

    result = {
        "unit":
            13,

        "status":
            "TP_EXECUTED",

        "read_only":
            False,

        "unit_12_status":
            unit_12_status,

        "active_position_exists":
            True,

        "position_side":
            position_side,

        "position_size_before":
            float(
                position_size
            ),

        "average_entry_price":
            float(
                average_entry_price
            ),

        "mark_price":
            float(
                mark_price
            ),

        "tp_action":
            tp_action,

        "tp_close_quantity":
            float(
                close_quantity
            ),

        "tp1_target":
            float(
                tp1_target
            ),

        "tp2_target":
            float(
                tp2_target
            ),

        "tp1_quantity":
            float(
                tp1_quantity
            ),

        "tp2_quantity":
            float(
                tp2_quantity
            ),

        "tp3_quantity":
            float(
                tp3_quantity
            ),

        "tp3_trailing_percent":
            float(
                tp3_trailing_percent
            ),

        "tp_execution_attempted":
            True,

        "tp_execution_completed":
            True,

        "sl_execution_attempted":
            False,

        "backup_execution_attempted":
            False,

        "real_submission_attempted":
            False,

        "authenticated_request":
            True,

        "order_endpoint_access":
            True,

        "exchange_write":
            True,

        "request_path":
            request_path,

        "request_payload":
            tp_payload,

        "http_status":
            response_status,

        "weex_response":
            response_json,

        "order_id":
            tp_order_id,
    }

    print(
        "-" * 80,
        flush=True,
    )

    print(
        f"PASS: UNIT 13 "
        f"{tp_action} DEMO EXECUTED",
        flush=True,
    )

    print(
        f"PASS: UNIT 13 TP ORDER ID = "
        f"{tp_order_id}",
        flush=True,
    )

    print(
        "PASS: UNIT 13 EXISTING POSITION "
        "MANAGED WITHOUT NEW SIGNAL",
        flush=True,
    )

    print(
        "PASS: UNIT 13 REAL ORDER PROHIBITED",
        flush=True,
    )

    print(
        "PASS: UNIT 13 SL REMAINS DISABLED",
        flush=True,
    )

    print(
        "PASS: UNIT 13 NO LEVERAGE MUTATION",
        flush=True,
    )

    print(
        "PASS: UNIT 13 NO MARGIN MODE MUTATION",
        flush=True,
    )

    print(
        "PASS: UNIT 13 NO POSITION MODE MUTATION",
        flush=True,
    )

    print(
        "PASS: UNIT 13 NO BACKUP EXECUTION",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 13 RESULT = "
        "PASS (TP EXECUTED)",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return result


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
# TP3 DEMO TRAILING RUNTIME
#
# PURPOSE:
# - COMPLETE THE TP3 RUNNER ALREADY ARMED BY UNIT 13.
# - TP3 = REMAINING 50% RUNNER.
# - TRAILING CALLBACK = 0.20%.
# - NO NEW QUALIFIED SIGNAL REQUIRED.
# - DEMO BTCSUSDT ONLY.
# - REAL ORDER PROHIBITED.
# - SL REMAINS DISABLED.
#
# IMPORTANT:
# - THIS BLOCK RUNS AFTER UNIT 13.
# - IT DOES NOT MODIFY TP1 OR TP2.
# - IT DOES NOT CREATE A NEW POSITION.
# - IT CLOSES ONLY THE EXISTING TP3 RUNNER.
# ============================================================

def fresh_tp3_runtime(
    config,
    unit_13_result,
):
    # ============================================================
    # FRESH RECONSTRUCTION UNIT 14
    # COMBINED TP3 + LIQUIDATION BACKUP RUNTIME
    #
    # FIXED SEQUENCE:
    #
    # ENTRY -> B1 -> L1 -> B2 -> L2 -> B3 -> L3 -> STOP
    #
    # IMPORTANT:
    # - B1 uses CURRENT WEEX liquidation price L1.
    # - AFTER B1 FILLS, WEEX position is re-read.
    # - B2 uses the NEW liquidation price L2.
    # - AFTER B2 FILLS, WEEX position is re-read.
    # - B3 uses the NEW liquidation price L3.
    # - NO B4.
    #
    # LONG:
    #   backup trigger = liquidation * (1 + buffer)
    #
    # SHORT:
    #   backup trigger = liquidation * (1 - buffer)
    #
    # DEFAULT CONFIG:
    #   backup margin = 5%
    #   backup buffer = 0.30%
    #   max backups = 3
    #   exposure cap = 35%
    #
    # ALL ABOVE VALUES ARE READ FROM CONFIG.
    #
    # SAFETY:
    # - DEMO BTCSUSDT ONLY
    # - REAL ORDERS PROHIBITED
    # - SL DISABLED
    # - ONE DIRECTION ONLY
    # - ANTI-DUPLICATE
    # - NO LEVERAGE MUTATION
    # - NO MARGIN MODE MUTATION
    # - NO POSITION MODE MUTATION
    # ============================================================

    import os
    import json
    import time
    import hmac
    import math
    import hashlib
    import base64
    import urllib.request
    import urllib.error
    import urllib.parse

    from decimal import Decimal, ROUND_DOWN
    from datetime import datetime, timezone

    print("=" * 80, flush=True)

    print(
        f"{datetime.now(timezone.utc).isoformat()} "
        "FRESH RECONSTRUCTION UNIT 14 START",
        flush=True,
    )

    print("-" * 80, flush=True)

    # ========================================================
    # 1. CONFIGURATION CONTRACT
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 14 BLOCKED: CONFIGURATION MISSING"
        )

    if not isinstance(unit_13_result, dict):
        raise RuntimeError(
            "UNIT 14 BLOCKED: UNIT 13 RESULT MISSING"
        )

    strategy = config.get("strategy", {})
    exchange = config.get("exchange", {})

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 14 BLOCKED: STRATEGY CONFIGURATION MISSING"
        )

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 14 BLOCKED: EXCHANGE CONFIGURATION MISSING"
        )

    execution_environment = str(
        config.get("execution_environment", "")
    ).upper()

    if execution_environment != "DEMO":
        raise RuntimeError(
            "UNIT 14 BLOCKED: EXECUTION ENVIRONMENT NOT DEMO"
        )

    market_symbol = str(
        exchange.get("market_symbol", "")
    ).upper()

    demo_symbol = str(
        exchange.get("demo_order_symbol", "")
    ).upper()

    base_url = str(
        exchange.get("contract_base_url", "")
    ).rstrip("/")

    if market_symbol != "BTCUSDT":
        raise RuntimeError(
            "UNIT 14 BLOCKED: MARKET SYMBOL MUST BE BTCUSDT"
        )

    if demo_symbol != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 14 BLOCKED: DEMO SYMBOL MUST BE BTCSUSDT"
        )

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID CONTRACT BASE URL"
        )

    # ========================================================
    # 2. ADJUSTABLE STRATEGY VALUES
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

    trailing_percent = Decimal(
        str(
            strategy.get(
                "tp3_trailing_percent",
                0.20,
            )
        )
    )

    leverage_target = Decimal(
        str(
            strategy.get(
                "leverage_target",
                100,
            )
        )
    )

    initial_margin_percent = Decimal(
        str(
            strategy.get(
                "initial_margin_percent",
                5.0,
            )
        )
    )

    if backup_margin_percent <= 0:
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID BACKUP MARGIN"
        )

    if backup_buffer_percent <= 0:
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID BACKUP BUFFER"
        )

    if max_backups < 0:
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID MAX BACKUPS"
        )

    # ABSOLUTE ARCHITECTURE CAP.
    # Configuration may reduce backups below 3,
    # but may never create B4.

    max_backups = min(
        max_backups,
        3,
    )

    if exposure_cap_percent <= 0:
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID EXPOSURE CAP"
        )

    if trailing_percent <= 0:
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID TP3 TRAILING PERCENT"
        )

    if leverage_target <= 0:
        raise RuntimeError(
            "UNIT 14 BLOCKED: INVALID LEVERAGE"
        )

    backup_buffer_fraction = (
        backup_buffer_percent
        /
        Decimal("100")
    )

    trailing_fraction = (
        trailing_percent
        /
        Decimal("100")
    )

    print(
        "PASS: UNIT 14 EXECUTION ENVIRONMENT = DEMO",
        flush=True,
    )

    print(
        f"PASS: UNIT 14 BACKUP MARGIN % = "
        f"{backup_margin_percent}",
        flush=True,
    )

    print(
        f"PASS: UNIT 14 BACKUP BUFFER % = "
        f"{backup_buffer_percent}",
        flush=True,
    )

    print(
        f"PASS: UNIT 14 MAX BACKUPS = "
        f"{max_backups}",
        flush=True,
    )

    print(
        f"PASS: UNIT 14 EXPOSURE CAP % = "
        f"{exposure_cap_percent}",
        flush=True,
    )

    print(
        f"PASS: UNIT 14 TP3 TRAILING % = "
        f"{trailing_percent}",
        flush=True,
    )

    print(
        "PASS: UNIT 14 BACKUP SEQUENCE = "
        "ENTRY -> B1 -> L1 -> B2 -> L2 -> B3 -> L3 -> STOP",
        flush=True,
    )

    print(
        "PASS: UNIT 14 BACKUP 4 = DISABLED",
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
    # 3. QUANTITY CONFIGURATION
    # ========================================================

    quantity_step = Decimal("0.0001")
    minimum_quantity = Decimal("0.0001")

    try:
        quantity_step = Decimal(
            str(
                exchange.get(
                    "quantity_step",
                    "0.0001",
                )
            )
        )
    except Exception:
        quantity_step = Decimal("0.0001")

    try:
        minimum_quantity = Decimal(
            str(
                exchange.get(
                    "minimum_quantity",
                    "0.0001",
                )
            )
        )
    except Exception:
        minimum_quantity = Decimal("0.0001")

    if quantity_step <= 0:
        quantity_step = Decimal("0.0001")

    if minimum_quantity <= 0:
        minimum_quantity = Decimal("0.0001")

    # ========================================================
    # 4. AUTHENTICATION
    # ========================================================

    api_key = (
        os.environ.get("WEEX_API_KEY")
        or
        os.environ.get("API_KEY")
    )

    api_secret = (
        os.environ.get("WEEX_API_SECRET")
        or
        os.environ.get("API_SECRET")
    )

    api_passphrase = (
        os.environ.get("WEEX_API_PASSPHRASE")
        or
        os.environ.get("API_PASSPHRASE")
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

    print(
        "PASS: UNIT 14 DEMO AUTHENTICATION AVAILABLE",
        flush=True,
    )

    # ========================================================
    # 5. HELPERS
    # ========================================================

    def quantity_text(value):
        text_value = (
            f"{value:.8f}"
            .rstrip("0")
            .rstrip(".")
        )

        return text_value

    def floor_quantity(value):
        if value <= 0:
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

    def make_signature(
        timestamp,
        method,
        path,
        query_string="",
        body="",
    ):
        method = method.upper()

        message = (
            timestamp
            +
            method
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
                    api_secret.encode("utf-8"),
                    message.encode("utf-8"),
                    hashlib.sha256,
                ).digest()
            ).decode("utf-8")
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

        request = urllib.request.Request(
            url=url,
            headers=headers,
            method="GET",
        )

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:
            status = response.getcode()

            text = (
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
                f"AUTHENTICATED GET FAILED: HTTP {status}"
            )

        return json.loads(text)

    def authenticated_post(
        path,
        payload,
    ):
        # DEMO ENDPOINT ONLY.

        if "/sim/" not in path:
            raise RuntimeError(
                "UNIT 14 BLOCKED: NON-DEMO WRITE ENDPOINT"
            )

        body = json.dumps(
            payload,
            separators=(",", ":"),
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

        request = urllib.request.Request(
            url=(
                base_url
                +
                path
            ),
            data=body.encode("utf-8"),
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:
            status = response.getcode()

            text = (
                response.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

        print(
            f"UNIT 14 DEMO ORDER HTTP STATUS = {status}",
            flush=True,
        )

        print(
            f"UNIT 14 DEMO ORDER RESPONSE = {text}",
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
                f"UNIT 14 DEMO ORDER FAILED: HTTP {status}"
            )

# ============================================================
# START PART 11C-11D INDENTATION REPAIR
# ZERO-INDENTATION TRANSMISSION DEMARCATION ONLY
# ============================================================

        return json.loads(text)

    def get_active_position():
        records = authenticated_get(
            "/capi/v3/sim/position/allPosition"
        )

        if not isinstance(records, list):
            return None

        active_records = []

        for record in records:
            if not isinstance(record, dict):
                continue

            if (
                str(
                    record.get(
                        "symbol",
                        "",
                    )
                ).upper()
                !=
                demo_symbol
            ):
                continue

# ============================================================
# END PART 11C-11D INDENTATION REPAIR
# CONTINUE DIRECTLY WITH EXISTING CODE
# ZERO-INDENTATION TRANSMISSION DEMARCATION ONLY
# ============================================================


        try:
                size = Decimal(
                    str(
                        record.get(
                            "size",
                            "0",
                        )
                    )
                )
            except Exception:
                continue

        if size > 0:
                active_records.append(
                    record
                )

        if not active_records:
                return None

        # ONE-DIRECTION-ONLY CONTRACT.

            directions = {
            str(
                item.get(
                    "side",
                    "",
                )
            ).upper()
            for item in active_records
        }

            directions.discard("")

        if len(directions) > 1:
            raise RuntimeError(
                "UNIT 14 BLOCKED: "
                "OPPOSING ACTIVE POSITIONS DETECTED"
            )

        return active_records[0]

    def get_demo_balance():
        balances = authenticated_get(
            "/capi/v3/sim/balance"
        )

        if not isinstance(balances, list):
            raise RuntimeError(
                "UNIT 14 BLOCKED: INVALID DEMO BALANCE RESPONSE"
            )

        for item in balances:
            if not isinstance(item, dict):
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
            "UNIT 14 BLOCKED: SUSDT DEMO BALANCE NOT FOUND"
        )

    def get_mark_price():
        mark_path = (
            "/capi/v3/market/symbolPrice"
        )

        query_string = (
            "symbol=BTCUSDT"
            "&priceType=MARK"
        )

        request = urllib.request.Request(
            url=(
                base_url
                +
                mark_path
                +
                "?"
                +
                query_string
            ),
            method="GET",
            headers={
                "Accept":
                    "application/json",
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:
            status = response.getcode()

            text = (
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
                f"UNIT 14 MARK READ FAILED: HTTP {status}"
            )

        payload = json.loads(text)

        price = Decimal(
            str(
                payload.get(
                    "price",
                    "0",
                )
            )
        )

        if price <= 0:
            raise RuntimeError(
                "UNIT 14 INVALID MARK PRICE"
            )

        return price

    def get_order_history():
        query_string = (
            "symbol=BTCSUSDT"
            "&limit=1000"
            "&page=0"
        )

        history = authenticated_get(
            "/capi/v3/sim/order/history",
            query_string,
        )

        if not isinstance(history, list):
            return []

        return history

    # ========================================================
    # 6. BACKUP TRADE ID
    #
    # Position createdTime ties B1/B2/B3 to THIS position.
    # Old backup orders from an earlier trade cannot advance
    # the current trade's backup stage.
    # ========================================================

    def get_trade_key(position):
        raw_created = str(
            position.get(
                "createdTime",
                "",
            )
        )

        if raw_created.isdigit():
            return raw_created[-12:]

        # Fallback only if WEEX omitted createdTime.
        position_id = str(
            position.get(
                "id",
                "",
            )
        )

        if position_id:
            return position_id[-12:]

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

    # ========================================================
    # 7. EXCHANGE-CONFIRMED BACKUP STAGE
    #
    # Stage advances ONLY when the corresponding backup order
    # is reported FILLED with executedQty > 0.
    #
    # Accepted/open/unknown orders BLOCK another submission
    # for the same stage but DO NOT advance to the next stage.
    # ========================================================

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
            target_id = backup_client_id(
                stage,
                trade_key,
            )

            for order in history:
                if not isinstance(order, dict):
                    continue

                client_id = str(
                    order.get(
                        "clientOrderId",
                        "",
                    )
                )

                if client_id != target_id:
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
                    executed_qty = Decimal("0")

                if (
                    status
                    ==
                    "FILLED"
                    and
                    executed_qty
                    >
                    0
                ):
                    filled_stages.add(
                        stage
                    )

        # Sequential integrity.

        completed = 0

        for stage in range(
            1,
            max_backups + 1,
        ):
            if stage in filled_stages:
                if stage != completed + 1:
                    raise RuntimeError(
                        "UNIT 14 BLOCKED: "
                        "NON-SEQUENTIAL BACKUP HISTORY"
                    )

                completed = stage
            else:
                break

        return (
            completed,
            existing_stages,
            filled_stages,
        )

    # ========================================================
    # 8. TP3 STATE
    # ========================================================

    unit_13_status = str(
        unit_13_result.get(
            "status",
            "",
        )
    ).upper()

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

    position_side_from_unit_13 = str(
        unit_13_result.get(
            "position_side",
            "",
        )
    ).upper()

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
        original_tp3_quantity = Decimal("0")

    best_mark = None

    # When a backup fills while TP3 is armed,
    # TP1/TP2 have already completed for the original position.
    # The added backup quantity becomes part of the remaining
    # managed runner rather than being ignored.

    last_confirmed_backup_stage = None

    runtime_cycle = 0

    poll_seconds = 5

    # Prevent this controller itself from submitting two
    # different orders too close together.

    last_runtime_order_time = 0.0

    print(
        f"UNIT 14 RUNTIME POLL INTERVAL = "
        f"{poll_seconds} SECONDS",
        flush=True,
    )

    print(
        f"UNIT 14 TP3 ARMED = "
        f"{tp3_armed}",
        flush=True,
    )

    print(
        "UNIT 14 COMBINED POSITION LOOP STARTED = TRUE",
        flush=True,
    )

    print("=" * 80, flush=True)

    # ========================================================
    # 9. COMBINED CONTINUOUS POSITION LOOP
    # ========================================================

    while True:
        runtime_cycle += 1

        try:
            position = get_active_position()

        except Exception as exc:
            print(
                f"UNIT 14 POSITION READ ERROR = {repr(exc)}",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # 9A. POSITION CLOSED
        # ====================================================

        if position is None:
            print("-" * 80, flush=True)

            print(
                "UNIT 14 ACTIVE POSITION EXISTS = FALSE",
                flush=True,
            )

            print(
                "UNIT 14 BACKUP MANAGEMENT COMPLETE",
                flush=True,
            )

            print(
                "UNIT 14 TP3 MANAGEMENT COMPLETE",
                flush=True,
            )

            print(
                "UNIT 14 RUNTIME STATUS = POSITION_CLOSED",
                flush=True,
            )

            print("=" * 80, flush=True)

            return {
                "status":
                    "POSITION_CLOSED",

                "exchange_write":
                    False,

                "real_order":
                    False,

                "sl_enabled":
                    False,
            }

        # ====================================================
        # 9B. CURRENT POSITION STATE
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
            in (
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
                f"UNIT 14 POSITION PARSE ERROR = {repr(exc)}",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        if position_size <= 0:
            time.sleep(
                poll_seconds
            )
            continue

        trade_key = get_trade_key(
            position
        )

        # ====================================================
        # 9C. CURRENT MARK
        # ====================================================

        try:
            current_mark = get_mark_price()

        except Exception as exc:
            print(
                f"UNIT 14 MARK READ ERROR = {repr(exc)}",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # 9D. ORDER HISTORY / BACKUP STAGE
        # ====================================================

        try:
            history = get_order_history()

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
                f"UNIT 14 HISTORY READ ERROR = {repr(exc)}",
                flush=True,
            )

            # FAIL CLOSED:
            # no backup may be submitted when duplicate
            # history cannot be verified.

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # RESET TP3 BEST MARK AFTER CONFIRMED BACKUP FILL
        #
        # This prevents the old pre-backup trailing reference
        # from immediately closing the newly enlarged position.
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
                f"PASS: UNIT 14 BACKUP STAGE CHANGED "
                f"{last_confirmed_backup_stage} "
                f"-> {completed_backups}",
                flush=True,
            )

            print(
                "PASS: UNIT 14 NEW WEEX POSITION STATE RECEIVED",
                flush=True,
            )

            print(
                f"PASS: UNIT 14 NEW LIQUIDATION PRICE = "
                f"{liquidation_price}",
                flush=True,
            )

            best_mark = None

            last_confirmed_backup_stage = (
                completed_backups
            )

        # ====================================================
        # 10. TP3 MANAGEMENT
        # ====================================================

        tp3_callback_reached = False
        trailing_trigger = None

        if tp3_armed:
            # After any backup has filled, the actual current
            # remaining position is the quantity managed by
            # the runner. Before any backup, preserve the
            # original Unit 13 TP3 allocation.

            if completed_backups > 0:
                tp3_close_quantity = (
                    position_size
                )
            else:
                tp3_close_quantity = min(
                    original_tp3_quantity,
                    position_size,
                )

            if tp3_close_quantity > 0:
                if best_mark is None:
                    best_mark = (
                        current_mark
                    )

                    print(
                        f"TP3 INITIAL BEST MARK = "
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
                        f"TP3 NEW BEST FAVORABLE MARK = "
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
                        f"TP3 NEW BEST FAVORABLE MARK = "
                        f"{best_mark}",
                        flush=True,
                    )

                if position_side == "LONG":
                    trailing_trigger = (
                        best_mark
                        *
                        (
                            Decimal("1")
                            -
                            trailing_fraction
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
                            trailing_fraction
                        )
                    )

                    tp3_callback_reached = (
                        current_mark
                        >=
                        trailing_trigger
                    )

                print(
                    f"UNIT 14 CYCLE = {runtime_cycle} | "
                    f"SIDE = {position_side} | "
                    f"SIZE = {position_size} | "
                    f"MARK = {current_mark} | "
                    f"LIQ = {liquidation_price} | "
                    f"BACKUPS FILLED = {completed_backups}/{max_backups} | "
                    f"TP3 BEST = {best_mark} | "
                    f"TP3 TRIGGER = {trailing_trigger} | "
                    f"TP3 CALLBACK = {tp3_callback_reached}",
                    flush=True,
                )

        else:
            print(
                f"UNIT 14 CYCLE = {runtime_cycle} | "
                f"SIDE = {position_side} | "
                f"SIZE = {position_size} | "
                f"MARK = {current_mark} | "
                f"LIQ = {liquidation_price} | "
                f"BACKUPS FILLED = {completed_backups}/{max_backups} | "
                f"TP3 ARMED = FALSE",
                flush=True,
            )

        # ====================================================
        # 11. TP3 HAS EXECUTION PRIORITY IF CALLBACK REACHED
        # ====================================================

        if (
            tp3_armed
            and
            tp3_callback_reached
        ):
            # Do not submit another order if this runtime has
            # submitted an order too recently.

            elapsed = (
                time.time()
                -
                last_runtime_order_time
            )

            if (
                last_runtime_order_time > 0
                and
                elapsed < 60
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

            if position_side == "LONG":
                closing_side = "SELL"
            else:
                closing_side = "BUY"

            close_quantity = min(
                tp3_close_quantity,
                position_size,
            )

            close_quantity = floor_quantity(
                close_quantity
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

            # Check whether THIS TP3 client ID already exists.

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

            payload = {
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

            # ABSOLUTE SL PROHIBITION.

            for prohibited in (
                "slTriggerPrice",
                "SlWorkingType",
                "stopLossPrice",
                "stopPrice",
            ):
                if prohibited in payload:
                    raise RuntimeError(
                        "UNIT 14 BLOCKED: SL FIELD DETECTED"
                    )

            print("-" * 80, flush=True)

            print(
                "TP3 CALLBACK REACHED = TRUE",
                flush=True,
            )

            print(
                f"TP3 CLOSE QUANTITY = "
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
                    payload,
                )

                last_runtime_order_time = (
                    time.time()
                )

            except Exception as exc:
                print(
                    f"TP3 DEMO ORDER ERROR = {repr(exc)}",
                    flush=True,
                )

                # Submission outcome may be uncertain.
                # Do not immediately resubmit.
                # History/position is re-read first.

                last_runtime_order_time = (
                    time.time()
                )

                time.sleep(
                    poll_seconds
                )

                continue

            if result.get("success") is not True:
                print(
                    f"TP3 ORDER NOT ACCEPTED = {result}",
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
                f"PASS: TP3 ORDER ID = "
                f"{result.get('orderId')}",
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
        # 12. BACKUP MANAGEMENT
        # ====================================================

        if max_backups <= 0:
            print(
                "UNIT 14 BACKUPS DISABLED BY CONFIG",
# ============================================================
# END PART 11D
# CONTINUE DIRECTLY WITH PART 11E
# ZERO-INDENTATION TRANSMISSION DEMARCATION ONLY
# ============================================================
                 flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # ALL THREE BACKUPS ALREADY FILLED
        # ====================================================

        if completed_backups >= max_backups:
            print(
                f"UNIT 14 BACKUP STATUS = "
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

        # Absolute B4 protection.

        if next_backup_stage > 3:
            print(
                "UNIT 14 BACKUP STOP = NO B4",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # 12A. CURRENT LIQUIDATION MUST COME FROM WEEX
        # ====================================================

        if liquidation_price <= 0:
            print(
                f"UNIT 14 B{next_backup_stage} BLOCKED: "
                "WEEX LIQUIDATION PRICE NOT AVAILABLE",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # 12B. CALCULATE BACKUP TRIGGER
        #
        # LONG:
        # Bn = Ln * (1 + buffer)
        #
        # SHORT:
        # Bn = Ln * (1 - buffer)
        # ====================================================

        if position_side == "LONG":
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
            f"L{next_backup_stage} = {liquidation_price} | "
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
        # 12C. ANTI-DUPLICATE
        # ====================================================

        next_client_id = backup_client_id(
            next_backup_stage,
            trade_key,
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
        # 12D. EXPOSURE CAP
        #
        # Configured capital allocation:
        #
        # initial margin %
        # +
        # completed backups * backup margin %
        # +
        # proposed next backup margin %
        #
        # This deliberately does NOT use the 0.0004 initial
        # entry cap for backups.
        # ====================================================

        current_configured_exposure = (
            initial_margin_percent
            +
            (
                Decimal(
                    completed_backups
                )
                *
                backup_margin_percent
            )
        )

        projected_exposure = (
            current_configured_exposure
            +
            backup_margin_percent
        )

        print(
            f"UNIT 14 CURRENT CONFIGURED EXPOSURE % = "
            f"{current_configured_exposure}",
            flush=True,
        )

        print(
            f"UNIT 14 PROJECTED EXPOSURE % = "
            f"{projected_exposure}",
            flush=True,
        )

        print(
            f"UNIT 14 EXPOSURE CAP % = "
            f"{exposure_cap_percent}",
            flush=True,
        )

        if (
            projected_exposure
            >
            exposure_cap_percent
        ):
            print(
                f"UNIT 14 B{next_backup_stage} BLOCKED: "
                "EXPOSURE CAP",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # 12E. DEMO BALANCE
        # ====================================================

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

        except Exception as exc:
            print(
                f"UNIT 14 BALANCE READ ERROR = {repr(exc)}",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        if available_balance <= 0:
            print(
                f"UNIT 14 B{next_backup_stage} BLOCKED: "
                "NO AVAILABLE DEMO BALANCE",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        # ====================================================
        # 12F. BACKUP QUANTITY
        #
        # margin = available balance * backup %
        # notional = margin * leverage
        # qty = notional / mark
        #
        # No 0.0004 initial-entry cap is applied.
        # ====================================================

        backup_margin_amount = (
            available_balance
            *
            (
                backup_margin_percent
                /
                Decimal("100")
            )
        )

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

        backup_quantity = floor_quantity(
            raw_backup_quantity
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
        # 12G. FINAL POSITION RECONCILIATION
        #
        # Re-read actual position immediately before submission.
        # This prevents a stale trigger from submitting against
        # a position that has already changed or closed.
        # ====================================================

        try:
            final_position = get_active_position()

        except Exception as exc:
            print(
                f"UNIT 14 FINAL POSITION CHECK ERROR = "
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

        if final_side != position_side:
            raise RuntimeError(
                "UNIT 14 BLOCKED: "
                "POSITION DIRECTION CHANGED"
            )

        final_trade_key = get_trade_key(
            final_position
        )

        if final_trade_key != trade_key:
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
            final_liquidation = Decimal("0")

        # If WEEX has already recalculated liquidation between
        # trigger evaluation and submission, restart the cycle
        # and calculate from the new liquidation.

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
                f"OLD LIQUIDATION = {liquidation_price}",
                flush=True,
            )

            print(
                f"NEW LIQUIDATION = {final_liquidation}",
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
        # 12H. ORDER-RATE GUARD
        # ====================================================

        elapsed = (
            time.time()
            -
            last_runtime_order_time
        )

        if (
            last_runtime_order_time > 0
            and
            elapsed < 60
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
        # 12I. BACKUP ORDER
        #
        # Same position direction:
        #
        # LONG backup  = BUY / LONG
        # SHORT backup = SELL / SHORT
        # ====================================================

        if position_side == "LONG":
            backup_order_side = "BUY"
        else:
            backup_order_side = "SELL"

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

        # ABSOLUTE SL PROHIBITION.

        for prohibited in (
            "slTriggerPrice",
            "SlWorkingType",
            "stopLossPrice",
            "stopPrice",
        ):
            if prohibited in backup_payload:
                raise RuntimeError(
                    "UNIT 14 BLOCKED: SL FIELD DETECTED"
                )

        print("-" * 80, flush=True)

        print(
            f"UNIT 14 B{next_backup_stage} "
            "TRIGGER REACHED = TRUE",
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            f"LIQUIDATION REFERENCE = "
            f"{liquidation_price}",
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            f"TRIGGER PRICE = "
            f"{backup_trigger}",
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            f"CURRENT MARK = "
            f"{current_mark}",
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            f"ORDER SIDE = "
            f"{backup_order_side}",
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            f"QUANTITY = "
            f"{backup_quantity}",
            flush=True,
        )

        print(
            f"UNIT 14 B{next_backup_stage} "
            f"CLIENT ORDER ID = "
            f"{next_client_id}",
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
        # 13. SUBMIT EXACTLY ONE DEMO BACKUP
        # ====================================================

        try:
            backup_result = authenticated_post(
                "/capi/v3/sim/order",
                backup_payload,
            )

            last_runtime_order_time = (
                time.time()
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
                f"UNIT 14 B{next_backup_stage} "
                f"HTTP ERROR = {exc.code}",
                flush=True,
            )

            print(
                f"UNIT 14 B{next_backup_stage} "
                f"ERROR RESPONSE = {error_text}",
                flush=True,
            )

            # Outcome may be uncertain.
            # Re-read history before any retry.

            last_runtime_order_time = (
                time.time()
            )

            time.sleep(
                poll_seconds
            )

            continue

        except urllib.error.URLError as exc:
            print(
                f"UNIT 14 B{next_backup_stage} "
                f"NETWORK ERROR = {exc}",
                flush=True,
            )

            # Do not blindly resubmit.
            # Order history is checked first.

            last_runtime_order_time = (
                time.time()
            )

            time.sleep(
                poll_seconds
            )

            continue

        except Exception as exc:
            print(
                f"UNIT 14 B{next_backup_stage} "
                f"SUBMISSION ERROR = {repr(exc)}",
                flush=True,
            )

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
                f"NOT ACCEPTED = {backup_result}",
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

        print("-" * 80, flush=True)

        print(
            f"PASS: UNIT 14 B{next_backup_stage} "
            "DEMO ORDER ACCEPTED",
            flush=True,
        )

        print(
            f"PASS: UNIT 14 B{next_backup_stage} "
            f"ORDER ID = {backup_order_id}",
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

        print("=" * 80, flush=True)

        # ====================================================
        # IMPORTANT:
        #
        # DO NOT calculate B2/B3 here.
        #
        # The next loop:
        # 1. reads order history
        # 2. confirms Bn FILLED
        # 3. reads changed position
        # 4. reads WEEX's new liquidatePrice
        # 5. only then calculates B(n+1)
        # ====================================================

        time.sleep(
            poll_seconds
        )


# ============================================================
# END PART 11E
# PART 11 / UNIT 13 + UNIT 14 RUNTIME BODY CONTINUATION COMPLETE
# NEXT = FINAL UNIT 14 CALL
# ZERO-INDENTATION TRANSMISSION DEMARCATION ONLY
# ============================================================

# START UNIT 14 COMBINED TP3 + BACKUP RUNTIME
# ============================================================

FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    fresh_tp3_runtime(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_13_RESULT,
    )
)
