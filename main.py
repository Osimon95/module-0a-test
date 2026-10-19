
# ============================================================
# FRESH WEEX RECONSTRUCTION
# UNIT 1 INDEPENDENT TEST
# ZERO INDENTATION START
# ============================================================

import json
import urllib.error
import urllib.parse
import urllib.request

from datetime import datetime, timezone


def log(message):
    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    print(timestamp, message, flush=True)


def fresh_reconstruction_unit_1():

    print("=" * 80, flush=True)

    log("FRESH RECONSTRUCTION UNIT 1 START")

    print("-" * 80, flush=True)

    # Verify standard library functionality.

    assert json.loads('{"test": true}')["test"] is True

    assert (
        urllib.parse.urlencode({"symbol": "BTCUSDT"})
        == "symbol=BTCUSDT"
    )

    assert callable(urllib.request.Request)

    assert hasattr(urllib.error, "URLError")

    assert datetime.now(timezone.utc).tzinfo is not None

    print(
        "PASS: MAIN PYTHON RUNTIME STARTED",
        flush=True
    )

    print(
        "PASS: PYTHON STANDARD LIBRARY AVAILABLE",
        flush=True
    )

    print(
        "PASS: JSON MODULE FUNCTIONAL",
        flush=True
    )

    print(
        "PASS: URLLIB MODULE FUNCTIONAL",
        flush=True
    )

    print(
        "PASS: UTC LOGGER FUNCTIONAL",
        flush=True
    )

    print(
        "UNIT 1 EXCHANGE CONNECTION = NONE",
        flush=True
    )

    print(
        "UNIT 1 HTTP REQUEST = NONE",
        flush=True
    )

    print(
        "UNIT 1 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 1 REAL ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 1 EXCHANGE WRITE = NONE",
        flush=True
    )

    print("-" * 80, flush=True)

    log("FRESH RECONSTRUCTION UNIT 1 RESULT = PASS")

    print("=" * 80, flush=True)

    return True


# ============================================================
# RUN INDEPENDENT UNIT 1 TEST
# ZERO INDENTATION
# ============================================================

if __name__ == "__main__":

    result = fresh_reconstruction_unit_1()

    if result is not True:
        raise RuntimeError(
            "UNIT 1 TEST FAILED"
        )

    print(
        "FINAL VERDICT: UNIT 1 VERIFIED",
        flush=True
    )

    print(
        "NEXT UNIT AUTHORIZED FOR TESTING = UNIT 2",
        flush=True
    )

# ============================================================
# END UNIT 1 INDEPENDENT TEST
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 2
# ZERO INDENTATION
# CONFIGURATION AND SAFETY CONTRACT
# ============================================================



# ============================================================
# UNIT 1 TO UNIT 2 VERIFICATION HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_1_READY = (
    fresh_reconstruction_unit_1()
)

if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
    raise RuntimeError(
        "UNIT 1 TO UNIT 2 HANDOVER FAILED"
    )

print(
    "PASS: UNIT 1 TO UNIT 2 HANDOVER VERIFIED",
    flush=True
)

# ============================================================
# END UNIT 1 TO UNIT 2 HANDOVER
# ============================================================
def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 2 START")
    print("-" * 80, flush=True)

    # ========================================================
    # 1. UNIT 1 DEPENDENCY
    # ========================================================

    if globals().get(
        "FRESH_RECONSTRUCTION_UNIT_1_READY"
    ) is not True:
        raise RuntimeError(
            "UNIT 2 BLOCKED: UNIT 1 NOT VERIFIED"
        )

    print(
        "PASS: UNIT 2 RECEIVED UNIT 1 RESULT",
        flush=True
    )

    # ========================================================
    # 2. EXCHANGE CONFIGURATION
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
    # 3. SAFETY CONFIGURATION
    # ========================================================

    safety = {
        "public_market_data_read_enabled": True,
        "demo_account_balance_read_enabled": False,
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
    # 4. STRATEGY CONFIGURATION
    # ========================================================

    strategy = {

        # LEVERAGE AND INITIAL ENTRY

        "leverage_target": 100,
        "initial_margin_percent": 5.0,
        "initial_fixed_usdt": 0.50,

        # FIVE BACKUPS

        "backup_margin_percent": 5.0,
        "backup_buffer_percent": 0.30,
        "max_backups": 5,
        "backup_multipliers": (
            1.0,
            1.5,
            2.0,
            2.5,
            3.0,
        ),

        # EXPOSURE PROTECTION

        "exposure_cap_percent": 35.0,
        "progressive_backup_funding": True,
        "full_ladder_reservation_required": False,

        # TAKE PROFIT

        "tp1_allocation_percent": 10.0,
        "tp2_allocation_percent": 20.0,
        "tp3_allocation_percent": 70.0,

        "tp1_net_roi_floor_percent": 5.0,
        "tp2_net_roi_floor_percent": 10.0,
        "tp1_tp2_min_roi_separation_percent": 5.0,

        # TP3 TRAILING

        "tp3_trailing_reference_percent": 0.20,
        "tp3_trailing_min_percent": 0.10,
        "tp3_trailing_max_percent": 0.40,

        # SIGNAL CONTROL

        "signal_expiry_seconds": 120,
        "loss_cooldown_seconds": 300,
        "one_direction_only": True,
        "anti_duplicate_orders": True,
        "active_trade_mode_lock": True,
        "exclusive_mode": True,
        "mode_confirmations_required": 3,

        # MODE ARBITRATION

        "mode_priority": (
            "BREAKOUT",
            "STRUCTURE",
            "SCALP",
        ),

        "structure_breakout_priority": True,
        "arbitration_before_scalp": True,
        "developing_candidate_protection": True,
        "scalp_requires_higher_modes_clear": True,
        "scalp_preemption_requires_confirmation": True,
        "preserve_active_position_management": True,

        # COMMON DIRECTION CONTROL

        "direction_votes_required": 2,
        "direction_votes_total": 3,
        "qualification_use_closed_candles": True,
        "reject_stale_signals": True,
        "reject_late_impulse_entry": True,
        "reject_spike_count_above": 2,

        # BREAKOUT

        "breakout_early_detection_enabled": True,
        "breakout_developing_candidate_enabled": True,
        "breakout_require_ema_crossover": False,
        "breakout_allow_preconfirmation": True,
        "breakout_require_price_confirmation": True,
        "breakout_require_momentum_confirmation": True,
        "breakout_require_direction_agreement": True,
        "breakout_retest_mandatory": False,

        # STRUCTURE

        "structure_early_detection_enabled": True,
        "structure_developing_candidate_enabled": True,
        "structure_require_ema_crossover": False,
        "structure_require_price_confirmation": True,
        "structure_require_direction_agreement": True,
        "structure_allow_pullback_entry": True,
        "structure_allow_continuation_entry": True,
        "structure_retest_mandatory": False,

        # SCALPING

        "scalp_sideways_preferred": True,
        "scalp_trending_market_block": True,
        "scalp_quality_threshold": 70.0,
        "scalp_price_weight_percent": 50.0,
        "scalp_other_factors_weight_percent": 50.0,
        "scalp_max_ema_extension_clusters": 1.5,
        "scalp_early_entry_enabled": True,
        "scalp_late_entry_rejection": True,

        # SCALP PROFITABILITY

        "scalp_fee_aware_enabled": True,
        "scalp_estimated_taker_fee_percent": 0.08,
        "scalp_include_entry_fee": True,
        "scalp_include_exit_fee": True,
        "scalp_include_estimated_slippage": True,
        "scalp_require_positive_net_profit": True,
        "scalp_profit_safety_buffer_enabled": True,
        "scalp_min_net_roi_percent": 2.0,

        # CONTINUOUS ENTRY SCANNING

        "continuous_entry_scan_enabled": True,
        "flat_position_reentry_enabled": True,
        "reentry_requires_confirmed_flat": True,
        "reentry_requires_no_pending_entry": True,
        "reentry_preserves_cooldown": True,
    }

    # ========================================================
    # 5. MARKET PRECISION
    # ========================================================

    market_precision = {
        "quantity_step": 0.0001,
        "minimum_quantity": 0.0001,
        "price_step": 0.1,
    }

    # ========================================================
    # 6. COMPLETE CONFIGURATION
    # ========================================================

    config = {
        "exchange": exchange,
        "execution_environment": execution_environment,
        "safety": safety,
        "strategy": strategy,
        "market_precision": market_precision,
    }

    # ========================================================
    # 7. VALIDATION ENGINE
    # ========================================================

    errors = []

    def check(condition, label):

        if condition:
            print(
                "PASS: UNIT 2 " + label,
                flush=True
            )
        else:
            print(
                "FAIL: UNIT 2 " + label,
                flush=True
            )
            errors.append(label)

    check(
        exchange["name"] == "WEEX",
        "EXCHANGE = WEEX"
    )

    check(
        exchange["api_version"] == "V3",
        "API VERSION = V3"
    )

    check(
        exchange["contract_base_url"]
        == "https://api-contract.weex.com",
        "CONTRACT API URL"
    )

    check(
        exchange["market_symbol"] == "BTCUSDT",
        "MARKET SYMBOL = BTCUSDT"
    )

    check(
        exchange["demo_order_symbol"] == "BTCSUSDT",
        "DEMO SYMBOL = BTCSUSDT"
    )

    check(
        execution_environment == "DEMO",
        "DEMO ENVIRONMENT"
    )

    check(
        strategy["leverage_target"] == 100,
        "LEVERAGE TARGET = 100X"
    )

    check(
        strategy["initial_fixed_usdt"] == 0.50
        and strategy["initial_margin_percent"] == 5.0,
        "INITIAL ENTRY CONFIGURATION"
    )

    check(
        strategy["max_backups"] == 5
        and strategy["backup_multipliers"]
        == (1.0, 1.5, 2.0, 2.5, 3.0),
        "FIVE BACKUP LADDER"
    )

    check(
        strategy["backup_buffer_percent"] == 0.30,
        "BACKUP BUFFER = 0.30%"
    )

    check(
        strategy["exposure_cap_percent"] == 35.0,
        "MAXIMUM EXPOSURE = 35%"
    )

    check(
        strategy["progressive_backup_funding"]
        is True
        and strategy["full_ladder_reservation_required"]
        is False,
        "PROGRESSIVE BACKUP FUNDING"
    )

    tp_total = (
        strategy["tp1_allocation_percent"]
        + strategy["tp2_allocation_percent"]
        + strategy["tp3_allocation_percent"]
    )

    check(
        (
            strategy["tp1_allocation_percent"],
            strategy["tp2_allocation_percent"],
            strategy["tp3_allocation_percent"],
        ) == (10.0, 20.0, 70.0)
        and tp_total == 100.0,
        "TP ALLOCATION = 10/20/70"
    )

    check(
        strategy["tp1_net_roi_floor_percent"] == 5.0
        and strategy["tp2_net_roi_floor_percent"] == 10.0,
        "TP NET ROI FLOORS"
    )

    check(
        0 < strategy["tp3_trailing_min_percent"]
        <= strategy["tp3_trailing_reference_percent"]
        <= strategy["tp3_trailing_max_percent"],
        "TP3 DYNAMIC TRAILING RANGE"
    )

    check(
        strategy["mode_priority"]
        == ("BREAKOUT", "STRUCTURE", "SCALP"),
        "MODE PRIORITY = BREAKOUT/STRUCTURE/SCALP"
    )

    check(
        strategy["direction_votes_required"] == 2
        and strategy["direction_votes_total"] == 3,
        "DIRECTION CONFIRMATION = 2/3"
    )

    check(
        strategy["arbitration_before_scalp"]
        and strategy["developing_candidate_protection"]
        and strategy["scalp_requires_higher_modes_clear"],
        "HIGHER MODE CANDIDATE PROTECTION"
    )

    check(
        strategy["scalp_quality_threshold"] == 70.0,
        "SCALP QUALITY THRESHOLD = 70"
    )

    check(
        strategy["scalp_price_weight_percent"] == 50.0
        and strategy["scalp_other_factors_weight_percent"]
        == 50.0,
        "SCALP PRICE WEIGHT = 50%"
    )

    check(
        strategy["scalp_fee_aware_enabled"]
        and strategy["scalp_require_positive_net_profit"]
        and strategy["scalp_include_entry_fee"]
        and strategy["scalp_include_exit_fee"],
        "FEE AWARE SCALPING CONFIGURED"
    )

    check(
        strategy["scalp_min_net_roi_percent"] > 0.0,
        "SCALP MINIMUM NET ROI CONFIGURED"
    )

    check(
        strategy["continuous_entry_scan_enabled"]
        and strategy["flat_position_reentry_enabled"]
        and strategy["reentry_requires_confirmed_flat"]
        and strategy["reentry_requires_no_pending_entry"],
        "CONTINUOUS SCAN AND FLAT REENTRY CONFIGURED"
    )

    check(
        strategy["one_direction_only"]
        and strategy["anti_duplicate_orders"]
        and strategy["active_trade_mode_lock"]
        and strategy["exclusive_mode"],
        "POSITION AND MODE PROTECTION FLAGS"
    )

    check(
        market_precision["quantity_step"] == 0.0001
        and market_precision["minimum_quantity"]
        == 0.0001
        and market_precision["price_step"] == 0.1,
        "MARKET PRECISION"
    )

    # ========================================================
    # 8. SAFETY CONTRACT VALIDATION
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

    check(
        all(
            safety.get(key) is False
            for key in forbidden_capabilities
        ),
        "EXCHANGE WRITE AND ACCOUNT ACCESS DISABLED"
    )

    check(
        safety["public_market_data_read_enabled"]
        is True,
        "PUBLIC MARKET DATA READ ENABLED"
    )

    check(
        safety["demo_account_balance_read_enabled"]
        is False,
        "DEMO ACCOUNT READ DISABLED DURING TEST"
    )

    # ========================================================
    # 9. CONFIGURATION DIAGNOSTICS
    # ========================================================

    full_ladder_multiplier = (
        1.0 + sum(strategy["backup_multipliers"])
    )

    full_ladder_margin = (
        strategy["initial_fixed_usdt"]
        * full_ladder_multiplier
    )

    print(
        "UNIT 2 FULL LADDER MULTIPLIER =",
        full_ladder_multiplier,
        flush=True
    )

    print(
        "UNIT 2 FULL LADDER MARGIN USDT =",
        full_ladder_margin,
        flush=True
    )

    print(
        "UNIT 2 TP ALLOCATION TOTAL =",
        tp_total,
        flush=True
    )

    print(
        "UNIT 2 SCALP PRICE WEIGHT =",
        strategy["scalp_price_weight_percent"],
        flush=True
    )

    print(
        "UNIT 2 SCALP OTHER FACTORS WEIGHT =",
        strategy["scalp_other_factors_weight_percent"],
        flush=True
    )

    print(
        "UNIT 2 DEMO ORDER SUBMISSION ENABLED =",
        safety["demo_order_submission_enabled"],
        flush=True
    )

    print(
        "UNIT 2 REAL ORDER SUBMISSION ENABLED =",
        safety["real_order_submission_enabled"],
        flush=True
    )

    # ========================================================
    # 10. FINAL VALIDATION
    # ========================================================

    if errors:
        print(
            "UNIT 2 VALIDATION ERRORS =",
            errors,
            flush=True
        )

        raise RuntimeError(
            "UNIT 2 CONFIGURATION VERIFICATION FAILED"
        )

    print("-" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 2 RESULT = PASS"
    )

    print(
        "PASS: UNIT 2 CONFIGURATION VALIDATED",
        flush=True
    )

    print(
        "PASS: UNIT 2 SAFETY CONTRACT VALIDATED",
        flush=True
    )

    print(
        "UNIT 2 EXCHANGE REQUEST = NONE",
        flush=True
    )

    print(
        "UNIT 2 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 2 REAL ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 2 EXCHANGE WRITE = NONE",
        flush=True
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
# END COMPLETE REPLACEMENT - UNIT 2
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 3
# ZERO INDENTATION
# WEEX V3 PUBLIC MARKET DATA VERIFICATION
# ============================================================

def fresh_reconstruction_unit_3():

    import json
    import math
    import urllib.parse
    import urllib.request
    import urllib.error
    import time

    print("=" * 80, flush=True)

    log("FRESH RECONSTRUCTION UNIT 3 START")

    print("-" * 80, flush=True)

    # ========================================================
    # 1. RECEIVE VERIFIED UNIT 2 CONFIGURATION
    # ========================================================

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 BLOCKED: UNIT 2 CONFIG MISSING"
        )

    exchange = config.get("exchange")
    safety = config.get("safety")
    strategy = config.get("strategy")

    if not all(
        isinstance(item, dict)
        for item in (exchange, safety, strategy)
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID UNIT 2 DATA"
        )

    print(
        "PASS: UNIT 3 RECEIVED UNIT 2 CONFIGURATION",
        flush=True
    )

    # ========================================================
    # 2. VERIFY EXCHANGE CONFIGURATION
    # ========================================================

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID EXCHANGE"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID API VERSION"
        )

    base_url = exchange.get(
        "contract_base_url"
    )

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID API DOMAIN"
        )

    symbol = exchange.get("market_symbol")

    if symbol != "BTCUSDT":
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID MARKET SYMBOL"
        )

    if config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 3 BLOCKED: NOT DEMO ENVIRONMENT"
        )

    print(
        "PASS: UNIT 3 WEEX V3 CONFIGURATION",
        flush=True
    )

    print(
        "PASS: UNIT 3 SYMBOL = BTCUSDT",
        flush=True
    )

    # ========================================================
    # 3. STRICT READ ONLY SAFETY GATE
    # ========================================================

    if safety.get(
        "public_market_data_read_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: MARKET READ DISABLED"
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
                "UNIT 3 BLOCKED: UNSAFE CAPABILITY "
                + capability
            )

    if safety.get(
        "demo_account_balance_read_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 3 BLOCKED: ACCOUNT READ ENABLED"
        )

    print(
        "PASS: UNIT 3 READ ONLY SAFETY GATE",
        flush=True
    )

    # ========================================================
    # 4. VERIFY STRATEGY HANDOVER
    # ========================================================

    if strategy.get("mode_priority") != (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP",
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: MODE PRIORITY MISMATCH"
        )

    if strategy.get(
        "continuous_entry_scan_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: SCANNING CONFIG MISSING"
        )

    if strategy.get(
        "scalp_fee_aware_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: FEE CONFIG MISSING"
        )

    if strategy.get(
        "developing_candidate_protection"
    ) is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: MODE PROTECTION MISSING"
        )

    print(
        "PASS: UNIT 3 STRATEGY CONFIGURATION RECEIVED",
        flush=True
    )

    # ========================================================
    # 5. CREATE WEEX PUBLIC REQUEST
    # ========================================================

    endpoint = "/capi/v3/market/symbolPrice"

    parameters = {
        "symbol": symbol,
        "priceType": "MARK",
    }

    query = urllib.parse.urlencode(parameters)

    url = base_url + endpoint + "?" + query

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Unit3-Verification/1.0",
        },
    )

    if request.get_method() != "GET":
        raise RuntimeError(
            "UNIT 3 BLOCKED: HTTP METHOD NOT GET"
        )

    if request.data is not None:
        raise RuntimeError(
            "UNIT 3 BLOCKED: REQUEST BODY DETECTED"
        )

    print(
        "PASS: UNIT 3 PUBLIC ENDPOINT CONFIGURED",
        flush=True
    )

    print(
        "PASS: UNIT 3 HTTP METHOD = GET",
        flush=True
    )

    print(
        "PASS: UNIT 3 AUTHENTICATION = NONE",
        flush=True
    )

    # ========================================================
    # 6. PREVENT HTTP REDIRECTION
    # ========================================================

    class NoRedirect(urllib.request.HTTPRedirectHandler):

        def redirect_request(
            self,
            req,
            fp,
            code,
            msg,
            headers,
            newurl
        ):
            return None

    opener = urllib.request.build_opener(
        NoRedirect()
    )

    # ========================================================
    # 7. EXECUTE PUBLIC WEEX GET REQUEST
    # ========================================================

    print(
        "UNIT 3 WEEX PUBLIC REQUEST START",
        flush=True
    )

    try:

        with opener.open(
            request,
            timeout=15
        ) as response:

            http_status = response.getcode()

            raw_body = response.read(
                65537
            )

    except urllib.error.HTTPError as exc:

        print(
            "UNIT 3 HTTP ERROR CODE =",
            exc.code,
            flush=True
        )

        print(
            "UNIT 3 HTTP ERROR BODY =",
            exc.read(500).decode(
                "utf-8",
                errors="replace"
            ),
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 WEEX HTTP REQUEST FAILED"
        ) from exc

    except urllib.error.URLError as exc:

        print(
            "UNIT 3 CONNECTION ERROR =",
            repr(exc.reason),
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 WEEX CONNECTION FAILED"
        ) from exc

    except Exception as exc:

        print(
            "UNIT 3 UNEXPECTED REQUEST ERROR =",
            repr(exc),
            flush=True
        )

        raise

    # ========================================================
    # 8. VERIFY HTTP RESPONSE
    # ========================================================

    print(
        "UNIT 3 HTTP STATUS =",
        http_status,
        flush=True
    )

    if http_status != 200:
        raise RuntimeError(
            "UNIT 3 BLOCKED: HTTP STATUS NOT 200"
        )

    if not raw_body:
        raise RuntimeError(
            "UNIT 3 BLOCKED: EMPTY HTTP RESPONSE"
        )

    if len(raw_body) > 65536:
        raise RuntimeError(
            "UNIT 3 BLOCKED: RESPONSE TOO LARGE"
        )

    print(
        "PASS: UNIT 3 WEEX RESPONSE RECEIVED",
        flush=True
    )

    # ========================================================
    # 9. DECODE JSON RESPONSE
    # ========================================================

    try:

        payload = json.loads(
            raw_body.decode("utf-8")
        )

    except (
        ValueError,
        UnicodeDecodeError
    ) as exc:

        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID JSON RESPONSE"
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID RESPONSE STRUCTURE"
        )

    print(
        "PASS: UNIT 3 JSON RESPONSE VALID",
        flush=True
    )

    # ========================================================
    # 10. VALIDATE WEEX RESPONSE SYMBOL
    # ========================================================

    response_symbol = payload.get("symbol")

    if response_symbol != symbol:
        raise RuntimeError(
            "UNIT 3 BLOCKED: RESPONSE SYMBOL MISMATCH"
        )

    print(
        "PASS: UNIT 3 RESPONSE SYMBOL =",
        response_symbol,
        flush=True
    )

    # ========================================================
    # 11. VALIDATE LIVE BTC MARK PRICE
    # ========================================================

    try:

        mark_price = float(
            payload.get("price")
        )

    except (
        TypeError,
        ValueError
    ) as exc:

        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID MARK PRICE"
        ) from exc

    if not math.isfinite(mark_price):
        raise RuntimeError(
            "UNIT 3 BLOCKED: NON FINITE PRICE"
        )

    if mark_price <= 0:
        raise RuntimeError(
            "UNIT 3 BLOCKED: NON POSITIVE PRICE"
        )

    print(
        "PASS: UNIT 3 LIVE BTC MARK PRICE =",
        mark_price,
        flush=True
    )

    # ========================================================
    # 12. VALIDATE EXCHANGE TIMESTAMP
    # ========================================================

    exchange_time_ms = payload.get("time")

    if (
        isinstance(exchange_time_ms, bool)
        or not isinstance(exchange_time_ms, int)
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID TIMESTAMP TYPE"
        )

    if not (
        1000000000000 <= exchange_time_ms
        < 100000000000000
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID MILLISECOND TIME"
        )

    received_time_ms = int(
        time.time() * 1000
    )

    market_age_seconds = (
        received_time_ms - exchange_time_ms
    ) / 1000.0

    max_market_age_seconds = 120.0

    future_tolerance_seconds = 30.0

    print(
        "UNIT 3 MARKET AGE SECONDS =",
        round(market_age_seconds, 3),
        flush=True
    )

    if market_age_seconds > max_market_age_seconds:
        raise RuntimeError(
            "UNIT 3 BLOCKED: STALE MARKET DATA"
        )

    if market_age_seconds < -future_tolerance_seconds:
        raise RuntimeError(
            "UNIT 3 BLOCKED: FUTURE TIMESTAMP"
        )

    print(
        "PASS: UNIT 3 MARKET DATA FRESH",
        flush=True
    )

    print(
        "PASS: UNIT 3 EXCHANGE TIMESTAMP VALID",
        flush=True
    )

    # ========================================================
    # 13. CREATE NORMALIZED MARKET SNAPSHOT
    # ========================================================

    market_snapshot = {

        "exchange": "WEEX",

        "api_version": "V3",

        "symbol": symbol,

        "price": mark_price,

        "price_type": "MARK",

        "exchange_time_ms": exchange_time_ms,

        "source": "WEEX_V3_PUBLIC_MARK_PRICE",

        "read_only": True,

        "received_time_ms": received_time_ms,

        "market_age_seconds": market_age_seconds,

        "max_market_age_seconds":
            max_market_age_seconds,

        "market_data_fresh": True,

        "finite_price_validated": True,

        "source_type": "MARK_PRICE",

        "strategy_data_ready": True,
    }

    # ========================================================
    # 14. VERIFY UNIT 4 HANDOVER CONTRACT
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
                "UNIT 3 BLOCKED: SNAPSHOT FIELD MISSING "
                + field
            )

    if market_snapshot["read_only"] is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID READ ONLY SNAPSHOT"
        )

    print(
        "PASS: UNIT 3 NORMALIZED SNAPSHOT CREATED",
        flush=True
    )

    print(
        "PASS: UNIT 3 SNAPSHOT READY FOR UNIT 4",
        flush=True
    )

    # ========================================================
    # 15. FINAL UNIT 3 DIAGNOSTICS
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "PASS: UNIT 3 WEEX V3 PUBLIC MARKET READ",
        flush=True
    )

    print(
        "PASS: UNIT 3 MARK PRICE VALIDATED",
        flush=True
    )

    print(
        "PASS: UNIT 3 DATA FRESHNESS VALIDATED",
        flush=True
    )

    print(
        "PASS: UNIT 3 STRATEGY HANDOVER VERIFIED",
        flush=True
    )

    print(
        "UNIT 3 AUTHENTICATED REQUEST = NONE",
        flush=True
    )

    print(
        "UNIT 3 ACCOUNT ACCESS = NONE",
        flush=True
    )

    print(
        "UNIT 3 POSITION ACCESS = NONE",
        flush=True
    )

    print(
        "UNIT 3 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 3 REAL ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 3 EXCHANGE WRITE = NONE",
        flush=True
    )

    print("-" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 3 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return market_snapshot


# ============================================================
# RUN UNIT 3
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# END COMPLETE REPLACEMENT - UNIT 3
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 4
# ZERO INDENTATION
# WEEX CLOSED-CANDLE EMA AND MARKET ANALYSIS
# PUBLIC READ ONLY - NO ORDER EXECUTION
# ============================================================

def fresh_reconstruction_unit_4():

    import json
    import math
    import time
    import urllib.parse
    import urllib.request
    import urllib.error

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 4 START")
    print("-" * 80, flush=True)

    # ========================================================
    # 1. RECEIVE VERIFIED PREVIOUS UNITS
    # ========================================================

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    market = globals().get(
        "FRESH_RECONSTRUCTION_MARKET_SNAPSHOT"
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 4 BLOCKED: UNIT 2 CONFIG MISSING"
        )

    if not isinstance(market, dict):
        raise RuntimeError(
            "UNIT 4 BLOCKED: UNIT 3 SNAPSHOT MISSING"
        )

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})
    strategy = config.get("strategy", {})

    if not all(
        isinstance(x, dict)
        for x in (exchange, safety, strategy)
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID CONFIGURATION"
        )

    if (
        exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or exchange.get("market_symbol") != "BTCUSDT"
        or exchange.get("contract_base_url")
        != "https://api-contract.weex.com"
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: EXCHANGE CONFIGURATION"
        )

    if (
        market.get("symbol") != "BTCUSDT"
        or market.get("exchange") != "WEEX"
        or market.get("api_version") != "V3"
        or market.get("price_type") != "MARK"
        or market.get("read_only") is not True
        or market.get("market_data_fresh") is not True
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID UNIT 3 SNAPSHOT"
        )

    print(
        "PASS: UNIT 4 RECEIVED UNITS 2 AND 3",
        flush=True
    )

    # ========================================================
    # 2. READ ONLY SAFETY GATE
    # ========================================================

    if safety.get(
        "public_market_data_read_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 4 BLOCKED: PUBLIC READ DISABLED"
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
                "UNIT 4 BLOCKED: UNSAFE FLAG " + key
            )

    print(
        "PASS: UNIT 4 READ ONLY SAFETY GATE",
        flush=True
    )

    # ========================================================
    # 3. VERIFY UNIT 3 PRICE FRESHNESS
    # ========================================================

    exchange_time_ms = market.get(
        "exchange_time_ms"
    )

    if (
        isinstance(exchange_time_ms, bool)
        or not isinstance(exchange_time_ms, int)
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID EXCHANGE TIME"
        )

    now_ms = int(time.time() * 1000)

    snapshot_age = (
        now_ms - exchange_time_ms
    ) / 1000.0

    if not (-30 <= snapshot_age <= 120):
        raise RuntimeError(
            "UNIT 4 BLOCKED: STALE UNIT 3 SNAPSHOT"
        )

    live_mark_price = float(
        market.get("price", 0)
    )

    if not (
        math.isfinite(live_mark_price)
        and live_mark_price > 0
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID LIVE PRICE"
        )

    # ========================================================
    # 4. WEEX MARK PRICE KLINE REQUEST
    # ========================================================

    interval = "1m"
    candle_limit = 300
    interval_ms = 60000

    endpoint = (
        "/capi/v3/market/markPriceKlines"
    )

    parameters = {
        "symbol": "BTCUSDT",
        "interval": interval,
        "limit": candle_limit,
    }

    url = (
        exchange["contract_base_url"]
        + endpoint
        + "?"
        + urllib.parse.urlencode(parameters)
    )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Unit4-Verification/1.0",
        },
    )

    if (
        request.get_method() != "GET"
        or request.data is not None
    ):
        raise RuntimeError(
            "UNIT 4 BLOCKED: UNSAFE HTTP METHOD"
        )

    class NoRedirect(
        urllib.request.HTTPRedirectHandler
    ):
        def redirect_request(
            self, req, fp, code,
            msg, headers, newurl
        ):
            return None

    opener = urllib.request.build_opener(
        NoRedirect()
    )

    print(
        "UNIT 4 KLINE REQUEST START",
        flush=True
    )

    try:
        with opener.open(
            request,
            timeout=15
        ) as response:

            status = response.getcode()
            raw = response.read(2000001)

    except urllib.error.HTTPError as exc:
        print(
            "UNIT 4 HTTP ERROR =",
            exc.code,
            flush=True
        )
        raise RuntimeError(
            "UNIT 4 WEEX HTTP ERROR"
        ) from exc

    except urllib.error.URLError as exc:
        print(
            "UNIT 4 CONNECTION ERROR =",
            repr(exc.reason),
            flush=True
        )
        raise RuntimeError(
            "UNIT 4 WEEX CONNECTION FAILURE"
        ) from exc

    print(
        "UNIT 4 HTTP STATUS =",
        status,
        flush=True
    )

    if status != 200 or not raw:
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID HTTP RESPONSE"
        )

    if len(raw) > 2000000:
        raise RuntimeError(
            "UNIT 4 BLOCKED: OVERSIZED RESPONSE"
        )

    try:
        response_data = json.loads(
            raw.decode("utf-8")
        )
    except (ValueError, UnicodeDecodeError) as exc:
        raise RuntimeError(
            "UNIT 4 BLOCKED: INVALID KLINE JSON"
        ) from exc

    if not isinstance(response_data, list):
        raise RuntimeError(
            "UNIT 4 BLOCKED: EXPECTED KLINE ARRAY"
        )

    print(
        "PASS: UNIT 4 WEEX KLINE RESPONSE RECEIVED",
        flush=True
    )

    # ========================================================
    # 5. NORMALIZE AND VALIDATE OHLC
    # ========================================================

    normalized = []

    for row in response_data:

        if not isinstance(row, (list, tuple)):
            raise RuntimeError(
                "UNIT 4 INVALID KLINE ROW"
            )

        if len(row) < 7:
            raise RuntimeError(
                "UNIT 4 INCOMPLETE KLINE ROW"
            )

        try:
            open_ms = int(row[0])
            close_ms = int(row[6])

            o = float(row[1])
            h = float(row[2])
            l = float(row[3])
            c = float(row[4])

        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                "UNIT 4 INVALID OHLC VALUE"
            ) from exc

        if not (
            all(
                math.isfinite(v) and v > 0
                for v in (o, h, l, c)
            )
            and h >= max(o, c)
            and l <= min(o, c)
            and h >= l
        ):
            raise RuntimeError(
                "UNIT 4 INVALID OHLC RELATIONSHIP"
            )

        if (
            open_ms <= 0
            or close_ms <= open_ms
            or close_ms - open_ms
            not in (59999, 60000)
            or open_ms % interval_ms != 0
        ):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE TIME"
            )

        normalized.append({
            "open_time_ms": open_ms,
            "close_time_ms": close_ms,
            "open": o,
            "high": h,
            "low": l,
            "close": c,
        })

    normalized.sort(
        key=lambda x: x["open_time_ms"]
    )

    times = [
        c["open_time_ms"]
        for c in normalized
    ]

    if len(times) != len(set(times)):
        raise RuntimeError(
            "UNIT 4 DUPLICATE CANDLE TIMESTAMPS"
        )

    # ========================================================
    # 6. EXCLUDE UNFINISHED CANDLES
    # ========================================================

    # Use both exchange time and current system time.
    # A candle must have ended before the earlier clock.

    cutoff_ms = min(
        exchange_time_ms,
        int(time.time() * 1000)
    )

    closed = [
        c for c in normalized
        if c["close_time_ms"] < cutoff_ms
    ]

    newest_returned_is_closed = (
        bool(normalized)
        and normalized[-1]["close_time_ms"] < cutoff_ms
    )

    if len(closed) < 200:
        raise RuntimeError(
            "UNIT 4 BLOCKED: FEWER THAN 200 CLOSED CANDLES"
        )

    # Reject missing intervals in the analysis window.

    for previous, current in zip(
        closed[-201:-1],
        closed[-200:]
    ):
        if (
            current["open_time_ms"]
            - previous["open_time_ms"]
            != interval_ms
        ):
            raise RuntimeError(
                "UNIT 4 BLOCKED: CANDLE GAP DETECTED"
            )

    latest = closed[-1]
    previous = closed[-2]

    latest_close = latest["close"]
    previous_close = previous["close"]

    latest_open_time_ms = latest[
        "open_time_ms"
    ]

    latest_close_time_ms = latest[
        "close_time_ms"
    ]

    closed_age = (
        cutoff_ms - latest_close_time_ms
    ) / 1000.0

    if closed_age > 125:
        raise RuntimeError(
            "UNIT 4 BLOCKED: CLOSED CANDLE STALE"
        )

    print(
        "UNIT 4 RETURNED CANDLE COUNT =",
        len(normalized),
        flush=True
    )

    print(
        "UNIT 4 CLOSED CANDLE COUNT =",
        len(closed),
        flush=True
    )

    print(
        "UNIT 4 NEWEST RETURNED CLOSED =",
        newest_returned_is_closed,
        flush=True
    )

    print(
        "PASS: UNIT 4 UNFINISHED CANDLE EXCLUDED",
        flush=True
    )

    # ========================================================
    # 7. EMA19 / EMA50 / EMA100 / EMA200
    # ========================================================

    prices = [
        c["close"]
        for c in closed
    ]

    def calculate_ema(values, period):

        if len(values) < period:
            raise RuntimeError(
                "UNIT 4 INSUFFICIENT EMA DATA"
            )

        result = sum(
            values[:period]
        ) / period

        alpha = 2.0 / (period + 1.0)

        for value in values[period:]:
            result = (
                alpha * value
                + (1.0 - alpha) * result
            )

        return result

    ema19 = calculate_ema(prices, 19)
    ema50 = calculate_ema(prices, 50)
    ema100 = calculate_ema(prices, 100)
    ema200 = calculate_ema(prices, 200)

    if not all(
        math.isfinite(value) and value > 0
        for value in (
            ema19, ema50, ema100, ema200
        )
    ):
        raise RuntimeError(
            "UNIT 4 INVALID EMA VALUES"
        )

    print(
        "PASS: UNIT 4 EMA19 =",
        round(ema19, 6),
        flush=True
    )

    print(
        "PASS: UNIT 4 EMA50 =",
        round(ema50, 6),
        flush=True
    )

    print(
        "PASS: UNIT 4 EMA100 =",
        round(ema100, 6),
        flush=True
    )

    print(
        "PASS: UNIT 4 EMA200 =",
        round(ema200, 6),
        flush=True
    )

    # ========================================================
    # 8. EMA STRUCTURE AND SEPARATION
    # ========================================================

    if ema19 > ema50 > ema200:
        ema_structure = "BULLISH"

    elif ema19 < ema50 < ema200:
        ema_structure = "BEARISH"

    else:
        ema_structure = "MIXED"

    ema19_50_separation_pct = (
        abs(ema19 - ema50) / ema50 * 100
    )

    print(
        "UNIT 4 EMA STRUCTURE =",
        ema_structure,
        flush=True
    )

    print(
        "UNIT 4 EMA19/50 SEPARATION % =",
        round(ema19_50_separation_pct, 6),
        flush=True
    )

    # ========================================================
    # 9. CLOSED-CANDLE PRICE MOVEMENT
    # ========================================================

    windows = (1, 5, 15, 30, 60, 120)
    movement = {}

    for minutes in windows:

        reference = prices[-1 - minutes]

        if reference <= 0:
            raise RuntimeError(
                "UNIT 4 INVALID REFERENCE PRICE"
            )

        movement[minutes] = (
            (latest_close - reference)
            / reference * 100.0
        )

        print(
            "UNIT 4", minutes,
            "MINUTE MOVE % =",
            round(movement[minutes], 6),
            flush=True
        )

    short_term_move_pct = movement[1]

    # ========================================================
    # 10. ATR14 VOLATILITY
    # ========================================================

    true_ranges = []

    for i in range(1, len(closed)):

        candle = closed[i]
        preceding = closed[i - 1]

        tr = max(
            candle["high"] - candle["low"],
            abs(
                candle["high"]
                - preceding["close"]
            ),
            abs(
                candle["low"]
                - preceding["close"]
            ),
        )

        true_ranges.append(tr)

    atr14 = sum(
        true_ranges[-14:]
    ) / 14.0

    if not (
        math.isfinite(atr14) and atr14 > 0
    ):
        raise RuntimeError(
            "UNIT 4 INVALID ATR14"
        )

    atr_percent = (
        atr14 / latest_close * 100.0
    )

    print(
        "UNIT 4 ATR14 =",
        round(atr14, 6),
        flush=True
    )

    # ========================================================
    # 11. EMA PRICE EXTENSION
    # ========================================================

    ema_cluster_height = max(
        ema19, ema50, ema200
    ) - min(
        ema19, ema50, ema200
    )

    ema_cluster_height = max(
        ema_cluster_height,
        atr14 * 0.10
    )

    price_extension_cluster = (
        abs(latest_close - ema19)
        / ema_cluster_height
    )

    extension_limit = float(
        strategy.get(
            "scalp_max_ema_extension_clusters",
            1.5
        )
    )

    price_overextended = (
        price_extension_cluster > extension_limit
    )

    # ========================================================
    # 12. SUPPORT AND RESISTANCE
    # ========================================================

    reference_candles = closed[-21:-1]

    resistance20 = max(
        c["high"]
        for c in reference_candles
    )

    support20 = min(
        c["low"]
        for c in reference_candles
    )

    range20 = resistance20 - support20
    range_atr_ratio = range20 / atr14

    # ========================================================
    # 13. BREAKOUT EARLY EVIDENCE
    # ========================================================

    near_resistance = (
        -0.10 * atr14
        <= resistance20 - latest_close
        <= 0.50 * atr14
    )

    near_support = (
        -0.10 * atr14
        <= latest_close - support20
        <= 0.50 * atr14
    )

    breakout_up = (
        latest_close
        > resistance20 + 0.10 * atr14
    )

    breakout_down = (
        latest_close
        < support20 - 0.10 * atr14
    )

    bullish_momentum = (
        movement[5] > 0
        and movement[15] > 0
    )

    bearish_momentum = (
        movement[5] < 0
        and movement[15] < 0
    )

    breakout_developing_long = (
        near_resistance and bullish_momentum
    )

    breakout_developing_short = (
        near_support and bearish_momentum
    )

    breakout_confirmed_long = (
        breakout_up and bullish_momentum
    )

    breakout_confirmed_short = (
        breakout_down and bearish_momentum
    )

    # ========================================================
    # 14. STRUCTURE DEVELOPMENT EVIDENCE
    # ========================================================

    near_ema19 = (
        abs(latest_close - ema19)
        <= 0.75 * atr14
    )

    bullish_recovery = (
        latest_close > previous_close
        and latest_close > latest["open"]
    )

    bearish_recovery = (
        latest_close < previous_close
        and latest_close < latest["open"]
    )

    structure_developing_long = (
        ema_structure == "BULLISH"
        and (near_ema19 or bullish_recovery)
        and movement[15] > 0
    )

    structure_developing_short = (
        ema_structure == "BEARISH"
        and (near_ema19 or bearish_recovery)
        and movement[15] < 0
    )

    # ========================================================
    # 15. SIDEWAYS MARKET EVIDENCE
    # ========================================================

    sideways_candidate = (
        abs(ema19 - ema50) / atr14 <= 0.70
        and range_atr_ratio <= 8.0
        and abs(movement[15])
        <= 1.5 * atr_percent
    )

    # ========================================================
    # 16. DIRECTION VOTES
    # ========================================================

    long_votes = sum((
        ema_structure == "BULLISH",
        movement[5] > 0,
        latest_close > previous_close,
    ))

    short_votes = sum((
        ema_structure == "BEARISH",
        movement[5] < 0,
        latest_close < previous_close,
    ))

    required_votes = int(
        strategy.get(
            "direction_votes_required",
            2
        )
    )

    if required_votes != 2:
        raise RuntimeError(
            "UNIT 4 INVALID VOTE CONFIGURATION"
        )

    long_direction_confirmed = (
        long_votes >= required_votes
    )

    short_direction_confirmed = (
        short_votes >= required_votes
    )

    # ========================================================
    # 17. NORMALIZED UNIT 4 SNAPSHOT
    # ========================================================

    analysis_snapshot = {

        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": "BTCUSDT",
        "interval": interval,
        "price_type": "MARK",

        "live_mark_price": live_mark_price,
        "previous_close": previous_close,
        "latest_close": latest_close,

        "latest_open_time_ms":
            latest_open_time_ms,

        "latest_close_time_ms":
            latest_close_time_ms,

        "exchange_time_ms":
            exchange_time_ms,

        "ema19": ema19,
        "ema50": ema50,
        "ema100": ema100,
        "ema200": ema200,

        "ema19_50_separation_pct":
            ema19_50_separation_pct,

        "ema_structure": ema_structure,

        "short_term_move_pct":
            short_term_move_pct,

        "move_1m_pct": movement[1],
        "move_5m_pct": movement[5],
        "move_15m_pct": movement[15],
        "move_30m_pct": movement[30],
        "move_60m_pct": movement[60],
        "move_120m_pct": movement[120],

        "atr14": atr14,
        "atr_percent": atr_percent,

        "ema_cluster_height":
            ema_cluster_height,

        "price_extension_cluster":
            price_extension_cluster,

        "price_overextended":
            price_overextended,

        "resistance20": resistance20,
        "support20": support20,
        "range20": range20,
        "range_atr_ratio": range_atr_ratio,

        "breakout_developing_long":
            breakout_developing_long,

        "breakout_developing_short":
            breakout_developing_short,

        "breakout_confirmed_long":
            breakout_confirmed_long,

        "breakout_confirmed_short":
            breakout_confirmed_short,

        "structure_developing_long":
            structure_developing_long,

        "structure_developing_short":
            structure_developing_short,

        "sideways_candidate":
            sideways_candidate,

        "long_votes": long_votes,
        "short_votes": short_votes,

        "long_direction_confirmed":
            long_direction_confirmed,

        "short_direction_confirmed":
            short_direction_confirmed,

        "recent_closed_klines": [
            dict(c)
            for c in closed[-60:]
        ],

        "candle_count": len(normalized),

        "closed_candle_count": len(closed),

        "newest_returned_candle_closed":
            newest_returned_is_closed,

        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",

        "read_only": True,
        "trade_authorized": False,
    }

    # ========================================================
    # 18. FINAL SNAPSHOT VALIDATION
    # ========================================================

    required_fields = (
        "symbol",
        "live_mark_price",
        "previous_close",
        "latest_close",
        "ema19",
        "ema50",
        "ema100",
        "ema200",
        "ema19_50_separation_pct",
        "ema_structure",
        "short_term_move_pct",
        "move_1m_pct",
        "move_5m_pct",
        "move_15m_pct",
        "move_30m_pct",
        "move_60m_pct",
        "move_120m_pct",
        "recent_closed_klines",
    )

    for field in required_fields:
        if field not in analysis_snapshot:
            raise RuntimeError(
                "UNIT 4 SNAPSHOT MISSING: " + field
            )

    if (
        analysis_snapshot["read_only"] is not True
        or analysis_snapshot["trade_authorized"]
        is not False
    ):
        raise RuntimeError(
            "UNIT 4 SAFETY CONTRACT FAILURE"
        )

    if latest_close_time_ms >= cutoff_ms:
        raise RuntimeError(
            "UNIT 4 UNFINISHED CANDLE USED"
        )

    if not math.isclose(
        movement[1],
        short_term_move_pct,
        abs_tol=1e-12
    ):
        raise RuntimeError(
            "UNIT 4 MOVEMENT CONSISTENCY FAILURE"
        )

    # ========================================================
    # 19. RENDER DIAGNOSTIC REPORT
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "PASS: UNIT 4 CLOSED-CANDLE EMA ENGINE",
        flush=True
    )

    print(
        "UNIT 4 LIVE MARK PRICE =",
        live_mark_price,
        flush=True
    )

    print(
        "UNIT 4 LATEST CLOSED PRICE =",
        latest_close,
        flush=True
    )

    print(
        "UNIT 4 EMA STRUCTURE =",
        ema_structure,
        flush=True
    )

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
        "UNIT 4 BREAKOUT CONFIRMED LONG =",
        breakout_confirmed_long,
        flush=True
    )

    print(
        "UNIT 4 BREAKOUT CONFIRMED SHORT =",
        breakout_confirmed_short,
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

    print(
        "UNIT 4 DIRECTION VOTES LONG/SHORT =",
        long_votes,
        "/",
        short_votes,
        flush=True
    )

    print(
        "PASS: UNIT 4 ANALYSIS SNAPSHOT READY",
        flush=True
    )

    print(
        "UNIT 4 TRADE AUTHORIZED = FALSE",
        flush=True
    )

    print(
        "UNIT 4 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 4 REAL ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 4 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "FRESH RECONSTRUCTION UNIT 4 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return analysis_snapshot


# ============================================================
# RUN UNIT 4
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_4_RESULT = (
    fresh_reconstruction_unit_4()
)

# Compatibility alias for downstream units.
FRESH_RECONSTRUCTION_UNIT_4_SNAPSHOT = (
    FRESH_RECONSTRUCTION_UNIT_4_RESULT
)

# ============================================================
# END COMPLETE REPLACEMENT - UNIT 4
# ZERO INDENTATION
# ============================================================
