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

MODULE_NAME = "0F-4H-R28"
API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()


def default_demo_symbol(symbol: str) -> str:
    if symbol.endswith("USDT"):
        return symbol[:-4] + "SUSDT"
    return symbol


DEMO_SYMBOL = os.getenv(
    "DEMO_SYMBOL",
    default_demo_symbol(SYMBOL)
).strip().upper()


# ============================================================
# ABSOLUTE EXECUTION SAFETY
# ============================================================
#
# R28 IS STILL PRE-LIVE.
#
# R28 adds a SHADOW EXECUTION COMMIT GATE:
#
# signal
#   -> intent
#   -> preflight
#   -> ready
#   -> shadow commit
#   -> reconcile
#
# The shadow commit proves that the exact live request is ready,
# fingerprinted, idempotent and locally signed.
#
# IT NEVER TRANSMITS A REAL /capi/v3/order POST.
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_REAL_POST_LOCK = True

R28_REAL_POST_CALLED = False

REAL_ORDER_PATH = "/capi/v3/order"

DEMO_ORDER_PATH = "/capi/v3/sim/order"

DEMO_HISTORY_PATH = (
    "/capi/v3/sim/order/history"
)

DEMO_POSITION_PATH = (
    "/capi/v3/sim/position/allPosition"
)

RUN_DEMO_ORDER_TEST = (
    os.getenv(
        "RUN_DEMO_ORDER_TEST",
        "true"
    ).lower()
    == "true"
)

DEMO_FILL_MODE = os.getenv(
    "DEMO_FILL_MODE",
    "AUTO"
).strip().upper()


# ============================================================
# ADJUSTABLE CONFIG
# ============================================================

ENTRY_PERCENT = Decimal(
    os.getenv(
        "ENTRY_PERCENT",
        "5"
    )
)

LEVERAGE = int(
    os.getenv(
        "LEVERAGE",
        "100"
    )
)

MAX_CONFIG_LEVERAGE = int(
    os.getenv(
        "MAX_CONFIG_LEVERAGE",
        "100"
    )
)

MARGIN_TYPE = os.getenv(
    "MARGIN_TYPE",
    "ISOLATED"
).strip().upper()


MAX_PYRAMID_ADDS = int(
    os.getenv(
        "MAX_PYRAMID_ADDS",
        "1"
    )
)

PYRAMID_SIZE_PERCENT = Decimal(
    os.getenv(
        "PYRAMID_SIZE_PERCENT",
        "5"
    )
)


MAX_BACKUPS = int(
    os.getenv(
        "MAX_BACKUPS",
        "3"
    )
)

BACKUP_SIZE_PERCENT = Decimal(
    os.getenv(
        "BACKUP_SIZE_PERCENT",
        "5"
    )
)

BACKUP_BUFFER_PERCENT = Decimal(
    os.getenv(
        "BACKUP_BUFFER_PERCENT",
        "0.3"
    )
)


MIN_LIQ_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "MIN_LIQ_DISTANCE_PERCENT",
        "0.2"
    )
)

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35"
    )
)


TP1_SHARE = Decimal("20")
TP2_SHARE = Decimal("20")
TP3_SHARE = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1")

TRAILING_DISTANCE_PERCENT = Decimal("0.2")


SIGNAL_EXPIRY_SECONDS = int(
    os.getenv(
        "SIGNAL_EXPIRY_SECONDS",
        "120"
    )
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv(
        "LOSS_COOLDOWN_SECONDS",
        "300"
    )
)


ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# ============================================================
# ENVIRONMENT
# ============================================================

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    ""
).strip()

WEEX_SECRET_KEY = os.getenv(
    "WEEX_SECRET_KEY",
    ""
).strip()

WEEX_PASSPHRASE = os.getenv(
    "WEEX_PASSPHRASE",
    ""
).strip()


TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    ""
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    ""
).strip()


PORT = int(
    os.getenv(
        "PORT",
        "10000"
    )
)


# ============================================================
# HELPERS
# ============================================================

D0 = Decimal("0")
D1 = Decimal("1")
D100 = Decimal("100")


def D(
    value: Any,
    default: str = "0",
) -> Decimal:

    try:
        if value is None or value == "":
            return Decimal(default)

        return Decimal(str(value))

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return Decimal(default)


def yesno(value: bool) -> str:

    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


def bool_word(value: bool) -> str:

    return (
        "✅ ACTIVE"
        if value
        else "❌ DISABLED"
    )


def fmt_decimal(
    value: Decimal,
) -> str:

    s = format(value, "f")

    if "." in s:
        s = (
            s.rstrip("0")
            .rstrip(".")
        )

    return s or "0"


def floor_to_step(
    value: Decimal,
    step: Decimal,
) -> Decimal:

    if step <= 0:
        return value

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def decimal_step_from_precision(
    precision: int,
) -> Decimal:

    if precision <= 0:
        return Decimal("1")

    return Decimal("1").scaleb(
        -precision
    )


def stable_json(
    data: Dict[str, Any],
) -> str:

    return json.dumps(
        data,
        separators=(",", ":"),
        sort_keys=True,
    )


def raw_json(
    data: Dict[str, Any],
) -> str:

    return json.dumps(
        data,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_hex(
    text: str,
) -> str:

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def make_client_order_id(
    prefix: str,
    seed: str,
) -> str:

    digest = hashlib.sha256(
        seed.encode("utf-8")
    ).hexdigest()[:20]

    value = (
        f"{prefix}-{digest}"
    )

    return value[:36]


def client_id_valid(
    value: str,
) -> bool:

    return bool(
        re.fullmatch(
            r"[\.A-Z\:/a-z0-9_-]{1,36}",
            value or "",
        )
    )


def env_credentials_present() -> bool:

    return bool(
        WEEX_API_KEY
        and WEEX_SECRET_KEY
        and WEEX_PASSPHRASE
    )


def validate_credentials() -> None:

    missing = []

    if not WEEX_API_KEY:
        missing.append(
            "WEEX_API_KEY"
        )

    if not WEEX_SECRET_KEY:
        missing.append(
            "WEEX_SECRET_KEY"
        )

    if not WEEX_PASSPHRASE:
        missing.append(
            "WEEX_PASSPHRASE"
        )

    if missing:
        raise RuntimeError(
            "Missing WEEX credentials: "
            + ", ".join(missing)
        )


# ============================================================
# DATA MODELS
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


@dataclass
class Signal:

    signal_id: str
    direction: str
    created_at: float


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

    history: List[str] = field(
        default_factory=lambda: [
            "NEW"
        ]
    )

    def transition(
        self,
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
                "SHADOW_COMMITTED",
                "REJECTED",
            },

            "SHADOW_COMMITTED": {
                "RECONCILED",
                "REJECTED",
            },

            "RECONCILED": set(),

            "REJECTED": set(),
        }

        if new_state in allowed.get(
            self.state,
            set(),
        ):

            self.state = new_state

            self.history.append(
                new_state
            )

            return True

        return False


@dataclass
class OrderStateMachine:

    state: str = "NONE"

    executed_qty: Decimal = D0

    seen_events: Set[str] = field(
        default_factory=set
    )

    def apply(
        self,
        event_id: str,
        status: str,
        cumulative_executed: Decimal,
    ) -> Tuple[bool, Decimal]:

        if event_id in self.seen_events:

            return (
                False,
                D0,
            )

        terminal = {
            "FILLED",
            "CANCELED",
            "CANCELLED",
            "REJECTED",
            "EXPIRED",
        }

        if self.state in terminal:

            return (
                False,
                D0,
            )

        self.seen_events.add(
            event_id
        )

        delta = max(
            D0,
            cumulative_executed
            - self.executed_qty,
        )

        self.executed_qty = max(
            self.executed_qty,
            cumulative_executed,
        )

        self.state = status

        return (
            True,
            delta,
        )


@dataclass
class ShadowCommit:

    endpoint: str

    payload: Dict[str, Any]

    body: str

    timestamp: str

    signature: str

    request_fingerprint: str

    intent_fingerprint: str

    commit_token: str

    real_post_blocked: bool


# ============================================================
# WEEX CLIENT
# ============================================================

class WeexClient:

    def __init__(
        self,
    ) -> None:

        self.session: Optional[
            aiohttp.ClientSession
        ] = None


    async def start(
        self,
    ) -> None:

        if (
            self.session is None
            or self.session.closed
        ):

            timeout = (
                aiohttp.ClientTimeout(
                    total=20
                )
            )

            self.session = (
                aiohttp.ClientSession(
                    timeout=timeout
                )
            )


    async def close(
        self,
    ) -> None:

        if (
            self.session
            and not self.session.closed
        ):

            await self.session.close()


    def _signature(
        self,
        timestamp: str,
        method: str,
        path: str,
        query: str = "",
        body: str = "",
    ) -> str:

        method = method.upper()

        prehash = (
            timestamp
            + method
            + path
        )

        if query:

            prehash += (
                "?"
                + query
            )

        prehash += body

        digest = hmac.new(
            WEEX_SECRET_KEY.encode(
                "utf-8"
            ),
            prehash.encode(
                "utf-8"
            ),
            hashlib.sha256,
        ).digest()

        return base64.b64encode(
            digest
        ).decode(
            "utf-8"
        )


    def signed_headers(
        self,
        method: str,
        path: str,
        query: str = "",
        body: str = "",
        timestamp: Optional[str] = None,
    ) -> Dict[str, str]:

        ts = (
            timestamp
            or str(
                int(
                    time.time()
                    * 1000
                )
            )
        )

        return {

            "ACCESS-KEY":
                WEEX_API_KEY,

            "ACCESS-SIGN":
                self._signature(
                    ts,
                    method,
                    path,
                    query,
                    body,
                ),

            "ACCESS-TIMESTAMP":
                ts,

            "ACCESS-PASSPHRASE":
                WEEX_PASSPHRASE,

            "Content-Type":
                "application/json",

            "User-Agent":
                f"{MODULE_NAME}/1.0",
        }


    async def public_get(
        self,
        path: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Any:

        await self.start()

        assert (
            self.session
            is not None
        )

        async with (
            self.session.get(
                API_BASE_URL + path,
                params=params,
            )
        ) as resp:

            text = await resp.text()

            if resp.status >= 400:

                raise RuntimeError(
                    "WEEX PUBLIC GET "
                    f"HTTP {resp.status}: "
                    f"{text}"
                )

            try:
                return json.loads(
                    text
                )

            except json.JSONDecodeError:

                return text
                
    async def private_get(
        self,
        path: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Any:

        await self.start()

        assert (
            self.session
            is not None
        )

        params = params or {}

        query = urlencode(
            params
        )

        headers = self.signed_headers(
            "GET",
            path,
            query=query,
        )

        url = (
            API_BASE_URL
            + path
        )

        if query:
            url += (
                "?"
                + query
            )

        async with (
            self.session.get(
                url,
                headers=headers,
            )
        ) as resp:

            text = await resp.text()

            if resp.status >= 400:

                raise RuntimeError(
                    "WEEX PRIVATE GET "
                    f"HTTP {resp.status}: "
                    f"{text}"
                )

            try:
                return json.loads(
                    text
                )

            except json.JSONDecodeError:
                return text


    async def demo_post(
        self,
        path: str,
        payload: Dict[str, Any],
    ) -> Any:

        await self.start()

        assert (
            self.session
            is not None
        )

        body = raw_json(
            payload
        )

        headers = self.signed_headers(
            "POST",
            path,
            body=body,
        )

        async with (
            self.session.post(
                API_BASE_URL + path,
                data=body,
                headers=headers,
            )
        ) as resp:

            text = await resp.text()

            if resp.status >= 400:

                raise RuntimeError(
                    "WEEX DEMO POST "
                    f"HTTP {resp.status}: "
                    f"{text}"
                )

            try:
                return json.loads(
                    text
                )

            except json.JSONDecodeError:
                return text


    async def real_post(
        self,
        path: str,
        payload: Dict[str, Any],
    ) -> Any:

        global R28_REAL_POST_CALLED

        # ====================================================
        # ABSOLUTE R28 REAL-ORDER TRANSMISSION LOCK
        # ====================================================
        #
        # No code below this guard is allowed to transmit
        # /capi/v3/order while R28 remains a pre-live module.
        # ====================================================

        if (
            HARD_REAL_POST_LOCK
            or not LIVE_ORDER_EXECUTION
            or path == REAL_ORDER_PATH
        ):

            raise RuntimeError(
                "R28 REAL ORDER POST BLOCKED "
                "BY ABSOLUTE EXECUTION SAFETY"
            )

        # This line must remain unreachable in R28.
        R28_REAL_POST_CALLED = True

        raise RuntimeError(
            "R28 safety invariant violated: "
            "real POST path became reachable"
        )


# ============================================================
# GENERIC RESPONSE EXTRACTION
# ============================================================

def unwrap_data(
    response: Any,
) -> Any:

    if not isinstance(
        response,
        dict,
    ):
        return response

    for key in (
        "data",
        "result",
    ):

        if key in response:
            return response[key]

    return response


def find_first_dict(
    value: Any,
) -> Optional[
    Dict[str, Any]
]:

    value = unwrap_data(
        value
    )

    if isinstance(
        value,
        dict,
    ):
        return value

    if isinstance(
        value,
        list,
    ):

        for item in value:

            if isinstance(
                item,
                dict,
            ):
                return item

    return None


def find_list(
    response: Any,
) -> List[
    Dict[str, Any]
]:

    value = unwrap_data(
        response
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

    if isinstance(
        value,
        dict,
    ):

        for key in (
            "list",
            "rows",
            "orders",
            "positions",
            "records",
            "items",
        ):

            candidate = value.get(
                key
            )

            if isinstance(
                candidate,
                list,
            ):

                return [
                    item
                    for item
                    in candidate
                    if isinstance(
                        item,
                        dict,
                    )
                ]

    return []


def first_value(
    data: Dict[str, Any],
    keys: Tuple[str, ...],
    default: Any = None,
) -> Any:

    for key in keys:

        if (
            key in data
            and data[key]
            is not None
        ):
            return data[key]

    return default


def response_code(
    response: Any,
) -> Optional[int]:

    if not isinstance(
        response,
        dict,
    ):
        return None

    value = first_value(
        response,
        (
            "code",
            "statusCode",
            "status_code",
        ),
    )

    if value is None:
        return None

    try:
        return int(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


def response_message(
    response: Any,
) -> str:

    if not isinstance(
        response,
        dict,
    ):
        return str(
            response
        )

    value = first_value(
        response,
        (
            "msg",
            "message",
            "error",
        ),
        "",
    )

    return str(
        value or ""
    )


def extract_order_id(
    response: Any,
) -> str:

    data = find_first_dict(
        response
    )

    if not data:
        return ""

    value = first_value(
        data,
        (
            "orderId",
            "order_id",
            "id",
        ),
        "",
    )

    return str(
        value or ""
    )


def extract_client_order_id(
    response: Any,
) -> str:

    data = find_first_dict(
        response
    )

    if not data:
        return ""

    value = first_value(
        data,
        (
            "clientOrderId",
            "clientOid",
            "client_order_id",
        ),
        "",
    )

    return str(
        value or ""
    )


# ============================================================
# CONTRACT / ACCOUNT EXTRACTION
# ============================================================

def extract_balance(
    response: Any,
) -> Decimal:

    data = unwrap_data(
        response
    )

    candidates: List[
        Dict[str, Any]
    ] = []

    if isinstance(
        data,
        dict,
    ):
        candidates.append(
            data
        )

    elif isinstance(
        data,
        list,
    ):

        candidates.extend(
            item
            for item in data
            if isinstance(
                item,
                dict,
            )
        )

    for row in candidates:

        coin = str(
            first_value(
                row,
                (
                    "coinName",
                    "coin",
                    "currency",
                    "asset",
                ),
                "",
            )
        ).upper()

        if (
            coin
            and coin != "USDT"
        ):
            continue

        value = first_value(
            row,
            (
                "available",
                "availableBalance",
                "availableAmount",
                "availableEquity",
                "balance",
                "equity",
            ),
        )

        if value is not None:
            return D(
                value
            )

    return D0


def extract_mark_price(
    response: Any,
) -> Decimal:

    data = unwrap_data(
        response
    )

    rows: List[
        Dict[str, Any]
    ] = []

    if isinstance(
        data,
        dict,
    ):
        rows.append(
            data
        )

    elif isinstance(
        data,
        list,
    ):

        rows.extend(
            item
            for item in data
            if isinstance(
                item,
                dict,
            )
        )

    for row in rows:

        value = first_value(
            row,
            (
                "markPrice",
                "price",
                "lastPrice",
                "close",
            ),
        )

        if value is not None:

            price = D(
                value
            )

            if price > 0:
                return price

    return D0


def extract_contract_info(
    response: Any,
    symbol: str,
) -> ContractInfo:

    data = unwrap_data(
        response
    )

    rows: List[
        Dict[str, Any]
    ] = []

    if isinstance(
        data,
        dict,
    ):

        nested = None

        for key in (
            "list",
            "symbols",
            "contracts",
            "rows",
        ):

            if isinstance(
                data.get(key),
                list,
            ):
                nested = data[key]
                break

        if nested is not None:

            rows.extend(
                item
                for item in nested
                if isinstance(
                    item,
                    dict,
                )
            )

        else:
            rows.append(
                data
            )

    elif isinstance(
        data,
        list,
    ):

        rows.extend(
            item
            for item in data
            if isinstance(
                item,
                dict,
            )
        )

    target: Optional[
        Dict[str, Any]
    ] = None

    for row in rows:

        row_symbol = str(
            first_value(
                row,
                (
                    "symbol",
                    "symbolName",
                    "contractCode",
                ),
                "",
            )
        ).upper()

        if row_symbol == symbol.upper():

            target = row
            break

    if target is None:

        if len(rows) == 1:
            target = rows[0]

        else:
            raise RuntimeError(
                f"Contract metadata not found "
                f"for {symbol}"
            )


    quantity_precision = int(
        D(
            first_value(
                target,
                (
                    "quantityPrecision",
                    "volumePlace",
                    "sizePrecision",
                ),
                4,
            )
        )
    )

    price_precision = int(
        D(
            first_value(
                target,
                (
                    "pricePrecision",
                    "pricePlace",
                ),
                1,
            )
        )
    )


    quantity_step = D(
        first_value(
            target,
            (
                "quantityStep",
                "sizeStep",
                "stepSize",
            ),
            decimal_step_from_precision(
                quantity_precision
            ),
        )
    )

    if quantity_step <= 0:

        quantity_step = (
            decimal_step_from_precision(
                quantity_precision
            )
        )


    price_step = D(
        first_value(
            target,
            (
                "priceStep",
                "tickSize",
            ),
            decimal_step_from_precision(
                price_precision
            ),
        )
    )

    if price_step <= 0:

        price_step = (
            decimal_step_from_precision(
                price_precision
            )
        )


    min_order = D(
        first_value(
            target,
            (
                "minOrderQty",
                "minOrderAmount",
                "minTradeNum",
                "minQty",
                "minSize",
            ),
            quantity_step,
        )
    )

    if min_order <= 0:
        min_order = quantity_step


    contract_value = D(
        first_value(
            target,
            (
                "contractValue",
                "contractSize",
                "faceValue",
            ),
            "0.0001",
        )
    )

    if contract_value <= 0:
        contract_value = Decimal(
            "0.0001"
        )


    min_leverage = int(
        D(
            first_value(
                target,
                (
                    "minLeverage",
                    "minLever",
                ),
                1,
            )
        )
    )


    max_leverage = int(
        D(
            first_value(
                target,
                (
                    "maxLeverage",
                    "maxLever",
                ),
                400,
            )
        )
    )


    return ContractInfo(

        symbol=symbol.upper(),

        min_order=min_order,

        quantity_precision=(
            quantity_precision
        ),

        quantity_step=(
            quantity_step
        ),

        price_precision=(
            price_precision
        ),

        price_step=(
            price_step
        ),

        contract_value=(
            contract_value
        ),

        min_leverage=(
            min_leverage
        ),

        max_leverage=(
            max_leverage
        ),
    )


# ============================================================
# API DISCOVERY
# ============================================================

async def get_balance(
    client: WeexClient,
) -> Decimal:

    candidates = [

        (
            "/capi/v3/account/balance",
            {
                "coinName": "USDT"
            },
        ),

        (
            "/capi/v3/account/balance",
            {},
        ),
    ]

    errors = []

    for (
        path,
        params,
    ) in candidates:

        try:

            response = (
                await client.private_get(
                    path,
                    params,
                )
            )

            balance = extract_balance(
                response
            )

            if balance > 0:
                return balance

        except Exception as exc:

            errors.append(
                f"{path}: {exc}"
            )

    raise RuntimeError(
        "Unable to obtain "
        "available USDT balance. "
        + " | ".join(errors)
    )


async def get_mark_price(
    client: WeexClient,
    symbol: str,
) -> Decimal:

    candidates = [

        (
            "/capi/v3/market/symbolPrice",
            {
                "symbol": symbol
            },
        ),

        (
            "/capi/v3/market/ticker",
            {
                "symbol": symbol
            },
        ),
    ]

    errors = []

    for (
        path,
        params,
    ) in candidates:

        try:

            response = (
                await client.public_get(
                    path,
                    params,
                )
            )

            price = extract_mark_price(
                response
            )

            if price > 0:
                return price

        except Exception as exc:

            errors.append(
                f"{path}: {exc}"
            )

    raise RuntimeError(
        "Unable to obtain mark price "
        f"for {symbol}. "
        + " | ".join(errors)
    )


async def get_contract(
    client: WeexClient,
    symbol: str,
) -> ContractInfo:

    candidates = [

        (
            "/capi/v3/market/exchangeInfo",
            {
                "symbol": symbol
            },
        ),

        (
            "/capi/v3/market/contracts",
            {
                "symbol": symbol
            },
        ),
    ]

    errors = []

    for (
        path,
        params,
    ) in candidates:

        try:

            response = (
                await client.public_get(
                    path,
                    params,
                )
            )

            return extract_contract_info(
                response,
                symbol,
            )

        except Exception as exc:

            errors.append(
                f"{path}: {exc}"
            )

    # R28 fails closed instead of guessing
    # live execution parameters.
    raise RuntimeError(
        "Unable to obtain contract "
        f"metadata for {symbol}. "
        + " | ".join(errors)
    )


# ============================================================
# QUANTITY / EXPOSURE
# ============================================================

def calculate_entry_margin(
    balance: Decimal,
) -> Decimal:

    return (
        balance
        
# ============================================================
# R28 SHADOW EXECUTION COMMIT GATE
# ============================================================

def build_shadow_commit(
    client: WeexClient,
    intent: ExecutionIntent,
    payload: Dict[str, Any],
) -> ShadowCommit:

    body = raw_json(
        payload
    )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = (
        client._signature(
            timestamp,
            "POST",
            REAL_ORDER_PATH,
            body=body,
        )
    )

    canonical_payload = (
        stable_json(
            payload
        )
    )

    request_fingerprint = (
        sha256_hex(
            "POST|"
            + REAL_ORDER_PATH
            + "|"
            + canonical_payload
        )
    )

    intent_fingerprint = (
        sha256_hex(
            "|".join(
                [
                    intent.intent_id,
                    intent.signal_id,
                    intent.symbol,
                    intent.side,
                    intent.position_side,
                    fmt_decimal(
                        intent.quantity
                    ),
                    str(
                        intent.leverage
                    ),
                    intent.client_order_id,
                ]
            )
        )
    )

    commit_token = (
        sha256_hex(
            "R28-SHADOW|"
            + intent_fingerprint
            + "|"
            + request_fingerprint
        )[:32]
    )

    return ShadowCommit(

        endpoint=(
            REAL_ORDER_PATH
        ),

        payload=payload,

        body=body,

        timestamp=timestamp,

        signature=signature,

        request_fingerprint=(
            request_fingerprint
        ),

        intent_fingerprint=(
            intent_fingerprint
        ),

        commit_token=(
            commit_token
        ),

        real_post_blocked=(
            HARD_REAL_POST_LOCK
            and
            not LIVE_ORDER_EXECUTION
        ),
    )


def validate_shadow_commit(
    commit: ShadowCommit,
    intent: ExecutionIntent,
) -> Dict[str, bool]:

    rebuilt_request_fingerprint = (
        sha256_hex(
            "POST|"
            + commit.endpoint
            + "|"
            + stable_json(
                commit.payload
            )
        )
    )


    rebuilt_intent_fingerprint = (
        sha256_hex(
            "|".join(
                [
                    intent.intent_id,
                    intent.signal_id,
                    intent.symbol,
                    intent.side,
                    intent.position_side,
                    fmt_decimal(
                        intent.quantity
                    ),
                    str(
                        intent.leverage
                    ),
                    intent.client_order_id,
                ]
            )
        )
    )


    rebuilt_commit_token = (
        sha256_hex(
            "R28-SHADOW|"
            + rebuilt_intent_fingerprint
            + "|"
            + rebuilt_request_fingerprint
        )[:32]
    )


    altered_payload = dict(
        commit.payload
    )

    altered_payload[
        "quantity"
    ] = fmt_decimal(
        D(
            altered_payload[
                "quantity"
            ]
        )
        + Decimal(
            "0.0001"
        )
    )


    altered_fingerprint = (
        sha256_hex(
            "POST|"
            + commit.endpoint
            + "|"
            + stable_json(
                altered_payload
            )
        )
    )


    checks = {

        "intent_fingerprint_stable":
            (
                rebuilt_intent_fingerprint
                ==
                commit.intent_fingerprint
            ),

        "request_fingerprint_stable":
            (
                rebuilt_request_fingerprint
                ==
                commit.request_fingerprint
            ),

        "commit_token_stable":
            (
                rebuilt_commit_token
                ==
                commit.commit_token
            ),

        "payload_mutation_detected":
            (
                altered_fingerprint
                !=
                commit.request_fingerprint
            ),

        "signature_nonempty":
            bool(
                commit.signature
            ),

        "real_post_still_blocked":
            (
                commit.real_post_blocked
            ),
    }


    checks[
        "overall"
    ] = all(
        checks.values()
    )

    return checks


# ============================================================
# DEMO POSITION HELPERS
# ============================================================

async def get_demo_positions(
    client: WeexClient,
) -> List[
    Dict[str, Any]
]:

    response = (
        await client.private_get(
            DEMO_POSITION_PATH,
            {
                "symbol":
                    DEMO_SYMBOL
            },
        )
    )

    return find_list(
        response
    )


def position_size(
    rows: List[
        Dict[str, Any]
    ],
    symbol: str,
    position_side: str,
) -> Decimal:

    target_symbol = (
        symbol.upper()
    )

    target_side = (
        position_side.upper()
    )

    for row in rows:

        row_symbol = str(
            first_value(
                row,
                (
                    "symbol",
                    "symbolName",
                ),
                "",
            )
        ).upper()

        if (
            row_symbol
            != target_symbol
        ):
            continue


        row_side = str(
            first_value(
                row,
                (
                    "positionSide",
                    "holdSide",
                    "side",
                ),
                "",
            )
        ).upper()


        if (
            row_side
            != target_side
        ):
            continue


        value = first_value(
            row,
            (
                "size",
                "quantity",
                "positionAmt",
                "positionAmount",
                "total",
                "available",
            ),
            "0",
        )


        return abs(
            D(
                value
            )
        )

    return D0


# ============================================================
# DEMO SIDE SELECTION
# ============================================================

def choose_demo_side_and_position(
    before_rows: List[
        Dict[str, Any]
    ],
    quantity: Decimal,
) -> Tuple[
    str,
    str,
]:

    long_size = (
        position_size(
            before_rows,
            DEMO_SYMBOL,
            "LONG",
        )
    )

    short_size = (
        position_size(
            before_rows,
            DEMO_SYMBOL,
            "SHORT",
        )
    )


    if (
        DEMO_FILL_MODE
        == "OPEN_LONG"
    ):

        return (
            "BUY",
            "LONG",
        )


    if (
        DEMO_FILL_MODE
        == "OPEN_SHORT"
    ):

        return (
            "SELL",
            "SHORT",
        )


    if (
        DEMO_FILL_MODE
        == "CLOSE_LONG"
    ):

        return (
            "SELL",
            "LONG",
        )


    if (
        DEMO_FILL_MODE
        == "CLOSE_SHORT"
    ):

        return (
            "BUY",
            "SHORT",
        )


    # AUTO MODE:
    # Prefer reducing an existing demo
    # position so repeated diagnostics
    # do not continuously accumulate
    # exposure.

    if (
        long_size
        >= quantity
    ):

        return (
            "SELL",
            "LONG",
        )


    if (
        short_size
        >= quantity
    ):

        return (
            "BUY",
            "SHORT",
        )


    return (
        "BUY",
        "LONG",
    )


# ============================================================
# DEMO PAYLOAD
# ============================================================

def build_demo_payload(
    side: str,
    position_side: str,
    quantity: Decimal,
) -> Dict[str, Any]:

    seed = (
        f"{DEMO_SYMBOL}|"
        f"{side}|"
        f"{position_side}|"
        f"{fmt_decimal(quantity)}|"
        f"{int(time.time() // 60)}"
    )


    client_order_id = (
        make_client_order_id(
            "r28d",
            seed,
        )
    )


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
            fmt_decimal(
                quantity
            ),

        "newClientOrderId":
            client_order_id,
    }


# ============================================================
# DEMO HISTORY LOOKUP
# ============================================================

def extract_history_order_id(
    row: Dict[str, Any],
) -> str:

    return str(
        first_value(
            row,
            (
                "orderId",
                "order_id",
                "id",
            ),
            "",
        )
        or ""
    )


def extract_history_client_id(
    row: Dict[str, Any],
) -> str:

    return str(
        first_value(
            row,
            (
                "clientOrderId",
                "newClientOrderId",
                "clientOid",
                "client_order_id",
            ),
            "",
        )
        or ""
    )


async def find_demo_history_row(
    client: WeexClient,
    order_id: str,
    client_id: str,
) -> Tuple[
    Optional[
        Dict[str, Any]
    ],
    int,
]:

    attempts = 0

    for _ in range(
        6
    ):

        attempts += 1


        response = (
            await client.private_get(
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
        )


        rows = find_list(
            response
        )


        for row in rows:

            history_order_id = (
                extract_history_order_id(
                    row
                )
            )

            history_client_id = (
                extract_history_client_id(
                    row
                )
            )


            if (
                order_id
                and
                history_order_id
                == order_id
            ):

                return (
                    row,
                    attempts,
                )


            if (
                client_id
                and
                history_client_id
                == client_id
            ):

                return (
                    row,
                    attempts,
                )


        await asyncio.sleep(
            1
        )


    return (
        None,
        attempts,
    )


# ============================================================
# DEMO HISTORY EXTRACTION
# ============================================================

def history_status(
    row: Dict[str, Any],
) -> str:

    value = first_value(
        row,
        (
            "status",
            "state",
            "orderStatus",
        ),
        "UNKNOWN",
    )

    return str(
        value
    ).upper()


def history_original_quantity(
    row: Dict[str, Any],
) -> Decimal:

    return D(
        first_value(
            row,
            (
                "origQty",
                "originalQty",
                "quantity",
                "size",
                "orderQty",
            ),
            "0",
        )
    )


def history_executed_quantity(
    row: Dict[str, Any],
) -> Decimal:

    return D(
        first_value(
            row,
            (
                "executedQty",
                "filledQty",
                "fillQty",
                "filledSize",
                "dealQty",
            ),
            "0",
        )
    )


def history_average_price(
    row: Dict[str, Any],
) -> Decimal:

    return D(
        first_value(
            row,
            (
                "avgPrice",
                "averagePrice",
                "fillPrice",
                "priceAvg",
                "price",
            ),
            "0",
        )
    )


# ============================================================
# R28 DEMO ACTUAL-FILL LIFECYCLE
# ============================================================

async def run_demo_lifecycle(
    client: WeexClient,
    quantity: Decimal,
) -> Dict[str, Any]:

    before_rows = (
        await get_demo_positions(
            client
        )
    )


    (
        side,
        position_side,
    ) = (
        choose_demo_side_and_position(
            before_rows,
            quantity,
        )
    )


    before_size = (
        position_size(
            before_rows,
            DEMO_SYMBOL,
            position_side,
        )
    )


    payload = (
        build_demo_payload(
            side,
            position_side,
            quantity,
        )
    )


    client_order_id = str(
        payload[
            "newClientOrderId"
        ]
    )


    # --------------------------------------------------------
    # DEMO POST ONLY
    # --------------------------------------------------------

    response = (
        await client.demo_post(
            DEMO_ORDER_PATH,
            payload,
        )
    )


    classification = (
        classify_order_response(
            response
        )
    )


    post_accepted = (
        classification
        == "ACCEPTED"
    )


    order_id = (
        extract_order_id(
            response
        )
    )


    response_client_id = (
        extract_client_order_id(
            response
        )
    )


    (
        history_row,
        history_attempts,
    ) = (
        await find_demo_history_row(
            client,
            order_id,
            client_order_id,
        )
    )


    if history_row is None:

        raise RuntimeError(
            "R28 demo order was not found "
            "in demo history"
        )


    final_status = (
        history_status(
            history_row
        )
    )


    original_quantity = (
        history_original_quantity(
            history_row
        )
    )


    executed_quantity = (
        history_executed_quantity(
            history_row
        )
    )


    average_fill_price = (
        history_average_price(
            history_row
        )
    )


    # ========================================================
    # REPLAY ACTUAL FILL THROUGH ORDER STATE MACHINE
    # ========================================================

    order_state = (
        OrderStateMachine()
    )


    (
        new_state_accepted,
        _,
    ) = order_state.apply(
        "r28-event-new",
        "NEW",
        D0,
    )


    partial_1_quantity = (
        floor_to_step(
            executed_quantity
            / Decimal(
                "3"
            ),
            Decimal(
                "0.00000001"
            ),
        )
    )


    (
        partial_1_accepted,
        partial_1_delta,
    ) = order_state.apply(
        "r28-event-partial-1",
        "PARTIALLY_FILLED",
        partial_1_quantity,
    )


    partial_2_quantity = (
        floor_to_step(
            executed_quantity
            * Decimal(
                "2"
            )
            / Decimal(
                "3"
            ),
            Decimal(
                "0.00000001"
            ),
        )
    )


    (
        partial_2_accepted,
        partial_2_delta,
    ) = order_state.apply(
        "r28-event-partial-2",
        "PARTIALLY_FILLED",
        partial_2_quantity,
    )


    (
        fill_accepted,
        final_fill_delta,
    ) = order_state.apply(
        "r28-event-filled",
        "FILLED",
        executed_quantity,
    )


    (
        duplicate_event_accepted,
        _,
    ) = order_state.apply(
        "r28-event-filled",
        "FILLED",
        executed_quantity,
    )


    (
        regression_accepted,
        _,
    ) = order_state.apply(
        "r28-event-regression",
        "NEW",
        executed_quantity,
    )


    actual_fill_delta = (
        partial_1_delta
        + partial_2_delta
        + final_fill_delta
    )


    # ========================================================
    # POSITION RECONCILIATION
    # ========================================================

    after_rows = (
        await get_demo_positions(
            client
        )
    )


    after_size = (
        position_size(
            after_rows,
            DEMO_SYMBOL,
            position_side,
        )
    )


    opens_position = (

        (
            side == "BUY"
            and
            position_side
            == "LONG"
        )

        or

        (
            side == "SELL"
            and
            position_side
            == "SHORT"
        )
    )


    if opens_position:

        expected_position_delta = (
            executed_quantity
        )

    else:

        expected_position_delta = (
            -executed_quantity
        )


    observed_position_delta = (
        after_size
        - before_size
    )


    position_reconciled = (
        observed_position_delta
        ==
        expected_position_delta
    )


    response_client_id_match = (

        not response_client_id

        or

        response_client_id
        == client_order_id
    )


    fill_lifecycle_valid = all(
        (
            post_accepted,

            final_status
            == "FILLED",

            executed_quantity
            > 0,

            original_quantity
            == quantity,

            actual_fill_delta
            == executed_quantity,

            new_state_accepted,

            partial_1_accepted,

            partial_2_accepted,

            fill_accepted,

            not duplicate_event_accepted,

            not regression_accepted,

            position_reconciled,
        )
    )


    return {

        "symbol":
            DEMO_SYMBOL,

        "fill_mode":
            DEMO_FILL_MODE,

        "side":
            side,

        "position_side":
            position_side,

        "type":
            "MARKET",

        "client_order_id":
            client_order_id,

        "client_order_id_valid":
            client_id_valid(
                client_order_id
            ),

        "post_attempted":
            True,

        "post_accepted":
            post_accepted,

        "order_id":
            order_id,

        "response_client_id_match":
            response_client_id_match,

        "history_lookup_attempted":
            True,

        "history_poll_attempts":
            history_attempts,

        "history_found":
            history_row
            is not None,

        "final_status":
            final_status,

        "requested_quantity":
            quantity,

        "original_quantity":
            original_quantity,

        "executed_quantity":
            executed_quantity,

        "average_fill_price":
            average_fill_price,

        "non_zero_fill":
            executed_quantity
            > 0,

        "actual_fill_delta":
            actual_fill_delta,

        "new_state_accepted":
            new_state_accepted,

        "partial_fill_1_delta":
            partial_1_accepted
            and
            partial_1_delta
            >= 0,

        "partial_fill_2_delta":
            partial_2_accepted
            and
            partial_2_delta
            >= 0,

        "filled_terminal_state":
            fill_accepted
            and
            order_state.state
            == "FILLED",

        "duplicate_fill_event_blocked":
            not duplicate_event_accepted,

        "terminal_regression_blocked":
            not regression_accepted,

        "position_size_before":
            before_size,

        "position_size_after":
            after_size,

        "expected_position_delta":
            expected_position_delta,

        "observed_position_delta":
            observed_position_delta,

        "position_reconciled":
            position_reconciled,

        "fill_lifecycle_valid":
            fill_lifecycle_valid,
    }
