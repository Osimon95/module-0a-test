
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

#!/usr/bin/env python3

"""
R36F.15.4 - PART 2 TESTABLE UNIT
GUARDED DEMO DISPATCH INTEGRATION

PURPOSE
-------
Test only the new R36F.15.4 demo-dispatch guard.

FLOW
----
1. Receive a prepared demo order candidate.
2. Fetch/use a fresh mark price immediately before dispatch.
3. Require:

    SHORT:
        TP < fresh_mark < SL

    LONG:
        SL < fresh_mark < TP

4. If invalid/stale/crossed:
       return JIT_DEMO_TRIGGER_VALIDATION_BLOCKED
       DO NOT call demo POST
       DO NOT create PREPARED journal

5. If valid:
       permit the demo-dispatch path
       create PREPARED journal only after JIT passes
       invoke the injected demo POST function

IMPORTANT
---------
This standalone unit DOES NOT contact WEEX.

A fake injected POST function is used so we can prove:

    blocked -> ZERO POST
    blocked -> ZERO PREPARED JOURNAL

and:

    valid -> exactly one permitted POST call
    valid -> exactly one PREPARED journal entry

REAL ORDER EXECUTION DOES NOT EXIST IN THIS UNIT.
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
    """
    R36F.15.4 frozen JIT rule.

    SHORT:
        TP < fresh_mark < SL

    LONG:
        SL < fresh_mark < TP
    """

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


class TestDispatchState:
    """
    Small in-memory diagnostic state.

    Used only to prove:

        blocked -> no POST
        blocked -> no PREPARED journal

        valid -> POST permitted
        valid -> PREPARED journal permitted
    """

    def __init__(self):
        self.demo_post_count = 0
        self.prepared_journal_count = 0

        self.demo_post_payloads = []
        self.prepared_journals = []


def build_demo_order_payload(
    symbol,
    direction,
    quantity,
    take_profit,
    stop_loss,
):
    direction = str(direction).strip().upper()

    if direction == "LONG":
        side = "BUY"
    elif direction == "SHORT":
        side = "SELL"
    else:
        raise ValueError(
            f"INVALID_DIRECTION: {direction}"
        )

    return {
        "symbol": str(symbol),
        "direction": direction,
        "side": side,
        "quantity": decimal_text(quantity),
        "take_profit": decimal_text(take_profit),
        "stop_loss": decimal_text(stop_loss),
        "endpoint": DEMO_ORDER_PATH,
    }


def write_prepared_journal(
    state,
    order_payload,
    jit_validation,
):
    """
    Test-only journal implementation.

    IMPORTANT:
    This function must never be called before JIT validation passes.
    """

    entry = {
        "status": "PREPARED",
        "stage": STAGE,
        "direction": order_payload["direction"],
        "symbol": order_payload["symbol"],
        "quantity": order_payload["quantity"],
        "take_profit": order_payload["take_profit"],
        "stop_loss": order_payload["stop_loss"],
        "fresh_mark": jit_validation["fresh_mark"],
        "jit_reason": jit_validation["reason"],
    }

    state.prepared_journal_count += 1

    state.prepared_journals.append(
        entry
    )

    log(
        f"{STAGE} PREPARED JOURNAL = "
        + json.dumps(
            entry,
            separators=(",", ":"),
        )
    )

    return entry


def fake_demo_post(
    state,
    endpoint,
    payload,
):
    """
    Fake demo POST.

    No network connection.
    No exchange mutation.

    It only increments a counter.
    """

    state.demo_post_count += 1

    state.demo_post_payloads.append(
        {
            "endpoint": endpoint,
            "payload": payload,
        }
    )

    log(
        f"{STAGE} TEST DEMO POST PERMITTED = "
        + json.dumps(
            {
                "endpoint": endpoint,
                "direction": payload["direction"],
                "side": payload["side"],
                "quantity": payload["quantity"],
            },
            separators=(",", ":"),
        )
    )

    return {
        "ok": True,
        "simulated": True,
        "endpoint": endpoint,
        "test_order_id": (
            f"TEST-DEMO-{state.demo_post_count}"
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
    demo_post_function,
):
    """
    R36F.15.4 guarded dispatch.

    THE CRITICAL ORDER IS:

        build candidate
              |
              v
        obtain fresh mark
              |
              v
        JIT validation
              |
        +-----+------+
        |            |
      FAIL          PASS
        |            |
        v            v
     RETURN      PREPARED
     BLOCKED     journal
                     |
                     v
                  DEMO POST

    A blocked JIT result returns BEFORE:
        - PREPARED journal
        - demo POST
    """

    order_payload = (
        build_demo_order_payload(
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            take_profit=take_profit,
            stop_loss=stop_loss,
        )
    )

    jit_validation = (
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
            jit_validation,
            separators=(",", ":"),
        )
    )

    if not jit_validation["valid"]:

        result = {
            "ok": False,
            "status": (
                "JIT_DEMO_TRIGGER_VALIDATION_BLOCKED"
            ),
            "reason": jit_validation["reason"],
            "direction": (
                str(direction)
                .strip()
                .upper()
            ),
            "fresh_mark": (
                jit_validation["fresh_mark"]
            ),
            "tp": jit_validation["tp"],
            "sl": jit_validation["sl"],
            "demo_post_attempted": False,
            "prepared_journal_written": False,
            "wait_for_reevaluation": True,
        }

        log(
            f"{STAGE} DEMO DISPATCH BLOCKED = "
            + json.dumps(
                result,
                separators=(",", ":"),
            )
        )

        return result

    prepared_journal = (
        write_prepared_journal(
            state=state,
            order_payload=order_payload,
            jit_validation=jit_validation,
        )
    )

    post_result = (
        demo_post_function(
            state,
            DEMO_ORDER_PATH,
            order_payload,
        )
    )

    result = {
        "ok": True,
        "status": "DEMO_DISPATCH_PERMITTED",
        "reason": jit_validation["reason"],
        "direction": (
            str(direction)
            .strip()
            .upper()
        ),
        "fresh_mark": (
            jit_validation["fresh_mark"]
        ),
        "tp": jit_validation["tp"],
        "sl": jit_validation["sl"],
        "demo_post_attempted": True,
        "prepared_journal_written": True,
        "wait_for_reevaluation": False,
        "prepared_journal": prepared_journal,
        "post_result": post_result,
    }

    log(
        f"{STAGE} DEMO DISPATCH RESULT = "
        + json.dumps(
            result,
            separators=(",", ":"),
        )
    )

    return result


def assert_test(
    name,
    condition,
    details=None,
):
    if condition:

        log(
            f"PASS: {name}"
        )

        return

    log(
        f"FAIL: {name}"
    )

    if details is not None:

        log(
            "FAILED DETAILS = "
            + json.dumps(
                details,
                separators=(",", ":"),
                default=str,
            )
        )

    raise AssertionError(name)


def test_exact_old_short_failure_blocks_before_post():
    """
    Exact failure seen previously:

        mark = 78268.1
        SHORT TP = 78287.5
        SL = 78692.4

    Required:

        TP < mark < SL

    becomes:

        78287.5 < 78268.1 < 78692.4

    FALSE.

    Therefore:

        no demo POST
        no PREPARED journal
        reevaluation requested
    """

    state = TestDispatchState()

    result = (
        guarded_demo_dispatch(
            state=state,
            symbol="BTCUSDT",
            direction="SHORT",
            quantity="0.0004",
            take_profit="78287.5",
            stop_loss="78692.4",
            fresh_mark="78268.1",
            demo_post_function=fake_demo_post,
        )
    )

    assert_test(
        "EXACT_OLD_SHORT_FAILURE_STATUS_BLOCKED",
        result["status"]
        == "JIT_DEMO_TRIGGER_VALIDATION_BLOCKED",
        result,
    )

    assert_test(
        "EXACT_OLD_SHORT_FAILURE_REASON",
        result["reason"]
        == "JIT_SHORT_TRIGGER_STALE_OR_CROSSED",
        result,
    )

    assert_test(
        "EXACT_OLD_SHORT_FAILURE_ZERO_POST",
        state.demo_post_count == 0,
        {
            "demo_post_count":
                state.demo_post_count
        },
    )

    assert_test(
        "EXACT_OLD_SHORT_FAILURE_ZERO_PREPARED_JOURNAL",
        state.prepared_journal_count == 0,
        {
            "prepared_journal_count":
                state.prepared_journal_count
        },
    )

    assert_test(
        "EXACT_OLD_SHORT_FAILURE_REEVALUATION_TRUE",
        result["wait_for_reevaluation"] is True,
        result,
    )


def test_valid_short_allows_dispatch():
    """
    Valid SHORT:

        TP < mark < SL

        78287.5 < 78300.0 < 78692.4
    """

    state = TestDispatchState()

    result = (
        guarded_demo_dispatch(
            state=state,
            symbol="BTCUSDT",
            direction="SHORT",
            quantity="0.0004",
            take_profit="78287.5",
            stop_loss="78692.4",
            fresh_mark="78300.0",
            demo_post_function=fake_demo_post,
        )
    )

    assert_test(
        "VALID_SHORT_DISPATCH_PERMITTED",
        result["status"]
        == "DEMO_DISPATCH_PERMITTED",
        result,
    )

    assert_test(
        "VALID_SHORT_JIT_REASON",
        result["reason"]
        == "JIT_SHORT_TRIGGERS_VALID",
        result,
    )

    assert_test(
        "VALID_SHORT_ONE_PREPARED_JOURNAL",
        state.prepared_journal_count == 1,
        {
            "prepared_journal_count":
                state.prepared_journal_count
        },
    )

    assert_test(
        "VALID_SHORT_ONE_DEMO_POST",
        state.demo_post_count == 1,
        {
            "demo_post_count":
                state.demo_post_count
        },
    )


def test_short_tp_exact_touch_blocks():
    state = TestDispatchState()

    result = (
        guarded_demo_dispatch(
            state=state,
            symbol="BTCUSDT",
            direction="SHORT",
            quantity="0.0004",
            take_profit="78287.5",
            stop_loss="78692.4",
            fresh_mark="78287.5",
            demo_post_function=fake_demo_post,
        )
    )

    assert_test(
        "SHORT_TP_TOUCH_BLOCKS_DISPATCH",
        result["ok"] is False,
        result,
    )

    assert_test(
        "SHORT_TP_TOUCH_ZERO_POST",
        state.demo_post_count == 0,
    )

    assert_test(
        "SHORT_TP_TOUCH_ZERO_PREPARED",
        state.prepared_journal_count == 0,
    )


def test_short_sl_exact_touch_blocks():
    state = TestDispatchState()

    result = (
        guarded_demo_dispatch(
            state=state,
            symbol="BTCUSDT",
            direction="SHORT",
            quantity="0.0004",
            take_profit="78287.5",
            stop_loss="78692.4",
            fresh_mark="78692.4",
            demo_post_function=fake_demo_post,
        )
    )

    assert_test(
        "SHORT_SL_TOUCH_BLOCKS_DISPATCH",
        result["ok"] is False,
        result,
    )

    assert_test(
        "SHORT_SL_TOUCH_ZERO_POST",
        state.demo_post_count == 0,
    )

    assert_test(
        "SHORT_SL_TOUCH_ZERO_PREPARED",
        state.prepared_journal_count == 0,
    )


def test_valid_long_allows_dispatch():
    """
    LONG:

        SL < mark < TP

        77900 < 78200 < 78500
    """

    state = TestDispatchState()

    result = (
        guarded_demo_dispatch(
            state=state,
            symbol="BTCUSDT",
            direction="LONG",
            quantity="0.0004",
            take_profit="78500",
            stop_loss="77900",
            fresh_mark="78200",
            demo_post_function=fake_demo_post,
        )
    )

    assert_test(
        "VALID_LONG_DISPATCH_PERMITTED",
        result["status"]
        == "DEMO_DISPATCH_PERMITTED",
        result,
    )

    assert_test(
        "VALID_LONG_JIT_REASON",
        result["reason"]
        == "JIT_LONG_TRIGGERS_VALID",
        result,
    )

    assert_test(
        "VALID_LONG_ONE_PREPARED_JOURNAL",
        state.prepared_journal_count == 1,
    )

    assert_test(
        "VALID_LONG_ONE_DEMO_POST",
        state.demo_post_count == 1,
    )


def test_long_tp_crossed_blocks():
    state = TestDispatchState()

    result = (
        guarded_demo_dispatch(
            state=state,
            symbol="BTCUSDT",
            direction="LONG",
            quantity="0.0004",
            take_profit="78500",
            stop_loss="77900",
            fresh_mark="78510",
            demo_post_function=fake_demo_post,
        )
    )

    assert_test(
        "LONG_TP_CROSSED_BLOCKS",
        result["status"]
        == "JIT_DEMO_TRIGGER_VALIDATION_BLOCKED",
        result,
    )

    assert_test(
        "LONG_TP_CROSSED_ZERO_POST",
        state.demo_post_count == 0,
    )

    assert_test(
        "LONG_TP_CROSSED_ZERO_PREPARED",
        state.prepared_journal_count == 0,
    )


def test_long_sl_crossed_blocks():
    state = TestDispatchState()

    result = (
        guarded_demo_dispatch(
            state=state,
            symbol="BTCUSDT",
            direction="LONG",
            quantity="0.0004",
            take_profit="78500",
            stop_loss="77900",
            fresh_mark="77890",
            demo_post_function=fake_demo_post,
        )
    )

    assert_test(
        "LONG_SL_CROSSED_BLOCKS",
        result["status"]
        == "JIT_DEMO_TRIGGER_VALIDATION_BLOCKED",
        result,
    )

    assert_test(
        "LONG_SL_CROSSED_ZERO_POST",
        state.demo_post_count == 0,
    )

    assert_test(
        "LONG_SL_CROSSED_ZERO_PREPARED",
        state.prepared_journal_count == 0,
    )


def test_invalid_short_trigger_order_blocks():
    state = TestDispatchState()

    result = (
        guarded_demo_dispatch(
            state=state,
            symbol="BTCUSDT",
            direction="SHORT",
            quantity="0.0004",
            take_profit="78700",
            stop_loss="78200",
            fresh_mark="78300",
            demo_post_function=fake_demo_post,
        )
    )

    assert_test(
        "INVALID_SHORT_TRIGGER_ORDER_BLOCKED",
        result["reason"]
        == "JIT_SHORT_TRIGGER_ORDER_INVALID",
        result,
    )

    assert_test(
        "INVALID_SHORT_TRIGGER_ORDER_ZERO_POST",
        state.demo_post_count == 0,
    )

    assert_test(
        "INVALID_SHORT_TRIGGER_ORDER_ZERO_PREPARED",
        state.prepared_journal_count == 0,
    )


def test_invalid_long_trigger_order_blocks():
    state = TestDispatchState()

    result = (
        guarded_demo_dispatch(
            state=state,
            symbol="BTCUSDT",
            direction="LONG",
            quantity="0.0004",
            take_profit="77900",
            stop_loss="78700",
            fresh_mark="78300",
            demo_post_function=fake_demo_post,
        )
    )

    assert_test(
        "INVALID_LONG_TRIGGER_ORDER_BLOCKED",
        result["reason"]
        == "JIT_LONG_TRIGGER_ORDER_INVALID",
        result,
    )

    assert_test(
        "INVALID_LONG_TRIGGER_ORDER_ZERO_POST",
        state.demo_post_count == 0,
    )

    assert_test(
        "INVALID_LONG_TRIGGER_ORDER_ZERO_PREPARED",
        state.prepared_journal_count == 0,
    )


def run_all_tests():

    log(
        "-" * 100
    )

    log(
        f"{STAGE} PART 2 TESTABLE UNIT START"
    )

    log(
        "PURPOSE = GUARDED DEMO DISPATCH INTEGRATION"
    )

    log(
        "REAL EXCHANGE EXECUTION = NOT PRESENT"
    )

    log(
        "WEEX NETWORK POST = NOT PRESENT"
    )

    log(
        "TEST POST COUNTER ONLY"
    )

    log(
        "-" * 100
    )

    test_exact_old_short_failure_blocks_before_post()

    test_valid_short_allows_dispatch()

    test_short_tp_exact_touch_blocks()

    test_short_sl_exact_touch_blocks()

    test_valid_long_allows_dispatch()

    test_long_tp_crossed_blocks()

    test_long_sl_crossed_blocks()

    test_invalid_short_trigger_order_blocks()

    test_invalid_long_trigger_order_blocks()

    log(
        "-" * 100
    )

    log(
        "PASS: R36F15_4_PART2_GUARDED_DEMO_DISPATCH"
    )

    log(
        "PASS: JIT_VALIDATION_OCCURS_BEFORE_PREPARED_JOURNAL"
    )

    log(
        "PASS: JIT_VALIDATION_OCCURS_BEFORE_DEMO_POST"
    )

    log(
        "PASS: BLOCKED_CASE_WRITES_ZERO_PREPARED_JOURNAL"
    )

    log(
        "PASS: BLOCKED_CASE_ATTEMPTS_ZERO_DEMO_POST"
    )

    log(
        "PASS: VALID_SHORT_REACHES_DISPATCH_PATH"
    )

    log(
        "PASS: VALID_LONG_REACHES_DISPATCH_PATH"
    )

    log(
        "PASS: EXACT_R36F15_3_FAILURE_BLOCKED_BEFORE_POST"
    )

    log(
        f"{STAGE} PART 2 FINAL STATUS = PASS"
    )

    log(
        "-" * 100
    )


if __name__ == "__main__":
    run_all_tests()
