
#!/usr/bin/env python3
"""
R36F.15.4.1 - TELEGRAM DEMO EVENT NOTIFICATION TESTABLE UNIT

PURPOSE
-------
Test the notification layer that will later be merged into the proven
R36F.15.4 bot.

THIS UNIT DOES NOT:
- Send a WEEX real order
- Send a WEEX demo order
- Change leverage
- Change margin mode
- Change positions
- Write a production trading journal

DEFAULT TELEGRAM MODE
---------------------
Fake/local Telegram sender only.

Optional:
Set R36F1541_REAL_TELEGRAM_TEST=true
to send harmless TEST notifications through the existing Telegram bot.

Environment variables used for optional real Telegram test:
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID

Expected final result:
R36F.15.4.1 SINGLE TESTABLE UNIT FINAL STATUS = PASS
"""

import os
import json
import hashlib
import urllib.parse
import urllib.request
from datetime import datetime, timezone


STAGE = "R36F.15.4.1"

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False

REAL_TELEGRAM_TEST = (
    os.getenv("R36F1541_REAL_TELEGRAM_TEST", "false")
    .strip()
    .lower()
    == "true"
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

_SENT_NOTIFICATION_KEYS = set()
_TEST_RESULTS = []


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def log(message):
    print(f"{now_iso()} {message}", flush=True)


def pass_check(name, detail=""):
    _TEST_RESULTS.append((name, True))
    log(f"PASS: {name}")
    if detail:
        log(f"      {detail}")


def fail_check(name, detail=""):
    _TEST_RESULTS.append((name, False))
    log(f"FAIL: {name}")
    if detail:
        log(f"      {detail}")


def stable_notification_key(event_name, direction, reason, cycle_id):
    raw = "|".join(
        [
            str(event_name),
            str(direction),
            str(reason),
            str(cycle_id),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def telegram_send_real(message):
    if not TELEGRAM_BOT_TOKEN:
        return {
            "attempted": False,
            "sent": False,
            "reason": "TELEGRAM_BOT_TOKEN_MISSING",
        }

    if not TELEGRAM_CHAT_ID:
        return {
            "attempted": False,
            "sent": False,
            "reason": "TELEGRAM_CHAT_ID_MISSING",
        }

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    data = urllib.parse.urlencode(
        {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")

    try:
        request = urllib.request.Request(
            url,
            data=data,
            method="POST",
        )

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:
            body = response.read().decode(
                "utf-8",
                errors="replace",
            )

            status = response.getcode()

        return {
            "attempted": True,
            "sent": 200 <= status < 300,
            "http_status": status,
            "response_preview": body[:300],
        }

    except Exception as exc:
        return {
            "attempted": True,
            "sent": False,
            "reason": f"{type(exc).__name__}: {exc}",
        }


def telegram_send_fake(message):
    log("------------------------------------------------------------")
    log("R36F.15.4.1 TEST TELEGRAM MESSAGE")
    print(message, flush=True)
    log("------------------------------------------------------------")

    return {
        "attempted": True,
        "sent": True,
        "mode": "FAKE_LOCAL_TEST",
    }


def telegram_send(message):
    if REAL_TELEGRAM_TEST:
        return telegram_send_real(message)

    return telegram_send_fake(message)


def build_notification_message(
    event_name,
    direction,
    ema_direction,
    tp_approved,
    command_authorized,
    jit_status,
    demo_order_status,
    reason,
    fresh_mark=None,
    tp=None,
    sl=None,
):
    lines = [
        f"{STAGE} | {event_name}",
        "",
        f"Direction: {direction}",
        f"EMA direction: {ema_direction}",
        f"TP clusters approved: {tp_approved}",
        f"Telegram command authorized: {command_authorized}",
        f"JIT trigger validation: {jit_status}",
        f"Demo order status: {demo_order_status}",
        f"Reason: {reason}",
    ]

    if fresh_mark is not None:
        lines.append(f"Fresh mark: {fresh_mark}")

    if tp is not None:
        lines.append(f"TP: {tp}")

    if sl is not None:
        lines.append(f"SL: {sl}")

    lines.extend(
        [
            "",
            "Production real-money execution remains disabled.",
        ]
    )

    return "\n".join(lines)


def notify_demo_event(
    *,
    event_name,
    direction,
    ema_direction,
    tp_approved,
    command_authorized,
    jit_status,
    demo_order_status,
    reason,
    cycle_id,
    fresh_mark=None,
    tp=None,
    sl=None,
):
    key = stable_notification_key(
        event_name,
        direction,
        reason,
        cycle_id,
    )

    if key in _SENT_NOTIFICATION_KEYS:
        result = {
            "attempted": False,
            "sent": False,
            "deduplicated": True,
            "reason": "DUPLICATE_NOTIFICATION_BLOCKED",
            "key": key,
        }

        log(
            "R36F.15.4.1 TELEGRAM EVENT RESULT = "
            + json.dumps(
                result,
                separators=(",", ":"),
                sort_keys=True,
            )
        )

        return result

    message = build_notification_message(
        event_name=event_name,
        direction=direction,
        ema_direction=ema_direction,
        tp_approved=tp_approved,
        command_authorized=command_authorized,
        jit_status=jit_status,
        demo_order_status=demo_order_status,
        reason=reason,
        fresh_mark=fresh_mark,
        tp=tp,
        sl=sl,
    )

    result = telegram_send(message)

    if result.get("sent"):
        _SENT_NOTIFICATION_KEYS.add(key)

    result["deduplicated"] = False
    result["key"] = key
    result["event_name"] = event_name

    log(
        "R36F.15.4.1 TELEGRAM EVENT RESULT = "
        + json.dumps(
            result,
            separators=(",", ":"),
            sort_keys=True,
        )
    )

    return result


def evaluate_notification_event(snapshot):
    direction = snapshot["direction"]
    ema_direction = snapshot["ema_direction"]
    tp_approved = bool(snapshot["tp_approved"])
    command_authorized = bool(
        snapshot["command_authorized"]
    )

    jit_status = snapshot.get(
        "jit_status",
        "NOT_REACHED",
    )

    demo_order_status = snapshot.get(
        "demo_order_status",
        "NOT_ATTEMPTED",
    )

    reason = snapshot.get(
        "reason",
        "NONE",
    )

    if direction != ema_direction:
        return "COMMAND_DIRECTION_MISMATCH"

    if not tp_approved:
        return "TP_APPROVAL_WAITING"

    if not command_authorized:
        return "COMMAND_NOT_AUTHORIZED"

    if jit_status == "PASSED":
        if demo_order_status == "ACCEPTED":
            return "DEMO_ORDER_ACCEPTED"

        if demo_order_status == "REJECTED":
            return "DEMO_ORDER_REJECTED"

        return "DEMO_TRADE_READY"

    if jit_status == "BLOCKED":
        return "JIT_TRIGGER_BLOCKED"

    return "DEMO_TRADE_READY"


def process_snapshot(snapshot):
    event_name = evaluate_notification_event(snapshot)

    return notify_demo_event(
        event_name=event_name,
        direction=snapshot["direction"],
        ema_direction=snapshot["ema_direction"],
        tp_approved=snapshot["tp_approved"],
        command_authorized=snapshot[
            "command_authorized"
        ],
        jit_status=snapshot.get(
            "jit_status",
            "NOT_REACHED",
        ),
        demo_order_status=snapshot.get(
            "demo_order_status",
            "NOT_ATTEMPTED",
        ),
        reason=snapshot.get(
            "reason",
            "NONE",
        ),
        cycle_id=snapshot["cycle_id"],
        fresh_mark=snapshot.get("fresh_mark"),
        tp=snapshot.get("tp"),
        sl=snapshot.get("sl"),
    )


def test_long_waiting_for_second_cluster():
    snapshot = {
        "cycle_id": "TEST_LONG_CLUSTER_WAIT",
        "direction": "LONG",
        "ema_direction": "LONG",
        "tp_approved": False,
        "command_authorized": False,
        "jit_status": "NOT_REACHED",
        "demo_order_status": "NOT_ATTEMPTED",
        "reason": "ONLY_ONE_VALID_CLUSTER",
    }

    event = evaluate_notification_event(snapshot)

    if event == "TP_APPROVAL_WAITING":
        pass_check(
            "LONG_ONE_CLUSTER_NOTIFICATION_STATE",
            event,
        )
    else:
        fail_check(
            "LONG_ONE_CLUSTER_NOTIFICATION_STATE",
            event,
        )


def test_long_trade_ready():
    snapshot = {
        "cycle_id": "TEST_LONG_READY",
        "direction": "LONG",
        "ema_direction": "LONG",
        "tp_approved": True,
        "command_authorized": True,
        "jit_status": "PASSED",
        "demo_order_status": "NOT_ATTEMPTED",
        "reason": "ALL_AUTHORIZATION_GATES_PASSED",
        "fresh_mark": "78200.0",
        "tp": "78500.0",
        "sl": "77900.0",
    }

    result = process_snapshot(snapshot)

    if result.get("sent"):
        pass_check(
            "LONG_READY_TELEGRAM_NOTIFICATION_SENT"
        )
    else:
        fail_check(
            "LONG_READY_TELEGRAM_NOTIFICATION_SENT",
            str(result),
        )


def test_jit_blocked():
    snapshot = {
        "cycle_id": "TEST_JIT_BLOCK",
        "direction": "SHORT",
        "ema_direction": "SHORT",
        "tp_approved": True,
        "command_authorized": True,
        "jit_status": "BLOCKED",
        "demo_order_status": "NOT_ATTEMPTED",
        "reason": "JIT_SHORT_TRIGGER_STALE_OR_CROSSED",
        "fresh_mark": "78268.1",
        "tp": "78287.5",
        "sl": "78692.4",
    }

    event = evaluate_notification_event(snapshot)

    result = process_snapshot(snapshot)

    if (
        event == "JIT_TRIGGER_BLOCKED"
        and result.get("sent")
    ):
        pass_check(
            "JIT_BLOCKED_TELEGRAM_NOTIFICATION"
        )
    else:
        fail_check(
            "JIT_BLOCKED_TELEGRAM_NOTIFICATION",
            f"event={event} result={result}",
        )


def test_demo_order_accepted():
    snapshot = {
        "cycle_id": "TEST_DEMO_ACCEPTED",
        "direction": "LONG",
        "ema_direction": "LONG",
        "tp_approved": True,
        "command_authorized": True,
        "jit_status": "PASSED",
        "demo_order_status": "ACCEPTED",
        "reason": "WEEX_DEMO_ORDER_ACCEPTED",
        "fresh_mark": "78200.0",
        "tp": "78500.0",
        "sl": "77900.0",
    }

    event = evaluate_notification_event(snapshot)

    result = process_snapshot(snapshot)

    if (
        event == "DEMO_ORDER_ACCEPTED"
        and result.get("sent")
    ):
        pass_check(
            "DEMO_ORDER_ACCEPTED_NOTIFICATION"
        )
    else:
        fail_check(
            "DEMO_ORDER_ACCEPTED_NOTIFICATION",
            f"event={event} result={result}",
        )


def test_demo_order_rejected():
    snapshot = {
        "cycle_id": "TEST_DEMO_REJECTED",
        "direction": "LONG",
        "ema_direction": "LONG",
        "tp_approved": True,
        "command_authorized": True,
        "jit_status": "PASSED",
        "demo_order_status": "REJECTED",
        "reason": "WEEX_DEMO_ORDER_REJECTED",
        "fresh_mark": "78200.0",
        "tp": "78500.0",
        "sl": "77900.0",
    }

    event = evaluate_notification_event(snapshot)

    result = process_snapshot(snapshot)

    if (
        event == "DEMO_ORDER_REJECTED"
        and result.get("sent")
    ):
        pass_check(
            "DEMO_ORDER_REJECTED_NOTIFICATION"
        )
    else:
        fail_check(
            "DEMO_ORDER_REJECTED_NOTIFICATION",
            f"event={event} result={result}",
        )


def test_notification_deduplication():
    snapshot = {
        "cycle_id": "TEST_DEDUPE_001",
        "direction": "LONG",
        "ema_direction": "LONG",
        "tp_approved": True,
        "command_authorized": True,
        "jit_status": "PASSED",
        "demo_order_status": "NOT_ATTEMPTED",
        "reason": "ALL_AUTHORIZATION_GATES_PASSED",
    }

    first = process_snapshot(snapshot)
    second = process_snapshot(snapshot)

    if (
        first.get("sent")
        and second.get("deduplicated")
        and not second.get("attempted")
    ):
        pass_check(
            "TELEGRAM_EVENT_DEDUPLICATION"
        )
    else:
        fail_check(
            "TELEGRAM_EVENT_DEDUPLICATION",
            f"first={first} second={second}",
        )


def test_real_money_firebreak():
    good = (
        REAL_ORDER_EXECUTION is False
        and DEMO_ORDER_EXECUTION is False
        and EXCHANGE_MUTATION_TRANSPORT_ENABLED
        is False
        and ORDER_SUBMISSION_ENABLED is False
    )

    if good:
        pass_check(
            "REAL_MONEY_ZERO_WRITE_INVARIANTS"
        )
    else:
        fail_check(
            "REAL_MONEY_ZERO_WRITE_INVARIANTS"
        )


def main():
    log(
        "============================================================"
    )

    log(
        "R36F.15.4.1: TELEGRAM DEMO EVENT "
        "NOTIFICATION TESTABLE UNIT"
    )

    log(
        "============================================================"
    )

    log(
        f"REAL_TELEGRAM_TEST = {REAL_TELEGRAM_TEST}"
    )

    log(
        "WEEX REAL ORDER EXECUTION = DISABLED"
    )

    log(
        "WEEX DEMO ORDER EXECUTION = DISABLED"
    )

    log(
        "EXCHANGE MUTATION TRANSPORT = DISABLED"
    )

    test_real_money_firebreak()
    test_long_waiting_for_second_cluster()
    test_long_trade_ready()
    test_jit_blocked()
    test_demo_order_accepted()
    test_demo_order_rejected()
    test_notification_deduplication()

    failures = [
        name
        for name, passed in _TEST_RESULTS
        if not passed
    ]

    log(
        "------------------------------------------------------------"
    )

    if failures:
        log(
            "R36F.15.4.1 SINGLE TESTABLE UNIT "
            "FINAL STATUS = FAIL"
        )

        log(
            "FAILURES = "
            + json.dumps(failures)
        )

        raise SystemExit(1)

    log(
        "PASS: R36F1541_TELEGRAM_EVENT_ENGINE"
    )

    log(
        "PASS: R36F1541_READY_EVENT_NOTIFICATION"
    )

    log(
        "PASS: R36F1541_JIT_BLOCK_NOTIFICATION"
    )

    log(
        "PASS: R36F1541_ACCEPTED_REJECTED_NOTIFICATION"
    )

    log(
        "PASS: R36F1541_NOTIFICATION_DEDUPLICATION"
    )

    log(
        "PASS: R36F1541_ZERO_WEEX_WRITE"
    )

    log(
        "R36F.15.4.1 SINGLE TESTABLE UNIT "
        "FINAL STATUS = PASS"
    )

    log(
        "------------------------------------------------------------"
    )


if __name__ == "__main__":
    main()
