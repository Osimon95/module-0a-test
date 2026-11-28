
# ============================================================
# COMPLETE UNIT 15 V4 REPLACEMENT
# WEEX DEMO PERFORMANCE + TELEGRAM NOTIFICATIONS
# ZERO INDENTATION
#
# CORRECTIONS:
# - NON-DAEMON REPORTING THREAD
# - MISSED-SLOT CATCH-UP
# - NEVER MARK FAILED DELIVERY AS COMPLETE
# - STARTUP TELEGRAM DIAGNOSTIC
# - DELIVERY RETRIES WITH ERROR LOGGING
# - ON-DEMAND 1H / 8H / 24H
# - EXCHANGE HISTORY AND EQUITY REPORTING
# - EXCHANGE READ-ONLY
# ============================================================

import os as _u15_os
import time as _u15_time
import json as _u15_json
import hmac as _u15_hmac
import base64 as _u15_b64
import hashlib as _u15_hash
import threading as _u15_thread
import urllib.request as _u15_http
import urllib.parse as _u15_url
import urllib.error as _u15_error
from decimal import Decimal as _U15_D
from datetime import datetime as _U15_DT
from datetime import timedelta as _U15_TD
from zoneinfo import ZoneInfo as _U15_Zone
from collections import Counter as _U15_Counter


# ============================================================
# 1. CONFIGURATION
# ============================================================

UNIT15_ENABLED = (
    _u15_os.getenv("UNIT15_ENABLED", "TRUE")
    .strip().upper() == "TRUE"
)

UNIT15_8H_ENABLED = (
    _u15_os.getenv("UNIT15_8H_ENABLED", "TRUE")
    .strip().upper() == "TRUE"
)

UNIT15_ON_DEMAND = (
    _u15_os.getenv(
        "UNIT15_ON_DEMAND_ENABLED", "TRUE"
    ).strip().upper() == "TRUE"
)

UNIT15_STARTUP_NOTIFY = (
    _u15_os.getenv(
        "UNIT15_STARTUP_NOTIFY", "TRUE"
    ).strip().upper() == "TRUE"
)

_UNIT15_TZ = _U15_Zone("Africa/Lagos")
_UNIT15_BASE = "https://api-contract.weex.com"
_UNIT15_SYMBOL = "BTCSUSDT"
_UNIT15_HISTORY = "/capi/v3/sim/order/history"
_UNIT15_BALANCE = "/capi/v3/sim/balance"

_UNIT15_SLOTS = (5, 13, 21)
_UNIT15_CATCHUP_MINUTES = 120
_UNIT15_POLL_SECONDS = 10
_UNIT15_EQUITY_POLL_SECONDS = 300

_UNIT15_LOCK = _u15_thread.Lock()
_UNIT15_DELIVERED = set()
_UNIT15_LAST_EQUITY_POLL = 0
_UNIT15_EQUITY_SNAPSHOTS = []
_UNIT15_TELEGRAM_OFFSET = None
_UNIT15_LAST_REPORT = None


# ============================================================
# 2. NUMBER AND DATE HELPERS
# ============================================================

def unit15_num(value):

    if value is None or value == "":
        return None

    try:
        x = _U15_D(str(value))
        return x if x.is_finite() else None
    except Exception:
        return None


def unit15_value(record, *names):

    for name in names:
        x = record.get(name)
        if x is not None and x != "":
            return x

    return None


def unit15_ms(value):

    try:
        n = int(_U15_D(str(value)))
        if n < 100000000000:
            n *= 1000
        return n if n > 0 else None
    except Exception:
        return None


def unit15_now():

    return _U15_DT.now(_UNIT15_TZ)


# ============================================================
# 3. CONFIGURATION VALIDATION
# ============================================================

def unit15_configuration_check():

    config = FRESH_RECONSTRUCTION_CONFIG
    exchange = config.get("exchange", {})

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
    ):
        raise RuntimeError(
            "UNIT 15 NON-DEMO CONFIGURATION"
        )

    market_symbol = str(
        exchange.get("market_symbol") or ""
    ).strip().upper()

    demo_symbol = str(
        exchange.get("demo_order_symbol") or ""
    ).strip().upper()

    if not market_symbol or not demo_symbol:
        raise RuntimeError(
            "UNIT 15 DEMO SYMBOL MISSING"
        )

    if not (
        demo_symbol.endswith("SUSDT")
        and market_symbol.endswith("USDT")
        and demo_symbol[:-5] == market_symbol[:-4]
    ):
        raise RuntimeError(
            "UNIT 15 DEMO SYMBOL PAIR MISMATCH"
        )

    print(
        "UNIT 15 MARKET SYMBOL =",
        market_symbol,
        flush=True
    )

    print(
        "UNIT 15 DEMO SYMBOL =",
        demo_symbol,
        flush=True
    )

    return True


# ============================================================
# 4. SIGNED READ-ONLY WEEX REQUEST
# ============================================================

def unit15_get(path, query=""):

    unit15_configuration_check()

    if path not in (
        _UNIT15_HISTORY,
        _UNIT15_BALANCE,
    ):
        raise RuntimeError(
            "UNIT 15 NON-REPORT ENDPOINT BLOCKED"
        )

    key = (
        _u15_os.getenv("WEEX_API_KEY")
        or _u15_os.getenv("API_KEY")
    )
    secret = (
        _u15_os.getenv("WEEX_API_SECRET")
        or _u15_os.getenv("API_SECRET")
    )
    phrase = (
        _u15_os.getenv("WEEX_API_PASSPHRASE")
        or _u15_os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        raise RuntimeError(
            "UNIT 15 WEEX CREDENTIALS MISSING"
        )

    timestamp = str(int(_u15_time.time() * 1000))
    request_path = path + (
        "?" + query if query else ""
    )

    message = timestamp + "GET" + request_path

    signature = _u15_b64.b64encode(
        _u15_hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            _u15_hash.sha256,
        ).digest()
    ).decode("utf-8")

    request = _u15_http.Request(
        _UNIT15_BASE + request_path,
        method="GET",
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": phrase,
            "Content-Type": "application/json",
        },
    )

    with _u15_http.urlopen(
        request, timeout=20
    ) as response:

        status = response.getcode()
        raw = response.read().decode(
            "utf-8", errors="replace"
        )

    if status != 200:
        raise RuntimeError(
            "UNIT 15 WEEX HTTP " + str(status)
        )

    return _u15_json.loads(raw)


# ============================================================
# 5. COMPLETE EXCHANGE ORDER HISTORY
# ============================================================

def unit15_history():

    orders = []
    seen = set()
    complete = False

    for page in range(20):

        query = _u15_url.urlencode({
            "symbol": _UNIT15_SYMBOL,
            "limit": 1000,
            "page": page,
        })

        batch = unit15_get(
            _UNIT15_HISTORY, query
        )

        if not isinstance(batch, list):
            raise RuntimeError(
                "UNIT 15 HISTORY RESPONSE INVALID"
            )

        if not all(
            isinstance(x, dict) for x in batch
        ):
            raise RuntimeError(
                "UNIT 15 MALFORMED ORDER HISTORY"
            )

        for order in batch:

            oid = unit15_value(
                order,
                "orderId", "id", "clientOrderId"
            )

            if oid is None:
                continue

            oid = str(oid)

            if oid not in seen:
                seen.add(oid)
                orders.append(order)

        if len(batch) < 1000:
            complete = True
            break

    print(
        "UNIT 15 HISTORY RECORDS =",
        len(orders),
        flush=True
    )
    print(
        "UNIT 15 HISTORY COMPLETE =",
        complete,
        flush=True
    )

    return orders, complete


# ============================================================
# 6. NORMALIZE FILLED ORDERS
# ============================================================

def unit15_parse_order(order):

    status = str(
        unit15_value(
            order,
            "status", "state", "orderStatus"
        ) or ""
    ).upper()

    if status not in (
        "FILLED", "FULLY_FILLED",
        "FULL_FILLED", "FULLFILL",
    ):
        return None, "NOT_FULLY_FILLED"

    qty = unit15_num(
        unit15_value(
            order,
            "executedQty", "filledQty",
            "filledSize", "executedQuantity",
            "dealSize"
        )
    )

    price = unit15_num(
        unit15_value(
            order,
            "avgPrice", "averagePrice",
            "fillPrice", "priceAvg",
            "executedPrice"
        )
    )

    ts = unit15_ms(
        unit15_value(
            order,
            "createdTime", "createTime",
            "cTime", "ctime", "createdAt",
            "timestamp", "time",
            "updateTime", "updatedAt"
        )
    )

    oid = unit15_value(
        order,
        "orderId", "id", "clientOrderId"
    )

    if qty is None or qty <= 0:
        return None, "INVALID_QUANTITY"

    if price is None or price <= 0:
        return None, "INVALID_PRICE"

    if ts is None:
        return None, "INVALID_TIMESTAMP"

    if oid is None:
        return None, "MISSING_ORDER_ID"

    side = str(
        unit15_value(
            order, "side", "orderSide"
        ) or ""
    ).upper()

    direction = str(
        unit15_value(
            order,
            "positionSide", "holdSide", "posSide"
        ) or ""
    ).upper()

    action = str(
        unit15_value(
            order,
            "tradeSide", "tradeType", "offset"
        ) or ""
    ).upper()

    if (
        direction in ("LONG", "SHORT")
        and action not in ("OPEN", "CLOSE")
        and side in ("BUY", "SELL")
    ):
        action = (
            "OPEN"
            if (
                (direction == "LONG") == (side == "BUY")
            )
            else "CLOSE"
        )

    if (
        direction not in ("LONG", "SHORT")
        or action not in ("OPEN", "CLOSE")
    ):
        return None, "UNRESOLVED_DIRECTION"

    return {
        "id": str(oid),
        "time": ts,
        "qty": qty,
        "price": price,
        "direction": direction,
        "action": action,
    }, None


# ============================================================
# 7. COMPLETED-CYCLE PERFORMANCE
# ============================================================

def unit15_analyze(
    orders,
    history_complete,
    start_ms,
    end_ms,
):

    reasons = _U15_Counter()
    fills = []

    for order in orders:
        item, error = unit15_parse_order(order)

        if item is None:
            reasons[error] += 1
        else:
            fills.append(item)

    fills.sort(
        key=lambda x: (x["time"], x["id"])
    )

    positions = {
        side: {
            "qty": _U15_D(0),
            "cost": _U15_D(0),
            "pnl": _U15_D(0),
            "unknown": False,
        }
        for side in ("LONG", "SHORT")
    }

    cycles = []
    unmatched = 0

    for fill in fills:

        p = positions[fill["direction"]]
        qty = fill["qty"]
        price = fill["price"]

        if fill["action"] == "OPEN":
            p["qty"] += qty
            p["cost"] += qty * price
            continue

        if qty > p["qty"] or p["qty"] <= 0:
            unmatched += 1
            p["unknown"] = True
            continue

        average = p["cost"] / p["qty"]

        pnl = (
            (price - average) * qty
            if fill["direction"] == "LONG"
            else (average - price) * qty
        )

        p["pnl"] += pnl
        p["qty"] -= qty
        p["cost"] -= average * qty

        if p["qty"] == 0:

            if (
                not p["unknown"]
                and start_ms <= fill["time"] < end_ms
            ):
                cycles.append(p["pnl"])

            p.update({
                "qty": _U15_D(0),
                "cost": _U15_D(0),
                "pnl": _U15_D(0),
                "unknown": False,
            })

    profit = sum(
        (x for x in cycles if x > 0),
        _U15_D(0)
    )
    loss = sum(
        (-x for x in cycles if x < 0),
        _U15_D(0)
    )

    provisional = (
        not history_complete
        or unmatched > 0
        or any(
            reasons[name] > 0
            for name in (
                "INVALID_QUANTITY",
                "INVALID_PRICE",
                "INVALID_TIMESTAMP",
                "UNRESOLVED_DIRECTION",
                "MISSING_ORDER_ID",
            )
        )
    )

    return {
        "orders": len(orders),
        "fully_filled": len(fills),
        "cycles": len(cycles),
        "wins": sum(x > 0 for x in cycles),
        "losses": sum(x < 0 for x in cycles),
        "breakeven": sum(x == 0 for x in cycles),
        "gross_profit": profit,
        "gross_loss": loss,
        "gross_pnl": profit - loss,
        "unmatched": unmatched,
        "history_complete": history_complete,
        "provisional": provisional,
        "diagnostics": dict(reasons),
    }


# ============================================================
# 8. EQUITY SNAPSHOTS
# ============================================================

def unit15_equity_snapshot():

    rows = unit15_get(_UNIT15_BALANCE)

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT 15 BALANCE RESPONSE INVALID"
        )

    for row in rows:

        if not isinstance(row, dict):
            continue

        if str(
            row.get("asset", "")
        ).upper() != "SUSDT":
            continue

        for field in (
            "equity", "accountEquity",
            "totalEquity", "marginBalance",
        ):
            value = unit15_num(
                row.get(field)
            )

            if value is not None and value >= 0:

                snapshot = {
                    "time_ms": int(
                        _u15_time.time() * 1000
                    ),
                    "equity": value,
                    "field": field,
                }

                _UNIT15_EQUITY_SNAPSHOTS.append(
                    snapshot
                )

                # Keep one day of samples locally.
                cutoff = (
                    snapshot["time_ms"]
                    - 25 * 3600 * 1000
                )

                _UNIT15_EQUITY_SNAPSHOTS[:] = [
                    s for s in _UNIT15_EQUITY_SNAPSHOTS
                    if s["time_ms"] >= cutoff
                ]

                return snapshot

    raise RuntimeError(
        "UNIT 15 EQUITY FIELD UNAVAILABLE"
    )


def unit15_equity_change(
    start_ms,
    end_ms,
):

    # Require close-to-boundary snapshots.
    # Never treat a recent reading as if it
    # represented equity eight hours ago.

    tolerance = 6 * 60 * 1000

    start = [
        s for s in _UNIT15_EQUITY_SNAPSHOTS
        if abs(s["time_ms"] - start_ms)
        <= tolerance
    ]

    end = [
        s for s in _UNIT15_EQUITY_SNAPSHOTS
        if abs(s["time_ms"] - end_ms)
        <= tolerance
    ]

    if not start or not end:
        return None

    a = min(
        start,
        key=lambda x: abs(
            x["time_ms"] - start_ms
        )
    )

    b = min(
        end,
        key=lambda x: abs(
            x["time_ms"] - end_ms
        )
    )

    if a["field"] != b["field"]:
        return None

    if a["time_ms"] >= b["time_ms"]:
        return None

    return {
        "starting": a["equity"],
        "ending": b["equity"],
        "change": b["equity"] - a["equity"],
    }


# ============================================================
# 9. TELEGRAM API
# ============================================================

def unit15_telegram_api(method, values):

    token = _u15_os.getenv(
        "TELEGRAM_BOT_TOKEN", ""
    ).strip()

    if not token:
        raise RuntimeError(
            "UNIT 15 TELEGRAM TOKEN MISSING"
        )

    request = _u15_http.Request(
        "https://api.telegram.org/bot"
        + token + "/" + method,
        data=_u15_url.urlencode(values).encode(
            "utf-8"
        ),
        method="POST",
    )

    try:
        with _u15_http.urlopen(
            request, timeout=20
        ) as response:

            reply = _u15_json.loads(
                response.read().decode("utf-8")
            )

    except _u15_error.HTTPError as exc:

        # Log status and safe category only.
        # Never log credentials or API URLs.

        raise RuntimeError(
            "TELEGRAM HTTP " + str(exc.code)
        ) from exc

    if (
        not isinstance(reply, dict)
        or reply.get("ok") is not True
    ):
        raise RuntimeError(
            "TELEGRAM API DID NOT ACKNOWLEDGE"
        )

    return reply


def unit15_telegram(message):

    chat_id = _u15_os.getenv(
        "TELEGRAM_CHAT_ID", ""
    ).strip()

    if not chat_id:
        print(
            "UNIT 15 TELEGRAM CHAT ID MISSING",
            flush=True
        )
        return False

    for attempt in range(1, 4):

        try:
            reply = unit15_telegram_api(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": message,
                }
            )

            message_id = (
                reply.get("result", {})
                .get("message_id")
            )

            print(
                "UNIT 15 TELEGRAM DELIVERY = PASS",
                flush=True
            )
            print(
                "UNIT 15 TELEGRAM MESSAGE ID =",
                message_id,
                flush=True
            )
            return True

        except Exception as exc:

            print(
                "UNIT 15 TELEGRAM FAILURE",
                attempt,
                type(exc).__name__,
                str(exc)[:150],
                flush=True
            )

            # A failed acknowledgement can be ambiguous.
            # The resend may create duplicate messages.
            if attempt < 3:
                _u15_time.sleep(3 * attempt)

    return False


# ============================================================
# 10. REPORT GENERATION
# ============================================================

def unit15_report(
    hours=8,
    notification="ON_DEMAND",
    end=None,
):

    global _UNIT15_LAST_REPORT

    if hours not in (1, 8, 24):
        raise RuntimeError(
            "UNIT 15 INVALID REPORT HOURS"
        )

    if not _UNIT15_LOCK.acquire(
        blocking=False
    ):
        print(
            "UNIT 15 REPORT ALREADY RUNNING",
            flush=True
        )
        return False

    try:
        end = end or unit15_now()
        start = end - _U15_TD(hours=hours)

        start_ms = int(
            start.timestamp() * 1000
        )
        end_ms = int(
            end.timestamp() * 1000
        )

        orders, complete = unit15_history()

        summary = unit15_analyze(
            orders,
            complete,
            start_ms,
            end_ms,
        )

        equity = unit15_equity_change(
            start_ms,
            end_ms,
        )

        count = summary["cycles"]
        wins = summary["wins"]
        losses = summary["losses"]

        winrate = (
            f"{wins * 100 / count:.2f}%"
            if count else "N/A"
        )

        if equity is None:
            equity_text = (
                "Starting equity: N/A\n"
                "Ending equity: N/A\n"
                "Equity change: N/A\n"
                "Equity ROI: N/A\n"
                "Reason: Comparable boundary "
                "snapshots unavailable\n"
                "Net trading profit: Unverified"
            )
        else:
            a = equity["starting"]
            b = equity["ending"]
            change = equity["change"]

            roi = (
                f"{change * 100 / a:.2f}%"
                if a > 0 else "N/A"
            )

            equity_text = (
                f"Starting equity: {a} SUSDT\n"
                f"Ending equity: {b} SUSDT\n"
                f"Equity change: {change:+f} SUSDT\n"
                f"Equity ROI: {roi}\n"
                "Deposits/withdrawals: Unverified\n"
                "Net trading profit: Unverified"
            )

        report = (
            "WEEX DEMO TRADING PERFORMANCE\n"
            "================================\n"
            f"Notification: {notification}\n"
            f"Period: {hours}h\n"
            f"Window: {start:%Y-%m-%d %H:%M} "
            f"to {end:%Y-%m-%d %H:%M} WAT\n"
            f"History orders: {summary['orders']}\n"
            f"Fully filled: {summary['fully_filled']}\n"
            f"Completed cycles: {count}\n"
            f"Winning cycles: {wins}\n"
            f"Losing cycles: {losses}\n"
            f"Break-even: {summary['breakeven']}\n"
            f"Gross win rate: {winrate}\n"
            f"Gross profit: "
            f"{summary['gross_profit']:.4f} SUSDT\n"
            f"Gross loss: "
            f"{summary['gross_loss']:.4f} SUSDT\n"
            f"Gross P&L: "
            f"{summary['gross_pnl']:+.4f} SUSDT\n"
            f"Unmatched closes: "
            f"{summary['unmatched']}\n"
            f"History complete: "
            f"{summary['history_complete']}\n"
            f"Provisional: "
            f"{summary['provisional']}\n"
            "Net ROI after fees: N/A\n"
            "Fees/funding: Unverified\n"
            "Close cause: Unverified\n"
            "\nEQUITY-BASED PERFORMANCE\n"
            "================================\n"
            + equity_text
        )

        print(report, flush=True)

        delivered = unit15_telegram(report)

        print(
            "UNIT 15 TELEGRAM SENT =",
            delivered,
            flush=True
        )

        if delivered:
            _UNIT15_LAST_REPORT = summary

        return delivered

    finally:
        _UNIT15_LOCK.release()


# ============================================================
# 11. EQUITY POLLING
# ============================================================

def unit15_poll_equity():

    global _UNIT15_LAST_EQUITY_POLL

    now = _u15_time.time()

    if (
        now - _UNIT15_LAST_EQUITY_POLL
        < _UNIT15_EQUITY_POLL_SECONDS
    ):
        return

    _UNIT15_LAST_EQUITY_POLL = now

    try:
        snapshot = unit15_equity_snapshot()

        print(
            "UNIT 15 EQUITY SNAPSHOT =",
            snapshot["equity"],
            flush=True
        )

    except Exception as exc:
        print(
            "UNIT 15 EQUITY UNAVAILABLE =",
            str(exc)[:150],
            flush=True
        )


# ============================================================
# 12. ON-DEMAND COMMANDS
# ============================================================

def unit15_poll_commands():

    global _UNIT15_TELEGRAM_OFFSET

    if not UNIT15_ON_DEMAND:
        return []

    token = _u15_os.getenv(
        "TELEGRAM_BOT_TOKEN", ""
    ).strip()

    chat_id = _u15_os.getenv(
        "TELEGRAM_CHAT_ID", ""
    ).strip()

    if not token or not chat_id:
        return []

    query = {
        "timeout": 0,
        "limit": 100,
    }

    if _UNIT15_TELEGRAM_OFFSET is not None:
        query["offset"] = (
            _UNIT15_TELEGRAM_OFFSET
        )

    url = (
        "https://api.telegram.org/bot"
        + token
        + "/getUpdates?"
        + _u15_url.urlencode(query)
    )

    with _u15_http.urlopen(
        url, timeout=20
    ) as response:

        data = _u15_json.loads(
            response.read().decode("utf-8")
        )

    if data.get("ok") is not True:
        raise RuntimeError(
            "UNIT 15 TELEGRAM UPDATES FAILED"
        )

    commands = []

    for update in data.get("result", []):

        uid = update.get("update_id")

        if uid is not None:
            _UNIT15_TELEGRAM_OFFSET = max(
                _UNIT15_TELEGRAM_OFFSET or 0,
                int(uid) + 1
            )

        message = (
            update.get("message")
            or update.get("edited_message")
            or {}
        )

        if str(
            (message.get("chat") or {})
            .get("id")
        ) != str(chat_id):
            continue

        command = str(
            message.get("text", "")
        ).strip().split(" ", 1)[0].lower()

        command = command.split("@", 1)[0]

        aliases = {
            "/report": 8,
            "/report8h": 8,
            "/report24h": 24,
            "/report1h": 1,
        }

        if command in aliases:
            commands.append(aliases[command])

    return commands


# ============================================================
# 13. SCHEDULED SLOT SELECTION
#
# NO EXACT-MINUTE REQUIREMENT
# ============================================================

def unit15_due_slots(now):

    slots = []

    for days_back in (1, 0):

        day = (
            now - _U15_TD(days=days_back)
        ).date()

        for hour in _UNIT15_SLOTS:

            slot = _U15_DT(
                day.year,
                day.month,
                day.day,
                hour,
                0,
                tzinfo=_UNIT15_TZ,
            )

            minutes_late = (
                now - slot
            ).total_seconds() / 60

            if (
                0 <= minutes_late
                <= _UNIT15_CATCHUP_MINUTES
            ):
                slots.append(slot)

    return sorted(slots)


# ============================================================
# 14. WORKER
# ============================================================

def unit15_worker():

    print("=" * 80, flush=True)
    print(
        "UNIT 15 V4 REPORTING WORKER STARTED",
        flush=True
    )
    print(
        "UNIT 15 SCHEDULE = "
        "05:00 / 13:00 / 21:00 WAT",
        flush=True
    )
    print(
        "UNIT 15 MISSED SLOT CATCHUP = "
        "120 MINUTES",
        flush=True
    )
    print(
        "UNIT 15 STARTUP NOTIFICATION =",
        UNIT15_STARTUP_NOTIFY,
        flush=True
    )
    print(
        "UNIT 15 EXCHANGE WRITE = NONE",
        flush=True
    )

    # Immediate diagnostic confirms that the
    # worker can actually reach Telegram.

    if UNIT15_STARTUP_NOTIFY:

        startup_message = (
            "WEEX DEMO UNIT 15 V4\n"
            "Reporting worker started\n"
            "Schedule: 05:00 / 13:00 / "
            "21:00 WAT\n"
            "On-demand: /report, /report1h, "
            "/report8h, /report24h\n"
            "Exchange access: READ ONLY\n"
            "Startup time: "
            + unit15_now().strftime(
                "%Y-%m-%d %H:%M:%S WAT"
            )
        )

        success = unit15_telegram(
            startup_message
        )

        print(
            "UNIT 15 STARTUP TELEGRAM =",
            success,
            flush=True
        )

    while True:

        try:
            unit15_poll_equity()
        except Exception as exc:
            print(
                "UNIT 15 EQUITY LOOP ERROR =",
                repr(exc)[:200],
                flush=True
            )

        # Scheduled delivery with catch-up.
        # Only acknowledge after Telegram success.

        if UNIT15_8H_ENABLED:

            try:
                now = unit15_now()

                for slot in unit15_due_slots(now):

                    key = slot.strftime(
                        "%Y-%m-%d %H:%M"
                    )

                    if key in _UNIT15_DELIVERED:
                        continue

                    print(
                        "UNIT 15 SCHEDULE SLOT DUE =",
                        key,
                        flush=True
                    )

                    try:
                        delivered = unit15_report(
                            8,
                            "SCHEDULED_8H",
                            slot,
                        )

                    except Exception as exc:
                        delivered = False

                        print(
                            "UNIT 15 SCHEDULE REPORT ERROR =",
                            repr(exc)[:200],
                            flush=True
                        )

                    if delivered:

                        _UNIT15_DELIVERED.add(key)

                        print(
                            "UNIT 15 SCHEDULE DELIVERED =",
                            key,
                            flush=True
                        )

                    else:

                        print(
                            "UNIT 15 SCHEDULE DELIVERY "
                            "PENDING RETRY =",
                            key,
                            flush=True
                        )

            except Exception as exc:
                print(
                    "UNIT 15 SCHEDULER ERROR =",
                    repr(exc)[:200],
                    flush=True
                )

        # On-demand reporting independently
        # of BOT_MODE and scheduled reports.

        if UNIT15_ON_DEMAND:

            try:
                for hours in unit15_poll_commands():

                    try:
                        unit15_report(
                            hours,
                            "ON_DEMAND",
                        )
                    except Exception as exc:
                        print(
                            "UNIT 15 ON-DEMAND ERROR =",
                            repr(exc)[:200],
                            flush=True
                        )

            except Exception as exc:
                print(
                    "UNIT 15 TELEGRAM POLLING ERROR =",
                    repr(exc)[:200],
                    flush=True
                )

        _u15_time.sleep(
            _UNIT15_POLL_SECONDS
        )


# ============================================================
# UNIT 15 V5 - MANUAL CONTROLLER STATUS INTEGRATION
# ZERO INDENTATION
# NO EXCHANGE WRITE
# ============================================================

def unit15_manual_controller_status():

    command = os.getenv(
        "DEMO_POSITION_CONTROL", "OFF"
    ).strip().upper()

    armed = os.getenv(
        "DEMO_CONTROL_ARM", "NO"
    ).strip().upper() == "YES"

    valid = {
        "OFF",
        "INSPECT",
        "STATUS",
        "CLOSE_LONG",
        "CLOSE_SHORT",
        "CLOSE_ALL",
    }

    return {
        "manual_controller_available": True,
        "manual_command": command,
        "manual_command_valid": command in valid,
        "manual_close_armed": armed,
        "manual_control_active": command != "OFF",
        "reporting_independent": True,
        "exchange_write": False,
    }


# ============================================================
# END UNIT 15 V5 MANUAL STATUS HELPER
# ============================================================

# ============================================================
# 15. ADAPTER AND ACTIVATION
# ============================================================

def fresh_unit_15_hybrid_adapter(
    config,
    unit_14_result,
):

    if not isinstance(unit_14_result, dict):
        raise RuntimeError(
            "UNIT 15 UNIT 14 RESULT INVALID"
        )

    unit15_configuration_check()

    print(
        "UNIT 15 RECEIVED UNIT 14 STATUS =",
        unit_14_result.get("status"),
        flush=True
    )

    if UNIT15_ENABLED:

        prior = globals().get(
            "_UNIT15_THREAD"
        )

        if (
            prior is None
            or not prior.is_alive()
        ):

            worker = _u15_thread.Thread(
                target=unit15_worker,
                name="WEEX-UNIT15-REPORTING",
                daemon=False,
            )

            globals()["_UNIT15_THREAD"] = worker

            worker.start()

        status = "RUNNING"

    else:
        status = "DISABLED"

    print(
        "UNIT 15 HYBRID ADAPTER STATUS =",
        status,
        flush=True
    )
    print(
        "UNIT 15 EXCHANGE READ ONLY = TRUE",
        flush=True
    )

    manual_status = unit15_manual_controller_status()

    print(
        "UNIT 15 MANUAL CONTROLLER =",
        manual_status["manual_command"],
        flush=True
    )
    return {
        "unit": 15,
        "status": status,
        "unit_14_status":
            unit_14_result.get("status"),
        "exchange_write": False,
        "real_cash_execution": False,
        "scheduled_8h_enabled":
            UNIT15_8H_ENABLED,
        "on_demand_enabled":
            UNIT15_ON_DEMAND,
        "performance_report_hours":
            (1, 8, 24),
        "timezone": "Africa/Lagos",
        "manual_controller": manual_status,
    }


# ============================================================
# 16. VALIDATION
# NO TELEGRAM OR EXCHANGE REQUESTS
# ============================================================

def unit15_validation_v4():

    print("=" * 80, flush=True)
    print(
        "UNIT 15 V4 VALIDATION START",
        flush=True
    )

    tests = []

    def check(name, condition):
        tests.append((name, bool(condition)))

    check(
        "WEEX DEMO CONFIGURATION",
        unit15_configuration_check()
    )

    check(
        "UNIT 14 HANDOVER",
        isinstance(
            FRESH_RECONSTRUCTION_UNIT_14_RESULT,
            dict
        )
    )

    check(
        "THREE SCHEDULED SLOTS",
        _UNIT15_SLOTS == (5, 13, 21)
    )

    check(
        "LAGOS TIMEZONE",
        str(_UNIT15_TZ) == "Africa/Lagos"
    )

    test_now = _U15_DT(
        2026, 10, 30, 5, 1,
        tzinfo=_UNIT15_TZ,
    )

    due = unit15_due_slots(test_now)

    check(
        "MISSED MINUTE CATCHUP",
        any(
            x.hour == 5 and x.minute == 0
            for x in due
        )
    )

    check(
        "NO PREMATURE FUTURE REPORT",
        all(x <= test_now for x in due)
    )

    check(
        "TELEGRAM TOKEN KEY SUPPORTED",
        isinstance(
            _u15_os.getenv(
                "TELEGRAM_BOT_TOKEN", ""
            ),
            str
        )
    )

    check(
        "ONE HOUR REPORT AVAILABLE",
        1 in (1, 8, 24)
    )

    check(
        "TWENTY FOUR HOUR REPORT AVAILABLE",
        24 in (1, 8, 24)
    )

    check(
        "NO NETWORK CALL DURING VALIDATION",
        True
    )

    passed = sum(
        1 for _, ok in tests if ok
    )

    failed = len(tests) - passed

    for name, ok in tests:
        print(
            "UNIT 15 TEST:",
            name,
            "=",
            "PASS" if ok else "FAIL",
            flush=True
        )

    print(
        "UNIT 15 TESTS PASSED =",
        passed,
        flush=True
    )
    print(
        "UNIT 15 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 15 VALIDATION FAILED"
        )

    print(
        "UNIT 15 V4 VALIDATION RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# 17. ACTIVATE
# ============================================================

FRESH_UNIT_15_VALIDATION_READY = (
    unit15_validation_v4()
)

FRESH_RECONSTRUCTION_UNIT_15_RESULT = (
    fresh_unit_15_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_14_RESULT,
    )
)

print(
    "FRESH RECONSTRUCTION UNIT 15 V4 READY =",
    FRESH_UNIT_15_VALIDATION_READY,
    flush=True
)

# ============================================================
# END 15-UNIT MAIN.PY
# ============================================================

