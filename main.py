
#!/usr/bin/env python3

"""
R36F.15.4 - PART 1 TESTABLE UNIT
JIT DEMO TRIGGER VALIDATION

PURPOSE
-------
Test only the new R36F.15.4 Just-In-Time trigger validation.

NO DEMO ORDER POST IS PERFORMED HERE.
NO PREPARED JOURNAL IS WRITTEN HERE.
NO REAL ORDER IS POSSIBLE HERE.

SHORT VALID:
    TP < fresh_mark < SL

LONG VALID:
    SL < fresh_mark < TP

If the fresh WEEX mark price has already crossed either trigger,
the validation must block before demo dispatch.

Required regression case:

    direction = SHORT
    fresh_mark = 78268.1
    TP = 78287.5
    SL = 78692.4

Expected:
    BLOCKED

because:

    78287.5 < 78268.1 < 78692.4

is FALSE.
"""

import json
import time
from decimal import Decimal, InvalidOperation

import requests


STAGE = "R36F.15.4"
PUBLIC_SYMBOL = "cmt_btcusdt"

WEEX_CONTRACT_BASE_URL = "https://api-contract.weex.com"

TICKER_PATH = "/capi/v2/market/ticker"

HTTP_TIMEOUT_SECONDS = 10


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


def fetch_fresh_weex_mark_price(
    symbol=PUBLIC_SYMBOL,
    timeout=HTTP_TIMEOUT_SECONDS,
):
    """
    Fetch a fresh WEEX mark price immediately before
    demo dispatch.

    Public read only.
    No authentication.
    No exchange mutation.
    """

    url = (
        WEEX_CONTRACT_BASE_URL
        + TICKER_PATH
    )

    response = requests.get(
        url,
        params={
            "symbol": symbol,
        },
        timeout=timeout,
    )

    if response.status_code != 200:
        raise RuntimeError(
            "JIT_MARK_PRICE_HTTP_FAILED "
            f"status={response.status_code} "
            f"body={response.text[:500]}"
        )

    try:
        payload = response.json()
    except Exception as exc:
        raise RuntimeError(
            "JIT_MARK_PRICE_JSON_FAILED "
            f"body={response.text[:500]}"
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError(
            "JIT_MARK_PRICE_RESPONSE_NOT_DICT "
            f"payload={payload!r}"
        )

    mark_price_raw = payload.get("markPrice")

    if mark_price_raw in (
        None,
        "",
    ):
        raise RuntimeError(
            "JIT_MARK_PRICE_MISSING "
            f"payload={payload!r}"
        )

    mark_price = D(mark_price_raw)

    if mark_price <= 0:
        raise RuntimeError(
            "JIT_MARK_PRICE_NON_POSITIVE "
            f"mark_price={mark_price}"
        )

    return mark_price


def validate_jit_demo_triggers(
    direction,
    fresh_mark,
    take_profit,
    stop_loss,
):
    """
    Core R36F.15.4 validation.

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


def jit_demo_trigger_validation(
    direction,
    take_profit,
    stop_loss,
    fresh_mark_override=None,
):
    """
    Public wrapper.

    Production-style path:
        fetch fresh mark from WEEX.

    Test path:
        fresh_mark_override supplied.

    This function NEVER posts an order.
    """

    if fresh_mark_override is None:

        fresh_mark = (
            fetch_fresh_weex_mark_price()
        )

        mark_source = "WEEX_FRESH_MARK"

    else:

        fresh_mark = D(
            fresh_mark_override
        )

        mark_source = "TEST_OVERRIDE"

    result = (
        validate_jit_demo_triggers(
            direction=direction,
            fresh_mark=fresh_mark,
            take_profit=take_profit,
            stop_loss=stop_loss,
        )
    )

    result["mark_source"] = mark_source

    log(
        f"{STAGE} JIT DEMO TRIGGER VALIDATION = "
        + json.dumps(
            result,
            separators=(",", ":"),
        )
    )

    return result


def assert_test(
    name,
    condition,
    result=None,
):
    if condition:

        log(
            f"PASS: {name}"
        )

        return

    log(
        f"FAIL: {name}"
    )

    if result is not None:
        log(
            "FAILED RESULT = "
            + json.dumps(
                result,
                separators=(",", ":"),
            )
        )

    raise AssertionError(name)


def run_short_stale_regression_test():
    """
    Exact R36F.15.3 failure condition.

    Fresh mark is already below SHORT TP.

    SHORT requires:

        TP < mark < SL

    78287.5 < 78268.1 < 78692.4

    must therefore BLOCK.
    """

    result = (
        jit_demo_trigger_validation(
            direction="SHORT",
            fresh_mark_override="78268.1",
            take_profit="78287.5",
            stop_loss="78692.4",
        )
    )

    assert_test(
        "SHORT_STALE_REGRESSION_BLOCKED",
        result["valid"] is False,
        result,
    )

    assert_test(
        "SHORT_STALE_REGRESSION_REASON",
        result["reason"]
        == "JIT_SHORT_TRIGGER_STALE_OR_CROSSED",
        result,
    )


def run_short_valid_test():
    """
    Fresh mark above SHORT TP and below SHORT SL.
    """

    result = (
        jit_demo_trigger_validation(
            direction="SHORT",
            fresh_mark_override="78300.0",
            take_profit="78287.5",
            stop_loss="78692.4",
        )
    )

    assert_test(
        "SHORT_VALID_APPROVED",
        result["valid"] is True,
        result,
    )

    assert_test(
        "SHORT_VALID_REASON",
        result["reason"]
        == "JIT_SHORT_TRIGGERS_VALID",
        result,
    )


def run_short_sl_crossed_test():
    """
    Fresh mark has reached/passed SHORT stop loss.
    """

    result = (
        jit_demo_trigger_validation(
            direction="SHORT",
            fresh_mark_override="78692.4",
            take_profit="78287.5",
            stop_loss="78692.4",
        )
    )

    assert_test(
        "SHORT_SL_CROSSED_BLOCKED",
        result["valid"] is False,
        result,
    )


def run_short_tp_exact_touch_test():
    """
    Exact TP touch must block.

    Strict condition is:

        TP < mark

    not:

        TP <= mark
    """

    result = (
        jit_demo_trigger_validation(
            direction="SHORT",
            fresh_mark_override="78287.5",
            take_profit="78287.5",
            stop_loss="78692.4",
        )
    )

    assert_test(
        "SHORT_TP_EXACT_TOUCH_BLOCKED",
        result["valid"] is False,
        result,
    )


def run_long_valid_test():
    """
    LONG requires:

        SL < mark < TP
    """

    result = (
        jit_demo_trigger_validation(
            direction="LONG",
            fresh_mark_override="78200.0",
            take_profit="78500.0",
            stop_loss="77900.0",
        )
    )

    assert_test(
        "LONG_VALID_APPROVED",
        result["valid"] is True,
        result,
    )

    assert_test(
        "LONG_VALID_REASON",
        result["reason"]
        == "JIT_LONG_TRIGGERS_VALID",
        result,
    )


def run_long_tp_crossed_test():

    result = (
        jit_demo_trigger_validation(
            direction="LONG",
            fresh_mark_override="78500.0",
            take_profit="78500.0",
            stop_loss="77900.0",
        )
    )

    assert_test(
        "LONG_TP_CROSSED_BLOCKED",
        result["valid"] is False,
        result,
    )


def run_long_sl_crossed_test():

    result = (
        jit_demo_trigger_validation(
            direction="LONG",
            fresh_mark_override="77900.0",
            take_profit="78500.0",
            stop_loss="77900.0",
        )
    )

    assert_test(
        "LONG_SL_CROSSED_BLOCKED",
        result["valid"] is False,
        result,
    )


def run_invalid_short_trigger_order_test():

    result = (
        jit_demo_trigger_validation(
            direction="SHORT",
            fresh_mark_override="78300",
            take_profit="78700",
            stop_loss="78200",
        )
    )

    assert_test(
        "SHORT_INVALID_TRIGGER_ORDER_BLOCKED",
        result["valid"] is False,
        result,
    )

    assert_test(
        "SHORT_INVALID_TRIGGER_ORDER_REASON",
        result["reason"]
        == "JIT_SHORT_TRIGGER_ORDER_INVALID",
        result,
    )


def run_invalid_long_trigger_order_test():

    result = (
        jit_demo_trigger_validation(
            direction="LONG",
            fresh_mark_override="78300",
            take_profit="77900",
            stop_loss="78700",
        )
    )

    assert_test(
        "LONG_INVALID_TRIGGER_ORDER_BLOCKED",
        result["valid"] is False,
        result,
    )

    assert_test(
        "LONG_INVALID_TRIGGER_ORDER_REASON",
        result["reason"]
        == "JIT_LONG_TRIGGER_ORDER_INVALID",
        result,
    )


def run_all_deterministic_tests():

    log(
        "-" * 100
    )

    log(
        f"{STAGE} PART 1 TESTABLE UNIT START"
    )

    log(
        "REAL ORDER EXECUTION = DISABLED"
    )

    log(
        "DEMO ORDER POST = DISABLED IN THIS UNIT"
    )

    log(
        "PREPARED JOURNAL WRITE = DISABLED IN THIS UNIT"
    )

    log(
        "-" * 100
    )

    run_short_stale_regression_test()

    run_short_valid_test()

    run_short_sl_crossed_test()

    run_short_tp_exact_touch_test()

    run_long_valid_test()

    run_long_tp_crossed_test()

    run_long_sl_crossed_test()

    run_invalid_short_trigger_order_test()

    run_invalid_long_trigger_order_test()

    log(
        "-" * 100
    )

    log(
        "PASS: R36F15_4_PART1_JIT_VALIDATION"
    )

    log(
        "PASS: EXACT_R36F15_3_SHORT_FAILURE_NOW_BLOCKED"
    )

    log(
        "PASS: SHORT_VALID_CASE_APPROVED"
    )

    log(
        "PASS: LONG_VALID_CASE_APPROVED"
    )

    log(
        "PASS: STALE_OR_CROSSED_TRIGGER_CASES_BLOCKED"
    )

    log(
        "ZERO ORDER POST: PASS"
    )

    log(
        "ZERO JOURNAL WRITE: PASS"
    )

    log(
        f"{STAGE} PART 1 FINAL STATUS = PASS"
    )

    log(
        "-" * 100
    )


if __name__ == "__main__":
    run_all_deterministic_tests()

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
