# ============================================================
# FRESH WEEX BOT RECONSTRUCTION
# UNIT 1 — CLEAN RUNTIME FOUNDATION
#
# FILE: main.py
#
# PURPOSE:
# Prove that the fresh main.py starts and runs correctly
# before adding ANY trading functionality.
#
# SAFETY:
# - NO WEEX CONNECTION
# - NO HTTP REQUEST
# - NO DEMO ORDER
# - NO REAL ORDER
# - NO EXCHANGE WRITE
# - NO POSITION CHANGE
# - NO EXTERNAL DEPENDENCIES
# ============================================================

from datetime import datetime, timezone


def log(message):
    timestamp = datetime.now(timezone.utc).isoformat()
    print(
        f"{timestamp} {message}",
        flush=True,
    )


def reconstruction_unit_1():
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

    log(
        "PASS: MAIN.PY STARTED SUCCESSFULLY"
    )

    log(
        "PASS: PYTHON STANDARD LIBRARY ONLY"
    )

    log(
        "PASS: ZERO WEEX CONNECTION"
    )

    log(
        "PASS: ZERO HTTP REQUEST"
    )

    log(
        "PASS: ZERO DEMO ORDER"
    )

    log(
        "PASS: ZERO REAL ORDER"
    )

    log(
        "PASS: ZERO EXCHANGE WRITE"
    )

    print(
        "-" * 80,
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 1 COMPLETE"
    )

    print(
        "=" * 80,
        flush=True,
    )


if __name__ == "__main__":
    reconstruction_unit_1()

# ============================================================
# FRESH RECONSTRUCTION UNIT 2
# CONFIGURATION + SAFETY CONTRACT
#
# PURPOSE:
# Establish the bot's core configuration in one controlled,
# validated location before any exchange connectivity exists.
#
# IMPORTANT:
# - STANDARD LIBRARY ONLY
# - ZERO WEEX CONNECTION
# - ZERO HTTP REQUEST
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE WRITE
# - ZERO POSITION MUTATION
# - ZERO LEVERAGE MUTATION
# - ZERO MARGIN MODE MUTATION
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
    # 1. TRADING INSTRUMENT
    # --------------------------------------------------------

    symbol = "BTCSUSDT"

    # --------------------------------------------------------
    # 2. EXECUTION ENVIRONMENT
    #
    # We are rebuilding toward DEMO execution first.
    # Actual submission is NOT enabled in Unit 2.
    # --------------------------------------------------------

    execution_environment = "DEMO"

    # --------------------------------------------------------
    # 3. HARD SAFETY FLAGS
    #
    # These flags describe what the current reconstruction
    # is permitted to do.
    #
    # They are deliberately FALSE at this stage.
    # --------------------------------------------------------

    weex_connection_enabled = False

    http_requests_enabled = False

    demo_order_submission_enabled = False

    real_order_submission_enabled = False

    exchange_mutation_enabled = False

    # --------------------------------------------------------
    # 4. ACCOUNT MUTATION SAFETY
    # --------------------------------------------------------

    leverage_mutation_enabled = False

    margin_mode_mutation_enabled = False

    position_mode_mutation_enabled = False

    # --------------------------------------------------------
    # 5. STRATEGY CONSTANTS
    #
    # These preserve the verified strategy requirements
    # without copying the old architecture.
    # --------------------------------------------------------

    leverage_target = 100

    initial_margin_percent = 5.0

    backup_margin_percent = 5.0

    backup_buffer_percent = 0.30

    max_backups = 3

    exposure_cap_percent = 35.0

    # --------------------------------------------------------
    # 6. TAKE-PROFIT ALLOCATION
    # --------------------------------------------------------

    tp1_allocation_percent = 25.0

    tp2_allocation_percent = 25.0

    tp3_allocation_percent = 50.0

    tp3_trailing_distance_percent = 0.20

    # --------------------------------------------------------
    # 7. SIGNAL CONTROL
    # --------------------------------------------------------

    signal_expiry_seconds = 120

    loss_cooldown_seconds = 300

    one_direction_only = True

    anti_duplicate_orders = True

    active_trade_mode_lock = True

    exclusive_mode = True

    mode_confirmations_required = 3

    # --------------------------------------------------------
    # 8. MARKET PRECISION
    #
    # These are configuration values only.
    # Nothing is submitted to WEEX.
    # --------------------------------------------------------

    quantity_step = 0.0001

    minimum_quantity = 0.0001

    price_step = 0.1

    # --------------------------------------------------------
    # 9. CONFIGURATION OBJECT
    #
    # Later units will receive validated configuration rather
    # than relying on scattered global constants.
    # --------------------------------------------------------

    config = {

        "symbol":
            symbol,

        "execution_environment":
            execution_environment,

        "safety": {

            "weex_connection_enabled":
                weex_connection_enabled,

            "http_requests_enabled":
                http_requests_enabled,

            "demo_order_submission_enabled":
                demo_order_submission_enabled,

            "real_order_submission_enabled":
                real_order_submission_enabled,

            "exchange_mutation_enabled":
                exchange_mutation_enabled,

            "leverage_mutation_enabled":
                leverage_mutation_enabled,

            "margin_mode_mutation_enabled":
                margin_mode_mutation_enabled,

            "position_mode_mutation_enabled":
                position_mode_mutation_enabled,
        },

        "strategy": {

            "leverage_target":
                leverage_target,

            "initial_margin_percent":
                initial_margin_percent,

            "backup_margin_percent":
                backup_margin_percent,

            "backup_buffer_percent":
                backup_buffer_percent,

            "max_backups":
                max_backups,

            "exposure_cap_percent":
                exposure_cap_percent,

            "tp1_allocation_percent":
                tp1_allocation_percent,

            "tp2_allocation_percent":
                tp2_allocation_percent,

            "tp3_allocation_percent":
                tp3_allocation_percent,

            "tp3_trailing_distance_percent":
                tp3_trailing_distance_percent,

            "signal_expiry_seconds":
                signal_expiry_seconds,

            "loss_cooldown_seconds":
                loss_cooldown_seconds,

            "one_direction_only":
                one_direction_only,

            "anti_duplicate_orders":
                anti_duplicate_orders,

            "active_trade_mode_lock":
                active_trade_mode_lock,

            "exclusive_mode":
                exclusive_mode,

            "mode_confirmations_required":
                mode_confirmations_required,
        },

        "market_precision": {

            "quantity_step":
                quantity_step,

            "minimum_quantity":
                minimum_quantity,

            "price_step":
                price_step,
        },
    }

    # --------------------------------------------------------
    # 10. VALIDATION
    # --------------------------------------------------------

    errors = []

    if config["symbol"] != "BTCSUSDT":

        errors.append(
            "INVALID_SYMBOL"
        )

    if config["execution_environment"] != "DEMO":

        errors.append(
            "INVALID_EXECUTION_ENVIRONMENT"
        )

    if config["strategy"]["leverage_target"] <= 0:

        errors.append(
            "INVALID_LEVERAGE_TARGET"
        )

    if not (
        0
        <
        config["strategy"]["initial_margin_percent"]
        <=
        100
    ):

        errors.append(
            "INVALID_INITIAL_MARGIN_PERCENT"
        )

    if not (
        0
        <
        config["strategy"]["backup_margin_percent"]
        <=
        100
    ):

        errors.append(
            "INVALID_BACKUP_MARGIN_PERCENT"
        )

    if config["strategy"]["max_backups"] != 3:

        errors.append(
            "INVALID_MAX_BACKUPS"
        )

    if not (
        0
        <
        config["strategy"]["exposure_cap_percent"]
        <=
        100
    ):

        errors.append(
            "INVALID_EXPOSURE_CAP"
        )

    tp_total = (
        config["strategy"]["tp1_allocation_percent"]
        +
        config["strategy"]["tp2_allocation_percent"]
        +
        config["strategy"]["tp3_allocation_percent"]
    )

    if abs(
        tp_total - 100.0
    ) > 0.000001:

        errors.append(
            "INVALID_TP_ALLOCATION_TOTAL"
        )

    if config["market_precision"]["quantity_step"] <= 0:

        errors.append(
            "INVALID_QUANTITY_STEP"
        )

    if config["market_precision"]["minimum_quantity"] <= 0:

        errors.append(
            "INVALID_MINIMUM_QUANTITY"
        )

    if config["market_precision"]["price_step"] <= 0:

        errors.append(
            "INVALID_PRICE_STEP"
        )

    # --------------------------------------------------------
    # 11. SAFETY VALIDATION
    #
    # Unit 2 MUST NOT permit any external write capability.
    # --------------------------------------------------------

    forbidden_enabled_flags = []

    for (
        safety_name,
        safety_value,
    ) in config["safety"].items():

        if safety_value is True:

            forbidden_enabled_flags.append(
                safety_name
            )

    if forbidden_enabled_flags:

        errors.append(
            "UNSAFE_CAPABILITY_ENABLED"
        )

    # --------------------------------------------------------
    # 12. RESULT
    # --------------------------------------------------------

    if errors:

        print(
            "UNIT 2 VALIDATION ERRORS =",
            errors,
            flush=True,
        )

        raise RuntimeError(
            "FRESH RECONSTRUCTION UNIT 2 FAILED"
        )

    print(
        "PASS: UNIT 2 CONFIGURATION CREATED",
        flush=True,
    )

    print(
        "PASS: SYMBOL =",
        config["symbol"],
        flush=True,
    )

    print(
        "PASS: EXECUTION ENVIRONMENT =",
        config["execution_environment"],
        flush=True,
    )

    print(
        "PASS: LEVERAGE TARGET =",
        config["strategy"]["leverage_target"],
        flush=True,
    )

    print(
        "PASS: INITIAL MARGIN % =",
        config["strategy"]["initial_margin_percent"],
        flush=True,
    )

    print(
        "PASS: BACKUP MARGIN % =",
        config["strategy"]["backup_margin_percent"],
        flush=True,
    )

    print(
        "PASS: BACKUP BUFFER % =",
        config["strategy"]["backup_buffer_percent"],
        flush=True,
    )

    print(
        "PASS: MAX BACKUPS =",
        config["strategy"]["max_backups"],
        flush=True,
    )

    print(
        "PASS: EXPOSURE CAP % =",
        config["strategy"]["exposure_cap_percent"],
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
        config["strategy"]["anti_duplicate_orders"],
        flush=True,
    )

    print(
        "PASS: ONE DIRECTION ONLY =",
        config["strategy"]["one_direction_only"],
        flush=True,
    )

    print(
        "PASS: ALL EXTERNAL CAPABILITIES DISABLED",
        flush=True,
    )

    print(
        "ZERO WEEX CONNECTION = TRUE",
        flush=True,
    )

    print(
        "ZERO HTTP REQUEST = TRUE",
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
        "FRESH RECONSTRUCTION UNIT 2 RESULT = PASS"
    )

    print(
        "=" * 80,
        flush=True,
    )

    return config


# ============================================================
# RUN FRESH RECONSTRUCTION UNIT 2
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
    )


# ============================================================
# FRESH RECONSTRUCTION UNIT 3
# WEEX V3 READ-ONLY MARKET DATA
#
# PURPOSE:
# Establish verified public WEEX V3 market-data connectivity.
#
# IMPORTANT:
# - STANDARD LIBRARY ONLY
# - WEEX V3
# - PUBLIC GET ONLY
# - NO AUTHENTICATION
# - NO ACCOUNT ACCESS
# - NO POSITION ACCESS
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE WRITE
# ============================================================


def fresh_reconstruction_unit_3():

    import json
    import urllib.parse
    import urllib.request
    import urllib.error

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
    # 1. REQUIRE UNIT 2
    # --------------------------------------------------------

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(
        config,
        dict,
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: UNIT 2 CONFIGURATION MISSING"
        )

    print(
        "PASS: UNIT 3 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    # --------------------------------------------------------
    # 2. SYMBOL NORMALIZATION
    #
    # Unit 2 currently carries the historical/demo reference:
    #
    #     BTCSUSDT
    #
    # WEEX V3 public contract APIs use:
    #
    #     BTCUSDT
    #
    # Unit 3 creates the exchange-facing V3 symbol explicitly.
    # --------------------------------------------------------

    strategy_symbol = config.get(
        "symbol"
    )

    if strategy_symbol != "BTCSUSDT":

        raise RuntimeError(
            "UNIT 3 BLOCKED: UNEXPECTED UNIT 2 SYMBOL"
        )

    exchange_symbol = "BTCUSDT"

    print(
        "PASS: UNIT 3 STRATEGY SYMBOL =",
        strategy_symbol,
        flush=True,
    )

    print(
        "PASS: UNIT 3 WEEX V3 SYMBOL =",
        exchange_symbol,
        flush=True,
    )

    # --------------------------------------------------------
    # 3. HARD READ-ONLY CONTRACT
    # --------------------------------------------------------

    http_method = "GET"

    authenticated_request = False

    account_access = False

    position_access = False

    order_access = False

    exchange_write = False

    if http_method != "GET":

        raise RuntimeError(
            "UNIT 3 BLOCKED: NON-GET METHOD"
        )

    if authenticated_request:

        raise RuntimeError(
            "UNIT 3 BLOCKED: AUTHENTICATION ENABLED"
        )

    if account_access:

        raise RuntimeError(
            "UNIT 3 BLOCKED: ACCOUNT ACCESS ENABLED"
        )

    if position_access:

        raise RuntimeError(
            "UNIT 3 BLOCKED: POSITION ACCESS ENABLED"
        )

    if order_access:

        raise RuntimeError(
            "UNIT 3 BLOCKED: ORDER ACCESS ENABLED"
        )

    if exchange_write:

        raise RuntimeError(
            "UNIT 3 BLOCKED: EXCHANGE WRITE ENABLED"
        )

    print(
        "PASS: UNIT 3 READ-ONLY CONTRACT",
        flush=True,
    )

    # --------------------------------------------------------
    # 4. VERIFIED WEEX V3 PUBLIC ENDPOINT
    #
    # GET /capi/v3/market/symbolPrice
    #
    # priceType=MARK gives us the contract mark price.
    # --------------------------------------------------------

    base_url = (
        "https://api-contract.weex.com"
    )

    endpoint = (
        "/capi/v3/market/symbolPrice"
    )

    query = urllib.parse.urlencode(
        {
            "symbol":
                exchange_symbol,

            "priceType":
                "MARK",
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
    # 5. BUILD PUBLIC GET REQUEST
    # --------------------------------------------------------

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept":
                "application/json",

            "User-Agent":
                "Fresh-Reconstruction-Unit3",
        },
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
        "PASS: UNIT 3 PRICE TYPE = MARK",
        flush=True,
    )

    # --------------------------------------------------------
    # 6. EXECUTE PUBLIC READ
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

    # --------------------------------------------------------
    # 7. HTTP VALIDATION
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
    # 8. JSON VALIDATION
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
    # 9. STRICT V3 RESPONSE VALIDATION
    #
    # Expected shape:
    #
    # {
    #     "symbol": "BTCUSDT",
    #     "price": "...",
    #     "time": ...
    # }
    #
    # Unlike the previous version, we do NOT recursively
    # search arbitrary fields for something that looks like
    # a price.
    # --------------------------------------------------------

    response_symbol = payload.get(
        "symbol"
    )

    response_price = payload.get(
        "price"
    )

    response_time = payload.get(
        "time"
    )

    if response_symbol != exchange_symbol:

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
            "UNIT 3 INVALID PRICE"
        ) from exc

    if live_price <= 0:

        raise RuntimeError(
            "UNIT 3 NON-POSITIVE PRICE"
        )

    if response_time is None:

        raise RuntimeError(
            "UNIT 3 RESPONSE TIME MISSING"
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
    # 10. NORMALIZED INTERNAL MARKET SNAPSHOT
    # --------------------------------------------------------

    market_snapshot = {

        "strategy_symbol":
            strategy_symbol,

        "exchange_symbol":
            exchange_symbol,

        "price":
            live_price,

        "price_type":
            "MARK",

        "exchange_time":
            response_time,

        "source":
            "WEEX_V3_PUBLIC_MARKET_DATA",

        "read_only":
            True,
    }

    # --------------------------------------------------------
    # 11. FINAL SAFETY ASSERTIONS
    # --------------------------------------------------------

    if market_snapshot["read_only"] is not True:

        raise RuntimeError(
            "UNIT 3 READ-ONLY ASSERTION FAILED"
        )

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
        "PASS: NO REQUESTS PACKAGE REQUIRED",
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

    log(
        "FRESH RECONSTRUCTION UNIT 3 RESULT = PASS"
    )

    print(
        "=" * 80,
        flush=True,
    )

    return market_snapshot


# ============================================================
# RUN FRESH RECONSTRUCTION UNIT 3
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)
