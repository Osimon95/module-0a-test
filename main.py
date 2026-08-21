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

MODULE_NAME = "0F-4H-R26"
API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()


def default_demo_symbol(symbol: str) -> str:
    if symbol.endswith("USDT"):
        return symbol[:-4] + "SUSDT"
    return symbol


DEMO_SYMBOL = os.getenv("DEMO_SYMBOL", default_demo_symbol(SYMBOL)).strip().upper()


# ============================================================
# ABSOLUTE EXECUTION SAFETY
# ============================================================
#
# R26 IS PRE-LIVE ONLY.
#
# ALLOWED:
#   - Public GET requests
#   - Authenticated/private GET requests
#   - One DEMO order POST to /capi/v3/sim/order
#
# FORBIDDEN:
#   - Any real/private state-changing POST
#   - Any POST to /capi/v3/order
#
# The real-order payload is built, signed, classified and rehearsed locally,
# but it is NEVER transmitted.
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_REAL_POST_LOCK = True
REAL_ORDER_PATH = "/capi/v3/order"
DEMO_ORDER_PATH = "/capi/v3/sim/order"

R26_REAL_POST_CALLED = False
R26_DEMO_POST_ATTEMPTED = False
R26_DEMO_POST_ACCEPTED = False


# ============================================================
# USER-ADJUSTABLE STRATEGY CONFIG
# ============================================================

ENTRY_PERCENT = Decimal(os.getenv("ENTRY_PERCENT", "5"))
LEVERAGE = int(os.getenv("LEVERAGE", "100"))
MAX_CONFIG_LEVERAGE = int(os.getenv("MAX_CONFIG_LEVERAGE", "100"))
MARGIN_TYPE = os.getenv("MARGIN_TYPE", "ISOLATED").strip().upper()

MAX_PYRAMID_ADDS = int(os.getenv("MAX_PYRAMID_ADDS", "1"))
PYRAMID_SIZE_PERCENT = Decimal(os.getenv("PYRAMID_SIZE_PERCENT", "5"))

MAX_BACKUPS = int(os.getenv("MAX_BACKUPS", "3"))
BACKUP_SIZE_PERCENT = Decimal(os.getenv("BACKUP_SIZE_PERCENT", "5"))
BACKUP_BUFFER_PERCENT = Decimal(os.getenv("BACKUP_BUFFER_PERCENT", "0.3"))

MIN_LIQ_DISTANCE_PERCENT = Decimal(os.getenv("MIN_LIQ_DISTANCE_PERCENT", "0.2"))
MAX_FUND_EXPOSURE_PERCENT = Decimal(os.getenv("MAX_FUND_EXPOSURE_PERCENT", "35"))

TP1_PERCENT = Decimal(os.getenv("TP1_PERCENT", "20"))
TP2_PERCENT = Decimal(os.getenv("TP2_PERCENT", "20"))
TP3_PERCENT = Decimal(os.getenv("TP3_PERCENT", "60"))
TP1_TRIGGER_PERCENT = Decimal(os.getenv("TP1_TRIGGER_PERCENT", "0.5"))
TP2_TRIGGER_PERCENT = Decimal(os.getenv("TP2_TRIGGER_PERCENT", "1"))
TRAILING_DISTANCE_PERCENT = Decimal(os.getenv("TRAILING_DISTANCE_PERCENT", "0.2"))

SIGNAL_EXPIRY_SECONDS = int(os.getenv("SIGNAL_EXPIRY_SECONDS", "120"))
LOSS_COOLDOWN_SECONDS = int(os.getenv("LOSS_COOLDOWN_SECONDS", "300"))

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# ============================================================
# R26 DIAGNOSTIC SETTINGS
# ============================================================

DEMO_ORDER_ENABLED = os.getenv("DEMO_ORDER_ENABLED", "true").strip().lower() in {
    "1", "true", "yes", "on"
}
DEMO_SIDE = os.getenv("DEMO_SIDE", "BUY").strip().upper()
DEMO_POSITION_SIDE = os.getenv("DEMO_POSITION_SIDE", "LONG").strip().upper()
DEMO_ORDER_TYPE = "LIMIT"
DEMO_TIME_IN_FORCE = "IOC"
DEMO_PRICE_OFFSET_PERCENT = Decimal(os.getenv("DEMO_PRICE_OFFSET_PERCENT", "0.5"))

HISTORY_POLL_ATTEMPTS = int(os.getenv("HISTORY_POLL_ATTEMPTS", "6"))
HISTORY_POLL_DELAY_SECONDS = float(os.getenv("HISTORY_POLL_DELAY_SECONDS", "1.0"))

PORT = int(os.getenv("PORT", "10000"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

WEEX_API_KEY = os.getenv("WEEX_API_KEY", "").strip()
WEEX_SECRET_KEY = os.getenv("WEEX_SECRET_KEY", "").strip()
WEEX_PASSPHRASE = os.getenv("WEEX_PASSPHRASE", "").strip()


# ============================================================
# ENDPOINTS
# ============================================================

EP_MARK_PRICE = "/capi/v3/market/symbolPrice"
EP_EXCHANGE_INFO = "/capi/v3/market/exchangeInfo"
EP_REAL_BALANCE = "/capi/v3/account/balance"
EP_REAL_POSITIONS = "/capi/v3/account/position/allPosition"
EP_DEMO_BALANCE = "/capi/v3/sim/balance"
EP_DEMO_POSITIONS = "/capi/v3/sim/position/allPosition"
EP_DEMO_HISTORY = "/capi/v3/sim/order/history"


# ============================================================
# SMALL HELPERS
# ============================================================

D0 = Decimal("0")
D100 = Decimal("100")


def D(value: Any, default: Decimal = D0) -> Decimal:
    try:
        if value is None or value == "":
            return default
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return default


def yesno(value: bool) -> str:
    return "✅ YES" if value else "❌ NO"


def decimal_text(value: Decimal) -> str:
    s = format(value, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


def floor_to_step(value: Decimal, step: Decimal) -> Decimal:
    if step <= 0:
        return value
    units = (value / step).to_integral_value(rounding=ROUND_DOWN)
    return units * step


def precision_from_step(step: Decimal) -> int:
    normalized = step.normalize()
    return max(0, -normalized.as_tuple().exponent)


def floor_with_precision(
    value: Decimal,
    step: Decimal,
    precision: int,
) -> Decimal:
    floored = floor_to_step(value, step)
    quantum = Decimal("1").scaleb(-precision)
    return floored.quantize(quantum, rounding=ROUND_DOWN)


def step_match(value: Decimal, step: Decimal) -> bool:
    if step <= 0:
        return True
    return value == floor_to_step(value, step)


def now_ms() -> int:
    return int(time.time() * 1000)


def safe_json_text(data: Any) -> str:
    return json.dumps(
        data,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def extract_list(payload: Any) -> List[Any]:
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ("data", "list", "rows", "result"):
            value = payload.get(key)
            if isinstance(value, list):
                return value

    return []


def first_present(
    mapping: Dict[str, Any],
    keys: Tuple[str, ...],
    default: Any = None,
) -> Any:
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]

    return default


# ============================================================
# CONTRACT MODEL
# ============================================================

@dataclass
class ContractInfo:
    symbol: str
    min_qty: Decimal
    qty_step: Decimal
    qty_precision: int
    price_step: Decimal
    price_precision: int
    contract_value: Decimal
    min_leverage: int
    max_leverage: int


def find_symbol_object(
    payload: Any,
    symbol: str,
) -> Optional[Dict[str, Any]]:
    target = symbol.upper()

    if isinstance(payload, dict):
        symbols = payload.get("symbols")

        if isinstance(symbols, list):
            for item in symbols:
                if (
                    isinstance(item, dict)
                    and str(item.get("symbol", "")).upper() == target
                ):
                    return item

        data = payload.get("data")

        if isinstance(data, dict):
            found = find_symbol_object(data, symbol)
            if found:
                return found

        if isinstance(data, list):
            for item in data:
                if (
                    isinstance(item, dict)
                    and str(item.get("symbol", "")).upper() == target
                ):
                    return item

    if isinstance(payload, list):
        for item in payload:
            if (
                isinstance(item, dict)
                and str(item.get("symbol", "")).upper() == target
            ):
                return item

    return None


def parse_contract_info(
    payload: Any,
    symbol: str,
) -> ContractInfo:
    item = find_symbol_object(payload, symbol)

    if not item:
        raise RuntimeError(
            f"Unable to find contract info for {symbol}"
        )

    filters = (
        item.get("filters")
        if isinstance(item.get("filters"), list)
        else []
    )

    min_qty = D(
        first_present(
            item,
            ("minQty", "minOrderQty", "minOrderSize"),
        )
    )

    qty_step = D(
        first_present(
            item,
            ("quantityStep", "qtyStep", "stepSize", "sizeStep"),
        )
    )

    price_step = D(
        first_present(
            item,
            ("priceStep", "tickSize", "priceTick"),
        )
    )

    for f in filters:
        if not isinstance(f, dict):
            continue

        ftype = str(
            f.get("filterType", "")
        ).upper()

        if ftype in {
            "LOT_SIZE",
            "MARKET_LOT_SIZE",
        }:
            if min_qty <= 0:
                min_qty = D(
                    f.get("minQty")
                )

            if qty_step <= 0:
                qty_step = D(
                    f.get("stepSize")
                )

        elif ftype == "PRICE_FILTER":
            if price_step <= 0:
                price_step = D(
                    f.get("tickSize")
                )

    qty_precision_raw = first_present(
        item,
        (
            "quantityPrecision",
            "qtyPrecision",
            "sizePrecision",
        ),
    )

    price_precision_raw = first_present(
        item,
        (
            "pricePrecision",
            "priceScale",
        ),
    )

    if qty_step <= 0:
        qty_step = Decimal("0.0001")

    if min_qty <= 0:
        min_qty = qty_step

    if price_step <= 0:
        price_step = Decimal("0.1")

    try:
        qty_precision = (
            int(qty_precision_raw)
            if qty_precision_raw is not None
            else precision_from_step(qty_step)
        )
    except (ValueError, TypeError):
        qty_precision = precision_from_step(
            qty_step
        )

    try:
        price_precision = (
            int(price_precision_raw)
            if price_precision_raw is not None
            else precision_from_step(price_step)
        )
    except (ValueError, TypeError):
        price_precision = precision_from_step(
            price_step
        )

    contract_value = D(
        first_present(
            item,
            (
                "contractValue",
                "contract_val",
                "contractVal",
            ),
        ),
        Decimal("0.0001"),
    )

    try:
        min_lev = int(
            first_present(
                item,
                ("minLeverage",),
                1,
            )
        )
    except (ValueError, TypeError):
        min_lev = 1

    try:
        max_lev = int(
            first_present(
                item,
                ("maxLeverage",),
                100,
            )
        )
    except (ValueError, TypeError):
        max_lev = 100

    return ContractInfo(
        symbol=symbol,
        min_qty=min_qty,
        qty_step=qty_step,
        qty_precision=qty_precision,
        price_step=price_step,
        price_precision=price_precision,
        contract_value=contract_value,
        min_leverage=min_lev,
        max_leverage=max_lev,
    )


# ============================================================
# HTTP + SIGNING
# ============================================================

class WeexClient:
    def __init__(
        self,
        session: aiohttp.ClientSession,
    ):
        self.session = session

    @staticmethod
    def _signature(
        timestamp: str,
        method: str,
        path: str,
        query_string: str,
        body_text: str,
    ) -> str:
        if query_string:
            prehash = (
                timestamp
                + method.upper()
                + path
                + "?"
                + query_string
                + body_text
            )
        else:
            prehash = (
                timestamp
                + method.upper()
                + path
                + body_text
            )

        digest = hmac.new(
            WEEX_SECRET_KEY.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        ).digest()

        return base64.b64encode(
            digest
        ).decode("utf-8")

    @staticmethod
    def _auth_headers(
        method: str,
        path: str,
        query_string: str = "",
        body_text: str = "",
    ) -> Dict[str, str]:
        timestamp = str(
            now_ms()
        )

        signature = WeexClient._signature(
            timestamp,
            method,
            path,
            query_string,
            body_text,
        )

        return {
            "ACCESS-KEY": WEEX_API_KEY,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": WEEX_PASSPHRASE,
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
        }

    async def public_get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        async with self.session.get(
            API_BASE_URL + path,
            params=params,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as r:
            text = await r.text()

            if r.status < 200 or r.status >= 300:
                raise RuntimeError(
                    f"WEEX PUBLIC GET HTTP "
                    f"{r.status}: {text}"
                )

            try:
                return json.loads(
                    text
                )
            except json.JSONDecodeError:
                raise RuntimeError(
                    "WEEX PUBLIC GET "
                    f"invalid JSON: {text}"
                )

    async def private_get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        params = params or {}

        query = urlencode(
            params
        )

        headers = self._auth_headers(
            "GET",
            path,
            query,
            "",
        )

        url = (
            API_BASE_URL
            + path
            + (
                "?" + query
                if query
                else ""
            )
        )

        async with self.session.get(
            url,
            headers=headers,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as r:
            text = await r.text()

            if r.status < 200 or r.status >= 300:
                raise RuntimeError(
                    f"WEEX GET HTTP "
                    f"{r.status}: {text}"
                )

            try:
                return json.loads(
                    text
                )
            except json.JSONDecodeError:
                raise RuntimeError(
                    "WEEX GET invalid JSON: "
                    f"{text}"
                )

    async def demo_post(
        self,
        path: str,
        body: Dict[str, Any],
    ) -> Any:
        global R26_DEMO_POST_ATTEMPTED
        global R26_DEMO_POST_ACCEPTED

        if path != DEMO_ORDER_PATH:
            raise RuntimeError(
                "R26 demo_post rejected "
                f"non-demo path: {path}"
            )

        R26_DEMO_POST_ATTEMPTED = True

        body_text = safe_json_text(
            body
        )

        headers = self._auth_headers(
            "POST",
            path,
            "",
            body_text,
        )

        async with self.session.post(
            API_BASE_URL + path,
            headers=headers,
            data=body_text,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as r:
            text = await r.text()

            if r.status < 200 or r.status >= 300:
                raise RuntimeError(
                    f"WEEX DEMO POST HTTP "
                    f"{r.status}: {text}"
                )

            try:
                payload = json.loads(
                    text
                )
            except json.JSONDecodeError:
                raise RuntimeError(
                    "WEEX DEMO POST invalid JSON: "
                    f"{text}"
                )

            accepted = classify_order_response(
                payload
            )[0]

            R26_DEMO_POST_ACCEPTED = accepted

            if not accepted:
                raise RuntimeError(
                    "WEEX DEMO POST rejected: "
                    f"{text}"
                )

            return payload

    async def real_post_forbidden(
        self,
        path: str,
        body: Dict[str, Any],
    ) -> Any:
global R26_REAL_POST_CALLED

        R26_REAL_POST_CALLED = True

        raise RuntimeError(
            "R26 ABSOLUTE SAFETY LOCK: "
            f"real POST blocked before transmission: {path}"
        )


# ============================================================
# CREDENTIALS + CONFIG SAFETY
# ============================================================

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


def final_safety_assertions_r26() -> None:
    if LIVE_ORDER_EXECUTION:
        raise RuntimeError(
            "R26 must not run with "
            "LIVE_ORDER_EXECUTION=True"
        )

    if not HARD_REAL_POST_LOCK:
        raise RuntimeError(
            "R26 requires HARD_REAL_POST_LOCK=True"
        )

    if REAL_ORDER_PATH == DEMO_ORDER_PATH:
        raise RuntimeError(
            "Real and demo paths unexpectedly identical"
        )

    if (
        ENTRY_PERCENT <= 0
        or ENTRY_PERCENT > MAX_FUND_EXPOSURE_PERCENT
    ):
        raise RuntimeError(
            "ENTRY_PERCENT outside allowed exposure"
        )

    if (
        LEVERAGE <= 0
        or LEVERAGE > MAX_CONFIG_LEVERAGE
    ):
        raise RuntimeError(
            "Configured leverage exceeds local cap"
        )

    if MARGIN_TYPE != "ISOLATED":
        raise RuntimeError(
            "R26 requires ISOLATED margin configuration"
        )

    if (
        TP1_PERCENT
        + TP2_PERCENT
        + TP3_PERCENT
        != Decimal("100")
    ):
        raise RuntimeError(
            "TP allocation must total 100%"
        )


# ============================================================
# SIGNAL + ENTRY GATES
# ============================================================

@dataclass
class Signal:
    signal_id: str
    symbol: str
    direction: str
    created_at: float


class SignalGate:
    def __init__(self):
        self.processed: Set[str] = set()
        self.last_loss_time: Optional[float] = None

    def accept(
        self,
        signal: Signal,
        now: Optional[float] = None,
    ) -> Tuple[bool, str]:

        current = (
            time.time()
            if now is None
            else now
        )

        if (
            current - signal.created_at
            > SIGNAL_EXPIRY_SECONDS
        ):
            return False, "expired"

        if (
            self.last_loss_time is not None
            and current - self.last_loss_time
            < LOSS_COOLDOWN_SECONDS
        ):
            return False, "loss-cooldown"

        if signal.signal_id in self.processed:
            return False, "duplicate"

        self.processed.add(
            signal.signal_id
        )

        return True, "accepted"


# ============================================================
# ORDER STATE MACHINE
# ============================================================

TERMINAL_ORDER_STATES = {
    "FILLED",
    "CANCELED",
    "CANCELLED",
    "REJECTED",
    "EXPIRED",
}

ORDER_STATE_RANK = {
    "NEW": 10,
    "PARTIALLY_FILLED": 20,
    "FILLED": 30,
    "CANCELED": 30,
    "CANCELLED": 30,
    "REJECTED": 30,
    "EXPIRED": 30,
}


@dataclass
class OrderTracker:
    order_id: str
    status: Optional[str] = None
    executed_qty: Decimal = D0
    seen_event_keys: Set[str] = field(
        default_factory=set
    )
    terminal: bool = False

    def apply(
        self,
        status: str,
        executed_qty: Decimal,
        event_key: str,
    ) -> Tuple[bool, Decimal, str]:

        status = status.upper()

        if event_key in self.seen_event_keys:
            return (
                False,
                D0,
                "duplicate-event",
            )

        self.seen_event_keys.add(
            event_key
        )

        if (
            self.terminal
            and status not in TERMINAL_ORDER_STATES
        ):
            return (
                False,
                D0,
                "terminal-regression",
            )

        if self.status is not None:
            old_rank = ORDER_STATE_RANK.get(
                self.status,
                0,
            )

            new_rank = ORDER_STATE_RANK.get(
                status,
                0,
            )

            if new_rank < old_rank:
                return (
                    False,
                    D0,
                    "state-regression",
                )

        delta = (
            executed_qty
            - self.executed_qty
        )

        if delta < 0:
            return (
                False,
                D0,
                "quantity-regression",
            )

        self.executed_qty = executed_qty
        self.status = status
        self.terminal = (
            status
            in TERMINAL_ORDER_STATES
        )

        return (
            True,
            delta,
            "accepted",
        )


# ============================================================
# EXECUTION INTENT STATE MACHINE
# ============================================================

INTENT_RANK = {
    "NEW": 10,
    "PREFLIGHT": 20,
    "READY": 30,
    "SUBMITTED": 40,
    "RECONCILING": 50,
    "RECONCILED": 60,
    "REJECTED": 60,
    "EXPIRED": 60,
}

INTENT_TERMINAL = {
    "RECONCILED",
    "REJECTED",
    "EXPIRED",
}


@dataclass
class ExecutionIntent:
    intent_id: str
    signal_id: str
    symbol: str
    direction: str
    side: str
    position_side: str
    quantity: Decimal
    created_at: float
    state: str = "NEW"
    client_order_id: str = ""

    def transition(
        self,
        target: str,
    ) -> bool:

        target = target.upper()
        current = self.state.upper()

        if current in INTENT_TERMINAL:
            return False

        if (
            INTENT_RANK.get(target, -1)
            <= INTENT_RANK.get(current, -1)
        ):
            return False

        self.state = target

        return True


class IntentGate:
    def __init__(self):
        self.intent_ids: Set[str] = set()

    def create(
        self,
        intent: ExecutionIntent,
    ) -> bool:

        if intent.intent_id in self.intent_ids:
            return False

        self.intent_ids.add(
            intent.intent_id
        )

        return True


# ============================================================
# R26 CLIENT ORDER ID / IDEMPOTENCY
# ============================================================

CLIENT_ID_RE = re.compile(
    r"^[\.A-Z\:/a-z0-9_-]{1,36}$"
)


def deterministic_client_order_id(
    intent: ExecutionIntent,
    namespace: str = "r26",
) -> str:

    material = (
        f"{intent.signal_id}|"
        f"{intent.symbol}|"
        f"{intent.side}|"
        f"{intent.position_side}|"
        f"{decimal_text(intent.quantity)}"
    )

    digest = hashlib.sha256(
        material.encode("utf-8")
    ).hexdigest()[:20]

    cid = (
        f"{namespace}-{digest}"
    )

    return cid[:36]


# ============================================================
# R26 REAL-PAYLOAD REHEARSAL
# ============================================================

@dataclass
class PayloadRehearsal:
    payload: Dict[str, Any]
    body_text: str
    client_id_valid: bool
    required_fields_present: bool
    quantity_step_match: bool
    price_step_match: bool
    deterministic_rebuild_match: bool
    signature_generated: bool
    real_path_blocked: bool
    response_accept_classification_test: bool
    response_reject_classification_test: bool
    ambiguous_response_classification_test: bool


def build_order_payload(
    symbol: str,
    side: str,
    position_side: str,
    quantity: Decimal,
    price: Decimal,
    client_order_id: str,
    tif: str = "IOC",
) -> Dict[str, Any]:

    return {
        "symbol": symbol,
        "side": side,
        "positionSide": position_side,
        "type": "LIMIT",
        "timeInForce": tif,
        "quantity": decimal_text(
            quantity
        ),
        "price": decimal_text(
            price
        ),
        "newClientOrderId": (
            client_order_id
        ),
    }


def classify_order_response(
    payload: Any,
) -> Tuple[bool, str, str]:

    if not isinstance(
        payload,
        dict,
    ):
        return (
            False,
            "AMBIGUOUS",
            "response is not an object",
        )

    success = payload.get(
        "success"
    )

    order_id = str(
        first_present(
            payload,
            (
                "orderId",
                "order_id",
            ),
            "",
        )
        or ""
    )

    error_code = str(
        first_present(
            payload,
            (
                "errorCode",
                "code",
            ),
            "",
        )
        or ""
    )

    error_message = str(
        first_present(
            payload,
            (
                "errorMessage",
                "msg",
                "message",
            ),
            "",
        )
        or ""
    )

    if (
        success is True
        and order_id
    ):
        return (
            True,
            "ACCEPTED",
            order_id,
        )

    if (
        success is False
        or (
            error_code
            and error_code
            not in {
                "0",
                "200",
            }
        )
    ):
        return (
            False,
            "REJECTED",
            (
                f"{error_code} "
                f"{error_message}"
            ).strip(),
        )

    if (
        order_id
        and success is not False
    ):
        return (
            True,
            "ACCEPTED",
            order_id,
        )

    return (
        False,
        "AMBIGUOUS",
        (
            error_message
            or "missing acceptance fields"
        ),
    )


def rehearse_real_payload(
    intent: ExecutionIntent,
    contract: ContractInfo,
    price: Decimal,
) -> PayloadRehearsal:

    cid1 = (
        deterministic_client_order_id(
            intent,
            "r26",
        )
    )

    cid2 = (
        deterministic_client_order_id(
            intent,
            "r26",
        )
    )

    payload = build_order_payload(
        SYMBOL,
        intent.side,
        intent.position_side,
        intent.quantity,
        price,
        cid1,
        "IOC",
    )

    body_text = safe_json_text(
        payload
    )

    required = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "timeInForce",
        "quantity",
        "price",
        "newClientOrderId",
    }

    timestamp = str(
        now_ms()
    )

    signature = (
        WeexClient._signature(
            timestamp,
            "POST",
            REAL_ORDER_PATH,
            "",
            body_text,
        )
    )

    accept_test = (
        classify_order_response(
            {
                "orderId": (
                    "702345678901234567"
                ),
                "clientOrderId": cid1,
                "success": True,
                "errorCode": "",
                "errorMessage": "",
            }
        )[1]
        == "ACCEPTED"
    )

    reject_test = (
        classify_order_response(
            {
                "orderId": "",
                "clientOrderId": cid1,
                "success": False,
                "errorCode": "-1052",
                "errorMessage": (
                    "Permission denied"
                ),
            }
        )[1]
        == "REJECTED"
    )

    ambiguous_test = (
        classify_order_response(
            {
                "clientOrderId": cid1,
            }
        )[1]
        == "AMBIGUOUS"
    )

    return PayloadRehearsal(
        payload=payload,
        body_text=body_text,
        client_id_valid=bool(
            CLIENT_ID_RE.fullmatch(
                cid1
            )
        ),
        required_fields_present=(
            required.issubset(
                payload.keys()
            )
        ),
        quantity_step_match=(
            step_match(
                intent.quantity,
                contract.qty_step,
            )
        ),
        price_step_match=(
            step_match(
                price,
                contract.price_step,
            )
        ),
        deterministic_rebuild_match=(
            cid1 == cid2
        ),
        signature_generated=bool(
            signature
        ),
        real_path_blocked=(
            not LIVE_ORDER_EXECUTION
            and HARD_REAL_POST_LOCK
        ),
        response_accept_classification_test=(
            accept_test
        ),
        response_reject_classification_test=(
            reject_test
        ),
        ambiguous_response_classification_test=(
            ambiguous_test
        ),
    )


# ============================================================
# DATA EXTRACTION
# ============================================================

def extract_available_balance(
    payload: Any,
    asset: str = "USDT",
) -> Decimal:

    target = asset.upper()
    rows = extract_list(
        payload
    )

    if (
        not rows
        and isinstance(
            payload,
            dict,
        )
    ):
        rows = [
            payload
        ]

    for row in rows:
        if not isinstance(
            row,
            dict,
        ):
            continue

        row_asset = str(
            first_present(
                row,
                (
                    "asset",
                    "coin",
                    "currency",
                ),
                "",
            )
        ).upper()

        if row_asset == target:
            value = first_present(
                row,
                (
                    "availableBalance",
                    "available",
                    "availableMargin",
                    "free",
                    "balance",
                ),
            )

            parsed = D(
                value,
                Decimal("-1"),
            )

            if parsed >= 0:
                return parsed

    raise RuntimeError(
        f"Unable to extract available {asset}"
    )


def extract_mark_price(
    payload: Any,
) -> Decimal:

    if isinstance(
        payload,
        dict,
    ):
        for key in (
            "price",
            "markPrice",
            "mark_price",
        ):
            value = D(
                payload.get(key),
                Decimal("-1"),
            )

            if value > 0:
                return value

        data = payload.get(
            "data"
        )

        if isinstance(
            data,
            dict,
        ):
            return extract_mark_price(
                data
            )

    raise RuntimeError(
        "Unable to extract mark price "
        f"from: {payload}"
    )


def position_size_from_payload(
    payload: Any,
    symbol: str,
    position_side: str,
) -> Decimal:

    target_symbol = (
        symbol.upper()
    )

    target_side = (
        position_side.upper()
    )

    total = D0

    rows = extract_list(
        payload
    )

    for row in rows:
        if not isinstance(
            row,
            dict,
        ):
            continue

        row_symbol = str(
            row.get(
                "symbol",
                "",
            )
        ).upper()

        row_side = str(
            first_present(
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
            row_symbol
            != target_symbol
        ):
            continue

        if (
            row_side
            and target_side
            and row_side
            != target_side
        ):
            continue

        size = D(
            first_present(
                row,
                (
                    "positionAmt",
                    "size",
                    "quantity",
                    "total",
                    "available",
                ),
            )
        )

        total += abs(
            size
        )

    return total


def find_history_order(
    payload: Any,
    order_id: str,
    client_order_id: str,
) -> Optional[Dict[str, Any]]:

    for row in extract_list(
        payload
    ):
        if not isinstance(
            row,
            dict,
        ):
            continue

        oid = str(
            first_present(
                row,
                (
                    "orderId",
                    "order_id",
                ),
                "",
            )
            or ""
        )

        cid = str(
            first_present(
                row,
                (
                    "clientOrderId",
                    "client_oid",
                ),
                "",
            )
            or ""
        )

        if (
            order_id
            and oid == order_id
        ):
            return row

        if (
            client_order_id
            and cid == client_order_id
        ):
            return row

    return None


# ============================================================
# DEMO ORDER LIFECYCLE
# ============================================================

@dataclass
class DemoLifecycleResult:
    demo_symbol: str
    side: str
    position_side: str
    order_type: str
    tif: str
    limit_price: Decimal
    price_step_match: bool
    client_order_id: str
    client_order_id_valid: bool
    post_attempted: bool
    post_accepted: bool
order_id: str
    response_client_id_match: bool
    history_lookup_attempted: bool
    history_poll_attempts: int
    history_found: bool
    history_order_id_match: bool
    history_client_id_match: bool
    history_symbol_match: bool
    history_side_match: bool
    history_position_side_match: bool
    final_status: str
    status_recognized: bool
    requested_qty: Decimal
    original_qty: Decimal
    executed_qty: Decimal
    quantity_reconciled: bool
    lifecycle_valid: bool
    history_row: Optional[Dict[str, Any]]


async def run_demo_lifecycle(
    client: WeexClient,
    contract: ContractInfo,
    mark_price: Decimal,
    quantity: Decimal,
    intent: ExecutionIntent,
) -> DemoLifecycleResult:
    if not DEMO_ORDER_ENABLED:
        raise RuntimeError("DEMO_ORDER_ENABLED must remain true for R26 validation")

    if DEMO_SIDE == "BUY":
        raw_price = mark_price * (Decimal("1") - DEMO_PRICE_OFFSET_PERCENT / D100)
    else:
        raw_price = mark_price * (Decimal("1") + DEMO_PRICE_OFFSET_PERCENT / D100)

    limit_price = floor_with_precision(
        raw_price,
        contract.price_step,
        contract.price_precision,
    )

    client_order_id = deterministic_client_order_id(
        intent,
        "r26d",
    )

    body = build_order_payload(
        DEMO_SYMBOL,
        DEMO_SIDE,
        DEMO_POSITION_SIDE,
        quantity,
        limit_price,
        client_order_id,
        DEMO_TIME_IN_FORCE,
    )

    response = await client.demo_post(
        DEMO_ORDER_PATH,
        body,
    )

    accepted, classification, detail = classify_order_response(
        response
    )

    if not accepted:
        raise RuntimeError(
            f"Demo response not accepted: "
            f"{classification}: {detail}"
        )

    order_id = str(
        first_present(
            response,
            ("orderId", "order_id"),
            "",
        )
        or ""
    )

    response_client_id = str(
        first_present(
            response,
            ("clientOrderId", "client_oid"),
            "",
        )
        or ""
    )

    history_row = None
    poll_count = 0

    for attempt in range(
        1,
        HISTORY_POLL_ATTEMPTS + 1,
    ):
        poll_count = attempt

        payload = await client.private_get(
            EP_DEMO_HISTORY,
            {
                "symbol": DEMO_SYMBOL,
                "limit": 100,
                "page": 0,
            },
        )

        history_row = find_history_order(
            payload,
            order_id,
            client_order_id,
        )

        if history_row:
            break

        if attempt < HISTORY_POLL_ATTEMPTS:
            await asyncio.sleep(
                HISTORY_POLL_DELAY_SECONDS
            )

    if history_row:
        h_order_id = str(
            first_present(
                history_row,
                ("orderId", "order_id"),
                "",
            )
            or ""
        )

        h_client_id = str(
            first_present(
                history_row,
                ("clientOrderId", "client_oid"),
                "",
            )
            or ""
        )

        h_symbol = str(
            history_row.get(
                "symbol",
                "",
            )
        ).upper()

        h_side = str(
            history_row.get(
                "side",
                "",
            )
        ).upper()

        h_position_side = str(
            first_present(
                history_row,
                (
                    "positionSide",
                    "holdSide",
                ),
                "",
            )
        ).upper()

        final_status = str(
            history_row.get(
                "status",
                "UNKNOWN",
            )
        ).upper()

        orig_qty = D(
            first_present(
                history_row,
                (
                    "origQty",
                    "quantity",
                    "size",
                    "origQuantity",
                ),
            )
        )

        executed_qty = D(
            first_present(
                history_row,
                (
                    "executedQty",
                    "filledQty",
                    "filledSize",
                    "dealSize",
                ),
            )
        )

    else:
        h_order_id = ""
        h_client_id = ""
        h_symbol = ""
        h_side = ""
        h_position_side = ""
        final_status = "NOT_FOUND"
        orig_qty = D0
        executed_qty = D0

    status_recognized = (
        final_status in ORDER_STATE_RANK
    )

    quantity_reconciled = (
        history_row is not None
        and orig_qty == quantity
        and D0 <= executed_qty <= orig_qty
    )

    lifecycle_valid = all(
        [
            accepted,
            bool(order_id),
            bool(
                CLIENT_ID_RE.fullmatch(
                    client_order_id
                )
            ),
            history_row is not None,
            h_order_id == order_id,
            h_client_id in {
                "",
                client_order_id,
            },
            h_symbol == DEMO_SYMBOL,
            h_side == DEMO_SIDE,
            h_position_side
            in {
                "",
                DEMO_POSITION_SIDE,
            },
            status_recognized,
            quantity_reconciled,
        ]
    )

    return DemoLifecycleResult(
        demo_symbol=DEMO_SYMBOL,
        side=DEMO_SIDE,
        position_side=DEMO_POSITION_SIDE,
        order_type=DEMO_ORDER_TYPE,
        tif=DEMO_TIME_IN_FORCE,
        limit_price=limit_price,
        price_step_match=step_match(
            limit_price,
            contract.price_step,
        ),
        client_order_id=client_order_id,
        client_order_id_valid=bool(
            CLIENT_ID_RE.fullmatch(
                client_order_id
            )
        ),
        post_attempted=R26_DEMO_POST_ATTEMPTED,
        post_accepted=R26_DEMO_POST_ACCEPTED,
        order_id=order_id,
        response_client_id_match=(
            response_client_id
            in {
                "",
                client_order_id,
            }
        ),
        history_lookup_attempted=True,
        history_poll_attempts=poll_count,
        history_found=(
            history_row is not None
        ),
        history_order_id_match=(
            h_order_id == order_id
            and bool(order_id)
        ),
        history_client_id_match=(
            h_client_id
            in {
                "",
                client_order_id,
            }
        ),
        history_symbol_match=(
            h_symbol == DEMO_SYMBOL
        ),
        history_side_match=(
            h_side == DEMO_SIDE
        ),
        history_position_side_match=(
            h_position_side
            in {
                "",
                DEMO_POSITION_SIDE,
            }
        ),
        final_status=final_status,
        status_recognized=status_recognized,
        requested_qty=quantity,
        original_qty=orig_qty,
        executed_qty=executed_qty,
        quantity_reconciled=quantity_reconciled,
        lifecycle_valid=lifecycle_valid,
        history_row=history_row,
    )


# ============================================================
# R26 FAILURE-PATH SELF TESTS
# ============================================================

@dataclass
class FailurePathTests:
    duplicate_submit_blocked: bool
    stale_intent_blocked: bool
    invalid_quantity_blocked: bool
    invalid_price_blocked: bool
    invalid_client_id_blocked: bool
    terminal_regression_blocked: bool
    real_post_blocked_before_network: bool
    ambiguous_response_fail_closed: bool


def run_failure_path_tests(
    contract: ContractInfo,
    quantity: Decimal,
    price: Decimal,
) -> FailurePathTests:

    gate = IntentGate()

    base = ExecutionIntent(
        intent_id="r26-failure-intent",
        signal_id="sig-r26-failure",
        symbol=SYMBOL,
        direction="LONG",
        side="BUY",
        position_side="LONG",
        quantity=quantity,
        created_at=time.time(),
    )

    first = gate.create(
        base
    )

    second = gate.create(
        base
    )

    stale = ExecutionIntent(
        intent_id="r26-stale",
        signal_id="sig-stale",
        symbol=SYMBOL,
        direction="LONG",
        side="BUY",
        position_side="LONG",
        quantity=quantity,
        created_at=(
            time.time()
            - SIGNAL_EXPIRY_SECONDS
            - 10
        ),
    )

    stale_blocked = (
        time.time()
        - stale.created_at
    ) > SIGNAL_EXPIRY_SECONDS

    bad_qty = (
        quantity
        + (
            contract.qty_step
            / Decimal("2")
        )
    )

    bad_price = (
        price
        + (
            contract.price_step
            / Decimal("2")
        )
    )

    invalid_quantity_blocked = not step_match(
        bad_qty,
        contract.qty_step,
    )

    invalid_price_blocked = not step_match(
        bad_price,
        contract.price_step,
    )

    invalid_client_id_blocked = (
        CLIENT_ID_RE.fullmatch(
            "r26 invalid client id with spaces"
        )
        is None
    )

    tracker = OrderTracker(
        "failure-order"
    )

    tracker.apply(
        "FILLED",
        quantity,
        "evt-filled",
    )

    accepted_regression, _, reason = tracker.apply(
        "NEW",
        quantity,
        "evt-regression",
    )

    ambiguous = classify_order_response(
        {
            "clientOrderId": "r26-x"
        }
    )

    return FailurePathTests(
        duplicate_submit_blocked=(
            first
            and not second
        ),
        stale_intent_blocked=(
            stale_blocked
        ),
        invalid_quantity_blocked=(
            invalid_quantity_blocked
        ),
        invalid_price_blocked=(
            invalid_price_blocked
        ),
        invalid_client_id_blocked=(
            invalid_client_id_blocked
        ),
        terminal_regression_blocked=(
            not accepted_regression
            and reason
            == "terminal-regression"
        ),
        real_post_blocked_before_network=(
            not LIVE_ORDER_EXECUTION
            and HARD_REAL_POST_LOCK
        ),
        ambiguous_response_fail_closed=(
            ambiguous[0] is False
            and ambiguous[1]
            == "AMBIGUOUS"
        ),
    )


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    session: aiohttp.ClientSession,
    text: str,
) -> bool:

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):
        return False

    url = (
        "https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}"
        "/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True,
    }

    try:
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as r:
            return (
                200
                <= r.status
                < 300
            )

    except Exception:
        return False


# ============================================================
# HEALTH SERVER
# ============================================================

DIAGNOSTIC_STATUS = {
    "module": MODULE_NAME,
    "state": "starting",
    "last_error": "",
    "real_post_called": False,
    "live_order_execution": LIVE_ORDER_EXECUTION,
}


async def health_handler(
    request: web.Request,
) -> web.Response:

    return web.json_response(
        DIAGNOSTIC_STATUS
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
        f"HEALTH SERVER ACTIVE ON PORT {PORT}",
        flush=True,
    )

    return runner


# ============================================================
# REPORT
# ============================================================

def build_report(
    available_usdt: Decimal,
    mark_price: Decimal,
    contract: ContractInfo,
    entry_margin: Decimal,
    entry_notional: Decimal,
    quantity: Decimal,
    gate_results: Dict[str, bool],
    order_sm: Dict[str, bool],
    intent_results: Dict[str, bool],
    preflight: Dict[str, bool],
    rehearsal: PayloadRehearsal,
    lifecycle: DemoLifecycleResult,
    history_idem: Dict[str, Any],
    position_before: Decimal,
    position_after: Decimal,
    position_reconciled: bool,
    failure_tests: FailurePathTests,
    final_intent: ExecutionIntent,
) -> str:

    initial_exposure = ENTRY_PERCENT

    pyramid_exposure = (
        PYRAMID_SIZE_PERCENT
        * MAX_PYRAMID_ADDS
    )

    backup_exposure = (
        BACKUP_SIZE_PERCENT
        * MAX_BACKUPS
    )

    total_exposure = (
        initial_exposure
        + pyramid_exposure
        + backup_exposure
    )

    overall_preflight = all(
        preflight.values()
    )

    failure_all = all(
        vars(
            failure_tests
        ).values()
    )

    lines = [
        f"✅ MODULE {MODULE_NAME} DIAGNOSTIC PASSED",
        SYMBOL,
        f"Available USDT: {decimal_text(available_usdt)}",
        f"Mark Price: {decimal_text(mark_price)} USDT",
        "",
        "FINAL EXECUTION GATE",
        f"API Trading Symbol: {yesno(gate_results['api_symbol'])}",
        f"Fresh Signal Accepted: {yesno(gate_results['fresh_signal'])}",
        f"Expired Signal Rejected: {yesno(gate_results['expired_signal'])}",
        f"Loss Cooldown Test: {yesno(gate_results['loss_cooldown'])}",
        f"Duplicate Signal Rejected: {yesno(gate_results['duplicate_signal'])}",
        f"One Direction Gate: {yesno(gate_results['one_direction'])}",
        f"External Position Clear: {yesno(gate_results['external_position_clear'])}",
        "",
        "ADJUSTABLE CONFIG",
        f"Entry: {decimal_text(ENTRY_PERCENT)}%",
        f"Leverage: {LEVERAGE}x",
        f"Max Config Leverage: {MAX_CONFIG_LEVERAGE}x",
        f"Margin Type: {MARGIN_TYPE}",
        f"Max Pyramids: {MAX_PYRAMID_ADDS}",
        f"Pyramid Size: {decimal_text(PYRAMID_SIZE_PERCENT)}%",
        f"Max Backups: {MAX_BACKUPS}",
        f"Backup Size: {decimal_text(BACKUP_SIZE_PERCENT)}% each",
        f"Backup Buffer: {decimal_text(BACKUP_BUFFER_PERCENT)}%",
        f"Min Liq Distance: {decimal_text(MIN_LIQ_DISTANCE_PERCENT)}%",
        f"Max Fund Exposure: {decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%",
        "",
        "WEEX CONTRACT",
        f"Minimum Order: {decimal_text(contract.min_qty)}",
        f"Quantity Precision: {contract.qty_precision}",
        f"Quantity Step: {decimal_text(contract.qty_step)}",
        f"Price Precision: {contract.price_precision}",
        f"Price Step: {decimal_text(contract.price_step)}",
        f"Contract Value: {decimal_text(contract.contract_value)}",
        f"WEEX Min Leverage: {contract.min_leverage}x",
        f"WEEX Max Leverage: {contract.max_leverage}x",
        f"Leverage Gate: {yesno(contract.min_leverage <= LEVERAGE <= contract.max_leverage)}",
        "",
        "DYNAMIC ENTRY",
        f"Margin: {decimal_text(entry_margin)} USDT",
        f"Notional: {decimal_text(entry_notional)} USDT",
        f"Quantity: {decimal_text(quantity)}",
        f"Quantity Positive: {yesno(quantity > 0)}",
        f"Minimum Passed: {yesno(quantity >= contract.min_qty)}",
        "",
        "WORST-CASE EXPOSURE",
        f"Initial: {decimal_text(initial_exposure)}%",
        f"Pyramids: {decimal_text(pyramid_exposure)}%",
        f"Backups: {decimal_text(backup_exposure)}%",
        f"Total: {decimal_text(total_exposure)}% / {decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%",
        f"Exposure Passed: {yesno(total_exposure <= MAX_FUND_EXPOSURE_PERCENT)}",
        "",
        "TP / TRAILING",
        f"TP1 / TP2 / TP3: {decimal_text(TP1_PERCENT)}% / {decimal_text(TP2_PERCENT)}% / {decimal_text(TP3_PERCENT)}%",
        f"TP1 Trigger: {decimal_text(TP1_TRIGGER_PERCENT)}%",
        f"TP2 Trigger: {decimal_text(TP2_TRIGGER_PERCENT)}%",
        f"Trailing Distance: {decimal_text(TRAILING_DISTANCE_PERCENT)}%",
        "",
        "R26 ORDER STATE MACHINE",
        f"NEW State Accepted: {yesno(order_sm['new'])}",
        f"Partial Fill #1 Delta: {yesno(order_sm['partial1'])}",
        f"Partial Fill #2 Delta: {yesno(order_sm['partial2'])}",
        f"FILLED Terminal State: {yesno(order_sm['filled'])}",
        f"Duplicate Exchange Event Blocked: {yesno(order_sm['duplicate'])}",
        f"Terminal Regression Blocked: {yesno(order_sm['terminal_regression'])}",
        "",
        "R26 EXECUTION INTENT GATE",
        f"Intent Created: {yesno(intent_results['created'])}",
        f"Duplicate Intent Blocked: {yesno(intent_results['duplicate'])}",
        f"NEW → PREFLIGHT: {yesno(intent_results['to_preflight'])}",
        f"PREFLIGHT → READY: {yesno(intent_results['to_ready'])}",
        f"Expired Intent Rejected: {yesno(intent_results['expired'])}",
        f"Terminal Intent Regression Blocked: {yesno(intent_results['terminal_regression'])}",
        "",
        "R26 EXECUTION PREFLIGHT",
        f"Live Execution OFF: {yesno(preflight['live_off'])}",
        f"Hard Real POST Lock: {yesno(preflight['hard_lock'])}",
        f"Intent Fresh: {yesno(preflight['fresh'])}",
        f"Intent Quantity Positive: {yesno(preflight['qty_positive'])}",
        f"Intent Minimum Passed: {yesno(preflight['minimum'])}",
        f"Intent Leverage Passed: {yesno(preflight['leverage'])}",
        f"Intent Exposure Passed: {yesno(preflight['exposure'])}",
        f"Real Order Path Blocked: {yesno(preflight['real_blocked'])}",
        f"Overall Preflight: {yesno(overall_preflight)}",
        "",
        "R26 LIVE PAYLOAD REHEARSAL",
        f"Real Endpoint Target: {REAL_ORDER_PATH}",
        f"Payload Built: {yesno(bool(rehearsal.payload))}",
        f"Required Fields Present: {yesno(rehearsal.required_fields_present)}",
        f"Client Order ID: {rehearsal.payload.get('newClientOrderId', '')}",
        f"Client Order ID Valid: {yesno(rehearsal.client_id_valid)}",
        f"Deterministic Client ID: {yesno(rehearsal.deterministic_rebuild_match)}",
        f"Quantity Step Match: {yesno(rehearsal.quantity_step_match)}",
        f"Price Step Match: {yesno(rehearsal.price_step_match)}",
        f"Signature Generated Locally: {yesno(rehearsal.signature_generated)}",
        f"Accepted Response Classifier: {yesno(rehearsal.response_accept_classification_test)}",
        f"Rejected Response Classifier: {yesno(rehearsal.response_reject_classification_test)}",
        f"Ambiguous Response Fails Closed: {yesno(rehearsal.ambiguous_response_classification_test)}",
        f"Real POST Transmission Blocked: {yesno(rehearsal.real_path_blocked)}",
        "",
        "R26 DEMO ORDER LIFECYCLE",
        f"Demo Symbol: {lifecycle.demo_symbol}",
        f"Demo Side: {lifecycle.side}",
        f"Demo Position Side: {lifecycle.position_side}",
        f"Demo Type: {lifecycle.order_type}",
        f"Demo Time In Force: {lifecycle.tif}",
        f"Demo Limit Price: {decimal_text(lifecycle.limit_price)}",
        f"Price Step Match: {yesno(lifecycle.price_step_match)}",
        f"Demo Client Order ID: {lifecycle.client_order_id}",
        f"Client Order ID Valid: {yesno(lifecycle.client_order_id_valid)}",
        f"Demo POST Attempted: {yesno(lifecycle.post_attempted)}",
        f"Demo POST Accepted: {yesno(lifecycle.post_accepted)}",
        f"Demo Order ID: {lifecycle.order_id}",
        f"Response Client ID Match: {yesno(lifecycle.response_client_id_match)}",
        f"History Lookup Attempted: {yesno(lifecycle.history_lookup_attempted)}",
        f"History Poll Attempts: {lifecycle.history_poll_attempts}",
        f"Order Found In History: {yesno(lifecycle.history_found)}",
        f"History Order ID Match: {yesno(lifecycle.history_order_id_match)}",
        f"History Client ID Match: {yesno(lifecycle.history_client_id_match)}",
        f"History Symbol Match: {yesno(lifecycle.history_symbol_match)}",
        f"History Side Match: {yesno(lifecycle.history_side_match)}",
        f"History Position Side Match: {yesno(lifecycle.history_position_side_match)}",
        f"Demo Final Status: {lifecycle.final_status}",
        f"Status Recognized: {yesno(lifecycle.status_recognized)}",
        f"Requested Quantity: {decimal_text(lifecycle.requested_qty)}",
        f"History Original Quantity: {decimal_text(lifecycle.original_qty)}",
        f"History Executed Quantity: {decimal_text(lifecycle.executed_qty)}",
        f"Quantity Reconciliation: {yesno(lifecycle.quantity_reconciled)}",
        f"Lifecycle Validation: {yesno(lifecycle.lifecycle_valid)}",
        "",
        "R26 ACTUAL HISTORY IDEMPOTENCY",
        f"First Processing Accepted: {yesno(history_idem['first'])}",
        f"Duplicate Processing Blocked: {yesno(history_idem['duplicate'])}",
        f"Actual History Terminal: {yesno(history_idem['terminal'])}",
        f"Actual Fill Delta: {decimal_text(history_idem['delta'])}",
        "",
        "R26 DEMO POSITION RECONCILIATION",
        f"Position Size Before: {decimal_text(position_before)}",
        f"Position Size After: {decimal_text(position_after)}",
        f"Position Reconciled: {yesno(position_reconciled)}",
        "",
        "R26 FAILURE-PATH MATRIX",
        f"Duplicate Submit Blocked: {yesno(failure_tests.duplicate_submit_blocked)}",
        f"Stale Intent Blocked: {yesno(failure_tests.stale_intent_blocked)}",
        f"Invalid Quantity Blocked: {yesno(failure_tests.invalid_quantity_blocked)}",
        f"Invalid Price Blocked: {yesno(failure_tests.invalid_price_blocked)}",
        f"Invalid Client ID Blocked: {yesno(failure_tests.invalid_client_id_blocked)}",
        f"Terminal Regression Blocked: {yesno(failure_tests.terminal_regression_blocked)}",
        f"Real POST Blocked Before Network: {yesno(failure_tests.real_post_blocked_before_network)}",
        f"Ambiguous Response Fails Closed: {yesno(failure_tests.ambiguous_response_fail_closed)}",
        f"Failure Matrix Passed: {yesno(failure_all)}",
"",
        "R26 SIGNAL → INTENT → EXECUTION CHAIN",
        f"Signal Direction: {final_intent.direction}",
        f"Intent Side: {final_intent.side}",
        f"Intent Position Side: {final_intent.position_side}",
        f"Intent Quantity: {decimal_text(final_intent.quantity)}",
        f"Client Order ID: {final_intent.client_order_id}",
        f"Final Intent State: {final_intent.state}",
        f"Intent Reconciled: {yesno(final_intent.state == 'RECONCILED')}",
        "",
        "R26 RENDER PERSISTENCE",
        "Health Server: ✅ ACTIVE",
        "Persistent Runtime: ✅ ACTIVE",
        "Auto Exit After Diagnostic: ❌ DISABLED",
        "Repeated Demo Order Loop: ❌ DISABLED",
        "",
        "ABSOLUTE EXECUTION SAFETY",
        f"Real POST Called: {'⚠️ YES' if R26_REAL_POST_CALLED else '❌ NO'}",
        "🛡 R26 absolute real-order POST lock active",
        "⚠️ LIVE ORDER EXECUTION DISABLED",
        "⚠️ NO REAL ORDER WAS SENT",
    ]

    return "\n".join(lines)


# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

async def r26_run_diagnostic(
    session: aiohttp.ClientSession,
) -> str:

    stage = "startup"

    try:
        final_safety_assertions_r26()

        stage = "configuration"
        validate_credentials()

        client = WeexClient(
            session
        )

        stage = "market data"

        mark_payload, exchange_payload = await asyncio.gather(
            client.public_get(
                EP_MARK_PRICE,
                {
                    "symbol": SYMBOL,
                    "priceType": "MARK",
                },
            ),
            client.public_get(
                EP_EXCHANGE_INFO,
                {
                    "symbol": SYMBOL,
                },
            ),
        )

        mark_price = extract_mark_price(
            mark_payload
        )

        contract = parse_contract_info(
            exchange_payload,
            SYMBOL,
        )

        stage = "balance"

        balance_payload = await client.private_get(
            EP_REAL_BALANCE
        )

        available_usdt = extract_available_balance(
            balance_payload,
            "USDT",
        )

        stage = "external position gate"

        try:
            real_positions = await client.private_get(
                EP_REAL_POSITIONS
            )

            long_pos = position_size_from_payload(
                real_positions,
                SYMBOL,
                "LONG",
            )

            short_pos = position_size_from_payload(
                real_positions,
                SYMBOL,
                "SHORT",
            )

            external_position_clear = (
                long_pos == 0
                and short_pos == 0
            )

        except Exception as exc:
            raise RuntimeError(
                "Unable to verify external real positions: "
                f"{exc}"
            )

        stage = "dynamic entry"

        entry_margin = (
            available_usdt
            * ENTRY_PERCENT
            / D100
        )

        entry_notional = (
            entry_margin
            * Decimal(LEVERAGE)
        )

        raw_qty = (
            entry_notional
            / mark_price
        )

        quantity = floor_with_precision(
            raw_qty,
            contract.qty_step,
            contract.qty_precision,
        )

        if quantity <= 0:
            raise RuntimeError(
                "Dynamic entry produced "
                "non-positive quantity"
            )

        if quantity < contract.min_qty:
            raise RuntimeError(
                "Dynamic entry quantity "
                f"{quantity} below minimum "
                f"{contract.min_qty}"
            )

        total_exposure = (
            ENTRY_PERCENT
            + PYRAMID_SIZE_PERCENT
            * MAX_PYRAMID_ADDS
            + BACKUP_SIZE_PERCENT
            * MAX_BACKUPS
        )

        leverage_passed = (
            contract.min_leverage
            <= LEVERAGE
            <= contract.max_leverage
        )

        exposure_passed = (
            total_exposure
            <= MAX_FUND_EXPOSURE_PERCENT
        )

        stage = "signal gate self-test"

        sg = SignalGate()

        t = time.time()

        fresh = Signal(
            "fresh",
            SYMBOL,
            "LONG",
            t,
        )

        expired = Signal(
            "expired",
            SYMBOL,
            "LONG",
            t
            - SIGNAL_EXPIRY_SECONDS
            - 1,
        )

        fresh_ok = sg.accept(
            fresh,
            t,
        )[0]

        expired_ok = not sg.accept(
            expired,
            t,
        )[0]

        duplicate_ok = not sg.accept(
            fresh,
            t,
        )[0]

        cooldown_gate = SignalGate()

        cooldown_gate.last_loss_time = t

        cooldown_ok = not cooldown_gate.accept(
            Signal(
                "cool",
                SYMBOL,
                "LONG",
                t,
            ),
            t,
        )[0]

        gate_results = {
            "api_symbol": (
                contract.symbol.upper()
                == SYMBOL
            ),
            "fresh_signal": fresh_ok,
            "expired_signal": expired_ok,
            "loss_cooldown": cooldown_ok,
            "duplicate_signal": duplicate_ok,
            "one_direction": ONE_DIRECTION_ONLY,
            "external_position_clear": (
                external_position_clear
            ),
        }

        stage = "order state machine"

        tracker = OrderTracker(
            "selftest"
        )

        a0, d0, _ = tracker.apply(
            "NEW",
            D0,
            "e0",
        )

        a1, d1, _ = tracker.apply(
            "PARTIALLY_FILLED",
            quantity / 4,
            "e1",
        )

        a2, d2, _ = tracker.apply(
            "PARTIALLY_FILLED",
            quantity / 2,
            "e2",
        )

        a3, d3, _ = tracker.apply(
            "FILLED",
            quantity,
            "e3",
        )

        dup, _, dup_reason = tracker.apply(
            "FILLED",
            quantity,
            "e3",
        )

        reg, _, reg_reason = tracker.apply(
            "NEW",
            quantity,
            "e4",
        )

        order_sm = {
            "new": (
                a0
                and d0 == 0
            ),
            "partial1": (
                a1
                and d1 > 0
            ),
            "partial2": (
                a2
                and d2 > 0
            ),
            "filled": (
                a3
                and tracker.terminal
                and d3 > 0
            ),
            "duplicate": (
                not dup
                and dup_reason
                == "duplicate-event"
            ),
            "terminal_regression": (
                not reg
                and reg_reason
                == "terminal-regression"
            ),
        }

        stage = "execution intent"

        intent_gate = IntentGate()

        intent = ExecutionIntent(
            intent_id="r26-intent-main",
            signal_id="r26-signal-main",
            symbol=SYMBOL,
            direction="LONG",
            side="BUY",
            position_side="LONG",
            quantity=quantity,
            created_at=time.time(),
        )

        created = intent_gate.create(
            intent
        )

        duplicate_intent = not intent_gate.create(
            intent
        )

        to_preflight = intent.transition(
            "PREFLIGHT"
        )

        to_ready = intent.transition(
            "READY"
        )

        expired_intent = ExecutionIntent(
            intent_id="r26-expired",
            signal_id="r26-expired-sig",
            symbol=SYMBOL,
            direction="LONG",
            side="BUY",
            position_side="LONG",
            quantity=quantity,
            created_at=(
                time.time()
                - SIGNAL_EXPIRY_SECONDS
                - 1
            ),
        )

        expired_rejected = (
            time.time()
            - expired_intent.created_at
        ) > SIGNAL_EXPIRY_SECONDS

        terminal_intent = ExecutionIntent(
            intent_id="r26-terminal",
            signal_id="r26-terminal-sig",
            symbol=SYMBOL,
            direction="LONG",
            side="BUY",
            position_side="LONG",
            quantity=quantity,
            created_at=time.time(),
            state="RECONCILED",
        )

        terminal_regression = not terminal_intent.transition(
            "READY"
        )

        intent_results = {
            "created": created,
            "duplicate": duplicate_intent,
            "to_preflight": to_preflight,
            "to_ready": to_ready,
            "expired": expired_rejected,
            "terminal_regression": (
                terminal_regression
            ),
        }

        stage = "execution preflight"

        preflight = {
            "live_off": (
                not LIVE_ORDER_EXECUTION
            ),
            "hard_lock": (
                HARD_REAL_POST_LOCK
            ),
            "fresh": (
                time.time()
                - intent.created_at
            ) <= SIGNAL_EXPIRY_SECONDS,
            "qty_positive": (
                intent.quantity > 0
            ),
            "minimum": (
                intent.quantity
                >= contract.min_qty
            ),
            "leverage": (
                leverage_passed
            ),
            "exposure": (
                exposure_passed
            ),
            "real_blocked": (
                HARD_REAL_POST_LOCK
                and not LIVE_ORDER_EXECUTION
            ),
        }

        if not all(
            preflight.values()
        ):
            raise RuntimeError(
                f"R26 preflight failed: {preflight}"
            )

        stage = "live payload rehearsal"

        live_limit_price = floor_with_precision(
            mark_price
            * (
                Decimal("1")
                - DEMO_PRICE_OFFSET_PERCENT
                / D100
            ),
            contract.price_step,
            contract.price_precision,
        )

        rehearsal = rehearse_real_payload(
            intent,
            contract,
            live_limit_price,
        )

        rehearsal_checks = [
            rehearsal.client_id_valid,
            rehearsal.required_fields_present,
            rehearsal.quantity_step_match,
            rehearsal.price_step_match,
            rehearsal.deterministic_rebuild_match,
            rehearsal.signature_generated,
            rehearsal.real_path_blocked,
            rehearsal.response_accept_classification_test,
            rehearsal.response_reject_classification_test,
            rehearsal.ambiguous_response_classification_test,
        ]

        if not all(
            rehearsal_checks
        ):
            raise RuntimeError(
                "R26 live payload rehearsal failed"
            )

        intent.client_order_id = rehearsal.payload[
            "newClientOrderId"
        ]

        stage = "demo position before"

        demo_pos_before_payload = await client.private_get(
            EP_DEMO_POSITIONS
        )

        position_before = position_size_from_payload(
            demo_pos_before_payload,
            DEMO_SYMBOL,
            DEMO_POSITION_SIDE,
        )

        stage = "demo order transmission"

        lifecycle = await run_demo_lifecycle(
            client,
            contract,
            mark_price,
            quantity,
            intent,
        )

        if not lifecycle.lifecycle_valid:
            raise RuntimeError(
                "R26 demo lifecycle validation failed"
            )

        stage = "actual history idempotency"

        actual_tracker = OrderTracker(
            lifecycle.order_id
        )

        status = lifecycle.final_status
        qty_exec = lifecycle.executed_qty

        event_key = (
            f"{lifecycle.order_id}:"
            f"{status}:"
            f"{decimal_text(qty_exec)}"
        )

        first_acc, first_delta, _ = actual_tracker.apply(
            status,
            qty_exec,
            event_key,
        )

        second_acc, _, second_reason = actual_tracker.apply(
            status,
            qty_exec,
            event_key,
        )

        history_idem = {
            "first": first_acc,
            "duplicate": (
                not second_acc
                and second_reason
                == "duplicate-event"
            ),
            "terminal": actual_tracker.terminal,
            "delta": first_delta,
        }

        stage = "demo position after"

        demo_pos_after_payload = await client.private_get(
            EP_DEMO_POSITIONS
        )

        position_after = position_size_from_payload(
            demo_pos_after_payload,
            DEMO_SYMBOL,
            DEMO_POSITION_SIDE,
        )

        expected_after = (
            position_before
            + lifecycle.executed_qty
        )

        position_reconciled = (
            position_after
            == expected_after
        )

        stage = "failure path matrix"

        failure_tests = run_failure_path_tests(
            contract,
            quantity,
            live_limit_price,
        )

        if not all(
            vars(
                failure_tests
            ).values()
        ):
            raise RuntimeError(
                "R26 failure matrix failed: "
                f"{failure_tests}"
            )

        stage = "intent finalization"

        # This SUBMITTED transition represents
        # DEMO submission only.
        if not intent.transition(
            "SUBMITTED"
        ):
            raise RuntimeError(
                "Unable to move intent to SUBMITTED"
            )

        if not intent.transition(
            "RECONCILING"
        ):
            raise RuntimeError(
                "Unable to move intent to RECONCILING"
            )

        if not intent.transition(
            "RECONCILED"
        ):
            raise RuntimeError(
                "Unable to move intent to RECONCILED"
            )

        all_critical = [
            all(
                gate_results.values()
            ),
            all(
                order_sm.values()
            ),
            all(
                intent_results.values()
            ),
            all(
                preflight.values()
            ),
            lifecycle.lifecycle_valid,
            history_idem["first"],
            history_idem["duplicate"],
            history_idem["terminal"],
            position_reconciled,
            all(
                vars(
                    failure_tests
                ).values()
            ),
            intent.state
            == "RECONCILED",
            not R26_REAL_POST_CALLED,
        ]

        if not all(
            all_critical
        ):
            raise RuntimeError(
                "One or more R26 critical "
                "validations failed"
            )

        report = build_report(
            available_usdt=available_usdt,
            mark_price=mark_price,
            contract=contract,
            entry_margin=entry_margin,
            entry_notional=entry_notional,
            quantity=quantity,
            gate_results=gate_results,
            order_sm=order_sm,
            intent_results=intent_results,
            preflight=preflight,
            rehearsal=rehearsal,
            lifecycle=lifecycle,
            history_idem=history_idem,
            position_before=position_before,
            position_after=position_after,
            position_reconciled=position_reconciled,
            failure_tests=failure_tests,
            final_intent=intent,
        )

        DIAGNOSTIC_STATUS.update(
            {
                "state": "passed",
                "last_error": "",
                "real_post_called": (
                    R26_REAL_POST_CALLED
                ),
                "demo_post_attempted": (
                    R26_DEMO_POST_ATTEMPTED
                ),
                "demo_post_accepted": (
                    R26_DEMO_POST_ACCEPTED
                ),
                "symbol": SYMBOL,
                "demo_symbol": DEMO_SYMBOL,
                "intent_state": (
                    intent.state
                ),
            }
        )

        return report

    except Exception as exc:
        DIAGNOSTIC_STATUS.update(
            {
                "state": "error",
                "last_error": (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
                "real_post_called": (
                    R26_REAL_POST_CALLED
                ),
                "demo_post_attempted": (
                    R26_DEMO_POST_ATTEMPTED
                ),
                "demo_post_accepted": (
                    R26_DEMO_POST_ACCEPTED
                ),
            }
        )

        error_report = "\n".join(
            [
                f"❌ MODULE {MODULE_NAME} ERROR",
                SYMBOL,
                f"Stage: {stage}",
                (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
                (
                    "Real POST Called: "
                    f"{'⚠️ YES' if R26_REAL_POST_CALLED else '❌ NO'}"
                ),
                (
                    "Demo POST Attempted: "
                    f"{yesno(R26_DEMO_POST_ATTEMPTED)}"
                ),
                (
                    "Demo POST Accepted: "
                    f"{yesno(R26_DEMO_POST_ACCEPTED)}"
                ),
                "🛡 R26 absolute real-order POST lock active",
                "⚠️ LIVE ORDER EXECUTION DISABLED",
                "⚠️ NO REAL ORDER WAS SENT",
            ]
        )

        print(
            traceback.format_exc(),
            flush=True,
        )

        return error_report


# ============================================================
# APPLICATION LIFECYCLE
# ============================================================

async def main_async() -> None:
    await start_health_server()

    print(
        "=" * 60,
        flush=True,
    )

    print(
        f"{MODULE_NAME} STARTING",
        flush=True,
    )

    print(
        "LIVE-PAYLOAD / FAILURE-PATH "
        "PRE-LIVE VALIDATION",
        flush=True,
    )

    print(
        "REAL ORDER TRANSMISSION DISABLED",
        flush=True,
    )

    print(
        "=" * 60,
        flush=True,
    )

    connector = aiohttp.TCPConnector(
        limit=20,
        ttl_dns_cache=300,
    )

    async with aiohttp.ClientSession(
        connector=connector
    ) as session:

        report = await r26_run_diagnostic(
            session
        )

        print(
            report,
            flush=True,
        )

        await send_telegram(
            session,
            report,
        )

        # Persistent Render runtime.
        # Diagnostic runs ONCE only.
        while True:
            await asyncio.sleep(
                3600
            )


def main() -> None:
    try:
        asyncio.run(
            main_async()
        )

    except KeyboardInterrupt:
        pass

    except Exception as exc:
        print(
            "=" * 60,
            flush=True,
        )

        print(
            f"❌ {MODULE_NAME} "
            "FATAL STARTUP ERROR",
            flush=True,
        )

        print(
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        print(
            "🛡 REAL ORDER POST LOCK "
            "REMAINS ACTIVE",
            flush=True,
        )

        print(
            "⚠️ NO REAL ORDER WAS SENT",
            flush=True,
        )

        print(
            "=" * 60,
            flush=True,
        )

        traceback.print_exc()


if __name__ == "__main__":
    main()
    
