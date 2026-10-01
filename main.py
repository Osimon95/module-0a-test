# ============================================================
# FRESH WEEX BOT RECONSTRUCTION
# UNIT 1 — CLEAN RUNTIME FOUNDATION
#
# FILE: main.py
#
# PURPOSE:
# Prove that the fresh main.py starts and runs correctly
# before adding ANY trading functionality.
#
# SAFETY:
# - NO WEEX CONNECTION
# - NO HTTP REQUEST
# - NO DEMO ORDER
# - NO REAL ORDER
# - NO EXCHANGE WRITE
# - NO POSITION CHANGE
# - NO EXTERNAL DEPENDENCIES
# ============================================================

from datetime import datetime, timezone


def log(message):
    timestamp = datetime.now(timezone.utc).isoformat()
    print(
        f"{timestamp} {message}",
        flush=True,
    )


def reconstruction_unit_1():
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

    log(
        "PASS: MAIN.PY STARTED SUCCESSFULLY"
    )

    log(
        "PASS: PYTHON STANDARD LIBRARY ONLY"
    )

    log(
        "PASS: ZERO WEEX CONNECTION"
    )

    log(
        "PASS: ZERO HTTP REQUEST"
    )

    log(
        "PASS: ZERO DEMO ORDER"
    )

    log(
        "PASS: ZERO REAL ORDER"
    )

    log(
        "PASS: ZERO EXCHANGE WRITE"
    )

    print(
        "-" * 80,
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 1 COMPLETE"
    )

    print(
        "=" * 80,
        flush=True,
    )


if __name__ == "__main__":
    reconstruction_unit_1()

# ============================================================
# FRESH RECONSTRUCTION UNIT 2
# CONFIGURATION + SAFETY CONTRACT
#
# PURPOSE:
# Establish the bot's core configuration in one controlled,
# validated location before any exchange connectivity exists.
#
# IMPORTANT:
# - STANDARD LIBRARY ONLY
# - ZERO WEEX CONNECTION
# - ZERO HTTP REQUEST
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE WRITE
# - ZERO POSITION MUTATION
# - ZERO LEVERAGE MUTATION
# - ZERO MARGIN MODE MUTATION
# ============================================================


def fresh_reconstruction_unit_2():

    print(
        "=" * 80,
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 2 START"
    )

    print(
        "-" * 80,
        flush=True,
    )

    # --------------------------------------------------------
    # 1. TRADING INSTRUMENT
    # --------------------------------------------------------

    symbol = "BTCSUSDT"

    # --------------------------------------------------------
    # 2. EXECUTION ENVIRONMENT
    #
    # We are rebuilding toward DEMO execution first.
    # Actual submission is NOT enabled in Unit 2.
    # --------------------------------------------------------

    execution_environment = "DEMO"

    # --------------------------------------------------------
    # 3. HARD SAFETY FLAGS
    #
    # These flags describe what the current reconstruction
    # is permitted to do.
    #
    # They are deliberately FALSE at this stage.
    # --------------------------------------------------------

    weex_connection_enabled = False

    http_requests_enabled = False

    demo_order_submission_enabled = False

    real_order_submission_enabled = False

    exchange_mutation_enabled = False

    # --------------------------------------------------------
    # 4. ACCOUNT MUTATION SAFETY
    # --------------------------------------------------------

    leverage_mutation_enabled = False

    margin_mode_mutation_enabled = False

    position_mode_mutation_enabled = False

    # --------------------------------------------------------
    # 5. STRATEGY CONSTANTS
    #
    # These preserve the verified strategy requirements
    # without copying the old architecture.
    # --------------------------------------------------------

    leverage_target = 100

    initial_margin_percent = 5.0

    backup_margin_percent = 5.0

    backup_buffer_percent = 0.30

    max_backups = 3

    exposure_cap_percent = 35.0

    # --------------------------------------------------------
    # 6. TAKE-PROFIT ALLOCATION
    # --------------------------------------------------------

    tp1_allocation_percent = 25.0

    tp2_allocation_percent = 25.0

    tp3_allocation_percent = 50.0

    tp3_trailing_distance_percent = 0.20

    # --------------------------------------------------------
    # 7. SIGNAL CONTROL
    # --------------------------------------------------------

    signal_expiry_seconds = 120

    loss_cooldown_seconds = 300

    one_direction_only = True

    anti_duplicate_orders = True

    active_trade_mode_lock = True

    exclusive_mode = True

    mode_confirmations_required = 3

    # --------------------------------------------------------
    # 8. MARKET PRECISION
    #
    # These are configuration values only.
    # Nothing is submitted to WEEX.
    # --------------------------------------------------------

    quantity_step = 0.0001

    minimum_quantity = 0.0001

    price_step = 0.1

    # --------------------------------------------------------
    # 9. CONFIGURATION OBJECT
    #
    # Later units will receive validated configuration rather
    # than relying on scattered global constants.
    # --------------------------------------------------------

    config = {

        "symbol":
            symbol,

        "execution_environment":
            execution_environment,

        "safety": {

            "weex_connection_enabled":
                weex_connection_enabled,

            "http_requests_enabled":
                http_requests_enabled,

            "demo_order_submission_enabled":
                demo_order_submission_enabled,

            "real_order_submission_enabled":
                real_order_submission_enabled,

            "exchange_mutation_enabled":
                exchange_mutation_enabled,

            "leverage_mutation_enabled":
                leverage_mutation_enabled,

            "margin_mode_mutation_enabled":
                margin_mode_mutation_enabled,

            "position_mode_mutation_enabled":
                position_mode_mutation_enabled,
        },

        "strategy": {

            "leverage_target":
                leverage_target,

            "initial_margin_percent":
                initial_margin_percent,

            "backup_margin_percent":
                backup_margin_percent,

            "backup_buffer_percent":
                backup_buffer_percent,

            "max_backups":
                max_backups,

            "exposure_cap_percent":
                exposure_cap_percent,

            "tp1_allocation_percent":
                tp1_allocation_percent,

            "tp2_allocation_percent":
                tp2_allocation_percent,

            "tp3_allocation_percent":
                tp3_allocation_percent,

            "tp3_trailing_distance_percent":
                tp3_trailing_distance_percent,

            "signal_expiry_seconds":
                signal_expiry_seconds,

            "loss_cooldown_seconds":
                loss_cooldown_seconds,

            "one_direction_only":
                one_direction_only,

            "anti_duplicate_orders":
                anti_duplicate_orders,

            "active_trade_mode_lock":
                active_trade_mode_lock,

            "exclusive_mode":
                exclusive_mode,

            "mode_confirmations_required":
                mode_confirmations_required,
        },

        "market_precision": {

            "quantity_step":
                quantity_step,

            "minimum_quantity":
                minimum_quantity,

            "price_step":
                price_step,
        },
    }

    # --------------------------------------------------------
    # 10. VALIDATION
    # --------------------------------------------------------

    errors = []

    if config["symbol"] != "BTCSUSDT":

        errors.append(
            "INVALID_SYMBOL"
        )

    if config["execution_environment"] != "DEMO":

        errors.append(
            "INVALID_EXECUTION_ENVIRONMENT"
        )

    if config["strategy"]["leverage_target"] <= 0:

        errors.append(
            "INVALID_LEVERAGE_TARGET"
        )

    if not (
        0
        <
        config["strategy"]["initial_margin_percent"]
        <=
        100
    ):

        errors.append(
            "INVALID_INITIAL_MARGIN_PERCENT"
        )

    if not (
        0
        <
        config["strategy"]["backup_margin_percent"]
        <=
        100
    ):

        errors.append(
            "INVALID_BACKUP_MARGIN_PERCENT"
        )

    if config["strategy"]["max_backups"] != 3:

        errors.append(
            "INVALID_MAX_BACKUPS"
        )

    if not (
        0
        <
        config["strategy"]["exposure_cap_percent"]
        <=
        100
    ):

        errors.append(
            "INVALID_EXPOSURE_CAP"
        )

    tp_total = (
        config["strategy"]["tp1_allocation_percent"]
        +
        config["strategy"]["tp2_allocation_percent"]
        +
        config["strategy"]["tp3_allocation_percent"]
    )

    if abs(
        tp_total - 100.0
    ) > 0.000001:

        errors.append(
            "INVALID_TP_ALLOCATION_TOTAL"
        )

    if config["market_precision"]["quantity_step"] <= 0:

        errors.append(
            "INVALID_QUANTITY_STEP"
        )

    if config["market_precision"]["minimum_quantity"] <= 0:

        errors.append(
            "INVALID_MINIMUM_QUANTITY"
        )

    if config["market_precision"]["price_step"] <= 0:

        errors.append(
            "INVALID_PRICE_STEP"
        )

    # --------------------------------------------------------
    # 11. SAFETY VALIDATION
    #
    # Unit 2 MUST NOT permit any external write capability.
    # --------------------------------------------------------

    forbidden_enabled_flags = []

    for (
        safety_name,
        safety_value,
    ) in config["safety"].items():

        if safety_value is True:

            forbidden_enabled_flags.append(
                safety_name
            )

    if forbidden_enabled_flags:

        errors.append(
            "UNSAFE_CAPABILITY_ENABLED"
        )

    # --------------------------------------------------------
    # 12. RESULT
    # --------------------------------------------------------

    if errors:

        print(
            "UNIT 2 VALIDATION ERRORS =",
            errors,
            flush=True,
        )

        raise RuntimeError(
            "FRESH RECONSTRUCTION UNIT 2 FAILED"
        )

    print(
        "PASS: UNIT 2 CONFIGURATION CREATED",
        flush=True,
    )

    print(
        "PASS: SYMBOL =",
        config["symbol"],
        flush=True,
    )

    print(
        "PASS: EXECUTION ENVIRONMENT =",
        config["execution_environment"],
        flush=True,
    )

    print(
        "PASS: LEVERAGE TARGET =",
        config["strategy"]["leverage_target"],
        flush=True,
    )

    print(
        "PASS: INITIAL MARGIN % =",
        config["strategy"]["initial_margin_percent"],
        flush=True,
    )

    print(
        "PASS: BACKUP MARGIN % =",
        config["strategy"]["backup_margin_percent"],
        flush=True,
    )

    print(
        "PASS: BACKUP BUFFER % =",
        config["strategy"]["backup_buffer_percent"],
        flush=True,
    )

    print(
        "PASS: MAX BACKUPS =",
        config["strategy"]["max_backups"],
        flush=True,
    )

    print(
        "PASS: EXPOSURE CAP % =",
        config["strategy"]["exposure_cap_percent"],
        flush=True,
    )

    print(
        "PASS: TP ALLOCATION =",
        tp_total,
        "%",
        flush=True,
    )

    print(
        "PASS: ANTI-DUPLICATE ORDERS =",
        config["strategy"]["anti_duplicate_orders"],
        flush=True,
    )

    print(
        "PASS: ONE DIRECTION ONLY =",
        config["strategy"]["one_direction_only"],
        flush=True,
    )

    print(
        "PASS: ALL EXTERNAL CAPABILITIES DISABLED",
        flush=True,
    )

    print(
        "ZERO WEEX CONNECTION = TRUE",
        flush=True,
    )

    print(
        "ZERO HTTP REQUEST = TRUE",
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
        "-" * 80,
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 2 RESULT = PASS"
    )

    print(
        "=" * 80,
        flush=True,
    )

    return config


# ============================================================
# RUN FRESH RECONSTRUCTION UNIT 2
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
    )
