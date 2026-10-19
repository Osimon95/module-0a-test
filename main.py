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
# WEEX RECONSTRUCTION
# UNIT 2 INDEPENDENT VERIFICATION
# ZERO INDENTATION START
#
# READS UNIT 2 DIRECTLY FROM main.py
# DOES NOT EXECUTE THE FULL main.py
# DOES NOT CONNECT TO WEEX
# DOES NOT SUBMIT ORDERS
# ============================================================

import ast
from pathlib import Path
from datetime import datetime, timezone


def log(message):
    timestamp = datetime.now(
        timezone.utc
    ).isoformat()
    print(timestamp, message, flush=True)


def verify(condition, label):
    if not condition:
        print("FAIL:", label, flush=True)
        raise RuntimeError(label)

    print("PASS:", label, flush=True)


def load_actual_unit_2():

    source_path = Path("main.py")

    verify(
        source_path.is_file(),
        "MAIN.PY SOURCE AVAILABLE"
    )

    source = source_path.read_text(
        encoding="utf-8"
    )

    start_marker = (
        "def fresh_reconstruction_unit_2():"
    )

    verify(
        start_marker in source,
        "ORIGINAL UNIT 2 FUNCTION FOUND"
    )

    start = source.index(start_marker)

    # Find the end of Unit 2's top-level function.
    remaining = source[start:]
    lines = remaining.splitlines(keepends=True)
    selected = []

    for index, line in enumerate(lines):
        if index > 0:
            if line.strip() and not line[0].isspace():
                if not line.lstrip().startswith("#"):
                    break

        selected.append(line)

    unit_source = "".join(selected)
    tree = ast.parse(unit_source)

    verify(
        len(tree.body) == 1
        and isinstance(
            tree.body[0],
            ast.FunctionDef
        )
        and tree.body[0].name
        == "fresh_reconstruction_unit_2",
        "UNIT 2 FUNCTION ISOLATED"
    )

    # Guard against exchange operations.
    forbidden_names = {
        "urlopen",
        "Request",
        "HTTPConnection",
        "HTTPSConnection",
        "socket",
        "requests",
        "httpx",
        "subprocess",
        "os",
        "eval",
        "exec",
        "open",
        "__import__",
        "getattr",
        "setattr",
        "globals",
        "locals",
    }

    for node in ast.walk(tree):
        if isinstance(
            node,
            (ast.Import, ast.ImportFrom)
        ):
            raise RuntimeError(
                "UNIT 2 TEST BLOCKED: IMPORT DETECTED"
            )

        if isinstance(node, ast.Name):
            if node.id in forbidden_names:
                raise RuntimeError(
                    "UNIT 2 TEST BLOCKED: "
                    + node.id
                )

        if isinstance(node, ast.Attribute):
            if node.attr in forbidden_names:
                raise RuntimeError(
                    "UNIT 2 TEST BLOCKED: "
                    + node.attr
                )

    print(
        "PASS: UNIT 2 BASIC SOURCE SAFETY CHECK",
        flush=True
    )

    namespace = {
        "__builtins__": {
            "print": print,
            "len": len,
            "sum": sum,
            "abs": abs,
            "any": any,
            "all": all,
            "range": range,
            "isinstance": isinstance,
            "dict": dict,
            "tuple": tuple,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "RuntimeError": RuntimeError,
            "AssertionError": AssertionError,
        },
        "log": log,
        "FRESH_RECONSTRUCTION_UNIT_1_READY": True,
    }

    exec(
        compile(tree, "unit2_isolated", "exec"),
        namespace
    )

    return namespace[
        "fresh_reconstruction_unit_2"
    ]()


def test_unit_2():

    print("=" * 70, flush=True)
    log("INDEPENDENT UNIT 2 TEST START")
    print("=" * 70, flush=True)

    config = load_actual_unit_2()

    verify(
        isinstance(config, dict),
        "UNIT 2 RETURNS CONFIGURATION"
    )

    exchange = config["exchange"]
    strategy = config["strategy"]
    safety = config["safety"]
    precision = config["market_precision"]

    verify(
        exchange["name"] == "WEEX"
        and exchange["api_version"] == "V3",
        "WEEX V3 CONFIGURATION"
    )

    verify(
        exchange["market_symbol"] == "BTCUSDT"
        and exchange["demo_order_symbol"]
        == "BTCSUSDT",
        "MARKET AND DEMO SYMBOLS"
    )

    verify(
        config["execution_environment"]
        == "DEMO",
        "DEMO ENVIRONMENT"
    )

    verify(
        strategy["leverage_target"] == 100,
        "LEVERAGE TARGET 100X"
    )

    verify(
        strategy["initial_fixed_usdt"] == 0.50
        and strategy["initial_margin_percent"]
        == 5.0,
        "INITIAL ENTRY CONFIGURATION"
    )

    verify(
        strategy["max_backups"] == 5
        and tuple(
            strategy["backup_multipliers"]
        ) == (1.0, 1.5, 2.0, 2.5, 3.0),
        "FIVE BACKUP MULTIPLIERS"
    )

    verify(
        strategy["exposure_cap_percent"]
        == 35.0,
        "MAXIMUM EXPOSURE 35%"
    )

    verify(
        (
            strategy["tp1_allocation_percent"],
            strategy["tp2_allocation_percent"],
            strategy["tp3_allocation_percent"],
        ) == (10.0, 20.0, 70.0),
        "TP ALLOCATION 10/20/70"
    )

    verify(
        strategy["tp1_net_roi_floor_percent"]
        == 5.0
        and strategy["tp2_net_roi_floor_percent"]
        == 10.0,
        "TP NET ROI FLOORS"
    )

    verify(
        tuple(strategy["mode_priority"])
        == ("BREAKOUT", "STRUCTURE", "SCALP"),
        "MODE PRIORITY"
    )

    verify(
        strategy["direction_votes_required"] == 2
        and strategy["direction_votes_total"] == 3,
        "DIRECTION CONFIRMATION 2/3"
    )

    verify(
        strategy["scalp_price_weight_percent"]
        == 50.0,
        "SCALP PRICE WEIGHT 50%"
    )

    verify(
        strategy["scalp_fee_aware_enabled"]
        is True
        and strategy[
            "scalp_require_positive_net_profit"
        ] is True,
        "FEE AWARE SCALPING CONFIGURATION"
    )

    verify(
        strategy["continuous_entry_scan_enabled"]
        is True
        and strategy["flat_position_reentry_enabled"]
        is True,
        "CONTINUOUS SCAN AND REENTRY CONFIGURED"
    )

    verify(
        strategy["arbitration_before_scalp"]
        is True
        and strategy[
            "developing_candidate_protection"
        ] is True,
        "HIGHER MODE CANDIDATE PROTECTION"
    )

    verify(
        strategy["progressive_backup_funding"]
        is True
        and strategy[
            "full_ladder_reservation_required"
        ] is False,
        "PROGRESSIVE BACKUP FUNDING"
    )

    verify(
        precision["quantity_step"] == 0.0001
        and precision["minimum_quantity"]
        == 0.0001
        and precision["price_step"] == 0.1,
        "MARKET PRECISION CONFIGURATION"
    )

    forbidden_flags = (
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

    verify(
        all(
            safety.get(flag) is False
            for flag in forbidden_flags
        ),
        "READ ONLY CONFIGURATION FLAGS"
    )

    if (
        safety.get("demo_account_balance_read_enabled")
        is True
        and safety.get("account_access_enabled")
        is False
    ):
        print(
            "WARNING: DEMO BALANCE READ CONFIGURED "
            "BUT ACCOUNT ACCESS DISABLED",
            flush=True
        )

    print("=" * 70, flush=True)
    print(
        "FINAL VERDICT: UNIT 2 CONFIGURATION VERIFIED",
        flush=True
    )
    print(
        "EXCHANGE REQUESTS BY TEST = NONE",
        flush=True
    )
    print(
        "DEMO ORDERS BY TEST = NONE",
        flush=True
    )
    print(
        "REAL ORDERS BY TEST = NONE",
        flush=True
    )
    print(
        "NEXT UNIT AUTHORIZED FOR TESTING = UNIT 3",
        flush=True
    )
    print("=" * 70, flush=True)


if __name__ == "__main__":
    test_unit_2()

# ============================================================
# END UNIT 2 INDEPENDENT TEST
# ZERO INDENTATION
# ============================================================
