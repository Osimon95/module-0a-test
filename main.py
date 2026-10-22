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

UNIT_3_ISOLATED_TEST = False
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


# ============================================================
# START COMPLETE UNIT 4 REPLACEMENT
# ZERO INDENTATION
# WEEX OLD 15-UNIT + NEW RECONSTRUCTION
# ============================================================

def fresh_reconstruction_unit_4():

    import math

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 4 START")

    # ========================================================
    # 1. RECEIVE UNITS 2 AND 3
    # ========================================================

    config = FRESH_RECONSTRUCTION_CONFIG
    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 4 CONFIG MISSING")

    if not isinstance(market, dict):
        raise RuntimeError("UNIT 4 MARKET MISSING")

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})
    strategy = config.get("strategy", {})

    if not all(
        isinstance(x, dict)
        for x in (exchange, safety, strategy)
    ):
        raise RuntimeError("UNIT 4 INVALID CONFIG")

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError("UNIT 4 DEMO ENVIRONMENT REQUIRED")

    if (
        exchange.get("contract_base_url")
        != "https://api-contract.weex.com"
        or exchange.get("market_symbol") != "BTCUSDT"
        or market.get("exchange") != "WEEX"
        or market.get("api_version") != "V3"
        or market.get("symbol") != "BTCUSDT"
        or market.get("price_type") != "MARK"
        or market.get("read_only") is not True
    ):
        raise RuntimeError("UNIT 4 MARKET CONTRACT FAILED")

    if safety.get("public_market_data_read_enabled") is not True:
        raise RuntimeError("UNIT 4 PUBLIC READ DISABLED")

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
                "UNIT 4 UNSAFE CONFIG: " + key
            )

    def finite(value, label):
        try:
            value = float(value)
        except (ValueError, TypeError, OverflowError) as exc:
            raise RuntimeError(
                "UNIT 4 INVALID " + label
            ) from exc

        if not math.isfinite(value):
            raise RuntimeError(
                "UNIT 4 NONFINITE " + label
            )
        return value

    exchange_ms = int(market["exchange_time_ms"])
    live_mark = finite(market["price"], "MARK PRICE")

    if exchange_ms <= 0 or live_mark <= 0:
        raise RuntimeError("UNIT 4 INVALID MARKET DATA")

    print("PASS: UNIT 4 RECEIVED UNITS 2 AND 3", flush=True)
    print("PASS: UNIT 4 READ ONLY SAFETY", flush=True)

    # ========================================================
    # 2. WEEX PUBLIC MARK-PRICE CANDLES
    # ========================================================

    endpoint = "/capi/v3/market/markPriceKlines"

    query = urllib.parse.urlencode({
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 300,
    })

    url = (
        exchange["contract_base_url"]
        + endpoint
        + "?"
        + query
    )

    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Unit4-Adapter/1.0",
        },
    )

    if (
        request.get_method() != "GET"
        or request.data is not None
    ):
        raise RuntimeError("UNIT 4 NON-GET REQUEST")

    # Prevent HTTP redirects.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(
            self, req, fp, code, msg, headers, newurl
        ):
            return None

    opener = urllib.request.build_opener(NoRedirect())

    try:
        with opener.open(request, timeout=15) as response:
            status = response.getcode()
            raw = response.read(2 * 1024 * 1024 + 1)

    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            "UNIT 4 HTTP ERROR " + str(exc.code)
        ) from exc

    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(
            "UNIT 4 CONNECTION FAILED"
        ) from exc

    if (
        status != 200
        or not raw
        or len(raw) > 2 * 1024 * 1024
    ):
        raise RuntimeError("UNIT 4 HTTP RESPONSE INVALID")

    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            "UNIT 4 INVALID JSON"
        ) from exc

    if not isinstance(payload, list) or len(payload) < 200:
        raise RuntimeError("UNIT 4 INSUFFICIENT KLINES")

    print("PASS: UNIT 4 HTTP STATUS = 200", flush=True)

    # ========================================================
    # 3. NORMALIZE CANDLES
    # ========================================================

    candles = []

    for raw_candle in payload:

        if (
            not isinstance(raw_candle, (list, tuple))
            or len(raw_candle) < 7
        ):
            raise RuntimeError("UNIT 4 INVALID CANDLE SHAPE")

        try:
            c = {
                "open_time_ms": int(raw_candle[0]),
                "open": finite(raw_candle[1], "OPEN"),
                "high": finite(raw_candle[2], "HIGH"),
                "low": finite(raw_candle[3], "LOW"),
                "close": finite(raw_candle[4], "CLOSE"),
                "volume": finite(raw_candle[5], "VOLUME"),
                "close_time_ms": int(raw_candle[6]),
            }

        except (ValueError, TypeError, OverflowError) as exc:
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE TIMESTAMP"
            ) from exc

        if not (
            c["open_time_ms"] > 0
            and c["close_time_ms"] > c["open_time_ms"]
            and 0 < c["low"]
            <= min(c["open"], c["close"])
            and max(c["open"], c["close"]) <= c["high"]
            and c["volume"] >= 0
        ):
            raise RuntimeError("UNIT 4 INVALID OHLC")

        candles.append(c)

    candles.sort(key=lambda c: c["open_time_ms"])

    if any(
        candles[i]["open_time_ms"]
        <= candles[i - 1]["open_time_ms"]
        for i in range(1, len(candles))
    ):
        raise RuntimeError("UNIT 4 DUPLICATE CANDLE TIME")

    # ========================================================
    # 4. CLOSED CANDLES ONLY
    # ========================================================

    closed = [
        c for c in candles
        if c["close_time_ms"] <= exchange_ms
    ]

    if len(closed) < 201:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT CLOSED CANDLES"
        )

    latest = closed[-1]
    previous = closed[-2]

    candle_age = (
        exchange_ms - latest["close_time_ms"]
    ) / 1000.0

    if not 0 <= candle_age <= 180:
        raise RuntimeError("UNIT 4 STALE CLOSED CANDLE")

    prices = [c["close"] for c in closed]

    # ========================================================
    # 5. EMA19 / EMA50 / EMA100 / EMA200
    # ========================================================

    def ema(series, period):

        result = sum(series[:period]) / period
        alpha = 2.0 / (period + 1.0)

        for price in series[period:]:
            result += alpha * (price - result)

        return result

    e19 = ema(prices, 19)
    e50 = ema(prices, 50)
    e100 = ema(prices, 100)
    e200 = ema(prices, 200)

    if e19 > e50 > e200:
        structure = "BULLISH"
    elif e19 < e50 < e200:
        structure = "BEARISH"
    else:
        structure = "MIXED"

    # ========================================================
    # 6. MULTI-WINDOW MOMENTUM
    # ========================================================

    moves = {
        n: (
            latest["close"] / prices[-(n + 1)] - 1.0
        ) * 100.0
        for n in (1, 5, 15, 30, 60, 120)
    }

    # ========================================================
    # 7. ATR14
    # ========================================================

    true_ranges = []

    for i in range(1, len(closed)):
        current = closed[i]
        prior = closed[i - 1]

        tr = max(
            current["high"] - current["low"],
            abs(current["high"] - prior["close"]),
            abs(current["low"] - prior["close"]),
        )

        true_ranges.append(tr)

    atr14 = sum(true_ranges[-14:]) / 14.0

    if not math.isfinite(atr14) or atr14 <= 0:
        raise RuntimeError("UNIT 4 INVALID ATR14")

    atr_pct = 100.0 * atr14 / latest["close"]

    # ========================================================
    # 8. SUPPORT / RESISTANCE
    # ========================================================

    preceding20 = closed[-21:-1]

    resistance = max(
        c["high"] for c in preceding20
    )

    support = min(
        c["low"] for c in preceding20
    )

    range_ratio = (resistance - support) / atr14

    near_resistance = (
        -0.10 * atr14
        <= resistance - latest["close"]
        <= 0.50 * atr14
    )

    near_support = (
        -0.10 * atr14
        <= latest["close"] - support
        <= 0.50 * atr14
    )

    # ========================================================
    # 9. PRICE EXTENSION
    # ========================================================

    cluster_height = max(
        max(e19, e50, e200) - min(e19, e50, e200),
        0.10 * atr14,
    )

    extension = (
        abs(latest["close"] - e19)
        / cluster_height
    )

    extension_limit = finite(
        strategy.get(
            "scalp_max_ema_extension_clusters", 1.5
        ),
        "EXTENSION LIMIT",
    )

    if extension_limit <= 0:
        raise RuntimeError("UNIT 4 INVALID EXTENSION LIMIT")

    # ========================================================
    # 10. DEVELOPING / CONFIRMED BREAKOUT
    # ========================================================

    bullish = moves[5] > 0 and moves[15] > 0
    bearish = moves[5] < 0 and moves[15] < 0

    breakout_developing_long = (
        near_resistance and bullish
    )

    breakout_developing_short = (
        near_support and bearish
    )

    breakout_confirmed_long = (
        latest["close"] > resistance + 0.10 * atr14
        and bullish
    )

    breakout_confirmed_short = (
        latest["close"] < support - 0.10 * atr14
        and bearish
    )

    # ========================================================
    # 11. DEVELOPING STRUCTURE
    # ========================================================

    near_e19 = (
        abs(latest["close"] - e19) <= 0.75 * atr14
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
        structure == "BULLISH"
        and moves[15] > 0
        and (near_e19 or bullish_recovery)
    )

    structure_developing_short = (
        structure == "BEARISH"
        and moves[15] < 0
        and (near_e19 or bearish_recovery)
    )

    # ========================================================
    # 12. SIDEWAYS REGIME AND DIRECTION VOTES
    # ========================================================

    sideways = (
        abs(e19 - e50) / atr14 <= 0.70
        and range_ratio <= 8.0
        and abs(moves[15]) <= 1.5 * atr_pct
    )

    long_votes = sum((
        structure == "BULLISH",
        moves[5] > 0,
        latest["close"] > previous["close"],
    ))

    short_votes = sum((
        structure == "BEARISH",
        moves[5] < 0,
        latest["close"] < previous["close"],
    ))

    if long_votes >= 2 and long_votes > short_votes:
        direction = "LONG"
    elif short_votes >= 2 and short_votes > long_votes:
        direction = "SHORT"
    else:
        direction = "NONE"

    # ========================================================
    # 13. COMBINED OUTPUT
    # ORIGINAL 30 KEYS PRESERVED
    # NEW EVIDENCE KEYS ADDED
    # ========================================================

    result = {

        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": "BTCUSDT",
        "interval": "1m",
        "price_type": "MARK",

        "live_mark_price": live_mark,
        "previous_close": previous["close"],
        "latest_close": latest["close"],

        "latest_open_time_ms": latest["open_time_ms"],
        "latest_close_time_ms": latest["close_time_ms"],
        "exchange_time_ms": exchange_ms,

        "ema19": e19,
        "ema50": e50,
        "ema100": e100,
        "ema200": e200,

        "ema19_50_separation_pct":
            abs(e19 - e50) / e50 * 100.0,

        "short_term_move_pct": moves[1],
        "move_1m_pct": moves[1],
        "move_5m_pct": moves[5],
        "move_15m_pct": moves[15],
        "move_30m_pct": moves[30],
        "move_60m_pct": moves[60],
        "move_120m_pct": moves[120],

        "ema_structure": structure,

        "recent_closed_klines": [
            dict(c) for c in closed[-60:]
        ],

        "candle_count": len(candles),
        "closed_candle_count": len(closed),

        "newest_returned_candle_closed":
            candles[-1]["close_time_ms"] <= exchange_ms,

        "source": "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",
        "read_only": True,

        # New evidence

        "atr14": atr14,
        "atr_percent": atr_pct,

        "ema_cluster_height": cluster_height,
        "price_extension_cluster": extension,
        "price_overextended": extension > extension_limit,

        "support20": support,
        "resistance20": resistance,
        "range20_atr_ratio": range_ratio,

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

        "sideways_candidate": sideways,

        "direction_long_votes": long_votes,
        "direction_short_votes": short_votes,
        "direction_evidence": direction,

        "candle_age_seconds": candle_age,
        "candle_data_fresh": True,

        "strategy_evidence_version":
            "U4_OLD_NEW_ADAPTED_V1",

        "trade_authorized": False,
    }

    # ========================================================
    # 14. RENDER DIAGNOSTICS
    # ========================================================

    print(
        "PASS: UNIT 4 CLOSED CANDLES =",
        len(closed),
        flush=True,
    )

    print(
        "PASS: UNIT 4 EMA19/50/100/200 =",
        e19, e50, e100, e200,
        flush=True,
    )

    print(
        "PASS: UNIT 4 ATR14 =",
        atr14,
        flush=True,
    )

    print(
        "UNIT 4 EMA STRUCTURE =",
        structure,
        flush=True,
    )

    print(
        "UNIT 4 BREAKOUT DEVELOPING L/S =",
        breakout_developing_long,
        breakout_developing_short,
        flush=True,
    )

    print(
        "UNIT 4 BREAKOUT CONFIRMED L/S =",
        breakout_confirmed_long,
        breakout_confirmed_short,
        flush=True,
    )

    print(
        "UNIT 4 STRUCTURE DEVELOPING L/S =",
        structure_developing_long,
        structure_developing_short,
        flush=True,
    )

    print(
        "UNIT 4 SIDEWAYS CANDIDATE =",
        sideways,
        flush=True,
    )

    print(
        "UNIT 4 DIRECTION EVIDENCE =",
        direction,
        flush=True,
    )

    print(
        "UNIT 4 CANDLE AGE SECONDS =",
        round(candle_age, 3),
        flush=True,
    )

    print("UNIT 4 TRADE AUTHORIZED = FALSE", flush=True)
    print("UNIT 4 EXCHANGE WRITE = NONE", flush=True)

    log("FRESH RECONSTRUCTION UNIT 4 RESULT = PASS")

    return result


# ============================================================
# RUN UNIT 4
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)


# ============================================================
# UNIT 4 ISOLATED TEST
# ============================================================

UNIT_4_ISOLATED_TEST = True

original_keys = (
    "exchange", "api_version", "symbol",
    "interval", "price_type", "live_mark_price",
    "previous_close", "latest_close",
    "latest_open_time_ms", "latest_close_time_ms",
    "exchange_time_ms",
    "ema19", "ema50", "ema100", "ema200",
    "ema19_50_separation_pct",
    "short_term_move_pct",
    "move_1m_pct", "move_5m_pct",
    "move_15m_pct", "move_30m_pct",
    "move_60m_pct", "move_120m_pct",
    "ema_structure", "recent_closed_klines",
    "candle_count", "closed_candle_count",
    "newest_returned_candle_closed",
    "source", "read_only",
)

snapshot = FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT

if not isinstance(snapshot, dict):
    raise RuntimeError("UNIT 4 SNAPSHOT TYPE FAILED")

missing = [
    key for key in original_keys
    if key not in snapshot
]

if missing:
    raise RuntimeError(
        "UNIT 4 MISSING ORIGINAL KEYS: " + str(missing)
    )

if (
    snapshot["read_only"] is not True
    or snapshot["trade_authorized"] is not False
    or snapshot["candle_data_fresh"] is not True
):
    raise RuntimeError(
        "UNIT 4 SAFETY VALIDATION FAILED"
    )

print("=" * 80, flush=True)
print("UNIT 4 ISOLATED TEST = PASS", flush=True)
print("UNIT 4 VERIFIED = TRUE", flush=True)
print("UNITS 5-15 EXECUTION = NOT STARTED", flush=True)
print("=" * 80, flush=True)

UNIT_4_ISOLATED_TEST = False
if UNIT_4_ISOLATED_TEST:

    print(
        "UNIT 4 TEST COMPLETE - STOPPING BEFORE UNIT 5",
        flush=True,
    )

    raise SystemExit(0)


# ============================================================
# END COMPLETE UNIT 4 REPLACEMENT
# ZERO INDENTATION
# EXISTING UNIT 5 CONTINUES BELOW
# ============================================================


# ============================================================
# START COMPLETE UNIT 5 REPLACEMENT - ZERO INDENTATION
# OLD 15-UNIT HANDOVER + NEW COORDINATED ARBITRATION
# ============================================================

def fresh_reconstruction_unit_5(unit_2_config, unit_4_snapshot):
    import math

    print('=' * 80, flush=True)
    log('FRESH RECONSTRUCTION UNIT 5 START')

    if not isinstance(unit_2_config, dict) or not isinstance(unit_4_snapshot, dict):
        raise RuntimeError('UNIT 5 INPUT CONTRACT FAILED')

    strategy = unit_2_config.get('strategy', {})
    safety = unit_2_config.get('safety', {})
    if not isinstance(strategy, dict) or not isinstance(safety, dict):
        raise RuntimeError('UNIT 5 CONFIG CONTRACT FAILED')

    if strategy.get('mode_priority') != ('BREAKOUT', 'STRUCTURE', 'SCALP'):
        raise RuntimeError('UNIT 5 MODE PRIORITY FAILED')

    for key in ('authenticated_api_enabled', 'account_access_enabled',
                'position_access_enabled', 'order_endpoint_access_enabled',
                'demo_order_submission_enabled', 'real_order_submission_enabled',
                'exchange_mutation_enabled'):
        if safety.get(key) is not False:
            raise RuntimeError('UNIT 5 UNSAFE FLAG: ' + key)

    s = unit_4_snapshot
    if (s.get('symbol') != 'BTCUSDT' or s.get('read_only') is not True
            or s.get('trade_authorized') is not False
            or s.get('candle_data_fresh') is not True
            or s.get('strategy_evidence_version') != 'U4_OLD_NEW_ADAPTED_V1'):
        raise RuntimeError('UNIT 5 UNIT 4 HANDOVER FAILED')

    def num(key):
        value = float(s[key])
        if not math.isfinite(value):
            raise RuntimeError('UNIT 5 NONFINITE FIELD: ' + key)
        return value

    live = num('live_mark_price')
    latest = num('latest_close')
    previous = num('previous_close')
    e19, e50, e100, e200 = (num(k) for k in ('ema19', 'ema50', 'ema100', 'ema200'))
    sep = num('ema19_50_separation_pct')
    move1, move5, move15, move30 = (num(k) for k in
                                      ('move_1m_pct', 'move_5m_pct', 'move_15m_pct', 'move_30m_pct'))
    atr = num('atr14')
    age = num('candle_age_seconds')
    if min(live, latest, previous, e19, e50, e100, e200, atr) <= 0 or not 0 <= age <= 180:
        raise RuntimeError('UNIT 5 INVALID PRICE/AGE')

    direction_evidence = s.get('direction_evidence', 'NONE')
    if direction_evidence not in ('LONG', 'SHORT', 'NONE'):
        raise RuntimeError('UNIT 5 INVALID DIRECTION')

    def signed_direction(x):
        return 'LONG' if x > 0 else 'SHORT' if x < 0 else 'NONE'

    breakout_long = bool(s.get('breakout_developing_long'))
    breakout_short = bool(s.get('breakout_developing_short'))
    breakout_ready_long = bool(s.get('breakout_confirmed_long'))
    breakout_ready_short = bool(s.get('breakout_confirmed_short'))
    structure_long = bool(s.get('structure_developing_long'))
    structure_short = bool(s.get('structure_developing_short'))

    # A confirmed or developing higher-priority candidate wins
    # arbitration before any SCALP consideration.
    breakout_candidate = breakout_long or breakout_short or breakout_ready_long or breakout_ready_short
    breakout_ready = breakout_ready_long or breakout_ready_short
    structure_candidate = structure_long or structure_short
    structure_ready = (structure_candidate and
                       ((structure_long and direction_evidence == 'LONG') or
                        (structure_short and direction_evidence == 'SHORT')) and
                       signed_direction(move15) == direction_evidence)
    higher_mode_developing = breakout_candidate or structure_candidate

    sideways = s.get('sideways_candidate') is True
    recent = s.get('recent_closed_klines', [])
    if not isinstance(recent, list) or len(recent) < 20:
        raise RuntimeError('UNIT 5 CANDLE HANDOVER MISSING')
    highs = [float(c['high']) for c in recent[-20:]]
    lows = [float(c['low']) for c in recent[-20:]]
    scalp_range_pct = 100.0 * (max(highs) - min(lows)) / latest
    if not math.isfinite(scalp_range_pct) or scalp_range_pct < 0:
        raise RuntimeError('UNIT 5 INVALID SCALP RANGE')

    # Fee-aware prospective headroom: range alone is NOT a
    # profit forecast. Unit 6 must revalidate net economics.
    fee_each_pct = float(strategy.get('scalp_estimated_taker_fee_percent', 0.08))
    minimum_sustainable_range_pct = 2.0 * fee_each_pct + 0.02
    scalp_range_feasible = scalp_range_pct > minimum_sustainable_range_pct
    extension_ok = s.get('price_overextended') is False
    scalp_pending = (sideways and not higher_mode_developing
                     and scalp_range_feasible and extension_ok
                     and direction_evidence in ('LONG', 'SHORT'))

    candidate_mode = 'NONE'
    candidate_stage = 'NONE'
    active_mode = 'NONE'
    direction = 'NONE'
    qualified = False
    reason = 'NO_QUALIFIED_CANDIDATE'

    if breakout_candidate:
        candidate_mode = 'BREAKOUT'
        if breakout_ready:
            candidate_stage = 'PENDING_UNIT_6'
            active_mode = 'BREAKOUT'
            direction = 'LONG' if breakout_ready_long else 'SHORT'
            qualified = direction == direction_evidence
            reason = ('BREAKOUT_READY_FOR_UNIT6' if qualified
                      else 'BREAKOUT_DIRECTION_NOT_CONFIRMED')
        else:
            candidate_stage = 'DEVELOPING'
            direction = 'LONG' if breakout_long else 'SHORT'
            reason = 'BREAKOUT_DEVELOPING_PRIORITY'

    elif structure_candidate:
        candidate_mode = 'STRUCTURE'
        direction = 'LONG' if structure_long else 'SHORT'
        if structure_ready:
            candidate_stage = 'PENDING_UNIT_6'
            active_mode = 'STRUCTURE'
            qualified = True
            reason = 'STRUCTURE_READY_FOR_UNIT6'
        else:
            candidate_stage = 'DEVELOPING'
            reason = 'STRUCTURE_DEVELOPING_PRIORITY'

    elif scalp_pending:
        candidate_mode = 'SCALP'
        candidate_stage = 'PENDING_UNIT_6'
        active_mode = 'SCALP'
        direction = direction_evidence
        qualified = True
        reason = 'SCALP_SIDEWAYS_FEE_PRECHECK_PASS'

    elif sideways and not higher_mode_developing:
        candidate_mode = 'SCALP'
        candidate_stage = 'DEVELOPING'
        direction = direction_evidence
        reason = 'SCALP_ECONOMIC_OR_EXTENSION_BLOCK'

    # ========================================================
    # OUTPUT CONTRACT
    # ========================================================

    result = {
        'exchange': 'WEEX',
        'symbol': 'BTCUSDT',
        'market_symbol': 'BTCUSDT',
        'price_type': 'MARK',
        'interval': '1m',
        'market_price': live,
        'live_mark_price': live,
        'latest_close': latest,
        'previous_close': previous,
        'latest_close_time_ms': s['latest_close_time_ms'],
        'exchange_time_ms': s['exchange_time_ms'],
        'ema19': e19,
        'ema50': e50,
        'ema100': e100,
        'ema200': e200,
        'ema_structure': s['ema_structure'],
        'ema19_50_separation_pct': sep,
        'short_term_move_pct': move1,
        'move_1m_pct': move1,
        'move_5m_pct': move5,
        'move_15m_pct': move15,
        'move_30m_pct': move30,
        'move_60m_pct': s['move_60m_pct'],
        'move_120m_pct': s['move_120m_pct'],
        'atr14': atr,
        'atr_percent': s['atr_percent'],
        'active_mode': active_mode,
        'candidate_mode': candidate_mode,
        'candidate_stage': candidate_stage,
        'direction': direction,
        'qualified': qualified,
        'qualification_reason': reason,
        'reason': reason,
        'mode_priority': ('BREAKOUT', 'STRUCTURE', 'SCALP'),
        'higher_mode_developing': higher_mode_developing,
        'breakout_candidate': breakout_candidate,
        'breakout_ready': breakout_ready,
        'structure_candidate': structure_candidate,
        'structure_ready': structure_ready,
        'scalp_candidate': scalp_pending,
        'scalp_sideways': sideways,
        'scalp_range_pct': scalp_range_pct,
        'scalp_fee_precheck_pass': scalp_range_feasible,
        'price_overextended': not extension_ok,
        'direction_evidence': direction_evidence,
        'closed_candle_id': s['latest_open_time_ms'],
        'recent_closed_klines': recent,
        'structure_direction': 'LONG' if structure_long else 'SHORT' if structure_short else 'NONE',
        'structure_move_pct': abs(move15),
        'breakout_direction': 'LONG' if (breakout_long or breakout_ready_long) else 'SHORT' if (breakout_short or breakout_ready_short) else 'NONE',
        'breakout_move_pct': abs(move30),
        'breakout_fast_support': signed_direction(move5) == direction_evidence,
        'candle_data_fresh': True, 'read_only': True,
        'trade_authorized': False,
        'strategy_evidence_version': 'U4_OLD_NEW_ADAPTED_V1',
    }

    print('UNIT 5 BREAKOUT CANDIDATE =', breakout_candidate, flush=True)
    print('UNIT 5 STRUCTURE CANDIDATE =', structure_candidate, flush=True)
    print('UNIT 5 HIGHER MODE DEVELOPING =', higher_mode_developing, flush=True)
    print('UNIT 5 SIDEWAYS =', sideways, flush=True)
    print('UNIT 5 SCALP RANGE % =', round(scalp_range_pct, 5), flush=True)
    print('UNIT 5 CANDIDATE MODE =', candidate_mode, flush=True)
    print('UNIT 5 CANDIDATE STAGE =', candidate_stage, flush=True)
    print('UNIT 5 ACTIVE MODE =', active_mode, flush=True)
    print('UNIT 5 DIRECTION =', direction, flush=True)
    print('UNIT 5 QUALIFIED =', qualified, flush=True)
    print('UNIT 5 REASON =', reason, flush=True)
    print('UNIT 5 TRADE AUTHORIZED = FALSE', flush=True)
    print('UNIT 5 EXCHANGE WRITE = NONE', flush=True)
    log('FRESH RECONSTRUCTION UNIT 5 RESULT = PASS')
    print('=' * 80, flush=True)
    return result


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
# UNIT 5 ISOLATED TEST - STOP BEFORE UNIT 6
# ============================================================

UNIT_5_ISOLATED_TEST = False
UNIT_5_ISOLATED_TEST = False

_u5 = FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
assert isinstance(_u5, dict)
assert _u5['symbol'] == 'BTCUSDT'
assert _u5['read_only'] is True
assert _u5['trade_authorized'] is False
assert _u5['active_mode'] in ('NONE', 'BREAKOUT', 'STRUCTURE', 'SCALP')
assert not (_u5['active_mode'] == 'SCALP' and _u5['higher_mode_developing'])
assert not (_u5['qualified'] and _u5['candidate_stage'] == 'DEVELOPING')
print('UNIT 5 ISOLATED TEST = PASS', flush=True)
print('UNIT 5 VERIFIED = TRUE', flush=True)
print('UNITS 6-15 EXECUTION = NOT STARTED', flush=True)
if UNIT_5_ISOLATED_TEST:
    print('UNIT 5 TEST COMPLETE - STOPPING BEFORE UNIT 6', flush=True)
    raise SystemExit(0)

# ============================================================
# END COMPLETE UNIT 5 REPLACEMENT - ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE UNIT 6 REPLACEMENT
# ZERO INDENTATION
# OLD 15-UNIT + NEW RECONSTRUCTION
# SIGNAL ADMISSION / QUALITY / UNIT 7 HANDOVER
# ============================================================

def fresh_reconstruction_unit_6(
    unit_2_config,
    unit_4_analysis,
    unit_5_candidate,
):

    import math

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 6 START")

    # ========================================================
    # 1. INPUT AND SAFETY CONTRACT
    # ========================================================

    if not all(
        isinstance(x, dict)
        for x in (
            unit_2_config,
            unit_4_analysis,
            unit_5_candidate,
        )
    ):
        raise RuntimeError("UNIT 6 INVALID INPUT")

    strategy = unit_2_config.get("strategy", {})
    safety = unit_2_config.get("safety", {})
    market = unit_4_analysis
    signal = unit_5_candidate

    if not isinstance(strategy, dict):
        raise RuntimeError("UNIT 6 INVALID STRATEGY")

    if not isinstance(safety, dict):
        raise RuntimeError("UNIT 6 INVALID SAFETY")

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
                "UNIT 6 UNSAFE CONFIG: " + key
            )

    if (
        market.get("read_only") is not True
        or market.get("trade_authorized") is not False
        or market.get("candle_data_fresh") is not True
        or market.get("strategy_evidence_version")
        != "U4_OLD_NEW_ADAPTED_V1"
    ):
        raise RuntimeError(
            "UNIT 6 UNIT 4 CONTRACT FAILED"
        )

    if (
        signal.get("read_only") is not True
        or signal.get("trade_authorized") is not False
        or signal.get("symbol") != market.get("symbol")
    ):
        raise RuntimeError(
            "UNIT 6 UNIT 5 CONTRACT FAILED"
        )

    for key in (
        "one_direction_only",
        "anti_duplicate_orders",
        "exclusive_mode",
        "active_trade_mode_lock",
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 6 PROTECTION DISABLED: " + key
            )

    def number(value, label):
        try:
            result = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise RuntimeError(
                "UNIT 6 INVALID " + label
            ) from exc

        if not math.isfinite(result):
            raise RuntimeError(
                "UNIT 6 NONFINITE " + label
            )

        return result

    age = number(
        market.get("candle_age_seconds"),
        "CANDLE AGE",
    )

    if not 0 <= age <= 180:
        raise RuntimeError("UNIT 6 STALE CANDLES")

    print(
        "PASS: UNIT 6 RECEIVED UNITS 2/4/5",
        flush=True,
    )

    print(
        "PASS: UNIT 6 READ ONLY SAFETY",
        flush=True,
    )

    # ========================================================
    # 2. VALIDATE UNIT 5 ADMISSION FIELDS
    # ========================================================

    qualified = signal.get("qualified") is True
    mode = signal.get("active_mode", "NONE")
    side = signal.get("direction", "NONE")

    candidate_mode = signal.get(
        "candidate_mode", "NONE"
    )

    candidate_stage = signal.get(
        "candidate_stage", "NONE"
    )

    unit5_reason = str(
        signal.get(
            "qualification_reason",
            "UNKNOWN",
        )
    )

    higher_mode = signal.get(
        "higher_mode_developing"
    ) is True

    if mode not in (
        "NONE", "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError("UNIT 6 INVALID ACTIVE MODE")

    if side not in ("NONE", "LONG", "SHORT"):
        raise RuntimeError("UNIT 6 INVALID DIRECTION")

    if candidate_mode not in (
        "NONE", "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError("UNIT 6 INVALID CANDIDATE")

    if candidate_stage not in (
        "NONE", "DEVELOPING", "QUALIFIED",
        "PENDING_UNIT_6", "REJECTED"
    ):
        raise RuntimeError("UNIT 6 INVALID STAGE")

    if qualified and (
        mode == "NONE"
        or side == "NONE"
        or candidate_mode != mode
        or candidate_stage not in (
            "QUALIFIED",
            "PENDING_UNIT_6",
        )
    ):
        raise RuntimeError(
            "UNIT 6 QUALIFIED SIGNAL INCONSISTENT"
        )

    if not qualified and mode != "NONE":
        raise RuntimeError(
            "UNIT 6 UNQUALIFIED MODE LEAK"
        )

    # ========================================================
    # 3. LEVERAGE REFERENCE
    # ========================================================

    leverage = number(
        strategy.get("leverage_target", 100),
        "LEVERAGE",
    )

    if leverage <= 0:
        raise RuntimeError("UNIT 6 INVALID LEVERAGE")

    leverage_regime = (
        "GE_100X" if leverage >= 100
        else "50_99X" if leverage >= 50
        else "20_49X" if leverage >= 20
        else "11_19X" if leverage >= 11
        else "LE_10X"
    )

    # No exchange leverage has been checked here.

    # ========================================================
    # 4. CLOSED-CANDLE DIRECTION PERSISTENCE
    # ========================================================

    candles = signal.get(
        "recent_closed_klines", []
    )

    if not isinstance(candles, list) or len(candles) < 4:
        raise RuntimeError(
            "UNIT 6 INSUFFICIENT CLOSED CANDLES"
        )

    persistence_window = 3
    persistence_required = 2

    persistence_directions = []

    for candle in candles[-persistence_window:]:

        candle_open = number(
            candle.get("open"),
            "CANDLE OPEN",
        )

        candle_close = number(
            candle.get("close"),
            "CANDLE CLOSE",
        )

        if candle_close > candle_open:
            persistence_directions.append("LONG")
        elif candle_close < candle_open:
            persistence_directions.append("SHORT")
        else:
            persistence_directions.append("NONE")

    persistence_confirmations = (
        persistence_directions.count(side)
        if side in ("LONG", "SHORT")
        else 0
    )

    persistence_pass = (
        persistence_confirmations
        >= persistence_required
    )

    # ========================================================
    # 5. DIRECTION AND MOMENTUM EVIDENCE
    # ========================================================

    direction_evidence = market.get(
        "direction_evidence", "NONE"
    )

    move5 = number(
        market.get("move_5m_pct"),
        "FIVE MINUTE MOVE",
    )

    move15 = number(
        market.get("move_15m_pct"),
        "FIFTEEN MINUTE MOVE",
    )

    sign = (
        1 if side == "LONG"
        else -1 if side == "SHORT"
        else 0
    )

    fifteen_minute_support_pass = (
        sign != 0
        and move15 * sign >= 0
    )

    momentum_conflict = (
        sign != 0
        and move5 * sign < 0
    )

    sideways_regime = (
        market.get("sideways_candidate") is True
    )

    separation = number(
        market.get("ema19_50_separation_pct"),
        "EMA SEPARATION",
    )

    compression_threshold_pct = 0.09
    ema_compressed = (
        separation <= compression_threshold_pct
    )

    # ========================================================
    # 6. SCALP PRICE AND QUALITY PRECHECK
    # ========================================================

    scalp_quality_minimum = number(
        strategy.get(
            "scalp_quality_threshold", 70.0
        ),
        "SCALP QUALITY MINIMUM",
    )

    if not 0 < scalp_quality_minimum <= 100:
        raise RuntimeError(
            "UNIT 6 INVALID SCALP QUALITY FLOOR"
        )

    price_weight = number(
        strategy.get(
            "scalp_price_weight_percent", 50.0
        ),
        "SCALP PRICE WEIGHT",
    )

    if price_weight != 50.0:
        raise RuntimeError(
            "UNIT 6 SCALP PRICE WEIGHT NOT 50%"
        )

    extension = number(
        market.get("price_extension_cluster"),
        "PRICE EXTENSION",
    )

    extension_limit = number(
        strategy.get(
            "scalp_max_ema_extension_clusters", 1.5
        ),
        "EXTENSION LIMIT",
    )

    extension_pass = (
        extension <= extension_limit
    )

    atr = number(
        market.get("atr14"),
        "ATR",
    )

    price = number(
        market.get("latest_close"),
        "LATEST PRICE",
    )

    if price <= 0 or atr <= 0:
        raise RuntimeError("UNIT 6 INVALID PRICE/ATR")

    scalp_pending = (
        qualified
        and mode == "SCALP"
        and candidate_mode == "SCALP"
    )

    price_score = 0.0
    other_score = 0.0
    scalp_score = None
    scalp_pass = False

    if scalp_pending:

        price_score = (
            20.0 if sideways_regime else 0.0
        )

        price_score += (
            15.0 if extension_pass else 0.0
        )

        price_score += (
            15.0 if not momentum_conflict else 0.0
        )

        other_score = (
            20.0 if persistence_pass else 0.0
        )

        other_score += (
            15.0 if fifteen_minute_support_pass
            else 0.0
        )

        other_score += (
            15.0 if not higher_mode else 0.0
        )

        scalp_score = (
            price_score + other_score
        )

        scalp_pass = (
            scalp_score >= scalp_quality_minimum
        )

    # ========================================================
    # 7. ESTIMATED SCALP ECONOMICS
    # ========================================================

    fee_side_pct = number(
        strategy.get(
            "scalp_estimated_taker_fee_percent",
            0.08,
        ),
        "TAKER FEE",
    )

    prospective_range_pct = number(
        signal.get("scalp_range_pct", 0.0),
        "PROSPECTIVE RANGE",
    )

    estimated_round_trip_pct = (
        2.0 * fee_side_pct + 0.02
    )

    estimated_net_price_pct = (
        prospective_range_pct
        - estimated_round_trip_pct
    )

    estimated_net_roi_pct = (
        estimated_net_price_pct * leverage
    )

    min_net_roi = number(
        strategy.get(
            "scalp_min_net_roi_percent", 5.0
        ),
        "MIN NET ROI",
    )

    estimated_fee_pass = (
        estimated_net_roi_pct >= min_net_roi
    )

    # Public candles do not verify order-book spread,
    # actual slippage, funding or execution fees.
    live_cost_verified = False

    scalp_details = {
        "price_score": price_score,
        "other_score": other_score,
        "extension_ratio": extension,
        "extension_pass": extension_pass,
        "persistence_confirmations":
            persistence_confirmations,
        "prospective_range_pct":
            prospective_range_pct,
        "estimated_round_trip_cost_pct":
            estimated_round_trip_pct,
        "estimated_net_price_pct":
            estimated_net_price_pct,
        "provisional_leveraged_roi_pct":
            estimated_net_roi_pct,
        "minimum_net_roi_pct": min_net_roi,
        "estimated_fee_pass": estimated_fee_pass,
        "live_cost_verified": False,
    }

    # ========================================================
    # 8. ARBITRATION AND ADMISSION
    # ========================================================

    execution_intent = False
    admitted_mode = "NONE"
    admitted_side = "NONE"

    reason = (
        "UNIT_5_NOT_QUALIFIED:" + unit5_reason
    )

    if qualified and mode in (
        "BREAKOUT", "STRUCTURE"
    ):

        if direction_evidence != side:
            reason = "DIRECTION_EVIDENCE_CONFLICT"

        elif mode == "BREAKOUT" and not (
            signal.get("breakout_ready") is True
        ):
            reason = "BREAKOUT_NOT_CONFIRMED"

        elif mode == "STRUCTURE" and not (
            signal.get("structure_ready") is True
        ):
            reason = "STRUCTURE_NOT_CONFIRMED"

        else:
            execution_intent = True
            admitted_mode = mode
            admitted_side = side

            reason = (
                mode + "_PRELIMINARY_ADMISSION_PASS"
            )

    elif scalp_pending:

        if higher_mode:
            reason = "SCALP_BLOCKED_BY_HIGHER_MODE"

        elif not sideways_regime:
            reason = "SCALP_NOT_SIDEWAYS"

        elif not extension_pass:
            reason = "SCALP_EXTENSION_REJECTED"

        elif not persistence_pass:
            reason = "SCALP_PERSISTENCE_REJECTED"

        elif not scalp_pass:
            reason = "SCALP_QUALITY_BELOW_THRESHOLD"

        elif not estimated_fee_pass:
            reason = "SCALP_ESTIMATED_NET_ROI_TOO_LOW"

        else:
            reason = (
                "SCALP_PRELIMINARY_PASS_"
                "AWAITING_VERIFIED_LIVE_COSTS"
            )

        # Do not authorize SCALP from estimated costs alone.
        execution_intent = False

    elif candidate_stage == "DEVELOPING":
        reason = (
            "HIGHER_MODE_DEVELOPING"
            if higher_mode
            else "CANDIDATE_DEVELOPING"
        )

    # ========================================================
    # 9. CONSISTENT UNIT 7 HANDOVER
    # ========================================================

    if not execution_intent:
        admitted_mode = "NONE"
        admitted_side = "NONE"

    signal_qualified = execution_intent

    if execution_intent:
        if (
            admitted_mode not in (
                "BREAKOUT", "STRUCTURE"
            )
            or admitted_side not in (
                "LONG", "SHORT"
            )
        ):
            raise RuntimeError(
                "UNIT 6 ADMISSION INCONSISTENT"
            )

    result = {

        "execution_intent": execution_intent,
        "signal_qualified": signal_qualified,

        "active_mode": admitted_mode,
        "direction": admitted_side,

        "candidate_mode": candidate_mode,
        "candidate_stage": candidate_stage,

        "higher_mode_developing": higher_mode,

        "unit_5_reason": unit5_reason,
        "admission_reason": reason,

        "leverage_target": leverage,
        "leverage_regime": leverage_regime,

        "exchange_leverage_verified": False,
        "leverage_source": "WEEX_EXCHANGE",
        "effective_leverage": None,

        "sideways_regime": sideways_regime,
        "ema_compressed": ema_compressed,
        "compression_threshold_pct":
            compression_threshold_pct,

        "momentum_conflict": momentum_conflict,

        "persistence_window": persistence_window,
        "persistence_required": persistence_required,
        "persistence_confirmations":
            persistence_confirmations,
        "persistence_directions":
            persistence_directions,
        "persistence_pass": persistence_pass,

        "fifteen_minute_support_pass":
            fifteen_minute_support_pass,

        "scalp_quality_score": scalp_score,
        "scalp_quality_minimum":
            scalp_quality_minimum,
        "scalp_quality_pass": scalp_pass,
        "scalp_quality_details": scalp_details,

        "live_cost_verified": live_cost_verified,

        "read_only": True,
        "trade_authorized": False,
        "order_payload_created": False,
        "demo_order_submitted": False,
        "real_order_submitted": False,
        "exchange_write": False,
    }

    print(
        "UNIT 6 CANDIDATE MODE =",
        candidate_mode,
        flush=True,
    )

    print(
        "UNIT 6 CANDIDATE STAGE =",
        candidate_stage,
        flush=True,
    )

    print(
        "UNIT 6 ADMITTED MODE =",
        admitted_mode,
        flush=True,
    )

    print(
        "UNIT 6 DIRECTION =",
        admitted_side,
        flush=True,
    )

    print(
        "UNIT 6 EXECUTION INTENT =",
        execution_intent,
        flush=True,
    )

    print(
        "UNIT 6 ADMISSION REASON =",
        reason,
        flush=True,
    )

    print(
        "UNIT 6 SCALP QUALITY SCORE =",
        scalp_score,
        flush=True,
    )

    print(
        "UNIT 6 SCALP EST NET ROI =",
        round(estimated_net_roi_pct, 4),
        flush=True,
    )

    print(
        "UNIT 6 LIVE COST VERIFIED = FALSE",
        flush=True,
    )

    print(
        "UNIT 6 TRADE AUTHORIZED = FALSE",
        flush=True,
    )

    print(
        "UNIT 6 EXCHANGE WRITE = NONE",
        flush=True,
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
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE,
    )
)


# ============================================================
# UNIT 6 ISOLATED VERIFICATION
# ZERO INDENTATION
# ============================================================

UNIT_6_ISOLATED_TEST = True

_u6 = FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE

if not isinstance(_u6, dict):
    raise RuntimeError("UNIT 6 OUTPUT NOT DICT")

_required_u6 = (
    "execution_intent",
    "signal_qualified",
    "active_mode",
    "direction",
    "admission_reason",
    "leverage_target",
    "persistence_confirmations",
    "scalp_quality_score",
    "read_only",
    "trade_authorized",
    "order_payload_created",
    "demo_order_submitted",
    "real_order_submitted",
    "exchange_write",
)

for _key in _required_u6:
    if _key not in _u6:
        raise RuntimeError(
            "UNIT 6 MISSING OUTPUT: " + _key
        )

if _u6["execution_intent"] != _u6["signal_qualified"]:
    raise RuntimeError(
        "UNIT 6 INTENT / QUALIFICATION MISMATCH"
    )

if not _u6["execution_intent"]:
    if (
        _u6["active_mode"] != "NONE"
        or _u6["direction"] != "NONE"
    ):
        raise RuntimeError(
            "UNIT 6 IDLE OUTPUT INCONSISTENT"
        )

if (
    _u6["read_only"] is not True
    or _u6["trade_authorized"] is not False
    or _u6["order_payload_created"] is not False
    or _u6["demo_order_submitted"] is not False
    or _u6["real_order_submitted"] is not False
    or _u6["exchange_write"] is not False
):
    raise RuntimeError("UNIT 6 SAFETY CONTRACT FAILED")

print("=" * 80, flush=True)
print("UNIT 6 ISOLATED TEST = PASS", flush=True)
print("UNIT 6 VERIFIED = TRUE", flush=True)
print("UNITS 7-15 EXECUTION = NOT STARTED", flush=True)
print("=" * 80, flush=True)

UNIT_6_ISOLATED_TEST = False
if UNIT_6_ISOLATED_TEST:
    print(
        "UNIT 6 TEST COMPLETE - STOPPING BEFORE UNIT 7",
        flush=True,
    )
    raise SystemExit(0)


# ============================================================
# END COMPLETE UNIT 6 REPLACEMENT
# ZERO INDENTATION
# EXISTING UNIT 7 CONTINUES BELOW
# ============================================================


# ============================================================
# START COMPLETE UNIT 7 REPLACEMENT
# ZERO INDENTATION
# OLD 15 UNIT + NEW RECONSTRUCTION ADAPTATION
# UNIT 6 TO UNIT 8 POSITION SIZING HANDOVER
# ============================================================

def fresh_reconstruction_unit_7(
    unit_2_config,
    unit_6_candidate,
):

    import math

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 7 START")

    # ========================================================
    # 1. INPUT VALIDATION
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 7 INVALID UNIT 2 CONFIG"
        )

    if not isinstance(unit_6_candidate, dict):
        raise RuntimeError(
            "UNIT 7 INVALID UNIT 6 RESULT"
        )

    strategy = unit_2_config.get("strategy")
    safety = unit_2_config.get("safety")
    exchange = unit_2_config.get("exchange")
    precision = unit_2_config.get("market_precision")

    if not all(
        isinstance(x, dict)
        for x in (strategy, safety, exchange, precision)
    ):
        raise RuntimeError(
            "UNIT 7 CONFIG SECTIONS MISSING"
        )

    if (
        unit_2_config.get("execution_environment")
        != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or exchange.get("market_symbol") != "BTCUSDT"
        or exchange.get("demo_order_symbol") != "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 7 EXCHANGE CONTRACT FAILED"
        )

    print(
        "PASS: UNIT 7 RECEIVED UNIT 2 CONFIG",
        flush=True,
    )

    # ========================================================
    # 2. SAFETY BOUNDARY
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

    for key in forbidden:
        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 7 UNSAFE CAPABILITY: " + key
            )

    if (
        unit_6_candidate.get("read_only") is not True
        or unit_6_candidate.get("trade_authorized") is not False
        or unit_6_candidate.get("exchange_write") is not False
        or unit_6_candidate.get("order_payload_created") is not False
    ):
        raise RuntimeError(
            "UNIT 7 UNIT 6 SAFETY FAILED"
        )

    print(
        "PASS: UNIT 7 READ ONLY SAFETY",
        flush=True,
    )

    # ========================================================
    # 3. VALIDATE UNIT 6 SIGNAL
    # ========================================================

    required = (
        "execution_intent",
        "signal_qualified",
        "active_mode",
        "direction",
        "admission_reason",
        "unit_5_reason",
    )

    for key in required:
        if key not in unit_6_candidate:
            raise RuntimeError(
                "UNIT 7 MISSING UNIT 6 FIELD: " + key
            )

    intent = unit_6_candidate["execution_intent"]
    qualified = unit_6_candidate["signal_qualified"]
    mode = unit_6_candidate["active_mode"]
    side = unit_6_candidate["direction"]

    admission_reason = str(
        unit_6_candidate["admission_reason"]
    )

    unit5_reason = str(
        unit_6_candidate["unit_5_reason"]
    )

    if (
        type(intent) is not bool
        or type(qualified) is not bool
        or intent != qualified
    ):
        raise RuntimeError(
            "UNIT 7 INTENT QUALIFICATION MISMATCH"
        )

    if intent:

        if (
            mode not in ("BREAKOUT", "STRUCTURE")
            or side not in ("LONG", "SHORT")
        ):
            raise RuntimeError(
                "UNIT 7 INVALID ADMITTED SIGNAL"
            )

        expected_reason = (
            mode + "_PRELIMINARY_ADMISSION_PASS"
        )

        if admission_reason != expected_reason:
            raise RuntimeError(
                "UNIT 7 INVALID ADMISSION REASON"
            )

    else:

        if mode != "NONE" or side != "NONE":
            raise RuntimeError(
                "UNIT 7 IDLE SIGNAL INCONSISTENT"
            )

    print(
        "PASS: UNIT 7 RECEIVED UNIT 6 HANDOVER",
        flush=True,
    )

    # ========================================================
    # 4. VALIDATE SIZING PARAMETERS
    # ========================================================

    def positive_number(value, label):

        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
            OverflowError,
        ) as exc:
            raise RuntimeError(
                "UNIT 7 INVALID " + label
            ) from exc

        if not math.isfinite(value) or value <= 0:
            raise RuntimeError(
                "UNIT 7 NONPOSITIVE " + label
            )

        return value

    configured_leverage = positive_number(
        strategy.get("leverage_target"),
        "LEVERAGE",
    )

    initial_margin_percent = positive_number(
        strategy.get("initial_margin_percent"),
        "MARGIN PERCENT",
    )

    fixed_initial_usdt = positive_number(
        strategy.get("initial_fixed_usdt"),
        "INITIAL USDT",
    )

    exposure_cap = positive_number(
        strategy.get("exposure_cap_percent"),
        "EXPOSURE CAP",
    )

    quantity_step = positive_number(
        precision.get("quantity_step"),
        "QUANTITY STEP",
    )

    minimum_quantity = positive_number(
        precision.get("minimum_quantity"),
        "MINIMUM QUANTITY",
    )

    price_step = positive_number(
        precision.get("price_step"),
        "PRICE STEP",
    )

    if exposure_cap > 35.0:
        raise RuntimeError(
            "UNIT 7 EXPOSURE CAP EXCEEDED"
        )

    if configured_leverage > 100:
        raise RuntimeError(
            "UNIT 7 LEVERAGE REFERENCE EXCEEDED"
        )

    if (
        strategy.get("one_direction_only") is not True
        or strategy.get("anti_duplicate_orders") is not True
        or strategy.get("active_trade_mode_lock") is not True
        or strategy.get("exclusive_mode") is not True
    ):
        raise RuntimeError(
            "UNIT 7 STRATEGY PROTECTION DISABLED"
        )

    # ========================================================
    # 5. ACTUAL EXCHANGE READINESS
    # ========================================================

    # This unit deliberately does not read private account
    # endpoints or submit orders.
    #
    # A reference leverage setting is NOT proof of the
    # actual leverage assigned to LONG or SHORT by WEEX.
    #
    # Margin, executable quantity, liquidation boundary,
    # pending orders, and position state remain unverified.

    balance_verified = False
    position_state_verified = False
    margin_mode_verified = False
    exchange_leverage_verified = False
    quantity_rules_verified = False
    executable_price_verified = False
    maximum_exposure_verified = False
    backup_capacity_verified = False

    effective_leverage = None
    initial_margin_usdt = None
    position_notional_usdt = None
    proposed_quantity = None

    position_sizing_performed = False
    quantity_calculated = False
    order_payload_created = False

    # ========================================================
    # 6. SIGNAL STATUS
    # ========================================================

    if intent:

        status = "HELD"

        sizing_reason = (
            "QUALIFIED_SIGNAL_AWAITING_"
            "VERIFIED_ACCOUNT_AND_EXCHANGE_DATA"
        )

    else:

        status = "IDLE"

        sizing_reason = (
            "NO_QUALIFIED_SIGNAL"
        )

    # The original signal is retained as information.
    # No execution authorization passes this unit.

    trade_authorized = False
    demo_order_enabled = False
    real_order_enabled = False
    exchange_write = False

    # ========================================================
    # 7. PRESERVE OLD AND NEW OUTPUT INTERFACES
    # ========================================================

    result = {

        "status": status,

        "signal_received": intent,
        "signal_qualified": qualified,

        "active_mode": mode,
        "direction": side,

        "unit_5_reason": unit5_reason,
        "admission_reason": admission_reason,
        "sizing_reason": sizing_reason,

        "configured_leverage": configured_leverage,
        "leverage_target": configured_leverage,
        "leverage_source": "UNIT_2_REFERENCE",

        "exchange_leverage_verified":
            exchange_leverage_verified,

        "effective_leverage":
            effective_leverage,

        "precision_reference": {
            "configuration_present": True,
            "quantity_step": quantity_step,
            "minimum_quantity": minimum_quantity,
            "price_step": price_step,
            "exchange_precision_verified": False,
        },

        "initial_margin_percent":
            initial_margin_percent,

        "initial_fixed_usdt":
            fixed_initial_usdt,

        "exposure_cap_percent":
            exposure_cap,

        "balance_verified":
            balance_verified,

        "position_state_verified":
            position_state_verified,

        "margin_mode_verified":
            margin_mode_verified,

        "quantity_rules_verified":
            quantity_rules_verified,

        "executable_price_verified":
            executable_price_verified,

        "maximum_exposure_verified":
            maximum_exposure_verified,

        "backup_capacity_verified":
            backup_capacity_verified,

        "account_balance_required": intent,

        "initial_margin_usdt":
            initial_margin_usdt,

        "position_notional_usdt":
            position_notional_usdt,

        "proposed_quantity":
            proposed_quantity,

        "position_sizing_performed":
            position_sizing_performed,

        "quantity_calculated":
            quantity_calculated,

        "order_payload_created":
            order_payload_created,

        "trade_authorized":
            trade_authorized,

        "demo_order_enabled":
            demo_order_enabled,

        "real_order_enabled":
            real_order_enabled,

        "exchange_write":
            exchange_write,

        "read_only": True,

        # Deliberately cleared at the sizing boundary.
        "execution_intent": False,

        # Preserve information for later verification.
        "upstream_execution_intent": intent,

        "candidate_mode":
            unit_6_candidate.get(
                "candidate_mode", "NONE"
            ),

        "candidate_stage":
            unit_6_candidate.get(
                "candidate_stage", "NONE"
            ),

        "closed_candle_id": None,

        "skip_reason": (
            admission_reason
            if status == "IDLE"
            else sizing_reason
        ),
    }

    # ========================================================
    # 8. FINAL HARD SAFETY VALIDATION
    # ========================================================

    if (
        result["execution_intent"] is not False
        or result["trade_authorized"] is not False
        or result["order_payload_created"] is not False
        or result["quantity_calculated"] is not False
        or result["position_sizing_performed"] is not False
        or result["demo_order_enabled"] is not False
        or result["real_order_enabled"] is not False
        or result["exchange_write"] is not False
    ):
        raise RuntimeError(
            "UNIT 7 EXECUTION SAFETY FAILURE"
        )

    if status == "HELD" and not intent:
        raise RuntimeError(
            "UNIT 7 HELD STATE INVALID"
        )

    if status == "IDLE" and intent:
        raise RuntimeError(
            "UNIT 7 IDLE STATE INVALID"
        )

    # ========================================================
    # 9. RENDER DIAGNOSTICS
    # ========================================================

    print(
        "UNIT 7 STATUS =",
        status,
        flush=True,
    )

    print(
        "UNIT 7 SIGNAL RECEIVED =",
        intent,
        flush=True,
    )

    print(
        "UNIT 7 ACTIVE MODE =",
        mode,
        flush=True,
    )

    print(
        "UNIT 7 DIRECTION =",
        side,
        flush=True,
    )

    print(
        "UNIT 7 CONFIGURED LEVERAGE =",
        configured_leverage,
        flush=True,
    )

    print(
        "UNIT 7 EXCHANGE LEVERAGE VERIFIED = FALSE",
        flush=True,
    )

    print(
        "UNIT 7 BALANCE VERIFIED = FALSE",
        flush=True,
    )

    print(
        "UNIT 7 POSITION VERIFIED = FALSE",
        flush=True,
    )

    print(
        "UNIT 7 SIZING REASON =",
        sizing_reason,
        flush=True,
    )

    print(
        "UNIT 7 EXECUTION INTENT = FALSE",
        flush=True,
    )

    print(
        "UNIT 7 QUANTITY CALCULATED = FALSE",
        flush=True,
    )

    print(
        "UNIT 7 DEMO ORDER = NONE",
        flush=True,
    )

    print(
        "UNIT 7 REAL ORDER = NONE",
        flush=True,
    )

    print(
        "UNIT 7 EXCHANGE WRITE = NONE",
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 7 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 7
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_7_RESULT = (
    fresh_reconstruction_unit_7(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE,
    )
)

# Legacy frozen 15-unit model compatibility.

FRESH_RECONSTRUCTION_SIZING_CANDIDATE = (
    FRESH_RECONSTRUCTION_UNIT_7_RESULT
)


# ============================================================
# UNIT 7 ISOLATED TEST
# ZERO INDENTATION
# ============================================================

UNIT_7_ISOLATED_TEST = True

_u7 = FRESH_RECONSTRUCTION_UNIT_7_RESULT

if not isinstance(_u7, dict):
    raise RuntimeError(
        "UNIT 7 OUTPUT IS NOT A DICTIONARY"
    )

_required_u7 = (
    "status",
    "signal_received",
    "signal_qualified",
    "active_mode",
    "direction",
    "sizing_reason",
    "configured_leverage",
    "exchange_leverage_verified",
    "balance_verified",
    "position_state_verified",
    "account_balance_required",
    "proposed_quantity",
    "position_sizing_performed",
    "quantity_calculated",
    "order_payload_created",
    "trade_authorized",
    "execution_intent",
    "read_only",
    "exchange_write",
)

for _key in _required_u7:
    if _key not in _u7:
        raise RuntimeError(
            "UNIT 7 MISSING OUTPUT FIELD: " + _key
        )

if _u7["status"] not in ("IDLE", "HELD"):
    raise RuntimeError(
        "UNIT 7 INVALID STATUS"
    )

if _u7["status"] == "IDLE":
    if (
        _u7["signal_received"] is not False
        or _u7["account_balance_required"] is not False
    ):
        raise RuntimeError(
            "UNIT 7 IDLE HANDOVER FAILED"
        )

if _u7["status"] == "HELD":
    if (
        _u7["signal_received"] is not True
        or _u7["account_balance_required"] is not True
    ):
        raise RuntimeError(
            "UNIT 7 HELD HANDOVER FAILED"
        )

if (
    _u7["execution_intent"] is not False
    or _u7["read_only"] is not True
    or _u7["trade_authorized"] is not False
    or _u7["exchange_write"] is not False
    or _u7["quantity_calculated"] is not False
    or _u7["order_payload_created"] is not False
):
    raise RuntimeError(
        "UNIT 7 SAFETY TEST FAILED"
    )

# ============================================================
# SYNTHETIC BRANCH TESTS
# NO NETWORK REQUESTS
# ============================================================

_fake_admitted = dict(
    FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE
)

_fake_admitted.update({
    "execution_intent": True,
    "signal_qualified": True,
    "active_mode": "BREAKOUT",
    "direction": "LONG",
    "admission_reason":
        "BREAKOUT_PRELIMINARY_ADMISSION_PASS",
})

_fake_result = fresh_reconstruction_unit_7(
    FRESH_RECONSTRUCTION_CONFIG,
    _fake_admitted,
)

if (
    _fake_result["status"] != "HELD"
    or _fake_result["signal_received"] is not True
    or _fake_result["trade_authorized"] is not False
    or _fake_result["quantity_calculated"] is not False
    or _fake_result["execution_intent"] is not False
):
    raise RuntimeError(
        "UNIT 7 SYNTHETIC HELD TEST FAILED"
    )

_fake_invalid = dict(_fake_admitted)
_fake_invalid["direction"] = "NONE"

try:
    fresh_reconstruction_unit_7(
        FRESH_RECONSTRUCTION_CONFIG,
        _fake_invalid,
    )
except RuntimeError:
    print(
        "PASS: UNIT 7 REJECTED INVALID DIRECTION",
        flush=True,
    )
else:
    raise RuntimeError(
        "UNIT 7 INVALID SIGNAL WAS ACCEPTED"
    )

print("=" * 80, flush=True)
print(
    "UNIT 7 ISOLATED TEST = PASS",
    flush=True,
)
print(
    "UNIT 7 VERIFIED = TRUE",
    flush=True,
)
print(
    "UNIT 7 SYNTHETIC HELD TEST = PASS",
    flush=True,
)
print(
    "UNITS 8-15 EXECUTION = NOT STARTED",
    flush=True,
)
print("=" * 80, flush=True)

UNIT_7_ISOLATED_TEST = False
if UNIT_7_ISOLATED_TEST:
    print(
        "UNIT 7 TEST COMPLETE - STOPPING BEFORE UNIT 8",
        flush=True,
    )
    raise SystemExit(0)


# ============================================================
# END COMPLETE UNIT 7 REPLACEMENT
# ZERO INDENTATION
# UNIT 8 CONTINUES BELOW
# ============================================================


# ============================================================
# START COMPLETE UNIT 8 REPLACEMENT
# ZERO INDENTATION
# OLD 15-UNIT + NEW RECONSTRUCTION ADAPTATION
#
# ACTUAL WEEX LEVERAGE POLICY:
# NO CONFIGURED-LEVERAGE SUBSTITUTION
# NO ORDER / ACCOUNT MUTATION
# ============================================================

def fresh_reconstruction_unit_8(
    unit_2_config,
    unit_4_analysis,
    unit_7_result,
):
    import math

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 8 START")

    # ========================================================
    # 1. INPUT CONTRACT
    # ========================================================

    if not all(
        isinstance(x, dict)
        for x in (
            unit_2_config,
            unit_4_analysis,
            unit_7_result,
        )
    ):
        raise RuntimeError("UNIT 8 INVALID INPUT")

    config = unit_2_config
    market = unit_4_analysis
    upstream = unit_7_result

    safety = config.get("safety", {})
    strategy = config.get("strategy", {})
    exchange = config.get("exchange", {})

    if not all(
        isinstance(x, dict)
        for x in (safety, strategy, exchange)
    ):
        raise RuntimeError("UNIT 8 INVALID CONFIG")

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or exchange.get("market_symbol") != "BTCUSDT"
        or exchange.get("demo_order_symbol") != "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 8 EXCHANGE CONTRACT FAILED"
        )

    # ========================================================
    # 2. READ-ONLY SAFETY
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

    for key in forbidden:
        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 8 UNSAFE FLAG: " + key
            )

    for key, expected in (
        ("read_only", True),
        ("trade_authorized", False),
        ("exchange_write", False),
        ("order_payload_created", False),
        ("execution_intent", False),
        ("quantity_calculated", False),
    ):
        if upstream.get(key) is not expected:
            raise RuntimeError(
                "UNIT 8 UNSAFE UNIT 7 FIELD: " + key
            )

    if (
        market.get("read_only") is not True
        or market.get("trade_authorized") is not False
        or market.get("strategy_evidence_version")
        != "U4_OLD_NEW_ADAPTED_V1"
    ):
        raise RuntimeError(
            "UNIT 8 MARKET CONTRACT FAILED"
        )

    print(
        "PASS: UNIT 8 READ ONLY SAFETY",
        flush=True,
    )

    # ========================================================
    # 3. NUMERIC VALIDATION
    # ========================================================

    def finite_number(value, label):
        try:
            result = float(value)
        except (
            ValueError,
            TypeError,
            OverflowError,
        ) as exc:
            raise RuntimeError(
                "UNIT 8 INVALID " + label
            ) from exc

        if not math.isfinite(result):
            raise RuntimeError(
                "UNIT 8 NONFINITE " + label
            )

        return result

    age = finite_number(
        market.get("candle_age_seconds"),
        "CANDLE AGE",
    )

    market_fresh = (
        market.get("candle_data_fresh") is True
        and 0 <= age <= 180
    )

    market_direction = market.get(
        "direction_evidence", "NONE"
    )

    if market_direction not in (
        "LONG", "SHORT", "NONE"
    ):
        raise RuntimeError(
            "UNIT 8 INVALID MARKET DIRECTION"
        )

    # ========================================================
    # 4. UNIT 7 HANDOVER
    # ========================================================

    upstream_status = upstream.get("status")
    signal_received = upstream.get("signal_received")
    signal_qualified = upstream.get("signal_qualified")
    mode = upstream.get("active_mode", "NONE")
    side = upstream.get("direction", "NONE")

    if upstream_status not in ("IDLE", "HELD"):
        raise RuntimeError(
            "UNIT 8 INVALID UNIT 7 STATUS"
        )

    if (
        type(signal_received) is not bool
        or type(signal_qualified) is not bool
        or signal_received != signal_qualified
    ):
        raise RuntimeError(
            "UNIT 8 INVALID SIGNAL FLAGS"
        )

    if upstream_status == "HELD":
        if (
            not signal_received
            or mode not in ("BREAKOUT", "STRUCTURE")
            or side not in ("LONG", "SHORT")
        ):
            raise RuntimeError(
                "UNIT 8 INVALID HELD HANDOVER"
            )
    else:
        if (
            signal_received
            or mode != "NONE"
            or side != "NONE"
        ):
            raise RuntimeError(
                "UNIT 8 INVALID IDLE HANDOVER"
            )

    print(
        "PASS: UNIT 8 RECEIVED UNIT 7 RESULT",
        flush=True,
    )

    # ========================================================
    # 5. ACTUAL WEEX LEVERAGE
    # ========================================================

    # Unit 2 contains only target/reference leverage.
    # The reference must never become effective leverage.
    #
    # Real exchange leverage is side/account-specific.
    #
    # Unit 8 currently has no authenticated account reads.
    # Therefore actual WEEX leverage is UNKNOWN.
    #
    # Do not silently fall back to the configured target.

    configured_leverage_reference = finite_number(
        strategy.get("leverage_target"),
        "CONFIGURED LEVERAGE",
    )

    if configured_leverage_reference <= 0:
        raise RuntimeError(
            "UNIT 8 INVALID LEVERAGE REFERENCE"
        )

    effective_leverage = None
    exchange_leverage_verified = False
    exchange_leverage_source = None
    exchange_leverage_side = None

    # Future authenticated reader must independently
    # verify leverage for the actual DEMO position side.
    #
    # Do not inject leverage via configuration here.
    # Do not use guessed 100x or 20x values.
    # Do not mutate leverage on WEEX.

    position_sizing_allowed = False

    # ========================================================
    # 6. SIGNAL FRESHNESS
    # ========================================================

    signal_direction_match = (
        signal_received
        and market_direction == side
    )

    if not market_fresh:
        status = "BLOCKED"
        reason = "STALE_MARKET_EVIDENCE"

    elif upstream_status == "IDLE":
        status = "IDLE"
        reason = "NO_QUALIFIED_SIGNAL"

    elif not signal_direction_match:
        status = "BLOCKED"
        reason = "SIGNAL_DIRECTION_CONFLICT"

    else:
        status = "PENDING"
        reason = (
            "SIGNAL_ALIGNED_AWAITING_"
            "WEEX_AND_CONTINUITY_VERIFICATION"
        )

    candidate_preserved = status == "PENDING"

    pending_mode = (
        mode if candidate_preserved else "NONE"
    )

    pending_direction = (
        side if candidate_preserved else "NONE"
    )

    # ========================================================
    # 7. CONTINUITY AND DUPLICATE SAFETY
    # ========================================================

    # A single startup snapshot is not sufficient
    # to establish multiple independent confirmations.
    #
    # The later continuous scanner must provide
    # distinct candle IDs across multiple scans.

    continuity_required = int(
        strategy.get(
            "direction_confirmation_required", 2
        )
    )

    if not 1 <= continuity_required <= 3:
        raise RuntimeError(
            "UNIT 8 INVALID CONTINUITY REQUIREMENT"
        )

    continuity_observations = (
        1 if candidate_preserved else 0
    )

    continuity_verified = False

    # These must come from authenticated WEEX reads
    # or independently verified later modules.

    position_flat_verified = False
    pending_orders_checked = False
    existing_position_checked = False
    duplicate_order_absence_verified = False
    reentry_authorized = False

    # ========================================================
    # 8. LEVERAGE-DEPENDENT TRADE PLAN
    # ========================================================

    # Only actual exchange leverage can support sizing.
    # In the current read-only Unit 8 test, balance,
    # leverage, position mode and quantity rules
    # have not been independently verified.

    balance_verified = False
    contract_rules_verified = False
    price_for_execution_verified = False

    position_sizing = {
        "status": "NOT_CALCULATED",
        "reference_leverage":
            configured_leverage_reference,
        "effective_leverage":
            effective_leverage,
        "exchange_leverage_verified":
            exchange_leverage_verified,
        "exchange_leverage_source":
            exchange_leverage_source,
        "exchange_leverage_side":
            exchange_leverage_side,
        "available_balance": None,
        "initial_margin_usdt": None,
        "position_notional_usdt": None,
        "quantity": None,
        "position_sizing_performed": False,
        "quantity_calculated": False,
    }

    trade_plan = None
    trade_plan_ready = False
    execution_intent = False
    trade_authorized = False

    if (
        exchange_leverage_verified
        and balance_verified
        and contract_rules_verified
        and price_for_execution_verified
        and position_flat_verified
        and pending_orders_checked
        and continuity_verified
    ):
        # This branch is intentionally unreachable
        # until independent exchange-data integrations
        # are implemented and validated.
        position_sizing_allowed = True

    if position_sizing_allowed:
        raise RuntimeError(
            "UNIT 8 UNEXPECTED SIZING ENABLEMENT"
        )

    # ========================================================
    # 9. COMPATIBLE UNIT 8 OUTPUT
    # ========================================================

    result = {
        "status": status,
        "reason": reason,
        "skip_reason": reason,

        # Old Unit 9 interface
        "active_mode": pending_mode,
        "direction": pending_direction,
        "signal_qualified": signal_qualified,
        "execution_intent": False,
        "trade_plan_ready": False,
        "trade_plan": None,
        "read_only": True,

        # Position sizing interface
        "position_sizing": position_sizing,
        "quantity_calculated": False,
        "position_sizing_performed": False,
        "effective_leverage": None,
        "exchange_leverage_verified": False,
        "exchange_leverage_source": None,
        "configured_leverage_reference":
            configured_leverage_reference,

        # New continuity interface
        "upstream_status": upstream_status,
        "upstream_signal_received": signal_received,
        "candidate_preserved": candidate_preserved,
        "pending_mode": pending_mode,
        "pending_direction": pending_direction,
        "market_fresh": market_fresh,
        "candle_age_seconds": age,
        "market_direction": market_direction,
        "signal_direction_match":
            signal_direction_match,
        "continuity_observations":
            continuity_observations,
        "continuity_required": continuity_required,
        "continuity_verified": False,

        "existing_position_checked": False,
        "position_flat_verified": False,
        "pending_orders_checked": False,
        "duplicate_order_absence_verified": False,
        "reentry_authorized": False,

        "balance_verified": False,
        "contract_rules_verified": False,
        "price_for_execution_verified": False,

        # Hard no-order boundary
        "trade_authorized": False,
        "order_payload_created": False,
        "demo_order_submitted": False,
        "real_order_submitted": False,
        "exchange_write": False,
    }

    if (
        result["trade_plan_ready"]
        or result["trade_plan"] is not None
        or result["effective_leverage"] is not None
        or result["execution_intent"]
        or result["trade_authorized"]
        or result["exchange_write"]
        or result["reentry_authorized"]
    ):
        raise RuntimeError(
            "UNIT 8 EXECUTION SAFETY FAILURE"
        )

    # ========================================================
    # 10. RENDER DIAGNOSTICS
    # ========================================================

    print(
        "UNIT 8 STATUS =",
        status,
        flush=True,
    )
    print(
        "UNIT 8 REASON =",
        reason,
        flush=True,
    )
    print(
        "UNIT 8 PENDING MODE =",
        pending_mode,
        flush=True,
    )
    print(
        "UNIT 8 PENDING DIRECTION =",
        pending_direction,
        flush=True,
    )
    print(
        "UNIT 8 CONFIGURED LEVERAGE REFERENCE =",
        configured_leverage_reference,
        flush=True,
    )
    print(
        "UNIT 8 WEEX EFFECTIVE LEVERAGE = UNKNOWN",
        flush=True,
    )
    print(
        "UNIT 8 EXCHANGE LEVERAGE VERIFIED = FALSE",
        flush=True,
    )
    print(
        "UNIT 8 POSITION SIZING = BLOCKED",
        flush=True,
    )
    print(
        "UNIT 8 CONTINUITY VERIFIED = FALSE",
        flush=True,
    )
    print(
        "UNIT 8 POSITION FLAT VERIFIED = FALSE",
        flush=True,
    )
    print(
        "UNIT 8 REENTRY AUTHORIZED = FALSE",
        flush=True,
    )
    print(
        "UNIT 8 TRADE PLAN READY = FALSE",
        flush=True,
    )
    print(
        "UNIT 8 DEMO ORDER = NONE",
        flush=True,
    )
    print(
        "UNIT 8 REAL ORDER = NONE",
        flush=True,
    )
    print(
        "UNIT 8 EXCHANGE WRITE = NONE",
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 8 RESULT = PASS"
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 8
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_8_RESULT = (
    fresh_reconstruction_unit_8(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        FRESH_RECONSTRUCTION_UNIT_7_RESULT,
    )
)


# ============================================================
# UNIT 8 ISOLATED TEST
# ZERO INDENTATION
# ============================================================

UNIT_8_ISOLATED_TEST = True

_u8 = FRESH_RECONSTRUCTION_UNIT_8_RESULT

if not isinstance(_u8, dict):
    raise RuntimeError(
        "UNIT 8 OUTPUT INVALID"
    )

_required_u8 = (
    "status",
    "active_mode",
    "direction",
    "signal_qualified",
    "execution_intent",
    "trade_plan_ready",
    "trade_plan",
    "skip_reason",
    "read_only",
    "exchange_leverage_verified",
    "effective_leverage",
    "continuity_verified",
    "position_flat_verified",
    "reentry_authorized",
    "exchange_write",
)

for _key in _required_u8:
    if _key not in _u8:
        raise RuntimeError(
            "UNIT 8 MISSING FIELD: " + _key
        )

if _u8["status"] not in (
    "IDLE", "PENDING", "BLOCKED"
):
    raise RuntimeError(
        "UNIT 8 INVALID STATUS"
    )

if (
    _u8["exchange_leverage_verified"] is not False
    or _u8["effective_leverage"] is not None
    or _u8["execution_intent"] is not False
    or _u8["trade_plan_ready"] is not False
    or _u8["trade_plan"] is not None
    or _u8["continuity_verified"] is not False
    or _u8["position_flat_verified"] is not False
    or _u8["reentry_authorized"] is not False
    or _u8["read_only"] is not True
    or _u8["exchange_write"] is not False
):
    raise RuntimeError(
        "UNIT 8 SAFETY TEST FAILED"
    )

# ============================================================
# SYNTHETIC PENDING TEST
# ============================================================

_fake_market = dict(
    FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
)

_fake_market.update({
    "direction_evidence": "LONG",
    "candle_data_fresh": True,
    "candle_age_seconds": 20.0,
})

_fake_u7 = dict(
    FRESH_RECONSTRUCTION_UNIT_7_RESULT
)

_fake_u7.update({
    "status": "HELD",
    "signal_received": True,
    "signal_qualified": True,
    "active_mode": "BREAKOUT",
    "direction": "LONG",
})

_fake_u8 = fresh_reconstruction_unit_8(
    FRESH_RECONSTRUCTION_CONFIG,
    _fake_market,
    _fake_u7,
)

if (
    _fake_u8["status"] != "PENDING"
    or _fake_u8["pending_mode"] != "BREAKOUT"
    or _fake_u8["effective_leverage"] is not None
    or _fake_u8["trade_plan_ready"] is not False
    or _fake_u8["execution_intent"] is not False
):
    raise RuntimeError(
        "UNIT 8 SYNTHETIC PENDING TEST FAILED"
    )

# ============================================================
# SYNTHETIC DIRECTION CONFLICT TEST
# ============================================================

_fake_conflict = dict(_fake_market)

_fake_conflict["direction_evidence"] = "SHORT"

_conflict_u8 = fresh_reconstruction_unit_8(
    FRESH_RECONSTRUCTION_CONFIG,
    _fake_conflict,
    _fake_u7,
)

if (
    _conflict_u8["status"] != "BLOCKED"
    or _conflict_u8["reason"]
    != "SIGNAL_DIRECTION_CONFLICT"
):
    raise RuntimeError(
        "UNIT 8 DIRECTION CONFLICT TEST FAILED"
    )

print("=" * 80, flush=True)


# ============================================================
# START UNIT 8 WEEX ACTUAL LEVERAGE EXTENSION
# ZERO INDENTATION
# SOURCE: ORIGINAL 15-UNIT UNIT 12 AUTHENTICATED GET
# READ ONLY - NO EXCHANGE MUTATION
# ============================================================

def fresh_unit_8_weex_leverage_read(
    config,
    unit_8_result,
):
    import os
    import time
    import hmac
    import hashlib
    import base64
    import json
    import math
    import urllib.request
    import urllib.error

    print("=" * 80, flush=True)
    print(
        "UNIT 8 WEEX LEVERAGE READ START",
        flush=True,
    )

    result = {
        "status": "UNVERIFIED",
        "source": "WEEX_DEMO_ACTIVE_POSITION",
        "request_method": "GET",
        "request_attempted": False,
        "http_success": False,
        "positions_read": False,
        "active_position_count": 0,
        "leverage_by_side": {
            "LONG": None,
            "SHORT": None,
        },
        "verified_by_side": {
            "LONG": False,
            "SHORT": False,
        },
        "effective_leverage": None,
        "exchange_leverage_verified": False,
        "reason": "NOT_CHECKED",
        "order_submission": False,
        "leverage_mutation": False,
        "exchange_write": False,
    }

    if (
        not isinstance(config, dict)
        or not isinstance(unit_8_result, dict)
    ):
        raise RuntimeError(
            "UNIT 8 LEVERAGE INPUT FAILED"
        )

    if config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 8 LEVERAGE NON-DEMO BLOCKED"
        )

    if (
        unit_8_result.get("trade_authorized")
        is not False
        or unit_8_result.get("exchange_write")
        is not False
        or unit_8_result.get("execution_intent")
        is not False
    ):
        raise RuntimeError(
            "UNIT 8 LEVERAGE SAFETY FAILED"
        )

    exchange = config.get("exchange", {})

    if (
        exchange.get("contract_base_url")
        != "https://api-contract.weex.com"
        or exchange.get("demo_order_symbol")
        != "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 8 LEVERAGE EXCHANGE CONFIG FAILED"
        )

    # --------------------------------------------------------
    # EXISTING RENDER ENVIRONMENT CREDENTIALS
    # --------------------------------------------------------

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
        result["status"] = "UNAVAILABLE"
        result["reason"] = "WEEX_CREDENTIALS_MISSING"

        print(
            "UNIT 8 WEEX LEVERAGE = UNAVAILABLE",
            flush=True,
        )

        return result

    # --------------------------------------------------------
    # DEMO POSITION READ - NEVER USE LIVE POSITION PATH
    # --------------------------------------------------------

    request_path = (
        "/capi/v3/sim/position/allPosition"
    )

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
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    request = urllib.request.Request(
        url=(
            "https://api-contract.weex.com"
            + request_path
        ),
        method="GET",
        headers={
            "ACCESS-KEY": api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": api_passphrase,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )

    if (
        request.get_method() != "GET"
        or request.data is not None
    ):
        raise RuntimeError(
            "UNIT 8 LEVERAGE NON-GET BLOCKED"
        )

    class Unit8NoRedirect(
        urllib.request.HTTPRedirectHandler
    ):
        def redirect_request(
            self, req, fp, code, msg,
            headers, newurl
        ):
            return None

    opener = urllib.request.build_opener(
        Unit8NoRedirect()
    )

    result["request_attempted"] = True

    try:
        with opener.open(
            request,
            timeout=15,
        ) as response:

            http_status = response.getcode()
            response_url = response.geturl()
            raw = response.read(1024 * 1024 + 1)

        if (
            http_status != 200
            or response_url != (
                "https://api-contract.weex.com"
                + request_path
            )
            or not raw
            or len(raw) > 1024 * 1024
        ):
            raise RuntimeError(
                "INVALID_WEEX_HTTP_RESPONSE"
            )

        payload = json.loads(
            raw.decode("utf-8")
        )

    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        TimeoutError,
        ValueError,
        UnicodeError,
        RuntimeError,
    ) as exc:

        result["status"] = "UNAVAILABLE"
        result["reason"] = (
            "WEEX_READ_FAILED_"
            + type(exc).__name__
        )

        # Never print API credentials,
        # signatures, authentication headers,
        # or private response bodies.

        print(
            "UNIT 8 WEEX READ = FAILED",
            flush=True,
        )

        return result

    result["http_success"] = True

    # Original Unit 12 expected a list.
    # Fail closed if WEEX changes that contract.

    if not isinstance(payload, list):

        result["status"] = "UNVERIFIED"
        result["reason"] = (
            "UNEXPECTED_POSITION_RESPONSE_SHAPE"
        )

        return result

    result["positions_read"] = True

    seen = {
        "LONG": [],
        "SHORT": [],
    }

    for record in payload:

        if not isinstance(record, dict):
            result["reason"] = "MALFORMED_POSITION"
            return result

        symbol = str(
            record.get("symbol", "")
        ).upper()

        if symbol != "BTCSUSDT":
            continue

        try:
            size = float(record.get("size"))
        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            result["reason"] = "INVALID_POSITION_SIZE"
            return result

        if (
            not math.isfinite(size)
            or size < 0
        ):
            result["reason"] = "INVALID_POSITION_SIZE"
            return result

        # A zero-size position does not prove
        # effective leverage for a future entry.

        if size == 0:
            continue

        side = str(
            record.get("side", "")
        ).upper()

        if side not in seen:
            result["reason"] = "INVALID_POSITION_SIDE"
            return result

        try:
            leverage = float(
                record.get("leverage")
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            result["reason"] = "INVALID_LEVERAGE"
            return result

        if (
            not math.isfinite(leverage)
            or leverage <= 0
        ):
            result["reason"] = "INVALID_LEVERAGE"
            return result

        margin_mode = str(
            record.get("marginType", "")
        ).upper()

        if margin_mode not in (
            "CROSSED",
            "ISOLATED",
        ):
            result["reason"] = "INVALID_MARGIN_MODE"
            return result

        seen[side].append({
            "leverage": leverage,
            "size": size,
            "margin_mode": margin_mode,
        })

    result["active_position_count"] = (
        len(seen["LONG"])
        + len(seen["SHORT"])
    )

    # Multiple positions may have different leverage.
    # Never select one arbitrarily.

    for side in ("LONG", "SHORT"):

        positions = seen[side]

        if not positions:
            continue

        unique_leverage = {
            p["leverage"]
            for p in positions
        }

        unique_margin_modes = {
            p["margin_mode"]
            for p in positions
        }

        if (
            len(unique_leverage) != 1
            or len(unique_margin_modes) != 1
        ):
            result["reason"] = (
                "AMBIGUOUS_" + side + "_POSITIONS"
            )
            return result

        result["leverage_by_side"][side] = (
            positions[0]["leverage"]
        )

        result["verified_by_side"][side] = True

    wanted_side = unit_8_result.get(
        "pending_direction", "NONE"
    )

    # Crucial: a position's leverage describes
    # that existing position, not necessarily
    # a new flat-position entry.

    if wanted_side in (
        "LONG",
        "SHORT",
    ) and result["verified_by_side"][wanted_side]:

        result["effective_leverage"] = (
            result["leverage_by_side"][wanted_side]
        )

        result["exchange_leverage_verified"] = True
        result["status"] = "EXISTING_POSITION_VERIFIED"
        result["reason"] = (
            "WEEX_ACTIVE_POSITION_LEVERAGE_READ"
        )

    elif result["active_position_count"] == 0:

        result["status"] = "FLAT"
        result["reason"] = (
            "NO_ACTIVE_POSITION_"
            "ENTRY_LEVERAGE_UNVERIFIED"
        )

    else:

        result["status"] = "PARTIAL"
        result["reason"] = (
            "REQUESTED_SIDE_LEVERAGE_UNAVAILABLE"
        )

    print(
        "UNIT 8 WEEX POSITION READ = SUCCESS",
        flush=True,
    )

    print(
        "UNIT 8 WEEX LONG LEVERAGE =",
        result["leverage_by_side"]["LONG"],
        flush=True,
    )

    print(
        "UNIT 8 WEEX SHORT LEVERAGE =",
        result["leverage_by_side"]["SHORT"],
        flush=True,
    )

    print(
        "UNIT 8 WEEX LEVERAGE STATUS =",
        result["status"],
        flush=True,
    )

    print(
        "UNIT 8 WEEX LEVERAGE REASON =",
        result["reason"],
        flush=True,
    )

    print(
        "UNIT 8 WEEX LEVERAGE MUTATION = NONE",
        flush=True,
    )

    print(
        "UNIT 8 WEEX ORDER SUBMISSION = NONE",
        flush=True,
    )

    return result


# ============================================================
# RUN LEVERAGE EXTENSION
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_8_WEEX_LEVERAGE = (
    fresh_unit_8_weex_leverage_read(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT,
    )
)

# Copy verification metadata into the existing
# Unit 8 result. Do not enable sizing or orders.

_u8_leverage = (
    FRESH_RECONSTRUCTION_UNIT_8_WEEX_LEVERAGE
)

FRESH_RECONSTRUCTION_UNIT_8_RESULT[
    "weex_leverage_read"
] = _u8_leverage

FRESH_RECONSTRUCTION_UNIT_8_RESULT[
    "weex_leverage_by_side"
] = dict(_u8_leverage["leverage_by_side"])

FRESH_RECONSTRUCTION_UNIT_8_RESULT[
    "weex_leverage_status"
] = _u8_leverage["status"]

FRESH_RECONSTRUCTION_UNIT_8_RESULT[
    "effective_leverage"
] = _u8_leverage["effective_leverage"]

FRESH_RECONSTRUCTION_UNIT_8_RESULT[
    "exchange_leverage_verified"
] = _u8_leverage["exchange_leverage_verified"]

# Preserve the current execution safety boundary.

assert (
    FRESH_RECONSTRUCTION_UNIT_8_RESULT[
        "execution_intent"
    ] is False
)

assert (
    FRESH_RECONSTRUCTION_UNIT_8_RESULT[
        "trade_plan_ready"
    ] is False
)

assert (
    FRESH_RECONSTRUCTION_UNIT_8_RESULT[
        "exchange_write"
    ] is False
)

print(
    "UNIT 8 ACTUAL WEEX LEVERAGE EXTENSION = COMPLETE",
    flush=True,
)

print(
    "UNIT 8 EFFECTIVE LEVERAGE =",
    _u8_leverage["effective_leverage"],
    flush=True,
)

print(
    "UNIT 8 NO ORDER / NO MUTATION = TRUE",
    flush=True,
)

# ============================================================
# END UNIT 8 WEEX LEVERAGE EXTENSION
# ZERO INDENTATION
# ============================================================

print(
    "UNIT 8 SYNTHETIC PENDING TEST = PASS",
    flush=True,
)
print(
    "UNIT 8 DIRECTION CONFLICT TEST = PASS",
    flush=True,
)
print(
    "UNIT 8 EXCHANGE LEVERAGE SAFETY = PASS",
    flush=True,
)
print(
    "UNIT 8 ISOLATED TEST = PASS",
    flush=True,
)
print(
    "UNIT 8 VERIFIED = TRUE",
    flush=True,
)
print(
    "UNITS 9-15 EXECUTION = NOT STARTED",
    flush=True,
)
print("=" * 80, flush=True)

    
# ============================================================
# START UNIT 8 WEEX LEVERAGE LIMIT DIAGNOSTIC
# ZERO INDENTATION
# PUBLIC V3 GET ONLY
# NO ORDERS - NO ACCOUNT MUTATION
# ============================================================

def fresh_unit_8_leverage_limit_diagnostic():
    import json
    import math
    import urllib.request
    import urllib.error

    result = {
        "status": "UNVERIFIED",
        "source": "WEEX_PUBLIC_RISK_LIMITS",
        "symbol": "BTCUSDT",
        "bracket_count": 0,
        "brackets": [],
        "actual_long_leverage": None,
        "actual_short_leverage": None,
        "entry_leverage_verified": False,
        "exchange_write": False,
        "reason": "NOT_REQUESTED",
    }

    url = (
        "https://api-contract.weex.com"
        "/capi/v3/market/riskLimits"
        "?symbol=BTCUSDT"
    )

    request = urllib.request.Request(
        url,
        method="GET",
        headers={"Accept": "application/json"},
    )

    class NoRedirect(
        urllib.request.HTTPRedirectHandler
    ):
        def redirect_request(
            self, req, fp, code, msg,
            headers, newurl
        ):
            return None

    try:
        opener = urllib.request.build_opener(
            NoRedirect()
        )

        with opener.open(
            request,
            timeout=12,
        ) as response:

            if (
                response.getcode() != 200
                or response.geturl() != url
            ):
                raise ValueError("UNEXPECTED_RESPONSE")

            raw = response.read(1024 * 1024 + 1)

        if not raw or len(raw) > 1024 * 1024:
            raise ValueError("INVALID_RESPONSE_SIZE")

        payload = json.loads(
            raw.decode("utf-8")
        )

        if not isinstance(payload, list):
            raise ValueError("INVALID_PAYLOAD")

        matches = [
            record
            for record in payload
            if (
                isinstance(record, dict)
                and record.get("symbol") == "BTCUSDT"
            )
        ]

        if len(matches) != 1:
            raise ValueError("SYMBOL_MATCH_FAILED")

        brackets = matches[0].get("brackets")

        if (
            not isinstance(brackets, list)
            or not brackets
        ):
            raise ValueError("NO_VALID_BRACKETS")

        for item in brackets:

            if not isinstance(item, dict):
                raise ValueError("INVALID_BRACKET")

            leverage = float(
                item.get("initialLeverage")
            )

            floor = float(
                item.get("notionalFloor")
            )

            cap = float(
                item.get("notionalCap")
            )

            if (
                not all(
                    math.isfinite(v)
                    for v in (leverage, floor, cap)
                )
                or leverage <= 0
                or floor < 0
                or cap <= floor
            ):
                raise ValueError(
                    "INVALID_BRACKET_VALUES"
                )

            result["brackets"].append({
                "notional_floor": floor,
                "notional_cap": cap,
                "leverage_limit": leverage,
            })

        result["bracket_count"] = len(
            result["brackets"]
        )

        result["status"] = "LIMITS_READ"
        result["reason"] = (
            "PUBLIC_LIMITS_ARE_NOT_"
            "ACCOUNT_LEVERAGE"
        )

    except (
        urllib.error.URLError,
        TimeoutError,
        ValueError,
        TypeError,
        OverflowError,
        UnicodeError,
    ) as exc:

        result["status"] = "UNAVAILABLE"
        result["reason"] = (
            "RISK_LIMIT_READ_FAILED_"
            + type(exc).__name__
        )

        result["brackets"] = []
        result["bracket_count"] = 0

    # Hard boundary: never use bracket leverage
    # as the actual WEEX account setting.

    assert result["actual_long_leverage"] is None
    assert result["actual_short_leverage"] is None
    assert result["entry_leverage_verified"] is False
    assert result["exchange_write"] is False

    return result


FRESH_RECONSTRUCTION_UNIT_8_RISK_LIMITS = (
    fresh_unit_8_leverage_limit_diagnostic()
)

_risk = FRESH_RECONSTRUCTION_UNIT_8_RISK_LIMITS

FRESH_RECONSTRUCTION_UNIT_8_RESULT[
    "weex_risk_limits"
] = _risk

print("=" * 80, flush=True)
print(
    "UNIT 8 RISK LIMIT STATUS =",
    _risk["status"],
    flush=True,
)
print(
    "UNIT 8 RISK LIMIT BRACKETS =",
    _risk["bracket_count"],
    flush=True,
)
print(
    "UNIT 8 FLAT ENTRY LEVERAGE VERIFIED = FALSE",
    flush=True,
)
print(
    "UNIT 8 CONFIGURED LEVERAGE SUBSTITUTION = NONE",
    flush=True,
)
print(
    "UNIT 8 RISK LIMIT EXCHANGE WRITE = NONE",
    flush=True,
)
print("=" * 80, flush=True)

# ============================================================
# END UNIT 8 WEEX LEVERAGE LIMIT DIAGNOSTIC
# ZERO INDENTATION
# ============================================================

UNIT_8_ISOLATED_TEST = False
if UNIT_8_ISOLATED_TEST:
    print(
        "UNIT 8 TEST COMPLETE - STOPPING BEFORE UNIT 9",
        flush=True,
    )
    raise SystemExit(0)


# ============================================================
# END COMPLETE UNIT 8 REPLACEMENT
# ZERO INDENTATION
# UNIT 9 CONTINUES BELOW
# ============================================================


# ============================================================
# START COMPLETE UNIT 9 REPLACEMENT
# ZERO INDENTATION
# ORIGINAL 22524 + NEW 13975 MODEL ADAPTATION
# SIGNAL CONTINUITY + EXECUTION HANDOVER
# NO DEMO ORDER - NO REAL ORDER - NO EXCHANGE WRITE
# ============================================================

import time


# ============================================================
# UNIT 9 PROCESS-LOCAL STATE
# ============================================================

FRESH_UNIT_9_STATE = {
    "signal_key": None,
    "first_seen": None,
    "last_candle_id": None,
    "confirmations": 0,
    "last_status": "IDLE",
}


def fresh_reconstruction_unit_9(
    unit_2_config,
    unit_4_analysis,
    unit_8_result,
    state=None,
    now=None,
):

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 9 START")

    # ========================================================
    # 1. INPUT VERIFICATION
    # ========================================================

    if not all(
        isinstance(item, dict)
        for item in (
            unit_2_config,
            unit_4_analysis,
            unit_8_result,
        )
    ):
        raise RuntimeError(
            "UNIT 9 INVALID INPUT CONTRACT"
        )

    config = unit_2_config
    market = unit_4_analysis
    upstream = unit_8_result

    safety = config.get("safety")

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 9 SAFETY CONFIG MISSING"
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
                "UNIT 9 UNSAFE CONFIG: " + key
            )

    for key in (
        "execution_intent",
        "trade_authorized",
        "trade_plan_ready",
        "order_payload_created",
        "exchange_write",
    ):
        if upstream.get(key) is not False:
            raise RuntimeError(
                "UNIT 9 UNSAFE UNIT 8: " + key
            )

    if (
        upstream.get("read_only") is not True
        or upstream.get("trade_plan") is not None
    ):
        raise RuntimeError(
            "UNIT 9 UPSTREAM SAFETY FAILED"
        )

    if (
        market.get("strategy_evidence_version")
        != "U4_OLD_NEW_ADAPTED_V1"
    ):
        raise RuntimeError(
            "UNIT 9 MARKET VERSION MISMATCH"
        )

    print(
        "PASS: UNIT 9 RECEIVED UNITS 2/4/8",
        flush=True,
    )

    print(
        "PASS: UNIT 9 READ ONLY SAFETY",
        flush=True,
    )

    # ========================================================
    # 2. STATE MANAGEMENT
    # ========================================================

    if state is None:
        state = FRESH_UNIT_9_STATE

    if not isinstance(state, dict):
        raise RuntimeError(
            "UNIT 9 STATE INVALID"
        )

    defaults = {
        "signal_key": None,
        "first_seen": None,
        "last_candle_id": None,
        "confirmations": 0,
        "last_status": "IDLE",
    }

    for key, value in defaults.items():
        state.setdefault(key, value)

    if now is None:
        now = time.monotonic()

    now = float(now)

    if not (
        0 <= now < float("inf")
    ):
        raise RuntimeError(
            "UNIT 9 CLOCK INVALID"
        )

    confirmations_required = 2
    signal_expiry_seconds = 120.0

    def reset_state():
        state["signal_key"] = None
        state["first_seen"] = None
        state["last_candle_id"] = None
        state["confirmations"] = 0
        state["last_status"] = "IDLE"

    # ========================================================
    # 3. DEFAULT STATUS
    # ========================================================

    upstream_status = upstream.get("status")

    if upstream_status not in (
        "IDLE",
        "PENDING",
        "BLOCKED",
    ):
        raise RuntimeError(
            "UNIT 9 INVALID UNIT 8 STATUS"
        )

    status = "IDLE"
    reason = "NO_PENDING_SIGNAL"

    mode = "NONE"
    direction = "NONE"
    candle_id = None

    duplicate_candle = False
    signal_changed = False
    signal_expired = False
    continuity_verified = False

    # ========================================================
    # 4. CANDIDATE HANDLING
    # ========================================================

    if upstream_status != "PENDING":

        reset_state()

        if upstream_status == "BLOCKED":
            status = "BLOCKED"
            reason = (
                "UPSTREAM_SIGNAL_BLOCKED:"
                + str(
                    upstream.get(
                        "reason", "UNKNOWN"
                    )
                )
            )

    else:

        mode = upstream.get("pending_mode")
        direction = upstream.get(
            "pending_direction"
        )

        if (
            mode not in ("BREAKOUT", "STRUCTURE")
            or direction not in ("LONG", "SHORT")
        ):
            raise RuntimeError(
                "UNIT 9 INVALID PENDING SIGNAL"
            )

        if (
            upstream.get("candidate_preserved")
            is not True
            or upstream.get(
                "signal_direction_match"
            ) is not True
        ):
            status = "BLOCKED"
            reason = "CANDIDATE_IDENTITY_INVALID"
            reset_state()

        elif (
            market.get("candle_data_fresh")
            is not True
        ):
            status = "BLOCKED"
            reason = "STALE_CANDLE_DATA"
            reset_state()

        elif (
            market.get("direction_evidence")
            != direction
        ):
            status = "BLOCKED"
            reason = "MARKET_DIRECTION_CHANGED"
            reset_state()

        else:

            symbol = market.get("symbol")

            candles = market.get(
                "recent_closed_klines"
            )

            if (
                not isinstance(symbol, str)
                or not symbol
                or not isinstance(candles, list)
                or not candles
                or not isinstance(
                    candles[-1], dict
                )
            ):
                status = "BLOCKED"
                reason = "CLOSED_CANDLE_DATA_MISSING"
                reset_state()

            else:

                last_candle = candles[-1]
                raw_id = None

                for name in (
                    "timestamp",
                    "open_time",
                    "openTime",
                    "start_time",
                    "startTime",
                    "time",
                    "ts",
                ):
                    if name in last_candle:
                        raw_id = last_candle[name]
                        break

                try:
                    if (
                        raw_id is None
                        or isinstance(raw_id, bool)
                    ):
                        raise ValueError(
                            "MISSING_CANDLE_ID"
                        )

                    candle_id = int(raw_id)

                    if candle_id <= 0:
                        raise ValueError(
                            "BAD_CANDLE_ID"
                        )

                except (
                    TypeError,
                    ValueError,
                    OverflowError,
                ):
                    candle_id = None
                    status = "BLOCKED"
                    reason = "INVALID_CLOSED_CANDLE_ID"
                    reset_state()

                if candle_id is not None:

                    signal_key = (
                        symbol,
                        mode,
                        direction,
                    )

                    previous_key = state[
                        "signal_key"
                    ]

                    previous_candle = state[
                        "last_candle_id"
                    ]

                    # ----------------------------------------
                    # SIGNAL CHANGE
                    # ----------------------------------------

                    if (
                        previous_key is not None
                        and previous_key != signal_key
                    ):
                        signal_changed = True
                        reset_state()

                    # ----------------------------------------
                    # EXPIRY
                    # ----------------------------------------

                    first_seen = state[
                        "first_seen"
                    ]

                    if first_seen is not None:

                        if (
                            now - first_seen
                            > signal_expiry_seconds
                        ):
                            signal_expired = True
                            reset_state()

                    previous_candle = state[
                        "last_candle_id"
                    ]

                    # ----------------------------------------
                    # FIRST DISTINCT CLOSED CANDLE
                    # ----------------------------------------

                    if state["signal_key"] is None:

                        state["signal_key"] = signal_key
                        state["first_seen"] = now
                        state["last_candle_id"] = candle_id
                        state["confirmations"] = 1

                        status = "PENDING"

                        if signal_changed:
                            reason = (
                                "SIGNAL_CHANGED_RESET"
                            )
                        elif signal_expired:
                            reason = (
                                "SIGNAL_EXPIRED_RESET"
                            )
                        else:
                            reason = (
                                "FIRST_CLOSED_CANDLE"
                            )

                    # ----------------------------------------
                    # DUPLICATE CANDLE
                    # ----------------------------------------

                    elif candle_id == previous_candle:

                        duplicate_candle = True

                        status = "PENDING"

                        reason = (
                            "DUPLICATE_CLOSED_CANDLE"
                        )

                    # ----------------------------------------
                    # CANDLE TIME REGRESSION
                    # ----------------------------------------

                    elif candle_id < previous_candle:

                        reset_state()
                        status = "BLOCKED"

                        reason = (
                            "CLOSED_CANDLE_TIME_REGRESSION"
                        )

                    # ----------------------------------------
                    # NEXT DISTINCT CANDLE
                    # ----------------------------------------

                    else:

                        state[
                            "last_candle_id"
                        ] = candle_id

                        state["confirmations"] = min(
                            state["confirmations"] + 1,
                            confirmations_required,
                        )

                        status = "PENDING"

                        reason = (
                            "NEW_CLOSED_CANDLE"
                        )

                    # ----------------------------------------
                    # CONTINUITY QUALIFIED
                    # ----------------------------------------

                    if (
                        status == "PENDING"
                        and state["confirmations"]
                        >= confirmations_required
                    ):

                        continuity_verified = True

                        status = "CONFIRMED"

                        reason = (
                            "DISTINCT_CLOSED_CANDLE_"
                            "CONTINUITY_VERIFIED"
                        )

                    state["last_status"] = status

    # ========================================================
    # 5. EXCHANGE-READINESS HANDOVER
    # ========================================================

    # The older model can forward a READY execution
    # candidate after verified trade-plan checks.
    #
    # The current Unit 8 does not yet produce a
    # verified entry leverage, balance-based sizing,
    # position-flat check or executable trade plan.
    #
    # Therefore this unit must NOT synthesize READY.

    exchange_leverage_verified = (
        upstream.get(
            "exchange_leverage_verified"
        ) is True
    )

    effective_leverage = upstream.get(
        "effective_leverage"
    )

    balance_verified = (
        upstream.get("balance_verified")
        is True
    )

    position_flat_verified = (
        upstream.get(
            "position_flat_verified"
        ) is True
    )

    pending_orders_verified = (
        upstream.get(
            "pending_orders_checked"
        ) is True
    )

    duplicate_order_absence_verified = (
        upstream.get(
            "duplicate_order_absence_verified"
        ) is True
    )

    # A position-specific leverage reading cannot
    # automatically authorize a new flat entry.

    entry_leverage_verified = (
        upstream.get(
            "entry_leverage_verified"
        ) is True
    )

    if not entry_leverage_verified:
        exchange_leverage_verified = False
        effective_leverage = None

    trade_plan_ready = False
    trade_plan = None
    execution_ready = False
    execution_candidate = None
    execution_intent = False
    trade_authorized = False

    # Remain read-only even when continuity passes.
    # READY must be implemented only after the
    # upstream plan contract has been verified.

    reentry_authorized = False
    quantity_calculated = False
    order_payload_created = False
    demo_order_submitted = False
    real_order_submitted = False
    exchange_write = False

    if status == "CONFIRMED":
        skip_reason = (
            "CONTINUITY_CONFIRMED_"
            "AWAITING_VERIFIED_TRADE_PLAN"
        )
    else:
        skip_reason = reason

    # ========================================================
    # 6. ORIGINAL UNIT 9 + NEW UNIT 9 OUTPUT
    # ========================================================

    result = {

        "status": status,
        "reason": reason,
        "skip_reason": skip_reason,

        "upstream_status": upstream_status,

        "active_mode": mode,
        "mode": mode,
        "direction": direction,

        "signal_qualified":
            continuity_verified,

        "closed_candle_id": candle_id,

        "signal_key": (
            list(state["signal_key"])
            if state["signal_key"] is not None
            else None
        ),

        "confirmations":
            state["confirmations"],

        "confirmations_required":
            confirmations_required,

        "signal_expiry_seconds":
            signal_expiry_seconds,

        "duplicate_candle":
            duplicate_candle,

        "signal_changed":
            signal_changed,

        "signal_expired":
            signal_expired,

        "continuity_verified":
            continuity_verified,

        "state_persistent_across_restart":
            False,

        "exchange_leverage_verified":
            exchange_leverage_verified,

        "effective_leverage":
            effective_leverage,

        "entry_leverage_verified":
            entry_leverage_verified,

        "balance_verified":
            balance_verified,

        "position_flat_verified":
            position_flat_verified,

        "pending_orders_verified":
            pending_orders_verified,

        "duplicate_order_absence_verified":
            duplicate_order_absence_verified,

        "reentry_authorized":
            reentry_authorized,

        # Original execution candidate interface.
        "trade_plan_ready":
            trade_plan_ready,

        "trade_plan":
            trade_plan,

        "execution_ready":
            execution_ready,

        "execution_candidate":
            execution_candidate,

        "execution_intent":
            execution_intent,

        "trade_authorized":
            trade_authorized,

        # Hard exchange safety boundary.
        "quantity_calculated":
            quantity_calculated,

        "order_payload_created":
            order_payload_created,

        "demo_order_submitted":
            demo_order_submitted,

        "real_order_submitted":
            real_order_submitted,

        "exchange_write":
            exchange_write,

        "read_only": True,
    }

    # ========================================================
    # 7. FINAL SAFETY VALIDATION
    # ========================================================

    for key in (
        "trade_plan_ready",
        "execution_ready",
        "execution_intent",
        "trade_authorized",
        "reentry_authorized",
        "quantity_calculated",
        "order_payload_created",
        "demo_order_submitted",
        "real_order_submitted",
        "exchange_write",
    ):
        if result[key] is not False:
            raise RuntimeError(
                "UNIT 9 SAFETY FAILURE: " + key
            )

    if (
        result["trade_plan"] is not None
        or result["execution_candidate"]
        is not None
    ):
        raise RuntimeError(
            "UNIT 9 PREMATURE TRADE PLAN"
        )

    # ========================================================
    # 8. RENDER DIAGNOSTICS
    # ========================================================

    print("-" * 80, flush=True)

    for label, value in (
        ("STATUS", status),
        ("REASON", reason),
        ("MODE", mode),
        ("DIRECTION", direction),
        ("CLOSED CANDLE ID", candle_id),
        (
            "CONFIRMATIONS",
            state["confirmations"],
        ),
        (
            "REQUIRED",
            confirmations_required,
        ),
        (
            "DUPLICATE CANDLE",
            duplicate_candle,
        ),
        (
            "SIGNAL CHANGED",
            signal_changed,
        ),
        (
            "SIGNAL EXPIRED",
            signal_expired,
        ),
        (
            "CONTINUITY VERIFIED",
            continuity_verified,
        ),
        (
            "EXCHANGE LEVERAGE VERIFIED",
            exchange_leverage_verified,
        ),
        (
            "POSITION FLAT VERIFIED",
            position_flat_verified,
        ),
        (
            "REENTRY AUTHORIZED",
            reentry_authorized,
        ),
        (
            "EXECUTION READY",
            execution_ready,
        ),
        (
            "EXECUTION INTENT",
            execution_intent,
        ),
        (
            "TRADE AUTHORIZED",
            trade_authorized,
        ),
        (
            "EXCHANGE WRITE",
            exchange_write,
        ),
    ):
        print(
            "UNIT 9 " + label + " =",
            value,
            flush=True,
        )

    log(
        "FRESH RECONSTRUCTION UNIT 9 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# RUN UNIT 9 - ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_9_RESULT = (
    fresh_reconstruction_unit_9(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT,
    )
)

# Preserve original execution-candidate naming.
FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE_UNIT_9 = (
    FRESH_RECONSTRUCTION_UNIT_9_RESULT
)


# ============================================================
# UNIT 9 ISOLATED AND SYNTHETIC TESTS
# ============================================================

UNIT_9_ISOLATED_TEST = True

_u9 = FRESH_RECONSTRUCTION_UNIT_9_RESULT

if not isinstance(_u9, dict):
    raise RuntimeError(
        "UNIT 9 RESULT INVALID"
    )

if (
    _u9["read_only"] is not True
    or _u9["execution_intent"] is not False
    or _u9["execution_ready"] is not False
    or _u9["exchange_write"] is not False
):
    raise RuntimeError(
        "UNIT 9 LIVE SAFETY TEST FAILED"
    )

print(
    "PASS: UNIT 9 LIVE READ ONLY HANDOVER",
    flush=True,
)

# ============================================================
# SYNTHETIC DISTINCT-CANDLE CONTINUITY TEST
# ============================================================

_test_state = {
    "signal_key": None,
    "first_seen": None,
    "last_candle_id": None,
    "confirmations": 0,
    "last_status": "IDLE",
}

_test_market = dict(
    FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
)

_test_market.update({
    "symbol": "BTCUSDT",
    "candle_data_fresh": True,
    "direction_evidence": "LONG",
    "recent_closed_klines": [
        {"timestamp": 1792630000000}
    ],
})

_test_u8 = dict(
    FRESH_RECONSTRUCTION_UNIT_8_RESULT
)

_test_u8.update({
    "status": "PENDING",
    "reason": "SYNTHETIC_PENDING",
    "pending_mode": "BREAKOUT",
    "pending_direction": "LONG",
    "candidate_preserved": True,
    "signal_direction_match": True,
})

_test_1 = fresh_reconstruction_unit_9(
    FRESH_RECONSTRUCTION_CONFIG,
    _test_market,
    _test_u8,
    state=_test_state,
    now=1000.0,
)

if (
    _test_1["status"] != "PENDING"
    or _test_1["confirmations"] != 1
):
    raise RuntimeError(
        "UNIT 9 FIRST CANDLE TEST FAILED"
    )

# Same candle must not count twice.

_test_duplicate = fresh_reconstruction_unit_9(
    FRESH_RECONSTRUCTION_CONFIG,
    _test_market,
    _test_u8,
    state=_test_state,
    now=1001.0,
)

if (
    _test_duplicate["duplicate_candle"]
    is not True
    or _test_duplicate["confirmations"] != 1
):
    raise RuntimeError(
        "UNIT 9 DUPLICATE CANDLE TEST FAILED"
    )

# Distinct next closed candle.

_test_market_2 = dict(_test_market)

_test_market_2["recent_closed_klines"] = [
    {"timestamp": 1792630060000}
]

_test_2 = fresh_reconstruction_unit_9(
    FRESH_RECONSTRUCTION_CONFIG,
    _test_market_2,
    _test_u8,
    state=_test_state,
    now=1060.0,
)

if (
    _test_2["status"] != "CONFIRMED"
    or _test_2["continuity_verified"]
    is not True
    or _test_2["confirmations"] != 2
    or _test_2["execution_ready"] is not False
    or _test_2["execution_intent"] is not False
):
    raise RuntimeError(
        "UNIT 9 CONTINUITY TEST FAILED"
    )

print(
    "PASS: UNIT 9 DISTINCT-CANDLE CONTINUITY",
    flush=True,
)

# ============================================================
# SYNTHETIC EXPIRY TEST
# ============================================================

_test_market_3 = dict(_test_market)

_test_market_3["recent_closed_klines"] = [
    {"timestamp": 1792630120000}
]

_test_expired = fresh_reconstruction_unit_9(
    FRESH_RECONSTRUCTION_CONFIG,
    _test_market_3,
    _test_u8,
    state=_test_state,
    now=1201.0,
)

if (
    _test_expired["signal_expired"] is not True
    or _test_expired["confirmations"] != 1
    or _test_expired["execution_ready"] is not False
):
    raise RuntimeError(
        "UNIT 9 EXPIRY TEST FAILED"
    )

print(
    "PASS: UNIT 9 120 SECOND EXPIRY",
    flush=True,
)

# ============================================================
# FINAL ISOLATED TEST
# ============================================================

print("=" * 80, flush=True)

print(
    "UNIT 9 ISOLATED TEST = PASS",
    flush=True,
)

print(
    "UNIT 9 VERIFIED = TRUE",
    flush=True,
)

print(
    "UNIT 9 CONTINUITY TEST = PASS",
    flush=True,
)

print(
    "UNIT 9 DUPLICATE PREVENTION = PASS",
    flush=True,
)

print(
    "UNIT 9 EXPIRY TEST = PASS",
    flush=True,
)

print(
    "UNIT 9 EXECUTION HANDOVER FIELDS = PRESENT",
    flush=True,
)

print(
    "UNIT 9 DEMO ORDER = NONE",
    flush=True,
)

print(
    "UNIT 9 REAL ORDER = NONE",
    flush=True,
)

print(
    "UNIT 9 EXCHANGE WRITE = NONE",
    flush=True,
)

print(
    "UNITS 10-15 EXECUTION = NOT STARTED",
    flush=True,
)

print("=" * 80, flush=True)

if UNIT_9_ISOLATED_TEST:
    print(
        "UNIT 9 TEST COMPLETE - STOPPING BEFORE UNIT 10",
        flush=True,
    )
    raise SystemExit(0)


# ============================================================
# END COMPLETE UNIT 9 REPLACEMENT
# ZERO INDENTATION
# UNIT 10 CONTINUES BELOW
# ============================================================
