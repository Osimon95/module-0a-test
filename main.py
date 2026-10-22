
# ============================================================
# WEEX BOT - UNIT 1 - RUNTIME FOUNDATION
# COMPLETE REPLACEMENT - ZERO INDENTATION
# ============================================================

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


def log(message):
    timestamp = datetime.now(timezone.utc).isoformat()
    print(timestamp, message, flush=True)


def fresh_reconstruction_unit_1():
    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 1 START")
    print("-" * 80, flush=True)

    try:
        sample = {"ready": True, "unit": 1}
        encoded = json.dumps(sample)

        if json.loads(encoded) != sample:
            raise RuntimeError("JSON ROUNDTRIP FAILED")

        print(
            "PASS: UNIT 1 JSON ENCODE/DECODE",
            flush=True
        )

        query = urllib.parse.urlencode({
            "symbol": "BTCUSDT"
        })

        if query != "symbol=BTCUSDT":
            raise RuntimeError("URL ENCODING FAILED")

        if not callable(urllib.request.Request):
            raise RuntimeError("HTTP REQUEST BUILDER MISSING")

        if not hasattr(urllib.error, "URLError"):
            raise RuntimeError("HTTP ERROR HANDLER MISSING")

        print(
            "PASS: UNIT 1 URL AND HTTP LIBRARIES",
            flush=True
        )

        utc_now = datetime.now(timezone.utc)

        if (
            utc_now.tzinfo is None
            or utc_now.utcoffset().total_seconds() != 0
        ):
            raise RuntimeError("UTC CLOCK FAILED")

        print(
            "PASS: UNIT 1 UTC CLOCK",
            flush=True
        )

    except Exception as exc:
        log("FRESH RECONSTRUCTION UNIT 1 RESULT = FAIL")
        raise RuntimeError(
            "UNIT 1 RUNTIME VERIFICATION FAILED"
        ) from exc

    print(
        "PASS: MAIN.PY STARTED SUCCESSFULLY",
        flush=True
    )

    print(
        "PASS: PYTHON STANDARD LIBRARY AVAILABLE",
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

    log("FRESH RECONSTRUCTION UNIT 1 RESULT = PASS")

    print("=" * 80, flush=True)

    return True


FRESH_RECONSTRUCTION_UNIT_1_READY = (
    fresh_reconstruction_unit_1()
)


# ============================================================
# END UNIT 1
# UNIT 2 CONTINUES UNCHANGED BELOW
# ZERO INDENTATION
# ============================================================


# ============================================================
# START UNIT 2
# ZERO INDENTATION
# WEEX CONFIGURATION AND SAFETY CONTRACT
# ORIGINAL 22525-LINE MODEL BASELINE
# ============================================================


def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 2 START")

    # ========================================================
    # 1. UNIT 1 HANDOVER
    # ========================================================

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
        raise RuntimeError(
            "UNIT 2 BLOCKED: UNIT 1 NOT READY"
        )

    
# ============================================================
# START UNIT 2 - REVISED CONFIGURATION
# ZERO INDENTATION
# ORIGINAL 22525 MODEL + UNIT 3 DATA POLICY
# ============================================================

def fresh_reconstruction_unit_2():

    import math

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 2 START")

    # ========================================================
    # 1. UNIT 1 HANDOVER
    # ========================================================

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
        raise RuntimeError(
            "UNIT 2 BLOCKED: UNIT 1 NOT READY"
        )

    # ========================================================
    # 2. ORIGINAL EXCHANGE CONTRACT
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
    # 3. ORIGINAL SAFETY CONTRACT
    #
    # DO NOT CHANGE THESE FLAGS TO ENABLE UNIT 12.
    # THE ORIGINAL UNIT 12 HAS ITS OWN AUTHENTICATED
    # DEMO ORDER EXECUTION PATH.
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
    # 4. ORIGINAL TRADING STRATEGY
    # NO CHANGES TO ORIGINAL VALUES
    # ========================================================

    strategy = {

        # LEVERAGE AND ENTRY
        "leverage_target": 100,
        "initial_margin_percent": 5.0,
        "initial_fixed_usdt": 0.50,

        # BACKUP LADDER CONFIGURATION
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

        # EXPOSURE
        "exposure_cap_percent": 35.0,
        "progressive_backup_funding": True,
        "full_ladder_reservation_required": False,

        # TAKE PROFITS
        "tp1_allocation_percent": 10.0,
        "tp2_allocation_percent": 20.0,
        "tp3_allocation_percent": 70.0,

        # ROI
        "tp1_net_roi_floor_percent": 5.0,
        "tp2_net_roi_floor_percent": 10.0,
        "tp1_tp2_min_roi_separation_percent": 5.0,

        # DYNAMIC TRAILING
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
    }

    # ========================================================
    # 5. ORIGINAL MARKET PRECISION
    # ========================================================

    market_precision = {
        "quantity_step": 0.0001,
        "minimum_quantity": 0.0001,
        "price_step": 0.1,
    }

    # ========================================================
    # 6. NEW UNIT 3 MARKET DATA POLICY
    #
    # ONLY PUBLIC DATA VALIDATION PARAMETERS.
    # NO TRADING MODE CONTROL.
    # NO ORDER EXECUTION CONTROL.
    # ========================================================

    market_data_policy = {

        # Maximum allowed age of WEEX mark price.
        "max_market_age_seconds": 120.0,

        # Tolerance for exchange/local clock difference.
        "future_tolerance_seconds": 30.0,

        # Protect against malformed large responses.
        "max_response_bytes": 65536,

        # Reject unusable numerical prices.
        "require_finite_price": True,

        # Validate the response timestamp.
        "require_timestamp_validation": True,

        # Reject stale data rather than trading on it.
        "require_fresh_market_data": True,
    }

    # ========================================================
    # 7. COMBINED CONFIGURATION
    #
    # ALL ORIGINAL KEYS PRESERVED.
    # ONLY market_data_policy IS ADDED.
    # ========================================================

    config = {
        "exchange": exchange,
        "execution_environment": execution_environment,
        "safety": safety,
        "strategy": strategy,
        "market_precision": market_precision,
        "market_data_policy": market_data_policy,
    }

    # ========================================================
    # 8. VALIDATE EXCHANGE CONTRACT
    # ========================================================

    if exchange["name"] != "WEEX":
        raise RuntimeError("UNIT 2 INVALID EXCHANGE")

    if exchange["api_version"] != "V3":
        raise RuntimeError("UNIT 2 INVALID API VERSION")

    if exchange["contract_base_url"] != (
        "https://api-contract.weex.com"
    ):
        raise RuntimeError("UNIT 2 INVALID API URL")

    if exchange["market_symbol"] != "BTCUSDT":
        raise RuntimeError("UNIT 2 INVALID MARKET SYMBOL")

    if exchange["demo_order_symbol"] != "BTCSUSDT":
        raise RuntimeError("UNIT 2 INVALID DEMO SYMBOL")

    if execution_environment != "DEMO":
        raise RuntimeError(
            "UNIT 2 INVALID EXECUTION ENVIRONMENT"
        )

    # ========================================================
    # 9. VALIDATE ORIGINAL SAFETY CONTRACT
    # ========================================================

    if safety["public_market_data_read_enabled"] is not True:
        raise RuntimeError(
            "UNIT 2 PUBLIC MARKET READ DISABLED"
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
        if safety[key] is not False:
            raise RuntimeError(
                "UNIT 2 INVALID SAFETY FLAG: " + key
            )

    # ========================================================
    # 10. VALIDATE STRATEGY
    # ========================================================

    if not (
        strategy["leverage_target"] > 0
        and 0 < strategy["initial_margin_percent"] <= 5.0
        and strategy["initial_fixed_usdt"] > 0
    ):
        raise RuntimeError(
            "UNIT 2 INVALID ENTRY CONFIGURATION"
        )

    multipliers = strategy["backup_multipliers"]

    if not (
        strategy["max_backups"] == 5
        and multipliers == (1.0, 1.5, 2.0, 2.5, 3.0)
        and strategy["backup_buffer_percent"] > 0
        and 0 < strategy["backup_margin_percent"] <= 5.0
    ):
        raise RuntimeError(
            "UNIT 2 INVALID BACKUP CONFIGURATION"
        )

    if not (
        0 < strategy["exposure_cap_percent"] <= 35.0
        and strategy["progressive_backup_funding"] is True
        and strategy["full_ladder_reservation_required"]
        is False
    ):
        raise RuntimeError(
            "UNIT 2 INVALID EXPOSURE CONFIGURATION"
        )

    tp_total = sum(
        strategy[key]
        for key in (
            "tp1_allocation_percent",
            "tp2_allocation_percent",
            "tp3_allocation_percent",
        )
    )

    if not math.isclose(
        tp_total, 100.0, rel_tol=0, abs_tol=0.000001
    ):
        raise RuntimeError(
            "UNIT 2 TP ALLOCATION NOT 100%"
        )

    if not (
        strategy["tp1_net_roi_floor_percent"] >= 5.0
        and strategy["tp2_net_roi_floor_percent"] >= 10.0
        and strategy["tp2_net_roi_floor_percent"]
        > strategy["tp1_net_roi_floor_percent"]
        and strategy["tp1_tp2_min_roi_separation_percent"] > 0
    ):
        raise RuntimeError(
            "UNIT 2 INVALID TP ROI CONFIGURATION"
        )

    if not (
        0 < strategy["tp3_trailing_min_percent"]
        <= strategy["tp3_trailing_reference_percent"]
        <= strategy["tp3_trailing_max_percent"]
    ):
        raise RuntimeError(
            "UNIT 2 INVALID TP3 TRAILING"
        )

    for key in (
        "signal_expiry_seconds",
        "loss_cooldown_seconds",
        "mode_confirmations_required",
    ):
        if strategy[key] <= 0:
            raise RuntimeError(
                "UNIT 2 INVALID SIGNAL CONFIG: " + key
            )

    for key in (
        "one_direction_only",
        "anti_duplicate_orders",
        "active_trade_mode_lock",
        "exclusive_mode",
    ):
        if strategy[key] is not True:
            raise RuntimeError(
                "UNIT 2 REQUIRED STRATEGY FLAG FALSE: " + key
            )

    for key in (
        "quantity_step",
        "minimum_quantity",
        "price_step",
    ):
        if market_precision[key] <= 0:
            raise RuntimeError(
                "UNIT 2 INVALID PRECISION: " + key
            )

    # ========================================================
    # 11. VALIDATE NEW MARKET DATA POLICY
    # ========================================================

    if not (
        0 < market_data_policy["max_market_age_seconds"]
        <= 120
    ):
        raise RuntimeError(
            "UNIT 2 INVALID MARKET AGE LIMIT"
        )

    if not (
        0 <= market_data_policy["future_tolerance_seconds"]
        <= 30
    ):
        raise RuntimeError(
            "UNIT 2 INVALID CLOCK TOLERANCE"
        )

    if not (
        1024 <= market_data_policy["max_response_bytes"]
        <= 65536
    ):
        raise RuntimeError(
            "UNIT 2 INVALID RESPONSE LIMIT"
        )

    for key in (
        "require_finite_price",
        "require_timestamp_validation",
        "require_fresh_market_data",
    ):
        if market_data_policy[key] is not True:
            raise RuntimeError(
                "UNIT 2 INVALID DATA PROTECTION: " + key
            )

    # ========================================================
    # 12. FINISH
    # ========================================================

    print(
        "PASS: UNIT 2 ORIGINAL CONFIGURATION PRESERVED",
        flush=True
    )

    print(
        "PASS: UNIT 2 UNIT 3 DATA POLICY READY",
        flush=True
    )

    print(
        "UNIT 2 MARKET DATA MAX AGE =",
        market_data_policy["max_market_age_seconds"],
        "SECONDS",
        flush=True
    )

    print(
        "UNIT 2 MARKET FUTURE TOLERANCE =",
        market_data_policy["future_tolerance_seconds"],
        "SECONDS",
        flush=True
    )

    print(
        "UNIT 2 INITIAL ENTRY USDT =",
        strategy["initial_fixed_usdt"],
        flush=True
    )

    print(
        "UNIT 2 BACKUP MULTIPLIERS =",
        strategy["backup_multipliers"],
        flush=True
    )

    print(
        "UNIT 2 EXPOSURE CAP =",
        strategy["exposure_cap_percent"],
        "%",
        flush=True
    )

    print(
        "UNIT 2 TP ALLOCATION = 10 / 20 / 70",
        flush=True
    )

    print(
        "UNIT 2 EXCHANGE WRITE = NONE",
        flush=True
    )

    log("FRESH RECONSTRUCTION UNIT 2 RESULT = PASS")
    print("=" * 80, flush=True)

    return config


# ============================================================
# UNIT 2 EXECUTION AND HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# END UNIT 2
# ZERO INDENTATION
# ============================================================
     

# ============================================================
# START UNIT 3 - IMPROVED HYBRID V3
# ZERO INDENTATION
#
# SOURCE:
# ORIGINAL 22525-LINE WORKING MODEL
# PLUS SELECTED 12356-LINE MODEL IMPROVEMENTS
#
# PRESERVE:
# - UNIT 2 CONFIGURATION INTERFACE
# - UNIT 4 EIGHT-FIELD SNAPSHOT
# - ORIGINAL UNITS 4 THROUGH 15
# - UNIT 12 DEMO ORDER EXECUTION
#
# PUBLIC MARKET READ ONLY
# NO ACCOUNT MUTATION
# NO ORDER SUBMISSION
# NO NEW BOT MODE
# ============================================================


def fresh_reconstruction_unit_3():

    import json
    import math
    import time
    import urllib.error
    import urllib.parse
    import urllib.request

    print("=" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 3 HYBRID V3 START"
    )

    # ========================================================
    # 1. RECEIVE UNIT 2 CONFIGURATION
    # ========================================================

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 INVALID UNIT 2 CONFIGURATION"
        )

    exchange = config.get("exchange")
    safety = config.get("safety")
    policy = config.get("market_data_policy", {})

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 3 INVALID EXCHANGE CONFIGURATION"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 3 INVALID SAFETY CONFIGURATION"
        )

    if not isinstance(policy, dict):
        raise RuntimeError(
            "UNIT 3 INVALID MARKET POLICY"
        )

    # ========================================================
    # 2. ORIGINAL EXCHANGE CONTRACT
    # ========================================================

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 3 EXCHANGE MUST BE WEEX"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 3 API VERSION MISMATCH"
        )

    base_url = exchange.get(
        "contract_base_url"
    )

    symbol = exchange.get(
        "market_symbol"
    )

    demo_symbol = exchange.get(
        "demo_order_symbol"
    )

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 3 INVALID WEEX API URL"
        )

    if symbol != "BTCUSDT":
        raise RuntimeError(
            "UNIT 3 INVALID PUBLIC SYMBOL"
        )

    if demo_symbol != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 3 INVALID DEMO SYMBOL"
        )

    if config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 3 DEMO ENVIRONMENT REQUIRED"
        )

    print(
        "PASS: UNIT 3 ORIGINAL WEEX CONTRACT",
        flush=True
    )

    # ========================================================
    # 3. PRESERVE UNIT 2 SAFETY CONTRACT
    # ========================================================

    if safety.get(
        "public_market_data_read_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 3 PUBLIC MARKET READ DISABLED"
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
                "UNIT 3 INVALID SAFETY FLAG: " + key
            )

    print(
        "PASS: UNIT 3 PUBLIC READ SAFETY",
        flush=True
    )

    # ========================================================
    # 4. USE REVISED UNIT 2 DATA POLICY
    # ========================================================

    try:

        max_market_age_seconds = float(
            policy.get(
                "max_market_age_seconds",
                120.0
            )
        )

        future_tolerance_seconds = float(
            policy.get(
                "future_tolerance_seconds",
                30.0
            )
        )

        max_response_bytes = int(
            policy.get(
                "max_response_bytes",
                65536
            )
        )

    except (
        TypeError,
        ValueError,
        OverflowError
    ) as exc:

        raise RuntimeError(
            "UNIT 3 INVALID NUMERIC MARKET POLICY"
        ) from exc

    if not (
        math.isfinite(max_market_age_seconds)
        and 0 < max_market_age_seconds <= 120.0
    ):
        raise RuntimeError(
            "UNIT 3 INVALID MAX MARKET AGE"
        )

    if not (
        math.isfinite(future_tolerance_seconds)
        and 0 <= future_tolerance_seconds <= 30.0
    ):
        raise RuntimeError(
            "UNIT 3 INVALID CLOCK TOLERANCE"
        )

    if not (
        1024 <= max_response_bytes <= 65536
    ):
        raise RuntimeError(
            "UNIT 3 INVALID RESPONSE SIZE LIMIT"
        )

    # These protections are mandatory for the
    # improved hybrid data-validation contract.

    for key in (
        "require_finite_price",
        "require_timestamp_validation",
        "require_fresh_market_data",
    ):

        if policy.get(key, True) is not True:

            raise RuntimeError(
                "UNIT 3 REQUIRED DATA PROTECTION "
                "DISABLED: " + key
            )

    print(
        "PASS: UNIT 3 UNIT 2 MARKET POLICY RECEIVED",
        flush=True
    )

    # ========================================================
    # 5. ORIGINAL WEEX PUBLIC ENDPOINT
    # ========================================================

    endpoint = "/capi/v3/market/symbolPrice"

    query = urllib.parse.urlencode({
        "symbol": symbol,
        "priceType": "MARK",
    })

    url = (
        base_url
        + endpoint
        + "?"
        + query
    )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Hybrid-Unit3-V3",
        },
    )

    if request.get_method() != "GET":
        raise RuntimeError(
            "UNIT 3 INVALID HTTP METHOD"
        )

    if request.data is not None:
        raise RuntimeError(
            "UNIT 3 UNEXPECTED REQUEST BODY"
        )

    # ========================================================
    # 6. PROTECT AGAINST HTTP REDIRECTION
    # ========================================================

    class NoRedirect(
        urllib.request.HTTPRedirectHandler
    ):

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

    print(
        "UNIT 3 PUBLIC MARKET REQUEST START",
        flush=True
    )

    # ========================================================
    # 7. PERFORM BOUNDED PUBLIC MARKET READ
    # ========================================================

    try:

        with opener.open(
            request,
            timeout=15
        ) as response:

            http_status = response.getcode()

            raw_body = response.read(
                max_response_bytes + 1
            )

            received_time_ms = int(
                time.time() * 1000
            )

    except urllib.error.HTTPError as exc:

        error_body = exc.read(500).decode(
            "utf-8",
            errors="replace"
        )

        print(
            "UNIT 3 HTTP ERROR CODE =",
            exc.code,
            flush=True
        )

        print(
            "UNIT 3 HTTP ERROR BODY =",
            error_body,
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 WEEX PUBLIC HTTP FAILURE"
        ) from exc

    except urllib.error.URLError as exc:

        print(
            "UNIT 3 NETWORK ERROR =",
            repr(exc.reason),
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 WEEX CONNECTION FAILED"
        ) from exc

    if http_status != 200:
        raise RuntimeError(
            "UNIT 3 HTTP STATUS NOT 200"
        )

    if not raw_body:
        raise RuntimeError(
            "UNIT 3 EMPTY WEEX RESPONSE"
        )

    if len(raw_body) > max_response_bytes:
        raise RuntimeError(
            "UNIT 3 RESPONSE SIZE LIMIT EXCEEDED"
        )

    print(
        "PASS: UNIT 3 WEEX RESPONSE RECEIVED",
        flush=True
    )

    # ========================================================
    # 8. VALIDATE RESPONSE JSON
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
            "UNIT 3 INVALID WEEX JSON"
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError(
            "UNIT 3 INVALID RESPONSE STRUCTURE"
        )

    if payload.get("symbol") != symbol:
        raise RuntimeError(
            "UNIT 3 RESPONSE SYMBOL MISMATCH"
        )

    print(
        "PASS: UNIT 3 RESPONSE SYMBOL =",
        symbol,
        flush=True
    )

    # ========================================================
    # 9. FINITE AND POSITIVE MARK PRICE VALIDATION
    # ========================================================

    raw_price = payload.get("price")

    if isinstance(raw_price, bool):
        raise RuntimeError(
            "UNIT 3 BOOLEAN PRICE REJECTED"
        )

    try:

        mark_price = float(raw_price)

    except (
        TypeError,
        ValueError,
        OverflowError
    ) as exc:

        raise RuntimeError(
            "UNIT 3 INVALID MARK PRICE"
        ) from exc

    if not math.isfinite(mark_price):
        raise RuntimeError(
            "UNIT 3 NON-FINITE PRICE REJECTED"
        )

    if mark_price <= 0:
        raise RuntimeError(
            "UNIT 3 NON-POSITIVE PRICE REJECTED"
        )

    print(
        "PASS: UNIT 3 BTC MARK PRICE =",
        mark_price,
        flush=True
    )

    # ========================================================
    # 10. VERIFY EXCHANGE TIMESTAMP
    # ========================================================

    exchange_time_ms = payload.get("time")

    if (
        isinstance(exchange_time_ms, bool)
        or not isinstance(exchange_time_ms, int)
    ):
        raise RuntimeError(
            "UNIT 3 INVALID TIMESTAMP TYPE"
        )

    if not (
        1000000000000
        <= exchange_time_ms
        < 100000000000000
    ):
        raise RuntimeError(
            "UNIT 3 INVALID MILLISECOND TIMESTAMP"
        )

    market_age_seconds = (
        received_time_ms
        - exchange_time_ms
    ) / 1000.0

    if not math.isfinite(market_age_seconds):
        raise RuntimeError(
            "UNIT 3 INVALID MARKET AGE"
        )

    # ========================================================
    # 11. MARKET DATA FRESHNESS PROTECTION
    # ========================================================

    if market_age_seconds > max_market_age_seconds:

        print(
            "UNIT 3 STALE DATA AGE =",
            round(market_age_seconds, 3),
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 STALE MARKET DATA"
        )

    if market_age_seconds < -future_tolerance_seconds:

        print(
            "UNIT 3 FUTURE TIMESTAMP OFFSET =",
            round(market_age_seconds, 3),
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 EXCHANGE CLOCK MISMATCH"
        )

    print(
        "PASS: UNIT 3 MARKET DATA FRESH",
        flush=True
    )

    print(
        "UNIT 3 MARKET AGE SECONDS =",
        round(market_age_seconds, 3),
        flush=True
    )

    # ========================================================
    # 12. EXACT ORIGINAL UNIT 4 SNAPSHOT CONTRACT
    #
    # ALL EIGHT ORIGINAL FIELDS PRESERVED
    # NO ADDITIONAL REQUIRED DOWNSTREAM FIELDS
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
    }

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

    if any(
        key not in market_snapshot
        for key in required_fields
    ):
        raise RuntimeError(
            "UNIT 3 INCOMPLETE MARKET SNAPSHOT"
        )

    # ========================================================
    # 13. FINAL HANDOVER
    # ========================================================

    print(
        "PASS: UNIT 3 ORIGINAL SNAPSHOT PRESERVED",
        flush=True
    )

    print(
        "PASS: UNIT 3 SNAPSHOT READY FOR UNIT 4",
        flush=True
    )

    print(
        "UNIT 3 AUTHENTICATED API = NONE",
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

    log(
        "FRESH RECONSTRUCTION UNIT 3 HYBRID V3 "
        "RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return market_snapshot


# ============================================================
# UNIT 3 EXECUTION AND UNIT 4 HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# END UNIT 3 - IMPROVED HYBRID V3
# ZERO INDENTATION
#
# ORIGINAL UNIT 4 CONTINUES BELOW
# ============================================================
