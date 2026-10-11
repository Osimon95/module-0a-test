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
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 12
# ZERO INDENTATION DEMARCATION
# ============================================================
#
# WEEX DEMO POSITION AND RE-ENTRY SAFETY GATE
#
# - Accepts Unit 11 IDLE / PREPARED_BLOCKED
# - Performs authenticated DEMO position GET only
# - Detects existing BTC demo positions
# - Does not assume pending orders are cleared
# - Does not assume actual leverage is verified
# - Does not authorize an entry
# - Preserves independent Unit 13 position management
# - No initial entry, TP, SL or backup submission
# - No real-money exchange access
#
# ZERO EXCHANGE WRITE
# ============================================================

import os
import time
import json
import hmac
import hashlib
import base64
import urllib.request
import urllib.error

from decimal import Decimal, InvalidOperation


# ============================================================
# UNIT 12 MASTER BOT SWITCH
# ZERO INDENTATION
#
# RUN   = scanning permitted; submissions still blocked
# PAUSE = new entry scanning and submissions paused
#
# DEFAULT PAUSE DURING INTEGRATION
# ============================================================

BOT_MODE = os.getenv(
    "BOT_MODE", "PAUSE"
).strip().upper()

if BOT_MODE not in ("RUN", "PAUSE"):
    raise RuntimeError(
        "UNIT 12 INVALID BOT_MODE"
    )


# ============================================================
# UNIT 12 AUTHENTICATED DEMO GET HELPER
# ZERO INDENTATION
# ============================================================

def fresh_unit_12_demo_get(path):

    if path != "/capi/v3/sim/position/allPosition":
        raise RuntimeError(
            "UNIT 12 ENDPOINT NOT ALLOWED"
        )

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
            "UNIT 12 DEMO READ CREDENTIALS MISSING"
        )

    timestamp = str(int(time.time() * 1000))

    prehash = timestamp + "GET" + path

    signature = base64.b64encode(
        hmac.new(
            api_secret.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Fresh-WEEX-Unit12",
    }

    url = (
        "https://api-contract.weex.com"
        + path
    )

    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    if request.get_method() != "GET":
        raise RuntimeError(
            "UNIT 12 NON-GET REQUEST BLOCKED"
        )

    if request.data is not None:
        raise RuntimeError(
            "UNIT 12 REQUEST BODY BLOCKED"
        )

    with urllib.request.urlopen(
        request,
        timeout=15,
    ) as response:

        if response.getcode() != 200:
            raise RuntimeError(
                "UNIT 12 DEMO GET HTTP FAILURE"
            )

        raw = response.read().decode("utf-8")

    data = json.loads(raw)

    if not isinstance(data, list):
        raise RuntimeError(
            "UNIT 12 UNEXPECTED POSITION RESPONSE"
        )

    return data


# ============================================================
# UNIT 12 POSITION NORMALIZATION
# ZERO INDENTATION
# ============================================================

def fresh_unit_12_parse_positions(records):

    if not isinstance(records, list):
        raise RuntimeError(
            "UNIT 12 POSITION LIST INVALID"
        )

    active = []

    for record in records:

        if not isinstance(record, dict):
            raise RuntimeError(
                "UNIT 12 POSITION RECORD INVALID"
            )

        symbol = str(
            record.get("symbol", "")
        ).upper()

        if symbol != "BTCSUSDT":
            continue

        if "size" not in record:
            raise RuntimeError(
                "UNIT 12 BTC POSITION SIZE MISSING"
            )

        try:
            size = Decimal(
                str(record["size"])
            )
        except (InvalidOperation, TypeError) as exc:
            raise RuntimeError(
                "UNIT 12 BTC POSITION SIZE INVALID"
            ) from exc

        if not size.is_finite():
            raise RuntimeError(
                "UNIT 12 NON-FINITE POSITION SIZE"
            )

        if size < 0:
            raise RuntimeError(
                "UNIT 12 NEGATIVE POSITION SIZE"
            )

        if size > 0:

            active.append({
                "symbol": symbol,
                "size": str(size),
                "side": record.get(
                    "positionSide",
                    record.get("side"),
                ),
                "leverage": record.get(
                    "leverage"
                ),
                "marginType": record.get(
                    "marginType"
                ),
                "id": record.get("id"),
            })

    return active


# ============================================================
# UNIT 12 MAIN SAFETY GATE
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_12(
    config,
    unit_11_result,
):

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 12 START")

    # ========================================================
    # 1. VERIFY CONFIGURATION
    # INDENTATION: 4 SPACES
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 12 CONFIGURATION MISSING"
        )

    if not isinstance(unit_11_result, dict):
        raise RuntimeError(
            "UNIT 12 UNIT 11 RESULT MISSING"
        )

    exchange = config.get("exchange")
    strategy = config.get("strategy")

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 12 EXCHANGE CONFIGURATION MISSING"
        )

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 12 STRATEGY CONFIGURATION MISSING"
        )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 12 REAL ENVIRONMENT PROHIBITED"
        )

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 12 INVALID EXCHANGE"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 12 INVALID API VERSION"
        )

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 12 INVALID DEMO SYMBOL"
        )

    if unit_11_result.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 12 UNIT 11 NOT READ ONLY"
        )

    if strategy.get(
        "real_money_execution_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 12 REAL EXECUTION ENABLED"
        )

    # ========================================================
    # 2. INITIAL FAIL-CLOSED RESULT
    # INDENTATION: 4 SPACES
    # ========================================================

    result = {
        "unit": 12,
        "status": "IDLE",
        "read_only": True,

        "active_mode": "NONE",
        "direction": "NONE",
        "signal_qualified": False,
        "execution_intent": False,

        "preparation_status":
            unit_11_result.get(
                "preparation_status", "IDLE"
            ),

        "signal_id":
            unit_11_result.get("signal_id"),

        "position_check_attempted": False,
        "position_check_completed": False,
        "position_endpoint_access": False,

        "active_position_exists": False,
        "active_positions": [],

        "flat_position_confirmed": False,
        "pending_orders_cleared": False,
        "actual_leverage_verified": False,
        "exchange_state_reconciled": False,
        "anti_duplicate_verified": False,

        "demo_submission_attempted": False,
        "demo_submission_completed": False,
        "real_submission_attempted": False,

        "authenticated_request": False,
        "order_endpoint_access": False,
        "exchange_write": False,

        "reentry_authorized": False,
        "order_submission_authorized": False,

        "skip_reason": "NO_QUALIFIED_SIGNAL",
    }

    # ========================================================
    # 3. BOT MODE
    # INDENTATION: 4 SPACES
    # ========================================================

    print(
        "BOT MODE =",
        BOT_MODE,
        flush=True,
    )

    if BOT_MODE == "PAUSE":

        result["skip_reason"] = "BOT_MODE_PAUSE"

        print(
            "UNIT 12 INITIAL ENTRIES = PAUSED",
            flush=True,
        )

        print(
            "UNIT 12 POSITION MANAGEMENT = "
            "INDEPENDENT UNIT 13/14",
            flush=True,
        )

        return result

    # ========================================================
    # 4. UNIT 11 SAFETY BOUNDARY
    # INDENTATION: 4 SPACES
    # ========================================================

    if unit_11_result.get("status") != "IDLE":
        raise RuntimeError(
            "UNIT 12 UNEXPECTED UNIT 11 STATUS"
        )

    if unit_11_result.get(
        "order_submission_authorized"
    ) is not False:
        raise RuntimeError(
            "UNIT 12 UNSAFE ORDER AUTHORIZATION"
        )

    if unit_11_result.get(
        "order_payload"
    ) is not None:
        raise RuntimeError(
            "UNIT 12 ORDER PAYLOAD MUST BE NONE"
        )

    preparation_status = unit_11_result.get(
        "preparation_status", "IDLE"
    )

    if preparation_status == "IDLE":

        result["skip_reason"] = (
            unit_11_result.get("skip_reason")
            or "UNIT_11_IDLE"
        )

        print(
            "UNIT 12 STATUS = IDLE",
            flush=True,
        )

        print(
            "UNIT 12 SKIP REASON =",
            result["skip_reason"],
            flush=True,
        )

        return result

    if preparation_status != "PREPARED_BLOCKED":
        raise RuntimeError(
            "UNIT 12 UNKNOWN PREPARATION STATUS"
        )

    prepared = unit_11_result.get(
        "prepared_candidate"
    )

    if not isinstance(prepared, dict):
        raise RuntimeError(
            "UNIT 12 PREPARED CANDIDATE MISSING"
        )

    if prepared.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 12 PREPARED CANDIDATE UNSAFE"
        )

    if prepared.get("submission_allowed") is not False:
        raise RuntimeError(
            "UNIT 12 SUBMISSION NOT BLOCKED"
        )

    if prepared.get("exchange_checks_completed") is not False:
        raise RuntimeError(
            "UNIT 12 UNEXPECTED COMPLETED CHECKS"
        )

    # ========================================================
    # 5. READ CURRENT DEMO POSITION
    # INDENTATION: 4 SPACES
    #
    # This is a diagnostic exchange read only.
    # No order is submitted even if position is flat.
    # ========================================================

    result["position_check_attempted"] = True

    try:

        records = fresh_unit_12_demo_get(
            "/capi/v3/sim/position/allPosition"
        )

        result["authenticated_request"] = True
        result["position_endpoint_access"] = True

        active = fresh_unit_12_parse_positions(
            records
        )

    except Exception as exc:

        result["skip_reason"] = (
            "DEMO_POSITION_VERIFICATION_FAILED"
        )

        print(
            "UNIT 12 POSITION CHECK ERROR =",
            repr(exc),
            flush=True,
        )

        print(
            "UNIT 12 ENTRY = BLOCKED",
            flush=True,
        )

        return result

    result["position_check_completed"] = True
    result["active_positions"] = active

    result["active_position_exists"] = (
        len(active) > 0
    )

    result["flat_position_confirmed"] = (
        len(active) == 0
    )

    # ========================================================
    # 6. ACTIVE POSITION PROTECTION
    # INDENTATION: 4 SPACES
    # ========================================================

    if result["active_position_exists"]:

        result["status"] = "BLOCKED_ACTIVE_POSITION"
        result["skip_reason"] = (
            "NON_ZERO_DEMO_POSITION_BLOCK"
        )

        print(
            "UNIT 12 ACTIVE POSITION COUNT =",
            len(active),
            flush=True,
        )

        print(
            "UNIT 12 ENTRY = BLOCKED",
            flush=True,
        )

        print(
            "UNIT 12 EXISTING POSITION MANAGEMENT = "
            "UNIT 13/14",
            flush=True,
        )

        return result

    # ========================================================
    # 7. FLAT DOES NOT EQUAL AUTHORIZED
    # INDENTATION: 4 SPACES
    #
    # Pending orders and actual leverage are not yet
    # independently verified by this correction.
    #
    # Never infer their status from position size zero.
    # ========================================================

    result["status"] = "FLAT_PENDING_CHECKS"

    result["skip_reason"] = (
        "PENDING_ORDERS_LEVERAGE_AND_DUPLICATE_"
        "RECONCILIATION_NOT_COMPLETED"
    )

    print(
        "UNIT 12 FLAT POSITION CONFIRMED = TRUE",
        flush=True,
    )

    print(
        "UNIT 12 PENDING ORDERS CLEARED = FALSE",
        flush=True,
    )

    print(
        "UNIT 12 ACTUAL LEVERAGE VERIFIED = FALSE",
        flush=True,
    )

    print(
        "UNIT 12 DUPLICATE CHECK VERIFIED = FALSE",
        flush=True,
    )

    print(
        "UNIT 12 EXCHANGE STATE RECONCILED = FALSE",
        flush=True,
    )

    print(
        "UNIT 12 REENTRY AUTHORIZED = FALSE",
        flush=True,
    )

    print(
        "UNIT 12 DEMO ORDER SUBMISSION = BLOCKED",
        flush=True,
    )

    print(
        "UNIT 12 REAL ORDER SUBMISSION = BLOCKED",
        flush=True,
    )

    print(
        "ZERO ORDER ENDPOINT ACCESS = TRUE",
        flush=True,
    )

    print(
        "ZERO EXCHANGE WRITE = TRUE",
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 12 "
        "RESULT = PASS (FLAT_PENDING_CHECKS)"
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# INITIAL UNIT 12 EXECUTION
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_12_RESULT = (
    fresh_reconstruction_unit_12(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_11_RESULT,
    )
)


# ============================================================
# UNIT 12 REUSABLE REFRESH
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_refresh_unit_12(
    unit_11_result=None
):

    global FRESH_RECONSTRUCTION_UNIT_12_RESULT

    if unit_11_result is None:
        unit_11_result = (
            FRESH_RECONSTRUCTION_UNIT_11_RESULT
        )

    refreshed = fresh_reconstruction_unit_12(
        FRESH_RECONSTRUCTION_CONFIG,
        unit_11_result,
    )

    FRESH_RECONSTRUCTION_UNIT_12_RESULT = refreshed

    return refreshed


# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 12
# ZERO INDENTATION DEMARCATION
#
# UNIT 12 FULLY CLOSED
# UNIT 12 CALLED ONCE
# REFRESH FUNCTION CREATED
# DEMO POSITION READ ONLY
# NO DEMO ORDER ENDPOINT
# NO REAL ORDER ENDPOINT
# NO LEVERAGE MUTATION
# NO MARGIN MODE MUTATION
# NO POSITION MODE MUTATION
#
# EXISTING UNIT 13 CONTINUES DIRECTLY BELOW
# ============================================================
     
# ============================================================
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 13
# ZERO INDENTATION DEMARCATION
# ============================================================
#
# EXISTING POSITION TP MANAGEMENT PLANNER
#
# COORDINATED RECONSTRUCTION VERSION
#
# - Independent of fresh entry qualification
# - Authenticated WEEX DEMO position GET only
# - Step-aware TP1 / TP2 / TP3 calculation
# - TP1 net ROI floor 5%
# - TP2 net ROI floor 10%
# - TP3 dynamic trailing configuration preserved
# - Unit 14 handoff fields preserved
# - No demo order submission in this unit
# - No real-money trading
# - SL remains disabled
#
# IMPORTANT:
# Unit 14 must be separately verified or paused.
# This Unit 13 does not disable Unit 14 exchange writes.
#
# ZERO EXCHANGE WRITE BY UNIT 13
# ============================================================

import os
import time
import json
import hmac
import base64
import hashlib
import urllib.request
import urllib.error

from decimal import Decimal, ROUND_DOWN, ROUND_UP


# ============================================================
# UNIT 13 DECIMAL HELPER
# ZERO INDENTATION
# ============================================================

def fresh_unit_13_decimal(value, name):

    try:
        number = Decimal(str(value))
    except Exception as exc:
        raise RuntimeError(
            "UNIT 13 INVALID NUMBER: " + name
        ) from exc

    if not number.is_finite():
        raise RuntimeError(
            "UNIT 13 NON-FINITE NUMBER: " + name
        )

    return number


# ============================================================
# UNIT 13 DEMO POSITION READ
# ZERO INDENTATION
# ============================================================

def fresh_unit_13_read_positions():

    path = "/capi/v3/sim/position/allPosition"

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
            "UNIT 13 DEMO CREDENTIALS MISSING"
        )

    timestamp = str(int(time.time() * 1000))
    message = timestamp + "GET" + path

    signature = base64.b64encode(
        hmac.new(
            api_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    request = urllib.request.Request(
        url=(
            "https://api-contract.weex.com"
            + path
        ),
        method="GET",
        headers={
            "ACCESS-KEY": api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": passphrase,
            "Accept": "application/json",
            "User-Agent": "Fresh-WEEX-Unit13",
        },
    )

    if request.get_method() != "GET":
        raise RuntimeError(
            "UNIT 13 NON-GET REQUEST BLOCKED"
        )

    if request.data is not None:
        raise RuntimeError(
            "UNIT 13 REQUEST BODY BLOCKED"
        )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            if response.getcode() != 200:
                raise RuntimeError(
                    "UNIT 13 POSITION HTTP FAILURE"
                )

            raw = response.read().decode("utf-8")

    except urllib.error.URLError as exc:
        raise RuntimeError(
            "UNIT 13 POSITION READ FAILED"
        ) from exc

    try:
        records = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT 13 INVALID POSITION JSON"
        ) from exc

    if not isinstance(records, list):
        raise RuntimeError(
            "UNIT 13 INVALID POSITION RESPONSE"
        )

    return records


# ============================================================
# UNIT 13 STEP-AWARE ALLOCATION
# ZERO INDENTATION
# ============================================================

def fresh_unit_13_allocate(total_steps):

    if total_steps < 1:
        return 0, 0, 0

    # Fewer than three steps cannot support three
    # separate executable TP stages.

    if total_steps == 1:
        return 0, 0, 1

    if total_steps == 2:
        return 0, 0, 2

    tp1 = max(
        1,
        int(
            Decimal(total_steps)
            * Decimal("0.10")
        ),
    )

    tp2 = max(
        1,
        int(
            Decimal(total_steps)
            * Decimal("0.20")
        ),
    )

    tp3 = total_steps - tp1 - tp2

    if tp3 < 1:
        tp1 = 1
        tp2 = 1
        tp3 = total_steps - 2

    if tp1 + tp2 + tp3 != total_steps:
        raise RuntimeError(
            "UNIT 13 TP ALLOCATION MISMATCH"
        )

    return tp1, tp2, tp3


# ============================================================
# UNIT 13 MAIN FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_13(
    config,
    unit_12_result,
):

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 13 START")

    # ========================================================
    # 1. INPUT VALIDATION
    # INDENTATION: 4 SPACES
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 13 CONFIGURATION MISSING"
        )

    if not isinstance(unit_12_result, dict):
        raise RuntimeError(
            "UNIT 13 UNIT 12 RESULT MISSING"
        )

    strategy = config.get("strategy")
    exchange = config.get("exchange")
    precision = config.get("market_precision")

    if not all(
        isinstance(item, dict)
        for item in (strategy, exchange, precision)
    ):
        raise RuntimeError(
            "UNIT 13 CONFIGURATION INVALID"
        )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 13 REAL ENVIRONMENT PROHIBITED"
        )

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 13 DEMO SYMBOL MISMATCH"
        )

    if strategy.get(
        "real_money_execution_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 13 REAL EXECUTION NOT BLOCKED"
        )

    if strategy.get("stop_loss_enabled") is not False:
        raise RuntimeError(
            "UNIT 13 UNEXPECTED SL ENABLED"
        )

    # ========================================================
    # 2. TP CONFIGURATION
    # INDENTATION: 4 SPACES
    # ========================================================

    tp1_pct = fresh_unit_13_decimal(
        strategy["tp1_allocation_percent"],
        "tp1 allocation",
    )

    tp2_pct = fresh_unit_13_decimal(
        strategy["tp2_allocation_percent"],
        "tp2 allocation",
    )

    tp3_pct = fresh_unit_13_decimal(
        strategy["tp3_allocation_percent"],
        "tp3 allocation",
    )

    if (tp1_pct, tp2_pct, tp3_pct) != (
        Decimal("10"),
        Decimal("20"),
        Decimal("70"),
    ):
        raise RuntimeError(
            "UNIT 13 TP ALLOCATION CONTRACT MISMATCH"
        )

    quantity_step = fresh_unit_13_decimal(
        precision["quantity_step"],
        "quantity step",
    )

    price_step = fresh_unit_13_decimal(
        precision["price_step"],
        "price step",
    )

    leverage_target = fresh_unit_13_decimal(
        strategy["leverage_target"],
        "target leverage",
    )

    fee_per_side = fresh_unit_13_decimal(
        strategy.get(
            "futures_taker_fee_percent",
            0.08,
        ),
        "estimated taker fee",
    )

    tp1_net_floor = fresh_unit_13_decimal(
        strategy["tp1_net_roi_floor_percent"],
        "tp1 net ROI floor",
    )

    tp2_net_floor = fresh_unit_13_decimal(
        strategy["tp2_net_roi_floor_percent"],
        "tp2 net ROI floor",
    )

    separation_roi = fresh_unit_13_decimal(
        strategy[
            "tp1_tp2_min_roi_separation_percent"
        ],
        "TP separation",
    )

    trailing_reference = fresh_unit_13_decimal(
        strategy["tp3_trailing_reference_percent"],
        "trailing reference",
    )

    trailing_min = fresh_unit_13_decimal(
        strategy["tp3_trailing_min_percent"],
        "trailing minimum",
    )

    trailing_max = fresh_unit_13_decimal(
        strategy["tp3_trailing_max_percent"],
        "trailing maximum",
    )

    if quantity_step <= 0 or price_step <= 0:
        raise RuntimeError(
            "UNIT 13 INVALID MARKET PRECISION"
        )

    if leverage_target <= 0:
        raise RuntimeError(
            "UNIT 13 INVALID LEVERAGE"
        )

    if not (
        Decimal("0") <
        trailing_min <= trailing_reference <= trailing_max
    ):
        raise RuntimeError(
            "UNIT 13 INVALID TRAILING RANGE"
        )

    if fee_per_side < 0:
        raise RuntimeError(
            "UNIT 13 INVALID FEE ESTIMATE"
        )

    # ========================================================
    # 3. NORMALIZED IDLE RESULT
    # INDENTATION: 4 SPACES
    # ========================================================

    result = {
        "unit": 13,
        "status": "IDLE_NO_POSITION",
        "read_only": True,
        "unit_12_status":
            unit_12_result.get("status", "UNKNOWN"),

        "position_exists": False,
        "active_position_exists": False,
        "position_side": "NONE",
        "position_size": "0",
        "average_entry_price": "0",

        "tp1_quantity": "0",
        "tp2_quantity": "0",
        "tp3_quantity": "0",

        "tp1_target": "0",
        "tp2_target": "0",
        "tp1_target_price": "0",
        "tp2_target_price": "0",

        "tp1_completed": False,
        "tp2_completed": False,
        "tp3_armed": False,

        "tp3_trailing_reference_percent":
            str(trailing_reference),
        "tp3_trailing_min_percent":
            str(trailing_min),
        "tp3_trailing_max_percent":
            str(trailing_max),

        "tp_management_required": False,
        "tp_execution_attempted": False,
        "tp_execution_completed": False,
        "demo_order_executed": False,
        "sl_execution_attempted": False,
        "backup_execution_attempted": False,
        "real_submission_attempted": False,
        "exchange_write": False,

        "actual_leverage_verified": False,
        "profit_targets_estimated": True,
        "skip_reason": "NO_ACTIVE_BTCSUSDT_POSITION",
    }

    # ========================================================
    # 4. INDEPENDENT DEMO POSITION READ
    # INDENTATION: 4 SPACES
    #
    # Unit 12 may be IDLE or PAUSED.
    # Existing-position monitoring does not require
    # another qualified entry signal.
    # ========================================================

    records = fresh_unit_13_read_positions()

    active = []

    for record in records:

        if not isinstance(record, dict):
            raise RuntimeError(
                "UNIT 13 INVALID POSITION RECORD"
            )

        if str(
            record.get("symbol", "")
        ).upper() != "BTCSUSDT":
            continue

        if "size" not in record:
            raise RuntimeError(
                "UNIT 13 POSITION SIZE MISSING"
            )

        size = fresh_unit_13_decimal(
            record["size"],
            "position size",
        )

        if size < 0:
            raise RuntimeError(
                "UNIT 13 NEGATIVE POSITION SIZE"
            )

        if size > 0:
            active.append(record)

    if len(active) == 0:

        print(
            "UNIT 13 STATUS = IDLE_NO_POSITION",
            flush=True,
        )

        print(
            "UNIT 13 ACTIVE POSITION = FALSE",
            flush=True,
        )

        print(
            "ZERO EXCHANGE WRITE BY UNIT 13 = TRUE",
            flush=True,
        )

        log(
            "FRESH RECONSTRUCTION UNIT 13 "
            "RESULT = PASS (IDLE_NO_POSITION)"
        )

        return result

    if len(active) != 1:
        raise RuntimeError(
            "UNIT 13 MULTIPLE ACTIVE BTC POSITIONS"
        )

    position = active[0]

    # ========================================================
    # 5. POSITION NORMALIZATION
    # INDENTATION: 4 SPACES
    # ========================================================

    side = str(
        position.get(
            "side",
            position.get("positionSide", ""),
        )
    ).upper()

    if side not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 13 INVALID POSITION SIDE"
        )

    size = fresh_unit_13_decimal(
        position["size"],
        "position size",
    )

    open_value = fresh_unit_13_decimal(
        position.get("openValue"),
        "open value",
    )

    if size <= 0 or open_value <= 0:
        raise RuntimeError(
            "UNIT 13 INVALID ACTIVE POSITION"
        )

    average_entry = open_value / size

    if average_entry <= 0:
        raise RuntimeError(
            "UNIT 13 INVALID AVERAGE ENTRY"
        )

    # ========================================================
    # 6. HISTORICAL EXECUTABLE QUANTITY
    # INDENTATION: 4 SPACES
    #
    # Prefer cumulative original entry size where valid.
    # This avoids reallocating the entire TP plan
    # every time an earlier TP reduces open quantity.
    # ========================================================

    original_size = fresh_unit_13_decimal(
        position.get("cumOpenSize", size),
        "cumulative open size",
    )

    if original_size < size:
        raise RuntimeError(
            "UNIT 13 INCONSISTENT ORIGINAL SIZE"
        )

    total_steps = int(
        (original_size / quantity_step)
        .to_integral_value(rounding=ROUND_DOWN)
    )

    if total_steps < 1:
        raise RuntimeError(
            "UNIT 13 POSITION BELOW EXECUTABLE STEP"
        )

    steps1, steps2, steps3 = (
        fresh_unit_13_allocate(total_steps)
    )

    qty1 = quantity_step * steps1
    qty2 = quantity_step * steps2
    qty3 = quantity_step * steps3

    # ========================================================
    # 7. ESTIMATED NET ROI TO PRICE TARGETS
    # INDENTATION: 4 SPACES
    #
    # These are estimates using configured leverage
    # and a simplified round-trip taker-fee model.
    #
    # Actual exchange leverage and realized fees
    # have NOT been independently confirmed.
    # ========================================================

    round_trip_fee_pct = (
        fee_per_side * Decimal("2")
    )

    fee_roi_drag = (
        round_trip_fee_pct * leverage_target
    )

    required_tp1_gross_roi = (
        tp1_net_floor + fee_roi_drag
    )

    required_tp2_gross_roi = (
        tp2_net_floor + fee_roi_drag
    )

    price_move1_pct = (
        required_tp1_gross_roi
        / leverage_target
    )

    price_move2_pct = (
        required_tp2_gross_roi
        / leverage_target
    )

    if side == "LONG":

        raw_tp1 = average_entry * (
            Decimal("1")
            + price_move1_pct / Decimal("100")
        )

        raw_tp2 = average_entry * (
            Decimal("1")
            + price_move2_pct / Decimal("100")
        )

        tp1_target = (
            raw_tp1 / price_step
        ).to_integral_value(
            rounding=ROUND_UP
        ) * price_step

        tp2_target = (
            raw_tp2 / price_step
        ).to_integral_value(
            rounding=ROUND_UP
        ) * price_step

        minimum_separation = (
            average_entry
            * separation_roi
            / leverage_target
            / Decimal("100")
        )

        tp2_target = max(
            tp2_target,
            tp1_target + price_step,
            tp1_target + minimum_separation,
        )

        tp2_target = (
            tp2_target / price_step
        ).to_integral_value(
            rounding=ROUND_UP
        ) * price_step

    else:

        raw_tp1 = average_entry * (
            Decimal("1")
            - price_move1_pct / Decimal("100")
        )

        raw_tp2 = average_entry * (
            Decimal("1")
            - price_move2_pct / Decimal("100")
        )

        tp1_target = (
            raw_tp1 / price_step
        ).to_integral_value(
            rounding=ROUND_DOWN
        ) * price_step

        tp2_target = (
            raw_tp2 / price_step
        ).to_integral_value(
            rounding=ROUND_DOWN
        ) * price_step

        minimum_separation = (
            average_entry
            * separation_roi
            / leverage_target
            / Decimal("100")
        )

        tp2_target = min(
            tp2_target,
            tp1_target - price_step,
            tp1_target - minimum_separation,
        )

        tp2_target = (
            tp2_target / price_step
        ).to_integral_value(
            rounding=ROUND_DOWN
        ) * price_step

    if tp1_target <= 0 or tp2_target <= 0:
        raise RuntimeError(
            "UNIT 13 INVALID TP PRICE TARGET"
        )

    # ========================================================
    # 8. BUILD NON-EXECUTING TP PLAN
    # INDENTATION: 4 SPACES
    #
    # Completion cannot be proven from size alone.
    # Historical fills must be reconciled separately.
    # No TP3 arming is claimed without fill evidence.
    # ========================================================

    result.update({
        "status": "TP_PLAN_READ_ONLY",
        "position_exists": True,
        "active_position_exists": True,
        "position_side": side,
        "position_size": str(size),
        "average_entry_price": str(average_entry),

        "total_executable_steps": total_steps,

        "tp1_quantity": str(qty1),
        "tp2_quantity": str(qty2),
        "tp3_quantity": str(qty3),

        "tp1_target": str(tp1_target),
        "tp2_target": str(tp2_target),
        "tp1_target_price": str(tp1_target),
        "tp2_target_price": str(tp2_target),

        "tp1_completed": False,
        "tp2_completed": False,
        "tp3_armed": False,

        "tp_management_required": True,

        "required_tp1_gross_roi":
            str(required_tp1_gross_roi),

        "required_tp2_gross_roi":
            str(required_tp2_gross_roi),

        "estimated_fee_roi_drag":
            str(fee_roi_drag),

        "tp_execution_attempted": False,
        "tp_execution_completed": False,
        "demo_order_executed": False,
        "exchange_write": False,

        "skip_reason":
            "TP_EXECUTION_PAUSED_PENDING_FILL_"
            "RECONCILIATION_AND_UNIT14_INTEGRATION",
    })

    # ========================================================
    # 9. RENDER STATUS
    # INDENTATION: 4 SPACES
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "UNIT 13 STATUS = TP_PLAN_READ_ONLY",
        flush=True,
    )

    print(
        "UNIT 13 POSITION SIDE =",
        side,
        flush=True,
    )

    print(
        "UNIT 13 POSITION SIZE =",
        size,
        flush=True,
    )

    print(
        "UNIT 13 AVERAGE ENTRY =",
        average_entry,
        flush=True,
    )

    print(
        "UNIT 13 TP ALLOCATION = 10/20/70 TARGET",
        flush=True,
    )

    print(
        "UNIT 13 TP1 QUANTITY =",
        qty1,
        flush=True,
    )

    print(
        "UNIT 13 TP2 QUANTITY =",
        qty2,
        flush=True,
    )

    print(
        "UNIT 13 TP3 QUANTITY =",
        qty3,
        flush=True,
    )

    print(
        "UNIT 13 TP1 TARGET =",
        tp1_target,
        flush=True,
    )

    print(
        "UNIT 13 TP2 TARGET =",
        tp2_target,
        flush=True,
    )

    print(
        "UNIT 13 TP3 TRAILING REFERENCE =",
        trailing_reference,
        "%",
        flush=True,
    )

    print(
        "UNIT 13 TP3 TRAILING RANGE =",
        trailing_min,
        "TO",
        trailing_max,
        "%",
        flush=True,
    )

    print(
        "UNIT 13 TP1/TP2 FILL STATE = UNVERIFIED",
        flush=True,
    )

    print(
        "UNIT 13 TP3 ARMED = FALSE",
        flush=True,
    )

    print(
        "UNIT 13 NEW ENTRY SIGNAL REQUIRED = FALSE",
        flush=True,
    )

    print(
        "UNIT 13 DEMO TP SUBMISSION = PAUSED",
        flush=True,
    )

    print(
        "UNIT 13 REAL ORDER SUBMISSION = BLOCKED",
        flush=True,
    )

    print(
        "ZERO EXCHANGE WRITE BY UNIT 13 = TRUE",
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 13 "
        "RESULT = PASS (TP_PLAN_READ_ONLY)"
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# INITIAL UNIT 13 EXECUTION
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_13_RESULT = (
    fresh_reconstruction_unit_13(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_12_RESULT,
    )
)


# ============================================================
# UNIT 13 REUSABLE REFRESH
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_refresh_unit_13(
    unit_12_result=None
):

    global FRESH_RECONSTRUCTION_UNIT_13_RESULT

    if unit_12_result is None:
        unit_12_result = (
            FRESH_RECONSTRUCTION_UNIT_12_RESULT
        )

    refreshed = fresh_reconstruction_unit_13(
        FRESH_RECONSTRUCTION_CONFIG,
        unit_12_result,
    )

    FRESH_RECONSTRUCTION_UNIT_13_RESULT = refreshed

    return refreshed


# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 13
# ZERO INDENTATION DEMARCATION
#
# UNIT 13 FULLY CLOSED
# UNIT 13 CALLED ONCE
# REFRESH FUNCTION CREATED
# UNIT 14 TP FIELD NAMES PRESERVED
# NO ORDER SUBMISSION IN UNIT 13
# NO OPEN FUNCTION
# NO OPEN IF
# NO OPEN TRY
# NO OPEN LOOP
#
# UNIT 14 CONTINUES DIRECTLY BELOW
# ============================================================
 
# ============================================================
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 14
# ZERO INDENTATION DEMARCATION
# ============================================================
#
# COORDINATED TP AND BACKUP MONITOR
#
# TP1 / TP2:
# - Detect target-price conditions
# - Never infer actual fill from mark price
#
# TP3:
# - Dynamic 0.10% to 0.40% callback
# - Reference 0.20%
# - ATR, EMA trend and momentum context
# - Trailing simulation only until fills verified
#
# BACKUPS:
# ENTRY -> B1 -> L1 -> B2 -> L2 -> B3 -> L3 -> STOP
#
# B4 DISABLED
# SL DISABLED
# DEMO BTCSUSDT ONLY
# NO ORDER SUBMISSION
# NO EXCHANGE WRITE
#
# NO INFINITE LOOP IN THIS UNIT.
# FUTURE CONTROLLER WILL SCHEDULE REFRESHES.
# ============================================================

import time
import math
from decimal import Decimal, InvalidOperation


# ============================================================
# UNIT 14 RUNTIME STATE
# ZERO INDENTATION
# ============================================================

FRESH_UNIT_14_STATE = {
    "position_key": None,
    "best_mark": None,
    "last_position_size": None,
    "last_scan_ms": None,
    "closure_candidate": False,
}


# ============================================================
# UNIT 14 DECIMAL HELPER
# ZERO INDENTATION
# ============================================================

def fresh_unit_14_decimal(value, name):

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 14 INVALID NUMBER: " + name
        ) from exc

    if not number.is_finite():
        raise RuntimeError(
            "UNIT 14 NON-FINITE NUMBER: " + name
        )

    return number


# ============================================================
# UNIT 14 MAIN FUNCTION
# ZERO INDENTATION
# ============================================================

def fresh_tp3_runtime(
    config,
    unit_13_result,
    market_snapshot=None,
    analysis_snapshot=None,
):

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 14 START")

    # ========================================================
    # 1. CONFIGURATION
    # INDENTATION: 4 SPACES
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 14 CONFIG MISSING")

    if not isinstance(unit_13_result, dict):
        raise RuntimeError("UNIT 14 UNIT 13 MISSING")

    strategy = config.get("strategy", {})
    exchange = config.get("exchange", {})

    if not isinstance(strategy, dict):
        raise RuntimeError("UNIT 14 STRATEGY INVALID")

    if not isinstance(exchange, dict):
        raise RuntimeError("UNIT 14 EXCHANGE INVALID")

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError("UNIT 14 REAL ENVIRONMENT BLOCK")

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError("UNIT 14 DEMO SYMBOL INVALID")

    if strategy.get("max_backups") != 3:
        raise RuntimeError("UNIT 14 BACKUP COUNT INVALID")

    if strategy.get("stop_loss_enabled") is not False:
        raise RuntimeError("UNIT 14 SL CONFIG INVALID")

    if strategy.get(
        "real_money_execution_enabled"
    ) is not False:
        raise RuntimeError("UNIT 14 REAL EXECUTION BLOCK")

    if unit_13_result.get("read_only") is not True:
        raise RuntimeError("UNIT 14 UNIT 13 NOT READ ONLY")

    # ========================================================
    # 2. REFRESH SNAPSHOT INPUTS
    # INDENTATION: 4 SPACES
    # ========================================================

    if market_snapshot is None:
        market_snapshot = (
            FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
        )

    if analysis_snapshot is None:
        analysis_snapshot = (
            FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
        )

    if not isinstance(market_snapshot, dict):
        raise RuntimeError("UNIT 14 MARKET DATA MISSING")

    if not isinstance(analysis_snapshot, dict):
        raise RuntimeError("UNIT 14 ANALYSIS MISSING")

    if (
        market_snapshot.get("read_only") is not True
        or analysis_snapshot.get("read_only") is not True
    ):
        raise RuntimeError("UNIT 14 SNAPSHOT NOT READ ONLY")

    if (
        market_snapshot.get("symbol") != "BTCUSDT"
        or analysis_snapshot.get("symbol") != "BTCUSDT"
    ):
        raise RuntimeError("UNIT 14 SYMBOL MISMATCH")

    now_ms = int(time.time() * 1000)

    market_time_ms = int(
        market_snapshot["exchange_time_ms"]
    )

    if not (
        -30000 <= now_ms - market_time_ms <= 120000
    ):
        raise RuntimeError(
            "UNIT 14 MARKET DATA STALE"
        )

    if int(
        analysis_snapshot["exchange_time_ms"]
    ) != market_time_ms:
        raise RuntimeError(
            "UNIT 14 MARKET/ANALYSIS MISMATCH"
        )

    mark = fresh_unit_14_decimal(
        market_snapshot["price"], "mark"
    )

    if mark <= 0:
        raise RuntimeError("UNIT 14 INVALID MARK PRICE")

    # ========================================================
    # 3. VALIDATED STRATEGY VALUES
    # INDENTATION: 4 SPACES
    # ========================================================

    reference = fresh_unit_14_decimal(
        strategy["tp3_trailing_reference_percent"],
        "reference callback",
    )

    minimum = fresh_unit_14_decimal(
        strategy["tp3_trailing_min_percent"],
        "minimum callback",
    )

    maximum = fresh_unit_14_decimal(
        strategy["tp3_trailing_max_percent"],
        "maximum callback",
    )

    buffer_pct = fresh_unit_14_decimal(
        strategy["backup_buffer_percent"],
        "backup buffer",
    )

    if not (
        Decimal("0") < minimum
        <= reference <= maximum
    ):
        raise RuntimeError(
            "UNIT 14 TRAILING RANGE INVALID"
        )

    if buffer_pct <= 0:
        raise RuntimeError(
            "UNIT 14 BACKUP BUFFER INVALID"
        )

    # ========================================================
    # 4. CURRENT DEMO POSITION READ
    # INDENTATION: 4 SPACES
    #
    # Reuse Unit 13 authenticated GET helper.
    # No new exchange-write capability introduced.
    # ========================================================

    records = fresh_unit_13_read_positions()

    positions = []

    for item in records:

        if not isinstance(item, dict):
            raise RuntimeError(
                "UNIT 14 INVALID POSITION RECORD"
            )

        if str(
            item.get("symbol", "")
        ).upper() != "BTCSUSDT":
            continue

        if "size" not in item:
            raise RuntimeError(
                "UNIT 14 POSITION SIZE MISSING"
            )

        size = fresh_unit_14_decimal(
            item["size"], "position size"
        )

        if size < 0:
            raise RuntimeError(
                "UNIT 14 NEGATIVE POSITION"
            )

        if size > 0:
            positions.append(item)

    # ========================================================
    # 5. NORMALIZED SAFE RESULT
    # INDENTATION: 4 SPACES
    # ========================================================

    result = {
        "unit": 14,
        "status": "IDLE_NO_POSITION",
        "read_only": True,
        "position_exists": False,
        "position_side": "NONE",
        "position_size": "0",
        "mark_price": str(mark),

        "tp1_target_reached": False,
        "tp2_target_reached": False,
        "tp1_fill_verified": False,
        "tp2_fill_verified": False,
        "tp3_armed": False,
        "tp3_simulation_armed": False,
        "tp3_callback_percent": str(reference),
        "tp3_trailing_stop": None,
        "tp3_trailing_triggered": False,

        "backup_stage_verified": 0,
        "next_backup": None,
        "backup_trigger": None,
        "backup_trigger_reached": False,
        "liquidation_price_verified": False,

        "closure_candidate": False,
        "position_closed_confirmed": False,
        "reentry_authorized": False,

        "tp_execution_attempted": False,
        "backup_execution_attempted": False,
        "demo_order_submitted": False,
        "real_order_submitted": False,
        "exchange_write": False,
    }

    # ========================================================
    # 6. NO ACTIVE POSITION
    # INDENTATION: 4 SPACES
    # ========================================================

    if not positions:

        state = FRESH_UNIT_14_STATE

        if state["position_key"] is not None:
            result["closure_candidate"] = True

        state["closure_candidate"] = (
            result["closure_candidate"]
        )

        state["position_key"] = None
        state["best_mark"] = None
        state["last_position_size"] = None
        state["last_scan_ms"] = now_ms

        # Position closure cannot be established from
        # one zero-position response alone. Pending orders
        # and trade history remain to be reconciled.

        print(
            "UNIT 14 ACTIVE POSITION = FALSE",
            flush=True,
        )

        print(
            "UNIT 14 CLOSURE CANDIDATE =",
            result["closure_candidate"],
            flush=True,
        )

        print(
            "UNIT 14 REENTRY AUTHORIZED = FALSE",
            flush=True,
        )

        log(
            "FRESH RECONSTRUCTION UNIT 14 "
            "RESULT = PASS (IDLE_NO_POSITION)"
        )

        return result

    if len(positions) != 1:
        raise RuntimeError(
            "UNIT 14 MULTIPLE ACTIVE BTC POSITIONS"
        )

    # ========================================================
    # 7. ACTIVE POSITION
    # INDENTATION: 4 SPACES
    # ========================================================

    position = positions[0]

    side = str(
        position.get(
            "side",
            position.get("positionSide", ""),
        )
    ).upper()

    if side not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 14 POSITION SIDE INVALID"
        )

    size = fresh_unit_14_decimal(
        position["size"], "size"
    )

    state = FRESH_UNIT_14_STATE

    # Treat identity derived from missing exchange IDs
    # as unverified. It is not suitable for order execution.

    position_key = (
        str(position.get("id", "")),
        side,
        str(position.get("openValue", "")),
    )

    if state["position_key"] != position_key:
        state["position_key"] = position_key
        state["best_mark"] = mark

    # ========================================================
    # 8. DYNAMIC TP3 CALLBACK
    # INDENTATION: 4 SPACES
    #
    # Advisory calculation only.
    # ========================================================

    atr_pct = fresh_unit_14_decimal(
        analysis_snapshot["atr14_percent"],
        "ATR percentage",
    )

    ema19 = fresh_unit_14_decimal(
        analysis_snapshot["ema19"], "EMA19"
    )

    ema50 = fresh_unit_14_decimal(
        analysis_snapshot["ema50"], "EMA50"
    )

    move_1m = fresh_unit_14_decimal(
        analysis_snapshot["move_1m_pct"],
        "1-minute momentum",
    )

    move_5m = fresh_unit_14_decimal(
        analysis_snapshot["move_5m_pct"],
        "5-minute momentum",
    )

    if atr_pct < 0 or ema19 <= 0 or ema50 <= 0:
        raise RuntimeError(
            "UNIT 14 INVALID INDICATORS"
        )

    sign = Decimal("1") if side == "LONG" else Decimal("-1")

    trend_supports = (
        sign * (ema19 - ema50) > 0
    )

    momentum_supports = (
        sign * move_5m > 0
    )

    momentum_deteriorating = (
        sign * move_1m < 0
    )

    callback = reference

    # Allow additional breathing room in strong trends.
    if trend_supports and momentum_supports:
        callback += Decimal("0.05")

    # Volatility adjustment, capped to avoid runaway.
    volatility_addition = min(
        atr_pct * Decimal("0.25"),
        Decimal("0.10"),
    )

    callback += volatility_addition

    # Tighten when short-term momentum deteriorates.
    if momentum_deteriorating:
        callback -= Decimal("0.10")

    callback = max(
        minimum,
        min(maximum, callback),
    )

    # ========================================================
    # 9. TP1 AND TP2 TARGET MONITORING
    # INDENTATION: 4 SPACES
    # ========================================================

    tp1_reached = False
    tp2_reached = False

    if unit_13_result.get(
        "status"
    ) == "TP_PLAN_READ_ONLY":

        if (
            unit_13_result.get("position_side") == side
            and fresh_unit_14_decimal(
                unit_13_result["position_size"],
                "Unit 13 position size",
            ) == size
        ):

            tp1_price = fresh_unit_14_decimal(
                unit_13_result["tp1_target"],
                "TP1 target",
            )

            tp2_price = fresh_unit_14_decimal(
                unit_13_result["tp2_target"],
                "TP2 target",
            )

            if side == "LONG":
                tp1_reached = mark >= tp1_price
                tp2_reached = mark >= tp2_price

            else:
                tp1_reached = mark <= tp1_price
                tp2_reached = mark <= tp2_price

    # Target reach is not evidence of a fill.
    # No TP3 arming based only on prices.

    # ========================================================
    # 10. TP3 ADVISORY TRAILING
    # INDENTATION: 4 SPACES
    #
    # Track favorable mark for diagnostics only.
    # Cannot be treated as executable trailing state.
    # ========================================================

    best = state["best_mark"]

    if side == "LONG":
        best = max(best, mark)

        trailing_stop = best * (
            Decimal("1")
            - callback / Decimal("100")
        )

        trailing_triggered = (
            mark <= trailing_stop
        )

    else:
        best = min(best, mark)

        trailing_stop = best * (
            Decimal("1")
            + callback / Decimal("100")
        )

        trailing_triggered = (
            mark >= trailing_stop
        )

    state["best_mark"] = best
    state["last_position_size"] = str(size)
    state["last_scan_ms"] = now_ms

    # ========================================================
    # 11. BACKUP TRIGGER ADVISORY
    # INDENTATION: 4 SPACES
    #
    # Do not infer B1/B2/B3 fills from position size.
    #
    # Pending order and fill reconciliation is required
    # before choosing B2 or B3.
    # ========================================================

    liq_raw = position.get(
        "liquidationPrice",
        position.get("liqPrice"),
    )

    backup_trigger = None
    backup_reached = False
    liquidation_verified = False

    if liq_raw not in (None, "", "0"):

        liquidation = fresh_unit_14_decimal(
            liq_raw, "liquidation price"
        )

        if liquidation > 0:
            liquidation_verified = True

            if side == "LONG":
                backup_trigger = liquidation * (
                    Decimal("1")
                    + buffer_pct / Decimal("100")
                )

                backup_reached = (
                    mark <= backup_trigger
                )

            else:
                backup_trigger = liquidation * (
                    Decimal("1")
                    - buffer_pct / Decimal("100")
                )

                backup_reached = (
                    mark >= backup_trigger
                )

    # We cannot establish whether B1, B2 or B3 has
    # already filled from the position snapshot.
    #
    # Therefore the next executable backup is UNKNOWN.
    # Never create a backup order from this calculation.

    # ========================================================
    # 12. RETURN MONITORING RESULT
    # INDENTATION: 4 SPACES
    # ========================================================

    result.update({
        "status": "ACTIVE_POSITION_READ_ONLY",
        "position_exists": True,
        "position_side": side,
        "position_size": str(size),

        "tp1_target_reached": tp1_reached,
        "tp2_target_reached": tp2_reached,

        "tp1_fill_verified": False,
        "tp2_fill_verified": False,
        "tp3_armed": False,
        "tp3_simulation_armed": False,

        "tp3_callback_percent": str(callback),
        "tp3_trailing_stop": str(trailing_stop),
        "tp3_trailing_triggered": trailing_triggered,

        "backup_stage_verified": 0,
        "next_backup": "UNVERIFIED",
        "backup_trigger": (
            str(backup_trigger)
            if backup_trigger is not None
            else None
        ),
        "backup_trigger_reached": backup_reached,
        "liquidation_price_verified":
            liquidation_verified,

        "reentry_authorized": False,
        "demo_order_submitted": False,
        "real_order_submitted": False,
        "exchange_write": False,
    })

    # ========================================================
    # 13. RENDER LOGGING
    # INDENTATION: 4 SPACES
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "UNIT 14 STATUS = ACTIVE_POSITION_READ_ONLY",
        flush=True,
    )

    print(
        "UNIT 14 POSITION SIDE =",
        side,
        flush=True,
    )

    print(
        "UNIT 14 POSITION SIZE =",
        size,
        flush=True,
    )

    print(
        "UNIT 14 MARK PRICE =",
        mark,
        flush=True,
    )

    print(
        "UNIT 14 TP1 TARGET REACHED =",
        tp1_reached,
        flush=True,
    )

    print(
        "UNIT 14 TP2 TARGET REACHED =",
        tp2_reached,
        flush=True,
    )

    print(
        "UNIT 14 TP1/TP2 FILLS = UNVERIFIED",
        flush=True,
    )

    print(
        "UNIT 14 TP3 ARMED = FALSE",
        flush=True,
    )

    print(
        "UNIT 14 TP3 DYNAMIC CALLBACK % =",
        callback,
        flush=True,
    )

    print(
        "UNIT 14 TP3 ADVISORY TRAILING LEVEL =",
        trailing_stop,
        flush=True,
    )

    print(
        "UNIT 14 BACKUP SEQUENCE = "
        "ENTRY/B1/L1/B2/L2/B3/L3/STOP",
        flush=True,
    )

    print(
        "UNIT 14 BACKUP STAGE = UNVERIFIED",
        flush=True,
    )

    print(
        "UNIT 14 CURRENT LIQ BUFFER TRIGGER =",
        backup_trigger,
        flush=True,
    )

    print(
        "UNIT 14 BUFFER LEVEL REACHED =",
        backup_reached,
        flush=True,
    )

    print(
        "UNIT 14 B4 = DISABLED",
        flush=True,
    )

    print(
        "UNIT 14 SL = DISABLED",
        flush=True,
    )

    print(
        "UNIT 14 DEMO TP/BACKUP SUBMISSIONS = BLOCKED",
        flush=True,
    )

    print(
        "UNIT 14 REENTRY AUTHORIZED = FALSE",
        flush=True,
    )

    print(
        "ZERO EXCHANGE WRITE BY UNIT 14 = TRUE",
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 14 "
        "RESULT = PASS (ACTIVE_POSITION_READ_ONLY)"
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# INITIAL UNIT 14 EXECUTION
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    fresh_tp3_runtime(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_13_RESULT,
    )
)


# ============================================================
# UNIT 14 REUSABLE REFRESH
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_refresh_unit_14(
    unit_13_result=None,
    market_snapshot=None,
    analysis_snapshot=None,
):

    global FRESH_RECONSTRUCTION_UNIT_14_RESULT

    if unit_13_result is None:
        unit_13_result = (
            FRESH_RECONSTRUCTION_UNIT_13_RESULT
        )

    result = fresh_tp3_runtime(
        FRESH_RECONSTRUCTION_CONFIG,
        unit_13_result,
        market_snapshot,
        analysis_snapshot,
    )

    FRESH_RECONSTRUCTION_UNIT_14_RESULT = result

    return result


# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 14
# ZERO INDENTATION DEMARCATION
#
# UNIT 14 FULLY CLOSED
# UNIT 14 CALLED ONCE
# REUSABLE REFRESH FUNCTION CREATED
#
# NO INFINITE LOOP
# NO ORDER ENDPOINT ACCESS
# NO DEMO ORDER
# NO REAL ORDER
# NO EXCHANGE WRITE
#
# TP1 / TP2 = TARGET MONITORING ONLY
# TP3 = ADVISORY DYNAMIC TRAILING ONLY
# B1 / B2 / B3 = RECONCILIATION REQUIRED
# B4 = DISABLED
# SL = DISABLED
#
# END OF UNIT 14
# ============================================================
