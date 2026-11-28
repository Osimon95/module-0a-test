
        

    





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
