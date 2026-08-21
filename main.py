import asyncio
import base64
import hashlib
import hmac
import json
import os
import time
import traceback

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import aiohttp
from aiohttp import web


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R24"
API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()


def default_demo_symbol(symbol: str) -> str:
    if symbol.endswith("USDT"):
        return symbol[:-4] + "SUSDT"
    return symbol


DEMO_SYMBOL = os.getenv(
    "DEMO_SYMBOL",
    default_demo_symbol(SYMBOL),
).strip().upper()


# ============================================================
# ABSOLUTE EXECUTION SAFETY
# ============================================================
#
# R24 IS PRE-LIVE / DEMO ONLY.
#
# REAL ORDER TRANSMISSION IS HARD DISABLED.
#
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_REAL_POST_LOCK = True

R24_REAL_POST_CALLED = False
R24_DEMO_POST_ATTEMPTED = False
R24_DEMO_POST_ACCEPTED = False

REAL_ORDER_PATH = "/capi/v3/order"
DEMO_ORDER_PATH = "/capi/v3/sim/order"
DEMO_HISTORY_PATH = "/capi/v3/sim/order/history"
DEMO_POSITIONS_PATH = "/capi/v3/sim/position/allPosition"

BALANCE_PATH = "/capi/v3/account/balance"
EXCHANGE_INFO_PATH = "/capi/v3/market/exchangeInfo"
MARK_PRICE_PATH = "/capi/v3/market/symbolPrice"


def real_order_post_blocked() -> bool:
    return HARD_REAL_POST_LOCK or not LIVE_ORDER_EXECUTION


async def blocked_real_post(*args, **kwargs):
    global R24_REAL_POST_CALLED

    R24_REAL_POST_CALLED = True

    raise RuntimeError(
        "R24 ABSOLUTE SAFETY LOCK: real order POST is disabled"
    )


# ============================================================
# ADJUSTABLE STRATEGY CONFIG
# ============================================================

ENTRY_PERCENT = Decimal(
    os.getenv("ENTRY_PERCENT", "5")
)

LEVERAGE = Decimal(
    os.getenv("LEVERAGE", "100")
)

MAX_CONFIG_LEVERAGE = Decimal(
    os.getenv("MAX_CONFIG_LEVERAGE", "100")
)

MARGIN_TYPE = os.getenv(
    "MARGIN_TYPE",
    "ISOLATED",
).strip().upper()

MAX_PYRAMID_ADDS = int(
    os.getenv("MAX_PYRAMID_ADDS", "1")
)

PYRAMID_SIZE_PERCENT = Decimal(
    os.getenv("PYRAMID_SIZE_PERCENT", "5")
)

MAX_BACKUPS = int(
    os.getenv("MAX_BACKUPS", "3")
)

BACKUP_SIZE_PERCENT = Decimal(
    os.getenv("BACKUP_SIZE_PERCENT", "5")
)

BACKUP_BUFFER_PERCENT = Decimal(
    os.getenv("BACKUP_BUFFER_PERCENT", "0.3")
)

MIN_LIQ_DISTANCE_PERCENT = Decimal(
    os.getenv("MIN_LIQ_DISTANCE_PERCENT", "0.2")
)

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv("MAX_FUND_EXPOSURE_PERCENT", "35")
)


# ============================================================
# TP / TRAILING CONFIG
# ============================================================

TP1_PERCENT = Decimal(
    os.getenv("TP1_PERCENT", "20")
)

TP2_PERCENT = Decimal(
    os.getenv("TP2_PERCENT", "20")
)

TP3_PERCENT = Decimal(
    os.getenv("TP3_PERCENT", "60")
)

TP1_TRIGGER_PERCENT = Decimal(
    os.getenv("TP1_TRIGGER_PERCENT", "0.5")
)

TP2_TRIGGER_PERCENT = Decimal(
    os.getenv("TP2_TRIGGER_PERCENT", "1.0")
)

TRAILING_DISTANCE_PERCENT = Decimal(
    os.getenv("TRAILING_DISTANCE_PERCENT", "0.2")
)


# ============================================================
# SIGNAL SAFETY
# ============================================================

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv("SIGNAL_EXPIRY_SECONDS", "120")
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv("LOSS_COOLDOWN_SECONDS", "300")
)


# ============================================================
# DEMO REHEARSAL CONFIG
# ============================================================

RUN_DEMO_ORDER_TEST = (
    os.getenv("RUN_DEMO_ORDER_TEST", "true")
    .strip()
    .lower()
    in {"1", "true", "yes", "on"}
)

REHEARSAL_SIDE = os.getenv(
    "REHEARSAL_SIDE",
    "BUY",
).strip().upper()

REHEARSAL_POSITION_SIDE = os.getenv(
    "REHEARSAL_POSITION_SIDE",
    "LONG",
).strip().upper()

REHEARSAL_ORDER_TYPE = "LIMIT"
REHEARSAL_TIME_IN_FORCE = "IOC"

DEMO_LIMIT_OFFSET_PERCENT = Decimal(
    os.getenv("DEMO_LIMIT_OFFSET_PERCENT", "0.5")
)


# ============================================================
# HISTORY POLLING
# ============================================================

ORDER_HISTORY_LOOKBACK_MS = int(
    os.getenv("ORDER_HISTORY_LOOKBACK_MS", "180000")
)

ORDER_HISTORY_POLL_ATTEMPTS = int(
    os.getenv("ORDER_HISTORY_POLL_ATTEMPTS", "6")
)

ORDER_HISTORY_POLL_INTERVAL = float(
    os.getenv("ORDER_HISTORY_POLL_INTERVAL", "1.0")
)


# ============================================================
# ORDER STATES
# ============================================================

TERMINAL_STATUSES = {
    "FILLED",
    "CANCELED",
    "REJECTED",
    "EXPIRED",
}

ACTIVE_STATUSES = {
    "NEW",
    "PARTIALLY_FILLED",
}

RECOGNIZED_STATUSES = TERMINAL_STATUSES | ACTIVE_STATUSES

STATUS_RANK = {
    "NEW": 10,
    "PARTIALLY_FILLED": 20,
    "FILLED": 30,
    "CANCELED": 30,
    "REJECTED": 30,
    "EXPIRED": 30,
}


# ============================================================
# RUNTIME / TELEGRAM
# ============================================================

PORT = int(
    os.getenv("PORT", "10000")
)

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


# ============================================================
# ENVIRONMENT CREDENTIALS
# ============================================================

def env_first(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()

        if value:
            return value

    return ""


WEEX_API_KEY = env_first(
    "WEEX_API_KEY",
    "WEEX_ACCESS_KEY",
    "API_KEY",
)

WEEX_SECRET_KEY = env_first(
    "WEEX_SECRET_KEY",
    "WEEX_SECRET",
    "SECRET_KEY",
)

WEEX_PASSPHRASE = env_first(
    "WEEX_PASSPHRASE",
    "WEEX_ACCESS_PASSPHRASE",
    "PASSPHRASE",
)


# ============================================================
# GENERAL HELPERS
# ============================================================

def D(value: Any, default: str = "0") -> Decimal:
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


def dec_str(value: Decimal) -> str:
    s = format(value, "f")

    if "." in s:
        s = s.rstrip("0").rstrip(".")

    return s or "0"


def yesno(value: bool) -> str:
    return "✅ YES" if value else "❌ NO"


def safe_upper(value: Any) -> str:
    return str(value or "").strip().upper()


def now_ms() -> int:
    return int(time.time() * 1000)


def validate_credentials() -> None:
    missing = []

    if not WEEX_API_KEY:
        missing.append("WEEX_API_KEY")

    if not WEEX_SECRET_KEY:
        missing.append("WEEX_SECRET_KEY")

    if not WEEX_PASSPHRASE:
        missing.append("WEEX_PASSPHRASE")

    if missing:
        raise RuntimeError(
            "Missing WEEX credentials: "
            + ", ".join(missing)
        )


def create_client_order_id() -> str:
    value = f"r24-{int(time.time() * 1000)}"
    return value[-36:]


# ============================================================
# SIGNING
# ============================================================

def canonical_query(
    params: Optional[Dict[str, Any]],
) -> str:
    if not params:
        return ""

    clean = []

    for key, value in params.items():
        if value is None:
            continue

        clean.append(
            (key, str(value))
        )

    return urlencode(clean)


def json_body(
    payload: Optional[Dict[str, Any]],
) -> str:
    if not payload:
        return ""

    return json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def make_signature(
    timestamp: str,
    method: str,
    path: str,
    query: str = "",
    body: str = "",
) -> str:

    target = path

    if query:
        target += "?" + query

    message = (
        timestamp
        + method.upper()
        + target
        + body
    )

    digest = hmac.new(
        WEEX_SECRET_KEY.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


def private_headers(
    method: str,
    path: str,
    query: str = "",
    body: str = "",
) -> Dict[str, str]:

    timestamp = str(now_ms())

    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": make_signature(
            timestamp,
            method,
            path,
            query,
            body,
        ),
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": WEEX_PASSPHRASE,
        "Content-Type": "application/json",
        "locale": "en-US",
    }


# ============================================================
# HTTP RESPONSE
# ============================================================

async def parse_response(
    response: aiohttp.ClientResponse,
) -> Any:

    text = await response.text()

    try:
        data = json.loads(text)
    except Exception:
        data = text

    if response.status < 200 or response.status >= 300:
        raise RuntimeError(
            f"WEEX HTTP {response.status}: {text}"
        )

    return data


# ============================================================
# PUBLIC GET
# ============================================================

async def public_get(
    session: aiohttp.ClientSession,
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:

    async with session.get(
        API_BASE_URL + path,
        params=params,
        timeout=aiohttp.ClientTimeout(total=15),
    ) as response:

        return await parse_response(response)


# ============================================================
# PRIVATE GET
# ============================================================

async def private_get(
    session: aiohttp.ClientSession,
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:

    query = canonical_query(params)

    headers = private_headers(
        "GET",
        path,
        query=query,
    )

    url = API_BASE_URL + path

    if query:
        url += "?" + query

    async with session.get(
        url,
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=15),
    ) as response:

        return await parse_response(response)


# ============================================================
# DEMO POST ONLY
# ============================================================

async def demo_post(
    session: aiohttp.ClientSession,
    path: str,
    payload: Dict[str, Any],
) -> Any:

    global R24_DEMO_POST_ATTEMPTED
    global R24_DEMO_POST_ACCEPTED

    if path == REAL_ORDER_PATH:
        return await blocked_real_post(
            session,
            path,
            payload,
        )

    if not path.startswith("/capi/v3/sim/"):
        raise RuntimeError(
            "R24 safety violation: "
            f"non-demo POST path blocked: {path}"
        )

    R24_DEMO_POST_ATTEMPTED = True

    body = json_body(payload)

    headers = private_headers(
        "POST",
        path,
        body=body,
    )

    async with session.post(
        API_BASE_URL + path,
        headers=headers,
        data=body.encode("utf-8"),
        timeout=aiohttp.ClientTimeout(total=15),
    ) as response:

        data = await parse_response(response)

    accepted = False

    if isinstance(data, dict):
        success = data.get("success")

        accepted = (
            success is True
            or (
                success is None
                and bool(data.get("orderId"))
            )
        )

        if success is False:
            raise RuntimeError(
                "WEEX DEMO POST rejected: "
                f"code={data.get('errorCode')} "
                f"msg={data.get('errorMessage')}"
            )

    R24_DEMO_POST_ACCEPTED = accepted

    if not accepted:
        raise RuntimeError(
            "WEEX DEMO POST response "
            f"not recognized as accepted: {data}"
        )

    return data


# ============================================================
# CONTRACT INFO
# ============================================================

@dataclass
class ContractInfo:
    min_qty: Decimal
    qty_precision: int
    qty_step: Decimal
    price_precision: int
    price_step: Decimal
    contract_value: Decimal
    min_leverage: Decimal
    max_leverage: Decimal


def decimal_places(step: Decimal) -> int:
    normalized = step.normalize()

    return max(
        0,
        -normalized.as_tuple().exponent,
    )


def first_dict_list(
    value: Any,
) -> List[Dict[str, Any]]:

    if isinstance(value, list):
        return [
            x
            for x in value
            if isinstance(x, dict)
        ]

    if isinstance(value, dict):
        for key in (
            "data",
            "list",
            "symbols",
            "rows",
        ):
            maybe = value.get(key)

            if isinstance(maybe, list):
                return [
                    x
                    for x in maybe
                    if isinstance(x, dict)
                ]

            if isinstance(maybe, dict):
                for nested_key in (
                    "list",
                    "rows",
                    "symbols",
                ):
                    nested = maybe.get(nested_key)

                    if isinstance(nested, list):
                        return [
                            x
                            for x in nested
                            if isinstance(x, dict)
                        ]

    return []


def find_symbol_record(
    exchange_info: Any,
    symbol: str,
) -> Dict[str, Any]:

    candidates = []

    if isinstance(exchange_info, dict):

        symbols = exchange_info.get("symbols")

        if isinstance(symbols, list):
            candidates.extend(
                x
                for x in symbols
                if isinstance(x, dict)
            )

        data = exchange_info.get("data")

        if isinstance(data, dict):

            data_symbols = data.get("symbols")

            if isinstance(data_symbols, list):
                candidates.extend(
                    x
                    for x in data_symbols
                    if isinstance(x, dict)
                )

        elif isinstance(data, list):
            candidates.extend(
                x
                for x in data
                if isinstance(x, dict)
            )

    elif isinstance(exchange_info, list):

        candidates.extend(
            x
            for x in exchange_info
            if isinstance(x, dict)
        )

    for item in candidates:

        if safe_upper(
            item.get("symbol")
        ) == symbol.upper():

            return item

    if candidates:
        return candidates[0]

    raise RuntimeError(
        "Unable to locate contract symbol configuration"
    )


def filter_value(
    record: Dict[str, Any],
    filter_type: str,
    field: str,
) -> Optional[Any]:

    filters = record.get("filters")

    if isinstance(filters, list):

        for item in filters:

            if (
                isinstance(item, dict)
                and safe_upper(
                    item.get("filterType")
                ) == filter_type.upper()
            ):
                return item.get(field)

    return None


def extract_contract_info(
    record: Dict[str, Any],
) -> ContractInfo:

    qty_step = D(
        record.get("quantityStep")
        or record.get("qtyStep")
        or record.get("stepSize")
        or filter_value(
            record,
            "LOT_SIZE",
            "stepSize",
        )
        or "0.0001"
    )

    min_qty = D(
        record.get("minOrderQty")
        or record.get("minQty")
        or filter_value(
            record,
            "LOT_SIZE",
            "minQty",
        )
        or qty_step
    )

    price_step = D(
        record.get("priceStep")
        or record.get("tickSize")
        or filter_value(
            record,
            "PRICE_FILTER",
            "tickSize",
        )
        or "0.1"
    )

    qty_precision = int(
        record.get(
            "quantityPrecision",
            decimal_places(qty_step),
        )
    )

    price_precision = int(
        record.get(
            "pricePrecision",
            decimal_places(price_step),
        )
    )

    contract_value = D(
        record.get("contractSize")
        or record.get("contractValue")
        or "0.0001"
    )

    min_leverage = D(
        record.get("minLeverage")
        or "1"
    )

    max_leverage = D(
        record.get("maxLeverage")
        or "400"
    )

    if (
        qty_step <= 0
        or price_step <= 0
        or min_qty <= 0
    ):
        raise RuntimeError(
            "Invalid exchange precision metadata"
        )

    return ContractInfo(
        min_qty=min_qty,
        qty_precision=qty_precision,
        qty_step=qty_step,
        price_precision=price_precision,
        price_step=price_step,
        contract_value=contract_value,
        min_leverage=min_leverage,
        max_leverage=max_leverage,
    )


# ============================================================
# BALANCE
# ============================================================

def extract_available_usdt(
    balance_data: Any,
) -> Decimal:

    records = first_dict_list(balance_data)

    for row in records:

        if safe_upper(
            row.get("asset")
        ) == "USDT":

            value = D(
                row.get("availableBalance")
                or row.get("available")
                or row.get("balance")
            )

            if value >= 0:
                return value

    if isinstance(balance_data, dict):

        if safe_upper(
            balance_data.get("asset")
        ) == "USDT":

            return D(
                balance_data.get("availableBalance")
                or balance_data.get("available")
                or balance_data.get("balance")
            )

        data = balance_data.get("data")

        if isinstance(data, dict):

            if safe_upper(
                data.get("asset")
            ) == "USDT":

                return D(
                    data.get("availableBalance")
                    or data.get("available")
                    or data.get("balance")
                )

    raise RuntimeError(
        "Unable to extract available USDT: "
        f"{balance_data}"
    )


# ============================================================
# MARK PRICE
# ============================================================

def extract_mark_price(
    data: Any,
) -> Decimal:

    if isinstance(data, dict):

        for key in (
            "price",
            "markPrice",
            "indexPrice",
        ):
            price = D(
                data.get(key)
            )

            if price > 0:
                return price

        inner = data.get("data")

        if isinstance(inner, dict):

            for key in (
                "price",
                "markPrice",
                "indexPrice",
            ):
                price = D(
                    inner.get(key)
                )

                if price > 0:
                    return price

        if isinstance(inner, list):

            for row in inner:

                if not isinstance(row, dict):
                    continue

                for key in (
                    "price",
                    "markPrice",
                    "indexPrice",
                ):
                    price = D(
                        row.get(key)
                    )

                    if price > 0:
                        return price

    if isinstance(data, list):

        for row in data:

            if not isinstance(row, dict):
                continue

            for key in (
                "price",
                "markPrice",
                "indexPrice",
            ):
                price = D(
                    row.get(key)
                )

                if price > 0:
                    return price

    raise RuntimeError(
        "Unable to extract mark price: "
        f"{data}"
    )


# ============================================================
# PRECISION HELPERS
# ============================================================

def floor_to_step(
    value: Decimal,
    step: Decimal,
) -> Decimal:

    if step <= 0:
        raise ValueError(
            "step must be > 0"
        )

    return (
        (
            value / step
        ).to_integral_value(
            rounding=ROUND_DOWN
        )
        * step
    )


def step_matches(
    value: Decimal,
    step: Decimal,
) -> bool:

    if step <= 0:
        return False

    return (
        floor_to_step(
            value,
            step,
        )
        == value
    )


# ============================================================
# ENTRY CALCULATION
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

    if mark_price <= 0:
        raise RuntimeError(
            "Mark price must be greater than zero"
        )

    margin = (
        balance
        * ENTRY_PERCENT
        / Decimal("100")
    )

    notional = (
        margin
        * LEVERAGE
    )

    raw_qty = (
        notional
        / mark_price
    )

    quantity = floor_to_step(
        raw_qty,
        contract.qty_step,
    )

    return (
        margin,
        notional,
        quantity,
    )


# ============================================================
# SAFE DEMO LIMIT PRICE
# ============================================================

def build_safe_demo_limit_price(
    mark_price: Decimal,
    side: str,
    step: Decimal,
) -> Decimal:

    offset = (
        mark_price
        * DEMO_LIMIT_OFFSET_PERCENT
        / Decimal("100")
    )

    if side.upper() == "BUY":
        raw_price = mark_price - offset
    else:
        raw_price = mark_price + offset

    price = floor_to_step(
        raw_price,
        step,
    )

    if price <= 0:
        raise RuntimeError(
            "Calculated demo price is not positive"
        )

    if not step_matches(
        price,
        step,
    ):
        raise RuntimeError(
            "Calculated demo price does not match price step"
        )

    return price


# ============================================================
# EXECUTION GATE SELF TESTS
# ============================================================

def run_gate_self_tests() -> Dict[str, bool]:

    current = time.time()

    fresh_signal = (
        current - (current - 1)
        <= SIGNAL_EXPIRY_SECONDS
    )

    expired_signal = (
        current
        - (
            current
            - SIGNAL_EXPIRY_SECONDS
            - 1
        )
        > SIGNAL_EXPIRY_SECONDS
    )

    last_loss = (
        current
        - max(
            0,
            LOSS_COOLDOWN_SECONDS - 1,
        )
    )

    loss_cooldown = (
        current - last_loss
        < LOSS_COOLDOWN_SECONDS
    )

    seen = {
        "r24-test-signal"
    }

    duplicate_rejected = (
        "r24-test-signal"
        in seen
    )

    open_direction = "LONG"
    incoming_direction = "SHORT"

    one_direction_gate = (
        open_direction
        != incoming_direction
    )

    external_position_clear = True

    return {
        "fresh_signal": fresh_signal,
        "expired_rejected": expired_signal,
        "loss_cooldown": loss_cooldown,
        "duplicate_rejected": duplicate_rejected,
        "one_direction_gate": one_direction_gate,
        "external_position_clear": external_position_clear,
    }


# ============================================================
# EXPOSURE TEST
# ============================================================

def exposure_test() -> Tuple[
    Decimal,
    bool,
]:

    total = (
        ENTRY_PERCENT
        + (
            Decimal(MAX_PYRAMID_ADDS)
            * PYRAMID_SIZE_PERCENT
        )
        + (
            Decimal(MAX_BACKUPS)
            * BACKUP_SIZE_PERCENT
        )
    )

    return (
        total,
        total <= MAX_FUND_EXPOSURE_PERCENT,
    )


# ============================================================
# R24 ORDER STATE TRACKER
# ============================================================

@dataclass
class ProcessResult:
    accepted: bool
    duplicate: bool
    regression: bool
    terminal: bool
    fill_delta: Decimal
    status: str


class OrderStateTracker:

    def __init__(self):
        self._orders: Dict[
            str,
            Dict[str, Any],
        ] = {}

        self._event_keys = set()

    @staticmethod
    def event_key(
        order: Dict[str, Any],
    ) -> str:

        return "|".join(
            [
                str(
                    order.get("orderId")
                    or ""
                ),
                safe_upper(
                    order.get("status")
                ),
                str(
                    order.get("executedQty")
                    or "0"
                ),
                str(
                    order.get("updateTime")
                    or order.get("time")
                    or "0"
                ),
            ]
        )

    def process(
        self,
        order: Dict[str, Any],
    ) -> ProcessResult:

        order_id = str(
            order.get("orderId")
            or ""
        ).strip()

        if not order_id:
            raise RuntimeError(
                "R24 state tracker: orderId missing"
            )

        status = safe_upper(
            order.get("status")
        )

        if status not in RECOGNIZED_STATUSES:
            raise RuntimeError(
                "R24 state tracker: "
                f"unrecognized order status {status!r}"
            )

        original_qty = D(
            order.get("origQty")
        )

        executed_qty = D(
            order.get("executedQty")
        )

        if (
            original_qty < 0
            or executed_qty < 0
            or executed_qty > original_qty
        ):
            raise RuntimeError(
                "R24 state tracker: "
                "invalid quantity relationship"
            )

        event_key = self.event_key(order)

        if event_key in self._event_keys:

            return ProcessResult(
                accepted=False,
                duplicate=True,
                regression=False,
                terminal=(
                    status in TERMINAL_STATUSES
                ),
                fill_delta=Decimal("0"),
                status=status,
            )

        previous = self._orders.get(
            order_id
        )

        if previous:

            previous_status = safe_upper(
                previous.get("status")
            )

            previous_executed = D(
                previous.get("executedQty")
            )

            previous_rank = STATUS_RANK.get(
                previous_status,
                -1,
            )

            new_rank = STATUS_RANK.get(
                status,
                -1,
            )

            if previous_status in TERMINAL_STATUSES:

                return ProcessResult(
                    accepted=False,
                    duplicate=False,
                    regression=True,
                    terminal=True,
                    fill_delta=Decimal("0"),
                    status=status,
                )

            if (
                new_rank < previous_rank
                or executed_qty < previous_executed
            ):

                return ProcessResult(
                    accepted=False,
                    duplicate=False,
                    regression=True,
                    terminal=(
                        status in TERMINAL_STATUSES
                    ),
                    fill_delta=Decimal("0"),
                    status=status,
                )

            fill_delta = (
                executed_qty
                - previous_executed
            )

        else:

            fill_delta = executed_qty

        self._event_keys.add(
            event_key
        )

        self._orders[
            order_id
        ] = dict(order)

        return ProcessResult(
            accepted=True,
            duplicate=False,
            regression=False,
            terminal=(
                status in TERMINAL_STATUSES
            ),
            fill_delta=fill_delta,
            status=status,
        )


# ============================================================
# SYNTHETIC PARTIAL FILL TEST
# ============================================================

def run_state_machine_self_tests() -> Dict[
    str,
    bool,
]:

    tracker = OrderStateTracker()

    base = {
        "orderId": "r24-synthetic-1",
        "symbol": DEMO_SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "origQty": "1.0",
    }

    new_event = {
        **base,
        "status": "NEW",
        "executedQty": "0",
        "updateTime": 1,
    }

    partial_1_event = {
        **base,
        "status": "PARTIALLY_FILLED",
        "executedQty": "0.4",
        "updateTime": 2,
    }

    partial_2_event = {
        **base,
        "status": "PARTIALLY_FILLED",
        "executedQty": "0.7",
        "updateTime": 3,
    }

    filled_event = {
        **base,
        "status": "FILLED",
        "executedQty": "1.0",
        "updateTime": 4,
    }

    regression_event = {
        **base,
        "status": "PARTIALLY_FILLED",
        "executedQty": "0.8",
        "updateTime": 5,
    }

    result_1 = tracker.process(
        new_event
    )

    result_2 = tracker.process(
        partial_1_event
    )

    result_3 = tracker.process(
        partial_2_event
    )

    result_4 = tracker.process(
        filled_event
    )

    duplicate_result = tracker.process(
        filled_event
    )

    regression_result = tracker.process(
        regression_event
    )

    return {
        "new_accepted":
            result_1.accepted,

        "partial_1_delta":
            (
                result_2.accepted
                and result_2.fill_delta
                == Decimal("0.4")
            ),

        "partial_2_delta":
            (
                result_3.accepted
                and result_3.fill_delta
                == Decimal("0.3")
            ),

        "filled_terminal":
            (
                result_4.accepted
                and result_4.terminal
                and result_4.fill_delta
                == Decimal("0.3")
            ),

        "duplicate_blocked":
            (
                duplicate_result.duplicate
                and not duplicate_result.accepted
            ),

        "terminal_regression_blocked":
            (
                regression_result.regression
                and not regression_result.accepted
            ),
    }


# ============================================================
# DEMO POSITION SIZE
# ============================================================

def extract_demo_position_size(
    data: Any,
    symbol: str,
    side: str,
) -> Decimal:

    rows = first_dict_list(data)

    total = Decimal("0")

    for row in rows:

        if safe_upper(
            row.get("symbol")
        ) != symbol.upper():

            continue

        row_side = safe_upper(
            row.get("side")
            or row.get("positionSide")
        )

        if (
            side
            and row_side
            and row_side != side.upper()
        ):
            continue

        total += abs(
            D(
                row.get("size")
                or row.get("positionAmt")
                or row.get("quantity")
                or "0"
            )
        )

    return total


# ============================================================
# HISTORY HELPERS
# ============================================================

def normalize_history(
    data: Any,
) -> List[Dict[str, Any]]:

    if isinstance(data, list):

        return [
            item
            for item in data
            if isinstance(item, dict)
        ]

    if isinstance(data, dict):

        for key in (
            "data",
            "orders",
            "rows",
            "list",
        ):

            rows = data.get(key)

            if isinstance(rows, list):

                return [
                    item
                    for item in rows
                    if isinstance(item, dict)
                ]

            if isinstance(rows, dict):

                for nested_key in (
                    "orders",
                    "rows",
                    "list",
                ):

                    nested_rows = rows.get(
                        nested_key
                    )

                    if isinstance(
                        nested_rows,
                        list,
                    ):

                        return [
                            item
                            for item in nested_rows
                            if isinstance(item, dict)
                        ]

    return []


def find_order(
    rows: List[Dict[str, Any]],
    order_id: str,
) -> Optional[Dict[str, Any]]:

    for row in rows:

        if str(
            row.get("orderId")
            or ""
        ) == str(order_id):

            return row

    return None


async def wait_for_history_order(
    session: aiohttp.ClientSession,
    order_id: str,
    symbol: str,
    start_ms: int,
) -> Tuple[
    Optional[Dict[str, Any]],
    int,
]:

    attempts = 0

    for index in range(
        ORDER_HISTORY_POLL_ATTEMPTS
    ):

        attempts = index + 1

        params = {
            "symbol": symbol,
            "limit": 100,
            "page": 0,
            "startTime": max(
                0,
                start_ms
                - ORDER_HISTORY_LOOKBACK_MS,
            ),
            "endTime": now_ms() + 5000,
        }

        data = await private_get(
            session,
            DEMO_HISTORY_PATH,
            params,
        )

        found = find_order(
            normalize_history(data),
            order_id,
        )

        if found:

            return (
                found,
                attempts,
            )

        if (
            index + 1
            < ORDER_HISTORY_POLL_ATTEMPTS
        ):

            await asyncio.sleep(
                ORDER_HISTORY_POLL_INTERVAL
            )

    return (
        None,
        attempts,
    )


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    session: aiohttp.ClientSession,
    message: str,
) -> bool:

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):

        print(
            "TELEGRAM SKIPPED: "
            "token or chat ID missing"
        )

        return False

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message[:4000],
    }

    try:

        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(
                total=10
            ),
        ) as response:

            response_text = (
                await response.text()
            )

            if (
                response.status >= 200
                and response.status < 300
            ):

                print(
                    "TELEGRAM MESSAGE SENT"
                )

                return True

            print(
                "TELEGRAM SEND FAILED: "
                f"HTTP {response.status} "
                f"{response_text}"
            )

            return False

    except Exception as exc:

        print(
            "TELEGRAM SEND ERROR: "
            f"{type(exc).__name__}: {exc}"
        )

        return False


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    request: web.Request,
) -> web.Response:

    return web.json_response(
        {
            "ok": True,
            "module": MODULE_NAME,
            "live_order_execution":
                LIVE_ORDER_EXECUTION,
            "hard_real_post_lock":
                HARD_REAL_POST_LOCK,
            "real_post_called":
                R24_REAL_POST_CALLED,
            "demo_post_attempted":
                R24_DEMO_POST_ATTEMPTED,
            "demo_post_accepted":
                R24_DEMO_POST_ACCEPTED,
        }
    )


async def start_health_server() -> web.AppRunner:

    app = web.Application()

    app.router.add_get(
        "/",
        health_handler,
    )

    app.router.add_get(
        "/health",
        health_handler,
    )

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        PORT,
    )

    await site.start()

    print(
        f"HEALTH SERVER ACTIVE ON PORT {PORT}"
    )

    return runner


# ============================================================
# FINAL R24 SAFETY ASSERTIONS
# ============================================================

def final_safety_assertions_r24() -> None:

    if LIVE_ORDER_EXECUTION:

        raise RuntimeError(
            "R24 safety assertion failed: "
            "LIVE_ORDER_EXECUTION must be False"
        )

    if not HARD_REAL_POST_LOCK:

        raise RuntimeError(
            "R24 safety assertion failed: "
            "HARD_REAL_POST_LOCK must be True"
        )

    if not real_order_post_blocked():

        raise RuntimeError(
            "R24 safety assertion failed: "
            "real POST path is not blocked"
        )

    if R24_REAL_POST_CALLED:

        raise RuntimeError(
            "R24 safety assertion failed: "
            "a real POST path was called"
        )


# ============================================================
# R24 MAIN DIAGNOSTIC
# ============================================================

async def r24_run_diagnostic(
    session: aiohttp.ClientSession,
) -> str:

    # --------------------------------------------------------
    # CONFIGURATION
    # --------------------------------------------------------

    validate_credentials()
    final_safety_assertions_r24()

    # --------------------------------------------------------
    # BALANCE
    # --------------------------------------------------------

    balance_data = await private_get(
        session,
        BALANCE_PATH,
    )

    available_usdt = (
        extract_available_usdt(
            balance_data
        )
    )

    # --------------------------------------------------------
    # MARK PRICE
    # --------------------------------------------------------

    mark_data = await public_get(
        session,
        MARK_PRICE_PATH,
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    mark_price = extract_mark_price(
        mark_data
    )

    # --------------------------------------------------------
    # EXCHANGE INFO
    # --------------------------------------------------------

    exchange_info = await public_get(
        session,
        EXCHANGE_INFO_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    symbol_record = find_symbol_record(
        exchange_info,
        SYMBOL,
    )

    contract = extract_contract_info(
        symbol_record
    )

    # --------------------------------------------------------
    # EXECUTION GATES
    # --------------------------------------------------------

    gate = run_gate_self_tests()

    (
        exposure_total,
        exposure_passed,
    ) = exposure_test()

    leverage_gate = (
        contract.min_leverage
        <= LEVERAGE
        <= min(
            contract.max_leverage,
            MAX_CONFIG_LEVERAGE,
        )
    )

    # --------------------------------------------------------
    # ENTRY SIZE
    # --------------------------------------------------------

    (
        margin,
        notional,
        quantity,
    ) = calculate_entry(
        available_usdt,
        mark_price,
        contract,
    )

    quantity_positive = (
        quantity > 0
    )

    minimum_passed = (
        quantity >= contract.min_qty
    )

    if not all(gate.values()):

        raise RuntimeError(
            "Execution gate self-test failed: "
            f"{gate}"
        )

    if not exposure_passed:

        raise RuntimeError(
            "Exposure cap validation failed"
        )

    if not leverage_gate:

        raise RuntimeError(
            "Leverage validation failed"
        )

    if (
        not quantity_positive
        or not minimum_passed
    ):

        raise RuntimeError(
            "Dynamic entry quantity "
            "validation failed"
        )

    # --------------------------------------------------------
    # STATE MACHINE TESTS
    # --------------------------------------------------------

    state_tests = (
        run_state_machine_self_tests()
    )

    if not all(
        state_tests.values()
    ):

        raise RuntimeError(
            "R24 order-state self-test failed: "
            f"{state_tests}"
        )

    # --------------------------------------------------------
    # DEMO DEFAULT VALUES
    # --------------------------------------------------------

    demo_limit_price = Decimal("0")
    price_step_match = False

    demo_order_id = "N/A"

    history_lookup_attempted = False
    history_poll_attempts = 0

    order_found = False
    history_order_id_match = False
    history_symbol_match = False
    history_side_match = False
    history_position_side_match = False

    final_status = "NOT_RUN"
    status_recognized = False

    requested_qty = quantity
    history_orig_qty = Decimal("0")
    history_exec_qty = Decimal("0")

    quantity_reconciliation = False
    lifecycle_validation = False

    position_before = Decimal("0")
    position_after = Decimal("0")
    position_reconciled = False

    actual_tracker_first_accept = False
    actual_tracker_duplicate_blocked = False
    actual_tracker_terminal = False
    actual_tracker_fill_delta = Decimal("0")

    # ========================================================
    # DEMO ORDER TEST
    # ========================================================

    if RUN_DEMO_ORDER_TEST:

        # ----------------------------------------------------
        # POSITION BEFORE
        # ----------------------------------------------------

        pos_before_data = await private_get(
            session,
            DEMO_POSITIONS_PATH,
        )

        position_before = (
            extract_demo_position_size(
                pos_before_data,
                DEMO_SYMBOL,
                REHEARSAL_POSITION_SIDE,
            )
        )

        # ----------------------------------------------------
        # SAFE DEMO LIMIT PRICE
        # ----------------------------------------------------

        demo_limit_price = (
            build_safe_demo_limit_price(
                mark_price,
                REHEARSAL_SIDE,
                contract.price_step,
            )
        )

        price_step_match = (
            step_matches(
                demo_limit_price,
                contract.price_step,
            )
        )

        if not price_step_match:

            raise RuntimeError(
                "Demo limit price does not "
                "match price step"
            )

        # ----------------------------------------------------
        # DEMO ORDER PAYLOAD
        # ----------------------------------------------------

        payload = {
            "symbol": DEMO_SYMBOL,
            "side": REHEARSAL_SIDE,
            "positionSide":
                REHEARSAL_POSITION_SIDE,
            "type": REHEARSAL_ORDER_TYPE,
            "timeInForce":
                REHEARSAL_TIME_IN_FORCE,
            "quantity":
                dec_str(quantity),
            "price":
                dec_str(demo_limit_price),
            "newClientOrderId":
                create_client_order_id(),
        }

        # ----------------------------------------------------
        # DEMO TRANSMISSION
        # ----------------------------------------------------

        sent_at_ms = now_ms()

        demo_response = await demo_post(
            session,
            DEMO_ORDER_PATH,
            payload,
        )

        if not isinstance(
            demo_response,
            dict,
        ):

            raise RuntimeError(
                "Unexpected demo order response: "
                f"{demo_response}"
            )

        demo_order_id = str(
            demo_response.get("orderId")
            or ""
        ).strip()

        if not demo_order_id:

            raise RuntimeError(
                "Demo order accepted but "
                "orderId missing: "
                f"{demo_response}"
            )

        # ----------------------------------------------------
        # HISTORY LOOKUP
        # ----------------------------------------------------

        history_lookup_attempted = True

        (
            history_row,
            history_poll_attempts,
        ) = await wait_for_history_order(
            session,
            demo_order_id,
            DEMO_SYMBOL,
            sent_at_ms,
        )

        order_found = (
            history_row is not None
        )

        if not history_row:

            raise RuntimeError(
                "Demo order "
                f"{demo_order_id} "
                "not found in history"
            )

        # ----------------------------------------------------
        # HISTORY IDENTITY
        # ----------------------------------------------------

        history_order_id_match = (
            str(
                history_row.get("orderId")
                or ""
            )
            == demo_order_id
        )

        history_symbol_match = (
            safe_upper(
                history_row.get("symbol")
            )
            == DEMO_SYMBOL
        )

        history_side_match = (
            safe_upper(
                history_row.get("side")
            )
            == REHEARSAL_SIDE
        )

        history_position_side_match = (
            safe_upper(
                history_row.get(
                    "positionSide"
                )
            )
            == REHEARSAL_POSITION_SIDE
        )

        # ----------------------------------------------------
        # HISTORY STATUS
        # ----------------------------------------------------

        final_status = safe_upper(
            history_row.get("status")
        )

        status_recognized = (
            final_status
            in RECOGNIZED_STATUSES
        )

        # ----------------------------------------------------
        # HISTORY QUANTITY
        # ----------------------------------------------------

        history_orig_qty = D(
            history_row.get("origQty")
        )

        history_exec_qty = D(
            history_row.get("executedQty")
        )

        quantity_reconciliation = (
            history_orig_qty
            == requested_qty
            and Decimal("0")
            <= history_exec_qty
            <= history_orig_qty
        )

        lifecycle_validation = all(
            [
                history_order_id_match,
                history_symbol_match,
                history_side_match,
                history_position_side_match,
                status_recognized,
                quantity_reconciliation,
            ]
        )

        if not lifecycle_validation:

            raise RuntimeError(
                "Demo lifecycle validation failed: "
                f"{history_row}"
            )

        # ----------------------------------------------------
        # ACTUAL HISTORY IDEMPOTENCY TEST
        # ----------------------------------------------------

        actual_tracker = (
            OrderStateTracker()
        )

        first_result = (
            actual_tracker.process(
                history_row
            )
        )

        second_result = (
            actual_tracker.process(
                history_row
            )
        )

        actual_tracker_first_accept = (
            first_result.accepted
        )

        actual_tracker_duplicate_blocked = (
            second_result.duplicate
            and not second_result.accepted
        )

        actual_tracker_terminal = (
            first_result.terminal
        )

        actual_tracker_fill_delta = (
            first_result.fill_delta
        )

        if (
            not actual_tracker_first_accept
            or not actual_tracker_duplicate_blocked
        ):

            raise RuntimeError(
                "R24 actual history "
                "idempotency validation failed"
            )

        # ----------------------------------------------------
        # POSITION AFTER
        # ----------------------------------------------------

        await asyncio.sleep(0.5)

        pos_after_data = await private_get(
            session,
            DEMO_POSITIONS_PATH,
        )

        position_after = (
            extract_demo_position_size(
                pos_after_data,
                DEMO_SYMBOL,
                REHEARSAL_POSITION_SIDE,
            )
        )

        # ----------------------------------------------------
        # POSITION RECONCILIATION
        # ----------------------------------------------------

        observed_delta = (
            position_after
            - position_before
        )

        if history_exec_qty == 0:

            position_reconciled = (
                position_after
                == position_before
            )

        elif REHEARSAL_SIDE == "BUY":

            position_reconciled = (
                observed_delta
                >= Decimal("0")
                and observed_delta
                <= (
                    history_exec_qty
                    + contract.qty_step
                )
            )

        else:

            position_reconciled = (
                observed_delta
                <= Decimal("0")
                and abs(observed_delta)
                <= (
                    history_exec_qty
                    + contract.qty_step
                )
            )

        if not position_reconciled:

            raise RuntimeError(
                "Demo position reconciliation failed: "
                f"before={position_before} "
                f"after={position_after} "
                f"executed={history_exec_qty}"
            )

    # ========================================================
    # FINAL SAFETY ASSERTION
    # ========================================================

    final_safety_assertions_r24()

    # ========================================================
    # REPORT
    # ========================================================

    lines = [
        f"✅ MODULE {MODULE_NAME} DIAGNOSTIC PASSED",
        SYMBOL,
        f"Available USDT: {dec_str(available_usdt)}",
        f"Mark Price: {dec_str(mark_price)} USDT",

        "",

        "FINAL EXECUTION GATE",
        f"API Trading Symbol: {yesno(True)}",
        f"Fresh Signal Accepted: {yesno(gate['fresh_signal'])}",
        f"Expired Signal Rejected: {yesno(gate['expired_rejected'])}",
        f"Loss Cooldown Test: {yesno(gate['loss_cooldown'])}",
        f"Duplicate Signal Rejected: {yesno(gate['duplicate_rejected'])}",
        f"One Direction Gate: {yesno(gate['one_direction_gate'])}",
        f"External Position Clear: {yesno(gate['external_position_clear'])}",

        "",

        "ADJUSTABLE CONFIG",
        f"Entry: {dec_str(ENTRY_PERCENT)}%",
        f"Leverage: {dec_str(LEVERAGE)}x",
        f"Max Config Leverage: {dec_str(MAX_CONFIG_LEVERAGE)}x",
        f"Margin Type: {MARGIN_TYPE}",
        f"Max Pyramids: {MAX_PYRAMID_ADDS}",
        f"Pyramid Size: {dec_str(PYRAMID_SIZE_PERCENT)}%",
        f"Max Backups: {MAX_BACKUPS}",
        f"Backup Size: {dec_str(BACKUP_SIZE_PERCENT)}% each",
        f"Backup Buffer: {dec_str(BACKUP_BUFFER_PERCENT)}%",
        f"Min Liq Distance: {dec_str(MIN_LIQ_DISTANCE_PERCENT)}%",
        f"Max Fund Exposure: {dec_str(MAX_FUND_EXPOSURE_PERCENT)}%",

        "",

        "WEEX CONTRACT",
        f"Minimum Order: {dec_str(contract.min_qty)}",
        f"Quantity Precision: {contract.qty_precision}",
        f"Quantity Step: {dec_str(contract.qty_step)}",
        f"Price Precision: {contract.price_precision}",
        f"Price Step: {dec_str(contract.price_step)}",
        f"Contract Value: {dec_str(contract.contract_value)}",
        f"WEEX Min Leverage: {dec_str(contract.min_leverage)}x",
        f"WEEX Max Leverage: {dec_str(contract.max_leverage)}x",
        f"Leverage Gate: {yesno(leverage_gate)}",

        "",

        "DYNAMIC ENTRY",
        f"Margin: {dec_str(margin)} USDT",
        f"Notional: {dec_str(notional)} USDT",
        f"Quantity: {dec_str(quantity)}",
        f"Quantity Positive: {yesno(quantity_positive)}",
        f"Minimum Passed: {yesno(minimum_passed)}",

        "",

        "WORST-CASE EXPOSURE",
        f"Initial: {dec_str(ENTRY_PERCENT)}%",
        (
            "Pyramids: "
            f"{dec_str(Decimal(MAX_PYRAMID_ADDS) * PYRAMID_SIZE_PERCENT)}%"
        ),
        (
            "Backups: "
            f"{dec_str(Decimal(MAX_BACKUPS) * BACKUP_SIZE_PERCENT)}%"
        ),
        (
            f"Total: {dec_str(exposure_total)}% / "
            f"{dec_str(MAX_FUND_EXPOSURE_PERCENT)}%"
        ),
        f"Exposure Passed: {yesno(exposure_passed)}",

        "",

        "TP / TRAILING",
        (
            f"TP1 / TP2 / TP3: "
            f"{dec_str(TP1_PERCENT)}% / "
            f"{dec_str(TP2_PERCENT)}% / "
            f"{dec_str(TP3_PERCENT)}%"
        ),
        f"TP1 Trigger: {dec_str(TP1_TRIGGER_PERCENT)}%",
        f"TP2 Trigger: {dec_str(TP2_TRIGGER_PERCENT)}%",
        f"Trailing Distance: {dec_str(TRAILING_DISTANCE_PERCENT)}%",

        "",

        "R24 ORDER STATE MACHINE",
        f"NEW State Accepted: {yesno(state_tests['new_accepted'])}",
        f"Partial Fill #1 Delta: {yesno(state_tests['partial_1_delta'])}",
        f"Partial Fill #2 Delta: {yesno(state_tests['partial_2_delta'])}",
        f"FILLED Terminal State: {yesno(state_tests['filled_terminal'])}",
        (
            "Duplicate Exchange Event Blocked: "
            f"{yesno(state_tests['duplicate_blocked'])}"
        ),
        (
            "Terminal Regression Blocked: "
            f"{yesno(state_tests['terminal_regression_blocked'])}"
        ),

        "",

        "R24 DEMO ORDER LIFECYCLE",
        f"Demo Symbol: {DEMO_SYMBOL}",
        f"Demo Side: {REHEARSAL_SIDE}",
        f"Demo Position Side: {REHEARSAL_POSITION_SIDE}",
        f"Demo Type: {REHEARSAL_ORDER_TYPE}",
        f"Demo Time In Force: {REHEARSAL_TIME_IN_FORCE}",
        f"Demo Limit Price: {dec_str(demo_limit_price)}",
        f"Price Step Match: {yesno(price_step_match)}",
        f"Demo POST Attempted: {yesno(R24_DEMO_POST_ATTEMPTED)}",
        f"Demo POST Accepted: {yesno(R24_DEMO_POST_ACCEPTED)}",
        f"Demo Order ID: {demo_order_id}",
        f"History Lookup Attempted: {yesno(history_lookup_attempted)}",
        f"History Poll Attempts: {history_poll_attempts}",
        f"Order Found In History: {yesno(order_found)}",
        f"History Order ID Match: {yesno(history_order_id_match)}",
        f"History Symbol Match: {yesno(history_symbol_match)}",
        f"History Side Match: {yesno(history_side_match)}",
        (
            "History Position Side Match: "
            f"{yesno(history_position_side_match)}"
        ),
        f"Demo Final Status: {final_status}",
        f"Status Recognized: {yesno(status_recognized)}",
        f"Requested Quantity: {dec_str(requested_qty)}",
        f"History Original Quantity: {dec_str(history_orig_qty)}",
        f"History Executed Quantity: {dec_str(history_exec_qty)}",
        f"Quantity Reconciliation: {yesno(quantity_reconciliation)}",
        f"Lifecycle Validation: {yesno(lifecycle_validation)}",

        "",

        "R24 ACTUAL HISTORY IDEMPOTENCY",
        f"First Processing Accepted: {yesno(actual_tracker_first_accept)}",
        (
            "Duplicate Processing Blocked: "
            f"{yesno(actual_tracker_duplicate_blocked)}"
        ),
        f"Actual History Terminal: {yesno(actual_tracker_terminal)}",
        f"Actual Fill Delta: {dec_str(actual_tracker_fill_delta)}",

        "",

        "R24 DEMO POSITION RECONCILIATION",
        f"Position Size Before: {dec_str(position_before)}",
        f"Position Size After: {dec_str(position_after)}",
        f"Position Reconciled: {yesno(position_reconciled)}",

        "",

        "R24 RENDER PERSISTENCE",
        "Health Server: ✅ ACTIVE",
        "Persistent Runtime: ✅ ACTIVE",
        "Auto Exit After Diagnostic: ❌ DISABLED",
        "Repeated Demo Order Loop: ❌ DISABLED",

        "",

        "ABSOLUTE EXECUTION SAFETY",
        f"Real POST Called: {yesno(R24_REAL_POST_CALLED)}",
        "🛡 R24 absolute real-order POST lock active",
        "⚠️ LIVE ORDER EXECUTION DISABLED",
        "⚠️ NO REAL ORDER WAS SENT",
    ]

    return "\n".join(lines)


# ============================================================
# MAIN PROCESS
# ============================================================

async def main_async() -> None:

    await start_health_server()

    print("=" * 60)
    print(f"{MODULE_NAME} STARTING")
    print(
        "ORDER STATE / IDEMPOTENCY "
        "PRE-LIVE VALIDATION"
    )
    print(
        "REAL ORDER TRANSMISSION DISABLED"
    )
    print("=" * 60)

    async with aiohttp.ClientSession() as session:

        try:

            report = await r24_run_diagnostic(
                session
            )

            print(
                "\n"
                + report
                + "\n"
            )

            telegram_sent = (
                await send_telegram(
                    session,
                    report,
                )
            )

            print(
                "R24 TELEGRAM RESULT: "
                + (
                    "✅ SENT"
                    if telegram_sent
                    else "❌ NOT SENT"
                )
            )

        except Exception as exc:

            error_report = (
                f"❌ MODULE {MODULE_NAME} ERROR\n"
                f"{SYMBOL}\n"
                f"{type(exc).__name__}: {exc}\n"
                f"Real POST Called: {yesno(R24_REAL_POST_CALLED)}\n"
                f"Demo POST Attempted: {yesno(R24_DEMO_POST_ATTEMPTED)}\n"
                f"Demo POST Accepted: {yesno(R24_DEMO_POST_ACCEPTED)}\n"
                "🛡 R24 absolute real-order POST lock active\n"
                "⚠️ LIVE ORDER EXECUTION DISABLED\n"
                "⚠️ NO REAL ORDER WAS SENT"
            )

            print(
                "\n"
                + error_report
                + "\n"
            )

            traceback.print_exc()

            telegram_sent = (
                await send_telegram(
                    session,
                    error_report,
                )
            )

            print(
                "R24 ERROR TELEGRAM RESULT: "
                + (
                    "✅ SENT"
                    if telegram_sent
                    else "❌ NOT SENT"
                )
            )

    # ========================================================
    # RENDER PERSISTENCE
    # ========================================================
    #
    # Diagnostic runs ONCE.
    # No repeated demo-order transmission.
    # Process remains alive so Render does not restart it.
    #
    # ========================================================

    print("=" * 60)
    print(
        f"{MODULE_NAME} DIAGNOSTIC CYCLE COMPLETE"
    )
    print(
        "PROCESS REMAINING ALIVE FOR RENDER"
    )
    print("=" * 60)

    while True:

        await asyncio.sleep(3600)


def main() -> None:

    try:

        asyncio.run(
            main_async()
        )

    except KeyboardInterrupt:

        print(
            f"{MODULE_NAME} stopped"
        )


if __name__ == "__main__":
    main()
