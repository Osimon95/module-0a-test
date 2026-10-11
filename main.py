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
# ============================================================
#
# COORDINATED ENTRY AND RE-ENTRY CONFIGURATION
#
# PRESERVED:
# - WEEX V3
# - BTCUSDT public market
# - BTCSUSDT demo environment
# - 100x target leverage
# - Initial margin 5%
# - Backup margin 5%
# - Maximum backups 3
# - Exposure cap 35%
# - TP allocation 10/20/70
# - TP3 dynamic trailing
# - SL disabled
# - One direction only
# - Anti-duplicate protection
# - REAL TRADING DISABLED
#
# NEW CONFIGURATION:
# - Continuous entry scan
# - Five-second scan interval
# - Flat-position re-entry
# - Fresh signal requirement
# - Price-led scalp scoring
# - Exchange-state reconciliation
# ============================================================


def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 2 START")

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
        raise RuntimeError(
            "UNIT 2 BLOCKED: UNIT 1 NOT READY"
        )

    # ========================================================
    # EXCHANGE CONFIGURATION
    # INDENTATION: 4 SPACES
    # ========================================================

    exchange = {
        "name": "WEEX",
        "api_version": "V3",
        "contract_base_url":
            "https://api-contract.weex.com",
        "market_symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",
    }

    execution_environment = "DEMO"

    # ========================================================
    # SAFETY CONFIGURATION
    # INDENTATION: 4 SPACES
    #
    # These are baseline capabilities.
    # Validated later demo execution units use separate gates.
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
    # STRATEGY CONFIGURATION
    # INDENTATION: 4 SPACES
    # ========================================================

    strategy = {

        # LEVERAGE AND POSITION SIZE
        "leverage_target": 100,
        "initial_margin_percent": 5.0,
        "backup_margin_percent": 5.0,
        "backup_buffer_percent": 0.30,
        "max_backups": 3,
        "exposure_cap_percent": 35.0,

        # PROFIT ALLOCATION
        "tp1_allocation_percent": 10.0,
        "tp2_allocation_percent": 20.0,
        "tp3_allocation_percent": 70.0,

        # NET ROI TARGET FLOORS
        "tp1_net_roi_floor_percent": 5.0,
        "tp2_net_roi_floor_percent": 10.0,
        "tp1_tp2_min_roi_separation_percent": 5.0,

        # TP3 DYNAMIC TRAILING
        "tp3_trailing_reference_percent": 0.20,
        "tp3_trailing_min_percent": 0.10,
        "tp3_trailing_max_percent": 0.40,

        # FEE ESTIMATE; NOT AN EXCHANGE FEE QUOTE
        "futures_taker_fee_percent": 0.08,

        # EXISTING SIGNAL CONTROL
        "signal_expiry_seconds": 120,
        "loss_cooldown_seconds": 300,
        "one_direction_only": True,
        "anti_duplicate_orders": True,
        "active_trade_mode_lock": True,
        "exclusive_mode": True,
        "mode_confirmations_required": 3,

        # CONTINUOUS ENTRY SCANNING
        "continuous_entry_scan_enabled": True,
        "entry_scan_interval_seconds": 5.0,
        "refresh_market_each_scan": True,
        "refresh_signal_each_scan": True,
        "refresh_indicators_on_new_candle": True,

        # FLAT POSITION RE-ENTRY
        "flat_position_reentry_enabled": True,
        "require_fresh_reentry_signal": True,
        "require_confirmed_flat_position": True,
        "require_no_pending_entry_orders": True,
        "require_exchange_state_reconciliation": True,

        # RE-ENTRY PROTECTION
        "profitable_close_reentry_enabled": True,
        "loss_cooldown_reentry_required": True,
        "block_duplicate_signal_ids": True,
        "block_unconfirmed_order_state": True,
        "require_fresh_account_balance": True,
        "reconcile_after_restart": True,

        # SCALP QUALITY SCORING
        "scalp_quality_threshold": 70.0,

        "scalp_price_weight": 50.0,
        "scalp_ema_weight": 15.0,
        "scalp_momentum_weight": 15.0,
        "scalp_structure_weight": 10.0,
        "scalp_volatility_timing_weight": 10.0,

        # MODE PRESERVATION
        "scalp_mode_enabled": True,
        "structure_mode_enabled": True,
        "breakout_mode_enabled": True,

        # EXISTING SL POLICY
        "stop_loss_enabled": False,

        # EXECUTION BOUNDARY
        "real_money_execution_enabled": False,
    }

    # ========================================================
    # MARKET PRECISION
    # INDENTATION: 4 SPACES
    # ========================================================

    market_precision = {
        "quantity_step": 0.0001,
        "minimum_quantity": 0.0001,
        "price_step": 0.1,
    }

    # ========================================================
    # COMPLETE CONFIGURATION
    # INDENTATION: 4 SPACES
    # ========================================================

    config = {
        "exchange": exchange,
        "execution_environment": execution_environment,
        "safety": safety,
        "strategy": strategy,
        "market_precision": market_precision,
    }

    # ========================================================
    # STRICT VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    errors = []

    if exchange["name"] != "WEEX":
        errors.append("INVALID_EXCHANGE")

    if exchange["api_version"] != "V3":
        errors.append("INVALID_API_VERSION")

    if exchange["contract_base_url"] != (
        "https://api-contract.weex.com"
    ):
        errors.append("INVALID_BASE_URL")

    if exchange["market_symbol"] != "BTCUSDT":
        errors.append("INVALID_MARKET_SYMBOL")

    if exchange["demo_order_symbol"] != "BTCSUSDT":
        errors.append("INVALID_DEMO_SYMBOL")

    if execution_environment != "DEMO":
        errors.append("REAL_ENVIRONMENT_PROHIBITED")

    if strategy["leverage_target"] <= 0:
        errors.append("INVALID_LEVERAGE")

    if not (0 < strategy["initial_margin_percent"] <= 5):
        errors.append("INVALID_INITIAL_MARGIN")

    if not (0 < strategy["backup_margin_percent"] <= 5):
        errors.append("INVALID_BACKUP_MARGIN")

    if strategy["max_backups"] != 3:
        errors.append("INVALID_BACKUP_COUNT")

    if strategy["backup_buffer_percent"] <= 0:
        errors.append("INVALID_BACKUP_BUFFER")

    if not (0 < strategy["exposure_cap_percent"] <= 35):
        errors.append("INVALID_EXPOSURE_CAP")

    staged_margin = (
        strategy["initial_margin_percent"]
        + strategy["max_backups"]
        * strategy["backup_margin_percent"]
    )

    if staged_margin > strategy["exposure_cap_percent"]:
        errors.append("STAGED_MARGIN_EXCEEDS_CAP")

    # ========================================================
    # TAKE PROFIT VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    tp_total = sum((
        strategy["tp1_allocation_percent"],
        strategy["tp2_allocation_percent"],
        strategy["tp3_allocation_percent"],
    ))

    if abs(tp_total - 100.0) > 0.000001:
        errors.append("INVALID_TP_ALLOCATION")

    if strategy["tp1_net_roi_floor_percent"] < 5:
        errors.append("INVALID_TP1_FLOOR")

    if strategy["tp2_net_roi_floor_percent"] < 10:
        errors.append("INVALID_TP2_FLOOR")

    if strategy["tp1_tp2_min_roi_separation_percent"] <= 0:
        errors.append("INVALID_TP_SEPARATION")

    trailing_min = strategy["tp3_trailing_min_percent"]
    trailing_ref = strategy["tp3_trailing_reference_percent"]
    trailing_max = strategy["tp3_trailing_max_percent"]

    if not (0 < trailing_min <= trailing_ref <= trailing_max):
        errors.append("INVALID_DYNAMIC_TRAILING_RANGE")

    # ========================================================
    # ENTRY SCAN VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    if strategy["continuous_entry_scan_enabled"] is not True:
        errors.append("CONTINUOUS_SCAN_DISABLED")

    if strategy["entry_scan_interval_seconds"] < 5:
        errors.append("SCAN_INTERVAL_TOO_SHORT")

    if strategy["refresh_market_each_scan"] is not True:
        errors.append("MARKET_REFRESH_DISABLED")

    if strategy["refresh_signal_each_scan"] is not True:
        errors.append("SIGNAL_REFRESH_DISABLED")

    if strategy["signal_expiry_seconds"] <= 0:
        errors.append("INVALID_SIGNAL_EXPIRY")

    if strategy["loss_cooldown_seconds"] < 300:
        errors.append("INSUFFICIENT_LOSS_COOLDOWN")

    # ========================================================
    # SCALP WEIGHT VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    weight_keys = (
        "scalp_price_weight",
        "scalp_ema_weight",
        "scalp_momentum_weight",
        "scalp_structure_weight",
        "scalp_volatility_timing_weight",
    )

    total_weight = sum(
        strategy[key] for key in weight_keys
    )

    if abs(total_weight - 100.0) > 0.000001:
        errors.append("SCALP_WEIGHTS_NOT_100")

    if strategy["scalp_price_weight"] != 50.0:
        errors.append("PRICE_WEIGHT_NOT_50")

    quality_threshold = strategy["scalp_quality_threshold"]

    if not (0 < quality_threshold <= 100):
        errors.append("INVALID_SCALP_THRESHOLD")

    # ========================================================
    # ANTI-DUPLICATE AND RE-ENTRY VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    required_protections = (
        "one_direction_only",
        "anti_duplicate_orders",
        "active_trade_mode_lock",
        "exclusive_mode",
        "flat_position_reentry_enabled",
        "require_fresh_reentry_signal",
        "require_confirmed_flat_position",
        "require_no_pending_entry_orders",
        "require_exchange_state_reconciliation",
        "block_duplicate_signal_ids",
        "block_unconfirmed_order_state",
        "require_fresh_account_balance",
        "reconcile_after_restart",
        "loss_cooldown_reentry_required",
    )

    for key in required_protections:
        if strategy.get(key) is not True:
            errors.append("PROTECTION_DISABLED:" + key)

    if strategy["mode_confirmations_required"] <= 0:
        errors.append("INVALID_MODE_CONFIRMATIONS")

    # ========================================================
    # MARKET PRECISION VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    for key in (
        "quantity_step",
        "minimum_quantity",
        "price_step",
    ):
        if market_precision[key] <= 0:
            errors.append("INVALID_PRECISION:" + key)

    # ========================================================
    # ZERO REAL-MONEY WRITE SAFETY
    # INDENTATION: 4 SPACES
    # ========================================================

    if strategy["real_money_execution_enabled"] is not False:
        errors.append("REAL_EXECUTION_NOT_BLOCKED")

    if safety["public_market_data_read_enabled"] is not True:
        errors.append("PUBLIC_MARKET_READ_DISABLED")

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

    for key in forbidden_capabilities:
        if safety.get(key) is not False:
            errors.append("UNSAFE_CAPABILITY:" + key)

    # ========================================================
    # VALIDATION RESULT
    # INDENTATION: 4 SPACES
    # ========================================================

    if errors:
        print(
            "UNIT 2 VALIDATION ERRORS =",
            errors,
            flush=True,
        )
        raise RuntimeError(
            "UNIT 2 CONFIGURATION VALIDATION FAILED"
        )

    # ========================================================
    # RENDER LOGGING
    # INDENTATION: 4 SPACES
    # ========================================================

    print("PASS: UNIT 2 CONFIGURATION CREATED", flush=True)
    print("PASS: EXCHANGE = WEEX V3", flush=True)
    print("PASS: MARKET SYMBOL = BTCUSDT", flush=True)
    print("PASS: DEMO SYMBOL = BTCSUSDT", flush=True)

    print(
        "PASS: CONTINUOUS ENTRY SCAN CONFIGURED = TRUE",
        flush=True,
    )

    print(
        "PASS: ENTRY SCAN INTERVAL = 5 SECONDS",
        flush=True,
    )

    print(
        "PASS: FLAT POSITION REENTRY CONFIGURED = TRUE",
        flush=True,
    )

    print(
        "PASS: FRESH REENTRY SIGNAL REQUIRED",
        flush=True,
    )

    print(
        "PASS: EXCHANGE STATE RECONCILIATION REQUIRED",
        flush=True,
    )

    print(
        "PASS: ANTI-DUPLICATE PROTECTION CONFIGURED",
        flush=True,
    )

    print(
        "PASS: POSITION SIZE CONFIGURATION VALIDATED",
        flush=True,
    )

    print(
        "PASS: SCALP PRICE WEIGHT = 50%",
        flush=True,
    )

    print(
        "PASS: SCALP QUALITY THRESHOLD = 70",
        flush=True,
    )

    print(
        "PASS: SCALP / STRUCTURE / BREAKOUT CONFIGURED",
        flush=True,
    )

    print(
        "PASS: TP ALLOCATION = 10 / 20 / 70",
        flush=True,
    )

    print(
        "PASS: TP3 DYNAMIC TRAILING CONFIGURED",
        flush=True,
    )

    print(
        "PASS: MAXIMUM BACKUPS = 3",
        flush=True,
    )

    print(
        "PASS: SL REMAINS DISABLED",
        flush=True,
    )

    print(
        "PASS: REAL MONEY EXECUTION DISABLED",
        flush=True,
    )

    print(
        "ZERO EXCHANGE WRITE BY UNIT 2 = TRUE",
        flush=True,
    )

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
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 2
# ZERO INDENTATION DEMARCATION
#
# UNIT 2 FULLY CLOSED
# UNIT 2 CALLED ONCE
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN TRY
# NO OPEN LOOP
# NO OPEN DICTIONARY
#
# EXISTING UNIT 3 CONTINUES DIRECTLY BELOW
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 3
# ZERO INDENTATION DEMARCATION
# ============================================================
#
# PURPOSE:
# - WEEX V3 public live BTC mark-price reader
# - Reusable price refresh function
# - Prepared for continuous entry scanning
# - Exchange timestamp validation
# - Reject stale or invalid market responses
# - Maintain Unit 4 snapshot compatibility
#
# IMPORTANT:
# - Unit 3 performs HTTP GET only
# - No authentication
# - No account access
# - No position access
# - No order execution
# - No exchange mutation
# - Real-money trading prohibited
#
# Continuous scheduling is handled by the later
# runtime controller, not by Unit 3 itself.
# ============================================================


import time
import math


# ============================================================
# UNIT 3 MARKET REFRESH FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_3():

    print("=" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 3 START"
    )

    # ========================================================
    # 1. RECEIVE UNIT 2 CONFIGURATION
    # INDENTATION: 4 SPACES
    # ========================================================

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 BLOCKED: CONFIGURATION MISSING"
        )

    exchange = config.get("exchange")
    safety = config.get("safety")
    strategy = config.get("strategy")

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 3 BLOCKED: EXCHANGE CONFIG MISSING"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 3 BLOCKED: SAFETY CONFIG MISSING"
        )

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 3 BLOCKED: STRATEGY CONFIG MISSING"
        )

    print(
        "PASS: UNIT 3 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    # ========================================================
    # 2. EXCHANGE CONTRACT VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 3 INVALID EXCHANGE"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 3 INVALID API VERSION"
        )

    base_url = exchange.get(
        "contract_base_url"
    )

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 3 INVALID BASE URL"
        )

    market_symbol = exchange.get(
        "market_symbol"
    )

    if market_symbol != "BTCUSDT":
        raise RuntimeError(
            "UNIT 3 INVALID MARKET SYMBOL"
        )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 3 INVALID EXECUTION ENVIRONMENT"
        )

    # ========================================================
    # 3. CONTINUOUS SCAN CONFIGURATION
    # INDENTATION: 4 SPACES
    # ========================================================

    scan_enabled = strategy.get(
        "continuous_entry_scan_enabled",
        False,
    )

    scan_interval = float(
        strategy.get(
            "entry_scan_interval_seconds",
            5.0,
        )
    )

    refresh_enabled = strategy.get(
        "refresh_market_each_scan",
        False,
    )

    if scan_enabled is not True:
        raise RuntimeError(
            "UNIT 3 CONTINUOUS SCAN NOT CONFIGURED"
        )

    if refresh_enabled is not True:
        raise RuntimeError(
            "UNIT 3 MARKET REFRESH DISABLED"
        )

    if not math.isfinite(scan_interval):
        raise RuntimeError(
            "UNIT 3 INVALID SCAN INTERVAL"
        )

    if scan_interval < 5.0:
        raise RuntimeError(
            "UNIT 3 SCAN INTERVAL BELOW MINIMUM"
        )

    print(
        "PASS: UNIT 3 CONTINUOUS SCAN CONFIGURATION",
        flush=True,
    )

    print(
        "UNIT 3 CONFIGURED SCAN INTERVAL =",
        scan_interval,
        "SECONDS",
        flush=True,
    )

    # ========================================================
    # 4. STRICT READ-ONLY SAFETY
    # INDENTATION: 4 SPACES
    # ========================================================

    if safety.get(
        "public_market_data_read_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 3 PUBLIC MARKET READ DISABLED"
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
                "UNIT 3 UNSAFE CAPABILITY: "
                + capability
            )

    if strategy.get(
        "real_money_execution_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 3 REAL EXECUTION NOT BLOCKED"
        )

    print(
        "PASS: UNIT 3 READ-ONLY SAFETY GATE",
        flush=True,
    )

    # ========================================================
    # 5. WEEX V3 LIVE MARKET ENDPOINT
    # INDENTATION: 4 SPACES
    # ========================================================

    endpoint = (
        "/capi/v3/market/symbolPrice"
    )

    price_type = "MARK"

    query = urllib.parse.urlencode({
        "symbol": market_symbol,
        "priceType": price_type,
    })

    request_url = (
        base_url
        + endpoint
        + "?"
        + query
    )

    request = urllib.request.Request(
        url=request_url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent":
                "Fresh-WEEX-Reconstruction/Unit3",
            "Cache-Control": "no-cache",
        },
    )

    if request.get_method() != "GET":
        raise RuntimeError(
            "UNIT 3 NON-GET REQUEST BLOCKED"
        )

    if request.data is not None:
        raise RuntimeError(
            "UNIT 3 REQUEST BODY BLOCKED"
        )

    # ========================================================
    # 6. LIVE MARKET PRICE RETRIEVAL
    # INDENTATION: 4 SPACES
    # ========================================================

    request_started_ms = int(
        time.time() * 1000
    )

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

        print(
            "UNIT 3 HTTP ERROR =",
            exc.code,
            flush=True,
        )

        raise RuntimeError(
            "UNIT 3 MARKET HTTP REQUEST FAILED"
        ) from exc

    except urllib.error.URLError as exc:

        print(
            "UNIT 3 CONNECTION ERROR =",
            repr(exc.reason),
            flush=True,
        )

        raise RuntimeError(
            "UNIT 3 MARKET CONNECTION FAILED"
        ) from exc

    response_received_ms = int(
        time.time() * 1000
    )

    if http_status != 200:
        raise RuntimeError(
            "UNIT 3 INVALID HTTP STATUS"
        )

    if not response_body:
        raise RuntimeError(
            "UNIT 3 EMPTY MARKET RESPONSE"
        )

    # ========================================================
    # 7. JSON VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    try:

        payload = json.loads(
            response_body
        )

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "UNIT 3 INVALID JSON RESPONSE"
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError(
            "UNIT 3 INVALID RESPONSE STRUCTURE"
        )

    # ========================================================
    # 8. MARKET SYMBOL AND PRICE VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    response_symbol = payload.get(
        "symbol"
    )

    if response_symbol != market_symbol:
        raise RuntimeError(
            "UNIT 3 MARKET SYMBOL MISMATCH"
        )

    try:

        live_price = float(
            payload.get("price")
        )

    except (TypeError, ValueError) as exc:

        raise RuntimeError(
            "UNIT 3 INVALID BTC PRICE"
        ) from exc

    if not math.isfinite(live_price):
        raise RuntimeError(
            "UNIT 3 NON-FINITE BTC PRICE"
        )

    if live_price <= 0:
        raise RuntimeError(
            "UNIT 3 NON-POSITIVE BTC PRICE"
        )

    # ========================================================
    # 9. EXCHANGE TIMESTAMP VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    raw_exchange_time = payload.get(
        "time"
    )

    try:

        exchange_time_ms = int(
            raw_exchange_time
        )

    except (TypeError, ValueError) as exc:

        raise RuntimeError(
            "UNIT 3 INVALID EXCHANGE TIMESTAMP"
        ) from exc

    if exchange_time_ms <= 0:
        raise RuntimeError(
            "UNIT 3 INVALID MARKET TIMESTAMP"
        )

    # Normalize seconds to milliseconds if necessary.
    # Modern Unix milliseconds are approximately 13 digits.

    if exchange_time_ms < 100000000000:
        exchange_time_ms *= 1000

    market_age_ms = (
        response_received_ms
        - exchange_time_ms
    )

    # Small clock deviations are tolerated.
    # Very old market data is not accepted.

    if market_age_ms > 120000:
        raise RuntimeError(
            "UNIT 3 STALE MARKET PRICE"
        )

    if market_age_ms < -30000:
        raise RuntimeError(
            "UNIT 3 INVALID FUTURE MARKET TIMESTAMP"
        )

    # ========================================================
    # 10. NORMALIZED LIVE MARKET SNAPSHOT
    # INDENTATION: 4 SPACES
    # ========================================================

    market_snapshot = {

        # Existing Unit 4 compatibility fields
        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": market_symbol,
        "price": live_price,
        "price_type": price_type,
        "exchange_time_ms": exchange_time_ms,
        "source": "WEEX_V3_PUBLIC_MARK_PRICE",
        "read_only": True,

        # Additional scan diagnostics
        "request_started_ms": request_started_ms,
        "response_received_ms": response_received_ms,
        "market_age_ms": market_age_ms,
        "scan_interval_seconds": scan_interval,
        "continuous_scan_configured": True,
        "market_refresh_completed": True,
        "http_method": "GET",
        "authenticated": False,
    }

    # ========================================================
    # 11. FINAL SNAPSHOT VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    required_fields = (
        "exchange",
        "api_version",
        "symbol",
        "price",
        "price_type",
        "exchange_time_ms",
        "source",
        "read_only",
    )

    for field in required_fields:

        if field not in market_snapshot:
            raise RuntimeError(
                "UNIT 3 SNAPSHOT FIELD MISSING: "
                + field
            )

    if market_snapshot["read_only"] is not True:
        raise RuntimeError(
            "UNIT 3 READ-ONLY VALIDATION FAILED"
        )

    # ========================================================
    # 12. VISIBLE RENDER STATUS
    # INDENTATION: 4 SPACES
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "PASS: UNIT 3 LIVE BTC MARKET READ",
        flush=True,
    )

    print(
        "UNIT 3 MARKET SYMBOL =",
        market_symbol,
        flush=True,
    )

    print(
        "UNIT 3 LIVE BTC MARK PRICE =",
        live_price,
        flush=True,
    )

    print(
        "UNIT 3 EXCHANGE TIMESTAMP =",
        exchange_time_ms,
        flush=True,
    )

    print(
        "UNIT 3 MARKET AGE MS =",
        market_age_ms,
        flush=True,
    )

    print(
        "UNIT 3 SCAN INTERVAL CONFIGURED =",
        scan_interval,
        flush=True,
    )

    print(
        "UNIT 3 MARKET REFRESH = COMPLETED",
        flush=True,
    )

    print(
        "UNIT 3 SNAPSHOT READY FOR UNIT 4 = TRUE",
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

    print("-" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 3 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return market_snapshot


# ============================================================
# RUN UNIT 3 - INITIAL MARKET SNAPSHOT
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# UNIT 3 REUSABLE REFRESH ENTRY POINT
# ZERO INDENTATION
#
# The forthcoming runtime controller will call:
#
# fresh_reconstruction_refresh_unit_3()
#
# This retrieves an entirely new market snapshot.
# It does NOT submit an order.
# ============================================================

def fresh_reconstruction_refresh_unit_3():

    global FRESH_RECONSTRUCTION_MARKET_SNAPSHOT

    fresh_snapshot = (
        fresh_reconstruction_unit_3()
    )

    FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
        fresh_snapshot
    )

    return fresh_snapshot


# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 3
# ZERO INDENTATION DEMARCATION
#
# UNIT 3 FULLY CLOSED
# INITIAL MARKET SNAPSHOT CREATED
# REUSABLE MARKET REFRESH FUNCTION CREATED
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN LOOP
# NO OPEN TRY
# NO OPEN DICTIONARY
#
# EXISTING UNIT 4 CONTINUES DIRECTLY BELOW
# ============================================================



# ============================================================
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 4
# ZERO INDENTATION DEMARCATION
# ============================================================
#
# REFRESHABLE BTC MARKET ANALYSIS
#
# PRESERVED:
# - WEEX V3 public market data
# - BTCUSDT
# - 1-minute mark-price candles
# - EMA19 / EMA50 / EMA100 / EMA200
# - Closed-candle momentum
# - Unit 5 compatibility
#
# ADDED:
# - Reusable analysis refresh
# - Fresh Unit 3 snapshot support
# - Recent support and resistance
# - Candle range and wick analysis
# - Price position within recent range
# - ATR-style volatility estimate
# - Source timestamps and validation
#
# NO DEMO ORDER
# NO REAL ORDER
# ZERO EXCHANGE WRITE
# ============================================================

import math
import time
import urllib.error
import urllib.parse
import urllib.request
import json


# ============================================================
# UNIT 4 EMA HELPER
# ZERO INDENTATION
# ============================================================

def fresh_unit_4_calculate_ema(prices, period):

    if len(prices) < period:
        raise ValueError(
            "INSUFFICIENT EMA DATA"
        )

    value = sum(
        prices[:period]
    ) / period

    multiplier = (
        2.0 / (period + 1.0)
    )

    for price in prices[period:]:
        value = (
            price * multiplier
            + value * (1.0 - multiplier)
        )

    if not math.isfinite(value):
        raise ValueError(
            "INVALID EMA RESULT"
        )

    return float(value)


# ============================================================
# UNIT 4 MARKET ANALYSIS
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_4(
    market_snapshot=None
):

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 4 START")

    # ========================================================
    # 1. CONFIGURATION
    # INDENTATION: 4 SPACES
    # ========================================================

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 4 CONFIGURATION MISSING"
        )

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})
    strategy = config.get("strategy", {})

    if not all(
        isinstance(item, dict)
        for item in (exchange, safety, strategy)
    ):
        raise RuntimeError(
            "UNIT 4 INVALID CONFIGURATION SECTIONS"
        )

    if market_snapshot is None:
        market_snapshot = (
            FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
        )

    if not isinstance(market_snapshot, dict):
        raise RuntimeError(
            "UNIT 4 MARKET SNAPSHOT MISSING"
        )

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 4 INVALID EXCHANGE"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 4 INVALID API VERSION"
        )

    symbol = exchange.get("market_symbol")

    if symbol != "BTCUSDT":
        raise RuntimeError(
            "UNIT 4 INVALID MARKET SYMBOL"
        )

    if market_snapshot.get("symbol") != symbol:
        raise RuntimeError(
            "UNIT 4 MARKET SYMBOL MISMATCH"
        )

    if market_snapshot.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 4 MARKET SNAPSHOT NOT READ ONLY"
        )

    if market_snapshot.get("price_type") != "MARK":
        raise RuntimeError(
            "UNIT 4 PRICE TYPE MISMATCH"
        )

    # ========================================================
    # 2. SAFETY GATE
    # INDENTATION: 4 SPACES
    # ========================================================

    if safety.get(
        "public_market_data_read_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 4 PUBLIC READ DISABLED"
        )

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
                "UNIT 4 UNSAFE CAPABILITY: " + key
            )

    if strategy.get(
        "real_money_execution_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 4 REAL EXECUTION NOT BLOCKED"
        )

    # ========================================================
    # 3. VALIDATE LIVE SNAPSHOT
    # INDENTATION: 4 SPACES
    # ========================================================

    live_mark = float(
        market_snapshot["price"]
    )

    exchange_time_ms = int(
        market_snapshot["exchange_time_ms"]
    )

    now_ms = int(time.time() * 1000)

    if not math.isfinite(live_mark) or live_mark <= 0:
        raise RuntimeError(
            "UNIT 4 INVALID LIVE PRICE"
        )

    if exchange_time_ms <= 0:
        raise RuntimeError(
            "UNIT 4 INVALID EXCHANGE TIME"
        )

    if now_ms - exchange_time_ms > 120000:
        raise RuntimeError(
            "UNIT 4 STALE MARKET SNAPSHOT"
        )

    if exchange_time_ms - now_ms > 30000:
        raise RuntimeError(
            "UNIT 4 FUTURE MARKET TIMESTAMP"
        )

    # ========================================================
    # 4. PUBLIC CANDLE REQUEST
    # INDENTATION: 4 SPACES
    # ========================================================

    interval = "1m"
    limit = 300

    base_url = exchange.get(
        "contract_base_url"
    )

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 4 INVALID BASE URL"
        )

    endpoint = (
        "/capi/v3/market/markPriceKlines"
    )

    query = urllib.parse.urlencode({
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    })

    request_url = (
        base_url + endpoint + "?" + query
    )

    request = urllib.request.Request(
        url=request_url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent":
                "Fresh-WEEX-Reconstruction/Unit4",
            "Cache-Control": "no-cache",
        },
    )

    if request.get_method() != "GET":
        raise RuntimeError(
            "UNIT 4 NON-GET REQUEST"
        )

    if request.data is not None:
        raise RuntimeError(
            "UNIT 4 REQUEST BODY NOT ALLOWED"
        )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            status = response.getcode()

            raw_body = (
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            "UNIT 4 HTTP ERROR: "
            + str(exc.code)
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            "UNIT 4 CONNECTION ERROR"
        ) from exc

    if status != 200:
        raise RuntimeError(
            "UNIT 4 INVALID HTTP STATUS"
        )

    try:
        raw_klines = json.loads(raw_body)
    except (ValueError, TypeError) as exc:
        raise RuntimeError(
            "UNIT 4 INVALID KLINE JSON"
        ) from exc

    if not isinstance(raw_klines, list):
        raise RuntimeError(
            "UNIT 4 KLINES NOT A LIST"
        )

    if len(raw_klines) < 201:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT KLINES"
        )

    # ========================================================
    # 5. NORMALIZE CANDLES
    # INDENTATION: 4 SPACES
    # ========================================================

    candles = []

    for item in raw_klines:

        if not isinstance(item, (list, tuple)):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE FORMAT"
            )

        if len(item) < 7:
            raise RuntimeError(
                "UNIT 4 INCOMPLETE CANDLE"
            )

        try:

            candle = {
                "open_time_ms": int(item[0]),
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4]),
                "volume": float(item[5]),
                "close_time_ms": int(item[6]),
            }

        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE VALUES"
            ) from exc

        prices = (
            candle["open"],
            candle["high"],
            candle["low"],
            candle["close"],
        )

        if not all(
            math.isfinite(x) and x > 0
            for x in prices
        ):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE PRICE"
            )

        if not math.isfinite(candle["volume"]):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE VOLUME"
            )

        if candle["volume"] < 0:
            raise RuntimeError(
                "UNIT 4 NEGATIVE CANDLE VOLUME"
            )

        if candle["high"] < max(
            candle["open"],
            candle["close"],
            candle["low"],
        ):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE HIGH"
            )

        if candle["low"] > min(
            candle["open"],
            candle["close"],
            candle["high"],
        ):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE LOW"
            )

        if (
            candle["open_time_ms"] <= 0
            or candle["close_time_ms"]
            <= candle["open_time_ms"]
        ):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE TIMESTAMPS"
            )

        candles.append(candle)

    candles.sort(
        key=lambda x: x["open_time_ms"]
    )

    for index in range(1, len(candles)):

        if (
            candles[index]["open_time_ms"]
            <= candles[index - 1]["open_time_ms"]
        ):
            raise RuntimeError(
                "UNIT 4 DUPLICATE CANDLE TIMESTAMP"
            )

    # ========================================================
    # 6. CLOSED-CANDLE FILTER
    # INDENTATION: 4 SPACES
    # ========================================================

    closed = [
        candle
        for candle in candles
        if candle["close_time_ms"] <= exchange_time_ms
    ]

    if len(closed) < 200:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT CLOSED CANDLES"
        )

    latest = closed[-1]
    previous = closed[-2]

    latest_close = latest["close"]
    previous_close = previous["close"]

    if exchange_time_ms - latest["close_time_ms"] > 120000:
        raise RuntimeError(
            "UNIT 4 STALE CLOSED CANDLE DATA"
        )

    newest_returned_is_closed = (
        candles[-1]["close_time_ms"]
        <= exchange_time_ms
    )

    close_prices = [
        candle["close"]
        for candle in closed
    ]

    # ========================================================
    # 7. EMA CALCULATIONS
    # INDENTATION: 4 SPACES
    # ========================================================

    ema19 = fresh_unit_4_calculate_ema(
        close_prices, 19
    )

    ema50 = fresh_unit_4_calculate_ema(
        close_prices, 50
    )

    ema100 = fresh_unit_4_calculate_ema(
        close_prices, 100
    )

    ema200 = fresh_unit_4_calculate_ema(
        close_prices, 200
    )

    separation = (
        abs(ema19 - ema50)
        / ema50
        * 100.0
    )

    if ema19 > ema50 > ema200:
        ema_structure = "BULLISH"

    elif ema19 < ema50 < ema200:
        ema_structure = "BEARISH"

    else:
        ema_structure = "MIXED"

    if ema19 > ema50 > ema100:
        scalp_ema_context = "BULLISH"

    elif ema19 < ema50 < ema100:
        scalp_ema_context = "BEARISH"

    else:
        scalp_ema_context = "MIXED"

    # ========================================================
    # 8. MULTI-WINDOW CLOSED-CANDLE MOMENTUM
    # INDENTATION: 4 SPACES
    # ========================================================

    window_moves = {}

    for minutes in (1, 5, 15, 30, 60, 120):

        if len(close_prices) <= minutes:
            raise RuntimeError(
                "UNIT 4 INSUFFICIENT WINDOW DATA"
            )

        reference = close_prices[-(minutes + 1)]

        movement = (
            (latest_close - reference)
            / reference
            * 100.0
        )

        window_moves[minutes] = movement

    short_term_move = window_moves[1]

    # ========================================================
    # 9. RECENT SUPPORT AND RESISTANCE
    # INDENTATION: 4 SPACES
    # ========================================================

    recent_10 = closed[-10:]
    recent_20 = closed[-20:]

    resistance_10 = max(
        candle["high"]
        for candle in recent_10
    )

    support_10 = min(
        candle["low"]
        for candle in recent_10
    )

    resistance_20 = max(
        candle["high"]
        for candle in recent_20
    )

    support_20 = min(
        candle["low"]
        for candle in recent_20
    )

    range_10 = (
        resistance_10 - support_10
    )

    range_20 = (
        resistance_20 - support_20
    )

    range_position_20 = (
        (live_mark - support_20)
        / range_20
        * 100.0
        if range_20 > 0
        else 50.0
    )

    # Values outside 0-100% are intentionally retained.
    # They indicate price outside the closed-candle range.

    # ========================================================
    # 10. CANDLE PRICE-ACTION MEASUREMENTS
    # INDENTATION: 4 SPACES
    # ========================================================

    candle_range = (
        latest["high"] - latest["low"]
    )

    candle_body = abs(
        latest["close"] - latest["open"]
    )

    upper_wick = (
        latest["high"]
        - max(latest["open"], latest["close"])
    )

    lower_wick = (
        min(latest["open"], latest["close"])
        - latest["low"]
    )

    body_ratio = (
        candle_body / candle_range
        if candle_range > 0
        else 0.0
    )

    if latest["close"] > latest["open"]:
        candle_direction = "BULLISH"

    elif latest["close"] < latest["open"]:
        candle_direction = "BEARISH"

    else:
        candle_direction = "NEUTRAL"

    # ========================================================
    # 11. VOLATILITY / ATR-STYLE MEASURE
    # INDENTATION: 4 SPACES
    # ========================================================

    true_ranges = []

    for index in range(-14, 0):

        current = closed[index]
        prior = closed[index - 1]

        true_range = max(
            current["high"] - current["low"],
            abs(current["high"] - prior["close"]),
            abs(current["low"] - prior["close"]),
        )

        true_ranges.append(true_range)

    atr14 = (
        sum(true_ranges)
        / len(true_ranges)
    )

    atr14_percent = (
        atr14 / latest_close * 100.0
    )

    # ========================================================
    # 12. LIVE PRICE CONTEXT
    # INDENTATION: 4 SPACES
    # ========================================================

    live_vs_close_pct = (
        (live_mark - latest_close)
        / latest_close
        * 100.0
    )

    live_vs_ema19_pct = (
        (live_mark - ema19)
        / ema19
        * 100.0
    )

    live_vs_ema50_pct = (
        (live_mark - ema50)
        / ema50
        * 100.0
    )

    # ========================================================
    # 13. NORMALIZED ANALYSIS SNAPSHOT
    # INDENTATION: 4 SPACES
    #
    # Existing fields remain available to Unit 5.
    # New fields support subsequent scoring improvements.
    # ========================================================

    analysis_snapshot = {

        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": symbol,
        "interval": interval,
        "price_type": "MARK",

        "live_mark_price": live_mark,

        "previous_close": previous_close,
        "latest_close": latest_close,

        "latest_open_time_ms":
            latest["open_time_ms"],

        "latest_close_time_ms":
            latest["close_time_ms"],

        "exchange_time_ms": exchange_time_ms,

        "ema19": ema19,
        "ema50": ema50,
        "ema100": ema100,
        "ema200": ema200,

        "ema19_50_separation_pct": separation,
        "ema_structure": ema_structure,
        "scalp_ema_context": scalp_ema_context,

        "short_term_move_pct": short_term_move,

        "move_1m_pct": window_moves[1],
        "move_5m_pct": window_moves[5],
        "move_15m_pct": window_moves[15],
        "move_30m_pct": window_moves[30],
        "move_60m_pct": window_moves[60],
        "move_120m_pct": window_moves[120],

        "support_10": support_10,
        "resistance_10": resistance_10,
        "support_20": support_20,
        "resistance_20": resistance_20,

        "range_10": range_10,
        "range_20": range_20,
        "range_position_20_pct": range_position_20,

        "latest_candle_direction":
            candle_direction,

        "latest_candle_body_ratio":
            body_ratio,

        "latest_upper_wick": upper_wick,
        "latest_lower_wick": lower_wick,

        "atr14": atr14,
        "atr14_percent": atr14_percent,

        "live_vs_close_pct":
            live_vs_close_pct,

        "live_vs_ema19_pct":
            live_vs_ema19_pct,

        "live_vs_ema50_pct":
            live_vs_ema50_pct,

        "recent_closed_klines": [
            dict(candle)
            for candle in closed[-60:]
        ],

        "candle_count": len(candles),
        "closed_candle_count": len(closed),

        "newest_returned_candle_closed":
            newest_returned_is_closed,

        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",

        "read_only": True,

        "market_refresh_completed": True,
        "analysis_refresh_completed": True,
        "continuous_scan_configured":
            strategy.get(
                "continuous_entry_scan_enabled",
                False,
            ),
    }

    # ========================================================
    # 14. FINAL VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    required_fields = (
        "symbol",
        "live_mark_price",
        "ema19",
        "ema50",
        "ema100",
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
        "recent_closed_klines",
        "read_only",
    )

    missing = [
        key
        for key in required_fields
        if key not in analysis_snapshot
    ]

    if missing:
        raise RuntimeError(
            "UNIT 4 MISSING OUTPUT FIELDS: "
            + str(missing)
        )

    if analysis_snapshot["read_only"] is not True:
        raise RuntimeError(
            "UNIT 4 READ-ONLY VALIDATION FAILED"
        )

    if (
        analysis_snapshot["latest_close_time_ms"]
        > exchange_time_ms
    ):
        raise RuntimeError(
            "UNIT 4 UNFINISHED CANDLE DETECTED"
        )

    if abs(
        analysis_snapshot["move_1m_pct"]
        - analysis_snapshot["short_term_move_pct"]
    ) > 0.000000001:
        raise RuntimeError(
            "UNIT 4 MOMENTUM CONTRACT MISMATCH"
        )

    # ========================================================
    # 15. RENDER LOGGING
    # INDENTATION: 4 SPACES
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "PASS: UNIT 4 LIVE MARKET ANALYSIS",
        flush=True,
    )

    print(
        "UNIT 4 LIVE BTC PRICE =",
        live_mark,
        flush=True,
    )

    print(
        "UNIT 4 EMA19 =",
        round(ema19, 4),
        flush=True,
    )

    print(
        "UNIT 4 EMA50 =",
        round(ema50, 4),
        flush=True,
    )

    print(
        "UNIT 4 EMA100 =",
        round(ema100, 4),
        flush=True,
    )

    print(
        "UNIT 4 EMA200 =",
        round(ema200, 4),
        flush=True,
    )

    print(
        "UNIT 4 EMA STRUCTURE =",
        ema_structure,
        flush=True,
    )

    print(
        "UNIT 4 SCALP EMA CONTEXT =",
        scalp_ema_context,
        flush=True,
    )

    print(
        "UNIT 4 EMA19/50 SEPARATION % =",
        round(separation, 6),
        flush=True,
    )

    for minutes in (1, 5, 15, 30, 60, 120):
        print(
            "UNIT 4",
            str(minutes) + "M MOVE % =",
            round(window_moves[minutes], 6),
            flush=True,
        )

    print(
        "UNIT 4 SUPPORT 20 =",
        support_20,
        flush=True,
    )

    print(
        "UNIT 4 RESISTANCE 20 =",
        resistance_20,
        flush=True,
    )

    print(
        "UNIT 4 RANGE POSITION % =",
        round(range_position_20, 4),
        flush=True,
    )

    print(
        "UNIT 4 ATR14 % =",
        round(atr14_percent, 6),
        flush=True,
    )

    print(
        "UNIT 4 CLOSED CANDLES =",
        len(closed),
        flush=True,
    )

    print(
        "UNIT 4 NEWEST RETURNED CANDLE CLOSED =",
        newest_returned_is_closed,
        flush=True,
    )

    print(
        "PASS: UNIT 4 PRICE ACTION INPUTS READY",
        flush=True,
    )

    print(
        "PASS: UNIT 4 UNIT 5 CONTRACT PRESERVED",
        flush=True,
    )

    print(
        "PASS: UNIT 4 REUSABLE ANALYSIS READY",
        flush=True,
    )

    print(
        "ZERO AUTHENTICATED API ACCESS = TRUE",
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
        "FRESH RECONSTRUCTION UNIT 4 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return analysis_snapshot


# ============================================================
# RUN UNIT 4 INITIAL ANALYSIS
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)


# ============================================================
# UNIT 4 REUSABLE REFRESH
# ZERO INDENTATION
#
# To be called by the forthcoming runtime controller.
# Unit 3 must refresh first.
# ============================================================

def fresh_reconstruction_refresh_unit_4(
    market_snapshot=None
):

    global FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT

    if market_snapshot is None:
        market_snapshot = (
            FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
        )

    refreshed_analysis = (
        fresh_reconstruction_unit_4(
            market_snapshot=market_snapshot
        )
    )

    FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
        refreshed_analysis
    )

    return refreshed_analysis


# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 4
# ZERO INDENTATION DEMARCATION
#
# UNIT 4 FULLY CLOSED
# INITIAL ANALYSIS CREATED
# REUSABLE REFRESH FUNCTION CREATED
# EMA19 / EMA50 / EMA100 / EMA200 INCLUDED
# PRICE ACTION INPUTS INCLUDED
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN LOOP
# NO OPEN TRY
#
# EXISTING UNIT 5 CONTINUES BELOW
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 5
# ZERO INDENTATION DEMARCATION
# ============================================================
#
# PRICE-LED MULTI-MODE QUALIFICATION ENGINE
#
# SCALP:
# PRICE ACTION                 50%
# EMA CONTEXT                  15%
# MOMENTUM                     15%
# SUPPORT / RESISTANCE         10%
# VOLATILITY / TIMING          10%
#
# QUALITY THRESHOLD = 70 / 100
#
# MODE PRIORITY:
# BREAKOUT -> STRUCTURE -> SCALP
#
# PRESERVED:
# - One exclusive active mode
# - EMA19 / EMA50 / EMA200
# - EMA100 scalp context
# - 1M / 5M / 15M / 30M momentum
# - Zero exchange writes
#
# THIS UNIT DOES NOT SUBMIT ORDERS.
# ============================================================

import math
from datetime import datetime, timezone


# ============================================================
# UNIT 5 HELPER FUNCTIONS
# ZERO INDENTATION
# ============================================================

def fresh_unit_5_direction(value, deadband=0.0):

    if value > deadband:
        return "LONG"

    if value < -deadband:
        return "SHORT"

    return "NONE"


def fresh_unit_5_clamp(value, minimum, maximum):

    return max(
        minimum,
        min(maximum, value)
    )


def fresh_unit_5_fraction(value):

    return fresh_unit_5_clamp(
        value, 0.0, 1.0
    )


# ============================================================
# UNIT 5 MAIN QUALIFICATION ENGINE
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_5(
    unit_2_config,
    unit_4_snapshot,
):

    print("=" * 80, flush=True)

    print(
        datetime.now(timezone.utc).isoformat(),
        "FRESH RECONSTRUCTION UNIT 5 START",
        flush=True,
    )

    # ========================================================
    # 1. VALIDATE INPUTS
    # INDENTATION: 4 SPACES
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 5 INVALID CONFIGURATION"
        )

    if not isinstance(unit_4_snapshot, dict):
        raise RuntimeError(
            "UNIT 5 INVALID ANALYSIS SNAPSHOT"
        )

    strategy = unit_2_config.get("strategy", {})

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 5 STRATEGY MISSING"
        )

    if unit_4_snapshot.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 5 ANALYSIS NOT READ ONLY"
        )

    if unit_4_snapshot.get("symbol") != "BTCUSDT":
        raise RuntimeError(
            "UNIT 5 SYMBOL MISMATCH"
        )

    if strategy.get(
        "real_money_execution_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 5 REAL EXECUTION NOT BLOCKED"
        )

    # ========================================================
    # 2. READ MARKET VALUES
    # INDENTATION: 4 SPACES
    # ========================================================

    required_numeric = (
        "live_mark_price",
        "ema19",
        "ema50",
        "ema100",
        "ema200",
        "ema19_50_separation_pct",
        "previous_close",
        "latest_close",
        "short_term_move_pct",
        "move_1m_pct",
        "move_5m_pct",
        "move_15m_pct",
        "move_30m_pct",
        "move_60m_pct",
        "move_120m_pct",
        "support_20",
        "resistance_20",
        "atr14_percent",
        "latest_candle_body_ratio",
    )

    data = {}

    for key in required_numeric:

        try:
            value = float(unit_4_snapshot[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError(
                "UNIT 5 INVALID MARKET FIELD: " + key
            ) from exc

        if not math.isfinite(value):
            raise RuntimeError(
                "UNIT 5 NON-FINITE FIELD: " + key
            )

        data[key] = value

    price = data["live_mark_price"]
    ema19 = data["ema19"]
    ema50 = data["ema50"]
    ema100 = data["ema100"]
    ema200 = data["ema200"]

    separation = abs(
        data["ema19_50_separation_pct"]
    )

    previous_close = data["previous_close"]
    latest_close = data["latest_close"]

    move_1m = data["move_1m_pct"]
    move_5m = data["move_5m_pct"]
    move_15m = data["move_15m_pct"]
    move_30m = data["move_30m_pct"]
    move_60m = data["move_60m_pct"]
    move_120m = data["move_120m_pct"]

    support = data["support_20"]
    resistance = data["resistance_20"]
    atr_pct = data["atr14_percent"]
    body_ratio = data["latest_candle_body_ratio"]

    if any(
        value <= 0
        for value in (
            price, ema19, ema50, ema100,
            ema200, previous_close, latest_close
        )
    ):
        raise RuntimeError(
            "UNIT 5 INVALID NON-POSITIVE PRICE"
        )

    if not (0 <= body_ratio <= 1):
        raise RuntimeError(
            "UNIT 5 INVALID BODY RATIO"
        )

    if support <= 0 or resistance <= support:
        raise RuntimeError(
            "UNIT 5 INVALID MARKET RANGE"
        )

    if atr_pct < 0:
        raise RuntimeError(
            "UNIT 5 INVALID ATR"
        )

    # ========================================================
    # 3. VERIFY SCORING CONFIGURATION
    # INDENTATION: 4 SPACES
    # ========================================================

    weights = {
        "price": float(
            strategy["scalp_price_weight"]
        ),
        "ema": float(
            strategy["scalp_ema_weight"]
        ),
        "momentum": float(
            strategy["scalp_momentum_weight"]
        ),
        "structure": float(
            strategy["scalp_structure_weight"]
        ),
        "timing": float(
            strategy["scalp_volatility_timing_weight"]
        ),
    }

    if abs(sum(weights.values()) - 100) > 0.000001:
        raise RuntimeError(
            "UNIT 5 INVALID SCALP WEIGHTS"
        )

    if weights != {
        "price": 50.0,
        "ema": 15.0,
        "momentum": 15.0,
        "structure": 10.0,
        "timing": 10.0,
    }:
        raise RuntimeError(
            "UNIT 5 SCALP WEIGHT CONTRACT MISMATCH"
        )

    threshold = float(
        strategy["scalp_quality_threshold"]
    )

    if not (0 < threshold <= 100):
        raise RuntimeError(
            "UNIT 5 INVALID QUALITY THRESHOLD"
        )

    # ========================================================
    # 4. DIRECTIONAL CONTEXT
    # INDENTATION: 4 SPACES
    # ========================================================

    ema_structure = (
        unit_4_snapshot["ema_structure"]
    )

    ema_direction = "NONE"

    if ema19 > ema50 > ema200:
        ema_direction = "LONG"

    elif ema19 < ema50 < ema200:
        ema_direction = "SHORT"

    momentum_1m = fresh_unit_5_direction(move_1m)
    momentum_5m = fresh_unit_5_direction(move_5m)
    momentum_15m = fresh_unit_5_direction(move_15m)
    momentum_30m = fresh_unit_5_direction(move_30m)
    momentum_60m = fresh_unit_5_direction(move_60m)
    momentum_120m = fresh_unit_5_direction(move_120m)

    # ========================================================
    # 5. SCALP DIRECTION CANDIDATES
    # INDENTATION: 4 SPACES
    #
    # Score both directions independently.
    # This does not automatically force EMA agreement.
    # ========================================================

    scalp_scores = {}
    scalp_components = {}

    recent = unit_4_snapshot.get(
        "recent_closed_klines"
    )

    if not isinstance(recent, list) or len(recent) < 20:
        raise RuntimeError(
            "UNIT 5 CLOSED-CANDLE HISTORY MISSING"
        )

    for candle in recent[-20:]:

        if not isinstance(candle, dict):
            raise RuntimeError(
                "UNIT 5 INVALID CANDLE HISTORY"
            )

    # ========================================================
    # 6. CALCULATE DIRECTIONAL SCORES
    # INDENTATION: 4 SPACES
    # ========================================================

    for side in ("LONG", "SHORT"):

        sign = 1 if side == "LONG" else -1

        directional_1m = sign * move_1m
        directional_5m = sign * move_5m
        directional_15m = sign * move_15m

        directional_candle = (
            sign * (latest_close - previous_close)
            / previous_close
            * 100.0
        )

        # ----------------------------------------------------
        # PRICE ACTION - MAXIMUM 50 POINTS
        # ----------------------------------------------------

        recent_high = max(
            float(c["high"])
            for c in recent[-5:]
        )

        recent_low = min(
            float(c["low"])
            for c in recent[-5:]
        )

        recent_range = max(
            recent_high - recent_low,
            0.00000001,
        )

        position = fresh_unit_5_fraction(
            (price - recent_low) / recent_range
        )

        directional_position = (
            position
            if side == "LONG"
            else 1.0 - position
        )

        price_parts = {
            "five_minute_move":
                15.0 * fresh_unit_5_fraction(
                    directional_5m / 0.08
                ),

            "one_minute_move":
                10.0 * fresh_unit_5_fraction(
                    directional_1m / 0.035
                ),

            "closed_candle_direction":
                10.0 * fresh_unit_5_fraction(
                    directional_candle / 0.04
                ),

            "candle_body":
                5.0 * body_ratio
                if directional_candle > 0
                else 0.0,

            "recent_range_position":
                10.0 * directional_position,
        }

        price_score = sum(price_parts.values())

        # ----------------------------------------------------
        # EMA CONTEXT - MAXIMUM 15 POINTS
        # ----------------------------------------------------

        favorable_ema19 = (
            sign * (price - ema19) > 0
        )

        favorable_ema50 = (
            sign * (ema19 - ema50) > 0
        )

        favorable_ema100 = (
            sign * (ema50 - ema100) > 0
        )

        ema_score = (
            (5.0 if favorable_ema19 else 0.0)
            + (5.0 if favorable_ema50 else 0.0)
            + (3.0 if favorable_ema100 else 0.0)
            + (
                2.0 * fresh_unit_5_fraction(
                    separation / 0.03
                )
                if favorable_ema50
                else 0.0
            )
        )

        # ----------------------------------------------------
        # MOMENTUM - MAXIMUM 15 POINTS
        # ----------------------------------------------------

        momentum_score = (
            (6.0 if directional_5m > 0 else 0.0)
            + (5.0 if directional_15m > 0 else 0.0)
            + (4.0 if directional_1m > 0 else 0.0)
        )

        # ----------------------------------------------------
        # SUPPORT / RESISTANCE - MAXIMUM 10 POINTS
        # ----------------------------------------------------

        market_range = resistance - support

        distance_to_target = (
            resistance - price
            if side == "LONG"
            else price - support
        )

        available_room = fresh_unit_5_fraction(
            distance_to_target / market_range
        )

        structure_score = (
            10.0 * available_room
        )

        # ----------------------------------------------------
        # VOLATILITY / TIMING - MAXIMUM 10 POINTS
        #
        # Excessive extension is penalized.
        # Very low volatility earns fewer points.
        # ----------------------------------------------------

        ema_extension = (
            abs(price - ema19)
            / ema19
            * 100.0
        )

        extension_limit = max(
            1.5 * atr_pct,
            0.02,
        )

        extension_factor = fresh_unit_5_fraction(
            1.0 - ema_extension / extension_limit
        )

        volatility_factor = fresh_unit_5_fraction(
            atr_pct / 0.08
        )

        timing_score = (
            6.0 * extension_factor
            + 4.0 * volatility_factor
        )

        components = {
            "price_action": round(price_score, 4),
            "ema": round(ema_score, 4),
            "momentum": round(momentum_score, 4),
            "structure": round(structure_score, 4),
            "volatility_timing": round(timing_score, 4),
        }

        total_score = sum(components.values())

        scalp_scores[side] = round(
            total_score, 4
        )

        scalp_components[side] = components

    # ========================================================
    # 7. SELECT SCALP CANDIDATE
    # INDENTATION: 4 SPACES
    # ========================================================

    long_score = scalp_scores["LONG"]
    short_score = scalp_scores["SHORT"]

    scalp_direction = "NONE"
    scalp_score = max(long_score, short_score)

    best_side = (
        "LONG"
        if long_score > short_score
        else "SHORT"
    )

    # Avoid arbitrary selection on a tied score.
    score_difference = abs(
        long_score - short_score
    )

    if (
        scalp_score >= threshold
        and score_difference >= 5.0
    ):
        # Some actual directional movement is necessary.
        side_sign = (
            1 if best_side == "LONG" else -1
        )

        if (
            side_sign * move_5m > 0
            and side_sign * move_1m >= 0
        ):
            scalp_direction = best_side

    scalp_move_pct = abs(move_5m)

    scalp_1m_support = (
        scalp_direction != "NONE"
        and momentum_1m == scalp_direction
    )

    # ========================================================
    # 8. STRUCTURE QUALIFICATION
    # INDENTATION: 4 SPACES
    #
    # Preserve original minimum thresholds.
    # ========================================================

    structure_direction = "NONE"
    structure_move_pct = abs(move_15m)

    structure_direction_agreement = (
        ema_direction != "NONE"
        and momentum_15m == ema_direction
    )

    if (
        structure_direction_agreement
        and separation >= 0.070
        and structure_move_pct >= 0.040
    ):
        structure_direction = ema_direction

    # ========================================================
    # 9. BREAKOUT QUALIFICATION
    # INDENTATION: 4 SPACES
    # ========================================================

    breakout_direction = "NONE"
    breakout_move_pct = abs(move_30m)

    breakout_fast_support = (
        momentum_30m != "NONE"
        and momentum_5m == momentum_30m
        and momentum_15m == momentum_30m
    )

    breakout_long = (
        momentum_30m == "LONG"
        and breakout_fast_support
        and ema19 > ema50
        and price > ema19
        and price > ema200
    )

    breakout_short = (
        momentum_30m == "SHORT"
        and breakout_fast_support
        and ema19 < ema50
        and price < ema19
        and price < ema200
    )

    if (
        separation >= 0.120
        and breakout_move_pct >= 0.080
    ):

        if breakout_long:
            breakout_direction = "LONG"

        elif breakout_short:
            breakout_direction = "SHORT"

    # ========================================================
    # 10. EXCLUSIVE MODE SELECTION
    # INDENTATION: 4 SPACES
    # ========================================================

    active_mode = "NONE"
    direction = "NONE"
    qualified = False

    qualification_reason = (
        "NO_MODE_QUALIFIED"
    )

    if (
        breakout_direction != "NONE"
        and strategy.get(
            "breakout_mode_enabled"
        ) is True
    ):

        active_mode = "BREAKOUT"
        direction = breakout_direction
        qualified = True

        qualification_reason = (
            "BREAKOUT_QUALIFIED"
        )

    elif (
        structure_direction != "NONE"
        and strategy.get(
            "structure_mode_enabled"
        ) is True
    ):

        active_mode = "STRUCTURE"
        direction = structure_direction
        qualified = True

        qualification_reason = (
            "STRUCTURE_QUALIFIED"
        )

    elif (
        scalp_direction != "NONE"
        and strategy.get(
            "scalp_mode_enabled"
        ) is True
    ):

        active_mode = "SCALP"
        direction = scalp_direction
        qualified = True

        qualification_reason = (
            "SCALP_PRICE_LED_SCORE_QUALIFIED"
        )

    else:

        if score_difference < 5.0:
            qualification_reason = (
                "SCALP_DIRECTION_AMBIGUOUS"
            )

        elif scalp_score < threshold:
            qualification_reason = (
                "SCALP_QUALITY_BELOW_THRESHOLD"
            )

        else:
            qualification_reason = (
                "DIRECTIONAL_MOMENTUM_NOT_CONFIRMED"
            )

    # ========================================================
    # 11. PREPARE DOWNSTREAM COMPATIBILITY
    # INDENTATION: 4 SPACES
    # ========================================================

    price_above_ema19 = price > ema19
    price_above_ema50 = price > ema50
    price_above_ema200 = price > ema200

    latest_close_above_previous = (
        latest_close > previous_close
    )

    signal_candidate = {

        # ORIGINAL UNIT 6 CONTRACT
        "symbol": "BTCUSDT",
        "qualified": qualified,
        "active_mode": active_mode,
        "direction": direction,
        "qualification_reason": qualification_reason,

        "live_mark_price": price,
        "ema19": ema19,
        "ema50": ema50,
        "ema100": ema100,
        "ema200": ema200,

        "ema19_50_separation_pct": separation,
        "ema_structure": ema_structure,
        "ema_direction": ema_direction,

        "momentum_direction": momentum_1m,

        "direction_agreement":
            structure_direction_agreement,

        "short_term_move_pct":
            data["short_term_move_pct"],

        "absolute_short_term_move_pct":
            abs(data["short_term_move_pct"]),

        "previous_close": previous_close,
        "latest_close": latest_close,

        "price_above_ema19": price_above_ema19,
        "price_above_ema50": price_above_ema50,
        "price_above_ema200": price_above_ema200,

        "latest_close_above_previous":
            latest_close_above_previous,

        "move_1m_pct": move_1m,
        "move_5m_pct": move_5m,
        "move_15m_pct": move_15m,
        "move_30m_pct": move_30m,
        "move_60m_pct": move_60m,
        "move_120m_pct": move_120m,

        "momentum_1m_direction": momentum_1m,
        "momentum_5m_direction": momentum_5m,
        "momentum_15m_direction": momentum_15m,
        "momentum_30m_direction": momentum_30m,
        "momentum_60m_direction": momentum_60m,
        "momentum_120m_direction": momentum_120m,

        "scalp_direction": scalp_direction,
        "scalp_move_pct": scalp_move_pct,
        "scalp_1m_support": scalp_1m_support,

        "structure_direction": structure_direction,
        "structure_move_pct": structure_move_pct,

        "breakout_direction": breakout_direction,
        "breakout_move_pct": breakout_move_pct,
        "breakout_fast_support": breakout_fast_support,

        # NEW QUALITY DIAGNOSTICS
        "scalp_quality_score": scalp_score,
        "scalp_quality_threshold": threshold,

        "scalp_long_score": long_score,
        "scalp_short_score": short_score,

        "scalp_score_components":
            scalp_components,

        "price_action_weight": 50.0,

        # FRESHNESS
        "exchange_time_ms":
            unit_4_snapshot.get(
                "exchange_time_ms"
            ),

        "latest_close_time_ms":
            unit_4_snapshot.get(
                "latest_close_time_ms"
            ),

        # EXECUTION SAFETY
        "read_only": True,
        "order_payload": None,
        "execution_intent": False,
    }

    # ========================================================
    # 12. RENDER STATUS LOGGING
    # INDENTATION: 4 SPACES
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "UNIT 5 LIVE BTC PRICE =",
        price,
        flush=True,
    )

    print(
        "UNIT 5 SCALP PRICE WEIGHT = 50%",
        flush=True,
    )

    print(
        "UNIT 5 SCALP QUALITY THRESHOLD =",
        threshold,
        flush=True,
    )

    print(
        "UNIT 5 SCALP LONG SCORE =",
        long_score,
        flush=True,
    )

    print(
        "UNIT 5 SCALP SHORT SCORE =",
        short_score,
        flush=True,
    )

    print(
        "UNIT 5 SCALP DIRECTION =",
        scalp_direction,
        flush=True,
    )

    print(
        "UNIT 5 SCALP COMPONENT SCORES =",
        scalp_components,
        flush=True,
    )

    print(
        "UNIT 5 EMA19/50 SEPARATION =",
        separation,
        flush=True,
    )

    print(
        "UNIT 5 EMA SEPARATION = WEIGHTED FOR SCALP",
        flush=True,
    )

    print(
        "UNIT 5 STRUCTURE DIRECTION =",
        structure_direction,
        flush=True,
    )

    print(
        "UNIT 5 BREAKOUT DIRECTION =",
        breakout_direction,
        flush=True,
    )

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
        "PASS: UNIT 5 NO NETWORK REQUEST",
        flush=True,
    )

    print(
        "PASS: UNIT 5 NO ORDER PAYLOAD",
        flush=True,
    )

    print(
        "ZERO AUTHENTICATED API ACCESS = TRUE",
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
        "FRESH RECONSTRUCTION UNIT 5 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return signal_candidate


# ============================================================
# RUN UNIT 5 INITIAL QUALIFICATION
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
    fresh_reconstruction_unit_5(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
    )
)


# ============================================================
# UNIT 5 REUSABLE REFRESH FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_refresh_unit_5(
    analysis_snapshot=None
):

    global FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE

    if analysis_snapshot is None:
        analysis_snapshot = (
            FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
        )

    refreshed_candidate = (
        fresh_reconstruction_unit_5(
            FRESH_RECONSTRUCTION_CONFIG,
            analysis_snapshot,
        )
    )

    FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
        refreshed_candidate
    )

    return refreshed_candidate


# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 5
# ZERO INDENTATION DEMARCATION
#
# UNIT 5 FULLY CLOSED
# INITIAL QUALIFICATION EXECUTED
# REUSABLE REFRESH FUNCTION CREATED
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN LOOP
# NO OPEN TRY
#
# EXISTING UNIT 6 CONTINUES DIRECTLY BELOW
# ============================================================

 
# ============================================================
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 6
# ZERO INDENTATION DEMARCATION
# ============================================================
#
# COORDINATED SIGNAL ADMISSION ENGINE
#
# FUNCTIONS:
# - Receive new Unit 5 price-led qualification
# - Preserve SCALP / STRUCTURE / BREAKOUT modes
# - Scalp price-action weight = 50%
# - Scalp quality threshold = 70/100
# - No conflicting second quality calculation
# - Three fresh-snapshot confirmations
# - Signal freshness validation
# - Directional persistence
# - Reusable refresh entry point
# - Stable Unit 7 execution candidate
#
# NO ACCOUNT ACCESS
# NO ORDER SUBMISSION
# NO EXCHANGE WRITE
# ============================================================

import math
import time


# ============================================================
# UNIT 6 SIGNAL CONFIRMATION STATE
# ZERO INDENTATION
# ============================================================

FRESH_UNIT_6_CONFIRMATION_STATE = {
    "mode": "NONE",
    "direction": "NONE",
    "count": 0,
    "last_snapshot_id": None,
}


# ============================================================
# UNIT 6 RESET FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_unit_6_reset_confirmations():

    state = FRESH_UNIT_6_CONFIRMATION_STATE

    state["mode"] = "NONE"
    state["direction"] = "NONE"
    state["count"] = 0
    state["last_snapshot_id"] = None


# ============================================================
# UNIT 6 MAIN ADMISSION FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_6(
    unit_2_config,
    unit_4_analysis,
    unit_5_candidate,
):

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 6 START")

    # ========================================================
    # 1. INPUT VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 6 CONFIGURATION MISSING"
        )

    if not isinstance(unit_4_analysis, dict):
        raise RuntimeError(
            "UNIT 6 ANALYSIS MISSING"
        )

    if not isinstance(unit_5_candidate, dict):
        raise RuntimeError(
            "UNIT 6 SIGNAL CANDIDATE MISSING"
        )

    strategy = unit_2_config.get("strategy")
    safety = unit_2_config.get("safety")

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 6 STRATEGY MISSING"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 6 SAFETY CONFIGURATION MISSING"
        )

    if (
        unit_4_analysis.get("read_only") is not True
        or unit_5_candidate.get("read_only") is not True
    ):
        raise RuntimeError(
            "UNIT 6 READ-ONLY CONTRACT FAILED"
        )

    if (
        unit_4_analysis.get("symbol") != "BTCUSDT"
        or unit_5_candidate.get("symbol") != "BTCUSDT"
    ):
        raise RuntimeError(
            "UNIT 6 MARKET SYMBOL MISMATCH"
        )

    # ========================================================
    # 2. STRICT EXECUTION SAFETY
    # INDENTATION: 4 SPACES
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

    for key in forbidden_capabilities:

        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 6 UNSAFE CAPABILITY: " + key
            )

    if strategy.get(
        "real_money_execution_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 6 REAL EXECUTION NOT BLOCKED"
        )

    for key in (
        "one_direction_only",
        "anti_duplicate_orders",
        "active_trade_mode_lock",
        "exclusive_mode",
        "require_fresh_reentry_signal",
    ):

        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 6 REQUIRED PROTECTION DISABLED: "
                + key
            )

    # ========================================================
    # 3. SIGNAL CONFIGURATION
    # INDENTATION: 4 SPACES
    # ========================================================

    leverage_target = float(
        strategy["leverage_target"]
    )

    quality_minimum = float(
        strategy["scalp_quality_threshold"]
    )

    confirmation_required = int(
        strategy["mode_confirmations_required"]
    )

    signal_expiry_ms = int(
        float(strategy["signal_expiry_seconds"])
        * 1000
    )

    if not (0 < quality_minimum <= 100):
        raise RuntimeError(
            "UNIT 6 INVALID QUALITY THRESHOLD"
        )

    if confirmation_required < 1:
        raise RuntimeError(
            "UNIT 6 INVALID CONFIRMATION COUNT"
        )

    if signal_expiry_ms <= 0:
        raise RuntimeError(
            "UNIT 6 INVALID SIGNAL EXPIRY"
        )

    # ========================================================
    # 4. UNIT 5 CANDIDATE
    # INDENTATION: 4 SPACES
    # ========================================================

    qualified = unit_5_candidate.get(
        "qualified"
    )

    active_mode = unit_5_candidate.get(
        "active_mode", "NONE"
    )

    direction = unit_5_candidate.get(
        "direction", "NONE"
    )

    qualification_reason = unit_5_candidate.get(
        "qualification_reason", "UNKNOWN"
    )

    if not isinstance(qualified, bool):
        raise RuntimeError(
            "UNIT 6 INVALID QUALIFICATION FLAG"
        )

    if active_mode not in (
        "NONE", "SCALP", "STRUCTURE", "BREAKOUT"
    ):
        raise RuntimeError(
            "UNIT 6 INVALID ACTIVE MODE"
        )

    if direction not in (
        "NONE", "LONG", "SHORT"
    ):
        raise RuntimeError(
            "UNIT 6 INVALID DIRECTION"
        )

    if qualified and (
        active_mode == "NONE"
        or direction == "NONE"
    ):
        raise RuntimeError(
            "UNIT 6 INCONSISTENT QUALIFIED SIGNAL"
        )

    # ========================================================
    # 5. SCALP QUALITY CONTRACT
    # INDENTATION: 4 SPACES
    # ========================================================

    scalp_quality_score = float(
        unit_5_candidate.get(
            "scalp_quality_score", 0.0
        )
    )

    if not math.isfinite(scalp_quality_score):
        raise RuntimeError(
            "UNIT 6 NON-FINITE SCALP SCORE"
        )

    if not 0 <= scalp_quality_score <= 100:
        raise RuntimeError(
            "UNIT 6 INVALID SCALP SCORE"
        )

    price_weight = float(
        unit_5_candidate.get(
            "price_action_weight", 0.0
        )
    )

    if price_weight != 50.0:
        raise RuntimeError(
            "UNIT 6 PRICE WEIGHT MUST BE 50%"
        )

    scalp_quality_pass = (
        scalp_quality_score >= quality_minimum
    )

    # Unit 5 already calculates the score.
    # Unit 6 does not recompute it.

    if active_mode == "SCALP":

        selected_score = float(
            unit_5_candidate.get(
                "scalp_long_score"
                if direction == "LONG"
                else "scalp_short_score",
                -1.0,
            )
        )

        if not math.isclose(
            selected_score,
            scalp_quality_score,
            abs_tol=0.0001,
        ):
            raise RuntimeError(
                "UNIT 6 SELECTED SCALP SCORE MISMATCH"
            )

    # ========================================================
    # 6. FRESH MARKET TIMESTAMP CONTRACT
    # INDENTATION: 4 SPACES
    # ========================================================

    market_time_ms = int(
        unit_4_analysis["exchange_time_ms"]
    )

    candidate_time_ms = int(
        unit_5_candidate["exchange_time_ms"]
    )

    if market_time_ms != candidate_time_ms:
        raise RuntimeError(
            "UNIT 6 CANDIDATE MARKET TIME MISMATCH"
        )

    latest_candle_ms = int(
        unit_4_analysis["latest_close_time_ms"]
    )

    candidate_candle_ms = int(
        unit_5_candidate["latest_close_time_ms"]
    )

    if latest_candle_ms != candidate_candle_ms:
        raise RuntimeError(
            "UNIT 6 CANDLE SNAPSHOT MISMATCH"
        )

    now_ms = int(time.time() * 1000)

    signal_age_ms = (
        now_ms - market_time_ms
    )

    signal_fresh = (
        -30000 <= signal_age_ms <= signal_expiry_ms
    )

    snapshot_id = (
        market_time_ms,
        latest_candle_ms,
    )

    # ========================================================
    # 7. CHECK ENTRY SIGNAL ADMISSIBILITY
    # INDENTATION: 4 SPACES
    # ========================================================

    signal_admissible = False

    admission_reason = (
        "UNIT_5_NOT_QUALIFIED:"
        + str(qualification_reason)
    )

    if not signal_fresh:

        admission_reason = (
            "SIGNAL_EXPIRED_OR_INVALID_TIMESTAMP"
        )

    elif not qualified:

        admission_reason = (
            "UNIT_5_NOT_QUALIFIED:"
            + str(qualification_reason)
        )

    elif (
        active_mode == "SCALP"
        and not scalp_quality_pass
    ):

        admission_reason = (
            "SCALP_QUALITY_BELOW_THRESHOLD"
        )

    else:

        signal_admissible = True

        admission_reason = (
            "SIGNAL_QUALITY_ACCEPTED"
        )

    # ========================================================
    # 8. CONTINUOUS CONFIRMATION CONTROL
    # INDENTATION: 4 SPACES
    #
    # One unchanged market snapshot cannot increase the
    # confirmation count multiple times.
    #
    # Three separate fresh snapshots are required.
    # ========================================================

    state = FRESH_UNIT_6_CONFIRMATION_STATE

    if not signal_admissible:

        fresh_unit_6_reset_confirmations()

    else:

        candidate_changed = (
            state["mode"] != active_mode
            or state["direction"] != direction
        )

        if candidate_changed:

            state["mode"] = active_mode
            state["direction"] = direction
            state["count"] = 0
            state["last_snapshot_id"] = None

        if state["last_snapshot_id"] != snapshot_id:

            state["count"] = min(
                confirmation_required,
                state["count"] + 1
            )

            state["last_snapshot_id"] = snapshot_id

    persistence_confirmations = state["count"]

    persistence_pass = (
        signal_admissible
        and persistence_confirmations
        >= confirmation_required
    )

    # ========================================================
    # 9. NORMALIZE DOWNSTREAM EXECUTION CANDIDATE
    # INDENTATION: 4 SPACES
    #
    # IDLE MUST BE REPRESENTED AS:
    # execution_intent = False
    # signal_qualified = False
    # active_mode = NONE
    # direction = NONE
    # ========================================================

    execution_intent = False

    normalized_signal_qualified = False
    normalized_active_mode = "NONE"
    normalized_direction = "NONE"

    if signal_admissible and not persistence_pass:

        admission_reason = (
            "AWAITING_FRESH_CONFIRMATIONS:"
            + str(persistence_confirmations)
            + "/"
            + str(confirmation_required)
        )

    elif signal_admissible and persistence_pass:

        execution_intent = True

        normalized_signal_qualified = True
        normalized_active_mode = active_mode
        normalized_direction = direction

        admission_reason = (
            "QUALIFIED_SIGNAL_ADMITTED"
        )

    # ========================================================
    # 10. SIGNAL IDENTIFIER
    # INDENTATION: 4 SPACES
    #
    # Diagnostic identity only.
    # Does not authorize duplicate submissions.
    # ========================================================

    signal_id = None

    if execution_intent:

        signal_id = (
            "BTCUSDT:"
            + active_mode
            + ":"
            + direction
            + ":"
            + str(latest_candle_ms)
        )

    # ========================================================
    # 11. COMPATIBILITY WITH UNIT 7
    # INDENTATION: 4 SPACES
    # ========================================================

    execution_candidate = {

        "execution_intent":
            bool(execution_intent),

        "active_mode":
            normalized_active_mode,

        "direction":
            normalized_direction,

        "signal_qualified":
            bool(normalized_signal_qualified),

        "unit_5_reason":
            qualification_reason,

        "admission_reason":
            admission_reason,

        "leverage_target":
            leverage_target,

        "leverage_regime":
            "HIGH_LEVERAGE"
            if leverage_target >= 50
            else "STANDARD",

        "sideways_regime": False,

        "ema_compressed":
            unit_4_analysis.get(
                "ema19_50_separation_pct", 0.0
            ) < 0.030,

        "compression_threshold_pct": 0.030,

        "momentum_conflict": False,

        "persistence_window":
            confirmation_required,

        "persistence_required":
            confirmation_required,

        "persistence_confirmations":
            persistence_confirmations,

        "persistence_directions":
            [state["direction"]]
            * persistence_confirmations
            if state["direction"] != "NONE"
            else [],

        "persistence_pass":
            bool(persistence_pass),

        "fifteen_minute_support_pass":
            unit_5_candidate.get(
                "momentum_15m_direction"
            ) == direction,

        "scalp_quality_score":
            scalp_quality_score,

        "scalp_quality_minimum":
            quality_minimum,

        "scalp_quality_pass":
            bool(scalp_quality_pass),

        "scalp_quality_details":
            unit_5_candidate.get(
                "scalp_score_components", {}
            ),

        "signal_id":
            signal_id,

        "signal_age_ms":
            signal_age_ms,

        "signal_fresh":
            signal_fresh,

        "price_action_weight": 50.0,

        "read_only": True,

        "order_payload": None,
    }

    # ========================================================
    # 12. RENDER LOGGING
    # INDENTATION: 4 SPACES
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "UNIT 6 PRICE ACTION WEIGHT = 50%",
        flush=True,
    )

    print(
        "UNIT 6 SCALP QUALITY SCORE =",
        scalp_quality_score,
        flush=True,
    )

    print(
        "UNIT 6 SCALP QUALITY THRESHOLD =",
        quality_minimum,
        flush=True,
    )

    print(
        "UNIT 6 SCALP QUALITY PASS =",
        scalp_quality_pass,
        flush=True,
    )

    print(
        "UNIT 6 SIGNAL AGE MS =",
        signal_age_ms,
        flush=True,
    )

    print(
        "UNIT 6 SIGNAL FRESH =",
        signal_fresh,
        flush=True,
    )

    print(
        "UNIT 6 CONFIRMATIONS =",
        persistence_confirmations,
        "/",
        confirmation_required,
        flush=True,
    )

    print(
        "UNIT 6 PERSISTENCE PASS =",
        persistence_pass,
        flush=True,
    )

    print(
        "UNIT 6 ACTIVE MODE =",
        normalized_active_mode,
        flush=True,
    )

    print(
        "UNIT 6 DIRECTION =",
        normalized_direction,
        flush=True,
    )

    print(
        "UNIT 6 SIGNAL QUALIFIED =",
        normalized_signal_qualified,
        flush=True,
    )

    print(
        "UNIT 6 EXECUTION INTENT =",
        execution_intent,
        flush=True,
    )

    print(
        "UNIT 6 ADMISSION REASON =",
        admission_reason,
        flush=True,
    )

    print(
        "UNIT 6 SIGNAL ID =",
        signal_id,
        flush=True,
    )

    print(
        "PASS: UNIT 6 NO NETWORK REQUEST",
        flush=True,
    )

    print(
        "PASS: UNIT 6 NO ORDER PAYLOAD",
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
        "FRESH RECONSTRUCTION UNIT 6 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return execution_candidate


# ============================================================
# RUN UNIT 6 INITIAL ADMISSION
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
# UNIT 6 REUSABLE REFRESH ENTRY POINT
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_refresh_unit_6(
    analysis_snapshot=None,
    signal_candidate=None,
):

    global FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE

    if analysis_snapshot is None:
        analysis_snapshot = (
            FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
        )

    if signal_candidate is None:
        signal_candidate = (
            FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
        )

    result = fresh_reconstruction_unit_6(
        FRESH_RECONSTRUCTION_CONFIG,
        analysis_snapshot,
        signal_candidate,
    )

    FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE = (
        result
    )

    return result


# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 6
# ZERO INDENTATION DEMARCATION
#
# UNIT 6 FULLY CLOSED
# UNIT 6 CALLED ONCE
# REFRESH FUNCTION CREATED
# UNIT 7 CONTRACT FIELDS PRESERVED
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN LOOP
# NO OPEN TRY
# NO OPEN DICTIONARY
#
# EXISTING UNIT 7 CONTINUES DIRECTLY BELOW
# ============================================================
 
# ============================================================
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 7
# ZERO INDENTATION DEMARCATION
# ============================================================
#
# COORDINATED ENTRY SIZING PREPARATION
#
# PURPOSE:
# - Receive refreshed Unit 6 candidate
# - Preserve normal IDLE state
# - Prepare qualified SCALP / STRUCTURE / BREAKOUT
# - Preserve initial margin protection
# - Preserve quantity precision requirements
# - Carry signal ID and market freshness downstream
# - Prepare protected flat-position re-entry
#
# NO ACCOUNT BALANCE INVENTED
# NO QUANTITY INVENTED
# NO ORDER PAYLOAD
# NO EXCHANGE REQUEST
# NO DEMO ORDER
# NO REAL ORDER
# ZERO EXCHANGE WRITE
# ============================================================

import math
import time


# ============================================================
# UNIT 7 MAIN FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_7(
    unit_2_config,
    unit_6_candidate,
):

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 7 START")

    # ========================================================
    # 1. INPUT CONFIGURATION
    # INDENTATION: 4 SPACES
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
    safety = unit_2_config.get("safety")
    exchange = unit_2_config.get("exchange")
    precision = unit_2_config.get("market_precision")

    for name, section in (
        ("STRATEGY", strategy),
        ("SAFETY", safety),
        ("EXCHANGE", exchange),
        ("PRECISION", precision),
    ):
        if not isinstance(section, dict):
            raise RuntimeError(
                "UNIT 7 MISSING SECTION: " + name
            )

    # ========================================================
    # 2. SAFETY GATE
    # INDENTATION: 4 SPACES
    # ========================================================

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 7 INVALID EXCHANGE"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 7 INVALID API VERSION"
        )

    if exchange.get("market_symbol") != "BTCUSDT":
        raise RuntimeError(
            "UNIT 7 INVALID MARKET SYMBOL"
        )

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 7 INVALID DEMO SYMBOL"
        )

    if unit_2_config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 7 INVALID EXECUTION ENVIRONMENT"
        )

    if unit_6_candidate.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 7 UNIT 6 NOT READ ONLY"
        )

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

    if strategy.get(
        "real_money_execution_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 7 REAL EXECUTION NOT DISABLED"
        )

    for key in (
        "anti_duplicate_orders",
        "one_direction_only",
        "active_trade_mode_lock",
        "exclusive_mode",
        "require_confirmed_flat_position",
        "require_no_pending_entry_orders",
        "require_exchange_state_reconciliation",
        "require_fresh_reentry_signal",
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 7 PROTECTION DISABLED: " + key
            )

    # ========================================================
    # 3. POSITION SIZE CONFIGURATION
    # INDENTATION: 4 SPACES
    # ========================================================

    margin_percent = float(
        strategy["initial_margin_percent"]
    )

    backup_margin_percent = float(
        strategy["backup_margin_percent"]
    )

    max_backups = int(
        strategy["max_backups"]
    )

    exposure_cap_percent = float(
        strategy["exposure_cap_percent"]
    )

    leverage_target = float(
        strategy["leverage_target"]
    )

    quantity_step = float(
        precision["quantity_step"]
    )

    minimum_quantity = float(
        precision["minimum_quantity"]
    )

    price_step = float(
        precision["price_step"]
    )

    size_values = (
        margin_percent,
        backup_margin_percent,
        exposure_cap_percent,
        leverage_target,
        quantity_step,
        minimum_quantity,
        price_step,
    )

    if not all(
        math.isfinite(value) and value > 0
        for value in size_values
    ):
        raise RuntimeError(
            "UNIT 7 INVALID SIZING PARAMETERS"
        )

    if margin_percent > 5.0:
        raise RuntimeError(
            "UNIT 7 INITIAL MARGIN EXCEEDS 5%"
        )

    if backup_margin_percent > 5.0:
        raise RuntimeError(
            "UNIT 7 BACKUP MARGIN EXCEEDS 5%"
        )

    if max_backups != 3:
        raise RuntimeError(
            "UNIT 7 INVALID MAX BACKUPS"
        )

    if exposure_cap_percent > 35.0:
        raise RuntimeError(
            "UNIT 7 EXPOSURE CAP EXCEEDS 35%"
        )

    staged_margin = (
        margin_percent
        + max_backups * backup_margin_percent
    )

    if staged_margin > exposure_cap_percent:
        raise RuntimeError(
            "UNIT 7 STAGED MARGIN EXCEEDS CAP"
        )

    # ========================================================
    # 4. UNIT 6 SIGNAL CONTRACT
    # INDENTATION: 4 SPACES
    # ========================================================

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
            "UNIT 7 MISSING SIGNAL FIELDS: "
            + str(missing)
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
            "UNIT 7 INVALID EXECUTION INTENT"
        )

    if not isinstance(signal_qualified, bool):
        raise RuntimeError(
            "UNIT 7 INVALID SIGNAL QUALIFICATION"
        )

    if execution_intent != signal_qualified:
        raise RuntimeError(
            "UNIT 7 SIGNAL STATE CONFLICT"
        )

    # ========================================================
    # 5. CREATE SHARED DOWNSTREAM CONTRACT
    # INDENTATION: 4 SPACES
    # ========================================================

    sizing_candidate = {
        "status": "IDLE",
        "symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",

        "active_mode": "NONE",
        "direction": "NONE",

        "execution_intent": False,
        "signal_qualified": False,

        "unit_5_reason": unit_5_reason,
        "admission_reason": admission_reason,

        "initial_margin_percent":
            margin_percent,

        "backup_margin_percent":
            backup_margin_percent,

        "max_backups": max_backups,

        "exposure_cap_percent":
            exposure_cap_percent,

        "leverage_target": leverage_target,

        "quantity_step": quantity_step,
        "minimum_quantity": minimum_quantity,
        "price_step": price_step,

        "account_balance_required": False,
        "position_sizing_performed": False,
        "quantity_calculated": False,
        "proposed_quantity": None,

        "order_payload_created": False,
        "read_only": True,

        "skip_reason": admission_reason,

        # CONTINUOUS SCAN DIAGNOSTICS
        "continuous_scan_configured":
            strategy.get(
                "continuous_entry_scan_enabled"
            ),

        "scan_interval_seconds":
            strategy.get(
                "entry_scan_interval_seconds"
            ),

        "signal_id": None,
        "signal_age_ms": None,
        "signal_fresh": False,

        # DOWNSTREAM RE-ENTRY REQUIREMENTS
        "flat_position_check_required": False,
        "pending_order_check_required": False,
        "exchange_reconciliation_required": False,
        "fresh_balance_check_required": False,

        # NOT YET EXCHANGE VERIFIED
        "flat_position_confirmed": False,
        "pending_orders_cleared": False,
        "exchange_state_reconciled": False,

        "reentry_authorized": False,
        "order_submission_authorized": False,
    }

    # ========================================================
    # 6. NORMAL IDLE PATH
    # INDENTATION: 4 SPACES
    # ========================================================

    if execution_intent is False:

        if active_mode != "NONE":
            raise RuntimeError(
                "UNIT 7 IDLE MODE MUST BE NONE"
            )

        if direction != "NONE":
            raise RuntimeError(
                "UNIT 7 IDLE DIRECTION MUST BE NONE"
            )

        print("-" * 80, flush=True)
        print("UNIT 7 STATUS = IDLE", flush=True)

        print(
            "UNIT 7 SKIP REASON =",
            admission_reason,
            flush=True,
        )

        print(
            "UNIT 7 CONTINUOUS SCAN CONFIGURED =",
            sizing_candidate[
                "continuous_scan_configured"
            ],
            flush=True,
        )

        print(
            "UNIT 7 POSITION SIZING = SKIPPED",
            flush=True,
        )

        print(
            "UNIT 7 REENTRY AUTHORIZED = FALSE",
            flush=True,
        )

        print(
            "ZERO EXCHANGE WRITE = TRUE",
            flush=True,
        )

        log(
            "FRESH RECONSTRUCTION UNIT 7 "
            "RESULT = PASS (IDLE)"
        )

        print("=" * 80, flush=True)

        return sizing_candidate

    # ========================================================
    # 7. QUALIFIED SIGNAL VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    if admission_reason != "QUALIFIED_SIGNAL_ADMITTED":
        raise RuntimeError(
            "UNIT 7 QUALIFIED ADMISSION MISSING"
        )

    if active_mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        raise RuntimeError(
            "UNIT 7 INVALID QUALIFIED MODE"
        )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 7 INVALID QUALIFIED DIRECTION"
        )

    if unit_6_candidate.get(
        "persistence_pass"
    ) is not True:
        raise RuntimeError(
            "UNIT 7 CONFIRMATIONS NOT COMPLETE"
        )

    if unit_6_candidate.get(
        "signal_fresh"
    ) is not True:
        raise RuntimeError(
            "UNIT 7 SIGNAL NOT FRESH"
        )

    signal_id = unit_6_candidate.get(
        "signal_id"
    )

    if not isinstance(signal_id, str):
        raise RuntimeError(
            "UNIT 7 SIGNAL IDENTIFIER MISSING"
        )

    if not signal_id:
        raise RuntimeError(
            "UNIT 7 EMPTY SIGNAL IDENTIFIER"
        )

    try:
        signal_age_ms = int(
            unit_6_candidate["signal_age_ms"]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 7 INVALID SIGNAL AGE"
        ) from exc

    expiry_ms = int(
        float(strategy["signal_expiry_seconds"])
        * 1000
    )

    # IMPORTANT:
    # A previously qualified signal may have expired
    # during processing. Reject stale admission.

    if not (-30000 <= signal_age_ms <= expiry_ms):
        sizing_candidate["skip_reason"] = (
            "SIGNAL_EXPIRED_BEFORE_SIZING"
        )

        print(
            "UNIT 7 STATUS = IDLE",
            flush=True,
        )

        print(
            "UNIT 7 SKIP REASON =",
            sizing_candidate["skip_reason"],
            flush=True,
        )

        return sizing_candidate

    # ========================================================
    # 8. PREPARE SIZING HANDOFF
    # INDENTATION: 4 SPACES
    #
    # No exchange balance has been fetched.
    # No quantity has been calculated.
    # ========================================================

    sizing_candidate.update({

        "status": "READY_FOR_BALANCE",

        "active_mode": active_mode,
        "direction": direction,

        "execution_intent": True,
        "signal_qualified": True,

        "skip_reason": None,

        "account_balance_required": True,

        "signal_id": signal_id,
        "signal_age_ms": signal_age_ms,
        "signal_fresh": True,

        "flat_position_check_required": True,
        "pending_order_check_required": True,
        "exchange_reconciliation_required": True,
        "fresh_balance_check_required": True,

        "position_sizing_performed": False,
        "quantity_calculated": False,
        "proposed_quantity": None,

        "order_payload_created": False,
        "reentry_authorized": False,
        "order_submission_authorized": False,
    })

    # ========================================================
    # 9. OUTPUT CONTRACT
    # INDENTATION: 4 SPACES
    # ========================================================

    if sizing_candidate["read_only"] is not True:
        raise RuntimeError(
            "UNIT 7 READ-ONLY CONTRACT FAILED"
        )

    if sizing_candidate["quantity_calculated"] is not False:
        raise RuntimeError(
            "UNIT 7 QUANTITY STATE INVALID"
        )

    if sizing_candidate["proposed_quantity"] is not None:
        raise RuntimeError(
            "UNIT 7 QUANTITY INVENTED"
        )

    if sizing_candidate["order_payload_created"] is not False:
        raise RuntimeError(
            "UNIT 7 ORDER PAYLOAD INVALID"
        )

    if sizing_candidate["reentry_authorized"] is not False:
        raise RuntimeError(
            "UNIT 7 REENTRY AUTHORIZATION INVALID"
        )

    if (
        sizing_candidate["order_submission_authorized"]
        is not False
    ):
        raise RuntimeError(
            "UNIT 7 ORDER AUTHORIZATION INVALID"
        )

    # ========================================================
    # 10. VISIBLE RENDER LOGGING
    # INDENTATION: 4 SPACES
    # ========================================================

    print("-" * 80, flush=True)

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
        "UNIT 7 SIGNAL ID =",
        signal_id,
        flush=True,
    )

    print(
        "UNIT 7 INITIAL MARGIN =",
        margin_percent,
        "%",
        flush=True,
    )

    print(
        "UNIT 7 MAX EXPOSURE =",
        exposure_cap_percent,
        "%",
        flush=True,
    )

    print(
        "UNIT 7 POSITION SIZING = AWAITING BALANCE",
        flush=True,
    )

    print(
        "UNIT 7 FLAT POSITION CHECK = REQUIRED",
        flush=True,
    )

    print(
        "UNIT 7 PENDING ORDER CHECK = REQUIRED",
        flush=True,
    )

    print(
        "UNIT 7 EXCHANGE RECONCILIATION = REQUIRED",
        flush=True,
    )

    print(
        "UNIT 7 REENTRY AUTHORIZED = FALSE",
        flush=True,
    )

    print(
        "UNIT 7 ORDER SUBMISSION AUTHORIZED = FALSE",
        flush=True,
    )

    print(
        "PASS: UNIT 7 SIZING HANDOFF READY",
        flush=True,
    )

    print(
        "PASS: UNIT 7 NO NETWORK REQUEST",
        flush=True,
    )

    print(
        "PASS: UNIT 7 NO QUANTITY INVENTED",
        flush=True,
    )

    print(
        "PASS: UNIT 7 NO ORDER PAYLOAD",
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
        "FRESH RECONSTRUCTION UNIT 7 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return sizing_candidate


# ============================================================
# INITIAL UNIT 7 EXECUTION
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_SIZING_CANDIDATE = (
    fresh_reconstruction_unit_7(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE,
    )
)


# ============================================================
# UNIT 7 REUSABLE REFRESH FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_refresh_unit_7(
    execution_candidate=None
):

    global FRESH_RECONSTRUCTION_SIZING_CANDIDATE

    if execution_candidate is None:
        execution_candidate = (
            FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE
        )

    refreshed = fresh_reconstruction_unit_7(
        FRESH_RECONSTRUCTION_CONFIG,
        execution_candidate,
    )

    FRESH_RECONSTRUCTION_SIZING_CANDIDATE = (
        refreshed
    )

    return refreshed


# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 7
# ZERO INDENTATION DEMARCATION
#
# UNIT 7 FULLY CLOSED
# INITIAL EXECUTION COMPLETED
# REFRESH FUNCTION CREATED
# UNIT 8 HANDOFF VARIABLE PRESERVED
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN LOOP
# NO OPEN TRY
# NO OPEN DICTIONARY
#
# EXISTING UNIT 8 CONTINUES BELOW
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 8
# ZERO INDENTATION DEMARCATION
# ============================================================
#
# VERIFIED WEEX DEMO BALANCE AND POSITION SIZING
#
# PRESERVED:
# - Authenticated DEMO balance GET only
# - SUSDT available balance
# - Initial margin maximum 5%
# - BTC position quantity step 0.0001
# - Initial entry quantity maximum 0.0004 BTC
# - No position or order endpoint access
# - No order submission
#
# ADDED:
# - Fresh-signal validation
# - Continuous-scan compatibility
# - Fresh BTC market snapshot validation
# - Protected flat-position re-entry handoff
# - Explicit sizing and margin checks
# - Reusable Unit 8 refresh function
#
# ZERO EXCHANGE WRITE
# ============================================================

import os
import time
import math
import json
import hmac
import base64
import hashlib
import urllib.request
import urllib.error

from decimal import Decimal, ROUND_DOWN


# ============================================================
# UNIT 8 MAIN FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_8(
    config,
    unit_7_result,
    market_snapshot,
):

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 8 START")

    # ========================================================
    # 1. INPUT VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    if not all(
        isinstance(item, dict)
        for item in (
            config,
            unit_7_result,
            market_snapshot,
        )
    ):
        raise RuntimeError(
            "UNIT 8 INVALID INPUT CONTRACT"
        )

    strategy = config.get("strategy")
    safety = config.get("safety")
    exchange = config.get("exchange")
    precision = config.get("market_precision")

    if not all(
        isinstance(item, dict)
        for item in (
            strategy,
            safety,
            exchange,
            precision,
        )
    ):
        raise RuntimeError(
            "UNIT 8 CONFIGURATION SECTIONS MISSING"
        )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 8 REAL ENVIRONMENT PROHIBITED"
        )

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 8 INVALID EXCHANGE"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 8 INVALID API VERSION"
        )

    if exchange.get("market_symbol") != "BTCUSDT":
        raise RuntimeError(
            "UNIT 8 INVALID MARKET SYMBOL"
        )

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 8 INVALID DEMO SYMBOL"
        )

    base_url = exchange.get(
        "contract_base_url"
    )

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 8 INVALID BASE URL"
        )

    # ========================================================
    # 2. SAFETY CONTRACT
    # INDENTATION: 4 SPACES
    # ========================================================

    if safety.get(
        "demo_account_balance_read_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 8 DEMO BALANCE READ DISABLED"
        )

    forbidden = (
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
                "UNIT 8 UNSAFE CAPABILITY: " + key
            )

    if strategy.get(
        "real_money_execution_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 8 REAL EXECUTION NOT BLOCKED"
        )

    # ========================================================
    # 3. VALIDATE UNIT 7 HANDOFF
    # INDENTATION: 4 SPACES
    # ========================================================

    if unit_7_result.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 8 UNIT 7 NOT READ ONLY"
        )

    status = str(
        unit_7_result.get("status", "IDLE")
    ).upper()

    active_mode = unit_7_result.get(
        "active_mode", "NONE"
    )

    direction = unit_7_result.get(
        "direction", "NONE"
    )

    execution_intent = unit_7_result.get(
        "execution_intent"
    )

    signal_qualified = unit_7_result.get(
        "signal_qualified"
    )

    if not isinstance(execution_intent, bool):
        raise RuntimeError(
            "UNIT 8 INVALID EXECUTION INTENT"
        )

    if not isinstance(signal_qualified, bool):
        raise RuntimeError(
            "UNIT 8 INVALID SIGNAL FLAG"
        )

    if execution_intent != signal_qualified:
        raise RuntimeError(
            "UNIT 8 SIGNAL CONTRACT CONFLICT"
        )

    # ========================================================
    # 4. NORMALIZED IDLE RESULT
    # INDENTATION: 4 SPACES
    # ========================================================

    idle_result = {
        "status": "IDLE",
        "active_mode": "NONE",
        "direction": "NONE",
        "signal_qualified": False,
        "execution_intent": False,
        "trade_plan_ready": False,
        "trade_plan": None,
        "skip_reason": unit_7_result.get(
            "skip_reason"
        ) or "NO_QUALIFIED_SIGNAL",
        "read_only": True,
        "order_submission_authorized": False,
        "reentry_authorized": False,
    }

    if execution_intent is False:

        if status != "IDLE":
            raise RuntimeError(
                "UNIT 8 INVALID IDLE STATUS"
            )

        if active_mode != "NONE" or direction != "NONE":
            raise RuntimeError(
                "UNIT 8 INVALID IDLE DIRECTION"
            )

        print("UNIT 8 STATUS = IDLE", flush=True)
        print(
            "UNIT 8 SKIP REASON =",
            idle_result["skip_reason"],
            flush=True,
        )

        print(
            "PASS: UNIT 8 NO AUTHENTICATED REQUEST",
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
            "FRESH RECONSTRUCTION UNIT 8 "
            "RESULT = PASS (IDLE)"
        )

        print("=" * 80, flush=True)

        return idle_result

    # ========================================================
    # 5. QUALIFIED SIGNAL VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    if status != "READY_FOR_BALANCE":
        raise RuntimeError(
            "UNIT 8 INVALID QUALIFIED STATUS"
        )

    if active_mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        raise RuntimeError(
            "UNIT 8 INVALID ACTIVE MODE"
        )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 8 INVALID DIRECTION"
        )

    if unit_7_result.get(
        "signal_fresh"
    ) is not True:
        raise RuntimeError(
            "UNIT 8 SIGNAL NOT FRESH"
        )

    signal_id = unit_7_result.get(
        "signal_id"
    )

    if not isinstance(signal_id, str) or not signal_id:
        raise RuntimeError(
            "UNIT 8 SIGNAL ID MISSING"
        )

    required_handoff = (
        "flat_position_check_required",
        "pending_order_check_required",
        "exchange_reconciliation_required",
        "fresh_balance_check_required",
    )

    for key in required_handoff:

        if unit_7_result.get(key) is not True:
            raise RuntimeError(
                "UNIT 8 REQUIRED PROTECTION MISSING: "
                + key
            )

    # ========================================================
    # 6. MARKET SNAPSHOT VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    if market_snapshot.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 8 MARKET SNAPSHOT NOT READ ONLY"
        )

    if market_snapshot.get("symbol") != "BTCUSDT":
        raise RuntimeError(
            "UNIT 8 MARKET SYMBOL MISMATCH"
        )

    if market_snapshot.get("price_type") != "MARK":
        raise RuntimeError(
            "UNIT 8 PRICE TYPE MISMATCH"
        )

    try:

        live_price = Decimal(
            str(market_snapshot["price"])
        )

        market_time_ms = int(
            market_snapshot["exchange_time_ms"]
        )

    except (
        KeyError,
        TypeError,
        ValueError,
        ArithmeticError,
    ) as exc:

        raise RuntimeError(
            "UNIT 8 INVALID MARKET SNAPSHOT"
        ) from exc

    if not live_price.is_finite() or live_price <= 0:
        raise RuntimeError(
            "UNIT 8 INVALID LIVE BTC PRICE"
        )

    now_ms = int(time.time() * 1000)

    market_age_ms = (
        now_ms - market_time_ms
    )

    if not -30000 <= market_age_ms <= 120000:
        raise RuntimeError(
            "UNIT 8 STALE MARKET SNAPSHOT"
        )

    # ========================================================
    # 7. SIGNAL FRESHNESS
    # INDENTATION: 4 SPACES
    # ========================================================

    signal_age_ms = int(
        unit_7_result["signal_age_ms"]
    )

    expiry_ms = int(
        float(strategy["signal_expiry_seconds"])
        * 1000
    )

    if not -30000 <= signal_age_ms <= expiry_ms:
        idle_result["skip_reason"] = (
            "SIGNAL_EXPIRED_BEFORE_BALANCE_READ"
        )
        return idle_result

    # ========================================================
    # 8. VERIFIED POSITION SIZING PARAMETERS
    # INDENTATION: 4 SPACES
    # ========================================================

    initial_margin_pct = Decimal(
        str(unit_7_result["initial_margin_percent"])
    )

    backup_margin_pct = Decimal(
        str(unit_7_result["backup_margin_percent"])
    )

    exposure_cap_pct = Decimal(
        str(unit_7_result["exposure_cap_percent"])
    )

    leverage_target = Decimal(
        str(unit_7_result["leverage_target"])
    )

    quantity_step = Decimal(
        str(unit_7_result["quantity_step"])
    )

    minimum_quantity = Decimal(
        str(unit_7_result["minimum_quantity"])
    )

    initial_quantity_cap = Decimal("0.0004")

    sizing_values = (
        initial_margin_pct,
        backup_margin_pct,
        exposure_cap_pct,
        leverage_target,
        quantity_step,
        minimum_quantity,
    )

    if not all(
        value.is_finite() and value > 0
        for value in sizing_values
    ):
        raise RuntimeError(
            "UNIT 8 INVALID SIZING VALUES"
        )

    if initial_margin_pct > Decimal("5"):
        raise RuntimeError(
            "UNIT 8 INITIAL MARGIN EXCEEDS 5%"
        )

    if backup_margin_pct > Decimal("5"):
        raise RuntimeError(
            "UNIT 8 BACKUP MARGIN EXCEEDS 5%"
        )

    if exposure_cap_pct > Decimal("35"):
        raise RuntimeError(
            "UNIT 8 EXPOSURE CAP EXCEEDS 35%"
        )

    if int(unit_7_result["max_backups"]) != 3:
        raise RuntimeError(
            "UNIT 8 INVALID BACKUP COUNT"
        )

    staged_margin_pct = (
        initial_margin_pct
        + Decimal("3") * backup_margin_pct
    )

    if staged_margin_pct > exposure_cap_pct:
        raise RuntimeError(
            "UNIT 8 STAGED MARGIN EXCEEDS CAP"
        )

    # ========================================================
    # 9. LOAD DEMO READ CREDENTIALS
    # INDENTATION: 4 SPACES
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
        raise RuntimeError(
            "UNIT 8 DEMO CREDENTIALS MISSING"
        )

    # ========================================================
    # 10. AUTHENTICATED DEMO BALANCE GET
    # INDENTATION: 4 SPACES
    #
    # Preserves the source file's endpoint and signing
    # scheme. API permissions must be independently
    # restricted to the intended demo environment.
    # ========================================================

    request_path = (
        "/capi/v3/sim/balance"
    )

    request_timestamp = str(
        int(time.time() * 1000)
    )

    method = "GET"

    message = (
        request_timestamp
        + method
        + request_path
    )

    signature = base64.b64encode(
        hmac.new(
            api_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": request_timestamp,
        "ACCESS-PASSPHRASE": api_passphrase,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent":
            "Fresh-WEEX-Reconstruction/Unit8",
    }

    request = urllib.request.Request(
        url=base_url + request_path,
        headers=headers,
        method="GET",
    )

    if request.get_method() != "GET":
        raise RuntimeError(
            "UNIT 8 NON-GET REQUEST BLOCKED"
        )

    if request.data is not None:
        raise RuntimeError(
            "UNIT 8 REQUEST BODY BLOCKED"
        )

    print(
        "UNIT 8 DEMO BALANCE READ = START",
        flush=True,
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            if response.getcode() != 200:
                raise RuntimeError(
                    "UNIT 8 DEMO BALANCE HTTP FAILURE"
                )

            raw_response = (
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as exc:

        raise RuntimeError(
            "UNIT 8 DEMO BALANCE HTTP ERROR: "
            + str(exc.code)
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "UNIT 8 DEMO BALANCE CONNECTION FAILED"
        ) from exc

    try:

        balances = json.loads(
            raw_response
        )

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "UNIT 8 INVALID BALANCE RESPONSE"
        ) from exc

    if not isinstance(balances, list):
        raise RuntimeError(
            "UNIT 8 UNEXPECTED BALANCE RESPONSE"
        )

    susdt_items = [
        item
        for item in balances
        if isinstance(item, dict)
        and str(item.get("asset", "")).upper()
        == "SUSDT"
    ]

    if len(susdt_items) != 1:
        raise RuntimeError(
            "UNIT 8 SUSDT BALANCE NOT UNIQUE"
        )

    try:

        available_balance = Decimal(
            str(
                susdt_items[0]["availableBalance"]
            )
        )

    except (
        KeyError,
        TypeError,
        ValueError,
        ArithmeticError,
    ) as exc:

        raise RuntimeError(
            "UNIT 8 INVALID SUSDT BALANCE"
        ) from exc

    if not available_balance.is_finite():
        raise RuntimeError(
            "UNIT 8 NON-FINITE BALANCE"
        )

    if available_balance <= 0:
        idle_result["skip_reason"] = (
            "INSUFFICIENT_DEMO_BALANCE"
        )
        return idle_result

    # ========================================================
    # 11. POSITION SIZING CALCULATION
    # INDENTATION: 4 SPACES
    # ========================================================

    margin_allocation = (
        available_balance
        * initial_margin_pct
        / Decimal("100")
    )

    theoretical_notional = (
        margin_allocation
        * leverage_target
    )

    raw_quantity = (
        theoretical_notional
        / live_price
    )

    raw_steps = (
        raw_quantity / quantity_step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    theoretical_quantity = (
        raw_steps * quantity_step
    )

    max_cap_steps = (
        initial_quantity_cap / quantity_step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    max_cap_quantity = (
        max_cap_steps * quantity_step
    )

    executable_quantity = min(
        theoretical_quantity,
        max_cap_quantity,
    )

    # ========================================================
    # 12. VALIDATE EXECUTABLE QUANTITY
    # INDENTATION: 4 SPACES
    # ========================================================

    if executable_quantity < minimum_quantity:

        idle_result["skip_reason"] = (
            "CALCULATED_QUANTITY_BELOW_MINIMUM"
        )

        print(
            "UNIT 8 STATUS = IDLE",
            flush=True,
        )

        print(
            "UNIT 8 SKIP REASON =",
            idle_result["skip_reason"],
            flush=True,
        )

        return idle_result

    executable_margin = (
        executable_quantity
        * live_price
        / leverage_target
    )

    if executable_margin > margin_allocation:
        raise RuntimeError(
            "UNIT 8 INITIAL MARGIN LIMIT EXCEEDED"
        )

    if executable_quantity > initial_quantity_cap:
        raise RuntimeError(
            "UNIT 8 INITIAL QUANTITY CAP EXCEEDED"
        )

    if (
        executable_quantity / quantity_step
    ) % 1 != 0:
        raise RuntimeError(
            "UNIT 8 QUANTITY STEP ERROR"
        )

    # ========================================================
    # 13. BUILD POSITION SIZING RESULT
    # INDENTATION: 4 SPACES
    # ========================================================

    position_sizing = {
        "asset": "SUSDT",
        "available_balance": float(
            available_balance
        ),
        "initial_margin_percent": float(
            initial_margin_pct
        ),
        "margin_allocation": float(
            margin_allocation
        ),
        "actual_initial_margin": float(
            executable_margin
        ),
        "leverage_target": float(
            leverage_target
        ),
        "live_mark_price": float(
            live_price
        ),
        "raw_quantity": float(
            raw_quantity
        ),
        "theoretical_quantity": float(
            theoretical_quantity
        ),
        "initial_quantity_cap": float(
            initial_quantity_cap
        ),
        "quantity_step": float(
            quantity_step
        ),
        "minimum_quantity": float(
            minimum_quantity
        ),
        "quantity": float(
            executable_quantity
        ),
        "position_sizing_performed": True,
        "quantity_calculated": True,
        "source": "WEEX_V3_DEMO_BALANCE",
        "read_only": True,
    }

    # ========================================================
    # 14. INTERNAL TRADE PLAN
    # INDENTATION: 4 SPACES
    #
    # NOT AN EXCHANGE ORDER PAYLOAD.
    # ========================================================

    trade_plan = {
        "active_mode": active_mode,
        "direction": direction,
        "quantity": float(
            executable_quantity
        ),
        "position_sizing": position_sizing,
        "execution_environment": "DEMO",
        "signal_id": signal_id,
        "market_time_ms": market_time_ms,
        "balance_read_time_ms": int(
            time.time() * 1000
        ),
        "exchange_state_reconciliation_required": True,
        "flat_position_check_required": True,
        "pending_order_check_required": True,
        "anti_duplicate_check_required": True,
        "order_submission_authorized": False,
        "reentry_authorized": False,
    }

    # ========================================================
    # 15. NORMALIZED UNIT 8 RESULT
    # INDENTATION: 4 SPACES
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
        "signal_id": signal_id,
        "order_submission_authorized": False,
        "reentry_authorized": False,
    }

    # ========================================================
    # 16. FINAL OUTPUT VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    if trade_plan["quantity"] <= 0:
        raise RuntimeError(
            "UNIT 8 ZERO TRADE QUANTITY"
        )

    if result["read_only"] is not True:
        raise RuntimeError(
            "UNIT 8 READ-ONLY CONTRACT FAILED"
        )

    if result["order_submission_authorized"] is not False:
        raise RuntimeError(
            "UNIT 8 INVALID ORDER AUTHORIZATION"
        )

    # ========================================================
    # 17. RENDER LOGGING
    # INDENTATION: 4 SPACES
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "PASS: UNIT 8 VERIFIED DEMO BALANCE READ",
        flush=True,
    )

    print(
        "UNIT 8 AVAILABLE SUSDT =",
        float(available_balance),
        flush=True,
    )

    print(
        "UNIT 8 LIVE BTC PRICE =",
        float(live_price),
        flush=True,
    )

    print(
        "UNIT 8 INITIAL MARGIN % =",
        float(initial_margin_pct),
        flush=True,
    )

    print(
        "UNIT 8 LEVERAGE TARGET =",
        float(leverage_target),
        flush=True,
    )

    print(
        "UNIT 8 THEORETICAL BTC QUANTITY =",
        float(theoretical_quantity),
        flush=True,
    )

    print(
        "UNIT 8 INITIAL ENTRY CAP BTC =",
        float(initial_quantity_cap),
        flush=True,
    )

    print(
        "UNIT 8 EXECUTABLE BTC QUANTITY =",
        float(executable_quantity),
        flush=True,
    )

    print(
        "UNIT 8 EXECUTABLE INITIAL MARGIN =",
        float(executable_margin),
        "SUSDT",
        flush=True,
    )

    print(
        "UNIT 8 SIGNAL ID =",
        signal_id,
        flush=True,
    )

    print(
        "UNIT 8 POSITION CHECK = REQUIRED",
        flush=True,
    )

    print(
        "UNIT 8 PENDING ORDER CHECK = REQUIRED",
        flush=True,
    )

    print(
        "UNIT 8 REENTRY AUTHORIZED = FALSE",
        flush=True,
    )

    print(
        "UNIT 8 ORDER SUBMISSION AUTHORIZED = FALSE",
        flush=True,
    )

    print(
        "PASS: UNIT 8 TRADE PLAN READY",
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
        "FRESH RECONSTRUCTION UNIT 8 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 8 INITIAL SIZING
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
# UNIT 8 REUSABLE REFRESH FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_refresh_unit_8(
    sizing_candidate=None,
    market_snapshot=None,
):

    global FRESH_RECONSTRUCTION_UNIT_8_RESULT

    if sizing_candidate is None:
        sizing_candidate = (
            FRESH_RECONSTRUCTION_SIZING_CANDIDATE
        )

    if market_snapshot is None:
        market_snapshot = (
            FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
        )

    refreshed_result = fresh_reconstruction_unit_8(
        FRESH_RECONSTRUCTION_CONFIG,
        sizing_candidate,
        market_snapshot,
    )

    FRESH_RECONSTRUCTION_UNIT_8_RESULT = (
        refreshed_result
    )

    return refreshed_result


# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 8
# ZERO INDENTATION DEMARCATION
#
# UNIT 8 FULLY CLOSED
# UNIT 8 CALLED ONCE
# REFRESH FUNCTION CREATED
# UNIT 9 HANDOFF VARIABLE PRESERVED
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN TRY
# NO OPEN LOOP
# NO OPEN DICTIONARY
#
# EXISTING UNIT 9 CONTINUES BELOW
# ============================================================

# ============================================================
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 9
# ZERO INDENTATION DEMARCATION
# ============================================================
#
# COORDINATED INTERNAL EXECUTION PREPARATION
#
# FUNCTIONS:
# - Receive refreshed Unit 8 trade plan
# - Preserve normal IDLE behavior
# - Validate SCALP / STRUCTURE / BREAKOUT
# - Validate signal identity and freshness
# - Recheck position quantity and margin
# - Carry flat-position re-entry requirements
# - Preserve Unit 10 handoff
# - Never authorize order submission
#
# NO AUTHENTICATED NETWORK REQUEST
# NO POSITION REQUEST
# NO ORDER ENDPOINT REQUEST
# NO DEMO ORDER
# NO REAL ORDER
# NO EXCHANGE WRITE
# ============================================================

import time
import math
from decimal import Decimal


# ============================================================
# UNIT 9 DECIMAL VALIDATION HELPER
# ZERO INDENTATION
# ============================================================

def fresh_unit_9_decimal(value, name):

    try:
        number = Decimal(str(value))
    except Exception as exc:
        raise RuntimeError(
            "UNIT 9 INVALID NUMBER: " + name
        ) from exc

    if not number.is_finite():
        raise RuntimeError(
            "UNIT 9 NON-FINITE NUMBER: " + name
        )

    return number


# ============================================================
# UNIT 9 MAIN FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_9(
    config,
    unit_8_result,
):

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 9 START")

    # ========================================================
    # 1. INPUT VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 9 CONFIGURATION MISSING"
        )

    if not isinstance(unit_8_result, dict):
        raise RuntimeError(
            "UNIT 9 UNIT 8 RESULT MISSING"
        )

    strategy = config.get("strategy")
    safety = config.get("safety")
    exchange = config.get("exchange")
    precision = config.get("market_precision")

    for name, section in (
        ("STRATEGY", strategy),
        ("SAFETY", safety),
        ("EXCHANGE", exchange),
        ("PRECISION", precision),
    ):
        if not isinstance(section, dict):
            raise RuntimeError(
                "UNIT 9 CONFIG MISSING: " + name
            )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 9 REAL ENVIRONMENT PROHIBITED"
        )

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 9 INVALID EXCHANGE"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 9 INVALID API VERSION"
        )

    if exchange.get("market_symbol") != "BTCUSDT":
        raise RuntimeError(
            "UNIT 9 INVALID MARKET SYMBOL"
        )

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 9 INVALID DEMO SYMBOL"
        )

    # ========================================================
    # 2. STRICT READ-ONLY SAFETY
    # INDENTATION: 4 SPACES
    # ========================================================

    if unit_8_result.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 9 UNIT 8 NOT READ ONLY"
        )

    forbidden = (
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
                "UNIT 9 UNSAFE CAPABILITY: " + key
            )

    if strategy.get(
        "real_money_execution_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 9 REAL EXECUTION NOT BLOCKED"
        )

    protections = (
        "one_direction_only",
        "anti_duplicate_orders",
        "active_trade_mode_lock",
        "exclusive_mode",
        "require_confirmed_flat_position",
        "require_no_pending_entry_orders",
        "require_exchange_state_reconciliation",
        "require_fresh_reentry_signal",
        "block_duplicate_signal_ids",
        "reconcile_after_restart",
    )

    for key in protections:
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 9 PROTECTION DISABLED: " + key
            )

    # ========================================================
    # 3. VERIFY UNIT 8 CONTRACT
    # INDENTATION: 4 SPACES
    # ========================================================

    required = (
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
        key for key in required
        if key not in unit_8_result
    ]

    if missing:
        raise RuntimeError(
            "UNIT 9 MISSING UNIT 8 FIELDS: "
            + str(missing)
        )

    status = unit_8_result["status"]
    mode = unit_8_result["active_mode"]
    direction = unit_8_result["direction"]

    qualified = unit_8_result["signal_qualified"]
    intent = unit_8_result["execution_intent"]
    plan_ready = unit_8_result["trade_plan_ready"]

    trade_plan = unit_8_result["trade_plan"]

    if not all(
        isinstance(value, bool)
        for value in (qualified, intent, plan_ready)
    ):
        raise RuntimeError(
            "UNIT 9 INVALID BOOLEAN CONTRACT"
        )

    # ========================================================
    # 4. NORMALIZED DOWNSTREAM RESULT
    # INDENTATION: 4 SPACES
    # ========================================================

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
        "skip_reason": unit_8_result.get(
            "skip_reason"
        ) or "NO_QUALIFIED_SIGNAL",

        "order_payload_created": False,
        "tp_execution_requested": False,
        "sl_execution_requested": False,

        "read_only": True,

        # COORDINATED SCANNING
        "continuous_scan_configured":
            strategy.get(
                "continuous_entry_scan_enabled"
            ),

        "signal_id": None,
        "signal_fresh": False,

        # RE-ENTRY PROTECTION
        "flat_position_check_required": False,
        "pending_order_check_required": False,
        "exchange_reconciliation_required": False,
        "anti_duplicate_check_required": False,

        # THESE ARE NOT YET VERIFIED
        "flat_position_confirmed": False,
        "pending_orders_cleared": False,
        "exchange_state_reconciled": False,

        # EXPLICITLY NO AUTHORIZATION
        "reentry_authorized": False,
        "order_submission_authorized": False,
    }

    # ========================================================
    # 5. NORMAL IDLE PATH
    # INDENTATION: 4 SPACES
    # ========================================================

    if (
        status == "IDLE"
        and qualified is False
        and intent is False
        and plan_ready is False
        and trade_plan is None
    ):

        if mode != "NONE" or direction != "NONE":
            raise RuntimeError(
                "UNIT 9 INCONSISTENT IDLE MODE"
            )

        print("-" * 80, flush=True)

        print(
            "UNIT 9 STATUS = IDLE",
            flush=True,
        )

        print(
            "UNIT 9 SKIP REASON =",
            result["skip_reason"],
            flush=True,
        )

        print(
            "UNIT 9 CONTINUOUS SCAN CONFIGURED =",
            result["continuous_scan_configured"],
            flush=True,
        )

        print(
            "UNIT 9 EXECUTION READY = FALSE",
            flush=True,
        )

        print(
            "UNIT 9 REENTRY AUTHORIZED = FALSE",
            flush=True,
        )

        print(
            "ZERO EXCHANGE WRITE = TRUE",
            flush=True,
        )

        log(
            "FRESH RECONSTRUCTION UNIT 9 "
            "RESULT = PASS (IDLE)"
        )

        print("=" * 80, flush=True)

        return result

    # ========================================================
    # 6. QUALIFIED SIGNAL CONTRACT
    # INDENTATION: 4 SPACES
    # ========================================================

    if status != "READY":
        raise RuntimeError(
            "UNIT 9 INVALID ACTIONABLE STATUS"
        )

    if not (
        qualified is True
        and intent is True
        and plan_ready is True
    ):
        raise RuntimeError(
            "UNIT 9 INCONSISTENT QUALIFIED STATE"
        )

    if mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        raise RuntimeError(
            "UNIT 9 INVALID ACTIVE MODE"
        )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 9 INVALID DIRECTION"
        )

    if not isinstance(trade_plan, dict):
        raise RuntimeError(
            "UNIT 9 TRADE PLAN MISSING"
        )

    if trade_plan.get("active_mode") != mode:
        raise RuntimeError(
            "UNIT 9 MODE MISMATCH"
        )

    if trade_plan.get("direction") != direction:
        raise RuntimeError(
            "UNIT 9 DIRECTION MISMATCH"
        )

    if trade_plan.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 9 INVALID TRADE ENVIRONMENT"
        )

    # ========================================================
    # 7. SIGNAL ID AND FRESHNESS
    # INDENTATION: 4 SPACES
    # ========================================================

    signal_id = unit_8_result.get("signal_id")

    if not isinstance(signal_id, str) or not signal_id:
        raise RuntimeError(
            "UNIT 9 SIGNAL ID MISSING"
        )

    if trade_plan.get("signal_id") != signal_id:
        raise RuntimeError(
            "UNIT 9 SIGNAL ID MISMATCH"
        )

    try:
        market_time_ms = int(
            trade_plan["market_time_ms"]
        )
        balance_read_time_ms = int(
            trade_plan["balance_read_time_ms"]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 9 INVALID SNAPSHOT TIME"
        ) from exc

    now_ms = int(time.time() * 1000)

    market_age = now_ms - market_time_ms
    balance_age = now_ms - balance_read_time_ms

    signal_expiry_ms = int(
        float(strategy["signal_expiry_seconds"])
        * 1000
    )

    if not -30000 <= market_age <= signal_expiry_ms:
        result["skip_reason"] = "SIGNAL_EXPIRED"
        return result

    if not -5000 <= balance_age <= 30000:
        result["skip_reason"] = "BALANCE_SNAPSHOT_STALE"
        return result

    # ========================================================
    # 8. VERIFY POSITION SIZING
    # INDENTATION: 4 SPACES
    # ========================================================

    sizing = trade_plan.get("position_sizing")

    if not isinstance(sizing, dict):
        raise RuntimeError(
            "UNIT 9 POSITION SIZING MISSING"
        )

    if sizing.get(
        "position_sizing_performed"
    ) is not True:
        raise RuntimeError(
            "UNIT 9 POSITION SIZING NOT COMPLETED"
        )

    if sizing.get(
        "quantity_calculated"
    ) is not True:
        raise RuntimeError(
            "UNIT 9 QUANTITY NOT CALCULATED"
        )

    if sizing.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 9 SIZING NOT READ ONLY"
        )

    quantity = fresh_unit_9_decimal(
        trade_plan.get("quantity"),
        "quantity",
    )

    sizing_quantity = fresh_unit_9_decimal(
        sizing.get("quantity"),
        "sizing quantity",
    )

    quantity_step = fresh_unit_9_decimal(
        precision["quantity_step"],
        "quantity step",
    )

    minimum_quantity = fresh_unit_9_decimal(
        precision["minimum_quantity"],
        "minimum quantity",
    )

    leverage = fresh_unit_9_decimal(
        sizing.get("leverage_target"),
        "leverage",
    )

    initial_margin = fresh_unit_9_decimal(
        sizing.get("actual_initial_margin"),
        "initial margin",
    )

    margin_allocation = fresh_unit_9_decimal(
        sizing.get("margin_allocation"),
        "margin allocation",
    )

    price = fresh_unit_9_decimal(
        sizing.get("live_mark_price"),
        "mark price",
    )

    balance = fresh_unit_9_decimal(
        sizing.get("available_balance"),
        "balance",
    )

    if quantity <= 0 or quantity != sizing_quantity:
        raise RuntimeError(
            "UNIT 9 QUANTITY MISMATCH"
        )

    if quantity < minimum_quantity:
        raise RuntimeError(
            "UNIT 9 QUANTITY BELOW MINIMUM"
        )

    if quantity > Decimal("0.0004"):
        raise RuntimeError(
            "UNIT 9 INITIAL QUANTITY CAP EXCEEDED"
        )

    if quantity_step <= 0:
        raise RuntimeError(
            "UNIT 9 INVALID QUANTITY STEP"
        )

    if quantity % quantity_step != 0:
        raise RuntimeError(
            "UNIT 9 QUANTITY STEP VIOLATION"
        )

    if leverage <= 0 or price <= 0 or balance <= 0:
        raise RuntimeError(
            "UNIT 9 INVALID MARKET OR BALANCE"
        )

    if margin_allocation <= 0:
        raise RuntimeError(
            "UNIT 9 INVALID MARGIN ALLOCATION"
        )

    if initial_margin <= 0:
        raise RuntimeError(
            "UNIT 9 INVALID INITIAL MARGIN"
        )

    if initial_margin > margin_allocation:
        raise RuntimeError(
            "UNIT 9 MARGIN ALLOCATION EXCEEDED"
        )

    calculated_margin = (
        quantity * price / leverage
    )

    if abs(
        calculated_margin - initial_margin
    ) > Decimal("0.00000001"):
        raise RuntimeError(
            "UNIT 9 MARGIN CALCULATION MISMATCH"
        )

    maximum_initial_margin = (
        balance * Decimal("0.05")
    )

    if initial_margin > maximum_initial_margin:
        raise RuntimeError(
            "UNIT 9 INITIAL MARGIN EXCEEDS 5%"
        )

    configured_exposure = fresh_unit_9_decimal(
        strategy["exposure_cap_percent"],
        "exposure cap",
    )

    if not (
        Decimal("0") <
        configured_exposure <= Decimal("35")
    ):
        raise RuntimeError(
            "UNIT 9 EXPOSURE CAP INVALID"
        )

    # ========================================================
    # 9. REQUIRE ALL FUTURE EXCHANGE SAFEGUARDS
    # INDENTATION: 4 SPACES
    # ========================================================

    required_checks = (
        "flat_position_check_required",
        "pending_order_check_required",
        "exchange_state_reconciliation_required",
        "anti_duplicate_check_required",
    )

    for key in required_checks:

        if trade_plan.get(key) is not True:
            raise RuntimeError(
                "UNIT 9 MISSING SAFEGUARD: " + key
            )

    if trade_plan.get(
        "order_submission_authorized"
    ) is not False:
        raise RuntimeError(
            "UNIT 9 UNEXPECTED ORDER AUTHORIZATION"
        )

    if trade_plan.get(
        "reentry_authorized"
    ) is not False:
        raise RuntimeError(
            "UNIT 9 UNEXPECTED REENTRY AUTHORIZATION"
        )

    # ========================================================
    # 10. PREPARE INTERNAL EXECUTION CANDIDATE
    # INDENTATION: 4 SPACES
    #
    # NOT A WEEX EXCHANGE ORDER PAYLOAD
    # ========================================================

    internal_candidate = {
        "active_mode": mode,
        "direction": direction,
        "trade_plan": trade_plan,
        "execution_environment": "DEMO",
        "signal_id": signal_id,

        "signal_fresh": True,
        "signal_age_ms": market_age,
        "balance_age_ms": balance_age,

        "quantity": float(quantity),
        "leverage_target": float(leverage),

        "flat_position_check_required": True,
        "pending_order_check_required": True,
        "exchange_reconciliation_required": True,
        "anti_duplicate_check_required": True,

        "flat_position_confirmed": False,
        "pending_orders_cleared": False,
        "exchange_state_reconciled": False,

        "reentry_authorized": False,
        "order_submission_authorized": False,

        "read_only": True,
    }

    # ========================================================
    # 11. UNIT 10 COMPATIBILITY RESULT
    # INDENTATION: 4 SPACES
    # ========================================================

    result.update({
        "status": "READY",
        "active_mode": mode,
        "direction": direction,
        "signal_qualified": True,
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": trade_plan,
        "execution_ready": True,
        "execution_candidate": internal_candidate,
        "skip_reason": "NONE",

        "signal_id": signal_id,
        "signal_fresh": True,

        "flat_position_check_required": True,
        "pending_order_check_required": True,
        "exchange_reconciliation_required": True,
        "anti_duplicate_check_required": True,

        "flat_position_confirmed": False,
        "pending_orders_cleared": False,
        "exchange_state_reconciled": False,

        "reentry_authorized": False,
        "order_submission_authorized": False,

        "order_payload_created": False,
        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "read_only": True,
    })

    # ========================================================
    # 12. FINAL SAFETY CHECK
    # INDENTATION: 4 SPACES
    # ========================================================

    if result["order_payload_created"] is not False:
        raise RuntimeError(
            "UNIT 9 ORDER PAYLOAD GENERATED"
        )

    if result["order_submission_authorized"] is not False:
        raise RuntimeError(
            "UNIT 9 ORDER AUTHORIZATION VIOLATION"
        )

    if result["reentry_authorized"] is not False:
        raise RuntimeError(
            "UNIT 9 REENTRY AUTHORIZATION VIOLATION"
        )

    if result["read_only"] is not True:
        raise RuntimeError(
            "UNIT 9 READ-ONLY CONTRACT FAILURE"
        )

    # ========================================================
    # 13. RENDER LOGGING
    # INDENTATION: 4 SPACES
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "UNIT 9 STATUS = READY",
        flush=True,
    )

    print(
        "UNIT 9 ACTIVE MODE =",
        mode,
        flush=True,
    )

    print(
        "UNIT 9 DIRECTION =",
        direction,
        flush=True,
    )

    print(
        "UNIT 9 SIGNAL ID =",
        signal_id,
        flush=True,
    )

    print(
        "UNIT 9 SIGNAL AGE MS =",
        market_age,
        flush=True,
    )

    print(
        "UNIT 9 BALANCE AGE MS =",
        balance_age,
        flush=True,
    )

    print(
        "UNIT 9 BTC QUANTITY =",
        float(quantity),
        flush=True,
    )

    print(
        "UNIT 9 INITIAL MARGIN =",
        float(initial_margin),
        flush=True,
    )

    print(
        "UNIT 9 LEVERAGE TARGET =",
        float(leverage),
        flush=True,
    )

    print(
        "UNIT 9 INTERNAL EXECUTION READY = TRUE",
        flush=True,
    )

    print(
        "UNIT 9 FLAT POSITION CHECK = REQUIRED",
        flush=True,
    )

    print(
        "UNIT 9 PENDING ORDER CHECK = REQUIRED",
        flush=True,
    )

    print(
        "UNIT 9 ANTI-DUPLICATE CHECK = REQUIRED",
        flush=True,
    )

    print(
        "UNIT 9 EXCHANGE RECONCILIATION = REQUIRED",
        flush=True,
    )

    print(
        "UNIT 9 REENTRY AUTHORIZED = FALSE",
        flush=True,
    )

    print(
        "UNIT 9 ORDER SUBMISSION AUTHORIZED = FALSE",
        flush=True,
    )

    print(
        "PASS: UNIT 9 INTERNAL TRADE PLAN VALIDATED",
        flush=True,
    )

    print(
        "PASS: UNIT 9 UNIT 10 HANDOFF READY",
        flush=True,
    )

    print(
        "PASS: UNIT 9 NO NETWORK REQUEST",
        flush=True,
    )

    print(
        "PASS: UNIT 9 NO ORDER PAYLOAD",
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
        "FRESH RECONSTRUCTION UNIT 9 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# INITIAL UNIT 9 EXECUTION
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_9_RESULT = (
    fresh_reconstruction_unit_9(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT,
    )
)


# ============================================================
# REUSABLE UNIT 9 REFRESH FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_refresh_unit_9(
    unit_8_result=None
):

    global FRESH_RECONSTRUCTION_UNIT_9_RESULT

    if unit_8_result is None:
        unit_8_result = (
            FRESH_RECONSTRUCTION_UNIT_8_RESULT
        )

    refreshed = fresh_reconstruction_unit_9(
        FRESH_RECONSTRUCTION_CONFIG,
        unit_8_result,
    )

    FRESH_RECONSTRUCTION_UNIT_9_RESULT = (
        refreshed
    )

    return refreshed


# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 9
# ZERO INDENTATION DEMARCATION
#
# UNIT 9 FULLY CLOSED
# UNIT 9 CALLED ONCE
# REFRESH FUNCTION CREATED
# UNIT 10 HANDOFF PRESERVED
#
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN TRY
# NO OPEN LOOP
# NO OPEN DICTIONARY
#
# EXISTING UNIT 10 CONTINUES BELOW
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 10
# ZERO INDENTATION DEMARCATION
# ============================================================
#
# COORDINATED DEMO EXECUTION BOUNDARY
#
# FUNCTIONS:
# - Receive refreshed Unit 9 trade plan
# - Preserve IDLE and READY states
# - Validate signal identity and freshness
# - Preserve entry size restrictions
# - Require flat-position confirmation
# - Require pending-order reconciliation
# - Require anti-duplicate protection
# - Require actual leverage verification
# - Preserve Unit 11 instruction contract
# - Support continuous scanner refresh
#
# UNIT 10 DOES NOT:
# - Fetch account information
# - Read exchange positions
# - Create exchange order payloads
# - Submit demo or real orders
# - Execute TP, SL or backups
# - Authorize position re-entry
#
# ZERO EXCHANGE WRITE
# ============================================================

import time
from decimal import Decimal, InvalidOperation


# ============================================================
# UNIT 10 NUMERIC HELPER
# ZERO INDENTATION
# ============================================================

def fresh_unit_10_decimal(value, name):

    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise RuntimeError(
            "UNIT 10 INVALID NUMBER: " + name
        ) from exc

    if not number.is_finite():
        raise RuntimeError(
            "UNIT 10 NON-FINITE NUMBER: " + name
        )

    return number


# ============================================================
# UNIT 10 MAIN FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_10(
    config,
    unit_9_result,
):

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 10 START")

    # ========================================================
    # 1. INPUT CONFIGURATION
    # INDENTATION: 4 SPACES
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 10 CONFIGURATION MISSING"
        )

    if not isinstance(unit_9_result, dict):
        raise RuntimeError(
            "UNIT 10 UNIT 9 RESULT MISSING"
        )

    exchange = config.get("exchange")
    safety = config.get("safety")
    strategy = config.get("strategy")
    precision = config.get("market_precision")

    for name, section in (
        ("EXCHANGE", exchange),
        ("SAFETY", safety),
        ("STRATEGY", strategy),
        ("PRECISION", precision),
    ):
        if not isinstance(section, dict):
            raise RuntimeError(
                "UNIT 10 MISSING CONFIG: " + name
            )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 10 REAL ENVIRONMENT PROHIBITED"
        )

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 10 INVALID EXCHANGE"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 10 INVALID API VERSION"
        )

    if exchange.get("market_symbol") != "BTCUSDT":
        raise RuntimeError(
            "UNIT 10 INVALID MARKET SYMBOL"
        )

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 10 INVALID DEMO SYMBOL"
        )

    # ========================================================
    # 2. STRICT SAFETY CONTRACT
    # INDENTATION: 4 SPACES
    # ========================================================

    if unit_9_result.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 10 UNIT 9 NOT READ ONLY"
        )

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
                "UNIT 10 UNSAFE CAPABILITY: " + key
            )

    if strategy.get(
        "real_money_execution_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 10 REAL EXECUTION NOT BLOCKED"
        )

    required_protections = (
        "anti_duplicate_orders",
        "one_direction_only",
        "active_trade_mode_lock",
        "exclusive_mode",
        "flat_position_reentry_enabled",
        "require_fresh_reentry_signal",
        "require_confirmed_flat_position",
        "require_no_pending_entry_orders",
        "require_exchange_state_reconciliation",
        "block_duplicate_signal_ids",
        "block_unconfirmed_order_state",
        "reconcile_after_restart",
    )

    for key in required_protections:
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 10 PROTECTION DISABLED: " + key
            )

    # ========================================================
    # 3. VERIFY UNIT 9 OUTPUT CONTRACT
    # INDENTATION: 4 SPACES
    # ========================================================

    required_fields = (
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
        key for key in required_fields
        if key not in unit_9_result
    ]

    if missing:
        raise RuntimeError(
            "UNIT 10 MISSING UNIT 9 FIELDS: "
            + str(missing)
        )

    if any((
        unit_9_result["order_payload_created"],
        unit_9_result["tp_execution_requested"],
        unit_9_result["sl_execution_requested"],
    )):
        raise RuntimeError(
            "UNIT 10 UNEXPECTED EXECUTION STATE"
        )

    if unit_9_result.get(
        "order_submission_authorized"
    ) is not False:
        raise RuntimeError(
            "UNIT 10 UNEXPECTED ORDER AUTHORIZATION"
        )

    if unit_9_result.get(
        "reentry_authorized"
    ) is not False:
        raise RuntimeError(
            "UNIT 10 UNEXPECTED REENTRY AUTHORIZATION"
        )

    status = unit_9_result["status"]
    mode = unit_9_result["active_mode"]
    direction = unit_9_result["direction"]

    qualified = unit_9_result["signal_qualified"]
    intent = unit_9_result["execution_intent"]

    trade_plan_ready = unit_9_result[
        "trade_plan_ready"
    ]

    execution_ready = unit_9_result[
        "execution_ready"
    ]

    trade_plan = unit_9_result["trade_plan"]

    execution_candidate = unit_9_result[
        "execution_candidate"
    ]

    for value in (
        qualified,
        intent,
        trade_plan_ready,
        execution_ready,
    ):
        if not isinstance(value, bool):
            raise RuntimeError(
                "UNIT 10 INVALID BOOLEAN CONTRACT"
            )

    # ========================================================
    # 4. NORMALIZED UNIT 11 HANDOFF
    # INDENTATION: 4 SPACES
    # ========================================================

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

        "skip_reason": unit_9_result.get(
            "skip_reason"
        ) or "NO_QUALIFIED_SIGNAL",

        "order_payload_created": False,
        "demo_submission_requested": False,
        "real_submission_requested": False,
        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "backup_execution_requested": False,

        "read_only": True,

        # CONTINUOUS SCANNING
        "continuous_scan_configured":
            strategy.get(
                "continuous_entry_scan_enabled"
            ),

        "signal_id": None,
        "signal_fresh": False,
        "signal_age_ms": None,

        # RE-ENTRY SAFEGUARDS
        "flat_position_check_required": False,
        "pending_order_check_required": False,
        "exchange_reconciliation_required": False,
        "anti_duplicate_check_required": False,
        "actual_leverage_check_required": False,

        "flat_position_confirmed": False,
        "pending_orders_cleared": False,
        "exchange_state_reconciled": False,
        "actual_leverage_verified": False,

        # NO AUTHORIZATION
        "reentry_authorized": False,
        "order_submission_authorized": False,
    }

    # ========================================================
    # 5. NORMAL IDLE PATH
    # INDENTATION: 4 SPACES
    # ========================================================

    if status == "IDLE":

        if any((
            qualified,
            intent,
            trade_plan_ready,
            execution_ready,
        )):
            raise RuntimeError(
                "UNIT 10 INVALID IDLE FLAGS"
            )

        if mode != "NONE" or direction != "NONE":
            raise RuntimeError(
                "UNIT 10 INVALID IDLE MODE"
            )

        if trade_plan is not None:
            raise RuntimeError(
                "UNIT 10 IDLE TRADE PLAN NOT EMPTY"
            )

        if execution_candidate is not None:
            raise RuntimeError(
                "UNIT 10 IDLE EXECUTION CANDIDATE"
            )

        print("-" * 80, flush=True)
        print("UNIT 10 STATUS = IDLE", flush=True)

        print(
            "UNIT 10 SKIP REASON =",
            result["skip_reason"],
            flush=True,
        )

        print(
            "UNIT 10 CONTINUOUS SCAN CONFIGURED =",
            result["continuous_scan_configured"],
            flush=True,
        )

        print(
            "UNIT 10 DEMO BOUNDARY READY = FALSE",
            flush=True,
        )

        print(
            "UNIT 10 REENTRY AUTHORIZED = FALSE",
            flush=True,
        )

        print(
            "ZERO EXCHANGE WRITE = TRUE",
            flush=True,
        )

        log(
            "FRESH RECONSTRUCTION UNIT 10 "
            "RESULT = PASS (IDLE)"
        )

        print("=" * 80, flush=True)

        return result

    # ========================================================
    # 6. QUALIFIED UNIT 9 CONTRACT
    # INDENTATION: 4 SPACES
    # ========================================================

    if status != "READY":
        raise RuntimeError(
            "UNIT 10 INVALID READY STATUS"
        )

    if not all((
        qualified,
        intent,
        trade_plan_ready,
        execution_ready,
    )):
        raise RuntimeError(
            "UNIT 10 INCOMPLETE READY FLAGS"
        )

    if mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        raise RuntimeError(
            "UNIT 10 INVALID TRADING MODE"
        )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 10 INVALID DIRECTION"
        )

    if not isinstance(trade_plan, dict):
        raise RuntimeError(
            "UNIT 10 TRADE PLAN MISSING"
        )

    if not isinstance(execution_candidate, dict):
        raise RuntimeError(
            "UNIT 10 EXECUTION CANDIDATE MISSING"
        )

    if trade_plan.get("active_mode") != mode:
        raise RuntimeError(
            "UNIT 10 TRADE PLAN MODE MISMATCH"
        )

    if trade_plan.get("direction") != direction:
        raise RuntimeError(
            "UNIT 10 TRADE PLAN DIRECTION MISMATCH"
        )

    if execution_candidate.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 10 INVALID CANDIDATE ENVIRONMENT"
        )

    if execution_candidate.get(
        "read_only"
    ) is not True:
        raise RuntimeError(
            "UNIT 10 CANDIDATE NOT READ ONLY"
        )

    # ========================================================
    # 7. SIGNAL ID AND FRESHNESS
    # INDENTATION: 4 SPACES
    # ========================================================

    signal_id = unit_9_result.get("signal_id")

    if not isinstance(signal_id, str) or not signal_id:
        raise RuntimeError(
            "UNIT 10 SIGNAL ID MISSING"
        )

    if signal_id != trade_plan.get("signal_id"):
        raise RuntimeError(
            "UNIT 10 SIGNAL ID TRADE PLAN MISMATCH"
        )

    if signal_id != execution_candidate.get(
        "signal_id"
    ):
        raise RuntimeError(
            "UNIT 10 SIGNAL ID CANDIDATE MISMATCH"
        )

    if unit_9_result.get(
        "signal_fresh"
    ) is not True:
        raise RuntimeError(
            "UNIT 10 SIGNAL NOT FRESH"
        )

    try:
        market_time_ms = int(
            trade_plan["market_time_ms"]
        )
        balance_time_ms = int(
            trade_plan["balance_read_time_ms"]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 10 INVALID SNAPSHOT TIMES"
        ) from exc

    now_ms = int(time.time() * 1000)

    signal_age_ms = now_ms - market_time_ms
    balance_age_ms = now_ms - balance_time_ms

    expiry_ms = int(
        float(strategy["signal_expiry_seconds"])
        * 1000
    )

    if not -30000 <= signal_age_ms <= expiry_ms:
        result["skip_reason"] = (
            "SIGNAL_EXPIRED_BEFORE_UNIT_11"
        )

        print(
            "UNIT 10 STATUS = IDLE",
            flush=True,
        )

        print(
            "UNIT 10 SKIP REASON =",
            result["skip_reason"],
            flush=True,
        )

        return result

    if not -5000 <= balance_age_ms <= 30000:
        result["skip_reason"] = (
            "BALANCE_STALE_BEFORE_UNIT_11"
        )

        print(
            "UNIT 10 STATUS = IDLE",
            flush=True,
        )

        print(
            "UNIT 10 SKIP REASON =",
            result["skip_reason"],
            flush=True,
        )

        return result

    # ========================================================
    # 8. POSITION SIZE REVALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    sizing = trade_plan.get("position_sizing")

    if not isinstance(sizing, dict):
        raise RuntimeError(
            "UNIT 10 SIZING INFORMATION MISSING"
        )

    quantity = fresh_unit_10_decimal(
        trade_plan.get("quantity"),
        "quantity",
    )

    quantity_step = fresh_unit_10_decimal(
        precision.get("quantity_step"),
        "quantity step",
    )

    minimum_quantity = fresh_unit_10_decimal(
        precision.get("minimum_quantity"),
        "minimum quantity",
    )

    balance = fresh_unit_10_decimal(
        sizing.get("available_balance"),
        "available balance",
    )

    initial_margin = fresh_unit_10_decimal(
        sizing.get("actual_initial_margin"),
        "initial margin",
    )

    leverage_target = fresh_unit_10_decimal(
        sizing.get("leverage_target"),
        "leverage target",
    )

    if quantity_step <= 0:
        raise RuntimeError(
            "UNIT 10 INVALID QUANTITY STEP"
        )

    if quantity < minimum_quantity:
        raise RuntimeError(
            "UNIT 10 QUANTITY BELOW MINIMUM"
        )

    if quantity > Decimal("0.0004"):
        raise RuntimeError(
            "UNIT 10 INITIAL QUANTITY CAP EXCEEDED"
        )

    if quantity % quantity_step != 0:
        raise RuntimeError(
            "UNIT 10 QUANTITY STEP INVALID"
        )

    if balance <= 0 or initial_margin <= 0:
        raise RuntimeError(
            "UNIT 10 INVALID BALANCE OR MARGIN"
        )

    if initial_margin > (
        balance * Decimal("0.05")
    ):
        raise RuntimeError(
            "UNIT 10 INITIAL MARGIN ABOVE 5%"
        )

    if leverage_target != fresh_unit_10_decimal(
        strategy.get("leverage_target"),
        "configured leverage",
    ):
        raise RuntimeError(
            "UNIT 10 LEVERAGE TARGET MISMATCH"
        )

    if fresh_unit_10_decimal(
        strategy.get("exposure_cap_percent"),
        "exposure cap",
    ) > Decimal("35"):
        raise RuntimeError(
            "UNIT 10 EXPOSURE CAP ABOVE 35%"
        )

    # ========================================================
    # 9. MANDATORY UNFINISHED EXCHANGE CHECKS
    # INDENTATION: 4 SPACES
    # ========================================================

    required_checks = (
        "flat_position_check_required",
        "pending_order_check_required",
        "exchange_reconciliation_required",
        "anti_duplicate_check_required",
    )

    for key in required_checks:

        if trade_plan.get(key) is not True:
            raise RuntimeError(
                "UNIT 10 REQUIRED CHECK MISSING: "
                + key
            )

    if execution_candidate.get(
        "order_submission_authorized"
    ) is not False:
        raise RuntimeError(
            "UNIT 10 UNEXPECTED ORDER AUTHORIZATION"
        )

    if execution_candidate.get(
        "reentry_authorized"
    ) is not False:
        raise RuntimeError(
            "UNIT 10 UNEXPECTED REENTRY AUTHORIZATION"
        )

    # ========================================================
    # 10. PREPARE UNIT 11 DEMO INSTRUCTION
    # INDENTATION: 4 SPACES
    #
    # The instruction is internal and read-only.
    #
    # IMPORTANT:
    # demo_boundary_ready means only that the internal
    # preparation contract has been validated.
    # ========================================================

    demo_instruction = {
        "exchange": "WEEX",
        "api_version": "V3",
        "execution_environment": "DEMO",
        "market_symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",

        "active_mode": mode,
        "direction": direction,

        "trade_plan": trade_plan,
        "execution_candidate": execution_candidate,

        "signal_id": signal_id,
        "signal_fresh": True,
        "signal_age_ms": signal_age_ms,

        "anti_duplicate_required": True,
        "one_direction_only_required": True,
        "active_trade_mode_lock_required": True,

        "flat_position_check_required": True,
        "pending_order_check_required": True,
        "exchange_reconciliation_required": True,
        "actual_leverage_check_required": True,

        "flat_position_confirmed": False,
        "pending_orders_cleared": False,
        "exchange_state_reconciled": False,
        "actual_leverage_verified": False,

        "payload_creation_allowed": False,
        "submission_allowed": False,
        "reentry_authorized": False,

        "read_only": True,
    }

    # ========================================================
    # 11. READY HANDOFF TO UNIT 11
    # INDENTATION: 4 SPACES
    # ========================================================

    result.update({
        "status": "READY",
        "active_mode": mode,
        "direction": direction,

        "signal_qualified": True,
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": trade_plan,
        "execution_ready": True,
        "execution_candidate": execution_candidate,

        "demo_boundary_ready": True,
        "demo_submission_instruction":
            demo_instruction,

        "skip_reason": "NONE",

        "signal_id": signal_id,
        "signal_fresh": True,
        "signal_age_ms": signal_age_ms,

        "flat_position_check_required": True,
        "pending_order_check_required": True,
        "exchange_reconciliation_required": True,
        "anti_duplicate_check_required": True,
        "actual_leverage_check_required": True,

        "flat_position_confirmed": False,
        "pending_orders_cleared": False,
        "exchange_state_reconciled": False,
        "actual_leverage_verified": False,

        "order_payload_created": False,
        "demo_submission_requested": False,
        "real_submission_requested": False,
        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "backup_execution_requested": False,

        "reentry_authorized": False,
        "order_submission_authorized": False,
        "read_only": True,
    })

    # ========================================================
    # 12. FINAL SAFETY ASSERTIONS
    # INDENTATION: 4 SPACES
    # ========================================================

    for key in (
        "order_payload_created",
        "demo_submission_requested",
        "real_submission_requested",
        "tp_execution_requested",
        "sl_execution_requested",
        "backup_execution_requested",
        "reentry_authorized",
        "order_submission_authorized",
    ):
        if result[key] is not False:
            raise RuntimeError(
                "UNIT 10 EXECUTION SAFETY FAILURE: "
                + key
            )

    if demo_instruction[
        "submission_allowed"
    ] is not False:
        raise RuntimeError(
            "UNIT 10 SUBMISSION NOT BLOCKED"
        )

    # ========================================================
    # 13. RENDER LOGGING
    # INDENTATION: 4 SPACES
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "UNIT 10 STATUS = READY",
        flush=True,
    )

    print(
        "UNIT 10 ACTIVE MODE =",
        mode,
        flush=True,
    )

    print(
        "UNIT 10 DIRECTION =",
        direction,
        flush=True,
    )

    print(
        "UNIT 10 SIGNAL ID =",
        signal_id,
        flush=True,
    )

    print(
        "UNIT 10 SIGNAL AGE MS =",
        signal_age_ms,
        flush=True,
    )

    print(
        "UNIT 10 BTC QUANTITY =",
        float(quantity),
        flush=True,
    )

    print(
        "UNIT 10 INITIAL MARGIN =",
        float(initial_margin),
        flush=True,
    )

    print(
        "UNIT 10 LEVERAGE TARGET =",
        float(leverage_target),
        flush=True,
    )

    print(
        "UNIT 10 DEMO BOUNDARY READY = TRUE",
        flush=True,
    )

    print(
        "UNIT 10 FLAT POSITION CHECK = REQUIRED",
        flush=True,
    )

    print(
        "UNIT 10 PENDING ORDER CHECK = REQUIRED",
        flush=True,
    )

    print(
        "UNIT 10 ANTI-DUPLICATE CHECK = REQUIRED",
        flush=True,
    )

    print(
        "UNIT 10 EXCHANGE RECONCILIATION = REQUIRED",
        flush=True,
    )

    print(
        "UNIT 10 ACTUAL LEVERAGE CHECK = REQUIRED",
        flush=True,
    )

    print(
        "UNIT 10 REENTRY AUTHORIZED = FALSE",
        flush=True,
    )

    print(
        "UNIT 10 PAYLOAD CREATION ALLOWED = FALSE",
        flush=True,
    )

    print(
        "UNIT 10 ORDER SUBMISSION AUTHORIZED = FALSE",
        flush=True,
    )

    print(
        "PASS: UNIT 10 UNIT 11 CONTRACT PREPARED",
        flush=True,
    )

    print(
        "PASS: UNIT 10 NO NETWORK REQUEST",
        flush=True,
    )

    print(
        "PASS: UNIT 10 NO ORDER PAYLOAD",
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

    log(
        "FRESH RECONSTRUCTION UNIT 10 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# INITIAL UNIT 10 EXECUTION
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_10_RESULT = (
    fresh_reconstruction_unit_10(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_9_RESULT,
    )
)


# ============================================================
# UNIT 10 REUSABLE REFRESH FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_refresh_unit_10(
    unit_9_result=None
):

    global FRESH_RECONSTRUCTION_UNIT_10_RESULT

    if unit_9_result is None:
        unit_9_result = (
            FRESH_RECONSTRUCTION_UNIT_9_RESULT
        )

    refreshed = fresh_reconstruction_unit_10(
        FRESH_RECONSTRUCTION_CONFIG,
        unit_9_result,
    )

    FRESH_RECONSTRUCTION_UNIT_10_RESULT = (
        refreshed
    )

    return refreshed


# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 10
# ZERO INDENTATION DEMARCATION
#
# UNIT 10 FULLY CLOSED
# INITIAL EXECUTION COMPLETED
# REFRESH FUNCTION CREATED
# UNIT 11 HANDOFF PRESERVED
#
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN TRY
# NO OPEN LOOP
# NO OPEN DICTIONARY
#
# EXISTING UNIT 11 CONTINUES DIRECTLY BELOW
# ============================================================



# ============================================================
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 11
# ZERO INDENTATION DEMARCATION
# ============================================================
#
# COORDINATED DEMO INSTRUCTION SAFETY BOUNDARY
#
# RESPONSIBILITIES:
# - Receive Unit 10 result
# - Preserve existing Unit 12 interface
# - Validate internal demo trade preparation
# - Preserve signal identity and freshness
# - Validate initial quantity and margin
# - Track unfinished re-entry checks
# - Keep demo entry submission paused
#
# IMPORTANT:
# Unit 12 must not receive READY until its
# coordinated protection correction is completed.
#
# ZERO ORDER PAYLOAD
# ZERO DEMO ORDER
# ZERO REAL ORDER
# ZERO EXCHANGE WRITE
# ============================================================

import time
from decimal import Decimal, InvalidOperation


# ============================================================
# UNIT 11 DECIMAL HELPER
# ZERO INDENTATION
# ============================================================

def fresh_unit_11_decimal(value, name):

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 11 INVALID NUMBER: " + name
        ) from exc

    if not number.is_finite():
        raise RuntimeError(
            "UNIT 11 NON-FINITE NUMBER: " + name
        )

    return number


# ============================================================
# UNIT 11 MAIN FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_11(
    config,
    unit_10_result,
):

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 11 START")

    # ========================================================
    # 1. VALIDATE CONFIGURATION
    # INDENTATION: 4 SPACES
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 11 CONFIGURATION MISSING"
        )

    if not isinstance(unit_10_result, dict):
        raise RuntimeError(
            "UNIT 11 UNIT 10 RESULT MISSING"
        )

    exchange = config.get("exchange")
    safety = config.get("safety")
    strategy = config.get("strategy")
    precision = config.get("market_precision")

    for name, section in (
        ("EXCHANGE", exchange),
        ("SAFETY", safety),
        ("STRATEGY", strategy),
        ("PRECISION", precision),
    ):
        if not isinstance(section, dict):
            raise RuntimeError(
                "UNIT 11 CONFIG MISSING: " + name
            )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 11 REAL ENVIRONMENT PROHIBITED"
        )

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 11 INVALID EXCHANGE"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 11 INVALID API VERSION"
        )

    if exchange.get("market_symbol") != "BTCUSDT":
        raise RuntimeError(
            "UNIT 11 INVALID MARKET SYMBOL"
        )

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 11 INVALID DEMO SYMBOL"
        )

    # ========================================================
    # 2. READ-ONLY SAFETY CONTRACT
    # INDENTATION: 4 SPACES
    # ========================================================

    if unit_10_result.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 11 UNIT 10 NOT READ ONLY"
        )

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
                "UNIT 11 UNSAFE CAPABILITY: " + key
            )

    if strategy.get(
        "real_money_execution_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 11 REAL EXECUTION NOT BLOCKED"
        )

    required_protections = (
        "anti_duplicate_orders",
        "one_direction_only",
        "active_trade_mode_lock",
        "exclusive_mode",
        "require_confirmed_flat_position",
        "require_no_pending_entry_orders",
        "require_exchange_state_reconciliation",
        "require_fresh_reentry_signal",
        "block_duplicate_signal_ids",
        "block_unconfirmed_order_state",
        "reconcile_after_restart",
    )

    for key in required_protections:
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 11 PROTECTION DISABLED: " + key
            )

    # ========================================================
    # 3. VERIFY UNIT 10 OUTPUT
    # INDENTATION: 4 SPACES
    # ========================================================

    required_fields = (
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
        "read_only",
    )

    for key in required_fields:
        if key not in unit_10_result:
            raise RuntimeError(
                "UNIT 11 MISSING UNIT 10 FIELD: " + key
            )

    for key in (
        "order_payload_created",
        "demo_submission_requested",
        "real_submission_requested",
        "tp_execution_requested",
        "sl_execution_requested",
        "backup_execution_requested",
        "reentry_authorized",
        "order_submission_authorized",
    ):
        if unit_10_result.get(key) is not False:
            raise RuntimeError(
                "UNIT 11 UNSAFE UNIT 10 STATE: " + key
            )

    source_status = unit_10_result["status"]

    # ========================================================
    # 4. NORMALIZED UNIT 12-SAFE RESULT
    # INDENTATION: 4 SPACES
    #
    # status MUST remain IDLE while Unit 12 still
    # contains its original submission behavior.
    # ========================================================

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
        "skip_reason": "NO_QUALIFIED_SIGNAL",

        "order_payload_created": False,
        "demo_submission_requested": False,
        "real_submission_requested": False,
        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "backup_execution_requested": False,

        "read_only": True,

        # INTERNAL COORDINATION DIAGNOSTICS
        "preparation_status": "IDLE",
        "prepared_candidate": None,
        "signal_id": None,
        "signal_fresh": False,
        "continuous_scan_configured":
            strategy.get(
                "continuous_entry_scan_enabled"
            ),

        "flat_position_confirmed": False,
        "pending_orders_cleared": False,
        "exchange_state_reconciled": False,
        "actual_leverage_verified": False,
        "anti_duplicate_verified": False,

        "reentry_authorized": False,
        "order_submission_authorized": False,
    }

    # ========================================================
    # 5. NORMAL IDLE PATH
    # INDENTATION: 4 SPACES
    # ========================================================

    if source_status == "IDLE":

        if any((
            unit_10_result["signal_qualified"],
            unit_10_result["execution_intent"],
            unit_10_result["trade_plan_ready"],
            unit_10_result["execution_ready"],
            unit_10_result["demo_boundary_ready"],
        )):
            raise RuntimeError(
                "UNIT 11 INCONSISTENT IDLE FLAGS"
            )

        result["skip_reason"] = (
            unit_10_result.get("skip_reason")
            or "UNIT_10_IDLE"
        )

        print("UNIT 11 STATUS = IDLE", flush=True)
        print(
            "UNIT 11 SKIP REASON =",
            result["skip_reason"],
            flush=True,
        )

        log(
            "FRESH RECONSTRUCTION UNIT 11 "
            "RESULT = PASS (IDLE)"
        )

        print("=" * 80, flush=True)

        return result

    # ========================================================
    # 6. VALIDATE INTERNALLY READY SIGNAL
    # INDENTATION: 4 SPACES
    # ========================================================

    if source_status != "READY":
        raise RuntimeError(
            "UNIT 11 INVALID UNIT 10 STATUS"
        )

    for key in (
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "execution_ready",
        "demo_boundary_ready",
    ):
        if unit_10_result.get(key) is not True:
            raise RuntimeError(
                "UNIT 11 MISSING READY FLAG: " + key
            )

    mode = unit_10_result["active_mode"]
    direction = unit_10_result["direction"]

    if mode not in (
        "SCALP", "STRUCTURE", "BREAKOUT"
    ):
        raise RuntimeError(
            "UNIT 11 INVALID TRADING MODE"
        )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 11 INVALID DIRECTION"
        )

    trade_plan = unit_10_result["trade_plan"]
    instruction = unit_10_result[
        "demo_submission_instruction"
    ]

    if not isinstance(trade_plan, dict):
        raise RuntimeError(
            "UNIT 11 TRADE PLAN MISSING"
        )

    if not isinstance(instruction, dict):
        raise RuntimeError(
            "UNIT 11 INTERNAL INSTRUCTION MISSING"
        )

    if instruction.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 11 INSTRUCTION NOT READ ONLY"
        )

    if instruction.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 11 INSTRUCTION NOT DEMO"
        )

    if instruction.get(
        "submission_allowed"
    ) is not False:
        raise RuntimeError(
            "UNIT 11 SUBMISSION NOT BLOCKED"
        )

    if instruction.get(
        "payload_creation_allowed"
    ) is not False:
        raise RuntimeError(
            "UNIT 11 PAYLOAD CREATION NOT BLOCKED"
        )

    # ========================================================
    # 7. SIGNAL ID AND FRESHNESS
    # INDENTATION: 4 SPACES
    # ========================================================

    signal_id = unit_10_result.get("signal_id")

    if not isinstance(signal_id, str) or not signal_id:
        raise RuntimeError(
            "UNIT 11 SIGNAL ID MISSING"
        )

    if trade_plan.get("signal_id") != signal_id:
        raise RuntimeError(
            "UNIT 11 TRADE PLAN SIGNAL MISMATCH"
        )

    if instruction.get("signal_id") != signal_id:
        raise RuntimeError(
            "UNIT 11 INSTRUCTION SIGNAL MISMATCH"
        )

    market_time = int(
        trade_plan["market_time_ms"]
    )

    balance_time = int(
        trade_plan["balance_read_time_ms"]
    )

    now_ms = int(time.time() * 1000)

    signal_age = now_ms - market_time
    balance_age = now_ms - balance_time

    expiry_ms = int(
        float(strategy["signal_expiry_seconds"])
        * 1000
    )

    if not (-30000 <= signal_age <= expiry_ms):
        result["skip_reason"] = (
            "SIGNAL_EXPIRED_AT_UNIT_11"
        )
        return result

    if not (-5000 <= balance_age <= 30000):
        result["skip_reason"] = (
            "BALANCE_STALE_AT_UNIT_11"
        )
        return result

    # ========================================================
    # 8. POSITION SIZE REVALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    sizing = trade_plan.get("position_sizing")

    if not isinstance(sizing, dict):
        raise RuntimeError(
            "UNIT 11 SIZING MISSING"
        )

    quantity = fresh_unit_11_decimal(
        trade_plan.get("quantity"),
        "quantity",
    )

    step = fresh_unit_11_decimal(
        precision["quantity_step"],
        "quantity_step",
    )

    minimum = fresh_unit_11_decimal(
        precision["minimum_quantity"],
        "minimum_quantity",
    )

    balance = fresh_unit_11_decimal(
        sizing.get("available_balance"),
        "balance",
    )

    initial_margin = fresh_unit_11_decimal(
        sizing.get("actual_initial_margin"),
        "initial_margin",
    )

    target_leverage = fresh_unit_11_decimal(
        sizing.get("leverage_target"),
        "leverage",
    )

    if step <= 0 or quantity < minimum:
        raise RuntimeError(
            "UNIT 11 INVALID QUANTITY"
        )

    if quantity > Decimal("0.0004"):
        raise RuntimeError(
            "UNIT 11 QUANTITY CAP EXCEEDED"
        )

    if quantity % step != 0:
        raise RuntimeError(
            "UNIT 11 QUANTITY STEP FAILURE"
        )

    if balance <= 0 or initial_margin <= 0:
        raise RuntimeError(
            "UNIT 11 INVALID BALANCE OR MARGIN"
        )

    if initial_margin > balance * Decimal("0.05"):
        raise RuntimeError(
            "UNIT 11 INITIAL MARGIN ABOVE 5%"
        )

    if target_leverage != fresh_unit_11_decimal(
        strategy["leverage_target"],
        "configured_leverage",
    ):
        raise RuntimeError(
            "UNIT 11 LEVERAGE TARGET MISMATCH"
        )

    # ========================================================
    # 9. VERIFY UNFINISHED EXCHANGE CHECKS
    # INDENTATION: 4 SPACES
    # ========================================================

    mandatory = (
        "flat_position_check_required",
        "pending_order_check_required",
        "exchange_reconciliation_required",
        "actual_leverage_check_required",
    )

    for key in mandatory:
        if instruction.get(key) is not True:
            raise RuntimeError(
                "UNIT 11 REQUIRED CHECK MISSING: " + key
            )

    for key in (
        "flat_position_confirmed",
        "pending_orders_cleared",
        "exchange_state_reconciled",
        "actual_leverage_verified",
    ):
        if instruction.get(key) is not False:
            raise RuntimeError(
                "UNIT 11 UNEXPECTED VERIFIED STATE: " + key
            )

    # ========================================================
    # 10. PRESERVE INTERNAL PREPARATION DIAGNOSTICS
    # INDENTATION: 4 SPACES
    #
    # The actual Unit 12 status remains IDLE.
    # No order payload is constructed.
    # ========================================================

    prepared = {
        "mode": mode,
        "direction": direction,
        "signal_id": signal_id,
        "quantity": str(quantity),
        "target_leverage": str(target_leverage),
        "signal_age_ms": signal_age,

        "flat_position_check_required": True,
        "pending_order_check_required": True,
        "exchange_reconciliation_required": True,
        "actual_leverage_check_required": True,
        "anti_duplicate_check_required": True,

        "exchange_checks_completed": False,
        "submission_allowed": False,
        "read_only": True,
    }

    result["preparation_status"] = "PREPARED_BLOCKED"
    result["prepared_candidate"] = prepared
    result["signal_id"] = signal_id
    result["signal_fresh"] = True

    result["skip_reason"] = (
        "DEMO_EXECUTION_PAUSED_PENDING_COORDINATED_"
        "UNIT_12_AND_RUNTIME_VALIDATION"
    )

    # ========================================================
    # 11. FINAL SAFETY ASSERTIONS
    # INDENTATION: 4 SPACES
    # ========================================================

    if result["status"] != "IDLE":
        raise RuntimeError(
            "UNIT 11 UNSAFE UNIT 12 HANDOFF STATUS"
        )

    if result["order_payload"] is not None:
        raise RuntimeError(
            "UNIT 11 UNEXPECTED ORDER PAYLOAD"
        )

    if result["execution_intent"] is not False:
        raise RuntimeError(
            "UNIT 11 EXECUTION INTENT NOT BLOCKED"
        )

    if result["demo_boundary_ready"] is not False:
        raise RuntimeError(
            "UNIT 11 DEMO BOUNDARY NOT BLOCKED"
        )

    if result["order_submission_authorized"] is not False:
        raise RuntimeError(
            "UNIT 11 ORDER AUTHORIZATION VIOLATION"
        )

    # ========================================================
    # 12. RENDER LOGGING
    # INDENTATION: 4 SPACES
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "UNIT 11 PREPARATION STATUS = PREPARED_BLOCKED",
        flush=True,
    )

    print(
        "UNIT 11 ACTIVE CANDIDATE MODE =",
        mode,
        flush=True,
    )

    print(
        "UNIT 11 CANDIDATE DIRECTION =",
        direction,
        flush=True,
    )

    print(
        "UNIT 11 SIGNAL ID =",
        signal_id,
        flush=True,
    )

    print(
        "UNIT 11 INITIAL BTC QUANTITY =",
        quantity,
        flush=True,
    )

    print(
        "UNIT 11 POSITION CHECK = NOT YET VERIFIED",
        flush=True,
    )

    print(
        "UNIT 11 PENDING ORDERS = NOT YET VERIFIED",
        flush=True,
    )

    print(
        "UNIT 11 DUPLICATE PROTECTION = NOT YET VERIFIED",
        flush=True,
    )

    print(
        "UNIT 11 ACTUAL LEVERAGE = NOT YET VERIFIED",
        flush=True,
    )

    print(
        "UNIT 11 HANDOFF STATUS TO UNIT 12 = IDLE",
        flush=True,
    )

    print(
        "UNIT 11 ORDER PAYLOAD = NONE",
        flush=True,
    )

    print(
        "UNIT 11 DEMO SUBMISSION = BLOCKED",
        flush=True,
    )

    print(
        "UNIT 11 REAL SUBMISSION = BLOCKED",
        flush=True,
    )

    print(
        "UNIT 11 EXCHANGE WRITE = FALSE",
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 11 "
        "RESULT = PASS (PREPARED_BLOCKED)"
    )

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
# UNIT 11 REUSABLE REFRESH FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_refresh_unit_11(
    unit_10_result=None
):

    global FRESH_RECONSTRUCTION_UNIT_11_RESULT

    if unit_10_result is None:
        unit_10_result = (
            FRESH_RECONSTRUCTION_UNIT_10_RESULT
        )

    refreshed = fresh_reconstruction_unit_11(
        FRESH_RECONSTRUCTION_CONFIG,
        unit_10_result,
    )

    FRESH_RECONSTRUCTION_UNIT_11_RESULT = refreshed

    return refreshed


# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 11
# ZERO INDENTATION DEMARCATION
#
# UNIT 11 FULLY CLOSED
# UNIT 11 CALLED ONCE
# REFRESH FUNCTION CREATED
# UNIT 12 HANDOFF PRESERVED
# ORDER PAYLOAD DISABLED
# DEMO ENTRY SUBMISSION BLOCKED
# REAL TRADING BLOCKED
#
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN TRY
# NO OPEN LOOP
# NO OPEN DICTIONARY
#
# EXISTING UNIT 12 CONTINUES DIRECTLY BELOW
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
    # 3. LEVERAGE + ESTIMATED TRANSACTION COST
    # ========================================================

    leverage_target = Decimal(
        str(
            strategy.get(
                "leverage_target",
                100,
            )
        )
    )

    if (
        leverage_target
        <=
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: INVALID LEVERAGE"
        )

    # --------------------------------------------------------
    # Conservative base/default WEEX futures taker fee.
    #
    # User may later override this in Unit 2:
    #
    # "futures_taker_fee_percent": 0.08
    #
    # Percentage here is NOTIONAL percentage.
    # --------------------------------------------------------

    futures_taker_fee_percent = Decimal(
        str(
            strategy.get(
                "futures_taker_fee_percent",
                0.08,
            )
        )
    )

    if (
        futures_taker_fee_percent
        <
        Decimal("0")
    ):
        raise RuntimeError(
            "UNIT 13 BLOCKED: INVALID TAKER FEE"
        )

    # --------------------------------------------------------
    # Entry + exit fee.
    #
    # Example:
    #
    # 0.08% entry
    # +
    # 0.08% exit
    # =
    # 0.16% notional round-trip estimate.
    #
    # At 100x leverage this corresponds to approximately
    # 16% ROI drag relative to initial margin.
    # --------------------------------------------------------

    estimated_round_trip_fee_price_percent = (
        futures_taker_fee_percent
        *
        Decimal("2")
    )

    estimated_round_trip_fee_roi_percent = (
        estimated_round_trip_fee_price_percent
        *
        leverage_target
    )

    # --------------------------------------------------------
    # Required gross leveraged ROI:
    #
    # gross ROI
    # -
    # estimated fee ROI drag
    # =
    # estimated net ROI
    #
    # Therefore:
    #
    # gross required
    # =
    # net floor
    # +
    # fee drag
    # --------------------------------------------------------

    tp1_required_gross_roi = (
        tp1_net_roi_floor
        +
        estimated_round_trip_fee_roi_percent
    )

    tp2_required_gross_roi = (
        tp2_net_roi_floor
        +
        estimated_round_trip_fee_roi_percent
    )

    # Mandatory ROI separation.

    minimum_tp2_from_tp1 = (
        tp1_required_gross_roi
        +
        tp1_tp2_min_roi_separation
    )

    if (
        tp2_required_gross_roi
        <
        minimum_tp2_from_tp1
    ):
        tp2_required_gross_roi = (
            minimum_tp2_from_tp1
        )

    tp1_price_move_percent = (
        tp1_required_gross_roi
        /
        leverage_target
    )

    tp2_price_move_percent = (
        tp2_required_gross_roi
        /
        leverage_target
    )

    print(
        "UNIT 13 LEVERAGE = "
        f"{leverage_target}x",
        flush=True,
    )

    print(
        "UNIT 13 ESTIMATED TAKER FEE = "
        f"{futures_taker_fee_percent}% NOTIONAL / SIDE",
        flush=True,
    )

    print(
        "UNIT 13 ESTIMATED ROUND-TRIP FEE = "
        f"{estimated_round_trip_fee_price_percent}% NOTIONAL",
        flush=True,
    )

    print(
        "UNIT 13 ESTIMATED FEE ROI DRAG = "
        f"{estimated_round_trip_fee_roi_percent}%",
        flush=True,
    )

    print(
        "UNIT 13 TP1 REQUIRED GROSS ROI = "
        f"{tp1_required_gross_roi}%",
        flush=True,
    )

    print(
        "UNIT 13 TP2 REQUIRED GROSS ROI = "
        f"{tp2_required_gross_roi}%",
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
            "UNIT 13 BLOCKED: INVALID POSITION SIZE"
        )

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

    max_backups = min(
        max(
            max_backups,
            0,
        ),
        3,
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
        "B3 -> L3 -> STOP",
        flush=True,
    )

    print(
        "PASS: UNIT 14 B4 = DISABLED",
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

    def get_active_position():

        records = authenticated_get(
            "/capi/v3/sim/position/allPosition"
        )

        if not isinstance(
            records,
            list,
        ):
            return None

        active_records = []

        for record in records:

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
                demo_symbol
            ):
                continue

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

            if (
                size
                >
                Decimal("0")
            ):
                active_records.append(
                    record
                )

        if not active_records:

            return None

        directions = {
            str(
                record.get(
                    "side",
                    "",
                )
            ).upper()
            for record in active_records
        }

        directions.discard(
            ""
        )

        if (
            len(directions)
            >
            1
        ):
            raise RuntimeError(
                "UNIT 14 BLOCKED: "
                "OPPOSING POSITIONS DETECTED"
            )

        if (
            len(active_records)
            >
            1
        ):
            raise RuntimeError(
                "UNIT 14 BLOCKED: "
                "MULTIPLE ACTIVE BTCSUSDT POSITIONS"
            )

        return (
            active_records[0]
        )

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

    def get_order_history():

        query = urllib.parse.urlencode(
            {
                "symbol":
                    demo_symbol,

                "limit":
                    1000,

                "page":
                    0,
            }
        )

        history = authenticated_get(
            "/capi/v3/sim/order/history",
            query,
        )

        if not isinstance(
            history,
            list,
        ):
            return []

        return history

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
    


    last_confirmed_backup_stage = None

    runtime_cycle = 0

    poll_seconds = 5

    last_runtime_order_time = 0.0

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

        if position is None:

            print(
                "-" * 80,
                flush=True,
            )

            print(
                "UNIT 14 ACTIVE POSITION EXISTS = FALSE",
                flush=True,
            )

            print(
                "UNIT 14 RUNTIME STATUS = POSITION_CLOSED",
                flush=True,
            )

            print(
                "PASS: UNIT 14 TP3 MANAGEMENT COMPLETE",
                flush=True,
            )

            print(
                "PASS: UNIT 14 BACKUP MANAGEMENT COMPLETE",
                flush=True,
            )

            print(
                "=" * 80,
                flush=True,
            )

            return {
                "unit":
                    14,

                "status":
                    "POSITION_CLOSED",

                "exchange_write":
                    False,

                "real_order":
                    False,

                "sl_enabled":
                    False,
            }

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

        if (
            next_backup_stage
            >
            3
        ):

            print(
                "UNIT 14 BACKUP STOP = NO B4",
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
        # 13D. EXPOSURE CAP
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
            "UNIT 14 CURRENT CONFIGURED EXPOSURE % = "
            f"{current_configured_exposure}",
            flush=True,
        )

        print(
            "UNIT 14 PROJECTED EXPOSURE % = "
            f"{projected_exposure}",
            flush=True,
        )

        print(
            "UNIT 14 EXPOSURE CAP % = "
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
        # 13E. DEMO BALANCE
        # ====================================================

        try:

            balance_item = (
                get_demo_balance()
            )

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
                "UNIT 14 BALANCE READ ERROR = "
                f"{repr(exc)}",
                flush=True,
            )

            time.sleep(
                poll_seconds
            )

            continue

        if (
            available_balance
            <=
            Decimal("0")
        ):

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
        # 13F. BACKUP QUANTITY
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
# RUN UNIT 14
# ============================================================

FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    fresh_tp3_runtime(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_13_RESULT,
    )
)


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


