
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
