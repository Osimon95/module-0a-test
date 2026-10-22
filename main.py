
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


# ============================================================
# START UNIT 4 - IMPROVED HYBRID V1
# ZERO INDENTATION
# ORIGINAL MARKET CONTRACT + NEW STRATEGY EVIDENCE
# PUBLIC MARKET READ ONLY
# ============================================================

def fresh_reconstruction_unit_4():

    import json
    import math
    import urllib.parse
    import urllib.request

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 4 HYBRID START")

    # ========================================================
    # 1. RECEIVE UNITS 2 AND 3
    # ========================================================

    config = FRESH_RECONSTRUCTION_CONFIG
    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 4 INVALID CONFIG")

    if not isinstance(market, dict):
        raise RuntimeError("UNIT 4 INVALID MARKET")

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})

    if (
        exchange.get("contract_base_url")
        != "https://api-contract.weex.com"
        or exchange.get("market_symbol") != "BTCUSDT"
        or market.get("symbol") != "BTCUSDT"
        or market.get("price_type") != "MARK"
        or market.get("read_only") is not True
    ):
        raise RuntimeError("UNIT 4 CONTRACT MISMATCH")

    if safety.get(
        "public_market_data_read_enabled"
    ) is not True:
        raise RuntimeError("UNIT 4 MARKET READ DISABLED")

    for key in (
        "demo_order_submission_enabled",
        "real_order_submission_enabled",
    ):
        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 4 SAFETY CONTRACT MISMATCH"
            )

    exchange_ms = int(market["exchange_time_ms"])
    live_mark = float(market["price"])

    if not math.isfinite(live_mark) or live_mark <= 0:
        raise RuntimeError("UNIT 4 INVALID MARK PRICE")

    print("PASS: UNIT 4 RECEIVED UNITS 2 AND 3", flush=True)

    # ========================================================
    # 2. ORIGINAL WEEX PUBLIC CANDLE ENDPOINT
    # ========================================================

    endpoint = "/capi/v3/market/markPriceKlines"

    query = urllib.parse.urlencode({
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 300,
    })

    url = (
        exchange["contract_base_url"]
        + endpoint + "?" + query
    )

    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Hybrid-Unit4",
        },
    )

    if request.get_method() != "GET":
        raise RuntimeError("UNIT 4 INVALID HTTP METHOD")

    with urllib.request.urlopen(
        request, timeout=15
    ) as response:

        if response.getcode() != 200:
            raise RuntimeError("UNIT 4 HTTP FAILED")

        raw_body = response.read(1024 * 1024 + 1)

    if not raw_body or len(raw_body) > 1024 * 1024:
        raise RuntimeError("UNIT 4 INVALID RESPONSE SIZE")

    payload = json.loads(raw_body.decode("utf-8"))

    if not isinstance(payload, list):
        raise RuntimeError("UNIT 4 INVALID KLINE RESPONSE")

    # ========================================================
    # 3. NORMALIZE MARKET CANDLES
    # ========================================================

    candles = []

    for raw in payload:

        if not isinstance(raw, (list, tuple)):
            raise RuntimeError("UNIT 4 INVALID KLINE")

        if len(raw) < 7:
            raise RuntimeError("UNIT 4 SHORT KLINE")

        candle = {
            "open_time_ms": int(raw[0]),
            "open": float(raw[1]),
            "high": float(raw[2]),
            "low": float(raw[3]),
            "close": float(raw[4]),
            "volume": float(raw[5]),
            "close_time_ms": int(raw[6]),
        }

        if not all(
            math.isfinite(candle[key])
            for key in (
                "open", "high", "low",
                "close", "volume"
            )
        ):
            raise RuntimeError("UNIT 4 NONFINITE KLINE")

        if not (
            candle["low"] > 0
            and candle["volume"] >= 0
            and candle["low"]
                <= min(candle["open"], candle["close"])
            and candle["high"]
                >= max(candle["open"], candle["close"])
            and candle["close_time_ms"]
                > candle["open_time_ms"]
        ):
            raise RuntimeError("UNIT 4 INVALID OHLC")

        candles.append(candle)

    candles.sort(
        key=lambda item: item["open_time_ms"]
    )

    for index in range(1, len(candles)):
        if (
            candles[index]["open_time_ms"]
            <= candles[index - 1]["open_time_ms"]
        ):
            raise RuntimeError(
                "UNIT 4 DUPLICATE CANDLE"
            )

    # ========================================================
    # 4. USE CLOSED CANDLES ONLY
    # ========================================================

    closed = [
        candle for candle in candles
        if candle["close_time_ms"] <= exchange_ms
    ]

    if len(closed) < 201:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT CLOSED HISTORY"
        )

    latest = closed[-1]
    previous = closed[-2]

    candle_age = (
        exchange_ms - latest["close_time_ms"]
    ) / 1000.0

    if not 0 <= candle_age <= 180:
        raise RuntimeError(
            "UNIT 4 STALE CLOSED CANDLES"
        )

    prices = [
        candle["close"] for candle in closed
    ]

    print(
        "PASS: UNIT 4 CLOSED CANDLES =",
        len(closed),
        flush=True
    )

    # ========================================================
    # 5. ORIGINAL EMA ENGINE
    # ========================================================

    def calculate_ema(period):

        value = sum(prices[:period]) / period
        weight = 2.0 / (period + 1.0)

        for price in prices[period:]:
            value = (
                price * weight
                + value * (1.0 - weight)
            )

        return value

    ema19 = calculate_ema(19)
    ema50 = calculate_ema(50)
    ema100 = calculate_ema(100)
    ema200 = calculate_ema(200)

    if ema19 > ema50 > ema200:
        ema_structure = "BULLISH"
    elif ema19 < ema50 < ema200:
        ema_structure = "BEARISH"
    else:
        ema_structure = "MIXED"

    ema_separation = (
        abs(ema19 - ema50) / ema50 * 100.0
    )

    # ========================================================
    # 6. ORIGINAL MULTI-WINDOW MOMENTUM
    # ========================================================

    moves = {}

    for window in (1, 5, 15, 30, 60, 120):
        reference_price = prices[-window - 1]

        moves[window] = (
            prices[-1] / reference_price - 1.0
        ) * 100.0

    # ========================================================
    # 7. NEW ATR14 VOLATILITY ANALYSIS
    # ========================================================

    true_ranges = []

    for index in range(1, len(closed)):

        current = closed[index]
        prior = closed[index - 1]

        true_range = max(
            current["high"] - current["low"],
            abs(
                current["high"] - prior["close"]
            ),
            abs(
                current["low"] - prior["close"]
            ),
        )

        true_ranges.append(true_range)

    atr14 = sum(true_ranges[-14:]) / 14.0

    if atr14 <= 0:
        raise RuntimeError("UNIT 4 INVALID ATR")

    atr_percent = (
        atr14 / latest["close"] * 100.0
    )

    # ========================================================
    # 8. NEW SUPPORT AND RESISTANCE
    # ========================================================

    reference20 = closed[-21:-1]

    support20 = min(
        candle["low"] for candle in reference20
    )

    resistance20 = max(
        candle["high"] for candle in reference20
    )

    range_atr_ratio = (
        resistance20 - support20
    ) / atr14

    near_resistance = (
        -0.10 * atr14
        <= resistance20 - latest["close"]
        <= 0.50 * atr14
    )

    near_support = (
        -0.10 * atr14
        <= latest["close"] - support20
        <= 0.50 * atr14
    )

    # ========================================================
    # 9. NEW EMA PRICE EXTENSION EVIDENCE
    # ========================================================

    ema_cluster_height = max(
        max(ema19, ema50, ema200)
        - min(ema19, ema50, ema200),
        0.10 * atr14,
    )

    price_extension_cluster = (
        abs(latest["close"] - ema19)
        / ema_cluster_height
    )

    price_overextended = (
        price_extension_cluster > 1.5
    )

    # ========================================================
    # 10. NEW BREAKOUT EVIDENCE
    # ========================================================

    bullish_momentum = (
        moves[5] > 0 and moves[15] > 0
    )

    bearish_momentum = (
        moves[5] < 0 and moves[15] < 0
    )

    breakout_developing_long = (
        near_resistance and bullish_momentum
    )

    breakout_developing_short = (
        near_support and bearish_momentum
    )

    breakout_confirmed_long = (
        latest["close"]
        > resistance20 + 0.10 * atr14
        and bullish_momentum
    )

    breakout_confirmed_short = (
        latest["close"]
        < support20 - 0.10 * atr14
        and bearish_momentum
    )

    # ========================================================
    # 11. NEW EARLY STRUCTURE EVIDENCE
    # ========================================================

    near_ema19 = (
        abs(latest["close"] - ema19)
        <= 0.75 * atr14
    )

    bullish_recovery = (
        latest["close"] > previous["close"]
        and latest["close"] > latest["open"]
    )

    bearish_recovery = (
        latest["close"] < previous["close"]
        and latest["close"] < latest["open"]
    )

    structure_developing_long = (
        ema19 > ema50 > ema200
        and (near_ema19 or bullish_recovery)
        and moves[15] > 0
    )

    structure_developing_short = (
        ema19 < ema50 < ema200
        and (near_ema19 or bearish_recovery)
        and moves[15] < 0
    )

    # ========================================================
    # 12. NEW SIDEWAYS REGIME EVIDENCE
    # ========================================================

    sideways_candidate = (
        abs(ema19 - ema50) / atr14 <= 0.70
        and range_atr_ratio <= 8.0
        and abs(moves[15]) <= 1.5 * atr_percent
    )

    # ========================================================
    # 13. NEW DIRECTIONAL EVIDENCE
    # ========================================================

    long_votes = sum((
        ema_structure == "BULLISH",
        moves[5] > 0,
        latest["close"] > previous["close"],
    ))

    short_votes = sum((
        ema_structure == "BEARISH",
        moves[5] < 0,
        latest["close"] < previous["close"],
    ))

    direction_evidence = "NONE"

    if long_votes >= 2 and long_votes > short_votes:
        direction_evidence = "LONG"

    elif (
        short_votes >= 2
        and short_votes > long_votes
    ):
        direction_evidence = "SHORT"

    # ========================================================
    # 14. ORIGINAL UNIT 5 SNAPSHOT + NEW EVIDENCE
    # ========================================================

    analysis_snapshot = {

        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": "BTCUSDT",
        "interval": "1m",
        "price_type": "MARK",

        "live_mark_price": live_mark,
        "previous_close": previous["close"],
        "latest_close": latest["close"],

        "latest_open_time_ms":
            latest["open_time_ms"],

        "latest_close_time_ms":
            latest["close_time_ms"],

        "exchange_time_ms": exchange_ms,

        "ema19": ema19,
        "ema50": ema50,
        "ema100": ema100,
        "ema200": ema200,

        "ema19_50_separation_pct":
            ema_separation,

        "short_term_move_pct": moves[1],

        "move_1m_pct": moves[1],
        "move_5m_pct": moves[5],
        "move_15m_pct": moves[15],
        "move_30m_pct": moves[30],
        "move_60m_pct": moves[60],
        "move_120m_pct": moves[120],

        "ema_structure": ema_structure,

        "recent_closed_klines": [
            dict(candle)
            for candle in closed[-60:]
        ],

        "candle_count": len(candles),
        "closed_candle_count": len(closed),

        "newest_returned_candle_closed":
            candles[-1]["close_time_ms"]
            <= exchange_ms,

        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",

        "read_only": True,

        # NEW HYBRID ANALYSIS FIELDS

        "atr14": atr14,
        "atr_percent": atr_percent,

        "ema_cluster_height":
            ema_cluster_height,

        "price_extension_cluster":
            price_extension_cluster,

        "price_overextended":
            price_overextended,

        "support20": support20,
        "resistance20": resistance20,

        "range20_atr_ratio": range_atr_ratio,

        "near_resistance": near_resistance,
        "near_support": near_support,

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

        "direction_long_votes": long_votes,
        "direction_short_votes": short_votes,

        "direction_evidence":
            direction_evidence,

        "candle_age_seconds": candle_age,
        "candle_data_fresh": True,

        "strategy_evidence_version":
            "U4_HYBRID_V1",

        "trade_authorized": False,
    }

    # ========================================================
    # 15. FINAL HANDOVER
    # ========================================================

    print(
        "PASS: UNIT 4 ORIGINAL UNIT 5 HANDOVER",
        flush=True
    )

    print(
        "UNIT 4 ATR14 =",
        round(atr14, 4),
        flush=True
    )

    print(
        "UNIT 4 DIRECTION EVIDENCE =",
        direction_evidence,
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
        "UNIT 4 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "FRESH RECONSTRUCTION UNIT 4 HYBRID "
        "RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return analysis_snapshot


# ============================================================
# UNIT 4 EXECUTION AND UNIT 5 HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)


# ============================================================
# END UNIT 4 - IMPROVED HYBRID V1
# ZERO INDENTATION
# UNIT 5 CONTINUES BELOW
# ============================================================


# ============================================================
# START UNIT 5 - IMPROVED HYBRID V1
# ZERO INDENTATION
#
# ORIGINAL 22525-LINE MODEL INTERFACE
# PLUS NEWER 12356-LINE SIGNAL ARBITRATION
#
# PRIORITY:
# BREAKOUT -> STRUCTURE -> SCALP
#
# NO EXCHANGE WRITE
# NO NEW BOT MODE
# UNIT 12 DEMO ORDER PATH PRESERVED
# ============================================================

def fresh_reconstruction_unit_5(
    unit_2_config,
    unit_4_snapshot
):

    import math

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 5 HYBRID START")

    # ========================================================
    # 1. INPUT COMPATIBILITY
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError("UNIT 5 INVALID CONFIG")

    if not isinstance(unit_4_snapshot, dict):
        raise RuntimeError("UNIT 5 INVALID ANALYSIS")

    strategy = unit_2_config.get("strategy", {})
    safety = unit_2_config.get("safety", {})

    if not isinstance(strategy, dict):
        raise RuntimeError("UNIT 5 INVALID STRATEGY")

    if not isinstance(safety, dict):
        raise RuntimeError("UNIT 5 INVALID SAFETY")

    if unit_4_snapshot.get("symbol") != "BTCUSDT":
        raise RuntimeError("UNIT 5 SYMBOL MISMATCH")

    if unit_4_snapshot.get("read_only") is not True:
        raise RuntimeError("UNIT 5 INVALID MARKET SOURCE")

    if unit_4_snapshot.get("candle_data_fresh") is not True:
        raise RuntimeError("UNIT 5 STALE CANDLE DATA")

    if unit_4_snapshot.get("trade_authorized") is not False:
        raise RuntimeError("UNIT 5 UNEXPECTED AUTHORIZATION")

    for key in (
        "authenticated_api_enabled",
        "account_access_enabled",
        "position_access_enabled",
        "order_endpoint_access_enabled",
        "demo_order_submission_enabled",
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
    ):
        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 5 SAFETY MISMATCH: " + key
            )

    print(
        "PASS: UNIT 5 RECEIVED HYBRID UNITS 2 AND 4",
        flush=True
    )

    # ========================================================
    # 2. REQUIRED ORIGINAL HANDOVER VALUES
    # ========================================================

    def number(key):

        value = float(unit_4_snapshot[key])

        if not math.isfinite(value):
            raise RuntimeError(
                "UNIT 5 NONFINITE VALUE: " + key
            )

        return value

    required = (
        "live_mark_price",
        "latest_close",
        "previous_close",
        "ema19",
        "ema50",
        "ema200",
        "ema19_50_separation_pct",
        "short_term_move_pct",
        "move_1m_pct",
        "move_5m_pct",
        "move_15m_pct",
        "move_30m_pct",
        "move_60m_pct",
        "move_120m_pct",
    )

    for key in required:
        if key not in unit_4_snapshot:
            raise RuntimeError(
                "UNIT 5 MISSING ORIGINAL FIELD: " + key
            )

    live_mark = number("live_mark_price")
    latest_close = number("latest_close")
    previous_close = number("previous_close")

    ema19 = number("ema19")
    ema50 = number("ema50")
    ema100 = number("ema100")
    ema200 = number("ema200")

    separation_pct = number(
        "ema19_50_separation_pct"
    )

    move1 = number("move_1m_pct")
    move5 = number("move_5m_pct")
    move15 = number("move_15m_pct")
    move30 = number("move_30m_pct")
    move60 = number("move_60m_pct")
    move120 = number("move_120m_pct")

    short_move = number("short_term_move_pct")

    if min(
        live_mark, latest_close, previous_close,
        ema19, ema50, ema100, ema200
    ) <= 0:
        raise RuntimeError("UNIT 5 INVALID MARKET PRICE")

    # ========================================================
    # 3. RECEIVE NEW UNIT 4 EVIDENCE
    # ========================================================

    direction_evidence = unit_4_snapshot.get(
        "direction_evidence", "NONE"
    )

    if direction_evidence not in (
        "LONG", "SHORT", "NONE"
    ):
        raise RuntimeError("UNIT 5 INVALID DIRECTION")

    breakout_developing_long = (
        unit_4_snapshot.get(
            "breakout_developing_long", False
        ) is True
    )

    breakout_developing_short = (
        unit_4_snapshot.get(
            "breakout_developing_short", False
        ) is True
    )

    breakout_confirmed_long = (
        unit_4_snapshot.get(
            "breakout_confirmed_long", False
        ) is True
    )

    breakout_confirmed_short = (
        unit_4_snapshot.get(
            "breakout_confirmed_short", False
        ) is True
    )

    structure_developing_long = (
        unit_4_snapshot.get(
            "structure_developing_long", False
        ) is True
    )

    structure_developing_short = (
        unit_4_snapshot.get(
            "structure_developing_short", False
        ) is True
    )

    sideways = (
        unit_4_snapshot.get(
            "sideways_candidate", False
        ) is True
    )

    price_overextended = (
        unit_4_snapshot.get(
            "price_overextended", False
        ) is True
    )

    atr14 = number("atr14")

    if atr14 <= 0:
        raise RuntimeError("UNIT 5 INVALID ATR")

    # ========================================================
    # 4. DIRECTION AND MOMENTUM HELPERS
    # ========================================================

    def movement_direction(value):

        if value > 0:
            return "LONG"

        if value < 0:
            return "SHORT"

        return "NONE"

    momentum1 = movement_direction(move1)
    momentum5 = movement_direction(move5)
    momentum15 = movement_direction(move15)
    momentum30 = movement_direction(move30)
    momentum60 = movement_direction(move60)
    momentum120 = movement_direction(move120)

    ema_direction = "NONE"

    if ema19 > ema50 > ema200:
        ema_direction = "LONG"

    elif ema19 < ema50 < ema200:
        ema_direction = "SHORT"

    def votes_for(side):

        if side == "LONG":
            return int(unit_4_snapshot.get(
                "direction_long_votes", 0
            ))

        if side == "SHORT":
            return int(unit_4_snapshot.get(
                "direction_short_votes", 0
            ))

        return 0

    # ========================================================
    # 5. BREAKOUT QUALIFICATION
    # ========================================================

    breakout_candidate = any((
        breakout_developing_long,
        breakout_developing_short,
        breakout_confirmed_long,
        breakout_confirmed_short,
    ))

    breakout_ready_long = (
        breakout_confirmed_long
        and direction_evidence == "LONG"
        and momentum5 == "LONG"
        and votes_for("LONG") >= 2
    )

    breakout_ready_short = (
        breakout_confirmed_short
        and direction_evidence == "SHORT"
        and momentum5 == "SHORT"
        and votes_for("SHORT") >= 2
    )

    breakout_ready = (
        breakout_ready_long or breakout_ready_short
    )

    breakout_promising = (
        (
            breakout_developing_long
            and direction_evidence == "LONG"
            and votes_for("LONG") >= 2
        )
        or
        (
            breakout_developing_short
            and direction_evidence == "SHORT"
            and votes_for("SHORT") >= 2
        )
    )

    # ========================================================
    # 6. STRUCTURE QUALIFICATION
    # ========================================================

    structure_candidate = (
        structure_developing_long
        or structure_developing_short
    )

    structure_ready_long = (
        structure_developing_long
        and direction_evidence == "LONG"
        and ema_direction == "LONG"
        and votes_for("LONG") >= 2
        and momentum15 == "LONG"
    )

    structure_ready_short = (
        structure_developing_short
        and direction_evidence == "SHORT"
        and ema_direction == "SHORT"
        and votes_for("SHORT") >= 2
        and momentum15 == "SHORT"
    )

    structure_ready = (
        structure_ready_long or structure_ready_short
    )

    structure_promising = (
        structure_candidate
        and (
            (
                structure_developing_long
                and direction_evidence == "LONG"
            )
            or
            (
                structure_developing_short
                and direction_evidence == "SHORT"
            )
        )
    )

    # ========================================================
    # 7. SCALP ELIGIBILITY
    #
    # SCALP MUST NOT OVERRIDE PROMISING TREND.
    # FINAL QUALITY AND PROFITABILITY REQUIRE
    # DOWNSTREAM CONFIRMATION.
    # ========================================================

    higher_mode_developing = (
        breakout_promising
        or structure_promising
    )

    scalp_range_pct = (
        atr14 / latest_close * 100.0
    )

    scalp_range_feasible = (
        scalp_range_pct > 0
        and math.isfinite(scalp_range_pct)
    )

    scalp_momentum_agreement = (
        direction_evidence in ("LONG", "SHORT")
        and (
            momentum5 == direction_evidence
            or momentum1 == direction_evidence
        )
    )

    scalp_ready = (
        sideways
        and not price_overextended
        and not higher_mode_developing
        and not breakout_ready
        and not structure_ready
        and scalp_range_feasible
        and scalp_momentum_agreement
    )

    # ========================================================
    # 8. PRIORITY ARBITRATION
    # ========================================================

    qualified = False
    active_mode = "NONE"
    direction = "NONE"

    candidate_mode = "NONE"
    candidate_stage = "NONE"

    qualification_reason = "NO_QUALIFIED_SIGNAL"

    if breakout_ready_long:

        qualified = True
        active_mode = "BREAKOUT"
        direction = "LONG"
        candidate_mode = "BREAKOUT"
        candidate_stage = "QUALIFIED"
        qualification_reason = "BREAKOUT_LONG_CONFIRMED"

    elif breakout_ready_short:

        qualified = True
        active_mode = "BREAKOUT"
        direction = "SHORT"
        candidate_mode = "BREAKOUT"
        candidate_stage = "QUALIFIED"
        qualification_reason = "BREAKOUT_SHORT_CONFIRMED"

    elif breakout_promising:

        candidate_mode = "BREAKOUT"
        candidate_stage = "DEVELOPING"
        qualification_reason = (
            "BREAKOUT_DEVELOPING_AWAITING_CONFIRMATION"
        )

    elif structure_ready_long:

        qualified = True
        active_mode = "STRUCTURE"
        direction = "LONG"
        candidate_mode = "STRUCTURE"
        candidate_stage = "QUALIFIED"
        qualification_reason = (
            "STRUCTURE_LONG_EARLY_QUALIFICATION"
        )

    elif structure_ready_short:

        qualified = True
        active_mode = "STRUCTURE"
        direction = "SHORT"
        candidate_mode = "STRUCTURE"
        candidate_stage = "QUALIFIED"
        qualification_reason = (
            "STRUCTURE_SHORT_EARLY_QUALIFICATION"
        )

    elif structure_promising:

        candidate_mode = "STRUCTURE"
        candidate_stage = "DEVELOPING"
        qualification_reason = (
            "STRUCTURE_DEVELOPING_AWAITING_CONFIRMATION"
        )

    elif scalp_ready:

        qualified = True
        active_mode = "SCALP"
        direction = direction_evidence
        candidate_mode = "SCALP"
        candidate_stage = "PENDING_UNIT_6"
        qualification_reason = (
            "SCALP_SIDEWAYS_PENDING_UNIT_6_SCORE"
        )

    elif breakout_candidate:

        candidate_mode = "BREAKOUT"
        candidate_stage = "REJECTED"
        qualification_reason = (
            "BREAKOUT_INSUFFICIENT_CONFIRMATION"
        )

    elif structure_candidate:

        candidate_mode = "STRUCTURE"
        candidate_stage = "REJECTED"
        qualification_reason = (
            "STRUCTURE_INSUFFICIENT_CONFIRMATION"
        )

    elif sideways and price_overextended:

        qualification_reason = (
            "SCALP_PRICE_OVEREXTENDED"
        )

    elif not sideways:

        qualification_reason = (
            "SCALP_REQUIRES_SIDEWAYS_CONTEXT"
        )

    # ========================================================
    # 9. PRESERVE ORIGINAL UNIT 6 HANDOVER
    # ========================================================

    signal_candidate = {

        "symbol": "BTCUSDT",

        "qualified": qualified,
        "active_mode": active_mode,
        "direction": direction,
        "qualification_reason": qualification_reason,

        "live_mark_price": live_mark,

        "ema19": ema19,
        "ema50": ema50,
        "ema100": ema100,
        "ema200": ema200,

        "ema19_50_separation_pct": separation_pct,

        "ema_structure": unit_4_snapshot.get(
            "ema_structure", "MIXED"
        ),

        "ema_direction": ema_direction,
        "momentum_direction": momentum1,

        "direction_agreement": (
            direction != "NONE"
            and direction == ema_direction
        ),

        "short_term_move_pct": short_move,

        "absolute_short_term_move_pct":
            abs(short_move),

        "previous_close": previous_close,
        "latest_close": latest_close,

        "price_above_ema19": live_mark > ema19,
        "price_above_ema50": live_mark > ema50,
        "price_above_ema200": live_mark > ema200,

        "latest_close_above_previous":
            latest_close > previous_close,

        "move_1m_pct": move1,
        "move_5m_pct": move5,
        "move_15m_pct": move15,
        "move_30m_pct": move30,
        "move_60m_pct": move60,
        "move_120m_pct": move120,

        "momentum_1m_direction": momentum1,
        "momentum_5m_direction": momentum5,
        "momentum_15m_direction": momentum15,
        "momentum_30m_direction": momentum30,
        "momentum_60m_direction": momentum60,
        "momentum_120m_direction": momentum120,

        "scalp_direction": (
            direction if active_mode == "SCALP"
            else "NONE"
        ),

        "scalp_move_pct": abs(move5),

        "scalp_1m_support": (
            momentum1 == direction
            and direction != "NONE"
        ),

        "structure_direction": (
            direction if active_mode == "STRUCTURE"
            else "NONE"
        ),

        "structure_move_pct": abs(move15),

        "breakout_direction": (
            direction if active_mode == "BREAKOUT"
            else "NONE"
        ),

        "breakout_move_pct": abs(move30),

        "breakout_fast_support": (
            momentum5 == direction
            and direction != "NONE"
        ),

        # NEW HYBRID CANDIDATE EVIDENCE

        "candidate_mode": candidate_mode,
        "candidate_stage": candidate_stage,

        "higher_mode_developing":
            higher_mode_developing,

        "breakout_candidate": breakout_candidate,
        "breakout_ready": breakout_ready,

        "structure_candidate": structure_candidate,
        "structure_ready": structure_ready,

        "sideways_context": sideways,

        "scalp_range_pct": scalp_range_pct,

        "scalp_range_feasible":
            scalp_range_feasible,

        "scalp_ready": scalp_ready,

        "direction_evidence": direction_evidence,

        "atr14": atr14,

        "price_overextended":
            price_overextended,

        "candle_data_fresh": True,
        "read_only": True,
        "trade_authorized": False,

        "strategy_evidence_version":
            "U5_HYBRID_V1",
    }

    # ========================================================
    # 10. FINAL RESULT
    # ========================================================

    print(
        "PASS: UNIT 5 ORIGINAL UNIT 6 HANDOVER",
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
        "UNIT 5 REASON =",
        qualification_reason,
        flush=True
    )

    print(
        "UNIT 5 HIGHER MODE DEVELOPING =",
        higher_mode_developing,
        flush=True
    )

    print(
        "UNIT 5 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "FRESH RECONSTRUCTION UNIT 5 HYBRID "
        "RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return signal_candidate


# ============================================================
# UNIT 5 EXECUTION AND UNIT 6 HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
    fresh_reconstruction_unit_5(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
    )
)


# ============================================================
# END UNIT 5 - IMPROVED HYBRID V1
# ZERO INDENTATION
# UNIT 6 CONTINUES BELOW
# ============================================================



# ============================================================
# START UNIT 6 - IMPROVED HYBRID V1
# ZERO INDENTATION
#
# ORIGINAL UNIT 7 INTERFACE PRESERVED
# HYBRID UNIT 4 AND UNIT 5 COMPATIBLE
# BREAKOUT / STRUCTURE / SCALP ADMISSION
# NO ORDER SUBMISSION
# NO EXCHANGE WRITE
# ============================================================


def fresh_reconstruction_unit_6(
    unit_2_config,
    unit_4_analysis,
    unit_5_candidate,
):

    import math
    from datetime import datetime, timezone

    print("=" * 80, flush=True)
    print(
        datetime.now(timezone.utc).isoformat(),
        "FRESH RECONSTRUCTION UNIT 6 HYBRID START",
        flush=True
    )

    # ========================================================
    # 1. VALIDATE UPSTREAM INTERFACES
    # ========================================================

    if not all(
        isinstance(item, dict)
        for item in (
            unit_2_config,
            unit_4_analysis,
            unit_5_candidate,
        )
    ):
        raise RuntimeError(
            "UNIT 6 INVALID UPSTREAM INTERFACE"
        )

    strategy = unit_2_config.get("strategy", {})
    safety = unit_2_config.get("safety", {})

    if not isinstance(strategy, dict):
        raise RuntimeError("UNIT 6 INVALID STRATEGY")

    if not isinstance(safety, dict):
        raise RuntimeError("UNIT 6 INVALID SAFETY")

    for key in (
        "one_direction_only",
        "anti_duplicate_orders",
        "exclusive_mode",
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 6 REQUIRED STRATEGY FLAG: " + key
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
                "UNIT 6 SAFETY FLAG MISMATCH: " + key
            )

    if (
        unit_4_analysis.get("read_only") is not True
        or unit_4_analysis.get("candle_data_fresh")
        is not True
        or unit_4_analysis.get("trade_authorized")
        is not False
    ):
        raise RuntimeError(
            "UNIT 6 INVALID UNIT 4 MARKET EVIDENCE"
        )

    if unit_4_analysis.get(
        "strategy_evidence_version"
    ) not in (
        "U4_HYBRID_V1",
        "U4_COORDINATED_V1",
    ):
        raise RuntimeError(
            "UNIT 6 UNKNOWN UNIT 4 INTERFACE"
        )

    if (
        unit_5_candidate.get("read_only") is not True
        or unit_5_candidate.get("trade_authorized")
        is not False
        or unit_5_candidate.get("symbol")
        != unit_4_analysis.get("symbol")
    ):
        raise RuntimeError(
            "UNIT 6 INVALID UNIT 5 HANDOVER"
        )

    # ========================================================
    # 2. NUMERIC VALIDATION
    # ========================================================

    def finite_number(value, label):

        if isinstance(value, bool):
            raise RuntimeError(
                "UNIT 6 BOOLEAN NUMERIC VALUE: " + label
            )

        try:
            result = float(value)
        except (
            TypeError,
            ValueError,
            OverflowError
        ) as exc:
            raise RuntimeError(
                "UNIT 6 INVALID VALUE: " + label
            ) from exc

        if not math.isfinite(result):
            raise RuntimeError(
                "UNIT 6 NONFINITE VALUE: " + label
            )

        return result

    candle_age = finite_number(
        unit_4_analysis.get("candle_age_seconds"),
        "CANDLE AGE"
    )

    if not 0 <= candle_age <= 180:
        raise RuntimeError(
            "UNIT 6 MARKET CANDLES TOO OLD"
        )

    atr14 = finite_number(
        unit_4_analysis.get("atr14"),
        "ATR14"
    )

    latest_close = finite_number(
        unit_4_analysis.get("latest_close"),
        "LATEST CLOSE"
    )

    if atr14 <= 0 or latest_close <= 0:
        raise RuntimeError(
            "UNIT 6 INVALID MARKET METRICS"
        )

    leverage_target = finite_number(
        strategy.get("leverage_target", 100),
        "LEVERAGE TARGET"
    )

    if leverage_target <= 0:
        raise RuntimeError(
            "UNIT 6 INVALID LEVERAGE TARGET"
        )

    # Configuration reference only.
    # The exchange controls actual leverage.

    # ========================================================
    # 3. READ UNIT 5 CANDIDATE
    # ========================================================

    qualified = (
        unit_5_candidate.get("qualified") is True
    )

    mode = unit_5_candidate.get(
        "active_mode", "NONE"
    )

    side = unit_5_candidate.get(
        "direction", "NONE"
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

    if side not in ("NONE", "LONG", "SHORT"):
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
        "NONE",
        "DEVELOPING",
        "QUALIFIED",
        "REJECTED",
        "PENDING_UNIT_6",
    ):
        raise RuntimeError(
            "UNIT 6 INVALID CANDIDATE STAGE"
        )

    if qualified:
        if (
            mode == "NONE"
            or side == "NONE"
            or candidate_mode != mode
        ):
            raise RuntimeError(
                "UNIT 6 QUALIFIED CANDIDATE INCONSISTENT"
            )
    else:
        if mode != "NONE" or side != "NONE":
            raise RuntimeError(
                "UNIT 6 UNQUALIFIED MODE LEAK"
            )

    # ========================================================
    # 4. INITIALIZE CLEAN IDLE RESULT
    # ========================================================

    execution_intent = False

    admitted_mode = "NONE"
    admitted_side = "NONE"

    admission_reason = (
        "UNIT_5_NOT_QUALIFIED:" + unit5_reason
    )

    scalp_quality_score = None
    scalp_quality_minimum = 70.0
    scalp_quality_pass = None

    scalp_quality_details = {}

    persistence_window = 3
    persistence_required = 2

    persistence_confirmations = 0
    persistence_directions = []
    persistence_pass = False

    round_trip_fee_pct = 0.16

    fee_coverage_pass = None

    # ========================================================
    # 5. STRUCTURE / BREAKOUT PRIORITY
    #
    # NO SCALP GATE APPLIED TO TREND OPPORTUNITIES.
    # ========================================================

    if qualified and mode in (
        "BREAKOUT", "STRUCTURE"
    ):

        direction_evidence = (
            unit_4_analysis.get(
                "direction_evidence", "NONE"
            )
        )

        expected_stage = "QUALIFIED"

        if candidate_stage != expected_stage:

            admission_reason = (
                "TREND_CANDIDATE_STAGE_NOT_QUALIFIED"
            )

        elif direction_evidence != side:

            admission_reason = (
                "TREND_DIRECTION_EVIDENCE_CONFLICT"
            )

        else:

            execution_intent = True

            admitted_mode = mode
            admitted_side = side

            admission_reason = (
                mode + "_PRELIMINARY_ADMISSION_PASS"
            )

    # ========================================================
    # 6. SCALP QUALIFICATION
    # ========================================================

    elif qualified and mode == "SCALP":

        if candidate_stage != "PENDING_UNIT_6":

            admission_reason = (
                "SCALP_INVALID_CANDIDATE_STAGE"
            )

        elif higher_mode_developing:

            admission_reason = (
                "SCALP_BLOCKED_BY_DEVELOPING_TREND"
            )

        elif unit_4_analysis.get(
            "sideways_candidate"
        ) is not True:

            admission_reason = (
                "SCALP_MARKET_NOT_SIDEWAYS"
            )

        elif unit_4_analysis.get(
            "price_overextended"
        ) is True:

            admission_reason = (
                "SCALP_PRICE_OVEREXTENDED"
            )

        else:

            # --------------------------------------------
            # 6A. DIRECTION CONFIRMATIONS
            # --------------------------------------------

            directions = [
                unit_5_candidate.get(
                    "momentum_1m_direction", "NONE"
                ),
                unit_5_candidate.get(
                    "momentum_5m_direction", "NONE"
                ),
                unit_5_candidate.get(
                    "momentum_15m_direction", "NONE"
                ),
            ]

            persistence_directions = directions

            persistence_confirmations = sum(
                item == side for item in directions
            )

            persistence_pass = (
                persistence_confirmations
                >= persistence_required
            )

            # --------------------------------------------
            # 6B. PRICE QUALITY
            # --------------------------------------------

            direction_votes = int(
                unit_4_analysis.get(
                    "direction_long_votes"
                    if side == "LONG"
                    else "direction_short_votes",
                    0
                )
            )

            price_extension = finite_number(
                unit_4_analysis.get(
                    "price_extension_cluster", 0
                ),
                "PRICE EXTENSION"
            )

            move1 = abs(finite_number(
                unit_5_candidate.get(
                    "move_1m_pct", 0
                ),
                "ONE MINUTE MOVE"
            ))

            move5 = abs(finite_number(
                unit_5_candidate.get(
                    "move_5m_pct", 0
                ),
                "FIVE MINUTE MOVE"
            ))

            atr_pct = (
                atr14 / latest_close * 100.0
            )

            # Volatility proxy, not an actual
            # executable take-profit forecast.

            projected_range_pct = max(
                atr_pct,
                move5
            )

            # Require estimated range to exceed
            # twice the baseline round-trip fees.

            fee_coverage_pass = (
                projected_range_pct
                >= 2.0 * round_trip_fee_pct
            )

            # Price evidence carries 50 points.
            # Remaining evidence carries 50 points.

            price_score = 0.0

            if price_extension <= 1.5:
                price_score += 20.0

            if move1 > 0:
                price_score += 15.0

            if projected_range_pct >= (
                2.0 * round_trip_fee_pct
            ):
                price_score += 15.0

            direction_score = (
                20.0
                if direction_votes >= 2
                else 0.0
            )

            persistence_score = (
                20.0
                if persistence_pass
                else 0.0
            )

            sideways_score = 10.0

            scalp_quality_score = (
                price_score
                + direction_score
                + persistence_score
                + sideways_score
            )

            scalp_quality_pass = (
                scalp_quality_score
                >= scalp_quality_minimum
            )

            scalp_quality_details = {
                "price_score": price_score,
                "direction_score": direction_score,
                "persistence_score":
                    persistence_score,
                "sideways_score": sideways_score,
                "projected_range_pct":
                    projected_range_pct,
                "round_trip_fee_pct":
                    round_trip_fee_pct,
                "fee_coverage_pass":
                    fee_coverage_pass,
            }

            # --------------------------------------------
            # 6C. FINAL SCALP ADMISSION
            # --------------------------------------------

            if not persistence_pass:

                admission_reason = (
                    "SCALP_DIRECTION_CONFIRMATION_FAILED"
                )

            elif not fee_coverage_pass:

                admission_reason = (
                    "SCALP_ESTIMATED_RANGE_BELOW_FEE_BUFFER"
                )

            elif not scalp_quality_pass:

                admission_reason = (
                    "SCALP_QUALITY_BELOW_70"
                )

            else:

                execution_intent = True

                admitted_mode = "SCALP"
                admitted_side = side

                admission_reason = (
                    "SCALP_PRELIMINARY_ADMISSION_PASS"
                )

    # ========================================================
    # 7. PRESERVE ORIGINAL UNIT 7 CONTRACT
    #
    # REJECTED SIGNALS ARE NORMALIZED TO IDLE.
    # ========================================================

    normalized_qualified = execution_intent

    if not execution_intent:
        admitted_mode = "NONE"
        admitted_side = "NONE"

    if execution_intent and (
        admitted_mode == "NONE"
        or admitted_side == "NONE"
    ):
        raise RuntimeError(
            "UNIT 6 INVALID ADMISSION STATE"
        )

    execution_candidate = {

        # ORIGINAL UNIT 7 REQUIRED FIELDS

        "execution_intent":
            execution_intent,

        "active_mode":
            admitted_mode,

        "direction":
            admitted_side,

        "signal_qualified":
            normalized_qualified,

        "unit_5_reason":
            unit5_reason,

        "admission_reason":
            admission_reason,

        # PRESERVED DIAGNOSTICS

        "leverage_target":
            leverage_target,

        "leverage_regime":
            "EXCHANGE_CONTROLLED",

        "sideways_regime":
            unit_4_analysis.get(
                "sideways_candidate", False
            ),

        "ema_compressed":
            False,

        "compression_threshold_pct":
            None,

        "momentum_conflict":
            False,

        "persistence_window":
            persistence_window,

        "persistence_required":
            persistence_required,

        "persistence_confirmations":
            persistence_confirmations,

        "persistence_directions":
            persistence_directions,

        "persistence_pass":
            persistence_pass,

        "fifteen_minute_support_pass":
            (
                unit_5_candidate.get(
                    "momentum_15m_direction"
                ) == admitted_side
                if execution_intent
                else False
            ),

        "scalp_quality_score":
            scalp_quality_score,

        "scalp_quality_minimum":
            scalp_quality_minimum,

        "scalp_quality_pass":
            scalp_quality_pass,

        "scalp_quality_details":
            scalp_quality_details,

        # NEW HYBRID DIAGNOSTICS

        "candidate_mode":
            candidate_mode,

        "candidate_stage":
            candidate_stage,

        "higher_mode_developing":
            higher_mode_developing,

        "fee_coverage_pass":
            fee_coverage_pass,

        "round_trip_fee_estimate_pct":
            round_trip_fee_pct,

        "candle_age_seconds":
            candle_age,

        "read_only":
            True,

        "order_payload_created":
            False,

        "strategy_evidence_version":
            "U6_HYBRID_V1",
    }

    # ========================================================
    # 8. FINAL OUTPUT
    # ========================================================

    print(
        "PASS: UNIT 6 RECEIVED HYBRID UNITS 2, 4, 5",
        flush=True
    )

    print(
        "PASS: UNIT 6 ORIGINAL UNIT 7 CONTRACT",
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
        "UNIT 6 ACTIVE MODE =",
        admitted_mode,
        flush=True
    )

    print(
        "UNIT 6 DIRECTION =",
        admitted_side,
        flush=True
    )

    print(
        "UNIT 6 SIGNAL QUALIFIED =",
        normalized_qualified,
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
        "UNIT 6 SCALP SCORE =",
        scalp_quality_score,
        flush=True
    )

    print(
        "UNIT 6 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        datetime.now(timezone.utc).isoformat(),
        "FRESH RECONSTRUCTION UNIT 6 HYBRID "
        "RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return execution_candidate


# ============================================================
# UNIT 6 EXECUTION AND UNIT 7 HANDOVER
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
# END UNIT 6 - IMPROVED HYBRID V1
# ZERO INDENTATION
# UNIT 7 CONTINUES BELOW
# ============================================================
