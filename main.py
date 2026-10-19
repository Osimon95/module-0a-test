
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


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 5
# ZERO INDENTATION
# SIGNAL QUALIFICATION AND MODE ARBITRATION
# READ ONLY - NO ORDERS
# ============================================================

def fresh_reconstruction_unit_5(
    unit_2_config,
    unit_4_snapshot,
):

    import math
    import time

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 5 START")
    print("-" * 80, flush=True)

    # ========================================================
    # 1. INPUT AND SAFETY CONTRACT
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 5 INVALID UNIT 2 CONFIG"
        )

    if not isinstance(unit_4_snapshot, dict):
        raise RuntimeError(
            "UNIT 5 INVALID UNIT 4 SNAPSHOT"
        )

    strategy = unit_2_config.get("strategy")
    safety = unit_2_config.get("safety")

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 5 INVALID STRATEGY"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 5 INVALID SAFETY CONTRACT"
        )

    if strategy.get("mode_priority") != (
        "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError(
            "UNIT 5 MODE PRIORITY MISMATCH"
        )

    for flag in (
        "demo_order_submission_enabled",
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
        "authenticated_api_enabled",
        "order_endpoint_access_enabled",
    ):
        if safety.get(flag) is not False:
            raise RuntimeError(
                "UNIT 5 UNSAFE CONFIG: " + flag
            )

    if (
        unit_4_snapshot.get("read_only") is not True
        or unit_4_snapshot.get("trade_authorized")
        is not False
        or unit_4_snapshot.get("symbol")
        != "BTCUSDT"
    ):
        raise RuntimeError(
            "UNIT 5 INVALID UNIT 4 SAFETY CONTRACT"
        )

    print(
        "PASS: UNIT 5 RECEIVED UNIT 2 AND UNIT 4",
        flush=True
    )

    # ========================================================
    # 2. CLOSED-CANDLE VALIDATION
    # ========================================================

    candles = unit_4_snapshot.get(
        "recent_closed_klines", []
    )

    if not isinstance(candles, list):
        raise RuntimeError(
            "UNIT 5 INVALID CANDLE SERIES"
        )

    if len(candles) < 30:
        raise RuntimeError(
            "UNIT 5 INSUFFICIENT CLOSED CANDLES"
        )

    latest_close_time = int(
        unit_4_snapshot.get(
            "latest_close_time_ms", 0
        )
    )

    now_ms = int(time.time() * 1000)

    if not (
        0 < now_ms - latest_close_time
        <= 180000
    ):
        raise RuntimeError(
            "UNIT 5 STALE OR FUTURE CANDLE"
        )

    previous_time = None

    for candle in candles:

        if not isinstance(candle, dict):
            raise RuntimeError(
                "UNIT 5 INVALID CANDLE"
            )

        values = [
            float(candle[k])
            for k in ("open", "high", "low", "close")
        ]

        o, h, l, c = values

        if not (
            all(
                math.isfinite(v) and v > 0
                for v in values
            )
            and h >= max(o, c)
            and l <= min(o, c)
        ):
            raise RuntimeError(
                "UNIT 5 INVALID OHLC"
            )

        opening = int(candle["open_time_ms"])
        closing = int(candle["close_time_ms"])

        if (
            closing >= now_ms
            or opening >= closing
            or closing - opening
            not in (59999, 60000)
        ):
            raise RuntimeError(
                "UNIT 5 UNFINISHED CANDLE DETECTED"
            )

        if previous_time is not None:
            if opening - previous_time != 60000:
                raise RuntimeError(
                    "UNIT 5 CANDLE GAP DETECTED"
                )

        previous_time = opening

    if int(candles[-1]["close_time_ms"]) != latest_close_time:
        raise RuntimeError(
            "UNIT 5 CANDLE HANDOVER MISMATCH"
        )

    print(
        "PASS: UNIT 5 FRESH CLOSED CANDLES",
        flush=True
    )

    # ========================================================
    # 3. NORMALIZE MARKET MEASUREMENTS
    # ========================================================

    required = (
        "live_mark_price",
        "ema19", "ema50", "ema100", "ema200",
        "ema19_50_separation_pct",
        "previous_close", "latest_close",
        "short_term_move_pct",
        "move_1m_pct", "move_5m_pct",
        "move_15m_pct", "move_30m_pct",
        "move_60m_pct", "move_120m_pct",
    )

    values = {}

    for key in required:

        if key not in unit_4_snapshot:
            raise RuntimeError(
                "UNIT 5 MISSING INPUT: " + key
            )

        value = float(unit_4_snapshot[key])

        if not math.isfinite(value):
            raise RuntimeError(
                "UNIT 5 NONFINITE INPUT: " + key
            )

        values[key] = value

    price = values["latest_close"]
    previous_close = values["previous_close"]
    live_price = values["live_mark_price"]

    ema19 = values["ema19"]
    ema50 = values["ema50"]
    ema100 = values["ema100"]
    ema200 = values["ema200"]

    move1 = values["move_1m_pct"]
    move5 = values["move_5m_pct"]
    move15 = values["move_15m_pct"]
    move30 = values["move_30m_pct"]

    for key in (
        "latest_close", "previous_close",
        "live_mark_price", "ema19",
        "ema50", "ema100", "ema200"
    ):
        if values[key] <= 0:
            raise RuntimeError(
                "UNIT 5 INVALID PRICE: " + key
            )

    if not math.isclose(
        move1,
        values["short_term_move_pct"],
        abs_tol=1e-8
    ):
        raise RuntimeError(
            "UNIT 5 1M MOVEMENT MISMATCH"
        )

    # ========================================================
    # 4. DIRECTION EVIDENCE
    # ========================================================

    def direction_of(value):
        if value > 0:
            return "LONG"
        if value < 0:
            return "SHORT"
        return "NONE"

    ema_structure = unit_4_snapshot.get(
        "ema_structure", "MIXED"
    )

    ema_direction = (
        "LONG" if ema19 > ema50
        else "SHORT" if ema19 < ema50
        else "NONE"
    )

    long_votes = int(
        unit_4_snapshot.get("long_votes", 0)
    )

    short_votes = int(
        unit_4_snapshot.get("short_votes", 0)
    )

    required_votes = int(
        strategy.get("direction_votes_required", 2)
    )

    if (
        required_votes != 2
        or not 0 <= long_votes <= 3
        or not 0 <= short_votes <= 3
    ):
        raise RuntimeError(
            "UNIT 5 INVALID DIRECTION VOTES"
        )

    direction_evidence = "NONE"

    if (
        long_votes >= required_votes
        and long_votes > short_votes
    ):
        direction_evidence = "LONG"

    elif (
        short_votes >= required_votes
        and short_votes > long_votes
    ):
        direction_evidence = "SHORT"

    print(
        "UNIT 5 DIRECTION EVIDENCE =",
        direction_evidence,
        flush=True
    )

    # ========================================================
    # 5. UNIT 4 HIGHER MODE EVIDENCE
    # ========================================================

    def evidence(key):
        value = unit_4_snapshot.get(key)
        if not isinstance(value, bool):
            raise RuntimeError(
                "UNIT 5 INVALID EVIDENCE: " + key
            )
        return value

    breakout_long = evidence(
        "breakout_confirmed_long"
    )

    breakout_short = evidence(
        "breakout_confirmed_short"
    )

    developing_breakout_long = evidence(
        "breakout_developing_long"
    )

    developing_breakout_short = evidence(
        "breakout_developing_short"
    )

    developing_structure_long = evidence(
        "structure_developing_long"
    )

    developing_structure_short = evidence(
        "structure_developing_short"
    )

    sideways = evidence(
        "sideways_candidate"
    )

    overextended = evidence(
        "price_overextended"
    )

    breakout_developing = (
        developing_breakout_long
        or developing_breakout_short
        or breakout_long
        or breakout_short
    )

    structure_developing = (
        developing_structure_long
        or developing_structure_short
    )

    higher_mode_developing = (
        breakout_developing
        or structure_developing
    )

    # ========================================================
    # 6. CLOSED-CANDLE RANGE EVIDENCE
    # ========================================================

    prior20 = candles[-21:-1]

    range_high = max(
        c["high"] for c in prior20
    )

    range_low = min(
        c["low"] for c in prior20
    )

    range_width_pct = (
        (range_high - range_low)
        / range_low * 100.0
    )

    recent_high = max(
        c["high"] for c in candles[-20:]
    )

    recent_low = min(
        c["low"] for c in candles[-20:]
    )

    recent_range_pct = (
        (recent_high - recent_low)
        / price * 100.0
    )

    # Historical range is only a feasibility
    # indicator; it is not a profit forecast.

    estimated_roundtrip_fee_pct = (
        2.0 * float(
            strategy.get(
                "scalp_estimated_taker_fee_percent",
                0.08
            )
        )
    )

    estimated_extra_friction_pct = 0.02
    minimum_net_price_profit_pct = 0.05

    minimum_range_pct = (
        estimated_roundtrip_fee_pct
        + estimated_extra_friction_pct
        + minimum_net_price_profit_pct
    )

    scalp_range_feasible = (
        recent_range_pct >= minimum_range_pct
    )

    # ========================================================
    # 7. BREAKOUT QUALIFICATION
    # ========================================================

    # Unit 4 confirms a breakout using price,
    # prior range and directional momentum.
    #
    # Unit 5 additionally requires agreement
    # with its 2-of-3 directional evidence.

    breakout_ready_long = (
        breakout_long
        and direction_evidence == "LONG"
        and not overextended
    )

    breakout_ready_short = (
        breakout_short
        and direction_evidence == "SHORT"
        and not overextended
    )

    breakout_ready = (
        breakout_ready_long
        or breakout_ready_short
    )

    breakout_candidate = breakout_developing

    breakout_direction = (
        "LONG" if (
            breakout_ready_long
            or developing_breakout_long
        )
        else "SHORT" if (
            breakout_ready_short
            or developing_breakout_short
        )
        else "NONE"
    )

    # ========================================================
    # 8. STRUCTURE QUALIFICATION
    # ========================================================

    # Developing structure from Unit 4 is
    # evidence, not an automatic trade.
    #
    # Confirm directional evidence and
    # avoid overextended entries.

    structure_ready_long = (
        developing_structure_long
        and direction_evidence == "LONG"
        and not overextended
        and move15 > 0
    )

    structure_ready_short = (
        developing_structure_short
        and direction_evidence == "SHORT"
        and not overextended
        and move15 < 0
    )

    structure_ready = (
        structure_ready_long
        or structure_ready_short
    )

    structure_candidate = structure_developing

    structure_direction = (
        "LONG" if (
            structure_ready_long
            or developing_structure_long
        )
        else "SHORT" if (
            structure_ready_short
            or developing_structure_short
        )
        else "NONE"
    )

    # ========================================================
    # 9. SCALP ELIGIBILITY
    # ========================================================

    scalp_direction = direction_evidence

    scalp_1m_support = (
        direction_of(move1) == scalp_direction
        and scalp_direction != "NONE"
    )

    scalp_5m_support = (
        direction_of(move5) == scalp_direction
        and scalp_direction != "NONE"
    )

    sideways_context = (
        sideways
        and not higher_mode_developing
        and not overextended
    )

    scalp_ready = (
        sideways_context
        and scalp_direction != "NONE"
        and scalp_5m_support
        and scalp_range_feasible
    )

    # Even if true, Scalp is never finally
    # qualified here. Unit 6 must inspect
    # quality, fees and prospective reward.

    # ========================================================
    # 10. EXCLUSIVE MODE ARBITRATION
    # ========================================================

    active_mode = "NONE"
    direction = "NONE"
    qualified = False

    candidate_mode = "NONE"
    candidate_stage = "NONE"

    qualification_reason = (
        "NO_ACCEPTABLE_CANDIDATE"
    )

    if breakout_ready:

        active_mode = "BREAKOUT"

        direction = (
            "LONG" if breakout_ready_long
            else "SHORT"
        )

        qualified = True
        candidate_mode = "BREAKOUT"
        candidate_stage = "QUALIFIED"

        qualification_reason = (
            "BREAKOUT_CLOSED_CANDLE_CONFIRMATION"
        )

    elif breakout_candidate:

        candidate_mode = "BREAKOUT"
        candidate_stage = "DEVELOPING"

        qualification_reason = (
            "BREAKOUT_DEVELOPING_SCALP_DEFERRED"
        )

    elif structure_ready:

        active_mode = "STRUCTURE"

        direction = (
            "LONG" if structure_ready_long
            else "SHORT"
        )

        qualified = True
        candidate_mode = "STRUCTURE"
        candidate_stage = "QUALIFIED"

        qualification_reason = (
            "STRUCTURE_EARLY_QUALIFICATION"
        )

    elif structure_candidate:

        candidate_mode = "STRUCTURE"
        candidate_stage = "DEVELOPING"

        qualification_reason = (
            "STRUCTURE_DEVELOPING_SCALP_DEFERRED"
        )

    elif scalp_ready:

        candidate_mode = "SCALP"
        candidate_stage = "PENDING_UNIT_6"

        qualification_reason = (
            "SCALP_PENDING_QUALITY_AND_FEES"
        )

    elif sideways and not scalp_range_feasible:

        qualification_reason = (
            "SCALP_HISTORICAL_RANGE_INSUFFICIENT"
        )

    elif overextended:

        qualification_reason = (
            "PRICE_OVEREXTENDED"
        )

    # ========================================================
    # 11. ARBITRATION SAFETY ASSERTIONS
    # ========================================================

    if qualified and (
        active_mode not in ("BREAKOUT", "STRUCTURE")
        or direction not in ("LONG", "SHORT")
    ):
        raise RuntimeError(
            "UNIT 5 INVALID QUALIFIED SIGNAL"
        )

    if (
        candidate_mode == "SCALP"
        and higher_mode_developing
    ):
        raise RuntimeError(
            "UNIT 5 SCALP PREEMPTED HIGHER MODE"
        )

    if (
        candidate_mode == "SCALP"
        and qualified
    ):
        raise RuntimeError(
            "UNIT 5 SCALP PREMATURELY QUALIFIED"
        )

    # ========================================================
    # 12. NORMALIZED SIGNAL CANDIDATE
    # ========================================================

    signal_candidate = {

        "symbol": "BTCUSDT",

        "qualified": qualified,
        "active_mode": active_mode,
        "direction": direction,

        "candidate_mode": candidate_mode,
        "candidate_stage": candidate_stage,

        "higher_mode_developing":
            higher_mode_developing,

        "qualification_reason":
            qualification_reason,

        "live_mark_price": live_price,
        "previous_close": previous_close,
        "latest_close": price,

        "ema19": ema19,
        "ema50": ema50,
        "ema100": ema100,
        "ema200": ema200,

        "ema19_50_separation_pct":
            values["ema19_50_separation_pct"],

        "ema_structure": ema_structure,
        "ema_direction": ema_direction,

        "momentum_direction":
            direction_of(move1),

        "direction_agreement":
            direction_evidence != "NONE",

        "direction_evidence":
            direction_evidence,

        "short_term_move_pct": move1,
        "absolute_short_term_move_pct":
            abs(move1),

        "move_1m_pct": move1,
        "move_5m_pct": move5,
        "move_15m_pct": move15,
        "move_30m_pct": move30,

        "move_60m_pct":
            values["move_60m_pct"],

        "move_120m_pct":
            values["move_120m_pct"],

        "momentum_1m_direction":
            direction_of(move1),

        "momentum_5m_direction":
            direction_of(move5),

        "momentum_15m_direction":
            direction_of(move15),

        "momentum_30m_direction":
            direction_of(move30),

        "momentum_60m_direction":
            direction_of(values["move_60m_pct"]),

        "momentum_120m_direction":
            direction_of(values["move_120m_pct"]),

        "scalp_direction": scalp_direction,
        "scalp_move_pct": abs(move5),
        "scalp_1m_support": scalp_1m_support,

        "structure_direction":
            structure_direction,

        "structure_move_pct": abs(move15),

        "breakout_direction":
            breakout_direction,

        "breakout_move_pct": abs(move30),

        "breakout_fast_support": (
            direction_of(move5)
            == breakout_direction
            and breakout_direction != "NONE"
        ),

        "breakout_candidate":
            breakout_candidate,

        "breakout_ready":
            breakout_ready,

        "structure_candidate":
            structure_candidate,

        "structure_ready":
            structure_ready,

        "sideways_context":
            sideways_context,

        "scalp_range_feasible":
            scalp_range_feasible,

        "scalp_ready":
            scalp_ready,

        "range_high": range_high,
        "range_low": range_low,
        "range_width_pct": range_width_pct,

        "recent_range_pct":
            recent_range_pct,

        "minimum_sustainable_range_pct":
            minimum_range_pct,

        "price_above_ema19":
            live_price > ema19,

        "price_above_ema50":
            live_price > ema50,

        "price_above_ema200":
            live_price > ema200,

        "latest_close_above_previous":
            price > previous_close,

        "read_only": True,
        "trade_authorized": False,
    }

    # ========================================================
    # 13. RENDER DIAGNOSTICS
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "UNIT 5 DIRECTION EVIDENCE =",
        direction_evidence,
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT CANDIDATE =",
        breakout_candidate,
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT READY =",
        breakout_ready,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE CANDIDATE =",
        structure_candidate,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE READY =",
        structure_ready,
        flush=True
    )

    print(
        "UNIT 5 HIGHER MODE DEVELOPING =",
        higher_mode_developing,
        flush=True
    )

    print(
        "UNIT 5 SIDEWAYS CONTEXT =",
        sideways_context,
        flush=True
    )

    print(
        "UNIT 5 SCALP RANGE % =",
        round(recent_range_pct, 6),
        flush=True
    )

    print(
        "UNIT 5 MINIMUM SCALP RANGE % =",
        round(minimum_range_pct, 6),
        flush=True
    )

    print(
        "UNIT 5 SCALP RANGE FEASIBLE =",
        scalp_range_feasible,
        flush=True
    )

    print(
        "UNIT 5 SCALP READY =",
        scalp_ready,
        flush=True
    )

    print(
        "UNIT 5 CANDIDATE MODE =",
        candidate_mode,
        flush=True
    )

    print(
        "UNIT 5 CANDIDATE STAGE =",
        candidate_stage,
        flush=True
    )

    print(
        "UNIT 5 ACTIVE MODE =",
        active_mode,
        flush=True
    )

    print(
        "UNIT 5 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 5 QUALIFIED =",
        qualified,
        flush=True
    )

    print(
        "UNIT 5 QUALIFICATION REASON =",
        qualification_reason,
        flush=True
    )

    print(
        "UNIT 5 TRADE AUTHORIZED = FALSE",
        flush=True
    )

    print(
        "UNIT 5 NETWORK REQUEST = NONE",
        flush=True
    )

    print(
        "UNIT 5 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 5 REAL ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 5 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "FRESH RECONSTRUCTION UNIT 5 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return signal_candidate


# ============================================================
# RUN UNIT 5
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    FRESH_RECONSTRUCTION_UNIT_4_RESULT
)

FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
    fresh_reconstruction_unit_5(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
    )
)

# ============================================================
# END COMPLETE REPLACEMENT - UNIT 5
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE REPLACEMENT - UNIT 6
# ZERO INDENTATION
#
# ENTRY ADMISSION AND SCALP QUALITY
# BREAKOUT / STRUCTURE / SCALP
#
# NO NETWORK REQUEST
# NO DEMO ORDER
# NO REAL ORDER
# NO EXCHANGE WRITE
# ============================================================

def fresh_reconstruction_unit_6(
    unit_2_config,
    unit_4_analysis,
    unit_5_candidate,
):

    import math
    import time

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 6 START")
    print("-" * 80, flush=True)

    # ========================================================
    # 1. INPUT VALIDATION
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 6 INVALID UNIT 2 CONFIG"
        )

    if not isinstance(unit_4_analysis, dict):
        raise RuntimeError(
            "UNIT 6 INVALID UNIT 4 ANALYSIS"
        )

    if not isinstance(unit_5_candidate, dict):
        raise RuntimeError(
            "UNIT 6 INVALID UNIT 5 CANDIDATE"
        )

    strategy = unit_2_config.get("strategy", {})
    safety = unit_2_config.get("safety", {})

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 6 INVALID STRATEGY"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 6 INVALID SAFETY SETTINGS"
        )

    if strategy.get("mode_priority") != (
        "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError(
            "UNIT 6 MODE PRIORITY MISMATCH"
        )

    for key in (
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
    ):
        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 6 UNSAFE CONFIG: " + key
            )

    if (
        unit_4_analysis.get("read_only") is not True
        or unit_4_analysis.get(
            "trade_authorized"
        ) is not False
        or unit_5_candidate.get(
            "read_only"
        ) is not True
        or unit_5_candidate.get(
            "trade_authorized"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT 6 READ ONLY CONTRACT FAILURE"
        )

    if (
        unit_4_analysis.get("symbol") != "BTCUSDT"
        or unit_5_candidate.get("symbol")
        != "BTCUSDT"
    ):
        raise RuntimeError(
            "UNIT 6 SYMBOL MISMATCH"
        )

    print(
        "PASS: UNIT 6 RECEIVED UNITS 2, 4 AND 5",
        flush=True
    )

    print(
        "PASS: UNIT 6 SAFETY CONTRACT",
        flush=True
    )

    # ========================================================
    # 2. VERIFY CURRENT CLOSED-CANDLE DATA
    # ========================================================

    candles = unit_4_analysis.get(
        "recent_closed_klines", []
    )

    if not isinstance(candles, list):
        raise RuntimeError(
            "UNIT 6 INVALID CANDLE ARRAY"
        )

    if len(candles) < 30:
        raise RuntimeError(
            "UNIT 6 INSUFFICIENT CLOSED CANDLES"
        )

    latest_close_time_ms = int(
        unit_4_analysis.get(
            "latest_close_time_ms", 0
        )
    )

    current_ms = int(time.time() * 1000)

    age_ms = current_ms - latest_close_time_ms

    if not 0 < age_ms <= 180000:
        raise RuntimeError(
            "UNIT 6 STALE OR FUTURE CANDLE DATA"
        )

    previous_open_ms = None

    for candle in candles:

        if not isinstance(candle, dict):
            raise RuntimeError(
                "UNIT 6 INVALID CANDLE OBJECT"
            )

        try:
            o = float(candle["open"])
            h = float(candle["high"])
            l = float(candle["low"])
            c = float(candle["close"])

            open_ms = int(
                candle["open_time_ms"]
            )

            close_ms = int(
                candle["close_time_ms"]
            )

        except (TypeError, ValueError, KeyError) as exc:
            raise RuntimeError(
                "UNIT 6 INVALID CANDLE FIELDS"
            ) from exc

        if not (
            all(
                math.isfinite(x) and x > 0
                for x in (o, h, l, c)
            )
            and h >= max(o, c)
            and l <= min(o, c)
            and close_ms < current_ms
            and close_ms - open_ms
            in (59999, 60000)
        ):
            raise RuntimeError(
                "UNIT 6 INVALID CLOSED CANDLE"
            )

        if previous_open_ms is not None:
            if open_ms - previous_open_ms != 60000:
                raise RuntimeError(
                    "UNIT 6 CANDLE SEQUENCE GAP"
                )

        previous_open_ms = open_ms

    if (
        int(candles[-1]["close_time_ms"])
        != latest_close_time_ms
    ):
        raise RuntimeError(
            "UNIT 6 CANDLE SNAPSHOT MISMATCH"
        )

    print(
        "PASS: UNIT 6 FRESH CLOSED-CANDLE EVIDENCE",
        flush=True
    )

    # ========================================================
    # 3. VERIFY UNIT 5 SELECTION
    # ========================================================

    mode = unit_5_candidate.get(
        "active_mode", "NONE"
    )

    side = unit_5_candidate.get(
        "direction", "NONE"
    )

    qualified = (
        unit_5_candidate.get("qualified")
        is True
    )

    candidate_mode = unit_5_candidate.get(
        "candidate_mode", "NONE"
    )

    candidate_stage = unit_5_candidate.get(
        "candidate_stage", "NONE"
    )

    unit5_reason = str(
        unit_5_candidate.get(
            "qualification_reason", "UNKNOWN"
        )
    )

    higher_mode_developing = (
        unit_5_candidate.get(
            "higher_mode_developing"
        ) is True
    )

    if mode not in (
        "NONE", "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError(
            "UNIT 6 INVALID ACTIVE MODE"
        )

    if side not in (
        "NONE", "LONG", "SHORT"
    ):
        raise RuntimeError(
            "UNIT 6 INVALID DIRECTION"
        )

    if candidate_mode not in (
        "NONE", "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError(
            "UNIT 6 INVALID CANDIDATE MODE"
        )

    if candidate_stage not in (
        "NONE", "DEVELOPING",
        "QUALIFIED", "PENDING_UNIT_6"
    ):
        raise RuntimeError(
            "UNIT 6 INVALID CANDIDATE STAGE"
        )

    if qualified and not (
        mode in ("BREAKOUT", "STRUCTURE")
        and side in ("LONG", "SHORT")
        and candidate_mode == mode
        and candidate_stage == "QUALIFIED"
    ):
        raise RuntimeError(
            "UNIT 6 INVALID QUALIFIED HANDOVER"
        )

    scalp_pending = (
        candidate_mode == "SCALP"
        and candidate_stage == "PENDING_UNIT_6"
        and not qualified
        and mode == "NONE"
        and side == "NONE"
        and not higher_mode_developing
    )

    print(
        "UNIT 6 UNIT 5 ACTIVE MODE =",
        mode,
        flush=True
    )

    print(
        "UNIT 6 CANDIDATE MODE =",
        candidate_mode,
        flush=True
    )

    print(
        "UNIT 6 CANDIDATE STAGE =",
        candidate_stage,
        flush=True
    )

    print(
        "UNIT 6 HIGHER MODE DEVELOPING =",
        higher_mode_developing,
        flush=True
    )

    print(
        "UNIT 6 SCALP PENDING =",
        scalp_pending,
        flush=True
    )

    # ========================================================
    # 4. VALIDATE MARKET NUMERICS
    # ========================================================

    def numeric(source, key, positive=False):

        try:
            value = float(source[key])

        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError(
                "UNIT 6 INVALID NUMERIC FIELD: " + key
            ) from exc

        if not math.isfinite(value):
            raise RuntimeError(
                "UNIT 6 NONFINITE FIELD: " + key
            )

        if positive and value <= 0:
            raise RuntimeError(
                "UNIT 6 NONPOSITIVE FIELD: " + key
            )

        return value

    price = numeric(
        unit_4_analysis,
        "latest_close",
        positive=True
    )

    live_price = numeric(
        unit_4_analysis,
        "live_mark_price",
        positive=True
    )

    ema19 = numeric(
        unit_4_analysis, "ema19", True
    )

    ema50 = numeric(
        unit_4_analysis, "ema50", True
    )

    ema100 = numeric(
        unit_4_analysis, "ema100", True
    )

    ema200 = numeric(
        unit_4_analysis, "ema200", True
    )

    atr14 = numeric(
        unit_4_analysis, "atr14", True
    )

    move1 = numeric(
        unit_4_analysis, "move_1m_pct"
    )

    move5 = numeric(
        unit_4_analysis, "move_5m_pct"
    )

    move15 = numeric(
        unit_4_analysis, "move_15m_pct"
    )

    move30 = numeric(
        unit_4_analysis, "move_30m_pct"
    )

    leverage = numeric(
        strategy,
        "leverage_target",
        positive=True
    )

    # This is only configured leverage.
    # Actual exchange leverage is not verified
    # by Unit 6.

    # ========================================================
    # 5. INITIALIZE ADMISSION STATE
    # ========================================================

    execution_intent = False

    admission_reason = (
        "NO_QUALIFIED_SIGNAL"
    )

    admitted_mode = "NONE"
    admitted_direction = "NONE"

    scalp_score = None
    scalp_pass = None

    details = {}

    # ========================================================
    # 6. BREAKOUT ADMISSION
    # ========================================================

    if (
        qualified
        and mode == "BREAKOUT"
        and side in ("LONG", "SHORT")
    ):

        expected_evidence = (
            "breakout_confirmed_long"
            if side == "LONG"
            else "breakout_confirmed_short"
        )

        if (
            unit_4_analysis.get(
                expected_evidence
            ) is not True
        ):
            admission_reason = (
                "BREAKOUT_EVIDENCE_NOT_CONFIRMED"
            )

        elif (
            unit_5_candidate.get(
                "direction_evidence"
            ) != side
        ):
            admission_reason = (
                "BREAKOUT_DIRECTION_CONFLICT"
            )

        elif unit_4_analysis.get(
            "price_overextended"
        ) is True:
            admission_reason = (
                "BREAKOUT_PRICE_OVEREXTENDED"
            )

        else:

            execution_intent = True

            admitted_mode = "BREAKOUT"
            admitted_direction = side

            admission_reason = (
                "BREAKOUT_PRELIMINARY_ADMISSION_PASS"
            )

    # ========================================================
    # 7. STRUCTURE ADMISSION
    # ========================================================

    elif (
        qualified
        and mode == "STRUCTURE"
        and side in ("LONG", "SHORT")
    ):

        expected_evidence = (
            "structure_developing_long"
            if side == "LONG"
            else "structure_developing_short"
        )

        if (
            unit_4_analysis.get(
                expected_evidence
            ) is not True
        ):
            admission_reason = (
                "STRUCTURE_EVIDENCE_NOT_CONFIRMED"
            )

        elif (
            unit_5_candidate.get(
                "direction_evidence"
            ) != side
        ):
            admission_reason = (
                "STRUCTURE_DIRECTION_CONFLICT"
            )

        elif unit_4_analysis.get(
            "price_overextended"
        ) is True:
            admission_reason = (
                "STRUCTURE_PRICE_OVEREXTENDED"
            )

        else:

            execution_intent = True

            admitted_mode = "STRUCTURE"
            admitted_direction = side

            admission_reason = (
                "STRUCTURE_PRELIMINARY_ADMISSION_PASS"
            )

    # ========================================================
    # 8. SCALP ADMISSION
    # QUALITY 70/100
    # PRICE WEIGHT 50/100
    # FEES AND SLIPPAGE INCLUDED
    # ========================================================

    elif scalp_pending:

        scalp_side = unit_5_candidate.get(
            "scalp_direction", "NONE"
        )

        if scalp_side not in ("LONG", "SHORT"):
            admission_reason = (
                "SCALP_INVALID_PROPOSED_DIRECTION"
            )

        elif unit_5_candidate.get(
            "sideways_context"
        ) is not True:
            admission_reason = (
                "SCALP_NOT_SIDEWAYS_MARKET"
            )

        elif unit_5_candidate.get(
            "scalp_range_feasible"
        ) is not True:
            admission_reason = (
                "SCALP_FEES_EXCEED_RANGE_FEASIBILITY"
            )

        elif unit_4_analysis.get(
            "sideways_candidate"
        ) is not True:
            admission_reason = (
                "SCALP_UNIT_4_SIDEWAYS_NOT_CONFIRMED"
            )

        elif unit_4_analysis.get(
            "price_overextended"
        ) is True:
            admission_reason = (
                "SCALP_PRICE_OVEREXTENDED"
            )

        else:

            # ------------------------------------------------
            # 8A. HISTORICAL PRICE HEADROOM
            # ------------------------------------------------

            history = candles[-30:-1]

            resistance = max(
                c["high"] for c in history
            )

            support = min(
                c["low"] for c in history
            )

            if scalp_side == "LONG":

                headroom_pct = max(
                    0.0,
                    (resistance - price)
                    / price * 100.0
                )

                direction_momentum = move5
                ema_support = price >= ema19

            else:

                headroom_pct = max(
                    0.0,
                    (price - support)
                    / price * 100.0
                )

                direction_momentum = -move5
                ema_support = price <= ema19

            # Historical levels do not guarantee
            # future profitable exits.

            # ------------------------------------------------
            # 8B. ESTIMATED TRADING COSTS
            # ------------------------------------------------

            fee_per_side_pct = numeric(
                strategy,
                "scalp_estimated_taker_fee_percent"
            )

            slippage_roundtrip_pct = 0.02

            if fee_per_side_pct < 0:
                raise RuntimeError(
                    "UNIT 6 NEGATIVE FEE ESTIMATE"
                )

            total_cost_pct = (
                fee_per_side_pct * 2.0
                + slippage_roundtrip_pct
            )

            projected_net_price_pct = (
                headroom_pct - total_cost_pct
            )

            projected_net_roi_pct = (
                projected_net_price_pct * leverage
            )

            minimum_net_roi_pct = numeric(
                strategy,
                "scalp_min_net_roi_percent",
                positive=True
            )

            required_gross_headroom_pct = (
                total_cost_pct
                + minimum_net_roi_pct / leverage
            )

            fee_pass = (
                headroom_pct
                >= required_gross_headroom_pct
                and projected_net_price_pct > 0
            )

            # ------------------------------------------------
            # 8C. PRICE SCORE: 50 POINTS
            # ------------------------------------------------

            if required_gross_headroom_pct <= 0:
                raise RuntimeError(
                    "UNIT 6 INVALID COST FLOOR"
                )

            price_score = (
                50.0
                * min(
                    1.0,
                    headroom_pct
                    / (
                        required_gross_headroom_pct
                        * 1.5
                    )
                )
            )

            # ------------------------------------------------
            # 8D. OTHER FACTORS: 50 POINTS
            # ------------------------------------------------

            momentum_score = (
                15.0
                if direction_momentum > 0
                else 0.0
            )

            ema_score = (
                15.0 if ema_support else 0.0
            )

            one_minute_support = (
                move1 > 0
                if scalp_side == "LONG"
                else move1 < 0
            )

            freshness_score = (
                10.0
                if one_minute_support
                else 0.0
            )

            atr_percent = (
                atr14 / price * 100.0
            )

            volatility_score = (
                10.0
                if atr_percent > 0
                else 0.0
            )

            other_score = (
                momentum_score
                + ema_score
                + freshness_score
                + volatility_score
            )

            scalp_score = round(
                price_score + other_score,
                4
            )

            score_floor = numeric(
                strategy,
                "scalp_quality_threshold",
                positive=True
            )

            if not 0 < score_floor <= 100:
                raise RuntimeError(
                    "UNIT 6 INVALID QUALITY THRESHOLD"
                )

            scalp_pass = (
                scalp_score >= score_floor
                and fee_pass
                and direction_momentum > 0
            )

            details = {

                "side": scalp_side,

                "headroom_pct":
                    headroom_pct,

                "fee_per_side_pct":
                    fee_per_side_pct,

                "slippage_roundtrip_pct":
                    slippage_roundtrip_pct,

                "total_cost_pct":
                    total_cost_pct,

                "projected_net_price_pct":
                    projected_net_price_pct,

                "projected_net_roi_pct":
                    projected_net_roi_pct,

                "minimum_net_roi_pct":
                    minimum_net_roi_pct,

                "required_gross_headroom_pct":
                    required_gross_headroom_pct,

                "price_score":
                    round(price_score, 4),

                "other_score":
                    round(other_score, 4),

                "momentum_score":
                    momentum_score,

                "ema_score":
                    ema_score,

                "freshness_score":
                    freshness_score,

                "volatility_score":
                    volatility_score,

                "fee_pass":
                    fee_pass,

                "historical_target_only":
                    True,

                "actual_exchange_fees_verified":
                    False,

                "actual_spread_verified":
                    False,

                "actual_slippage_verified":
                    False,

                "persistence_confirmations": 0,
                "persistence_required": 2,
                "persistence_verified": False,
            }

            print(
                "UNIT 6 SCALP PRICE SCORE =",
                round(price_score, 4),
                flush=True
            )

            print(
                "UNIT 6 SCALP OTHER SCORE =",
                round(other_score, 4),
                flush=True
            )

            print(
                "UNIT 6 SCALP TOTAL SCORE =",
                scalp_score,
                flush=True
            )

            print(
                "UNIT 6 SCALP HEADROOM % =",
                round(headroom_pct, 6),
                flush=True
            )

            print(
                "UNIT 6 SCALP COST % =",
                round(total_cost_pct, 6),
                flush=True
            )

            print(
                "UNIT 6 SCALP EST NET ROI % =",
                round(projected_net_roi_pct, 6),
                flush=True
            )

            print(
                "UNIT 6 SCALP FEE PASS =",
                fee_pass,
                flush=True
            )

            if not fee_pass:

                admission_reason = (
                    "SCALP_INSUFFICIENT_NET_HEADROOM"
                )

            elif scalp_score < score_floor:

                admission_reason = (
                    "SCALP_QUALITY_BELOW_THRESHOLD"
                )

            elif not scalp_pass:

                admission_reason = (
                    "SCALP_DIRECTION_MOMENTUM_CONFLICT"
                )

            else:

                # A single snapshot is insufficient
                # to prove signal persistence.
                #
                # Preserve the quality PASS, but
                # do not authorize execution intent.

                admission_reason = (
                    "SCALP_QUALITY_PASS_"
                    "AWAITING_PERSISTENCE_AND_LIVE_COSTS"
                )

                admitted_mode = "NONE"
                admitted_direction = "NONE"

                execution_intent = False

    # ========================================================
    # 9. ALL OTHER CANDIDATES
    # ========================================================

    else:

        if (
            candidate_stage == "DEVELOPING"
            and candidate_mode in (
                "BREAKOUT", "STRUCTURE"
            )
        ):

            admission_reason = (
                candidate_mode
                + "_DEVELOPING_NOT_QUALIFIED"
            )

        elif higher_mode_developing:

            admission_reason = (
                "HIGHER_MODE_DEVELOPING_SCALP_BLOCKED"
            )

        elif candidate_stage == "PENDING_UNIT_6":

            admission_reason = (
                "PENDING_CANDIDATE_INVALID"
            )

        else:

            admission_reason = (
                "UNIT_5_NOT_QUALIFIED:"
                + unit5_reason
            )

    # ========================================================
    # 10. FINAL ARBITRATION SAFETY
    # ========================================================

    if execution_intent:

        if not qualified:
            raise RuntimeError(
                "UNIT 6 UNQUALIFIED EXECUTION INTENT"
            )

        if admitted_mode not in (
            "BREAKOUT", "STRUCTURE"
        ):
            raise RuntimeError(
                "UNIT 6 UNSAFE ADMITTED MODE"
            )

        if admitted_direction not in (
            "LONG", "SHORT"
        ):
            raise RuntimeError(
                "UNIT 6 UNSAFE ADMITTED DIRECTION"
            )

    if (
        higher_mode_developing
        and admitted_mode == "SCALP"
    ):
        raise RuntimeError(
            "UNIT 6 SCALP PREEMPTION FAILURE"
        )

    # ========================================================
    # 11. OUTPUT CONTRACT
    # ========================================================

    result = {

        "execution_intent":
            execution_intent,

        "signal_qualified":
            qualified,

        "active_mode":
            admitted_mode,

        "direction":
            admitted_direction,

        "candidate_mode":
            candidate_mode,

        "candidate_stage":
            candidate_stage,

        "higher_mode_developing":
            higher_mode_developing,

        "unit_5_reason":
            unit5_reason,

        "admission_reason":
            admission_reason,

        "leverage_target":
            leverage,

        "leverage_regime": (
            "GE_100X" if leverage >= 100
            else "50_99X" if leverage >= 50
            else "20_49X" if leverage >= 20
            else "11_19X" if leverage >= 11
            else "LE_10X"
        ),

        "sideways_regime":
            unit_4_analysis.get(
                "sideways_candidate"
            ) is True,

        "ema_compressed": (
            abs(ema19 - ema50)
            / ema50 * 100.0 <= 0.09
        ),

        "compression_threshold_pct":
            0.09,

        "momentum_conflict": (
            admitted_direction == "LONG"
            and move5 < 0
        ) or (
            admitted_direction == "SHORT"
            and move5 > 0
        ),

        "persistence_window": 3,

        "persistence_required": 2,

        "persistence_confirmations":
            details.get(
                "persistence_confirmations", 0
            ),

        "persistence_directions": [],

        "persistence_pass": (
            True
            if admitted_mode in (
                "BREAKOUT", "STRUCTURE"
            )
            else False
        ),

        "fifteen_minute_support_pass": (
            move15 > 0
            if admitted_direction == "LONG"
            else move15 < 0
            if admitted_direction == "SHORT"
            else False
        ),

        "scalp_quality_score":
            scalp_score,

        "scalp_quality_minimum":
            float(
                strategy.get(
                    "scalp_quality_threshold",
                    70.0
                )
            ),

        "scalp_quality_pass":
            scalp_pass,

        "scalp_quality_details":
            details,

        "read_only": True,

        "trade_authorized": False,

        "order_payload_generated": False,

        "actual_exchange_leverage_verified":
            False,

        "actual_exchange_fees_verified":
            False,
    }

    # ========================================================
    # 12. FINAL RENDER DIAGNOSTICS
    # ========================================================

    print("-" * 80, flush=True)

    print(
        "UNIT 6 SELECTED MODE =",
        result["active_mode"],
        flush=True
    )

    print(
        "UNIT 6 DIRECTION =",
        result["direction"],
        flush=True
    )

    print(
        "UNIT 6 UNIT 5 QUALIFIED =",
        qualified,
        flush=True
    )

    print(
        "UNIT 6 ADMISSION REASON =",
        admission_reason,
        flush=True
    )

    print(
        "UNIT 6 SCALP SCORE =",
        scalp_score,
        flush=True
    )

    print(
        "UNIT 6 SCALP QUALITY PASS =",
        scalp_pass,
        flush=True
    )

    print(
        "UNIT 6 EXECUTION INTENT =",
        execution_intent,
        flush=True
    )

    print(
        "PASS: UNIT 6 NORMALIZED OUTPUT",
        flush=True
    )

    print(
        "UNIT 6 TRADE AUTHORIZED = FALSE",
        flush=True
    )

    print(
        "UNIT 6 NETWORK REQUEST = NONE",
        flush=True
    )

    print(
        "UNIT 6 ORDER PAYLOAD = NONE",
        flush=True
    )

    print(
        "UNIT 6 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 6 REAL ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 6 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "FRESH RECONSTRUCTION UNIT 6 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 6
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE = (
    fresh_reconstruction_unit_6(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_4_RESULT,
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE,
    )
)

# ============================================================
# END COMPLETE REPLACEMENT - UNIT 6
# ZERO INDENTATION
# ============================================================


# ============================================================
# START UNIT 6 CONTROLLED BRANCH TEST HARNESS
# ZERO INDENTATION
# TEMPORARY TEST CODE - REMOVE AFTER VERIFICATION
# ============================================================

def run_unit_6_controlled_tests():

    import copy
    import time

    print("=" * 80, flush=True)
    print(
        "UNIT 6 CONTROLLED BRANCH TEST START",
        flush=True
    )
    print("-" * 80, flush=True)

    config = copy.deepcopy(
        FRESH_RECONSTRUCTION_CONFIG
    )

    base_u4 = copy.deepcopy(
        FRESH_RECONSTRUCTION_UNIT_4_RESULT
    )

    base_u5 = copy.deepcopy(
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
    )

    results = []

    # ========================================================
    # HELPER - EXECUTE ONE BRANCH TEST
    # ========================================================

    def check_case(
        name,
        u4,
        u5,
        expected_intent,
        expected_mode,
        expected_reason,
    ):

        print("-" * 80, flush=True)
        print(
            "TEST CASE =",
            name,
            flush=True
        )

        try:

            result = fresh_reconstruction_unit_6(
                config,
                u4,
                u5,
            )

            actual_intent = result.get(
                "execution_intent"
            )

            actual_mode = result.get(
                "active_mode"
            )

            actual_reason = result.get(
                "admission_reason", ""
            )

            passed = (
                actual_intent is expected_intent
                and actual_mode == expected_mode
                and actual_reason == expected_reason
                and result.get(
                    "trade_authorized"
                ) is False
                and result.get(
                    "order_payload_generated"
                ) is False
            )

            print(
                "TEST EXPECTED REASON =",
                expected_reason,
                flush=True
            )

            print(
                "TEST ACTUAL REASON =",
                actual_reason,
                flush=True
            )

        except Exception as exc:

            passed = False

            print(
                "TEST EXCEPTION =",
                repr(exc),
                flush=True
            )

        results.append((name, passed))

        print(
            "TEST RESULT =",
            "PASS" if passed else "FAIL",
            flush=True
        )

    # ========================================================
    # CASE 1 - QUALIFIED BREAKOUT SHORT
    # ========================================================

    u4 = copy.deepcopy(base_u4)
    u5 = copy.deepcopy(base_u5)

    u4["breakout_confirmed_short"] = True
    u4["breakout_confirmed_long"] = False
    u4["price_overextended"] = False

    u5.update({
        "qualified": True,
        "active_mode": "BREAKOUT",
        "direction": "SHORT",
        "candidate_mode": "BREAKOUT",
        "candidate_stage": "QUALIFIED",
        "direction_evidence": "SHORT",
        "higher_mode_developing": True,
        "qualification_reason":
            "CONTROLLED_BREAKOUT_SHORT",
    })

    check_case(
        "BREAKOUT_SHORT_ADMISSION",
        u4,
        u5,
        True,
        "BREAKOUT",
        "BREAKOUT_PRELIMINARY_ADMISSION_PASS",
    )

    # ========================================================
    # CASE 2 - QUALIFIED STRUCTURE SHORT
    # ========================================================

    u4 = copy.deepcopy(base_u4)
    u5 = copy.deepcopy(base_u5)

    u4["structure_developing_short"] = True
    u4["structure_developing_long"] = False
    u4["breakout_confirmed_short"] = False
    u4["breakout_confirmed_long"] = False
    u4["price_overextended"] = False
    u4["move_15m_pct"] = -0.10

    u5.update({
        "qualified": True,
        "active_mode": "STRUCTURE",
        "direction": "SHORT",
        "candidate_mode": "STRUCTURE",
        "candidate_stage": "QUALIFIED",
        "direction_evidence": "SHORT",
        "higher_mode_developing": True,
        "qualification_reason":
            "CONTROLLED_STRUCTURE_SHORT",
    })

    check_case(
        "STRUCTURE_SHORT_ADMISSION",
        u4,
        u5,
        True,
        "STRUCTURE",
        "STRUCTURE_PRELIMINARY_ADMISSION_PASS",
    )

    # ========================================================
    # CASE 3 - DEVELOPING STRUCTURE REJECTED
    # ========================================================

    u4 = copy.deepcopy(base_u4)
    u5 = copy.deepcopy(base_u5)

    u5.update({
        "qualified": False,
        "active_mode": "NONE",
        "direction": "NONE",
        "candidate_mode": "STRUCTURE",
        "candidate_stage": "DEVELOPING",
        "higher_mode_developing": True,
        "qualification_reason":
            "CONTROLLED_STRUCTURE_DEVELOPING",
    })

    check_case(
        "DEVELOPING_STRUCTURE_REJECTION",
        u4,
        u5,
        False,
        "NONE",
        "STRUCTURE_DEVELOPING_NOT_QUALIFIED",
    )

    # ========================================================
    # HELPER - SYNTHETIC SIDEWAYS TEST CANDLES
    #
    # These are deliberately constructed test candles.
    # They do NOT represent WEEX market observations.
    # ========================================================

    def make_scalp_case(highroom):

        u4 = copy.deepcopy(base_u4)
        u5 = copy.deepcopy(base_u5)

        p = 82000.0

        last_open_ms = int(
            base_u4["recent_closed_klines"][-1][
                "open_time_ms"
            ]
        )

        synthetic = []

        for i in range(60):

            opening = (
                last_open_ms
                - (59 - i) * 60000
            )

            closing = p - (59 - i) * 2.0

            opening_price = closing - 1.0

            synthetic.append({
                "open_time_ms": opening,
                "close_time_ms":
                    opening + 59999,
                "open": opening_price,
                "high": closing + highroom,
                "low": opening_price - 1.0,
                "close": closing,
            })

        u4["recent_closed_klines"] = synthetic
        u4["latest_open_time_ms"] = (
            synthetic[-1]["open_time_ms"]
        )
        u4["latest_close_time_ms"] = (
            synthetic[-1]["close_time_ms"]
        )

        u4.update({
            "latest_close": p,
            "previous_close": p - 2.0,
            "live_mark_price": p,
            "ema19": p - 25.0,
            "ema50": p - 35.0,
            "ema100": p - 45.0,
            "ema200": p - 55.0,
            "atr14": 10.0,
            "move_1m_pct": 0.00244,
            "move_5m_pct": 0.01220,
            "move_15m_pct": 0.03660,
            "sideways_candidate": True,
            "price_overextended": False,
        })

        u5.update({
            "qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_mode": "SCALP",
            "candidate_stage": "PENDING_UNIT_6",
            "higher_mode_developing": False,
            "scalp_direction": "LONG",
            "sideways_context": True,
            "scalp_range_feasible": True,
            "qualification_reason":
                "CONTROLLED_SCALP_PENDING",
        })

        return u4, u5

    # ========================================================
    # CASE 4 - SCALP QUALITY PASSES,
    # BUT EXECUTION STAYS DISABLED
    # ========================================================

    u4, u5 = make_scalp_case(500.0)

    check_case(
        "SCALP_QUALITY_PASS_HELD",
        u4,
        u5,
        False,
        "NONE",
        "SCALP_QUALITY_PASS_"
        "AWAITING_PERSISTENCE_AND_LIVE_COSTS",
    )

    # ========================================================
    # CASE 5 - SCALP HEADROOM INSUFFICIENT
    # ========================================================

    u4, u5 = make_scalp_case(1.0)

    check_case(
        "SCALP_FEE_REJECTION",
        u4,
        u5,
        False,
        "NONE",
        "SCALP_INSUFFICIENT_NET_HEADROOM",
    )

    # ========================================================
    # CASE 6 - SCALP CANNOT OVERRIDE STRUCTURE
    # ========================================================

    u4, u5 = make_scalp_case(500.0)

    u5["higher_mode_developing"] = True

    check_case(
        "SCALP_HIGHER_MODE_PROTECTION",
        u4,
        u5,
        False,
        "NONE",
        "HIGHER_MODE_DEVELOPING_SCALP_BLOCKED",
    )

    # ========================================================
    # FINAL RESULTS
    # ========================================================

    print("=" * 80, flush=True)
    print(
        "UNIT 6 CONTROLLED TEST SUMMARY",
        flush=True
    )

    passed_count = sum(
        1 for _, passed in results
        if passed
    )

    for name, passed in results:

        print(
            name,
            "=",
            "PASS" if passed else "FAIL",
            flush=True
        )

    print(
        "UNIT 6 TESTS PASSED =",
        passed_count,
        "/",
        len(results),
        flush=True
    )

    print(
        "UNIT 6 CONTROLLED EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "UNIT 6 CONTROLLED DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 6 CONTROLLED REAL ORDER = NONE",
        flush=True
    )

    if passed_count != len(results):
        raise RuntimeError(
            "UNIT 6 CONTROLLED BRANCH TEST FAILED"
        )

    print(
        "FINAL VERDICT: UNIT 6 CONTROLLED TEST PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return True


# ============================================================
# RUN CONTROLLED TEST HARNESS
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_6_TEST_RESULT = (
    run_unit_6_controlled_tests()
)

# ============================================================
# END UNIT 6 CONTROLLED BRANCH TEST HARNESS
# ZERO INDENTATION
# ============================================================
