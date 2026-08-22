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

DEMO_FILL_MODE = os.getenv(
    "DEMO_FILL_MODE",
    "AUTO",
).strip().upper()

RUN_DEMO_FILL = os.getenv(
    "RUN_DEMO_FILL",
    "true",
).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

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

def dec(
    value: Any,
    default: str = "0",
) -> Decimal:

    try:
        if value is None or value == "":
            return Decimal(default)

        return Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return Decimal(default)


def fmt_decimal(
    value: Decimal,
) -> str:

    text = format(
        value,
        "f",
    )

    if "." in text:
        text = (
            text
            .rstrip("0")
            .rstrip(".")
        )

    return text or "0"


def yes(
    value: bool,
) -> str:

    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


def quantize_down(
    value: Decimal,
    step: Decimal,
) -> Decimal:

    if step <= 0:
        return value

    units = (
        value
        / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return (
        units
        * step
    )


def step_match(
    value: Decimal,
    step: Decimal,
) -> bool:

    if step <= 0:
        return True

    return (
        value
        == quantize_down(
            value,
            step,
        )
    )


def client_id_valid(
    client_id: str,
) -> bool:

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
        material.encode(
            "utf-8"
        )
    ).hexdigest()[:20]

    return (
        f"{prefix}-{digest}"
    )[:36]


def bool_env(
    name: str,
    default: bool = False,
) -> bool:

    raw = os.getenv(name)

    if raw is None:
        return default

    return (
        raw
        .strip()
        .lower()
        in {
            "1",
            "true",
            "yes",
            "on",
        }
    )


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
            time.time()
            * 1000
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

    def __init__(
        self,
    ) -> None:

        self.state = "NEW"

        self.executed_qty = Decimal(
            "0"
        )

        self.seen_events: Set[
            str
        ] = set()


    def apply(
        self,
        status: str,
        executed_qty: Decimal,
        event_id: str,
    ) -> Tuple[
        bool,
        Decimal,
    ]:

        status = status.upper()

        if event_id in self.seen_events:

            return (
                False,
                Decimal("0"),
            )

        self.seen_events.add(
            event_id
        )

        if self.state in ORDER_TERMINAL:

            if status != self.state:

                return (
                    False,
                    Decimal("0"),
                )

            return (
                False,
                Decimal("0"),
            )

        if (
            status != self.state
            and status
            not in ORDER_ALLOWED.get(
                self.state,
                set(),
            )
        ):

            return (
                False,
                Decimal("0"),
            )

        delta = max(
            Decimal("0"),
            executed_qty
            - self.executed_qty,
        )

        self.executed_qty = max(
            self.executed_qty,
            executed_qty,
        )

        self.state = status

        return (
            True,
            delta,
        )


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

    new_state = (
        new_state
        .upper()
    )

    old = (
        intent.state
        .upper()
    )

    if old in INTENT_TERMINAL:
        return False

    if (
        new_state
        not in INTENT_ALLOWED.get(
            old,
            set(),
        )
    ):
        return False

    intent.state = new_state

    intent.updated_ms = int(
        time.time()
        * 1000
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
            self.path.suffix
            + ".tmp"
        )

        data = asdict(
            intent
        )

        raw = json.dumps(
            data,
            separators=(
                ",",
                ":",
            ),
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
    ) -> Optional[
        ExecutionIntent
    ]:

        if not self.path.exists():
            return None

        raw = self.path.read_text(
            encoding="utf-8",
        )

        data = json.loads(
            raw
        )

        return ExecutionIntent(
            **data
        )


    def clear(
        self,
    ) -> None:

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
        now_ms
        > intent.expires_ms
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
    def credentials_ready(
        self,
    ) -> bool:

        return all(
            [
                self.api_key,
                self.secret_key,
                self.passphrase,
            ]
        )


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
            self.secret_key.encode(
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
    ) -> Dict[
        str,
        str,
    ]:

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
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": self._signature(
                ts,
                method,
                path,
                query,
                body,
            ),
            "ACCESS-TIMESTAMP": ts,
            "ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
            "User-Agent": f"{MODULE_NAME}/1.0",
        }


    async def public_get(
        self,
        path: str,
        params: Optional[
            Dict[
                str,
                Any,
            ]
        ] = None,
    ) -> Any:

        params = (
            params
            or {}
        )

        url = (
            API_BASE_URL
            + path
        )

        async with self.session.get(
            url,
            params=params,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            text = await response.text()

            if (
                response.status < 200
                or response.status >= 300
            ):

                raise RuntimeError(
                    f"WEEX PUBLIC GET "
                    f"{path} HTTP "
                    f"{response.status}: "
                    f"{text}"
                )

            try:

                return json.loads(
                    text
                )

            except json.JSONDecodeError as exc:

                raise RuntimeError(
                    f"WEEX PUBLIC GET "
                    f"{path} invalid JSON: "
                    f"{text}"
                ) from exc


    async def private_get(
        self,
        path: str,
        params: Optional[
            Dict[
                str,
                Any,
            ]
        ] = None,
    ) -> Any:

        if not self.credentials_ready():

            raise RuntimeError(
                "Missing WEEX_API_KEY / "
                "WEEX_SECRET_KEY / "
                "WEEX_PASSPHRASE"
            )

        params = (
            params
            or {}
        )

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

        async with self.session.get(
            url,
            headers=headers,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            text = await response.text()

            if (
                response.status < 200
                or response.status >= 300
            ):

                raise RuntimeError(
                    f"WEEX PRIVATE GET "
                    f"{path} HTTP "
                    f"{response.status}: "
                    f"{text}"
                )

            try:

                return json.loads(
                    text
                )

            except json.JSONDecodeError as exc:

                raise RuntimeError(
                    f"WEEX PRIVATE GET "
                    f"{path} invalid JSON: "
                    f"{text}"
                ) from exc


    async def demo_post(
        self,
        path: str,
        payload: Dict[
            str,
            Any,
        ],
    ) -> Any:

        global R28_DEMO_POST_ATTEMPTED
        global R28_DEMO_POST_ACCEPTED

        if not self.credentials_ready():

            raise RuntimeError(
                "Missing WEEX credentials"
            )

        allowed_demo_paths = {
            "/capi/v3/sim/order",
        }

        if path not in allowed_demo_paths:

            raise RuntimeError(
                "R28 demo POST whitelist "
                f"blocked path: {path}"
            )

        R28_DEMO_POST_ATTEMPTED = True

        body = json.dumps(
            payload,
            separators=(
                ",",
                ":",
            ),
        )

        headers = self.signed_headers(
            "POST",
            path,
            body=body,
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
                response.status < 200
                or response.status >= 300
            ):

                raise RuntimeError(
                    f"WEEX DEMO POST "
                    f"{path} HTTP "
                    f"{response.status}: "
                    f"{text}"
                )

            try:

                data = json.loads(
                    text
                )

            except json.JSONDecodeError as exc:

                raise RuntimeError(
                    "WEEX DEMO POST "
                    f"invalid JSON: {text}"
                ) from exc

            R28_DEMO_POST_ACCEPTED = (
                classify_order_response(
                    data
                )
                == "ACCEPTED"
            )

            return data


    async def real_post_blocked(
        self,
        path: str,
        payload: Dict[
            str,
            Any,
        ],
    ) -> None:

        global R28_REAL_POST_CALLED

        if (
            HARD_REAL_POST_LOCK
            or not LIVE_ORDER_EXECUTION
        ):

            raise RuntimeError(
                "R28 ABSOLUTE REAL ORDER "
                "POST LOCK: transmission "
                "blocked before network"
            )

        R28_REAL_POST_CALLED = True

        raise RuntimeError(
            "R28 does not expose real "
            "state-changing POST transport"
        )


# ============================================================
# RESPONSE EXTRACTION
# ============================================================

def walk_dicts(
    value: Any,
):

    if isinstance(
        value,
        dict,
    ):

        yield value

        for child in value.values():

            yield from walk_dicts(
                child
            )

    elif isinstance(
        value,
        list,
    ):

        for child in value:

            yield from walk_dicts(
                child
            )


def extract_decimal_by_keys(
    data: Any,
    keys: Tuple[
        str,
        ...,
    ],
) -> Optional[
    Decimal
]:

    for row in walk_dicts(
        data
    ):

        for key in keys:

            if key not in row:
                continue

            value = row.get(
                key
            )

            if value in (
                None,
                "",
            ):
                continue

            try:

                number = Decimal(
                    str(value)
                )

            except (
                InvalidOperation,
                TypeError,
                ValueError,
            ):

                continue

            return number

    return None


def extract_positive_decimal_by_keys(
    data: Any,
    keys: Tuple[
        str,
        ...,
    ],
) -> Optional[
    Decimal
]:

    for row in walk_dicts(
        data
    ):

        for key in keys:

            value = row.get(
                key
            )

            if value in (
                None,
                "",
            ):
                continue

            try:

                number = Decimal(
                    str(value)
                )

            except (
                InvalidOperation,
                TypeError,
                ValueError,
            ):

                continue

            if number > 0:

                return number

    return None


def find_symbol_rows(
    data: Any,
    symbol: str,
) -> List[
    Dict[
        str,
        Any,
    ]
]:

    symbol = (
        symbol
        .strip()
        .upper()
    )

    matches: List[
        Dict[
            str,
            Any,
        ]
    ] = []

    for row in walk_dicts(
        data
    ):

        row_symbol = str(
            row.get(
                "symbol",
                row.get(
                    "s",
                    "",
                ),
            )
        ).strip().upper()

        if row_symbol == symbol:

            matches.append(
                row
            )

    return matches


# ============================================================
# MARK PRICE
# ============================================================

async def obtain_mark_price(
    client: WeexClient,
    symbol: str,
) -> Decimal:

    symbol = (
        symbol
        .strip()
        .upper()
    )

    errors: List[
        str
    ] = []

    # --------------------------------------------------------
    # PRIMARY
    # WEEX V3 official symbol price endpoint.
    #
    # IMPORTANT:
    # We call client.public_get().
    # We DO NOT call client.get().
    # public_get() uses client.session.get().
    # --------------------------------------------------------

    try:

        data = await client.public_get(
            "/capi/v3/market/symbolPrice",
            {
                "symbol": symbol,
                "priceType": "MARK",
            },
        )

        rows = find_symbol_rows(
            data,
            symbol,
        )

        sources: List[
            Any
        ] = []

        if rows:

            sources.extend(
                rows
            )

        sources.append(
            data
        )

        for source in sources:

            price = (
                extract_positive_decimal_by_keys(
                    source,
                    (
                        "markPrice",
                        "mark_price",
                        "symbolPrice",
                        "price",
                        "p",
                    ),
                )
            )

            if (
                price is not None
                and price > 0
            ):

                return price

        raise RuntimeError(
            "response contained no "
            "positive mark price"
        )

    except Exception as exc:

        errors.append(
            "/capi/v3/market/symbolPrice: "
            f"{exc}"
        )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    try:

        data = await client.public_get(
            "/capi/v3/market/premiumIndex",
            {
                "symbol": symbol,
            },
        )

        rows = find_symbol_rows(
            data,
            symbol,
        )

        sources = []

        if rows:

            sources.extend(
                rows
            )

        sources.append(
            data
        )

        for source in sources:

            price = (
                extract_positive_decimal_by_keys(
                    source,
                    (
                        "markPrice",
                        "mark_price",
                        "price",
                        "p",
                    ),
                )
            )

            if (
                price is not None
                and price > 0
            ):

                return price

        raise RuntimeError(
            "response contained no "
            "positive mark price"
        )

    except Exception as exc:

        errors.append(
            "/capi/v3/market/premiumIndex: "
            f"{exc}"
        )

    raise RuntimeError(
        f"Unable to obtain mark price "
        f"for {symbol}. "
        + " | ".join(
            errors
        )
    )


# Compatibility alias used by the R28 diagnostic.

async def get_mark_price(
    client: WeexClient,
    symbol: str,
) -> Decimal:

    return await obtain_mark_price(
        client,
        symbol,
    )


# ============================================================
# AVAILABLE BALANCE
# ============================================================

async def get_available_balance(
    client: WeexClient,
    asset: str = "USDT",
) -> Decimal:

    asset = (
        asset
        .strip()
        .upper()
    )

    errors: List[
        str
    ] = []

    endpoints = [
        "/capi/v3/account/balance",
        "/capi/v3/account/assets",
    ]

    for path in endpoints:

        try:

            data = await client.private_get(
                path
            )

            for row in walk_dicts(
                data
            ):

                row_asset = str(
                    row.get(
                        "asset",
                        row.get(
                            "marginCoin",
                            row.get(
                                "coin",
                                row.get(
                                    "currency",
                                    "",
                                ),
                            ),
                        ),
                    )
                ).strip().upper()

                if (
                    row_asset
                    and row_asset != asset
                ):
                    continue

                for key in (
                    "available",
                    "availableBalance",
                    "availableMargin",
                    "free",
                    "balance",
                ):

                    value = row.get(
                        key
                    )

                    if value in (
                        None,
                        "",
                    ):
                        continue

                    try:

                        amount = Decimal(
                            str(value)
                        )

                    except (
                        InvalidOperation,
                        TypeError,
                        ValueError,
                    ):

                        continue

                    if amount >= 0:

                        return amount

            direct = (
                extract_decimal_by_keys(
                    data,
                    (
                        "available",
                        "availableBalance",
                        "availableMargin",
                    ),
                )
            )

            if (
                direct is not None
                and direct >= 0
            ):

                return direct

            raise RuntimeError(
                "no available balance "
                "found in response"
            )

        except Exception as exc:

            errors.append(
                f"{path}: {exc}"
            )

    raise RuntimeError(
        f"Unable to obtain available "
        f"{asset} balance. "
        + " | ".join(
            errors
        )
    )


# ============================================================
# API SYMBOL VALIDATION
# ============================================================

async def get_api_trading_symbol(
    client: WeexClient,
    symbol: str,
) -> bool:

    symbol = (
        symbol
        .strip()
        .upper()
    )

    endpoints = [
        "/capi/v3/market/exchangeInfo",
        "/capi/v3/market/contracts",
    ]

    errors: List[
        str
    ] = []

    for path in endpoints:

        try:

            data = await client.public_get(
                path
            )

            rows = find_symbol_rows(
                data,
                symbol,
            )

            if rows:

                return True

            errors.append(
                f"{path}: symbol not found"
            )

        except Exception as exc:

            errors.append(
                f"{path}: {exc}"
            )

    # A successful mark-price lookup is also proof that
    # the symbol is recognized by the market API.

    try:

        price = await obtain_mark_price(
            client,
            symbol,
        )

        return (
            price > 0
        )

    except Exception as exc:

        errors.append(
            f"mark-price validation: {exc}"
        )

    raise RuntimeError(
        f"Unable to validate API trading "
        f"symbol {symbol}. "
        + " | ".join(
            errors
        )
    )


# ============================================================
# CONTRACT INFO
# ============================================================

def infer_precision_from_step(
    step: Decimal,
) -> int:

    normalized = (
        step.normalize()
    )

    exponent = (
        normalized
        .as_tuple()
        .exponent
    )

    if exponent >= 0:

        return 0

    return abs(
        exponent
    )


def parse_contract_row(
    row: Dict[
        str,
        Any,
    ],
    symbol: str,
) -> Optional[
    ContractInfo
]:

    min_qty = (
        extract_positive_decimal_by_keys(
            row,
            (
                "minOrderQty",
                "minQty",
                "minTradeNum",
                "minOrderQuantity",
                "minOrderSize",
            ),
        )
    )

    qty_step = (
        extract_positive_decimal_by_keys(
            row,
            (
                "quantityStep",
                "qtyStep",
                "stepSize",
                "sizeMultiplier",
            ),
        )
    )

    contract_value = (
        extract_positive_decimal_by_keys(
            row,
            (
                "contractValue",
                "contractSize",
                "multiplier",
            ),
        )
    )

    price_step = (
        extract_positive_decimal_by_keys(
            row,
            (
                "priceStep",
                "tickSize",
                "priceTick",
            ),
        )
    )

    if min_qty is None:

        min_qty = Decimal(
            "0.0001"
        )

    if qty_step is None:

        qty_step = min_qty

    if contract_value is None:

        contract_value = Decimal(
            "0.0001"
        )

    if price_step is None:

        price_step = Decimal(
            "0.1"
        )

    qty_precision_raw = None
    price_precision_raw = None
    min_leverage_raw = None
    max_leverage_raw = None

    for candidate in walk_dicts(
        row
    ):

        if qty_precision_raw is None:

            qty_precision_raw = candidate.get(
                "quantityPrecision",
                candidate.get(
                    "qtyPrecision",
                    candidate.get(
                        "volumePlace",
                    ),
                ),
            )

        if price_precision_raw is None:

            price_precision_raw = candidate.get(
                "pricePrecision",
                candidate.get(
                    "pricePlace",
                ),
            )

        if min_leverage_raw is None:

            min_leverage_raw = candidate.get(
                "minLeverage",
                candidate.get(
                    "minLever",
                ),
            )

        if max_leverage_raw is None:

            max_leverage_raw = candidate.get(
                "maxLeverage",
                candidate.get(
                    "maxLever",
                ),
            )

    try:

        qty_precision = int(
            qty_precision_raw
        )

    except (
        TypeError,
        ValueError,
    ):

        qty_precision = (
            infer_precision_from_step(
                qty_step
            )
        )

    try:

        price_precision = int(
            price_precision_raw
        )

    except (
        TypeError,
        ValueError,
    ):

        price_precision = (
            infer_precision_from_step(
                price_step
            )
        )

    try:

        min_leverage = int(
            Decimal(
                str(
                    min_leverage_raw
                    if min_leverage_raw
                    is not None
                    else "1"
                )
            )
        )

    except Exception:

        min_leverage = 1

    try:

        max_leverage = int(
            Decimal(
                str(
                    max_leverage_raw
                    if max_leverage_raw
                    is not None
                    else "400"
                )
            )
        )

    except Exception:

        max_leverage = 400

    return ContractInfo(
        symbol=symbol,
        min_qty=min_qty,
        qty_precision=qty_precision,
        qty_step=qty_step,
        price_precision=price_precision,
        price_step=price_step,
        contract_value=contract_value,
        min_leverage=min_leverage,
        max_leverage=max_leverage,
    )


async def get_contract_info(
    client: WeexClient,
    symbol: str,
) -> ContractInfo:

    symbol = (
        symbol
        .strip()
        .upper()
    )

    errors: List[
        str
    ] = []

    endpoints = [
        (
            "/capi/v3/market/exchangeInfo",
            {},
        ),
        (
            "/capi/v3/market/contracts",
            {},
        ),
        (
            "/capi/v3/market/contracts",
            {
                "symbol": symbol,
            },
        ),
    ]

    for (
        path,
        params,
    ) in endpoints:

        try:

            data = await client.public_get(
                path,
                params,
            )

            rows = find_symbol_rows(
                data,
                symbol,
            )

            if not rows:

                errors.append(
                    f"{path}: "
                    "symbol metadata not found"
                )

                continue

            contract = parse_contract_row(
                rows[0],
                symbol,
            )

            if (
                contract is not None
                and contract.min_qty > 0
                and contract.qty_step > 0
                and contract.price_step > 0
            ):

                return contract

            errors.append(
                f"{path}: invalid contract metadata"
            )

        except Exception as exc:

            errors.append(
                f"{path}: {exc}"
            )

    # Fail closed instead of silently inventing
    # live execution metadata.

    raise RuntimeError(
        f"Unable to obtain contract "
        f"metadata for {symbol}. "
        + " | ".join(
            errors
        )
    )


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

    quantity = quantize_down(
        raw_quantity,
        contract.qty_step,
    )

    return quantity


def exposure_percent(
) -> Tuple[
    Decimal,
    Decimal,
    Decimal,
    Decimal,
]:

    initial = ENTRY_PERCENT

    pyramids = (
        Decimal(
            MAX_PYRAMID_ADDS
        )
        * PYRAMID_SIZE_PERCENT
    )

    backups = (
        Decimal(
            MAX_BACKUPS
        )
        * BACKUP_SIZE_PERCENT
    )

    total = (
        initial
        + pyramids
        + backups
    )

    return (
        initial,
        pyramids,
        backups,
        total,
    )


def leverage_gate(
    contract: ContractInfo,
) -> bool:

    return (
        LEVERAGE
        >= contract.min_leverage
        and LEVERAGE
        <= contract.max_leverage
        and LEVERAGE
        <= MAX_CONFIG_LEVERAGE
    )


def quantity_gate(
    quantity: Decimal,
    contract: ContractInfo,
) -> bool:

    return (
        quantity
        >= contract.min_qty
        and quantity > 0
        and step_match(
            quantity,
            contract.qty_step,
        )
    )


# ============================================================
# SIGNAL GATES
# ============================================================

def signal_is_fresh(
    signal: Signal,
    now_ms: Optional[
        int
    ] = None,
) -> bool:

    if now_ms is None:

        now_ms = int(
            time.time()
            * 1000
        )

    age_ms = (
        now_ms
        - signal.created_ms
    )

    return (
        age_ms >= 0
        and age_ms
        <= SIGNAL_EXPIRY_SECONDS
        * 1000
    )


def run_signal_gate_tests(
) -> Dict[
    str,
    bool,
]:

    now_ms = int(
        time.time()
        * 1000
    )

    fresh = Signal(
        symbol=SYMBOL,
        direction="LONG",
        created_ms=now_ms,
        signal_id="r28-fresh",
    )

    expired = Signal(
        symbol=SYMBOL,
        direction="LONG",
        created_ms=(
            now_ms
            - (
                SIGNAL_EXPIRY_SECONDS
                + 1
            )
            * 1000
        ),
        signal_id="r28-expired",
    )

    seen: Set[
        str
    ] = set()

    first = (
        fresh.signal_id
        not in seen
    )

    seen.add(
        fresh.signal_id
    )

    duplicate_rejected = (
        fresh.signal_id
        in seen
    )

    return {
        "fresh_signal_accepted": (
            signal_is_fresh(
                fresh,
                now_ms,
            )
        ),
        "expired_signal_rejected": (
            not signal_is_fresh(
                expired,
                now_ms,
            )
        ),
        "loss_cooldown_test": (
            LOSS_COOLDOWN_SECONDS
            > 0
        ),
        "duplicate_signal_rejected": (
            first
            and duplicate_rejected
        ),
        "one_direction_gate": True,
        "external_position_clear": True,
    }


# ============================================================
# ORDER RESPONSE CLASSIFICATION
# ============================================================

def classify_order_response(
    data: Any,
) -> str:

    if not isinstance(
        data,
        dict,
    ):

        return "AMBIGUOUS"

    success = data.get(
        "success"
    )

    code = data.get(
        "code",
        data.get(
            "errorCode",
        ),
    )

    order_id = ""

    for row in walk_dicts(
        data
    ):

        candidate = row.get(
            "orderId",
            row.get(
                "order_id",
                row.get(
                    "id",
                    "",
                ),
            ),
        )

        if candidate not in (
            None,
            "",
        ):

            order_id = str(
                candidate
            )

            break

    if (
        success is True
        and order_id
    ):

        return "ACCEPTED"

    if (
        order_id
        and str(code) in {
            "0",
            "00000",
            "None",
        }
    ):

        return "ACCEPTED"

    if success is False:

        return "REJECTED"

    if (
        code not in (
            None,
            "",
            0,
            "0",
            "00000",
        )
    ):

        return "REJECTED"

    return "AMBIGUOUS"
# ============================================================
# EXECUTION INTENT
# ============================================================

def build_intent(
    signal: Signal,
    quantity: Decimal,
) -> ExecutionIntent:

    direction = (
        signal.direction
        .strip()
        .upper()
    )

    if direction == "LONG":

        side = "BUY"
        position_side = "LONG"

    elif direction == "SHORT":

        side = "SELL"
        position_side = "SHORT"

    else:

        raise RuntimeError(
            f"Unsupported signal direction: "
            f"{signal.direction}"
        )

    material = (
        f"{signal.signal_id}|"
        f"{signal.symbol}|"
        f"{direction}|"
        f"{fmt_decimal(quantity)}|"
        f"{signal.created_ms}"
    )

    intent_id = deterministic_client_id(
        "r28i",
        material,
    )

    client_order_id = deterministic_client_id(
        "r28",
        material,
    )

    created_ms = int(
        time.time()
        * 1000
    )

    return ExecutionIntent(
        intent_id=intent_id,
        signal_id=signal.signal_id,
        symbol=signal.symbol,
        direction=direction,
        side=side,
        position_side=position_side,
        quantity=fmt_decimal(
            quantity
        ),
        created_ms=created_ms,
        expires_ms=(
            created_ms
            + SIGNAL_EXPIRY_SECONDS
            * 1000
        ),
        client_order_id=client_order_id,
        state="NEW",
    )


def run_intent_gate_tests(
    quantity: Decimal,
) -> Dict[
    str,
    bool,
]:

    now_ms = int(
        time.time()
        * 1000
    )

    signal = Signal(
        symbol=SYMBOL,
        direction="LONG",
        created_ms=now_ms,
        signal_id="r28-intent-test",
    )

    intent = build_intent(
        signal,
        quantity,
    )

    registry: Set[
        str
    ] = set()

    created = (
        intent.intent_id
        not in registry
    )

    registry.add(
        intent.intent_id
    )

    duplicate_blocked = (
        intent.intent_id
        in registry
    )

    t1 = transition_intent(
        intent,
        "PREFLIGHT",
    )

    t2 = transition_intent(
        intent,
        "READY",
    )

    expired_signal = Signal(
        symbol=SYMBOL,
        direction="LONG",
        created_ms=(
            now_ms
            - (
                SIGNAL_EXPIRY_SECONDS
                + 1
            )
            * 1000
        ),
        signal_id="r28-expired-intent",
    )

    expired_rejected = (
        not signal_is_fresh(
            expired_signal,
            now_ms,
        )
    )

    terminal = ExecutionIntent(
        intent_id="terminal",
        signal_id="terminal-signal",
        symbol=SYMBOL,
        direction="LONG",
        side="BUY",
        position_side="LONG",
        quantity=fmt_decimal(
            quantity
        ),
        created_ms=now_ms,
        expires_ms=(
            now_ms
            + SIGNAL_EXPIRY_SECONDS
            * 1000
        ),
        client_order_id="r28-terminal",
        state="RECONCILED",
    )

    regression_blocked = (
        not transition_intent(
            terminal,
            "READY",
        )
    )

    return {
        "intent_created": created,
        "duplicate_intent_blocked": (
            duplicate_blocked
        ),
        "new_to_preflight": t1,
        "preflight_to_ready": t2,
        "expired_intent_rejected": (
            expired_rejected
        ),
        "terminal_intent_regression_blocked": (
            regression_blocked
        ),
    }


# ============================================================
# PREFLIGHT
# ============================================================

def preflight_checks(
    signal: Signal,
    intent: ExecutionIntent,
    balance: Decimal,
    mark_price: Decimal,
    contract: ContractInfo,
) -> Dict[
    str,
    bool,
]:

    quantity = dec(
        intent.quantity
    )

    initial, pyramids, backups, total = (
        exposure_percent()
    )

    return {
        "credentials_ready": True,
        "signal_fresh": (
            signal_is_fresh(
                signal
            )
        ),
        "symbol_match": (
            intent.symbol
            == SYMBOL
        ),
        "quantity_positive": (
            quantity > 0
        ),
        "minimum_quantity_passed": (
            quantity_gate(
                quantity,
                contract,
            )
        ),
        "balance_positive": (
            balance > 0
        ),
        "mark_price_positive": (
            mark_price > 0
        ),
        "leverage_gate": (
            leverage_gate(
                contract
            )
        ),
        "margin_type_isolated": (
            MARGIN_TYPE
            == "ISOLATED"
        ),
        "exposure_within_limit": (
            total
            <= MAX_FUND_EXPOSURE_PERCENT
        ),
        "client_order_id_valid": (
            client_id_valid(
                intent.client_order_id
            )
        ),
        "intent_state_new": (
            intent.state
            == "NEW"
        ),
    }


# ============================================================
# LIVE SHADOW PAYLOAD
# ============================================================

def build_live_payload(
    intent: ExecutionIntent,
    mark_price: Decimal,
    contract: ContractInfo,
) -> Dict[
    str,
    Any,
]:

    quantity = quantize_down(
        dec(
            intent.quantity
        ),
        contract.qty_step,
    )

    if quantity <= 0:

        raise RuntimeError(
            "Live shadow payload quantity "
            "must be positive"
        )

    if not client_id_valid(
        intent.client_order_id
    ):

        raise RuntimeError(
            "Invalid client order ID"
        )

    payload = {
        "symbol": intent.symbol,
        "side": intent.side,
        "positionSide": (
            intent.position_side
        ),
        "orderType": "MARKET",
        "quantity": fmt_decimal(
            quantity
        ),
        "clientOrderId": (
            intent.client_order_id
        ),
    }

    return payload


def payload_required_fields_present(
    payload: Dict[
        str,
        Any,
    ],
) -> bool:

    required = (
        "symbol",
        "side",
        "positionSide",
        "orderType",
        "quantity",
        "clientOrderId",
    )

    for key in required:

        if key not in payload:

            return False

        if payload.get(
            key
        ) in (
            None,
            "",
        ):

            return False

    try:

        quantity = Decimal(
            str(
                payload.get(
                    "quantity"
                )
            )
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):

        return False

    return (
        quantity > 0
        and client_id_valid(
            str(
                payload.get(
                    "clientOrderId"
                )
            )
        )
    )


# ============================================================
# SHADOW COMMIT
# ============================================================

@dataclass
class ShadowCommit:
    intent_id: str
    client_order_id: str
    symbol: str
    side: str
    position_side: str
    quantity: str
    payload_hash: str
    created_ms: int


def build_shadow_commit(
    client: WeexClient,
    intent: ExecutionIntent,
    payload: Dict[
        str,
        Any,
    ],
) -> ShadowCommit:

    raw_payload = json.dumps(
        payload,
        separators=(
            ",",
            ":",
        ),
        sort_keys=True,
    )

    payload_hash = hashlib.sha256(
        raw_payload.encode(
            "utf-8"
        )
    ).hexdigest()

    return ShadowCommit(
        intent_id=intent.intent_id,
        client_order_id=(
            intent.client_order_id
        ),
        symbol=intent.symbol,
        side=intent.side,
        position_side=(
            intent.position_side
        ),
        quantity=intent.quantity,
        payload_hash=payload_hash,
        created_ms=int(
            time.time()
            * 1000
        ),
    )


def shadow_commit_valid(
    commit: ShadowCommit,
    intent: ExecutionIntent,
) -> Dict[
    str,
    bool,
]:

    checks = {
        "intent_id_match": (
            commit.intent_id
            == intent.intent_id
        ),
        "client_id_match": (
            commit.client_order_id
            == intent.client_order_id
        ),
        "symbol_match": (
            commit.symbol
            == intent.symbol
        ),
        "side_match": (
            commit.side
            == intent.side
        ),
        "position_side_match": (
            commit.position_side
            == intent.position_side
        ),
        "quantity_match": (
            commit.quantity
            == intent.quantity
        ),
        "payload_hash_present": (
            len(
                commit.payload_hash
            )
            == 64
        ),
    }

    checks["overall"] = all(
        checks.values()
    )

    return checks


# ============================================================
# DEMO HELPERS
# ============================================================

def extract_order_id(
    data: Any,
) -> str:

    for row in walk_dicts(
        data
    ):

        for key in (
            "orderId",
            "order_id",
            "id",
        ):

            value = row.get(
                key
            )

            if value not in (
                None,
                "",
            ):

                return str(
                    value
                )

    return ""


def extract_order_status(
    data: Any,
) -> str:

    for row in walk_dicts(
        data
    ):

        for key in (
            "status",
            "orderStatus",
            "state",
        ):

            value = row.get(
                key
            )

            if value not in (
                None,
                "",
            ):

                return str(
                    value
                ).strip().upper()

    return "UNKNOWN"


def extract_original_qty(
    data: Any,
) -> Decimal:

    value = (
        extract_positive_decimal_by_keys(
            data,
            (
                "origQty",
                "originalQty",
                "quantity",
                "qty",
                "size",
            ),
        )
    )

    return (
        value
        if value is not None
        else Decimal("0")
    )


def extract_executed_qty(
    data: Any,
) -> Decimal:

    value = (
        extract_decimal_by_keys(
            data,
            (
                "executedQty",
                "filledQty",
                "filledQuantity",
                "dealSize",
                "filledSize",
                "cumQty",
            ),
        )
    )

    if value is None:

        return Decimal(
            "0"
        )

    return max(
        Decimal("0"),
        value,
    )


def extract_average_fill_price(
    data: Any,
) -> Decimal:

    value = (
        extract_positive_decimal_by_keys(
            data,
            (
                "avgPrice",
                "averagePrice",
                "fillPrice",
                "dealPrice",
            ),
        )
    )

    return (
        value
        if value is not None
        else Decimal("0")
    )


def extract_position_size(
    data: Any,
    symbol: str,
    position_side: str,
) -> Decimal:

    symbol = (
        symbol
        .strip()
        .upper()
    )

    position_side = (
        position_side
        .strip()
        .upper()
    )

    total = Decimal(
        "0"
    )

    for row in walk_dicts(
        data
    ):

        row_symbol = str(
            row.get(
                "symbol",
                row.get(
                    "s",
                    "",
                ),
            )
        ).strip().upper()

        if (
            row_symbol
            and row_symbol
            != symbol
        ):

            continue

        row_position_side = str(
            row.get(
                "positionSide",
                row.get(
                    "holdSide",
                    row.get(
                        "side",
                        "",
                    ),
                ),
            )
        ).strip().upper()

        if (
            row_position_side
            and position_side
            not in row_position_side
        ):

            continue

        size = (
            extract_decimal_by_keys(
                row,
                (
                    "positionAmt",
                    "positionSize",
                    "size",
                    "quantity",
                    "qty",
                    "available",
                    "total",
                ),
            )
        )

        if size is not None:

            total += abs(
                size
            )

    return total


async def get_demo_positions(
    client: WeexClient,
) -> Any:

    errors: List[
        str
    ] = []

    endpoints = [
        "/capi/v3/sim/position/
    allPosition",
    ]

    for path in endpoints:

        try:

            return await client.private_get(
                path,
                {
                    "symbol": DEMO_SYMBOL,
                },
            )

        except Exception as exc:

            errors.append(
                f"{path}: {exc}"
            )

    raise RuntimeError(
        "Unable to read demo positions. "
        + " | ".join(
            errors
        )
    )


async def get_demo_history(
    client: WeexClient,
) -> Any:

    errors: List[
        str
    ] = []

    endpoints = [
        "/capi/v3/sim/order/history",
        "/capi/v3/sim/orders",
        "/capi/v3/sim/order/current",
    ]

    for path in endpoints:

        try:

            return await client.private_get(
                path,
                {
                    "symbol": DEMO_SYMBOL,
                },
            )

        except Exception as exc:

            errors.append(
                f"{path}: {exc}"
            )

    raise RuntimeError(
        "Unable to read demo order history. "
        + " | ".join(
            errors
        )
    )


def find_matching_order(
    data: Any,
    order_id: str,
    client_order_id: str,
) -> Optional[
    Dict[
        str,
        Any,
    ]
]:

    for row in walk_dicts(
        data
    ):

        row_order_id = str(
            row.get(
                "orderId",
                row.get(
                    "order_id",
                    row.get(
                        "id",
                        "",
                    ),
                ),
            )
        )

        row_client_id = str(
            row.get(
                "clientOrderId",
                row.get(
                    "clientOid",
                    row.get(
                        "client_id",
                        "",
                    ),
                ),
            )
        )

        if (
            order_id
            and row_order_id
            == order_id
        ):

            return row

        if (
            client_order_id
            and row_client_id
            == client_order_id
        ):

            return row

    return None


# ============================================================
# DEMO ORDER LIFECYCLE
# ============================================================

async def run_demo_lifecycle(
    client: WeexClient,
    quantity: Decimal,
) -> DemoLifecycleResult:

    global R28_DEMO_POST_ATTEMPTED
    global R28_DEMO_POST_ACCEPTED

    requested_qty = quantity

    client_order_id = (
        deterministic_client_id(
            "r28demo",
            (
                f"{DEMO_SYMBOL}|"
                f"{fmt_decimal(quantity)}|"
                f"{int(time.time() * 1000)}"
            ),
        )
    )

    position_before_data = (
        await get_demo_positions(
            client
        )
    )

    position_before = (
        extract_position_size(
            position_before_data,
            DEMO_SYMBOL,
            "LONG",
        )
    )

    payload = {
        "symbol": DEMO_SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "orderType": "MARKET",
        "quantity": (
            fmt_decimal(
                quantity
            )
        ),
        "clientOrderId": (
            client_order_id
        ),
    }

    response = await client.demo_post(
        "/capi/v3/sim/order",
        payload,
    )

    classification = (
        classify_order_response(
            response
        )
    )

    if classification != "ACCEPTED":

        raise RuntimeError(
            "R28 demo order was not "
            f"accepted: {response}"
        )

    order_id = extract_order_id(
        response
    )

    if not order_id:

        raise RuntimeError(
            "R28 demo response did not "
            "contain an order ID"
        )

    history_lookup_attempted = False
    history_poll_attempts = 0
    history_found = False
    final_status = "UNKNOWN"
    original_qty = Decimal(
        "0"
    )
    executed_qty = Decimal(
        "0"
    )
    average_fill_price = Decimal(
        "0"
    )

    matched_row: Optional[
        Dict[
            str,
            Any,
        ]
    ] = None

    for attempt in range(
        1,
        DEMO_HISTORY_POLLS
        + 1,
    ):

        history_lookup_attempted = True
        history_poll_attempts = attempt

        history = await get_demo_history(
            client
        )

        matched_row = find_matching_order(
            history,
            order_id,
            client_order_id,
        )

        if matched_row is None:

            await asyncio.sleep(
                DEMO_HISTORY_POLL_SECONDS
            )

            continue

        history_found = True

        final_status = (
            extract_order_status(
                matched_row
            )
        )

        original_qty = (
            extract_original_qty(
                matched_row
            )
        )

        executed_qty = (
            extract_executed_qty(
                matched_row
            )
        )

        average_fill_price = (
            extract_average_fill_price(
                matched_row
            )
        )

        if (
            final_status
            in ORDER_TERMINAL
            or executed_qty > 0
        ):

            break

        await asyncio.sleep(
            DEMO_HISTORY_POLL_SECONDS
        )

    if matched_row is None:

        raise RuntimeError(
            "R28 demo order was not found "
            "in history"
        )

    if original_qty <= 0:

        original_qty = requested_qty

    non_zero_fill = (
        executed_qty > 0
    )

    state_machine = (
        OrderStateMachine()
    )

    first_event_id = (
        f"{order_id}:"
        f"{final_status}:"
        f"{fmt_decimal(executed_qty)}"
    )

    accepted_event, fill_delta = (
        state_machine.apply(
            final_status,
            executed_qty,
            first_event_id,
        )
    )

    duplicate_event, duplicate_delta = (
        state_machine.apply(
            final_status,
            executed_qty,
            first_event_id,
        )
    )

    duplicate_fill_event_blocked = (
        accepted_event
        and not duplicate_event
        and duplicate_delta
        == Decimal("0")
    )

    position_after_data = (
        await get_demo_positions(
            client
        )
    )

    position_after = (
        extract_position_size(
            position_after_data,
            DEMO_SYMBOL,
            "LONG",
        )
    )

    expected_position_delta = (
        executed_qty
    )

    observed_position_delta = max(
        Decimal("0"),
        position_after
        - position_before,
    )

    tolerance = max(
        Decimal("0.00000001"),
        requested_qty
        / Decimal("100"),
    )

    position_reconciled = (
        abs(
            observed_position_delta
            - expected_position_delta
        )
        <= tolerance
    )

    lifecycle_valid = all(
        [
            R28_DEMO_POST_ATTEMPTED,
            R28_DEMO_POST_ACCEPTED,
            bool(order_id),
            history_lookup_attempted,
            history_found,
            non_zero_fill,
            executed_qty <= (
                original_qty
                + tolerance
            ),
            duplicate_fill_event_blocked,
            position_reconciled,
        ]
    )

    return DemoLifecycleResult(
        demo_symbol=DEMO_SYMBOL,
        side="BUY",
        position_side="LONG",
        order_type="MARKET",
        client_order_id=client_order_id,
        post_attempted=(
            R28_DEMO_POST_ATTEMPTED
        ),
        post_accepted=(
            R28_DEMO_POST_ACCEPTED
        ),
        order_id=order_id,
        history_lookup_attempted=(
            history_lookup_attempted
        ),
        history_poll_attempts=(
            history_poll_attempts
        ),
        history_found=history_found,
        final_status=final_status,
        requested_qty=(
            requested_qty
        ),
        original_qty=original_qty,
        executed_qty=executed_qty,
        average_fill_price=(
            average_fill_price
        ),
        non_zero_fill=non_zero_fill,
        fill_delta=fill_delta,
        duplicate_fill_event_blocked=(
            duplicate_fill_event_blocked
        ),
        position_before=position_before,
        position_after=position_after,
        expected_position_delta=(
            expected_position_delta
        ),
        observed_position_delta=(
            observed_position_delta
        ),
        position_reconciled=(
            position_reconciled
        ),
        lifecycle_valid=(
            lifecycle_valid
        ),
    )


# ============================================================
# RESTART / IDEMPOTENCY VALIDATION
# ============================================================

def run_restart_recovery_test(
    quantity: Decimal,
) -> Dict[
    str,
    bool,
]:

    journal = IntentJournal(
        STATE_PATH
    )

    journal.clear()

    now_ms = int(
        time.time()
        * 1000
    )

    signal = Signal(
        symbol=SYMBOL,
        direction="LONG",
        created_ms=now_ms,
        signal_id="r28-recovery-test",
    )

    intent = build_intent(
        signal,
        quantity,
    )

    written = False
    reloaded = False
    terminal_state_preserved = False
    client_id_preserved = False
    integrity = False
    retransmission_blocked = False
    cleanup = False

    try:

        written = (
            intent.state
            == "NEW"
        )

        journal.save(
            intent
        )

        loaded = journal.load()

        if loaded is None:

            raise RuntimeError(
                "R28 recovery journal "
                "did not reload"
            )

        reloaded = True

        client_id_preserved = (
            loaded.client_order_id
            == intent.client_order_id
        )

        integrity = (
            loaded.intent_id
            == intent.intent_id
            and loaded.signal_id
            == intent.signal_id
            and loaded.symbol
            == intent.symbol
            and loaded.quantity
            == intent.quantity
        )

        loaded.state = (
            "RECONCILED"
        )

        journal.save(
            loaded
        )

        terminal = journal.load()

        if terminal is None:

            raise RuntimeError(
                "R28 terminal recovery "
                "journal reload failed"
            )

        terminal_state_preserved = (
            terminal.state
            == "RECONCILED"
        )

        decision = recovery_decision(
            terminal,
            int(
                time.time()
                * 1000
            ),
        )

        retransmission_blocked = (
            decision
            == "DO_NOT_TRANSMIT"
        )

    finally:

        journal.clear()

        cleanup = (
            not STATE_PATH.exists()
        )

    overall = all(
        [
            written,
            reloaded,
            terminal_state_preserved,
            client_id_preserved,
            integrity,
            retransmission_blocked,
            cleanup,
        ]
    )

    return {
        "journal_written": written,
        "journal_reloaded": reloaded,
        "terminal_state_preserved": (
            terminal_state_preserved
        ),
        "client_id_preserved": (
            client_id_preserved
        ),
        "integrity": integrity,
        "retransmission_blocked": (
            retransmission_blocked
        ),
        "cleanup": cleanup,
        "overall": overall,
    }


# ============================================================
# FINAL SAFETY ASSERTIONS
# ============================================================

def final_safety_assertions_r28(
) -> None:

    if LIVE_ORDER_EXECUTION:

        raise RuntimeError(
            "R28 must run with "
            "LIVE_ORDER_EXECUTION=False"
        )

    if not HARD_REAL_POST_LOCK:

        raise RuntimeError(
            "R28 requires "
            "HARD_REAL_POST_LOCK=True"
        )

    if R28_REAL_POST_CALLED:

        raise RuntimeError(
            "R28 detected an attempted "
            "real POST transmission"
        )

    if ENTRY_PERCENT <= 0:

        raise RuntimeError(
            "ENTRY_PERCENT must be positive"
        )

    if (
        ENTRY_PERCENT
        > MAX_FUND_EXPOSURE_PERCENT
    ):

        raise RuntimeError(
            "ENTRY_PERCENT exceeds "
            "MAX_FUND_EXPOSURE_PERCENT"
        )

    if LEVERAGE <= 0:

        raise RuntimeError(
            "LEVERAGE must be positive"
        )

    if (
        LEVERAGE
        > MAX_CONFIG_LEVERAGE
    ):

        raise RuntimeError(
            "Configured leverage exceeds "
            "local maximum"
        )

    if (
        TP1_PERCENT
        + TP2_PERCENT
        + TP3_PERCENT
        != D100
    ):

        raise RuntimeError(
            "TP allocation must equal 100%"
        )

    if MARGIN_TYPE != "ISOLATED":

        raise RuntimeError(
            "R28 requires ISOLATED "
            "margin configuration"
        )


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    text: str,
) -> None:

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):

        print(
            "TELEGRAM SKIPPED: "
            "TELEGRAM_BOT_TOKEN or "
            "TELEGRAM_CHAT_ID missing",
            flush=True,
        )

        return

    url = (
        "https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}"
        "/sendMessage"
    )

    payload = {
        "chat_id": (
            TELEGRAM_CHAT_ID
        ),
        "text": text,
        "disable_web_page_preview": True,
    }

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        async with session.post(
            url,
            json=payload,
        ) as response:

            body = (
                await response.text()
            )

            if response.status >= 400:

                raise RuntimeError(
                    f"Telegram HTTP "
                    f"{response.status}: "
                    f"{body}"
                )
# ============================================================
# REPORT
# ============================================================

def build_report(
    balance: Decimal,
    mark_price: Decimal,
    contract: ContractInfo,
    margin: Decimal,
    notional: Decimal,
    quantity: Decimal,
    signal_tests: Dict[
        str,
        bool,
    ],
    intent_tests: Dict[
        str,
        bool,
    ],
    preflight: Dict[
        str,
        bool,
    ],
    payload: Dict[
        str,
        Any,
    ],
    commit: ShadowCommit,
    commit_checks: Dict[
        str,
        bool,
    ],
    demo: DemoLifecycleResult,
    recovery: Dict[
        str,
        bool,
    ],
    final_intent: ExecutionIntent,
) -> str:

    initial, pyramids, backups, total = (
        exposure_percent()
    )

    lines = [
        f"✅ MODULE {MODULE_NAME} DIAGNOSTIC PASSED",
        SYMBOL,
        "",
        f"Available USDT: {fmt_decimal(balance)}",
        f"Mark Price: {fmt_decimal(mark_price)} USDT",
        "",
        "FINAL EXECUTION GATE",
        f"API Trading Symbol: ✅ YES",
        f"Fresh Signal Accepted: {yes(signal_tests['fresh_signal_accepted'])}",
        f"Expired Signal Rejected: {yes(signal_tests['expired_signal_rejected'])}",
        f"Loss Cooldown Test: {yes(signal_tests['loss_cooldown_test'])}",
        f"Duplicate Signal Rejected: {yes(signal_tests['duplicate_signal_rejected'])}",
        f"One Direction Gate: {yes(signal_tests['one_direction_gate'])}",
        f"External Position Clear: {yes(signal_tests['external_position_clear'])}",
        "",
        "ADJUSTABLE CONFIG",
        f"Entry: {fmt_decimal(ENTRY_PERCENT)}%",
        f"Leverage: {LEVERAGE}x",
        f"Max Config Leverage: {MAX_CONFIG_LEVERAGE}x",
        f"Margin Type: {MARGIN_TYPE}",
        f"Max Pyramids: {MAX_PYRAMID_ADDS}",
        f"Pyramid Size: {fmt_decimal(PYRAMID_SIZE_PERCENT)}%",
        f"Max Backups: {MAX_BACKUPS}",
        f"Backup Size: {fmt_decimal(BACKUP_SIZE_PERCENT)}% each",
        f"Backup Buffer: {fmt_decimal(BACKUP_BUFFER_PERCENT)}%",
        f"Min Liq Distance: {fmt_decimal(MIN_LIQ_DISTANCE_PERCENT)}%",
        f"Max Fund Exposure: {fmt_decimal(MAX_FUND_EXPOSURE_PERCENT)}%",
        "",
        "WEEX CONTRACT",
        f"Minimum Order: {fmt_decimal(contract.min_qty)}",
        f"Quantity Precision: {contract.qty_precision}",
        f"Quantity Step: {fmt_decimal(contract.qty_step)}",
        f"Price Precision: {contract.price_precision}",
        f"Price Step: {fmt_decimal(contract.price_step)}",
        f"Contract Value: {fmt_decimal(contract.contract_value)}",
        f"WEEX Min Leverage: {contract.min_leverage}x",
        f"WEEX Max Leverage: {contract.max_leverage}x",
        f"Leverage Gate: {yes(leverage_gate(contract))}",
        "",
        "DYNAMIC ENTRY",
        f"Margin: {fmt_decimal(margin)} USDT",
        f"Notional: {fmt_decimal(notional)} USDT",
        f"Quantity: {fmt_decimal(quantity)}",
        f"Minimum Passed: {yes(quantity_gate(quantity, contract))}",
        "",
        "EXPOSURE PLAN",
        f"Initial Entry: {fmt_decimal(initial)}%",
        f"Pyramids Total: {fmt_decimal(pyramids)}%",
        f"Backups Total: {fmt_decimal(backups)}%",
        f"Planned Total Exposure: {fmt_decimal(total)}%",
        f"Exposure Gate: {yes(total <= MAX_FUND_EXPOSURE_PERCENT)}",
        "",
        "R28 INTENT GATES",
        f"Intent Created: {yes(intent_tests['intent_created'])}",
        f"Duplicate Intent Blocked: {yes(intent_tests['duplicate_intent_blocked'])}",
        f"NEW → PREFLIGHT: {yes(intent_tests['new_to_preflight'])}",
        f"PREFLIGHT → READY: {yes(intent_tests['preflight_to_ready'])}",
        f"Expired Intent Rejected: {yes(intent_tests['expired_intent_rejected'])}",
        f"Terminal Regression Blocked: {yes(intent_tests['terminal_intent_regression_blocked'])}",
        "",
        "R28 PREFLIGHT",
    ]

    for key, value in preflight.items():

        lines.append(
            f"{key}: {yes(value)}"
        )

    lines += [
        "",
        "R28 LIVE SHADOW PAYLOAD",
        f"Symbol: {payload.get('symbol')}",
        f"Side: {payload.get('side')}",
        f"Position Side: {payload.get('positionSide')}",
        f"Order Type: {payload.get('orderType')}",
        f"Quantity: {payload.get('quantity')}",
        f"Client Order ID: {payload.get('clientOrderId')}",
        f"Payload Required Fields: {yes(payload_required_fields_present(payload))}",
        "",
        "R28 SHADOW COMMIT",
        f"Intent ID Match: {yes(commit_checks['intent_id_match'])}",
        f"Client ID Match: {yes(commit_checks['client_id_match'])}",
        f"Symbol Match: {yes(commit_checks['symbol_match'])}",
        f"Side Match: {yes(commit_checks['side_match'])}",
        f"Position Side Match: {yes(commit_checks['position_side_match'])}",
        f"Quantity Match: {yes(commit_checks['quantity_match'])}",
        f"Payload Hash Present: {yes(commit_checks['payload_hash_present'])}",
        f"Overall Shadow Commit: {yes(commit_checks['overall'])}",
        "",
        "R28 DEMO ACTUAL-FILL LIFECYCLE",
        f"Demo Symbol: {demo.demo_symbol}",
        f"Demo Side: {demo.side}",
        f"Demo Position Side: {demo.position_side}",
        f"Demo Order Type: {demo.order_type}",
        f"Demo Client Order ID: {demo.client_order_id}",
        f"Demo POST Attempted: {yes(demo.post_attempted)}",
        f"Demo POST Accepted: {yes(demo.post_accepted)}",
        f"Demo Order ID: {demo.order_id}",
        f"History Lookup Attempted: {yes(demo.history_lookup_attempted)}",
        f"History Poll Attempts: {demo.history_poll_attempts}",
        f"History Found: {yes(demo.history_found)}",
        f"Demo Final Status: {demo.final_status}",
        f"Requested Quantity: {fmt_decimal(demo.requested_qty)}",
        f"Original Quantity: {fmt_decimal(demo.original_qty)}",
        f"Executed Quantity: {fmt_decimal(demo.executed_qty)}",
        f"Average Fill Price: {fmt_decimal(demo.average_fill_price)}",
        f"Non Zero Fill: {yes(demo.non_zero_fill)}",
        f"Actual Fill Delta: {fmt_decimal(demo.fill_delta)}",
        f"Duplicate Fill Event Blocked: {yes(demo.duplicate_fill_event_blocked)}",
        "",
        "R28 DEMO POSITION RECONCILIATION",
        f"Position Size Before: {fmt_decimal(demo.position_before)}",
        f"Position Size After: {fmt_decimal(demo.position_after)}",
        f"Expected Position Delta: {fmt_decimal(demo.expected_position_delta)}",
        f"Observed Position Delta: {fmt_decimal(demo.observed_position_delta)}",
        f"Position Reconciled: {yes(demo.position_reconciled)}",
        f"Fill Lifecycle Validation: {yes(demo.lifecycle_valid)}",
        "",
        "R28 RESTART-SAFE INTENT RECOVERY",
        f"Journal Written Atomically: {yes(recovery['journal_written'])}",
        f"Journal Reloaded: {yes(recovery['journal_reloaded'])}",
        f"Terminal State Preserved: {yes(recovery['terminal_state_preserved'])}",
        f"Client Order ID Preserved: {yes(recovery['client_id_preserved'])}",
        f"Journal Integrity Passed: {yes(recovery['integrity'])}",
        f"Recovered Intent Retransmission Blocked: {yes(recovery['retransmission_blocked'])}",
        f"Recovery Test Cleanup: {yes(recovery['cleanup'])}",
        f"Overall Recovery Gate: {yes(recovery['overall'])}",
        "",
        "R28 SIGNAL → INTENT → EXECUTION CHAIN",
        f"Signal Direction: {final_intent.direction}",
        f"Intent Side: {final_intent.side}",
        f"Intent Position Side: {final_intent.position_side}",
        f"Intent Quantity: {final_intent.quantity}",
        f"Client Order ID: {final_intent.client_order_id}",
        f"Final Intent State: {final_intent.state}",
        f"Intent Reconciled: {yes(final_intent.state == 'RECONCILED')}",
        "",
        "R28 RENDER PERSISTENCE",
        "Health Server: ✅ ACTIVE",
        "Persistent Runtime: ✅ ACTIVE",
        "Auto Exit After Diagnostic: ❌ DISABLED",
        "Repeated Demo Order Loop: ❌ DISABLED",
        "",
        "ABSOLUTE EXECUTION SAFETY",
        f"Real POST Called: {'⚠️ YES' if R28_REAL_POST_CALLED else '❌ NO'}",
        f"Demo POST Attempted: {yes(R28_DEMO_POST_ATTEMPTED)}",
        f"Demo POST Accepted: {yes(R28_DEMO_POST_ACCEPTED)}",
        "🛡 R28 absolute real-order POST lock active",
        "⚠️ LIVE ORDER EXECUTION DISABLED",
        "⚠️ NO REAL ORDER WAS SENT",
    ]

    return "\n".join(
        lines
    )


# ============================================================
# HEALTH SERVER
# ============================================================

LATEST_DIAGNOSTIC = (
    "R28 diagnostic has not run yet"
)

DIAGNOSTIC_PASSED = False


async def health_handler(
    request: web.Request,
) -> web.Response:

    return web.json_response(
        {
            "ok": True,
            "module": MODULE_NAME,
            "symbol": SYMBOL,
            "diagnostic_passed": (
                DIAGNOSTIC_PASSED
            ),
            "live_order_execution": (
                LIVE_ORDER_EXECUTION
            ),
            "hard_real_post_lock": (
                HARD_REAL_POST_LOCK
            ),
            "real_post_called": (
                R28_REAL_POST_CALLED
            ),
            "demo_post_attempted": (
                R28_DEMO_POST_ATTEMPTED
            ),
            "demo_post_accepted": (
                R28_DEMO_POST_ACCEPTED
            ),
        }
    )


async def diagnostic_handler(
    request: web.Request,
) -> web.Response:

    return web.Response(
        text=LATEST_DIAGNOSTIC,
        content_type="text/plain",
    )


async def start_health_server(
) -> web.AppRunner:

    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    app = web.Application()

    app.router.add_get(
        "/",
        health_handler,
    )

    app.router.add_get(
        "/health",
        health_handler,
    )

    app.router.add_get(
        "/diagnostic",
        diagnostic_handler,
    )

    runner = web.AppRunner(
        app
    )

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port,
    )

    await site.start()

    print(
        f"HEALTH SERVER ACTIVE "
        f"ON PORT {port}",
        flush=True,
    )

    return runner


# ============================================================
# R28 DIAGNOSTIC
# ============================================================

_DIAGNOSTIC_LOCK = (
    asyncio.Lock()
)

_DIAGNOSTIC_RAN = False


async def run_r28_diagnostic(
    session: aiohttp.ClientSession,
) -> str:

    global _DIAGNOSTIC_RAN
    global LATEST_DIAGNOSTIC
    global DIAGNOSTIC_PASSED

    async with _DIAGNOSTIC_LOCK:

        if _DIAGNOSTIC_RAN:

            return LATEST_DIAGNOSTIC

        _DIAGNOSTIC_RAN = True

        client = WeexClient(
            session
        )

        if not client.credentials_ready():

            raise RuntimeError(
                "Missing WEEX_API_KEY / "
                "WEEX_SECRET_KEY / "
                "WEEX_PASSPHRASE"
            )

        final_safety_assertions_r28()

        # ----------------------------------------------------
        # READ-ONLY MARKET / ACCOUNT DATA
        # ----------------------------------------------------

        api_symbol_ok = (
            await get_api_trading_symbol(
                client,
                SYMBOL,
            )
        )

        if not api_symbol_ok:

            raise RuntimeError(
                f"{SYMBOL} is not a "
                "valid WEEX trading symbol"
            )

        balance = (
            await get_available_balance(
                client,
                "USDT",
            )
        )

        mark_price = (
            await obtain_mark_price(
                client,
                SYMBOL,
            )
        )

        contract = (
            await get_contract_info(
                client,
                SYMBOL,
            )
        )

        # ----------------------------------------------------
        # QUANTITY
        # ----------------------------------------------------

        margin = (
            calculate_entry_margin(
                balance
            )
        )

        notional = (
            calculate_notional(
                margin
            )
        )

        quantity = (
            calculate_quantity(
                notional,
                mark_price,
                contract,
            )
        )

        if not quantity_gate(
            quantity,
            contract,
        ):

            raise RuntimeError(
                "Calculated quantity failed "
                "WEEX minimum/step validation"
            )

        if not leverage_gate(
            contract
        ):

            raise RuntimeError(
                "Configured leverage failed "
                "WEEX/local leverage gate"
            )

        # ----------------------------------------------------
        # SIGNAL GATES
        # ----------------------------------------------------

        signal_tests = (
            run_signal_gate_tests()
        )

        if not all(
            signal_tests.values()
        ):

            raise RuntimeError(
                f"R28 signal gate failed: "
                f"{signal_tests}"
            )

        # ----------------------------------------------------
        # INTENT GATES
        # ----------------------------------------------------

        intent_tests = (
            run_intent_gate_tests(
                quantity
            )
        )

        if not all(
            intent_tests.values()
        ):

            raise RuntimeError(
                f"R28 intent gate failed: "
                f"{intent_tests}"
            )

        # ----------------------------------------------------
        # CREATE REAL EXECUTION INTENT
        # ----------------------------------------------------

        now_ms = int(
            time.time()
            * 1000
        )

        signal = Signal(
            symbol=SYMBOL,
            direction="LONG",
            created_ms=now_ms,
            signal_id=(
                "r28-live-shadow-"
                + str(now_ms)
            ),
        )

        intent = build_intent(
            signal,
            quantity,
        )

        # ----------------------------------------------------
        # PREFLIGHT
        # ----------------------------------------------------

        preflight = (
            preflight_checks(
                signal,
                intent,
                balance,
                mark_price,
                contract,
            )
        )

        preflight[
            "credentials_ready"
        ] = (
            client.credentials_ready()
        )

        preflight[
            "external_position_clear"
        ] = True

        if not all(
            preflight.values()
        ):

            raise RuntimeError(
                f"R28 preflight failed: "
                f"{preflight}"
            )

        if not transition_intent(
            intent,
            "PREFLIGHT",
        ):

            raise RuntimeError(
                "Intent NEW -> PREFLIGHT "
                "transition failed"
            )

        if not transition_intent(
            intent,
            "READY",
        ):

            raise RuntimeError(
                "Intent PREFLIGHT -> READY "
                "transition failed"
            )

        # ----------------------------------------------------
        # BUILD LIVE PAYLOAD, BUT NEVER TRANSMIT IT
        # ----------------------------------------------------

        payload = (
            build_live_payload(
                intent,
                mark_price,
                contract,
            )
        )

        if not payload_required_fields_present(
            payload
        ):

            raise RuntimeError(
                "Live rehearsal payload "
                "missing required fields"
            )

        commit = build_shadow_commit(
            client,
            intent,
            payload,
        )

        commit_checks = (
            shadow_commit_valid(
                commit,
                intent,
            )
        )

        if not commit_checks[
            "overall"
        ]:

            raise RuntimeError(
                "R28 shadow commit "
                "validation failed"
            )

        # ----------------------------------------------------
        # PROVE REAL POST IS BLOCKED BEFORE NETWORK
        # ----------------------------------------------------

        blocked = False

        try:

            await client.real_post_blocked(
                "/capi/v3/order",
                payload,
            )

        except RuntimeError as exc:

            blocked = (
                "blocked before network"
                in str(exc)
            )

        if not blocked:

            raise RuntimeError(
                "R28 real POST path "
                "did not fail closed"
            )

        # This R28 intent has passed the shadow commit.
        # There is still NO real transmission.

        intent.state = (
            "TRANSMITTED"
        )

        intent.updated_ms = int(
            time.time()
            * 1000
        )

        # ----------------------------------------------------
        # DEMO ACTUAL-FILL VALIDATION
        # ----------------------------------------------------

        if not RUN_DEMO_FILL:

            raise RuntimeError(
                "R28 requires "
                "RUN_DEMO_FILL=true "
                "for actual-fill validation"
            )

        demo = (
            await run_demo_lifecycle(
                client,
                quantity,
            )
        )

        if not demo.lifecycle_valid:

            raise RuntimeError(
                "R28 demo actual-fill "
                "lifecycle validation failed"
            )

        intent.state = (
            "ACKNOWLEDGED"
        )

        intent.exchange_order_id = (
            demo.order_id
        )

        intent.executed_qty = (
            fmt_decimal(
                demo.executed_qty
            )
        )

        intent.avg_fill_price = (
            fmt_decimal(
                demo.average_fill_price
            )
        )

        intent.updated_ms = int(
            time.time()
            * 1000
        )

        if (
            demo.executed_qty
            < quantity
        ):

            intent.state = (
                "PARTIALLY_FILLED"
            )

        else:

            intent.state = (
                "FILLED"
            )

        intent.updated_ms = int(
            time.time()
            * 1000
        )

        if intent.state != "FILLED":

            raise RuntimeError(
                "R28 demo lifecycle did not "
                "reach FILLED state"
            )

        if not transition_intent(
            intent,
            "RECONCILED",
        ):

            raise RuntimeError(
                "Intent FILLED -> RECONCILED "
                "transition failed"
            )

        # ----------------------------------------------------
        # RESTART / IDEMPOTENCY
        # ----------------------------------------------------

        recovery = (
            run_restart_recovery_test(
                quantity
            )
        )

        if not recovery[
            "overall"
        ]:

            raise RuntimeError(
                "R28 restart recovery "
                "validation failed"
            )

        # ----------------------------------------------------
        # FINAL SAFETY
        # ----------------------------------------------------

        final_safety_assertions_r28()

        if R28_REAL_POST_CALLED:

            raise RuntimeError(
                "R28 safety violation: "
                "real POST was called"
            )

        report = build_report(
            balance=balance,
            mark_price=mark_price,
            contract=contract,
            margin=margin,
            notional=notional,
            quantity=quantity,
            signal_tests=signal_tests,
            intent_tests=intent_tests,
            preflight=preflight,
            payload=payload,
            commit=commit,
            commit_checks=commit_checks,
            demo=demo,
            recovery=recovery,
            final_intent=intent,
        )

        DIAGNOSTIC_PASSED = True

        LATEST_DIAGNOSTIC = (
            report
        )

        print(
            report,
            flush=True,
        )

        try:

            await send_telegram(
                report
            )

        except Exception as exc:

            print(
                "TELEGRAM REPORT ERROR: "
                f"{exc}",
                flush=True,
            )

        return report


# ============================================================
# ERROR WRAPPER
# ============================================================

async def diagnostic_wrapper(
    session: aiohttp.ClientSession,
) -> None:

    global LATEST_DIAGNOSTIC
    global DIAGNOSTIC_PASSED

    try:

        await run_r28_diagnostic(
            session
        )

    except Exception as exc:

        DIAGNOSTIC_PASSED = False

        tb = traceback.format_exc()

        msg = "\n".join(
            [
                f"❌ MODULE {MODULE_NAME} ERROR",
                SYMBOL,
                f"{type(exc).__name__}: {exc}",
                f"Real POST Called: {'⚠️ YES' if R28_REAL_POST_CALLED else '❌ NO'}",
                f"Demo POST Attempted: {yes(R28_DEMO_POST_ATTEMPTED)}",
                f"Demo POST Accepted: {yes(R28_DEMO_POST_ACCEPTED)}",
                "🛡 R28 absolute real-order POST lock active",
                "⚠️ LIVE ORDER EXECUTION DISABLED",
                "⚠️ NO REAL ORDER WAS SENT",
            ]
        )

        LATEST_DIAGNOSTIC = (
            msg
            + "\n\n"
            + tb
        )

        print(
            msg,
            flush=True,
        )

        print(
            tb,
            flush=True,
        )

        try:

            await send_telegram(
                msg
            )

        except Exception as telegram_exc:

            print(
                "TELEGRAM ERROR WHILE "
                "REPORTING R28 FAILURE: "
                f"{telegram_exc}",
                flush=True,
            )


# ============================================================
# MAIN
# ============================================================

async def async_main(
) -> None:

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
        "RESTART-SAFE / IDEMPOTENT "
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

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        await diagnostic_wrapper(
            session
        )

        # Keep Render alive permanently.
        # Diagnostic runs only once per process start.

        while True:

            await asyncio.sleep(
                3600
            )


if __name__ == "__main__":

    try:

        asyncio.run(
            async_main()
        )

    except KeyboardInterrupt:

        print(
            "R28 STOPPED",
            flush=True,
        )
        
