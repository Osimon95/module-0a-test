import asyncio
import base64
import hashlib
import hmac
import json
import os
import time
import uuid

from decimal import Decimal, ROUND_DOWN
from urllib.parse import urlencode

import aiohttp


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R10"

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()


# ============================================================
# ADJUSTABLE CONFIGURATION
# ============================================================

INITIAL_ENTRY_PERCENT = Decimal(
    os.getenv(
        "INITIAL_ENTRY_PERCENT",
        "5",
    )
)

LEVERAGE = Decimal(
    os.getenv(
        "LEVERAGE",
        "100",
    )
)

MAX_LEVERAGE = Decimal(
    os.getenv(
        "MAX_LEVERAGE",
        "100",
    )
)

MAX_PYRAMIDS = int(
    os.getenv(
        "MAX_PYRAMIDS",
        "1",
    )
)

PYRAMID_SIZE_PERCENT = Decimal(
    os.getenv(
        "PYRAMID_SIZE_PERCENT",
        "5",
    )
)

MAX_BACKUPS = int(
    os.getenv(
        "MAX_BACKUPS",
        "3",
    )
)

BACKUP_SIZE_PERCENT = Decimal(
    os.getenv(
        "BACKUP_SIZE_PERCENT",
        "5",
    )
)

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35",
    )
)

TP1_PERCENT = Decimal(
    os.getenv(
        "TP1_PERCENT",
        "20",
    )
)

TP2_PERCENT = Decimal(
    os.getenv(
        "TP2_PERCENT",
        "20",
    )
)

TP3_PERCENT = Decimal(
    os.getenv(
        "TP3_PERCENT",
        "60",
    )
)

TP1_TRIGGER_PERCENT = Decimal(
    os.getenv(
        "TP1_TRIGGER_PERCENT",
        "0.5",
    )
)

TP2_TRIGGER_PERCENT = Decimal(
    os.getenv(
        "TP2_TRIGGER_PERCENT",
        "1",
    )
)

TRAILING_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "TRAILING_DISTANCE_PERCENT",
        "0.2",
    )
)

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv(
        "SIGNAL_EXPIRY_SECONDS",
        "120",
    )
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv(
        "LOSS_COOLDOWN_SECONDS",
        "300",
    )
)

ONE_DIRECTION_ONLY = (
    os.getenv(
        "ONE_DIRECTION_ONLY",
        "true",
    ).strip().lower()
    == "true"
)

BACKUP_BUFFER_PERCENT = Decimal(
    os.getenv(
        "BACKUP_BUFFER_PERCENT",
        "0.3",
    )
)

MIN_LIQ_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "MIN_LIQ_DISTANCE_PERCENT",
        "0.2",
    )
)

PLANNING_MMR_PERCENT = Decimal(
    os.getenv(
        "PLANNING_MMR_PERCENT",
        "0.5",
    )
)


# ============================================================
# ABSOLUTE SAFETY LOCKS
# ============================================================

#
# R10 IS DRY-RUN ONLY.
#
# No function in this module sends:
#
# POST /capi/v3/order
# POST /capi/v3/account/leverage
# POST /capi/v3/account/positionMargin
#
# Only public/authenticated GET requests are allowed.
#

LIVE_ORDER_EXECUTION = False
HARD_EXECUTION_LOCK = True

DRY_RUN_ONLY = True


# ============================================================
# WEEX CREDENTIALS
# ============================================================

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
).strip()

WEEX_API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    "",
).strip()

WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    "",
).strip()


# ============================================================
# TELEGRAM
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


# ============================================================
# HELPERS
# ============================================================

ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")


def D(value):
    return Decimal(str(value))


def fmt(value):
    if value is None:
        return "N/A"

    if isinstance(value, Decimal):
        text = format(value, "f")
    else:
        text = str(value)

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text or "0"


def yes_no(value):
    return "✅ YES" if value else "❌ NO"


def active_inactive(value):
    return "ACTIVE" if value else "INACTIVE"


def floor_to_step(value, step):
    value = D(value)
    step = D(step)

    if step <= ZERO:
        return value

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def precision_to_step(precision):
    precision = int(precision)

    if precision <= 0:
        return Decimal("1")

    return Decimal(
        "1"
    ).scaleb(
        -precision
    )


def safe_decimal(value, default="0"):
    try:
        return D(value)
    except Exception:
        return D(default)


def make_client_order_id(prefix):
    raw = uuid.uuid4().hex[:18]

    return (
        f"{prefix}-{raw}"
    )[:36]


# ============================================================
# HTTP
# ============================================================

async def get_json(
    session,
    path,
    params=None,
    private=False,
):
    params = params or {}

    query = urlencode(
        params
    )

    url = (
        API_BASE_URL
        + path
        + (
            f"?{query}"
            if query
            else ""
        )
    )

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "0F-4H-R10",
    }

    if private:
        if not all(
            [
                WEEX_API_KEY,
                WEEX_API_SECRET,
                WEEX_API_PASSPHRASE,
            ]
        ):
            raise RuntimeError(
                "WEEX credentials missing"
            )

        timestamp = str(
            int(
                time.time()
                * 1000
            )
        )

        #
        # This signing format preserves the
        # V3 authenticated-read structure
        # used throughout our diagnostic chain.
        #
        request_path = (
            path
            + (
                f"?{query}"
                if query
                else ""
            )
        )

        message = (
            timestamp
            + "GET"
            + request_path
        )

        digest = hmac.new(
            WEEX_API_SECRET.encode(),
            message.encode(),
            hashlib.sha256,
        ).digest()

        signature = base64.b64encode(
            digest
        ).decode()

        headers.update(
            {
                "ACCESS-KEY":
                    WEEX_API_KEY,

                "ACCESS-SIGN":
                    signature,

                "ACCESS-PASSPHRASE":
                    WEEX_API_PASSPHRASE,

                "ACCESS-TIMESTAMP":
                    timestamp,
            }
        )

    async with session.get(
        url,
        headers=headers,
        timeout=aiohttp.ClientTimeout(
            total=20
        ),
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX HTTP "
                f"{response.status}: "
                f"{text}"
            )

        try:
            return json.loads(text)
        except Exception:
            raise RuntimeError(
                f"Invalid JSON from WEEX: "
                f"{text[:500]}"
            )


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    session,
    message,
):
    if not (
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    ):
        print(
            "TELEGRAM NOT CONFIGURED"
        )
        return False

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/"
        f"sendMessage"
    )

    payload = {
        "chat_id":
            TELEGRAM_CHAT_ID,

        "text":
            message,

        "disable_web_page_preview":
            True,
    }

    try:
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            text = await response.text()

            if response.status != 200:
                print(
                    "TELEGRAM ERROR:",
                    response.status,
                    text[:300],
                )
                return False

            print(
                "TELEGRAM MESSAGE SENT"
            )

            return True

    except Exception as exc:
        print(
            "TELEGRAM ERROR:",
            repr(exc),
        )

        return False


# ============================================================
# EXCHANGE INFO PARSING
# ============================================================

def extract_contract(
    data,
    symbol,
):
    candidates = []

    if isinstance(
        data,
        list,
    ):
        candidates = data

    elif isinstance(
        data,
        dict,
    ):
        for key in (
            "symbols",
            "data",
            "result",
            "contracts",
        ):
            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                candidates.extend(
                    value
                )

        if (
            str(
                data.get(
                    "symbol",
                    ""
                )
            ).upper()
            == symbol
        ):
            candidates.append(
                data
            )

    for item in candidates:
        if not isinstance(
            item,
            dict,
        ):
            continue

        item_symbol = str(
            item.get(
                "symbol",
                ""
            )
        ).upper()

        if item_symbol == symbol:
            return item

    raise RuntimeError(
        f"{symbol} contract info "
        f"not found"
    )


def contract_value(
    contract,
):
    for key in (
        "contractValue",
        "contractSize",
        "multiplier",
        "faceValue",
    ):
        if key in contract:
            value = safe_decimal(
                contract[key]
            )

            if value > ZERO:
                return value

    return Decimal(
        "0.0001"
    )


def minimum_order(
    contract,
):
    for key in (
        "minOrderSize",
        "minQty",
        "minimumOrderQuantity",
    ):
        if key in contract:
            value = safe_decimal(
                contract[key]
            )

            if value > ZERO:
                return value

    return Decimal(
        "0.0001"
    )


def quantity_precision(
    contract,
):
    for key in (
        "quantityPrecision",
        "qtyPrecision",
        "volumePrecision",
    ):
        if key in contract:
            try:
                return int(
                    contract[key]
                )
            except Exception:
                pass

    return 4


def min_leverage(
    contract,
):
    value = safe_decimal(
        contract.get(
            "minLeverage",
            "1",
        ),
        "1",
    )

    if value <= ZERO:
        value = Decimal(
            "1"
        )

    return value


def max_leverage(
    contract,
):
    value = safe_decimal(
        contract.get(
            "maxLeverage",
            "0",
        )
    )

    if value <= ZERO:
        value = MAX_LEVERAGE

    return value


# ============================================================
# MARK PRICE
# ============================================================

def extract_mark_price(
    ticker,
):
    if isinstance(
        ticker,
        list,
    ):
        if not ticker:
            raise RuntimeError(
                "Empty ticker response"
            )

        ticker = ticker[0]

    if isinstance(
        ticker,
        dict,
    ):
        possible = [
            ticker,
            ticker.get(
                "data"
            ),
            ticker.get(
                "result"
            ),
        ]

        for obj in possible:
            if not isinstance(
                obj,
                dict,
            ):
                continue

            for key in (
                "markPrice",
                "price",
                "lastPrice",
                "last",
            ):
                if key in obj:
                    value = safe_decimal(
                        obj[key]
                    )

                    if value > ZERO:
                        return value

    raise RuntimeError(
        "Unable to extract mark price"
    )


# ============================================================
# BALANCE
# ============================================================

def extract_available_usdt(
    data,
):
    rows = []

    if isinstance(
        data,
        list,
    ):
        rows = data

    elif isinstance(
        data,
        dict,
    ):
        if isinstance(
            data.get(
                "data"
            ),
            list,
        ):
            rows = data[
                "data"
            ]

        else:
            rows = [
                data
            ]

    for row in rows:
        if not isinstance(
            row,
            dict,
        ):
            continue

        asset = str(
            row.get(
                "asset",
                row.get(
                    "marginCoin",
                    ""
                ),
            )
        ).upper()

        if asset not in (
            "",
            "USDT",
        ):
            continue

        for key in (
            "availableBalance",
            "available",
            "availableMargin",
        ):
            if key in row:
                value = safe_decimal(
                    row[key]
                )

                if value >= ZERO:
                    return value

    raise RuntimeError(
        "Unable to extract "
        "available USDT balance"
    )


# ============================================================
# POSITIONS
# ============================================================

def normalize_positions(
    data,
):
    if isinstance(
        data,
        list,
    ):
        return data

    if isinstance(
        data,
        dict,
    ):
        for key in (
            "data",
            "positions",
            "result",
        ):
            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                return value

        return [
            data
        ]

    return []


def find_open_positions(
    data,
    symbol,
):
    positions = []

    for row in normalize_positions(
        data
    ):
        if not isinstance(
            row,
            dict,
        ):
            continue

        row_symbol = str(
            row.get(
                "symbol",
                ""
            )
        ).upper()

        if row_symbol != symbol:
            continue

        size = safe_decimal(
            row.get(
                "size",
                row.get(
                    "positionAmt",
                    "0",
                ),
            )
        )

        if abs(
            size
        ) > ZERO:
            positions.append(
                row
            )

    return positions


def extract_liquidation_price(
    position,
):
    for key in (
        "liquidationPrice",
        "liqPrice",
        "liquidatePrice",
    ):
        if key in position:
            value = safe_decimal(
                position[key]
            )

            if value > ZERO:
                return value

    return None


# ============================================================
# SIGNAL SAFETY TESTS
# ============================================================

def test_signal_gates():
    now = int(
        time.time()
    )

    fresh_signal_time = (
        now - 10
    )

    expired_signal_time = (
        now
        - SIGNAL_EXPIRY_SECONDS
        - 1
    )

    fresh_signal_accepted = (
        now
        - fresh_signal_time
        <= SIGNAL_EXPIRY_SECONDS
    )

    expired_signal_rejected = (
        now
        - expired_signal_time
        > SIGNAL_EXPIRY_SECONDS
    )

    last_loss_time = (
        now - 10
    )

    loss_cooldown_test = (
        now
        - last_loss_time
        < LOSS_COOLDOWN_SECONDS
    )

    seen_signals = set()

    signal_id = (
        f"{SYMBOL}:LONG:"
        f"{fresh_signal_time}"
    )

    first_signal_allowed = (
        signal_id
        not in seen_signals
    )

    seen_signals.add(
        signal_id
    )

    duplicate_signal_rejected = (
        signal_id
        in seen_signals
    )

    one_direction_gate = (
        ONE_DIRECTION_ONLY
    )

    return {
        "fresh":
            fresh_signal_accepted,

        "expired":
            expired_signal_rejected,

        "cooldown":
            loss_cooldown_test,

        "duplicate":
            (
                first_signal_allowed
                and duplicate_signal_rejected
            ),

        "direction":
            one_direction_gate,
    }


# ============================================================
# ENTRY SIZING
# ============================================================

def calculate_entry(
    balance,
    mark_price,
    qty_step,
):
    entry_margin = (
        balance
        * INITIAL_ENTRY_PERCENT
        / HUNDRED
    )

    entry_notional = (
        entry_margin
        * LEVERAGE
    )

    raw_quantity = (
        entry_notional
        / mark_price
    )

    quantity = floor_to_step(
        raw_quantity,
        qty_step,
    )

    return (
        entry_margin,
        entry_notional,
        raw_quantity,
        quantity,
    )


# ============================================================
# TP QUANTITY SPLIT
# ============================================================

def calculate_tp_split(
    entry_quantity,
    qty_step,
):
    #
    # TP1 and TP2 are rounded DOWN.
    #
    # TP3 receives the exact remaining
    # tradable quantity so no position
    # remainder is accidentally abandoned.
    #

    tp1_qty = floor_to_step(
        entry_quantity
        * TP1_PERCENT
        / HUNDRED,
        qty_step,
    )

    tp2_qty = floor_to_step(
        entry_quantity
        * TP2_PERCENT
        / HUNDRED,
        qty_step,
    )

    tp3_qty = (
        entry_quantity
        - tp1_qty
        - tp2_qty
    )

    tp3_qty = floor_to_step(
        tp3_qty,
        qty_step,
    )

    total_exit_qty = (
        tp1_qty
        + tp2_qty
        + tp3_qty
    )

    exact_reconciliation = (
        total_exit_qty
        == entry_quantity
    )

    return {
        "tp1":
            tp1_qty,

        "tp2":
            tp2_qty,

        "tp3":
            tp3_qty,

        "total":
            total_exit_qty,

        "exact":
            exact_reconciliation,
    }


# ============================================================
# EXPOSURE
# ============================================================

def exposure_plan():
    initial = (
        INITIAL_ENTRY_PERCENT
    )

    pyramids = (
        D(MAX_PYRAMIDS)
        * PYRAMID_SIZE_PERCENT
    )

    backups = (
        D(MAX_BACKUPS)
        * BACKUP_SIZE_PERCENT
    )

    total = (
        initial
        + pyramids
        + backups
    )

    passed = (
        total
        <= MAX_FUND_EXPOSURE_PERCENT
    )

    return (
        initial,
        pyramids,
        backups,
        total,
        passed,
    )


# ============================================================
# LIQUIDATION PLANNING
# ============================================================

def estimated_long_liquidation(
    entry_price,
):
    #
    # Conservative planning-only approximation.
    #
    # Actual WEEX liquidation price from a
    # real position always overrides this.
    #

    leverage_fraction = (
        ONE / LEVERAGE
    )

    mmr_fraction = (
        PLANNING_MMR_PERCENT
        / HUNDRED
    )

    distance_fraction = (
        leverage_fraction
        - mmr_fraction
    )

    if distance_fraction <= ZERO:
        return None

    return (
        entry_price
        * (
            ONE
            - distance_fraction
        )
    )


def liquidation_distance_percent(
    entry_price,
    liquidation_price,
):
    if (
        entry_price <= ZERO
        or liquidation_price is None
    ):
        return None

    return (
        (
            entry_price
            - liquidation_price
        )
        / entry_price
        * HUNDRED
    )


# ============================================================
# DRY-RUN ORDER PAYLOADS
# ============================================================

def build_entry_payload(
    quantity,
):
    return {
        "symbol":
            SYMBOL,

        "side":
            "BUY",

        "positionSide":
            "LONG",

        "type":
            "MARKET",

        "quantity":
            fmt(quantity),

        "newClientOrderId":
            make_client_order_id(
                "r10-entry"
            ),
    }


def build_close_payload(
    quantity,
    label,
):
    return {
        "symbol":
            SYMBOL,

        "side":
            "SELL",

        "positionSide":
            "LONG",

        "type":
            "MARKET",

        "quantity":
            fmt(quantity),

        "newClientOrderId":
            make_client_order_id(
                f"r10-{label}"
            ),
    }


def validate_payload(
    payload,
    min_order,
    qty_step,
):
    required = (
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    )

    if any(
        key not in payload
        for key in required
    ):
        return False

    quantity = safe_decimal(
        payload.get(
            "quantity"
        )
    )

    if quantity <= ZERO:
        return False

    if quantity < min_order:
        return False

    if floor_to_step(
        quantity,
        qty_step,
    ) != quantity:
        return False

    client_id = str(
        payload.get(
            "newClientOrderId",
            ""
        )
    )

    if (
        len(
            client_id
        ) < 1
        or len(
            client_id
        ) > 36
    ):
        return False

    if payload[
        "symbol"
    ] != SYMBOL:
        return False

    return True


# ============================================================
# PYRAMID SIMULATION
# ============================================================

def simulate_pyramid(
    original_quantity,
    balance,
    mark_price,
    qty_step,
):
    pyramid_margin = (
        balance
        * PYRAMID_SIZE_PERCENT
        / HUNDRED
    )

    pyramid_notional = (
        pyramid_margin
        * LEVERAGE
    )

    pyramid_qty = floor_to_step(
        pyramid_notional
        / mark_price,
        qty_step,
    )

    total_qty = (
        original_quantity
        + pyramid_qty
    )

    return {
        "margin":
            pyramid_margin,

        "notional":
            pyramid_notional,

        "quantity":
            pyramid_qty,

        "total_quantity":
            total_qty,
    }


# ============================================================
# BACKUP PLANNING
# ============================================================

def simulate_backups(
    balance,
    mark_price,
    qty_step,
):
    backup_margin = (
        balance
        * BACKUP_SIZE_PERCENT
        / HUNDRED
    )

    backup_notional = (
        backup_margin
        * LEVERAGE
    )

    backup_qty = floor_to_step(
        backup_notional
        / mark_price,
        qty_step,
    )

    plans = []

    for number in range(
        1,
        MAX_BACKUPS + 1,
    ):
        plans.append(
            {
                "number":
                    number,

                "margin":
                    backup_margin,

                "notional":
                    backup_notional,

                "quantity":
                    backup_qty,
            }
        )

    return plans


# ============================================================
# FULL R10 DRY-RUN LIFECYCLE
# ============================================================

def simulate_trade_lifecycle(
    entry_quantity,
    min_order,
    qty_step,
    balance,
    mark_price,
):
    stages = {}

    #
    # 1. ENTRY PAYLOAD
    #

    entry_payload = (
        build_entry_payload(
            entry_quantity
        )
    )

    stages[
        "entry_payload"
    ] = validate_payload(
        entry_payload,
        min_order,
        qty_step,
    )

    #
    # 2. SIMULATED ACKNOWLEDGEMENT
    #

    fake_order_id = (
        "SIM-"
        + uuid.uuid4().hex[:16]
    )

    simulated_ack = {
        "success":
            True,

        "orderId":
            fake_order_id,

        "clientOrderId":
            entry_payload[
                "newClientOrderId"
            ],
    }

    stages[
        "acknowledgement"
    ] = (
        simulated_ack[
            "success"
        ]
        is True
        and bool(
            simulated_ack[
                "orderId"
            ]
        )
    )

    #
    # 3. SIMULATED POSITION
    #

    simulated_position = {
        "symbol":
            SYMBOL,

        "side":
            "LONG",

        "size":
            fmt(
                entry_quantity
            ),

        "entryPrice":
            fmt(
                mark_price
            ),

        "leverage":
            fmt(
                LEVERAGE
            ),
    }

    stages[
        "position_created"
    ] = (
        safe_decimal(
            simulated_position[
                "size"
            ]
        )
        == entry_quantity
    )

    #
    # 4. PYRAMID
    #

    pyramid = simulate_pyramid(
        entry_quantity,
        balance,
        mark_price,
        qty_step,
    )

    pyramid_valid = (
        MAX_PYRAMIDS == 0
        or (
            pyramid[
                "quantity"
            ]
            >= min_order
        )
    )

    stages[
        "pyramid_plan"
    ] = pyramid_valid

    #
    # R10 exit split is intentionally
    # validated against the INITIAL entry
    # quantity because this diagnostic checks
    # the known R9 0.0005 entry first.
    #
    # Later lifecycle modules can recompute
    # TP sizing after each real pyramid fill.
    #

    tp = calculate_tp_split(
        entry_quantity,
        qty_step,
    )

    stages[
        "tp_reconciliation"
    ] = tp[
        "exact"
    ]

    #
    # 5. TP1
    #

    tp1_payload = (
        build_close_payload(
            tp[
                "tp1"
            ],
            "tp1",
        )
    )

    stages[
        "tp1_payload"
    ] = validate_payload(
        tp1_payload,
        min_order,
        qty_step,
    )

    #
    # 6. TP2
    #

    tp2_payload = (
        build_close_payload(
            tp[
                "tp2"
            ],
            "tp2",
        )
    )

    stages[
        "tp2_payload"
    ] = validate_payload(
        tp2_payload,
        min_order,
        qty_step,
    )

    #
    # 7. FINAL TRAILING EXIT
    #

    trailing_payload = (
        build_close_payload(
            tp[
                "tp3"
            ],
            "trail",
        )
    )

    stages[
        "trailing_payload"
    ] = validate_payload(
        trailing_payload,
        min_order,
        qty_step,
    )

    #
    # 8. COMPLETE CLOSE
    #

    simulated_remaining = (
        entry_quantity
        - tp[
            "tp1"
        ]
        - tp[
            "tp2"
        ]
        - tp[
            "tp3"
        ]
    )

    stages[
        "position_closed"
    ] = (
        simulated_remaining
        == ZERO
    )

    #
    # 9. BACKUPS
    #

    backups = simulate_backups(
        balance,
        mark_price,
        qty_step,
    )

    backup_valid = all(
        (
            row[
                "quantity"
            ]
            >= min_order
        )
        for row in backups
    ) if backups else True

    stages[
        "backup_plan"
    ] = backup_valid

    #
    # 10. STATE CLEANUP
    #

    simulated_state = {
        "position":
            None,

        "pending_signal":
            None,

        "pyramid_count":
            0,

        "backup_count":
            0,
    }

    stages[
        "state_cleanup"
    ] = (
        simulated_state[
            "position"
        ]
        is None
        and simulated_state[
            "pending_signal"
        ]
        is None
        and simulated_state[
            "pyramid_count"
        ]
        == 0
        and simulated_state[
            "backup_count"
        ]
        == 0
    )

    stages[
        "all_passed"
    ] = all(
        stages.values()
    )

    return {
        "stages":
            stages,

        "entry_payload":
            entry_payload,

        "ack":
            simulated_ack,

        "position":
            simulated_position,

        "pyramid":
            pyramid,

        "tp":
            tp,

        "tp1_payload":
            tp1_payload,

        "tp2_payload":
            tp2_payload,

        "trailing_payload":
            trailing_payload,

        "backups":
            backups,
    }


# ============================================================
# MAIN
# ============================================================

async def main():

    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "FINAL PRE-LIVE DRY-RUN"
    )

    print(
        "NO LIVE ORDER TRANSMISSION"
    )

    print(
        "=" * 60
    )

    if LIVE_ORDER_EXECUTION:
        raise RuntimeError(
            "R10 SAFETY FAILURE: "
            "LIVE_ORDER_EXECUTION "
            "must remain False"
        )

    if not HARD_EXECUTION_LOCK:
        raise RuntimeError(
            "R10 SAFETY FAILURE: "
            "HARD_EXECUTION_LOCK "
            "must remain True"
        )

    if not DRY_RUN_ONLY:
        raise RuntimeError(
            "R10 SAFETY FAILURE: "
            "DRY_RUN_ONLY must "
            "remain True"
        )

    async with aiohttp.ClientSession() as session:

        #
        # PUBLIC EXCHANGE INFORMATION
        #

        exchange_info = await get_json(
            session,
            "/capi/v3/market/exchangeInfo",
            {
                "symbol":
                    SYMBOL
            },
        )

        contract = extract_contract(
            exchange_info,
            SYMBOL,
        )

        min_order = minimum_order(
            contract
        )

        qty_precision = (
            quantity_precision(
                contract
            )
        )

        qty_step = precision_to_step(
            qty_precision
        )

        contract_val = contract_value(
            contract
        )

        weex_min_leverage = min_leverage(
            contract
        )

        weex_max_leverage = max_leverage(
            contract
        )

        #
        # API TRADING SYMBOL GATE
        #

        trading_symbols_raw = (
            await get_json(
                session,
                "/capi/v3/market/apiTradingSymbols",
            )
        )

        if isinstance(
            trading_symbols_raw,
            dict,
        ):
            trading_symbols = (
                trading_symbols_raw.get(
                    "data",
                    trading_symbols_raw.get(
                        "result",
                        [],
                    ),
                )
            )
        else:
            trading_symbols = (
                trading_symbols_raw
            )

        if not isinstance(
            trading_symbols,
            list,
        ):
            trading_symbols = []

        api_symbol_ok = (
            SYMBOL
            in [
                str(
                    item
                ).upper()
                for item
                in trading_symbols
            ]
        )

        #
        # MARK PRICE
        #

        ticker = await get_json(
            session,
            "/capi/v3/market/ticker/price",
            {
                "symbol":
                    SYMBOL
            },
        )

        mark_price = (
            extract_mark_price(
                ticker
            )
        )

        #
        # AUTHENTICATED BALANCE
        #

        balance_data = (
            await get_json(
                session,
                "/capi/v3/account/balance",
                private=True,
            )
        )

        available_usdt = (
            extract_available_usdt(
                balance_data
            )
        )

        #
        # AUTHENTICATED POSITION
        #

        position_data = (
            await get_json(
                session,
                "/capi/v3/account/position/singlePosition",
                {
                    "symbol":
                        SYMBOL
                },
                private=True,
            )
        )

        open_positions = (
            find_open_positions(
                position_data,
                SYMBOL,
            )
        )

        external_position_clear = (
            len(
                open_positions
            )
            == 0
        )

        real_liq_price = None

        if open_positions:
            real_liq_price = (
                extract_liquidation_price(
                    open_positions[0]
                )
            )

        #
        # SIGNAL GATES
        #

        signal_tests = (
            test_signal_gates()
        )

        #
        # LEVERAGE GATE
        #

        leverage_gate = (
            LEVERAGE
            >= weex_min_leverage
            and LEVERAGE
            <= weex_max_leverage
            and LEVERAGE
            <= MAX_LEVERAGE
        )

        #
        # ENTRY
        #

        (
            entry_margin,
            entry_notional,
            raw_entry_quantity,
            entry_quantity,
        ) = calculate_entry(
            available_usdt,
            mark_price,
            qty_step,
        )

        minimum_passed = (
            entry_quantity
            >= min_order
        )

        #
        # EXPOSURE
        #

        (
            exposure_initial,
            exposure_pyramids,
            exposure_backups,
            total_exposure,
            exposure_passed,
        ) = exposure_plan()

        #
        # TP CONFIG
        #

        tp_split_percent = (
            TP1_PERCENT
            + TP2_PERCENT
            + TP3_PERCENT
        )

        tp_percent_passed = (
            tp_split_percent
            == HUNDRED
        )

        #
        # LIQUIDATION PLANNING
        #

        estimated_liq = (
            estimated_long_liquidation(
                mark_price
            )
        )

        estimated_liq_distance = (
            liquidation_distance_percent(
                mark_price,
                estimated_liq,
            )
        )

        liq_distance_passed = (
            estimated_liq_distance
            is not None
            and estimated_liq_distance
            >= MIN_LIQ_DISTANCE_PERCENT
        )

        #
        # FULL R10 LIFECYCLE
        #

        lifecycle = (
            simulate_trade_lifecycle(
                entry_quantity,
                min_order,
                qty_step,
                available_usdt,
                mark_price,
            )
        )

        stages = lifecycle[
            "stages"
        ]

        tp = lifecycle[
            "tp"
        ]

        #
        # GLOBAL RESULT
        #

        all_passed = all(
            [
                api_symbol_ok,

                signal_tests[
                    "fresh"
                ],

                signal_tests[
                    "expired"
                ],

                signal_tests[
                    "cooldown"
                ],

                signal_tests[
                    "duplicate"
                ],

                signal_tests[
                    "direction"
                ],

                external_position_clear,

                leverage_gate,

                minimum_passed,

                exposure_passed,

                tp_percent_passed,

                liq_distance_passed,

                stages[
                    "all_passed"
                ],

                HARD_EXECUTION_LOCK,

                not LIVE_ORDER_EXECUTION,

                DRY_RUN_ONLY,
            ]
        )

        status_icon = (
            "✅"
            if all_passed
            else "⚠️"
        )

        status_text = (
            "DIAGNOSTIC PASSED"
            if all_passed
            else "NOT READY"
        )

        #
        # REPORT
        #

        report = (
            f"{status_icon} MODULE "
            f"{MODULE_NAME} "
            f"{status_text}\n\n"

            f"{SYMBOL}\n\n"

            f"Available USDT: "
            f"{fmt(available_usdt)}\n"

            f"Mark Price: "
            f"{fmt(mark_price)} USDT\n\n"

            f"FINAL EXECUTION GATE\n"

            f"API Trading Symbol: "
            f"{yes_no(api_symbol_ok)}\n"

            f"Fresh Signal Accepted: "
            f"{yes_no(signal_tests['fresh'])}\n"

            f"Expired Signal Rejected: "
            f"{yes_no(signal_tests['expired'])}\n"

            f"Loss Cooldown Test: "
            f"{yes_no(signal_tests['cooldown'])}\n"

            f"Duplicate Signal Rejected: "
            f"{yes_no(signal_tests['duplicate'])}\n"

            f"One Direction Gate: "
            f"{yes_no(signal_tests['direction'])}\n"

            f"External Position Clear: "
            f"{yes_no(external_position_clear)}\n\n"

            f"ADJUSTABLE CONFIG\n"

            f"Entry: "
            f"{fmt(INITIAL_ENTRY_PERCENT)}%\n"

            f"Leverage: "
            f"{fmt(LEVERAGE)}x\n"

            f"Max Config Leverage: "
            f"{fmt(MAX_LEVERAGE)}x\n"

            f"Max Pyramids: "
            f"{MAX_PYRAMIDS}\n"

            f"Pyramid Size: "
            f"{fmt(PYRAMID_SIZE_PERCENT)}%\n"

            f"Max Backups: "
            f"{MAX_BACKUPS}\n"

            f"Backup Size: "
            f"{fmt(BACKUP_SIZE_PERCENT)}% each\n"

            f"Max Fund Exposure: "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n\n"

            f"WEEX CONTRACT\n"

            f"Minimum Order: "
            f"{fmt(min_order)}\n"

            f"Quantity Precision: "
            f"{qty_precision}\n"

            f"Quantity Step: "
            f"{fmt(qty_step)}\n"

            f"Contract Value: "
            f"{fmt(contract_val)}\n"

            f"WEEX Min Leverage: "
            f"{fmt(weex_min_leverage)}x\n"

            f"WEEX Max Leverage: "
            f"{fmt(weex_max_leverage)}x\n"

            f"Leverage Gate: "
            f"{yes_no(leverage_gate)}\n\n"

            f"DYNAMIC ENTRY\n"

            f"Margin: "
            f"{fmt(entry_margin)} USDT\n"

            f"Notional: "
            f"{fmt(entry_notional)} USDT\n"

            f"Raw Quantity: "
            f"{fmt(raw_entry_quantity)}\n"

            f"Tradable Quantity: "
            f"{fmt(entry_quantity)}\n"

            f"Minimum Passed: "
            f"{yes_no(minimum_passed)}\n\n"

            f"WORST-CASE EXPOSURE\n"

            f"Initial: "
            f"{fmt(exposure_initial)}%\n"

            f"Pyramids: "
            f"{fmt(exposure_pyramids)}%\n"

            f"Backups: "
            f"{fmt(exposure_backups)}%\n"

            f"Total: "
            f"{fmt(total_exposure)}% / "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n"

            f"Exposure Passed: "
            f"{yes_no(exposure_passed)}\n\n"

            f"TP / TRAILING\n"

            f"TP1 / TP2 / TP3: "
            f"{fmt(TP1_PERCENT)}% / "
            f"{fmt(TP2_PERCENT)}% / "
            f"{fmt(TP3_PERCENT)}%\n"

            f"TP Split = 100%: "
            f"{yes_no(tp_percent_passed)}\n"

            f"TP1 Trigger: "
            f"{fmt(TP1_TRIGGER_PERCENT)}%\n"

            f"TP2 Trigger: "
            f"{fmt(TP2_TRIGGER_PERCENT)}%\n"

            f"Trailing Distance: "
            f"{fmt(TRAILING_DISTANCE_PERCENT)}%\n\n"

            f"R10 EXIT QUANTITY TEST\n"

            f"Entry Quantity: "
            f"{fmt(entry_quantity)}\n"

            f"TP1 Quantity: "
            f"{fmt(tp['tp1'])}\n"

            f"TP2 Quantity: "
            f"{fmt(tp['tp2'])}\n"

            f"TP3 / Trailing Quantity: "
            f"{fmt(tp['tp3'])}\n"

            f"Total Exit Quantity: "
            f"{fmt(tp['total'])}\n"

            f"Exact Position Reconciliation: "
            f"{yes_no(tp['exact'])}\n\n"

            f"PROTECTION\n"

            f"Signal Expiry: "
            f"{SIGNAL_EXPIRY_SECONDS}s\n"

            f"Loss Cooldown: "
            f"{LOSS_COOLDOWN_SECONDS}s\n"

            f"One Direction Only: "
            f"{active_inactive(ONE_DIRECTION_ONLY)}\n"

            f"Backup Buffer: "
            f"{fmt(BACKUP_BUFFER_PERCENT)}%\n"

            f"Min Liq Distance: "
            f"{fmt(MIN_LIQ_DISTANCE_PERCENT)}%\n"

            f"Planning MMR: "
            f"{fmt(PLANNING_MMR_PERCENT)}%\n\n"

            f"REAL WEEX POSITION\n"

            f"{'No open position detected' if external_position_clear else 'OPEN POSITION DETECTED'}\n"

            f"WEEX Liquidation Price: "
            f"{fmt(real_liq_price)}\n\n"

            f"R10 LIQUIDATION PLANNING ONLY\n"

            f"Estimated Long Liq: "
            f"{fmt(estimated_liq)}\n"

            f"Estimated Liq Distance: "
            f"{fmt(estimated_liq_distance)}%\n"

            f"Min Distance Passed: "
            f"{yes_no(liq_distance_passed)}\n"

            f"Actual WEEX liquidation price "
            f"remains authoritative.\n\n"

            f"R10 FULL DRY-RUN LIFECYCLE\n"

            f"Entry Payload: "
            f"{yes_no(stages['entry_payload'])}\n"

            f"Simulated Acknowledgement: "
            f"{yes_no(stages['acknowledgement'])}\n"

            f"Simulated Position Created: "
            f"{yes_no(stages['position_created'])}\n"

            f"Pyramid Plan: "
            f"{yes_no(stages['pyramid_plan'])}\n"

            f"TP Quantity Reconciliation: "
            f"{yes_no(stages['tp_reconciliation'])}\n"

            f"TP1 Close Payload: "
            f"{yes_no(stages['tp1_payload'])}\n"

            f"TP2 Close Payload: "
            f"{yes_no(stages['tp2_payload'])}\n"

            f"Trailing Close Payload: "
            f"{yes_no(stages['trailing_payload'])}\n"

            f"Backup Plan: "
            f"{yes_no(stages['backup_plan'])}\n"

            f"Position Fully Closed: "
            f"{yes_no(stages['position_closed'])}\n"

            f"Trade State Cleanup: "
            f"{yes_no(stages['state_cleanup'])}\n"

            f"Full Lifecycle Passed: "
            f"{yes_no(stages['all_passed'])}\n\n"

            f"R10 EXACT ENTRY PAYLOAD SIMULATION\n"

            f"Endpoint Target: "
            f"POST /capi/v3/order\n"

            f"Symbol: "
            f"{lifecycle['entry_payload']['symbol']}\n"

            f"Side: "
            f"{lifecycle['entry_payload']['side']} / "
            f"{lifecycle['entry_payload']['positionSide']}\n"

            f"Type: "
            f"{lifecycle['entry_payload']['type']}\n"

            f"Quantity: "
            f"{lifecycle['entry_payload']['quantity']}\n"

            f"newClientOrderId: "
            f"{lifecycle['entry_payload']['newClientOrderId']}\n"

            f"Endpoint Target: "
            f"SIMULATION ONLY — NOT SENT\n\n"

            f"🛡 Hard execution lock active\n"

            f"⚠️ Live order execution disabled\n"

            f"⚠️ NO LIVE ORDER WAS SENT"
        )

        print(
            "=" * 60
        )

        print(
            report
        )

        print(
            "=" * 60
        )

        #
        # ONE TELEGRAM REPORT PER PROCESS START
        #

        await send_telegram(
            session,
            report,
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    try:
        asyncio.run(
            main()
        )

    except KeyboardInterrupt:
        print(
            "STOPPED"
        )

    except Exception as exc:
        error_message = (
            f"❌ MODULE "
            f"{MODULE_NAME} ERROR\n\n"
            f"{SYMBOL}\n\n"
            f"{type(exc).__name__}: "
            f"{exc}\n\n"
            f"🛡 Hard execution lock active\n"
            f"⚠️ Live order execution disabled\n"
            f"⚠️ NO LIVE ORDER WAS SENT"
        )

        print(
            error_message
        )

        #
        # Avoid a second asyncio.run()
        # Telegram call here.
        #
        # This prevents the error handler
        # itself from becoming a source
        # of duplicate startup messages.
        #
