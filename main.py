# ============================================================
# START COMPLETE UNIT 1 REPLACEMENT
# ZERO INDENTATION
# WEEX 15-UNIT DEMO BOT
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
# UNIT 1
# RUNTIME FOUNDATION
# ============================================================

def fresh_reconstruction_unit_1():

    print("=" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 1 START"
    )

    print("-" * 80, flush=True)

    # ========================================================
    # 1. PYTHON RUNTIME TEST
    # ========================================================

    print(
        "PASS: MAIN.PY STARTED SUCCESSFULLY",
        flush=True,
    )

    # ========================================================
    # 2. STANDARD LIBRARY TEST
    # ========================================================

    required_modules = {
        "json": json,
        "urllib.error": urllib.error,
        "urllib.parse": urllib.parse,
        "urllib.request": urllib.request,
    }

    for name, module in required_modules.items():

        if module is None:

            raise RuntimeError(
                "UNIT 1 MODULE MISSING: " + name
            )

        print(
            "PASS: MODULE AVAILABLE =",
            name,
            flush=True,
        )

    # ========================================================
    # 3. JSON FUNCTION TEST
    # ========================================================

    test_object = {
        "unit": 1,
        "status": "PASS",
    }

    encoded = json.dumps(test_object)
    decoded = json.loads(encoded)

    if decoded != test_object:

        raise RuntimeError(
            "UNIT 1 JSON TEST FAILED"
        )

    print(
        "PASS: JSON ENCODE / DECODE",
        flush=True,
    )

    # ========================================================
    # 4. URL ENCODING TEST
    # ========================================================

    test_query = urllib.parse.urlencode(
        {
            "symbol": "BTCUSDT",
        }
    )

    if test_query != "symbol=BTCUSDT":

        raise RuntimeError(
            "UNIT 1 URL ENCODING FAILED"
        )

    print(
        "PASS: URL ENCODING",
        flush=True,
    )

    # ========================================================
    # 5. UTC TIMESTAMP TEST
    # ========================================================

    now = datetime.now(timezone.utc)

    if now.tzinfo is None:

        raise RuntimeError(
            "UNIT 1 UTC TIMEZONE FAILED"
        )

    print(
        "PASS: UTC TIMESTAMP AVAILABLE",
        flush=True,
    )

    # ========================================================
    # 6. SHARED LOGGER TEST
    # ========================================================

    log(
        "PASS: SHARED LOGGER OPERATIONAL"
    )

    # ========================================================
    # 7. UNIT-LOCAL SAFETY REPORT
    # ========================================================

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

    # ========================================================
    # 8. UNIT 1 FINAL VERDICT
    # ========================================================

    print("-" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 1 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return True


# ============================================================
# RUN UNIT 1
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_1_READY = (
    fresh_reconstruction_unit_1()
)


# ============================================================
# UNIT 1 ISOLATED TEST CONTROL
# ============================================================

UNIT_1_ISOLATED_TEST = False

if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:

    raise RuntimeError(
        "UNIT 1 FINAL VERIFICATION FAILED"
    )

print("=" * 80, flush=True)
print("UNIT 1 ISOLATED TEST = PASS", flush=True)
print("UNIT 1 VERIFIED = TRUE", flush=True)
print("UNITS 2-15 = PRESERVED", flush=True)
print("DEMO EXECUTION = NOT STARTED", flush=True)
print("=" * 80, flush=True)

UNIT__1_ISOLATED_TEST = False
if UNIT_1_ISOLATED_TEST:

    print(
        "UNIT 1 TEST COMPLETE - STOPPING BEFORE UNIT 2",
        flush=True,
    )

    raise SystemExit(0)


# ============================================================
# END COMPLETE UNIT 1 REPLACEMENT
# ZERO INDENTATION
#
# UNIT 1 FUNCTION CLOSED
# UNIT 1 CALLED
# TEST CONTROL INCLUDED
#
# EXISTING UNIT 2 CONTINUES BELOW
# ============================================================



# ============================================================
# START COMPLETE UNIT 2 REPLACEMENT
# ZERO INDENTATION
# WEEX 15-UNIT DEMO BOT
# VERSION: UNIT2-COMPAT-20261021
# ============================================================

def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 2 START")
    print("-" * 80, flush=True)

    # ========================================================
    # 1. REQUIRE VERIFIED UNIT 1
    # ========================================================

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
        raise RuntimeError(
            "UNIT 2 BLOCKED: UNIT 1 NOT VERIFIED"
        )

    print(
        "PASS: UNIT 2 RECEIVED UNIT 1",
        flush=True,
    )

    # ========================================================
    # 2. EXCHANGE CONFIGURATION
    # ========================================================

    exchange = {
        "name": "WEEX",
        "api_version": "V3",
        "contract_base_url": (
            "https://api-contract.weex.com"
        ),
        "market_symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",
    }

    execution_environment = "DEMO"

    # ========================================================
    # 3. SAFETY CONTRACT
    #
    # Unit 2 itself performs no exchange operations.
    #
    # The existing authenticated demo execution engine
    # remains under later-unit authorization.
    #
    # These initial flags must retain their existing
    # interface for compatibility with Units 3-15.
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
    # 4. STRATEGY CONFIGURATION
    # ========================================================

    strategy = {

        # ----------------------------------------------------
        # EXCHANGE LEVERAGE REFERENCE
        # ----------------------------------------------------

        "leverage_target": 100,

        # ----------------------------------------------------
        # INITIAL ENTRY
        # ----------------------------------------------------

        "initial_margin_percent": 5.0,
        "initial_fixed_usdt": 0.50,

        # ----------------------------------------------------
        # FIVE PROGRESSIVE BACKUPS
        # ----------------------------------------------------

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

        "exposure_cap_percent": 35.0,

        "progressive_backup_funding": True,

        "full_ladder_reservation_required": False,

        # ----------------------------------------------------
        # TAKE PROFIT
        # ----------------------------------------------------

        "tp1_allocation_percent": 10.0,
        "tp2_allocation_percent": 20.0,
        "tp3_allocation_percent": 70.0,

        "tp1_net_roi_floor_percent": 5.0,
        "tp2_net_roi_floor_percent": 10.0,

        "tp1_tp2_min_roi_separation_percent": 5.0,

        # ----------------------------------------------------
        # TP3 DYNAMIC TRAILING
        # ----------------------------------------------------

        "tp3_trailing_reference_percent": 0.20,
        "tp3_trailing_min_percent": 0.10,
        "tp3_trailing_max_percent": 0.40,

        # ----------------------------------------------------
        # SIGNAL CONTROL
        # ----------------------------------------------------

        "signal_expiry_seconds": 120,
        "loss_cooldown_seconds": 300,

        "one_direction_only": True,
        "anti_duplicate_orders": True,
        "active_trade_mode_lock": True,
        "exclusive_mode": True,

        # Preserve working Unit 2 contract.
        "mode_confirmations_required": 3,

        # ----------------------------------------------------
        # NEWER RECONSTRUCTION POLICY REFERENCES
        #
        # These additional settings record our intended
        # policy. Downstream units must separately
        # implement and validate their enforcement.
        # ----------------------------------------------------

        "mode_priority": (
            "BREAKOUT",
            "STRUCTURE",
            "SCALP",
        ),

        "direction_confirmation_required": 2,
        "direction_confirmation_total": 3,

        "scalp_quality_threshold": 70.0,
        "scalp_price_weight_percent": 50.0,

        "continuous_entry_scan_enabled": True,
        "flat_position_reentry_enabled": True,

        "fee_aware_scalping_enabled": True,
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
    # 6. PRESERVE ORIGINAL CONFIGURATION INTERFACE
    # ========================================================

    config = {
        "exchange": exchange,
        "execution_environment": execution_environment,
        "safety": safety,
        "strategy": strategy,
        "market_precision": market_precision,
    }

    # ========================================================
    # 7. STRICT CONFIGURATION VALIDATION
    # ========================================================

    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    require(
        exchange["name"] == "WEEX",
        "INVALID EXCHANGE",
    )

    require(
        exchange["api_version"] == "V3",
        "INVALID API VERSION",
    )

    require(
        exchange["contract_base_url"] ==
        "https://api-contract.weex.com",
        "INVALID CONTRACT BASE URL",
    )

    require(
        exchange["market_symbol"] == "BTCUSDT",
        "INVALID PUBLIC MARKET SYMBOL",
    )

    require(
        exchange["demo_order_symbol"] == "BTCSUSDT",
        "INVALID DEMO SYMBOL",
    )

    require(
        execution_environment == "DEMO",
        "REAL-CASH EXECUTION ENVIRONMENT FORBIDDEN",
    )

    # ========================================================
    # 8. ENTRY / LEVERAGE VALIDATION
    # ========================================================

    require(
        strategy["leverage_target"] == 100,
        "INVALID LEVERAGE REFERENCE",
    )

    require(
        0 < strategy["initial_margin_percent"] <= 5.0,
        "INVALID INITIAL MARGIN PERCENT",
    )

    require(
        strategy["initial_fixed_usdt"] > 0,
        "INVALID INITIAL FIXED MARGIN",
    )

    # ========================================================
    # 9. BACKUP VALIDATION
    # ========================================================

    expected_multipliers = (
        1.0,
        1.5,
        2.0,
        2.5,
        3.0,
    )

    require(
        strategy["max_backups"] == 5,
        "INVALID NUMBER OF BACKUPS",
    )

    require(
        strategy["backup_multipliers"] ==
        expected_multipliers,
        "INVALID BACKUP MULTIPLIERS",
    )

    require(
        0 < strategy["backup_margin_percent"] <= 5.0,
        "INVALID BACKUP MARGIN PERCENT",
    )

    require(
        strategy["backup_buffer_percent"] > 0,
        "INVALID BACKUP BUFFER",
    )

    require(
        strategy["progressive_backup_funding"] is True,
        "PROGRESSIVE BACKUP FUNDING DISABLED",
    )

    require(
        strategy["full_ladder_reservation_required"] is False,
        "FULL LADDER RESERVATION MUST BE DISABLED",
    )

    require(
        0 < strategy["exposure_cap_percent"] <= 35.0,
        "EXPOSURE CAP EXCEEDS LIMIT",
    )

    backup_multiplier_total = sum(
        strategy["backup_multipliers"]
    )

    full_ladder_multiplier = (
        1.0 + backup_multiplier_total
    )

    full_ladder_margin = (
        strategy["initial_fixed_usdt"]
        * full_ladder_multiplier
    )

    # This calculation is informational only.
    # Later execution units must enforce actual
    # available margin, step size and exposure.

    # ========================================================
    # 10. TAKE-PROFIT VALIDATION
    # ========================================================

    tp_total = sum((
        strategy["tp1_allocation_percent"],
        strategy["tp2_allocation_percent"],
        strategy["tp3_allocation_percent"],
    ))

    require(
        abs(tp_total - 100.0) < 0.000001,
        "TP ALLOCATION MUST TOTAL 100%",
    )

    require(
        strategy["tp1_net_roi_floor_percent"] >= 5.0,
        "TP1 NET ROI FLOOR TOO LOW",
    )

    require(
        strategy["tp2_net_roi_floor_percent"] >= 10.0,
        "TP2 NET ROI FLOOR TOO LOW",
    )

    roi_separation = (
        strategy["tp2_net_roi_floor_percent"]
        - strategy["tp1_net_roi_floor_percent"]
    )

    require(
        roi_separation >=
        strategy[
            "tp1_tp2_min_roi_separation_percent"
        ],
        "INVALID TP1/TP2 ROI SEPARATION",
    )

    trailing_min = strategy[
        "tp3_trailing_min_percent"
    ]

    trailing_ref = strategy[
        "tp3_trailing_reference_percent"
    ]

    trailing_max = strategy[
        "tp3_trailing_max_percent"
    ]

    require(
        0 < trailing_min <= trailing_ref <= trailing_max,
        "INVALID TP3 TRAILING RANGE",
    )

    # ========================================================
    # 11. SIGNAL VALIDATION
    # ========================================================

    for key in (
        "signal_expiry_seconds",
        "loss_cooldown_seconds",
        "mode_confirmations_required",
    ):
        require(
            strategy[key] > 0,
            "INVALID SIGNAL CONTROL: " + key,
        )

    for key in (
        "one_direction_only",
        "anti_duplicate_orders",
        "active_trade_mode_lock",
        "exclusive_mode",
    ):
        require(
            strategy[key] is True,
            "REQUIRED PROTECTION DISABLED: " + key,
        )

    require(
        strategy["mode_priority"] ==
        ("BREAKOUT", "STRUCTURE", "SCALP"),
        "INVALID STRATEGY PRIORITY",
    )

    require(
        1 <= strategy["direction_confirmation_required"]
        <= strategy["direction_confirmation_total"],
        "INVALID DIRECTION CONFIRMATION",
    )

    require(
        0 <= strategy["scalp_quality_threshold"] <= 100,
        "INVALID SCALP QUALITY THRESHOLD",
    )

    require(
        strategy["scalp_price_weight_percent"] == 50.0,
        "INVALID SCALP PRICE WEIGHT",
    )

    for key in (
        "continuous_entry_scan_enabled",
        "flat_position_reentry_enabled",
        "fee_aware_scalping_enabled",
    ):
        require(
            strategy[key] is True,
            "REQUIRED POLICY DISABLED: " + key,
        )

    # ========================================================
    # 12. PRECISION VALIDATION
    # ========================================================

    for key in (
        "quantity_step",
        "minimum_quantity",
        "price_step",
    ):
        require(
            market_precision[key] > 0,
            "INVALID MARKET PRECISION: " + key,
        )

    # ========================================================
    # 13. SAFETY VALIDATION
    # ========================================================

    require(
        safety["public_market_data_read_enabled"] is True,
        "PUBLIC MARKET READ DISABLED",
    )

    require(
        safety["demo_account_balance_read_enabled"] is True,
        "DEMO BALANCE READ CONFIGURATION INVALID",
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

    for capability in forbidden:
        require(
            safety[capability] is False,
            "UNSAFE UNIT 2 CAPABILITY: " + capability,
        )

    # ========================================================
    # 14. FINAL CONFIGURATION VERDICT
    # ========================================================

    if errors:
        for error in errors:
            print(
                "UNIT 2 FAIL:",
                error,
                flush=True,
            )

        raise RuntimeError(
            "UNIT 2 CONFIGURATION VALIDATION FAILED"
        )

    # ========================================================
    # 15. RENDER DIAGNOSTICS
    # ========================================================

    print("PASS: UNIT 2 CONFIGURATION CREATED", flush=True)
    print("PASS: EXCHANGE = WEEX V3", flush=True)
    print("PASS: ENVIRONMENT = DEMO", flush=True)

    print(
        "PASS: PUBLIC SYMBOL =",
        exchange["market_symbol"],
        flush=True,
    )

    print(
        "PASS: DEMO SYMBOL =",
        exchange["demo_order_symbol"],
        flush=True,
    )

    print(
        "PASS: LEVERAGE REFERENCE =",
        strategy["leverage_target"],
        flush=True,
    )

    print(
        "PASS: DEFAULT INITIAL MARGIN =",
        strategy["initial_fixed_usdt"],
        flush=True,
    )

    print(
        "PASS: INITIAL MARGIN PERCENT =",
        strategy["initial_margin_percent"],
        flush=True,
    )

    print(
        "PASS: MAX BACKUPS =",
        strategy["max_backups"],
        flush=True,
    )

    print(
        "PASS: BACKUP MULTIPLIERS =",
        strategy["backup_multipliers"],
        flush=True,
    )

    print(
        "PASS: FULL LADDER MULTIPLIER =",
        full_ladder_multiplier,
        flush=True,
    )

    print(
        "PASS: FULL LADDER MARGIN USDT =",
        full_ladder_margin,
        flush=True,
    )

    print(
        "PASS: EXPOSURE CAP % =",
        strategy["exposure_cap_percent"],
        flush=True,
    )

    print(
        "PASS: TP ALLOCATION = 10 / 20 / 70",
        flush=True,
    )

    print(
        "PASS: TP1/TP2 NET ROI FLOORS = 5 / 10",
        flush=True,
    )

    print(
        "PASS: TP3 DYNAMIC TRAILING RANGE =",
        trailing_min,
        "TO",
        trailing_max,
        flush=True,
    )

    print(
        "PASS: MODE PRIORITY = BREAKOUT / STRUCTURE / SCALP",
        flush=True,
    )

    print(
        "PASS: DIRECTION POLICY = 2 OF 3",
        flush=True,
    )

    print(
        "PASS: SCALP QUALITY POLICY =",
        strategy["scalp_quality_threshold"],
        flush=True,
    )

    print(
        "PASS: SCALP PRICE WEIGHT POLICY = 50%",
        flush=True,
    )

    print(
        "PASS: CONTINUOUS SCAN POLICY = TRUE",
        flush=True,
    )

    print(
        "PASS: FLAT POSITION REENTRY POLICY = TRUE",
        flush=True,
    )

    print(
        "PASS: FEE AWARE SCALP POLICY = TRUE",
        flush=True,
    )

    print(
        "PASS: UNIT 2 ORIGINAL CONFIG INTERFACE PRESERVED",
        flush=True,
    )

    print(
        "PASS: UNIT 2 REAL CASH SUBMISSION DISABLED",
        flush=True,
    )

    print(
        "UNIT 2 EXCHANGE HTTP REQUEST = NONE",
        flush=True,
    )

    print(
        "UNIT 2 EXCHANGE WRITE = NONE",
        flush=True,
    )

    print(
        "UNIT 2 DEMO ORDER SUBMISSION = NONE",
        flush=True,
    )

    print(
        "UNIT 2 FUTURE DEMO EXECUTION ENGINE = PRESERVED",
        flush=True,
    )

    print("-" * 80, flush=True)

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
# UNIT 2 ISOLATED TEST
#
# TRUE = STOP BEFORE UNIT 3
# FALSE = CONTINUE TO UNIT 3
# ============================================================

UNIT_2_ISOLATED_TEST = True

if not isinstance(
    FRESH_RECONSTRUCTION_CONFIG,
    dict,
):
    raise RuntimeError(
        "UNIT 2 ISOLATED TEST FAILED"
    )

if FRESH_RECONSTRUCTION_CONFIG.get(
    "execution_environment"
) != "DEMO":
    raise RuntimeError(
        "UNIT 2 INVALID EXECUTION ENVIRONMENT"
    )

if FRESH_RECONSTRUCTION_CONFIG.get(
    "strategy", {}
).get("max_backups") != 5:
    raise RuntimeError(
        "UNIT 2 BACKUP CONFIGURATION FAILED"
    )

print("=" * 80, flush=True)
print("UNIT 2 ISOLATED TEST = PASS", flush=True)
print("UNIT 2 VERIFIED = TRUE", flush=True)
print("UNITS 3-15 = PRESERVED", flush=True)
print("DEMO ORDER EXECUTION = NOT STARTED", flush=True)
print("=" * 80, flush=True)

UNIT_2_ISOLATED_TEST = False
if UNIT_2_ISOLATED_TEST:
    print(
        "UNIT 2 TEST COMPLETE - STOPPING BEFORE UNIT 3",
        flush=True,
    )
    raise SystemExit(0)


# ============================================================
# END COMPLETE UNIT 2 REPLACEMENT
# ZERO INDENTATION
#
# UNIT 2 FUNCTION CLOSED
# UNIT 2 CALLED
# UNIT 2 ISOLATED TEST INCLUDED
#
# EXISTING UNIT 3 CONTINUES BELOW
# ============================================================


# ============================================================
# START COMPLETE UNIT 3 REPLACEMENT
# ZERO INDENTATION - WEEX V3 PUBLIC MARK PRICE
# ============================================================

def fresh_reconstruction_unit_3():
    import math
    import time

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 3 START")

    # 1. Receive validated Unit 2 configuration.

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 BLOCKED: UNIT 2 CONFIG MISSING"
        )

    exchange = config.get("exchange")
    safety = config.get("safety")

    if (
        not isinstance(exchange, dict)
        or not isinstance(safety, dict)
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID CONFIG STRUCTURE"
        )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 3 BLOCKED: NON-DEMO ENVIRONMENT"
        )

    if (
        exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID EXCHANGE/API VERSION"
        )

    if exchange.get("contract_base_url") != (
        "https://api-contract.weex.com"
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID BASE URL"
        )

    if exchange.get("market_symbol") != "BTCUSDT":
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID MARKET SYMBOL"
        )

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID DEMO SYMBOL"
        )

    # 2. Read-only configuration safeguard.

    if safety.get(
        "public_market_data_read_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: MARKET READ DISABLED"
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

    for name in forbidden:
        if safety.get(name) is not False:
            raise RuntimeError(
                "UNIT 3 BLOCKED: UNSAFE FLAG " + name
            )

    print(
        "PASS: UNIT 3 RECEIVED UNIT 2 CONFIGURATION",
        flush=True,
    )

    print(
        "PASS: UNIT 3 READ-ONLY SAFETY GATE",
        flush=True,
    )

    # 3. Established WEEX V3 endpoint.

    params = urllib.parse.urlencode({
        "symbol": exchange["market_symbol"],
        "priceType": "MARK",
    })

    endpoint = "/capi/v3/market/symbolPrice"

    url = (
        exchange["contract_base_url"]
        + endpoint
        + "?"
        + params
    )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-15-Unit-Demo-Unit3/1.0",
        },
    )

    if (
        request.get_method() != "GET"
        or request.data is not None
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: HTTP REQUEST NOT READ ONLY"
        )

    if (
        request.has_header("Authorization")
        or request.has_header("ACCESS-KEY")
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: AUTH HEADER PRESENT"
        )

    print(
        "PASS: UNIT 3 ENDPOINT = WEEX V3 SYMBOL PRICE",
        flush=True,
    )

    print(
        "PASS: UNIT 3 PRICE TYPE = MARK",
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

    # 4. Public GET only.

    local_before_ms = int(time.time() * 1000)

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            http_status = response.getcode()
            response_url = response.geturl()
            raw_body = response.read(1024 * 1024 + 1)

    except urllib.error.HTTPError as exc:
        print(
            "UNIT 3 HTTP ERROR =",
            exc.code,
            flush=True,
        )
        raise RuntimeError(
            "UNIT 3 WEEX PUBLIC HTTP FAILURE"
        ) from exc

    except urllib.error.URLError as exc:
        print(
            "UNIT 3 CONNECTION ERROR =",
            repr(exc.reason),
            flush=True,
        )
        raise RuntimeError(
            "UNIT 3 WEEX PUBLIC CONNECTION FAILURE"
        ) from exc

    except TimeoutError as exc:
        raise RuntimeError(
            "UNIT 3 WEEX PUBLIC REQUEST TIMEOUT"
        ) from exc

    local_after_ms = int(time.time() * 1000)

    if http_status != 200:
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID HTTP STATUS"
        )

    if (
        len(raw_body) == 0
        or len(raw_body) > 1024 * 1024
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: EMPTY/OVERSIZE RESPONSE"
        )

    parsed_url = urllib.parse.urlparse(response_url)

    if (
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
    ) != (
        "https",
        "api-contract.weex.com",
        endpoint,
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: UNEXPECTED RESPONSE URL"
        )

    # 5. Validate the original WEEX response contract.

    try:
        payload = json.loads(
            raw_body.decode("utf-8")
        )

    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID JSON RESPONSE"
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError(
            "UNIT 3 BLOCKED: RESPONSE IS NOT AN OBJECT"
        )

    if payload.get("symbol") != exchange["market_symbol"]:
        raise RuntimeError(
            "UNIT 3 BLOCKED: RESPONSE SYMBOL MISMATCH"
        )

    try:
        price = float(payload["price"])
        exchange_time_ms = int(payload["time"])

    except (
        KeyError,
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID PRICE/TIME FIELD"
        ) from exc

    if not math.isfinite(price) or price <= 0:
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID MARK PRICE"
        )

    if exchange_time_ms <= 0:
        raise RuntimeError(
            "UNIT 3 BLOCKED: INVALID EXCHANGE TIMESTAMP"
        )

    if not (
        local_before_ms - 120000
        <= exchange_time_ms
        <= local_after_ms + 120000
    ):
        raise RuntimeError(
            "UNIT 3 BLOCKED: STALE/FUTURE EXCHANGE TIMESTAMP"
        )

    # 6. Preserve the exact Unit 4 input interface.

    market_snapshot = {
        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": "BTCUSDT",
        "price": price,
        "price_type": "MARK",
        "exchange_time_ms": exchange_time_ms,
        "source": "WEEX_V3_PUBLIC_MARK_PRICE",
        "read_only": True,
    }

    print(
        "PASS: UNIT 3 HTTP STATUS = 200",
        flush=True,
    )

    print(
        "PASS: UNIT 3 RESPONSE SYMBOL =",
        market_snapshot["symbol"],
        flush=True,
    )

    print(
        "PASS: UNIT 3 LIVE BTC MARK PRICE =",
        price,
        flush=True,
    )

    print(
        "PASS: UNIT 3 MARKET TIMESTAMP =",
        exchange_time_ms,
        flush=True,
    )

    print(
        "PASS: UNIT 3 NORMALIZED MARKET SNAPSHOT",
        flush=True,
    )

    print(
        "UNIT 3 ACCOUNT ACCESS = NONE",
        flush=True,
    )

    print(
        "UNIT 3 DEMO ORDER = NONE",
        flush=True,
    )

    print(
        "UNIT 3 REAL ORDER = NONE",
        flush=True,
    )

    print(
        "UNIT 3 EXCHANGE WRITE = NONE",
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 3 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return market_snapshot


# ============================================================
# RUN UNIT 3 - ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# UNIT 3 ISOLATED TEST
# TRUE = STOP BEFORE UNIT 4
# ============================================================

UNIT_3_ISOLATED_TEST = True

_required_unit_3_keys = (
    "exchange",
    "api_version",
    "symbol",
    "price",
    "price_type",
    "exchange_time_ms",
    "source",
    "read_only",
)

if not isinstance(
    FRESH_RECONSTRUCTION_MARKET_SNAPSHOT,
    dict,
):
    raise RuntimeError(
        "UNIT 3 ISOLATED TEST FAILED: SNAPSHOT TYPE"
    )

if any(
    key not in FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    for key in _required_unit_3_keys
):
    raise RuntimeError(
        "UNIT 3 ISOLATED TEST FAILED: MISSING FIELD"
    )

if FRESH_RECONSTRUCTION_MARKET_SNAPSHOT[
    "read_only"
] is not True:
    raise RuntimeError(
        "UNIT 3 ISOLATED TEST FAILED: READ-ONLY FIELD"
    )

print(
    "UNIT 3 ISOLATED TEST = PASS",
    flush=True,
)

print(
    "UNIT 3 VERIFIED = TRUE",
    flush=True,
)

print(
    "UNITS 4-15 EXECUTION = NOT STARTED",
    flush=True,
)

if UNIT_3_ISOLATED_TEST:

    print(
        "UNIT 3 TEST COMPLETE - STOPPING BEFORE UNIT 4",
        flush=True,
    )

    raise SystemExit(0)


# ============================================================
# END COMPLETE UNIT 3 REPLACEMENT
# ZERO INDENTATION
# ============================================================
