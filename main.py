
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

# ============================================================
# START COMPLETE REPLACEMENT - UNIT 2
# ZERO INDENTATION - WEEX LEVERAGE ONLY
# ============================================================

def fresh_reconstruction_unit_2():
    print('=' * 80, flush=True)
    log('FRESH RECONSTRUCTION UNIT 2 START')
    print('-' * 80, flush=True)

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
        raise RuntimeError('UNIT 2 BLOCKED: UNIT 1 NOT READY')

    # ========================================================
    # 1. EXCHANGE CONFIGURATION
    # ========================================================

    exchange_name = 'WEEX'
    api_version = 'V3'
    contract_base_url = 'https://api-contract.weex.com'
    market_symbol = 'BTCUSDT'
    demo_order_symbol = 'BTCSUSDT'
    execution_environment = 'DEMO'

    # ========================================================
    # 2. UNIT-LOCAL SAFETY CONTRACT
    # ========================================================
    # These flags describe Unit 2 only.
    # They must NOT disable authorized demo execution
    # in later trading units.
    # ========================================================

    safety = {
        'public_market_data_read_enabled': True,
        'demo_account_balance_read_enabled': True,
        'authenticated_api_enabled': False,
        'account_access_enabled': False,
        'position_access_enabled': False,
        'order_endpoint_access_enabled': False,
        'demo_order_submission_enabled': False,
        'real_order_submission_enabled': False,
        'exchange_mutation_enabled': False,
        'leverage_mutation_enabled': False,
        'margin_mode_mutation_enabled': False,
        'position_mode_mutation_enabled': False,
    }

    # ========================================================
    # 3. STRATEGY CONFIGURATION
    # ========================================================
    # NO FIXED PYTHON LEVERAGE TARGET.
    #
    # WEEX exclusively controls LONG/SHORT leverage.
    #
    # Later units must read actual exchange leverage.
    # Never substitute an assumed leverage for
    # order sizing or ROI-dependent decisions.
    # ========================================================

    strategy = {
        'initial_margin_percent': 5.0,
        'initial_fixed_usdt': 0.50,

        'backup_margin_percent': 5.0,
        'backup_buffer_percent': 0.30,
        'max_backups': 5,
        'backup_multipliers': (
            1.0,
            1.5,
            2.0,
            2.5,
            3.0,
        ),

        'exposure_cap_percent': 35.0,
        'progressive_backup_funding': True,
        'full_ladder_reservation_required': False,

        'tp1_allocation_percent': 10.0,
        'tp2_allocation_percent': 20.0,
        'tp3_allocation_percent': 70.0,

        'tp1_net_roi_floor_percent': 5.0,
        'tp2_net_roi_floor_percent': 10.0,
        'tp1_tp2_min_roi_separation_percent': 5.0,

        'tp3_trailing_reference_percent': 0.20,
        'tp3_trailing_min_percent': 0.10,
        'tp3_trailing_max_percent': 0.40,

        'signal_expiry_seconds': 120,
        'loss_cooldown_seconds': 300,

        'one_direction_only': True,
        'anti_duplicate_orders': True,
        'active_trade_mode_lock': True,
        'exclusive_mode': True,
        'mode_confirmations_required': 3,
    }

    # ========================================================
    # 4. MARKET PRECISION
    # ========================================================

    market_precision = {
        'quantity_step': 0.0001,
        'minimum_quantity': 0.0001,
        'price_step': 0.1,
    }

    # ========================================================
    # 5. ORIGINAL DOWNSTREAM CONFIGURATION CONTRACT
    # ========================================================

    config = {
        'exchange': {
            'name': exchange_name,
            'api_version': api_version,
            'contract_base_url': contract_base_url,
            'market_symbol': market_symbol,
            'demo_order_symbol': demo_order_symbol,
        },

        'execution_environment': execution_environment,

        'safety': safety,

        'strategy': strategy,

        'market_precision': market_precision,
    }

    # ========================================================
    # 6. CONFIGURATION VALIDATION
    # ========================================================

    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    require(
        exchange_name == 'WEEX',
        'INVALID EXCHANGE'
    )

    require(
        api_version == 'V3',
        'INVALID API VERSION'
    )

    require(
        contract_base_url == 'https://api-contract.weex.com',
        'INVALID CONTRACT BASE URL'
    )

    require(
        market_symbol == 'BTCUSDT',
        'INVALID MARKET SYMBOL'
    )

    require(
        demo_order_symbol == 'BTCSUSDT',
        'INVALID DEMO SYMBOL'
    )

    require(
        execution_environment == 'DEMO',
        'REAL TRADING NOT ALLOWED'
    )

    require(
        0 < strategy['initial_margin_percent'] <= 5.0,
        'INVALID INITIAL MARGIN PERCENT'
    )

    require(
        strategy['initial_fixed_usdt'] > 0,
        'INVALID FIXED INITIAL MARGIN'
    )

    # ========================================================
    # 7. FIVE BACKUP VALIDATION
    # ========================================================

    require(
        strategy['max_backups'] == 5,
        'MAX BACKUPS MUST BE FIVE'
    )

    require(
        strategy['backup_multipliers']
        == (1.0, 1.5, 2.0, 2.5, 3.0),
        'INVALID BACKUP MULTIPLIERS'
    )

    require(
        0 < strategy['backup_margin_percent'] <= 5.0,
        'INVALID BACKUP MARGIN PERCENT'
    )

    require(
        strategy['backup_buffer_percent'] > 0,
        'INVALID BACKUP BUFFER'
    )

    require(
        strategy['progressive_backup_funding'] is True,
        'PROGRESSIVE FUNDING DISABLED'
    )

    require(
        strategy['full_ladder_reservation_required'] is False,
        'FULL LADDER RESERVATION MUST BE OFF'
    )

    require(
        0 < strategy['exposure_cap_percent'] <= 35.0,
        'EXPOSURE CAP EXCEEDS 35%'
    )

    # ========================================================
    # 8. TAKE PROFIT VALIDATION
    # ========================================================

    tp_total = sum(
        strategy[k]
        for k in (
            'tp1_allocation_percent',
            'tp2_allocation_percent',
            'tp3_allocation_percent'
        )
    )

    require(
        abs(tp_total - 100.0) <= 0.000001,
        'TP ALLOCATION MUST TOTAL 100%'
    )

    require(
        all(
            strategy[k] > 0
            for k in (
                'tp1_allocation_percent',
                'tp2_allocation_percent',
                'tp3_allocation_percent'
            )
        ),
        'INVALID TP ALLOCATION'
    )

    require(
        strategy['tp1_net_roi_floor_percent'] >= 5.0,
        'TP1 ROI FLOOR TOO LOW'
    )

    require(
        strategy['tp2_net_roi_floor_percent'] >= 10.0,
        'TP2 ROI FLOOR TOO LOW'
    )

    require(
        strategy['tp2_net_roi_floor_percent']
        > strategy['tp1_net_roi_floor_percent'],
        'TP2 MUST EXCEED TP1'
    )

    require(
        strategy['tp1_tp2_min_roi_separation_percent'] > 0,
        'INVALID TP SEPARATION'
    )

    require(
        0
        < strategy['tp3_trailing_min_percent']
        <= strategy['tp3_trailing_reference_percent']
        <= strategy['tp3_trailing_max_percent'],
        'INVALID TP3 TRAILING RANGE'
    )

    # ========================================================
    # 9. SIGNAL CONTROL VALIDATION
    # ========================================================

    for key in (
        'signal_expiry_seconds',
        'loss_cooldown_seconds',
        'mode_confirmations_required'
    ):
        require(
            strategy[key] > 0,
            'INVALID SIGNAL CONTROL: ' + key
        )

    for key in (
        'one_direction_only',
        'anti_duplicate_orders',
        'active_trade_mode_lock',
        'exclusive_mode'
    ):
        require(
            strategy[key] is True,
            'REQUIRED FLAG DISABLED: ' + key
        )

    # ========================================================
    # 10. PRECISION VALIDATION
    # ========================================================

    for key in (
        'quantity_step',
        'minimum_quantity',
        'price_step'
    ):
        require(
            market_precision[key] > 0,
            'INVALID MARKET PRECISION: ' + key
        )

    # ========================================================
    # 11. UNIT-LOCAL SAFETY VALIDATION
    # ========================================================

    require(
        safety['public_market_data_read_enabled'] is True,
        'PUBLIC MARKET READ DISABLED'
    )

    for key in (
        'authenticated_api_enabled',
        'account_access_enabled',
        'position_access_enabled',
        'order_endpoint_access_enabled',
        'demo_order_submission_enabled',
        'real_order_submission_enabled',
        'exchange_mutation_enabled',
        'leverage_mutation_enabled',
        'margin_mode_mutation_enabled',
        'position_mode_mutation_enabled'
    ):
        require(
            safety[key] is False,
            'UNSAFE CAPABILITY: ' + key
        )

    if errors:
        print(
            'UNIT 2 VALIDATION ERRORS =',
            errors,
            flush=True
        )

        raise RuntimeError(
            'UNIT 2 CONFIGURATION VALIDATION FAILED'
        )

    # ========================================================
    # 12. LADDER MARGIN CALCULATION
    # ========================================================

    full_ladder_margin = (
        strategy['initial_fixed_usdt']
        * (
            1.0
            + sum(strategy['backup_multipliers'])
        )
    )

    # ========================================================
    # 13. CONFIGURATION REPORT
    # ========================================================

    print('PASS: UNIT 2 CONFIGURATION CREATED', flush=True)
    print('PASS: EXCHANGE =', exchange_name, flush=True)
    print('PASS: API VERSION =', api_version, flush=True)
    print('PASS: MARKET SYMBOL =', market_symbol, flush=True)
    print('PASS: DEMO ORDER SYMBOL =', demo_order_symbol, flush=True)
    print('PASS: EXECUTION ENVIRONMENT =', execution_environment, flush=True)

    print(
        'PASS: LEVERAGE CONTROL = WEEX EXCHANGE ONLY',
        flush=True
    )

    print(
        'PASS: PYTHON FIXED LEVERAGE TARGET = NONE',
        flush=True
    )

    print(
        'PASS: LEVERAGE MUTATION = DISABLED',
        flush=True
    )

    print(
        'PASS: INITIAL MARGIN % =',
        strategy['initial_margin_percent'],
        flush=True
    )

    print(
        'PASS: DEFAULT INITIAL MARGIN USDT =',
        strategy['initial_fixed_usdt'],
        flush=True
    )

    print(
        'PASS: BACKUP MARGIN % =',
        strategy['backup_margin_percent'],
        flush=True
    )

    print(
        'PASS: BACKUP BUFFER % =',
        strategy['backup_buffer_percent'],
        flush=True
    )

    print(
        'PASS: MAX BACKUPS =',
        strategy['max_backups'],
        flush=True
    )

    print(
        'PASS: BACKUP MULTIPLIERS =',
        strategy['backup_multipliers'],
        flush=True
    )

    print('PASS: BACKUP FUNDING = PROGRESSIVE', flush=True)
    print('PASS: FULL LADDER RESERVATION = FALSE', flush=True)

    print(
        'PASS: EXPOSURE CAP % =',
        strategy['exposure_cap_percent'],
        flush=True
    )

    print(
        'UNIT 2 FULL LADDER MARGIN USDT =',
        full_ladder_margin,
        flush=True
    )

    print(
        'PASS: TP TARGET ALLOCATION = 10% / 20% / 70%',
        flush=True
    )

    print(
        'PASS: TP ALLOCATION TOTAL =',
        tp_total,
        '%',
        flush=True
    )

    print(
        'PASS: TP1 NET ROI FLOOR =',
        strategy['tp1_net_roi_floor_percent'],
        '%',
        flush=True
    )

    print(
        'PASS: TP2 NET ROI FLOOR =',
        strategy['tp2_net_roi_floor_percent'],
        '%',
        flush=True
    )

    print(
        'PASS: TP1 -> TP2 MIN ROI SEPARATION =',
        strategy['tp1_tp2_min_roi_separation_percent'],
        '%',
        flush=True
    )

    print(
        'PASS: TP3 TRAILING REFERENCE =',
        strategy['tp3_trailing_reference_percent'],
        '%',
        flush=True
    )

    print(
        'PASS: TP3 TRAILING RANGE =',
        strategy['tp3_trailing_min_percent'],
        '% TO',
        strategy['tp3_trailing_max_percent'],
        '%',
        flush=True
    )

    print('PASS: TP3 TRAILING MODE = DYNAMIC', flush=True)

    print(
        'PASS: TP3 DYNAMIC INPUTS = '
        'TREND + ATR/VOLATILITY + MOMENTUM DETERIORATION',
        flush=True
    )

    print('PASS: TP QUANTITY MODE = STEP-AWARE', flush=True)

    print(
        'PASS: QUANTITY STEP =',
        market_precision['quantity_step'],
        flush=True
    )

    print(
        'PASS: MINIMUM QUANTITY =',
        market_precision['minimum_quantity'],
        flush=True
    )

    print(
        'PASS: PRICE STEP =',
        market_precision['price_step'],
        flush=True
    )

    print(
        'PASS: ANTI-DUPLICATE ORDERS =',
        strategy['anti_duplicate_orders'],
        flush=True
    )

    print(
        'PASS: ONE DIRECTION ONLY =',
        strategy['one_direction_only'],
        flush=True
    )

    print(
        'PASS: ACTIVE TRADE MODE LOCK =',
        strategy['active_trade_mode_lock'],
        flush=True
    )

    print(
        'PASS: EXCLUSIVE MODE =',
        strategy['exclusive_mode'],
        flush=True
    )

    print('PASS: SL = DISABLED', flush=True)
    print('PASS: PUBLIC MARKET DATA READ ENABLED', flush=True)

    for name in (
        'AUTHENTICATED API ACCESS',
        'ACCOUNT ACCESS',
        'POSITION ACCESS',
        'ORDER ENDPOINT ACCESS',
        'DEMO ORDER SUBMISSION',
        'REAL ORDER SUBMISSION',
        'EXCHANGE MUTATION',
        'LEVERAGE MUTATION',
        'MARGIN MODE MUTATION',
        'POSITION MODE MUTATION'
    ):
        print(
            'ZERO ' + name + ' = TRUE',
            flush=True
        )

    # ========================================================
    # 14. UNIT 2 COMPLETE
    # ========================================================

    print('-' * 80, flush=True)

    log(
        'FRESH RECONSTRUCTION UNIT 2 RESULT = PASS'
    )

    print('=' * 80, flush=True)

    return config


# ============================================================
# UNIT 2 EXECUTION AND ORIGINAL DOWNSTREAM HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# END COMPLETE REPLACEMENT - UNIT 2
# ZERO INDENTATION
# UNIT 3 CONTINUES BELOW
# ============================================================


# ============================================================
# RECONSTRUCTION UNIT 3
# WEEX V3 PUBLIC READ-ONLY MARKET DATA
# ORIGINAL 22524-LINE MODEL
# ZERO INDENTATION
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
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# END COMPLETE UNIT 3
# UNIT 3 FULLY CLOSED AND CALLED
# ZERO INDENTATION
# UNIT 4 CONTINUES BELOW
# ============================================================


# ============================================================
# START COMPLETE UNIT 4 REPLACEMENT
# ORIGINAL 22524-LINE FUNCTIONAL BASELINE
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_4():
    print('=' * 80, flush=True)
    log('FRESH RECONSTRUCTION UNIT 4 START')
    print('-' * 80, flush=True)

    config = FRESH_RECONSTRUCTION_CONFIG
    if not isinstance(config, dict):
        raise RuntimeError(
            'UNIT 4 BLOCKED: INVALID UNIT 2 CONFIGURATION'
        )
    print(
        'PASS: UNIT 4 RECEIVED UNIT 2 CONFIGURATION',
        flush=True
    )

    market_snapshot = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    if not isinstance(market_snapshot, dict):
        raise RuntimeError(
            'UNIT 4 BLOCKED: INVALID UNIT 3 MARKET SNAPSHOT'
        )
    print(
        'PASS: UNIT 4 RECEIVED UNIT 3 MARKET SNAPSHOT',
        flush=True
    )

    required_snapshot_fields = (
        'exchange', 'api_version', 'symbol', 'price',
        'price_type', 'exchange_time_ms', 'source',
        'read_only'
    )
    missing_snapshot_fields = [
        field for field in required_snapshot_fields
        if field not in market_snapshot
    ]
    if missing_snapshot_fields:
        raise RuntimeError(
            'UNIT 4 BLOCKED: UNIT 3 SNAPSHOT MISSING FIELDS = '
            + str(missing_snapshot_fields)
        )

    if market_snapshot['exchange'] != 'WEEX':
        raise RuntimeError('UNIT 4 BLOCKED: INVALID EXCHANGE')
    if market_snapshot['api_version'] != 'V3':
        raise RuntimeError('UNIT 4 BLOCKED: INVALID API VERSION')
    if market_snapshot['symbol'] != 'BTCUSDT':
        raise RuntimeError('UNIT 4 BLOCKED: INVALID MARKET SYMBOL')
    if market_snapshot['price_type'] != 'MARK':
        raise RuntimeError('UNIT 4 BLOCKED: INVALID PRICE TYPE')
    if market_snapshot['read_only'] is not True:
        raise RuntimeError(
            'UNIT 4 BLOCKED: UNIT 3 SNAPSHOT NOT READ ONLY'
        )

    exchange_time_ms = int(
        market_snapshot['exchange_time_ms']
    )
    if exchange_time_ms <= 0:
        raise RuntimeError(
            'UNIT 4 BLOCKED: INVALID EXCHANGE TIME'
        )
    print(
        'PASS: UNIT 4 UNIT 3 SNAPSHOT VALIDATED',
        flush=True
    )

    exchange_config = config.get('exchange')
    safety = config.get('safety')
    if not isinstance(exchange_config, dict):
        raise RuntimeError(
            'UNIT 4 BLOCKED: EXCHANGE CONFIGURATION MISSING'
        )
    if not isinstance(safety, dict):
        raise RuntimeError(
            'UNIT 4 BLOCKED: SAFETY CONFIGURATION MISSING'
        )

    base_url = exchange_config.get('contract_base_url')
    market_symbol = exchange_config.get('market_symbol')

    if base_url != 'https://api-contract.weex.com':
        raise RuntimeError(
            'UNIT 4 BLOCKED: INVALID CONTRACT BASE URL'
        )
    if market_symbol != market_snapshot['symbol']:
        raise RuntimeError(
            'UNIT 4 BLOCKED: MARKET SYMBOL MISMATCH'
        )
    if safety.get('public_market_data_read_enabled') is not True:
        raise RuntimeError(
            'UNIT 4 BLOCKED: PUBLIC MARKET READ DISABLED'
        )

    # Unit 4 is public market analysis only.
    # These checks apply to this stage, not to the
    # later authenticated demo-order execution units.
    forbidden_capabilities = (
        'authenticated_api_enabled',
        'account_access_enabled',
        'position_access_enabled',
        'order_endpoint_access_enabled',
        'demo_order_submission_enabled',
        'real_order_submission_enabled',
        'exchange_mutation_enabled',
        'leverage_mutation_enabled',
        'margin_mode_mutation_enabled',
        'position_mode_mutation_enabled'
    )

    for capability in forbidden_capabilities:
        if safety.get(capability) is not False:
            raise RuntimeError(
                'UNIT 4 BLOCKED: UNSAFE CAPABILITY ENABLED: '
                + capability
            )

    print(
        'PASS: UNIT 4 READ-ONLY SAFETY GATE',
        flush=True
    )

    interval = '1m'
    candle_limit = 300
    endpoint = '/capi/v3/market/markPriceKlines'
    query_parameters = {
        'symbol': market_symbol,
        'interval': interval,
        'limit': candle_limit
    }
    query_string = urllib.parse.urlencode(query_parameters)
    request_url = base_url + endpoint + '?' + query_string

    print(
        'PASS: UNIT 4 ENDPOINT = WEEX V3 MARK PRICE KLINES',
        flush=True
    )
    print('PASS: UNIT 4 HTTP METHOD = GET', flush=True)
    print('PASS: UNIT 4 AUTHENTICATION = NONE', flush=True)
    print('PASS: UNIT 4 REQUEST BODY = NONE', flush=True)
    print('PASS: UNIT 4 MARKET SYMBOL =', market_symbol, flush=True)
    print('PASS: UNIT 4 INTERVAL =', interval, flush=True)
    print('PASS: UNIT 4 CANDLE LIMIT =', candle_limit, flush=True)

    request = urllib.request.Request(
        url=request_url,
        method='GET',
        headers={
            'Accept': 'application/json',
            'User-Agent': 'Fresh-WEEX-Reconstruction/1-4'
        }
    )

    if request.get_method() != 'GET':
        raise RuntimeError('UNIT 4 BLOCKED: NON-GET REQUEST')
    if request.data is not None:
        raise RuntimeError('UNIT 4 BLOCKED: REQUEST BODY PRESENT')

    try:
        with urllib.request.urlopen(
            request, timeout=15
        ) as response:
            http_status = response.getcode()
            response_body = response.read().decode('utf-8')

    except urllib.error.HTTPError as exc:
        error_body = ''
        try:
            error_body = exc.read().decode('utf-8')
        except Exception:
            pass

        print(
            'UNIT 4 HTTP ERROR CODE =',
            exc.code,
            flush=True
        )
        print(
            'UNIT 4 HTTP ERROR BODY =',
            error_body[:1000],
            flush=True
        )
        raise RuntimeError(
            'UNIT 4 WEEX V3 KLINE HTTP ERROR'
        ) from exc

    except urllib.error.URLError as exc:
        print(
            'UNIT 4 URL ERROR =',
            repr(exc.reason),
            flush=True
        )
        raise RuntimeError(
            'UNIT 4 WEEX V3 KLINE CONNECTION FAILED'
        ) from exc

    except Exception as exc:
        print(
            'UNIT 4 UNEXPECTED CONNECTION ERROR =',
            repr(exc),
            flush=True
        )
        raise

    print(
        'UNIT 4 HTTP STATUS =',
        http_status,
        flush=True
    )

    if http_status != 200:
        raise RuntimeError(
            'UNIT 4 BLOCKED: NON-200 HTTP STATUS'
        )
    if not response_body:
        raise RuntimeError(
            'UNIT 4 BLOCKED: EMPTY KLINE RESPONSE'
        )

    print(
        'PASS: UNIT 4 WEEX V3 KLINE RESPONSE RECEIVED',
        flush=True
    )

    try:
        raw_klines = json.loads(response_body)
    except json.JSONDecodeError as exc:
        print(
            'UNIT 4 RAW RESPONSE =',
            response_body[:1000],
            flush=True
        )
        raise RuntimeError(
            'UNIT 4 BLOCKED: INVALID JSON RESPONSE'
        ) from exc

    print('PASS: UNIT 4 VALID JSON RESPONSE', flush=True)

    if not isinstance(raw_klines, list):
        raise RuntimeError(
            'UNIT 4 BLOCKED: KLINE RESPONSE IS NOT A LIST'
        )
    if len(raw_klines) < 200:
        raise RuntimeError(
            'UNIT 4 BLOCKED: FEWER THAN 200 KLINES RECEIVED'
        )

    print(
        'PASS: UNIT 4 KLINES RECEIVED =',
        len(raw_klines),
        flush=True
    )

    normalized_klines = []

    for raw_candle in raw_klines:
        if not isinstance(raw_candle, (list, tuple)):
            raise RuntimeError(
                'UNIT 4 BLOCKED: INVALID KLINE ENTRY'
            )
        if len(raw_candle) < 7:
            raise RuntimeError(
                'UNIT 4 BLOCKED: INCOMPLETE KLINE ENTRY'
            )

        try:
            normalized_candle = {
                'open_time_ms': int(raw_candle[0]),
                'open': float(raw_candle[1]),
                'high': float(raw_candle[2]),
                'low': float(raw_candle[3]),
                'close': float(raw_candle[4]),
                'volume': float(raw_candle[5]),
                'close_time_ms': int(raw_candle[6])
            }
        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                'UNIT 4 BLOCKED: INVALID KLINE VALUE'
            ) from exc

        if (
            normalized_candle['open'] <= 0
            or normalized_candle['high'] <= 0
            or normalized_candle['low'] <= 0
            or normalized_candle['close'] <= 0
        ):
            raise RuntimeError(
                'UNIT 4 BLOCKED: NON-POSITIVE KLINE PRICE'
            )

        normalized_klines.append(normalized_candle)

    normalized_klines.sort(
        key=lambda candle: candle['open_time_ms']
    )

    print('PASS: UNIT 4 KLINES NORMALIZED', flush=True)
    print(
        'PASS: UNIT 4 KLINES ORDERED OLDEST -> NEWEST',
        flush=True
    )

    previous_open_time = None

    for candle in normalized_klines:
        current_open_time = candle['open_time_ms']

        if (
            previous_open_time is not None
            and current_open_time <= previous_open_time
        ):
            raise RuntimeError(
                'UNIT 4 BLOCKED: DUPLICATE OR UNORDERED KLINE TIME'
            )

        previous_open_time = current_open_time

    print(
        'PASS: UNIT 4 KLINE TIMESTAMPS VALIDATED',
        flush=True
    )

    closed_klines = [
        candle for candle in normalized_klines
        if candle['close_time_ms'] <= exchange_time_ms
    ]

    if len(closed_klines) < 200:
        raise RuntimeError(
            'UNIT 4 BLOCKED: INSUFFICIENT CLOSED KLINES'
        )

    newest_returned_candle = normalized_klines[-1]
    newest_returned_is_closed = (
        newest_returned_candle['close_time_ms']
        <= exchange_time_ms
    )

    print(
        'PASS: UNIT 4 EXCHANGE TIME =',
        exchange_time_ms,
        flush=True
    )
    print(
        'PASS: UNIT 4 RETURNED KLINES =',
        len(normalized_klines),
        flush=True
    )
    print(
        'PASS: UNIT 4 CLOSED KLINES =',
        len(closed_klines),
        flush=True
    )
    print(
        'UNIT 4 NEWEST RETURNED CANDLE CLOSED =',
        newest_returned_is_closed,
        flush=True
    )

    close_prices = [
        candle['close'] for candle in closed_klines
    ]

    if len(close_prices) < 200:
        raise RuntimeError(
            'UNIT 4 BLOCKED: INSUFFICIENT CLOSED CLOSE PRICES'
        )

    print(
        'PASS: UNIT 4 CLOSED-CANDLE PRICE SERIES READY',
        flush=True
    )

    # ========================================================
    # EMA CALCULATION - ORIGINAL BEHAVIOR
    # ========================================================

    def calculate_ema(prices, period):
        if len(prices) < period:
            raise RuntimeError(
                'INSUFFICIENT DATA FOR EMA' + str(period)
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
        for value in (ema19, ema50, ema100, ema200)
    ):
        raise RuntimeError(
            'UNIT 4 BLOCKED: INVALID EMA VALUE'
        )

    print('PASS: UNIT 4 EMA19 =', round(ema19, 6), flush=True)
    print('PASS: UNIT 4 EMA50 =', round(ema50, 6), flush=True)
    print('PASS: UNIT 4 EMA100 =', round(ema100, 6), flush=True)
    print('PASS: UNIT 4 EMA200 =', round(ema200, 6), flush=True)

    if ema50 == 0:
        raise RuntimeError(
            'UNIT 4 BLOCKED: EMA50 IS ZERO'
        )

    ema19_50_separation_pct = (
        abs(ema19 - ema50) / ema50 * 100.0
    )

    print(
        'PASS: UNIT 4 EMA19/50 SEPARATION % =',
        round(ema19_50_separation_pct, 6),
        flush=True
    )

    if ema19 > ema50 and ema50 > ema200:
        ema_structure = 'BULLISH'
    elif ema19 < ema50 and ema50 < ema200:
        ema_structure = 'BEARISH'
    else:
        ema_structure = 'MIXED'

    print(
        'PASS: UNIT 4 EMA STRUCTURE =',
        ema_structure,
        flush=True
    )

    latest_candle = closed_klines[-1]
    previous_candle = closed_klines[-2]

    latest_close = float(latest_candle['close'])
    previous_close = float(previous_candle['close'])
    latest_open_time_ms = int(
        latest_candle['open_time_ms']
    )
    latest_close_time_ms = int(
        latest_candle['close_time_ms']
    )

    print(
        'PASS: UNIT 4 PREVIOUS KLINE CLOSE =',
        previous_close,
        flush=True
    )
    print(
        'PASS: UNIT 4 LATEST KLINE CLOSE =',
        latest_close,
        flush=True
    )
    print(
        'PASS: UNIT 4 LATEST KLINE OPEN TIME =',
        latest_open_time_ms,
        flush=True
    )
    print(
        'PASS: UNIT 4 LATEST KLINE CLOSE TIME =',
        latest_close_time_ms,
        flush=True
    )

    if previous_close <= 0:
        raise RuntimeError(
            'UNIT 4 BLOCKED: PREVIOUS CLOSE IS ZERO'
        )

    short_term_move_pct = (
        (latest_close - previous_close)
        / previous_close * 100.0
    )

    print(
        'PASS: UNIT 4 SHORT-TERM MOVE % =',
        round(short_term_move_pct, 6),
        flush=True
    )

    diagnostic_windows = (1, 5, 15, 30, 60, 120)
    window_moves_pct = {}

    print('-' * 80, flush=True)
    print('UNIT 4 BREAKOUT WINDOW DIAGNOSTIC', flush=True)

    for window_minutes in diagnostic_windows:
        if len(close_prices) <= window_minutes:
            raise RuntimeError(
                'UNIT 4 BLOCKED: INSUFFICIENT DATA FOR '
                + str(window_minutes) + 'M MOVE'
            )

        reference_close = float(
            close_prices[-(window_minutes + 1)]
        )

        if reference_close <= 0:
            raise RuntimeError(
                'UNIT 4 BLOCKED: INVALID '
                + str(window_minutes) + 'M REFERENCE CLOSE'
            )

        window_move_pct = (
            (latest_close - reference_close)
            / reference_close * 100.0
        )

        window_moves_pct[window_minutes] = float(
            window_move_pct
        )

        print(
            f'UNIT 4 {window_minutes}M MOVE % = '
            f'{round(window_move_pct, 6)}',
            flush=True
        )

    print(
        'UNIT 4 SIGNAL MOVE SOURCE = '
        'FULLY CLOSED 1M CANDLE VS PREVIOUS '
        'FULLY CLOSED 1M CANDLE',
        flush=True
    )

    print('-' * 80, flush=True)

    live_mark_price = float(
        market_snapshot['price']
    )

    if live_mark_price <= 0:
        raise RuntimeError(
            'UNIT 4 BLOCKED: INVALID LIVE MARK PRICE'
        )

    print(
        'PASS: UNIT 4 LIVE MARK PRICE =',
        live_mark_price,
        flush=True
    )

    # ========================================================
    # NORMALIZED OUTPUT FOR UNIT 5
    # ========================================================

    analysis_snapshot = {
        'exchange': 'WEEX',
        'api_version': 'V3',
        'symbol': market_symbol,
        'interval': interval,
        'price_type': 'MARK',
        'live_mark_price': live_mark_price,
        'previous_close': previous_close,
        'latest_close': latest_close,
        'latest_open_time_ms': latest_open_time_ms,
        'latest_close_time_ms': latest_close_time_ms,
        'exchange_time_ms': exchange_time_ms,
        'ema19': ema19,
        'ema50': ema50,
        'ema100': ema100,
        'ema200': ema200,
        'ema19_50_separation_pct': ema19_50_separation_pct,
        'short_term_move_pct': short_term_move_pct,
        'move_1m_pct': window_moves_pct[1],
        'move_5m_pct': window_moves_pct[5],
        'move_15m_pct': window_moves_pct[15],
        'move_30m_pct': window_moves_pct[30],
        'move_60m_pct': window_moves_pct[60],
        'move_120m_pct': window_moves_pct[120],
        'ema_structure': ema_structure,
        'recent_closed_klines': [
            dict(candle) for candle in closed_klines[-60:]
        ],
        'candle_count': len(normalized_klines),
        'closed_candle_count': len(closed_klines),
        'newest_returned_candle_closed': newest_returned_is_closed,
        'source': 'WEEX_V3_PUBLIC_MARK_PRICE_KLINES',
        'read_only': True
    }

    required_analysis_fields = (
        'exchange',
        'api_version',
        'symbol',
        'interval',
        'price_type',
        'live_mark_price',
        'previous_close',
        'latest_close',
        'latest_open_time_ms',
        'latest_close_time_ms',
        'exchange_time_ms',
        'ema19',
        'ema50',
        'ema100',
        'ema200',
        'ema19_50_separation_pct',
        'short_term_move_pct',
        'move_1m_pct',
        'move_5m_pct',
        'move_15m_pct',
        'move_30m_pct',
        'move_60m_pct',
        'move_120m_pct',
        'ema_structure',
        'recent_closed_klines',
        'candle_count',
        'closed_candle_count',
        'newest_returned_candle_closed',
        'source',
        'read_only'
    )

    missing_analysis_fields = [
        field for field in required_analysis_fields
        if field not in analysis_snapshot
    ]

    if missing_analysis_fields:
        raise RuntimeError(
            'UNIT 4 ANALYSIS SNAPSHOT MISSING FIELDS = '
            + str(missing_analysis_fields)
        )

    if analysis_snapshot['read_only'] is not True:
        raise RuntimeError(
            'UNIT 4 ANALYSIS SNAPSHOT READ-ONLY FAILURE'
        )

    if (
        analysis_snapshot['latest_close_time_ms']
        > analysis_snapshot['exchange_time_ms']
    ):
        raise RuntimeError(
            'UNIT 4 CLOSED-CANDLE SAFETY FAILURE'
        )

    if abs(
        analysis_snapshot['move_1m_pct']
        - analysis_snapshot['short_term_move_pct']
    ) > 1e-09:
        raise RuntimeError(
            'UNIT 4 1M MOVE CONSISTENCY FAILURE'
        )

    print('-' * 80, flush=True)

    print(
        'PASS: UNIT 4 NORMALIZED MARKET ANALYSIS SNAPSHOT',
        flush=True
    )
    print(
        'PASS: UNIT 4 CLOSED-CANDLE SIGNAL SOURCE VERIFIED',
        flush=True
    )
    print(
        'PASS: UNIT 4 MULTI-WINDOW MOMENTUM SNAPSHOT READY',
        flush=True
    )
    print(
        'PASS: UNIT 4 PUBLIC MARKET ANALYSIS COMPLETED',
        flush=True
    )
    print(
        'PASS: UNIT 4 EMA19 / EMA50 / EMA200 COMPLETED',
        flush=True
    )
    print(
        'PASS: UNIT 4 NO ENTRY SIGNAL GENERATED',
        flush=True
    )
    print(
        'PASS: UNIT 4 NO ORDER PAYLOAD GENERATED',
        flush=True
    )

    print(
        'ZERO AUTHENTICATED REQUEST = TRUE',
        flush=True
    )
    print('ZERO ACCOUNT ACCESS = TRUE', flush=True)
    print('ZERO POSITION ACCESS = TRUE', flush=True)
    print('ZERO ORDER ENDPOINT ACCESS = TRUE', flush=True)
    print('ZERO DEMO ORDER = TRUE', flush=True)
    print('ZERO REAL ORDER = TRUE', flush=True)
    print('ZERO EXCHANGE WRITE = TRUE', flush=True)
    print('ZERO LEVERAGE MUTATION = TRUE', flush=True)
    print('ZERO MARGIN MODE MUTATION = TRUE', flush=True)
    print('ZERO POSITION MODE MUTATION = TRUE', flush=True)

    print('-' * 80, flush=True)
    log('FRESH RECONSTRUCTION UNIT 4 RESULT = PASS')
    print('=' * 80, flush=True)

    return analysis_snapshot


# ============================================================
# RUN UNIT 4
# ORIGINAL UNIT 5 HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)

# ============================================================
# END COMPLETE UNIT 4 REPLACEMENT
# ZERO INDENTATION
# UNIT 5 CONTINUES BELOW
# ============================================================

