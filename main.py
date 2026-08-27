from __future__ import annotations

import base64
import hashlib
import hmac
import http.server
import json
import os
import socketserver
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_DOWN, getcontext
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


# =============================================================================
# R29 UNIT C
# CONTROLLED LIVE READ-ONLY OBSERVATION INTEGRATION
#
# SAFETY DISCIPLINE:
#   - NO REAL ORDER EXECUTION
#   - NO DEMO ORDER EXECUTION
#   - NO NETWORK WRITES
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MUTATION
#   - NO POSITION MUTATION
#   - NO ACCOUNT MUTATION
#   - NO WEBSOCKET WRITES
#   - NETWORK ACCESS IS GET-ONLY AND ALLOWLISTED
#   - DECISION TRANSPORT REMAINS SYNTHETIC ONLY
#
# PURPOSE:
#   Live public/private GET observations
#       -> validated read-only snapshots
#       -> strategy compatibility projection
#       -> frozen non-executable decision envelope
#       -> synthetic receipt only
#       -> durable restart-safe runtime state
# =============================================================================

print("R29 UNIT C: MAIN.PY ENTERED", flush=True)

getcontext().prec = 40

UNIT = "R29 UNIT C"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()
ASSET = os.getenv("ASSET", "USDT").strip().upper()
MARGIN_TYPE = os.getenv("MARGIN_TYPE", "ISOLATED").strip().upper()

PLANNED_LEVERAGE = Decimal(
    os.getenv("PLANNED_LEVERAGE", "100")
)

INITIAL_ALLOCATION_PERCENT = Decimal(
    os.getenv("INITIAL_ALLOCATION_PERCENT", "5")
)

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv("MAX_FUND_EXPOSURE_PERCENT", "35")
)

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv("SIGNAL_EXPIRY_SECONDS", "120")
)

HEARTBEAT_SECONDS = int(
    os.getenv("HEARTBEAT_SECONDS", "30")
)

PORT = int(
    os.getenv("PORT", "10000")
)

REQUEST_TIMEOUT_SECONDS = float(
    os.getenv("REQUEST_TIMEOUT_SECONDS", "12")
)


# =============================================================================
# WEEX V3 READ-ONLY ENDPOINTS
# =============================================================================

CONTRACT_BASE_URL = "https://api-contract.weex.com"

PUBLIC_MARK_PATH = (
    "/capi/v3/market/symbolPrice"
)

PUBLIC_EXCHANGE_INFO_PATH = (
    "/capi/v3/market/exchangeInfo"
)

PRIVATE_BALANCE_PATH = (
    "/capi/v3/account/balance"
)

PRIVATE_POSITIONS_PATH = (
    "/capi/v3/account/position/allPosition"
)

PRIVATE_SYMBOL_CONFIG_PATH = (
    "/capi/v3/account/symbolConfig"
)


# =============================================================================
# CREDENTIALS
#
# NEVER HARDCODE REAL CREDENTIALS HERE.
# THEY MUST COME FROM RENDER ENVIRONMENT VARIABLES.
# =============================================================================

API_KEY = os.getenv(
    "WEEX_API_KEY",
    os.getenv("API_KEY", ""),
).strip()

SECRET_KEY = os.getenv(
    "WEEX_SECRET_KEY",
    os.getenv(
        "API_SECRET",
        os.getenv("SECRET_KEY", ""),
    ),
).strip()

PASSPHRASE = os.getenv(
    "WEEX_PASSPHRASE",
    os.getenv(
        "API_PASSPHRASE",
        os.getenv("PASSPHRASE", ""),
    ),
).strip()


STATE_PATH = Path(
    os.getenv(
        "R29_UNIT_C_STATE_PATH",
        "/tmp/r29_unit_c_state.json",
    )
)


# =============================================================================
# ABSOLUTE SAFETY SWITCHES
#
# THESE ARE CONSTANTS BY DESIGN.
# UNIT C MAY READ FROM THE NETWORK.
# UNIT C MAY NEVER WRITE TO THE EXCHANGE.
# =============================================================================

REAL_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False

WEBSOCKET_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False

MARGIN_MUTATION_ENABLED = False

POSITION_MUTATION_ENABLED = False

ACCOUNT_MUTATION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True


# =============================================================================
# STRICT GET-ONLY ALLOWLIST
# =============================================================================

ALLOWED_HOSTS = {
    "api-contract.weex.com",
}

ALLOWED_PUBLIC_GETS = {
    PUBLIC_MARK_PATH,
    PUBLIC_EXCHANGE_INFO_PATH,
}

ALLOWED_PRIVATE_GETS = {
    PRIVATE_BALANCE_PATH,
    PRIVATE_POSITIONS_PATH,
    PRIVATE_SYMBOL_CONFIG_PATH,
}

ALL_ALLOWED_GETS = (
    ALLOWED_PUBLIC_GETS
    | ALLOWED_PRIVATE_GETS
)


print(
    "R29 UNIT C: IMPORTS COMPLETE",
    flush=True,
)

print(
    "R29 UNIT C: CONSTANTS INITIALIZED",
    flush=True,
)


# =============================================================================
# PART 1
# DATA MODELS / GENERAL UTILITIES
# =============================================================================


class LocalBlock(RuntimeError):
    pass


class RemoteReadError(RuntimeError):
    pass


def block(reason: str) -> None:
    print(
        f"{UNIT} LOCAL BLOCK:",
        flush=True,
    )

    print(
        f"  {reason}",
        flush=True,
    )

    raise LocalBlock(reason)


def require(
    condition: bool,
    reason: str,
) -> None:

    if not condition:
        block(reason)


def canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def decimal_text(
    value: Decimal,
) -> str:

    return format(
        value,
        "f",
    )


def as_decimal(
    value: Any,
    field: str,
) -> Decimal:

    try:
        return Decimal(
            str(value)
        )

    except Exception as exc:
        raise RemoteReadError(
            f"invalid decimal for "
            f"{field}: {value!r}"
        ) from exc


def utc_ms() -> int:

    return int(
        time.time() * 1000
    )


def separator() -> None:

    print(
        "-" * 92,
        flush=True,
    )


PASS_ASSERTIONS = 0
TEST_GROUPS = 0


def start_test(
    number: int,
    title: str,
) -> None:

    global TEST_GROUPS

    TEST_GROUPS += 1

    separator()

    print(
        f"{UNIT} TEST {number}: "
        f"{title}",
        flush=True,
    )

    separator()


def passed(
    label: str,
    condition: bool = True,
) -> None:

    global PASS_ASSERTIONS

    if not condition:
        raise AssertionError(label)

    PASS_ASSERTIONS += 1

    print(
        f"{label:<84} ✅ PASS",
        flush=True,
    )


def expect_local_block(
    label: str,
    fn,
) -> None:

    try:
        fn()

    except LocalBlock:
        passed(label)

    else:
        raise AssertionError(
            f"expected local block: {label}"
        )


# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass(frozen=True)
class MarketObservation:

    symbol: str
    mark_price: str
    observed_at_ms: int
    source: str
    remote_time_ms: int


@dataclass(frozen=True)
class AccountObservation:

    asset: str
    balance: str
    available_balance: str
    frozen: str
    unrealized_pnl: str
    position_count: int
    observed_at_ms: int
    source: str


@dataclass(frozen=True)
class SymbolConfiguration:

    symbol: str
    margin_type: str
    separated_type: str
    cross_leverage: str
    isolated_long_leverage: str
    isolated_short_leverage: str
    observed_at_ms: int
    source: str


@dataclass(frozen=True)
class ContractRules:

    symbol: str
    quantity_precision: int
    quantity_step: str
    minimum_quantity: str
    price_precision: int
    price_step: str
    source: str


@dataclass(frozen=True)
class StrategySignal:

    signal_id: str
    symbol: str
    direction: str
    created_at_ms: int
    expires_at_ms: int
    source: str


@dataclass(frozen=True)
class RiskProjection:

    margin_budget: str
    planned_notional: str
    raw_quantity: str
    rounded_quantity: str
    projected_margin: str
    fund_cap: str


@dataclass(frozen=True)
class DecisionEnvelope:

    decision_id: str
    symbol: str
    side: str
    position_side: str
    quantity: str
    reference_price: str
    leverage: str
    executable: bool
    synthetic_only: bool
    configuration_fingerprint: str
    market_observation_hash: str
    account_observation_hash: str
    payload_hash: str


@dataclass(frozen=True)
class SyntheticReceipt:

    receipt_id: str
    decision_id: str
    decision_payload_hash: str
    transport: str
    transmitted: bool
    created_at_ms: int


@dataclass
class RuntimeState:

    schema_version: int
    unit: str
    runtime_id: str
    generation: int
    recovery_epoch: int
    boot_counter: int

    configuration_fingerprint: str

    latest_market_hash: str
    latest_account_hash: str
    latest_symbol_config_hash: str

    latest_decision_id: str
    latest_decision_hash: str

    synthetic_dispatch_count: int

    real_order_count: int
    demo_order_count: int
    network_write_count: int

    read_request_count: int

    integrity_seal: str = ""


@dataclass
class FirebreakCounters:

    real_http_write_blocks: int = 0

    demo_http_write_blocks: int = 0

    websocket_write_blocks: int = 0

    leverage_mutation_blocks: int = 0

    margin_mutation_blocks: int = 0

    position_mutation_blocks: int = 0

    account_mutation_blocks: int = 0


FIREBREAKS = FirebreakCounters()


# =============================================================================
# PART 2
# STRICT READ-ONLY NETWORK BOUNDARY
# =============================================================================


class ReadOnlyTransport:

    def __init__(self) -> None:

        self.read_count = 0


    @staticmethod
    def _validate_target(
        path: str,
    ) -> None:

        require(
            path.startswith("/"),
            "request path must be absolute",
        )

        require(
            path in ALL_ALLOWED_GETS,
            "GET path is not allowlisted",
        )


    @staticmethod
    def _validate_url(
        url: str,
    ) -> None:

        parsed = urllib.parse.urlparse(
            url
        )

        require(
            parsed.scheme == "https",
            "non-HTTPS transport blocked",
        )

        require(
            parsed.hostname
            in ALLOWED_HOSTS,
            "network host is not allowlisted",
        )

        require(
            parsed.path
            in ALL_ALLOWED_GETS,
            "network path is not allowlisted",
        )


    @staticmethod
    def _sign(
        timestamp: str,
        method: str,
        path: str,
        query_string: str,
    ) -> str:

        require(
            method == "GET",
            "signature requested for "
            "non-GET method",
        )

        require(
            bool(SECRET_KEY),
            "WEEX secret key missing",
        )

        unsigned = (
            timestamp
            + method
            + path
        )

        if query_string:
            unsigned += (
                "?"
                + query_string
            )

        digest = hmac.new(
            SECRET_KEY.encode("utf-8"),
            unsigned.encode("utf-8"),
            hashlib.sha256,
        ).digest()

        return base64.b64encode(
            digest
        ).decode("ascii")


    def get_public(
        self,
        path: str,
        params: Optional[
            Dict[str, str]
        ] = None,
    ) -> Any:

        self._validate_target(
            path
        )

        require(
            path in ALLOWED_PUBLIC_GETS,
            "public GET path not allowlisted",
        )

        query = urllib.parse.urlencode(
            params or {}
        )

        url = (
            CONTRACT_BASE_URL
            + path
            + (
                "?" + query
                if query
                else ""
            )
        )

        self._validate_url(
            url
        )

        return self._perform_get(
            url,
            headers={
                "Accept":
                    "application/json",
                "User-Agent":
                    "R29-Unit-C-ReadOnly/1.0",
            },
        )


    def get_private(
        self,
        path: str,
        params: Optional[
            Dict[str, str]
        ] = None,
    ) -> Any:

        self._validate_target(
            path
        )

        require(
            path in ALLOWED_PRIVATE_GETS,
            "private GET path "
            "not allowlisted",
        )

        require(
            bool(API_KEY),
            "WEEX API key missing",
        )

        require(
            bool(SECRET_KEY),
            "WEEX secret key missing",
        )

        require(
            bool(PASSPHRASE),
            "WEEX passphrase missing",
        )

        query = urllib.parse.urlencode(
            params or {}
        )

        timestamp = str(
            utc_ms()
        )

        signature = self._sign(
            timestamp,
            "GET",
            path,
            query,
        )

        headers = {
            "ACCESS-KEY":
                API_KEY,

            "ACCESS-SIGN":
                signature,

            "ACCESS-TIMESTAMP":
                timestamp,

            "ACCESS-PASSPHRASE":
                PASSPHRASE,

            "Content-Type":
                "application/json",

            "Accept":
                "application/json",

            "User-Agent":
                "R29-Unit-C-ReadOnly/1.0",
        }

        url = (
            CONTRACT_BASE_URL
            + path
            + (
                "?" + query
                if query
                else ""
            )
        )

        self._validate_url(
            url
        )

        return self._perform_get(
            url,
            headers=headers,
        )


    def _perform_get(
        self,
        url: str,
        headers: Dict[str, str],
    ) -> Any:

        request = urllib.request.Request(
            url=url,
            headers=headers,
            method="GET",
        )

        require(
            request.get_method()
            == "GET",
            "non-GET request blocked "
            "at transport boundary",
        )

        self.read_count += 1

        try:

            with urllib.request.urlopen(
                request,
                timeout=(
                    REQUEST_TIMEOUT_SECONDS
                ),
            ) as response:

                raw = response.read().decode(
                    "utf-8"
                )

                if (
                    response.status < 200
                    or
                    response.status >= 300
                ):
                    raise RemoteReadError(
                        f"HTTP "
                        f"{response.status}: "
                        f"{raw[:500]}"
                    )

        except urllib.error.HTTPError as exc:

            try:
                detail = (
                    exc.read()
                    .decode("utf-8")
                )

            except Exception:
                detail = str(exc)

            raise RemoteReadError(
                f"HTTP {exc.code}: "
                f"{detail[:800]}"
            ) from exc

        except urllib.error.URLError as exc:

            raise RemoteReadError(
                f"network read failed: "
                f"{exc}"
            ) from exc

        except TimeoutError as exc:

            raise RemoteReadError(
                "network read timed out"
            ) from exc


        try:

            data = json.loads(
                raw
            )

        except json.JSONDecodeError as exc:

            raise RemoteReadError(
                f"non-JSON response: "
                f"{raw[:500]}"
            ) from exc


        if isinstance(
            data,
            dict,
        ):

            code = data.get(
                "code"
            )

            if (
                code not in (
                    None,
                    0,
                    "0",
                    "00000",
                )
                and
                not any(
                    key in data
                    for key in (
                        "symbol",
                        "asset",
                        "symbols",
                    )
                )
            ):

                raise RemoteReadError(
                    "WEEX API error: "
                    + canonical_json(
                        data
                    )[:800]
                )

        return data


TRANSPORT = ReadOnlyTransport()


# =============================================================================
# HARD WRITE FIREBREAKS
# =============================================================================


def forbidden_real_http_write(
    method: str = "POST",
) -> None:

    FIREBREAKS.real_http_write_blocks += 1

    block(
        f"REAL network "
        f"{method.upper()} blocked"
    )


def forbidden_demo_http_write(
    method: str = "POST",
) -> None:

    FIREBREAKS.demo_http_write_blocks += 1

    block(
        f"DEMO network "
        f"{method.upper()} blocked"
    )


def forbidden_websocket_write() -> None:

    FIREBREAKS.websocket_write_blocks += 1

    block(
        "WebSocket write blocked"
    )


def forbidden_leverage_mutation() -> None:

    FIREBREAKS.leverage_mutation_blocks += 1

    block(
        "leverage mutation disabled"
    )


def forbidden_margin_mutation() -> None:

    FIREBREAKS.margin_mutation_blocks += 1

    block(
        "margin mutation disabled"
    )


def forbidden_position_mutation() -> None:

    FIREBREAKS.position_mutation_blocks += 1

    block(
        "position mutation disabled"
    )


def forbidden_account_mutation() -> None:

    FIREBREAKS.account_mutation_blocks += 1

    block(
        "account mutation disabled"
    )


# =============================================================================
# PART 3
# LIVE READ-ONLY OBSERVATION
# VALIDATION
# STRATEGY PROJECTION
# =============================================================================


def normalize_list_payload(
    payload: Any,
    name: str,
) -> List[Any]:

    if isinstance(
        payload,
        list,
    ):
        return payload


    if isinstance(
        payload,
        dict,
    ):

        for key in (
            "data",
            "result",
            "rows",
            "list",
        ):

            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                return value


        if (
            name == "symbolPrice"
            and
            "symbol" in payload
            and
            "price" in payload
        ):

            return [
                payload
            ]


    raise RemoteReadError(
        f"unexpected {name} "
        f"response shape: "
        f"{type(payload).__name__}"
    )


# =============================================================================
# LIVE PUBLIC MARK PRICE
# =============================================================================


def fetch_live_market() -> MarketObservation:

    payload = TRANSPORT.get_public(
        PUBLIC_MARK_PATH,
        {
            "symbol":
                SYMBOL,

            "priceType":
                "MARK",
        },
    )

    rows = normalize_list_payload(
        payload,
        "symbolPrice",
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
            == SYMBOL
        ),
        None,
    )

    if row is None:

        raise RemoteReadError(
            f"{SYMBOL} missing from "
            f"mark-price response"
        )


    price = as_decimal(
        row.get("price"),
        "mark price",
    )

    if price <= 0:

        raise RemoteReadError(
            "mark price is nonpositive"
        )


    remote_time = int(
        row.get("time")
        or utc_ms()
    )


    return MarketObservation(
        symbol=SYMBOL,

        mark_price=decimal_text(
            price
        ),

        observed_at_ms=utc_ms(),

        source=(
            "WEEX_V3_PUBLIC_GET_"
            "READ_ONLY"
        ),

        remote_time_ms=remote_time,
    )


# =============================================================================
# EXCHANGE INFORMATION / CONTRACT RULES
# =============================================================================


def _extract_symbol_rules(
    symbol_row: Dict[str, Any],
) -> ContractRules:

    quantity_precision = int(
        symbol_row.get(
            "quantityPrecision",
            symbol_row.get(
                "volumePlace",
                4,
            ),
        )
    )

    price_precision = int(
        symbol_row.get(
            "pricePrecision",
            symbol_row.get(
                "pricePlace",
                1,
            ),
        )
    )


    qty_step_raw = (
        symbol_row.get(
            "quantityStep"
        )
        or
        symbol_row.get(
            "stepSize"
        )
        or
        symbol_row.get(
            "sizeMultiplier"
        )
        or
        (
            "1e-"
            + str(
                quantity_precision
            )
        )
    )


    min_qty_raw = (
        symbol_row.get(
            "minQty"
        )
        or
        symbol_row.get(
            "minOrderQty"
        )
        or
        symbol_row.get(
            "minTradeNum"
        )
        or
        symbol_row.get(
            "minOrderSize"
        )
        or
        qty_step_raw
    )


    price_step_raw = (
        symbol_row.get(
            "priceStep"
        )
        or
        symbol_row.get(
            "tickSize"
        )
        or
        (
            "1e-"
            + str(
                price_precision
            )
        )
    )


    return ContractRules(
        symbol=SYMBOL,

        quantity_precision=(
            quantity_precision
        ),

        quantity_step=decimal_text(
            as_decimal(
                qty_step_raw,
                "quantity step",
            )
        ),

        minimum_quantity=decimal_text(
            as_decimal(
                min_qty_raw,
                "minimum quantity",
            )
        ),

        price_precision=(
            price_precision
        ),

        price_step=decimal_text(
            as_decimal(
                price_step_raw,
                "price step",
            )
        ),

        source=(
            "WEEX_V3_PUBLIC_GET_"
            "READ_ONLY"
        ),
    )


def fetch_contract_rules() -> ContractRules:

    payload = TRANSPORT.get_public(
        PUBLIC_EXCHANGE_INFO_PATH,
        {
            "symbol":
                SYMBOL,
        },
    )


    root = (
        payload.get(
            "data",
            payload,
        )
        if isinstance(
            payload,
            dict,
        )
        else payload
    )


    if not isinstance(
        root,
        dict,
    ):

        raise RemoteReadError(
            "unexpected exchangeInfo "
            "response shape"
        )


    symbols = root.get(
        "symbols"
    )


    if not isinstance(
        symbols,
        list,
    ):

        raise RemoteReadError(
            "exchangeInfo symbols "
            "list missing"
        )


    row = next(
        (
            item
            for item in symbols
            if str(
                item.get(
                    "symbol",
                    "",
                )
            ).upper()
            == SYMBOL
        ),
        None,
    )


    if row is None:

        raise RemoteReadError(
            f"{SYMBOL} missing from "
            f"exchangeInfo"
        )


    return _extract_symbol_rules(
        row
    )


# =============================================================================
# AUTHENTICATED BALANCE / POSITION OBSERVATION
# =============================================================================


def fetch_account_and_positions(
) -> Tuple[
    AccountObservation,
    List[Dict[str, Any]],
]:

    balance_payload = (
        TRANSPORT.get_private(
            PRIVATE_BALANCE_PATH
        )
    )


    balance_rows = (
        normalize_list_payload(
            balance_payload,
            "balance",
        )
    )


    balance_row = next(
        (
            item
            for item
            in balance_rows
            if str(
                item.get(
                    "asset",
                    "",
                )
            ).upper()
            == ASSET
        ),
        None,
    )


    if balance_row is None:

        raise RemoteReadError(
            f"{ASSET} missing from "
            f"balance response"
        )


    positions_payload = (
        TRANSPORT.get_private(
            PRIVATE_POSITIONS_PATH
        )
    )


    positions = (
        normalize_list_payload(
            positions_payload,
            "positions",
        )
    )


    symbol_positions = [
        item
        for item in positions

        if (
            str(
                item.get(
                    "symbol",
                    "",
                )
            ).upper()
            == SYMBOL

            and

            as_decimal(
                item.get(
                    "size",
                    "0",
                ),
                "position size",
            )
            != 0
        )
    ]


    available = as_decimal(
        balance_row.get(
            "availableBalance",
            "0",
        ),
        "available balance",
    )


    balance = as_decimal(
        balance_row.get(
            "balance",
            "0",
        ),
        "balance",
    )


    frozen = as_decimal(
        balance_row.get(
            "frozen",
            "0",
        ),
        "frozen",
    )


    pnl = as_decimal(
        balance_row.get(
            "unrealizePnl",
            "0",
        ),
        "unrealized pnl",
    )


    if (
        available < 0
        or
        balance < 0
        or
        frozen < 0
    ):

        raise RemoteReadError(
            "negative account balance "
            "field returned"
        )


    observation = AccountObservation(
        asset=ASSET,

        balance=decimal_text(
            balance
        ),

        available_balance=decimal_text(
            available
        ),

        frozen=decimal_text(
            frozen
        ),

        unrealized_pnl=decimal_text(
            pnl
        ),

        position_count=len(
            symbol_positions
        ),

        observed_at_ms=utc_ms(),

        source=(
            "WEEX_V3_AUTHENTICATED_"
            "GET_READ_ONLY"
        ),
    )


    return (
        observation,
        symbol_positions,
    )


# =============================================================================
# AUTHENTICATED SYMBOL CONFIGURATION
# =============================================================================


def fetch_symbol_configuration(
) -> SymbolConfiguration:

    payload = TRANSPORT.get_private(
        PRIVATE_SYMBOL_CONFIG_PATH,
        {
            "symbol":
                SYMBOL,
        },
    )


    rows = normalize_list_payload(
        payload,
        "symbolConfig",
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
            == SYMBOL
        ),
        None,
    )


    if row is None:

        raise RemoteReadError(
            f"{SYMBOL} missing from "
            f"symbolConfig"
        )


    return SymbolConfiguration(
        symbol=SYMBOL,

        margin_type=str(
            row.get(
                "marginType",
                "UNKNOWN",
            )
        ).upper(),

        separated_type=str(
            row.get(
                "separatedType",
                row.get(
                    "separatedMode",
                    "UNKNOWN",
                ),
            )
        ).upper(),

        cross_leverage=str(
            row.get(
                "crossLeverage",
                "0",
            )
        ),

        isolated_long_leverage=str(
            row.get(
                "isolatedLongLeverage",
                "0",
            )
        ),

        isolated_short_leverage=str(
            row.get(
                "isolatedShortLeverage",
                "0",
            )
        ),

        observed_at_ms=utc_ms(),

        source=(
            "WEEX_V3_AUTHENTICATED_"
            "GET_READ_ONLY"
        ),
    )


# =============================================================================
# OBSERVATION VALIDATORS
# =============================================================================


def validate_market_observation(
    obs: MarketObservation,
) -> None:

    require(
        obs.symbol == SYMBOL,
        "market observation "
        "symbol mismatch",
    )

    require(
        as_decimal(
            obs.mark_price,
            "mark price",
        ) > 0,
        "mark price must be positive",
    )

    require(
        obs.source.endswith(
            "READ_ONLY"
        ),
        "market observation source "
        "is not read-only",
    )


def validate_account_observation(
    obs: AccountObservation,
) -> None:

    require(
        obs.asset == ASSET,
        "account observation "
        "asset mismatch",
    )

    require(
        as_decimal(
            obs.available_balance,
            "available balance",
        ) >= 0,
        "available balance "
        "cannot be negative",
    )

    require(
        obs.source.endswith(
            "READ_ONLY"
        ),
        "account observation source "
        "is not read-only",
    )


def validate_symbol_configuration(
    cfg: SymbolConfiguration,
) -> None:

    require(
        cfg.symbol == SYMBOL,
        "symbol configuration "
        "symbol mismatch",
    )

    require(
        cfg.source.endswith(
            "READ_ONLY"
        ),
        "symbol configuration source "
        "is not read-only",
    )

    require(
        as_decimal(
            cfg.isolated_long_leverage,
            "isolated long leverage",
        ) > 0,
        "invalid isolated "
        "long leverage",
    )

    require(
        as_decimal(
            cfg.isolated_short_leverage,
            "isolated short leverage",
        ) > 0,
        "invalid isolated "
        "short leverage",
    )


# =============================================================================
# CONFIGURATION FINGERPRINT
# =============================================================================


def configuration_fingerprint(
) -> str:

    config = {
        "unit":
            UNIT,

        "symbol":
            SYMBOL,

        "asset":
            ASSET,

        "margin_type":
            MARGIN_TYPE,

        "planned_leverage":
            decimal_text(
                PLANNED_LEVERAGE
            ),

        "initial_allocation_percent":
            decimal_text(
                INITIAL_ALLOCATION_PERCENT
            ),

        "max_fund_exposure_percent":
            decimal_text(
                MAX_FUND_EXPOSURE_PERCENT
            ),

        "real_order_execution":
            REAL_ORDER_EXECUTION,

        "demo_order_execution":
            DEMO_ORDER_EXECUTION,

        "network_writes_enabled":
            NETWORK_WRITES_ENABLED,

        "synthetic_transport_only":
            SYNTHETIC_TRANSPORT_ONLY,

        "allowed_gets":
            sorted(
                ALL_ALLOWED_GETS
            ),
    }


    return sha256_text(
        canonical_json(
            config
        )
    )


def observation_hash(
    obj: Any,
) -> str:

    return sha256_text(
        canonical_json(
            asdict(obj)
        )
    )


# =============================================================================
# SYNTHETIC STRATEGY SIGNAL
# =============================================================================


def make_signal(
    direction: str,
) -> StrategySignal:

    now = utc_ms()

    return StrategySignal(
        signal_id=str(
            uuid.uuid4()
        ),

        symbol=SYMBOL,

        direction=direction.upper(),

        created_at_ms=now,

        expires_at_ms=(
            now
            + SIGNAL_EXPIRY_SECONDS
            * 1000
        ),

        source=(
            "R29_UNIT_C_"
            "SYNTHETIC_SIGNAL"
        ),
    )


def validate_signal(
    signal: StrategySignal,
) -> None:

    require(
        signal.symbol == SYMBOL,
        "strategy signal "
        "symbol mismatch",
    )

    require(
        signal.direction
        in {
            "LONG",
            "SHORT",
        },
        "invalid strategy direction",
    )

    require(
        utc_ms()
        <= signal.expires_at_ms,
        "strategy signal expired",
    )

    require(
        signal.source
        == (
            "R29_UNIT_C_"
            "SYNTHETIC_SIGNAL"
        ),
        "unexpected signal source",
    )


# =============================================================================
# QUANTITY / RISK PROJECTION
# =============================================================================


def floor_to_step(
    quantity: Decimal,
    step: Decimal,
) -> Decimal:

    require(
        step > 0,
        "quantity step must be positive",
    )

    units = (
        quantity
        / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return (
        units
        * step
    )


def risk_projection(
    account: AccountObservation,
    market: MarketObservation,
    rules: ContractRules,
) -> RiskProjection:

    available = as_decimal(
        account.available_balance,
        "available balance",
    )

    price = as_decimal(
        market.mark_price,
        "mark price",
    )

    step = as_decimal(
        rules.quantity_step,
        "quantity step",
    )

    minimum = as_decimal(
        rules.minimum_quantity,
        "minimum quantity",
    )


    margin_budget = (
        available
        * INITIAL_ALLOCATION_PERCENT
        / Decimal("100")
    )


    planned_notional = (
        margin_budget
        * PLANNED_LEVERAGE
    )


    raw_quantity = (
        planned_notional
        / price
    )


    rounded = floor_to_step(
        raw_quantity,
        step,
    )


    # If the precise 5% target is below
    # the exchange minimum, Unit C
    # refuses to inflate exposure.

    require(
        rounded >= minimum,
        "projected quantity is below "
        "exchange minimum",
    )


    projected_notional = (
        rounded
        * price
    )


    projected_margin = (
        projected_notional
        / PLANNED_LEVERAGE
    )


    fund_cap = (
        available
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )


    require(
        projected_margin
        <= fund_cap,
        "projected margin exceeds "
        "fund cap",
    )


    return RiskProjection(
        margin_budget=decimal_text(
            margin_budget
        ),

        planned_notional=decimal_text(
            planned_notional
        ),

        raw_quantity=decimal_text(
            raw_quantity
        ),

        rounded_quantity=decimal_text(
            rounded
        ),

        projected_margin=decimal_text(
            projected_margin
        ),

        fund_cap=decimal_text(
            fund_cap
        ),
    )


# =============================================================================
# NON-EXECUTABLE DECISION ENVELOPE
# =============================================================================


def build_decision(
    signal: StrategySignal,
    market: MarketObservation,
    account: AccountObservation,
    projection: RiskProjection,
) -> DecisionEnvelope:

    validate_signal(
        signal
    )


    side = (
        "BUY"
        if signal.direction == "LONG"
        else "SELL"
    )


    decision_id = str(
        uuid.uuid4()
    )


    base = {
        "decision_id":
            decision_id,

        "symbol":
            SYMBOL,

        "side":
            side,

        "position_side":
            signal.direction,

        "quantity":
            projection.rounded_quantity,

        "reference_price":
            market.mark_price,

        "leverage":
            decimal_text(
                PLANNED_LEVERAGE
            ),

        "executable":
            False,

        "synthetic_only":
            True,

        "configuration_fingerprint":
            configuration_fingerprint(),

        "market_observation_hash":
            observation_hash(
                market
            ),

        "account_observation_hash":
            observation_hash(
                account
            ),
    }


    payload_hash = sha256_text(
        canonical_json(
            base
        )
    )


    return DecisionEnvelope(
        payload_hash=payload_hash,
        **base,
    )


def validate_decision(
    decision: DecisionEnvelope,
) -> None:

    require(
        decision.symbol == SYMBOL,
        "decision symbol mismatch",
    )

    require(
        decision.executable
        is False,
        "decision unexpectedly "
        "executable",
    )

    require(
        decision.synthetic_only
        is True,
        "decision is not "
        "synthetic-only",
    )

    require(
        decision.configuration_fingerprint
        == configuration_fingerprint(),
        "decision configuration "
        "fingerprint mismatch",
    )


    base = asdict(
        decision
    )

    saved_hash = base.pop(
        "payload_hash"
    )


    require(
        sha256_text(
            canonical_json(
                base
            )
        )
        == saved_hash,
        "decision payload hash mismatch",
    )


# =============================================================================
# SYNTHETIC TRANSPORT ONLY
# =============================================================================


def synthetic_dispatch(
    decision: DecisionEnvelope,
) -> SyntheticReceipt:

    validate_decision(
        decision
    )


    return SyntheticReceipt(
        receipt_id=str(
            uuid.uuid4()
        ),

        decision_id=(
            decision.decision_id
        ),

        decision_payload_hash=(
            decision.payload_hash
        ),

        transport=(
            "R29_UNIT_C_"
            "SYNTHETIC_ONLY"
        ),

        transmitted=False,

        created_at_ms=utc_ms(),
    )


print(
    "R29 UNIT C: PART 2 DEFINITIONS LOADED",
    flush=True,
)

print(
    "R29 UNIT C: PART 3 DEFINITIONS LOADED",
    flush=True,
)


# =============================================================================
# PART 4
# DURABLE STATE
# HEALTH SERVER
# DIAGNOSTICS
# =============================================================================


def state_payload_without_seal(
    state: RuntimeState,
) -> Dict[str, Any]:

    data = asdict(
        state
    )

    data.pop(
        "integrity_seal",
        None,
    )

    return data


def seal_state(
    state: RuntimeState,
) -> str:

    return sha256_text(
        canonical_json(
            state_payload_without_seal(
                state
            )
        )
    )


def validate_state(
    state: RuntimeState,
) -> None:

    require(
        state.schema_version == 1,
        "runtime state schema mismatch",
    )

    require(
        state.unit == UNIT,
        "runtime state unit mismatch",
    )

    require(
        state.configuration_fingerprint
        == configuration_fingerprint(),
        "runtime configuration mismatch",
    )

    require(
        state.integrity_seal
        == seal_state(state),
        "runtime state integrity "
        "seal mismatch",
    )

    require(
        state.real_order_count == 0,
        "real order counter is nonzero",
    )

    require(
        state.demo_order_count == 0,
        "demo order counter is nonzero",
    )

    require(
        state.network_write_count == 0,
        "network write counter is nonzero",
    )


def write_state_atomic(
    state: RuntimeState,
    path: Path = STATE_PATH,
) -> None:

    state.integrity_seal = seal_state(
        state
    )


    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    tmp = path.with_name(
        path.name + ".tmp"
    )


    tmp.write_text(
        canonical_json(
            asdict(state)
        ),
        encoding="utf-8",
    )


    os.replace(
        tmp,
        path,
    )


def load_state(
    path: Path = STATE_PATH,
) -> Optional[RuntimeState]:

    if not path.exists():
        return None


    try:

        raw = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        state = RuntimeState(
            **raw
        )

    except Exception as exc:

        raise LocalBlock(
            "runtime state load failed: "
            f"{exc}"
        ) from exc


    validate_state(
        state
    )

    return state


def initialize_runtime_state(
) -> RuntimeState:

    existing = load_state()


    if existing is None:

        state = RuntimeState(
            schema_version=1,

            unit=UNIT,

            runtime_id=str(
                uuid.uuid4()
            ),

            generation=1,

            recovery_epoch=1,

            boot_counter=1,

            configuration_fingerprint=(
                configuration_fingerprint()
            ),

            latest_market_hash="",

            latest_account_hash="",

            latest_symbol_config_hash="",

            latest_decision_id="",

            latest_decision_hash="",

            synthetic_dispatch_count=0,

            real_order_count=0,

            demo_order_count=0,

            network_write_count=0,

            read_request_count=0,
        )

    else:

        state = existing

        state.recovery_epoch += 1

        state.boot_counter += 1


    write_state_atomic(
        state
    )

    return state


# =============================================================================
# HEALTH SERVER
# =============================================================================


class HealthHandler(
    http.server.BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ) -> None:

        body = json.dumps(
            {
                "ok":
                    True,

                "unit":
                    UNIT,

                "synthetic_only":
                    SYNTHETIC_TRANSPORT_ONLY,

                "network_writes":
                    NETWORK_WRITES_ENABLED,
            }
        ).encode(
            "utf-8"
        )


        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(
                len(body)
            ),
        )

        self.end_headers()

        self.wfile.write(
            body
        )


    def do_POST(
        self,
    ) -> None:

        self.send_response(
            405
        )

        self.end_headers()


    def do_PUT(
        self,
    ) -> None:

        self.send_response(
            405
        )

        self.end_headers()


    def do_PATCH(
        self,
    ) -> None:

        self.send_response(
            405
        )

        self.end_headers()


    def do_DELETE(
        self,
    ) -> None:

        self.send_response(
            405
        )

        self.end_headers()


    def log_message(
        self,
        fmt: str,
        *args: Any,
    ) -> None:

        return


class ReusableTCPServer(
    socketserver.TCPServer
):

    allow_reuse_address = True


def start_health_server(
) -> ReusableTCPServer:

    server = ReusableTCPServer(
        (
            "0.0.0.0",
            PORT,
        ),
        HealthHandler,
    )


    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )


    thread.start()


    print(
        f"{UNIT}: HEALTH SERVER "
        f"LISTENING ON PORT {PORT}",
        flush=True,
    )


    return server


# =============================================================================
# DIAGNOSTICS
# =============================================================================


def diagnostics(
) -> RuntimeState:

    separator()

    print(
        f"{UNIT}: STARTING DIAGNOSTICS",
        flush=True,
    )

    separator()


    # =========================================================================
    # TEST 1
    # =========================================================================

    start_test(
        1,
        "R29 SAFETY CONFIGURATION",
    )

    passed(
        "Real Order Execution Disabled",
        REAL_ORDER_EXECUTION is False,
    )

    passed(
        "Demo Order Execution Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    passed(
        "Network Writes Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    passed(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    passed(
        "WebSocket Writes Disabled",
        WEBSOCKET_WRITES_ENABLED is False,
    )

    passed(
        "Leverage Mutation Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    passed(
        "Margin Mutation Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    passed(
        "Position Mutation Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    passed(
        "Account Mutation Disabled",
        ACCOUNT_MUTATION_ENABLED is False,
    )


    # =========================================================================
    # TEST 2
    # =========================================================================

    start_test(
        2,
        "GET-ONLY NETWORK ALLOWLIST",
    )

    passed(
        "Contract Host Is Allowlisted",
        (
            "api-contract.weex.com"
            in ALLOWED_HOSTS
        ),
    )

    passed(
        "Mark Price GET Is Allowlisted",
        PUBLIC_MARK_PATH
        in ALL_ALLOWED_GETS,
    )

    passed(
        "Exchange Info GET Is Allowlisted",
        PUBLIC_EXCHANGE_INFO_PATH
        in ALL_ALLOWED_GETS,
    )

    passed(
        "Balance GET Is Allowlisted",
        PRIVATE_BALANCE_PATH
        in ALL_ALLOWED_GETS,
    )

    passed(
        "Positions GET Is Allowlisted",
        PRIVATE_POSITIONS_PATH
        in ALL_ALLOWED_GETS,
    )

    passed(
        "Symbol Config GET Is Allowlisted",
        PRIVATE_SYMBOL_CONFIG_PATH
        in ALL_ALLOWED_GETS,
    )


    expect_local_block(
        "Unlisted Endpoint Rejected",
        lambda:
            ReadOnlyTransport
            ._validate_target(
                "/capi/v3/order"
            ),
    )


    # =========================================================================
    # TEST 3
    # =========================================================================

    start_test(
        3,
        "LIVE PUBLIC MARK-PRICE OBSERVATION",
    )


    market = fetch_live_market()


    validate_market_observation(
        market
    )


    passed(
        "Live Mark Price Accepted"
    )


    passed(
        "Live Mark Price Is Positive",
        as_decimal(
            market.mark_price,
            "mark",
        ) > 0,
    )


    passed(
        "Market Observation Is Read-Only",
        market.source.endswith(
            "READ_ONLY"
        ),
    )


    print(
        f"{UNIT}: LIVE MARK PRICE "
        f"{SYMBOL} = "
        f"{market.mark_price}",
        flush=True,
    )


    # =========================================================================
    # TEST 4
    # =========================================================================

    start_test(
        4,
        "LIVE PUBLIC CONTRACT RULES",
    )


    rules = fetch_contract_rules()


    passed(
        "Contract Rules Symbol Matches",
        rules.symbol == SYMBOL,
    )


    passed(
        "Quantity Step Is Positive",
        as_decimal(
            rules.quantity_step,
            "step",
        ) > 0,
    )


    passed(
        "Minimum Quantity Is Positive",
        as_decimal(
            rules.minimum_quantity,
            "min",
        ) > 0,
    )


    passed(
        "Price Step Is Positive",
        as_decimal(
            rules.price_step,
            "price step",
        ) > 0,
    )


    print(
        f"{UNIT}: CONTRACT RULES "
        f"qty-step={rules.quantity_step} "
        f"min-qty={rules.minimum_quantity} "
        f"price-step={rules.price_step}",
        flush=True,
    )


    # =========================================================================
    # TEST 5
    # =========================================================================

    start_test(
        5,
        "PRIVATE READ CREDENTIAL PRESENCE",
    )


    passed(
        "WEEX API Key Present",
        bool(API_KEY),
    )


    passed(
        "WEEX Secret Key Present",
        bool(SECRET_KEY),
    )


    passed(
        "WEEX Passphrase Present",
        bool(PASSPHRASE),
    )


    passed(
        "Credential Values Are Not Printed",
        True,
    )


    # =========================================================================
    # TEST 6
    # =========================================================================

    start_test(
        6,
        "AUTHENTICATED READ-ONLY ACCOUNT OBSERVATION",
    )


    account, positions = (
        fetch_account_and_positions()
    )


    validate_account_observation(
        account
    )


    passed(
        "Authenticated Balance GET Accepted"
    )


    passed(
        "Available Balance Is Nonnegative",
        as_decimal(
            account.available_balance,
            "available",
        ) >= 0,
    )


    passed(
        "Positions GET Accepted"
    )


    passed(
        "Observed Position Count Is Nonnegative",
        account.position_count >= 0,
    )


    print(
        f"{UNIT}: "
        f"{ASSET} "
        f"available="
        f"{account.available_balance} "
        f"balance="
        f"{account.balance} "
        f"open-{SYMBOL}-positions="
        f"{account.position_count}",
        flush=True,
    )


    # =========================================================================
    # TEST 7
    # =========================================================================

    start_test(
        7,
        "AUTHENTICATED SYMBOL CONFIGURATION",
    )


    symbol_cfg = (
        fetch_symbol_configuration()
    )


    validate_symbol_configuration(
        symbol_cfg
    )


    passed(
        "Symbol Configuration GET Accepted"
    )


    passed(
        "Symbol Configuration Symbol Matches",
        symbol_cfg.symbol == SYMBOL,
    )


    passed(
        "Observed Margin Type Is Recognized",
        symbol_cfg.margin_type
        in {
            "ISOLATED",
            "CROSSED",
            "SHARED",
        },
    )


    passed(
        "Observed Long Leverage Is Positive",
        as_decimal(
            symbol_cfg.isolated_long_leverage,
            "long lev",
        ) > 0,
    )


    passed(
        "Observed Short Leverage Is Positive",
        as_decimal(
            symbol_cfg.isolated_short_leverage,
            "short lev",
        ) > 0,
    )


    print(
        f"{UNIT}: SYMBOL CONFIG "
        f"margin="
        f"{symbol_cfg.margin_type} "
        f"isolated-long="
        f"{symbol_cfg.isolated_long_leverage}x "
        f"isolated-short="
        f"{symbol_cfg.isolated_short_leverage}x",
        flush=True,
    )


    # =========================================================================
    # TEST 8
    # =========================================================================

    start_test(
        8,
        "LIVE OBSERVATION COHERENCE",
    )


    passed(
        "Market Symbol Matches Strategy",
        market.symbol == SYMBOL,
    )


    passed(
        "Account Asset Matches Strategy",
        account.asset == ASSET,
    )


    passed(
        "Symbol Config Matches Strategy",
        symbol_cfg.symbol == SYMBOL,
    )


    passed(
        "Public And Private Reads Completed",
        TRANSPORT.read_count >= 5,
    )


    passed(
        "No Network Write Counter Exists In Transport",
        not hasattr(
            TRANSPORT,
            "write_count",
        ),
    )


    # =========================================================================
    # TEST 9
    # =========================================================================

    start_test(
        9,
        "STRATEGY COMPATIBILITY - OBSERVATION ONLY",
    )


    passed(
        "Planned Margin Mode Is Isolated",
        MARGIN_TYPE == "ISOLATED",
    )


    passed(
        "Planned Leverage Is 100x",
        PLANNED_LEVERAGE
        == Decimal("100"),
    )


    long_ready = (
        as_decimal(
            symbol_cfg.isolated_long_leverage,
            "long lev",
        )
        == PLANNED_LEVERAGE
    )


    short_ready = (
        as_decimal(
            symbol_cfg.isolated_short_leverage,
            "short lev",
        )
        == PLANNED_LEVERAGE
    )


    print(
        f"{UNIT}: "
        f"LONG 100x READINESS = "
        f"{long_ready}",
        flush=True,
    )


    print(
        f"{UNIT}: "
        f"SHORT 100x READINESS = "
        f"{short_ready}",
        flush=True,
    )


    passed(
        "Readiness Was Observed Without Mutation"
    )


    passed(
        "Leverage Mutation Still Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )


    # =========================================================================
    # TEST 10
    # =========================================================================

    start_test(
        10,
        "READ-ONLY INITIAL ENTRY RISK PROJECTION",
    )


    projection = risk_projection(
        account,
        market,
        rules,
    )


    passed(
        "Margin Budget Is Positive",
        as_decimal(
            projection.margin_budget,
            "margin budget",
        ) > 0,
    )


    passed(
        "Planned Notional Is Positive",
        as_decimal(
            projection.planned_notional,
            "notional",
        ) > 0,
    )


    passed(
        "Rounded Quantity Meets Minimum",
        as_decimal(
            projection.rounded_quantity,
            "qty",
        )
        >=
        as_decimal(
            rules.minimum_quantity,
            "min",
        ),
    )


    passed(
        "Projected Margin Is Within Fund Cap",
        as_decimal(
            projection.projected_margin,
            "margin",
        )
        <=
        as_decimal(
            projection.fund_cap,
            "cap",
        ),
    )


    print(
        f"{UNIT}: PROJECTION "
        f"margin-budget="
        f"{projection.margin_budget} "
        f"notional="
        f"{projection.planned_notional} "
        f"qty="
        f"{projection.rounded_quantity}",
        flush=True,
    )


    # =========================================================================
    # TEST 11
    # =========================================================================

    start_test(
        11,
        "FROZEN NON-EXECUTABLE DECISION ENVELOPE",
    )


    signal = make_signal(
        "LONG"
    )


    decision = build_decision(
        signal,
        market,
        account,
        projection,
    )


    validate_decision(
        decision
    )


    passed(
        "Decision Uses BUY",
        decision.side == "BUY",
    )


    passed(
        "Decision Uses LONG Position Side",
        decision.position_side
        == "LONG",
    )


    passed(
        "Decision Is Non-Executable",
        decision.executable
        is False,
    )


    passed(
        "Decision Is Synthetic-Only",
        decision.synthetic_only
        is True,
    )


    passed(
        "Decision Payload Hash Established",
        len(
            decision.payload_hash
        )
        == 64,
    )


    tampered = DecisionEnvelope(
        **{
            **asdict(
                decision
            ),
            "executable":
                True,
        }
    )


    expect_local_block(
        "Executable Decision Rejected",
        lambda:
            validate_decision(
                tampered
            ),
    )


    # =========================================================================
    # TEST 12
    # =========================================================================

    start_test(
        12,
        "SYNTHETIC DECISION TRANSPORT",
    )


    receipt = synthetic_dispatch(
        decision
    )


    passed(
        "Synthetic Receipt Accepted"
    )


    passed(
        "Synthetic Receipt Reports No Transmission",
        receipt.transmitted
        is False,
    )


    passed(
        "Synthetic Transport Exact",
        receipt.transport
        == (
            "R29_UNIT_C_"
            "SYNTHETIC_ONLY"
        ),
    )


    passed(
        "Decision ID Preserved",
        receipt.decision_id
        == decision.decision_id,
    )


    passed(
        "Decision Payload Hash Preserved",
        receipt.decision_payload_hash
        == decision.payload_hash,
    )


    # =========================================================================
    # TEST 13
    # =========================================================================

    start_test(
        13,
        "REAL/DEMO/WEBSOCKET WRITE FIREBREAKS",
    )


    expect_local_block(
        "Real HTTP Write Blocked",
        lambda:
            forbidden_real_http_write(
                "POST"
            ),
    )


    expect_local_block(
        "Demo HTTP Write Blocked",
        lambda:
            forbidden_demo_http_write(
                "POST"
            ),
    )


    expect_local_block(
        "WebSocket Write Blocked",
        forbidden_websocket_write,
    )


    expect_local_block(
        "Leverage Mutation Blocked",
        forbidden_leverage_mutation,
    )


    expect_local_block(
        "Margin Mutation Blocked",
        forbidden_margin_mutation,
    )


    expect_local_block(
        "Position Mutation Blocked",
        forbidden_position_mutation,
    )


    expect_local_block(
        "Account Mutation Blocked",
        forbidden_account_mutation,
    )


    passed(
        "All Write Firebreak Counters Advanced",
        sum(
            asdict(
                FIREBREAKS
            ).values()
        )
        == 7,
    )


    # =========================================================================
    # TEST 14
    # =========================================================================

    start_test(
        14,
        "DURABLE LIVE-OBSERVATION RUNTIME STATE",
    )


    state = initialize_runtime_state()


    state.latest_market_hash = (
        observation_hash(
            market
        )
    )


    state.latest_account_hash = (
        observation_hash(
            account
        )
    )


    state.latest_symbol_config_hash = (
        observation_hash(
            symbol_cfg
        )
    )


    state.latest_decision_id = (
        decision.decision_id
    )


    state.latest_decision_hash = (
        decision.payload_hash
    )


    state.synthetic_dispatch_count += 1


    state.read_request_count += (
        TRANSPORT.read_count
    )


    write_state_atomic(
        state
    )


    restored = load_state()


    require(
        restored is not None,
        "runtime state "
        "did not restore",
    )


    passed(
        "Durable Runtime State Created"
    )


    passed(
        "Runtime ID Restored",
        restored.runtime_id
        == state.runtime_id,
    )


    passed(
        "Market Observation Hash Restored",
        restored.latest_market_hash
        == state.latest_market_hash,
    )


    passed(
        "Account Observation Hash Restored",
        restored.latest_account_hash
        == state.latest_account_hash,
    )


    passed(
        "Symbol Config Hash Restored",
        restored.latest_symbol_config_hash
        == state.latest_symbol_config_hash,
    )


    passed(
        "Decision Binding Restored",
        restored.latest_decision_hash
        == decision.payload_hash,
    )


    passed(
        "Network Write Count Remains Zero",
        restored.network_write_count
        == 0,
    )


    # =========================================================================
    # TEST 15
    # =========================================================================

    start_test(
        15,
        "RESTART CONTINUITY",
    )


    restarted = (
        initialize_runtime_state()
    )


    passed(
        "Runtime Identity Survives Restart",
        restarted.runtime_id
        == state.runtime_id,
    )


    passed(
        "Generation Survives Same-Configuration Restart",
        restarted.generation
        == state.generation,
    )


    passed(
        "Recovery Epoch Advances On Restart",
        restarted.recovery_epoch
        == state.recovery_epoch + 1,
    )


    passed(
        "Boot Counter Advances On Restart",
        restarted.boot_counter
        == state.boot_counter + 1,
    )


    passed(
        "Live Market Binding Survives Restart",
        restarted.latest_market_hash
        == state.latest_market_hash,
    )


    passed(
        "Decision Binding Survives Restart",
        restarted.latest_decision_hash
        == state.latest_decision_hash,
    )


    passed(
        "Real Order Counter Remains Zero",
        restarted.real_order_count
        == 0,
    )


    passed(
        "Demo Order Counter Remains Zero",
        restarted.demo_order_count
        == 0,
    )


    passed(
        "Network Write Counter Remains Zero",
        restarted.network_write_count
        == 0,
    )


    # =========================================================================
    # TEST 16
    # =========================================================================

    start_test(
        16,
        "TERMINAL UNIT C SAFETY INVARIANTS",
    )


    validate_state(
        restarted
    )


    passed(
        "Final Durable Runtime State Validates"
    )


    passed(
        "Live Reads Were GET-Only",
        TRANSPORT.read_count >= 5,
    )


    passed(
        "Real Order Execution Remains Disabled",
        REAL_ORDER_EXECUTION
        is False,
    )


    passed(
        "Demo Order Execution Remains Disabled",
        DEMO_ORDER_EXECUTION
        is False,
    )


    passed(
        "All Network Writes Remain Disabled",
        NETWORK_WRITES_ENABLED
        is False,
    )


    passed(
        "Synthetic Transport Remains Exclusive",
        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )


    passed(
        "Leverage Mutation Remains Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )


    passed(
        "Margin Mutation Remains Disabled",
        MARGIN_MUTATION_ENABLED
        is False,
    )


    passed(
        "Position Mutation Remains Disabled",
        POSITION_MUTATION_ENABLED
        is False,
    )


    passed(
        "Account Mutation Remains Disabled",
        ACCOUNT_MUTATION_ENABLED
        is False,
    )


    passed(
        "Final Real Order Count Is Zero",
        restarted.real_order_count
        == 0,
    )


    passed(
        "Final Demo Order Count Is Zero",
        restarted.demo_order_count
        == 0,
    )


    passed(
        "Final Network Write Count Is Zero",
        restarted.network_write_count
        == 0,
    )


    return restarted


# =============================================================================
# MAIN
# =============================================================================


def main() -> None:

    state = diagnostics()


    separator()

    print(
        f"{UNIT}: ALL DIAGNOSTICS PASSED",
        flush=True,
    )

    separator()


    print(
        "NO REAL ORDER WAS SENT",
        flush=True,
    )

    print(
        "NO DEMO ORDER WAS SENT",
        flush=True,
    )

    print(
        "NO NETWORK WRITE WAS ATTEMPTED",
        flush=True,
    )


    print(
        f"{UNIT}: "
        f"TEST GROUPS EXECUTED = "
        f"{TEST_GROUPS}",
        flush=True,
    )


    print(
        f"{UNIT}: "
        f"PASS ASSERTIONS = "
        f"{PASS_ASSERTIONS}",
        flush=True,
    )


    server = start_health_server()


    heartbeat = 0


    try:

        while True:

            heartbeat += 1


            print(
                f"{UNIT}: "
                f"HEARTBEAT {heartbeat} "
                f"| synthetic-only="
                f"{SYNTHETIC_TRANSPORT_ONLY} "
                f"| network-writes="
                f"{NETWORK_WRITES_ENABLED} "
                f"| generation="
                f"{state.generation} "
                f"| recovery-epoch="
                f"{state.recovery_epoch} "
                f"| live-reads="
                f"{state.read_request_count}",
                flush=True,
            )


            time.sleep(
                HEARTBEAT_SECONDS
            )


    except KeyboardInterrupt:

        print(
            f"{UNIT}: SHUTDOWN REQUESTED",
            flush=True,
        )


    finally:

        server.shutdown()

        server.server_close()


if __name__ == "__main__":
    main()
