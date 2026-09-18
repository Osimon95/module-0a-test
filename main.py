#!/usr/bin/env python3
"""
WRITE.PY R1.1
R36F.15.10.5 -> PRODUCTION WRITER VALIDATOR BRIDGE
ZERO PRODUCTION WRITE

Purpose
-------
1. Accept an immutable instruction directly from main.py.
2. Do NOT require WRITE_R1_INSTRUCTION_JSON for bridge operation.
3. Validate symbol, direction, entry, quantity, TP1, TP2, TP3 policy and SL.
4. Validate WEEX price and quantity steps.
5. Validate LONG/SHORT price ordering.
6. Select an exactly representable TP allocation:
      preferred 20/20/60
      adjusted 25/25/50
7. Construct the production ENTRY payload for inspection only.
8. Hash the instruction and payload deterministically.
9. Journal successful validation.
10. Detect replay.
11. NEVER transmit a production order.

R1.1 DOES NOT SEND AN ORDER.
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN


STAGE = "WRITE.PY-R1.1"

SYMBOL = "BTCUSDT"

PRICE_STEP = Decimal("0.1")
QUANTITY_STEP = Decimal("0.0001")
MIN_QUANTITY = Decimal("0.0001")

MARGIN_MODE = "ISOLATED"

TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")
SIGNAL_EXPIRY_SECONDS = 120


# ============================================================
# ABSOLUTE R1.1 PRODUCTION FIREBREAK
# ============================================================

REAL_ORDER_EXECUTION = False

PRODUCTION_WRITE_TRANSPORT = False
PRODUCTION_ORDER_SUBMISSION = False
FIRST_REAL_CANARY_ALLOWED = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False


# ============================================================
# CONSTRUCTION-ONLY ENDPOINTS
# ============================================================

PRODUCTION_ORDER_ENDPOINT = "/capi/v3/order"
PRODUCTION_TPSL_ENDPOINT = "/capi/v3/placeTpSlOrder"
PRODUCTION_ALGO_ENDPOINT = "/capi/v3/algoOrder"


# ============================================================
# TP ALLOCATIONS
# ============================================================

PREFERRED_ALLOCATION = (
    Decimal("20"),
    Decimal("20"),
    Decimal("60"),
)

ADJUSTED_ALLOCATION = (
    Decimal("25"),
    Decimal("25"),
    Decimal("50"),
)


# ============================================================
# DURABLE VALIDATION JOURNAL
# ============================================================

WRITE_R1_STATE_DIR = os.getenv(
    "WRITE_R1_STATE_DIR",
    "/var/data/r36f_state",
).strip()

WRITE_R1_JOURNAL_FILE = os.path.join(
    WRITE_R1_STATE_DIR,
    "write_r1_validation_journal.json",
)


# ============================================================
# BASIC HELPERS
# ============================================================

def now_iso():
    return datetime.now(timezone.utc).isoformat()


def log(message):
    print(
        f"{now_iso()} {message}",
        flush=True,
    )


def line():
    print(
        "----------------------------------------------------------------------------------------------------",
        flush=True,
    )


def D(value):
    return Decimal(str(value))


def decimal_to_string(value):
    if value is None:
        return None

    value = D(value)

    text = format(
        value,
        "f",
    )

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text


def canonical_json(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def sha256_text(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def quantize_down(value, step):
    value = D(value)
    step = D(step)

    if step <= 0:
        raise ValueError(
            "INVALID_QUANTIZATION_STEP"
        )

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def is_exact_step(value, step):
    value = D(value)
    step = D(step)

    if value <= 0:
        return False

    if step <= 0:
        return False

    return (
        quantize_down(
            value,
            step,
        )
        == value
    )


def read_json_file(
    path,
    default=None,
):
    if default is None:
        default = {}

    try:
        if not os.path.exists(path):
            return default

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    except Exception as exc:
        log(
            "WRITE_R1 JOURNAL READ FAILED "
            f"path={path} error={exc}"
        )

        return default


def write_json_file(
    path,
    data,
):
    os.makedirs(
        os.path.dirname(path),
        exist_ok=True,
    )

    tmp = path + ".tmp"

    with open(
        tmp,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            indent=2,
            sort_keys=True,
            default=str,
        )

    os.replace(
        tmp,
        path,
    )


# ============================================================
# FIREBREAK
# ============================================================

def production_firebreak_intact():
    return bool(
        REAL_ORDER_EXECUTION is False
        and PRODUCTION_WRITE_TRANSPORT is False
        and PRODUCTION_ORDER_SUBMISSION is False
        and FIRST_REAL_CANARY_ALLOWED is False
        and EXCHANGE_MUTATION_TRANSPORT_ENABLED is False
        and ORDER_SUBMISSION_ENABLED is False
        and LEVERAGE_MUTATION_ENABLED is False
        and MARGIN_MODE_MUTATION_ENABLED is False
        and POSITION_MUTATION_ENABLED is False
    )


# ============================================================
# INSTRUCTION FIELD HELPERS
# ============================================================

def first_value(
    instruction,
    names,
    default=None,
):
    for name in names:
        if name in instruction:
            value = instruction.get(name)

            if value is not None:
                return value

    return default


def normalize_instruction(
    instruction,
):
    if not isinstance(
        instruction,
        dict,
    ):
        raise ValueError(
            "INSTRUCTION_MUST_BE_DICT"
        )

    direction = str(
        first_value(
            instruction,
            (
                "direction",
                "position_side",
                "positionSide",
            ),
            "",
        )
    ).strip().upper()

    symbol = str(
        first_value(
            instruction,
            (
                "symbol",
            ),
            SYMBOL,
        )
    ).strip().upper()

    entry = D(
        first_value(
            instruction,
            (
                "entry_price",
                "entry",
                "mark_price",
            ),
            "0",
        )
    )

    quantity = D(
        first_value(
            instruction,
            (
                "quantity",
                "entry_quantity",
                "planned_entry_quantity",
            ),
            "0",
        )
    )

    tp1 = D(
        first_value(
            instruction,
            (
                "tp1",
                "tp1_price",
                "tp1_trigger_price",
            ),
            "0",
        )
    )

    tp2 = D(
        first_value(
            instruction,
            (
                "tp2",
                "tp2_price",
                "tp2_trigger_price",
            ),
            "0",
        )
    )

    tp3_raw = first_value(
        instruction,
        (
            "tp3",
            "tp3_price",
            "tp3_trigger_price",
        ),
        None,
    )

    tp3 = None

    if tp3_raw not in (
        None,
        "",
    ):
        try:
            tp3 = D(tp3_raw)

        except Exception:
            # TP3 can be a trailing-runner policy rather than
            # a fixed price.
            tp3 = None

    stop = D(
        first_value(
            instruction,
            (
                "stop_price",
                "sl",
                "sl_price",
                "protective_stop_price",
            ),
            "0",
        )
    )

    tp3_policy = str(
        first_value(
            instruction,
            (
                "tp3_policy",
                "runner_policy",
            ),
            "TRAILING_RUNNER",
        )
    ).strip().upper()

    source_stage = str(
        instruction.get(
            "source_stage",
            "",
        )
    ).strip()

    source_mode = str(
        instruction.get(
            "source_mode",
            "",
        )
    ).strip().upper()

    created_at = str(
        instruction.get(
            "created_at",
            "",
        )
    ).strip()

    return {
        "direction": direction,
        "symbol": symbol,
        "entry_price": entry,
        "quantity": quantity,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "tp3_policy": tp3_policy,
        "stop_price": stop,
        "source_stage": source_stage,
        "source_mode": source_mode,
        "created_at": created_at,
    }


# ============================================================
# PRICE STRUCTURE
# ============================================================

def validate_price_structure(
    direction,
    entry,
    tp1,
    tp2,
    stop,
):
    if direction == "LONG":
        return bool(
            stop
            < entry
            < tp1
            < tp2
        )

    if direction == "SHORT":
        return bool(
            stop
            > entry
            > tp1
            > tp2
            > 0
        )

    return False


# ============================================================
# TP QUANTITY ALLOCATION
# ============================================================

def allocation_quantities(
    quantity,
    percentages,
):
    quantity = D(quantity)

    p1, p2, p3 = percentages

    q1_raw = (
        quantity
        * p1
        / Decimal("100")
    )

    q2_raw = (
        quantity
        * p2
        / Decimal("100")
    )

    q3_raw = (
        quantity
        * p3
        / Decimal("100")
    )

    q1 = quantize_down(
        q1_raw,
        QUANTITY_STEP,
    )

    q2 = quantize_down(
        q2_raw,
        QUANTITY_STEP,
    )

    q3 = quantize_down(
        q3_raw,
        QUANTITY_STEP,
    )

    exact = bool(
        q1 == q1_raw
        and q2 == q2_raw
        and q3 == q3_raw
        and q1 >= MIN_QUANTITY
        and q2 >= MIN_QUANTITY
        and q3 >= MIN_QUANTITY
        and (
            q1
            + q2
            + q3
        )
        == quantity
    )

    return {
        "exact": exact,
        "tp1_quantity": q1,
        "tp2_quantity": q2,
        "tp3_quantity": q3,
    }


def select_allocation(
    quantity,
):
    preferred = allocation_quantities(
        quantity,
        PREFERRED_ALLOCATION,
    )

    if preferred["exact"]:
        return {
            "name": "20/20/60",
            **preferred,
        }

    adjusted = allocation_quantities(
        quantity,
        ADJUSTED_ALLOCATION,
    )

    if adjusted["exact"]:
        return {
            "name": "25/25/50",
            **adjusted,
        }

    return None


# ============================================================
# DETERMINISTIC CLIENT ORDER ID
# ============================================================

def build_client_order_id(
    direction,
    instruction_hash,
):
    prefix = (
        "L"
        if direction == "LONG"
        else "S"
        if direction == "SHORT"
        else "X"
    )

    value = (
        f"WR11-{prefix}-"
        + instruction_hash[:16].upper()
    )

    if len(value) > 36:
        raise ValueError(
            "CLIENT_ORDER_ID_TOO_LONG"
        )

    return value


# ============================================================
# PRODUCTION PAYLOAD CONSTRUCTION
# ZERO TRANSPORT
# ============================================================

def build_production_entry_payload(
    direction,
    quantity,
    tp1,
    stop,
    client_order_id,
):
    if direction == "LONG":
        side = "BUY"
        position_side = "LONG"

    elif direction == "SHORT":
        side = "SELL"
        position_side = "SHORT"

    else:
        raise ValueError(
            "INVALID_DIRECTION"
        )

    return {
        "symbol": SYMBOL,
        "side": side,
        "positionSide": position_side,
        "type": "MARKET",
        "quantity": decimal_to_string(
            quantity
        ),
        "newClientOrderId": (
            client_order_id
        ),
        "tpTriggerPrice": (
            decimal_to_string(tp1)
        ),
        "slTriggerPrice": (
            decimal_to_string(stop)
        ),
        "TpWorkingType": "MARK_PRICE",
        "SlWorkingType": "MARK_PRICE",
    }


# ============================================================
# PAYLOAD VALIDATION
# ============================================================

def validate_payload(
    payload,
    normalized,
):
    direction = normalized[
        "direction"
    ]

    expected_side = (
        "BUY"
        if direction == "LONG"
        else "SELL"
    )

    checks = {
        "endpoint_exact": (
            PRODUCTION_ORDER_ENDPOINT
            == "/capi/v3/order"
        ),
        "symbol_exact": (
            payload.get("symbol")
            == SYMBOL
        ),
        "side_exact": (
            payload.get("side")
            == expected_side
        ),
        "position_side_exact": (
            payload.get(
                "positionSide"
            )
            == direction
        ),
        "market_type_exact": (
            payload.get("type")
            == "MARKET"
        ),
        "quantity_exact": (
            payload.get("quantity")
            == decimal_to_string(
                normalized["quantity"]
            )
        ),
        "tp1_exact": (
            payload.get(
                "tpTriggerPrice"
            )
            == decimal_to_string(
                normalized["tp1"]
            )
        ),
        "sl_exact": (
            payload.get(
                "slTriggerPrice"
            )
            == decimal_to_string(
                normalized[
                    "stop_price"
                ]
            )
        ),
        "tp_working_type": (
            payload.get(
                "TpWorkingType"
            )
            == "MARK_PRICE"
        ),
        "sl_working_type": (
            payload.get(
                "SlWorkingType"
            )
            == "MARK_PRICE"
        ),
    }

    return (
        all(checks.values()),
        checks,
    )


# ============================================================
# R1.1 BRIDGE VALIDATOR
# ============================================================

def validate_instruction(
    instruction,
    *,
    source="MAIN.PY_BRIDGE",
    persist=True,
):
    """
    Validate ONE immutable instruction.

    This function performs no exchange network write.

    main.py may import and call:

        from write import validate_instruction

        result = validate_instruction(instruction)

    result["validated"] is True only when every
    R1.1 validation gate passes.
    """

    blockers = []

    line()

    log(
        f"{STAGE}: IMMUTABLE INSTRUCTION "
        f"VALIDATION START source={source}"
    )

    firebreak_ok = (
        production_firebreak_intact()
    )

    log(
        "PASS: PRODUCTION_FIREBREAK_INTACT"
        if firebreak_ok
        else
        "FAIL: PRODUCTION_FIREBREAK_INTACT"
    )

    if not firebreak_ok:
        blockers.append(
            "PRODUCTION_FIREBREAK_NOT_INTACT"
        )

    try:
        normalized = (
            normalize_instruction(
                instruction
            )
        )

    except Exception as exc:
        blockers.append(
            "INSTRUCTION_NORMALIZATION_FAILED"
        )

        result = {
            "stage": STAGE,
            "validated": False,
            "state": "BLOCKED",
            "source": source,
            "reason": (
                "INSTRUCTION_NORMALIZATION_FAILED"
            ),
            "error": str(exc),
            "blockers": blockers,
            "real_order_attempted": False,
            "real_order_sent": False,
            "production_mutation_sent": False,
        }

        log(
            f"{STAGE}: BLOCKED "
            f"error={exc}"
        )

        line()

        return result

    direction = normalized["direction"]
    symbol = normalized["symbol"]
    entry = normalized["entry_price"]
    quantity = normalized["quantity"]
    tp1 = normalized["tp1"]
    tp2 = normalized["tp2"]
    tp3 = normalized["tp3"]
    stop = normalized["stop_price"]

    if direction not in (
        "LONG",
        "SHORT",
    ):
        blockers.append(
            "DIRECTION_INVALID"
        )

    if symbol != SYMBOL:
        blockers.append(
            "SYMBOL_INVALID"
        )

    if entry <= 0:
        blockers.append(
            "ENTRY_MISSING_OR_INVALID"
        )

    if quantity < MIN_QUANTITY:
        blockers.append(
            "QUANTITY_MISSING_OR_INVALID"
        )

    if tp1 <= 0:
        blockers.append(
            "TP1_MISSING_OR_INVALID"
        )

    if tp2 <= 0:
        blockers.append(
            "TP2_MISSING_OR_INVALID"
        )

    if stop <= 0:
        blockers.append(
            "STOP_MISSING_OR_INVALID"
        )

    if not is_exact_step(
        quantity,
        QUANTITY_STEP,
    ):
        blockers.append(
            "QUANTITY_NOT_ON_WEEX_STEP"
        )

    for name, price in (
        ("ENTRY", entry),
        ("TP1", tp1),
        ("TP2", tp2),
        ("STOP", stop),
    ):
        if (
            price > 0
            and not is_exact_step(
                price,
                PRICE_STEP,
            )
        ):
            blockers.append(
                f"{name}_NOT_ON_WEEX_PRICE_STEP"
            )

    if (
        tp3 is not None
        and tp3 > 0
        and not is_exact_step(
            tp3,
            PRICE_STEP,
        )
    ):
        blockers.append(
            "TP3_NOT_ON_WEEX_PRICE_STEP"
        )

    structure_ok = (
        validate_price_structure(
            direction,
            entry,
            tp1,
            tp2,
            stop,
        )
    )

    if not structure_ok:
        blockers.append(
            "TP_SL_PRICE_STRUCTURE_INVALID"
        )

    allocation = select_allocation(
        quantity
    )

    if allocation is None:
        blockers.append(
            "NO_EXACT_TP_ALLOCATION"
        )

    immutable_material = {
        "stage": STAGE,
        "direction": direction,
        "symbol": symbol,
        "entry_price": (
            decimal_to_string(entry)
        ),
        "quantity": (
            decimal_to_string(quantity)
        ),
        "tp1": (
            decimal_to_string(tp1)
        ),
        "tp2": (
            decimal_to_string(tp2)
        ),
        "tp3": (
            decimal_to_string(tp3)
            if tp3 is not None
            else None
        ),
        "tp3_policy": normalized[
            "tp3_policy"
        ],
        "stop_price": (
            decimal_to_string(stop)
        ),
        "source_stage": normalized[
            "source_stage"
        ],
        "source_mode": normalized[
            "source_mode"
        ],
        "created_at": normalized[
            "created_at"
        ],
    }

    instruction_hash = sha256_text(
        canonical_json(
            immutable_material
        )
    )

    previous = read_json_file(
        WRITE_R1_JOURNAL_FILE,
        default={},
    )

    replay = bool(
        isinstance(previous, dict)
        and previous.get(
            "instruction_sha256"
        )
        == instruction_hash
        and previous.get("state")
        == "VALIDATED_NOT_SENT"
    )

    if replay:
        blockers.append(
            "INSTRUCTION_PREVIOUSLY_VALIDATED"
        )

    payload = None
    payload_hash = None
    payload_checks = {}

    if not blockers:
        client_order_id = (
            build_client_order_id(
                direction,
                instruction_hash,
            )
        )

        payload = (
            build_production_entry_payload(
                direction,
                quantity,
                tp1,
                stop,
                client_order_id,
            )
        )

        payload_ok, payload_checks = (
            validate_payload(
                payload,
                normalized,
            )
        )

        if not payload_ok:
            blockers.append(
                "PRODUCTION_PAYLOAD_VALIDATION_FAILED"
            )

        else:
            payload_hash = sha256_text(
                canonical_json(
                    payload
                )
            )

    validated = bool(
        not blockers
        and payload is not None
        and payload_hash
        and production_firebreak_intact()
    )

    state = (
        "VALIDATED_NOT_SENT"
        if validated
        else "BLOCKED"
    )

    result = {
        "stage": STAGE,
        "validated_at": now_iso(),
        "validated": validated,
        "state": state,
        "source": source,
        "direction": direction,
        "symbol": symbol,
        "entry_price": (
            decimal_to_string(entry)
        ),
        "quantity": (
            decimal_to_string(quantity)
        ),
        "tp1": (
            decimal_to_string(tp1)
        ),
        "tp2": (
            decimal_to_string(tp2)
        ),
        "tp3": (
            decimal_to_string(tp3)
            if tp3 is not None
            else None
        ),
        "tp3_policy": normalized[
            "tp3_policy"
        ],
        "stop_price": (
            decimal_to_string(stop)
        ),
        "allocation": (
            allocation["name"]
            if allocation
            else None
        ),
        "tp1_quantity": (
            decimal_to_string(
                allocation[
                    "tp1_quantity"
                ]
            )
            if allocation
            else None
        ),
        "tp2_quantity": (
            decimal_to_string(
                allocation[
                    "tp2_quantity"
                ]
            )
            if allocation
            else None
        ),
        "tp3_quantity": (
            decimal_to_string(
                allocation[
                    "tp3_quantity"
                ]
            )
            if allocation
            else None
        ),
        "instruction_sha256": (
            instruction_hash
        ),
        "payload_sha256": payload_hash,
        "payload": payload,
        "payload_checks": (
            payload_checks
        ),
        "endpoint": (
            PRODUCTION_ORDER_ENDPOINT
            if payload
            else None
        ),
        "blockers": blockers,
        "real_order_execution": (
            REAL_ORDER_EXECUTION
        ),
        "production_write_transport": (
            PRODUCTION_WRITE_TRANSPORT
        ),
        "production_order_submission": (
            PRODUCTION_ORDER_SUBMISSION
        ),
        "first_real_canary_allowed": (
            FIRST_REAL_CANARY_ALLOWED
        ),
        "real_order_attempted": False,
        "real_order_sent": False,
        "production_mutation_sent": False,
    }

    if validated and persist:
        write_json_file(
            WRITE_R1_JOURNAL_FILE,
            result,
        )

    log(
        f"{STAGE}: DIRECTION = "
        f"{direction}"
    )

    log(
        f"{STAGE}: SYMBOL = "
        f"{symbol}"
    )

    log(
        f"{STAGE}: ENTRY = "
        f"{decimal_to_string(entry)}"
    )

    log(
        f"{STAGE}: QUANTITY = "
        f"{decimal_to_string(quantity)}"
    )

    log(
        f"{STAGE}: TP1 = "
        f"{decimal_to_string(tp1)}"
    )

    log(
        f"{STAGE}: TP2 = "
        f"{decimal_to_string(tp2)}"
    )

    log(
        f"{STAGE}: TP3 POLICY = "
        f"{normalized['tp3_policy']}"
    )

    log(
        f"{STAGE}: STOP = "
        f"{decimal_to_string(stop)}"
    )

    log(
        f"{STAGE}: ALLOCATION = "
        f"{result['allocation']}"
    )

    log(
        f"{STAGE}: INSTRUCTION SHA256 = "
        f"{instruction_hash}"
    )

    log(
        f"{STAGE}: PAYLOAD SHA256 = "
        f"{payload_hash}"
    )

    if payload is not None:
        log(
            f"{STAGE}: PRODUCTION PAYLOAD PREVIEW = "
            + canonical_json(payload)
        )

    log(
        f"{STAGE}: FINAL STATE = "
        f"{state}"
    )

    log(
        f"{STAGE}: BLOCKER COUNT = "
        f"{len(blockers)}"
    )

    for blocker in blockers:
        log(
            f"{STAGE}: BLOCKER = "
            f"{blocker}"
        )

    log(
        f"{STAGE}: REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"{STAGE}: "
        f"PRODUCTION_WRITE_TRANSPORT="
        f"{PRODUCTION_WRITE_TRANSPORT}"
    )

    log(
        f"{STAGE}: "
        f"PRODUCTION_ORDER_SUBMISSION="
        f"{PRODUCTION_ORDER_SUBMISSION}"
    )

    log(
        f"{STAGE}: "
        f"FIRST_REAL_CANARY_ALLOWED="
        f"{FIRST_REAL_CANARY_ALLOWED}"
    )

    log(
        "NO REAL ORDER WAS SENT"
    )

    log(
        "NO PRODUCTION EXCHANGE MUTATION "
        "WAS SENT"
    )

    line()

    return result


# ============================================================
# OPTIONAL STANDALONE TEST
# ============================================================

def load_standalone_instruction():
    """
    Optional only.

    R1.1 bridge operation does NOT require this environment
    variable. It remains available solely for an isolated
    write.py validation test.
    """

    raw = os.getenv(
        "WRITE_R1_INSTRUCTION_JSON",
        "",
    ).strip()

    if not raw:
        return None

    data = json.loads(raw)

    if not isinstance(data, dict):
        raise ValueError(
            "WRITE_R1_INSTRUCTION_JSON_MUST_BE_OBJECT"
        )

    return data


def main():
    line()

    log(
        f"{STAGE}: ZERO-WRITE "
        "PRODUCTION WRITER VALIDATOR"
    )

    log(
        f"{STAGE}: "
        "PRODUCTION FIREBREAK = "
        f"{production_firebreak_intact()}"
    )

    instruction = (
        load_standalone_instruction()
    )

    if instruction is None:
        log(
            f"{STAGE}: STANDALONE INSTRUCTION "
            "NOT PRESENT"
        )

        log(
            f"{STAGE}: READY FOR "
            "MAIN.PY INTERNAL BRIDGE"
        )

        log(
            f"{STAGE}: NO VALIDATION "
            "ATTEMPTED"
        )

        log(
            "NO REAL ORDER WAS SENT"
        )

        log(
            "NO PRODUCTION EXCHANGE "
            "MUTATION WAS SENT"
        )

        line()

        return

    validate_instruction(
        instruction,
        source="STANDALONE_ENV_TEST",
        persist=True,
    )


# ============================================================
# WRITE.PY-R1.2
# ZERO-WRITE MAIN.PY INTERNAL BRIDGE VALIDATION
# ============================================================

R12_STAGE = "WRITE.PY-R1.2"

R12_INTERNAL_BRIDGE_TEST = (
    os.getenv(
        "WRITE_R12_INTERNAL_BRIDGE_TEST",
        "true",
    ).strip().lower()
    == "true"
)


def build_r12_internal_bridge_instruction():
    """
    Construct one deterministic MAIN.PY-style instruction.

    IMPORTANT:
    This is validation material only.
    It cannot reach an exchange because the R1.1 production
    firebreak remains hard-disabled.
    """

    return {
        "symbol": "BTCUSDT",

        "direction": "LONG",

        "entry_price": "80000.0",

        "quantity": "0.0004",

        "tp1": "80100.0",

        "tp2": "80200.0",

        "tp3": None,

        "tp3_policy": "TRAILING_RUNNER",

        "stop_price": "79600.0",

        "source_stage": "R36F.15.10.5",

        "source_mode": "MAIN.PY_INTERNAL_BRIDGE",

        "created_at": now_iso(),
    }


def validate_r12_internal_bridge():
    line()

    log(
        f"{R12_STAGE}: "
        "ZERO-WRITE INTERNAL BRIDGE VALIDATOR"
    )

    firebreak_ok = production_firebreak_intact()

    log(
        f"{R12_STAGE}: "
        f"PRODUCTION FIREBREAK = {firebreak_ok}"
    )

    if not firebreak_ok:
        log(
            f"{R12_STAGE}: "
            "INTERNAL BRIDGE = BLOCKED"
        )

        log(
            f"{R12_STAGE}: "
            "REASON = PRODUCTION_FIREBREAK_NOT_INTACT"
        )

        log(
            "NO REAL ORDER WAS SENT"
        )

        log(
            "NO PRODUCTION EXCHANGE MUTATION WAS SENT"
        )

        line()

        return {
            "stage": R12_STAGE,
            "passed": False,
            "reason": (
                "PRODUCTION_FIREBREAK_NOT_INTACT"
            ),
        }

    if not R12_INTERNAL_BRIDGE_TEST:
        log(
            f"{R12_STAGE}: "
            "INTERNAL BRIDGE TEST DISABLED"
        )

        log(
            "NO REAL ORDER WAS SENT"
        )

        log(
            "NO PRODUCTION EXCHANGE MUTATION WAS SENT"
        )

        line()

        return {
            "stage": R12_STAGE,
            "passed": False,
            "reason": (
                "INTERNAL_BRIDGE_TEST_DISABLED"
            ),
        }

    instruction = (
        build_r12_internal_bridge_instruction()
    )

    log(
        f"{R12_STAGE}: "
        "INTERNAL BRIDGE INSTRUCTION CREATED"
    )

    log(
        f"{R12_STAGE}: "
        "INTERNAL BRIDGE SOURCE = MAIN.PY"
    )

    log(
        f"{R12_STAGE}: "
        "CALLING R1.1 IMMUTABLE VALIDATOR"
    )

    result = validate_instruction(
        instruction,
        source="MAIN.PY_INTERNAL_BRIDGE",
        persist=False,
    )

    validated = bool(
        result.get("validated") is True
    )

    state_ok = bool(
        result.get("state")
        == "VALIDATED_NOT_SENT"
    )

    no_real_attempt = bool(
        result.get("real_order_attempted")
        is False
    )

    no_real_sent = bool(
        result.get("real_order_sent")
        is False
    )

    no_mutation_sent = bool(
        result.get("production_mutation_sent")
        is False
    )

    firebreak_after = (
        production_firebreak_intact()
    )

    schema_ok = bool(
        result.get("symbol") == "BTCUSDT"
        and result.get("direction") == "LONG"
        and result.get("quantity") == "0.0004"
    )

    tp_policy_ok = bool(
        result.get("tp1") == "80100"
        and result.get("tp2") == "80200"
        and result.get("tp3_policy")
        == "TRAILING_RUNNER"
        and result.get("allocation")
        == "25/25/50"
    )

    stop_ok = bool(
        result.get("stop_price")
        == "79600"
    )

    payload_ok = bool(
        isinstance(
            result.get("payload"),
            dict,
        )
        and result.get("payload_checks")
        and all(
            result.get(
                "payload_checks",
                {},
            ).values()
        )
    )

    hash_ok = bool(
        result.get("instruction_sha256")
        and result.get("payload_sha256")
    )

    blockers_ok = bool(
        result.get("blockers") == []
    )

    checks = {
        "INSTRUCTION_SCHEMA": schema_ok,

        "R1_1_VALIDATION": validated,

        "VALIDATED_NOT_SENT_STATE": state_ok,

        "TP_POLICY": tp_policy_ok,

        "PROTECTIVE_STOP": stop_ok,

        "PAYLOAD_CONSTRUCTION": payload_ok,

        "DETERMINISTIC_HASHES": hash_ok,

        "ZERO_BLOCKERS": blockers_ok,

        "NO_REAL_ORDER_ATTEMPT": (
            no_real_attempt
        ),

        "NO_REAL_ORDER_SENT": (
            no_real_sent
        ),

        "NO_PRODUCTION_MUTATION_SENT": (
            no_mutation_sent
        ),

        "FIREBREAK_REMAINS_INTACT": (
            firebreak_after
        ),
    }

    for name, passed in checks.items():
        log(
            f"{R12_STAGE}: "
            f"{name} = "
            f"{'PASS' if passed else 'FAIL'}"
        )

    bridge_pass = all(
        checks.values()
    )

    if bridge_pass:
        log(
            f"{R12_STAGE}: "
            "PRODUCTION WRITE BLOCKED BY FIREBREAK"
        )

        log(
            f"{R12_STAGE}: "
            "INTERNAL BRIDGE = PASS"
        )

    else:
        log(
            f"{R12_STAGE}: "
            "INTERNAL BRIDGE = FAIL"
        )

        failed = [
            name
            for name, passed
            in checks.items()
            if not passed
        ]

        for name in failed:
            log(
                f"{R12_STAGE}: "
                f"FAILED CHECK = {name}"
            )

    log(
        f"{R12_STAGE}: "
        f"FINAL FIREBREAK = "
        f"{production_firebreak_intact()}"
    )

    log(
        "NO REAL ORDER WAS SENT"
    )

    log(
        "NO PRODUCTION EXCHANGE MUTATION WAS SENT"
    )

    line()

    return {
        "stage": R12_STAGE,
        "passed": bridge_pass,
        "checks": checks,
        "validator_result": result,
    }


def r12_main():
    """
    Run the existing R1.1 startup diagnostic first,
    followed by the new R1.2 internal bridge test.
    """

    main()

    validate_r12_internal_bridge()


if __name__ == "__main__":
    r12_main()
