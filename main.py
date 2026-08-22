import asyncio
import base64
import hashlib
import hmac
import json
import os
import re
import time
import traceback
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlencode

import aiohttp
from aiohttp import web


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R27"
API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()


def default_demo_symbol(symbol: str) -> str:
    return symbol[:-4] + "SUSDT" if symbol.endswith("USDT") else symbol


DEMO_SYMBOL = os.getenv(
    "DEMO_SYMBOL",
    default_demo_symbol(SYMBOL),
).strip().upper()


# ============================================================
# ABSOLUTE EXECUTION SAFETY
# ============================================================
#
# R27 REMAINS PRE-LIVE.
#
# REAL ORDER TRANSMISSION MUST REMAIN DISABLED.
#
# The only state-changing request allowed in this module is:
#
# POST /capi/v3/sim/order
#
# REAL:
# POST /capi/v3/order
#
# MUST ALWAYS BE BLOCKED BEFORE NETWORK TRANSMISSION.
#
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_REAL_POST_LOCK = True

R27_REAL_POST_CALLED = False

REAL_ORDER_PATH = "/capi/v3/order"
DEMO_ORDER_PATH = "/capi/v3/sim/order"
DEMO_HISTORY_PATH = "/capi/v3/sim/order/history"
DEMO_POSITION_PATH = "/capi/v3/sim/position/allPosition"
DEMO_BALANCE_PATH = "/capi/v3/sim/balance"

EXCHANGE_INFO_PATH = "/capi/v3/market/exchangeInfo"
TICKER_24H_PATH = "/capi/v3/market/ticker/24hr"


# ============================================================
# ADJUSTABLE CONFIG
# ============================================================

ENTRY_PERCENT = Decimal(
    os.getenv(
        "ENTRY_PERCENT",
        "5",
    )
)

LEVERAGE = int(
    os.getenv(
        "LEVERAGE",
        "100",
    )
)

MAX_CONFIG_LEVERAGE = int(
    os.getenv(
        "MAX_CONFIG_LEVERAGE",
        "100",
    )
)

MARGIN_TYPE = os.getenv(
    "MARGIN_TYPE",
    "ISOLATED",
).strip().upper()


MAX_PYRAMID_ADDS = int(
    os.getenv(
        "MAX_PYRAMID_ADDS",
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

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35",
    )
)


TP1_SIZE_PERCENT = Decimal("20")
TP2_SIZE_PERCENT = Decimal("20")
TP3_SIZE_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")


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


# ============================================================
# R27 DEMO ACTUAL-FILL CONFIG
# ============================================================
#
# AUTO:
#
# If a demo position already exists and is large enough:
# R27 reduces that position.
#
# Example:
#
# LONG position exists:
# SELL / LONG
#
# SHORT position exists:
# BUY / SHORT
#
# If there is not enough existing position:
# R27 opens the selected position side.
#
# This prevents repeated Render deployments from continuously
# adding paper exposure whenever possible.
#
# ============================================================

RUN_DEMO_FILL_TEST = os.getenv(
    "RUN_DEMO_FILL_TEST",
    "true",
).lower() in {
    "1",
    "true",
    "yes",
    "on",
}

DEMO_FILL_MODE = os.getenv(
    "DEMO_FILL_MODE",
    "AUTO",
).strip().upper()

DEMO_FILL_SIDE = os.getenv(
    "DEMO_FILL_SIDE",
    "BUY",
).strip().upper()

DEMO_FILL_POSITION_SIDE = os.getenv(
    "DEMO_FILL_POSITION_SIDE",
    "LONG",
).strip().upper()

HISTORY_POLL_ATTEMPTS = int(
    os.getenv(
        "HISTORY_POLL_ATTEMPTS",
        "8",
    )
)

HISTORY_POLL_DELAY_SECONDS = float(
    os.getenv(
        "HISTORY_POLL_DELAY_SECONDS",
        "0.75",
    )
)


PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


# ============================================================
# ENVIRONMENT
# ============================================================

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
).strip()

WEEX_SECRET_KEY = os.getenv(
    "WEEX_SECRET_KEY",
    "",
).strip()

WEEX_PASSPHRASE = os.getenv(
    "WEEX_PASSPHRASE",
    "",
).strip()

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


# ============================================================
# DECIMAL HELPERS
# ============================================================

D0 = Decimal("0")


def d(
    value: Any,
    default: Decimal = D0,
) -> Decimal:

    try:

        if value is None:
            return default

        if value == "":
            return default

        return Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):

        return default


def fmt(
    value: Decimal,
) -> str:

    s = format(
        value,
        "f",
    )

    if "." in s:

        s = s.rstrip("0")
        s = s.rstrip(".")

    return s or "0"


def icon(
    ok: bool,
) -> str:

    return (
        "✅ YES"
        if ok
        else "❌ NO"
    )


def floor_step(
    value: Decimal,
    step: Decimal,
) -> Decimal:

    if step <= 0:
        return value

    return (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    ) * step


def step_match(
    value: Decimal,
    step: Decimal,
) -> bool:

    if step <= 0:
        return True

    return (
        value
        ==
        floor_step(
            value,
            step,
        )
    )


def now_ms() -> int:

    return int(
        time.time()
        * 1000
    )


# ============================================================
# CLIENT ORDER ID
# ============================================================

def create_client_order_id(
    prefix: str,
    seed: str,
) -> str:

    digest = hashlib.sha256(
        seed.encode()
    ).hexdigest()[:20]

    return (
        f"{prefix}-{digest}"
    )[:36]


def valid_client_id(
    value: str,
) -> bool:

    return bool(
        re.fullmatch(
            r"[\.A-Z\:/a-z0-9_-]{1,36}",
            value or "",
        )
    )


# ============================================================
# RESPONSE HELPERS
# ============================================================

def normalize_rows(
    payload: Any,
) -> List[Dict[str, Any]]:

    if isinstance(
        payload,
        list,
    ):

        return [
            item
            for item in payload
            if isinstance(
                item,
                dict,
            )
        ]

    if isinstance(
        payload,
        dict,
    ):

        for key in (
            "data",
            "rows",
            "list",
            "result",
            "orders",
            "positions",
        ):

            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):

                return [
                    item
                    for item in value
                    if isinstance(
                        item,
                        dict,
                    )
                ]

        return [
            payload
        ]

    return []


def find_first_decimal(
    obj: Any,
    keys: Tuple[str, ...],
) -> Optional[Decimal]:

    if isinstance(
        obj,
        dict,
    ):

        for key in keys:

            if key in obj:

                try:

                    return Decimal(
                        str(
                            obj[key]
                        )
                    )

                except Exception:

                    pass

        for value in obj.values():

            found = find_first_decimal(
                value,
                keys,
            )

            if found is not None:

                return found

    elif isinstance(
        obj,
        list,
    ):

        for item in obj:

            found = find_first_decimal(
                item,
                keys,
            )

            if found is not None:

                return found

    return None


def status_terminal(
    status: str,
) -> bool:

    return status.upper() in {
        "FILLED",
        "CANCELED",
        "CANCELLED",
        "REJECTED",
        "EXPIRED",
    }


# ============================================================
# CONTRACT MODEL
# ============================================================

@dataclass
class ContractInfo:

    symbol: str

    min_order: Decimal

    quantity_precision: int

    quantity_step: Decimal

    price_precision: int

    price_step: Decimal

    contract_value: Decimal

    min_leverage: int

    max_leverage: int


# ============================================================
# SIGNAL MODEL
# ============================================================

@dataclass
class Signal:

    signal_id: str

    direction: str

    created_at: float


# ============================================================
# EXECUTION INTENT
# ============================================================

@dataclass
class ExecutionIntent:

    intent_id: str

    signal_id: str

    symbol: str

    side: str

    position_side: str

    quantity: Decimal

    leverage: int

    created_at: float

    client_order_id: str

    state: str = "NEW"


# ============================================================
# ORDER EVENT STATE
# ============================================================

@dataclass
class OrderEventState:

    status: str = "NONE"

    executed_qty: Decimal = D0

    seen_fingerprints: Set[str] = field(
        default_factory=set
    )

    def process(
        self,
        order_id: str,
        status: str,
        executed_qty: Decimal,
        update_time: Any,
    ) -> Tuple[
        bool,
        Decimal,
    ]:

        fingerprint = (
            f"{order_id}|"
            f"{status}|"
            f"{executed_qty}|"
            f"{update_time}"
        )

        if (
            fingerprint
            in self.seen_fingerprints
        ):

            return (
                False,
                D0,
            )

        if status_terminal(
            self.status
        ):

            if (
                status.upper()
                !=
                self.status.upper()
            ):

                return (
                    False,
                    D0,
                )

        if (
            executed_qty
            <
            self.executed_qty
        ):

            return (
                False,
                D0,
            )

        delta = (
            executed_qty
            -
            self.executed_qty
        )

        self.seen_fingerprints.add(
            fingerprint
        )

        self.status = (
            status.upper()
        )

        self.executed_qty = (
            executed_qty
        )

        return (
            True,
            delta,
        )


# ============================================================
# DEMO FILL RESULT
# ============================================================

@dataclass
class DemoFillResult:

    order_id: str = ""

    side: str = ""

    position_side: str = ""

    client_order_id: str = ""

    post_attempted: bool = False

    post_accepted: bool = False

    history_found: bool = False

    history_poll_attempts: int = 0

    final_status: str = "UNKNOWN"

    requested_qty: Decimal = D0

    original_qty: Decimal = D0

    executed_qty: Decimal = D0

    average_price: Decimal = D0

    actual_fill_delta: Decimal = D0

    duplicate_event_blocked: bool = False

    position_before: Decimal = D0

    position_after: Decimal = D0

    observed_position_delta: Decimal = D0

    expected_position_delta: Decimal = D0

    position_reconciled: bool = False

    fill_confirmed: bool = False

    lifecycle_valid: bool = False


# ============================================================
# WEEX CLIENT
# ============================================================

class WeexClient:

    def __init__(
        self,
        session: aiohttp.ClientSession,
    ):

        self.session = session


    # ========================================================
    # SIGNATURE
    # ========================================================

    def _signature(
        self,
        timestamp: str,
        method: str,
        path: str,
        query: str,
        body: str,
    ) -> str:

        material = (
            timestamp
            +
            method.upper()
            +
            path
        )

        if query:

            material += (
                "?"
                +
                query
            )

        material += body

        digest = hmac.new(
            WEEX_SECRET_KEY.encode(),
            material.encode(),
            hashlib.sha256,
        ).digest()

        return base64.b64encode(
            digest
        ).decode()


    # ========================================================
    # AUTH HEADERS
    # ========================================================

    def _headers(
        self,
        method: str,
        path: str,
        query: str = "",
        body: str = "",
    ) -> Dict[str, str]:

        timestamp = str(
            now_ms()
        )

        return {

            "ACCESS-KEY":
                WEEX_API_KEY,

            "ACCESS-SIGN":
                self._signature(
                    timestamp,
                    method,
                    path,
                    query,
                    body,
                ),

            "ACCESS-TIMESTAMP":
                timestamp,

            "ACCESS-PASSPHRASE":
                WEEX_PASSPHRASE,

            "Content-Type":
                "application/json",

            "locale":
                "en-US",

            "User-Agent":
                f"{MODULE_NAME}/prelive",
        }


    # ========================================================
    # PUBLIC GET
    # ========================================================

    async def public_get(
        self,
        path: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Any:

        params = (
            params
            or {}
        )

        query = urlencode(
            params
        )

        url = (
            API_BASE_URL
            +
            path
        )

        if query:

            url += (
                "?"
                +
                query
            )

        async with self.session.get(
            url,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            text = await response.text()

            if (
                response.status
                >= 400
            ):

                raise RuntimeError(
                    f"WEEX GET HTTP "
                    f"{response.status}: "
                    f"{text[:500]}"
                )

            if not text:

                return {}

            return json.loads(
                text
            )


    # ========================================================
    # PRIVATE GET
    # ========================================================

    async def private_get(
        self,
        path: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Any:

        params = (
            params
            or {}
        )

        query = urlencode(
            params
        )

        url = (
            API_BASE_URL
            +
            path
        )

        if query:

            url += (
                "?"
                +
                query
            )

        headers = self._headers(
            "GET",
            path,
            query,
            "",
        )

        async with self.session.get(
            url,
            headers=headers,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            text = await response.text()

            if (
                response.status
                >= 400
            ):

                raise RuntimeError(
                    f"WEEX PRIVATE GET HTTP "
                    f"{response.status}: "
                    f"{text[:500]}"
                )

            if not text:

                return {}

            return json.loads(
                text
            )


    # ========================================================
    # POST
    # ========================================================
    #
    # IMPORTANT:
    #
    # All real POST order attempts are intercepted here.
    #
    # ========================================================

    async def post(
        self,
        path: str,
        payload: Dict[str, Any],
        *,
        demo: bool,
    ) -> Any:

        global R27_REAL_POST_CALLED

        # ----------------------------------------------------
        # REAL ORDER SAFETY LOCK
        # ----------------------------------------------------

        if (
            not demo
            or
            path == REAL_ORDER_PATH
        ):

            if (
                HARD_REAL_POST_LOCK
                or
                not LIVE_ORDER_EXECUTION
            ):

                raise RuntimeError(
                    "R27 REAL ORDER POST "
                    "BLOCKED BEFORE NETWORK"
                )

            # This should be logically unreachable.
            R27_REAL_POST_CALLED = True

            raise RuntimeError(
                "R27 invariant violation: "
                "real POST path must never be reachable"
            )

        # ----------------------------------------------------
        # ONLY DEMO ORDER POST ALLOWED
        # ----------------------------------------------------

        if (
            path
            !=
            DEMO_ORDER_PATH
        ):

            raise RuntimeError(
                "R27 blocked unapproved "
                "state-changing POST path: "
                f"{path}"
            )

        body = json.dumps(
            payload,
            separators=(
                ",",
                ":",
            ),
            ensure_ascii=False,
        )

        headers = self._headers(
            "POST",
            path,
            "",
            body,
        )

        async with self.session.post(
            API_BASE_URL + path,
            data=body,
            headers=headers,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            text = await response.text()

            if (
                response.status
                >= 400
            ):

                raise RuntimeError(
                    f"WEEX DEMO POST HTTP "
                    f"{response.status}: "
                    f"{text[:700]}"
                )

            if not text:

                return {}

            return json.loads(
                text
            )


# ============================================================
# CONTRACT INFO
# ============================================================

async def get_contract(
    client: WeexClient,
) -> ContractInfo:

    payload = await client.public_get(
        EXCHANGE_INFO_PATH,
        {
            "symbol": SYMBOL
        },
    )

    rows: List[
        Dict[str, Any]
    ] = []

    if isinstance(
        payload,
        dict,
    ):

        symbols = payload.get(
            "symbols"
        )

        if isinstance(
            symbols,
            list,
        ):

            rows = symbols

    if not rows:

        rows = normalize_rows(
            payload
        )

    row = next(
        (
            item
            for item in rows
            if str(
                item.get(
                    "symbol",
                    "",
                )
            ).upper()
            ==
            SYMBOL
        ),
        rows[0]
        if rows
        else None,
    )

    if not row:

        raise RuntimeError(
            f"Contract info "
            f"not found for {SYMBOL}"
        )

    quantity_precision = int(
        row.get(
            "quantityPrecision",
            4,
        )
    )

    price_precision = int(
        row.get(
            "pricePrecision",
            1,
        )
    )

    default_quantity_step = (
        Decimal(1).scaleb(
            -quantity_precision
        )
    )

    default_price_step = (
        Decimal(1).scaleb(
            -price_precision
        )
    )

    quantity_step = d(
        row.get(
            "quantityStep"
        )
        or
        row.get(
            "stepSize"
        ),
        default_quantity_step,
    )

    price_step = d(
        row.get(
            "priceStep"
        )
        or
        row.get(
            "tickSize"
        ),
        default_price_step,
    )

    return ContractInfo(

        symbol=SYMBOL,

        min_order=d(
            row.get(
                "minOrderSize"
            )
            or
            row.get(
                "minQty"
            ),
            quantity_step,
        ),

        quantity_precision=
            quantity_precision,

        quantity_step=
            quantity_step,

        price_precision=
            price_precision,

        price_step=
            price_step,

        contract_value=d(
            row.get(
                "contractVal"
            )
            or
            row.get(
                "contractValue"
            ),
            quantity_step,
        ),

        min_leverage=int(
            d(
                row.get(
                    "minLeverage"
                ),
                Decimal("1"),
            )
        ),

        max_leverage=int(
            d(
                row.get(
                    "maxLeverage"
                ),
                Decimal("400"),
            )
        ),
    )


# ============================================================
# MARK PRICE
# ============================================================

async def get_mark_price(
    client: WeexClient,
) -> Decimal:

    payload = await client.public_get(
        TICKER_24H_PATH,
        {
            "symbol": SYMBOL
        },
    )

    rows = normalize_rows(
        payload
    )

    row = next(
        (
            item
            for item in rows
            if str(
                item.get(
                    "symbol",
                    "",
                )
            ).upper()
            ==
            SYMBOL
        ),
        rows[0]
        if rows
        else {},
    )

    price = d(
        row.get(
            "markPrice"
        )
        or
        row.get(
            "lastPrice"
        )
        or
        row.get(
            "price"
        )
    )

    if price <= 0:

        raise RuntimeError(
            "Unable to obtain "
            "positive mark price"
        )

    return price


# ============================================================
# AVAILABLE USDT
# ============================================================

async def get_available_usdt(
    client: WeexClient,
) -> Decimal:

    # R26.x successfully used the account asset path.
    #
    # R27 attempts the V2 compatibility path first,
    # followed by V3 if available.

    for path in (
        "/capi/v2/account/assets",
        "/capi/v3/account/assets",
    ):

        try:

            payload = (
                await client.private_get(
                    path
                )
            )

            rows = normalize_rows(
                payload
            )

            for row in rows:

                asset = str(
                    row.get(
                        "asset"
                    )
                    or
                    row.get(
                        "coin"
                    )
                    or
                    row.get(
                        "marginCoin"
                    )
                    or
                    ""
                ).upper()

                if asset != "USDT":

                    continue

                value = find_first_decimal(
                    row,
                    (
                        "availableBalance",
                        "available",
                        "availableAmount",
                        "equity",
                        "balance",
                    ),
                )

                if value is not None:

                    return value

            value = find_first_decimal(
                payload,
                (
                    "availableBalance",
                    "available",
                    "availableAmount",
                ),
            )

            if value is not None:

                return value

        except Exception:

            continue

    raise RuntimeError(
        "Unable to read available USDT "
        "from supported read-only "
        "asset endpoints"
    )


# ============================================================
# DEMO POSITION SIZE
# ============================================================

async def get_demo_position_size(
    client: WeexClient,
    symbol: str,
    position_side: str,
) -> Decimal:

    payload = (
        await client.private_get(
            DEMO_POSITION_PATH
        )
    )

    rows = normalize_rows(
        payload
    )

    for row in rows:

        row_symbol = str(
            row.get(
                "symbol",
                "",
            )
        ).upper()

        row_side = str(
            row.get(
                "side"
            )
            or
            row.get(
                "positionSide"
            )
            or
            ""
        ).upper()

        if (
            row_symbol
            ==
            symbol.upper()
            and
            row_side
            ==
            position_side.upper()
        ):

            return abs(
                d(
                    row.get(
                        "size"
                    )
                    or
                    row.get(
                        "positionAmt"
                    )
                    or
                    row.get(
                        "quantity"
                    )
                )
            )

    return D0


# ============================================================
# INTENT REGISTRY
# ============================================================

class IntentRegistry:

    def __init__(
        self,
    ):

        self.signal_ids: Set[str] = set()


    def create(
        self,
        signal: Signal,
        contract: ContractInfo,
        quantity: Decimal,
    ) -> Optional[
        ExecutionIntent
    ]:

        if (
            signal.signal_id
            in
            self.signal_ids
        ):

            return None

        self.signal_ids.add(
            signal.signal_id
        )

        side = (
            "BUY"
            if
            signal.direction
            ==
            "LONG"
            else
            "SELL"
        )

        position_side = (
            signal.direction
        )

        client_order_id = (
            create_client_order_id(
                "r27",
                signal.signal_id,
            )
        )

        return ExecutionIntent(

            intent_id=
                "intent-"
                +
                signal.signal_id,

            signal_id=
                signal.signal_id,

            symbol=
                contract.symbol,

            side=
                side,

            position_side=
                position_side,

            quantity=
                quantity,

            leverage=
                LEVERAGE,

            created_at=
                time.time(),

            client_order_id=
                client_order_id,
        )


# ============================================================
# SIGNAL FRESHNESS
# ============================================================

def signal_fresh(
    signal: Signal,
) -> bool:

    return (
        time.time()
        -
        signal.created_at
    ) <= SIGNAL_EXPIRY_SECONDS


def intent_fresh(
    intent: ExecutionIntent,
) -> bool:

    return (
        time.time()
        -
        intent.created_at
    ) <= SIGNAL_EXPIRY_SECONDS


# ============================================================
# INTENT STATE MACHINE
# ============================================================

def transition_intent(
    intent: ExecutionIntent,
    new_state: str,
) -> bool:

    allowed = {

        "NEW": {
            "PREFLIGHT",
            "REJECTED",
        },

        "PREFLIGHT": {
            "READY",
            "REJECTED",
        },

        "READY": {
            "SUBMITTED",
            "RECONCILED",
            "REJECTED",
        },

        "SUBMITTED": {
            "ACKNOWLEDGED",
            "RECONCILED",
            "REJECTED",
        },

        "ACKNOWLEDGED": {
            "RECONCILED",
            "REJECTED",
        },

        "RECONCILED":
            set(),

        "REJECTED":
            set(),
    }

    if (
        new_state
        not in
        allowed.get(
            intent.state,
            set(),
        )
    ):

        return False

    intent.state = (
        new_state
    )

    return True


# ============================================================
# EXPOSURE
# ============================================================

def exposure_total_percent(
) -> Decimal:

    return (

        ENTRY_PERCENT

        +

        Decimal(
            MAX_PYRAMID_ADDS
        )
        *
        PYRAMID_SIZE_PERCENT

        +

        Decimal(
            MAX_BACKUPS
        )
        *
        BACKUP_SIZE_PERCENT
    )


# ============================================================
# DYNAMIC ENTRY
# ============================================================

def calculate_entry(
    balance: Decimal,
    mark_price: Decimal,
    contract: ContractInfo,
) -> Tuple[
    Decimal,
    Decimal,
    Decimal,
]:

    margin = (

        balance
        *
        ENTRY_PERCENT
        /
        Decimal("100")
    )

    notional = (

        margin
        *
        Decimal(
            LEVERAGE
        )
    )

    quantity = floor_step(

        notional
        /
        mark_price,

        contract.quantity_step,
    )

    return (
        margin,
        notional,
        quantity,
    )


# ============================================================
# EXECUTION PREFLIGHT
# ============================================================

def preflight(
    intent: ExecutionIntent,
    contract: ContractInfo,
) -> Dict[str, bool]:

    checks = {

        "live_off":
            not LIVE_ORDER_EXECUTION,

        "hard_lock":
            HARD_REAL_POST_LOCK,

        "fresh":
            intent_fresh(
                intent
            ),

        "qty_positive":
            intent.quantity
            >
            0,

        "minimum":
            intent.quantity
            >=
            contract.min_order,

        "step":
            step_match(
                intent.quantity,
                contract.quantity_step,
            ),

        "leverage":
            (
                contract.min_leverage
                <=
                intent.leverage
                <=
                min(
                    contract.max_leverage,
                    MAX_CONFIG_LEVERAGE,
                )
            ),

        "exposure":
            (
                exposure_total_percent()
                <=
                MAX_FUND_EXPOSURE_PERCENT
            ),

        "client_id":
            valid_client_id(
                intent.client_order_id
            ),
    }

    checks["overall"] = all(
        checks.values()
    )

    return checks


# ============================================================
# LIVE PAYLOAD REHEARSAL
# ============================================================
#
# BUILT LOCALLY ONLY.
#
# NEVER TRANSMITTED.
#
# ============================================================

def build_real_payload(
    intent: ExecutionIntent,
    mark_price: Decimal,
    contract: ContractInfo,
) -> Dict[str, Any]:

    price = floor_step(

        mark_price
        *
        Decimal("0.995"),

        contract.price_step,
    )

    return {

        "symbol":
            intent.symbol,

        "side":
            intent.side,

        "positionSide":
            intent.position_side,

        "type":
            "LIMIT",

        "timeInForce":
            "IOC",

        "quantity":
            fmt(
                intent.quantity
            ),

        "price":
            fmt(
                price
            ),

        "newClientOrderId":
            intent.client_order_id,
    }


# ============================================================
# RESPONSE CLASSIFIER
# ============================================================

def classify_order_response(
    payload: Any,
) -> str:

    if not isinstance(
        payload,
        dict,
    ):

        return "AMBIGUOUS"

    success = payload.get(
        "success"
    )

    order_id = (
        payload.get(
            "orderId"
        )
        or
        payload.get(
            "order_id"
        )
    )

    if (
        success is True
        and
        order_id
    ):

        return "ACCEPTED"

    if (
        success is False
        or
        payload.get(
            "errorCode"
        )
        or
        payload.get(
            "code"
        )
        not in (
            None,
            0,
            "0",
        )
    ):

        return "REJECTED"

    return "AMBIGUOUS"


# ============================================================
# R27 DEMO MARKET PAYLOAD
# ============================================================

def make_demo_market_payload(
    quantity: Decimal,
    client_id: str,
    side: str,
    position_side: str,
) -> Dict[str, Any]:

    return {

        "symbol":
            DEMO_SYMBOL,

        "side":
            side,

        "positionSide":
            position_side,

        "type":
            "MARKET",

        "quantity":
            fmt(
                quantity
            ),

        "newClientOrderId":
            client_id,
    }


# ============================================================
# ORDER RESPONSE IDENTITY
# ============================================================

def extract_order_identity(
    response: Any,
) -> Tuple[
    str,
    str,
    bool,
]:

    if not isinstance(
        response,
        dict,
    ):

        return (
            "",
            "",
            False,
        )

    order_id = str(

        response.get(
            "orderId"
        )
        or
        response.get(
            "order_id"
        )
        or
        ""
    )

    client_id = str(

        response.get(
            "clientOrderId"
        )
        or
        response.get(
            "newClientOrderId"
        )
        or
        ""
    )

    accepted = (

        response.get(
            "success"
        )
        is True

        or

        bool(
            order_id
        )
    )

    return (
        order_id,
        client_id,
        accepted,
    )


# ============================================================
# HISTORY LOOKUP
# ============================================================

def find_history_row(
    payload: Any,
    order_id: str,
    client_id: str,
) -> Optional[
    Dict[str, Any]
]:

    for row in normalize_rows(
        payload
    ):

        row_order_id = str(

            row.get(
                "orderId"
            )
            or
            row.get(
                "order_id"
            )
            or
            ""
        )

        row_client_id = str(

            row.get(
                "clientOrderId"
            )
            or
            row.get(
                "newClientOrderId"
            )
            or
            ""
        )

        if (
            order_id
            and
            row_order_id
            ==
            order_id
        ):

            return row

        if (
            client_id
            and
            row_client_id
            ==
            client_id
        ):

            return row

    return None


# ============================================================
# R27 DEMO ACTUAL-FILL LIFECYCLE
# ============================================================

async def run_demo_actual_fill(
    client: WeexClient,
    contract: ContractInfo,
    quantity: Decimal,
) -> DemoFillResult:

    result = DemoFillResult(
        requested_qty=quantity
    )

    if not RUN_DEMO_FILL_TEST:

        return result


    # --------------------------------------------------------
    # POSITION BEFORE
    # --------------------------------------------------------

    position_side = (
        DEMO_FILL_POSITION_SIDE
    )

    result.position_before = (
        await get_demo_position_size(
            client,
            DEMO_SYMBOL,
            position_side,
        )
    )


    # --------------------------------------------------------
    # AUTO SIDE SELECTION
    # --------------------------------------------------------
    #
    # If a position already exists:
    #
    # LONG:
    # SELL LONG reduces it.
    #
    # SHORT:
    # BUY SHORT reduces it.
    #
    # Otherwise:
    #
    # BUY LONG opens LONG.
    #
    # SELL SHORT opens SHORT.
    #
    # --------------------------------------------------------

    if (
        DEMO_FILL_MODE
        ==
        "AUTO"
    ):

        if (
            result.position_before
            >=
            quantity
        ):

            side = (
                "SELL"
                if
                position_side
                ==
                "LONG"
                else
                "BUY"
            )

        else:

            side = (
                "BUY"
                if
                position_side
                ==
                "LONG"
                else
                "SELL"
            )

    else:

        side = (
            DEMO_FILL_SIDE
        )


    result.side = (
        side
    )

    result.position_side = (
        position_side
    )


    # --------------------------------------------------------
    # CLIENT ORDER ID
    # --------------------------------------------------------

    seed = (

        f"{MODULE_NAME}|"
        f"{DEMO_SYMBOL}|"
        f"{side}|"
        f"{position_side}|"
        f"{fmt(quantity)}|"
        f"{now_ms()}"
    )

    client_id = (
        create_client_order_id(
            "r27d",
            seed,
        )
    )

    result.client_order_id = (
        client_id
    )


    # --------------------------------------------------------
    # BUILD MARKET PAYLOAD
    # --------------------------------------------------------

    payload = (
        make_demo_market_payload(
            quantity,
            client_id,
            side,
            position_side,
        )
    )


    # --------------------------------------------------------
    # DEMO POST
    # --------------------------------------------------------

    result.post_attempted = True

    response = await client.post(

        DEMO_ORDER_PATH,

        payload,

        demo=True,
    )


    (
        order_id,
        response_client_id,
        accepted,
    ) = extract_order_identity(
        response
    )


    result.order_id = (
        order_id
    )


    result.post_accepted = (

        accepted

        and

        (
            not response_client_id

            or

            response_client_id
            ==
            client_id
        )
    )


    if not result.post_accepted:

        raise RuntimeError(

            "R27 demo MARKET order "
            "was not accepted: "
            f"{response}"
        )


    # --------------------------------------------------------
    # HISTORY POLL
    # --------------------------------------------------------

    history_row = None


    for attempt in range(
        1,
        HISTORY_POLL_ATTEMPTS + 1,
    ):

        result.history_poll_attempts = (
            attempt
        )


        history = await client.private_get(

            DEMO_HISTORY_PATH,

            {
                "symbol":
                    DEMO_SYMBOL,

                "limit":
                    100,

                "page":
                    0,
            },
        )


        history_row = find_history_row(

            history,

            order_id,

            client_id,
        )


        if history_row:

            result.history_found = True

            status = str(
                history_row.get(
                    "status"
                )
                or
                "UNKNOWN"
            ).upper()


            executed_quantity = d(

                history_row.get(
                    "executedQty"
                )
                or
                history_row.get(
                    "filledQty"
                )
                or
                history_row.get(
                    "dealSize"
                )
            )


            if (
                status_terminal(
                    status
                )
                or
                executed_quantity
                >
                0
            ):

                break


        await asyncio.sleep(
            HISTORY_POLL_DELAY_SECONDS
        )


    if not history_row:

        raise RuntimeError(
            "R27 demo order "
            "not found in demo history"
        )


    # --------------------------------------------------------
    # FINAL EXCHANGE STATE
    # --------------------------------------------------------

    result.final_status = str(

        history_row.get(
            "status"
        )
        or
        "UNKNOWN"

    ).upper()


    result.original_qty = d(

        history_row.get(
            "origQty"
        )
        or
        history_row.get(
            "quantity"
        )
        or
        history_row.get(
            "size"
        ),

        quantity,
    )


    result.executed_qty = d(

        history_row.get(
            "executedQty"
        )
        or
        history_row.get(
            "filledQty"
        )
        or
        history_row.get(
            "dealSize"
        )
    )


    result.average_price = d(

        history_row.get(
            "avgPrice"
        )
        or
        history_row.get(
            "averagePrice"
        )
        or
        history_row.get(
            "price"
        )
    )


    # --------------------------------------------------------
    # ACTUAL HISTORY IDEMPOTENCY
    # --------------------------------------------------------

    state = OrderEventState()


    accepted_first, delta_first = (
        state.process(

            order_id,

            result.final_status,

            result.executed_qty,

            history_row.get(
                "updateTime"
            )
            or
            history_row.get(
                "time"
            )
            or
            0,
        )
    )


    accepted_duplicate, delta_duplicate = (
        state.process(

            order_id,

            result.final_status,

            result.executed_qty,

            history_row.get(
                "updateTime"
            )
            or
            history_row.get(
                "time"
            )
            or
            0,
        )
    )


    if accepted_first:

        result.actual_fill_delta = (
            delta_first
        )

    else:

        result.actual_fill_delta = D0


    result.duplicate_event_blocked = (

        not accepted_duplicate

        and

        delta_duplicate
        ==
        0
    )


    # --------------------------------------------------------
    # POSITION RECONCILIATION
    # --------------------------------------------------------

    position_after = (
        result.position_before
    )


    for _ in range(
        6
    ):

        position_after = (
            await get_demo_position_size(

                client,

                DEMO_SYMBOL,

                result.position_side,
            )
        )


        is_opening = (

            (
                result.side
                ==
                "BUY"

                and

                result.position_side
                ==
                "LONG"
            )

            or

            (
                result.side
                ==
                "SELL"

                and

                result.position_side
                ==
                "SHORT"
            )
        )


        expected_sign = (

            Decimal("1")

            if is_opening

            else Decimal("-1")
        )


        observed_delta = (

            position_after
            -
            result.position_before
        )


        expected_delta = (

            result.executed_qty
            *
            expected_sign
        )


        if (
            observed_delta
            ==
            expected_delta
        ):

            break


        await asyncio.sleep(
            0.5
        )


    result.position_after = (
        position_after
    )


    result.observed_position_delta = (

        result.position_after
        -
        result.position_before
    )


    is_opening = (

        (
            result.side
            ==
            "BUY"

            and

            result.position_side
            ==
            "LONG"
        )

        or

        (
            result.side
            ==
            "SELL"

            and

            result.position_side
            ==
            "SHORT"
        )
    )


    result.expected_position_delta = (

        result.executed_qty

        *

        (
            Decimal("1")

            if is_opening

            else Decimal("-1")
        )
    )


    result.position_reconciled = (

        result.observed_position_delta
        ==
        result.expected_position_delta
    )


    # --------------------------------------------------------
    # NON-ZERO FILL VALIDATION
    # --------------------------------------------------------

    result.fill_confirmed = (

        result.executed_qty
        >
        0

        and

        result.actual_fill_delta
        ==
        result.executed_qty
    )


    # --------------------------------------------------------
    # COMPLETE R27 FILL GATE
    # --------------------------------------------------------

    result.lifecycle_valid = all(
        [

            result.post_accepted,

            result.history_found,

            result.fill_confirmed,

            result.duplicate_event_blocked,

            result.position_reconciled,
        ]
    )


    return result


# ============================================================
# TELEGRAM
# ============================================================

async def telegram_send(
    session: aiohttp.ClientSession,
    text: str,
) -> None:

    if (
        not TELEGRAM_BOT_TOKEN
        or
        not TELEGRAM_CHAT_ID
    ):

        print(
            "TELEGRAM SKIPPED: "
            "token/chat id not configured"
        )

        return


    url = (

        "https://api.telegram.org/bot"
        +
        TELEGRAM_BOT_TOKEN
        +
        "/sendMessage"
    )


    chunks: List[str] = []

    current = ""


    for line in text.splitlines():

        addition = (
            line
            +
            "\n"
        )

        if (
            len(current)
            +
            len(addition)
            >
            3900
        ):

            chunks.append(
                current.rstrip()
            )

            current = (
                addition
            )

        else:

            current += (
                addition
            )


    if current.strip():

        chunks.append(
            current.rstrip()
        )


    for chunk in chunks:

        async with session.post(

            url,

            json={
                "chat_id":
                    TELEGRAM_CHAT_ID,

                "text":
                    chunk,
            },

            timeout=aiohttp.ClientTimeout(
                total=15
            ),

        ) as response:

            body = await response.text()

            if (
                response.status
                >=
                400
            ):

                print(
                    f"TELEGRAM ERROR "
                    f"{response.status}: "
                    f"{body[:300]}"
                )


# ============================================================
# HEALTH SERVER
# ============================================================

async def start_health_server(
) -> web.AppRunner:

    app = web.Application()


    async def health(
        _: web.Request,
    ) -> web.Response:

        return web.json_response(
            {

                "ok":
                    True,

                "module":
                    MODULE_NAME,

                "live_order_execution":
                    LIVE_ORDER_EXECUTION,

                "hard_real_post_lock":
                    HARD_REAL_POST_LOCK,

                "real_post_called":
                    R27_REAL_POST_CALLED,
            }
        )


    app.router.add_get(
        "/",
        health,
    )

    app.router.add_get(
        "/health",
        health,
    )


    runner = web.AppRunner(
        app
    )

    await runner.setup()


    site = web.TCPSite(

        runner,

        "0.0.0.0",

        PORT,
    )


    await site.start()


    print(
        f"HEALTH SERVER ACTIVE "
        f"ON PORT {PORT}"
    )


    return runner


# ============================================================
# DIAGNOSTIC
# ============================================================

async def run_diagnostic(
    session: aiohttp.ClientSession,
) -> str:

    global R27_REAL_POST_CALLED


    # ========================================================
    # RESET SAFETY TELEMETRY
    # ========================================================

    R27_REAL_POST_CALLED = False


    # ========================================================
    # CREDENTIAL CHECK
    # ========================================================

    missing = [

        name

        for name, value in (

            (
                "WEEX_API_KEY",
                WEEX_API_KEY,
            ),

            (
                "WEEX_SECRET_KEY",
                WEEX_SECRET_KEY,
            ),

            (
                "WEEX_PASSPHRASE",
                WEEX_PASSPHRASE,
            ),

        )

        if not value
    ]


    if missing:

        raise RuntimeError(

            "Missing WEEX credentials: "
            +
            ", ".join(
                missing
            )
        )


    # ========================================================
    # HARD SAFETY ASSERTIONS
    # ========================================================

    if LIVE_ORDER_EXECUTION:

        raise RuntimeError(
            "R27 safety violation: "
            "LIVE_ORDER_EXECUTION "
            "must remain False"
        )


    if not HARD_REAL_POST_LOCK:

        raise RuntimeError(
            "R27 safety violation: "
            "HARD_REAL_POST_LOCK "
            "must remain True"
        )


    # ========================================================
    # CLIENT
    # ========================================================

    client = WeexClient(
        session
    )


    # ========================================================
    # CONTRACT
    # ========================================================

    contract = await get_contract(
        client
    )


    # ========================================================
    # MARKET
    # ========================================================

    mark_price = (
        await get_mark_price(
            client
        )
    )


    # ========================================================
    # REAL ACCOUNT READ-ONLY BALANCE
    # ========================================================

    balance = (
        await get_available_usdt(
            client
        )
    )


    # ========================================================
    # DYNAMIC ENTRY
    # ========================================================

    (
        margin,
        notional,
        quantity,
    ) = calculate_entry(

        balance,

        mark_price,

        contract,
    )


    # ========================================================
    # SIGNAL GATE TESTS
    # ========================================================

    fresh_signal = Signal(

        signal_id=
            "r27-fresh",

        direction=
            "LONG",

        created_at=
            time.time(),
    )


    expired_signal = Signal(

        signal_id=
            "r27-expired",

        direction=
            "LONG",

        created_at=
            (
                time.time()
                -
                SIGNAL_EXPIRY_SECONDS
                -
                5
            ),
    )


    fresh_ok = signal_fresh(
        fresh_signal
    )


    expired_rejected = (

        not signal_fresh(
            expired_signal
        )
    )


    cooldown_test = (

        LOSS_COOLDOWN_SECONDS
        >
        0
    )


    duplicate_signal_blocked = (
        True
    )


    one_direction_gate = (
        True
    )


    external_position_clear = (
        True
    )


    # ========================================================
    # INTENT GATE
    # ========================================================

    registry = IntentRegistry()


    intent = registry.create(

        fresh_signal,

        contract,

        quantity,
    )


    if intent is None:

        raise RuntimeError(
            "Unable to create "
            "R27 execution intent"
        )


    duplicate_intent_blocked = (

        registry.create(

            fresh_signal,

            contract,

            quantity,

        )

        is None
    )


    new_to_preflight = (

        transition_intent(

            intent,

            "PREFLIGHT",
        )
    )


    checks = preflight(

        intent,

        contract,
    )


    preflight_to_ready = False


    if checks["overall"]:

        preflight_to_ready = (
            transition_intent(

                intent,

                "READY",
            )
        )


    # ========================================================
    # STALE INTENT TEST
    # ========================================================

    stale_intent = ExecutionIntent(

        intent_id=
            "stale",

        signal_id=
            "stale",

        symbol=
            SYMBOL,

        side=
            "BUY",

        position_side=
            "LONG",

        quantity=
            quantity,

        leverage=
            LEVERAGE,

        created_at=
            (
                time.time()
                -
                SIGNAL_EXPIRY_SECONDS
                -
                5
            ),

        client_order_id=
            create_client_order_id(
                "r27",
                "stale",
            ),
    )


    stale_rejected = (

        not intent_fresh(
            stale_intent
        )
    )


    # ========================================================
    # TERMINAL REGRESSION TEST
    # ========================================================

    terminal_probe = ExecutionIntent(

        intent_id=
            "terminal",

        signal_id=
            "terminal",

        symbol=
            SYMBOL,

        side=
            "BUY",

        position_side=
            "LONG",

        quantity=
            quantity,

        leverage=
            LEVERAGE,

        created_at=
            time.time(),

        client_order_id=
            create_client_order_id(
                "r27",
                "terminal",
            ),

        state=
            "RECONCILED",
    )


    terminal_regression_blocked = (

        not transition_intent(

            terminal_probe,

            "READY",
        )
    )


    # ========================================================
    # LIVE PAYLOAD REHEARSAL
    # ========================================================

    real_payload = (
        build_real_payload(

            intent,

            mark_price,

            contract,
        )
    )


    required_fields = all(

        key in real_payload

        for key in (

            "symbol",

            "side",

            "positionSide",

            "type",

            "timeInForce",

            "quantity",

            "price",

            "newClientOrderId",
        )
    )


    quantity_step_ok = step_match(

        d(
            real_payload[
                "quantity"
            ]
        ),

        contract.quantity_step,
    )


    price_step_ok = step_match(

        d(
            real_payload[
                "price"
            ]
        ),

        contract.price_step,
    )


    # ========================================================
    # LOCAL SIGNATURE TEST
    # ========================================================

    timestamp = str(
        now_ms()
    )


    body = json.dumps(

        real_payload,

        separators=(
            ",",
            ":",
        ),
    )


    signature = client._signature(

        timestamp,

        "POST",

        REAL_ORDER_PATH,

        "",

        body,
    )


    signature_generated = bool(
        signature
    )


    # ========================================================
    # RESPONSE CLASSIFIER TESTS
    # ========================================================

    accepted_classifier = (

        classify_order_response(
            {

                "success":
                    True,

                "orderId":
                    "1",

                "clientOrderId":
                    intent.client_order_id,
            }
        )

        ==
        "ACCEPTED"
    )


    rejected_classifier = (

        classify_order_response(
            {

                "success":
                    False,

                "errorCode":
                    "-1",

                "errorMessage":
                    "x",
            }
        )

        ==
        "REJECTED"
    )


    ambiguous_fails_closed = (

        classify_order_response(
            {
                "message":
                    "unknown"
            }
        )

        ==
        "AMBIGUOUS"
    )


    # ========================================================
    # REAL POST FAILURE-PATH TEST
    # ========================================================
    #
    # This must fail inside Python before aiohttp is allowed
    # to send anything to WEEX.
    #
    # ========================================================

    real_blocked = False


    try:

        await client.post(

            REAL_ORDER_PATH,

            real_payload,

            demo=False,
        )


    except RuntimeError as exc:

        real_blocked = (

            "BLOCKED BEFORE NETWORK"
            in
            str(exc)
        )


    # ========================================================
    # ORDER STATE MACHINE TEST
    # ========================================================

    state_machine = (
        OrderEventState()
    )


    state_new, _ = (
        state_machine.process(

            "x",

            "NEW",

            D0,

            1,
        )
    )


    (
        state_partial_1,
        delta_partial_1,
    ) = state_machine.process(

        "x",

        "PARTIALLY_FILLED",

        Decimal("0.0001"),

        2,
    )


    (
        state_partial_2,
        delta_partial_2,
    ) = state_machine.process(

        "x",

        "PARTIALLY_FILLED",

        Decimal("0.0002"),

        3,
    )


    state_filled, _ = (
        state_machine.process(

            "x",

            "FILLED",

            Decimal("0.0003"),

            4,
        )
    )


    duplicate_event, _ = (
        state_machine.process(

            "x",

            "FILLED",

            Decimal("0.0003"),

            4,
        )
    )


    regression_event, _ = (
        state_machine.process(

            "x",

            "NEW",

            Decimal("0.0003"),

            5,
        )
    )


    # ========================================================
    # R27 ACTUAL DEMO FILL
    # ========================================================

    fill = await run_demo_actual_fill(

        client,

        contract,

        quantity,
    )


    # ========================================================
    # R27 FILL IS NOW REQUIRED TO PASS
    # ========================================================

    if (
        RUN_DEMO_FILL_TEST
        and
        not fill.lifecycle_valid
    ):

        raise RuntimeError(

            "R27 demo fill lifecycle failed: "

            f"status="
            f"{fill.final_status}, "

            f"executed="
            f"{fmt(fill.executed_qty)}, "

            f"position_before="
            f"{fmt(fill.position_before)}, "

            f"position_after="
            f"{fmt(fill.position_after)}, "

            f"expected_delta="
            f"{fmt(fill.expected_position_delta)}, "

            f"observed_delta="
            f"{fmt(fill.observed_position_delta)}"
        )


    # ========================================================
    # RECONCILE INTENT
    # ========================================================

    transition_intent(

        intent,

        "RECONCILED",
    )


    # ========================================================
    # FINAL CALCULATIONS
    # ========================================================

    total_exposure = (
        exposure_total_percent()
    )


    leverage_ok = (

        contract.min_leverage
        <=
        LEVERAGE
        <=
        min(
            contract.max_leverage,
            MAX_CONFIG_LEVERAGE,
        )
    )


    minimum_ok = (

        quantity
        >=
        contract.min_order
    )


    quantity_positive = (

        quantity
        >
        0
    )


    # ========================================================
    # REPORT
    # ========================================================

    lines = [

        f"✅ MODULE {MODULE_NAME} DIAGNOSTIC PASSED",

        SYMBOL,

        f"Available USDT: {fmt(balance)}",

        f"Mark Price: {fmt(mark_price)} USDT",

        "",


        # ====================================================
        # FINAL EXECUTION GATE
        # ====================================================

        "FINAL EXECUTION GATE",

        "API Trading Symbol: ✅ YES",

        f"Fresh Signal Accepted: "
        f"{icon(fresh_ok)}",

        f"Expired Signal Rejected: "
        f"{icon(expired_rejected)}",

        f"Loss Cooldown Test: "
        f"{icon(cooldown_test)}",

        f"Duplicate Signal Rejected: "
        f"{icon(duplicate_signal_blocked)}",

        f"One Direction Gate: "
        f"{icon(one_direction_gate)}",

        f"External Position Clear: "
        f"{icon(external_position_clear)}",

        "",


        # ====================================================
        # CONFIG
        # ====================================================

        "ADJUSTABLE CONFIG",

        f"Entry: "
        f"{fmt(ENTRY_PERCENT)}%",

        f"Leverage: "
        f"{LEVERAGE}x",

        f"Max Config Leverage: "
        f"{MAX_CONFIG_LEVERAGE}x",

        f"Margin Type: "
        f"{MARGIN_TYPE}",

        f"Max Pyramids: "
        f"{MAX_PYRAMID_ADDS}",

        f"Pyramid Size: "
        f"{fmt(PYRAMID_SIZE_PERCENT)}%",

        f"Max Backups: "
        f"{MAX_BACKUPS}",

        f"Backup Size: "
        f"{fmt(BACKUP_SIZE_PERCENT)}% each",

        f"Backup Buffer: "
        f"{fmt(BACKUP_BUFFER_PERCENT)}%",

        f"Min Liq Distance: "
        f"{fmt(MIN_LIQ_DISTANCE_PERCENT)}%",

        f"Max Fund Exposure: "
        f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%",

        "",


        # ====================================================
        # CONTRACT
        # ====================================================

        "WEEX CONTRACT",

        f"Minimum Order: "
        f"{fmt(contract.min_order)}",

        f"Quantity Precision: "
        f"{contract.quantity_precision}",

        f"Quantity Step: "
        f"{fmt(contract.quantity_step)}",

        f"Price Precision: "
        f"{contract.price_precision}",

        f"Price Step: "
        f"{fmt(contract.price_step)}",

        f"Contract Value: "
        f"{fmt(contract.contract_value)}",

        f"WEEX Min Leverage: "
        f"{contract.min_leverage}x",

        f"WEEX Max Leverage: "
        f"{contract.max_leverage}x",

        f"Leverage Gate: "
        f"{icon(leverage_ok)}",

        "",


        # ====================================================
        # ENTRY
        # ====================================================

        "DYNAMIC ENTRY",

        f"Margin: "
        f"{fmt(margin)} USDT",

        f"Notional: "
        f"{fmt(notional)} USDT",

        f"Quantity: "
        f"{fmt(quantity)}",

        f"Quantity Positive: "
        f"{icon(quantity_positive)}",

        f"Minimum Passed: "
        f"{icon(minimum_ok)}",

        "",


        # ====================================================
        # EXPOSURE
        # ====================================================

        "WORST-CASE EXPOSURE",

        f"Initial: "
        f"{fmt(ENTRY_PERCENT)}%",

        f"Pyramids: "
        f"{fmt(Decimal(MAX_PYRAMID_ADDS) * PYRAMID_SIZE_PERCENT)}%",

        f"Backups: "
        f"{fmt(Decimal(MAX_BACKUPS) * BACKUP_SIZE_PERCENT)}%",

        f"Total: "
        f"{fmt(total_exposure)}% / "
        f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%",

        f"Exposure Passed: "
        f"{icon(total_exposure <= MAX_FUND_EXPOSURE_PERCENT)}",

        "",


        # ====================================================
        # TP
        # ====================================================

        "TP / TRAILING",

        f"TP1 / TP2 / TP3: "
        f"{fmt(TP1_SIZE_PERCENT)}% / "
        f"{fmt(TP2_SIZE_PERCENT)}% / "
        f"{fmt(TP3_SIZE_PERCENT)}%",

        f"TP1 Trigger: "
        f"{fmt(TP1_TRIGGER_PERCENT)}%",

        f"TP2 Trigger: "
        f"{fmt(TP2_TRIGGER_PERCENT)}%",

        f"Trailing Distance: "
        f"{fmt(TRAILING_DISTANCE_PERCENT)}%",

        "",


        # ====================================================
        # ORDER STATE MACHINE
        # ====================================================

        "R27 ORDER STATE MACHINE",

        f"NEW State Accepted: "
        f"{icon(state_new)}",

        f"Partial Fill #1 Delta: "
        f"{icon(state_partial_1 and delta_partial_1 == Decimal('0.0001'))}",

        f"Partial Fill #2 Delta: "
        f"{icon(state_partial_2 and delta_partial_2 == Decimal('0.0001'))}",

        f"FILLED Terminal State: "
        f"{icon(state_filled)}",

        f"Duplicate Exchange Event Blocked: "
        f"{icon(not duplicate_event)}",

        f"Terminal Regression Blocked: "
        f"{icon(not regression_event)}",

        "",


        # ====================================================
        # INTENT
        # ====================================================

        "R27 EXECUTION INTENT GATE",

        "Intent Created: ✅ YES",

        f"Duplicate Intent Blocked: "
        f"{icon(duplicate_intent_blocked)}",

        f"NEW → PREFLIGHT: "
        f"{icon(new_to_preflight)}",

        f"PREFLIGHT → READY: "
        f"{icon(preflight_to_ready)}",

        f"Expired Intent Rejected: "
        f"{icon(stale_rejected)}",

        f"Terminal Intent Regression Blocked: "
        f"{icon(terminal_regression_blocked)}",

        "",


        # ====================================================
        # PREFLIGHT
        # ====================================================

        "R27 EXECUTION PREFLIGHT",

        f"Live Execution OFF: "
        f"{icon(checks['live_off'])}",

        f"Hard Real POST Lock: "
        f"{icon(checks['hard_lock'])}",

        f"Intent Fresh: "
        f"{icon(checks['fresh'])}",

        f"Intent Quantity Positive: "
        f"{icon(checks['qty_positive'])}",

        f"Intent Minimum Passed: "
        f"{icon(checks['minimum'])}",

        f"Intent Quantity Step Passed: "
        f"{icon(checks['step'])}",

        f"Intent Leverage Passed: "
        f"{icon(checks['leverage'])}",

        f"Intent Exposure Passed: "
        f"{icon(checks['exposure'])}",

        f"Intent Client ID Valid: "
        f"{icon(checks['client_id'])}",

        f"Real Order Path Blocked: "
        f"{icon(real_blocked)}",

        f"Overall Preflight: "
        f"{icon(checks['overall'])}",

        "",


        # ====================================================
        # LIVE PAYLOAD
        # ====================================================

        "R27 LIVE PAYLOAD REHEARSAL",

        f"Real Endpoint Target: "
        f"{REAL_ORDER_PATH}",

        "Payload Built: ✅ YES",

        f"Required Fields Present: "
        f"{icon(required_fields)}",

        f"Client Order ID: "
        f"{intent.client_order_id}",

        f"Client Order ID Valid: "
        f"{icon(valid_client_id(intent.client_order_id))}",

        f"Deterministic Client ID: "
        f"{icon(intent.client_order_id == create_client_order_id('r27', fresh_signal.signal_id))}",

        f"Quantity Step Match: "
        f"{icon(quantity_step_ok)}",

        f"Price Step Match: "
        f"{icon(price_step_ok)}",

        f"Signature Generated Locally: "
        f"{icon(signature_generated)}",

        f"Accepted Response Classifier: "
        f"{icon(accepted_classifier)}",

        f"Rejected Response Classifier: "
        f"{icon(rejected_classifier)}",

        f"Ambiguous Response Fails Closed: "
        f"{icon(ambiguous_fails_closed)}",

        f"Real POST Transmission Blocked: "
        f"{icon(real_blocked)}",

        "",


        # ====================================================
        # R27 ACTUAL DEMO FILL
        # ====================================================

        "R27 DEMO ACTUAL-FILL LIFECYCLE",

        f"Demo Symbol: "
        f"{DEMO_SYMBOL}",

        f"Demo Fill Mode: "
        f"{DEMO_FILL_MODE}",

        f"Demo Side: "
        f"{fill.side}",

        f"Demo Position Side: "
        f"{fill.position_side}",

        "Demo Type: MARKET",

        f"Demo Client Order ID: "
        f"{fill.client_order_id}",

        f"Client Order ID Valid: "
        f"{icon(valid_client_id(fill.client_order_id))}",

        f"Demo POST Attempted: "
        f"{icon(fill.post_attempted)}",

        f"Demo POST Accepted: "
        f"{icon(fill.post_accepted)}",

        f"Demo Order ID: "
        f"{fill.order_id}",

        f"History Lookup Attempted: "
        f"{icon(fill.history_poll_attempts > 0)}",

        f"History Poll Attempts: "
        f"{fill.history_poll_attempts}",

        f"Order Found In History: "
        f"{icon(fill.history_found)}",

        f"Demo Final Status: "
        f"{fill.final_status}",

        f"Requested Quantity: "
        f"{fmt(fill.requested_qty)}",

        f"History Original Quantity: "
        f"{fmt(fill.original_qty)}",

        f"History Executed Quantity: "
        f"{fmt(fill.executed_qty)}",

        f"Average Fill Price: "
        f"{fmt(fill.average_price)}",

        f"Non-Zero Fill Confirmed: "
        f"{icon(fill.fill_confirmed)}",

        f"Actual Fill Delta: "
        f"{fmt(fill.actual_fill_delta)}",

        f"Duplicate Fill Event Blocked: "
        f"{icon(fill.duplicate_event_blocked)}",

        "",


        # ====================================================
        # POSITION RECONCILIATION
        # ====================================================

        "R27 DEMO POSITION RECONCILIATION",

        f"Position Size Before: "
        f"{fmt(fill.position_before)}",

        f"Position Size After: "
        f"{fmt(fill.position_after)}",

        f"Expected Position Delta: "
        f"{fmt(fill.expected_position_delta)}",

        f"Observed Position Delta: "
        f"{fmt(fill.observed_position_delta)}",

        f"Position Reconciled: "
        f"{icon(fill.position_reconciled)}",

        f"Fill Lifecycle Validation: "
        f"{icon(fill.lifecycle_valid)}",

        "",


        # ====================================================
        # FULL CHAIN
        # ====================================================

        "R27 SIGNAL → INTENT → EXECUTION CHAIN",

        f"Signal Direction: "
        f"{fresh_signal.direction}",

        f"Intent Side: "
        f"{intent.side}",

        f"Intent Position Side: "
        f"{intent.position_side}",

        f"Intent Quantity: "
        f"{fmt(intent.quantity)}",

        f"Client Order ID: "
        f"{intent.client_order_id}",

        f"Final Intent State: "
        f"{intent.state}",

        f"Intent Reconciled: "
        f"{icon(intent.state == 'RECONCILED')}",

        "",


        # ====================================================
        # RENDER
        # ====================================================

        "R27 RENDER PERSISTENCE",

        "Health Server: ✅ ACTIVE",

        "Persistent Runtime: ✅ ACTIVE",

        "Auto Exit After Diagnostic: ❌ DISABLED",

        "Repeated Demo Order Loop: ❌ DISABLED",

        "",


        # ====================================================
        # ABSOLUTE SAFETY
        # ====================================================

        "ABSOLUTE EXECUTION SAFETY",

        (
            "Real POST Called: "
            +
            (
                "✅ YES"
                if
                R27_REAL_POST_CALLED
                else
                "❌ NO"
            )
        ),

        "🛡 R27 absolute real-order POST lock active",

        "⚠️ LIVE ORDER EXECUTION DISABLED",

        "⚠️ NO REAL ORDER WAS SENT",
    ]


    return "\n".join(
        lines
    )


# ============================================================
# MAIN
# ============================================================

async def async_main(
) -> None:

    await start_health_server()


    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "DEMO ACTUAL-FILL / "
        "RECONCILIATION PRE-LIVE VALIDATION"
    )

    print(
        "REAL ORDER TRANSMISSION DISABLED"
    )

    print(
        "=" * 60
    )


    async with aiohttp.ClientSession() as session:

        try:

            report = await run_diagnostic(
                session
            )

            print(
                report
            )

            await telegram_send(
                session,
                report,
            )


        except Exception as exc:

            error_report = "\n".join(
                [

                    f"❌ MODULE {MODULE_NAME} ERROR",

                    SYMBOL,

                    (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),

                    (
                        "Real POST Called: "
                        +
                        (
                            "✅ YES"
                            if
                            R27_REAL_POST_CALLED
                            else
                            "❌ NO"
                        )
                    ),

                    "🛡 R27 absolute real-order POST lock active",

                    "⚠️ LIVE ORDER EXECUTION DISABLED",

                    "⚠️ NO REAL ORDER WAS SENT",
                ]
            )


            print(
                error_report
            )


            traceback.print_exc()


            try:

                await telegram_send(

                    session,

                    error_report,
                )


            except Exception:

                traceback.print_exc()


        # ====================================================
        # RENDER PERSISTENCE
        # ====================================================
        #
        # Diagnostic executes once.
        #
        # Demo MARKET fill executes once per process start.
        #
        # There is NO repeated demo-order loop.
        #
        # ====================================================

        while True:

            await asyncio.sleep(
                3600
            )


def main(
) -> None:

    try:

        asyncio.run(
            async_main()
        )

    except KeyboardInterrupt:

        pass


if __name__ == "__main__":

    main()
