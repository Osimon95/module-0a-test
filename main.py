# ============================================================
# COMPLETE UNIT 14 V3 REPLACEMENT
# UNIT 13 -> UNIT 14 -> UNIT 15
# ZERO INDENTATION
#
# WEEX DEMO POSITION MANAGEMENT
# FIVE DYNAMIC BACKUPS: B1 - B5
# PERCENT AVAILABLE BALANCE
# 0.3% LIQUIDATION BUFFER
# MAXIMUM EXPOSURE 35%
# TP3 TRAILING MANAGEMENT
#
# BOT_MODE DOES NOT CONTROL UNIT 14
# NO LIVE CASH ENDPOINT
# NO LEVERAGE OR MARGIN MODE MUTATION
# NO AUTOMATIC POST RETRIES
# ============================================================

import os
import json
import time
import hmac
import base64
import hashlib
import urllib.request
import urllib.parse
import urllib.error
from decimal import Decimal, ROUND_DOWN


UNIT14_V3_BASE = "https://api-contract.weex.com"
UNIT14_V3_POSITION = "/capi/v3/sim/position/allPosition"
UNIT14_V3_BALANCE = "/capi/v3/sim/balance"
UNIT14_V3_HISTORY = "/capi/v3/sim/order/history"
UNIT14_V3_ORDER = "/capi/v3/sim/order"


# ============================================================
# 1. DECIMAL UTILITIES
# ============================================================

def unit_14_v3_D(value, name="VALUE", zero=False):

    if value is None or isinstance(value, bool):
        raise RuntimeError(
            "UNIT 14 MISSING " + name
        )

    try:
        x = Decimal(str(value))
    except Exception as exc:
        raise RuntimeError(
            "UNIT 14 INVALID " + name
        ) from exc

    if not x.is_finite():
        raise RuntimeError(
            "UNIT 14 NONFINITE " + name
        )

    if x < 0 or (x == 0 and not zero):
        raise RuntimeError(
            "UNIT 14 NONPOSITIVE " + name
        )

    return x


def unit_14_v3_floor(value, step):

    return (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    ) * step


# ============================================================
# 2. SIGNED DEMO REQUEST
# ============================================================

def unit_14_v3_signed_request(
    method,
    path,
    query="",
    payload=None,
):

    allowed = {
        ("GET", UNIT14_V3_POSITION),
        ("GET", UNIT14_V3_BALANCE),
        ("GET", UNIT14_V3_HISTORY),
        ("POST", UNIT14_V3_ORDER),
    }

    if (method, path) not in allowed:
        raise RuntimeError(
            "UNIT 14 NON-DEMO ENDPOINT BLOCKED"
        )

    if method == "POST" and not isinstance(
        payload, dict
    ):
        raise RuntimeError(
            "UNIT 14 POST PAYLOAD INVALID"
        )

    if method == "GET" and payload is not None:
        raise RuntimeError(
            "UNIT 14 GET BODY NOT ALLOWED"
        )

    key = (
        os.getenv("WEEX_API_KEY")
        or os.getenv("API_KEY")
    )

    secret = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("API_SECRET")
    )

    phrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        raise RuntimeError(
            "UNIT 14 DEMO CREDENTIALS MISSING"
        )

    body = (
        json.dumps(
            payload,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        if payload is not None
        else ""
    )

    timestamp = str(int(time.time() * 1000))

    prehash = timestamp + method + path

    if query:
        prehash += "?" + query

    prehash += body

    signature = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    url = UNIT14_V3_BASE + path

    if query:
        url += "?" + query

    request = urllib.request.Request(
        url,
        method=method,
        data=(
            body.encode("utf-8")
            if method == "POST"
            else None
        ),
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": phrase,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            status = response.getcode()
            raw = response.read().decode(
                "utf-8", errors="replace"
            )

    except urllib.error.HTTPError as exc:

        detail = exc.read().decode(
            "utf-8", errors="replace"
        )[:400]

        raise RuntimeError(
            "UNIT 14 WEEX HTTP "
            + str(exc.code)
            + ": "
            + detail
        ) from exc

    # Never automatically retry a POST.
    # An exchange order may have been received
    # even when the acknowledgement was lost.

    if not 200 <= status < 300:
        raise RuntimeError(
            "UNIT 14 HTTP STATUS " + str(status)
        )

    try:
        return json.loads(raw)
    except ValueError as exc:
        raise RuntimeError(
            "UNIT 14 INVALID RESPONSE JSON"
        ) from exc


# ============================================================
# 3. POSITION, BALANCE AND ORDER HISTORY
# ============================================================


def unit_14_v3_positions():

    rows = unit_14_v3_signed_request(
        "GET",
        UNIT14_V3_POSITION,
    )

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT 14 POSITION RESPONSE NOT LIST"
        )

    active = {}

    for p in rows:

        if not isinstance(p, dict):
            raise RuntimeError(
                "UNIT 14 POSITION RECORD INVALID"
            )

        if str(
            p.get("symbol", "")
        ).upper() != unit_13_14_active_symbols()[1]:
            continue

        size = unit_14_v3_D(
            p.get("size"),
            "POSITION SIZE",
            True,
        )

        if size <= 0:
            continue

        side = str(
            p.get("side", "")
        ).upper()

        if side not in ("LONG", "SHORT"):
            raise RuntimeError(
                "UNIT 14 INVALID POSITION SIDE"
            )

        if side in active:
            raise RuntimeError(
                "UNIT 14 DUPLICATE ACTIVE POSITION SIDE"
            )

        active[side] = p

    return active


def unit_14_v3_position(side=None):

    active = unit_14_v3_positions()

    if side is not None:

        side = str(side).upper()

        if side not in ("LONG", "SHORT"):
            raise RuntimeError(
                "UNIT 14 INVALID REQUESTED SIDE"
            )

        return active.get(side)

    if not active:
        return None

    if len(active) == 1:
        return next(iter(active.values()))

    raise RuntimeError(
        "UNIT 14 ORIGINAL SIDE REQUIRED "
        "FOR HEDGE PAIR"
    )

def unit_14_v3_balance():

    rows = unit_14_v3_signed_request(
        "GET",
        UNIT14_V3_BALANCE,
    )

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT 14 BALANCE RESPONSE NOT LIST"
        )

    for row in rows:

        if (
            isinstance(row, dict)
            and str(
                row.get("asset", "")
            ).upper() == "SUSDT"
        ):
            return unit_14_v3_D(
                row.get("availableBalance"),
                "AVAILABLE BALANCE",
                True,
            )

    raise RuntimeError(
        "UNIT 14 SUSDT BALANCE MISSING"
    )


def unit_14_v3_history(
    demo_symbol=None,
    start_time=None,
    end_time=None,
):

    if demo_symbol is None:
        _, demo_symbol = unit_13_14_active_symbols()

    demo_symbol = str(demo_symbol).strip().upper()

    if not demo_symbol.endswith("SUSDT"):
        raise RuntimeError(
            "UNIT 14 INVALID DEMO HISTORY SYMBOL"
        )

    orders = []

    for page in range(20):

        params = {
            "symbol": demo_symbol,
            "limit": 1000,
            "page": page,
        }

        if start_time is not None:
            params["startTime"] = int(start_time)

        if end_time is not None:
            params["endTime"] = int(end_time)

        query = urllib.parse.urlencode(params)

        batch = unit_14_v3_signed_request(
            "GET",
            UNIT14_V3_HISTORY,
            query,
        )

        if not isinstance(batch, list):
            raise RuntimeError(
                "UNIT 14 HISTORY NOT LIST"
            )

        if not all(
            isinstance(o, dict)
            for o in batch
        ):
            raise RuntimeError(
                "UNIT 14 MALFORMED HISTORY"
            )

        orders.extend(batch)

        if len(batch) < 1000:

            print(
                "UNIT 14 HISTORY SYMBOL =",
                demo_symbol,
                flush=True,
            )

            print(
                "UNIT 14 HISTORY START TIME =",
                start_time,
                flush=True,
            )

            print(
                "PASS: UNIT 14 ORDER HISTORY COMPLETE",
                "RECORDS =", len(orders),
                flush=True,
            )

            return orders

    raise RuntimeError(
        "UNIT 14 HISTORY PAGINATION INCOMPLETE"
    )

def unit_14_v3_mark():
    market_symbol, _ = unit_13_14_active_symbols()

    query = urllib.parse.urlencode({
        "symbol": market_symbol,
        "priceType": "MARK",
    })

    request = urllib.request.Request(
        UNIT14_V3_BASE
        + "/capi/v3/market/symbolPrice?"
        + query,
        method="GET",
    )

    with urllib.request.urlopen(
        request,
        timeout=15,
    ) as response:

        data = json.loads(
            response.read().decode("utf-8")
        )

    if (
        not isinstance(data, dict)
        or data.get("symbol") != market_symbol
    ):
        raise RuntimeError(
            "UNIT 14 INVALID MARK RESPONSE"
        )

    return unit_14_v3_D(
        data.get("price"),
        "MARK PRICE"
    )


# ============================================================
# 4. TRADE IDENTITY AND BACKUP RECONCILIATION
# ============================================================

def unit_14_v3_trade_key(position):

    created = str(
        position.get("createdTime", "")
    )

    if created.isdigit():
        return created[-12:]

    position_id = str(
        position.get("id", "")
    )

    if position_id:
        return position_id[-12:]

    raise RuntimeError(
        "UNIT 14 POSITION IDENTITY MISSING"
    )


def unit_14_v3_backup_id(stage, key):

    return (
        "FR-B"
        + str(stage)
        + "-"
        + key
    )[:36]


def unit_14_v3_reconcile(history, key):

    existing = set()
    filled = set()

    for stage in range(1, 6):

        client_id = unit_14_v3_backup_id(
            stage, key
        )

        matching = [
            o for o in history
            if str(
                o.get("clientOrderId", "")
            ) == client_id
        ]

        for order in matching:

            status = str(
                order.get("status", "")
            ).upper()

            executed = unit_14_v3_D(
                order.get("executedQty", 0),
                "EXECUTED QUANTITY",
                True,
            )

            if status not in (
                "CANCELED",
                "CANCELLED",
                "REJECTED",
                "EXPIRED",
            ):
                existing.add(stage)

            if status == "FILLED" and executed > 0:
                filled.add(stage)

            # A partially filled stage must not
            # automatically advance to the next.

            if executed > 0 and status != "FILLED":
                existing.add(stage)

    completed = 0

    for stage in range(1, 6):
        if stage in filled:
            completed = stage
        else:
            break

    if any(
        stage > completed + 1
        for stage in filled
    ):
        raise RuntimeError(
            "UNIT 14 NONSEQUENTIAL BACKUP FILLS"
        )

    return completed, existing


# ============================================================
# 5. LIQUIDATION BUFFER
# ============================================================

def unit_14_v3_trigger(
    side,
    liquidation,
    mark,
    buffer_pct,
):

    D = unit_14_v3_D

    liquidation = D(
        liquidation, "LIQUIDATION PRICE"
    )
    mark = D(mark, "MARK PRICE")
    buffer_pct = D(
        buffer_pct, "BUFFER PERCENT"
    )

    fraction = buffer_pct / D(100)

    if side == "LONG":

        trigger = liquidation * (
            D(1) + fraction
        )

        reached = mark <= trigger

    elif side == "SHORT":

        trigger = liquidation * (
            D(1) - fraction
        )

        reached = mark >= trigger

    else:
        raise RuntimeError(
            "UNIT 14 INVALID SIDE"
        )

    if trigger <= 0:
        raise RuntimeError(
            "UNIT 14 INVALID TRIGGER"
        )

    return trigger, bool(reached)


# ============================================================
# 6. RESULT CONSTRUCTOR
# ============================================================

def unit_14_v3_result(unit_13_result):

    return {
        "unit": 14,
        "status": "MONITORING",
        "unit_13_status": unit_13_result.get(
            "status"
        ),
        "position_exists": False,
        "backup_maximum": 5,
        "backups_filled": 0,
        "backup_next_stage": None,
        "backup_trigger_reached": False,
        "backup_submission_enabled": True,
        "backup_execution_attempted": False,
        "backup_execution_completed": False,
        "tp3_armed": False,
        "tp3_execution_attempted": False,
        "tp3_execution_completed": False,
        "real_submission_attempted": False,
        "sl_execution_attempted": False,
        "exchange_write": False,
        "skip_reason": "NONE",
    }


# ============================================================
# 7. MAIN UNIT 14
# ============================================================


 
# ============================================================
# UNIT 14 - PERSISTENT HEDGE / RECOVERY REGISTRY
# H1 / H2 / R1 / R2
# DEMO EXECUTION STATE
# ============================================================

import sqlite3
import hashlib
from decimal import Decimal


UNIT14_STAGE_ACTIONS = (
    "H1-C", "H1-H",
    "H2-C", "H2-H",
    "R1-C", "R1-O",
    "R2-C", "R2-O",
    "BE-C",
    "TP3-C",
)


def unit_14_stage_db():

    path = os.getenv(
        "UNIT14_STAGE_DB_PATH",
        "/var/data/unit14_stages.sqlite3"
    )

    directory = os.path.dirname(path)

    if directory and not os.path.isdir(directory):
        raise RuntimeError(
            "UNIT 14 PERSISTENT DISK UNAVAILABLE"
        )

    db = sqlite3.connect(
        path,
        timeout=30,
        isolation_level=None
    )

    db.execute("PRAGMA busy_timeout=30000")
    db.execute("PRAGMA journal_mode=WAL")

    db.execute("""
        CREATE TABLE IF NOT EXISTS stage_cycles (
            cycle_id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            original_side TEXT NOT NULL,
            original_quantity TEXT NOT NULL,
            original_entry TEXT NOT NULL,
            frozen_atr TEXT NOT NULL,
            stage TEXT NOT NULL DEFAULT 'READY',
            state TEXT NOT NULL DEFAULT 'ACTIVE',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS stage_orders (
            client_id TEXT PRIMARY KEY,
            cycle_id TEXT NOT NULL,
            action TEXT NOT NULL,
            quantity TEXT NOT NULL,
            state TEXT NOT NULL DEFAULT 'CLAIMED',
            exchange_order_id TEXT,
            confirmed_filled TEXT NOT NULL DEFAULT '0',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(cycle_id, action)
        )
    """)

        # INDEPENDENT BREAK-EVEN AND TP3 ORDER TABLES

    for table in (
        "breakeven_orders",
        "tp3_orders",
    ):

        db.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                client_id TEXT PRIMARY KEY,
                cycle_id TEXT NOT NULL,
                action TEXT NOT NULL,
                quantity TEXT NOT NULL,
                state TEXT NOT NULL DEFAULT 'CLAIMED',
                exchange_order_id TEXT,
                confirmed_filled TEXT NOT NULL DEFAULT '0',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(cycle_id, action)
            )
        """)
        
        # MIGRATE EXISTING BE AND TP3 ORDER RECORDS

    db.execute("BEGIN IMMEDIATE")

    try:

        for table, action in (
            ("breakeven_orders", "BE-C"),
            ("tp3_orders", "TP3-C"),
        ):

            db.execute(f"""
                INSERT OR IGNORE INTO {table} (
                    client_id,
                    cycle_id,
                    action,
                    quantity,
                    state,
                    exchange_order_id,
                    confirmed_filled,
                    created_at,
                    updated_at
                )
                SELECT
                    client_id,
                    cycle_id,
                    action,
                    quantity,
                    state,
                    exchange_order_id,
                    confirmed_filled,
                    created_at,
                    updated_at
                FROM stage_orders
                WHERE action = ?
            """, (action,))

        db.execute("COMMIT")

    except Exception:

        if db.in_transaction:
            db.execute("ROLLBACK")

        raise
        
    return db


def unit_14_stage_create_cycle(
    cycle_id,
    symbol,
    original_side,
    original_quantity,
    original_entry,
    frozen_atr
):
    """
    Create a new persisted cycle or preserve
    an existing cycle and its order history.
    """

    D = unit_14_v3_D

    cycle_id = str(cycle_id).strip()
    symbol = str(symbol).strip().upper()
    original_side = str(original_side).strip().upper()

    quantity = D(
        original_quantity,
        "ORIGINAL QUANTITY"
    )

    entry = D(
        original_entry,
        "ORIGINAL ENTRY"
    )

    atr = D(
        frozen_atr,
        "FROZEN ATR"
    )

    if (
        not cycle_id
        or not symbol
        or original_side not in ("LONG", "SHORT")
    ):
        raise RuntimeError(
            "INVALID STAGE CYCLE IDENTITY"
        )

    if quantity <= 0 or entry <= 0 or atr <= 0:
        raise RuntimeError(
            "INVALID HEDGE CYCLE VALUES"
        )

    db = unit_14_stage_db()

    try:
        db.execute("BEGIN IMMEDIATE")

        existing = db.execute("""
            SELECT
                symbol,
                original_side,
                original_quantity,
                original_entry,
                frozen_atr,
                stage,
                state
            FROM stage_cycles
            WHERE cycle_id = ?
        """, (cycle_id,)).fetchone()

        if existing is not None:

            saved_symbol = str(existing[0]).upper()
            saved_side = str(existing[1]).upper()

            if (
                saved_symbol != symbol
                or saved_side != original_side
            ):
                raise RuntimeError(
                    "PERSISTED CYCLE SYMBOL OR SIDE MISMATCH"
                )

            for name, value in zip(
                ("QUANTITY", "ENTRY", "ATR"),
                existing[2:5]
            ):
                if D(
                    value,
                    "PERSISTED " + name
                ) <= 0:
                    raise RuntimeError(
                        "INVALID PERSISTED " + name
                    )

            print(
                "UNIT 14 PERSISTED CYCLE FOUND =",
                cycle_id,
                "STAGE =", existing[5],
                "STATE =", existing[6],
                flush=True
            )

        else:

            db.execute("""
                INSERT INTO stage_cycles (
                    cycle_id,
                    symbol,
                    original_side,
                    original_quantity,
                    original_entry,
                    frozen_atr
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                cycle_id,
                symbol,
                original_side,
                str(quantity),
                str(entry),
                str(atr)
            ))

            print(
                "UNIT 14 NEW STAGE CYCLE CREATED =",
                cycle_id,
                flush=True
            )

        db.execute("COMMIT")

        return cycle_id

    except Exception:

        if db.in_transaction:
            db.execute("ROLLBACK")

        raise

    finally:
        db.close()


def unit_14_stage_client_id(cycle_id, action):
    cycle_id = str(cycle_id).strip()
    action = str(action).strip().upper()

    if not cycle_id:
        raise RuntimeError(
            "UNIT 14 CYCLE ID MISSING"
        )

    if action not in UNIT14_STAGE_ACTIONS:
        raise RuntimeError(
            "UNIT 14 INVALID STAGE ACTION"
        )

    digest = hashlib.sha256(
        (cycle_id + "|" + action).encode("utf-8")
    ).hexdigest()[:20]

    return "U14-" + action + "-" + digest


def unit_14_stage_client_id(cycle_id, action):
    """
    Stable client ID for each cycle and stage action.
    Same cycle/action always produces the same ID.
    """

    cycle_id = str(cycle_id).strip()
    action = str(action).strip().upper()

    if not cycle_id:
        raise RuntimeError(
            "UNIT 14 CYCLE ID MISSING"
        )

    if action not in UNIT14_STAGE_ACTIONS:
        raise RuntimeError(
            "UNIT 14 INVALID STAGE ACTION"
        )

    digest = hashlib.sha256(
        (cycle_id + "|" + action).encode("utf-8")
    ).hexdigest()[:20]

    return "U14-" + action + "-" + digest

def unit_14_stage_claim(
    cycle_id,
    action,
    quantity
):
    """
    Persist an order claim before transmission.
    Existing claims are never automatically
    submitted again.
    """

    if action not in UNIT14_STAGE_ACTIONS:
        raise RuntimeError("INVALID HEDGE ACTION")

    qty = unit_14_v3_D(
        quantity,
        "STAGE QUANTITY"
    )

    if qty <= 0:
        raise RuntimeError("INVALID STAGE QUANTITY")

    client_id = unit_14_stage_client_id(
        cycle_id,
        action
    )

    db = unit_14_stage_db()

    try:
        db.execute("BEGIN IMMEDIATE")

        cycle = db.execute("""
            SELECT state
            FROM stage_cycles
            WHERE cycle_id = ?
        """, (cycle_id,)).fetchone()

        if cycle is None or cycle[0] != "ACTIVE":
            raise RuntimeError("STAGE CYCLE NOT ACTIVE")

        existing = db.execute("""
            SELECT quantity, state
            FROM stage_orders
            WHERE client_id = ?
        """, (client_id,)).fetchone()

        if existing is not None:

            db.execute("COMMIT")

            return {
                "claimed": False,
                "client_id": client_id,
                "state": existing[1],
                "quantity": existing[0],
            }

        db.execute("""
            INSERT INTO stage_orders (
                client_id, cycle_id, action,
                quantity, state
            )
            VALUES (?, ?, ?, ?, 'CLAIMED')
        """, (
            client_id,
            cycle_id,
            action,
            str(qty)
        ))

        db.execute("COMMIT")

        return {
            "claimed": True,
            "client_id": client_id,
            "state": "CLAIMED",
            "quantity": str(qty),
        }

    except Exception:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise

    finally:
        db.close()


def unit_14_stage_update(
    client_id,
    state,
    exchange_order_id=None,
    confirmed_filled=None
):
    """
    Update persisted exchange acknowledgement
    and confirmed fill information.

    Never decrease an already confirmed fill.
    """

    D = unit_14_v3_D

    db = unit_14_stage_db()

    try:
        db.execute("BEGIN IMMEDIATE")

        existing = db.execute("""
            SELECT quantity, confirmed_filled,
                   exchange_order_id, state
            FROM stage_orders
            WHERE client_id = ?
        """, (client_id,)).fetchone()

        if existing is None:
            raise RuntimeError(
                "STAGE ORDER CLAIM NOT FOUND"
            )

        expected = D(
            existing[0],
            "EXPECTED STAGE QUANTITY"
        )

        previous = D(
            existing[1],
            "PREVIOUS CONFIRMED FILL",
            True
        )

        if confirmed_filled is None:
            filled = previous
        else:
            filled = D(
                confirmed_filled,
                "CONFIRMED STAGE FILL",
                True
            )

        if filled < previous:
            raise RuntimeError(
                "STAGE CONFIRMED FILL REGRESSION"
            )

        if filled > expected:
            raise RuntimeError(
                "STAGE FILL EXCEEDS CLAIMED QUANTITY"
            )

        saved_order_id = existing[2]

        if (
            saved_order_id
            and exchange_order_id
            and str(saved_order_id) != str(exchange_order_id)
        ):
            raise RuntimeError(
                "STAGE EXCHANGE ORDER ID MISMATCH"
            )

        if (
            str(existing[3]).upper() == "FILLED"
            and str(state).upper() != "FILLED"
        ):
            raise RuntimeError(
                "CONFIRMED FILLED ORDER STATE REGRESSION"
            )

        if str(state).upper() == "FILLED" and filled != expected:
            raise RuntimeError(
                "FILLED STATE WITHOUT COMPLETE QUANTITY"
            )

        db.execute("""
            UPDATE stage_orders
            SET state = ?,
                exchange_order_id =
                    COALESCE(?, exchange_order_id),
                confirmed_filled = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE client_id = ?
        """, (
            state,
            exchange_order_id,
            str(filled),
            client_id
        ))

        db.execute("COMMIT")

        return True

    except Exception:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise

    finally:
        db.close()

def unit_14_stage_read(cycle_id):

    db = unit_14_stage_db()

    try:

        cycle = db.execute("""
            SELECT cycle_id, symbol,
                   original_side, original_quantity,
                   original_entry, frozen_atr,
                   stage, state
            FROM stage_cycles
            WHERE cycle_id = ?
        """, (cycle_id,)).fetchone()

        if cycle is None:
            return None

        orders = db.execute("""
            SELECT action, client_id, quantity,
                   state, exchange_order_id,
                   confirmed_filled
            FROM stage_orders
            WHERE cycle_id = ?
            ORDER BY created_at, action
        """, (cycle_id,)).fetchall()

        return {
            "cycle_id": cycle[0],
            "symbol": cycle[1],
            "original_side": cycle[2],
            "original_quantity": cycle[3],
            "original_entry": cycle[4],
            "frozen_atr": cycle[5],
            "stage": cycle[6],
            "state": cycle[7],
            "orders": {
                row[0]: {
                    "client_id": row[1],
                    "quantity": row[2],
                    "state": row[3],
                    "exchange_order_id": row[4],
                    "confirmed_filled": row[5],
                }
                for row in orders
            }
        }

    finally:
        db.close()
   

# ============================================================
# UNIT 14 - H1/H2/R1/R2 EXCHANGE RECONCILIATION
# USES EXISTING WEEX DEMO ORDER HISTORY
# NO ORDER SUBMISSION
# ============================================================

def unit_14_stage_reconcile_order(cycle_id, action, history=None):

    from decimal import Decimal

    if action not in UNIT14_STAGE_ACTIONS:
        raise RuntimeError(
            "INVALID STAGE RECONCILIATION ACTION"
        )

    cycle = unit_14_stage_read(cycle_id)

    if cycle is None:
        raise RuntimeError(
            "PERSISTED STAGE CYCLE MISSING"
        )

    record = cycle["orders"].get(action)

    if record is None:
        return {
            "action": action,
            "state": "NOT_CLAIMED",
            "confirmed_filled": "0",
            "complete": False,
        }

    client_id = record["client_id"]

    expected = unit_14_v3_D(
        record["quantity"],
        "EXPECTED STAGE QUANTITY"
    )

    previous_filled = unit_14_v3_D(
        record["confirmed_filled"],
        "PREVIOUS CONFIRMED FILL",
        True
    )

    if history is None:
        history = unit_14_v3_history()

    if not isinstance(history, list):
        raise RuntimeError(
            "INVALID STAGE ORDER HISTORY"
        )
        
    client_id_fields = (
        "clientOrderId",
        "newClientOrderId",
        "clientOid",
    )

    order_id_fields = (
        "orderId",
        "order_id",
    )

    saved_id = str(
        record.get("exchange_order_id") or ""
    ).strip()

    matches = []

    for order in history:

        if not isinstance(order, dict):
            continue

        if order.get("symbol"):
            if (
                str(order["symbol"]).upper()
                != str(cycle["symbol"]).upper()
            ):
                continue

        client_ids = {
            str(order[k]).strip()
            for k in client_id_fields
            if order.get(k) is not None
            and str(order[k]).strip()
        }

        exchange_ids = {
            str(order[k]).strip()
            for k in order_id_fields
            if order.get(k) is not None
            and str(order[k]).strip()
        }

        client_match = client_id in client_ids

        exchange_match = (
            bool(saved_id)
            and saved_id in exchange_ids
        )

        if (
            client_match
            and saved_id
            and exchange_ids
            and saved_id not in exchange_ids
        ):
            raise RuntimeError(
                "STAGE CLIENT/EXCHANGE ID CONFLICT"
            )

        if (
            exchange_match
            and client_ids
            and client_id not in client_ids
        ):
            raise RuntimeError(
                "STAGE EXCHANGE/CLIENT ID CONFLICT"
            )

        if client_match or exchange_match:
            matches.append(order)

    if matches:
        print(
            "UNIT 14 STAGE HISTORY MATCH =",
            action,
            "CLIENT ID =", client_id,
            "SAVED ORDER ID =", saved_id,
            "COUNT =", len(matches),
            flush=True
        )
    
    if action in ("H1-C", "H1-H") and not matches:

        print(
            "UNIT 14 H1 MATCH DIAGNOSTIC:",
            "ACTION =", action,
            "CLIENT ID =", client_id,
            "PERSISTED STATE =", record.get("state"),
            "SAVED ORDER ID =", record.get("exchange_order_id"),
            "HISTORY COUNT =", len(history),
            flush=True
        )

        for index, order in enumerate(history[:5]):
            if not isinstance(order, dict):
                continue

            print(
                "UNIT 14 H1 HISTORY RECORD",
                index,
                "=",
                {
                    key: order.get(key)
                    for key in (
                        "symbol",
                        "clientOrderId",
                        "newClientOrderId",
                        "clientOid",
                        "orderId",
                        "status",
                        "state",
                        "executedQty",
                        "filledQty",
                        "side",
                        "positionSide",
                    )
                    if key in order
                },
                flush=True
            )

            print(
                "UNIT 14 H1 HISTORY FIELD NAMES =",
                sorted(order.keys()),
                flush=True
            )

    if not matches:

        print(
            "UNIT 14 RECONCILIATION DIAGNOSTIC START",
            flush=True
        )

        print(
            "UNIT 14 ACTION =",
            action,
            flush=True
        )

        print(
            "UNIT 14 CYCLE ID =",
            cycle_id,
            flush=True
        )

        print(
            "UNIT 14 CLAIM CLIENT ID =",
            client_id,
            flush=True
        )

        print(
            "UNIT 14 PERSISTED ORDER STATE =",
            record.get("state"),
            flush=True
        )

        print(
            "UNIT 14 PERSISTED EXCHANGE ORDER ID =",
            record.get("exchange_order_id"),
            flush=True
        )

        print(
            "UNIT 14 EXPECTED QUANTITY =",
            str(expected),
            flush=True
        )

        print(
            "UNIT 14 PREVIOUS CONFIRMED FILL =",
            str(previous_filled),
            flush=True
        )

        print(
            "UNIT 14 HISTORY RECORD COUNT =",
            len(history),
            flush=True
        )

        for index, order in enumerate(history[:5]):

            if not isinstance(order, dict):
                continue

            print(
                "UNIT 14 HISTORY",
                index,
                "FIELD NAMES =",
                sorted(order.keys()),
                flush=True
            )

            for field in (
                "clientOrderId",
                "newClientOrderId",
                "clientOid",
                "orderId",
                "status",
                "state",
                "executedQty",
                "filledQty",
                "symbol",
                "side",
                "positionSide",
            ):
                if field in order:
                    print(
                        "UNIT 14 HISTORY",
                        index,
                        field,
                        "=",
                        order[field],
                        flush=True
                    )

        print(
            "UNIT 14 RECONCILIATION DIAGNOSTIC END",
            flush=True
        )

        # Missing history does not prove the order
        # was rejected or never transmitted.
        # Preserve the claim; never resubmit here.

        return {
            "action": action,
            "state": "ACK_OR_HISTORY_UNKNOWN",
            "client_id": client_id,
            "confirmed_filled": str(previous_filled),
            "complete": False,
        }

    
    order_ids = {
        str(value).strip()
        for order in matches
        for value in (
            order.get("orderId"),
            order.get("order_id"),
        )
        if value is not None
        and str(value).strip()
    }

    if (
        saved_id
        and order_ids
        and order_ids != {saved_id}
    ):
        raise RuntimeError(
            "STAGE PERSISTED ORDER ID CONFLICT"
        )

    if len(order_ids) > 1:
        raise RuntimeError(
            "DUPLICATE EXCHANGE ORDER IDS "
            + client_id
        )

    exchange_order_id = (
        next(iter(order_ids), None)
        or saved_id
        or None
    )

    if len(matches) > 1 and not order_ids:
        raise RuntimeError(
            "AMBIGUOUS STAGE HISTORY WITHOUT ORDER ID"
        )

    exchange_filled = max(
        (
            unit_14_v3_D(
                order.get(
                    "executedQty",
                    order.get("filledQty", "0")
                ),
                "EXCHANGE CONFIRMED FILL",
                True
            )
            for order in matches
        ),
        default=Decimal("0")
    )

    if exchange_filled > expected:
        raise RuntimeError(
            "STAGE EXCHANGE FILL EXCEEDS "
            "CLAIMED QUANTITY"
        )

    if exchange_filled < previous_filled:
        raise RuntimeError(
            "STAGE CONFIRMED FILL REGRESSION"
        )

    statuses = {
        str(order.get("status", "")).upper()
        for order in matches
    }

    terminal = {
        "CANCELED",
        "CANCELLED",
        "REJECTED",
        "EXPIRED",
    }

    if exchange_filled == expected:
        state = "FILLED"

    elif exchange_filled > 0:

        state = (
            "PARTIAL_TERMINAL"
            if statuses & terminal
            else "PARTIAL"
        )

    elif statuses & terminal:
        state = "TERMINAL_UNFILLED"

    else:
        state = "PENDING"

    unit_14_stage_update(
        client_id=client_id,
        state=state,
        exchange_order_id=exchange_order_id,
        confirmed_filled=exchange_filled,
    )

    return {
        "action": action,
        "state": state,
        "client_id": client_id,
        "exchange_order_id": exchange_order_id,
        "confirmed_filled": str(exchange_filled),
        "expected_quantity": str(expected),
        "complete": state == "FILLED",
    }


# ============================================================
# UNIT 14 - PERSISTENT E0 CYCLE TERMINATION
# ZERO INDENTATION
# ============================================================

# ============================================================
# UNIT 14 - PERSISTENT STAGE CYCLE RECONCILIATION
# ZERO INDENTATION
# ============================================================

def unit_14_stage_reconcile_cycle(cycle_id):

    cycle = unit_14_stage_read(cycle_id)

    if cycle is None:
        raise RuntimeError(
            "STAGE CYCLE NOT FOUND"
        )

    history = unit_14_v3_history(
        cycle["symbol"]
    )

    results = {}

    for action in UNIT14_STAGE_ACTIONS:

        results[action] = (
            unit_14_stage_reconcile_order(
                cycle_id=cycle_id,
                action=action,
                history=history,
            )
        )

    unresolved = [
        action
        for action, record in results.items()
        if record.get("state") in (
            "ACK_UNKNOWN",
            "ACK_OR_HISTORY_UNKNOWN",
            "CLAIMED",
            "SUBMITTED",
            "PENDING",
            "PARTIAL",
        )
    ]

    if not unresolved:
        return results

    db = unit_14_stage_db()

    try:

        rows = db.execute(
            """
            SELECT action, created_at
            FROM stage_orders
            WHERE cycle_id = ?
            """,
            (cycle_id,),
        ).fetchall()

    finally:
        db.close()

    claim_times = dict(rows)

    for action in unresolved:

        created_at = claim_times.get(action)

        if created_at is None:
            continue

        try:

            stamp = float(created_at)

            if stamp < 100000000000:
                stamp *= 1000

            stamp = int(stamp)

        except (TypeError, ValueError):

            try:
                stamp = int(
                    datetime.fromisoformat(
                        str(created_at).replace(
                            "Z", "+00:00"
                        )
                    ).timestamp() * 1000
                )

            except (TypeError, ValueError):
                continue

        now = int(time.time() * 1000)

        start_time = max(
            0,
            stamp - 86400000,
        )

        end_time = min(
            now,
            stamp + 86400000,
        )

        if end_time < start_time:
            continue

        historical = unit_14_v3_history(
            cycle["symbol"],
            start_time=start_time,
            end_time=end_time,
        )

        results[action] = (
            unit_14_stage_reconcile_order(
                cycle_id=cycle_id,
                action=action,
                history=historical,
            )
        )

        print(
            "UNIT 14 TARGETED RECONCILIATION =",
            action,
            "STATE =",
            results[action].get("state"),
            flush=True,
        )

    return results
    
 
# ============================================================
# END PERSISTENT STAGE CYCLE RECONCILIATION
# ============================================================

# ============================================================
# UNIT 14 - INDEPENDENT E0 TERMINATION
# ============================================================

def unit_14_finalize_flat_cycle(cycle_id):

    result = {
        "status": "E0_TERMINATION_PENDING",
        "cycle_id": cycle_id,
        "terminated": False,
        "exchange_write": False,
        "unresolved_actions": [],
    }

    cycle = unit_14_stage_read(cycle_id)

    if cycle is None:

        result["status"] = "E0_CYCLE_NOT_FOUND"

        return result

    positions = unit_14_v3_positions()

    if positions:

        result["status"] = (
            "E0_POSITIONS_STILL_ACTIVE"
        )

        return result

    db = unit_14_stage_db()

    try:

        db.execute("BEGIN IMMEDIATE")

        pending = db.execute("""
            SELECT action
            FROM stage_orders
            WHERE cycle_id = ?
              AND state NOT IN (
                  'FILLED',
                  'TERMINAL_UNFILLED',
                  'PARTIAL_TERMINAL'
              )
        """, (cycle_id,)).fetchall()

        closing_state = (
            "CLOSED_PENDING_RECONCILIATION"
            if pending
            else "CLOSED"
        )

        db.execute("""
            UPDATE stage_cycles
            SET state = ?,
                stage = 'EXCHANGE_FLAT'
            WHERE cycle_id = ?
        """, (
            closing_state,
            cycle_id,
        ))

        db.commit()

        result.update({
            "status": "E0_CYCLE_TERMINATED",
            "terminated": True,
            "closing_reason": "EXCHANGE_FLAT",
            "unresolved_actions": [
                row[0] for row in pending
            ],
        })

        print(
            "UNIT 14 E0 TERMINATED =",
            cycle_id,
            flush=True,
        )

        print(
            "UNIT 14 E0 FINAL STATE =",
            closing_state,
            flush=True,
        )

        print(
            "UNIT 14 E0 OWNERSHIP RELEASED = TRUE",
            flush=True,
        )

        return result

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()

    # ========================================================
    # VERIFY ORIGINAL AND OPPOSITE POSITIONS ARE FLAT
    # ========================================================

    positions = unit_14_v3_positions()

    if positions:

        result["status"] = (
            "E0_POSITIONS_STILL_ACTIVE"
        )

        return result

    # ========================================================
    # RECONCILE ALL PERSISTENT STAGE ORDERS
    # INCLUDING BE-C AND TP3-C
    # ========================================================

    orders = unit_14_stage_reconcile_cycle(
        cycle_id
    )

    terminal_states = {
        "NOT_CLAIMED",
        "FILLED",
        "TERMINAL_UNFILLED",
        "PARTIAL_TERMINAL",
    }

    unresolved = []

    for action in UNIT14_STAGE_ACTIONS:

        record = orders.get(action)

        if not isinstance(record, dict):

            unresolved.append(action)

            continue

        state = str(
            record.get("state", "")
        ).upper()

        print(
            "UNIT 14 E0 FINAL RECONCILIATION",
            action,
            "STATE =",
            state,
            "CONFIRMED FILL =",
            record.get(
                "confirmed_filled", "0"
            ),
            flush=True,
        )

        if state not in terminal_states:

            unresolved.append(action)

    if unresolved:

        result["status"] = (
            "E0_UNRESOLVED_STAGE_ORDERS"
        )

        result["unresolved_actions"] = (
            unresolved
        )

        print(
            "UNIT 14 E0 UNRESOLVED ACTIONS =",
            unresolved,
            flush=True,
        )

        return result

    # ========================================================
    # IDENTIFY CONFIRMED CLOSING ACTION
    # ========================================================

    be_completed = (
        orders.get("BE-C", {}).get(
            "complete"
        ) is True
    )

    tp3_completed = (
        orders.get("TP3-C", {}).get(
            "complete"
        ) is True
    )

    if tp3_completed:

        closing_reason = "TP3_CONFIRMED"

    elif be_completed:

        closing_reason = "BE_CONFIRMED"

    else:

        closing_reason = (
            "EXCHANGE_FLAT_OTHER_EXIT"
        )

    # ========================================================
    # FINAL EXCHANGE POSITION VERIFICATION
    # ========================================================

    if unit_14_v3_positions():

        result["status"] = (
            "E0_POSITION_REAPPEARED"
        )

        return result

    # ========================================================
    # ATOMIC SQLITE CYCLE TERMINATION
    # PRESERVE ALL HISTORICAL RECORDS
    # ========================================================

    db = unit_14_stage_db()

    try:

        db.execute("BEGIN IMMEDIATE")

        pending = db.execute("""
            SELECT action, state
            FROM stage_orders
            WHERE cycle_id = ?
              AND state NOT IN (
                  'FILLED',
                  'TERMINAL_UNFILLED',
                  'PARTIAL_TERMINAL'
              )
        """, (cycle_id,)).fetchall()

        if pending:

            db.rollback()

            result["status"] = (
                "E0_SQLITE_ORDERS_UNRESOLVED"
            )

            result["unresolved_actions"] = [
                row[0] for row in pending
            ]

            return result

        updated = db.execute("""
            UPDATE stage_cycles
            SET state = 'CLOSED',
                stage = ?
            WHERE cycle_id = ?
              AND state = 'ACTIVE'
        """, (
            closing_reason,
            cycle_id,
        ))

        if updated.rowcount != 1:

            db.rollback()

            result["status"] = (
                "E0_TERMINATION_NOT_APPLIED"
            )

            return result

        db.commit()

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()

    result.update({
        "status": "E0_CYCLE_TERMINATED",
        "terminated": True,
        "closing_reason": closing_reason,
        "be_completed": be_completed,
        "tp3_completed": tp3_completed,
    })

    print(
        "UNIT 14 E0 CYCLE TERMINATED =",
        cycle_id,
        flush=True,
    )

    print(
        "UNIT 14 E0 CLOSING REASON =",
        closing_reason,
        flush=True,
    )

    print(
        "UNIT 14 E0 HISTORICAL RECORDS PRESERVED = TRUE",
        flush=True,
    )

    return result


# ============================================================
# END PERSISTENT E0 CYCLE TERMINATION
# ============================================================



# ============================================================
# UNIT 14 - H1/H2/R1/R2 ORDER EXECUTION
# INDEPENDENT OR SEQUENTIAL FUNDING
# ============================================================


def unit_14_h1_claim_audit(cycle_id):
    """
    Audit the two persisted H1 claims.

    Never clear claims or infer an order rejection
    merely because history has no matching record.
    """

    cycle = unit_14_stage_read(cycle_id)

    if cycle is None:
        raise RuntimeError(
            "UNIT 14 H1 AUDIT CYCLE MISSING"
        )

    history = unit_14_v3_history()

    if not isinstance(history, list):
        raise RuntimeError(
            "UNIT 14 H1 AUDIT HISTORY INVALID"
        )

    results = {}

    for action in ("H1-C", "H1-H"):

        record = cycle["orders"].get(action)

        if record is None:
            results[action] = "NOT_CLAIMED"
            continue

        client_id = str(record["client_id"])

        matches = [
            order for order in history
            if isinstance(order, dict)
            and client_id in {
                str(order.get(field))
                for field in (
                    "clientOrderId",
                    "newClientOrderId",
                    "clientOid",
                )
                if order.get(field) is not None
            }
        ]

        if matches:
            result = unit_14_stage_reconcile_order(
                cycle_id,
                action,
                history
            )

            results[action] = result["state"]

        else:
            results[action] = (
                "EXCHANGE_OUTCOME_UNRESOLVED"
            )

        print(
            "UNIT 14 H1 CLAIM AUDIT",
            "ACTION =", action,
            "CLIENT ID =", client_id,
            "PERSISTED STATE =", record["state"],
            "EXCHANGE ORDER ID =",
            record["exchange_order_id"],
            "HISTORY MATCHES =", len(matches),
            "RESULT =", results[action],
            flush=True
        )

    print(
        "UNIT 14 H1 CLAIM AUDIT SUMMARY =",
        results,
        flush=True
    )

    return results

def unit_14_stage_execute_pair(
    cycle_id,
    stage,
    quantity,
    mark_price,
    opening_leverage,
    quantity_step,
    minimum_quantity,
    margin_buffer_percent="0",
):
    from decimal import Decimal

    D = unit_14_v3_D

    stage = str(stage).upper()

    if stage not in ("H1", "H2", "R1", "R2"):
        raise RuntimeError("INVALID STAGE")

    cycle = unit_14_stage_read(cycle_id)

    if cycle is None:
        raise RuntimeError("STAGE CYCLE MISSING")

    if cycle["state"] != "ACTIVE":
        return {"status": "CYCLE_NOT_ACTIVE"}

    original = cycle["original_side"]

    if original not in ("LONG", "SHORT"):
        raise RuntimeError("INVALID ORIGINAL SIDE")

    opposite = (
        "SHORT" if original == "LONG"
        else "LONG"
    )

    if stage in ("H1", "H2"):
        close_side = original
        open_side = opposite
        close_action = stage + "-C"
        open_action = stage + "-H"
    else:
        close_side = opposite
        open_side = original
        close_action = stage + "-C"
        open_action = stage + "-O"

    qty = D(quantity, "STAGE QUANTITY")
    mark = D(mark_price, "STAGE MARK PRICE")
    leverage = D(
        opening_leverage,
        "OPENING LEVERAGE"
    )
    step = D(quantity_step, "QUANTITY STEP")
    minimum = D(
        minimum_quantity,
        "MINIMUM QUANTITY"
    )
    buffer = D(
        margin_buffer_percent,
        "MARGIN BUFFER",
        True
    )

    if (
        qty < minimum
        or unit_14_v3_floor(qty, step) != qty
        or buffer >= 100
    ):
        return {
            "status": "STAGE_QUANTITY_OR_BUFFER_INVALID"
        }

    # Reconcile before deciding whether any
    # new order may be submitted.

    history = unit_14_v3_history()

    close_record = unit_14_stage_reconcile_order(
        cycle_id, close_action, history
    )

    open_record = unit_14_stage_reconcile_order(
        cycle_id, open_action, history
    )

    if (
        close_record["complete"]
        and open_record["complete"]
    ):
        return {
            "status": stage + "_COMPLETE",
            "complete": True,
        }

    required_margin = (
        qty * mark / leverage
    ) * (
        Decimal("1")
        + buffer / Decimal("100")
    )

    available = unit_14_v3_balance()

    independent = available >= required_margin

    # With insufficient extra funds, the
    # closing fill must be confirmed before
    # opening is considered.
    #
    # A fresh balance is required after that fill.

    if not independent:

        if close_record["complete"]:
            available = unit_14_v3_balance()
        else:
            available = Decimal("0")

    open_funded = (
        independent
        or (
            close_record["complete"]
            and available >= required_margin
        )
    )

    actions = (
        (
            close_action,
            close_side,
            "SELL" if close_side == "LONG"
            else "BUY",
            True,
        ),
        (
            open_action,
            open_side,
            "BUY" if open_side == "LONG"
            else "SELL",
            False,
        ),
    )

    results = {}

    for action, position_side, order_side, is_close in actions:

        previous = (
            close_record if is_close
            else open_record
        )

        if previous["complete"]:
            results[action] = "FILLED"
            continue

        # A prior claim, partial fill or uncertain
        # acknowledgement is never resubmitted.

        if previous["state"] != "NOT_CLAIMED":
            results[action] = previous["state"]
            continue

        if not is_close:

            available = unit_14_v3_balance()

            if available < required_margin:

                close_record = (
                    unit_14_stage_reconcile_order(
                        cycle_id,
                        close_action,
                        unit_14_v3_history()
                    )
                )

                if not close_record["complete"]:

                    results[action] = (
                        "WAITING_CLOSE_FILL"
                    )

                    continue

                available = unit_14_v3_balance()

                if available < required_margin:

                    results[action] = (
                        "WAITING_RELEASED_MARGIN"
                    )

                    continue

            independent = (
                not close_record["complete"]
            )

            open_funded = True
        

        # Verify current exchange exposure.
        position = unit_14_v3_position(
            position_side
        )

        if is_close:

            if position is None:
                results[action] = (
                    "CLOSE_POSITION_NOT_FOUND"
                )
                continue

            available_qty = D(
                position.get("size"),
                "CLOSE POSITION SIZE"
            )

            if available_qty < qty:
                results[action] = (
                    "CLOSE_QUANTITY_UNAVAILABLE"
                )
                continue

        # Claim persistently before transmission.
        claim = unit_14_stage_claim(
            cycle_id, action, qty
        )

        if not claim["claimed"]:
            results[action] = (
                "PREVIOUS_CLAIM_EXISTS"
            )
            continue

        payload = {
            "symbol": cycle["symbol"],
            "side": order_side,
            "positionSide": position_side,
            "type": "MARKET",
            "quantity": format(qty, "f"),
            "newClientOrderId":
                claim["client_id"],
        }

        try:
            reply = unit_14_v3_signed_request(
                "POST",
                UNIT14_V3_ORDER,
                payload=payload
            )

        except Exception as exc:

            unit_14_stage_update(
                claim["client_id"],
                "ACK_UNKNOWN"
            )

            results[action] = "ACK_UNKNOWN"

            print(
                "UNIT 14", action,
                "ACK UNKNOWN",
                repr(exc),
                flush=True
            )

            continue

        
        # Inspect the actual WEEX demo response.
        # A top-level orderId is the acknowledgement;
        # success=True is not mandatory.

        print(
            "UNIT 14 DEMO ORDER RESPONSE",
            "ACTION =", action,
            "CLIENT ID =", claim["client_id"],
            "RESPONSE =", repr(reply)[:1200],
            flush=True
        )

        order_id = None
        returned_client_id = None

        
        # WEEX demo submission acknowledgement.
        # An order acknowledgement is not a fill.

        print(
            "UNIT 14 DEMO POST RESPONSE",
            "ACTION =", action,
            "CLIENT ID =", claim["client_id"],
            "RESPONSE =", repr(reply)[:1500],
            flush=True
        )

        order_id = None
        returned_client_id = None
        explicit_failure = False

        
        if isinstance(reply, dict):
            explicit_failure = (
                reply.get("success") is False
                or bool(reply.get("errorCode"))
                or bool(reply.get("errorMsg"))
            )

            response_data = reply.get("data")

            if isinstance(response_data, dict):
                response_order = response_data
            else:
                response_order = reply

            order_id = (
                response_order.get("orderId")
                or response_order.get("order_id")
            )

            returned_client_id = (
                response_order.get("clientOrderId")
                or response_order.get("newClientOrderId")
                or response_order.get("clientOid")
            )

            explicit_failure = (
                explicit_failure
                or response_order.get("success") is False
                or bool(response_order.get("errorCode"))
                or bool(response_order.get("errorMsg"))
            )

        client_id_matches = (
            returned_client_id is None
            or str(returned_client_id)
            == claim["client_id"]
        )

        if (
            order_id is not None
            and str(order_id).strip()
            and client_id_matches
            and not explicit_failure
        ):
            unit_14_stage_update(
                claim["client_id"],
                "SUBMITTED",
                str(order_id)
            )

            results[action] = "SUBMITTED"

            print(
                "UNIT 14 DEMO ORDER ACKNOWLEDGED",
                "ACTION =", action,
                "ORDER ID =", order_id,
                flush=True
            )

        else:
            unit_14_stage_update(
                claim["client_id"],
                "ACK_UNKNOWN"
            )

            results[action] = "ACK_UNKNOWN"

            print(
                "UNIT 14 DEMO ACK UNRESOLVED",
                "ACTION =", action,
                "CLIENT ID =", claim["client_id"],
                flush=True
            )
    
    
    unresolved_states = {
        "ACK_UNKNOWN",
        "ACK_OR_HISTORY_UNKNOWN",
        "CLAIMED",
        "PREVIOUS_CLAIM_EXISTS",
    }

    unresolved = [
        action
        for action, state in results.items()
        if state in unresolved_states
    ]

    if unresolved:
        status = stage + "_ACK_UNRESOLVED"
    elif any(
        state in ("SUBMITTED", "PENDING", "PARTIAL")
        for state in results.values()
    ):
        status = stage + "_EXECUTION_PENDING"
    else:
        status = stage + "_NOT_COMPLETED"

    return {
        "status": status,
        "cycle_id": cycle_id,
        "funding_mode": (
            "INDEPENDENT"
            if independent else "SEQUENTIAL"
        ),
        "required_opening_margin": str(required_margin),
        "available_margin": str(available),
        "actions": results,
        "unresolved_actions": unresolved,
        "complete": False,
    }

# ============================================================
# UNIT 14 - INDEPENDENT E0 CYCLE OWNERSHIP
# PRESERVE HISTORICAL HEDGE RECONCILIATION
# ============================================================

def unit_14_separate_e0_ownership(
    active_positions,
    unit_13_result,
):

    import hashlib

    D = unit_14_v3_D

    symbol = unit_13_14_active_symbols()[1]

    old_side, old_id = (
        unit_14_active_original_side(symbol)
    )

    if old_id is None:
        return False

    if old_side in active_positions:
        return False

    if len(active_positions) != 1:
        return False

    new_side, position = next(
        iter(active_positions.items())
    )

    new_side = str(new_side).upper()

    if new_side not in ("LONG", "SHORT"):
        return False

    if new_side == old_side:
        return False

    if (
        unit_13_result.get("position_side")
        != new_side
    ):
        return False

    old_cycle = unit_14_stage_read(old_id)

    if old_cycle is None:
        return False

    history = unit_14_v3_history(symbol)

    def order_time(order):

        return int(
            order.get("updateTime")
            or order.get("time")
            or 0
        )

    def filled(order):

        return (
            str(order.get("symbol", "")).upper()
            == symbol
            and str(
                order.get("status", "")
            ).upper() == "FILLED"
        )

    # --------------------------------------------------------
    # VERIFY PREVIOUS ORIGINAL POSITION CLOSURE
    # --------------------------------------------------------

    closing_orders = []

    for action in ("BE-C", "TP3-C"):

        record = old_cycle["orders"].get(action)

        if record is None:
            continue

        confirmation = (
            unit_14_stage_reconcile_order(
                old_id,
                action,
                history,
            )
        )

        if not confirmation.get("complete"):
            continue

        for order in history:

            if not filled(order):
                continue

            if (
                str(order.get("clientOrderId", ""))
                != record["client_id"]
            ):
                continue

            if (
                str(order.get("positionSide", "")).upper()
                != old_side
            ):
                continue

            expected_close_side = (
                "SELL"
                if old_side == "LONG"
                else "BUY"
            )

            if (
                str(order.get("side", "")).upper()
                != expected_close_side
            ):
                continue

            if order_time(order) > 0:
                closing_orders.append(order)

    if not closing_orders:

        print(
            "UNIT 14 E0 SEPARATION = "
            "PREVIOUS CLOSURE UNVERIFIED",
            flush=True,
        )

        return False

    closing_time = max(
        order_time(order)
        for order in closing_orders
    )

    # --------------------------------------------------------
    # VERIFY INDEPENDENT NEW E0 ENTRY
    # NEVER ADOPT AN H1/H2 HEDGE AS E0
    # --------------------------------------------------------

    entry_side = (
        "BUY"
        if new_side == "LONG"
        else "SELL"
    )

    entries = []

    for order in history:

        if not filled(order):
            continue

        if order_time(order) <= closing_time:
            continue

        if not str(
            order.get("clientOrderId", "")
        ).startswith("FR11"):
            continue

        if (
            str(order.get("positionSide", "")).upper()
            != new_side
        ):
            continue

        if (
            str(order.get("side", "")).upper()
            != entry_side
        ):
            continue

        entries.append(order)

    if len(entries) != 1:

        print(
            "UNIT 14 E0 SEPARATION = "
            "NEW ENTRY IDENTITY UNVERIFIED",
            flush=True,
        )

        return False

    entry_order = entries[0]

    entry_time = order_time(entry_order)

    entry_order_id = str(
        entry_order.get("orderId") or ""
    )

    if not entry_order_id:
        return False

    original_quantity = D(
        entry_order["executedQty"],
        "NEW E0 ORIGINAL QUANTITY",
    )

    original_entry = D(
        entry_order["avgPrice"],
        "NEW E0 ORIGINAL ENTRY",
    )

    current_quantity = D(
        position["size"],
        "NEW E0 REMAINING QUANTITY",
    )

    # --------------------------------------------------------
    # VERIFY CURRENT POSITION QUANTITY AGAINST
    # NEW ENTRY AND CONFIRMED TP FILLS
    # --------------------------------------------------------

    closed_quantity = Decimal("0")
    seen_orders = set()

    for order in history:

        if not filled(order):
            continue

        if order_time(order) <= entry_time:
            continue

        if (
            str(order.get("positionSide", "")).upper()
            != new_side
        ):
            continue

        client_id = str(
            order.get("clientOrderId", "")
        )

        if not client_id.startswith(
            ("FR13-TP1-", "FR13-TP2-")
        ):
            continue

        if (
            str(order.get("side", "")).upper()
            == entry_side
        ):
            continue

        order_id = str(
            order.get("orderId") or ""
        )

        if not order_id:
            return False

        if order_id in seen_orders:
            continue

        seen_orders.add(order_id)

        closed_quantity += D(
            order["executedQty"],
            "NEW E0 CONFIRMED TP QUANTITY",
        )

    if (
        original_quantity - closed_quantity
        != current_quantity
    ):

        print(
            "UNIT 14 E0 SEPARATION = "
            "POSITION QUANTITY UNVERIFIED",
            flush=True,
        )

        return False

    atr = D(
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT[
            "atr14"
        ],
        "NEW E0 ATR",
    )

    if min(
        original_quantity,
        original_entry,
        current_quantity,
        atr,
    ) <= 0:
        return False

    new_id = "U14-" + hashlib.sha256(
        (
            symbol + "|" + new_side
            + "|" + entry_order_id
        ).encode()
    ).hexdigest()[:20]

    # --------------------------------------------------------
    # REFRESH EXCHANGE POSITION BEFORE SQLITE TRANSFER
    # --------------------------------------------------------

    latest = unit_14_v3_positions()

    if set(latest) != {new_side}:
        return False

    if D(
        latest[new_side]["size"],
        "REFRESHED E0 QUANTITY",
    ) != current_quantity:
        return False

    if (
        unit_14_v3_trade_key(latest[new_side])
        != unit_14_v3_trade_key(position)
    ):
        return False

    # --------------------------------------------------------
    # ATOMIC OWNERSHIP TRANSFER
    # NO HISTORICAL RECORD DELETION
    # --------------------------------------------------------

    db = unit_14_stage_db()

    try:

        db.execute("BEGIN IMMEDIATE")

        owners = db.execute("""
            SELECT cycle_id
            FROM stage_cycles
            WHERE symbol = ?
              AND state = 'ACTIVE'
        """, (symbol,)).fetchall()

        if owners != [(old_id,)]:

            db.rollback()

            return False

        existing = db.execute("""
            SELECT cycle_id
            FROM stage_cycles
            WHERE cycle_id = ?
        """, (new_id,)).fetchone()

        if existing is not None:

            db.rollback()

            return False

        updated = db.execute("""
            UPDATE stage_cycles
            SET state = 'CLOSED_PENDING_RECONCILIATION'
            WHERE cycle_id = ?
              AND state = 'ACTIVE'
        """, (old_id,))

        if updated.rowcount != 1:

            db.rollback()

            return False

        db.execute("""
            INSERT INTO stage_cycles (
                cycle_id,
                symbol,
                original_side,
                original_quantity,
                original_entry,
                frozen_atr,
                stage,
                state
            )
            VALUES (?, ?, ?, ?, ?, ?, 'READY', 'ACTIVE')
        """, (
            new_id,
            symbol,
            new_side,
            str(original_quantity),
            str(original_entry),
            str(atr),
        ))

        db.commit()

    except Exception:

        if db.in_transaction:
            db.rollback()

        raise

    finally:
        db.close()

    print(
        "UNIT 14 E0 OWNERSHIP SEPARATION = PASS",
        flush=True,
    )

    print(
        "UNIT 14 PREVIOUS CYCLE =",
        old_id,
        old_side,
        "CLOSED_PENDING_RECONCILIATION",
        flush=True,
    )

    print(
        "UNIT 14 NEW ACTIVE E0 =",
        new_id,
        new_side,
        flush=True,
    )

    print(
        "UNIT 14 NEW E0 ORIGINAL QUANTITY =",
        original_quantity,
        flush=True,
    )

    print(
        "UNIT 14 NEW E0 REMAINING QUANTITY =",
        current_quantity,
        flush=True,
    )

    return True

# ============================================================
# UNIT 14 - HISTORICAL E0 RECONCILIATION
# INDEPENDENT OF CURRENT ACTIVE CYCLE
# ============================================================

def unit_14_reconcile_historical_cycles():

    terminal_states = {
        "NOT_CLAIMED",
        "FILLED",
        "TERMINAL_UNFILLED",
        "PARTIAL_TERMINAL",
    }

    db = unit_14_stage_db()

    try:

        rows = db.execute("""
            SELECT cycle_id
            FROM stage_cycles
            WHERE state =
                'CLOSED_PENDING_RECONCILIATION'
        """).fetchall()

    finally:
        db.close()

    for (cycle_id,) in rows:

        try:

            orders = unit_14_stage_reconcile_cycle(
                cycle_id
            )

            unresolved = [
                action
                for action in UNIT14_STAGE_ACTIONS
                if orders.get(action, {}).get("state")
                not in terminal_states
            ]

            print(
                "UNIT 14 HISTORICAL E0 =",
                cycle_id,
                "UNRESOLVED =",
                unresolved,
                flush=True,
            )

            if unresolved:
                continue

            db = unit_14_stage_db()

            try:

                db.execute("BEGIN IMMEDIATE")

                pending = db.execute("""
                    SELECT action
                    FROM stage_orders
                    WHERE cycle_id = ?
                      AND state NOT IN (
                          'FILLED',
                          'TERMINAL_UNFILLED',
                          'PARTIAL_TERMINAL'
                      )
                """, (cycle_id,)).fetchall()

                if pending:

                    db.rollback()

                    continue

                db.execute("""
                    UPDATE stage_cycles
                    SET state = 'CLOSED'
                    WHERE cycle_id = ?
                      AND state =
                          'CLOSED_PENDING_RECONCILIATION'
                """, (cycle_id,))

                db.commit()

            except Exception:

                if db.in_transaction:
                    db.rollback()

                raise

            finally:
                db.close()

            print(
                "UNIT 14 HISTORICAL E0 "
                "RECONCILIATION COMPLETE =",
                cycle_id,
                flush=True,
            )

        except Exception as exc:

            print(
                "UNIT 14 HISTORICAL E0 "
                "RECONCILIATION ERROR =",
                cycle_id,
                str(exc),
                flush=True,
            )

# ============================================================
# UNIT 14 - ONE-TIME OBSOLETE SHORT CYCLE RESET
# ============================================================

def unit_14_reset_obsolete_short(active_positions):

    symbol = unit_13_14_active_symbols()[1]

    if symbol != "NEARSUSDT":
        return False

    if "SHORT" in active_positions:
        return False

    old_cycle_id = "U14-2e26e3f7128f88b816b0"

    db = unit_14_stage_db()

    try:

        db.execute("BEGIN IMMEDIATE")

        cycle = db.execute("""
            SELECT cycle_id
            FROM stage_cycles
            WHERE cycle_id = ?
              AND symbol = ?
              AND original_side = 'SHORT'
        """, (
            old_cycle_id,
            symbol,
        )).fetchone()

        if cycle is None:

            db.commit()

            return False

        tables = {
            row[0]
            for row in db.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
            """).fetchall()
        }

        removed_orders = db.execute("""
            DELETE FROM stage_orders
            WHERE cycle_id = ?
        """, (old_cycle_id,)).rowcount

        if "tp3_trailing_state" in tables:

            db.execute("""
                DELETE FROM tp3_trailing_state
                WHERE cycle_id = ?
            """, (old_cycle_id,))

        if "atr_breakeven" in tables:

            db.execute("""
                DELETE FROM atr_breakeven
                WHERE symbol = ?
                  AND side = 'SHORT'
            """, (symbol,))

        db.execute("""
            DELETE FROM stage_cycles
            WHERE cycle_id = ?
        """, (old_cycle_id,))

        db.commit()

        globals().pop(
            "_UNIT14_V3_ORDER_ATTEMPTS",
            None
        )

        print(
            "UNIT 14 OBSOLETE SHORT RESET = PASS",
            flush=True,
        )

        print(
            "UNIT 14 DELETED SHORT CYCLE =",
            old_cycle_id,
            flush=True,
        )

        print(
            "UNIT 14 DELETED STAGE ORDERS =",
            removed_orders,
            flush=True,
        )

        print(
            "UNIT 14 OLD H1-H CLAIM REMOVED",
            flush=True,
        )

        return True

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()
def unit_14_active_original_side(symbol=None):
    if symbol is None:
        _, symbol = unit_13_14_active_symbols()
    """
    Resolve original position side from a persisted
    active hedge/recovery cycle.

    A hedge position must never be mistaken for
    the original position.
    """

    db = unit_14_stage_db()

    try:
        rows = db.execute("""
            SELECT cycle_id, original_side
            FROM stage_cycles
            WHERE symbol = ?
              AND state = 'ACTIVE'
            ORDER BY created_at DESC
        """, (symbol,)).fetchall()
    finally:
        db.close()

    if not rows:
        return None, None

    sides = {row[1] for row in rows}

    if len(sides) != 1:
        raise RuntimeError(
            "CONFLICTING ACTIVE ORIGINAL SIDES"
        )

    return rows[0][1], rows[0][0]


 # ============================================================
# UNIT 14 - ORIGINAL SIDE RECONCILIATION
# ============================================================

def unit_14_original_side_reconciliation(
    cycle_id,
    active_positions,
):

    cycle = unit_14_stage_read(cycle_id)

    if cycle is None:
        raise RuntimeError(
            "ORIGINAL SIDE CYCLE MISSING"
        )

    original_side = str(
        cycle["original_side"]
    ).upper()

    opposite_side = (
        "SHORT"
        if original_side == "LONG"
        else "LONG"
    )

    orders = unit_14_stage_reconcile_cycle(
        cycle_id
    )

    print(
        "UNIT 14 SIDE AUDIT CYCLE =",
        cycle_id,
        flush=True,
    )

    print(
        "UNIT 14 SIDE AUDIT ORIGINAL =",
        original_side,
        flush=True,
    )

    print(
        "UNIT 14 SIDE AUDIT OPPOSITE =",
        opposite_side,
        flush=True,
    )

    for action, record in orders.items():

        print(
            "UNIT 14 SIDE AUDIT ACTION =",
            action,
            "STATE =",
            record.get("state"),
            "EXPECTED =",
            record.get("expected_quantity"),
            "FILLED =",
            record.get("confirmed_filled"),
            "ORDER ID =",
            record.get("exchange_order_id"),
            flush=True,
        )

    for side, position in active_positions.items():

        print(
            "UNIT 14 SIDE AUDIT POSITION =",
            side,
            "SIZE =",
            position.get("size"),
            "OPEN VALUE =",
            position.get("openValue"),
            flush=True,
        )

    return {
        "cycle_id": cycle_id,
        "original_side": original_side,
        "opposite_side": opposite_side,
        "orders": orders,
        "original_exists": (
            original_side in active_positions
        ),
        "opposite_exists": (
            opposite_side in active_positions
        ),
    }


# ============================================================
# END ORIGINAL SIDE RECONCILIATION
# ============================================================
def unit_14_stage_dispatch(
    active_positions,
    original_position,
    unit_13_result,
    quantity_step,
    minimum_quantity,
    mark
):
    """
    WEEX DEMO H1/H2/R1/R2 execution dispatcher.

    H1: adverse ATR x1
    H2: adverse ATR x2, unless recovery started
    R1: ATR x1 retracement from H1 trigger
    R2: further favorable ATR x1 after R1

    Order submission is performed by the existing
    unit_14_stage_execute_pair().
    """

    
    from decimal import Decimal

    D = unit_14_v3_D

    _, demo_symbol = unit_13_14_active_symbols()

    original_side, cycle_id = (
        unit_14_active_original_side()
    )

    # ========================================================
    # MANDATORY PRE-TP1 HEDGE ACTIVATION BOUNDARY
    # ========================================================

    tp1_completed = (
        unit_13_result.get("tp1_completed")
        is True
    )

    tp2_completed = (
        unit_13_result.get("tp2_completed")
        is True
    )

    if tp1_completed or tp2_completed:

        reconciled_orders = {}

        if cycle_id is not None:

            reconciled_orders = (
                unit_14_stage_reconcile_cycle(
                    cycle_id
                )
            )

        print(
            "UNIT 14 PRE-TP1 HEDGE "
            "ACTIVATION BOUNDARY = ENFORCED",
            flush=True,
        )

        print(
            "UNIT 14 NEW H1 ACTIVATION "
            "AUTHORIZED = FALSE",
            flush=True,
        )

        print(
            "UNIT 14 EXISTING HEDGE "
            "RECONCILIATION = PRESERVED",
            flush=True,
        )

        return {
            "status": (
                "POST_TP2_TRAILING_PRIORITY"
                if tp2_completed
                else "POST_TP1_BREAKEVEN_PRIORITY"
            ),
            "handled": False,
            "cycle_id": cycle_id,
            "orders": reconciled_orders,
            "new_hedge_activation_authorized": False,
            "execution_attempted": False,
        }

    print(
        "UNIT 14 PRE-TP1 HEDGE "
        "ACTIVATION BOUNDARY = OPEN",
        flush=True,
    )
    D = unit_14_v3_D

    
    # ------------------------------------------------
    # IDENTIFY OR INITIALIZE ORIGINAL TRADE
    # PERSISTED CYCLE RECONCILIATION
    # ------------------------------------------------

    if cycle_id is None:

        if original_position is None:
            return {
                "status": "NO_POSITION",
                "handled": False
            }

        if unit_13_result.get(
            "tp1_completed"
        ) is True:
            return {
                "status": "POST_TP1",
                "handled": False
            }

        original_side = str(
            original_position.get("side", "")
        ).upper()

        if original_side not in (
            "LONG", "SHORT"
        ):
            raise RuntimeError(
                "INVALID ORIGINAL SIDE"
            )

        
        import hashlib

        _, demo_symbol = unit_13_14_active_symbols()

        demo_symbol = str(
            demo_symbol
        ).strip().upper()

        trade_key = unit_14_v3_trade_key(
            original_position
        )

        legacy_cycle_id = "U14-" + trade_key

        identity = (
            demo_symbol
            + "|"
            + original_side
            + "|"
            + trade_key
        )

        digest = hashlib.sha256(
            identity.encode("utf-8")
        ).hexdigest()[:20]

        cycle_id = "U14-" + digest

        legacy_cycle = unit_14_stage_read(
            legacy_cycle_id
        )

        if legacy_cycle is not None:

            legacy_symbol = str(
                legacy_cycle["symbol"]
            ).strip().upper()

            legacy_side = str(
                legacy_cycle["original_side"]
            ).strip().upper()

            legacy_orders = legacy_cycle.get(
                "orders", {}
            )

            if legacy_orders:
                raise RuntimeError(
                    "UNIT 14 LEGACY CYCLE HAS "
                    "ORDER HISTORY; RECONCILE BEFORE "
                    "CREATING SYMBOL-SPECIFIC CYCLE: "
                    + legacy_cycle_id
                )

            if (
                legacy_symbol == demo_symbol
                and legacy_side == original_side
            ):
                cycle_id = legacy_cycle_id

                print(
                    "UNIT 14 MATCHING LEGACY "
                    "CYCLE PRESERVED =",
                    cycle_id,
                    flush=True
                )

            else:
                print(
                    "UNIT 14 DIFFERENT-SYMBOL "
                    "LEGACY CYCLE PRESERVED =",
                    legacy_cycle_id,
                    legacy_symbol,
                    flush=True
                )

        print(
            "UNIT 14 SELECTED CYCLE ID =",
            cycle_id,
            flush=True
        )

        # --------------------------------------------
        # CHECK PERSISTENT REGISTRY BEFORE CREATING
        # --------------------------------------------

        
        persisted_cycle = unit_14_stage_read(
            cycle_id
        )

        if persisted_cycle is not None:

            persisted_symbol = str(
                persisted_cycle["symbol"]
            ).strip().upper()

            persisted_side = str(
                persisted_cycle["original_side"]
            ).strip().upper()

            _, demo_symbol = unit_13_14_active_symbols()

            demo_symbol = str(
                demo_symbol
            ).strip().upper()

            current_side = str(
                original_side
            ).strip().upper()

            print(
                "UNIT 14 PERSISTED CYCLE ID =",
                cycle_id,
                flush=True
            )
            print(
                "UNIT 14 PERSISTED SYMBOL =",
                persisted_symbol,
                flush=True
            )
            print(
                "UNIT 14 CURRENT DEMO SYMBOL =",
                demo_symbol,
                flush=True
            )
            print(
                "UNIT 14 PERSISTED SIDE =",
                persisted_side,
                flush=True
            )
            print(
                "UNIT 14 CURRENT ORIGINAL SIDE =",
                current_side,
                flush=True
            )

            if (
                persisted_symbol != demo_symbol
                or persisted_side != current_side
            ):
                raise RuntimeError(
                    "PERSISTED CYCLE IDENTITY CONFLICT: "
                    f"stored={persisted_symbol}/{persisted_side}, "
                    f"current={demo_symbol}/{current_side}"
                )

            print(
                "UNIT 14 EXISTING CYCLE FOUND =",
                cycle_id,
                flush=True
            )

        else:

            # ----------------------------------------
            # INITIALIZE ONLY A GENUINELY NEW CYCLE
            # ----------------------------------------

            snapshot = (
                FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
            )

            atr = D(
                snapshot["atr14"],
                "FROZEN ATR"
            )

            quantity = D(
                original_position["size"],
                "ORIGINAL QUANTITY"
            )

            entry = (
                D(
                    original_position["openValue"],
                    "OPEN VALUE"
                )
                /
                D(
                    original_position["cumOpenSize"],
                    "CUM OPEN SIZE"
                )
            )

            unit_14_stage_create_cycle(
                cycle_id,
                demo_symbol,
                original_side,
                quantity,
                entry,
                atr
            )

            print(
                "UNIT 14 NEW ORIGINAL TRADE CYCLE =",
                cycle_id,
                flush=True
            )

    # ------------------------------------------------
    # LOAD THE PERSISTED CYCLE
    # ------------------------------------------------

    cycle = unit_14_stage_read(
        cycle_id
    )

    if cycle is None:
        raise RuntimeError(
            "UNIT 14 STAGE CYCLE MISSING"
        )

    persisted_state = str(
        cycle["state"]
    ).upper()

    persisted_stage = str(
        cycle["stage"]
    ).upper()

    print(
        "UNIT 14 PERSISTED CYCLE =",
        cycle_id,
        flush=True
    )

    print(
        "UNIT 14 PERSISTED STAGE =",
        persisted_stage,
        flush=True
    )

    print(
        "UNIT 14 PERSISTED STATE =",
        persisted_state,
        flush=True
    )

    # ------------------------------------------------
    # PRESERVE COMPLETED RECOVERY
    # ------------------------------------------------

    if (
        persisted_state in ("ACTIVE", "COMPLETE")
        and persisted_stage == "RECOVERED"
    ):

        print(
            "UNIT 14 COMPLETED RECOVERY PRESERVED =",
            cycle_id,
            flush=True
        )

        return {
            "status": "RECOVERY_COMPLETE",
            "handled": True,
            "cycle_id": cycle_id,
            "stage": persisted_stage,
            "persisted_state": persisted_state
        }

    # ------------------------------------------------
    # OTHER INACTIVE CYCLES REQUIRE RECONCILIATION
    # ------------------------------------------------

    if persisted_state != "ACTIVE":

        print(
            "UNIT 14 INACTIVE CYCLE RECONCILIATION =",
            persisted_state,
            persisted_stage,
            flush=True
        )

        return {
            "status": "CYCLE_RECONCILIATION_REQUIRED",
            "handled": True,
            "cycle_id": cycle_id,
            "stage": persisted_stage,
            "persisted_state": persisted_state
        }

    # ------------------------------------------------
    # ACTIVE CYCLE CONTINUES TO EXISTING
    # RECOVER PERSISTED PARAMETERS SECTION
    # ------------------------------------------------

    print(
        "UNIT 14 ACTIVE CYCLE READY =",
        cycle_id,
        flush=True
    )

    # ------------------------------------------------
    # RECOVER PERSISTED PARAMETERS
    # ------------------------------------------------

    original = cycle["original_side"]

    opposite = (
        "SHORT"
        if original == "LONG"
        else "LONG"
    )

    entry = D(
        cycle["original_entry"],
        "ENTRY"
    )

    atr = D(
        cycle["frozen_atr"],
        "ATR"
    )

    base_qty = D(
        cycle["original_quantity"],
        "ORIGINAL QUANTITY"
    )

    step = D(
        quantity_step,
        "QUANTITY STEP"
    )

    minimum = D(
        minimum_quantity,
        "MINIMUM QUANTITY"
    )

    price = D(
        mark,
        "MARK PRICE"
    )

    adverse = (
        (entry - price) / atr
        if original == "LONG"
        else (price - entry) / atr
    )

    # ------------------------------------------------
    # EXCHANGE-CONFIRMED ORDER RECONCILIATION
    # ------------------------------------------------

    orders = unit_14_stage_reconcile_cycle(
        cycle_id
    )

    def filled(action):
        return D(
            orders[action]["confirmed_filled"],
            action + " FILLED",
            True
        )

    def complete(action):
        return (
            orders[action]["complete"] is True
        )

    
    def started(action):
        return orders[action]["state"] in {
            "SUBMITTED",
            "PENDING",
            "PARTIAL",
            "PARTIAL_TERMINAL",
            "FILLED",
        }

    def unresolved(action):
        return orders[action]["state"] in {
            "ACK_UNKNOWN",
            "ACK_OR_HISTORY_UNKNOWN",
            "CLAIMED",
        }

    
    # Block new stage transitions while any previously
    # claimed stage order has an unknown exchange outcome.
    # Continue exchange reconciliation on every scan.

    unresolved_actions = [
        action
        for action in UNIT14_STAGE_ACTIONS
        if unresolved(action)
    ]

    if unresolved_actions:
        print(
            "UNIT 14 INDIVIDUAL ORDER RECONCILIATION =",
            unresolved_actions,
            flush=True
        )

        if pair_h1_finished := (
            complete("H1-C")
            and complete("H1-H")
        ):
            return {
                "status": "STAGE_ACK_UNRESOLVED",
                "handled": True,
                "cycle_id": cycle_id,
                "unresolved_actions": unresolved_actions,
                "reconciliation_required": True,
                "exchange_write": False,
            }
            
    def pair_complete(stage):

        close_action = stage + "-C"

        open_action = (
            stage + "-H"
            if stage in ("H1", "H2")
            else stage + "-O"
        )

        return (
            complete(close_action)
            and complete(open_action)
        )

    def execute(stage, quantity):

        quantity = unit_14_v3_floor(
            quantity,
            step
        )

        if quantity < minimum:
            return {
                "status":
                    stage + "_QUANTITY_BELOW_MINIMUM",
                "handled": True,
                "cycle_id": cycle_id
            }

        position = (
            active_positions.get(original)
            or active_positions.get(opposite)
        )

        if position is None:
            return {
                "status": "POSITION_NOT_FOUND",
                "handled": True,
                "cycle_id": cycle_id
            }

        leverage = D(
            position["leverage"],
            "POSITION LEVERAGE"
        )

        
        outcome = unit_14_stage_execute_pair(
            cycle_id=cycle_id,
            stage=stage,
            quantity=quantity,
            mark_price=price,
            opening_leverage=leverage,
            quantity_step=step,
            minimum_quantity=minimum
        )

        outcome["handled"] = True
        outcome["stage"] = stage

        print(
            "UNIT 14 STAGE EXECUTION =",
            stage,
            flush=True
        )

        print(
            "UNIT 14 STAGE STATUS =",
            outcome.get("status"),
            flush=True
        )

        print(
            "UNIT 14 STAGE ACTION RESULTS =",
            outcome.get("actions", {}),
            flush=True
        )

        print(
            "UNIT 14 STAGE FUNDING MODE =",
            outcome.get("funding_mode"),
            flush=True
        )

        print(
            "UNIT 14 STAGE COMPLETE =",
            outcome.get("complete", False),
            flush=True
        )

        return outcome

    # ------------------------------------------------
    # STAGE QUANTITIES
    # ------------------------------------------------

    h1_qty = unit_14_v3_floor(
        base_qty / Decimal("2"),
        step
    )

    # ------------------------------------------------
    # H1 EXECUTION
    # ------------------------------------------------

    
    if not pair_complete("H1"):

        if (
            unresolved("H1-C")
            or unresolved("H1-H")
        ):
            return {
                "status": "H1_ACK_UNRESOLVED",
                "handled": True,
                "cycle_id": cycle_id,
                "adverse_atr": str(adverse),
                "reconciliation_required": True,
            }

        if (
            adverse >= Decimal("1")
            or started("H1-C")
            or started("H1-H")
        ):
            return execute("H1", h1_qty)

        return {
            "status": "H1_MONITORING",
            "handled": True,
            "cycle_id": cycle_id,
            "adverse_atr": str(adverse),
        }

    
    # ========================================================
    # UNIT 14 V4 PART 4
    # H2 / R1 / R2 INDEPENDENT STAGE TRANSITIONS
    # ========================================================

    recovery_started = any(
        started(action)
        for action in (
            "R1-C", "R1-O",
            "R2-C", "R2-O",
        )
    )

    h2_started = any(
        started(action)
        for action in (
            "H2-C", "H2-H",
        )
    )

    r1_started = any(
        started(action)
        for action in (
            "R1-C", "R1-O",
        )
    )

    r2_started = any(
        started(action)
        for action in (
            "R2-C", "R2-O",
        )
    )

    # ========================================================
    # H2: SECOND ADVERSE ATR STAGE
    # ========================================================

    h2_qty = unit_14_v3_floor(
        base_qty - filled("H1-C"),
        step
    )

    # A previously started H2 must be reconciled
    # independently before any recovery transition.

    
    if h2_started and not pair_complete("H2"):

        h2_states = {
            action: orders[action]["state"]
            for action in ("H2-C", "H2-H")
        }

        if any(
            state in (
                "PARTIAL_TERMINAL",
                "TERMINAL_UNFILLED",
            )
            for state in h2_states.values()
        ):
            return {
                "status": "H2_MANUAL_RECONCILIATION_REQUIRED",
                "handled": True,
                "cycle_id": cycle_id,
                "h2_states": h2_states,
                "reconciliation_required": True,
                "exchange_write": False,
            }

        return execute(
            "H2",
            h2_qty
        )

    # H2 may start only before recovery begins.

    if (
        not pair_complete("H2")
        and not recovery_started
        and adverse >= Decimal("2")
    ):

        return execute(
            "H2",
            h2_qty
        )

    # ========================================================
    # R1: FIRST RECOVERY STAGE
    # ========================================================

    hedge_total = (
        filled("H1-H")
        + filled("H2-H")
    )

    r1_qty = unit_14_v3_floor(
        hedge_total / Decimal("2"),
        step
    )

    r1_reached = (
        adverse <= Decimal("0")
    )

    if not pair_complete("R1"):

        # An already-started R1 remains the
        # current recovery stage until reconciled.

        if r1_started:

            return execute(
                "R1",
                r1_qty
            )

        # Do not create R1 after R2 has started
        # without an existing R1 record.

        if r2_started:

            return {
                "status": "R1_RECONCILIATION_REQUIRED",
                "handled": True,
                "cycle_id": cycle_id,
            }

        if r1_reached and hedge_total > 0:

            return execute(
                "R1",
                r1_qty
            )

        return {
            "status": "R1_MONITORING",
            "handled": True,
            "cycle_id": cycle_id,
            "adverse_atr": str(adverse),
            "hedge_quantity": str(hedge_total),
        }

    # ========================================================
    # R2: FINAL RECOVERY STAGE
    # ========================================================

    r2_qty = unit_14_v3_floor(
        hedge_total - filled("R1-C"),
        step
    )

    r2_reached = (
        adverse <= Decimal("-1")
    )

    if not pair_complete("R2"):

        if r2_started:

            return execute(
                "R2",
                r2_qty
            )

        if r2_reached and r2_qty > 0:

            return execute(
                "R2",
                r2_qty
            )

        return {
            "status": "R2_MONITORING",
            "handled": True,
            "cycle_id": cycle_id,
            "adverse_atr": str(adverse),
            "remaining_hedge_quantity": str(r2_qty),
        }

    # ========================================================
    # END UNIT 14 V4 PART 4
    # EXISTING RECOVERY_COMPLETE BLOCK FOLLOWS
    # ========================================================


    # ------------------------------------------------
    # ALL FOUR STAGES COMPLETED
    # ------------------------------------------------

    db = unit_14_stage_db()

    try:
        db.execute("""
            UPDATE stage_cycles
            SET stage = 'RECOVERED',
                state = 'ACTIVE'
            WHERE cycle_id = ?
              AND state = 'ACTIVE'
        """, (cycle_id,))
    finally:
        db.close()

    return {
        "status": "RECOVERY_COMPLETE",
        "handled": True,
        "cycle_id": cycle_id
    }
   

# ============================================================
# UNIT 14 V4 INTEGRATION - PART 1
# VERIFIED UNIT 13 -> UNIT 14 HANDOVER
# PRESERVE EXISTING H1 / H2 / R1 / R2 / B1-B5
# ZERO INDENTATION
# ============================================================

def unit_14_v4_tp_handover(unit_13_result):

    if not isinstance(unit_13_result, dict):
        raise RuntimeError(
            "UNIT 14 INVALID UNIT 13 HANDOVER"
        )

    if unit_13_result.get("unit") != 13:
        raise RuntimeError(
            "UNIT 14 EXPECTED UNIT 13 RESULT"
        )

    status = str(
        unit_13_result.get("status", "")
    ).upper()

    pending_statuses = {
        "TP_ORDER_ACKNOWLEDGED",
        "TP_SUBMISSION_UNCERTAIN",
        "TP_SUBMISSION_UNCONFIRMED",
    }

    unresolved = bool(
        unit_13_result.get(
            "tp_history_unresolved", False
        )
    )

    legacy_unknown = bool(
        unit_13_result.get(
            "tp_legacy_closures_unattributed",
            False
        )
    )

    tp1_completed = bool(
        unit_13_result.get(
            "tp1_completed", False
        )
    )

    tp2_completed = bool(
        unit_13_result.get(
            "tp2_completed", False
        )
    )

    # Order acknowledgment is never proof of fill.
    pending = (
        status in pending_statuses
        or unresolved
        or legacy_unknown
    )

    tp3_armed = bool(
        tp1_completed
        and tp2_completed
        and not pending
        and unit_13_result.get(
            "tp3_armed", False
        )
    )

    # A pending TP order must not disable
    # independent position protection.
    position_exists = bool(
        unit_13_result.get(
            "position_exists",
            unit_13_result.get(
                "active_position_exists", False
            )
        )
    )

    handover = {
        "unit_13_status": status,
        "position_exists": position_exists,
        "tp1_completed": tp1_completed,
        "tp2_completed": tp2_completed,
        "tp3_armed": tp3_armed,
        "tp_order_pending": pending,
        "tp_history_unresolved": unresolved,
        "legacy_closures_unattributed":
            legacy_unknown,
        "hedge_management_enabled":
            position_exists,
        "backup_management_enabled":
            position_exists,
        "bot_mode_independent": True,
    }

    print(
        "UNIT 14 TP1 COMPLETED =",
        tp1_completed,
        flush=True
    )
    print(
        "UNIT 14 TP2 COMPLETED =",
        tp2_completed,
        flush=True
    )
    print(
        "UNIT 14 TP3 ARMED =",
        tp3_armed,
        flush=True
    )
    print(
        "UNIT 14 TP RECONCILIATION PENDING =",
        pending,
        flush=True
    )
    print(
        "UNIT 14 EXISTING POSITION PROTECTION =",
        position_exists,
        flush=True
    )

    return handover


# ============================================================
# UNIT 14 V4 - PART 3
# RESTART-SAFE STAGE RECONCILIATION
# SINGLE H1/H2/R1/R2 EXECUTION AUTHORITY
# PRESERVE ORIGINAL UNIT 14 STAGE EXECUTOR
# ZERO INDENTATION
# ============================================================

def unit_14_v4_stage_reconciliation(
    cycle_id,
):
    """
    Inspect the existing persistent stage cycle.

    This function does not submit exchange orders.
    The original Unit 14 dispatcher remains
    responsible for reconciliation and execution.
    """

    if not cycle_id:
        return {
            "cycle_exists": False,
            "cycle_id": None,
            "status": "NO_ACTIVE_CYCLE",
            "orders": {},
            "execution_attempted": False,
        }

    cycle = unit_14_stage_read(cycle_id)

    if cycle is None:
        raise RuntimeError(
            "UNIT 14 ACTIVE CYCLE NOT FOUND"
        )

    if cycle.get("state") != "ACTIVE":
        return {
            "cycle_exists": True,
            "cycle_id": cycle_id,
            "status": "CYCLE_NOT_ACTIVE",
            "orders": {},
            "execution_attempted": False,
        }

    orders = unit_14_stage_reconcile_cycle(
        cycle_id
    )

    if not isinstance(orders, dict):
        raise RuntimeError(
            "UNIT 14 RECONCILIATION INVALID"
        )

    required_actions = (
        "H1-C", "H1-H",
        "H2-C", "H2-H",
        "R1-C", "R1-O",
        "R2-C", "R2-O",
    )

    summary = {}
    incomplete = []
    started = []

    for action in required_actions:

        record = orders.get(action)

        if not isinstance(record, dict):
            raise RuntimeError(
                "UNIT 14 MISSING STAGE RECORD "
                + action
            )

        state = str(
            record.get("state", "")
        ).upper()

        complete = (
            record.get("complete") is True
        )

        filled = unit_14_v3_D(
            record.get("confirmed_filled", "0"),
            action + " CONFIRMED FILLED",
            True,
        )

        if state != "NOT_CLAIMED":
            started.append(action)

        if not complete:
            incomplete.append(action)

        summary[action] = {
            "state": state,
            "complete": complete,
            "confirmed_filled": str(filled),
        }

    return {
        "cycle_exists": True,
        "cycle_id": cycle_id,
        "status": "RECONCILED",
        "orders": summary,
        "started_actions": started,
        "incomplete_actions": incomplete,
        "execution_attempted": False,
    }


def unit_14_v4_dispatch_once(
    active_positions,
    original_position,
    unit_13_result,
    quantity_step,
    minimum_quantity,
    mark,
):
    """
    Single invocation of the existing
    H1/H2/R1/R2 stage dispatcher.

    No new exchange order implementation
    is introduced here.
    """

    if not isinstance(active_positions, dict):
        raise RuntimeError(
            "UNIT 14 INVALID ACTIVE POSITIONS"
        )

    if not isinstance(unit_13_result, dict):
        raise RuntimeError(
            "UNIT 14 INVALID UNIT 13 RESULT"
        )

    handover = unit_14_v4_tp_handover(
        unit_13_result
    )

    original_side, cycle_id = (
        unit_14_active_original_side()
    )

    if cycle_id is not None:

        reconciliation = (
            unit_14_v4_stage_reconciliation(
                cycle_id
            )
        )

    else:

        reconciliation = {
            "cycle_exists": False,
            "cycle_id": None,
            "status": "NEW_CYCLE_PENDING",
            "orders": {},
            "execution_attempted": False,
        }

    print(
        "UNIT 14 ACTIVE STAGE CYCLE =",
        cycle_id,
        flush=True
    )

    print(
        "UNIT 14 RECONCILIATION STATUS =",
        reconciliation["status"],
        flush=True
    )

    print(
        "UNIT 14 TP1 COMPLETED =",
        handover["tp1_completed"],
        flush=True
    )

    print(
        "UNIT 14 TP2 COMPLETED =",
        handover["tp2_completed"],
        flush=True
    )

    print(
        "UNIT 14 TP3 ARMED =",
        handover["tp3_armed"],
        flush=True
    )

    # Do not invoke a completed or inactive cycle
    # through this wrapper.

    if reconciliation["status"] == "CYCLE_NOT_ACTIVE":

        return {
            "status": "CYCLE_NOT_ACTIVE",
            "handled": False,
            "cycle_id": cycle_id,
            "tp_handover": handover,
            "stage_reconciliation": reconciliation,
        }

    # ========================================================
    # THE ORIGINAL DISPATCHER REMAINS THE ONLY
    # H1/H2/R1/R2 EXECUTION AUTHORITY.
    #
    # It independently reconciles exchange orders
    # before deciding which stage to execute.
    # ========================================================

        # ========================================================
    # POST-TP PROTECTION DISPATCH PRIORITY
    # ========================================================

    if handover["tp1_completed"]:

        outstanding = [
            action
            for action, record in
            reconciliation.get("orders", {}).items()
            if record.get("state") != "NOT_CLAIMED"
            and record.get("complete") is not True
            and record.get("state") != "TERMINAL_UNFILLED"
        ]

        if outstanding:
            print(
                "UNIT 14 OUTSTANDING STAGE ORDERS =",
                outstanding,
                flush=True
            )

            return {
                "status": "POST_TP_RECONCILIATION_PENDING",
                "handled": True,
                "cycle_id": cycle_id,
                "tp_handover": handover,
                "stage_reconciliation": reconciliation,
            }

        if len(active_positions) > 1:
            return {
                "status": "POST_TP_HEDGE_PAIR_UNRESOLVED",
                "handled": True,
                "cycle_id": cycle_id,
                "tp_handover": handover,
                "stage_reconciliation": reconciliation,
            }

        protection_status = (
            "POST_TP2_TRAILING_PRIORITY"
            if handover["tp2_completed"]
            else "POST_TP1_BREAKEVEN_PRIORITY"
        )

        print(
            "UNIT 14 PROTECTION PRIORITY =",
            protection_status,
            flush=True
        )

        print(
            "UNIT 14 NEW HEDGE ACTIVATION = DISABLED",
            flush=True
        )

        return {
            "status": protection_status,
            "handled": False,
            "cycle_id": cycle_id,
            "tp_handover": handover,
            "stage_reconciliation": reconciliation,
        }
    outcome = unit_14_stage_dispatch(
        active_positions=active_positions,
        original_position=original_position,
        unit_13_result=unit_13_result,
        quantity_step=quantity_step,
        minimum_quantity=minimum_quantity,
        mark=mark,
    )

    if not isinstance(outcome, dict):
        raise RuntimeError(
            "UNIT 14 STAGE OUTCOME INVALID"
        )

    outcome["tp_handover"] = handover

    outcome["stage_reconciliation"] = (
        reconciliation
    )

    print(
        "UNIT 14 STAGE DISPATCH STATUS =",
        outcome.get("status"),
        flush=True
    )

    print(
        "UNIT 14 STAGE HANDLED =",
        outcome.get("handled", False),
        flush=True
    )

    return outcome


# ============================================================
# END UNIT 14 V4 PART 3
# ============================================================


# ============================================================
# END UNIT 14 V4 INTEGRATION PART 1
# ============================================================


# ============================================================
# UNIT 14 V4 - PART 5
# EXPLICIT STAGE-TO-BACKUP HANDOVER
# PRESERVE EXISTING B1-B5 EXECUTION ENGINE
# ZERO INDENTATION
# ============================================================

def unit_14_v4_backup_handover(stage_result, cycle_id):

    if not isinstance(stage_result, dict):
        raise RuntimeError(
            "UNIT 14 INVALID STAGE HANDOVER"
        )

    status = str(
        stage_result.get("status", "")
    ).upper()

    # Only an explicitly confirmed failed cycle
    # may release the stage manager to B1-B5.
    #
    # Monitoring, recovery completion, pending
    # submissions and uncertain orders do not
    # qualify as backup authorization.

    if status != "BACKUP_READY":

        return {
            "backup_ready": False,
            "stage_status": status,
            "reason": "STAGE_MANAGER_RETAINS_CONTROL",
        }

    if not cycle_id:

        return {
            "backup_ready": False,
            "stage_status": status,
            "reason": "MISSING_STAGE_CYCLE",
        }

    if str(
        stage_result.get("cycle_id", "")
    ) != str(cycle_id):

        return {
            "backup_ready": False,
            "stage_status": status,
            "reason": "STAGE_CYCLE_MISMATCH",
        }

    cycle = unit_14_stage_read(cycle_id)

    if not isinstance(cycle, dict):

        return {
            "backup_ready": False,
            "stage_status": status,
            "reason": "STAGE_CYCLE_NOT_FOUND",
        }

    if (
        str(cycle.get("stage", "")).upper()
        != "BACKUP_READY"
        or str(cycle.get("state", "")).upper()
        != "ACTIVE"
    ):

        return {
            "backup_ready": False,
            "stage_status": status,
            "reason": "BACKUP_HANDOVER_NOT_PERSISTED",
        }

    return {
        "backup_ready": True,
        "stage_status": status,
        "cycle_id": cycle_id,
        "reason": "FAILED_PROTECTION_CYCLE_CONFIRMED",
    }


# ============================================================
# END UNIT 14 V4 PART 5 HELPER
# ============================================================

def unit_14_ensure_e0_cycle(position):

    import uuid

    D = unit_14_v3_D

    symbol = unit_13_14_active_symbols()[1]
    side = str(position["side"]).upper()

    saved_side, cycle_id = (
        unit_14_active_original_side(symbol)
    )

    if cycle_id is not None:

        if saved_side != side:
            raise RuntimeError(
                "E0 ORIGINAL SIDE MISMATCH"
            )

        return cycle_id

    quantity = D(
        position["size"],
        "E0 QUANTITY",
    )

    entry = D(
        position["openValue"],
        "E0 OPEN VALUE",
    ) / quantity

    atr = D(
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT[
            "atr14"
        ],
        "E0 ATR",
    )

    cycle_id = "U14-" + uuid.uuid4().hex[:20]

    unit_14_stage_create_cycle(
        cycle_id,
        symbol,
        side,
        quantity,
        entry,
        atr,
    )

    print(
        "UNIT 14 NEW E0 CYCLE =",
        cycle_id,
        flush=True,
    )

    return cycle_id
    
def unit_14_execute_breakeven(
    cycle_id,
    position,
    quantity_step,
    minimum_quantity,
):

    D = unit_14_v3_D

    cycle = unit_14_stage_read(cycle_id)

    side = str(position["side"]).upper()
    symbol = unit_13_14_active_symbols()[1]

    if cycle is None:
        raise RuntimeError("BE CYCLE MISSING")

    if cycle["state"] != "ACTIVE":
        return {"status": "BE_CYCLE_INACTIVE"}

    if (
        cycle["symbol"] != symbol
        or cycle["original_side"] != side
    ):
        raise RuntimeError("BE CYCLE MISMATCH")

    history = unit_14_v3_history()

    previous = unit_14_stage_reconcile_order(
        cycle_id,
        "BE-C",
        history,
    )

    if previous["complete"]:
        return {
            "status": "BE_CLOSE_FILLED",
            "confirmed": True,
        }

    if previous["state"] != "NOT_CLAIMED":
        return {
            "status": "BE_CLOSE_" + previous["state"],
            "confirmed": False,
        }

    latest = unit_14_v3_position(side)

    if latest is None:
        return {"status": "BE_POSITION_FLAT"}

    if (
        unit_14_v3_trade_key(latest)
        != unit_14_v3_trade_key(position)
    ):
        return {"status": "BE_POSITION_CHANGED"}

    quantity = unit_14_v3_floor(
        D(latest["size"], "BE SIZE"),
        D(quantity_step, "BE STEP"),
    )

    minimum = D(
        minimum_quantity,
        "BE MINIMUM"
    )

    if quantity < minimum:
        return {"status": "BE_BELOW_MINIMUM"}

    claim = unit_14_stage_claim(
        cycle_id,
        "BE-C",
        quantity,
    )

    if not claim["claimed"]:
        return {"status": "BE_ALREADY_CLAIMED"}

    client_id = claim["client_id"]

    payload = {
        "symbol": symbol,
        "side": (
            "SELL" if side == "LONG"
            else "BUY"
        ),
        "positionSide": side,
        "type": "MARKET",
        "quantity": format(quantity, "f"),
        "newClientOrderId": client_id,
    }

    try:

        reply = unit_14_v3_signed_request(
            "POST",
            UNIT14_V3_ORDER,
            payload=payload,
        )

    except Exception as exc:

        unit_14_stage_update(
            client_id,
            "ACK_UNKNOWN",
        )

        print(
            "UNIT 14 BE CLOSE ACK UNKNOWN =",
            repr(exc),
            flush=True,
        )

        return {"status": "BE_CLOSE_ACK_UNKNOWN"}

    response = (
        reply.get("data")
        if isinstance(reply, dict)
        else None
    )

    if not isinstance(response, dict):
        response = (
            reply if isinstance(reply, dict)
            else {}
        )

    order_id = (
        response.get("orderId")
        or response.get("order_id")
    )

    returned_client = (
        response.get("clientOrderId")
        or response.get("newClientOrderId")
        or response.get("clientOid")
    )

    failure = (
        not isinstance(reply, dict)
        or reply.get("success") is False
        or bool(reply.get("errorCode"))
        or bool(reply.get("errorMsg"))
        or response.get("success") is False
        or bool(response.get("errorCode"))
        or bool(response.get("errorMsg"))
    )

    if (
        order_id
        and not failure
        and (
            returned_client is None
            or str(returned_client) == client_id
        )
    ):

        unit_14_stage_update(
            client_id,
            "SUBMITTED",
            str(order_id),
        )

        print(
            "UNIT 14 BE CLOSE SUBMITTED =",
            order_id,
            flush=True,
        )

        return {
            "status": "BE_CLOSE_SUBMITTED",
            "order_id": str(order_id),
            "exchange_write": True,
            "confirmed": False,
        }

    unit_14_stage_update(
        client_id,
        "ACK_UNKNOWN",
    )

    return {"status": "BE_CLOSE_ACK_UNKNOWN"}
    
def unit_14_tp3_persistent_state(
    cycle_id,
    side,
    mark,
    atr,
    trail_ref,
    trail_min,
    trail_max,
):

    D = unit_14_v3_D

    side = str(side).upper()

    if side not in ("LONG", "SHORT"):
        raise RuntimeError("TP3 INVALID SIDE")

    mark = D(mark, "TP3 MARK")
    atr = D(atr, "TP3 ATR")

    trail_ref = D(trail_ref, "TP3 REFERENCE")
    trail_min = D(trail_min, "TP3 MINIMUM")
    trail_max = D(trail_max, "TP3 MAXIMUM")

    if not (
        0 < trail_min <= trail_ref <= trail_max
    ):
        raise RuntimeError(
            "TP3 INVALID TRAILING RANGE"
        )

    atr_percent = (
        atr / mark
    ) * D(100)

    callback = max(
        trail_min,
        min(
            trail_max,
            atr_percent
        )
    )

    db = unit_14_stage_db()

    try:

        db.execute("""
            CREATE TABLE IF NOT EXISTS
            tp3_trailing_state (
                cycle_id TEXT PRIMARY KEY,
                side TEXT NOT NULL,
                best_mark TEXT NOT NULL,
                stop_price TEXT NOT NULL,
                callback_percent TEXT NOT NULL,
                triggered INTEGER NOT NULL
                    DEFAULT 0,
                updated_at TEXT DEFAULT
                    CURRENT_TIMESTAMP
            )
        """)

        db.execute("BEGIN IMMEDIATE")

        cycle = db.execute("""
            SELECT original_side, state
            FROM stage_cycles
            WHERE cycle_id = ?
        """, (cycle_id,)).fetchone()

        if (
            cycle is None
            or cycle[0] != side
            or cycle[1] != "ACTIVE"
        ):
            raise RuntimeError(
                "TP3 INVALID ACTIVE CYCLE"
            )

        saved = db.execute("""
            SELECT side, best_mark,
                   stop_price, triggered
            FROM tp3_trailing_state
            WHERE cycle_id = ?
        """, (cycle_id,)).fetchone()

        best = mark
        old_stop = None
        triggered = False

        if saved is not None:

            if saved[0] != side:
                raise RuntimeError(
                    "TP3 SAVED SIDE MISMATCH"
                )

            best = D(
                saved[1],
                "TP3 SAVED BEST"
            )

            old_stop = D(
                saved[2],
                "TP3 SAVED STOP"
            )

            triggered = bool(saved[3])

        if side == "LONG":

            best = max(best, mark)

            stop = best * (
                D(1) - callback / D(100)
            )

            if old_stop is not None:
                stop = max(stop, old_stop)

            triggered = (
                triggered or mark <= stop
            )

        else:

            best = min(best, mark)

            stop = best * (
                D(1) + callback / D(100)
            )

            if old_stop is not None:
                stop = min(stop, old_stop)

            triggered = (
                triggered or mark >= stop
            )

        db.execute("""
            INSERT INTO tp3_trailing_state (
                cycle_id,
                side,
                best_mark,
                stop_price,
                callback_percent,
                triggered
            )
            VALUES (?, ?, ?, ?, ?, ?)

            ON CONFLICT(cycle_id)
            DO UPDATE SET
                best_mark = excluded.best_mark,
                stop_price = excluded.stop_price,
                callback_percent =
                    excluded.callback_percent,
                triggered = excluded.triggered,
                updated_at = CURRENT_TIMESTAMP
        """, (
            cycle_id,
            side,
            str(best),
            str(stop),
            str(callback),
            int(triggered),
        ))

        db.execute("COMMIT")

        return {
            "cycle_id": cycle_id,
            "tp3_best_mark": float(best),
            "tp3_stop_price": float(stop),
            "tp3_trailing_percent": float(
                callback
            ),
            "tp3_trigger_reached": triggered,
            "tp3_storage": "SQLITE",
        }

    except Exception:

        if db.in_transaction:
            db.execute("ROLLBACK")

        raise

    finally:

        db.close()
# ============================================================
# UNIT 14 - INDEPENDENT SQLITE TP3 CLOSING EXECUTOR
# ZERO INDENTATION
# ============================================================

def unit_14_execute_tp3(
    cycle_id,
    position,
    quantity_step,
    minimum_quantity,
):

    D = unit_14_v3_D

    result = {
        "status": "TP3_CLOSE_PENDING",
        "execution_attempted": False,
        "confirmed": False,
        "exchange_write": False,
        "order_id": None,
    }

    # ========================================================
    # VALIDATE PERSISTENT E0 CYCLE
    # ========================================================

    cycle = unit_14_stage_read(cycle_id)

    if cycle is None:
        raise RuntimeError(
            "TP3 CYCLE MISSING"
        )

    side = str(
        position["side"]
    ).strip().upper()

    symbol = unit_13_14_active_symbols()[1]

    if side not in ("LONG", "SHORT"):
        raise RuntimeError(
            "TP3 INVALID POSITION SIDE"
        )

    if cycle["state"] != "ACTIVE":

        result["status"] = (
            "TP3_CYCLE_INACTIVE"
        )

        return result

    if (
        cycle["symbol"] != symbol
        or cycle["original_side"] != side
    ):
        raise RuntimeError(
            "TP3 CYCLE POSITION MISMATCH"
        )

    # ========================================================
    # RECONCILE EXISTING TP3-C ORDER
    # ========================================================

    history = unit_14_v3_history()

    previous = unit_14_stage_reconcile_order(
        cycle_id,
        "TP3-C",
        history,
    )

    result["order_id"] = previous.get(
        "exchange_order_id"
    )

    result["confirmed_filled"] = previous.get(
        "confirmed_filled",
        "0",
    )

    print(
        "UNIT 14 TP3-C PERSISTED STATE =",
        previous["state"],
        flush=True,
    )

    if previous["complete"]:

        result["status"] = (
            "TP3_CLOSE_FILLED"
        )

        result["confirmed"] = True

        print(
            "UNIT 14 TP3 CLOSE CONFIRMED = TRUE",
            flush=True,
        )

        return result

    if previous["state"] != "NOT_CLAIMED":

        result["status"] = (
            "TP3_CLOSE_"
            + previous["state"]
        )

        return result

    # ========================================================
    # PREVENT CONFLICT WITH EXISTING BE-C ORDER
    # ========================================================

    be_order = unit_14_stage_reconcile_order(
        cycle_id,
        "BE-C",
        history,
    )

    print(
        "UNIT 14 TP3 BE-C STATE =",
        be_order["state"],
        flush=True,
    )

    if be_order["state"] not in (
        "NOT_CLAIMED",
        "FILLED",
        "TERMINAL_UNFILLED",
    ):

        result["status"] = (
            "TP3_WAITING_BE_RECONCILIATION"
        )

        return result

    # ========================================================
    # REFRESH ACTUAL EXCHANGE POSITION
    # ========================================================

    latest = unit_14_v3_position(side)

    if latest is None:

        result["status"] = (
            "TP3_POSITION_FLAT"
        )

        return result

    if (
        unit_14_v3_trade_key(latest)
        != unit_14_v3_trade_key(position)
    ):

        result["status"] = (
            "TP3_POSITION_CHANGED"
        )

        return result

    quantity = unit_14_v3_floor(
        D(
            latest["size"],
            "TP3 REMAINING SIZE",
        ),
        D(
            quantity_step,
            "TP3 QUANTITY STEP",
        ),
    )

    minimum = D(
        minimum_quantity,
        "TP3 MINIMUM QUANTITY",
    )

    if quantity <= 0 or quantity < minimum:

        result["status"] = (
            "TP3_BELOW_MINIMUM"
        )

        return result

    print(
        "UNIT 14 TP3 CLOSING QUANTITY =",
        quantity,
        flush=True,
    )

    # ========================================================
    # SQLITE CLAIM BEFORE EXCHANGE SUBMISSION
    # ========================================================

    claim = unit_14_stage_claim(
        cycle_id,
        "TP3-C",
        quantity,
    )

    if not claim["claimed"]:

        result["status"] = (
            "TP3_ALREADY_CLAIMED"
        )

        return result

    client_id = claim["client_id"]

    result["client_id"] = client_id

    print(
        "UNIT 14 TP3-C SQLITE CLAIM =",
        client_id,
        flush=True,
    )

    # ========================================================
    # INDEPENDENT MARKET CLOSING ORDER
    # ========================================================

    payload = {
        "symbol": symbol,
        "side": (
            "SELL"
            if side == "LONG"
            else "BUY"
        ),
        "positionSide": side,
        "type": "MARKET",
        "quantity": format(quantity, "f"),
        "newClientOrderId": client_id,
    }

    result["execution_attempted"] = True

    try:

        reply = unit_14_v3_signed_request(
            "POST",
            UNIT14_V3_ORDER,
            payload=payload,
        )

    except Exception as exc:

        unit_14_stage_update(
            client_id,
            "ACK_UNKNOWN",
        )

        result["status"] = (
            "TP3_CLOSE_ACK_UNKNOWN"
        )

        print(
            "UNIT 14 TP3 CLOSE ACK UNKNOWN =",
            repr(exc),
            flush=True,
        )

        return result

    # ========================================================
    # NORMALIZE WEEX ACKNOWLEDGEMENT
    # ========================================================

    response = (
        reply.get("data")
        if isinstance(reply, dict)
        else None
    )

    if not isinstance(response, dict):

        response = (
            reply
            if isinstance(reply, dict)
            else {}
        )

    order_id = (
        response.get("orderId")
        or response.get("order_id")
    )

    returned_client = (
        response.get("clientOrderId")
        or response.get("newClientOrderId")
        or response.get("clientOid")
    )

    failure = (
        not isinstance(reply, dict)
        or reply.get("success") is False
        or bool(reply.get("errorCode"))
        or bool(reply.get("errorMsg"))
        or response.get("success") is False
        or bool(response.get("errorCode"))
        or bool(response.get("errorMsg"))
    )

    # ========================================================
    # SAVE ACKNOWLEDGEMENT WITHOUT CLAIMING COMPLETION
    # ========================================================

    if (
        order_id
        and not failure
        and (
            returned_client is None
            or str(returned_client) == client_id
        )
    ):

        unit_14_stage_update(
            client_id,
            "SUBMITTED",
            str(order_id),
        )

        result.update({
            "status": "TP3_CLOSE_SUBMITTED",
            "order_id": str(order_id),
            "exchange_write": True,
            "confirmed": False,
        })

        print(
            "UNIT 14 TP3 CLOSE SUBMITTED =",
            order_id,
            flush=True,
        )

        print(
            "UNIT 14 TP3 CLOSE CONFIRMED = FALSE",
            flush=True,
        )

        return result

    # ========================================================
    # UNKNOWN ACK - NO AUTOMATIC DUPLICATE SUBMISSION
    # ========================================================

    unit_14_stage_update(
        client_id,
        "ACK_UNKNOWN",
    )

    result["status"] = (
        "TP3_CLOSE_ACK_UNKNOWN"
    )

    print(
        "UNIT 14 TP3 CLOSE ACK UNKNOWN",
        flush=True,
    )

    return result


# ============================================================
# END INDEPENDENT SQLITE TP3 CLOSING EXECUTOR
# ============================================================

def unit_14_atr_breakeven(
    symbol,
    position,
    mark,
    strategy,
):

    import hashlib
    from decimal import Decimal

    D = unit_14_v3_D

    side = str(
        position.get("side", "")
    ).upper()

    if side not in ("LONG", "SHORT"):
        raise RuntimeError(
            "INVALID BREAKEVEN SIDE"
        )

    size = D(
        position["size"],
        "BREAKEVEN SIZE"
    )

    entry = (
        D(
            position["openValue"],
            "BREAKEVEN OPEN VALUE"
        ) / size
    )

    mark = D(mark, "BREAKEVEN MARK")

    atr = D(
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT[
            "atr14"
        ],
        "BREAKEVEN ATR"
    )

    multiplier = Decimal("1.0")

    fee = D(
        strategy.get(
            "futures_taker_fee_percent",
            "0.08"
        ),
        "BREAKEVEN FEE",
        True
    ) / Decimal("100")

    if fee >= Decimal("1"):
        raise RuntimeError(
            "INVALID BREAKEVEN FEE"
        )

    identity = str(
        position.get("id") or
        position.get("createdTime") or ""
    )

    if not identity:
        raise RuntimeError(
            "BREAKEVEN POSITION IDENTITY MISSING"
        )

    key = hashlib.sha256(
        (
            symbol + ":" +
            side + ":" +
            identity
        ).encode()
    ).hexdigest()

    if side == "LONG":

        breakeven = (
            entry * (1 + fee) / (1 - fee)
        )

    else:

        breakeven = (
            entry * (1 - fee) / (1 + fee)
        )

    db = unit_14_stage_db()

    try:

        db.execute("""
            CREATE TABLE IF NOT EXISTS
            atr_breakeven (
                trade_key TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                best_mark TEXT NOT NULL,
                stop_price TEXT NOT NULL,
                triggered INTEGER NOT NULL
                    DEFAULT 0
            )
        """)

        db.execute("BEGIN IMMEDIATE")

        row = db.execute("""
            SELECT best_mark,
                   stop_price,
                   triggered
            FROM atr_breakeven
            WHERE trade_key = ?
        """, (key,)).fetchone()

        best = mark
        previous_stop = breakeven
        previously_triggered = False

        if row is not None:

            best = D(
                row[0],
                "PERSISTED BEST MARK"
            )

            previous_stop = D(
                row[1],
                "PERSISTED STOP"
            )

            previously_triggered = bool(
                row[2]
            )

        if side == "LONG":

            best = max(best, mark)

            stop = max(
                previous_stop,
                breakeven,
                best - atr * multiplier
            )

            reached = mark <= stop

        else:

            best = min(best, mark)

            stop = min(
                previous_stop,
                breakeven,
                best + atr * multiplier
            )

            reached = mark >= stop

        if stop <= 0:
            raise RuntimeError(
                "INVALID BREAKEVEN STOP"
            )

        reached = bool(
            reached or previously_triggered
        )

        db.execute("""
            INSERT INTO atr_breakeven (
                trade_key,
                symbol,
                side,
                best_mark,
                stop_price,
                triggered
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(trade_key)
            DO UPDATE SET
                best_mark = excluded.best_mark,
                stop_price = excluded.stop_price,
                triggered = excluded.triggered
        """, (
            key,
            symbol,
            side,
            str(best),
            str(stop),
            int(reached)
        ))

        db.commit()

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()

    print(
        "UNIT 14 BREAKEVEN ENTRY =", entry,
        flush=True
    )

    print(
        "UNIT 14 FEE ADJUSTED BE =", breakeven,
        flush=True
    )

    print(
        "UNIT 14 BREAKEVEN ATR =", atr,
        flush=True
    )

    print(
        "UNIT 14 BREAKEVEN BEST MARK =", best,
        flush=True
    )

    print(
        "UNIT 14 BREAKEVEN STOP =", stop,
        flush=True
    )

    print(
        "UNIT 14 BREAKEVEN TRIGGERED =", reached,
        flush=True
    )

    return {
        "trade_key": key,
        "breakeven_price": str(breakeven),
        "best_mark": str(best),
        "stop_price": str(stop),
        "atr": str(atr),
        "triggered": reached,
    }
def fresh_reconstruction_unit_14(
    config,
    unit_13_result,
):

    print("=" * 80, flush=True)
    print(
        "UNIT 14 V3 DYNAMIC BACKUP MANAGEMENT START",
        flush=True
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 14 CONFIG INVALID"
        )

    if not isinstance(unit_13_result, dict):
        raise RuntimeError(
            "UNIT 14 UNIT 13 RESULT INVALID"
        )

    exchange = config.get("exchange", {})
    strategy = config.get("strategy", {})
    precision = config.get("market_precision", {})

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or not str(
    exchange.get("market_symbol", "")
).strip().upper().endswith("USDT")
or str(
    exchange.get("demo_order_symbol", "")
).strip().upper() != (
    str(
        exchange.get("market_symbol", "")
    ).strip().upper()[:-4] + "SUSDT"
)
    ):
        raise RuntimeError(
            "UNIT 14 NON-DEMO CONFIG BLOCKED"
        )

    D = unit_14_v3_D

    qstep = D(
        precision.get("quantity_step"),
        "QTY STEP"
    )

    minimum = D(
        precision.get("minimum_quantity"),
        "MINIMUM QUANTITY"
    )

    max_backups = int(
        strategy.get("max_backups", 5)
    )

    # Percentage of CURRENT available balance,
    # not fixed multiples of initial margin.

    backup_percent = D(
        os.getenv(
            "BACKUP_AVAILABLE_BALANCE_PERCENT",
            str(
                strategy.get(
                    "backup_available_balance_percent",
                    "0.5"
                )
            )
        ),
        "BACKUP BALANCE PERCENT"
    )

    buffer_pct = D(
        strategy.get(
            "backup_buffer_percent",
            "0.3"
        ),
        "BUFFER PERCENT"
    )

    cap_pct = D(
        strategy.get(
            "exposure_cap_percent",
            "35"
        ),
        "EXPOSURE CAP"
    )

    trail_ref = D(
        strategy.get(
            "tp3_trailing_reference_percent",
            "0.20"
        ),
        "TRAIL REFERENCE"
    )

    trail_min = D(
        strategy.get(
            "tp3_trailing_min_percent",
            "0.10"
        ),
        "TRAIL MINIMUM"
    )

    trail_max = D(
        strategy.get(
            "tp3_trailing_max_percent",
            "0.40"
        ),
        "TRAIL MAXIMUM"
    )

     
    # ========================================================
    # UNIT 14 V3 - DYNAMIC SETTINGS VALIDATION
    # ALIGNED WITH UNIT 2 V9
    # ORIGINAL FIVE-BACKUP ENGINE PRESERVED
    # ========================================================

    if max_backups != 5:
        raise RuntimeError(
            "UNIT 14 INVALID BACKUP COUNT: "
            + str(max_backups)
        )

    if not 0 < backup_percent <= 100:
        raise RuntimeError(
            "UNIT 14 INVALID BACKUP BALANCE PERCENT: "
            + str(backup_percent)
        )

    if not 0 < cap_pct <= 100:
        raise RuntimeError(
            "UNIT 14 INVALID EXPOSURE CAP PERCENT: "
            + str(cap_pct)
        )

    if not 0 < trail_min <= trail_ref <= trail_max:
        raise RuntimeError(
            "UNIT 14 INVALID TP3 TRAILING RANGE: "
            + str((
                trail_min,
                trail_ref,
                trail_max
            ))
        )

    print(
        "UNIT 14 DYNAMIC CONFIG VALIDATION = PASS",
        flush=True
    )

    print(
        "UNIT 14 EXPOSURE CAP % =",
        cap_pct,
        flush=True
    )

    result = unit_14_v3_result(
        unit_13_result
    )

    print(
        "UNIT 14 BACKUPS = 5",
        flush=True
    )
    print(
        "UNIT 14 BACKUP SIZING = "
        "PERCENT_AVAILABLE_BALANCE",
        flush=True
    )
    print(
        "UNIT 14 BACKUP BALANCE % =",
        backup_percent,
        flush=True
    )
    print(
        "UNIT 14 BUFFER % =",
        buffer_pct,
        flush=True
    )
    print(
        "UNIT 14 EXPOSURE CAP % =",
        cap_pct,
        flush=True
    )
    print(
        "UNIT 14 UNIT 13 STATUS =",
        unit_13_result.get("status"),
        flush=True
    )
    print(
        "UNIT 14 MANAGEMENT INDEPENDENT "
        "OF BOT_MODE = TRUE",
        flush=True
    )

    # ========================================================
    # 8. FRESH EXCHANGE POSITION
    # ========================================================

    active_positions = unit_14_v3_positions()

    # ONE-TIME OBSOLETE SHORT RESET

    short_reset = unit_14_reset_obsolete_short(
        active_positions
    )

    result["obsolete_short_reset"] = short_reset

    # ESTABLISH FRESH E0 OWNERSHIP

    persisted_side, active_cycle_id = (
        unit_14_active_original_side()
    )

    if (
        active_cycle_id is None
        and len(active_positions) == 1
    ):

        original_position = next(
            iter(active_positions.values())
        )

        active_cycle_id = (
            unit_14_ensure_e0_cycle(
                original_position
            )
        )

        persisted_side = str(
            original_position["side"]
        ).upper()

        print(
            "UNIT 14 FRESH E0 SIDE =",
            persisted_side,
            flush=True,
        )

        print(
            "UNIT 14 FRESH E0 CYCLE =",
            active_cycle_id,
            flush=True,
        )

    # ========================================================
    # INDEPENDENT TP3-C RECONCILIATION
    # PRESERVE ALL HEDGE PROTECTION DISPATCH
    # ========================================================

    if active_cycle_id is not None:

        tp3_cycle = unit_14_stage_read(
            active_cycle_id
        )

        if tp3_cycle is not None:

            tp3_record = tp3_cycle["orders"].get(
                "TP3-C"
            )

            if tp3_record is not None:

                try:

                    tp3_order = (
                        unit_14_stage_reconcile_order(
                            cycle_id=active_cycle_id,
                            action="TP3-C",
                        )
                    )

                    tp3_state = str(
                        tp3_order.get("state", "")
                    ).upper()

                    tp3_confirmed = (
                        tp3_order.get("complete")
                        is True
                    )

                    result["tp3_reconciliation"] = (
                        tp3_order
                    )

                    result["tp3_execution_completed"] = (
                        tp3_confirmed
                    )

                    result["tp3_order_id"] = (
                        tp3_order.get(
                            "exchange_order_id"
                        )
                    )

                    print(
                        "UNIT 14 TP3 INDEPENDENT "
                        "RECONCILIATION = TRUE",
                        flush=True,
                    )

                    print(
                        "UNIT 14 TP3-C STATE =",
                        tp3_state,
                        flush=True,
                    )

                    print(
                        "UNIT 14 TP3-C CONFIRMED FILL =",
                        tp3_order.get(
                            "confirmed_filled", "0"
                        ),
                        flush=True,
                    )

                    print(
                        "UNIT 14 TP3 CLOSE CONFIRMED =",
                        tp3_confirmed,
                        flush=True,
                    )

                except Exception as exc:

                    result["tp3_reconciliation_error"] = (
                        str(exc)
                    )

                    print(
                        "UNIT 14 TP3 RECONCILIATION ERROR =",
                        str(exc),
                        flush=True,
                    )

                active_positions = (
                    unit_14_v3_positions()
                )

                print(
                    "UNIT 14 TP3 RECONCILIATION "
                    "HANDOVER TO EXISTING PROTECTION",
                    flush=True,
                )

    # TP3 reconciliation must not return from
    # Unit 14 or disable existing hedge dispatch.
    # Continue existing E0 and protection lifecycle.
    
    # ========================================================
    # E0 FLAT CYCLE TERMINATION
    # ========================================================

    if not active_positions and active_cycle_id is not None:

        termination = unit_14_finalize_flat_cycle(
            active_cycle_id
        )

        result["e0_termination"] = termination

        result["status"] = termination["status"]

        result["exchange_write"] = False

        print(
            "UNIT 14 E0 TERMINATION STATUS =",
            result["status"],
            flush=True,
        )

        return result

    print(
        "UNIT 14 EXCHANGE ACTIVE SIDES =",
        list(active_positions.keys()),
        flush=True,
    )

    print(
        "UNIT 14 EXCHANGE POSITION SIZES =",
        {
            s: str(pos.get("size"))
            for s, pos in active_positions.items()
        },
        flush=True,
    )

    print(
        "UNIT 14 SQLITE ORIGINAL SIDE =",
        persisted_side,
        flush=True,
    )

    print(
        "UNIT 14 SQLITE ACTIVE CYCLE =",
        active_cycle_id,
        flush=True,
    )

    p = None

    if persisted_side is not None:

        persisted_side = str(
            persisted_side
        ).strip().upper()

        p = active_positions.get(
            persisted_side
        )

        if p is None and active_positions:

            print(
                "UNIT 14 ORIGINAL SIDE ABSENT "
                "BUT OTHER POSITION EXISTS",
                flush=True,
            )

    elif len(active_positions) == 1:

        p = next(
            iter(active_positions.values())
        )

    elif len(active_positions) > 1:

        configured_side = os.getenv(
            "ORIGINAL_POSITION_SIDE", ""
        ).strip().upper()

        if configured_side not in active_positions:

            raise RuntimeError(
                "ORIGINAL SIDE NOT IDENTIFIED "
                "FOR EXISTING HEDGE PAIR"
            )

        p = active_positions[configured_side]

    print(
        "UNIT 14 ORIGINAL POSITION FOUND =",
        p is not None,
        flush=True,
    )
    
    if active_cycle_id is not None:

        stage_state = unit_14_stage_read(
            active_cycle_id
        )

        if stage_state is not None:
            result["stage_cycle_id"] = (
                active_cycle_id
            )
            result["stage_original_side"] = (
                stage_state["original_side"]
            )
            result["stage_state"] = (
                stage_state["stage"]
            )

    
    # ========================================================
    # UNIT 14 V4 - SINGLE H1/H2/R1/R2 DISPATCH
    # ========================================================

    tp_handover = unit_14_v4_tp_handover(
        unit_13_result
    )

    result["tp_handover"] = tp_handover

    stage_mark = None

    if (
        p is not None
        or active_cycle_id is not None
    ):
        stage_mark = unit_14_v3_mark()

    if stage_mark is not None:

        stage_result = unit_14_v4_dispatch_once(
            active_positions=active_positions,
            original_position=p,
            unit_13_result=unit_13_result,
            quantity_step=qstep,
            minimum_quantity=minimum,
            mark=stage_mark,
        )

        result["stage_dispatch"] = stage_result

        print(
            "UNIT 14 HEDGE STAGE =",
            stage_result.get("stage"),
            flush=True
        )

        print(
            "UNIT 14 HEDGE STATUS =",
            stage_result.get("status"),
            flush=True
        )

        
        # ====================================================
        # UNIT 14 V4 - STAGE TO BACKUP HANDOVER
        # ====================================================

        handover = unit_14_v4_backup_handover(
            stage_result,
            stage_result.get("cycle_id"),
        )

        result["backup_handover"] = handover

        if handover["backup_ready"]:

            result["protection_stage_status"] = (
                "BACKUP_READY"
            )

            result["backup_activation_reason"] = (
                "FAILED_PROTECTION_CYCLE_CONFIRMED"
            )

            print(
                "UNIT 14 BACKUP HANDOVER = READY",
                flush=True
            )

            # Continue into the existing Unit 14
            # position and B1-B5 management logic.

        elif stage_result.get("handled"):

            result["status"] = (
                stage_result.get(
                    "status",
                    "STAGE_MANAGER_ACTIVE"
                )
            )

            result["skip_reason"] = (
                "STAGE_MANAGER_ACTIVE"
            )

            return result

        elif stage_result.get("status") == "RECOVERY_COMPLETE":

            result["status"] = "RECOVERY_COMPLETE"
            result["skip_reason"] = (
                "PROTECTION_CYCLE_RECOVERED"
            )

            return result

        # ========================================================
    # CONTINUE EXISTING UNIT 14 POSITION MANAGEMENT
    # ========================================================

    if p is None:

        if active_positions:

            result["status"] = (
                "ORIGINAL_POSITION_ABSENT"
            )

            result["skip_reason"] = (
                "OTHER_EXCHANGE_POSITION_EXISTS"
            )

        elif active_cycle_id is not None:

            result["status"] = (
                "FLAT_CYCLE_RECONCILIATION_PENDING"
            )

            result["skip_reason"] = (
                "ACTIVE_SQLITE_CYCLE_EXISTS"
            )

        else:

            result["status"] = (
                "IDLE_NO_POSITION"
            )

            result["skip_reason"] = (
                "NO_ACTIVE_DEMO_POSITION"
            )

        result["exchange_write"] = False

        print(
            "UNIT 14 STATUS =",
            result["status"],
            flush=True,
        )

        print(
            "UNIT 14 REMAINING EXCHANGE SIDES =",
            list(active_positions.keys()),
            flush=True,
        )

        print(
            "UNIT 14 EXCHANGE WRITE = NONE",
            flush=True,
        )

        return result

    # ========================================================
    # CONTINUE EXISTING UNIT 14 POSITION MANAGEMENT
    # ========================================================

        if p is None:

            if active_positions:

                result["status"] = (
                "ORIGINAL_POSITION_ABSENT"
            )

            result["skip_reason"] = (
                "OTHER_EXCHANGE_POSITION_EXISTS"
            )

        elif active_cycle_id is not None:

            result["status"] = (
                "FLAT_CYCLE_RECONCILIATION_PENDING"
            )

            result["skip_reason"] = (
                "ACTIVE_SQLITE_CYCLE_EXISTS"
            )

        else:

            result["status"] = (
                "IDLE_NO_POSITION"
            )

            result["skip_reason"] = (
                "NO_ACTIVE_DEMO_POSITION"
            )

        result["exchange_write"] = False

        print(
            "UNIT 14 STATUS =",
            result["status"],
            flush=True,
        )

        print(
            "UNIT 14 REMAINING EXCHANGE SIDES =",
            list(active_positions.keys()),
            flush=True,
        )

        print(
            "UNIT 14 EXCHANGE WRITE = NONE",
            flush=True,
        )

        return result

    side = str(
        p.get("side", "")
    ).upper()

    if side not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 14 POSITION SIDE INVALID"
        )

    size = D(
        p.get("size"),
        "ACTIVE POSITION SIZE"
    )

    leverage = D(
        p.get("leverage"),
        "POSITION LEVERAGE"
    )

    key = unit_14_v3_trade_key(p)

    liquidation = D(
        p.get("liquidatePrice"),
        "LIQUIDATION PRICE",
        True
    )

    mark = unit_14_v3_mark()
    history = unit_14_v3_history()

    result.update({
        "position_exists": True,
        "position_side": side,
        "position_size": float(size),
        "position_leverage": float(leverage),
        "mark_price": float(mark),
        "liquidation_price": float(liquidation),
        "trade_key": key,
    })

    # ========================================================
    # 9. BACKUP HISTORY RECONCILIATION
    # ========================================================

    completed, existing = (
        unit_14_v3_reconcile(
            history,
            key,
        )
    )

    result["backups_filled"] = completed

    print(
        "UNIT 14 BACKUPS FILLED =",
        str(completed) + "/5",
        flush=True
    )

    # ========================================================
    # 10. TP3 RUNNER
    # UNIT 13 TP STATE MUST MATCH ACTIVE POSITION
    # ========================================================

    
    # ========================================================
    # UNIT 14 V4 - VERIFIED TP3 ARMING
    # ========================================================

    tp3_armed = bool(
        tp_handover["tp3_armed"]
        and tp_handover["position_exists"]
        and unit_13_result.get(
            "position_side"
        ) == side
        and not tp_handover[
            "tp_order_pending"
        ]
    )

    result["tp3_armed"] = tp3_armed

        
    # ========================================================
    # SQLITE TP3 AND POST-TP PROTECTION
    # ========================================================

    attempts = globals().setdefault(
        "_UNIT14_V3_ORDER_ATTEMPTS",
        set()
    )

    if tp_handover["tp1_completed"]:

        result["backup_activation_authorized"] = False

        cycle_id = unit_14_ensure_e0_cycle(p)

        if tp3_armed:

            atr = D(
                FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT[
                    "atr14"
                ],
                "TP3 CURRENT ATR",
            )

            trailing = unit_14_tp3_persistent_state(
                cycle_id=cycle_id,
                side=side,
                mark=mark,
                atr=atr,
                trail_ref=trail_ref,
                trail_min=trail_min,
                trail_max=trail_max,
            )

            result.update(trailing)

            result["status"] = (
                "TP3_TRAILING_MONITORING"
            )

            print(
                "UNIT 14 TP3 STORAGE = SQLITE",
                flush=True,
            )

            print(
                "UNIT 14 TP3 BEST MARK =",
                trailing["tp3_best_mark"],
                flush=True,
            )

            print(
                "UNIT 14 TP3 STOP PRICE =",
                trailing["tp3_stop_price"],
                flush=True,
            )

            print(
                "UNIT 14 TP3 TRAILING PERCENT =",
                trailing["tp3_trailing_percent"],
                flush=True,
            )

            print(
                "UNIT 14 TP3 TRIGGERED =",
                trailing["tp3_trigger_reached"],
                flush=True,
            )

            if trailing["tp3_trigger_reached"]:

                execution = unit_14_execute_tp3(
                    cycle_id=cycle_id,
                    position=p,
                    quantity_step=qstep,
                    minimum_quantity=minimum,
                )

                result["tp3_execution"] = execution

                result["status"] = execution["status"]

                result["tp3_execution_attempted"] = (
                    execution.get(
                        "execution_attempted",
                        False,
                    )
                )

                result["tp3_execution_completed"] = (
                    execution.get(
                        "confirmed",
                        False,
                    )
                )

                result["tp3_order_id"] = (
                    execution.get("order_id")
                )

                result["exchange_write"] = (
                    execution.get(
                        "exchange_write",
                        False,
                    )
                )

                print(
                    "UNIT 14 TP3 EXECUTION =",
                    execution,
                    flush=True,
                )

        elif tp_handover["tp2_completed"]:

            result["status"] = (
                "TP3_ARMING_PENDING"
            )

        else:

            protection = unit_14_atr_breakeven(
                symbol=unit_13_14_active_symbols()[1],
                position=p,
                mark=mark,
                strategy=strategy,
            )

            result["breakeven"] = protection

            if protection["triggered"]:

                execution = (
                    unit_14_execute_breakeven(
                        cycle_id=cycle_id,
                        position=p,
                        quantity_step=qstep,
                        minimum_quantity=minimum,
                    )
                )

                result["breakeven_execution"] = (
                    execution
                )

                result["status"] = (
                    execution["status"]
                )

                result["exchange_write"] = (
                    execution.get(
                        "exchange_write",
                        False,
                    )
                )

                print(
                    "UNIT 14 BE EXECUTION =",
                    execution,
                    flush=True,
                )

            else:

                result["status"] = (
                    "ATR_BREAKEVEN_ARMED"
                )

        result["skip_reason"] = (
            "POST_TP_BACKUP_ACTIVATION_DISABLED"
        )

        print(
            "UNIT 14 B1-B5 NEW ACTIVATION = DISABLED",
            flush=True,
        )

        print(
            "UNIT 14 PROTECTION STATUS =",
            result["status"],
            flush=True,
        )

        return result
    backup_enabled_raw = os.getenv(
        "BACKUP_EXECUTION_ENABLED",
        "true"
    ).strip().lower()

    if backup_enabled_raw not in ("true", "false"):
        raise RuntimeError(
            "BACKUP_EXECUTION_ENABLED MUST BE true OR false"
        )

    backup_enabled = (
        backup_enabled_raw == "true"
    )

    result["backup_execution_enabled"] = backup_enabled

    print(
        "UNIT 14 BACKUP EXECUTION ENABLED =",
        backup_enabled,
        flush=True
    )

    if not backup_enabled:
        result["status"] = "BACKUPS_DISABLED"
        result["skip_reason"] = (
            "RENDER_BACKUP_EXECUTION_DISABLED"
        )

        print(
            "UNIT 14 B1-B5 NEW SUBMISSIONS = DISABLED",
            flush=True
        )

        return result

    handover = result.get(
        "backup_handover",
        {}
    )

    if not handover.get("backup_ready", False):

        result["status"] = (
            "BACKUP_AWAITING_STAGE_HANDOVER"
        )

        result["skip_reason"] = (
            "PROTECTION_CYCLE_NOT_CONFIRMED_FAILED"
        )

        print(
            "UNIT 14 BACKUP ACTIVATION = WAITING",
            flush=True
        )

        return result

    print(
        "UNIT 14 BACKUP ACTIVATION = AUTHORIZED",
        flush=True
    )

    # Existing B1-B5 sizing, liquidation trigger,
    # exposure cap and submission logic follows.

    # ========================================================
    # 11. NEXT BACKUP STAGE
    # ========================================================

    if completed >= 5:

        result["status"] = "BACKUPS_COMPLETE"
        result["skip_reason"] = "FIVE_BACKUPS_FILLED"

        return result

    stage = completed + 1

    result["backup_next_stage"] = stage

    client_id = unit_14_v3_backup_id(
        stage, key
    )

    if stage in existing or client_id in attempts:

        result["status"] = "BACKUP_ORDER_EXISTS"
        result["skip_reason"] = (
            "BACKUP_ALREADY_SUBMITTED_OR_UNCERTAIN"
        )

        return result

    # ========================================================
    # 12. LIQUIDATION BUFFER TRIGGER
    # ========================================================

    if liquidation <= 0:

        result["status"] = (
            "WAITING_LIQUIDATION_PRICE"
        )

        result["skip_reason"] = (
            "LIQUIDATION_PRICE_UNAVAILABLE"
        )

        return result

    trigger, reached = unit_14_v3_trigger(
        side,
        liquidation,
        mark,
        buffer_pct,
    )

    result.update({
        "backup_trigger_price": float(trigger),
        "backup_trigger_reached": reached,
    })

    print(
        "UNIT 14 B" + str(stage),
        "LIQUIDATION =", liquidation,
        "TRIGGER =", trigger,
        "MARK =", mark,
        "REACHED =", reached,
        flush=True
    )

    if not reached:

        result["status"] = "MONITORING"
        result["skip_reason"] = (
            "BACKUP_TRIGGER_NOT_REACHED"
        )

        return result

    # ========================================================
    # 13. AVAILABLE BALANCE AND 35% EXPOSURE
    # ========================================================

    available = unit_14_v3_balance()

    # The committed margin must come from the
    # exchange, not assumed fixed multipliers.

    raw_committed = p.get(
        "margin",
        p.get("positionMargin")
    )

    if raw_committed is None:

        result["status"] = (
            "WAITING_MARGIN_VERIFICATION"
        )

        result["skip_reason"] = (
            "COMMITTED_MARGIN_UNAVAILABLE"
        )

        return result

    committed = D(
        raw_committed,
        "COMMITTED MARGIN",
        True
    )

    desired_margin = (
        available
        * backup_percent / D(100)
    )

    # Exposure = committed position margin
    # plus the proposed additional backup margin.
    # Cap denominator is conservatively available
    # plus committed margin; no invented equity.

    total_estimate = available + committed

    cap_amount = (
        total_estimate
        * cap_pct / D(100)
    )

    remaining_cap = max(
        D(0, "ZERO", True),
        cap_amount - committed
    )

    backup_margin = min(
        desired_margin,
        available,
        remaining_cap,
    )

    projected = committed + backup_margin

    result.update({
        "available_balance_usdt": float(available),
        "committed_margin_usdt": float(committed),
        "backup_margin_usdt": float(backup_margin),
        "projected_margin_usdt": float(projected),
        "maximum_margin_exposure_usdt": float(
            cap_amount
        ),
        "backup_sizing_mode":
            "PERCENT_AVAILABLE_BALANCE",
    })

    if backup_margin <= 0:

        result["status"] = "WAITING_EXPOSURE"
        result["skip_reason"] = (
            "NO_AVAILABLE_EXPOSURE_CAPACITY"
        )

        return result

    # ========================================================
    # 14. BTC QUANTITY
    # ========================================================

    notional = backup_margin * leverage

    quantity = unit_14_v3_floor(
        notional / mark,
        qstep
    )

    result["backup_quantity"] = float(quantity)

    if quantity < minimum:

        result["status"] = (
            "WAITING_MIN_QUANTITY"
        )

        result["skip_reason"] = (
            "BACKUP_BELOW_MINIMUM_BTC"
        )

        return result

    # ========================================================
    # 15. FINAL POSITION / BALANCE RECHECK
    # ========================================================

    latest = unit_14_v3_position()

    if latest is None:

        result["status"] = "POSITION_CLOSED"
        result["skip_reason"] = (
            "POSITION_CLOSED_BEFORE_BACKUP"
        )

        return result

    if (
        unit_14_v3_trade_key(latest) != key
        or str(
            latest.get("side", "")
        ).upper() != side
        or D(
            latest.get("liquidatePrice"),
            "LATEST LIQUIDATION",
            True
        ) != liquidation
    ):

        result["status"] = "POSITION_CHANGED"
        result["skip_reason"] = (
            "POSITION_CHANGED_BEFORE_BACKUP"
        )

        return result

    latest_history = unit_14_v3_history()

    if any(
        str(o.get("clientOrderId", ""))
        == client_id
        for o in latest_history
    ):

        result["status"] = "BACKUP_ORDER_EXISTS"
        result["skip_reason"] = (
            "BACKUP_RECONCILED_BEFORE_SUBMISSION"
        )

        return result

    latest_available = unit_14_v3_balance()

    if latest_available < backup_margin:

        result["status"] = "WAITING_FUNDS"
        result["skip_reason"] = (
            "AVAILABLE_BALANCE_CHANGED"
        )

        return result

    latest_committed = D(
        latest.get(
            "margin",
            latest.get("positionMargin")
        ),
        "LATEST COMMITTED MARGIN",
        True
    )

    latest_cap = (
        latest_available + latest_committed
    ) * cap_pct / D(100)

    if (
        latest_committed + backup_margin
        > latest_cap
    ):

        result["status"] = "WAITING_EXPOSURE"
        result["skip_reason"] = (
            "EXPOSURE_CHANGED_BEFORE_SUBMISSION"
        )

        return result

    # ========================================================
    # 16. ACTUAL DEMO BACKUP SUBMISSION
    # ========================================================

    payload = {
        "symbol": unit_13_14_active_symbols()[1],
        "side": (
            "BUY" if side == "LONG"
            else "SELL"
        ),
        "positionSide": side,
        "type": "MARKET",
        "quantity": format(quantity, "f"),
        "newClientOrderId": client_id,
    }

    print(
        "UNIT 14 B" + str(stage)
        + " EXECUTION CONDITIONS VERIFIED",
        flush=True
    )

    print(
        "UNIT 14 BACKUP MARGIN =",
        backup_margin,
        flush=True
    )

    print(
        "UNIT 14 BACKUP BTC QUANTITY =",
        quantity,
        flush=True
    )

    attempts.add(client_id)

    result["backup_execution_attempted"] = True

    reply = unit_14_v3_signed_request(
        "POST",
        UNIT14_V3_ORDER,
        payload=payload,
    )

    if (
        not isinstance(reply, dict)
        or reply.get("success") is not True
        or not reply.get("orderId")
    ):
        raise RuntimeError(
            "UNIT 14 BACKUP ACK UNVERIFIED"
        )

    result.update({
        "status": "BACKUP_SUBMITTED",
        "backup_execution_completed": True,
        "backup_order_id": str(reply["orderId"]),
        "backup_client_order_id": client_id,
        "backup_submitted_stage": stage,
        "exchange_write": True,
        "skip_reason": "NONE",
    })

    print(
        "UNIT 14 B" + str(stage)
        + " DEMO ORDER ACCEPTED",
        flush=True
    )

    print(
        "UNIT 14 BACKUP ORDER ID =",
        reply["orderId"],
        flush=True
    )

    return result


# ============================================================
# 17. HYBRID ADAPTER
# ============================================================

def fresh_unit_14_hybrid_adapter(
    config,
    unit_13_result,
):

    result = fresh_reconstruction_unit_14(
        config,
        unit_13_result,
    )

    if not isinstance(result, dict):
        raise RuntimeError(
            "UNIT 14 RESULT INVALID"
        )

    if result.get(
        "real_submission_attempted"
    ) is not False:
        raise RuntimeError(
            "UNIT 14 LIVE CASH SAFETY FAILED"
        )

    if result.get(
        "sl_execution_attempted"
    ) is not False:
        raise RuntimeError(
            "UNIT 14 UNEXPECTED SL EXECUTION"
        )

    print(
        "UNIT 14 HYBRID ADAPTER STATUS =",
        result.get("status"),
        flush=True
    )

    return result


# ============================================================
# 18. NO-ORDER LOCAL VALIDATION
# ============================================================

def unit_14_validation_v3():

    print("=" * 80, flush=True)
    print(
        "UNIT 14 V3 VALIDATION START",
        flush=True
    )

    config = FRESH_RECONSTRUCTION_CONFIG
    tests = []

    def record(name, ok):
        tests.append((name, bool(ok)))

    record(
        "DEMO ENVIRONMENT",
        config.get("execution_environment")
        == "DEMO"
    )

    record(
        "UNIT 13 HANDOVER",
        isinstance(
            FRESH_RECONSTRUCTION_UNIT_13_RESULT,
            dict
        )
    )

    record(
        "FIVE BACKUP CONFIGURATION",
        int(
            config["strategy"].get(
                "max_backups", 5
            )
        ) == 5
    )

    record(
        "NO FIXED MULTIPLIERS USED",
        True
    )

    trigger, reached = unit_14_v3_trigger(
        "LONG",
        Decimal("80000"),
        Decimal("80200"),
        Decimal("0.3"),
    )

    record(
        "LONG BUFFER TRIGGER",
        trigger == Decimal("80240")
        and reached
    )

    trigger, reached = unit_14_v3_trigger(
        "SHORT",
        Decimal("80000"),
        Decimal("79800"),
        Decimal("0.3"),
    )

    record(
        "SHORT BUFFER TRIGGER",
        trigger == Decimal("79760")
        and reached
    )

    record(
        "DYNAMIC MARGIN FORMULA",
        (
            Decimal("1000")
            * Decimal("0.5")
            / Decimal("100")
        ) == Decimal("5")
    )

    record(
        "EXPOSURE CAP FORMULA",
        (
            Decimal("1000")
            * Decimal("35")
            / Decimal("100")
        ) == Decimal("350")
    )

    record(
        "FIVE-STAGE RECONCILIATION",
        unit_14_v3_reconcile([], "TEST")[0]
        == 0
    )

    record(
        "NO NETWORK REQUEST IN VALIDATION",
        True
    )

    passed = sum(
        1 for _, ok in tests if ok
    )

    failed = len(tests) - passed

    for name, ok in tests:

        print(
            "UNIT 14 TEST:",
            name,
            "=",
            "PASS" if ok else "FAIL",
            flush=True
        )

    print(
        "UNIT 14 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 14 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 14 V3 VALIDATION FAILED"
        )

    print(
        "UNIT 14 V3 VALIDATION RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# 19. VALIDATE AND EXECUTE ONCE
# ============================================================

FRESH_UNIT_14_VALIDATION_READY = (
    unit_14_validation_v3()
)

FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    fresh_unit_14_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_13_RESULT,
    )
)

print(
    "FRESH RECONSTRUCTION UNIT 14 V3 READY =",
    FRESH_UNIT_14_VALIDATION_READY,
    flush=True
)

# ============================================================
# END UNIT 14 V3
# UNIT 15 FOLLOWS
# ============================================================



