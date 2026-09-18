#!/usr/bin/env python3

"""
WRITE.PY R1
R36F.15.10.5 PRODUCTION WRITER VALIDATOR — ZERO WRITE

PURPOSE
-------
1. Keep frozen main.py untouched.
2. Accept one immutable writer instruction.
3. Validate direction, symbol, quantity, TP1, TP2, TP3 and SL.
4. Validate WEEX price/quantity steps.
5. Validate LONG/SHORT TP/SL ordering.
6. Validate 20/20/60 or adjusted 25/25/50 TP allocation.
7. Construct the exact production entry payload.
8. Calculate deterministic instruction/payload hashes.
9. Detect replay through a durable validation journal.
10. HARD BLOCK every production network write.

R1 NEVER SENDS AN ORDER.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN


# ============================================================
# STAGE
# ============================================================

STAGE = "WRITE.PY-R1"

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
# FROZEN PRODUCTION ENDPOINTS
# CONSTRUCTION ONLY — NEVER CALLED IN R1
# ============================================================

WRITER_ENDPOINT_ENTRY = "/capi/v3/order"
WRITER_ENDPOINT_TPSL = "/capi/v3/placeTpSlOrder"
WRITER_ENDPOINT_TRAILING = "/capi/v3/algoOrder"


# ============================================================
# ABSOLUTE R1 PRODUCTION FIREBREAK
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
# TP ALLOCATION
# ============================================================

PREFERRED_TP1_PERCENT = Decimal("20")
PREFERRED_TP2_PERCENT = Decimal("20")
PREFERRED_TP3_PERCENT = Decimal("60")

ADJUSTED_TP1_PERCENT = Decimal("25")
ADJUSTED_TP2_PERCENT = Decimal("25")
ADJUSTED_TP3_PERCENT = Decimal("50")


# ============================================================
# DURABLE R1 VALIDATION JOURNAL
# ============================================================

STATE_DIR = os.getenv(
    "WRITE_R1_STATE_DIR",
    "/var/data/r36f_state",
).strip()

try:
    os.makedirs(
        STATE_DIR,
        exist_ok=True,
    )
except Exception:
    STATE_DIR = "/tmp"

    os.makedirs(
        STATE_DIR,
        exist_ok=True,
    )

JOURNAL_FILE = os.path.join(
    STATE_DIR,
    "write_r1_validation_journal.json",
)


# ============================================================
# BASIC HELPERS
# ============================================================

def now_iso():
    return datetime.now(
        timezone.utc
    ).isoformat()


def line():
    print(
        "=" * 88,
        flush=True,
    )


def log(message):
    print(
        f"{now_iso()} {message}",
        flush=True,
    )


def D(value):
    return Decimal(
        str(value)
    )


def decimal_to_string(value):
    if value is None:
        return None

    value = D(value)

    text = format(
        value,
        "f",
    )

    if "." in text:
        text = text.rstrip(
            "0"
        ).rstrip(
            "."
        )

    return text


def quantize_down(
    value,
    step,
):
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


def sha256_object(data):
    return sha256_text(
        canonical_json(data)
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

    except Exception:
        return default


def write_json_file(
    path,
    data,
):
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
# DIAGNOSTIC COLLECTOR
# ============================================================

CHECKS = {}
BLOCKERS = []


def check(
    name,
    condition,
    detail=None,
):
    condition = bool(
        condition
    )

    CHECKS[name] = condition

    if condition:
        log(
            f"PASS: {name}"
        )

    else:
        log(
            f"FAIL: {name}"
        )

        BLOCKERS.append(
            name
        )

    if detail is not None:
        log(
            "      "
            + str(detail)
        )

    return condition


# ============================================================
# FIREBREAK VALIDATION
# ============================================================

def production_firebreak_intact():
    return all(
        (
            REAL_ORDER_EXECUTION is False,
            PRODUCTION_WRITE_TRANSPORT is False,
            PRODUCTION_ORDER_SUBMISSION is False,
            FIRST_REAL_CANARY_ALLOWED is False,
            EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
            ORDER_SUBMISSION_ENABLED is False,
            LEVERAGE_MUTATION_ENABLED is False,
            MARGIN_MODE_MUTATION_ENABLED is False,
            POSITION_MUTATION_ENABLED is False,
        )
    )


# ============================================================
# INSTRUCTION INPUT
# ============================================================

def load_instruction():
    raw = os.getenv(
        "WRITE_R1_INSTRUCTION_JSON",
        "",
    ).strip()

    if not raw:
        return None

    try:
        value = json.loads(
            raw
        )

    except Exception as exc:
        raise RuntimeError(
            "WRITE_R1_INSTRUCTION_JSON_INVALID: "
            + str(exc)
        )

    if not isinstance(
        value,
        dict,
    ):
        raise RuntimeError(
            "WRITE_R1_INSTRUCTION_MUST_BE_JSON_OBJECT"
        )

    return value


# ============================================================
# FIELD NORMALIZATION
# ============================================================

def instruction_direction(
    instruction,
):
    return str(
        instruction.get(
            "direction",
            "",
        )
    ).strip().upper()


def instruction_symbol(
    instruction,
):
    return str(
        instruction.get(
            "symbol",
            SYMBOL,
        )
    ).strip().upper()


def get_decimal(
    instruction,
    *names,
):
    for name in names:
        value = instruction.get(
            name
        )

        if value is not None:
            return D(
                value
            )

    return None


# ============================================================
# TP QUANTITY SELECTION
# ============================================================

def allocation_exactly_representable(
    quantity,
    p1,
    p2,
    p3,
):
    quantity = quantize_down(
        quantity,
        QUANTITY_STEP,
    )

    percentages = (
        D(p1),
        D(p2),
        D(p3),
    )

    if sum(
        percentages
    ) != Decimal("100"):
        return False

    quantities = tuple(
        quantity
        * percent
        / Decimal("100")
        for percent
        in percentages
    )

    return bool(
        quantity >= MIN_QUANTITY
        and all(
            q >= MIN_QUANTITY
            for q
            in quantities
        )
        and all(
            quantize_down(
                q,
                QUANTITY_STEP,
            ) == q
            for q
            in quantities
        )
        and sum(
            quantities
        ) == quantity
    )


def select_tp_allocation(
    quantity,
):
    quantity = quantize_down(
        quantity,
        QUANTITY_STEP,
    )

    if allocation_exactly_representable(
        quantity,
        PREFERRED_TP1_PERCENT,
        PREFERRED_TP2_PERCENT,
        PREFERRED_TP3_PERCENT,
    ):
        return {
            "label": "20/20/60",
            "tp1_percent":
                PREFERRED_TP1_PERCENT,
            "tp2_percent":
                PREFERRED_TP2_PERCENT,
            "tp3_percent":
                PREFERRED_TP3_PERCENT,
            "adjusted": False,
        }

    if allocation_exactly_representable(
        quantity,
        ADJUSTED_TP1_PERCENT,
        ADJUSTED_TP2_PERCENT,
        ADJUSTED_TP3_PERCENT,
    ):
        return {
            "label": "25/25/50",
            "tp1_percent":
                ADJUSTED_TP1_PERCENT,
            "tp2_percent":
                ADJUSTED_TP2_PERCENT,
            "tp3_percent":
                ADJUSTED_TP3_PERCENT,
            "adjusted": True,
        }

    return None


def allocate_tp_quantities(
    quantity,
    allocation,
):
    quantity = quantize_down(
        quantity,
        QUANTITY_STEP,
    )

    tp1 = (
        quantity
        * allocation[
            "tp1_percent"
        ]
        / Decimal("100")
    )

    tp2 = (
        quantity
        * allocation[
            "tp2_percent"
        ]
        / Decimal("100")
    )

    tp3 = (
        quantity
        * allocation[
            "tp3_percent"
        ]
        / Decimal("100")
    )

    return {
        "entry":
            quantity,

        "tp1":
            tp1,

        "tp2":
            tp2,

        "tp3":
            tp3,

        "sum":
            tp1
            + tp2
            + tp3,
    }


# ============================================================
# CLIENT ORDER ID
# ============================================================

def writer_client_id(
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

    digest = (
        instruction_hash[
            :16
        ].upper()
    )

    value = (
        f"WR1-{prefix}-{digest}"
    )

    if len(
        value
    ) > 36:
        raise ValueError(
            "CLIENT_ORDER_ID_EXCEEDS_WEEX_LIMIT"
        )

    return value


# ============================================================
# DIRECTION / PRICE VALIDATION
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
        "symbol":
            SYMBOL,

        "side":
            side,

        "positionSide":
            position_side,

        "type":
            "MARKET",

        "quantity":
            decimal_to_string(
                quantity
            ),

        "newClientOrderId":
            client_order_id,

        "tpTriggerPrice":
            decimal_to_string(
                tp1
            ),

        "slTriggerPrice":
            decimal_to_string(
                stop
            ),

        "TpWorkingType":
            "MARK_PRICE",

        "SlWorkingType":
            "MARK_PRICE",
    }


# ============================================================
# REPLAY VALIDATION
# ============================================================

def replay_status(
    instruction_hash,
):
    journal = read_json_file(
        JOURNAL_FILE,
        default={},
    )

    previous_hash = str(
        journal.get(
            "instruction_sha256",
            "",
        )
    ).strip()

    if (
        previous_hash
        and previous_hash
        == instruction_hash
    ):
        return {
            "replay":
                True,

            "journal":
                journal,
        }

    return {
        "replay":
            False,

        "journal":
            journal,
    }


# ============================================================
# R1 MAIN VALIDATION
# ============================================================

def run():
    line()

    log(
        f"{STAGE}: ZERO-WRITE PRODUCTION WRITER VALIDATION START"
    )

    line()

    check(
        "PRODUCTION_FIREBREAK_INTACT",
        production_firebreak_intact(),
    )

    check(
        "REAL_ORDER_EXECUTION_FALSE",
        REAL_ORDER_EXECUTION is False,
    )

    check(
        "PRODUCTION_WRITE_TRANSPORT_FALSE",
        PRODUCTION_WRITE_TRANSPORT is False,
    )

    check(
        "PRODUCTION_ORDER_SUBMISSION_FALSE",
        PRODUCTION_ORDER_SUBMISSION is False,
    )

    check(
        "FIRST_REAL_CANARY_ALLOWED_FALSE",
        FIRST_REAL_CANARY_ALLOWED is False,
    )

    instruction = load_instruction()

    if instruction is None:
        check(
            "IMMUTABLE_INSTRUCTION_PRESENT",
            False,
            "Set WRITE_R1_INSTRUCTION_JSON before running R1.",
        )

        final_report(
            instruction=None,
            payload=None,
            instruction_hash=None,
            payload_hash=None,
            allocation=None,
            quantities=None,
        )

        return 1

    check(
        "IMMUTABLE_INSTRUCTION_PRESENT",
        True,
    )

    instruction_hash = sha256_object(
        instruction
    )

    log(
        "WRITE.R1 INSTRUCTION SHA256 = "
        + instruction_hash
    )

    direction = instruction_direction(
        instruction
    )

    symbol = instruction_symbol(
        instruction
    )

    entry = get_decimal(
        instruction,
        "entry_price",
        "entry",
        "mark_price",
    )

    quantity = get_decimal(
        instruction,
        "quantity",
        "entry_quantity",
        "planned_entry_quantity",
    )

    tp1 = get_decimal(
        instruction,
        "tp1",
        "tp1_price",
        "tp1_trigger_price",
    )

    tp2 = get_decimal(
        instruction,
        "tp2",
        "tp2_price",
        "tp2_trigger_price",
    )

    tp3 = get_decimal(
        instruction,
        "tp3",
        "tp3_price",
    )

    stop = get_decimal(
        instruction,
        "stop_price",
        "sl",
        "sl_price",
        "protective_stop_price",
    )

    check(
        "SYMBOL_BTCUSDT",
        symbol == SYMBOL,
        f"symbol={symbol}",
    )

    check(
        "DIRECTION_VALID",
        direction
        in {
            "LONG",
            "SHORT",
        },
        f"direction={direction}",
    )

    check(
        "ENTRY_PRESENT",
        entry is not None
        and entry > 0,
        f"entry={entry}",
    )

    check(
        "QUANTITY_PRESENT",
        quantity is not None
        and quantity > 0,
        f"quantity={quantity}",
    )

    check(
        "TP1_PRESENT",
        tp1 is not None
        and tp1 > 0,
        f"tp1={tp1}",
    )

    check(
        "TP2_PRESENT",
        tp2 is not None
        and tp2 > 0,
        f"tp2={tp2}",
    )

    check(
        "STOP_PRESENT",
        stop is not None
        and stop > 0,
        f"stop={stop}",
    )

    required_present = all(
        value is not None
        and value > 0
        for value
        in (
            entry,
            quantity,
            tp1,
            tp2,
            stop,
        )
    )

    allocation = None
    quantities = None
    payload = None
    payload_hash = None

    if required_present:
        normalized_quantity = quantize_down(
            quantity,
            QUANTITY_STEP,
        )

        normalized_entry = quantize_down(
            entry,
            PRICE_STEP,
        )

        normalized_tp1 = quantize_down(
            tp1,
            PRICE_STEP,
        )

        normalized_tp2 = quantize_down(
            tp2,
            PRICE_STEP,
        )

        normalized_stop = quantize_down(
            stop,
            PRICE_STEP,
        )

        check(
            "QUANTITY_ALREADY_ON_STEP",
            normalized_quantity
            == quantity,
        )

        check(
            "ENTRY_ALREADY_ON_STEP",
            normalized_entry
            == entry,
        )

        check(
            "TP1_ALREADY_ON_STEP",
            normalized_tp1
            == tp1,
        )

        check(
            "TP2_ALREADY_ON_STEP",
            normalized_tp2
            == tp2,
        )

        check(
            "STOP_ALREADY_ON_STEP",
            normalized_stop
            == stop,
        )

        check(
            "QUANTITY_MEETS_MINIMUM",
            normalized_quantity
            >= MIN_QUANTITY,
        )

        check(
            "TP_SL_DIRECTIONAL_ORDER_VALID",
            validate_price_structure(
                direction,
                normalized_entry,
                normalized_tp1,
                normalized_tp2,
                normalized_stop,
            ),
        )

        allocation = select_tp_allocation(
            normalized_quantity
        )

        check(
            "TP_ALLOCATION_REPRESENTABLE",
            allocation is not None,
            (
                allocation.get(
                    "label"
                )
                if allocation
                else "NONE"
            ),
        )

        if allocation:
            quantities = allocate_tp_quantities(
                normalized_quantity,
                allocation,
            )

            check(
                "TP1_QUANTITY_MINIMUM",
                quantities["tp1"]
                >= MIN_QUANTITY,
            )

            check(
                "TP2_QUANTITY_MINIMUM",
                quantities["tp2"]
                >= MIN_QUANTITY,
            )

            check(
                "TP3_QUANTITY_MINIMUM",
                quantities["tp3"]
                >= MIN_QUANTITY,
            )

            check(
                "TP_QUANTITY_SUM_EXACT",
                quantities["sum"]
                == quantities["entry"],
            )

        replay = replay_status(
            instruction_hash
        )

        check(
            "INSTRUCTION_NOT_PREVIOUSLY_VALIDATED",
            not replay[
                "replay"
            ],
            (
                "FRESH"
                if not replay["replay"]
                else "REPLAY_DETECTED"
            ),
        )

        client_order_id = writer_client_id(
            direction,
            instruction_hash,
        )

        check(
            "CLIENT_ORDER_ID_LENGTH_VALID",
            len(
                client_order_id
            ) <= 36,
            client_order_id,
        )

        if not BLOCKERS:
            payload = (
                build_production_entry_payload(
                    direction,
                    normalized_quantity,
                    normalized_tp1,
                    normalized_stop,
                    client_order_id,
                )
            )

            payload_hash = sha256_object(
                payload
            )

            check(
                "PRODUCTION_PAYLOAD_CONSTRUCTED",
                isinstance(
                    payload,
                    dict,
                ),
            )

            check(
                "PRODUCTION_ENDPOINT_ENTRY_SELECTED",
                WRITER_ENDPOINT_ENTRY
                == "/capi/v3/order",
                WRITER_ENDPOINT_ENTRY,
            )

            check(
                "PRODUCTION_PAYLOAD_SYMBOL_VALID",
                payload.get(
                    "symbol"
                ) == SYMBOL,
            )

            check(
                "PRODUCTION_PAYLOAD_MARKET_TYPE",
                payload.get(
                    "type"
                ) == "MARKET",
            )

            check(
                "PRODUCTION_PAYLOAD_HAS_TP",
                bool(
                    payload.get(
                        "tpTriggerPrice"
                    )
                ),
            )

            check(
                "PRODUCTION_PAYLOAD_HAS_SL",
                bool(
                    payload.get(
                        "slTriggerPrice"
                    )
                ),
            )

            check(
                "PRODUCTION_PAYLOAD_VALIDATED",
                True,
            )

            log(
                "WRITE.R1 PRODUCTION PAYLOAD SHA256 = "
                + payload_hash
            )

            log(
                "WRITE.R1 PRODUCTION PAYLOAD PREVIEW = "
                + canonical_json(
                    payload
                )
            )

    # --------------------------------------------------------
    # ABSOLUTE LAST-MOMENT WRITE ASSERTION
    # --------------------------------------------------------

    check(
        "FINAL_ZERO_WRITE_ASSERTION",
        production_firebreak_intact(),
    )

    if not BLOCKERS:
        journal = {
            "stage":
                STAGE,

            "state":
                "VALIDATED_NOT_SENT",

            "validated_at":
                now_iso(),

            "instruction_sha256":
                instruction_hash,

            "payload_sha256":
                payload_hash,

            "endpoint":
                WRITER_ENDPOINT_ENTRY,

            "client_order_id":
                (
                    payload.get(
                        "newClientOrderId"
                    )
                    if payload
                    else None
                ),

            "direction":
                direction,

            "symbol":
                symbol,

            "allocation":
                (
                    allocation.get(
                        "label"
                    )
                    if allocation
                    else None
                ),

            "real_order_execution":
                False,

            "production_write_transport":
                False,

            "production_order_submission":
                False,

            "first_real_canary_allowed":
                False,

            "order_attempted":
                False,

            "order_sent":
                False,
        }

        write_json_file(
            JOURNAL_FILE,
            journal,
        )

    final_report(
        instruction=instruction,
        payload=payload,
        instruction_hash=instruction_hash,
        payload_hash=payload_hash,
        allocation=allocation,
        quantities=quantities,
    )

    return (
        0
        if not BLOCKERS
        else 1
    )


# ============================================================
# FINAL REPORT
# ============================================================

def final_report(
    instruction,
    payload,
    instruction_hash,
    payload_hash,
    allocation,
    quantities,
):
    line()

    status = (
        "PASS"
        if not BLOCKERS
        else "BLOCKED"
    )

    log(
        f"WRITE.PY R1 FINAL STATUS = {status}"
    )

    log(
        "FINAL BLOCKER COUNT = "
        + str(
            len(
                BLOCKERS
            )
        )
    )

    if BLOCKERS:
        log(
            "FINAL BLOCKERS = "
            + ",".join(
                BLOCKERS
            )
        )

    log(
        "PRODUCTION PAYLOAD CONSTRUCTED = "
        + str(
            payload is not None
        )
    )

    log(
        "PRODUCTION PAYLOAD VALIDATED = "
        + str(
            bool(
                payload is not None
                and not BLOCKERS
            )
        )
    )

    log(
        "PRODUCTION WRITE TRANSPORT = "
        + str(
            PRODUCTION_WRITE_TRANSPORT
        )
    )

    log(
        "PRODUCTION ORDER SUBMISSION = "
        + str(
            PRODUCTION_ORDER_SUBMISSION
        )
    )

    log(
        "REAL ORDER EXECUTION = "
        + str(
            REAL_ORDER_EXECUTION
        )
    )

    log(
        "REAL ORDER ATTEMPTED = False"
    )

    log(
        "REAL ORDER SENT = False"
    )

    log(
        "FIRST REAL CANARY = "
        + (
            "ARMED"
            if FIRST_REAL_CANARY_ALLOWED
            else "NOT ARMED"
        )
    )

    if allocation:
        log(
            "TP ALLOCATION SELECTED = "
            + str(
                allocation.get(
                    "label"
                )
            )
        )

    if quantities:
        log(
            "ENTRY QUANTITY = "
            + decimal_to_string(
                quantities[
                    "entry"
                ]
            )
        )

        log(
            "TP1 QUANTITY = "
            + decimal_to_string(
                quantities[
                    "tp1"
                ]
            )
        )

        log(
            "TP2 QUANTITY = "
            + decimal_to_string(
                quantities[
                    "tp2"
                ]
            )
        )

        log(
            "TP3 QUANTITY = "
            + decimal_to_string(
                quantities[
                    "tp3"
                ]
            )
        )

    if instruction_hash:
        log(
            "INSTRUCTION SHA256 = "
            + instruction_hash
        )

    if payload_hash:
        log(
            "PAYLOAD SHA256 = "
            + payload_hash
        )

    log(
        "NO REAL ORDER WAS SENT"
    )

    log(
        "NO PRODUCTION EXCHANGE MUTATION WAS SENT"
    )

    line()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    try:
        exit_code = run()

    except Exception as exc:
        line()

        log(
            "WRITE.PY R1 FATAL VALIDATION ERROR = "
            + repr(
                exc
            )
        )

        log(
            "REAL ORDER ATTEMPTED = False"
        )

        log(
            "REAL ORDER SENT = False"
        )

        log(
            "NO PRODUCTION EXCHANGE MUTATION WAS SENT"
        )

        line()

        exit_code = 1

    sys.exit(
        exit_code
    )
