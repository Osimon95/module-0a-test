print("R28 UNIT G: MAIN.PY ENTERED", flush=True)

import asyncio
import base64
import hashlib
import hmac
import json
import os
import re
import time
import traceback
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlencode

import aiohttp
from aiohttp import web

print("R28 UNIT G: IMPORTS COMPLETE", flush=True)


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
    default_demo_symbol(SYMBOL),
).strip().upper()


# ============================================================
# ABSOLUTE EXECUTION SAFETY
# ============================================================
# R28 IS PRE-LIVE / DEMO VALIDATION ONLY.
# REAL ORDER TRANSMISSION MUST REMAIN DISABLED.
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_REAL_POST_LOCK = True
R28_REAL_POST_CALLED = False
R28_DEMO_POST_ATTEMPTED = False
R28_DEMO_POST_ACCEPTED = False


# ============================================================
# ADJUSTABLE CONFIG
# ============================================================

D100 = Decimal("100")

ENTRY_PERCENT = Decimal(
    os.getenv("ENTRY_PERCENT", "5")
)

LEVERAGE = int(
    os.getenv("LEVERAGE", "100")
)

MAX_CONFIG_LEVERAGE = int(
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
    os.getenv("TP2_TRIGGER_PERCENT", "1")
)

TRAILING_DISTANCE_PERCENT = Decimal(
    os.getenv("TRAILING_DISTANCE_PERCENT", "0.2")
)

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv("SIGNAL_EXPIRY_SECONDS", "120")
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv("LOSS_COOLDOWN_SECONDS", "300")
)

DEMO_FILL_MODE = os.getenv(
    "DEMO_FILL_MODE",
    "AUTO",
).strip().upper()

RUN_DEMO_FILL = (
    os.getenv(
        "RUN_DEMO_FILL",
        "true",
    ).strip().lower()
    in {"1", "true", "yes", "on"}
)

DEMO_HISTORY_POLLS = int(
    os.getenv(
        "DEMO_HISTORY_POLLS",
        "8",
    )
)

DEMO_HISTORY_POLL_SECONDS = float(
    os.getenv(
        "DEMO_HISTORY_POLL_SECONDS",
        "0.8",
    )
)

STATE_PATH = Path(
    os.getenv(
        "R28_STATE_PATH",
        "/tmp/r28_intent_state.json",
    )
)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()


# ============================================================
# HELPERS
# ============================================================

def dec(value: Any, default: str = "0") -> Decimal:
    try:
        if value is None or value == "":
            return Decimal(default)
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def fmt_decimal(value: Decimal) -> str:
    s = format(value, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


def yes(value: bool) -> str:
    return "✅ YES" if value else "❌ NO"


def quantize_down(value: Decimal, step: Decimal) -> Decimal:
    if step <= 0:
        return value
    units = (value / step).to_integral_value(rounding=ROUND_DOWN)
    return units * step


def step_match(value: Decimal, step: Decimal) -> bool:
    if step <= 0:
        return True
    return value == quantize_down(value, step)


def client_id_valid(client_id: str) -> bool:
    return bool(
        re.fullmatch(
            r"[\.A-Z\:/a-z0-9_-]{1,36}",
            client_id,
        )
    )


def deterministic_client_id(
    prefix: str,
    material: str,
) -> str:
    digest = hashlib.sha256(
        material.encode("utf-8")
    ).hexdigest()[:20]

    return f"{prefix}-{digest}"[:36]


def bool_env(
    name: str,
    default: bool = False,
) -> bool:
    raw = os.getenv(name)

    if raw is None:
        return default

    return raw.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class ContractInfo:
    symbol: str
    min_qty: Decimal
    qty_precision: int
    qty_step: Decimal
    price_precision: int
    price_step: Decimal
    contract_value: Decimal
    min_leverage: int
    max_leverage: int


@dataclass
class Signal:
    symbol: str
    direction: str
    created_ms: int
    signal_id: str


@dataclass
class ExecutionIntent:
    intent_id: str
    signal_id: str
    symbol: str
    direction: str
    side: str
    position_side: str
    quantity: str
    created_ms: int
    expires_ms: int
    client_order_id: str
    state: str = "NEW"
    exchange_order_id: str = ""
    executed_qty: str = "0"
    avg_fill_price: str = "0"
    updated_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass
class DemoLifecycleResult:
    demo_symbol: str
    side: str
    position_side: str
    order_type: str
    client_order_id: str
    post_attempted: bool
    post_accepted: bool
    order_id: str
    history_lookup_attempted: bool
    history_poll_attempts: int
    history_found: bool
    final_status: str
    requested_qty: Decimal
    original_qty: Decimal
    executed_qty: Decimal
    average_fill_price: Decimal
    non_zero_fill: bool
    fill_delta: Decimal
    duplicate_fill_event_blocked: bool
    position_before: Decimal
    position_after: Decimal
    expected_position_delta: Decimal
    observed_position_delta: Decimal
    position_reconciled: bool
    lifecycle_valid: bool


# ============================================================
# ORDER / INTENT STATE MACHINES
# ============================================================

ORDER_TERMINAL = {
    "FILLED",
    "CANCELED",
    "REJECTED",
    "EXPIRED",
}

ORDER_ALLOWED = {
    "NEW": {
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELED",
        "REJECTED",
        "EXPIRED",
    },
    "PARTIALLY_FILLED": {
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELED",
        "EXPIRED",
    },
}


class OrderStateMachine:
    def __init__(self) -> None:
        self.state = "NEW"
        self.executed_qty = Decimal("0")
        self.seen_events: Set[str] = set()

    def apply(
        self,
        status: str,
        executed_qty: Decimal,
        event_id: str,
    ) -> Tuple[bool, Decimal]:

        status = status.upper()

        if event_id in self.seen_events:
            return False, Decimal("0")

        self.seen_events.add(event_id)

        if self.state in ORDER_TERMINAL:
            if status != self.state:
                return False, Decimal("0")

            return False, Decimal("0")

        if (
            status != self.state
            and status
            not in ORDER_ALLOWED.get(
                self.state,
                set(),
            )
        ):
            return False, Decimal("0")

        delta = max(
            Decimal("0"),
            executed_qty - self.executed_qty,
        )

        self.executed_qty = max(
            self.executed_qty,
            executed_qty,
        )

        self.state = status

        return True, delta


INTENT_TERMINAL = {
    "RECONCILED",
    "REJECTED",
    "EXPIRED",
    "FAILED",
}

INTENT_ALLOWED = {
    "NEW": {
        "PREFLIGHT",
        "REJECTED",
        "EXPIRED",
    },
    "PREFLIGHT": {
        "READY",
        "REJECTED",
        "EXPIRED",
    },
    "READY": {
        "TRANSMITTED",
        "REJECTED",
        "EXPIRED",
    },
    "TRANSMITTED": {
        "ACKNOWLEDGED",
        "REJECTED",
        "FAILED",
    },
    "ACKNOWLEDGED": {
        "PARTIALLY_FILLED",
        "FILLED",
        "FAILED",
    },
    "PARTIALLY_FILLED": {
        "PARTIALLY_FILLED",
        "FILLED",
        "FAILED",
    },
    "FILLED": {
        "RECONCILED",
        "FAILED",
    },
}


def transition_intent(
    intent: ExecutionIntent,
    new_state: str,
) -> bool:

    new_state = new_state.upper()
    old = intent.state.upper()

    if old in INTENT_TERMINAL:
        return False

    if new_state not in INTENT_ALLOWED.get(
        old,
        set(),
    ):
        return False

    intent.state = new_state
    intent.updated_ms = int(
        time.time() * 1000
    )

    return True


# ============================================================
# R28 JOURNAL / RESTART RECOVERY
# ============================================================

class IntentJournal:
    def __init__(
        self,
        path: Path,
    ) -> None:
        self.path = path

    def save(
        self,
        intent: ExecutionIntent,
    ) -> None:

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        tmp = self.path.with_suffix(
            self.path.suffix + ".tmp"
        )

        data = asdict(intent)

        raw = json.dumps(
            data,
            separators=(",", ":"),
            sort_keys=True,
        )

        tmp.write_text(
            raw,
            encoding="utf-8",
        )

        os.replace(
            tmp,
            self.path,
        )

    def load(
        self,
    ) -> Optional[ExecutionIntent]:

        if not self.path.exists():
            return None

        raw = self.path.read_text(
            encoding="utf-8"
        )

        data = json.loads(raw)

        return ExecutionIntent(**data)

    def clear(self) -> None:
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


def recovery_decision(
    intent: ExecutionIntent,
    now_ms: int,
) -> str:

    if intent.state in INTENT_TERMINAL:
        return "DO_NOT_TRANSMIT"

    if (
        now_ms > intent.expires_ms
        and intent.state
        in {
            "NEW",
            "PREFLIGHT",
            "READY",
        }
    ):
        return "EXPIRE"

    if intent.state in {
        "TRANSMITTED",
        "ACKNOWLEDGED",
        "PARTIALLY_FILLED",
        "FILLED",
    }:
        return "RECONCILE_ONLY"

    return "PREFLIGHT_ONLY"


# ============================================================
# HTTP CLIENT
# ============================================================
class WeexClient:
    def __init__(
        self,
        session: aiohttp.ClientSession,
    ) -> None:
        self.session = session
        self.api_key = os.getenv(
            "WEEX_API_KEY",
            "",
        ).strip()
        self.secret_key = os.getenv(
            "WEEX_SECRET_KEY",
            "",
        ).strip()
        self.passphrase = os.getenv(
            "WEEX_PASSPHRASE",
            "",
        ).strip()

    def credentials_ready(self) -> bool:
        return bool(
            self.api_key
            and self.secret_key
            and self.passphrase
        )

    def _signature(
        self,
        timestamp: str,
        method: str,
        path: str,
        query_string: str = "",
        body: str = "",
    ) -> str:

        message = (
            timestamp
            + method.upper()
            + path
        )

        if query_string:
            message += "?" + query_string

        message += body

        digest = hmac.new(
            self.secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).digest()

        return base64.b64encode(
            digest
        ).decode("utf-8")

    def signed_headers(
        self,
        method: str,
        path: str,
        query_string: str = "",
        body: str = "",
    ) -> Dict[str, str]:

        if not self.credentials_ready():
            raise RuntimeError(
                "Missing WEEX_API_KEY / "
                "WEEX_SECRET_KEY / "
                "WEEX_PASSPHRASE"
            )

        timestamp = str(
            int(
                time.time()
                * 1000
            )
        )

        return {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": self._signature(
                timestamp,
                method,
                path,
                query_string,
                body,
            ),
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
        }

    async def public_get(
        self,
        path: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Any:

        params = params or {}

        async with self.session.get(
            API_BASE_URL + path,
            params=params,
            timeout=15,
        ) as resp:

            text = await resp.text()

            if resp.status >= 400:
                raise RuntimeError(
                    f"WEEX GET {path} "
                    f"HTTP {resp.status}: "
                    f"{text}"
                )

            return json.loads(text)

    async def private_get(
        self,
        path: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Any:

        params = params or {}

        query = urlencode(
            params
        )

        headers = self.signed_headers(
            "GET",
            path,
            query,
        )

        url = (
            API_BASE_URL
            + path
            + (
                ("?" + query)
                if query
                else ""
            )
        )

        async with self.session.get(
            url,
            headers=headers,
            timeout=15,
        ) as resp:

            text = await resp.text()

            if resp.status >= 400:
                raise RuntimeError(
                    f"WEEX PRIVATE GET "
                    f"{path} "
                    f"HTTP {resp.status}: "
                    f"{text}"
                )

            return json.loads(text)

    async def demo_post(
        self,
        path: str,
        payload: Dict[str, Any],
    ) -> Any:

        global R28_DEMO_POST_ATTEMPTED
        global R28_DEMO_POST_ACCEPTED

        R28_DEMO_POST_ATTEMPTED = True

        body = json.dumps(
            payload,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        headers = self.signed_headers(
            "POST",
            path,
            "",
            body,
        )

        async with self.session.post(
            API_BASE_URL + path,
            data=body.encode("utf-8"),
            headers=headers,
            timeout=15,
        ) as resp:

            text = await resp.text()

            if resp.status >= 400:
                raise RuntimeError(
                    f"WEEX DEMO POST "
                    f"HTTP {resp.status}: "
                    f"{text}"
                )

            data = json.loads(text)

            success = bool(
                data.get(
                    "success",
                    True,
                )
            )

            if not success:
                raise RuntimeError(
                    "WEEX DEMO POST "
                    f"REJECTED: {text}"
                )

            R28_DEMO_POST_ACCEPTED = True

            return data

    async def real_post_blocked(
        self,
        path: str,
        payload: Dict[str, Any],
    ) -> None:

        global R28_REAL_POST_CALLED

        if (
            HARD_REAL_POST_LOCK
            or not LIVE_ORDER_EXECUTION
        ):
            return None

        R28_REAL_POST_CALLED = True

        raise RuntimeError(
            "R28 safety invariant violated: "
            "real POST path became reachable"
        )


# ============================================================
# MARKET / ACCOUNT EXTRACTION
# ============================================================

async def get_api_trading_symbol(
    client: WeexClient,
    symbol: str,
) -> bool:

    data = await client.public_get(
        "/capi/v3/market/apiTradingSymbols"
    )

    return symbol in {
        str(x).upper()
        for x in data
        if isinstance(x, str)
    }


async def get_mark_price(
    client: WeexClient,
    symbol: str,
) -> Decimal:

    data = await client.public_get(
        "/capi/v3/market/symbolPrice",
        {
            "symbol": symbol,
            "priceType": "MARK",
        },
    )

    price = (
        dec(data.get("price"))
        if isinstance(data, dict)
        else Decimal("0")
    )

    if price <= 0:
        raise RuntimeError(
            f"Invalid mark price response "
            f"for {symbol}: {data}"
        )

    return price


async def get_available_balance(
    client: WeexClient,
    asset: str = "USDT",
) -> Decimal:

    data = await client.private_get(
        "/capi/v3/account/balance"
    )

    if not isinstance(
        data,
        list,
    ):
        raise RuntimeError(
            "Unexpected account "
            f"balance response: {data}"
        )

    for row in data:

        if (
            str(
                row.get(
                    "asset",
                    "",
                )
            ).upper()
            == asset.upper()
        ):
            value = dec(
                row.get(
                    "availableBalance"
                )
            )

            if value >= 0:
                return value

    raise RuntimeError(
        f"Unable to find available "
        f"{asset} balance"
    )


def _precision_from_step(
    step: Decimal,
) -> int:

    exponent = (
        step
        .normalize()
        .as_tuple()
        .exponent
    )

    return max(
        0,
        -exponent,
    )


def _pick_filter(
    symbol_row: Dict[str, Any],
    names: Tuple[str, ...],
) -> Optional[Dict[str, Any]]:

    filters = symbol_row.get(
        "filters"
    )

    if not isinstance(
        filters,
        list,
    ):
        return None

    upper_names = {
        n.upper()
        for n in names
    }

    for item in filters:

        if (
            str(
                item.get(
                    "filterType",
                    "",
                )
            ).upper()
            in upper_names
        ):
            return item

    return None


async def get_contract_info(
    client: WeexClient,
    symbol: str,
) -> ContractInfo:

    data = await client.public_get(
        "/capi/v3/market/exchangeInfo",
        {
            "symbol": symbol,
        },
    )

    symbols = (
        data.get(
            "symbols",
            [],
        )
        if isinstance(
            data,
            dict,
        )
        else []
    )

    row = None

    for item in symbols:

        if (
            str(
                item.get(
                    "symbol",
                    "",
                )
            ).upper()
            == symbol.upper()
        ):
            row = item
            break

    if row is None:
        raise RuntimeError(
            "Unable to obtain contract "
            f"metadata for {symbol}"
        )

    lot = (
        _pick_filter(
            row,
            (
                "LOT_SIZE",
                "MARKET_LOT_SIZE",
            ),
        )
        or {}
    )

    price_filter = (
        _pick_filter(
            row,
            (
                "PRICE_FILTER",
            ),
        )
        or {}
    )

    qty_precision = int(
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

    qty_step = dec(
        lot.get("stepSize")
        or row.get("quantityStep")
        or row.get("qtyStep")
        or row.get("sizeStep")
        or (
            "1"
            if qty_precision == 0
            else (
                "0."
                + (
                    "0"
                    * (
                        qty_precision
                        - 1
                    )
                )
                + "1"
            )
        )
    )

    min_qty = dec(
        lot.get("minQty")
        or row.get("minOrderSize")
        or row.get("minQty")
        or row.get("minOrderQty")
        or qty_step
    )

    price_step = dec(
        price_filter.get("tickSize")
        or row.get("priceStep")
        or row.get("tickSize")
        or (
            "1"
            if price_precision == 0
            else (
                "0."
                + (
                    "0"
                    * (
                        price_precision
                        - 1
                    )
                )
                + "1"
            )
        )
    )

    contract_value = dec(
        row.get("contractVal")
        or row.get("contractValue")
        or row.get("contractSize")
        or "0.0001"
    )

    min_lev = int(
        dec(
            row.get("minLeverage")
            or "1"
        )
    )

    max_lev = int(
        dec(
            row.get("maxLeverage")
            or "400"
        )
    )

    return ContractInfo(
        symbol=symbol,
        min_qty=min_qty,
        qty_precision=qty_precision,
        qty_step=qty_step,
        price_precision=price_precision,
        price_step=price_step,
        contract_value=contract_value,
        min_leverage=min_lev,
        max_leverage=max_lev,
    )


async def get_demo_positions(
    client: WeexClient,
) -> List[Dict[str, Any]]:

    data = await client.private_get(
        "/capi/v3/sim/position/allPosition"
    )

    return (
        data
        if isinstance(
            data,
            list,
        )
        else []
    )


def demo_position_size(
    rows: List[Dict[str, Any]],
    symbol: str,
    side: str,
) -> Decimal:

    total = Decimal("0")

    for row in rows:

        if (
            str(
                row.get(
                    "symbol",
                    "",
                )
            ).upper()
            != symbol.upper()
        ):
            continue

        if (
            str(
                row.get(
                    "side",
                    "",
                )
            ).upper()
            != side.upper()
        ):
            continue

        total += abs(
            dec(
                row.get(
                    "size"
                )
            )
        )

    return total


# ============================================================
# QUANTITY / EXPOSURE
# ============================================================

def calculate_entry_margin(
    balance: Decimal,
) -> Decimal:

    return (
        balance
        * ENTRY_PERCENT
        / D100
    )


def calculate_notional(
    margin: Decimal,
) -> Decimal:

    return (
        margin
        * Decimal(
            LEVERAGE
        )
    )


def calculate_quantity(
    notional: Decimal,
    mark_price: Decimal,
    contract: ContractInfo,
) -> Decimal:

    if mark_price <= 0:
        raise RuntimeError(
            "Mark price must be positive"
        )

    raw_quantity = (
        notional
        / mark_price
    )

    return quantize_down(
        raw_quantity,
        contract.qty_step,
    )


def total_exposure_percent() -> Decimal:

    return (
        ENTRY_PERCENT
        + Decimal(
            MAX_PYRAMID_ADDS
        )
        * PYRAMID_SIZE_PERCENT
        + Decimal(
            MAX_BACKUPS
        )
        * BACKUP_SIZE_PERCENT
    )


# ============================================================
# SIGNAL / INTENT SELF TESTS
# ============================================================
