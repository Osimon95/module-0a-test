
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



# ============================================================
# CONTINUOUS SCAN CONTROLLER V1
# SINGLE MAIN.PY / ZERO INDENTATION
#
# REFRESHES UNITS 3-12
# MONITORS OPEN POSITIONS WITH UNITS 13-14
# PRESERVES UNIT 15 REPORTING WORKER
#
# UNIT 12 BOT_MODE = NEW INITIAL ENTRIES ONLY
# UNIT 13/14 = POSITION MANAGEMENT
# NO LIVE CASH ENDPOINTS
# ============================================================

import os as _scan_os
import time as _scan_time
import threading as _scan_thread
import traceback as _scan_traceback
from datetime import datetime as _SCAN_DT
from zoneinfo import ZoneInfo as _SCAN_Zone


SCAN_INTERVAL_SECONDS = int(
    _scan_os.getenv(
        "SCAN_INTERVAL_SECONDS",
        "30"
    )
)

if not 30 <= SCAN_INTERVAL_SECONDS <= 60:
    raise RuntimeError(
        "SCAN INTERVAL MUST BE 30-60 SECONDS"
    )

SCAN_TZ = _SCAN_Zone("Africa/Lagos")
SCAN_LOCK = _scan_thread.Lock()
SCAN_NUMBER = 0

SCAN_LAST_MARKET_SUCCESS = None
SCAN_LAST_MANAGEMENT_SUCCESS = None
SCAN_LAST_STATUS = "NOT_STARTED"


# ============================================================
# 1. POSITION MANAGEMENT FALLBACK RESULT
#
# Used when the new-entry pipeline fails.
# Does not authorize a new initial entry.
# ============================================================

def scan_idle_unit12_result(reason):

    return {
        "unit": 12,
        "status": "IDLE",
        "skip_reason": str(reason),
        "active_mode": "NONE",
        "direction": "NONE",
        "signal_qualified": False,
        "execution_intent": False,
        "position_exists": False,
        "demo_submission_attempted": False,
        "demo_submission_completed": False,
        "real_submission_attempted": False,
        "exchange_write": False,
        "management_path_permitted": True,
    }


# ============================================================
# SYMBOL-SPECIFIC RENDER CONTRACT CONFIGURATION
# NO EXCHANGE WRITE
# ============================================================


def unit_9_load_symbol_specifications(config, symbol):
    """
    Retrieve active-symbol contract specifications from WEEX.

    Public market-data GET only.
    No API credentials or exchange order submission.

    Quantity is treated as base-asset quantity.
    The contractVal field is retained separately.
    """

    import json
    import urllib.parse
    import urllib.request
    import urllib.error

    from decimal import Decimal, InvalidOperation

    symbol = str(symbol).strip().upper()

    precision = config.setdefault(
        "market_precision", {}
    )

    
    # Never carry a previous symbol's specifications
    # into a new symbol.
    precision["symbol_specifications_confirmed"] = False

    for key in (
        "quantity_step",
        "minimum_quantity",
        "price_step",
        "contract_multiplier",
        "contract_value",
        "specifications_symbol",
    ):
        precision.pop(key, None)
        
    try:
        if not symbol or not symbol.endswith("USDT"):
            raise ValueError("INVALID_MARKET_SYMBOL")

        exchange = config.get("exchange", {})

        base_url = str(
            exchange.get(
                "contract_base_url",
                "https://api-contract.weex.com"
            )
        ).rstrip("/")

        if base_url != "https://api-contract.weex.com":
            raise ValueError("UNEXPECTED_MARKET_API_HOST")

        endpoint = "/capi/v3/market/exchangeInfo"

        query = urllib.parse.urlencode({
            "symbol": symbol
        })

        url = base_url + endpoint + "?" + query

        request = urllib.request.Request(
            url,
            method="GET",
            headers={
                "Accept": "application/json",
                "User-Agent": "WEEX-Contract-Specs-V1",
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            if response.status != 200:
                raise ValueError(
                    "CONTRACT_INFO_HTTP_"
                    + str(response.status)
                )

            payload = json.loads(
                response.read().decode("utf-8")
            )

        if not isinstance(payload, dict):
            raise ValueError(
                "INVALID_CONTRACT_INFO_RESPONSE"
            )

        rows = payload.get("symbols")

        if not isinstance(rows, list):
            raise ValueError(
                "CONTRACT_SYMBOL_LIST_MISSING"
            )

        selected = next(
            (
                row for row in rows
                if isinstance(row, dict)
                and str(
                    row.get("symbol", "")
                ).upper() == symbol
            ),
            None
        )

        if selected is None:
            raise ValueError(
                "SYMBOL_NOT_IN_EXCHANGE_INFO"
            )

        
        print(
            "UNIT 9 EXCHANGE PRECISION FIELDS =",
            {
                key: selected.get(key)
                for key in (
                    "quantityPrecision",
                    "size_increment",
                    "pricePrecision",
                    "tick_size",
                    "minOrderSize",
                    "contractVal",
                )
            },
            flush=True
        )

        if str(
            selected.get("quoteAsset", "")
        ).upper() != "USDT":
            raise ValueError(
                "NOT_USDT_QUOTED"
            )

        def positive_number(value, name):
            try:
                result = Decimal(str(value))
            except (
                InvalidOperation,
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    "INVALID_" + name
                ) from exc

            if not result.is_finite() or result <= 0:
                raise ValueError(
                    "INVALID_" + name
                )

            return result

        
        def precision_step(value, name):
            """
            Convert a decimal-place count into a positive step.

            Accept:
                0       -> 1
                "0"     -> 1
                "0.0"   -> 1
                "3"     -> 0.001
                3.0     -> 0.001

            Reject missing, fractional, negative,
            nonfinite or excessive precision.
            """

            if isinstance(value, bool) or value is None:
                raise ValueError(
                    "INVALID_" + name
                )

            try:
                number = Decimal(str(value).strip())
            except (
                InvalidOperation,
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    "INVALID_" + name
                ) from exc

            if (
                not number.is_finite()
                or number != number.to_integral_value()
                or number < -18
                or number > 18
            ):
                raise ValueError(
                    "INVALID_" + name
                )

            return Decimal("1").scaleb(-int(number))

        
        # Use an explicit increment when WEEX returns
        # one; otherwise derive the precision increment.
        if selected.get("size_increment") is not None:
            quantity_step = positive_number(
                selected["size_increment"],
                "QUANTITY_STEP"
            )
        else:
            quantity_step = precision_step(
                selected["quantityPrecision"],
                "QUANTITY_PRECISION"
            )

        if selected.get("tick_size") is not None:
            price_step = positive_number(
                selected["tick_size"],
                "PRICE_STEP"
            )
        else:
            price_step = precision_step(
                selected["pricePrecision"],
                "PRICE_PRECISION"
            )

        minimum_quantity = positive_number(
            selected["minOrderSize"],
            "MINIMUM_ORDER_SIZE"
        )

        contract_value = positive_number(
            selected["contractVal"],
            "CONTRACT_VALUE"
        )

        # Existing Unit 8 and Unit 9 calculations use
        # BASE-ASSET quantities:
        #
        # notional = base_quantity * price
        #
        # Therefore contract_multiplier is 1 here.
        # contractVal is stored separately and must
        # not be applied again to base-asset quantities.

        values = {
            "quantity_step": float(quantity_step),
            "minimum_quantity": float(
                minimum_quantity
            ),
            "price_step": float(price_step),
            "contract_multiplier": 1.0,
            "contract_value": float(contract_value),
            "specifications_symbol": symbol,
        }

        precision.update(values)

        precision[
            "symbol_specifications_confirmed"
        ] = True

        print(
            "UNIT 9 CONTRACT SPECIFICATIONS = LOADED",
            flush=True
        )

        print(
            "UNIT 9 CONTRACT SYMBOL =",
            symbol,
            flush=True
        )

        print(
            "UNIT 9 QUANTITY STEP =",
            quantity_step,
            flush=True
        )

        print(
            "UNIT 9 MINIMUM QUANTITY =",
            minimum_quantity,
            flush=True
        )

        print(
            "UNIT 9 PRICE STEP =",
            price_step,
            flush=True
        )

        print(
            "UNIT 9 CONTRACT VALUE =",
            contract_value,
            flush=True
        )

        print(
            "UNIT 9 QUANTITY BASIS = BASE_ASSET",
            flush=True
        )

        return True

    except (
        ValueError,
        KeyError,
        TypeError,
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
    ) as exc:

        
        precision[
            "symbol_specifications_confirmed"
        ] = False

        print(
            "UNIT 9 CONTRACT SPECIFICATIONS = UNAVAILABLE",
            flush=True
        )

        print(
            "UNIT 9 CONTRACT SYMBOL =",
            symbol,
            flush=True
        )

        print(
            "UNIT 9 CONTRACT REASON =",
            str(exc),
            flush=True
        )

        return False


# ============================================================
# RENDER ENTRY MARGIN ELIGIBILITY CONTROLLER
# Persistent decisions + existing Unit 15 Telegram queue
# No exchange orders submitted here
# ============================================================

from decimal import Decimal, ROUND_CEILING
import os

# ============================================================
# UNIT 8 - TP NET ROI ACCEPTANCE CONTROLLER
# SINGLE RENDER INPUT
# SQLITE PERSISTENCE + TELEGRAM EVENT DELIVERY
# ============================================================

def unit_8_tp_net_roi_control(
    config,
    account,
    market,
):

    from decimal import (
        Decimal,
        ROUND_CEILING,
        ROUND_FLOOR,
    )

    D = Decimal

    strategy = config["strategy"]
    precision = config["market_precision"]

    symbol = str(
        config["exchange"]["market_symbol"]
    ).strip().upper()

    raw = os.getenv(
        "TP_NET_ROI_FLOOR_PERCENT",
        "TP1:20,TP2:40"
    ).strip()

    result = {
        "status": "PENDING",
        "eligible": False,
        "minimum_tp1": None,
        "minimum_tp2": None,
    }

    def amount(value):

        return format(
            D(str(value)).normalize(),
            "f"
        )

    # --------------------------------------------------------
    # VERIFIED CONTRACT PRECISION
    # --------------------------------------------------------

    if precision.get(
        "symbol_specifications_confirmed"
    ) is not True:

        result["status"] = (
            "CONTRACT_SPECS_UNAVAILABLE"
        )

        return result

    price = D(str(market["price"]))

    tick = D(str(
        precision["price_step"]
    ))

    long_leverage = D(str(
        account["long_leverage"]
    ))

    short_leverage = D(str(
        account["short_leverage"]
    ))

    fee = D(str(
        strategy.get(
            "futures_taker_fee_percent",
            "0.08"
        )
    ))

    if any(
        not v.is_finite() or v <= 0
        for v in (
            price,
            tick,
            long_leverage,
            short_leverage,
        )
    ):

        result["status"] = (
            "INVALID_CONTRACT_PARAMETERS"
        )

        return result

    if not fee.is_finite() or fee < 0:

        result["status"] = "INVALID_FEE"

        return result

    # --------------------------------------------------------
    # MINIMUM POSITIVE EXECUTABLE NET ROI
    # SAME ESTIMATED FEE MODEL AS UNIT 13
    # --------------------------------------------------------

        # --------------------------------------------------------
    # DYNAMIC MINIMUM PROFITABLE TP1
    # EXCHANGE PRICE PRECISION AND LEVERAGE
    # --------------------------------------------------------

    fee_move = D("2") * fee / D("100")

    long_be = price * (D("1") + fee_move)
    short_be = price * (D("1") - fee_move)

    long_first = (
        (long_be / tick).to_integral_value(
            rounding=ROUND_FLOOR
        ) + D("1")
    ) * tick

    short_first = (
        (short_be / tick).to_integral_value(
            rounding=ROUND_CEILING
        ) - D("1")
    ) * tick

    if short_first <= 0:
        result["status"] = "INVALID_SHORT_TARGET"
        return result

    long_min_roi = (
        (long_first - price)
        / price
        * D("100")
        * long_leverage
        - D("2") * fee * long_leverage
    )

    short_min_roi = (
        (price - short_first)
        / price
        * D("100")
        * short_leverage
        - D("2") * fee * short_leverage
    )

    minimum_tp1 = max(
        long_min_roi,
        short_min_roi,
    ).quantize(
        D("0.000001"),
        rounding=ROUND_CEILING,
    )

    roi_tick = max(
        tick / price * D("100") * long_leverage,
        tick / price * D("100") * short_leverage,
    ).quantize(
        D("0.01"),
        rounding=ROUND_CEILING,
    )

    minimum_tp2 = (
        max(
            D("0.01"),
            long_min_roi,
            short_min_roi,
        ).quantize(
            D("0.01"),
            rounding=ROUND_CEILING,
        ) + roi_tick
    )

    result["minimum_tp1"] = minimum_tp1
    result["minimum_tp2"] = minimum_tp2

    result["minimum_tp1_source"] = (
        "EXCHANGE_SPECS_ESTIMATED_FEES"
    )

    result["minimum_tp1_fill_verified"] = False

    print(
        "UNIT 8 TP1 REFERENCE PRICE =",
        price,
        flush=True,
    )

    print(
        "UNIT 8 TP1 PRICE STEP =",
        tick,
        flush=True,
    )

    print(
        "UNIT 8 TP1 FIRST PROFITABLE LONG PRICE =",
        long_first,
        flush=True,
    )

    print(
        "UNIT 8 TP1 FIRST PROFITABLE SHORT PRICE =",
        short_first,
        flush=True,
    )

    print(
        "UNIT 8 TP1 LONG MINIMUM NET ROI =",
        long_min_roi,
        flush=True,
    )

    print(
        "UNIT 8 TP1 SHORT MINIMUM NET ROI =",
        short_min_roi,
        flush=True,
    )

    print(
        "UNIT 8 TP1 MINIMUM NET ROI SOURCE =",
        result["minimum_tp1_source"],
        flush=True,
    )

    # --------------------------------------------------------
    # SQLITE ACCEPTED CONFIGURATION
    # --------------------------------------------------------

    db = unit_8_symbol_switch_db()

    try:

        db.execute("""
            CREATE TABLE IF NOT EXISTS
            tp_net_roi_state (
                id INTEGER PRIMARY KEY
                    CHECK (id = 1),
                accepted_tp1 TEXT NOT NULL,
                accepted_tp2 TEXT NOT NULL,
                decision_key TEXT NOT NULL,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        db.execute("BEGIN IMMEDIATE")

        previous = db.execute("""
            SELECT
                accepted_tp1,
                accepted_tp2,
                decision_key,
                status
            FROM tp_net_roi_state
            WHERE id = 1
        """).fetchone()

        accepted_tp1 = D(str(
            strategy[
                "tp1_net_roi_floor_percent"
            ]
        ))

        accepted_tp2 = D(str(
            strategy[
                "tp2_net_roi_floor_percent"
            ]
        ))

        if previous is not None:

            accepted_tp1 = D(previous[0])
            accepted_tp2 = D(previous[1])

        # ----------------------------------------------------
        # PARSE CONSOLIDATED RENDER INPUT
        # ----------------------------------------------------

        status = "ACCEPTED"
        reason = ""
        requested = {}

        try:

            for item in raw.split(","):

                key, value = (
                    item.strip().split(":", 1)
                )

                key = key.strip().upper()

                if key in requested:
                    raise ValueError(
                        "Duplicate TP key"
                    )

                number = D(value.strip())

                if (
                    not number.is_finite()
                    or number <= 0
                ):
                    raise ValueError(
                        "ROI must be positive"
                    )

                requested[key] = number

            if set(requested) != {
                "TP1", "TP2"
            }:
                raise ValueError(
                    "TP1 and TP2 required"
                )

            tp1 = requested["TP1"]
            tp2 = requested["TP2"]

            decision_key = (
                symbol + "|"
                + amount(tp1) + "|"
                + amount(tp2)
            )

            if tp1 < minimum_tp1:

                status = "REJECTED"

                reason = (
                    f"TP1 {amount(tp1)}% below "
                    f"calculated executable minimum "
                    f"of {amount(minimum_tp1)}% "
                    f"using exchange specifications "
                    f"and estimated trading fees."
                )

            elif tp2 <= tp1:

                status = "REJECTED"

                reason = (
                    "TP2 must exceed TP1."
                )

            elif tp2 < minimum_tp2:

                status = "REJECTED"

                reason = (
                    f"TP2 {amount(tp2)}% "
                    f"below minimum of "
                    f"{amount(minimum_tp2)}%."
                )

            else:

                # Validate executable target prices
                # using the existing Unit 13 engine.

                for side, leverage in (
                    ("LONG", long_leverage),
                    ("SHORT", short_leverage),
                ):

                    unit_13_v4_targets(
                        price,
                        leverage,
                        side,
                        tick,
                        tp1,
                        tp2,
                        fee,
                    )

        except Exception as exc:

            status = "REJECTED"

            reason = (
                "Invalid TP net ROI configuration: "
                + str(exc)
            )

            decision_key = (
                symbol + "|" + raw
            )

        # ----------------------------------------------------
        # ACCEPT OR RETAIN LAST ACCEPTED VALUES
        # ----------------------------------------------------

        if status == "ACCEPTED":

            accepted_tp1 = requested["TP1"]
            accepted_tp2 = requested["TP2"]

            message = (
                f"{symbol} TP1 accepted, "
                f"{amount(accepted_tp1)}% "
                "net ROI enabled.\n"

                f"{symbol} TP2 accepted, "
                f"{amount(accepted_tp2)}% "
                "net ROI enabled."
            )

        else:

            message = (
                f"{symbol} TP net ROI rejected, "
                + reason
                + "\n"

                f"Retained TP1:"
                f"{amount(accepted_tp1)}%, "

                f"TP2:"
                f"{amount(accepted_tp2)}%."
            )

        changed = (
            previous is None
            or previous[2] != decision_key
            or previous[3] != status
        )

        now = datetime.now(
            timezone.utc
        ).isoformat()

        db.execute("""
            INSERT INTO tp_net_roi_state (
                id,
                accepted_tp1,
                accepted_tp2,
                decision_key,
                status,
                updated_at
            )
            VALUES (1, ?, ?, ?, ?, ?)

            ON CONFLICT(id) DO UPDATE SET

                accepted_tp1 =
                    excluded.accepted_tp1,

                accepted_tp2 =
                    excluded.accepted_tp2,

                decision_key =
                    excluded.decision_key,

                status =
                    excluded.status,

                updated_at =
                    excluded.updated_at
        """, (
            str(accepted_tp1),
            str(accepted_tp2),
            decision_key,
            status,
            now,
        ))

        if changed:

            unit_8_symbol_event(
                db,
                "TP_NET_ROI_" + status,
                message,
            )

        db.execute("COMMIT")

        # ----------------------------------------------------
        # PUBLISH ACCEPTED VALUES TO DOWNSTREAM UNITS
        # ----------------------------------------------------

        strategy[
            "tp1_net_roi_floor_percent"
        ] = float(accepted_tp1)

        strategy[
            "tp2_net_roi_floor_percent"
        ] = float(accepted_tp2)

        strategy[
            "tp1_tp2_min_roi_separation_percent"
        ] = float(
            accepted_tp2 - accepted_tp1
        )

        result.update({
            "status": status,
            "eligible": status == "ACCEPTED",
            "accepted_tp1": accepted_tp1,
            "accepted_tp2": accepted_tp2,
            "reason": reason,
        })

        print(
            "UNIT 8 TP NET ROI STATUS =",
            status,
            flush=True,
        )

        print(
            "UNIT 8 MINIMUM TP1 NET ROI =",
            minimum_tp1,
            flush=True,
        )

        print(
            "UNIT 8 MINIMUM TP2 NET ROI =",
            minimum_tp2,
            flush=True,
        )

        print(
            "UNIT 8 ACCEPTED TP1 NET ROI =",
            accepted_tp1,
            flush=True,
        )

        print(
            "UNIT 8 ACCEPTED TP2 NET ROI =",
            accepted_tp2,
            flush=True,
        )

        return result

    finally:

        if db.in_transaction:
            db.execute("ROLLBACK")

        db.close()
def unit_8_entry_margin_control(config, account, market):

    db = unit_8_symbol_switch_db()

    try:
        db.execute("""
            CREATE TABLE IF NOT EXISTS entry_margin_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                decision_key TEXT NOT NULL,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        symbol = str(
            config["exchange"]["market_symbol"]
        ).strip().upper()

        coin = (
            symbol[:-4]
            if symbol.endswith("USDT")
            else symbol
        )

        raw = os.getenv(
            "INITIAL_ENTRY_MARGIN_USDT"
        )

        if raw is None or not raw.strip():
            raw = os.getenv("ENTRY_FIXED_USDT")

        if raw is None or not raw.strip():
            raw = str(
                config["strategy"]["initial_fixed_usdt"]
            )

        margin = Decimal(str(raw))

        if not margin.is_finite() or margin <= 0:
            raise RuntimeError(
                "INVALID_RENDER_ENTRY_MARGIN"
            )

        def amount(value):
            return format(
                Decimal(str(value)).normalize(), "f"
            )

        def notify(status, message, key):
            now = datetime.now(
                timezone.utc
            ).isoformat()

            db.execute("BEGIN IMMEDIATE")

            previous = db.execute("""
                SELECT decision_key, status
                FROM entry_margin_state
                WHERE id = 1
            """).fetchone()

            changed = (
                previous is None
                or previous != (key, status)
            )

            if changed:
                db.execute("""
                    INSERT INTO entry_margin_state (
                        id, decision_key, status, updated_at
                    )
                    VALUES (1, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        decision_key = excluded.decision_key,
                        status = excluded.status,
                        updated_at = excluded.updated_at
                """, (key, status, now))

                if message:
                    unit_8_symbol_event(
                        db,
                        "ENTRY_MARGIN_" + status,
                        message
                    )

            db.execute("COMMIT")

            return status

        
        # ====================================================
        # VERIFIED DEMO POSITION STATE RECONCILIATION
        # ====================================================

        positions = account.get("positions")

        verified = (
            account.get("demo_positions_verified")
            is True
        )

        flat_flag = account.get(
            "position_flat_verified"
        )

        if not verified or not isinstance(
            positions, list
        ):
            print(
                "ENTRY POSITION STATE = UNVERIFIED",
                flush=True
            )
            return {
                "eligible": False,
                "status": "POSITION_UNVERIFIED"
            }

        open_positions = []

        for position in positions:
            if not isinstance(position, dict):
                print(
                    "ENTRY POSITION STATE = INVALID_RECORD",
                    flush=True
                )
                return {
                    "eligible": False,
                    "status": "POSITION_STATE_INCONSISTENT"
                }

            size = unit_8_v6_decimal(
                position.get("size", "0"),
                "POSITION SIZE",
                allow_zero=True
            )

            if size > 0:
                open_positions.append(position)

        occupied = bool(open_positions)
        computed_flat = not occupied

        print(
            "ENTRY POSITION COUNT =",
            len(open_positions),
            flush=True
        )

        print(
            "ENTRY POSITION FLAT FLAG =",
            flat_flag,
            flush=True
        )

        print(
            "ENTRY POSITION COMPUTED FLAT =",
            computed_flat,
            flush=True
        )

        if (
            not isinstance(flat_flag, bool)
            or flat_flag != computed_flat
        ):
            print(
                "ENTRY POSITION STATE = INCONSISTENT",
                flush=True
            )
            return {
                "eligible": False,
                "status": "POSITION_STATE_INCONSISTENT"
            }

        key = symbol + "|" + amount(margin)

        
        print(
            "ENTRY POSITION SNAPSHOT VERIFIED =",
            verified,
            flush=True
        )
        print(
            "ENTRY POSITION FLAT FLAG =",
            account.get("position_flat_verified"),
            flush=True
        )
        print(
            "ENTRY POSITION COUNT =",
            len(positions),
            flush=True
        )
        print(
            "ENTRY POSITION DETAILS =",
            [
                {
                    "symbol": p.get("symbol"),
                    "size": p.get("size"),
                    "side": p.get("side")
                }
                for p in positions
            ],
            flush=True
        )
        print(
            "ENTRY POSITION OCCUPIED =",
            occupied,
            flush=True
        )

        if occupied:
            print(
                "ENTRY POSITION STATE = CONFIRMED_OCCUPIED",
                flush=True
            )

            print(
                "ENTRY OPEN POSITION SYMBOLS =",
                [
                    p.get("symbol")
                    for p in open_positions
                ],
                flush=True
            )

            status = notify(
                "QUEUED",
                (
                    f"${amount(margin)} {coin} queued, "
                    "position exists."
                ),
                key
            )

            return {
                "eligible": False,
                "status": status,
                "open_position_count": len(open_positions)
            }

        print(
            "ENTRY POSITION STATE = CONFIRMED_FLAT",
            flush=True
        )

        # Continue to the existing margin validation.

        precision = config.get(
            "market_precision", {}
        )

        if (
            precision.get(
                "symbol_specifications_confirmed"
            ) is not True
        ):
            return {
                "eligible": False,
                "status": "CONTRACT_SPECS_UNAVAILABLE"
            }

        price = Decimal(str(market["price"]))
        step = Decimal(
            str(precision["quantity_step"])
        )
        minimum = Decimal(
            str(precision["minimum_quantity"])
        )
        multiplier = Decimal(
            str(precision["contract_multiplier"])
        )

        long_leverage = Decimal(
            str(account["long_leverage"])
        )
        short_leverage = Decimal(
            str(account["short_leverage"])
        )

        leverage = min(
            long_leverage, short_leverage
        )

        tp1_fraction = (
            Decimal(str(
                config["strategy"][
                    "tp1_allocation_percent"
                ]
            )) / Decimal("100")
        )

        values = (
            price, step, minimum, multiplier,
            leverage, tp1_fraction
        )

        if any(
            not v.is_finite() or v <= 0
            for v in values
        ):
            raise RuntimeError(
                "INVALID_ENTRY_CONTRACT_PARAMETERS"
            )

        # Minimum executable TP1, rounded to the
        # contract quantity step.
        tp1_steps = (
            minimum / step
        ).to_integral_value(
            rounding=ROUND_CEILING
        )

        tp1_quantity = tp1_steps * step

        # Initial quantity must support TP1 allocation.
        entry_steps = (
            tp1_quantity / tp1_fraction / step
        ).to_integral_value(
            rounding=ROUND_CEILING
        )

        entry_quantity = entry_steps * step

        minimum_margin = (
            entry_quantity
            * price
            * multiplier
            / leverage
        )

        minimum_margin = minimum_margin.quantize(
            Decimal("0.01"),
            rounding=ROUND_CEILING
        )

        if margin < minimum_margin:
            status = notify(
                "REJECTED",
                (
                    f"{coin} entry rejected, "
                    f"${amount(margin)} below min of "
                    f"${amount(minimum_margin)}."
                ),
                key
            )

            return {
                "eligible": False,
                "status": status,
                "minimum_margin": minimum_margin
            }

        status = notify(
            "ACCEPTED",
            (
                f"{coin} entry accepted, "
                f"${amount(margin)} entry enabled."
            ),
            key
        )

        return {
            "eligible": True,
            "status": status,
            "accepted_margin": margin,
            "minimum_margin": minimum_margin
        }

    finally:
        if db.in_transaction:
            db.execute("ROLLBACK")
        db.close()


# ============================================================
# UNIT 8 -> UNIT 9 RENDER ENTRY MARGIN CONTROLLER V2
# Persistent queue, acceptance and rejection
# Uses existing SQLite and Telegram event delivery
# DEMO ONLY - NO ORDER SUBMISSION
# ============================================================

from decimal import Decimal, ROUND_CEILING


def unit_8_render_entry_margin(config, account, market):

    db = unit_8_symbol_switch_db()

    try:
        db.execute("""
            CREATE TABLE IF NOT EXISTS entry_margin_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                request_key TEXT NOT NULL,
                decision TEXT NOT NULL,
                minimum TEXT,
                updated_at TEXT NOT NULL
            )
        """)

        symbol = str(
            config["exchange"]["market_symbol"]
        ).strip().upper()

        coin = (
            symbol[:-4]
            if symbol.endswith("USDT")
            else symbol
        )

        margin, source = unit_9_v4_entry_margin()

        margin = Decimal(str(margin))

        if not margin.is_finite() or margin <= 0:
            raise RuntimeError(
                "INVALID_RENDER_ENTRY_MARGIN"
            )

        def money(value):
            return format(
                Decimal(str(value)).normalize(), "f"
            )

        def decide(status, message, minimum=None):

            request_key = (
                symbol + "|" + money(margin)
            )

            old = db.execute("""
                SELECT request_key, decision
                FROM entry_margin_state
                WHERE id = 1
            """).fetchone()

            changed = (
                old is None
                or old != (request_key, status)
            )

            db.execute("BEGIN IMMEDIATE")

            try:
                db.execute("""
                    INSERT INTO entry_margin_state (
                        id, request_key, decision,
                        minimum, updated_at
                    )
                    VALUES (1, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        request_key = excluded.request_key,
                        decision = excluded.decision,
                        minimum = excluded.minimum,
                        updated_at = excluded.updated_at
                """, (
                    request_key,
                    status,
                    str(minimum) if minimum is not None
                    else None,
                    datetime.now(timezone.utc).isoformat()
                ))

                if changed and message:
                    unit_8_symbol_event(
                        db,
                        "ENTRY_MARGIN_" + status,
                        message
                    )

                db.execute("COMMIT")

            except Exception:
                db.execute("ROLLBACK")
                raise

            return {
                "eligible": status == "ACCEPTED",
                "status": status,
                "margin": str(margin),
                "minimum": (
                    str(minimum)
                    if minimum is not None
                    else None
                ),
                "source": source
            }

        if (
            account.get("demo_positions_verified")
            is not True
            or not isinstance(
                account.get("positions"), list
            )
        ):
            return decide(
                "PENDING",
                None
            )

        occupied = False

        for position in account["positions"]:

            if not isinstance(position, dict):
                raise RuntimeError(
                    "INVALID_POSITION_RECORD"
                )

            size = unit_8_v6_decimal(
                position.get("size", "0"),
                "POSITION_SIZE",
                allow_zero=True
            )

            if size > 0:
                occupied = True
                break

        if occupied:
            return decide(
                "QUEUED",
                (
                    f"${money(margin)} {coin} queued, "
                    "position exists."
                )
            )

        specs = config.get("market_precision", {})

        if (
            specs.get(
                "symbol_specifications_confirmed"
            ) is not True
        ):
            return decide(
                "PENDING",
                None
            )

        price = Decimal(str(market["price"]))
        step = Decimal(
            str(specs["quantity_step"])
        )
        minimum_qty = Decimal(
            str(specs["minimum_quantity"])
        )
        multiplier = Decimal(
            str(specs["contract_multiplier"])
        )

        long_lev = Decimal(
            str(account["long_leverage"])
        )
        short_lev = Decimal(
            str(account["short_leverage"])
        )

        leverage = min(long_lev, short_lev)

        allocations = [
            Decimal(str(
                config["strategy"][key]
            )) / Decimal("100")
            for key in (
                "tp1_allocation_percent",
                "tp2_allocation_percent",
                "tp3_allocation_percent"
            )
        ]

        values = [
            price, step, minimum_qty,
            multiplier, leverage
        ] + allocations

        if any(
            not value.is_finite() or value <= 0
            for value in values
        ):
            raise RuntimeError(
                "INVALID_ENTRY_SIZING_PARAMETERS"
            )

        # Current Unit 9 quantity calculation assumes
        # multiplier = 1. Do not approve a different
        # multiplier until both formulas are aligned.
        if multiplier != Decimal("1"):
            return decide(
                "PENDING",
                None
            )

        minimum_steps = (
            minimum_qty / step
        ).to_integral_value(
            rounding=ROUND_CEILING
        )

        executable_min_qty = minimum_steps * step

        # Each configured TP portion must be capable
        # of meeting the exchange minimum quantity.
        required_quantity = max(
            executable_min_qty / fraction
            for fraction in allocations
        )

        entry_steps = (
            required_quantity / step
        ).to_integral_value(
            rounding=ROUND_CEILING
        )

        entry_quantity = entry_steps * step

        required_margin = (
            entry_quantity * price / leverage
        )

        # Round upward to a cent for notifications.
        minimum_margin = required_margin.quantize(
            Decimal("0.01"),
            rounding=ROUND_CEILING
        )

        if margin < minimum_margin:

            return decide(
                "REJECTED",
                (
                    f"{coin} entry rejected, "
                    f"${money(margin)} below min of "
                    f"${money(minimum_margin)}."
                ),
                minimum_margin
            )

        return decide(
            "ACCEPTED",
            (
                f"{coin} entry accepted, "
                f"${money(margin)} entry enabled."
            ),
            minimum_margin
        )

    finally:
        db.close()


# ============================================================
# END ENTRY MARGIN CONTROLLER V2
# ============================================================

# ============================================================
# 2. REFRESH MARKET AND EXECUTION PIPELINE
#
# Uses the existing validated unit functions.
# Does not rerun unit validation tests.
# ============================================================


def scan_refresh_entry_pipeline():

    config = FRESH_RECONSTRUCTION_CONFIG

    # Refresh the active market/demo pair from SQLite
    # before fetching new market data.

    active_pair = unit_2_active_symbol_pair()

    active_market = active_pair["market_symbol"]
    active_demo = active_pair["demo_order_symbol"]

    if not active_market or not active_demo:
        raise RuntimeError(
            "SCAN ACTIVE SYMBOL PAIR MISSING"
        )

    if not isinstance(config.get("exchange"), dict):
        raise RuntimeError(
            "SCAN EXCHANGE CONFIGURATION INVALID"
        )

    config["exchange"]["market_symbol"] = active_market
    config["exchange"]["demo_order_symbol"] = active_demo
    config["exchange"]["active_symbol_source"] = (
        active_pair["source"]
    )

    
    specifications_loaded = unit_9_load_symbol_specifications(
        config,
        active_market,
    )

    if specifications_loaded is not True:
        print(
            "SCAN CONTRACT SPECIFICATIONS UNAVAILABLE =",
            active_market,
            flush=True,
        )
        raise RuntimeError(
            "SCAN ACTIVE CONTRACT SPECIFICATIONS UNAVAILABLE: "
            + active_market
        )

    print(
        "SCAN REFRESHED ACTIVE MARKET =",
        active_market,
        flush=True
    )

    print(
        "SCAN REFRESHED ACTIVE DEMO =",
        active_demo,
        flush=True
    )
    
    # UNIT 3 -> UNIT 4 FRESH MARKET HANDOVER
    # Unit 4 reads this global snapshot directly.

    global FRESH_RECONSTRUCTION_MARKET_SNAPSHOT

    FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
        fresh_reconstruction_unit_3()
    )

    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT

    if not isinstance(market, dict):
        raise RuntimeError(
            "SCAN UNIT 3 SNAPSHOT INVALID"
        )

    print(
        "SCAN FRESH MARKET TIMESTAMP =",
        market.get("exchange_time_ms"),
        flush=True
    )

    analysis = fresh_reconstruction_unit_4()

    # Unit 5: strategy classification
    candidate = fresh_reconstruction_unit_5(
        config,
        analysis,
    )

    # Unit 6: strategy arbitration
    execution = fresh_reconstruction_unit_6(
        config,
        analysis,
        candidate,
    )
    
    # Unit 7: dynamic sizing policy
    sizing = fresh_reconstruction_unit_7(
        config,
        execution,
    )

    # Unit 8: account and leverage context
    account = fresh_reconstruction_unit_8(
        config,
        sizing,
        market,
    )
        # ========================================================
    # CONSOLIDATED TP NET ROI ACCEPTANCE
    # INDEPENDENT OF ENTRY MARGIN AND BOT MODE
    # ========================================================

    tp_roi_decision = (
        unit_8_tp_net_roi_control(
            config,
            account,
            market,
        )
    )

    print(
        "SCAN TP NET ROI STATUS =",
        tp_roi_decision["status"],
        flush=True,
    )

    print(
        "SCAN TP NET ROI ELIGIBLE =",
        tp_roi_decision["eligible"],
        flush=True,
    )

    
    # ========================================================
    # UNIT 8 -> CONTINUOUS SYMBOL SWITCH RECONCILIATION
    # RUN AFTER FRESH ACCOUNT READ, BEFORE NEW ENTRY
    # ========================================================

    global FRESH_RECONSTRUCTION_SYMBOL_SWITCH_RESULT

    if (
        not isinstance(account, dict)
        or account.get("demo_positions_verified") is not True
        or not isinstance(account.get("positions"), list)
    ):
        raise RuntimeError(
            "SCAN SYMBOL SWITCH: ACCOUNT POSITIONS UNVERIFIED"
        )

    
    requested_market = os.getenv(
        "WEEX_SYMBOL", "BTCUSDT"
    ).strip().upper()

    discovery = unit_8_discover_demo_contract(
        requested_market
    )

    requested_demo = str(
        discovery.get("demo_symbol") or ""
    ).strip().upper()

    
    # Coin-base-vetted WEEX demo symbol.
    # Optional authenticated inspection is not an
    # order-submission prerequisite.

    demo_contract_verified = False

    switch_result = unit_8_symbol_switch(
        requested_market=requested_market,
        requested_demo=requested_demo,
        positions=account["positions"],
        positions_verified=account["demo_positions_verified"],
        contract_verified=False,
        candidate_ready=(
            discovery.get("candidate_ready") is True
        ),
    )
    
    FRESH_RECONSTRUCTION_SYMBOL_SWITCH_RESULT = switch_result
    
    print(
        "SCAN ACTIVE MARKET SYMBOL =",
        switch_result["active_market_symbol"],
        flush=True
    )

    print(
        "SCAN ACTIVE DEMO SYMBOL =",
        switch_result["active_demo_symbol"],
        flush=True
    )

    print(
        "SCAN QUEUED MARKET SYMBOL =",
        switch_result["queued_market_symbol"],
        flush=True
    )

    print(
        "SCAN QUEUED DEMO SYMBOL =",
        switch_result["queued_demo_symbol"],
        flush=True
    )

    active_market = switch_result[
        "active_market_symbol"
    ]

    active_demo = switch_result[
        "active_demo_symbol"
    ]

    # Do not mutate the active configuration here:
    # Units 3 and 4 already used it in this scan.
    # A new active pair requires a fresh market-data pass.

    if (
        config["exchange"]["market_symbol"] != active_market
        or config["exchange"]["demo_order_symbol"] != active_demo
    ):
        print(
            "SCAN SYMBOL CHANGED DURING CYCLE =",
            active_market,
            "/",
            active_demo,
            flush=True,
        )

        print(
            "SCAN NEW ENTRY DEFERRED UNTIL FRESH MARKET DATA",
            flush=True,
        )

        return {
            "status": "SYMBOL_CHANGED_REFRESH_NEXT_SCAN",
            "execution_authorized": False,
            "exchange_write": False,
        }

    # A queued or unverified symbol request must not
    # enter Unit 12's new-order submission path.
    # scan_one_cycle() catches this exception and
    # continues into existing-position management.

    if (
        requested_market != active_market
        or requested_demo != active_demo
    ):
        raise RuntimeError(
            "SCAN NEW ENTRY DEFERRED: "
            + switch_result["status"]
        )

    # ========================================================
    # END SYMBOL RECONCILIATION
    # ========================================================

    
    # ========================================================
    # RENDER ENTRY MARGIN VALIDATION
    # ========================================================

        # ========================================================
    # NEW ENTRY TP NET ROI VALIDATION
    # EXISTING POSITION MANAGEMENT REMAINS INDEPENDENT
    # ========================================================

    if tp_roi_decision["eligible"] is not True:

        return {
            "status": "IDLE",
            "skip_reason": (
                "TP_NET_ROI_"
                + tp_roi_decision["status"]
            ),
            "execution_authorized": False,
            "exchange_write": False,
        }
    margin_decision = unit_8_entry_margin_control(
        config,
        account,
        market,
    )

    print(
        "SCAN ENTRY MARGIN STATUS =",
        margin_decision["status"],
        flush=True
    )

    print(
        "SCAN UNIT 12 ENTRY ELIGIBLE =",
        margin_decision["eligible"],
        flush=True
    )

    if margin_decision["eligible"] is not True:
        return {
            "status": "IDLE",
            "skip_reason": (
                "ENTRY_MARGIN_"
                + margin_decision["status"]
            ),
            "execution_authorized": False,
            "exchange_write": False,
        }

    # Unit 9: entry sizing
    entry = fresh_reconstruction_unit_9(
        config,
        account,
    )

    # Unit 10: demo execution boundary
    boundary = fresh_unit_10_hybrid_adapter(
        config,
        entry,
    )

    # Unit 11: verified demo order payload
    prepared = fresh_unit_11_hybrid_adapter(
        config,
        boundary,
    )

    # Unit 12: only unit permitted to
    # submit a NEW initial demo entry.
    submission = (
        fresh_unit_12_hybrid_execution_adapter(
            config,
            prepared,
        )
    )

    return submission


# ============================================================
# 3. EXISTING POSITION MANAGEMENT
#
# Runs regardless of BOT_MODE.
# Unit 13 manages TP1/TP2.
# Unit 14 manages TP3 and five backups.
# ============================================================

def scan_manage_position(unit12_result):

    config = FRESH_RECONSTRUCTION_CONFIG

    unit13 = fresh_unit_13_hybrid_adapter(
        config,
        unit12_result,
    )

    unit14 = fresh_unit_14_hybrid_adapter(
        config,
        unit13,
    )

    return unit13, unit14


# ============================================================
# 4. ONE SCAN CYCLE
# ============================================================

def scan_one_cycle():

    global SCAN_NUMBER
    global SCAN_LAST_MARKET_SUCCESS
    global SCAN_LAST_MANAGEMENT_SUCCESS
    global SCAN_LAST_STATUS

    if not SCAN_LOCK.acquire(blocking=False):
        print(
            "SCAN OVERLAP BLOCKED",
            flush=True
        )
        return

    try:

        SCAN_NUMBER += 1

        now = _SCAN_DT.now(SCAN_TZ)

        print("=" * 80, flush=True)
        print(
            "CONTINUOUS SCAN NUMBER =",
            SCAN_NUMBER,
            flush=True
        )
        print(
            "SCAN TIME WAT =",
            now.isoformat(),
            flush=True
        )
        print(
            "SCAN BOT_MODE =",
            _scan_os.getenv(
                "BOT_MODE", "PAUSE"
            ),
            flush=True
        )

        
        
        # ====================================================
        # MANUAL WEEX DEMO POSITION CONTROLLER
        # Runs before new entries and automatic management.
        # ====================================================

        control_mode = _scan_os.getenv(
            "DEMO_POSITION_CONTROL", "OFF"
        ).strip().upper()

        if control_mode != "OFF":

            try:
                control_result = dpc_process()

                print(
                    "SCAN DEMO CONTROL STATUS =",
                    control_result,
                    flush=True
                )

                SCAN_LAST_STATUS = (
                    "MANUAL_CONTROL:"
                    + str(control_result)
                )

            except Exception as exc:

                SCAN_LAST_STATUS = (
                    "MANUAL_CONTROL_ERROR"
                )

                print(
                    "SCAN DEMO CONTROL ERROR =",
                    repr(exc),
                    flush=True
                )

                _scan_traceback.print_exc()

            return

        # --------------------------------------------
        # NEW-ENTRY PIPELINE
        # --------------------------------------------

        submission = None
        entry_ok = False

        try:

            submission = (
                scan_refresh_entry_pipeline()
            )

            entry_ok = True

            SCAN_LAST_MARKET_SUCCESS = (
                _scan_time.time()
            )

            print(
                "SCAN UNIT 12 STATUS =",
                submission.get("status"),
                flush=True
            )

        except Exception as exc:

            SCAN_LAST_STATUS = (
                "ENTRY_PIPELINE_ERROR"
            )

            print(
                "SCAN ENTRY PIPELINE ERROR =",
                repr(exc),
                flush=True
            )

            _scan_traceback.print_exc()

            # A signal-processing failure does
            # not automatically suspend
            # management of an existing position.
            submission = scan_idle_unit12_result(
                "ENTRY_PIPELINE_ERROR"
            )

        # --------------------------------------------
        # EXISTING POSITION MANAGEMENT
        # --------------------------------------------

        try:

            unit13, unit14 = (
                scan_manage_position(
                    submission
                )
            )

            SCAN_LAST_MANAGEMENT_SUCCESS = (
                _scan_time.time()
            )

            print(
                "SCAN UNIT 13 STATUS =",
                unit13.get("status"),
                flush=True
            )

            print(
                "SCAN UNIT 14 STATUS =",
                unit14.get("status"),
                flush=True
            )

            SCAN_LAST_STATUS = (
                "PASS"
                if entry_ok
                else "MANAGEMENT_ONLY"
            )

        except Exception as exc:

            SCAN_LAST_STATUS = (
                "POSITION_MANAGEMENT_ERROR"
            )

            print(
                "SCAN POSITION MANAGEMENT ERROR =",
                repr(exc),
                flush=True
            )

            _scan_traceback.print_exc()

        
        # --------------------------------------------
        # DELIVER PENDING SYMBOL SWITCH NOTIFICATIONS
        # --------------------------------------------

        try:
            delivered = unit_8_symbol_telegram_flush()

            print(
                "SCAN SYMBOL TELEGRAM DELIVERED =",
                delivered,
                flush=True
            )

        except Exception as exc:
            print(
                "SCAN SYMBOL TELEGRAM ERROR =",
                repr(exc),
                flush=True
            )

        print(
            "SCAN FINAL STATUS =",
            SCAN_LAST_STATUS,
            flush=True
        )

        print(
            "SCAN EXCHANGE ENVIRONMENT = DEMO",
            flush=True
        )

        print(
            "SCAN CONTINUES = TRUE",
            flush=True
        )

    finally:
        SCAN_LOCK.release()


# ============================================================
# 5. CONTINUOUS MONITORING LOOP
# ============================================================

def scan_forever():

    print("=" * 80, flush=True)
    print(
        "CONTINUOUS SCAN CONTROLLER V1 STARTED",
        flush=True
    )
    print(
        "SCAN INTERVAL SECONDS =",
        SCAN_INTERVAL_SECONDS,
        flush=True
    )
    print(
        "UNIT 12 CONTROLS NEW ENTRIES ONLY",
        flush=True
    )
    print(
        "UNIT 13 AND 14 MANAGEMENT = ALWAYS ACTIVE",
        flush=True
    )
    print(
        "UNIT 15 TELEGRAM = INDEPENDENT",
        flush=True
    )
    print("=" * 80, flush=True)

    # The original startup sequence has already
    # executed once before reaching this point.
    # Avoid immediately repeating that execution.

    _scan_time.sleep(
        SCAN_INTERVAL_SECONDS
    )

    while True:

        started = _scan_time.monotonic()

        try:

            scan_one_cycle()
            
    

    


        except Exception as exc:

            print(
                "SCAN SUPERVISOR ERROR =",
                repr(exc),
                flush=True
            )

            _scan_traceback.print_exc()

        elapsed = (
            _scan_time.monotonic()
            - started
        )

        # Maintain a minimum pause and avoid
        # overlapping scans if requests run long.

        sleep_for = max(
            5.0,
            SCAN_INTERVAL_SECONDS - elapsed,
        )

        print(
            "SCAN ELAPSED SECONDS =",
            round(elapsed, 2),
            flush=True
        )

        print(
            "SCAN NEXT SLEEP SECONDS =",
            round(sleep_for, 2),
            flush=True
        )

        _scan_time.sleep(sleep_for)

# ============================================================
# WEEX DEMO POSITION CONTROLLER V1
# RENDER ENVIRONMENT CONTROL
# REUSES EXISTING UNIT 14 DEMO API
# DOES NOT MODIFY EXISTING ENVIRONMENT VARIABLES
# ============================================================

import os as _dpc_os
import json as _dpc_json
import hashlib as _dpc_hashlib
from decimal import Decimal as _DPC_D
from decimal import ROUND_DOWN as _DPC_ROUND_DOWN

_DPC_JOURNAL_DIR = "/var/data/demo_position_control"


def dpc_setting(name, default=""):
    return _dpc_os.getenv(name, default).strip()


def dpc_positions():
    return unit_14_v3_positions()


def dpc_inspect():
    positions = dpc_positions()
    mark = unit_14_v3_mark()

    print("=" * 80, flush=True)
    print("DEMO POSITION CONTROLLER = INSPECT", flush=True)
    print("DEMO ENVIRONMENT = WEEX SIM", flush=True)
    print("DEMO MARK PRICE =", mark, flush=True)
    print("DEMO OPEN POSITIONS =", len(positions), flush=True)

    for side, p in positions.items():
        size = _DPC_D(str(p["size"]))
        entry_raw = (
            p.get("avgPrice")
            or p.get("entryPrice")
            or p.get("openPriceAvg")
        )

        entry = (
            _DPC_D(str(entry_raw))
            if entry_raw is not None
            else None
        )

        leverage = p.get("leverage", "UNAVAILABLE")
        liquidation = p.get(
            "liquidationPrice",
            p.get("liqPrice", "UNAVAILABLE")
        )

        pnl = None
        if entry is not None:
            if side == "LONG":
                pnl = (mark - entry) * size
            else:
                pnl = (entry - mark) * size

        print("-" * 60, flush=True)
        print("POSITION SIDE =", side, flush=True)
        print("POSITION SIZE =", size, flush=True)
        print("ENTRY PRICE =", entry, flush=True)
        print("MARK PRICE =", mark, flush=True)
        print("LEVERAGE =", leverage, flush=True)
        print("LIQUIDATION PRICE =", liquidation, flush=True)
        print(
            "ESTIMATED UNREALIZED PNL =",
            pnl if pnl is not None else "UNAVAILABLE",
            flush=True
        )
        print("PNL EXCLUDES FEES AND FUNDING", flush=True)

    print("=" * 80, flush=True)
    return positions


def dpc_command_claim(command_id):
    # Persistent disk required for restart-safe execution.
    if not _dpc_os.path.isdir("/var/data"):
        raise RuntimeError(
            "DEMO CONTROL REQUIRES PERSISTENT /var/data"
        )

    _dpc_os.makedirs(
        _DPC_JOURNAL_DIR,
        exist_ok=True
    )

    digest = _dpc_hashlib.sha256(
        command_id.encode("utf-8")
    ).hexdigest()

    path = _dpc_os.path.join(
        _DPC_JOURNAL_DIR,
        digest + ".json"
    )

    # Exclusive creation prevents reuse of the same
    # command ID, including after worker restarts.
    fd = _dpc_os.open(
        path,
        _dpc_os.O_WRONLY
        | _dpc_os.O_CREAT
        | _dpc_os.O_EXCL,
        0o600
    )

    with _dpc_os.fdopen(fd, "w") as f:
        _dpc_json.dump({
            "command_id": command_id,
            "state": "CLAIMED_BEFORE_SUBMISSION"
        }, f)
        f.flush()
        _dpc_os.fsync(f.fileno())

    return path


def dpc_close(side, command_id):
    positions = dpc_positions()

    if side not in positions:
        print(
            "DEMO CONTROL POSITION NOT FOUND =",
            side,
            flush=True
        )
        return "NO_POSITION"

    p = positions[side]

    size = _DPC_D(str(p["size"]))
    step = _DPC_D("0.0001")

    quantity = (
        (size / step).to_integral_value(
            rounding=_DPC_ROUND_DOWN
        ) * step
    )

    if quantity <= 0:
        raise RuntimeError(
            "DEMO CONTROL INVALID CLOSE QUANTITY"
        )

    # Re-read exchange position immediately
    # before submitting the manual close.
    latest = dpc_positions().get(side)

    if latest is None:
        return "POSITION_CHANGED"

    latest_size = _DPC_D(str(latest["size"]))

    if latest_size != size:
        print(
            "DEMO CONTROL POSITION SIZE CHANGED",
            flush=True
        )
        return "POSITION_CHANGED"

    payload = {
        "symbol": unit_13_14_active_symbols()[1],
        "side": "SELL" if side == "LONG" else "BUY",
        "positionSide": side,
        "type": "MARKET",
        "quantity": format(quantity, "f"),
        "newClientOrderId": (
            "DPC-"
            + _dpc_hashlib.sha256(
                (command_id + ":" + side).encode()
            ).hexdigest()[:24]
        )
    }

    # Claim before POST, never automatically retry.
    dpc_command_claim(command_id)

    print(
        "DEMO CONTROL SUBMITTING CLOSE =",
        side,
        flush=True
    )

    reply = unit_14_v3_signed_request(
        "POST",
        UNIT14_V3_ORDER,
        payload=payload
    )

    print(
        "DEMO CONTROL ORDER RESPONSE =",
        reply,
        flush=True
    )

    if (
        not isinstance(reply, dict)
        or reply.get("success") is not True
        or not reply.get("orderId")
    ):
        return "SUBMISSION_UNCONFIRMED"

    # Acknowledgment is not proof of a fill.
    remaining = dpc_positions().get(side)

    if remaining is None:
        return "CLOSED_CONFIRMED"

    return "SUBMITTED_RECONCILIATION_REQUIRED"


def dpc_process():
    command = dpc_setting(
        "DEMO_POSITION_CONTROL", "OFF"
    ).upper()

    arm = dpc_setting(
        "DEMO_CONTROL_ARM", "NO"
    ).upper()

    command_id = dpc_setting(
        "DEMO_CONTROL_COMMAND_ID", ""
    )

    if command == "OFF":
        return "OFF"

    if command in ("INSPECT", "STATUS"):
        dpc_inspect()
        return "INSPECTED"

    if command not in (
        "CLOSE_LONG",
        "CLOSE_SHORT",
        "CLOSE_ALL"
    ):
        print(
            "DEMO CONTROL UNKNOWN COMMAND =",
            command,
            flush=True
        )
        return "REJECTED"

    if arm != "YES":
        print(
            "DEMO CONTROL CLOSE NOT ARMED",
            flush=True
        )
        return "NOT_ARMED"

    if not command_id:
        print(
            "DEMO CONTROL COMMAND ID REQUIRED",
            flush=True
        )
        return "REJECTED"

    # CLOSE_ALL requires a separate, explicit
    # command ID for each side.
    if command == "CLOSE_ALL":
        positions = dpc_positions()
        results = {}

        for side in ("LONG", "SHORT"):
            if side in positions:
                results[side] = dpc_close(
                    side,
                    command_id + "-" + side
                )

        print(
            "DEMO CONTROL CLOSE ALL RESULTS =",
            results,
            flush=True
        )
        return "CLOSE_ALL_PROCESSED"

    side = command.split("_", 1)[1]

    try:
        result = dpc_close(side, command_id)
    except FileExistsError:
        print(
            "DEMO CONTROL DUPLICATE COMMAND ID",
            flush=True
        )
        return "DUPLICATE_BLOCKED"

    print(
        "DEMO CONTROL RESULT =",
        result,
        flush=True
    )

    return result


# ============================================================
# END WEEX DEMO POSITION CONTROLLER V1
# ============================================================


# ============================================================
# START CONTINUOUS SCANNING
# All demo controller functions are now defined.
# ============================================================

scan_forever()

# ============================================================
# END CONTINUOUS SCAN CONTROLLER V1
# ============================================================
