
#!/usr/bin/env python3

"""
R36F.15.4 - SINGLE STANDALONE TESTABLE UNIT

PURPOSE
-------
Test the complete new JIT safety behavior without requiring:
- requests
- WEEX network access
- demo POST
- real journal writes
- real order execution

RULES
-----
SHORT valid:
    TP < fresh_mark < SL

LONG valid:
    SL < fresh_mark < TP

If fresh mark has already reached/crossed TP or SL:
    status = JIT_DEMO_TRIGGER_VALIDATION_BLOCKED
    demo POST count must remain 0
    PREPARED journal count must remain 0
    wait_for_reevaluation = True

Exact previous failure:
    SHORT
    fresh_mark = 78268.1
    TP = 78287.5
    SL = 78692.4

Expected:
    BLOCKED BEFORE POST
"""

import json
import time
from decimal import Decimal, InvalidOperation


STAGE = "R36F.15.4"
DEMO_ORDER_PATH = "/capi/v3/sim/order"


def log(message):
    print(
        f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
        f"{message}",
        flush=True,
    )


def D(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(
            f"INVALID_DECIMAL_VALUE: {value!r}"
        ) from exc


def decimal_text(value):
    value = D(value)

    text = format(value, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text


def validate_jit_demo_triggers(
    direction,
    fresh_mark,
    take_profit,
    stop_loss,
):
    direction = str(direction).strip().upper()

    fresh_mark = D(fresh_mark)
    take_profit = D(take_profit)
    stop_loss = D(stop_loss)

    result = {
        "stage": STAGE,
        "direction": direction,
        "fresh_mark": decimal_text(fresh_mark),
        "tp": decimal_text(take_profit),
        "sl": decimal_text(stop_loss),
        "valid": False,
        "reason": None,
    }

    if fresh_mark <= 0:
        result["reason"] = "JIT_MARK_PRICE_INVALID"
        return result

    if take_profit <= 0:
        result["reason"] = "JIT_TP_INVALID"
        return result

    if stop_loss <= 0:
        result["reason"] = "JIT_SL_INVALID"
        return result

    if direction == "SHORT":

        if not take_profit < stop_loss:
            result["reason"] = (
                "JIT_SHORT_TRIGGER_ORDER_INVALID"
            )
            return result

        if take_profit < fresh_mark < stop_loss:
            result["valid"] = True
            result["reason"] = (
                "JIT_SHORT_TRIGGERS_VALID"
            )
            return result

        result["reason"] = (
            "JIT_SHORT_TRIGGER_STALE_OR_CROSSED"
        )
        return result

    if direction == "LONG":

        if not stop_loss < take_profit:
            result["reason"] = (
                "JIT_LONG_TRIGGER_ORDER_INVALID"
            )
            return result

        if stop_loss < fresh_mark < take_profit:
            result["valid"] = True
            result["reason"] = (
                "JIT_LONG_TRIGGERS_VALID"
            )
            return result

        result["reason"] = (
            "JIT_LONG_TRIGGER_STALE_OR_CROSSED"
        )
        return result

    result["reason"] = "JIT_DIRECTION_INVALID"
    return result


class DiagnosticState:

    def __init__(self):
        self.demo_post_count = 0
        self.prepared_journal_count = 0
        self.demo_posts = []
        self.prepared_journals = []


def fake_prepared_journal(
    state,
    payload,
    jit_result,
):
    entry = {
        "status": "PREPARED",
        "symbol": payload["symbol"],
        "direction": payload["direction"],
        "quantity": payload["quantity"],
        "tp": payload["tp"],
        "sl": payload["sl"],
        "fresh_mark": jit_result["fresh_mark"],
    }

    state.prepared_journal_count += 1
    state.prepared_journals.append(entry)

    log(
        f"{STAGE} TEST PREPARED JOURNAL = "
        + json.dumps(
            entry,
            separators=(",", ":"),
        )
    )

    return entry


def fake_demo_post(
    state,
    payload,
):
    state.demo_post_count += 1

    record = {
        "endpoint": DEMO_ORDER_PATH,
        "payload": payload,
    }

    state.demo_posts.append(record)

    log(
        f"{STAGE} TEST DEMO POST PERMITTED = "
        + json.dumps(
            record,
            separators=(",", ":"),
        )
    )

    return {
        "ok": True,
        "simulated": True,
        "test_order_id": (
            f"TEST-{state.demo_post_count}"
        ),
    }


def guarded_demo_dispatch(
    *,
    state,
    symbol,
    direction,
    quantity,
    take_profit,
    stop_loss,
    fresh_mark,
):
    payload = {
        "symbol": str(symbol),
        "direction": (
            str(direction)
            .strip()
            .upper()
        ),
        "quantity": decimal_text(quantity),
        "tp": decimal_text(take_profit),
        "sl": decimal_text(stop_loss),
    }

    jit_result = (
        validate_jit_demo_triggers(
            direction=direction,
            fresh_mark=fresh_mark,
            take_profit=take_profit,
            stop_loss=stop_loss,
        )
    )

    log(
        f"{STAGE} JIT DEMO TRIGGER VALIDATION = "
        + json.dumps(
            jit_result,
            separators=(",", ":"),
        )
    )

    if not jit_result["valid"]:

        blocked = {
            "ok": False,
            "status": (
                "JIT_DEMO_TRIGGER_VALIDATION_BLOCKED"
            ),
            "reason": jit_result["reason"],
            "demo_post_attempted": False,
            "prepared_journal_written": False,
            "wait_for_reevaluation": True,
        }

        log(
            f"{STAGE} DEMO DISPATCH BLOCKED = "
            + json.dumps(
                blocked,
                separators=(",", ":"),
            )
        )

        return blocked

    fake_prepared_journal(
        state=state,
        payload=payload,
        jit_result=jit_result,
    )

    post_result = fake_demo_post(
        state=state,
        payload=payload,
    )

    return {
        "ok": True,
        "status": "DEMO_DISPATCH_PERMITTED",
        "reason": jit_result["reason"],
        "demo_post_attempted": True,
        "prepared_journal_written": True,
        "wait_for_reevaluation": False,
        "post_result": post_result,
    }


def assert_pass(
    name,
    condition,
    details=None,
):
    if condition:
        log(f"PASS: {name}")
        return

    log(f"FAIL: {name}")

    if details is not None:
        log(
            "FAIL DETAILS = "
            + json.dumps(
                details,
                separators=(",", ":"),
                default=str,
            )
        )

    raise AssertionError(name)


def test_exact_previous_short_failure():

    state = DiagnosticState()

    result = guarded_demo_dispatch(
        state=state,
        symbol="BTCUSDT",
        direction="SHORT",
        quantity="0.0004",
        take_profit="78287.5",
        stop_loss="78692.4",
        fresh_mark="78268.1",
    )

    assert_pass(
        "OLD_SHORT_FAILURE_BLOCKED",
        result["status"]
        == "JIT_DEMO_TRIGGER_VALIDATION_BLOCKED",
        result,
    )

    assert_pass(
        "OLD_SHORT_FAILURE_REASON_CORRECT",
        result["reason"]
        == "JIT_SHORT_TRIGGER_STALE_OR_CROSSED",
        result,
    )

    assert_pass(
        "OLD_SHORT_FAILURE_ZERO_POST",
        state.demo_post_count == 0,
    )

    assert_pass(
        "OLD_SHORT_FAILURE_ZERO_PREPARED_JOURNAL",
        state.prepared_journal_count == 0,
    )

    assert_pass(
        "OLD_SHORT_FAILURE_WAITS_FOR_REEVALUATION",
        result["wait_for_reevaluation"] is True,
    )


def test_valid_short():

    state = DiagnosticState()

    result = guarded_demo_dispatch(
        state=state,
        symbol="BTCUSDT",
        direction="SHORT",
        quantity="0.0004",
        take_profit="78287.5",
        stop_loss="78692.4",
        fresh_mark="78300.0",
    )

    assert_pass(
        "VALID_SHORT_PERMITTED",
        result["status"]
        == "DEMO_DISPATCH_PERMITTED",
        result,
    )

    assert_pass(
        "VALID_SHORT_ONE_PREPARED",
        state.prepared_journal_count == 1,
    )

    assert_pass(
        "VALID_SHORT_ONE_TEST_POST",
        state.demo_post_count == 1,
    )


def test_short_tp_touch():

    state = DiagnosticState()

    result = guarded_demo_dispatch(
        state=state,
        symbol="BTCUSDT",
        direction="SHORT",
        quantity="0.0004",
        take_profit="78287.5",
        stop_loss="78692.4",
        fresh_mark="78287.5",
    )

    assert_pass(
        "SHORT_EXACT_TP_TOUCH_BLOCKED",
        result["ok"] is False,
        result,
    )

    assert_pass(
        "SHORT_EXACT_TP_TOUCH_ZERO_POST",
        state.demo_post_count == 0,
    )

    assert_pass(
        "SHORT_EXACT_TP_TOUCH_ZERO_PREPARED",
        state.prepared_journal_count == 0,
    )


def test_short_sl_touch():

    state = DiagnosticState()

    result = guarded_demo_dispatch(
        state=state,
        symbol="BTCUSDT",
        direction="SHORT",
        quantity="0.0004",
        take_profit="78287.5",
        stop_loss="78692.4",
        fresh_mark="78692.4",
    )

    assert_pass(
        "SHORT_EXACT_SL_TOUCH_BLOCKED",
        result["ok"] is False,
        result,
    )

    assert_pass(
        "SHORT_EXACT_SL_TOUCH_ZERO_POST",
        state.demo_post_count == 0,
    )


def test_valid_long():

    state = DiagnosticState()

    result = guarded_demo_dispatch(
        state=state,
        symbol="BTCUSDT",
        direction="LONG",
        quantity="0.0004",
        take_profit="78500",
        stop_loss="77900",
        fresh_mark="78200",
    )

    assert_pass(
        "VALID_LONG_PERMITTED",
        result["status"]
        == "DEMO_DISPATCH_PERMITTED",
        result,
    )

    assert_pass(
        "VALID_LONG_ONE_PREPARED",
        state.prepared_journal_count == 1,
    )

    assert_pass(
        "VALID_LONG_ONE_TEST_POST",
        state.demo_post_count == 1,
    )


def test_long_tp_touch():

    state = DiagnosticState()

    result = guarded_demo_dispatch(
        state=state,
        symbol="BTCUSDT",
        direction="LONG",
        quantity="0.0004",
        take_profit="78500",
        stop_loss="77900",
        fresh_mark="78500",
    )

    assert_pass(
        "LONG_EXACT_TP_TOUCH_BLOCKED",
        result["ok"] is False,
        result,
    )

    assert_pass(
        "LONG_EXACT_TP_TOUCH_ZERO_POST",
        state.demo_post_count == 0,
    )


def test_long_sl_touch():

    state = DiagnosticState()

    result = guarded_demo_dispatch(
        state=state,
        symbol="BTCUSDT",
        direction="LONG",
        quantity="0.0004",
        take_profit="78500",
        stop_loss="77900",
        fresh_mark="77900",
    )

    assert_pass(
        "LONG_EXACT_SL_TOUCH_BLOCKED",
        result["ok"] is False,
        result,
    )

    assert_pass(
        "LONG_EXACT_SL_TOUCH_ZERO_POST",
        state.demo_post_count == 0,
    )


def test_short_invalid_trigger_order():

    state = DiagnosticState()

    result = guarded_demo_dispatch(
        state=state,
        symbol="BTCUSDT",
        direction="SHORT",
        quantity="0.0004",
        take_profit="78700",
        stop_loss="78200",
        fresh_mark="78300",
    )

    assert_pass(
        "SHORT_INVALID_TRIGGER_ORDER_BLOCKED",
        result["reason"]
        == "JIT_SHORT_TRIGGER_ORDER_INVALID",
        result,
    )

    assert_pass(
        "SHORT_INVALID_TRIGGER_ORDER_ZERO_POST",
        state.demo_post_count == 0,
    )


def test_long_invalid_trigger_order():

    state = DiagnosticState()

    result = guarded_demo_dispatch(
        state=state,
        symbol="BTCUSDT",
        direction="LONG",
        quantity="0.0004",
        take_profit="77900",
        stop_loss="78700",
        fresh_mark="78300",
    )

    assert_pass(
        "LONG_INVALID_TRIGGER_ORDER_BLOCKED",
        result["reason"]
        == "JIT_LONG_TRIGGER_ORDER_INVALID",
        result,
    )

    assert_pass(
        "LONG_INVALID_TRIGGER_ORDER_ZERO_POST",
        state.demo_post_count == 0,
    )


def run_tests():

    log("-" * 100)

    log(
        f"{STAGE} SINGLE TESTABLE UNIT START"
    )

    log(
        "NETWORK ACCESS = DISABLED"
    )

    log(
        "REQUESTS PACKAGE = NOT REQUIRED"
    )

    log(
        "REAL WEEX POST = ZERO"
    )

    log(
        "REAL JOURNAL WRITE = ZERO"
    )

    log(
        "REAL ORDER EXECUTION = ZERO"
    )

    log("-" * 100)

    test_exact_previous_short_failure()

    test_valid_short()

    test_short_tp_touch()

    test_short_sl_touch()

    test_valid_long()

    test_long_tp_touch()

    test_long_sl_touch()

    test_short_invalid_trigger_order()

    test_long_invalid_trigger_order()

    log("-" * 100)

    log(
        "PASS: R36F15_4_JIT_TRIGGER_ENGINE"
    )

    log(
        "PASS: R36F15_4_GUARDED_DISPATCH_SEQUENCE"
    )

    log(
        "PASS: EXACT_R36F15_3_FAILURE_BLOCKED"
    )

    log(
        "PASS: BLOCKED_CASE_ZERO_PREPARED_JOURNAL"
    )

    log(
        "PASS: BLOCKED_CASE_ZERO_DEMO_POST"
    )

    log(
        "PASS: VALID_SHORT_REACHES_TEST_DISPATCH"
    )

    log(
        "PASS: VALID_LONG_REACHES_TEST_DISPATCH"
    )

    log(
        "PASS: EXACT_TRIGGER_TOUCH_BLOCKED"
    )

    log(
        "REAL WEEX POST COUNT = 0"
    )

    log(
        "REAL ORDER EXECUTION COUNT = 0"
    )

    log(
        f"{STAGE} SINGLE TESTABLE UNIT FINAL STATUS = PASS"
    )

    log("-" * 100)


if __name__ == "__main__":
    run_tests()
