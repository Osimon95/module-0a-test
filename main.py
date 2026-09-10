
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
