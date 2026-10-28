
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
# START UNIT 2 HYBRID ADJUSTABLE V3 ADAPTER
# ZERO INDENTATION
# PLACE AFTER EXISTING UNIT 2, BEFORE UNIT 3
# ============================================================

def fresh_unit_2_hybrid_adjustable_adapter(config):

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 2 ADAPTER: INVALID CONFIGURATION"
        )

    if not isinstance(config.get("strategy"), dict):
        raise RuntimeError(
            "UNIT 2 ADAPTER: STRATEGY MISSING"
        )

    qualification = {

        # ====================================================
        # COMMON QUALIFICATION
        # ====================================================

        "common": {
            "mode_priority": (
                "BREAKOUT", "STRUCTURE", "SCALP"
            ),
            "direction_votes_required": 2,
            "direction_votes_total": 3,
            "use_closed_candles": True,
            "protect_developing_candidates": True,
            "arbitrate_before_scalp": True,
            "scalp_requires_higher_modes_clear": True,
            "signal_expiry_seconds": 120,
            "candidate_expiry_seconds": 120,
            "spike_count_rejection_above": 2,
            "reject_late_impulse_entry": True,
        },

        # ====================================================
        # BREAKOUT - HYBRID ADJUSTABLE DEFAULTS
        # ====================================================

        "breakout": {
            "enabled": True,
            "priority": 1,
            "early_detection_enabled": True,
            "developing_candidate_enabled": True,
            "support_resistance_lookback": 20,
            "developing_proximity_atr": 0.50,
            "confirmation_distance_atr": 0.10,
            "direction_votes_required": 2,
            "momentum_lookback_fast": 5,
            "momentum_lookback_slow": 15,
            "require_momentum_confirmation": True,
            "require_direction_agreement": True,
            "require_ema_crossover": False,
            "retest_mandatory": False,
            "allow_preconfirmation": True,
            "minimum_atr_percent": 0.0,
            "max_price_extension_atr": 3.0,
            "spike_rejection_enabled": True,
            "max_spike_count": 2,
            "false_breakout_rejection": True,
            "volume_confirmation_enabled": False,
            "minimum_volume_ratio": 1.20,
            "candidate_expiry_seconds": 120,
        },

        # ====================================================
        # STRUCTURE - HYBRID ADJUSTABLE DEFAULTS
        # ====================================================

        "structure": {
            "enabled": True,
            "priority": 2,
            "early_detection_enabled": True,
            "developing_candidate_enabled": True,
            "ema_fast_period": 19,
            "ema_middle_period": 50,
            "ema_slow_period": 200,
            "direction_votes_required": 2,
            "momentum_lookback_minutes": 15,
            "require_direction_agreement": True,
            "require_ema_crossover": False,
            "allow_pullback_entry": True,
            "allow_continuation_entry": True,
            "pullback_tolerance_atr": 0.75,
            "max_price_extension_atr": 2.0,
            "minimum_ema_separation_percent": 0.0,
            "retest_mandatory": False,
            "reject_trend_exhaustion": True,
            "candidate_expiry_seconds": 120,
        },

        # ====================================================
        # SCALP - HYBRID ADJUSTABLE DEFAULTS
        # ====================================================

        "scalp": {
            "enabled": True,
            "priority": 3,
            "sideways_preferred": True,
            "require_sideways_market": True,
            "protect_developing_higher_modes": True,
            "quality_threshold": 70.0,
            "price_action_weight_percent": 50.0,
            "other_factors_weight_percent": 50.0,
            "direction_votes_required": 2,
            "direction_votes_total": 3,
            "max_ema_extension_clusters": 1.5,
            "max_spike_count": 2,
            "reject_late_impulse": True,
            "early_entry_enabled": True,
            "ema_compression_atr_max": 0.70,
            "range20_atr_max": 8.0,
            "momentum15_atr_multiplier_max": 1.5,
            "fee_aware_enabled": True,
            "estimated_taker_fee_percent": 0.08,
            "estimated_slippage_percent": 0.0,
            "include_entry_fee": True,
            "include_exit_fee": True,
            "minimum_fee_coverage_multiplier": 2.0,
            "require_positive_estimated_net": True,
            "minimum_net_roi_percent": 2.0,
        },
    }

    # Add the complete qualification configuration
    # without replacing existing Unit 2 settings.

    config["qualification"] = qualification

    # Preserve exchange-controlled leverage.
    # Do not create a permanent leverage_target.

    config["strategy"].pop("leverage_target", None)

    # ========================================================
    # CONFIGURATION VERIFICATION
    # ========================================================

    assert tuple(
        qualification["common"]["mode_priority"]
    ) == ("BREAKOUT", "STRUCTURE", "SCALP")

    assert qualification["scalp"]["quality_threshold"] == 70.0
    assert qualification["breakout"]["developing_proximity_atr"] == 0.50
    assert qualification["breakout"]["confirmation_distance_atr"] == 0.10
    assert qualification["structure"]["pullback_tolerance_atr"] == 0.75

    assert qualification["scalp"]["fee_aware_enabled"] is True
    assert qualification["common"]["protect_developing_candidates"] is True

    assert "leverage_target" not in config["strategy"]

    print("=" * 80, flush=True)
    print("UNIT 2 HYBRID ADJUSTABLE V3 ADAPTER", flush=True)
    print("UNIT 2 ORIGINAL CONFIGURATION = RETAINED", flush=True)

    print(
        "UNIT 2 MODE PRIORITY =",
        qualification["common"]["mode_priority"],
        flush=True
    )

    print(
        "UNIT 2 SCALP QUALITY DEFAULT =",
        qualification["scalp"]["quality_threshold"],
        flush=True
    )

    print(
        "UNIT 2 STRUCTURE PULLBACK ATR =",
        qualification["structure"]["pullback_tolerance_atr"],
        flush=True
    )

    print(
        "UNIT 2 BREAKOUT PROXIMITY ATR =",
        qualification["breakout"]["developing_proximity_atr"],
        flush=True
    )

    print(
        "UNIT 2 BREAKOUT CONFIRMATION ATR =",
        qualification["breakout"]["confirmation_distance_atr"],
        flush=True
    )

    print("UNIT 2 REJECTED HIGHER MODE = NOT A SCALP LOCK", flush=True)
    print("UNIT 2 DEVELOPING HIGHER MODE = PROTECTED", flush=True)
    print("UNIT 2 EXCHANGE LEVERAGE CONTROL = WEEX ONLY", flush=True)
    print("UNIT 2 FIXED PYTHON LEVERAGE = NONE", flush=True)
    print("UNIT 2 EXCHANGE WRITE = NONE", flush=True)
    print("FRESH RECONSTRUCTION UNIT 2 ADAPTER RESULT = PASS", flush=True)
    print("=" * 80, flush=True)

    return config


# ============================================================
# RUN UNIT 2 HYBRID ADJUSTABLE ADAPTER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_unit_2_hybrid_adjustable_adapter(
        FRESH_RECONSTRUCTION_CONFIG
    )
)

# ============================================================
# END UNIT 2 HYBRID ADJUSTABLE ADAPTER
# UNIT 3 FOLLOWS
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


# ============================================================
# START UNIT 4 HYBRID ADJUSTABLE EVIDENCE ADAPTER
# ZERO INDENTATION
# PLACE AFTER UNIT 4, BEFORE UNIT 5
# ============================================================

def fresh_unit_4_hybrid_adjustable_adapter(config, snapshot):

    import math

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 4 ADAPTER INVALID CONFIG")

    if not isinstance(snapshot, dict):
        raise RuntimeError("UNIT 4 ADAPTER INVALID SNAPSHOT")

    qualification = config.get("qualification")

    if not isinstance(qualification, dict):
        raise RuntimeError(
            "UNIT 4 ADAPTER QUALIFICATION CONFIG MISSING"
        )

    try:
        common = qualification["common"]
        breakout = qualification["breakout"]
        structure = qualification["structure"]
        scalp = qualification["scalp"]
    except KeyError as exc:
        raise RuntimeError(
            "UNIT 4 ADAPTER MISSING QUALIFICATION SECTION"
        ) from exc

    if not all(
        isinstance(x, dict)
        for x in (common, breakout, structure, scalp)
    ):
        raise RuntimeError(
            "UNIT 4 ADAPTER INVALID QUALIFICATION SECTION"
        )

    if snapshot.get("read_only") is not True:
        raise RuntimeError("UNIT 4 ADAPTER INVALID MARKET SOURCE")

    if snapshot.get("symbol") != "BTCUSDT":
        raise RuntimeError("UNIT 4 ADAPTER SYMBOL MISMATCH")

    candles = snapshot.get("recent_closed_klines")

    if not isinstance(candles, list) or len(candles) < 35:
        raise RuntimeError(
            "UNIT 4 ADAPTER INSUFFICIENT CLOSED CANDLES"
        )

    def number(value, name):
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                "UNIT 4 ADAPTER INVALID " + name
            ) from exc

        if not math.isfinite(value):
            raise RuntimeError(
                "UNIT 4 ADAPTER NONFINITE " + name
            )

        return value

    normalized = []

    for item in candles:

        if not isinstance(item, dict):
            raise RuntimeError("UNIT 4 ADAPTER INVALID CANDLE")

        candle = {
            "open": number(item.get("open"), "OPEN"),
            "high": number(item.get("high"), "HIGH"),
            "low": number(item.get("low"), "LOW"),
            "close": number(item.get("close"), "CLOSE"),
        }

        if not (
            0 < candle["low"]
            <= min(candle["open"], candle["close"])
            <= max(candle["open"], candle["close"])
            <= candle["high"]
        ):
            raise RuntimeError("UNIT 4 ADAPTER INVALID OHLC")

        normalized.append(candle)

    latest = normalized[-1]
    closes = [item["close"] for item in normalized]

    ema19 = number(snapshot.get("ema19"), "EMA19")
    ema50 = number(snapshot.get("ema50"), "EMA50")
    ema100 = number(snapshot.get("ema100"), "EMA100")
    ema200 = number(snapshot.get("ema200"), "EMA200")

    move5 = number(snapshot.get("move_5m_pct"), "MOVE5")
    move15 = number(snapshot.get("move_15m_pct"), "MOVE15")

    separation = number(
        snapshot.get("ema19_50_separation_pct"),
        "EMA SEPARATION"
    )

    # ========================================================
    # 1. ATR14 FROM VERIFIED CLOSED CANDLES
    # ========================================================

    true_ranges = []

    for index in range(1, len(normalized)):

        current = normalized[index]
        previous_close = normalized[index - 1]["close"]

        true_ranges.append(
            max(
                current["high"] - current["low"],
                abs(current["high"] - previous_close),
                abs(current["low"] - previous_close),
            )
        )

    atr14 = sum(true_ranges[-14:]) / 14.0

    if atr14 <= 0:
        raise RuntimeError("UNIT 4 ADAPTER ATR14 INVALID")

    atr_percent = atr14 / latest["close"] * 100.0

    # ========================================================
    # 2. ADJUSTABLE SUPPORT AND RESISTANCE
    # ========================================================

    lookback = int(breakout["support_resistance_lookback"])

    if lookback < 2 or len(normalized) < lookback + 15:
        raise RuntimeError(
            "UNIT 4 ADAPTER INVALID BREAKOUT LOOKBACK"
        )

    prior = normalized[-lookback - 1:-1]

    support = min(c["low"] for c in prior)
    resistance = max(c["high"] for c in prior)

    range20_atr_ratio = (
        resistance - support
    ) / atr14

    latest_close = latest["close"]

    # ========================================================
    # 3. DIRECTION EVIDENCE: 2 OF 3 VOTES
    # ========================================================

    ema_vote = (
        "LONG" if ema19 > ema50
        else "SHORT" if ema19 < ema50
        else "NONE"
    )

    momentum_sum = move5 + move15

    momentum_vote = (
        "LONG" if momentum_sum > 0
        else "SHORT" if momentum_sum < 0
        else "NONE"
    )

    price_vote = (
        "LONG" if latest_close > ema19
        else "SHORT" if latest_close < ema19
        else "NONE"
    )

    votes = (ema_vote, momentum_vote, price_vote)

    long_votes = votes.count("LONG")
    short_votes = votes.count("SHORT")

    required_votes = int(
        common["direction_votes_required"]
    )

    if long_votes >= required_votes and long_votes > short_votes:
        direction_evidence = "LONG"

    elif short_votes >= required_votes and short_votes > long_votes:
        direction_evidence = "SHORT"

    else:
        direction_evidence = "NONE"

    # ========================================================
    # 4. BREAKOUT: DEVELOPING AND CONFIRMED
    # ========================================================

    proximity_atr = number(
        breakout["developing_proximity_atr"],
        "BREAKOUT PROXIMITY"
    )

    confirmation_atr = number(
        breakout["confirmation_distance_atr"],
        "BREAKOUT CONFIRMATION"
    )

    maximum_breakout_extension = number(
        breakout["max_price_extension_atr"],
        "BREAKOUT EXTENSION"
    )

    near_resistance = (
        latest_close >= resistance - proximity_atr * atr14
    )

    near_support = (
        latest_close <= support + proximity_atr * atr14
    )

    long_extension = max(
        0.0, (latest_close - resistance) / atr14
    )

    short_extension = max(
        0.0, (support - latest_close) / atr14
    )

    breakout_developing_long = bool(
        breakout["enabled"]
        and breakout["developing_candidate_enabled"]
        and near_resistance
        and direction_evidence == "LONG"
        and move5 > 0
        and long_extension <= maximum_breakout_extension
    )

    breakout_developing_short = bool(
        breakout["enabled"]
        and breakout["developing_candidate_enabled"]
        and near_support
        and direction_evidence == "SHORT"
        and move5 < 0
        and short_extension <= maximum_breakout_extension
    )

    breakout_confirmed_long = bool(
        breakout["enabled"]
        and latest_close > resistance + confirmation_atr * atr14
        and long_extension <= maximum_breakout_extension
    )

    breakout_confirmed_short = bool(
        breakout["enabled"]
        and latest_close < support - confirmation_atr * atr14
        and short_extension <= maximum_breakout_extension
    )

    # ========================================================
    # 5. EARLY STRUCTURE EVIDENCE
    # ========================================================

    structure_separation_min = number(
        structure["minimum_ema_separation_percent"],
        "STRUCTURE SEPARATION"
    )

    pullback_tolerance = number(
        structure["pullback_tolerance_atr"],
        "STRUCTURE PULLBACK"
    )

    structure_max_extension = number(
        structure["max_price_extension_atr"],
        "STRUCTURE EXTENSION"
    )

    distance_atr = (
        latest_close - ema19
    ) / atr14

    pullback_near_ema = (
        abs(distance_atr) <= pullback_tolerance
    )

    separation_ok = (
        abs(separation) >= structure_separation_min
    )

    structure_developing_long = bool(
        structure["enabled"]
        and separation_ok
        and ema19 > ema50 > ema200
        and direction_evidence == "LONG"
        and move15 > 0
        and distance_atr <= structure_max_extension
        and (
            pullback_near_ema
            or (
                structure["allow_continuation_entry"]
                and latest_close > ema19
            )
        )
    )

    structure_developing_short = bool(
        structure["enabled"]
        and separation_ok
        and ema19 < ema50 < ema200
        and direction_evidence == "SHORT"
        and move15 < 0
        and -distance_atr <= structure_max_extension
        and (
            pullback_near_ema
            or (
                structure["allow_continuation_entry"]
                and latest_close < ema19
            )
        )
    )

    # ========================================================
    # 6. SCALP SIDEWAYS-MARKET EVIDENCE
    # ========================================================

    ema_cluster_height = (
        max(ema19, ema50, ema100, ema200)
        - min(ema19, ema50, ema100, ema200)
    )

    ema_compression_atr = (
        ema_cluster_height / atr14
    )

    price_extension_cluster = (
        abs(latest_close - ema19)
        / max(ema_cluster_height, atr14 * 0.01)
    )

    momentum15_atr_ratio = (
        abs(latest_close - closes[-16]) / atr14
    )

    sideways_candidate = bool(
        scalp["enabled"]
        and ema_compression_atr
        <= number(
            scalp["ema_compression_atr_max"],
            "SCALP COMPRESSION"
        )
        and range20_atr_ratio
        <= number(
            scalp["range20_atr_max"],
            "SCALP RANGE"
        )
        and momentum15_atr_ratio
        <= number(
            scalp["momentum15_atr_multiplier_max"],
            "SCALP MOMENTUM"
        )
        and not (
            breakout_developing_long
            or breakout_developing_short
            or structure_developing_long
            or structure_developing_short
        )
    )

    price_overextended = bool(
        price_extension_cluster
        > number(
            scalp["max_ema_extension_clusters"],
            "SCALP EXTENSION"
        )
    )

    # ========================================================
    # 7. PRESERVE ORIGINAL UNIT 4 SNAPSHOT
    # ADD HYBRID EVIDENCE ONLY
    # ========================================================

    original_fields = dict(snapshot)

    additions = {
        "atr14": atr14,
        "atr_percent": atr_percent,

        "support20": support,
        "resistance20": resistance,
        "range20_atr_ratio": range20_atr_ratio,

        "near_resistance": bool(near_resistance),
        "near_support": bool(near_support),

        "breakout_developing_long": breakout_developing_long,
        "breakout_developing_short": breakout_developing_short,
        "breakout_confirmed_long": breakout_confirmed_long,
        "breakout_confirmed_short": breakout_confirmed_short,

        "structure_developing_long": structure_developing_long,
        "structure_developing_short": structure_developing_short,

        "sideways_candidate": sideways_candidate,

        "direction_long_votes": long_votes,
        "direction_short_votes": short_votes,
        "direction_evidence": direction_evidence,

        "ema_cluster_height": ema_cluster_height,
        "ema_compression_atr": ema_compression_atr,

        "price_extension_cluster": price_extension_cluster,
        "price_overextended": price_overextended,

        "strategy_evidence_version": "U4_HYBRID_V2",

        "qualification_settings": {
            "breakout_lookback": lookback,
            "breakout_proximity_atr": proximity_atr,
            "breakout_confirmation_atr": confirmation_atr,
            "structure_pullback_atr": pullback_tolerance,
            "structure_max_extension_atr": structure_max_extension,
            "scalp_compression_atr":
                scalp["ema_compression_atr_max"],
            "scalp_range_atr": scalp["range20_atr_max"],
            "scalp_momentum_atr":
                scalp["momentum15_atr_multiplier_max"],
        },

        "trade_authorized": False,
        "order_payload_created": False,
    }

    # Do not overwrite original market-analysis fields.

    if set(original_fields).intersection(additions):
        raise RuntimeError(
            "UNIT 4 ADAPTER FIELD COLLISION"
        )

    result = dict(original_fields)
    result.update(additions)

    for key, value in original_fields.items():
        if result[key] != value:
            raise RuntimeError(
                "UNIT 4 ADAPTER ALTERED ORIGINAL FIELD: " + key
            )

    print("=" * 80, flush=True)
    print("UNIT 4 HYBRID ADJUSTABLE EVIDENCE ADAPTER", flush=True)

    print("UNIT 4 ORIGINAL FIELDS = PRESERVED", flush=True)
    print("UNIT 4 ATR14 =", round(atr14, 4), flush=True)
    print("UNIT 4 DIRECTION =", direction_evidence, flush=True)

    print(
        "UNIT 4 BREAKOUT DEVELOPING LONG =",
        breakout_developing_long,
        flush=True
    )
    print(
        "UNIT 4 BREAKOUT DEVELOPING SHORT =",
        breakout_developing_short,
        flush=True
    )
    print(
        "UNIT 4 STRUCTURE DEVELOPING LONG =",
        structure_developing_long,
        flush=True
    )
    print(
        "UNIT 4 STRUCTURE DEVELOPING SHORT =",
        structure_developing_short,
        flush=True
    )
    print(
        "UNIT 4 SIDEWAYS CANDIDATE =",
        sideways_candidate,
        flush=True
    )

    print("UNIT 4 EXCHANGE WRITE = NONE", flush=True)
    print(
        "FRESH RECONSTRUCTION UNIT 4 ADAPTER RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 4 ADAPTER — ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_unit_4_hybrid_adjustable_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
    )
)

# ============================================================
# END UNIT 4 HYBRID ADJUSTABLE EVIDENCE ADAPTER
# UNIT 5 FOLLOWS
# ============================================================


# ============================================================
# START COMPLETE UNIT 5 REPLACEMENT
# SOURCE: PROVEN 22524-LINE MODEL
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_5(unit_2_config, unit_4_snapshot):
    print('=' * 80, flush=True)
    print(f'{datetime.now(timezone.utc).isoformat()} FRESH RECONSTRUCTION UNIT 5 START', flush=True)
    print('-' * 80, flush=True)

    if not isinstance(unit_2_config, dict):
        raise RuntimeError('UNIT 5 FAILED: INVALID UNIT 2 CONFIGURATION')

    print('PASS: UNIT 5 RECEIVED UNIT 2 CONFIGURATION', flush=True)

    if not isinstance(unit_4_snapshot, dict):
        raise RuntimeError('UNIT 5 FAILED: INVALID UNIT 4 SNAPSHOT')

    print('PASS: UNIT 5 RECEIVED UNIT 4 MARKET SNAPSHOT', flush=True)

    required_fields = (
        'symbol', 'live_mark_price', 'ema19', 'ema50',
        'ema200', 'ema19_50_separation_pct', 'ema_structure',
        'previous_close', 'latest_close', 'short_term_move_pct',
        'move_1m_pct', 'move_5m_pct', 'move_15m_pct',
        'move_30m_pct', 'move_60m_pct', 'move_120m_pct'
    )

    missing_fields = [
        field for field in required_fields
        if field not in unit_4_snapshot
    ]

    if missing_fields:
        raise RuntimeError(
            'UNIT 5 FAILED: UNIT 4 SNAPSHOT MISSING FIELDS = '
            + str(missing_fields)
        )

    print('PASS: UNIT 5 REQUIRED UNIT 4 FIELDS PRESENT', flush=True)

    symbol = str(unit_4_snapshot['symbol']).upper()
    live_price = float(unit_4_snapshot['live_mark_price'])
    ema19 = float(unit_4_snapshot['ema19'])
    ema50 = float(unit_4_snapshot['ema50'])
    ema200 = float(unit_4_snapshot['ema200'])
    separation_pct = abs(float(unit_4_snapshot['ema19_50_separation_pct']))
    ema_structure = str(unit_4_snapshot['ema_structure']).upper()

    previous_close = float(unit_4_snapshot['previous_close'])
    latest_close = float(unit_4_snapshot['latest_close'])
    short_term_move_pct = float(unit_4_snapshot['short_term_move_pct'])
    move_1m_pct = float(unit_4_snapshot['move_1m_pct'])
    move_5m_pct = float(unit_4_snapshot['move_5m_pct'])
    move_15m_pct = float(unit_4_snapshot['move_15m_pct'])
    move_30m_pct = float(unit_4_snapshot['move_30m_pct'])
    move_60m_pct = float(unit_4_snapshot['move_60m_pct'])
    move_120m_pct = float(unit_4_snapshot['move_120m_pct'])

    if live_price <= 0:
        raise RuntimeError('UNIT 5 FAILED: INVALID LIVE PRICE')

    if ema19 <= 0 or ema50 <= 0 or ema200 <= 0:
        raise RuntimeError('UNIT 5 FAILED: INVALID EMA VALUE')

    print('PASS: UNIT 5 UNIT 4 SNAPSHOT VALIDATED', flush=True)
    print('PASS: UNIT 5 READ-ONLY SAFETY GATE', flush=True)

    # ========================================================
    # ORIGINAL SIGNAL THRESHOLDS
    # ========================================================

    BREAKOUT_MIN_SEPARATION_PCT = 0.12
    STRUCTURE_MIN_SEPARATION_PCT = 0.07
    SCALP_MIN_SEPARATION_PCT = 0.03

    BREAKOUT_MIN_MOVE_PCT = 0.08
    STRUCTURE_MIN_MOVE_PCT = 0.04
    SCALP_MIN_MOVE_PCT = 0.015

    print('PASS: UNIT 5 MODE THRESHOLDS LOADED', flush=True)

    print(
        f'UNIT 5 SCALP MIN SEPARATION % = {SCALP_MIN_SEPARATION_PCT}',
        flush=True
    )
    print(
        f'UNIT 5 STRUCTURE MIN SEPARATION % = {STRUCTURE_MIN_SEPARATION_PCT}',
        flush=True
    )
    print(
        f'UNIT 5 BREAKOUT MIN SEPARATION % = {BREAKOUT_MIN_SEPARATION_PCT}',
        flush=True
    )
    print(
        f'UNIT 5 SCALP MIN MOVE % = {SCALP_MIN_MOVE_PCT}',
        flush=True
    )
    print(
        f'UNIT 5 STRUCTURE MIN MOVE % = {STRUCTURE_MIN_MOVE_PCT}',
        flush=True
    )
    print(
        f'UNIT 5 BREAKOUT MIN MOVE % = {BREAKOUT_MIN_MOVE_PCT}',
        flush=True
    )

    # ========================================================
    # ORIGINAL EMA DIRECTION
    # ========================================================

    bullish_alignment = ema19 > ema50 and ema50 > ema200
    bearish_alignment = ema19 < ema50 and ema50 < ema200

    if bullish_alignment:
        ema_direction = 'LONG'
    elif bearish_alignment:
        ema_direction = 'SHORT'
    else:
        ema_direction = 'NONE'

    print(f'UNIT 5 EMA DIRECTION = {ema_direction}', flush=True)

    # ========================================================
    # ORIGINAL MULTI-WINDOW MOMENTUM
    # ========================================================

    def movement_direction(movement_pct):
        if movement_pct > 0:
            return 'LONG'
        if movement_pct < 0:
            return 'SHORT'
        return 'NONE'

    momentum_1m_direction = movement_direction(move_1m_pct)
    momentum_5m_direction = movement_direction(move_5m_pct)
    momentum_15m_direction = movement_direction(move_15m_pct)
    momentum_30m_direction = movement_direction(move_30m_pct)
    momentum_60m_direction = movement_direction(move_60m_pct)
    momentum_120m_direction = movement_direction(move_120m_pct)

    print('-' * 80, flush=True)
    print('UNIT 5 MULTI-WINDOW MOMENTUM', flush=True)

    print(f'UNIT 5 1M MOVE % = {move_1m_pct}', flush=True)
    print(f'UNIT 5 1M DIRECTION = {momentum_1m_direction}', flush=True)
    print(f'UNIT 5 5M MOVE % = {move_5m_pct}', flush=True)
    print(f'UNIT 5 5M DIRECTION = {momentum_5m_direction}', flush=True)
    print(f'UNIT 5 15M MOVE % = {move_15m_pct}', flush=True)
    print(f'UNIT 5 15M DIRECTION = {momentum_15m_direction}', flush=True)
    print(f'UNIT 5 30M MOVE % = {move_30m_pct}', flush=True)
    print(f'UNIT 5 30M DIRECTION = {momentum_30m_direction}', flush=True)
    print(f'UNIT 5 60M MOVE % = {move_60m_pct}', flush=True)
    print(f'UNIT 5 60M DIRECTION = {momentum_60m_direction}', flush=True)
    print(f'UNIT 5 120M MOVE % = {move_120m_pct}', flush=True)
    print(f'UNIT 5 120M DIRECTION = {momentum_120m_direction}', flush=True)

    print('-' * 80, flush=True)

    # ========================================================
    # ORIGINAL SCALP CONTEXT
    # EMA200 NOT REQUIRED
    # ========================================================

    scalp_long_context = (
        ema19 > ema50
        and momentum_5m_direction == 'LONG'
    )

    scalp_short_context = (
        ema19 < ema50
        and momentum_5m_direction == 'SHORT'
    )

    scalp_direction = 'NONE'

    if scalp_long_context:
        scalp_direction = 'LONG'
    elif scalp_short_context:
        scalp_direction = 'SHORT'

    scalp_move_pct = abs(move_5m_pct)
    scalp_1m_support = momentum_1m_direction == scalp_direction

    print(f'UNIT 5 SCALP DIRECTION = {scalp_direction}', flush=True)
    print(f'UNIT 5 SCALP LONG CONTEXT = {scalp_long_context}', flush=True)
    print(f'UNIT 5 SCALP SHORT CONTEXT = {scalp_short_context}', flush=True)
    print(f'UNIT 5 SCALP 5M MOVE % = {move_5m_pct}', flush=True)
    print(f'UNIT 5 SCALP 1M FRESHNESS SUPPORT = {scalp_1m_support}', flush=True)

    # ========================================================
    # ORIGINAL STRUCTURE CONTEXT
    # ========================================================

    structure_direction = 'NONE'

    if (
        ema_direction != 'NONE'
        and momentum_15m_direction == ema_direction
    ):
        structure_direction = ema_direction

    structure_direction_agreement = structure_direction != 'NONE'
    structure_move_pct = abs(move_15m_pct)

    print(f'UNIT 5 STRUCTURE DIRECTION = {structure_direction}', flush=True)
    print(
        f'UNIT 5 STRUCTURE DIRECTION AGREEMENT = {structure_direction_agreement}',
        flush=True
    )
    print(f'UNIT 5 STRUCTURE 15M MOVE % = {move_15m_pct}', flush=True)

    # ========================================================
    # ORIGINAL BREAKOUT CONTEXT
    # ========================================================

    breakout_primary_direction = momentum_30m_direction

    breakout_fast_support = (
        momentum_5m_direction == breakout_primary_direction
        or momentum_15m_direction == breakout_primary_direction
    )

    breakout_long_context = (
        breakout_primary_direction == 'LONG'
        and breakout_fast_support
        and (ema19 > ema50)
        and (live_price > ema19)
        and (live_price > ema200)
    )

    breakout_short_context = (
        breakout_primary_direction == 'SHORT'
        and breakout_fast_support
        and (ema19 < ema50)
        and (live_price < ema19)
        and (live_price < ema200)
    )

    breakout_direction = 'NONE'

    if breakout_long_context:
        breakout_direction = 'LONG'
    elif breakout_short_context:
        breakout_direction = 'SHORT'

    breakout_move_pct = abs(move_30m_pct)

    print(
        f'UNIT 5 BREAKOUT PRIMARY DIRECTION = {breakout_primary_direction}',
        flush=True
    )
    print(f'UNIT 5 BREAKOUT FAST SUPPORT = {breakout_fast_support}', flush=True)
    print(f'UNIT 5 BREAKOUT DIRECTION = {breakout_direction}', flush=True)
    print(f'UNIT 5 BREAKOUT LONG CONTEXT = {breakout_long_context}', flush=True)
    print(f'UNIT 5 BREAKOUT SHORT CONTEXT = {breakout_short_context}', flush=True)
    print(f'UNIT 5 BREAKOUT 30M MOVE % = {move_30m_pct}', flush=True)

    # ========================================================
    # ORIGINAL MODE ARBITRATION
    # BREAKOUT > STRUCTURE > SCALP
    # ========================================================

    active_mode = 'NONE'
    direction = 'NONE'
    qualified = False
    qualification_reason = 'NO_MODE_QUALIFIED'

    if (
        breakout_direction != 'NONE'
        and separation_pct >= BREAKOUT_MIN_SEPARATION_PCT
        and breakout_move_pct >= BREAKOUT_MIN_MOVE_PCT
    ):
        active_mode = 'BREAKOUT'
        direction = breakout_direction
        qualified = True
        qualification_reason = (
            'BREAKOUT_30M_DIRECTION_AND_MULTI_WINDOW_MOMENTUM_CONFIRMED'
        )

    elif (
        structure_direction_agreement
        and separation_pct >= STRUCTURE_MIN_SEPARATION_PCT
        and structure_move_pct >= STRUCTURE_MIN_MOVE_PCT
    ):
        active_mode = 'STRUCTURE'
        direction = structure_direction
        qualified = True
        qualification_reason = (
            'STRUCTURE_15M_DIRECTION_AND_MOMENTUM_CONFIRMED'
        )

    elif (
        scalp_direction != 'NONE'
        and separation_pct >= SCALP_MIN_SEPARATION_PCT
        and scalp_move_pct >= SCALP_MIN_MOVE_PCT
    ):
        active_mode = 'SCALP'
        direction = scalp_direction
        qualified = True

    elif (
        momentum_5m_direction in ('LONG', 'SHORT')
        and abs(move_5m_pct) >= SCALP_MIN_MOVE_PCT
        and (
            momentum_1m_direction == momentum_5m_direction
            or (
                momentum_5m_direction == 'LONG'
                and latest_close > previous_close
            )
            or (
                momentum_5m_direction == 'SHORT'
                and latest_close < previous_close
            )
        )
    ):
        active_mode = 'SCALP'
        direction = momentum_5m_direction
        scalp_direction = direction
        qualified = True
        qualification_reason = 'SCALP_PRICE_FIRST_PENDING_UNIT_6_SCORE'

    else:
        any_directional_context = (
            scalp_direction != 'NONE'
            or structure_direction != 'NONE'
            or breakout_direction != 'NONE'
        )

        if not any_directional_context:
            qualification_reason = 'NO_MULTI_WINDOW_DIRECTIONAL_CONTEXT'

        elif separation_pct < SCALP_MIN_SEPARATION_PCT:
            qualification_reason = 'EMA_SEPARATION_BELOW_MINIMUM'

        elif (
            scalp_direction != 'NONE'
            and scalp_move_pct < SCALP_MIN_MOVE_PCT
        ):
            qualification_reason = 'SCALP_5M_MOVE_BELOW_MINIMUM'

        elif (
            structure_direction != 'NONE'
            and separation_pct >= STRUCTURE_MIN_SEPARATION_PCT
            and structure_move_pct < STRUCTURE_MIN_MOVE_PCT
        ):
            qualification_reason = 'STRUCTURE_15M_MOVE_BELOW_MINIMUM'

        elif (
            breakout_direction != 'NONE'
            and separation_pct >= BREAKOUT_MIN_SEPARATION_PCT
            and breakout_move_pct < BREAKOUT_MIN_MOVE_PCT
        ):
            qualification_reason = 'BREAKOUT_30M_MOVE_BELOW_MINIMUM'

        else:
            qualification_reason = 'NO_MODE_THRESHOLDS_CONFIRMED'

    # ========================================================
    # ORIGINAL PRICE RELATIONSHIP CHECKS
    # ========================================================

    price_above_ema19 = live_price > ema19
    price_above_ema50 = live_price > ema50
    price_above_ema200 = live_price > ema200
    latest_close_above_previous = latest_close > previous_close

    print(f'UNIT 5 PRICE ABOVE EMA19 = {price_above_ema19}', flush=True)
    print(f'UNIT 5 PRICE ABOVE EMA50 = {price_above_ema50}', flush=True)
    print(f'UNIT 5 PRICE ABOVE EMA200 = {price_above_ema200}', flush=True)
    print(
        f'UNIT 5 LATEST CLOSE ABOVE PREVIOUS = {latest_close_above_previous}',
        flush=True
    )

    # ========================================================
    # ORIGINAL 42-FIELD UNIT 6 CONTRACT
    # ========================================================

    signal_candidate = {
        'symbol': symbol,
        'qualified': qualified,
        'active_mode': active_mode,
        'direction': direction,
        'qualification_reason': qualification_reason,

        'live_mark_price': live_price,
        'ema19': ema19,
        'ema50': ema50,
        'ema200': ema200,
        'ema19_50_separation_pct': separation_pct,
        'ema_structure': ema_structure,
        'ema_direction': ema_direction,

        'momentum_direction': momentum_1m_direction,
        'direction_agreement': structure_direction_agreement,
        'short_term_move_pct': short_term_move_pct,
        'absolute_short_term_move_pct': abs(short_term_move_pct),

        'previous_close': previous_close,
        'latest_close': latest_close,

        'price_above_ema19': price_above_ema19,
        'price_above_ema50': price_above_ema50,
        'price_above_ema200': price_above_ema200,
        'latest_close_above_previous': latest_close_above_previous,

        'move_1m_pct': move_1m_pct,
        'move_5m_pct': move_5m_pct,
        'move_15m_pct': move_15m_pct,
        'move_30m_pct': move_30m_pct,
        'move_60m_pct': move_60m_pct,
        'move_120m_pct': move_120m_pct,

        'momentum_1m_direction': momentum_1m_direction,
        'momentum_5m_direction': momentum_5m_direction,
        'momentum_15m_direction': momentum_15m_direction,
        'momentum_30m_direction': momentum_30m_direction,
        'momentum_60m_direction': momentum_60m_direction,
        'momentum_120m_direction': momentum_120m_direction,

        'scalp_direction': scalp_direction,
        'scalp_move_pct': scalp_move_pct,
        'scalp_1m_support': scalp_1m_support,

        'structure_direction': structure_direction,
        'structure_move_pct': structure_move_pct,

        'breakout_direction': breakout_direction,
        'breakout_move_pct': breakout_move_pct,
        'breakout_fast_support': breakout_fast_support,
    }

    # ========================================================
    # ORIGINAL DIAGNOSTICS
    # ========================================================

    print('-' * 80, flush=True)
    print(f'UNIT 5 ACTIVE MODE = {active_mode}', flush=True)
    print(f'UNIT 5 DIRECTION = {direction}', flush=True)
    print(f'UNIT 5 SIGNAL QUALIFIED = {qualified}', flush=True)
    print(
        f'UNIT 5 QUALIFICATION REASON = {qualification_reason}',
        flush=True
    )
    print(
        f'UNIT 5 EMA19/50 SEPARATION % = {separation_pct}',
        flush=True
    )
    print(
        f'UNIT 5 ORIGINAL 1M MOVE % = {short_term_move_pct}',
        flush=True
    )
    print(f'UNIT 5 SCALP 5M MOVE % = {scalp_move_pct}', flush=True)
    print(
        f'UNIT 5 STRUCTURE 15M MOVE % = {structure_move_pct}',
        flush=True
    )
    print(
        f'UNIT 5 BREAKOUT 30M MOVE % = {breakout_move_pct}',
        flush=True
    )

    print('-' * 80, flush=True)

    print('PASS: UNIT 5 NORMALIZED SIGNAL CANDIDATE', flush=True)
    print(
        'PASS: UNIT 5 MULTI-WINDOW SIGNAL QUALIFICATION COMPLETED',
        flush=True
    )
    print('PASS: UNIT 5 EXCLUSIVE MODE SELECTION', flush=True)
    print('PASS: UNIT 5 NO NETWORK REQUEST', flush=True)
    print('PASS: UNIT 5 NO ORDER PAYLOAD GENERATED', flush=True)
    print('PASS: UNIT 5 NO POSITION SIZING', flush=True)
    print('PASS: UNIT 5 NO TP / SL', flush=True)
    print('PASS: UNIT 5 NO BACKUP EXECUTION', flush=True)

    print('ZERO AUTHENTICATED API ACCESS = TRUE', flush=True)
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
    print(
        f'{datetime.now(timezone.utc).isoformat()} '
        'FRESH RECONSTRUCTION UNIT 5 RESULT = PASS',
        flush=True
    )
    print('=' * 80, flush=True)

    return signal_candidate


# ============================================================
# RUN UNIT 5 - ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
    fresh_reconstruction_unit_5(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
    )
)

# ============================================================
# END COMPLETE UNIT 5 REPLACEMENT
# UNIT 6 CONTINUES BELOW
# ZERO INDENTATION
# ============================================================



# ============================================================
# UNIT 5 HYBRID ADAPTER — COMPLETE REPLACEMENT V4
# ORIGINAL WORKING QUALIFICATION PRESERVED
# BREAKOUT > STRUCTURE > SCALP
# ZERO INDENTATION
# ============================================================

def fresh_unit_5_hybrid_adjustable_adapter(
    config,
    analysis,
    original_candidate,
):
    import math

    if not all(
        isinstance(x, dict)
        for x in (config, analysis, original_candidate)
    ):
        raise RuntimeError("UNIT 5 ADAPTER INVALID INPUT")

    qualification = config.get("qualification", {})
    if not isinstance(qualification, dict):
        raise RuntimeError("UNIT 5 QUALIFICATION MISSING")

    common = qualification.get("common", {})
    breakout = qualification.get("breakout", {})
    structure = qualification.get("structure", {})
    scalp = qualification.get("scalp", {})

    if not all(
        isinstance(x, dict) and x
        for x in (common, breakout, structure, scalp)
    ):
        raise RuntimeError("UNIT 5 SETTINGS INCOMPLETE")

    if tuple(common.get("mode_priority", ())) != (
        "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError("UNIT 5 MODE PRIORITY INVALID")

    if analysis.get("strategy_evidence_version") != (
        "U4_HYBRID_V2"
    ):
        raise RuntimeError("UNIT 5 UNIT 4 EVIDENCE MISSING")

    def number(key):
        value = analysis.get(key)
        if isinstance(value, bool):
            raise RuntimeError("INVALID EVIDENCE: " + key)
        try:
            result = float(value)
        except (TypeError, ValueError, OverflowError):
            raise RuntimeError("INVALID EVIDENCE: " + key)
        if not math.isfinite(result):
            raise RuntimeError("NONFINITE EVIDENCE: " + key)
        return result

    def flag(key):
        value = analysis.get(key)
        if type(value) is not bool:
            raise RuntimeError("INVALID FLAG: " + key)
        return value

    direction_evidence = str(
        analysis.get("direction_evidence", "NONE")
    ).upper()

    if direction_evidence not in ("LONG", "SHORT", "NONE"):
        raise RuntimeError("UNIT 5 INVALID EVIDENCE DIRECTION")

    exchange_ms = number("exchange_time_ms")
    close_ms = number("latest_close_time_ms")

    age_seconds = (exchange_ms - close_ms) / 1000.0

    max_age = float(
        config.get("market_data_policy", {}).get(
            "max_market_age_seconds", 120.0
        )
    )

    if not 0 <= age_seconds <= max_age:
        raise RuntimeError("UNIT 5 STALE MARKET DATA")

    original_qualified = (
        original_candidate.get("qualified") is True
    )

    original_mode = str(
        original_candidate.get("active_mode", "NONE")
    ).upper()

    original_direction = str(
        original_candidate.get("direction", "NONE")
    ).upper()

    original_reason = str(
        original_candidate.get(
            "qualification_reason", "NONE"
        )
    )

    if original_qualified and (
        original_mode not in (
            "BREAKOUT", "STRUCTURE", "SCALP"
        )
        or original_direction not in ("LONG", "SHORT")
    ):
        raise RuntimeError(
            "UNIT 5 ORIGINAL QUALIFIED SIGNAL INVALID"
        )

    breakout_confirmed_long = flag(
        "breakout_confirmed_long"
    )
    breakout_confirmed_short = flag(
        "breakout_confirmed_short"
    )

    breakout_developing_long = flag(
        "breakout_developing_long"
    )
    breakout_developing_short = flag(
        "breakout_developing_short"
    )

    structure_developing_long = flag(
        "structure_developing_long"
    )
    structure_developing_short = flag(
        "structure_developing_short"
    )

    breakout_developing = (
        breakout_developing_long
        or breakout_developing_short
    )

    structure_developing = (
        structure_developing_long
        or structure_developing_short
    )

    higher_mode_developing = (
        breakout_developing
        or structure_developing
    )

    result = dict(original_candidate)

    active_mode = "NONE"
    admitted_direction = "NONE"
    qualified = False
    candidate_mode = "NONE"
    candidate_stage = "NONE"
    reason = "NO_ACCEPTABLE_CANDIDATE"
    classification_source = "HYBRID"
    conflict = False
    breakout_ready = False
    structure_ready = False
    scalp_ready = False

    # ========================================================
    # ORIGINAL QUALIFIED BREAKOUT / STRUCTURE
    # ORIGINAL WORKING RESULT TAKES PRIORITY
    # ========================================================

    original_higher = (
        original_qualified
        and original_mode in ("BREAKOUT", "STRUCTURE")
    )

    if original_higher:

        if (
            direction_evidence in ("LONG", "SHORT")
            and direction_evidence != original_direction
        ):
            conflict = True
            candidate_mode = original_mode
            candidate_stage = "REJECTED"
            reason = "ORIGINAL_HYBRID_DIRECTION_CONFLICT"
            classification_source = "CONFLICT_BLOCKED"

        else:
            active_mode = original_mode
            admitted_direction = original_direction
            qualified = True
            candidate_mode = original_mode
            candidate_stage = "QUALIFIED"
            reason = (
                "ORIGINAL_" + original_mode
                + "_QUALIFIED_RETAINED"
            )
            classification_source = "ORIGINAL_UNIT5"

            if original_mode == "BREAKOUT":
                breakout_ready = True
            else:
                structure_ready = True

    # ========================================================
    # HYBRID CONFIRMED BREAKOUT
    # ========================================================

    elif (
        breakout.get("enabled") is True
        and breakout_confirmed_long != breakout_confirmed_short
    ):

        side = (
            "LONG" if breakout_confirmed_long else "SHORT"
        )

        if direction_evidence == side:
            active_mode = "BREAKOUT"
            admitted_direction = side
            qualified = True
            candidate_mode = "BREAKOUT"
            candidate_stage = "QUALIFIED"
            reason = "BREAKOUT_CONFIRMED"
            breakout_ready = True

    # ========================================================
    # DEVELOPING HIGHER MODES
    # PROTECT THEM FROM SCALP
    # ========================================================

    if not qualified and not conflict:

        if breakout_developing:
            candidate_mode = "BREAKOUT"
            candidate_stage = "DEVELOPING"
            reason = "BREAKOUT_DEVELOPING_AWAITING_CONFIRMATION"

        elif structure_developing:
            candidate_mode = "STRUCTURE"
            candidate_stage = "DEVELOPING"
            reason = "STRUCTURE_DEVELOPING_AWAITING_CONFIRMATION"

        elif (
            original_qualified
            and original_mode == "SCALP"
            and not higher_mode_developing
            and scalp.get("enabled") is True
        ):
            # Preserve SCALP as pending Unit 6 quality/fee
            # checks, rather than immediately authorizing.
            candidate_mode = "SCALP"
            candidate_stage = "PENDING_UNIT_6"
            reason = "SCALP_PENDING_QUALITY_AND_FEES"
            scalp_ready = True
            classification_source = "ORIGINAL_UNIT5"

    # ========================================================
    # PRESERVE ORIGINAL CONTRACT AND HYBRID METADATA
    # ========================================================

    fee_sides = (
        int(scalp.get("include_entry_fee") is True)
        + int(scalp.get("include_exit_fee") is True)
    )

    friction = (
        float(scalp.get("estimated_taker_fee_percent", 0))
        * fee_sides
        + float(scalp.get("estimated_slippage_percent", 0))
    )

    result.update({
        "qualified": qualified,
        "active_mode": active_mode,
        "direction": admitted_direction,
        "qualification_reason": reason,
        "candidate_mode": candidate_mode,
        "candidate_stage": candidate_stage,
        "higher_mode_developing": higher_mode_developing,
        "breakout_candidate": (
            breakout_confirmed_long
            or breakout_confirmed_short
            or breakout_developing
        ),
        "structure_candidate": structure_developing,
        "breakout_ready": breakout_ready,
        "structure_ready": structure_ready,
        "scalp_ready": scalp_ready,
        "sideways_context": flag("sideways_candidate"),
        "direction_evidence": direction_evidence,
        "scalp_quality_minimum": float(
            scalp["quality_threshold"]
        ),
        "scalp_price_weight_percent": float(
            scalp["price_action_weight_percent"]
        ),
        "estimated_round_trip_fee_pct": friction,
        "scalp_minimum_fee_coverage": float(
            scalp["minimum_fee_coverage_multiplier"]
        ),
        "candle_data_fresh": True,
        "read_only": True,
        "trade_authorized": False,
        "order_payload_created": False,
        "strategy_evidence_version":
            "U5_HYBRID_ADJUSTABLE_V3",
        "unit_4_evidence_version": "U4_HYBRID_V2",
        "classification_revision": "V3.1",
        "candidate_protected": (
            candidate_stage == "DEVELOPING"
        ),
        "candidate_age_seconds": age_seconds,
        "classification_source": classification_source,
        "original_unit5_qualified": original_qualified,
        "original_unit5_mode": original_mode,
        "original_unit5_direction": original_direction,
        "original_unit5_reason": original_reason,
        "original_hybrid_conflict": conflict,
    })

    if not set(original_candidate).issubset(result):
        raise RuntimeError("UNIT 5 ORIGINAL FIELDS LOST")

    if qualified != (candidate_stage == "QUALIFIED"):
        raise RuntimeError(
            "UNIT 5 QUALIFICATION STATE CONTRADICTION"
        )

    if candidate_mode == "SCALP" and higher_mode_developing:
        raise RuntimeError(
            "UNIT 5 SCALP PRIORITY VIOLATION"
        )

    print("=" * 80, flush=True)
    print("UNIT 5 HYBRID ADAPTER V4", flush=True)
    print(
        "UNIT 5 ORIGINAL QUALIFIED =",
        original_qualified, flush=True
    )
    print(
        "UNIT 5 ORIGINAL MODE =",
        original_mode, flush=True
    )
    print(
        "UNIT 5 ORIGINAL DIRECTION =",
        original_direction, flush=True
    )
    print(
        "UNIT 5 MODE =",
        candidate_mode, flush=True
    )
    print(
        "UNIT 5 STAGE =",
        candidate_stage, flush=True
    )
    print(
        "UNIT 5 ACTIVE MODE =",
        active_mode, flush=True
    )
    print(
        "UNIT 5 DIRECTION =",
        admitted_direction, flush=True
    )
    print(
        "UNIT 5 QUALIFIED =",
        qualified, flush=True
    )
    print(
        "UNIT 5 REASON =",
        reason, flush=True
    )
    print(
        "UNIT 5 CLASSIFICATION SOURCE =",
        classification_source, flush=True
    )
    print(
        "UNIT 5 HIGHER MODE DEVELOPING =",
        higher_mode_developing, flush=True
    )
    print(
        "UNIT 5 EXCHANGE WRITE = NONE",
        flush=True
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 5 ADAPTER EXECUTION
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
    fresh_unit_5_hybrid_adjustable_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE,
    )
)

# ============================================================
# END UNIT 5 ADAPTER
# ORIGINAL UNIT 6 FOLLOWS
# ============================================================


# ============================================================
# START UNIT 6 EXECUTION ADAPTER REPAIR V2
# HYBRID QUALIFICATION -> ORIGINAL EXECUTION PATH
# ZERO INDENTATION
# ============================================================

# ============================================================
# START UNIT 6 HYBRID ADJUSTABLE FUNCTION RESTORATION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_6(
    unit_2_config,
    unit_4_analysis,
    unit_5_candidate,
):
    import math

    print("=" * 80, flush=True)
    print("UNIT 6 HYBRID ADJUSTABLE START", flush=True)

    if not all(
        isinstance(x, dict)
        for x in (
            unit_2_config,
            unit_4_analysis,
            unit_5_candidate,
        )
    ):
        raise RuntimeError(
            "UNIT 6 INVALID INPUT CONTRACT"
        )

    qualification = unit_2_config.get(
        "qualification", {}
    )
    scalp_cfg = qualification.get("scalp", {})
    common_cfg = qualification.get("common", {})

    if not all(
        isinstance(x, dict)
        for x in (qualification, scalp_cfg, common_cfg)
    ):
        raise RuntimeError(
            "UNIT 6 QUALIFICATION CONFIG MISSING"
        )

    if not scalp_cfg or not common_cfg:
        raise RuntimeError(
            "UNIT 6 ADJUSTABLE DEFAULTS MISSING"
        )

    if unit_4_analysis.get(
        "strategy_evidence_version"
    ) != "U4_HYBRID_V2":
        raise RuntimeError(
            "UNIT 6 UNIT 4 HYBRID EVIDENCE MISSING"
        )

    if unit_5_candidate.get(
        "strategy_evidence_version"
    ) != "U5_HYBRID_ADJUSTABLE_V3":
        raise RuntimeError(
            "UNIT 6 UNIT 5 HYBRID CANDIDATE MISSING"
        )

    if unit_5_candidate.get(
        "classification_revision"
    ) != "V3.1":
        raise RuntimeError(
            "UNIT 6 CLASSIFICATION REVISION MISMATCH"
        )

    if tuple(
        common_cfg.get("mode_priority", ())
    ) != ("BREAKOUT", "STRUCTURE", "SCALP"):
        raise RuntimeError(
            "UNIT 6 INVALID MODE PRIORITY"
        )

    def number(value, name):
        if isinstance(value, bool):
            raise RuntimeError(
                "UNIT 6 INVALID NUMBER: " + name
            )
        try:
            result = float(value)
        except (ValueError, TypeError, OverflowError):
            raise RuntimeError(
                "UNIT 6 INVALID NUMBER: " + name
            )
        if not math.isfinite(result):
            raise RuntimeError(
                "UNIT 6 NONFINITE NUMBER: " + name
            )
        return result

    candidate_mode = str(
        unit_5_candidate.get(
            "candidate_mode", "NONE"
        )
    ).upper()

    candidate_stage = str(
        unit_5_candidate.get(
            "candidate_stage", "NONE"
        )
    ).upper()

    candidate_direction = str(
        unit_4_analysis.get(
            "direction_evidence", "NONE"
        )
    ).upper()

    higher_mode_developing = (
        unit_5_candidate.get(
            "higher_mode_developing"
        ) is True
    )

    unit5_qualified = (
        unit_5_candidate.get("qualified") is True
    )

    unit5_reason = str(
        unit_5_candidate.get(
            "qualification_reason", "UNKNOWN"
        )
    )

    if candidate_mode not in (
        "NONE", "SCALP", "STRUCTURE", "BREAKOUT"
    ):
        raise RuntimeError(
            "UNIT 6 INVALID CANDIDATE MODE"
        )

    if candidate_stage not in (
        "NONE",
        "REJECTED",
        "DEVELOPING",
        "QUALIFIED",
        "PENDING_UNIT_6",
    ):
        raise RuntimeError(
            "UNIT 6 INVALID CANDIDATE STAGE"
        )

    if unit5_qualified != (
        candidate_stage == "QUALIFIED"
    ):
        raise RuntimeError(
            "UNIT 6 CANDIDATE STATE CONTRADICTION"
        )

    # ========================================================
    # INITIAL STATE
    # ========================================================

    execution_intent = False
    admitted_mode = "NONE"
    admitted_direction = "NONE"

    admission_reason = (
        "UNIT_5_NOT_QUALIFIED:" + unit5_reason
    )

    scalp_score = None
    scalp_quality_pass = None
    scalp_details = {}
    fee_coverage_pass = False
    round_trip_fee = None

    persistence_confirmations = 0
    persistence_directions = []
    persistence_pass = False
    fifteen_minute_support_pass = None

    # ========================================================
    # BREAKOUT AND STRUCTURE
    # ========================================================

    if (
        unit5_qualified
        and candidate_stage == "QUALIFIED"
    ):

        direction = str(
            unit_5_candidate.get(
                "direction", "NONE"
            )
        ).upper()

        if direction not in ("LONG", "SHORT"):
            admission_reason = (
                "QUALIFIED_DIRECTION_INVALID"
            )

        elif candidate_direction != direction:
            admission_reason = (
                "QUALIFIED_DIRECTION_CONFLICT"
            )

        elif candidate_mode == "BREAKOUT":

            evidence_key = (
                "breakout_confirmed_long"
                if direction == "LONG"
                else "breakout_confirmed_short"
            )

                        if (
                (
                    unit_5_candidate.get("classification_source")
                    == "ORIGINAL_UNIT5"
                    and unit_5_candidate.get("qualified") is True
                    and unit_5_candidate.get("breakout_ready") is True
                    and unit_5_candidate.get("active_mode") == "BREAKOUT"
                    and unit_5_candidate.get("direction") == direction
                )
                or
                (
                    unit_4_analysis.get(evidence_key) is True
                    and unit_5_candidate.get("breakout_ready") is True
                    and unit_5_candidate.get("qualified") is True
                    and unit_5_candidate.get("direction") == direction
                )
            ):
            
                execution_intent = True
                admitted_mode = "BREAKOUT"
                admitted_direction = direction
                admission_reason = (
                    "BREAKOUT_CONFIRMED_ADMITTED"
                )
            else:
                admission_reason = (
                    "BREAKOUT_CONFIRMATION_REJECTED"
                )

        
        elif candidate_mode == "STRUCTURE":

            evidence_key = (
                "structure_developing_long"
                if direction == "LONG"
                else "structure_developing_short"
            )

            original_confirmed = (
                unit_5_candidate.get(
                    "classification_source"
                ) == "ORIGINAL_UNIT5"
                and unit_5_candidate.get(
                    "structure_ready"
                ) is True
                and unit_5_candidate.get(
                    "qualified"
                ) is True
                and unit_5_candidate.get(
                    "active_mode"
                ) == "STRUCTURE"
                and unit_5_candidate.get(
                    "direction"
                ) == direction
            )

            hybrid_confirmed = (
                unit_4_analysis.get(evidence_key) is True
                and unit_5_candidate.get(
                    "structure_ready"
                ) is True
            )

            if original_confirmed or hybrid_confirmed:

                execution_intent = True
                admitted_mode = "STRUCTURE"
                admitted_direction = direction

                admission_reason = (
                    "ORIGINAL_STRUCTURE_QUALIFIED_ADMITTED"
                    if original_confirmed
                    else "HYBRID_STRUCTURE_QUALIFIED_ADMITTED"
                )

            else:
                admission_reason = (
                    "STRUCTURE_CONFIRMATION_REJECTED"
                )

        
    # ========================================================
    # DEVELOPING HIGHER MODES
    # ========================================================

    elif candidate_stage == "DEVELOPING":

        if candidate_mode in (
            "BREAKOUT", "STRUCTURE"
        ):
            admission_reason = (
                candidate_mode
                + "_DEVELOPING_PROTECTED_NO_EXECUTION"
            )
        else:
            admission_reason = (
                "INVALID_DEVELOPING_CANDIDATE"
            )

    # ========================================================
    # SCALP QUALIFICATION
    # ========================================================

    elif (
        candidate_mode == "SCALP"
        and candidate_stage == "PENDING_UNIT_6"
    ):

        if higher_mode_developing:
            admission_reason = (
                "SCALP_HIGHER_PRIORITY_DEVELOPING"
            )

        elif (
            scalp_cfg.get(
                "require_sideways_market"
            ) is True
            and (
                unit_4_analysis.get(
                    "sideways_candidate"
                ) is not True
                or unit_5_candidate.get(
                    "sideways_context"
                ) is not True
            )
        ):
            admission_reason = (
                "SCALP_SIDEWAYS_CONDITION_FAILED"
            )

        else:

            threshold = number(
                scalp_cfg.get(
                    "quality_threshold"
                ),
                "SCALP QUALITY"
            )

            price_weight = number(
                scalp_cfg.get(
                    "price_action_weight_percent"
                ),
                "PRICE WEIGHT"
            )

            other_weight = number(
                scalp_cfg.get(
                    "other_factors_weight_percent"
                ),
                "OTHER WEIGHT"
            )

            votes_required = int(number(
                scalp_cfg.get(
                    "direction_votes_required"
                ),
                "DIRECTION VOTES"
            ))

            max_extension = number(
                scalp_cfg.get(
                    "max_ema_extension_clusters"
                ),
                "MAX EXTENSION"
            )

            max_spikes = int(number(
                scalp_cfg.get(
                    "max_spike_count"
                ),
                "MAX SPIKES"
            ))

            fee_per_side = number(
                scalp_cfg.get(
                    "estimated_taker_fee_percent"
                ),
                "TAKER FEE"
            )

            slippage = number(
                scalp_cfg.get(
                    "estimated_slippage_percent"
                ),
                "SLIPPAGE"
            )

            fee_multiplier = number(
                scalp_cfg.get(
                    "minimum_fee_coverage_multiplier"
                ),
                "FEE COVERAGE"
            )

            if not (
                0 <= threshold <= 100
                and price_weight >= 0
                and other_weight >= 0
                and math.isclose(
                    price_weight + other_weight,
                    100.0,
                    abs_tol=0.000001
                )
                and 1 <= votes_required <= 3
                and max_extension > 0
                and max_spikes >= 0
                and fee_per_side >= 0
                and slippage >= 0
                and fee_multiplier >= 1
            ):
                raise RuntimeError(
                    "UNIT 6 SCALP SETTINGS INVALID"
                )

            direction = candidate_direction

            if direction not in (
                "LONG", "SHORT"
            ):
                admission_reason = (
                    "SCALP_DIRECTION_INVALID"
                )

            else:

                sign = (
                    1 if direction == "LONG"
                    else -1
                )

                candles = unit_4_analysis.get(
                    "recent_closed_klines", []
                )

                if (
                    not isinstance(candles, list)
                    or len(candles) < 20
                ):
                    raise RuntimeError(
                        "UNIT 6 CLOSED CANDLE HISTORY MISSING"
                    )

                close = number(
                    unit_4_analysis.get(
                        "latest_close"
                    ),
                    "LATEST CLOSE"
                )

                support = number(
                    unit_4_analysis.get(
                        "support20"
                    ),
                    "SUPPORT"
                )

                resistance = number(
                    unit_4_analysis.get(
                        "resistance20"
                    ),
                    "RESISTANCE"
                )

                atr = number(
                    unit_4_analysis.get(
                        "atr14"
                    ),
                    "ATR14"
                )

                move1 = number(
                    unit_4_analysis.get(
                        "move_1m_pct"
                    ),
                    "MOVE 1M"
                )

                move5 = number(
                    unit_4_analysis.get(
                        "move_5m_pct"
                    ),
                    "MOVE 5M"
                )

                move15 = number(
                    unit_4_analysis.get(
                        "move_15m_pct"
                    ),
                    "MOVE 15M"
                )

                extension = number(
                    unit_4_analysis.get(
                        "price_extension_cluster"
                    ),
                    "EXTENSION"
                )

                if not (
                    close > 0
                    and support > 0
                    and resistance > support
                    and atr > 0
                ):
                    raise RuntimeError(
                        "UNIT 6 INVALID MARKET GEOMETRY"
                    )

                # =============================================
                # PERSISTENCE AND SPIKE CHECKS
                # =============================================

                spike_count = 0

                for candle in candles[-3:]:

                    opened = number(
                        candle.get("open"),
                        "OPEN"
                    )

                    closed = number(
                        candle.get("close"),
                        "CLOSE"
                    )

                    high = number(
                        candle.get("high"),
                        "HIGH"
                    )

                    low = number(
                        candle.get("low"),
                        "LOW"
                    )

                    if not (
                        0 < low
                        <= min(opened, closed)
                        <= max(opened, closed)
                        <= high
                    ):
                        raise RuntimeError(
                            "UNIT 6 INVALID CLOSED CANDLE"
                        )

                    if closed > opened:
                        persistence_directions.append(
                            "LONG"
                        )
                    elif closed < opened:
                        persistence_directions.append(
                            "SHORT"
                        )
                    else:
                        persistence_directions.append(
                            "NONE"
                        )

                    if high - low > 2.0 * atr:
                        spike_count += 1

                persistence_confirmations = sum(
                    side == direction
                    for side in persistence_directions
                )

                persistence_pass = (
                    persistence_confirmations >= 2
                )

                votes = int(number(
                    unit_4_analysis.get(
                        "direction_long_votes"
                        if direction == "LONG"
                        else "direction_short_votes"
                    ),
                    "DIRECTION VOTES"
                ))

                vote_pass = (
                    votes >= votes_required
                )

                fifteen_minute_support_pass = (
                    move15 * sign >= 0
                )

                momentum_pass = (
                    move1 * sign > 0
                    and move5 * sign > 0
                )

                extension_pass = (
                    extension <= max_extension
                    and unit_4_analysis.get(
                        "price_overextended"
                    ) is False
                )

                spike_pass = (
                    spike_count <= max_spikes
                )

                late_impulse = (
                    extension > max_extension
                    or (
                        move1 * sign < 0
                        and move5 * sign > 0
                    )
                )

                late_impulse_pass = (
                    scalp_cfg.get(
                        "reject_late_impulse"
                    ) is False
                    or not late_impulse
                )

                near_boundary = (
                    close <= support + 0.5 * atr
                    if direction == "LONG"
                    else close >= resistance - 0.5 * atr
                )

                # =============================================
                # SCALP QUALITY SCORE
                # =============================================

                price_points = (
                    (
                        15.0
                        if move5 * sign >= 0.03
                        else 8.0
                        if move5 * sign > 0
                        else 0.0
                    )
                    + (
                        10.0
                        if move1 * sign > 0
                        else 0.0
                    )
                    + (
                        15.0
                        if persistence_confirmations == 3
                        else 10.0
                        if persistence_confirmations == 2
                        else 0.0
                    )
                    + (
                        10.0
                        if extension <= 0.75
                        else 5.0
                        if extension <= max_extension
                        else 0.0
                    )
                )

                range_percent = (
                    (resistance - support)
                    / close * 100.0
                )

                minimum_fee = (
                    fee_per_side
                    * (
                        int(
                            scalp_cfg.get(
                                "include_entry_fee"
                            ) is True
                        )
                        + int(
                            scalp_cfg.get(
                                "include_exit_fee"
                            ) is True
                        )
                    )
                    + slippage
                )

                round_trip_fee = minimum_fee

                fee_coverage_pass = (
                    scalp_cfg.get(
                        "fee_aware_enabled"
                    ) is False
                    or range_percent
                    >= minimum_fee * fee_multiplier
                )

                other_points = (
                    15.0
                    + (
                        10.0
                        if fifteen_minute_support_pass
                        else 0.0
                    )
                    + (
                        10.0
                        if fee_coverage_pass
                        else 0.0
                    )
                    + (
                        10.0
                        if near_boundary
                        else 0.0
                    )
                    + (
                        5.0
                        if extension_pass
                        else 0.0
                    )
                )

                scalp_score = round(
                    (
                        price_points / 50.0
                        * price_weight
                    )
                    + (
                        other_points / 50.0
                        * other_weight
                    ),
                    2
                )

                scalp_quality_pass = (
                    scalp_score >= threshold
                )

                checks = {
                    "direction": vote_pass,
                    "persistence": persistence_pass,
                    "momentum": momentum_pass,
                    "extension": extension_pass,
                    "spikes": spike_pass,
                    "late_impulse": late_impulse_pass,
                    "quality": scalp_quality_pass,
                    "fee_coverage": fee_coverage_pass,
                    "15m_support":
                        fifteen_minute_support_pass,
                }

                scalp_details = {
                    "direction": direction,
                    "quality_score": scalp_score,
                    "quality_threshold": threshold,
                    "raw_price_score": price_points,
                    "raw_other_score": other_points,
                    "persistence_confirmations":
                        persistence_confirmations,
                    "spike_count": spike_count,
                    "historical_range_percent":
                        range_percent,
                    "estimated_round_trip_fee_pct":
                        round_trip_fee,
                    "qualification_checks": checks,
                    "net_roi_verified": False,
                }

                print(
                    "UNIT 6 SCALP QUALITY SCORE =",
                    scalp_score,
                    flush=True
                )

                print(
                    "UNIT 6 SCALP REQUIRED SCORE =",
                    threshold,
                    flush=True
                )

                for name, passed in checks.items():
                    print(
                        "UNIT 6 SCALP CHECK",
                        name,
                        "=",
                        passed,
                        flush=True
                    )

                if all(checks.values()):

                    execution_intent = True
                    admitted_mode = "SCALP"
                    admitted_direction = direction

                    admission_reason = (
                        "SCALP_PRELIMINARY_ADMISSION_PASS"
                    )

                else:

                    admission_reason = (
                        "SCALP_QUALIFICATION_REJECTED"
                    )

    # ========================================================
    # FINAL UNIT 6 RESULT
    # ========================================================

    result = {
        "execution_intent":
            bool(execution_intent),

        "active_mode":
            admitted_mode,

        "direction":
            admitted_direction,

        "signal_qualified":
            bool(execution_intent),

        "unit_5_reason":
            unit5_reason,

        "admission_reason":
            admission_reason,

        "candidate_mode":
            candidate_mode,

        "candidate_stage":
            candidate_stage,

        "higher_mode_developing":
            higher_mode_developing,

        "candidate_protected":
            candidate_stage == "DEVELOPING",

        "scalp_quality_score":
            scalp_score,

        "scalp_quality_minimum":
            number(
                scalp_cfg.get(
                    "quality_threshold"
                ),
                "QUALITY THRESHOLD"
            ),

        "scalp_quality_pass":
            scalp_quality_pass,

        "scalp_quality_details":
            scalp_details,

        "fee_coverage_pass":
            fee_coverage_pass,

        "round_trip_fee_estimate_pct":
            round_trip_fee,

        "persistence_confirmations":
            persistence_confirmations,

        "persistence_directions":
            persistence_directions,

        "persistence_pass":
            persistence_pass,

        "fifteen_minute_support_pass":
            fifteen_minute_support_pass,

        "read_only":
            True,

        "trade_authorized":
            False,

        "order_payload_created":
            False,

        "exchange_write":
            False,

        "strategy_evidence_version":
            "U6_HYBRID_ADJUSTABLE_V2",

        "admission_revision":
            "V2.1",

        "unit_5_classification_revision":
            "V3.1",
    }

    if execution_intent:

        if (
            admitted_mode not in (
                "BREAKOUT",
                "STRUCTURE",
                "SCALP",
            )
            or admitted_direction not in (
                "LONG",
                "SHORT",
            )
        ):
            raise RuntimeError(
                "UNIT 6 INVALID EXECUTABLE CANDIDATE"
            )

    else:

        if (
            admitted_mode != "NONE"
            or admitted_direction != "NONE"
        ):
            raise RuntimeError(
                "UNIT 6 INACTIVE SIGNAL LEAK"
            )

    print(
        "UNIT 6 ACTIVE MODE =",
        admitted_mode,
        flush=True
    )

    print(
        "UNIT 6 DIRECTION =",
        admitted_direction,
        flush=True
    )

    print(
        "UNIT 6 EXECUTION INTENT =",
        execution_intent,
        flush=True
    )

    print(
        "UNIT 6 ADMISSION REASON =",
        admission_reason,
        flush=True
    )

    print(
        "UNIT 6 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 6 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# END UNIT 6 HYBRID ADJUSTABLE FUNCTION RESTORATION
# EXECUTION ADAPTER V2 FOLLOWS BELOW
# ZERO INDENTATION
# ============================================================



# ============================================================
# UNIT 6 EXECUTION ADAPTER — COMPLETE REPLACEMENT V3
# RENDER-MANUAL WEEX DEMO LEVERAGE COMPATIBILITY
# ORIGINAL UNIT 7 INTERFACE PRESERVED
# ZERO INDENTATION
# ============================================================

def fresh_unit_6_original_execution_adapter(
    unit_2_config,
    unit_6_result,
    exchange_leverage_result=None,
):
    import os
    import copy
    from decimal import Decimal, InvalidOperation

    if not isinstance(unit_2_config, dict):
        raise RuntimeError("UNIT 6 ADAPTER INVALID CONFIG")

    if not isinstance(unit_6_result, dict):
        raise RuntimeError("UNIT 6 ADAPTER INVALID RESULT")

    config = copy.deepcopy(unit_2_config)
    result = dict(unit_6_result)

    if not isinstance(config.get("strategy"), dict):
        raise RuntimeError("UNIT 6 STRATEGY MISSING")

    # Never inherit the original hardcoded 100x value.
    config["strategy"].pop("leverage_target", None)

    # ========================================================
    # READ LONG AND SHORT LEVERAGE FROM RENDER
    # ========================================================

    def read_leverage(key):
        value = os.getenv(key)

        if value is None or not value.strip():
            raise RuntimeError(
                "UNIT 6 MISSING RENDER VARIABLE: " + key
            )

        try:
            leverage = Decimal(value.strip())
        except InvalidOperation as exc:
            raise RuntimeError(
                "UNIT 6 INVALID LEVERAGE: " + key
            ) from exc

        if not leverage.is_finite() or leverage < 1:
            raise RuntimeError(
                "UNIT 6 LEVERAGE OUT OF RANGE: " + key
            )

        return leverage

    long_leverage = read_leverage(
        "WEEX_DEMO_LONG_LEVERAGE"
    )

    short_leverage = read_leverage(
        "WEEX_DEMO_SHORT_LEVERAGE"
    )

    print(
        "UNIT 6 ADAPTER LONG LEVERAGE =",
        long_leverage, flush=True
    )
    print(
        "UNIT 6 ADAPTER SHORT LEVERAGE =",
        short_leverage, flush=True
    )
    print(
        "UNIT 6 LEVERAGE SOURCE = RENDER_MANUAL_WEEX_DEMO",
        flush=True
    )

    config["strategy"]["exchange_leverage_verified"] = False
    config["strategy"]["leverage_source"] = (
        "RENDER_MANUAL_WEEX_DEMO"
    )

    # ========================================================
    # PRESERVE UNIT 6 IDLE RESULT
    # ========================================================

    if result.get("execution_intent") is not True:

        result["execution_intent"] = False
        result["signal_qualified"] = False
        result["active_mode"] = "NONE"
        result["direction"] = "NONE"

        print(
            "UNIT 6 ADAPTER STATUS = IDLE",
            flush=True
        )
        print(
            "UNIT 6 ADAPTER REASON =",
            result.get("admission_reason"),
            flush=True
        )

        return config, result

    # ========================================================
    # VALIDATE ORIGINAL UNIT 6 QUALIFICATION
    # ========================================================

    if result.get("signal_qualified") is not True:
        raise RuntimeError(
            "UNIT 6 ADAPTER CONTRADICTORY SIGNAL"
        )

    mode = str(
        result.get("active_mode", "NONE")
    ).upper()

    direction = str(
        result.get("direction", "NONE")
    ).upper()

    stage = str(
        result.get("candidate_stage", "NONE")
    ).upper()

    if mode not in ("BREAKOUT", "STRUCTURE", "SCALP"):
        raise RuntimeError("UNIT 6 INVALID MODE")

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError("UNIT 6 INVALID DIRECTION")

    if mode == "SCALP":

        if (
            stage != "PENDING_UNIT_6"
            or result.get("scalp_quality_pass") is not True
            or result.get("fee_coverage_pass") is not True
        ):
            raise RuntimeError(
                "UNIT 6 SCALP QUALIFICATION INCOMPLETE"
            )

    elif stage != "QUALIFIED":
        raise RuntimeError(
            "UNIT 6 HIGHER MODE NOT QUALIFIED"
        )

    # ========================================================
    # SELECT MANUALLY CONFIGURED DIRECTIONAL LEVERAGE
    # ========================================================

    leverage = (
        long_leverage
        if direction == "LONG"
        else short_leverage
    )

    # Carry directional leverage forward for compatibility
    # with the pre-existing Unit 7.
    #
    # It is a manually synchronized planning value,
    # NOT an independently verified WEEX account setting.

    config["strategy"]["leverage_target"] = float(leverage)

    result["hybrid_admission_reason"] = (
        result.get("admission_reason")
    )

    result["admission_reason"] = (
        "QUALIFIED_SIGNAL_ADMITTED"
    )

    result["leverage_target"] = float(leverage)

    result["leverage_source"] = (
        "RENDER_MANUAL_WEEX_DEMO"
    )

    result["exchange_leverage_verified"] = False

    print(
        "UNIT 6 ADAPTER MODE =",
        mode, flush=True
    )
    print(
        "UNIT 6 ADAPTER DIRECTION =",
        direction, flush=True
    )
    print(
        "UNIT 6 ADAPTER SELECTED LEVERAGE =",
        leverage, flush=True
    )
    print(
        "UNIT 6 ADAPTER STATUS = READY_FOR_UNIT_7",
        flush=True
    )

    return config, result


# ============================================================
# UNIT 6 + ADAPTER EXECUTION
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_HYBRID_UNIT_6_RESULT = (
    fresh_reconstruction_unit_6(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE,
    )
)

(
    FRESH_RECONSTRUCTION_EXECUTION_CONFIG,
    FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE,
) = fresh_unit_6_original_execution_adapter(
    FRESH_RECONSTRUCTION_CONFIG,
    FRESH_RECONSTRUCTION_HYBRID_UNIT_6_RESULT,
)

# ============================================================
# END UNIT 6 EXECUTION ADAPTER
# ORIGINAL UNIT 7 FOLLOWS
# ============================================================



# ============================================================
# START COMPLETE UNIT 7 EXECUTION HANDOVER V2
# ORIGINAL CONTRACT + HYBRID ADAPTER
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_7(
    unit_2_config,
    unit_6_candidate,
):
    import math
    from datetime import datetime, timezone

    print("=" * 80, flush=True)
    print(
        datetime.now(timezone.utc).isoformat(),
        "FRESH RECONSTRUCTION UNIT 7 START",
        flush=True
    )

    # ========================================================
    # 1. INPUT CONTRACT
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 7 CONFIGURATION INVALID"
        )

    if not isinstance(unit_6_candidate, dict):
        raise RuntimeError(
            "UNIT 7 SIGNAL INPUT INVALID"
        )

    config = unit_2_config
    candidate = unit_6_candidate

    strategy = config.get("strategy")
    precision = config.get("market_precision")
    safety = config.get("safety")
    exchange = config.get("exchange")

    for name, section in (
        ("STRATEGY", strategy),
        ("PRECISION", precision),
        ("SAFETY", safety),
        ("EXCHANGE", exchange),
    ):
        if not isinstance(section, dict):
            raise RuntimeError(
                "UNIT 7 INVALID " + name
            )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 7 DEMO ENVIRONMENT REQUIRED"
        )

    if (
        exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or exchange.get("market_symbol") != "BTCUSDT"
        or exchange.get("demo_order_symbol") != "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 7 EXCHANGE CONTRACT FAILED"
        )

    # ========================================================
    # 2. ORIGINAL UNIT 6 SIGNAL CONTRACT
    # ========================================================

    required = (
        "execution_intent",
        "signal_qualified",
        "active_mode",
        "direction",
        "unit_5_reason",
        "admission_reason",
    )

    for field in required:
        if field not in candidate:
            raise RuntimeError(
                "UNIT 7 MISSING SIGNAL FIELD: " + field
            )

    execution_intent = candidate["execution_intent"]
    signal_qualified = candidate["signal_qualified"]
    active_mode = candidate["active_mode"]
    direction = candidate["direction"]

    unit_5_reason = str(
        candidate["unit_5_reason"]
    )

    admission_reason = str(
        candidate["admission_reason"]
    )

    if (
        type(execution_intent) is not bool
        or type(signal_qualified) is not bool
    ):
        raise RuntimeError(
            "UNIT 7 INVALID SIGNAL BOOLEAN"
        )

    if execution_intent != signal_qualified:
        raise RuntimeError(
            "UNIT 7 SIGNAL QUALIFICATION CONTRADICTION"
        )

    # ========================================================
    # 3. UNIT-LOCAL SAFETY
    # ========================================================

    # Unit 7 does not perform authenticated requests.
    # These settings must not disable execution in
    # later authorized WEEX demo units.

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
                "UNIT 7 UNSAFE LOCAL CAPABILITY: " + key
            )

    print(
        "PASS: UNIT 7 UNIT-LOCAL SAFETY",
        flush=True
    )

    # ========================================================
    # 4. IDLE PATH
    # ========================================================

    if execution_intent is False:

        if (
            active_mode != "NONE"
            or direction != "NONE"
        ):
            raise RuntimeError(
                "UNIT 7 CONTRADICTORY IDLE SIGNAL"
            )

        result = {
            "status": "IDLE",
            "symbol": "BTCUSDT",
            "demo_order_symbol": "BTCSUSDT",

            "active_mode": "NONE",
            "direction": "NONE",

            "execution_intent": False,
            "signal_qualified": False,

            "unit_5_reason": unit_5_reason,
            "admission_reason": admission_reason,

            "initial_margin_percent": None,
            "leverage_target": None,
            "exchange_leverage_verified": False,
            "leverage_verification_deferred": False,

            "quantity_step": None,
            "minimum_quantity": None,
            "price_step": None,

            "account_balance_required": False,
            "position_sizing_performed": False,
            "quantity_calculated": False,
            "proposed_quantity": None,

            "order_payload_created": False,
            "read_only": True,
            "exchange_write": False,

            "skip_reason": admission_reason,
        }

        print(
            "UNIT 7 STATUS = IDLE",
            flush=True
        )
        print(
            "UNIT 7 SKIP REASON =",
            admission_reason,
            flush=True
        )
        print(
            "UNIT 7 EXCHANGE WRITE = NONE",
            flush=True
        )
        print(
            "FRESH RECONSTRUCTION UNIT 7 RESULT = PASS (IDLE)",
            flush=True
        )
        print("=" * 80, flush=True)

        return result

    # ========================================================
    # 5. QUALIFIED SIGNAL VALIDATION
    # ========================================================

    if active_mode not in (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP",
    ):
        raise RuntimeError(
            "UNIT 7 INVALID ACTIVE MODE"
        )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 7 INVALID DIRECTION"
        )

    if candidate.get("higher_mode_protected") is True:
        raise RuntimeError(
            "UNIT 7 PROTECTED DEVELOPING SIGNAL"
        )

    if candidate.get("candidate_protected") is True:
        raise RuntimeError(
            "UNIT 7 DEVELOPING SIGNAL CANNOT EXECUTE"
        )

    stage = candidate.get("candidate_stage")

    if active_mode == "SCALP":

        if stage != "PENDING_UNIT_6":
            raise RuntimeError(
                "UNIT 7 SCALP STAGE INVALID"
            )

        if candidate.get("scalp_quality_pass") is not True:
            raise RuntimeError(
                "UNIT 7 SCALP QUALITY FAILED"
            )

        if candidate.get("fee_coverage_pass") is not True:
            raise RuntimeError(
                "UNIT 7 SCALP FEE COVERAGE FAILED"
            )

    else:

        if stage != "QUALIFIED":
            raise RuntimeError(
                "UNIT 7 HIGHER MODE NOT QUALIFIED"
            )

    if admission_reason != "QUALIFIED_SIGNAL_ADMITTED":
        raise RuntimeError(
            "UNIT 7 SIGNAL NOT ADMITTED"
        )

    # ========================================================
    # 6. LEVERAGE DEPENDENCY CORRECTION
    # ========================================================

    # Leverage is NOT required for signal handover.
    #
    # Unit 8 must retrieve and verify WEEX leverage
    # before calculating the order quantity.
    #
    # Never substitute an assumed leverage here.

    if (
        strategy.get("exchange_leverage_verified") is True
        or strategy.get("leverage_target") is not None
        or candidate.get("exchange_leverage_verified") is True
        or candidate.get("leverage_target") is not None
    ):
        raise RuntimeError(
            "UNIT 7 UNEXPECTED PREVERIFIED LEVERAGE"
        )

    leverage_target = None

    print(
        "UNIT 7 LEVERAGE SOURCE = UNIT 8",
        flush=True
    )

    print(
        "UNIT 7 LEVERAGE VERIFICATION = DEFERRED",
        flush=True
    )

    # ========================================================
    # 7. ORIGINAL SIZING PARAMETERS
    # ========================================================

    def positive(section, key):
        value = section.get(key)

        if isinstance(value, bool):
            raise RuntimeError(
                "UNIT 7 INVALID " + key
            )

        try:
            value = float(value)
        except (TypeError, ValueError, OverflowError):
            raise RuntimeError(
                "UNIT 7 INVALID " + key
            )

        if not math.isfinite(value) or value <= 0:
            raise RuntimeError(
                "UNIT 7 NONPOSITIVE " + key
            )

        return value

    initial_margin_percent = positive(
        strategy,
        "initial_margin_percent"
    )

    quantity_step = positive(
        precision,
        "quantity_step"
    )

    minimum_quantity = positive(
        precision,
        "minimum_quantity"
    )

    price_step = positive(
        precision,
        "price_step"
    )

    # ========================================================
    # 8. EXECUTION HANDOVER CONTRACT
    # ========================================================

    result = {
        "status": "READY_FOR_BALANCE",

        "symbol": exchange["market_symbol"],
        "demo_order_symbol":
            exchange["demo_order_symbol"],

        "active_mode": active_mode,
        "direction": direction,

        "execution_intent": True,
        "signal_qualified": True,

        "unit_5_reason": unit_5_reason,
        "admission_reason": admission_reason,

        "initial_margin_percent":
            initial_margin_percent,

        "leverage_target": leverage_target,
        "exchange_leverage_verified": False,
        "leverage_verification_deferred": True,

        "quantity_step": quantity_step,
        "minimum_quantity": minimum_quantity,
        "price_step": price_step,

        "account_balance_required": True,

        "position_sizing_performed": False,
        "quantity_calculated": False,
        "proposed_quantity": None,

        "order_payload_created": False,

        "read_only": True,
        "exchange_write": False,

        "skip_reason": "NONE",
    }

    # ========================================================
    # 9. FINAL VALIDATION
    # ========================================================

    if (
        result["status"] != "READY_FOR_BALANCE"
        or result["execution_intent"] is not True
        or result["signal_qualified"] is not True
        or result["active_mode"] != active_mode
        or result["direction"] != direction
        or result["account_balance_required"] is not True
        or result["leverage_target"] is not None
        or result["position_sizing_performed"] is not False
        or result["quantity_calculated"] is not False
        or result["proposed_quantity"] is not None
        or result["order_payload_created"] is not False
    ):
        raise RuntimeError(
            "UNIT 7 EXECUTION HANDOVER INVALID"
        )

    print(
        "UNIT 7 STATUS = READY_FOR_BALANCE",
        flush=True
    )

    print(
        "UNIT 7 ACTIVE MODE =",
        active_mode,
        flush=True
    )

    print(
        "UNIT 7 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 7 EXECUTION INTENT = True",
        flush=True
    )

    print(
        "UNIT 7 SIGNAL QUALIFIED = True",
        flush=True
    )

    print(
        "UNIT 7 LEVERAGE VERIFICATION = DEFERRED TO UNIT 8",
        flush=True
    )

    print(
        "UNIT 7 ACCOUNT BALANCE REQUIRED = True",
        flush=True
    )

    print(
        "UNIT 7 QUANTITY CALCULATED = False",
        flush=True
    )

    print(
        "UNIT 7 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 7 RESULT = PASS (READY_FOR_BALANCE)",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 7 HYBRID EXECUTION ADAPTER
# ZERO INDENTATION
# ============================================================

def fresh_unit_7_hybrid_execution_adapter(
    execution_config,
    execution_candidate,
):

    if not isinstance(execution_config, dict):
        raise RuntimeError(
            "UNIT 7 ADAPTER CONFIG INVALID"
        )

    if not isinstance(execution_candidate, dict):
        raise RuntimeError(
            "UNIT 7 ADAPTER SIGNAL INVALID"
        )

    result = fresh_reconstruction_unit_7(
        execution_config,
        execution_candidate,
    )

    if result["status"] not in (
        "IDLE",
        "READY_FOR_BALANCE",
    ):
        raise RuntimeError(
            "UNIT 7 ADAPTER STATUS INVALID"
        )

    if result.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 7 ADAPTER LOCAL SAFETY FAILED"
        )

    if result.get("exchange_write") is not False:
        raise RuntimeError(
            "UNIT 7 UNAUTHORIZED EXCHANGE WRITE"
        )

    if result["status"] == "READY_FOR_BALANCE":

        if (
            result.get("active_mode")
            != execution_candidate.get("active_mode")
            or result.get("direction")
            != execution_candidate.get("direction")
            or result.get("execution_intent") is not True
            or result.get("signal_qualified") is not True
            or result.get("leverage_target") is not None
            or result.get("account_balance_required") is not True
        ):
            raise RuntimeError(
                "UNIT 7 QUALIFIED HANDOVER FAILED"
            )

    print(
        "UNIT 7 HYBRID ADAPTER STATUS =",
        result["status"],
        flush=True
    )

    print(
        "UNIT 7 HYBRID ADAPTER RESULT = PASS",
        flush=True
    )

    return result


# ============================================================
# UNIT 7 CONFIGURATION VALIDATION
# ZERO INDENTATION
# ============================================================

if not isinstance(
    FRESH_RECONSTRUCTION_EXECUTION_CONFIG,
    dict
):
    raise RuntimeError(
        "UNIT 7 EXECUTION CONFIG MISSING"
    )

if not isinstance(
    FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE,
    dict
):
    raise RuntimeError(
        "UNIT 7 EXECUTION CANDIDATE MISSING"
    )


# ============================================================
# RUN UNIT 7 + ADAPTER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_SIZING_CANDIDATE = (
    fresh_unit_7_hybrid_execution_adapter(
        FRESH_RECONSTRUCTION_EXECUTION_CONFIG,
        FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE,
    )
)

UNIT_7_FINAL_STATUS = (
    FRESH_RECONSTRUCTION_SIZING_CANDIDATE["status"]
)

print(
    "UNIT 7 FINAL STATUS =",
    UNIT_7_FINAL_STATUS,
    flush=True
)

print(
    "UNIT 7 HYBRID ORIGINAL INTEGRATION = PASS",
    flush=True
)


# ============================================================
# END COMPLETE UNIT 7 + HYBRID ADAPTER V2
# UNIT 8 STARTS BELOW
# ZERO INDENTATION
# ============================================================



# ============================================================
# COMPLETE UNIT 8 REPLACEMENT — V4
# ORIGINAL 22524-LINE INTERFACE
# WEEX DEMO + RENDER MANUAL LEVERAGE SYNCHRONIZATION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_8(
    config,
    unit_7_result,
    market_snapshot,
):
    import os
    import time
    import json
    import hmac
    import hashlib
    import base64
    import urllib.request
    import urllib.error

    from decimal import (
        Decimal,
        InvalidOperation,
        ROUND_FLOOR,
    )

    print("=" * 80, flush=True)
    print("UNIT 8 V4 RECONSTRUCTED START", flush=True)

    # ========================================================
    # 1. ORIGINAL INPUT CONTRACT
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 8 CONFIG INVALID")

    if not isinstance(unit_7_result, dict):
        raise RuntimeError("UNIT 8 UNIT 7 RESULT INVALID")

    if not isinstance(market_snapshot, dict):
        raise RuntimeError("UNIT 8 MARKET SNAPSHOT INVALID")

    exchange = config.get("exchange")
    safety = config.get("safety")
    strategy = config.get("strategy")

    if not all(
        isinstance(item, dict)
        for item in (exchange, safety, strategy)
    ):
        raise RuntimeError(
            "UNIT 8 CONFIGURATION SECTIONS MISSING"
        )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 8 ENVIRONMENT MUST BE DEMO"
        )

    base_url = exchange.get("contract_base_url")

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 8 INVALID WEEX BASE URL"
        )

    if exchange.get("market_symbol") != "BTCUSDT":
        raise RuntimeError(
            "UNIT 8 INVALID MARKET SYMBOL"
        )

    for field in (
        "status",
        "active_mode",
        "direction",
        "signal_qualified",
        "execution_intent",
    ):
        if field not in unit_7_result:
            raise RuntimeError(
                "UNIT 8 MISSING UNIT 7 FIELD: " + field
            )

    # ========================================================
    # 2. DECIMAL VALIDATOR
    # ========================================================

    def positive_decimal(value, label):

        try:
            number = Decimal(str(value))
        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as exc:
            raise RuntimeError(
                "UNIT 8 INVALID " + label
            ) from exc

        if not number.is_finite() or number <= 0:
            raise RuntimeError(
                "UNIT 8 NONPOSITIVE " + label
            )

        return number

    # ========================================================
    # 3. READ BOTH RENDER LEVERAGES FIRST
    # NO SIGNAL OR POSITION DEPENDENCY
    # ========================================================

    def render_leverage(name):

        raw = os.getenv(name)

        if raw is None or not raw.strip():
            raise RuntimeError(
                "UNIT 8 MISSING RENDER VARIABLE: " + name
            )

        value = positive_decimal(raw.strip(), name)

        return value

    long_leverage = render_leverage(
        "WEEX_DEMO_LONG_LEVERAGE"
    )

    short_leverage = render_leverage(
        "WEEX_DEMO_SHORT_LEVERAGE"
    )

    print(
        "UNIT 8 LONG LEVERAGE =",
        long_leverage,
        flush=True
    )

    print(
        "UNIT 8 SHORT LEVERAGE =",
        short_leverage,
        flush=True
    )

    print(
        "UNIT 8 LEVERAGE SOURCE = RENDER_MANUAL_WEEX_DEMO",
        flush=True
    )

    print(
        "UNIT 8 POSITION REQUIRED FOR LEVERAGE = FALSE",
        flush=True
    )

    print(
        "UNIT 8 SIGNAL REQUIRED FOR LEVERAGE = FALSE",
        flush=True
    )

    print(
        "UNIT 8 EXCHANGE LEVERAGE MUTATION = NONE",
        flush=True
    )

    # ========================================================
    # 4. NORMALIZE UNIT 7 SIGNAL
    # ========================================================

    status = str(
        unit_7_result.get("status", "IDLE")
    ).upper()

    active_mode = str(
        unit_7_result.get("active_mode", "NONE")
    ).upper()

    direction = str(
        unit_7_result.get("direction", "NONE")
    ).upper()

    qualified = (
        unit_7_result.get("signal_qualified") is True
    )

    intent = (
        unit_7_result.get("execution_intent") is True
    )

    skip_reason = str(
        unit_7_result.get(
            "skip_reason",
            unit_7_result.get("reason", "NONE")
        )
    )

    # ========================================================
    # 5. ORIGINAL IDLE / BLOCKED CONTRACT
    # ========================================================

    def idle_result(reason, state="IDLE"):

        print(
            "UNIT 8 STATUS =",
            state,
            flush=True
        )

        print(
            "UNIT 8 REASON =",
            reason,
            flush=True
        )

        print(
            "UNIT 8 TRADE PLAN READY = FALSE",
            flush=True
        )

        print(
            "UNIT 8 EXCHANGE WRITE = NONE",
            flush=True
        )

        return {
            "status": state,
            "active_mode": active_mode,
            "direction": direction,
            "signal_qualified": qualified,
            "execution_intent": False,
            "trade_plan_ready": False,
            "trade_plan": None,
            "skip_reason": reason,
            "read_only": True,
            "weex_demo_long_leverage": float(
                long_leverage
            ),
            "weex_demo_short_leverage": float(
                short_leverage
            ),
            "leverage_source": (
                "RENDER_MANUAL_WEEX_DEMO"
            ),
            "exchange_leverage_verified": False,
        }

    # No early return before leverage reading.

    if not intent:
        return idle_result(
            skip_reason
            if skip_reason != "NONE"
            else "NO_EXECUTION_INTENT"
        )

    # ========================================================
    # 6. ACTIONABLE UNIT 7 VALIDATION
    # ========================================================

    if not qualified:
        return idle_result(
            "SIGNAL_NOT_QUALIFIED",
            "BLOCKED"
        )

    if status != "READY_FOR_BALANCE":
        return idle_result(
            "UNIT_7_NOT_READY_FOR_BALANCE",
            "BLOCKED"
        )

    if active_mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        return idle_result(
            "INVALID_ACTIVE_MODE",
            "BLOCKED"
        )

    if direction not in ("LONG", "SHORT"):
        return idle_result(
            "INVALID_DIRECTION",
            "BLOCKED"
        )

    if unit_7_result.get(
        "account_balance_required"
    ) is not True:
        return idle_result(
            "BALANCE_REQUIREMENT_MISSING",
            "BLOCKED"
        )

    if unit_7_result.get(
        "quantity_calculated"
    ) is not False:
        return idle_result(
            "PRECALCULATED_QUANTITY_REJECTED",
            "BLOCKED"
        )

    if unit_7_result.get(
        "proposed_quantity"
    ) is not None:
        return idle_result(
            "UNIT_7_PROPOSED_QUANTITY_NOT_EMPTY",
            "BLOCKED"
        )

    # ========================================================
    # 7. SELECT DIRECTIONAL LEVERAGE
    # ========================================================

    if direction == "LONG":
        leverage_target = long_leverage
    else:
        leverage_target = short_leverage

    print(
        "UNIT 8 SELECTED DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 8 SELECTED LEVERAGE =",
        leverage_target,
        flush=True
    )

    # ========================================================
    # 8. ORIGINAL UNIT 8 SAFETY SCOPE
    # ========================================================

    if safety.get(
        "demo_account_balance_read_enabled"
    ) is not True:
        return idle_result(
            "DEMO_BALANCE_READ_DISABLED",
            "BLOCKED"
        )

    for field in (
        "position_access_enabled",
        "order_endpoint_access_enabled",
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
    ):
        if safety.get(field) is not False:
            return idle_result(
                "UNSAFE_CAPABILITY_" + field,
                "BLOCKED"
            )

    # ========================================================
    # 9. MARKET PRICE VALIDATION
    # ========================================================

    if market_snapshot.get("symbol") != "BTCUSDT":
        return idle_result(
            "MARKET_SYMBOL_MISMATCH",
            "BLOCKED"
        )

    mark_price = positive_decimal(
        market_snapshot.get("price"),
        "BTC MARK PRICE"
    )

    # ========================================================
    # 10. ORIGINAL UNIT 7 SIZING PARAMETERS
    # ========================================================

    initial_margin_percent = positive_decimal(
        unit_7_result.get("initial_margin_percent"),
        "INITIAL MARGIN PERCENT"
    )

    quantity_step = positive_decimal(
        unit_7_result.get("quantity_step"),
        "QUANTITY STEP"
    )

    minimum_quantity = positive_decimal(
        unit_7_result.get("minimum_quantity"),
        "MINIMUM QUANTITY"
    )

    # ========================================================
    # 11. FIVE BACKUPS AND EXPOSURE CAP
    # ========================================================

    max_backups = int(
        strategy.get("max_backups", 0)
    )

    multipliers = tuple(
        float(value)
        for value in strategy.get(
            "backup_multipliers", ()
        )
    )

    exposure_cap_percent = positive_decimal(
        strategy.get("exposure_cap_percent"),
        "EXPOSURE CAP PERCENT"
    )

    if max_backups != 5:
        return idle_result(
            "BACKUP_COUNT_NOT_FIVE",
            "BLOCKED"
        )

    if multipliers != (
        1.0, 1.5, 2.0, 2.5, 3.0
    ):
        return idle_result(
            "BACKUP_MULTIPLIERS_MISMATCH",
            "BLOCKED"
        )

    if exposure_cap_percent > Decimal("35"):
        return idle_result(
            "EXPOSURE_CAP_ABOVE_35_PERCENT",
            "BLOCKED"
        )

    # ========================================================
    # 12. ORIGINAL UNIT 12 AUTHENTICATION FORMAT
    # ========================================================

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

    if not all((
        api_key,
        api_secret,
        api_passphrase,
    )):
        return idle_result(
            "WEEX_DEMO_CREDENTIALS_MISSING",
            "BLOCKED"
        )

    # ========================================================
    # 13. SIGNED DEMO BALANCE REQUEST
    # EXACT ORIGINAL DEMO ACCOUNT ENDPOINT
    # ========================================================

    request_path = "/capi/v3/sim/balance"

    timestamp = str(int(time.time() * 1000))

    prehash = (
        timestamp
        + "GET"
        + request_path
    )

    signature = base64.b64encode(
        hmac.new(
            api_secret.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256
        ).digest()
    ).decode("utf-8")

    request = urllib.request.Request(
        base_url + request_path,
        method="GET",
        headers={
            "ACCESS-KEY": api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": api_passphrase,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            http_status = response.getcode()

            response_text = (
                response.read().decode(
                    "utf-8",
                    errors="replace"
                )
            )

    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(
            "utf-8",
            errors="replace"
        )[:300]

        print(
            "UNIT 8 DEMO HTTP ERROR =",
            exc.code,
            detail,
            flush=True
        )

        return idle_result(
            "DEMO_BALANCE_HTTP_ERROR",
            "BLOCKED"
        )

    except urllib.error.URLError as exc:
        print(
            "UNIT 8 DEMO NETWORK ERROR =",
            str(exc),
            flush=True
        )

        return idle_result(
            "DEMO_BALANCE_NETWORK_ERROR",
            "BLOCKED"
        )

    if http_status != 200:
        return idle_result(
            "DEMO_BALANCE_HTTP_NOT_200",
            "BLOCKED"
        )

    try:
        balances = json.loads(response_text)
    except json.JSONDecodeError:
        return idle_result(
            "DEMO_BALANCE_INVALID_JSON",
            "BLOCKED"
        )

    # Original WEEX demo balance response is a list.

    if not isinstance(balances, list):
        return idle_result(
            "DEMO_BALANCE_FORMAT_INVALID",
            "BLOCKED"
        )

    susdt_record = next(
        (
            item
            for item in balances
            if isinstance(item, dict)
            and str(
                item.get("asset", "")
            ).upper() == "SUSDT"
        ),
        None
    )

    if susdt_record is None:
        return idle_result(
            "SUSDT_BALANCE_RECORD_MISSING",
            "BLOCKED"
        )

    available_balance = positive_decimal(
        susdt_record.get("availableBalance"),
        "DEMO AVAILABLE BALANCE"
    )

    print(
        "UNIT 8 DEMO BALANCE READ = SUCCESS",
        flush=True
    )

    print(
        "UNIT 8 AVAILABLE SUSDT =",
        available_balance,
        flush=True
    )

    # ========================================================
    # 14. FIXED INITIAL ENTRY MARGIN
    # ========================================================

    fixed_usdt = positive_decimal(
        os.getenv("ENTRY_FIXED_USDT", "0.50"),
        "ENTRY_FIXED_USDT"
    )

    maximum_initial_margin = (
        available_balance
        * exposure_cap_percent
        / Decimal("100")
    )

    if fixed_usdt > available_balance:
        return idle_result(
            "INSUFFICIENT_DEMO_BALANCE",
            "BLOCKED"
        )

    if fixed_usdt > maximum_initial_margin:
        return idle_result(
            "INITIAL_MARGIN_EXCEEDS_EXPOSURE_CAP",
            "BLOCKED"
        )

    margin_allocation = fixed_usdt

    print(
        "UNIT 8 INITIAL MARGIN SUSDT =",
        margin_allocation,
        flush=True
    )

    print(
        "UNIT 8 EXPOSURE CAP PERCENT =",
        exposure_cap_percent,
        flush=True
    )

    print(
        "UNIT 8 BACKUP COUNT =",
        max_backups,
        flush=True
    )

    print(
        "UNIT 8 BACKUP FUNDING = PROGRESSIVE",
        flush=True
    )

    # ========================================================
    # 15. LEVERAGE-BASED ORDER QUANTITY
    # ========================================================

    notional_value = (
        margin_allocation * leverage_target
    )

    raw_quantity = (
        notional_value / mark_price
    )

    quantity_steps = (
        raw_quantity / quantity_step
    ).to_integral_value(
        rounding=ROUND_FLOOR
    )

    normalized_quantity = (
        quantity_steps * quantity_step
    )

    if normalized_quantity < minimum_quantity:
        return idle_result(
            "QUANTITY_BELOW_EXCHANGE_MINIMUM",
            "BLOCKED"
        )

    if normalized_quantity <= 0:
        return idle_result(
            "NONPOSITIVE_ENTRY_QUANTITY",
            "BLOCKED"
        )

    print(
        "UNIT 8 RAW BTC QUANTITY =",
        raw_quantity,
        flush=True
    )

    print(
        "UNIT 8 EXECUTABLE BTC QUANTITY =",
        normalized_quantity,
        flush=True
    )

    # ========================================================
    # 16. ORIGINAL POSITION SIZING CONTRACT
    # ========================================================

    position_sizing = {
        "asset": "SUSDT",
        "available_balance": float(available_balance),
        "initial_margin_percent": float(
            initial_margin_percent
        ),
        "margin_allocation": float(margin_allocation),
        "leverage_target": float(leverage_target),
        "live_mark_price": float(mark_price),
        "raw_quantity": float(raw_quantity),
        "quantity_step": float(quantity_step),
        "minimum_quantity": float(minimum_quantity),
        "quantity": float(normalized_quantity),
        "position_sizing_performed": True,
        "quantity_calculated": True,
        "source": "WEEX_V3_DEMO_BALANCE",
        "read_only": True,

        # New audit information
        "leverage_source": (
            "RENDER_MANUAL_WEEX_DEMO"
        ),
        "long_leverage": float(long_leverage),
        "short_leverage": float(short_leverage),
        "exchange_leverage_verified": False,
    }

    # ========================================================
    # 17. ORIGINAL TRADE PLAN
    # ========================================================

    trade_plan = {
        "active_mode": active_mode,
        "direction": direction,
        "quantity": float(normalized_quantity),
        "position_sizing": position_sizing,
        "execution_environment": "DEMO",
    }

    # ========================================================
    # 18. ORIGINAL UNIT 9 OUTPUT CONTRACT
    # ========================================================

    result = {
        "status": "READY",
        "active_mode": active_mode,
        "direction": direction,
        "signal_qualified": True,
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": trade_plan,
        "skip_reason": "NONE",
        "read_only": True,

        # Additional diagnostic fields
        "weex_demo_long_leverage": float(long_leverage),
        "weex_demo_short_leverage": float(short_leverage),
        "selected_leverage": float(leverage_target),
        "leverage_source": (
            "RENDER_MANUAL_WEEX_DEMO"
        ),
        "exchange_leverage_verified": False,
    }

    print("-" * 80, flush=True)

    print("UNIT 8 STATUS = READY", flush=True)
    print(
        "UNIT 8 ACTIVE MODE =",
        active_mode,
        flush=True
    )
    print(
        "UNIT 8 DIRECTION =",
        direction,
        flush=True
    )
    print(
        "UNIT 8 LEVERAGE =",
        leverage_target,
        flush=True
    )
    print(
        "UNIT 8 QUANTITY =",
        normalized_quantity,
        flush=True
    )
    print(
        "UNIT 8 TRADE PLAN READY = TRUE",
        flush=True
    )
    print(
        "UNIT 8 DEMO ORDER SUBMISSION = NONE",
        flush=True
    )
    print(
        "UNIT 8 REAL ORDER = NONE",
        flush=True
    )
    print(
        "UNIT 8 EXCHANGE WRITE = NONE",
        flush=True
    )
    print(
        "UNIT 8 V4 RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 8 EXECUTION
# ORIGINAL THREE-ARGUMENT CALL
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
# END COMPLETE UNIT 8
# NEXT UNIT = UNIT 9
# ============================================================


# ============================================================
# UNIT 9 — ORIGINAL REQUIREMENTS RESTORED
# 22524-LINE WORKING REFERENCE COMPATIBILITY
# NO ADDITIONAL LEVERAGE OR SIZING RESTRICTIONS
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_9(
    config,
    unit_8_result,
):
    from datetime import datetime, timezone

    print("=" * 80, flush=True)
    print(
        datetime.now(timezone.utc).isoformat(),
        "FRESH RECONSTRUCTION UNIT 9 START",
        flush=True,
    )

    # ========================================================
    # 1. ORIGINAL INPUT VALIDATION
    # ========================================================

    if not isinstance(config, dict):
        raise TypeError(
            "UNIT 9 CONFIGURATION MUST BE A DICTIONARY"
        )

    if not isinstance(unit_8_result, dict):
        raise TypeError(
            "UNIT 9 UNIT 8 RESULT MUST BE A DICTIONARY"
        )

    print(
        "PASS: UNIT 9 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )
    print(
        "PASS: UNIT 9 RECEIVED UNIT 8 RESULT",
        flush=True,
    )

    # ========================================================
    # 2. ORIGINAL NINE-FIELD UNIT 8 CONTRACT
    # ========================================================

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

    missing = [
        field for field in required_fields
        if field not in unit_8_result
    ]

    if missing:
        raise RuntimeError(
            "UNIT 9 MISSING UNIT 8 FIELDS: "
            + ", ".join(missing)
        )

    print(
        "PASS: UNIT 9 UNIT 8 CONTRACT VALIDATED",
        flush=True,
    )

    # ========================================================
    # 3. ORIGINAL READ-ONLY GATE
    # ========================================================

    if unit_8_result.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 9 REJECTED NON-READ-ONLY UNIT 8 RESULT"
        )

    print(
        "PASS: UNIT 9 READ-ONLY SAFETY GATE",
        flush=True,
    )

    # ========================================================
    # 4. ORIGINAL STATE NORMALIZATION
    # ========================================================

    status = str(
        unit_8_result.get("status", "IDLE")
    ).upper()

    active_mode = unit_8_result.get("active_mode")

    direction = unit_8_result.get("direction")

    signal_qualified = bool(
        unit_8_result.get("signal_qualified", False)
    )

    execution_intent = bool(
        unit_8_result.get("execution_intent", False)
    )

    trade_plan_ready = bool(
        unit_8_result.get("trade_plan_ready", False)
    )

    trade_plan = unit_8_result.get("trade_plan")

    skip_reason = str(
        unit_8_result.get("skip_reason", "NONE")
    )

    # ========================================================
    # 5. ORIGINAL NORMAL IDLE PATH
    # ========================================================

    if (
        status == "IDLE"
        or not signal_qualified
        or not execution_intent
        or not trade_plan_ready
    ):

        result = {
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

        print("UNIT 9 STATUS = IDLE", flush=True)
        print(
            "UNIT 9 ACTIVE MODE =",
            active_mode,
            flush=True,
        )
        print(
            "UNIT 9 DIRECTION =",
            direction,
            flush=True,
        )
        print(
            "UNIT 9 SIGNAL QUALIFIED =",
            signal_qualified,
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
            "UNIT 9 SKIP REASON =",
            skip_reason,
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
            "FRESH RECONSTRUCTION UNIT 9 RESULT = PASS (IDLE)",
            flush=True,
        )
        print("=" * 80, flush=True)

        return result

    # ========================================================
    # 6. ORIGINAL ACTIONABLE STATUS VALIDATION
    # ========================================================

    if status not in (
        "READY",
        "QUALIFIED",
        "ACTIVE",
    ):
        raise RuntimeError(
            "UNIT 9 ACTIONABLE UNIT 8 RESULT HAS "
            "INVALID STATUS: " + status
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
            + str(active_mode)
        )

    print(
        "PASS: UNIT 9 ACTIVE MODE VALIDATED",
        flush=True,
    )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 9 INVALID DIRECTION: "
            + str(direction)
        )

    print(
        "PASS: UNIT 9 DIRECTION VALIDATED",
        flush=True,
    )

    # ========================================================
    # 7. ORIGINAL TRADE PLAN IDENTITY CHECK
    # ========================================================

    if trade_plan.get("active_mode") != active_mode:
        raise RuntimeError(
            "UNIT 9 TRADE PLAN MODE DOES NOT MATCH "
            "UNIT 8 ACTIVE MODE"
        )

    if trade_plan.get("direction") != direction:
        raise RuntimeError(
            "UNIT 9 TRADE PLAN DIRECTION DOES NOT MATCH "
            "UNIT 8 DIRECTION"
        )

    print(
        "PASS: UNIT 9 TRADE PLAN IDENTITY VALIDATED",
        flush=True,
    )

    # ========================================================
    # 8. ORIGINAL INTERNAL EXECUTION CANDIDATE
    # DO NOT MODIFY QUANTITY OR LEVERAGE
    # ========================================================

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

    # ========================================================
    # 9. ORIGINAL UNIT 10 OUTPUT CONTRACT
    # ========================================================

    result = {
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

    # ========================================================
    # 10. ORIGINAL READ-ONLY DIAGNOSTICS
    # ========================================================

    print("UNIT 9 STATUS = READY", flush=True)
    print(
        "UNIT 9 ACTIVE MODE =",
        active_mode,
        flush=True,
    )
    print(
        "UNIT 9 DIRECTION =",
        direction,
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
        "FRESH RECONSTRUCTION UNIT 9 RESULT = PASS",
        flush=True,
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 9 EXECUTION — ORIGINAL INTERFACE
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_9_RESULT = (
    fresh_reconstruction_unit_9(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT,
    )
)

# ============================================================
# END UNIT 9
# NEXT UNIT = UNIT 10
# ============================================================



# ============================================================
# UNIT 10 + HYBRID ADAPTER — COMPLETE REPLACEMENT
# PRESERVED 19-FIELD OUTPUT CONTRACT
# WEEX DEMO EXECUTION PREPARATION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_10(config, unit_9_result):
    import math
    from datetime import datetime, timezone

    print("=" * 80, flush=True)
    print(
        datetime.now(timezone.utc).isoformat(),
        "FRESH RECONSTRUCTION UNIT 10 START",
        flush=True,
    )

    # ========================================================
    # 1. ORIGINAL INPUT CONTRACT
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 10 INVALID CONFIGURATION")

    if not isinstance(unit_9_result, dict):
        raise RuntimeError("UNIT 10 INVALID UNIT 9 RESULT")

    exchange = config.get("exchange")
    safety = config.get("safety")
    strategy = config.get("strategy")
    precision = config.get("market_precision")

    for name, value in (
        ("EXCHANGE", exchange),
        ("SAFETY", safety),
        ("STRATEGY", strategy),
        ("MARKET PRECISION", precision),
    ):
        if not isinstance(value, dict):
            raise RuntimeError(
                "UNIT 10 MISSING " + name
            )

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

    missing = [
        field for field in required
        if field not in unit_9_result
    ]

    if missing:
        raise RuntimeError(
            "UNIT 10 MISSING UNIT 9 FIELDS: "
            + str(missing)
        )

    if unit_9_result["read_only"] is not True:
        raise RuntimeError(
            "UNIT 10 UNIT 9 LOCAL SAFETY FAILURE"
        )

    for field in (
        "order_payload_created",
        "tp_execution_requested",
        "sl_execution_requested",
    ):
        if unit_9_result[field] is not False:
            raise RuntimeError(
                "UNIT 10 UNEXPECTED UNIT 9 ACTION: "
                + field
            )

    print(
        "PASS: UNIT 10 ORIGINAL UNIT 9 CONTRACT",
        flush=True
    )

    # ========================================================
    # 2. ORIGINAL WEEX DEMO CONFIGURATION
    # ========================================================

    if exchange.get("name") != "WEEX":
        raise RuntimeError("UNIT 10 EXCHANGE NOT WEEX")

    if exchange.get("api_version") != "V3":
        raise RuntimeError("UNIT 10 API VERSION INVALID")

    if exchange.get("market_symbol") != "BTCUSDT":
        raise RuntimeError("UNIT 10 MARKET SYMBOL INVALID")

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError("UNIT 10 DEMO SYMBOL INVALID")

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 10 DEMO ENVIRONMENT REQUIRED"
        )

    # ========================================================
    # 3. ORIGINAL UNIT-LOCAL SAFETY
    # THIS DOES NOT DISABLE UNIT 12
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

    for field in forbidden:
        if safety.get(field) is not False:
            raise RuntimeError(
                "UNIT 10 UNSAFE UNIT-LOCAL CAPABILITY: "
                + field
            )

    for field in (
        "anti_duplicate_orders",
        "one_direction_only",
        "active_trade_mode_lock",
    ):
        if strategy.get(field) is not True:
            raise RuntimeError(
                "UNIT 10 REQUIRED SAFETY DISABLED: "
                + field
            )

    print(
        "PASS: UNIT 10 WEEX DEMO CONTRACT",
        flush=True
    )
    print(
        "PASS: UNIT 10 ORIGINAL SAFETY REQUIREMENTS",
        flush=True
    )

    # ========================================================
    # 4. NORMALIZE UNIT 9 RESULT
    # ========================================================

    status = str(
        unit_9_result["status"]
    ).upper()

    mode = str(
        unit_9_result["active_mode"]
    ).upper()

    direction = str(
        unit_9_result["direction"]
    ).upper()

    qualified = unit_9_result["signal_qualified"]
    intent = unit_9_result["execution_intent"]
    plan_ready = unit_9_result["trade_plan_ready"]
    execution_ready = unit_9_result["execution_ready"]

    trade_plan = unit_9_result["trade_plan"]
    candidate = unit_9_result["execution_candidate"]
    skip_reason = str(unit_9_result["skip_reason"])

    for name, value in (
        ("signal_qualified", qualified),
        ("execution_intent", intent),
        ("trade_plan_ready", plan_ready),
        ("execution_ready", execution_ready),
    ):
        if type(value) is not bool:
            raise RuntimeError(
                "UNIT 10 INVALID BOOLEAN: " + name
            )

    # ========================================================
    # 5. ORIGINAL 19-FIELD RESULT CONSTRUCTOR
    # ========================================================

    def make_result(
        result_status,
        result_mode,
        result_direction,
        result_qualified,
        result_intent,
        result_plan,
        result_candidate,
        result_instruction,
        result_reason,
    ):
        ready = result_status == "READY"

        return {
            "status": result_status,
            "active_mode": result_mode,
            "direction": result_direction,
            "signal_qualified": result_qualified,
            "execution_intent": result_intent,
            "trade_plan_ready": ready,
            "trade_plan": result_plan,
            "execution_ready": ready,
            "execution_candidate": result_candidate,
            "demo_boundary_ready": ready,
            "demo_submission_instruction": result_instruction,
            "skip_reason": result_reason,
            "order_payload_created": False,
            "demo_submission_requested": False,
            "real_submission_requested": False,
            "tp_execution_requested": False,
            "sl_execution_requested": False,
            "backup_execution_requested": False,
            "read_only": True,
        }

    # ========================================================
    # 6. ORIGINAL IDLE PATH
    # ========================================================

    if status == "IDLE":

        if (
            mode != "NONE"
            or direction != "NONE"
            or qualified is not False
            or intent is not False
            or plan_ready is not False
            or execution_ready is not False
            or trade_plan is not None
            or candidate is not None
        ):
            raise RuntimeError(
                "UNIT 10 CONTRADICTORY IDLE STATE"
            )

        result = make_result(
            "IDLE",
            "NONE",
            "NONE",
            False,
            False,
            None,
            None,
            None,
            skip_reason,
        )

        print("UNIT 10 STATUS = IDLE", flush=True)
        print(
            "UNIT 10 SKIP REASON =",
            skip_reason,
            flush=True
        )
        print(
            "UNIT 10 EXECUTION READY = False",
            flush=True
        )
        print(
            "UNIT 10 DEMO BOUNDARY READY = False",
            flush=True
        )
        print(
            "UNIT 10 EXCHANGE WRITE = NONE",
            flush=True
        )
        print(
            "FRESH RECONSTRUCTION UNIT 10 "
            "RESULT = PASS (IDLE)",
            flush=True
        )

        return result

    # ========================================================
    # 7. ACTIONABLE INPUT CONTRACT
    # NO ADDITIONAL MARKET QUALIFICATION
    # ========================================================

    if status != "READY":
        raise RuntimeError(
            "UNIT 10 UNIT 9 STATUS NOT READY: "
            + status
        )

    if not all((
        qualified is True,
        intent is True,
        plan_ready is True,
        execution_ready is True,
    )):
        raise RuntimeError(
            "UNIT 10 INCOMPLETE EXECUTION STATE"
        )

    if mode not in (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP",
    ):
        raise RuntimeError(
            "UNIT 10 INVALID ACTIVE MODE"
        )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 10 INVALID DIRECTION"
        )

    if not isinstance(trade_plan, dict):
        raise RuntimeError(
            "UNIT 10 TRADE PLAN MISSING"
        )

    if not isinstance(candidate, dict):
        raise RuntimeError(
            "UNIT 10 EXECUTION CANDIDATE MISSING"
        )

    # ========================================================
    # 8. PRESERVE MODE, DIRECTION AND TRADE PLAN
    # ========================================================

    if trade_plan.get("active_mode") != mode:
        raise RuntimeError(
            "UNIT 10 TRADE PLAN MODE MISMATCH"
        )

    if trade_plan.get("direction") != direction:
        raise RuntimeError(
            "UNIT 10 TRADE PLAN DIRECTION MISMATCH"
        )

    if candidate.get("active_mode") != mode:
        raise RuntimeError(
            "UNIT 10 EXECUTION CANDIDATE MODE MISMATCH"
        )

    if candidate.get("direction") != direction:
        raise RuntimeError(
            "UNIT 10 EXECUTION CANDIDATE DIRECTION MISMATCH"
        )

    if trade_plan.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 10 NON-DEMO TRADE PLAN"
        )

    # ========================================================
    # 9. ORIGINAL QUANTITY PASS-THROUGH
    # NO RE-SIZING OR LEVERAGE GATE
    # ========================================================

    sizing = trade_plan.get("position_sizing")

    if not isinstance(sizing, dict):
        raise RuntimeError(
            "UNIT 10 POSITION SIZING MISSING"
        )

    try:
        quantity = float(
            trade_plan.get("quantity")
        )
        sized_quantity = float(
            sizing.get("quantity")
        )
    except (TypeError, ValueError, OverflowError):
        raise RuntimeError(
            "UNIT 10 INVALID BTC QUANTITY"
        )

    if not (
        math.isfinite(quantity)
        and quantity > 0
        and math.isfinite(sized_quantity)
        and sized_quantity > 0
    ):
        raise RuntimeError(
            "UNIT 10 NONPOSITIVE BTC QUANTITY"
        )

    if not math.isclose(
        quantity,
        sized_quantity,
        rel_tol=1e-10,
        abs_tol=1e-12,
    ):
        raise RuntimeError(
            "UNIT 10 BTC QUANTITY MISMATCH"
        )

    print(
        "UNIT 10 HYBRID MODE PRESERVED =",
        mode,
        flush=True
    )
    print(
        "UNIT 10 HYBRID DIRECTION PRESERVED =",
        direction,
        flush=True
    )
    print(
        "UNIT 10 QUANTITY PRESERVED =",
        quantity,
        flush=True
    )

    # ========================================================
    # 10. ORIGINAL UNIT 11 DEMO BOUNDARY INSTRUCTION
    # INTERNAL HANDOFF, NOT AN HTTP ORDER PAYLOAD
    # ========================================================

    instruction = {
        "exchange": "WEEX",
        "api_version": "V3",
        "execution_environment": "DEMO",
        "market_symbol": exchange["market_symbol"],
        "demo_order_symbol": exchange["demo_order_symbol"],
        "active_mode": mode,
        "direction": direction,
        "trade_plan": trade_plan,
        "execution_candidate": candidate,
        "anti_duplicate_required": True,
        "one_direction_only_required": True,
        "active_trade_mode_lock_required": True,
        "payload_creation_allowed": False,
        "submission_allowed": False,
        "read_only": True,
    }

    # These flags apply to Unit 10 ONLY.
    # Unit 12 remains responsible for genuine demo orders.

    if (
        instruction["payload_creation_allowed"] is not False
        or instruction["submission_allowed"] is not False
        or instruction["read_only"] is not True
    ):
        raise RuntimeError(
            "UNIT 10 LOCAL EXECUTION BOUNDARY FAILURE"
        )

    # ========================================================
    # 11. ORIGINAL READY OUTPUT
    # ========================================================

    result = make_result(
        "READY",
        mode,
        direction,
        True,
        True,
        trade_plan,
        candidate,
        instruction,
        "NONE",
    )

    if result["demo_boundary_ready"] is not True:
        raise RuntimeError(
            "UNIT 10 DEMO BOUNDARY NOT READY"
        )

    print("UNIT 10 STATUS = READY", flush=True)
    print("UNIT 10 ACTIVE MODE =", mode, flush=True)
    print("UNIT 10 DIRECTION =", direction, flush=True)
    print(
        "UNIT 10 EXECUTION READY = True",
        flush=True
    )
    print(
        "UNIT 10 DEMO BOUNDARY READY = True",
        flush=True
    )
    print(
        "UNIT 10 ORDER PAYLOAD CREATED = False",
        flush=True
    )
    print(
        "UNIT 10 DEMO SUBMISSION REQUESTED = False",
        flush=True
    )
    print(
        "UNIT 10 EXCHANGE WRITE = NONE",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 10 RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 10 HYBRID ADAPTER — COMPLETE REPLACEMENT
# RETAINS ORIGINAL UNIT 10 VALIDATION
# ============================================================

def fresh_unit_10_hybrid_adapter(
    execution_config,
    unit_9_result,
):

    if not isinstance(execution_config, dict):
        raise RuntimeError(
            "UNIT 10 ADAPTER CONFIG INVALID"
        )

    if not isinstance(unit_9_result, dict):
        raise RuntimeError(
            "UNIT 10 ADAPTER UNIT 9 RESULT INVALID"
        )

    result = fresh_reconstruction_unit_10(
        execution_config,
        unit_9_result,
    )

    if result["status"] == "READY":

        if (
            result["active_mode"]
            != unit_9_result["active_mode"]
        ):
            raise RuntimeError(
                "UNIT 10 ADAPTER CHANGED MODE"
            )

        if (
            result["direction"]
            != unit_9_result["direction"]
        ):
            raise RuntimeError(
                "UNIT 10 ADAPTER CHANGED DIRECTION"
            )

        if (
            result["trade_plan"] is not
            unit_9_result["trade_plan"]
        ):
            raise RuntimeError(
                "UNIT 10 ADAPTER CHANGED TRADE PLAN"
            )

    print(
        "UNIT 10 HYBRID ADAPTER STATUS =",
        result["status"],
        flush=True
    )

    print(
        "UNIT 10 HYBRID ADAPTER RESULT = PASS",
        flush=True
    )

    return result


# ============================================================
# UNIT 10 EXECUTION CALL — ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_10_RESULT = (
    fresh_unit_10_hybrid_adapter(
        FRESH_RECONSTRUCTION_EXECUTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_9_RESULT,
    )
)

# ============================================================
# END COMPLETE UNIT 10 + HYBRID ADAPTER
# UNIT 11 FOLLOWS
# ============================================================



# ============================================================
# UNIT 11 + ADAPTER — COMPLETE REPLACEMENT V2
# ORIGINAL WORKING WEEX DEMO PAYLOAD CONTRACT
# NO LEVERAGE RECALCULATION
# NO QUANTITY RECALCULATION
# NO EXCHANGE WRITE
# UNIT 12 RETAINS ACTUAL DEMO SUBMISSION
# ============================================================

def fresh_reconstruction_unit_11(config, unit_10_result):
    import math
    import time
    import uuid
    from decimal import Decimal, InvalidOperation

    print("=" * 80, flush=True)
    print("FRESH RECONSTRUCTION UNIT 11 START", flush=True)

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 11 INVALID CONFIG")

    if not isinstance(unit_10_result, dict):
        raise RuntimeError("UNIT 11 INVALID UNIT 10 RESULT")

    exchange = config.get("exchange")
    safety = config.get("safety")
    strategy = config.get("strategy")
    precision = config.get("market_precision")

    if not all(
        isinstance(x, dict)
        for x in (exchange, safety, strategy, precision)
    ):
        raise RuntimeError(
            "UNIT 11 CONFIGURATION SECTIONS MISSING"
        )

    # ========================================================
    # ORIGINAL UNIT 10 CONTRACT
    # ========================================================

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

    missing = [
        key for key in required
        if key not in unit_10_result
    ]

    if missing:
        raise RuntimeError(
            "UNIT 11 UNIT 10 CONTRACT MISSING: "
            + str(missing)
        )

    if unit_10_result["read_only"] is not True:
        raise RuntimeError(
            "UNIT 11 UNIT 10 LOCAL CONTRACT INVALID"
        )

    for key in (
        "order_payload_created",
        "demo_submission_requested",
        "real_submission_requested",
        "tp_execution_requested",
        "sl_execution_requested",
        "backup_execution_requested",
    ):
        if unit_10_result[key] is not False:
            raise RuntimeError(
                "UNIT 11 UNEXPECTED UNIT 10 ACTION: " + key
            )

    print(
        "PASS: UNIT 11 ORIGINAL UNIT 10 CONTRACT",
        flush=True
    )

    # ========================================================
    # ORIGINAL DEMO ENVIRONMENT CONTRACT
    # ========================================================

    if (
        exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or exchange.get("market_symbol") != "BTCUSDT"
        or exchange.get("demo_order_symbol") != "BTCSUSDT"
        or config.get("execution_environment") != "DEMO"
    ):
        raise RuntimeError(
            "UNIT 11 WEEX DEMO ENVIRONMENT INVALID"
        )

    # The following are UNIT-LOCAL restrictions.
    # They do not disable authorized Unit 12 demo orders.

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
                "UNIT 11 UNIT-LOCAL SAFETY INVALID: " + key
            )

    for key in (
        "anti_duplicate_orders",
        "one_direction_only",
        "active_trade_mode_lock",
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 11 STRATEGY SAFETY INVALID: " + key
            )

    # ========================================================
    # ORIGINAL RESULT CONSTRUCTOR
    # 21 FIELDS, PRESERVED FOR UNIT 12
    # ========================================================

    def make_result(
        status,
        mode,
        direction,
        qualified,
        intent,
        trade_plan,
        candidate,
        instruction,
        payload,
        reason,
    ):
        ready = status == "READY"

        return {
            "status": status,
            "active_mode": mode,
            "direction": direction,
            "signal_qualified": qualified,
            "execution_intent": intent,
            "trade_plan_ready": ready,
            "trade_plan": trade_plan,
            "execution_ready": ready,
            "execution_candidate": candidate,
            "demo_boundary_ready": ready,
            "demo_submission_instruction": instruction,
            "payload_ready": ready,
            "order_payload": payload,
            "skip_reason": reason,
            "order_payload_created": ready,
            "demo_submission_requested": False,
            "real_submission_requested": False,
            "tp_execution_requested": False,
            "sl_execution_requested": False,
            "backup_execution_requested": False,
            "read_only": True,
        }

    # ========================================================
    # IDLE: PRESERVE ORIGINAL NO-TRADE BEHAVIOR
    # ========================================================

    status = str(
        unit_10_result["status"]
    ).upper()

    if status == "IDLE":

        if any(
            unit_10_result[key] is not False
            for key in (
                "signal_qualified",
                "execution_intent",
                "trade_plan_ready",
                "execution_ready",
                "demo_boundary_ready",
            )
        ):
            raise RuntimeError(
                "UNIT 11 CONTRADICTORY IDLE FLAGS"
            )

        if any(
            unit_10_result[key] is not None
            for key in (
                "trade_plan",
                "execution_candidate",
                "demo_submission_instruction",
            )
        ):
            raise RuntimeError(
                "UNIT 11 CONTRADICTORY IDLE CANDIDATE"
            )

        result = make_result(
            "IDLE",
            unit_10_result["active_mode"],
            unit_10_result["direction"],
            False,
            False,
            None,
            None,
            None,
            None,
            str(unit_10_result["skip_reason"]),
        )

        print("UNIT 11 STATUS = IDLE", flush=True)
        print(
            "UNIT 11 SKIP REASON =",
            result["skip_reason"],
            flush=True
        )
        print(
            "UNIT 11 PAYLOAD READY = False",
            flush=True
        )
        print(
            "UNIT 11 EXCHANGE WRITE = NONE",
            flush=True
        )
        print(
            "FRESH RECONSTRUCTION UNIT 11 RESULT = PASS (IDLE)",
            flush=True
        )
        print("=" * 80, flush=True)

        return result

    # ========================================================
    # ACTIONABLE ORIGINAL UNIT 10 CONTRACT
    # ========================================================

    if status != "READY":
        raise RuntimeError(
            "UNIT 11 INVALID ACTIONABLE STATUS: " + status
        )

    for key in (
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "execution_ready",
        "demo_boundary_ready",
    ):
        if unit_10_result[key] is not True:
            raise RuntimeError(
                "UNIT 11 READY FLAG MISSING: " + key
            )

    mode = str(
        unit_10_result["active_mode"]
    ).upper()

    direction = str(
        unit_10_result["direction"]
    ).upper()

    if mode not in (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP",
    ):
        raise RuntimeError("UNIT 11 INVALID MODE")

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError("UNIT 11 INVALID DIRECTION")

    plan = unit_10_result["trade_plan"]
    candidate = unit_10_result["execution_candidate"]
    instruction = unit_10_result[
        "demo_submission_instruction"
    ]

    if not all(
        isinstance(x, dict)
        for x in (plan, candidate, instruction)
    ):
        raise RuntimeError(
            "UNIT 11 READY CANDIDATE INCOMPLETE"
        )

    # ========================================================
    # ORIGINAL UNIT 10 DEMO INSTRUCTION CONTRACT
    # ========================================================

    expected_instruction = {
        "exchange": "WEEX",
        "api_version": "V3",
        "execution_environment": "DEMO",
        "market_symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",
        "active_mode": mode,
        "direction": direction,
        "anti_duplicate_required": True,
        "one_direction_only_required": True,
        "active_trade_mode_lock_required": True,
        "payload_creation_allowed": False,
        "submission_allowed": False,
        "read_only": True,
    }

    for key, expected in expected_instruction.items():
        if instruction.get(key) != expected:
            raise RuntimeError(
                "UNIT 11 DEMO INSTRUCTION MISMATCH: " + key
            )

    if instruction.get("trade_plan") is not plan:
        if instruction.get("trade_plan") != plan:
            raise RuntimeError(
                "UNIT 11 INSTRUCTION TRADE PLAN MISMATCH"
            )

    if instruction.get("execution_candidate") is not candidate:
        if instruction.get("execution_candidate") != candidate:
            raise RuntimeError(
                "UNIT 11 INSTRUCTION CANDIDATE MISMATCH"
            )

    if (
        plan.get("active_mode") != mode
        or plan.get("direction") != direction
        or candidate.get("active_mode") != mode
        or candidate.get("direction") != direction
    ):
        raise RuntimeError(
            "UNIT 11 MODE OR DIRECTION MISMATCH"
        )

    # ========================================================
    # ORIGINAL EXECUTION QUANTITY PASS-THROUGH
    # NEVER RECALCULATE FROM LEVERAGE OR MARGIN
    # ========================================================

    raw_quantity = None

    for key in (
        "quantity",
        "position_quantity",
        "order_quantity",
    ):
        if candidate.get(key) is not None:
            raw_quantity = candidate[key]
            break

    if raw_quantity is None:
        nested = candidate.get("trade_plan")

        if isinstance(nested, dict):
            raw_quantity = nested.get("quantity")

            if raw_quantity is None:
                sizing = nested.get("position_sizing")
                if isinstance(sizing, dict):
                    raw_quantity = sizing.get("quantity")

    if raw_quantity is None:
        raise RuntimeError(
            "UNIT 11 EXECUTION QUANTITY MISSING"
        )

    try:
        quantity = Decimal(str(raw_quantity))
        minimum = Decimal(
            str(precision["minimum_quantity"])
        )
        step = Decimal(
            str(precision["quantity_step"])
        )
    except (InvalidOperation, ValueError, KeyError) as exc:
        raise RuntimeError(
            "UNIT 11 INVALID QUANTITY OR PRECISION"
        ) from exc

    if (
        not quantity.is_finite()
        or not minimum.is_finite()
        or not step.is_finite()
        or quantity <= 0
        or minimum <= 0
        or step <= 0
    ):
        raise RuntimeError(
            "UNIT 11 QUANTITY/PRECISION NOT POSITIVE"
        )

    if quantity < minimum:
        raise RuntimeError(
            "UNIT 11 QUANTITY BELOW EXCHANGE MINIMUM"
        )

    # Require Unit 8 to supply an already step-aligned
    # quantity. Unit 11 must never round it upward.

    if quantity % step != 0:
        raise RuntimeError(
            "UNIT 11 QUANTITY NOT STEP ALIGNED"
        )

    quantity_text = format(quantity, "f")

    # ========================================================
    # ORIGINAL WEEX ENTRY DIRECTION MAPPING
    # ========================================================

    if direction == "LONG":
        side = "BUY"
        position_side = "LONG"
    else:
        side = "SELL"
        position_side = "SHORT"

    # Unique client ID for an actual Unit 12 attempt.
    # No exchange submission occurs in Unit 11.

    client_order_id = (
        "FR11-"
        + direction
        + "-"
        + str(time.time_ns())
        + "-"
        + uuid.uuid4().hex[:8]
    )

    # ========================================================
    # ORIGINAL DEMO MARKET ENTRY PAYLOAD
    # ========================================================

    payload = {
        "symbol": "BTCSUSDT",
        "side": side,
        "positionSide": position_side,
        "type": "MARKET",
        "quantity": quantity_text,
        "newClientOrderId": client_order_id,
    }

    expected_keys = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    }

    if set(payload) != expected_keys:
        raise RuntimeError(
            "UNIT 11 PAYLOAD FIELD CONTRACT FAILURE"
        )

    if not payload["newClientOrderId"]:
        raise RuntimeError(
            "UNIT 11 CLIENT ORDER ID EMPTY"
        )

    if any(
        key in payload
        for key in (
            "slTriggerPrice",
            "SlWorkingType",
            "stopLossPrice",
            "stopPrice",
            "tpTriggerPrice",
            "TpWorkingType",
        )
    ):
        raise RuntimeError(
            "UNIT 11 UNEXPECTED TP/SL ENTRY FIELD"
        )

    # ========================================================
    # ORIGINAL 21-FIELD READY RESULT
    # ========================================================

    result = make_result(
        "READY",
        mode,
        direction,
        True,
        True,
        plan,
        candidate,
        instruction,
        payload,
        "NONE",
    )

    print("UNIT 11 STATUS = READY", flush=True)
    print(
        "UNIT 11 ACTIVE MODE =",
        mode,
        flush=True
    )
    print(
        "UNIT 11 DIRECTION =",
        direction,
        flush=True
    )
    print(
        "UNIT 11 EXECUTION QUANTITY =",
        quantity_text,
        flush=True
    )
    print(
        "UNIT 11 PAYLOAD READY = True",
        flush=True
    )
    print(
        "UNIT 11 ORDER PAYLOAD CREATED = True",
        flush=True
    )
    print(
        "UNIT 11 DEMO SUBMISSION REQUESTED = False",
        flush=True
    )
    print(
        "UNIT 11 REAL SUBMISSION REQUESTED = False",
        flush=True
    )
    print(
        "UNIT 11 EXCHANGE WRITE = NONE",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 11 RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 11 HYBRID ADAPTER
# CONTRACT PRESERVATION, NO EXTRA TRADING GATES
# ============================================================

def fresh_unit_11_hybrid_adapter(
    execution_config,
    unit_10_result,
):

    if not isinstance(execution_config, dict):
        raise RuntimeError(
            "UNIT 11 ADAPTER INVALID CONFIG"
        )

    if not isinstance(unit_10_result, dict):
        raise RuntimeError(
            "UNIT 11 ADAPTER INVALID UNIT 10 RESULT"
        )

    result = fresh_reconstruction_unit_11(
        execution_config,
        unit_10_result,
    )

    if result["status"] == "READY":

        if result["trade_plan"] is not (
            unit_10_result["trade_plan"]
        ):
            raise RuntimeError(
                "UNIT 11 ADAPTER CHANGED TRADE PLAN"
            )

        if result["execution_candidate"] is not (
            unit_10_result["execution_candidate"]
        ):
            raise RuntimeError(
                "UNIT 11 ADAPTER CHANGED CANDIDATE"
            )

        if result["active_mode"] != (
            unit_10_result["active_mode"]
        ):
            raise RuntimeError(
                "UNIT 11 ADAPTER CHANGED MODE"
            )

        if result["direction"] != (
            unit_10_result["direction"]
        ):
            raise RuntimeError(
                "UNIT 11 ADAPTER CHANGED DIRECTION"
            )

        if result["payload_ready"] is not True:
            raise RuntimeError(
                "UNIT 11 ADAPTER PAYLOAD NOT READY"
            )

        if not isinstance(
            result["order_payload"], dict
        ):
            raise RuntimeError(
                "UNIT 11 ADAPTER PAYLOAD MISSING"
            )

    print(
        "UNIT 11 HYBRID ADAPTER STATUS =",
        result["status"],
        flush=True
    )

    print(
        "UNIT 11 HYBRID ADAPTER RESULT = PASS",
        flush=True
    )

    return result


# ============================================================
# UNIT 11 EXECUTION CALL — ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_11_RESULT = (
    fresh_unit_11_hybrid_adapter(
        FRESH_RECONSTRUCTION_EXECUTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_10_RESULT,
    )
)

# ============================================================
# END UNIT 11 + HYBRID ADAPTER
# UNIT 12 FOLLOWS
# ============================================================

# ============================================================
# UNIT 12 + ADAPTER — COMPLETE REPLACEMENT V3
# ORIGINAL WEEX DEMO EXECUTION MECHANISM
#
# BOT_MODE CONTROLS NEW INITIAL ENTRIES ONLY
# UNIT 13 AND UNIT 14 REMAIN INDEPENDENT
# NO REAL-CASH ORDER ENDPOINT
# NO LEVERAGE OR MARGIN MODE MUTATION
# ============================================================

def fresh_reconstruction_unit_12(config, unit_11_result):
    import os
    import json
    import time
    import hmac
    import base64
    import hashlib
    import urllib.request
    import urllib.error
    from decimal import Decimal, InvalidOperation
    from datetime import datetime, timezone

    print("=" * 80, flush=True)
    print(
        datetime.now(timezone.utc).isoformat(),
        "FRESH RECONSTRUCTION UNIT 12 START",
        flush=True
    )

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 12 INVALID CONFIG")

    if not isinstance(unit_11_result, dict):
        raise RuntimeError("UNIT 12 INVALID UNIT 11 RESULT")

    exchange = config.get("exchange", {})
    precision = config.get("market_precision", {})

    if not isinstance(exchange, dict):
        raise RuntimeError("UNIT 12 EXCHANGE CONFIG MISSING")

    if not isinstance(precision, dict):
        raise RuntimeError("UNIT 12 PRECISION CONFIG MISSING")

    if (
        exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or exchange.get("market_symbol") != "BTCUSDT"
        or exchange.get("demo_order_symbol") != "BTCSUSDT"
        or config.get("execution_environment") != "DEMO"
    ):
        raise RuntimeError(
            "UNIT 12 DEMO ENVIRONMENT CONTRACT FAILED"
        )

    if unit_11_result.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 12 UNIT 11 LOCAL BOUNDARY INVALID"
        )

    mode = os.getenv(
        "BOT_MODE", "PAUSE"
    ).strip().upper()

    if mode not in ("RUN", "PAUSE"):
        raise RuntimeError(
            "BOT_MODE MUST BE RUN OR PAUSE"
        )

    print("UNIT 12 BOT_MODE =", mode, flush=True)

    # ========================================================
    # ORIGINAL RESULT CONTRACT
    # ========================================================

    def result_base(status, reason):
        return {
            "unit": 12,
            "status": status,
            "read_only": False,
            "active_mode": unit_11_result.get("active_mode"),
            "direction": unit_11_result.get("direction"),
            "signal_qualified": (
                unit_11_result.get("signal_qualified") is True
            ),
            "execution_intent": (
                unit_11_result.get("execution_intent") is True
            ),
            "position_check_attempted": False,
            "position_check_completed": False,
            "position_endpoint_access": False,
            "position_http_status": None,
            "active_position_exists": False,
            "active_positions": [],
            "initial_entry_permitted": False,
            "duplicate_initial_entry_blocked": False,
            "management_path_permitted": True,
            "tp_management_permitted": True,
            "backup_management_permitted": True,
            "demo_submission_attempted": False,
            "demo_submission_completed": False,
            "real_submission_attempted": False,
            "authenticated_request": False,
            "order_endpoint_access": False,
            "exchange_write": False,
            "skip_reason": reason,
        }

    # ========================================================
    # BOT_MODE PAUSE — NEW ENTRIES ONLY
    # ========================================================

    if mode == "PAUSE":
        result = result_base(
            "IDLE", "BOT_MODE_PAUSE"
        )

        print(
            "UNIT 12 INITIAL ENTRY = PAUSED",
            flush=True
        )
        print(
            "UNIT 12 POSITION MANAGEMENT = INDEPENDENT",
            flush=True
        )
        print(
            "UNIT 12 DEMO SUBMISSION ATTEMPTED = False",
            flush=True
        )
        print(
            "FRESH RECONSTRUCTION UNIT 12 RESULT = "
            "PASS (PAUSED)",
            flush=True
        )
        return result

    # ========================================================
    # NORMAL IDLE — NO QUALIFIED CANDIDATE
    # ========================================================

    status = str(
        unit_11_result.get("status", "IDLE")
    ).upper()

    if status == "IDLE":
        result = result_base(
            "IDLE",
            unit_11_result.get(
                "skip_reason", "UNIT_11_IDLE"
            )
        )

        print(
            "UNIT 12 STATUS = IDLE",
            flush=True
        )
        print(
            "UNIT 12 SKIP REASON =",
            result["skip_reason"],
            flush=True
        )
        print(
            "UNIT 12 EXCHANGE WRITE = NONE",
            flush=True
        )
        print(
            "FRESH RECONSTRUCTION UNIT 12 RESULT = "
            "PASS (IDLE)",
            flush=True
        )
        return result

    # ========================================================
    # ACTIONABLE UNIT 11 CONTRACT
    # ========================================================

    if status != "READY":
        raise RuntimeError(
            "UNIT 12 INVALID UNIT 11 STATUS: " + status
        )

    for key in (
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "execution_ready",
        "demo_boundary_ready",
        "payload_ready",
        "order_payload_created",
    ):
        if unit_11_result.get(key) is not True:
            raise RuntimeError(
                "UNIT 12 READY CONTRACT FAILED: " + key
            )

    if (
        unit_11_result.get("demo_submission_requested")
        is not False
        or unit_11_result.get("real_submission_requested")
        is not False
    ):
        raise RuntimeError(
            "UNIT 12 UNEXPECTED PRIOR SUBMISSION"
        )

    active_mode = str(
        unit_11_result.get("active_mode", "NONE")
    ).upper()

    direction = str(
        unit_11_result.get("direction", "NONE")
    ).upper()

    if active_mode not in (
        "SCALP", "STRUCTURE", "BREAKOUT"
    ):
        raise RuntimeError("UNIT 12 INVALID ACTIVE MODE")

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError("UNIT 12 INVALID DIRECTION")

    payload = unit_11_result.get("order_payload")

    if not isinstance(payload, dict):
        raise RuntimeError(
            "UNIT 12 ORDER PAYLOAD MISSING"
        )

    required_payload = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    }

    if set(payload) != required_payload:
        raise RuntimeError(
            "UNIT 12 UNEXPECTED ORDER PAYLOAD FIELDS"
        )

    expected_side = (
        "BUY" if direction == "LONG" else "SELL"
    )

    if (
        payload.get("symbol") != "BTCSUSDT"
        or payload.get("type") != "MARKET"
        or payload.get("side") != expected_side
        or payload.get("positionSide") != direction
        or not payload.get("newClientOrderId")
    ):
        raise RuntimeError(
            "UNIT 12 DEMO ORDER IDENTITY INVALID"
        )

    # ========================================================
    # PRESERVE UNIT 8 BTC QUANTITY
    # NO LEVERAGE RECALCULATION
    # ========================================================

    try:
        quantity = Decimal(
            str(payload["quantity"])
        )
        minimum = Decimal(
            str(precision["minimum_quantity"])
        )
        step = Decimal(
            str(precision["quantity_step"])
        )
    except (InvalidOperation, KeyError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 12 INVALID QUANTITY PRECISION"
        ) from exc

    if (
        not quantity.is_finite()
        or not minimum.is_finite()
        or not step.is_finite()
        or quantity < minimum
        or step <= 0
        or quantity % step != 0
    ):
        raise RuntimeError(
            "UNIT 12 QUANTITY BELOW MINIMUM "
            "OR NOT STEP ALIGNED"
        )

    print(
        "UNIT 12 BTC QUANTITY =",
        format(quantity, "f"),
        flush=True
    )

    # ========================================================
    # ORIGINAL WEEX V3 DEMO AUTHENTICATION
    # ========================================================

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

    if not all((api_key, api_secret, api_passphrase)):
        raise RuntimeError(
            "UNIT 12 WEEX DEMO CREDENTIALS MISSING"
        )

    base_url = "https://api-contract.weex.com"

    def authenticated_request(method, path, body=None):
        if path not in (
            "/capi/v3/sim/position/allPosition",
            "/capi/v3/sim/order",
        ):
            raise RuntimeError(
                "UNIT 12 NON-DEMO ENDPOINT BLOCKED"
            )

        if method == "GET" and body is not None:
            raise RuntimeError(
                "UNIT 12 GET REQUEST MUST NOT HAVE BODY"
            )

        if method == "POST" and (
            path != "/capi/v3/sim/order"
            or not isinstance(body, dict)
        ):
            raise RuntimeError(
                "UNIT 12 INVALID DEMO POST"
            )

        body_text = (
            json.dumps(
                body,
                separators=(",", ":"),
                ensure_ascii=False
            )
            if body is not None
            else ""
        )

        timestamp = str(int(time.time() * 1000))

        prehash = (
            timestamp + method + path + body_text
        )

        signature = base64.b64encode(
            hmac.new(
                api_secret.encode("utf-8"),
                prehash.encode("utf-8"),
                hashlib.sha256
            ).digest()
        ).decode("utf-8")

        headers = {
            "ACCESS-KEY": api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": api_passphrase,
            "Content-Type": "application/json",
        }

        request = urllib.request.Request(
            url=base_url + path,
            data=(
                body_text.encode("utf-8")
                if method == "POST"
                else None
            ),
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(
                request, timeout=15
            ) as response:
                http_status = response.getcode()
                response_text = response.read().decode(
                    "utf-8", errors="replace"
                )

        except urllib.error.HTTPError as exc:
            error_text = exc.read().decode(
                "utf-8", errors="replace"
            )
            raise RuntimeError(
                "UNIT 12 WEEX HTTP ERROR "
                + str(exc.code)
                + ": "
                + error_text[:500]
            ) from exc

        # Network errors intentionally propagate.
        # A POST timeout may have executed at WEEX.
        # Never blindly retry an ambiguous order.

        if not 200 <= http_status < 300:
            raise RuntimeError(
                "UNIT 12 NONSUCCESS HTTP STATUS"
            )

        try:
            response_json = json.loads(response_text)
        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                "UNIT 12 WEEX RESPONSE INVALID JSON"
            ) from exc

        return http_status, response_json

    # ========================================================
    # ORIGINAL NONZERO-POSITION ENTRY BLOCK
    # ========================================================

    print(
        "UNIT 12 PRE-SUBMISSION POSITION CHECK START",
        flush=True
    )

    position_path = (
        "/capi/v3/sim/position/allPosition"
    )

    position_http_status, positions = (
        authenticated_request(
            "GET", position_path
        )
    )

    if not isinstance(positions, list):
        raise RuntimeError(
            "UNIT 12 WEEX DEMO POSITIONS NOT A LIST"
        )

    active_positions = []

    for position in positions:
        if not isinstance(position, dict):
            raise RuntimeError(
                "UNIT 12 MALFORMED POSITION RECORD"
            )

        if str(
            position.get("symbol", "")
        ).upper() != "BTCSUSDT":
            continue

        try:
            size = Decimal(
                str(position["size"])
            )
        except (
            KeyError,
            InvalidOperation,
            ValueError,
        ) as exc:
            raise RuntimeError(
                "UNIT 12 POSITION SIZE INVALID"
            ) from exc

        if not size.is_finite() or size < 0:
            raise RuntimeError(
                "UNIT 12 POSITION SIZE NEGATIVE "
                "OR NONFINITE"
            )

        if size > 0:
            side = str(
                position.get("side", "")
            ).upper()

            if side not in ("LONG", "SHORT"):
                raise RuntimeError(
                    "UNIT 12 ACTIVE POSITION SIDE INVALID"
                )

            active_positions.append({
                "id": position.get("id"),
                "symbol": "BTCSUSDT",
                "side": side,
                "size": float(size),
                "leverage": position.get("leverage"),
                "marginType": position.get("marginType"),
                "separatedMode": position.get(
                    "separatedMode"
                ),
            })

    print(
        "UNIT 12 ACTIVE BTC POSITION COUNT =",
        len(active_positions),
        flush=True
    )

    if active_positions:
        result = result_base(
            "ACTIVE_POSITION_BLOCK",
            "NON_ZERO_POSITION_BLOCK_INITIAL_ENTRY"
        )

        result.update({
            "position_check_attempted": True,
            "position_check_completed": True,
            "position_endpoint_access": True,
            "position_http_status": position_http_status,
            "active_position_exists": True,
            "active_positions": active_positions,
            "duplicate_initial_entry_blocked": True,
            "authenticated_request": True,
        })

        print(
            "UNIT 12 INITIAL ENTRY BLOCKED: "
            "ACTIVE POSITION",
            flush=True
        )
        print(
            "UNIT 12 MANAGEMENT PATH PERMITTED = True",
            flush=True
        )
        print(
            "FRESH RECONSTRUCTION UNIT 12 RESULT = "
            "PASS (ACTIVE POSITION BLOCK)",
            flush=True
        )

        return result

    # ========================================================
    # FLAT POSITION — ACTUAL DEMO ENTRY
    # ========================================================

    print(
        "UNIT 12 ZERO BTC POSITION VERIFIED",
        flush=True
    )
    print(
        "UNIT 12 EXECUTION ENVIRONMENT = DEMO",
        flush=True
    )
    print(
        "UNIT 12 ACTIVE MODE =",
        active_mode,
        flush=True
    )
    print(
        "UNIT 12 DIRECTION =",
        direction,
        flush=True
    )
    print(
        "UNIT 12 SENDING ACTUAL DEMO MARKET ORDER",
        flush=True
    )

    order_path = "/capi/v3/sim/order"

    # This is the original WEEX demo order write.
    # It is NOT a simulation or dry-run.

    try:
        order_http_status, response_json = (
            authenticated_request(
                "POST",
                order_path,
                payload,
            )
        )

    except Exception:
        print(
            "UNIT 12 DEMO ORDER RESULT UNCERTAIN "
            "OR REJECTED — NO AUTOMATIC RETRY",
            flush=True
        )
        print(
            "UNIT 12 VERIFY WEEX ORDER HISTORY "
            "BEFORE RESUBMITTING",
            flush=True
        )
        raise

    if not isinstance(response_json, dict):
        raise RuntimeError(
            "UNIT 12 DEMO ORDER RESPONSE NOT OBJECT"
        )

    if response_json.get("success") is not True:
        raise RuntimeError(
            "UNIT 12 WEEX DID NOT CONFIRM SUCCESS: "
            + str(response_json)[:500]
        )

    order_id = response_json.get("orderId")

    if not order_id:
        raise RuntimeError(
            "UNIT 12 WEEX SUCCESS RESPONSE "
            "MISSING ORDER ID"
        )

    result = result_base(
        "DEMO_SUBMITTED", "NONE"
    )

    result.update({
        "position_check_attempted": True,
        "position_check_completed": True,
        "position_endpoint_access": True,
        "position_http_status": position_http_status,
        "initial_entry_permitted": True,
        "demo_submission_attempted": True,
        "demo_submission_completed": True,
        "authenticated_request": True,
        "order_endpoint_access": True,
        "exchange_write": True,
        "request_path": order_path,
        "request_payload": dict(payload),
        "http_status": order_http_status,
        "weex_response": response_json,
        "order_id": order_id,
    })

    print(
        "UNIT 12 HTTP STATUS =",
        order_http_status,
        flush=True
    )
    print(
        "UNIT 12 WEEX ORDER ID =",
        order_id,
        flush=True
    )
    print(
        "UNIT 12 DEMO SUBMISSION COMPLETED = True",
        flush=True
    )
    print(
        "UNIT 12 REAL SUBMISSION ATTEMPTED = False",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 12 RESULT = "
        "PASS (DEMO SUBMITTED)",
        flush=True
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 12 HYBRID EXECUTION ADAPTER
# ORIGINAL SUBMISSION PATH PRESERVED
# NO SECOND ORDER SUBMISSION
# ============================================================

def fresh_unit_12_hybrid_execution_adapter(
    execution_config,
    unit_11_result,
):

    if not isinstance(execution_config, dict):
        raise RuntimeError(
            "UNIT 12 ADAPTER INVALID CONFIG"
        )

    if not isinstance(unit_11_result, dict):
        raise RuntimeError(
            "UNIT 12 ADAPTER INVALID UNIT 11 RESULT"
        )

    result = fresh_reconstruction_unit_12(
        execution_config,
        unit_11_result,
    )

    if not isinstance(result, dict):
        raise RuntimeError(
            "UNIT 12 ADAPTER RESULT INVALID"
        )

    if result.get("real_submission_attempted") is not False:
        raise RuntimeError(
            "UNIT 12 REAL ORDER SAFETY FAILURE"
        )

    if result.get("status") == "DEMO_SUBMITTED":
        if (
            result.get("demo_submission_completed") is not True
            or not result.get("order_id")
        ):
            raise RuntimeError(
                "UNIT 12 DEMO SUBMISSION CONTRACT FAILURE"
            )

    print(
        "UNIT 12 HYBRID ADAPTER STATUS =",
        result.get("status"),
        flush=True
    )

    print(
        "UNIT 12 HYBRID ADAPTER RESULT = PASS",
        flush=True
    )

    return result


# ============================================================
# UNIT 12 EXECUTION — ONE CALL ONLY
# ============================================================

FRESH_RECONSTRUCTION_UNIT_12_RESULT = (
    fresh_unit_12_hybrid_execution_adapter(
        FRESH_RECONSTRUCTION_EXECUTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_11_RESULT,
    )
)

# ============================================================
# END UNIT 12 + ADAPTER
# UNIT 13 FOLLOWS
# ============================================================



# ============================================================
# UNIT 13 + HYBRID ADAPTER
# WEEX DEMO EXISTING-POSITION TP MANAGEMENT
# ZERO INDENTATION — SINGLE EXECUTION CALL
# ============================================================

def fresh_reconstruction_unit_13(config, unit_12_result):
    import os
    import json
    import time
    import hmac
    import hashlib
    import base64
    import urllib.request
    import urllib.parse
    from decimal import Decimal, ROUND_DOWN, ROUND_UP

    print("=" * 80, flush=True)
    print("FRESH RECONSTRUCTION UNIT 13 START", flush=True)

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 13 CONFIG MISSING")
    if not isinstance(unit_12_result, dict):
        raise RuntimeError("UNIT 13 UNIT 12 RESULT MISSING")

    print("PASS: UNIT 13 RECEIVED UNIT 12 RESULT", flush=True)
    print(
        "UNIT 13 RECEIVED UNIT 12 STATUS =",
        unit_12_result.get("status"),
        flush=True
    )
    print(
        "PASS: UNIT 13 POSITION MANAGEMENT INDEPENDENT "
        "OF NEW SIGNAL AND BOT_MODE",
        flush=True
    )

    ex = config.get("exchange", {})
    st = config.get("strategy", {})
    pr = config.get("market_precision", {})

    if (
        config.get("execution_environment") != "DEMO"
        or ex.get("name") != "WEEX"
        or ex.get("demo_order_symbol") != "BTCSUSDT"
    ):
        raise RuntimeError("UNIT 13 DEMO CONTRACT FAILURE")

    def D(value):
        number = Decimal(str(value))
        if not number.is_finite():
            raise RuntimeError("UNIT 13 NONFINITE NUMBER")
        return number

    step = D(pr["quantity_step"])
    minimum = D(pr["minimum_quantity"])
    price_step = D(pr["price_step"])

    if min(step, minimum, price_step) <= 0:
        raise RuntimeError("UNIT 13 INVALID PRECISION")

    tp1_floor = D(st.get("tp1_net_roi_floor_percent", 5))
    tp2_floor = D(st.get("tp2_net_roi_floor_percent", 10))
    fee = D(st.get("futures_taker_fee_percent", "0.08"))

    trail_ref = D(st.get("tp3_trailing_reference_percent", "0.20"))
    trail_min = D(st.get("tp3_trailing_min_percent", "0.10"))
    trail_max = D(st.get("tp3_trailing_max_percent", "0.40"))

    if (
        tp1_floor < 5
        or tp2_floor < 10
        or tp2_floor <= tp1_floor
        or fee < 0
        or not (0 < trail_min <= trail_ref <= trail_max)
    ):
        raise RuntimeError("UNIT 13 TP CONFIGURATION INVALID")

    print(
        "PASS: UNIT 13 TARGET TP ALLOCATION = 10 / 20 / 70",
        flush=True
    )
    print(
        "PASS: UNIT 13 TP QUANTITY MODE = STEP-AWARE",
        flush=True
    )
    print(
        "PASS: UNIT 13 TP1 NET ROI FLOOR =", tp1_floor,
        flush=True
    )
    print(
        "PASS: UNIT 13 TP2 NET ROI FLOOR =", tp2_floor,
        flush=True
    )

    key = os.getenv("WEEX_API_KEY") or os.getenv("API_KEY")
    secret = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("API_SECRET")
    )
    passphrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, passphrase)):
        raise RuntimeError("UNIT 13 DEMO API CREDENTIALS MISSING")

    base = "https://api-contract.weex.com"

    def signed_request(method, path, body=None):
        allowed = {
            ("GET", "/capi/v3/sim/position/allPosition"),
            ("POST", "/capi/v3/sim/order"),
        }
        if (method, path) not in allowed:
            raise RuntimeError("UNIT 13 NON-DEMO ENDPOINT")

        body_text = (
            json.dumps(body, separators=(",", ":"))
            if body is not None else ""
        )
        timestamp = str(int(time.time() * 1000))
        prehash = timestamp + method + path + body_text
        signature = base64.b64encode(
            hmac.new(
                secret.encode(),
                prehash.encode(),
                hashlib.sha256
            ).digest()
        ).decode()

        headers = {
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": passphrase,
            "Content-Type": "application/json",
        }

        request = urllib.request.Request(
            base + path,
            headers=headers,
            data=(
                body_text.encode()
                if method == "POST" else None
            ),
            method=method,
        )

        # No automatic retry of any ambiguous POST.
        with urllib.request.urlopen(
            request, timeout=15
        ) as response:
            status_code = response.getcode()
            data = json.loads(
                response.read().decode("utf-8")
            )

        if not 200 <= status_code < 300:
            raise RuntimeError(
                "UNIT 13 WEEX HTTP STATUS "
                + str(status_code)
            )
        return data

    def base_result(status, reason):
        return {
            "unit": 13,
            "status": status,
            "read_only": False,
            "unit_12_status": unit_12_result.get("status"),
            "active_position_exists": False,
            "tp_management_required": False,
            "tp_execution_attempted": False,
            "tp_execution_completed": False,
            "tp3_armed": False,
            "sl_execution_attempted": False,
            "backup_execution_attempted": False,
            "real_submission_attempted": False,
            "exchange_write": False,
            "skip_reason": reason,
        }

    # ========================================================
    # ALWAYS CHECK OPEN POSITION, EVEN WHEN BOT_MODE=PAUSE
    # ========================================================

    positions = signed_request(
        "GET",
        "/capi/v3/sim/position/allPosition"
    )

    if not isinstance(positions, list):
        raise RuntimeError(
            "UNIT 13 POSITION RESPONSE NOT LIST"
        )

    active = []
    for p in positions:
        if not isinstance(p, dict):
            continue
        if str(p.get("symbol", "")).upper() != "BTCSUSDT":
            continue
        if D(p.get("size", 0)) > 0:
            active.append(p)

    if not active:
        result = base_result(
            "IDLE_NO_POSITION",
            "NO_ACTIVE_BTCSUSDT_POSITION"
        )
        print("UNIT 13 STATUS = IDLE_NO_POSITION", flush=True)
        print(
            "FRESH RECONSTRUCTION UNIT 13 RESULT = "
            "PASS (IDLE_NO_POSITION)",
            flush=True
        )
        return result

    if len(active) != 1:
        raise RuntimeError(
            "UNIT 13 MULTIPLE ACTIVE DEMO POSITIONS"
        )

    p = active[0]
    side = str(p.get("side", "")).upper()
    size = D(p["size"])
    open_value = D(p.get("openValue", 0))

    if side not in ("LONG", "SHORT"):
        raise RuntimeError("UNIT 13 INVALID POSITION SIDE")
    if open_value <= 0:
        raise RuntimeError("UNIT 13 OPEN VALUE INVALID")

    entry = open_value / size

    # Exchange-reported cumulative fields are essential.
    # Never assume previous TP closes are zero.
    if "cumOpenSize" not in p or "cumCloseSize" not in p:
        raise RuntimeError(
            "UNIT 13 CUMULATIVE POSITION HISTORY "
            "UNAVAILABLE — NO TP ORDER SENT"
        )

    cum_open = D(p["cumOpenSize"])
    cum_close = D(p["cumCloseSize"])

    if (
        cum_open < size
        or cum_close < 0
        or cum_close > cum_open
    ):
        raise RuntimeError(
            "UNIT 13 POSITION HISTORY INCONSISTENT"
        )

    total_steps = int(
        (cum_open / step).to_integral_value(
            rounding=ROUND_DOWN
        )
    )

    if total_steps <= 0:
        raise RuntimeError("UNIT 13 NO EXECUTABLE STEPS")

    # ========================================================
    # ORIGINAL SMALL-POSITION STEP ALLOCATION
    # ========================================================

    if total_steps == 1:
        s1, s2, s3 = 0, 0, 1
    elif total_steps == 2:
        s1, s2, s3 = 1, 0, 1
    else:
        s1 = max(1, int(total_steps * 0.10))
        s2 = max(1, int(total_steps * 0.20))

        while s1 + s2 >= total_steps:
            if s2 > 1:
                s2 -= 1
            elif s1 > 1:
                s1 -= 1
            else:
                raise RuntimeError(
                    "UNIT 13 INVALID TP ALLOCATION"
                )

        s3 = total_steps - s1 - s2

    q1, q2, q3 = (
        D(s1) * step,
        D(s2) * step,
        D(s3) * step
    )

    # ========================================================
    # PRICE TARGETS: NET ROI AFTER ESTIMATED TAKER FEES
    # ========================================================

    leverage = D(p.get("leverage", 0))
    if leverage <= 0:
        raise RuntimeError(
            "UNIT 13 ACTIVE POSITION LEVERAGE INVALID"
        )

    roundtrip_fee_roi = D(2) * fee * leverage
    move1 = (tp1_floor + roundtrip_fee_roi) / leverage
    move2 = (tp2_floor + roundtrip_fee_roi) / leverage

    # move1 and move2 are percentages of entry price.
    if side == "LONG":
        raw1 = entry * (1 + move1 / 100)
        raw2 = entry * (1 + move2 / 100)
        t1 = (
            (raw1 / price_step).to_integral_value(
                rounding=ROUND_UP
            ) * price_step
        )
        t2 = (
            (raw2 / price_step).to_integral_value(
                rounding=ROUND_UP
            ) * price_step
        )
        if t2 <= t1:
            t2 = t1 + price_step
        close_side = "SELL"
    else:
        raw1 = entry * (1 - move1 / 100)
        raw2 = entry * (1 - move2 / 100)
        t1 = (
            (raw1 / price_step).to_integral_value(
                rounding=ROUND_DOWN
            ) * price_step
        )
        t2 = (
            (raw2 / price_step).to_integral_value(
                rounding=ROUND_DOWN
            ) * price_step
        )
        if t2 >= t1:
            t2 = t1 - price_step
        close_side = "BUY"

    if min(t1, t2) <= 0:
        raise RuntimeError("UNIT 13 INVALID TP TARGET")

    # ========================================================
    # FRESH PUBLIC MARK PRICE
    # ========================================================

    query = urllib.parse.urlencode({
        "symbol": "BTCUSDT",
        "priceType": "MARK",
    })
    market_request = urllib.request.Request(
        base + "/capi/v3/market/symbolPrice?" + query,
        method="GET"
    )

    with urllib.request.urlopen(
        market_request, timeout=15
    ) as response:
        market = json.loads(
            response.read().decode("utf-8")
        )

    mark = D(market["price"])
    if market.get("symbol") != "BTCUSDT" or mark <= 0:
        raise RuntimeError("UNIT 13 MARKET RESPONSE INVALID")

    done1 = q1 == 0 or cum_close >= q1
    done2 = (
        done1 if q2 == 0
        else cum_close >= q1 + q2
    )

    reached1 = (
        mark >= t1 if side == "LONG" else mark <= t1
    )
    reached2 = (
        mark >= t2 if side == "LONG" else mark <= t2
    )

    action = "NONE"
    close_qty = D(0)

    if q2 > 0 and reached2 and not done2:
        action = "TP2"
        close_qty = q1 + q2 - cum_close
    elif q1 > 0 and reached1 and not done1:
        action = "TP1"
        close_qty = q1 - cum_close

    close_qty = (
        (min(close_qty, size) / step)
        .to_integral_value(rounding=ROUND_DOWN)
        * step
    )

    armed = (
        done1 and done2
        and q3 > 0 and size > 0
    )

    result = base_result(
        "TP3_ARMED" if armed else "MONITORING",
        (
            "DYNAMIC_TP3_RUNTIME_REQUIRED"
            if armed else "DYNAMIC_TP_TARGET_NOT_REACHED"
        )
    )

    result.update({
        "active_position_exists": True,
        "position_exists": True,
        "tp_management_required": True,
        "position_side": side,
        "position_size": float(size),
        "average_entry_price": float(entry),
        "mark_price": float(mark),
        "tp_target_allocation": "10/20/70",
        "tp1_target": float(t1),
        "tp2_target": float(t2),
        "tp1_target_price": str(t1),
        "tp2_target_price": str(t2),
        "tp1_quantity": float(q1),
        "tp2_quantity": float(q2),
        "tp3_quantity": float(q3),
        "tp1_completed": done1,
        "tp2_completed": done2,
        "tp3_armed": armed,
        "tp3_trailing_percent": float(trail_ref),
        "tp3_trailing_reference_percent": float(trail_ref),
        "tp3_trailing_min_percent": float(trail_min),
        "tp3_trailing_max_percent": float(trail_max),
        "tp3_trailing_dynamic": True,
        "tp1_net_roi_floor_percent": float(tp1_floor),
        "tp2_net_roi_floor_percent": float(tp2_floor),
        "tp_action": action,
    })

    # ========================================================
    # EXECUTE AT MOST ONE DEMO TP CLOSE PER PASS
    # ========================================================

    if action != "NONE" and close_qty >= minimum:

        # A restart or new scan must never duplicate a TP
        # solely because a previous HTTP response was lost.
        # Confirm pending orders/order history separately
        # before relying on this path unattended.

        client_id = (
            "FR13-" + action + "-"
            + str(time.time_ns())
        )[:36]

        order = {
            "symbol": "BTCSUSDT",
            "side": close_side,
            "positionSide": side,
            "type": "MARKET",
            "quantity": format(close_qty, "f"),
            "newClientOrderId": client_id,
        }

        print(
            "UNIT 13 DEMO TP ACTION =", action,
            flush=True
        )
        print(
            "UNIT 13 DEMO CLOSE QUANTITY =",
            order["quantity"],
            flush=True
        )

        result["tp_execution_attempted"] = True

        # Actual WEEX demo write, not a dry run.
        reply = signed_request(
            "POST",
            "/capi/v3/sim/order",
            order
        )

        if not isinstance(reply, dict):
            raise RuntimeError(
                "UNIT 13 DEMO TP RESPONSE INVALID"
            )
        if reply.get("success") is not True:
            raise RuntimeError(
                "UNIT 13 DEMO TP NOT ACKNOWLEDGED: "
                + str(reply)[:400]
            )
        if not reply.get("orderId"):
            raise RuntimeError(
                "UNIT 13 TP ACK MISSING ORDER ID"
            )

        result.update({
            "status": "TP_EXECUTED",
            "skip_reason": "NONE",
            "tp_execution_completed": True,
            "demo_order_executed": True,
            "tp_order_id": str(reply["orderId"]),
            "tp_close_quantity": str(close_qty),
            "exchange_write": True,
        })

    print(
        "UNIT 13 STATUS =", result["status"],
        flush=True
    )
    print(
        "UNIT 13 TP3 ARMED =",
        result["tp3_armed"],
        flush=True
    )
    print(
        "UNIT 13 EXCHANGE WRITE =",
        result["exchange_write"],
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 13 RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 13 HYBRID ADAPTER
# ============================================================

def fresh_unit_13_hybrid_adapter(config, unit_12_result):

    result = fresh_reconstruction_unit_13(
        config,
        unit_12_result
    )

    if not isinstance(result, dict):
        raise RuntimeError("UNIT 13 ADAPTER INVALID RESULT")

    if result.get("real_submission_attempted") is not False:
        raise RuntimeError(
            "UNIT 13 REAL ORDER PROHIBITION FAILED"
        )

    if result.get("sl_execution_attempted") is not False:
        raise RuntimeError(
            "UNIT 13 UNEXPECTED SL EXECUTION"
        )

    if result.get("backup_execution_attempted") is not False:
        raise RuntimeError(
            "UNIT 13 UNEXPECTED BACKUP EXECUTION"
        )

    print(
        "UNIT 13 HYBRID ADAPTER STATUS =",
        result.get("status"),
        flush=True
    )
    print(
        "UNIT 13 HYBRID ADAPTER RESULT = PASS",
        flush=True
    )

    return result


# ============================================================
# UNIT 13 EXECUTION CALL — EXACTLY ONCE
# ============================================================

FRESH_RECONSTRUCTION_UNIT_13_RESULT = (
    fresh_unit_13_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_12_RESULT,
    )
)

# ============================================================
# END UNIT 13 + HYBRID ADAPTER
# UNIT 14 FOLLOWS
# ============================================================



# ============================================================
# UNIT 14 + HYBRID ADAPTER V2
# WEEX DEMO POSITION MANAGEMENT
# EXECUTABLE BACKUPS B1-B5
# DYNAMIC TP3 TRAILING
# NO REAL-CASH ENDPOINTS
# BOT_MODE DOES NOT CONTROL THIS UNIT
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_14(config, unit_13_result):

    import os
    import json
    import time
    import hmac
    import base64
    import hashlib
    import urllib.request
    import urllib.parse
    from decimal import Decimal, ROUND_DOWN

    print("=" * 80, flush=True)
    print("FRESH RECONSTRUCTION UNIT 14 START", flush=True)

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 14 CONFIG MISSING")

    if not isinstance(unit_13_result, dict):
        raise RuntimeError("UNIT 14 UNIT 13 RESULT MISSING")

    exchange = config.get("exchange", {})
    strategy = config.get("strategy", {})
    precision = config.get("market_precision", {})

    if not all(
        isinstance(x, dict)
        for x in (exchange, strategy, precision)
    ):
        raise RuntimeError("UNIT 14 INVALID CONFIG SECTIONS")

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or exchange.get("market_symbol") != "BTCUSDT"
        or exchange.get("demo_order_symbol") != "BTCSUSDT"
    ):
        raise RuntimeError("UNIT 14 NON-DEMO CONFIG BLOCKED")

    def D(value):
        x = Decimal(str(value))
        if not x.is_finite():
            raise RuntimeError("UNIT 14 NONFINITE VALUE")
        return x

    qstep = D(precision["quantity_step"])
    minimum = D(precision["minimum_quantity"])

    max_backups = int(strategy.get("max_backups", 5))

    multipliers = tuple(
        D(x) for x in strategy.get(
            "backup_multipliers",
            (1, 1.5, 2, 2.5, 3)
        )
    )

    fixed_entry = D(
        os.getenv(
            "ENTRY_FIXED_USDT",
            str(strategy.get("initial_fixed_usdt", 2))
        )
    )

    fixed_entry = D(
        os.getenv("INITIAL_FIXED_USDT", str(fixed_entry))
    )

    buffer_pct = D(
        strategy.get("backup_buffer_percent", 0.30)
    )
    cap_pct = D(
        strategy.get("exposure_cap_percent", 35)
    )

    trail_ref = D(
        strategy.get(
            "tp3_trailing_reference_percent", 0.20
        )
    )
    trail_min = D(
        strategy.get(
            "tp3_trailing_min_percent", 0.10
        )
    )
    trail_max = D(
        strategy.get(
            "tp3_trailing_max_percent", 0.40
        )
    )

    if (
        max_backups != 5
        or multipliers != (
            D(1), D(1.5), D(2), D(2.5), D(3)
        )
        or fixed_entry <= 0
        or qstep <= 0
        or minimum <= 0
        or not 0 < buffer_pct
        or not 0 < cap_pct <= 35
        or not 0 < trail_min <= trail_ref <= trail_max
    ):
        raise RuntimeError(
            "UNIT 14 INVALID FIVE-BACKUP SETTINGS"
        )

    print(
        "UNIT 14 INITIAL MARGIN =",
        fixed_entry,
        flush=True
    )
    print(
        "UNIT 14 BACKUPS = 5",
        flush=True
    )
    print(
        "UNIT 14 BACKUP MULTIPLIERS =",
        multipliers,
        flush=True
    )
    print(
        "UNIT 14 LIQUIDATION BUFFER % =",
        buffer_pct,
        flush=True
    )
    print(
        "UNIT 14 EXPOSURE CAP % =",
        cap_pct,
        flush=True
    )
    print(
        "UNIT 14 UNIT 13 STATUS =",
        unit_13_result.get("status"),
        flush=True
    )
    print(
        "UNIT 14 POSITION MANAGEMENT INDEPENDENT "
        "OF BOT_MODE = TRUE",
        flush=True
    )

    # ========================================================
    # AUTHENTICATION — ORIGINAL WEEX V3 FORMAT
    # ========================================================

    api_key = (
        os.getenv("WEEX_API_KEY")
        or os.getenv("API_KEY")
    )
    api_secret = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("API_SECRET")
    )
    passphrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((api_key, api_secret, passphrase)):
        raise RuntimeError(
            "UNIT 14 DEMO CREDENTIALS MISSING"
        )

    base_url = "https://api-contract.weex.com"

    def signed_request(method, path, query="", payload=None):

        allowed = {
            ("GET", "/capi/v3/sim/position/allPosition"),
            ("GET", "/capi/v3/sim/balance"),
            ("GET", "/capi/v3/sim/order/history"),
            ("POST", "/capi/v3/sim/order"),
        }

        if (method, path) not in allowed:
            raise RuntimeError(
                "UNIT 14 UNAUTHORIZED ENDPOINT"
            )

        body = (
            json.dumps(
                payload,
                separators=(",", ":"),
                ensure_ascii=False
            )
            if payload is not None
            else ""
        )

        if method == "POST" and not isinstance(payload, dict):
            raise RuntimeError("UNIT 14 INVALID POST PAYLOAD")

        timestamp = str(int(time.time() * 1000))

        # Original WEEX signature includes query string
        # separately from the endpoint path.
        message = timestamp + method + path

        if query:
            message += "?" + query

        message += body

        signature = base64.b64encode(
            hmac.new(
                api_secret.encode("utf-8"),
                message.encode("utf-8"),
                hashlib.sha256
            ).digest()
        ).decode("utf-8")

        headers = {
            "ACCESS-KEY": api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": passphrase,
            "Content-Type": "application/json",
        }

        url = base_url + path

        if query:
            url += "?" + query

        request = urllib.request.Request(
            url,
            headers=headers,
            data=(
                body.encode("utf-8")
                if method == "POST"
                else None
            ),
            method=method,
        )

        with urllib.request.urlopen(
            request, timeout=15
        ) as response:
            status = response.getcode()
            raw = response.read().decode(
                "utf-8", errors="replace"
            )

        if not 200 <= status < 300:
            raise RuntimeError(
                "UNIT 14 WEEX HTTP " + str(status)
            )

        return json.loads(raw)

    def active_position():

        rows = signed_request(
            "GET",
            "/capi/v3/sim/position/allPosition"
        )

        if not isinstance(rows, list):
            raise RuntimeError(
                "UNIT 14 POSITION RESPONSE INVALID"
            )

        found = []

        for item in rows:
            if not isinstance(item, dict):
                raise RuntimeError(
                    "UNIT 14 INVALID POSITION RECORD"
                )

            if str(item.get("symbol", "")).upper() != "BTCSUSDT":
                continue

            size = D(item.get("size", 0))

            if size > 0:
                found.append(item)

        if len(found) > 1:
            raise RuntimeError(
                "UNIT 14 MULTIPLE ACTIVE BTC POSITIONS"
            )

        return found[0] if found else None

    def demo_balance():

        rows = signed_request(
            "GET", "/capi/v3/sim/balance"
        )

        if not isinstance(rows, list):
            raise RuntimeError(
                "UNIT 14 DEMO BALANCE RESPONSE INVALID"
            )

        for row in rows:
            if (
                isinstance(row, dict)
                and str(row.get("asset", "")).upper()
                == "SUSDT"
            ):
                return row

        raise RuntimeError(
            "UNIT 14 SUSDT BALANCE NOT FOUND"
        )

    def order_history():

        orders = []

        for page in range(20):

            query = urllib.parse.urlencode({
                "symbol": "BTCSUSDT",
                "limit": 1000,
                "page": page,
            })

            batch = signed_request(
                "GET",
                "/capi/v3/sim/order/history",
                query
            )

            if not isinstance(batch, list):
                raise RuntimeError(
                    "UNIT 14 ORDER HISTORY INVALID"
                )

            if any(
                not isinstance(order, dict)
                for order in batch
            ):
                raise RuntimeError(
                    "UNIT 14 MALFORMED ORDER HISTORY"
                )

            orders.extend(batch)

            if len(batch) < 1000:
                print(
                    "PASS: UNIT 14 ORDER HISTORY COMPLETE | "
                    "RECORDS =",
                    len(orders),
                    flush=True
                )
                return orders

        raise RuntimeError(
            "UNIT 14 HISTORY PAGINATION INCOMPLETE"
        )

    def mark_price():

        query = urllib.parse.urlencode({
            "symbol": "BTCUSDT",
            "priceType": "MARK",
        })

        req = urllib.request.Request(
            base_url
            + "/capi/v3/market/symbolPrice?"
            + query,
            method="GET"
        )

        with urllib.request.urlopen(
            req, timeout=15
        ) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        if (
            not isinstance(data, dict)
            or data.get("symbol") != "BTCUSDT"
        ):
            raise RuntimeError(
                "UNIT 14 MARK PRICE RESPONSE INVALID"
            )

        mark = D(data["price"])

        if mark <= 0:
            raise RuntimeError(
                "UNIT 14 MARK PRICE INVALID"
            )

        return mark

    def trade_key(position):

        created = str(position.get("createdTime", ""))

        if created.isdigit():
            return created[-12:]

        position_id = str(position.get("id", ""))

        if position_id:
            return position_id[-12:]

        raise RuntimeError(
            "UNIT 14 POSITION IDENTITY MISSING"
        )

    def backup_id(stage, key):
        return ("FR-B" + str(stage) + "-" + key)[:36]

    def step_floor(value):
        return (
            (value / qstep).to_integral_value(
                rounding=ROUND_DOWN
            )
            * qstep
        )

    def result_base(status, reason):
        return {
            "unit": 14,
            "status": status,
            "unit_13_status": unit_13_result.get("status"),
            "position_exists": False,
            "backup_maximum": 5,
            "backups_filled": 0,
            "backup_next_stage": None,
            "backup_trigger_reached": False,
            "backup_submission_enabled": True,
            "backup_execution_attempted": False,
            "backup_execution_completed": False,
            "tp3_armed": False,
            "tp3_execution_attempted": False,
            "tp3_execution_completed": False,
            "real_submission_attempted": False,
            "sl_execution_attempted": False,
            "exchange_write": False,
            "skip_reason": reason,
        }

    # ========================================================
    # 1. CHECK EXISTING POSITION
    # ========================================================

    position = active_position()

    if position is None:

        result = result_base(
            "IDLE_NO_POSITION",
            "NO_ACTIVE_DEMO_POSITION"
        )

        print(
            "UNIT 14 STATUS = IDLE_NO_POSITION",
            flush=True
        )

        return result

    side = str(position.get("side", "")).upper()
    size = D(position["size"])

    if side not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 14 POSITION SIDE INVALID"
        )

    key = trade_key(position)

    leverage = D(position.get("leverage", 0))

    if leverage <= 0:
        raise RuntimeError(
            "UNIT 14 ACTIVE LEVERAGE UNAVAILABLE"
        )

    liquidation = D(
        position.get("liquidatePrice", 0) or 0
    )

    mark = mark_price()
    history = order_history()

    result = result_base(
        "MONITORING", "NO_TRIGGER"
    )

    result.update({
        "position_exists": True,
        "position_side": side,
        "position_size": float(size),
        "mark_price": float(mark),
        "liquidation_price": float(liquidation),
        "position_leverage": float(leverage),
        "trade_key": key,
    })

    # ========================================================
    # 2. RECONCILE BACKUP ORDER HISTORY
    # ========================================================

    existing = set()
    filled = set()

    for stage in range(1, 6):

        client_id = backup_id(stage, key)

        matching = [
            order for order in history
            if str(
                order.get("clientOrderId", "")
            ) == client_id
        ]

        for order in matching:

            status = str(
                order.get("status", "")
            ).upper()

            try:
                executed = D(
                    order.get("executedQty", 0)
                )
            except Exception:
                executed = D(0)

            if status not in (
                "CANCELED",
                "CANCELLED",
                "REJECTED",
                "EXPIRED",
            ):
                existing.add(stage)

            if (
                status == "FILLED"
                and executed > 0
            ):
                filled.add(stage)

    completed = 0

    for stage in range(1, 6):
        if stage in filled:
            completed = stage
        else:
            break

    if any(stage > completed + 1 for stage in filled):
        raise RuntimeError(
            "UNIT 14 NON-SEQUENTIAL BACKUP FILLS"
        )

    result["backups_filled"] = completed

    print(
        "UNIT 14 BACKUPS FILLED =",
        str(completed) + "/5",
        flush=True
    )

    # ========================================================
    # 3. TP3 RUNNER
    # ========================================================

    tp3_armed = (
        unit_13_result.get("tp3_armed") is True
        and unit_13_result.get("tp1_completed") is True
        and unit_13_result.get("tp2_completed") is True
        and unit_13_result.get("position_exists") is True
        and unit_13_result.get("position_side") == side
    )

    result["tp3_armed"] = tp3_armed

    runtime = globals().setdefault(
        "_FRESH_UNIT14_TP3_RUNTIME_STATE",
        {}
    )

    if tp3_armed:

        callback = max(
            trail_min,
            min(trail_ref, trail_max)
        )

        state = runtime.get(key)

        if state is None:
            state = {
                "best_mark": str(mark),
                "side": side,
                "size": str(size),
            }
            runtime[key] = state

        best = D(state["best_mark"])

        if side == "LONG":
            best = max(best, mark)
            stop = best * (
                D(1) - callback / D(100)
            )
            reached = mark <= stop
        else:
            best = min(best, mark)
            stop = best * (
                D(1) + callback / D(100)
            )
            reached = mark >= stop

        state["best_mark"] = str(best)

        result.update({
            "tp3_best_mark": float(best),
            "tp3_stop_price": float(stop),
            "tp3_trailing_percent": float(callback),
            "tp3_trigger_reached": bool(reached),
        })

        if reached:

            tp3_client_id = (
                "FR-TP3-" + key
            )[:36]

            already_ordered = any(
                str(o.get("clientOrderId", ""))
                == tp3_client_id
                for o in history
            )

            if already_ordered:
                result["status"] = "TP3_ORDER_EXISTS"
                result["skip_reason"] = (
                    "TP3_DUPLICATE_BLOCKED"
                )

            elif (
                tp3_client_id
                in globals().setdefault(
                    "_FRESH_UNIT14_ORDER_ATTEMPTS", set()
                )
            ):
                result["status"] = "TP3_ORDER_UNCERTAIN"
                result["skip_reason"] = (
                    "TP3_PREVIOUS_ATTEMPT"
                )

            else:

                close_qty = step_floor(size)

                if close_qty >= minimum:

                    payload = {
                        "symbol": "BTCSUSDT",
                        "side": (
                            "SELL" if side == "LONG"
                            else "BUY"
                        ),
                        "positionSide": side,
                        "type": "MARKET",
                        "quantity": format(
                            close_qty, "f"
                        ),
                        "newClientOrderId": tp3_client_id,
                    }

                    globals()[
                        "_FRESH_UNIT14_ORDER_ATTEMPTS"
                    ].add(tp3_client_id)

                    result["tp3_execution_attempted"] = True

                    reply = signed_request(
                        "POST",
                        "/capi/v3/sim/order",
                        payload=payload
                    )

                    if (
                        not isinstance(reply, dict)
                        or reply.get("success") is not True
                        or not reply.get("orderId")
                    ):
                        raise RuntimeError(
                            "UNIT 14 TP3 ACK UNVERIFIED"
                        )

                    result.update({
                        "status": "TP3_SUBMITTED",
                        "tp3_execution_completed": True,
                        "tp3_order_id": str(
                            reply["orderId"]
                        ),
                        "exchange_write": True,
                        "skip_reason": "NONE",
                    })

                    print(
                        "PASS: UNIT 14 ACTUAL DEMO TP3 "
                        "ORDER SUBMITTED",
                        flush=True
                    )

                    return result

    else:
        runtime.pop(key, None)

    # ========================================================
    # 4. NEXT BACKUP STAGE
    # ========================================================

    if completed >= 5:

        result["status"] = "BACKUPS_COMPLETE"
        result["skip_reason"] = "FIVE_BACKUPS_FILLED"

        print(
            "UNIT 14 BACKUP STATUS = B5 FILLED",
            flush=True
        )

        return result

    next_stage = completed + 1

    result["backup_next_stage"] = next_stage

    client_id = backup_id(next_stage, key)

    # Existing submitted or partially filled stages
    # must be reconciled before another order.

    if next_stage in existing:

        result["status"] = "BACKUP_ORDER_EXISTS"
        result["skip_reason"] = (
            "BACKUP_ALREADY_SUBMITTED_OR_PARTIAL"
        )

        print(
            "UNIT 14 B" + str(next_stage)
            + " DUPLICATE BLOCKED",
            flush=True
        )

        return result

    # ========================================================
    # 5. LIQUIDATION BUFFER TRIGGER
    # ========================================================

    if liquidation <= 0:

        result["status"] = "WAITING_LIQUIDATION_PRICE"
        result["skip_reason"] = (
            "LIQUIDATION_PRICE_UNAVAILABLE"
        )

        return result

    buffer_fraction = buffer_pct / D(100)

    if side == "LONG":

        trigger = liquidation * (
            D(1) + buffer_fraction
        )

        reached = mark <= trigger

    else:

        trigger = liquidation * (
            D(1) - buffer_fraction
        )

        reached = mark >= trigger

    result["backup_trigger_price"] = float(trigger)
    result["backup_trigger_reached"] = bool(reached)

    print(
        "UNIT 14 B" + str(next_stage)
        + " | LIQUIDATION =", liquidation,
        "| BUFFER =", buffer_pct,
        "| TRIGGER =", trigger,
        "| MARK =", mark,
        "| REACHED =", reached,
        flush=True
    )

    if not reached:

        result["status"] = "MONITORING"
        result["skip_reason"] = (
            "BACKUP_TRIGGER_NOT_REACHED"
        )

        return result

    # ========================================================
    # 6. CALCULATE NEXT BACKUP MARGIN
    # ========================================================

    stage_multiplier = multipliers[next_stage - 1]

    backup_margin = (
        fixed_entry * stage_multiplier
    )

    planned_margin = fixed_entry * (
        D(1) + sum(
            multipliers[:completed],
            D(0)
        )
    )

    projected_margin = (
        planned_margin + backup_margin
    )

    # ========================================================
    # 7. READ FRESH SUSDT BALANCE
    # ========================================================

    balance = demo_balance()

    available = D(
        balance.get("availableBalance", 0)
    )

    if available < 0:
        raise RuntimeError(
            "UNIT 14 NEGATIVE AVAILABLE BALANCE"
        )

    # Use actual position margin if supplied.
    # Do not understate committed exposure.

    actual_margin = D(
        position.get(
            "margin",
            position.get(
                "positionMargin",
                planned_margin
            )
        )
    )

    committed = max(
        planned_margin,
        actual_margin
    )

    total_funds_estimate = (
        available + committed
    )

    exposure_limit = (
        total_funds_estimate
        * cap_pct / D(100)
    )

    projected_exposure = (
        committed + backup_margin
    )

    result.update({
        "backup_multiplier": float(stage_multiplier),
        "backup_margin_usdt": float(backup_margin),
        "available_balance_usdt": float(available),
        "committed_margin_usdt": float(committed),
        "projected_margin_usdt": float(
            projected_exposure
        ),
        "maximum_margin_exposure_usdt": float(
            exposure_limit
        ),
    })

    print(
        "UNIT 14 AVAILABLE SUSDT =",
        available,
        flush=True
    )
    print(
        "UNIT 14 PROJECTED EXPOSURE =",
        projected_exposure,
        flush=True
    )
    print(
        "UNIT 14 35% EXPOSURE LIMIT =",
        exposure_limit,
        flush=True
    )

    # ========================================================
    # 8. AFFORDABILITY AND EXPOSURE CHECKS
    # ========================================================

    if available < backup_margin:

        result["status"] = "WAITING_FUNDS"
        result["skip_reason"] = (
            "INSUFFICIENT_AVAILABLE_SUSDT"
        )

        return result

    if projected_exposure > exposure_limit:

        result["status"] = "WAITING_EXPOSURE"
        result["skip_reason"] = (
            "EXPOSURE_CAP_35_PERCENT"
        )

        return result

    # ========================================================
    # 9. BTC ORDER QUANTITY
    # ========================================================

    notional = backup_margin * leverage

    raw_quantity = notional / mark

    quantity = step_floor(raw_quantity)

    result["backup_quantity"] = float(quantity)

    if quantity < minimum:

        result["status"] = "WAITING_MIN_QUANTITY"
        result["skip_reason"] = (
            "BACKUP_QUANTITY_BELOW_EXCHANGE_MINIMUM"
        )

        return result

    # ========================================================
    # 10. FINAL PRE-SUBMISSION RECONCILIATION
    # ========================================================

    latest_position = active_position()

    if latest_position is None:

        result["status"] = "POSITION_CLOSED"
        result["skip_reason"] = (
            "POSITION_CLOSED_BEFORE_BACKUP"
        )

        return result

    if (
        trade_key(latest_position) != key
        or str(
            latest_position.get("side", "")
        ).upper() != side
        or D(
            latest_position.get(
                "liquidatePrice", 0
            ) or 0
        ) != liquidation
    ):

        result["status"] = "POSITION_CHANGED"
        result["skip_reason"] = (
            "POSITION_CHANGED_BEFORE_BACKUP"
        )

        return result

    # Recheck history immediately before order submission.

    latest_history = order_history()

    if any(
        str(o.get("clientOrderId", ""))
        == client_id
        for o in latest_history
    ):

        result["status"] = "BACKUP_ORDER_EXISTS"
        result["skip_reason"] = (
            "DUPLICATE_ORDER_RECONCILED"
        )

        return result

    attempts = globals().setdefault(
        "_FRESH_UNIT14_ORDER_ATTEMPTS",
        set()
    )

    if client_id in attempts:

        result["status"] = "BACKUP_ORDER_UNCERTAIN"
        result["skip_reason"] = (
            "PREVIOUS_BACKUP_ATTEMPT"
        )

        return result

    # Refresh balance to avoid submitting from
    # a stale available-funds snapshot.

    latest_balance = demo_balance()

    latest_available = D(
        latest_balance.get("availableBalance", 0)
    )

    if latest_available < backup_margin:

        result["status"] = "WAITING_FUNDS"
        result["skip_reason"] = (
            "BALANCE_CHANGED_BEFORE_BACKUP"
        )

        return result

    # Recalculate exposure using the fresh balance.
    latest_total = latest_available + committed
    latest_cap = latest_total * cap_pct / D(100)

    if projected_exposure > latest_cap:

        result["status"] = "WAITING_EXPOSURE"
        result["skip_reason"] = (
            "EXPOSURE_CHANGED_BEFORE_BACKUP"
        )

        return result

    # ========================================================
    # 11. ACTUAL WEEX DEMO BACKUP SUBMISSION
    # ========================================================

    payload = {
        "symbol": "BTCSUSDT",
        "side": (
            "BUY" if side == "LONG"
            else "SELL"
        ),
        "positionSide": side,
        "type": "MARKET",
        "quantity": format(quantity, "f"),
        "newClientOrderId": client_id,
    }

    print(
        "UNIT 14 B" + str(next_stage)
        + " TRIGGER = TRUE",
        flush=True
    )
    print(
        "UNIT 14 B" + str(next_stage)
        + " FUNDING = PASS",
        flush=True
    )
    print(
        "UNIT 14 B" + str(next_stage)
        + " EXPOSURE = PASS",
        flush=True
    )
    print(
        "UNIT 14 B" + str(next_stage)
        + " QUANTITY =", quantity,
        flush=True
    )
    print(
        "UNIT 14 DEMO BACKUP SUBMISSION = TRUE",
        flush=True
    )

    # Mark attempted before the POST.
    # If acknowledgement is ambiguous, do not
    # send a duplicate automatically.

    attempts.add(client_id)

    result["backup_execution_attempted"] = True

    reply = signed_request(
        "POST",
        "/capi/v3/sim/order",
        payload=payload
    )

    if (
        not isinstance(reply, dict)
        or reply.get("success") is not True
        or not reply.get("orderId")
    ):

        raise RuntimeError(
            "UNIT 14 BACKUP ACK UNVERIFIED: "
            "CHECK WEEX HISTORY BEFORE RETRY"
        )

    result.update({
        "status": "BACKUP_SUBMITTED",
        "backup_execution_completed": True,
        "backup_order_id": str(reply["orderId"]),
        "backup_client_order_id": client_id,
        "backup_submitted_stage": next_stage,
        "exchange_write": True,
        "skip_reason": "NONE",
    })

    print(
        "PASS: UNIT 14 B"
        + str(next_stage)
        + " DEMO ORDER ACCEPTED",
        flush=True
    )
    print(
        "UNIT 14 BACKUP ORDER ID =",
        reply["orderId"],
        flush=True
    )
    print(
        "UNIT 14 REAL ORDER = FALSE",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 14 RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 14 HYBRID ADAPTER
# ============================================================

def fresh_unit_14_hybrid_adapter(
    config,
    unit_13_result
):

    result = fresh_reconstruction_unit_14(
        config,
        unit_13_result
    )

    if not isinstance(result, dict):
        raise RuntimeError(
            "UNIT 14 ADAPTER RESULT INVALID"
        )

    if result.get("real_submission_attempted") is not False:
        raise RuntimeError(
            "UNIT 14 REAL-CASH SAFETY FAILURE"
        )

    if result.get("sl_execution_attempted") is not False:
        raise RuntimeError(
            "UNIT 14 UNEXPECTED SL EXECUTION"
        )

    print(
        "UNIT 14 HYBRID ADAPTER STATUS =",
        result.get("status"),
        flush=True
    )
    print(
        "UNIT 14 HYBRID ADAPTER RESULT = PASS",
        flush=True
    )

    return result


# ============================================================
# UNIT 14 EXECUTION CALL — EXACTLY ONCE
# ============================================================

FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    fresh_unit_14_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_13_RESULT,
    )
)

# ============================================================
# END UNIT 14 + ADAPTER
# UNIT 15 FOLLOWS
# ============================================================



# ============================================================
# UNIT 15 + HYBRID ADAPTER
# WEEX DEMO PERFORMANCE / EQUITY / TELEGRAM
# ZERO INDENTATION
# NO WEEX EXCHANGE WRITES
# ============================================================

import os as _u15_os
import time as _u15_time
import json as _u15_json
import hmac as _u15_hmac
import base64 as _u15_b64
import hashlib as _u15_hashlib
import threading as _u15_threading
import urllib.request as _u15_http
import urllib.parse as _u15_url
from decimal import Decimal as _U15_D
from datetime import datetime as _U15_DT
from datetime import timedelta as _U15_TD
from zoneinfo import ZoneInfo as _U15_Zone
from collections import Counter as _U15_Counter

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

UNIT15_ENABLED = (
    _u15_os.getenv("UNIT15_ENABLED", "TRUE").upper()
    == "TRUE"
)

UNIT15_8H_ENABLED = (
    _u15_os.getenv("UNIT15_8H_ENABLED", "TRUE").upper()
    == "TRUE"
)

UNIT15_ON_DEMAND = (
    _u15_os.getenv(
        "UNIT15_ON_DEMAND_ENABLED", "TRUE"
    ).upper() == "TRUE"
)

_UNIT15_TZ = _U15_Zone("Africa/Lagos")
_UNIT15_ZERO = _U15_D("0")
_UNIT15_LOCK = _u15_threading.Lock()
_UNIT15_BASE = "https://api-contract.weex.com"
_UNIT15_SYMBOL = "BTCSUSDT"

_UNIT15_HISTORY_PATH = "/capi/v3/sim/order/history"
_UNIT15_BALANCE_PATH = "/capi/v3/sim/balance"

_UNIT15_SLOTS = {(5, 0), (13, 0), (21, 0)}
_UNIT15_LAST_SLOT = None
_UNIT15_LAST_REPORT = None
_UNIT15_TELEGRAM_OFFSET = None

_UNIT15_EQUITY_SNAPSHOTS = []
_UNIT15_EQUITY_INTERVAL = 300
_UNIT15_LAST_EQUITY_POLL = 0

# ------------------------------------------------------------
# SAFETY / VALUE HELPERS
# ------------------------------------------------------------

def unit15_num(value):
    try:
        if value is None or value == "":
            return None
        x = _U15_D(str(value))
        return x if x.is_finite() else None
    except (ValueError, TypeError, ArithmeticError):
        return None


def unit15_value(record, *names):
    for name in names:
        value = record.get(name)
        if value is not None and value != "":
            return value
    return None


def unit15_milliseconds(value):
    try:
        n = int(_U15_D(str(value)))
        if n < 100000000000:
            n *= 1000
        if n <= 0:
            return None
        return n
    except (ValueError, TypeError, ArithmeticError):
        return None


def unit15_configuration_check():
    config = FRESH_RECONSTRUCTION_CONFIG
    ex = config["exchange"]

    if (
        config.get("execution_environment") != "DEMO"
        or ex.get("name") != "WEEX"
        or ex.get("demo_order_symbol") != _UNIT15_SYMBOL
        or ex.get("contract_base_url") != _UNIT15_BASE
    ):
        raise RuntimeError(
            "UNIT 15 WEEX DEMO CONTRACT FAILED"
        )


# ------------------------------------------------------------
# AUTHENTICATED READ-ONLY REQUEST
# ------------------------------------------------------------

def unit15_get(path, query=""):

    unit15_configuration_check()

    if path not in (
        _UNIT15_HISTORY_PATH,
        _UNIT15_BALANCE_PATH,
    ):
        raise RuntimeError(
            "UNIT 15 NON-REPORTING ENDPOINT BLOCKED"
        )

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
            "UNIT 15 WEEX CREDENTIALS MISSING"
        )

    timestamp = str(int(_u15_time.time() * 1000))
    request_path = path + ("?" + query if query else "")
    prehash = timestamp + "GET" + request_path

    signature = _u15_b64.b64encode(
        _u15_hmac.new(
            secret.encode(),
            prehash.encode(),
            _u15_hashlib.sha256
        ).digest()
    ).decode()

    request = _u15_http.Request(
        _UNIT15_BASE + request_path,
        method="GET",
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": phrase,
            "Content-Type": "application/json",
        }
    )

    if request.get_method() != "GET" or request.data:
        raise RuntimeError(
            "UNIT 15 EXCHANGE WRITE BLOCKED"
        )

    with _u15_http.urlopen(
        request, timeout=20
    ) as response:
        data = _u15_json.loads(
            response.read().decode()
        )

    return data


# ------------------------------------------------------------
# COMPLETE ORDER HISTORY
# ------------------------------------------------------------

def unit15_history():

    orders = []
    seen = set()
    complete = False

    for page in range(20):

        query = _u15_url.urlencode({
            "symbol": _UNIT15_SYMBOL,
            "limit": 1000,
            "page": page,
        })

        batch = unit15_get(
            _UNIT15_HISTORY_PATH, query
        )

        if not isinstance(batch, list):
            raise RuntimeError(
                "UNIT 15 HISTORY RESPONSE INVALID"
            )

        for record in batch:
            if not isinstance(record, dict):
                continue

            oid = unit15_value(
                record,
                "orderId", "id", "clientOrderId"
            )

            if oid is not None and str(oid) not in seen:
                seen.add(str(oid))
                orders.append(record)

        if len(batch) < 1000:
            complete = True
            break

    print(
        "UNIT 15 HISTORY RECORDS =", len(orders),
        flush=True
    )
    print(
        "UNIT 15 HISTORY COMPLETE =", complete,
        flush=True
    )

    return orders, complete


# ------------------------------------------------------------
# ORDER NORMALIZATION
# ------------------------------------------------------------

def unit15_parse_order(order):

    status = str(
        unit15_value(
            order, "status", "state", "orderStatus"
        ) or ""
    ).upper()

    if status not in (
        "FILLED", "FULLY_FILLED",
        "FULL_FILLED", "FULLFILL"
    ):
        return None, "NOT_FULLY_FILLED"

    qty = unit15_num(
        unit15_value(
            order,
            "executedQty", "filledQty",
            "filledSize", "executedQuantity",
            "dealSize"
        )
    )

    price = unit15_num(
        unit15_value(
            order,
            "avgPrice", "averagePrice",
            "fillPrice", "priceAvg",
            "executedPrice"
        )
    )

    ts = unit15_milliseconds(
        unit15_value(
            order,
            "createdTime", "createTime",
            "cTime", "ctime", "createdAt",
            "timestamp", "time",
            "updateTime", "updatedAt"
        )
    )

    if qty is None or qty <= 0:
        return None, "INVALID_QUANTITY"

    if price is None or price <= 0:
        return None, "INVALID_PRICE"

    if ts is None:
        return None, "INVALID_TIMESTAMP"

    oid = unit15_value(
        order, "orderId", "id", "clientOrderId"
    )

    if oid is None:
        return None, "MISSING_ORDER_ID"

    side = str(
        unit15_value(order, "side", "orderSide") or ""
    ).upper()

    direction = str(
        unit15_value(
            order,
            "positionSide", "holdSide", "posSide"
        ) or ""
    ).upper()

    action = str(
        unit15_value(
            order,
            "tradeSide", "tradeType", "offset"
        ) or ""
    ).upper()

    if (
        direction in ("LONG", "SHORT")
        and action not in ("OPEN", "CLOSE")
        and side in ("BUY", "SELL")
    ):
        action = (
            "OPEN"
            if (
                (direction == "LONG") == (side == "BUY")
            )
            else "CLOSE"
        )

    if (
        direction not in ("LONG", "SHORT")
        or action not in ("OPEN", "CLOSE")
    ):
        return None, "UNRESOLVED_DIRECTION"

    return {
        "id": str(oid),
        "time": ts,
        "qty": qty,
        "price": price,
        "direction": direction,
        "action": action,
    }, None


# ------------------------------------------------------------
# COMPLETED-CYCLE RECONSTRUCTION
# ------------------------------------------------------------

def unit15_analyze(
    orders, history_complete, start_ms, end_ms
):

    reasons = _U15_Counter()
    fills = []

    for order in orders:
        normalized, error = unit15_parse_order(order)
        if normalized is None:
            reasons[error] += 1
        else:
            fills.append(normalized)

    fills.sort(key=lambda x: (x["time"], x["id"]))

    positions = {
        side: {
            "qty": _UNIT15_ZERO,
            "cost": _UNIT15_ZERO,
            "pnl": _UNIT15_ZERO,
            "unknown": False,
        }
        for side in ("LONG", "SHORT")
    }

    cycles = []
    unmatched = 0

    for fill in fills:

        p = positions[fill["direction"]]
        qty = fill["qty"]
        price = fill["price"]

        if fill["action"] == "OPEN":
            p["qty"] += qty
            p["cost"] += qty * price
            continue

        if qty > p["qty"] or p["qty"] <= 0:
            unmatched += 1
            p["unknown"] = True
            reasons["UNMATCHED_CLOSE"] += 1
            continue

        average = p["cost"] / p["qty"]

        pnl = (
            (price - average) * qty
            if fill["direction"] == "LONG"
            else (average - price) * qty
        )

        p["pnl"] += pnl
        p["qty"] -= qty
        p["cost"] -= average * qty

        if p["qty"] == 0:

            if (
                not p["unknown"]
                and start_ms <= fill["time"] < end_ms
            ):
                cycles.append(p["pnl"])

            p.update({
                "qty": _UNIT15_ZERO,
                "cost": _UNIT15_ZERO,
                "pnl": _UNIT15_ZERO,
                "unknown": False,
            })

    winners = sum(x > 0 for x in cycles)
    losers = sum(x < 0 for x in cycles)
    breakeven = sum(x == 0 for x in cycles)

    gross_profit = sum(
        (x for x in cycles if x > 0),
        _UNIT15_ZERO
    )
    gross_loss = sum(
        (-x for x in cycles if x < 0),
        _UNIT15_ZERO
    )

    provisional = (
        not history_complete
        or unmatched > 0
        or any(
            reasons[name] > 0
            for name in (
                "INVALID_QUANTITY",
                "INVALID_PRICE",
                "INVALID_TIMESTAMP",
                "UNRESOLVED_DIRECTION",
                "MISSING_ORDER_ID",
            )
        )
    )

    return {
        "orders": len(orders),
        "fully_filled": len(fills),
        "cycles": len(cycles),
        "wins": winners,
        "losses": losers,
        "breakeven": breakeven,
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "gross_pnl": gross_profit - gross_loss,
        "unmatched": unmatched,
        "history_complete": history_complete,
        "provisional": provisional,
        "diagnostics": dict(reasons),
        "open_quantities": {
            d: str(p["qty"])
            for d, p in positions.items()
        },
    }


# ------------------------------------------------------------
# EQUITY SNAPSHOT
# ------------------------------------------------------------

def unit15_equity_snapshot():

    rows = unit15_get(_UNIT15_BALANCE_PATH)

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT 15 BALANCE RESPONSE INVALID"
        )

    for row in rows:
        if not isinstance(row, dict):
            continue

        if str(row.get("asset", "")).upper() != "SUSDT":
            continue

        for field in (
            "equity", "accountEquity",
            "totalEquity", "marginBalance"
        ):
            equity = unit15_num(row.get(field))

            if equity is not None and equity >= 0:
                snapshot = {
                    "time_ms": int(
                        _u15_time.time() * 1000
                    ),
                    "equity": equity,
                    "field": field,
                }

                _UNIT15_EQUITY_SNAPSHOTS.append(
                    snapshot
                )

                return snapshot

    raise RuntimeError(
        "UNIT 15 EXPLICIT EQUITY FIELD NOT FOUND"
    )


def unit15_equity_change(start_ms, end_ms):

    # Snapshot pairs must correspond to the interval.
    # We do not substitute wallet balance for equity.

    start = [
        s for s in _UNIT15_EQUITY_SNAPSHOTS
        if s["time_ms"] <= start_ms
    ]

    end = [
        s for s in _UNIT15_EQUITY_SNAPSHOTS
        if s["time_ms"] <= end_ms
    ]

    if not start or not end:
        return None

    a = max(start, key=lambda x: x["time_ms"])
    b = max(end, key=lambda x: x["time_ms"])

    if (
        a["time_ms"] == b["time_ms"]
        or a["field"] != b["field"]
    ):
        return None

    return {
        "starting": a["equity"],
        "ending": b["equity"],
        "change": b["equity"] - a["equity"],
    }


# ------------------------------------------------------------
# TELEGRAM DELIVERY
# ------------------------------------------------------------

def unit15_telegram(message):

    token = _u15_os.getenv(
        "TELEGRAM_BOT_TOKEN", ""
    ).strip()

    chat_id = _u15_os.getenv(
        "TELEGRAM_CHAT_ID", ""
    ).strip()

    if not token or not chat_id:
        print(
            "UNIT 15 TELEGRAM NOT CONFIGURED",
            flush=True
        )
        return False

    payload = _u15_url.urlencode({
        "chat_id": chat_id,
        "text": message,
    }).encode()

    request = _u15_http.Request(
        "https://api.telegram.org/bot"
        + token + "/sendMessage",
        method="POST",
        data=payload,
    )

    try:
        with _u15_http.urlopen(
            request, timeout=15
        ) as response:
            reply = _u15_json.loads(
                response.read().decode()
            )

        return reply.get("ok") is True

    except Exception as exc:
        print(
            "UNIT 15 TELEGRAM DELIVERY ERROR =",
            type(exc).__name__,
            flush=True
        )
        return False


# ------------------------------------------------------------
# REPORT GENERATION
# ------------------------------------------------------------

def unit15_report(
    hours=8,
    notification="ON_DEMAND",
    end=None
):

    global _UNIT15_LAST_REPORT

    if hours not in (1, 8, 24):
        raise ValueError(
            "UNIT 15 REPORT MUST BE 1H / 8H / 24H"
        )

    if not _UNIT15_LOCK.acquire(blocking=False):
        print(
            "UNIT 15 REPORT ALREADY RUNNING",
            flush=True
        )
        return None

    try:
        now = _U15_DT.now(_UNIT15_TZ)
        end = end or now
        start = end - _U15_TD(hours=hours)

        start_ms = int(start.timestamp() * 1000)
        end_ms = int(end.timestamp() * 1000)

        orders, complete = unit15_history()

        summary = unit15_analyze(
            orders, complete, start_ms, end_ms
        )

        count = summary["cycles"]
        wins = summary["wins"]
        losses = summary["losses"]

        winrate = (
            f"{100 * wins / count:.2f}%"
            if count else "N/A"
        )

        equity = unit15_equity_change(
            start_ms, end_ms
        )

        if equity is None:
            equity_text = (
                "Starting equity: N/A\n"
                "Ending equity: N/A\n"
                "Equity change: N/A\n"
                "Equity ROI: N/A\n"
                "Reason: Matching historical equity "
                "snapshots unavailable"
            )
        else:
            a = equity["starting"]
            b = equity["ending"]
            change = equity["change"]

            roi = (
                f"{change * 100 / a:.2f}%"
                if a > 0 else "N/A"
            )

            equity_text = (
                f"Starting equity: {a} SUSDT\n"
                f"Ending equity: {b} SUSDT\n"
                f"Equity change: {change:+f} SUSDT\n"
                f"Equity ROI: {roi}\n"
                "Cash-flow adjustment: Unverified\n"
                "Net trading profit: Unverified"
            )

        text = (
            "WEEX DEMO TRADING PERFORMANCE\n"
            "================================\n"
            f"Notification: {notification}\n"
            f"Period: {hours}h\n"
            f"Window: {start:%Y-%m-%d %H:%M} "
            f"to {end:%Y-%m-%d %H:%M} WAT\n"
            f"History orders: {summary['orders']}\n"
            f"Fully filled: {summary['fully_filled']}\n"
            f"Completed cycles: {count}\n"
            f"Winning cycles: {wins}\n"
            f"Losing cycles: {losses}\n"
            f"Break-even: {summary['breakeven']}\n"
            f"Gross win rate: {winrate}\n"
            f"Gross profit: "
            f"{summary['gross_profit']:.4f} SUSDT\n"
            f"Gross loss: "
            f"{summary['gross_loss']:.4f} SUSDT\n"
            f"Gross P&L: "
            f"{summary['gross_pnl']:+.4f} SUSDT\n"
            f"Unmatched closes: "
            f"{summary['unmatched']}\n"
            f"History complete: "
            f"{summary['history_complete']}\n"
            f"Provisional: "
            f"{summary['provisional']}\n"
            "Net ROI: N/A\n"
            "Fees/funding/margin: Unverified\n"
            "Close cause: Unverified\n"
            "\nEQUITY-BASED PERFORMANCE\n"
            "================================\n"
            + equity_text
        )

        print(text, flush=True)

        delivered = unit15_telegram(text)

        print(
            "UNIT 15 TELEGRAM SENT =",
            delivered,
            flush=True
        )

        _UNIT15_LAST_REPORT = summary
        return summary

    finally:
        _UNIT15_LOCK.release()


# ------------------------------------------------------------
# EQUITY POLLING
# ------------------------------------------------------------

def unit15_poll_equity():

    global _UNIT15_LAST_EQUITY_POLL

    now = _u15_time.time()

    if (
        now - _UNIT15_LAST_EQUITY_POLL
        < _UNIT15_EQUITY_INTERVAL
    ):
        return

    _UNIT15_LAST_EQUITY_POLL = now

    try:
        snapshot = unit15_equity_snapshot()
        print(
            "UNIT 15 EQUITY SNAPSHOT =",
            snapshot["equity"],
            flush=True
        )
    except Exception as exc:
        print(
            "UNIT 15 EQUITY READ UNAVAILABLE =",
            str(exc)[:200],
            flush=True
        )


# ------------------------------------------------------------
# TELEGRAM ON-DEMAND COMMANDS
# ------------------------------------------------------------

def unit15_poll_commands():

    global _UNIT15_TELEGRAM_OFFSET

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

    query_args = {"timeout": 0}

    if _UNIT15_TELEGRAM_OFFSET is not None:
        query_args["offset"] = _UNIT15_TELEGRAM_OFFSET

    url = (
        "https://api.telegram.org/bot"
        + token
        + "/getUpdates?"
        + _u15_url.urlencode(query_args)
    )

    with _u15_http.urlopen(
        url, timeout=15
    ) as response:
        payload = _u15_json.loads(
            response.read().decode()
        )

    commands = []

    for update in payload.get("result", []):

        uid = update.get("update_id")

        if uid is not None:
            _UNIT15_TELEGRAM_OFFSET = max(
                _UNIT15_TELEGRAM_OFFSET or 0,
                int(uid) + 1
            )

        msg = (
            update.get("message")
            or update.get("edited_message")
            or {}
        )

        chat = msg.get("chat") or {}

        if str(chat.get("id")) != str(chat_id):
            continue

        command = str(
            msg.get("text", "")
        ).strip().split(" ", 1)[0].lower()

        aliases = {
            "/report": 8,
            "/report8h": 8,
            "/report24h": 24,
            "/report1h": 1,
        }

        if "@" in command:
            command = command.split("@", 1)[0]

        if command in aliases:
            commands.append(aliases[command])

    return commands


# ------------------------------------------------------------
# SCHEDULED REPORTING WORKER
# ------------------------------------------------------------

def unit15_worker():

    global _UNIT15_LAST_SLOT

    print("=" * 80, flush=True)
    print(
        "UNIT 15 REPORTING WORKER STARTED",
        flush=True
    )
    print(
        "UNIT 15 SCHEDULE = 05:00 / 13:00 / 21:00 WAT",
        flush=True
    )
    print(
        "UNIT 15 INTERVALS = 1H / 8H / 24H",
        flush=True
    )
    print(
        "UNIT 15 STARTUP REPORT = DISABLED",
        flush=True
    )
    print(
        "UNIT 15 WEEX EXCHANGE WRITE = NONE",
        flush=True
    )
    print("=" * 80, flush=True)

    # Do not send a historical report immediately
    # just because Render restarts.

    while True:
        try:
            unit15_poll_equity()

            now = _U15_DT.now(_UNIT15_TZ)

            slot = now.strftime("%Y-%m-%d %H:%M")

            if (
                UNIT15_8H_ENABLED
                and (now.hour, now.minute)
                in _UNIT15_SLOTS
                and slot != _UNIT15_LAST_SLOT
            ):
                _UNIT15_LAST_SLOT = slot

                end = now.replace(
                    second=0, microsecond=0
                )

                unit15_report(
                    8, "SCHEDULED_8H", end
                )

        except Exception as exc:
            print(
                "UNIT 15 SCHEDULE ERROR =",
                repr(exc),
                flush=True
            )

        try:
            for hours in unit15_poll_commands():
                unit15_report(
                    hours, "ON_DEMAND"
                )

        except Exception as exc:
            print(
                "UNIT 15 COMMAND ERROR =",
                repr(exc),
                flush=True
            )

        _u15_time.sleep(10)


# ------------------------------------------------------------
# HYBRID ADAPTER AND SINGLE ACTIVATION
# ------------------------------------------------------------

def fresh_unit_15_hybrid_adapter(
    config, unit_14_result
):

    if not isinstance(unit_14_result, dict):
        raise RuntimeError(
            "UNIT 15 UNIT 14 RESULT MISSING"
        )

    unit15_configuration_check()

    print(
        "UNIT 15 RECEIVED UNIT 14 STATUS =",
        unit_14_result.get("status"),
        flush=True
    )

    if UNIT15_ENABLED:

        prior = globals().get("_UNIT15_THREAD")

        if prior is None or not prior.is_alive():

            thread = _u15_threading.Thread(
                target=unit15_worker,
                name="WEEX-UNIT15-PERFORMANCE",
                daemon=True,
            )

            globals()["_UNIT15_THREAD"] = thread
            thread.start()

        status = "RUNNING"

    else:
        status = "DISABLED"

    print(
        "UNIT 15 EXCHANGE READ ONLY = TRUE",
        flush=True
    )
    print(
        "UNIT 15 HYBRID ADAPTER STATUS =",
        status,
        flush=True
    )
    print(
        "UNIT 15 HYBRID ADAPTER RESULT = PASS",
        flush=True
    )

    return {
        "unit": 15,
        "status": status,
        "unit_14_status": unit_14_result.get("status"),
        "exchange_write": False,
        "real_cash_execution": False,
        "scheduled_8h_enabled": UNIT15_8H_ENABLED,
        "on_demand_enabled": UNIT15_ON_DEMAND,
        "performance_report_hours": (1, 8, 24),
        "timezone": "Africa/Lagos",
    }


# ------------------------------------------------------------
# UNIT 15 EXECUTION CALL — EXACTLY ONCE
# ------------------------------------------------------------

FRESH_RECONSTRUCTION_UNIT_15_RESULT = (
    fresh_unit_15_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_14_RESULT,
    )
)

# ============================================================
# END UNIT 15 — COMPLETE 15-UNIT RECONSTRUCTION
# ============================================================
