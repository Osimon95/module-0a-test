
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
# START UNIT 5 HYBRID ADJUSTABLE ADAPTER
# ZERO INDENTATION
# PLACE AFTER EXISTING UNIT 5, BEFORE UNIT 6
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

    try:
        common = qualification["common"]
        breakout = qualification["breakout"]
        structure = qualification["structure"]
        scalp = qualification["scalp"]
    except (KeyError, TypeError):
        raise RuntimeError(
            "UNIT 5 ADAPTER QUALIFICATION CONFIG MISSING"
        )

    if analysis.get("strategy_evidence_version") != "U4_HYBRID_V2":
        raise RuntimeError(
            "UNIT 5 ADAPTER HYBRID UNIT 4 EVIDENCE MISSING"
        )

    if tuple(common["mode_priority"]) != (
        "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError("UNIT 5 ADAPTER INVALID PRIORITY")

    def number(key, default=None):
        value = analysis.get(key, default)
        if isinstance(value, bool):
            raise RuntimeError("INVALID NUMBER: " + key)
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise RuntimeError("INVALID NUMBER: " + key)
        if not math.isfinite(value):
            raise RuntimeError("NONFINITE NUMBER: " + key)
        return value

    def flag(key):
        value = analysis.get(key)
        if type(value) is not bool:
            raise RuntimeError("INVALID EVIDENCE FLAG: " + key)
        return value

    atr = number("atr14")
    close = number("latest_close")
    ema19 = number("ema19")
    ema50 = number("ema50")
    ema200 = number("ema200")
    move1 = number("move_1m_pct")
    move5 = number("move_5m_pct")
    move15 = number("move_15m_pct")
    support = number("support20")
    resistance = number("resistance20")
    separation = abs(number("ema19_50_separation_pct"))

    direction = analysis.get("direction_evidence", "NONE")
    long_votes = int(number("direction_long_votes"))
    short_votes = int(number("direction_short_votes"))

    if (
        atr <= 0
        or close <= 0
        or support <= 0
        or resistance <= support
        or direction not in ("LONG", "SHORT", "NONE")
        or long_votes < 0
        or short_votes < 0
        or long_votes + short_votes > 3
    ):
        raise RuntimeError("UNIT 5 INVALID MARKET EVIDENCE")

    # Freshness from exchange timestamps, not an
    # unverified success flag.

    exchange_ms = number("exchange_time_ms")
    close_ms = number("latest_close_time_ms")

    age_seconds = (exchange_ms - close_ms) / 1000.0

    max_age = float(
        config.get("market_data_policy", {}).get(
            "max_market_age_seconds", 120.0
        )
    )

    if not 0 <= age_seconds <= max_age:
        raise RuntimeError(
            "UNIT 5 ADAPTER STALE MARKET EVIDENCE"
        )

    def votes_ok(side, settings):
        required = int(settings["direction_votes_required"])
        if side == "LONG":
            return (
                direction == "LONG"
                and long_votes >= required
            )
        return (
            direction == "SHORT"
            and short_votes >= required
        )

    def fresh(settings):
        expiry = float(settings["candidate_expiry_seconds"])
        return age_seconds <= min(expiry, max_age)

    def state(side):
        if side == "LONG":
            return (
                close - resistance,
                move5 > 0 and move15 > 0
            )
        return (
            support - close,
            move5 < 0 and move15 < 0
        )

    # ========================================================
    # BREAKOUT QUALIFICATION
    # ========================================================

    breakout_candidates = (
        flag("breakout_developing_long")
        or flag("breakout_developing_short")
        or flag("breakout_confirmed_long")
        or flag("breakout_confirmed_short")
    )

    breakout_ready = "NONE"
    breakout_developing = False

    if breakout["enabled"] and fresh(breakout):
        for side in ("LONG", "SHORT"):
            distance, momentum_ok = state(side)

            extension_ok = (
                max(0.0, distance / atr)
                <= float(breakout["max_price_extension_atr"])
            )

            direction_ok = votes_ok(side, breakout)

            confirmed = flag(
                "breakout_confirmed_" + side.lower()
            )

            developing = flag(
                "breakout_developing_" + side.lower()
            )

            min_atr_ok = (
                number("atr_percent")
                >= float(breakout["minimum_atr_percent"])
            )

            quality_ok = (
                direction_ok
                and extension_ok
                and min_atr_ok
                and (
                    not breakout["require_momentum_confirmation"]
                    or momentum_ok
                )
            )

            if confirmed and quality_ok:
                breakout_ready = side
                break

            if (
                developing
                and breakout["early_detection_enabled"]
                and breakout["developing_candidate_enabled"]
                and direction_ok
                and extension_ok
                and (move5 > 0 if side == "LONG" else move5 < 0)
            ):
                breakout_developing = True

    # ========================================================
    # STRUCTURE QUALIFICATION
    # ========================================================

    structure_candidates = (
        flag("structure_developing_long")
        or flag("structure_developing_short")
    )

    structure_ready = "NONE"
    structure_developing = False

    if structure["enabled"] and fresh(structure):
        for side in ("LONG", "SHORT"):

            developing = flag(
                "structure_developing_" + side.lower()
            )

            trend_ok = (
                ema19 > ema50 > ema200
                if side == "LONG"
                else ema19 < ema50 < ema200
            )

            extension = (
                (close - ema19) / atr
                if side == "LONG"
                else (ema19 - close) / atr
            )

            base_ok = (
                developing
                and trend_ok
                and votes_ok(side, structure)
                and extension
                    <= float(structure["max_price_extension_atr"])
                and separation
                    >= float(
                        structure["minimum_ema_separation_percent"]
                    )
            )

            momentum_ok = (
                move5 > 0 and move15 > 0
                if side == "LONG"
                else move5 < 0 and move15 < 0
            )

            if base_ok:
                structure_developing = True

            if base_ok and momentum_ok:
                structure_ready = side
                break

    # ========================================================
    # SCALP ELIGIBILITY
    # ========================================================

    sideways = flag("sideways_candidate")
    overextended = flag("price_overextended")

    higher_mode_developing = (
        breakout_developing
        or structure_developing
    )

    fee_sides = (
        int(scalp["include_entry_fee"] is True)
        + int(scalp["include_exit_fee"] is True)
    )

    friction = (
        float(scalp["estimated_taker_fee_percent"])
        * fee_sides
        + float(scalp["estimated_slippage_percent"])
    )

    minimum_range = (
        friction
        * float(scalp["minimum_fee_coverage_multiplier"])
    )

    range_percent = (
        (resistance - support) / close * 100.0
    )

    scalp_direction_ok = (
        direction in ("LONG", "SHORT")
        and votes_ok(direction, scalp)
    )

    scalp_momentum_ok = (
        (direction == "LONG" and move1 > 0)
        or (direction == "SHORT" and move1 < 0)
    )

    scalp_pending = (
        scalp["enabled"] is True
        and (
            sideways
            or scalp["require_sideways_market"] is False
        )
        and not higher_mode_developing
        and not overextended
        and number("price_extension_cluster")
            <= float(scalp["max_ema_extension_clusters"])
        and scalp_direction_ok
        and scalp_momentum_ok
        and (
            scalp["fee_aware_enabled"] is False
            or range_percent >= minimum_range
        )
    )

    # ========================================================
    # EXCLUSIVE ARBITRATION
    # ========================================================

    active_mode = "NONE"
    admitted_direction = "NONE"
    qualified = False
    candidate_mode = "NONE"
    candidate_stage = "NONE"
    reason = "NO_ACCEPTABLE_CANDIDATE"

    if breakout_ready != "NONE":
        active_mode = "BREAKOUT"
        admitted_direction = breakout_ready
        qualified = True
        candidate_mode = "BREAKOUT"
        candidate_stage = "QUALIFIED"
        reason = "BREAKOUT_CONFIRMED"

    elif breakout_developing:
        candidate_mode = "BREAKOUT"
        candidate_stage = "DEVELOPING"
        reason = "BREAKOUT_DEVELOPING_AWAITING_CONFIRMATION"

    elif structure_ready != "NONE":
        active_mode = "STRUCTURE"
        admitted_direction = structure_ready
        qualified = True
        candidate_mode = "STRUCTURE"
        candidate_stage = "QUALIFIED"
        reason = "STRUCTURE_EARLY_QUALIFICATION"

    elif structure_developing:
        candidate_mode = "STRUCTURE"
        candidate_stage = "DEVELOPING"
        reason = "STRUCTURE_DEVELOPING_AWAITING_CONFIRMATION"

    elif scalp_pending:
        # SCALP is deliberately pending Unit 6.
        # It is NOT prematurely trade-authorized.
        candidate_mode = "SCALP"
        candidate_stage = "PENDING_UNIT_6"
        reason = "SCALP_PENDING_QUALITY_AND_FEES"

    elif breakout_candidates:
        candidate_mode = "BREAKOUT"
        candidate_stage = "REJECTED"
        reason = "BREAKOUT_EVIDENCE_NOT_QUALIFIED"

    elif structure_candidates:
        candidate_mode = "STRUCTURE"
        candidate_stage = "REJECTED"
        reason = "STRUCTURE_EVIDENCE_NOT_QUALIFIED"

    # ========================================================
    # ORIGINAL UNIT 5 CONTRACT + HYBRID FIELDS
    # ========================================================

    result = dict(original_candidate)

    # Preserve unrelated fields. Update classification
    # fields to reflect the hybrid decision.

    result.update({
        "qualified": qualified,
        "active_mode": active_mode,
        "direction": admitted_direction,
        "qualification_reason": reason,
        "candidate_mode": candidate_mode,
        "candidate_stage": candidate_stage,
        "higher_mode_developing": higher_mode_developing,
        "breakout_candidate": breakout_candidates,
        "structure_candidate": structure_candidates,
        "breakout_ready": breakout_ready != "NONE",
        "structure_ready": structure_ready != "NONE",
        "scalp_ready": scalp_pending,
        "sideways_context": sideways,
        "direction_evidence": direction,
        "scalp_quality_minimum":
            float(scalp["quality_threshold"]),
        "scalp_price_weight_percent":
            float(scalp["price_action_weight_percent"]),
        "estimated_round_trip_fee_pct": friction,
        "scalp_minimum_fee_coverage":
            float(scalp["minimum_fee_coverage_multiplier"]),
        "candle_data_fresh": True,
        "read_only": True,
        "trade_authorized": False,
        "order_payload_created": False,
        "strategy_evidence_version":
            "U5_HYBRID_ADJUSTABLE_V3",
        "unit_4_evidence_version": "U4_HYBRID_V2",
        "classification_revision": "V3.1",
        "candidate_protected":
            candidate_stage == "DEVELOPING",
        "candidate_age_seconds": age_seconds,
    })

    # All original candidate fields remain available.

    if not set(original_candidate).issubset(result):
        raise RuntimeError(
            "UNIT 5 ADAPTER ORIGINAL CONTRACT LOST"
        )

    if candidate_stage == "DEVELOPING" and qualified:
        raise RuntimeError(
            "UNIT 5 ADAPTER DEVELOPING SIGNAL AUTHORIZED"
        )

    if candidate_mode == "SCALP" and higher_mode_developing:
        raise RuntimeError(
            "UNIT 5 ADAPTER PRIORITY VIOLATION"
        )

    print("=" * 80, flush=True)
    print("UNIT 5 HYBRID ADJUSTABLE ADAPTER", flush=True)
    print("UNIT 5 MODE =", candidate_mode, flush=True)
    print("UNIT 5 STAGE =", candidate_stage, flush=True)
    print("UNIT 5 ACTIVE MODE =", active_mode, flush=True)
    print("UNIT 5 DIRECTION =", admitted_direction, flush=True)
    print("UNIT 5 QUALIFIED =", qualified, flush=True)
    print("UNIT 5 REASON =", reason, flush=True)
    print(
        "UNIT 5 HIGHER MODE DEVELOPING =",
        higher_mode_developing,
        flush=True
    )
    print(
        "UNIT 5 ORIGINAL FIELDS RETAINED = TRUE",
        flush=True
    )
    print(
        "UNIT 5 ADAPTER EXCHANGE WRITE = NONE",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 5 ADAPTER RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 5 HYBRID ADJUSTABLE ADAPTER
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
# END UNIT 5 HYBRID ADJUSTABLE ADAPTER
# UNIT 6 FOLLOWS
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
                unit_4_analysis.get(evidence_key) is True
                and unit_5_candidate.get(
                    "breakout_ready"
                ) is True
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

            if (
                unit_4_analysis.get(evidence_key) is True
                and unit_5_candidate.get(
                    "structure_ready"
                ) is True
            ):
                execution_intent = True
                admitted_mode = "STRUCTURE"
                admitted_direction = direction
                admission_reason = (
                    "STRUCTURE_QUALIFIED_ADMITTED"
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

def fresh_unit_6_original_execution_adapter(
    unit_2_config,
    unit_6_result,
    exchange_leverage_result=None,
):
    import copy

    print("=" * 80, flush=True)
    print("UNIT 6 EXECUTION ADAPTER V2 START", flush=True)

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 6 ADAPTER INVALID CONFIG"
        )

    if not isinstance(unit_6_result, dict):
        raise RuntimeError(
            "UNIT 6 ADAPTER INVALID SIGNAL"
        )

    config = copy.deepcopy(unit_2_config)
    result = dict(unit_6_result)

    strategy = config.get("strategy")

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 6 ADAPTER STRATEGY MISSING"
        )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 6 ADAPTER DEMO REQUIRED"
        )

    # ========================================================
    # 1. LEVERAGE POLICY
    # ========================================================

    # Do not invent leverage.
    # Do not modify WEEX exchange settings.
    # Leverage verification belongs to the authenticated
    # account preparation pathway in Unit 8.

    strategy.pop("leverage_target", None)
    strategy.pop("exchange_leverage_verified", None)

    # ========================================================
    # 2. ORIGINAL UNIT 7 REQUIRED FIELDS
    # ========================================================

    if "unit_5_reason" not in result:
        result["unit_5_reason"] = str(
            result.get(
                "admission_reason",
                "NONE"
            )
        )

    intent = result.get("execution_intent")
    qualified = result.get("signal_qualified")

    if type(intent) is not bool:
        raise RuntimeError(
            "UNIT 6 INVALID EXECUTION INTENT"
        )

    if type(qualified) is not bool:
        raise RuntimeError(
            "UNIT 6 INVALID SIGNAL QUALIFICATION"
        )

    if intent != qualified:
        raise RuntimeError(
            "UNIT 6 SIGNAL/INTENT CONTRADICTION"
        )

    # ========================================================
    # 3. IDLE / REJECTED / DEVELOPING SIGNAL
    # ========================================================

    if intent is False:

        result["execution_intent"] = False
        result["signal_qualified"] = False
        result["active_mode"] = "NONE"
        result["direction"] = "NONE"

        result["execution_handover_status"] = "IDLE"
        result["leverage_verification_deferred"] = False

        print(
            "UNIT 6 ADAPTER STATUS = IDLE",
            flush=True
        )

        print(
            "UNIT 6 ADAPTER REASON =",
            result.get("admission_reason"),
            flush=True
        )

        print(
            "UNIT 6 EXCHANGE WRITE = NONE",
            flush=True
        )

        print(
            "UNIT 6 EXECUTION ADAPTER V2 RESULT = PASS",
            flush=True
        )

        print("=" * 80, flush=True)

        return config, result

    # ========================================================
    # 4. QUALIFIED SIGNAL VALIDATION
    # ========================================================

    mode = result.get("active_mode")
    direction = result.get("direction")
    stage = result.get("candidate_stage")

    if mode not in (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP",
    ):
        raise RuntimeError(
            "UNIT 6 ADAPTER INVALID ACTIVE MODE"
        )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 6 ADAPTER INVALID DIRECTION"
        )

    if result.get("higher_mode_protected") is True:
        raise RuntimeError(
            "UNIT 6 DEVELOPING MODE NOT EXECUTABLE"
        )

    # ========================================================
    # 5. MODE-SPECIFIC QUALIFICATION
    # ========================================================

    if mode == "SCALP":

        if stage != "PENDING_UNIT_6":
            raise RuntimeError(
                "UNIT 6 SCALP STAGE INVALID"
            )

        if result.get("scalp_quality_pass") is not True:
            raise RuntimeError(
                "UNIT 6 SCALP QUALITY NOT PASSED"
            )

        if result.get("fee_coverage_pass") is not True:
            raise RuntimeError(
                "UNIT 6 SCALP FEE COVERAGE NOT PASSED"
            )

    else:

        if stage != "QUALIFIED":
            raise RuntimeError(
                "UNIT 6 HIGHER MODE NOT QUALIFIED"
            )

    # ========================================================
    # 6. PRESERVE HYBRID ADMISSION
    # ========================================================

    original_reason = str(
        result.get(
            "admission_reason",
            "NONE"
        )
    )

    result["hybrid_admission_reason"] = (
        original_reason
    )

    result["admission_reason"] = (
        "QUALIFIED_SIGNAL_ADMITTED"
    )

    result["execution_intent"] = True
    result["signal_qualified"] = True

    result["active_mode"] = mode
    result["direction"] = direction

    # ========================================================
    # 7. LEVERAGE VERIFICATION HANDOVER
    # ========================================================

    # Missing leverage must not erase a legitimately
    # qualified Hybrid signal.
    #
    # This does NOT mean leverage has been verified.
    # Unit 8 must authenticate and verify leverage
    # before calculating the order quantity.

    result["leverage_verification_deferred"] = True
    result["exchange_leverage_verified"] = False

    result["execution_handover_status"] = (
        "QUALIFIED_AWAITING_LEVERAGE"
    )

    result["leverage_target"] = None

    # ========================================================
    # 8. FINAL VERIFICATION
    # ========================================================

    if (
        result["execution_intent"] is not True
        or result["signal_qualified"] is not True
        or result["active_mode"] != mode
        or result["direction"] != direction
    ):
        raise RuntimeError(
            "UNIT 6 EXECUTION HANDOVER FAILED"
        )

    print(
        "UNIT 6 ADAPTER MODE =",
        mode,
        flush=True
    )

    print(
        "UNIT 6 ADAPTER DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 6 ADAPTER HYBRID REASON =",
        original_reason,
        flush=True
    )

    print(
        "UNIT 6 ADAPTER EXECUTION INTENT = True",
        flush=True
    )

    print(
        "UNIT 6 ADAPTER SIGNAL QUALIFIED = True",
        flush=True
    )

    print(
        "UNIT 6 ADAPTER STATUS = QUALIFIED_AWAITING_LEVERAGE",
        flush=True
    )

    print(
        "UNIT 6 ADAPTER LEVERAGE VERIFIED = False",
        flush=True
    )

    print(
        "UNIT 6 ADAPTER SIGNAL PRESERVED = True",
        flush=True
    )

    print(
        "UNIT 6 ADAPTER EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "UNIT 6 EXECUTION ADAPTER V2 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return config, result


# ============================================================
# RUN UNIT 6 AND EXECUTION ADAPTER
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
    None,
)


# ============================================================
# END UNIT 6 + EXECUTION ADAPTER
# ORIGINAL UNIT 7 CONTINUES BELOW
# ZERO INDENTATION
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
# COMPLETE UNIT 8 REPLACEMENT
# WEEX DEMO BALANCE + EXCHANGE LEVERAGE + POSITION SIZING
# ORIGINAL 22524-LINE INTERFACE
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
    import math
    import hmac
    import base64
    import hashlib
    import urllib.parse
    import urllib.request
    import urllib.error

    from decimal import Decimal, InvalidOperation
    from datetime import datetime, timezone

    print("=" * 80, flush=True)
    print("UNIT 8 RECONSTRUCTED START", flush=True)

    # ========================================================
    # 1. INPUT CONTRACT
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 8 CONFIG INVALID")

    if not isinstance(unit_7_result, dict):
        raise RuntimeError("UNIT 8 UNIT 7 INPUT INVALID")

    if not isinstance(market_snapshot, dict):
        raise RuntimeError("UNIT 8 MARKET INPUT INVALID")

    exchange = config.get("exchange")
    safety = config.get("safety")
    strategy = config.get("strategy")

    if not all(
        isinstance(x, dict)
        for x in (exchange, safety, strategy)
    ):
        raise RuntimeError("UNIT 8 CONFIG SECTIONS MISSING")

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError("UNIT 8 NOT DEMO ENVIRONMENT")

    base_url = exchange.get("contract_base_url")

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError("UNIT 8 WRONG WEEX BASE URL")

    if exchange.get("market_symbol") != "BTCUSDT":
        raise RuntimeError("UNIT 8 WRONG MARKET SYMBOL")

    # ========================================================
    # 2. UNIT 7 SIGNAL CONTRACT
    # ========================================================

    required = (
        "status",
        "active_mode",
        "direction",
        "signal_qualified",
        "execution_intent",
    )

    for field in required:
        if field not in unit_7_result:
            raise RuntimeError(
                "UNIT 8 UNIT 7 FIELD MISSING: " + field
            )

    status = str(
        unit_7_result["status"]
    ).upper()

    mode = str(
        unit_7_result["active_mode"]
    ).upper()

    direction = str(
        unit_7_result["direction"]
    ).upper()

    qualified = (
        unit_7_result["signal_qualified"] is True
    )

    intent = (
        unit_7_result["execution_intent"] is True
    )

    skip_reason = str(
        unit_7_result.get(
            "skip_reason",
            unit_7_result.get("reason", "NONE")
        )
    )

    # ========================================================
    # 3. ORIGINAL IDLE OUTPUT
    # ========================================================

    if not intent:

        result = {
            "status": "IDLE",
            "active_mode": mode,
            "direction": direction,
            "signal_qualified": qualified,
            "execution_intent": False,
            "trade_plan_ready": False,
            "trade_plan": None,
            "skip_reason": skip_reason,
            "read_only": True,
        }

        print("UNIT 8 STATUS = IDLE", flush=True)
        print("UNIT 8 REASON =", skip_reason, flush=True)
        print("UNIT 8 EXCHANGE WRITE = NONE", flush=True)

        return result

    if not qualified:
        raise RuntimeError(
            "UNIT 8 INTENT WITHOUT QUALIFIED SIGNAL"
        )

    if status != "READY_FOR_BALANCE":
        raise RuntimeError(
            "UNIT 8 NOT READY FOR BALANCE"
        )

    if mode not in ("SCALP", "STRUCTURE", "BREAKOUT"):
        raise RuntimeError("UNIT 8 INVALID MODE")

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError("UNIT 8 INVALID DIRECTION")

    if unit_7_result.get(
        "account_balance_required"
    ) is not True:
        raise RuntimeError(
            "UNIT 8 BALANCE REQUIREMENT MISSING"
        )

    if unit_7_result.get(
        "quantity_calculated"
    ) is not False:
        raise RuntimeError(
            "UNIT 8 UNIT 7 QUANTITY STATE INVALID"
        )

    if unit_7_result.get(
        "proposed_quantity"
    ) is not None:
        raise RuntimeError(
            "UNIT 8 UNIT 7 PRECALCULATED QUANTITY"
        )

    # ========================================================
    # 4. READ-ONLY SAFETY
    # ========================================================

    if safety.get(
        "demo_account_balance_read_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 8 DEMO BALANCE READ DISABLED"
        )

    for field in (
        "position_access_enabled",
        "order_endpoint_access_enabled",
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
    ):
        if safety.get(field) is not False:
            raise RuntimeError(
                "UNIT 8 UNSAFE CAPABILITY: " + field
            )

    # ========================================================
    # 5. VERIFIED BTC MARK PRICE
    # ========================================================

    if market_snapshot.get("symbol") != "BTCUSDT":
        raise RuntimeError(
            "UNIT 8 MARKET SNAPSHOT SYMBOL MISMATCH"
        )

    def positive_decimal(value, name):
        try:
            number = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise RuntimeError(
                "UNIT 8 INVALID " + name
            )

        if not number.is_finite() or number <= 0:
            raise RuntimeError(
                "UNIT 8 NONPOSITIVE " + name
            )

        return number

    mark_price = positive_decimal(
        market_snapshot.get("price"),
        "MARK PRICE"
    )

    # ========================================================
    # 6. ORIGINAL UNIT 12 API CREDENTIALS
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
            "UNIT 8 WEEX CREDENTIALS MISSING"
        )

    # ========================================================
    # 7. AUTHENTICATED WEEX GET
    # ORIGINAL UNIT 12 SIGNATURE FORMAT
    # ========================================================

    def signed_get(path, params=None):

        allowed_paths = {
            "/capi/v3/sim/balance",
            "/capi/v3/account/symbolConfig",
        }

        if path not in allowed_paths:
            raise RuntimeError(
                "UNIT 8 UNAUTHORIZED ENDPOINT"
            )

        query = urllib.parse.urlencode(params or {})

        request_path = (
            path + ("?" + query if query else "")
        )

        timestamp = str(int(time.time() * 1000))

        prehash = (
            timestamp + "GET" + request_path
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

                http_status = response.status

                body = json.loads(
                    response.read().decode("utf-8")
                )

        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(
                "utf-8",
                errors="replace"
            )[:400]

            raise RuntimeError(
                f"UNIT 8 HTTP {exc.code}: {detail}"
            ) from exc

        except urllib.error.URLError as exc:
            raise RuntimeError(
                "UNIT 8 NETWORK ERROR: " + str(exc)
            ) from exc

        if http_status != 200:
            raise RuntimeError(
                "UNIT 8 HTTP STATUS " + str(http_status)
            )

        if isinstance(body, dict):
            code = body.get("code")

            if code is not None and str(code) not in (
                "0", "200"
            ):
                raise RuntimeError(
                    "UNIT 8 WEEX ERROR: " + str(body)[:400]
                )

            return body.get("data", body)

        return body

    # ========================================================
    # 8. ORIGINAL DEMO BALANCE READ
    # ========================================================

    balance_data = signed_get(
        "/capi/v3/sim/balance"
    )

    if not isinstance(balance_data, list):
        raise RuntimeError(
            "UNIT 8 DEMO BALANCE RESPONSE INVALID"
        )

    susdt_record = next(
        (
            item
            for item in balance_data
            if isinstance(item, dict)
            and str(item.get("asset", "")).upper()
            == "SUSDT"
        ),
        None
    )

    if susdt_record is None:
        raise RuntimeError(
            "UNIT 8 SUSDT DEMO BALANCE MISSING"
        )

    available_balance = positive_decimal(
        susdt_record.get("availableBalance"),
        "SUSDT AVAILABLE BALANCE"
    )

    print(
        "UNIT 8 DEMO BALANCE =",
        available_balance,
        flush=True
    )

    # ========================================================
    # 9. NEW LEVERAGE CONFIGURATION REQUEST
    # NO OPEN POSITION REQUIRED
    #
    # This account configuration endpoint is documented by
    # WEEX, but its DEMO ACCOUNT scope is not yet verified.
    # Consequently the returned values are not automatically
    # treated as verified demo leverage.
    # ========================================================

    config_response = signed_get(
        "/capi/v3/account/symbolConfig",
        {"symbol": "BTCSUSDT"}
    )

    if isinstance(config_response, dict):
        config_items = [config_response]

    elif isinstance(config_response, list):
        config_items = config_response

    else:
        raise RuntimeError(
            "UNIT 8 LEVERAGE CONFIG FORMAT INVALID"
        )

    matching_configs = [
        item
        for item in config_items
        if isinstance(item, dict)
        and item.get("symbol") == "BTCSUSDT"
    ]

    if len(matching_configs) != 1:
        raise RuntimeError(
            "UNIT 8 BTCSUSDT LEVERAGE CONFIG NOT RETURNED"
        )

    leverage_config = matching_configs[0]

    long_leverage = positive_decimal(
        leverage_config.get("isolatedLongLeverage"),
        "LONG LEVERAGE"
    )

    short_leverage = positive_decimal(
        leverage_config.get("isolatedShortLeverage"),
        "SHORT LEVERAGE"
    )

    margin_mode = str(
        leverage_config.get("marginType", "")
    ).upper()

    if margin_mode != "ISOLATED":
        raise RuntimeError(
            "UNIT 8 EXPECTED ISOLATED MARGIN; GOT "
            + margin_mode
        )

    print(
        "UNIT 8 EXCHANGE LONG LEVERAGE =",
        long_leverage,
        flush=True
    )

    print(
        "UNIT 8 EXCHANGE SHORT LEVERAGE =",
        short_leverage,
        flush=True
    )

    print(
        "UNIT 8 OPEN POSITION REQUIRED = FALSE",
        flush=True
    )

    # No hardcoded 100x leverage.
    # No fallback to another symbol.
    #
    # This distinction is important:
    # A successful account configuration response does not
    # prove that WEEX is reporting DEMO account settings.
    #
    # Leave the next setting False until account scope has
    # been independently verified from WEEX.

    demo_leverage_scope_verified = False

    # ========================================================
    # 10. LEVERAGE SAFETY
    # ========================================================

    if not demo_leverage_scope_verified:
        raise RuntimeError(
            "UNIT 8 ACCOUNT LEVERAGES RECEIVED, "
            "BUT DEMO ACCOUNT SCOPE UNVERIFIED. "
            "DO NOT USE LIVE ACCOUNT LEVERAGE "
            "FOR DEMO POSITION SIZING."
        )

    leverage_target = (
        long_leverage
        if direction == "LONG"
        else short_leverage
    )

    # ========================================================
    # 11. ORIGINAL QUANTITY PARAMETERS
    # ========================================================

    quantity_step = positive_decimal(
        unit_7_result.get("quantity_step"),
        "QUANTITY STEP"
    )

    minimum_quantity = positive_decimal(
        unit_7_result.get("minimum_quantity"),
        "MINIMUM QUANTITY"
    )

    initial_margin_percent = positive_decimal(
        unit_7_result.get("initial_margin_percent"),
        "INITIAL MARGIN PERCENT"
    )

    # ========================================================
    # 12. ORIGINAL FIVE-BACKUP CONFIGURATION
    # ========================================================

    max_backups = int(
        strategy.get("max_backups", 0)
    )

    backup_multipliers = tuple(
        float(x)
        for x in strategy.get(
            "backup_multipliers", ()
        )
    )

    exposure_cap_percent = positive_decimal(
        strategy.get("exposure_cap_percent"),
        "EXPOSURE CAP"
    )

    if max_backups != 5:
        raise RuntimeError(
            "UNIT 8 EXPECTED FIVE BACKUPS"
        )

    if backup_multipliers != (
        1.0, 1.5, 2.0, 2.5, 3.0
    ):
        raise RuntimeError(
            "UNIT 8 BACKUP MULTIPLIERS INVALID"
        )

    if exposure_cap_percent > Decimal("35"):
        raise RuntimeError(
            "UNIT 8 EXPOSURE CAP ABOVE 35%"
        )

    # ========================================================
    # 13. ORIGINAL FIXED-USDT INITIAL ENTRY
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

    if fixed_usdt > maximum_initial_margin:
        raise RuntimeError(
            "UNIT 8 INITIAL MARGIN EXCEEDS EXPOSURE CAP"
        )

    if fixed_usdt > available_balance:
        raise RuntimeError(
            "UNIT 8 INSUFFICIENT AVAILABLE BALANCE"
        )

    margin_allocation = fixed_usdt

    # ========================================================
    # 14. EXCHANGE LEVERAGE-BASED POSITION SIZING
    # ========================================================

    notional = margin_allocation * leverage_target

    raw_quantity = notional / mark_price

    steps = (
        raw_quantity / quantity_step
    ).to_integral_value(rounding="ROUND_FLOOR")

    quantity = steps * quantity_step

    if quantity < minimum_quantity:
        raise RuntimeError(
            "UNIT 8 CALCULATED QUANTITY BELOW EXCHANGE MINIMUM"
        )

    if quantity <= 0:
        raise RuntimeError(
            "UNIT 8 NONPOSITIVE QUANTITY"
        )

    print(
        "UNIT 8 INITIAL MARGIN =",
        margin_allocation,
        flush=True
    )

    print(
        "UNIT 8 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 8 EFFECTIVE LEVERAGE =",
        leverage_target,
        flush=True
    )

    print(
        "UNIT 8 EXECUTABLE QUANTITY =",
        quantity,
        flush=True
    )

    # ========================================================
    # 15. ORIGINAL NORMALIZED POSITION SIZING
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
        "quantity": float(quantity),
        "position_sizing_performed": True,
        "quantity_calculated": True,
        "source": "WEEX_VERIFIED_DEMO_LEVERAGE",
        "read_only": True,
    }

    # ========================================================
    # 16. ORIGINAL TRADE PLAN
    # ========================================================

    trade_plan = {
        "active_mode": mode,
        "direction": direction,
        "quantity": float(quantity),
        "position_sizing": position_sizing,
        "execution_environment": "DEMO",
    }

    # ========================================================
    # 17. ORIGINAL UNIT 9 OUTPUT CONTRACT
    # ========================================================

    result = {
        "status": "READY",
        "active_mode": mode,
        "direction": direction,
        "signal_qualified": True,
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": trade_plan,
        "skip_reason": "NONE",
        "read_only": True,
    }

    print(
        "UNIT 8 TRADE PLAN READY = TRUE",
        flush=True
    )

    print(
        "UNIT 8 LEVERAGE MUTATION = NONE",
        flush=True
    )

    print(
        "UNIT 8 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 8 EXCHANGE WRITE = NONE",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 8 EXECUTION — ORIGINAL THREE ARGUMENT INTERFACE
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

