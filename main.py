#!/usr/bin/env python3

"""
WEEX PARALLEL BOT RECONSTRUCTION

UNIT 4C
LIVE UNIT 3 -> UNIT 4 INTEGRATION TEST

PURPOSE
-------
Prove the complete read-only runtime path:

WEEX MARKET DATA
    ->
NORMALIZED CANDLES
    ->
EMA19 / EMA50 / EMA200
    ->
UNIT 3 OUTPUT
    ->
UNIT 4B BRIDGE
    ->
UNIT 4 REGIME ENGINE
    ->
DIRECTION / REGIME / SIGNED MOVEMENT

SAFETY
------
GET ONLY
ZERO WEEX POST
ZERO DEMO ORDER
ZERO REAL ORDER
ZERO EXCHANGE MUTATION
NO ORDER PAYLOAD
NO POSITION SIZING
NO TP
NO SL
NO BACKUP EXECUTION

IMPORTANT
---------
This unit makes read-only public WEEX market requests.

It does NOT send authenticated trading requests.

It does NOT create a trading decision.

It does NOT submit any order.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from typing import Any
import json
import urllib.parse
import urllib.request


# ============================================================
# DECIMAL PRECISION
# ============================================================

getcontext().prec = 40


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "WEEX_PARALLEL_BOT"

APP_VERSION = "0.4.2"

RECONSTRUCTION_UNIT = (
    "UNIT_4C_LIVE_UNIT3_TO_UNIT4_INTEGRATION"
)


# ============================================================
# WEEX READ-ONLY MARKET CONFIGURATION
# ============================================================

WEEX_API_BASE = (
    "https://api-contract.weex.com"
)

WEEX_PUBLIC_SYMBOL = (
    "cmt_btcusdt"
)

WEEX_CANDLE_PERIOD = (
    "1m"
)

WEEX_CANDLE_LIMIT = 250

WEEX_REQUEST_TIMEOUT_SECONDS = 15


# ============================================================
# UNIT 3 EMA CONFIGURATION
# ============================================================

EMA_FAST_PERIOD = 19

EMA_MEDIUM_PERIOD = 50

EMA_SLOW_PERIOD = 200

MINIMUM_REQUIRED_CANDLES = (
    EMA_SLOW_PERIOD + 1
)


# ============================================================
# UNIT 4 CONFIGURATION
# ============================================================

REGIME_STRONG_EMA_SEPARATION_PERCENT = Decimal(
    "0.05"
)

REGIME_BREAKOUT_MOVE_PERCENT = Decimal(
    "0.60"
)

REGIME_MODE_CONFIRMATIONS_REQUIRED = 3

REGIME_VALID_MODES = (
    "SCALP",
    "STRUCTURE",
    "BREAKOUT",
)


# ============================================================
# EXECUTION FIREBREAK
# ============================================================

ALLOW_HTTP_POST = False

ALLOW_DEMO_ORDER = False

ALLOW_REAL_ORDER = False

ALLOW_EXCHANGE_MUTATION = False

ALLOW_ORDER_PAYLOAD = False

ALLOW_TRADING_DECISION = False


# ============================================================
# DECIMAL HELPERS
# ============================================================

def D(
    value: Any,
) -> Decimal:

    if isinstance(
        value,
        Decimal,
    ):
        return value

    return Decimal(
        str(value)
    )


def decimal_to_string(
    value: Any,
) -> str:

    value = D(
        value
    )

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

    return text


# ============================================================
# LOGGING
# ============================================================

def utc_now_iso() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def log(
    message: str,
) -> None:

    print(
        f"{utc_now_iso()} {message}",
        flush=True,
    )


def separator() -> None:

    print(
        "-" * 80,
        flush=True,
    )


# ============================================================
# ASSERTION
# ============================================================

def require(
    condition: bool,
    message: str,
) -> None:

    if not condition:

        raise RuntimeError(
            message
        )


# ============================================================
# DATA CONTRACTS
# ============================================================

@dataclass(
    frozen=True
)
class Candle:

    timestamp: int

    open: Decimal

    high: Decimal

    low: Decimal

    close: Decimal

    volume: Decimal


@dataclass(
    frozen=True
)
class Unit3Output:

    latest_close: Decimal

    ema19: Decimal

    ema50: Decimal

    ema200: Decimal

    ema19_50_separation_percent: Decimal


@dataclass(
    frozen=True
)
class Unit4MarketSnapshot:

    close_price: Decimal

    ema19: Decimal

    ema50: Decimal

    ema200: Decimal

    ema19_50_separation_percent: Decimal


@dataclass(
    frozen=True
)
class RegimeResult:

    raw_mode: str

    active_mode: str

    direction: str | None

    ema_separation_percent: Decimal

    short_term_move_percent: Decimal

    pending_mode: str | None

    pending_count: int

    mode_locked: bool

    reason: str


# ============================================================
# READ-ONLY HTTP CLIENT
# ============================================================

class ReadOnlyWeexClient:

    def __init__(
        self,
        base_url: str,
        timeout_seconds: int,
    ) -> None:

        self.base_url = (
            base_url.rstrip("/")
        )

        self.timeout_seconds = (
            timeout_seconds
        )

        self.get_count = 0

        self.post_count = 0


    def get_json(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:

        if not path.startswith("/"):

            raise ValueError(
                "Read-only WEEX path must begin with /."
            )

        query = ""

        if params:

            query = (
                "?"
                + urllib.parse.urlencode(
                    params
                )
            )

        url = (
            self.base_url
            + path
            + query
        )

        request = urllib.request.Request(
            url=url,
            method="GET",
            headers={
                "Accept": "application/json",
                "User-Agent": (
                    "WEEX-PARALLEL-BOT-"
                    "READ-ONLY-UNIT-4C"
                ),
            },
        )

        self.get_count += 1

        with urllib.request.urlopen(
            request,
            timeout=self.timeout_seconds,
        ) as response:

            raw = (
                response
                .read()
                .decode("utf-8")
            )

        return json.loads(
            raw
        )


    def post_json(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:

        self.post_count += 1

        raise RuntimeError(
            "UNIT 4C FIREBREAK: HTTP POST DISABLED."
        )


# ============================================================
# CANDLE RESPONSE EXTRACTION
# ============================================================

def extract_rows(
    payload: Any,
) -> list[Any]:

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

            if isinstance(
                value,
                dict,
            ):

                for nested_key in (
                    "data",
                    "rows",
                    "list",
                ):

                    nested = value.get(
                        nested_key
                    )

                    if isinstance(
                        nested,
                        list,
                    ):

                        return nested

    raise ValueError(
        "Unable to locate candle rows in WEEX response."
    )


# ============================================================
# CANDLE NORMALIZATION
# ============================================================

def normalize_candle_row(
    row: Any,
) -> Candle:

    if isinstance(
        row,
        dict,
    ):

        timestamp = (
            row.get("timestamp")
            or row.get("time")
            or row.get("ts")
        )

        open_price = (
            row.get("open")
            or row.get("o")
        )

        high_price = (
            row.get("high")
            or row.get("h")
        )

        low_price = (
            row.get("low")
            or row.get("l")
        )

        close_price = (
            row.get("close")
            or row.get("c")
        )

        volume = (
            row.get("volume")
            or row.get("vol")
            or row.get("v")
            or "0"
        )

    elif isinstance(
        row,
        (list, tuple),
    ):

        if len(row) < 5:

            raise ValueError(
                "Malformed candle row: fewer than 5 fields."
            )

        timestamp = row[0]

        open_price = row[1]

        high_price = row[2]

        low_price = row[3]

        close_price = row[4]

        volume = (
            row[5]
            if len(row) > 5
            else "0"
        )

    else:

        raise ValueError(
            "Unsupported candle row type."
        )

    if timestamp is None:

        raise ValueError(
            "Candle timestamp missing."
        )

    candle = Candle(

        timestamp=int(
            D(timestamp)
        ),

        open=D(
            open_price
        ),

        high=D(
            high_price
        ),

        low=D(
            low_price
        ),

        close=D(
            close_price
        ),

        volume=D(
            volume
        ),

    )

    if candle.open <= 0:

        raise ValueError(
            "Invalid candle open."
        )

    if candle.high <= 0:

        raise ValueError(
            "Invalid candle high."
        )

    if candle.low <= 0:

        raise ValueError(
            "Invalid candle low."
        )

    if candle.close <= 0:

        raise ValueError(
            "Invalid candle close."
        )

    if candle.high < candle.low:

        raise ValueError(
            "Candle high below candle low."
        )

    return candle


def normalize_candles(
    rows: list[Any],
) -> list[Candle]:

    candles = []

    for row in rows:

        try:

            candle = (
                normalize_candle_row(
                    row
                )
            )

            candles.append(
                candle
            )

        except Exception:

            continue

    if not candles:

        raise RuntimeError(
            "No valid candles returned."
        )

    # --------------------------------------------------------
    # Sort oldest -> newest.
    # --------------------------------------------------------

    candles.sort(
        key=lambda candle: candle.timestamp
    )

    # --------------------------------------------------------
    # Remove duplicate timestamps.
    # --------------------------------------------------------

    unique = {}

    for candle in candles:

        unique[
            candle.timestamp
        ] = candle

    candles = list(
        unique.values()
    )

    candles.sort(
        key=lambda candle: candle.timestamp
    )

    return candles


# ============================================================
# READ LIVE CANDLES
# ============================================================

def load_live_candles(
    client: ReadOnlyWeexClient,
) -> tuple[
    list[Candle],
    str,
]:

    attempts = [

        (
            "/capi/v2/market/candles",
            {
                "symbol": WEEX_PUBLIC_SYMBOL,
                "period": WEEX_CANDLE_PERIOD,
                "limit": WEEX_CANDLE_LIMIT,
            },
        ),

        (
            "/capi/v2/market/candles",
            {
                "symbol": WEEX_PUBLIC_SYMBOL,
                "granularity": WEEX_CANDLE_PERIOD,
                "limit": WEEX_CANDLE_LIMIT,
            },
        ),

    ]

    errors = []

    for (
        path,
        params,
    ) in attempts:

        try:

            payload = (
                client.get_json(
                    path,
                    params,
                )
            )

            rows = (
                extract_rows(
                    payload
                )
            )

            candles = (
                normalize_candles(
                    rows
                )
            )

            if (
                len(candles)
                < MINIMUM_REQUIRED_CANDLES
            ):

                raise RuntimeError(
                    "Insufficient candle history: "
                    + str(
                        len(candles)
                    )
                )

            return (
                candles,
                path,
            )

        except Exception as exc:

            errors.append(
                repr(
                    exc
                )
            )

    raise RuntimeError(
        "Unable to load live WEEX candles. "
        + " | ".join(
            errors
        )
    )


# ============================================================
# EMA
# ============================================================

def calculate_ema(
    values: list[Decimal],
    period: int,
) -> Decimal:

    if period <= 0:

        raise ValueError(
            "EMA period must be positive."
        )

    if len(values) < period:

        raise ValueError(
            "Insufficient values for EMA"
            + str(period)
            + "."
        )

    multiplier = (
        Decimal("2")
        / Decimal(
            period + 1
        )
    )

    seed_values = (
        values[:period]
    )

    ema = (
        sum(
            seed_values
        )
        / Decimal(
            period
        )
    )

    for value in values[
        period:
    ]:

        ema = (
            (
                value
                - ema
            )
            * multiplier
            + ema
        )

    return ema


# ============================================================
# PERCENT SEPARATION
# ============================================================

def percent_separation(
    a: Decimal,
    b: Decimal,
) -> Decimal:

    a = D(
        a
    )

    b = D(
        b
    )

    if b == 0:

        raise ValueError(
            "Cannot calculate separation against zero."
        )

    return (
        abs(
            a - b
        )
        / abs(
            b
        )
        * Decimal("100")
    )


# ============================================================
# UNIT 3 SNAPSHOT BUILDER
# ============================================================

def build_unit3_output(
    candles: list[Candle],
) -> Unit3Output:

    if (
        len(candles)
        < EMA_SLOW_PERIOD
    ):

        raise ValueError(
            "Insufficient candles for Unit 3 snapshot."
        )

    closes = [
        candle.close
        for candle in candles
    ]

    ema19 = (
        calculate_ema(
            closes,
            EMA_FAST_PERIOD,
        )
    )

    ema50 = (
        calculate_ema(
            closes,
            EMA_MEDIUM_PERIOD,
        )
    )

    ema200 = (
        calculate_ema(
            closes,
            EMA_SLOW_PERIOD,
        )
    )

    separation = (
        percent_separation(
            ema19,
            ema50,
        )
    )

    return Unit3Output(

        latest_close=(
            candles[-1].close
        ),

        ema19=ema19,

        ema50=ema50,

        ema200=ema200,

        ema19_50_separation_percent=(
            separation
        ),

    )


# ============================================================
# UNIT 3 OUTPUT VALIDATION
# ============================================================

def validate_unit3_output(
    output: Unit3Output,
) -> None:

    if output.latest_close <= 0:

        raise ValueError(
            "Invalid Unit 3 latest close."
        )

    if output.ema19 <= 0:

        raise ValueError(
            "Invalid Unit 3 EMA19."
        )

    if output.ema50 <= 0:

        raise ValueError(
            "Invalid Unit 3 EMA50."
        )

    if output.ema200 <= 0:

        raise ValueError(
            "Invalid Unit 3 EMA200."
        )

    if (
        output.ema19_50_separation_percent
        < 0
    ):

        raise ValueError(
            "Invalid Unit 3 EMA separation."
        )


# ============================================================
# UNIT 4 INPUT VALIDATION
# ============================================================

def validate_unit4_snapshot(
    snapshot: Unit4MarketSnapshot,
) -> None:

    if snapshot.close_price <= 0:

        raise ValueError(
            "Invalid Unit 4 close price."
        )

    if snapshot.ema19 <= 0:

        raise ValueError(
            "Invalid Unit 4 EMA19."
        )

    if snapshot.ema50 <= 0:

        raise ValueError(
            "Invalid Unit 4 EMA50."
        )

    if snapshot.ema200 <= 0:

        raise ValueError(
            "Invalid Unit 4 EMA200."
        )

    if (
        snapshot.ema19_50_separation_percent
        < 0
    ):

        raise ValueError(
            "Invalid Unit 4 EMA separation."
        )


# ============================================================
# UNIT 4B BRIDGE
# ============================================================

def unit4b_bridge(
    output: Unit3Output,
) -> Unit4MarketSnapshot:

    validate_unit3_output(
        output
    )

    snapshot = Unit4MarketSnapshot(

        close_price=(
            output.latest_close
        ),

        ema19=(
            output.ema19
        ),

        ema50=(
            output.ema50
        ),

        ema200=(
            output.ema200
        ),

        ema19_50_separation_percent=(
            output
            .ema19_50_separation_percent
        ),

    )

    validate_unit4_snapshot(
        snapshot
    )

    return snapshot


# ============================================================
# UNIT 4 REGIME ENGINE
# ============================================================

class RegimeEngine:

    def __init__(
        self,
    ) -> None:

        self.active_mode: str | None = None

        self.pending_mode: str | None = None

        self.pending_count = 0

        self.mode_locked = False

        self.reference_price: Decimal | None = None

        self.last_reason = (
            "NOT_EVALUATED"
        )


    @staticmethod
    def direction_from_ema(
        snapshot: Unit4MarketSnapshot,
    ) -> str | None:

        validate_unit4_snapshot(
            snapshot
        )

        if (
            snapshot.ema19
            > snapshot.ema50
            > snapshot.ema200
        ):

            return "LONG"

        if (
            snapshot.ema19
            < snapshot.ema50
            < snapshot.ema200
        ):

            return "SHORT"

        return None


    @staticmethod
    def move_percent(
        current: Decimal,
        reference: Decimal | None,
    ) -> Decimal:

        current = D(
            current
        )

        if current <= 0:

            raise ValueError(
                "Current price must be positive."
            )

        if reference is None:

            return Decimal(
                "0"
            )

        reference = D(
            reference
        )

        if reference <= 0:

            raise ValueError(
                "Reference price must be positive."
            )

        return (
            (
                current
                - reference
            )
            / reference
            * Decimal("100")
        )


    @staticmethod
    def classify(
        direction: str | None,
        ema_separation_percent: Decimal,
        movement_percent: Decimal,
    ) -> tuple[str, str]:

        ema_separation_percent = D(
            ema_separation_percent
        )

        movement_percent = D(
            movement_percent
        )

        if (
            direction == "LONG"
            and movement_percent
            >= REGIME_BREAKOUT_MOVE_PERCENT
        ):

            return (
                "BREAKOUT",
                "LONG_BREAKOUT_MOVE_CONFIRMED",
            )

        if (
            direction == "SHORT"
            and movement_percent
            <= -REGIME_BREAKOUT_MOVE_PERCENT
        ):

            return (
                "BREAKOUT",
                "SHORT_BREAKOUT_MOVE_CONFIRMED",
            )

        if (
            direction in (
                "LONG",
                "SHORT",
            )
            and ema_separation_percent
            >= REGIME_STRONG_EMA_SEPARATION_PERCENT
        ):

            return (
                "STRUCTURE",
                "STRONG_EMA_DIRECTION_CONFIRMED",
            )

        return (
            "SCALP",
            "NO_CONFIRMED_STRUCTURE_OR_BREAKOUT_CONDITION",
        )


    def update_mode(
        self,
        raw_mode: str,
        reason: str,
        *,
        trade_active: bool = False,
    ) -> str:

        if raw_mode not in REGIME_VALID_MODES:

            raise ValueError(
                "Invalid regime mode."
            )

        if trade_active:

            self.mode_locked = True

            if self.active_mode is None:

                self.active_mode = (
                    raw_mode
                )

            self.pending_mode = None

            self.pending_count = 0

            self.last_reason = (
                "ACTIVE_TRADE_MODE_LOCK"
            )

            return self.active_mode

        self.mode_locked = False

        if self.active_mode is None:

            self.active_mode = (
                raw_mode
            )

            self.pending_mode = None

            self.pending_count = 0

            self.last_reason = (
                "INITIAL_MODE_SELECTED:"
                + reason
            )

            return self.active_mode

        if raw_mode == self.active_mode:

            self.pending_mode = None

            self.pending_count = 0

            self.last_reason = (
                "ACTIVE_MODE_CONFIRMED:"
                + reason
            )

            return self.active_mode

        if self.pending_mode != raw_mode:

            self.pending_mode = (
                raw_mode
            )

            self.pending_count = 1

            self.last_reason = (
                "NEW_MODE_PENDING:"
                + reason
            )

            return self.active_mode

        self.pending_count += 1

        if (
            self.pending_count
            >= REGIME_MODE_CONFIRMATIONS_REQUIRED
        ):

            previous_mode = (
                self.active_mode
            )

            self.active_mode = (
                raw_mode
            )

            self.pending_mode = None

            self.pending_count = 0

            self.last_reason = (
                "THREE_CONFIRMATION_TRANSITION:"
                + str(previous_mode)
                + "_TO_"
                + raw_mode
            )

            return self.active_mode

        self.last_reason = (
            "MODE_CONFIRMATION_PENDING:"
            + reason
        )

        return self.active_mode


    def evaluate(
        self,
        snapshot: Unit4MarketSnapshot,
        *,
        trade_active: bool = False,
    ) -> RegimeResult:

        direction = (
            self.direction_from_ema(
                snapshot
            )
        )

        movement = (
            self.move_percent(
                snapshot.close_price,
                self.reference_price,
            )
        )

        (
            raw_mode,
            classifier_reason,
        ) = self.classify(
            direction,
            snapshot.ema19_50_separation_percent,
            movement,
        )

        active_mode = (
            self.update_mode(
                raw_mode,
                classifier_reason,
                trade_active=trade_active,
            )
        )

        self.reference_price = (
            snapshot.close_price
        )

        return RegimeResult(

            raw_mode=raw_mode,

            active_mode=active_mode,

            direction=direction,

            ema_separation_percent=(
                snapshot
                .ema19_50_separation_percent
            ),

            short_term_move_percent=(
                movement
            ),

            pending_mode=(
                self.pending_mode
            ),

            pending_count=(
                self.pending_count
            ),

            mode_locked=(
                self.mode_locked
            ),

            reason=(
                self.last_reason
            ),

        )


# ============================================================
# LOCAL SIGNED-MOVEMENT GUARD TEST
# ============================================================

def run_signed_movement_guard() -> None:

    require(
        RegimeEngine.move_percent(
            D("101"),
            D("100"),
        )
        == D("1"),
        (
            "UNIT 4C positive signed "
            "movement guard failed."
        ),
    )

    require(
        RegimeEngine.move_percent(
            D("99"),
            D("100"),
        )
        == D("-1"),
        (
            "UNIT 4C negative signed "
            "movement guard failed."
        ),
    )

    require(
        RegimeEngine.classify(
            "LONG",
            D("0.01"),
            D("0.60"),
        )[0]
        == "BREAKOUT",
        (
            "UNIT 4C LONG breakout "
            "guard failed."
        ),
    )

    require(
        RegimeEngine.classify(
            "SHORT",
            D("0.01"),
            D("-0.60"),
        )[0]
        == "BREAKOUT",
        (
            "UNIT 4C SHORT breakout "
            "guard failed."
        ),
    )

    log(
        "PASS: UNIT 4C SIGNED MOVEMENT GUARD"
    )


# ============================================================
# FIREBREAK
# ============================================================

def validate_firebreak(
    client: ReadOnlyWeexClient,
) -> None:

    require(
        ALLOW_HTTP_POST is False,
        "HTTP POST firebreak failed.",
    )

    require(
        ALLOW_DEMO_ORDER is False,
        "Demo-order firebreak failed.",
    )

    require(
        ALLOW_REAL_ORDER is False,
        "Real-order firebreak failed.",
    )

    require(
        ALLOW_EXCHANGE_MUTATION is False,
        "Exchange mutation firebreak failed.",
    )

    require(
        ALLOW_ORDER_PAYLOAD is False,
        "Order payload firebreak failed.",
    )

    require(
        ALLOW_TRADING_DECISION is False,
        "Trading decision firebreak failed.",
    )

    require(
        client.post_count == 0,
        (
            "Unexpected HTTP POST "
            "attempt detected."
        ),
    )


# ============================================================
# LIVE UNIT 4C TEST
# ============================================================

def run_unit_4c_live_test() -> bool:

    separator()

    log(
        "RECONSTRUCTION UNIT 4C LIVE TEST START"
    )

    separator()

    run_signed_movement_guard()

    # --------------------------------------------------------
    # CREATE READ-ONLY CLIENT
    # --------------------------------------------------------

    client = ReadOnlyWeexClient(

        base_url=(
            WEEX_API_BASE
        ),

        timeout_seconds=(
            WEEX_REQUEST_TIMEOUT_SECONDS
        ),

    )

    # --------------------------------------------------------
    # LIVE CANDLE READ
    # --------------------------------------------------------

    separator()

    log(
        "UNIT 4C LIVE WEEX CANDLE READ START"
    )

    (
        candles,
        candle_source,
    ) = load_live_candles(
        client
    )

    require(
        len(candles)
        >= MINIMUM_REQUIRED_CANDLES,
        (
            "UNIT 4C insufficient "
            "live candle history."
        ),
    )

    log(
        "PASS: UNIT 4C LIVE CANDLE READ"
    )

    log(
        "UNIT 4C CANDLE SOURCE = "
        + candle_source
    )

    log(
        "UNIT 4C VALID CANDLE COUNT = "
        + str(
            len(candles)
        )
    )

    log(
        "UNIT 4C PREVIOUS CANDLE TIMESTAMP = "
        + str(
            candles[-2].timestamp
        )
    )

    log(
        "UNIT 4C LATEST CANDLE TIMESTAMP = "
        + str(
            candles[-1].timestamp
        )
    )

    log(
        "UNIT 4C PREVIOUS CLOSE = "
        + decimal_to_string(
            candles[-2].close
        )
    )

    log(
        "UNIT 4C LATEST CLOSE = "
        + decimal_to_string(
            candles[-1].close
        )
    )

    # --------------------------------------------------------
    # BUILD TWO CONSECUTIVE UNIT 3 SNAPSHOTS
    #
    # Previous snapshot excludes newest candle.
    # Current snapshot includes newest candle.
    # --------------------------------------------------------

    previous_unit3 = (
        build_unit3_output(
            candles[:-1]
        )
    )

    current_unit3 = (
        build_unit3_output(
            candles
        )
    )

    validate_unit3_output(
        previous_unit3
    )

    validate_unit3_output(
        current_unit3
    )

    separator()

    log(
        "PASS: UNIT 4C LIVE UNIT 3 SNAPSHOTS"
    )

    log(
        "CURRENT EMA19 = "
        + decimal_to_string(
            current_unit3.ema19
        )
    )

    log(
        "CURRENT EMA50 = "
        + decimal_to_string(
            current_unit3.ema50
        )
    )

    log(
        "CURRENT EMA200 = "
        + decimal_to_string(
            current_unit3.ema200
        )
    )

    log(
        "CURRENT EMA19/50 SEPARATION % = "
        + decimal_to_string(
            current_unit3
            .ema19_50_separation_percent
        )
    )

    # --------------------------------------------------------
    # UNIT 4B BRIDGE
    # --------------------------------------------------------

    previous_snapshot = (
        unit4b_bridge(
            previous_unit3
        )
    )

    current_snapshot = (
        unit4b_bridge(
            current_unit3
        )
    )

    require(
        previous_snapshot.close_price
        == previous_unit3.latest_close,
        (
            "UNIT 4C previous bridge "
            "changed close price."
        ),
    )

    require(
        current_snapshot.close_price
        == current_unit3.latest_close,
        (
            "UNIT 4C current bridge "
            "changed close price."
        ),
    )

    require(
        current_snapshot.ema19
        == current_unit3.ema19,
        (
            "UNIT 4C bridge changed EMA19."
        ),
    )

    require(
        current_snapshot.ema50
        == current_unit3.ema50,
        (
            "UNIT 4C bridge changed EMA50."
        ),
    )

    require(
        current_snapshot.ema200
        == current_unit3.ema200,
        (
            "UNIT 4C bridge changed EMA200."
        ),
    )

    log(
        "PASS: UNIT 4C LIVE UNIT 4B BRIDGE"
    )

    # --------------------------------------------------------
    # UNIT 4 LIVE EVALUATION
    #
    # First evaluation establishes previous close as reference.
    # Second evaluation therefore produces signed movement
    # from previous close -> latest close.
    # --------------------------------------------------------

    engine = RegimeEngine()

    previous_result = (
        engine.evaluate(
            previous_snapshot
        )
    )

    current_result = (
        engine.evaluate(
            current_snapshot
        )
    )

    # --------------------------------------------------------
    # INDEPENDENT SIGNED MOVEMENT CALCULATION
    #
    # This proves the engine result matches the expected
    # previous-close -> current-close signed calculation.
    # --------------------------------------------------------

    expected_movement = (
        (
            current_unit3.latest_close
            - previous_unit3.latest_close
        )
        / previous_unit3.latest_close
        * Decimal("100")
    )

    require(
        current_result.short_term_move_percent
        == expected_movement,
        (
            "UNIT 4C live signed movement "
            "does not match independent calculation."
        ),
    )

    separator()

    log(
        "PASS: UNIT 4C LIVE REGIME EVALUATION"
    )

    log(
        "UNIT 4C PREVIOUS RAW MODE = "
        + previous_result.raw_mode
    )

    log(
        "UNIT 4C CURRENT RAW MODE = "
        + current_result.raw_mode
    )

    log(
        "UNIT 4C ACTIVE MODE = "
        + current_result.active_mode
    )

    log(
        "UNIT 4C DIRECTION = "
        + str(
            current_result.direction
        )
    )

    log(
        "UNIT 4C EMA19/50 SEPARATION % = "
        + decimal_to_string(
            current_result
            .ema_separation_percent
        )
    )

    log(
        "UNIT 4C SIGNED SHORT-TERM MOVE % = "
        + decimal_to_string(
            current_result
            .short_term_move_percent
        )
    )

    log(
        "UNIT 4C EXPECTED SIGNED MOVE % = "
        + decimal_to_string(
            expected_movement
        )
    )

    log(
        "UNIT 4C PENDING MODE = "
        + str(
            current_result.pending_mode
        )
    )

    log(
        "UNIT 4C PENDING COUNT = "
        + str(
            current_result.pending_count
        )
    )

    log(
        "UNIT 4C MODE LOCKED = "
        + str(
            current_result.mode_locked
        )
    )

    log(
        "UNIT 4C REASON = "
        + current_result.reason
    )

    # --------------------------------------------------------
    # FIREBREAK
    # --------------------------------------------------------

    separator()

    validate_firebreak(
        client
    )

    log(
        "PASS: UNIT 4C FINAL EXECUTION FIREBREAK"
    )

    log(
        "READ-ONLY HTTP GET COUNT = "
        + str(
            client.get_count
        )
    )

    log(
        "HTTP POST COUNT = "
        + str(
            client.post_count
        )
    )

    log(
        "ZERO WEEX POST = TRUE"
    )

    log(
        "ZERO DEMO ORDER = TRUE"
    )

    log(
        "ZERO REAL ORDER = TRUE"
    )

    log(
        "ZERO EXCHANGE MUTATION = TRUE"
    )

    log(
        "NO ORDER PAYLOAD GENERATED = TRUE"
    )

    log(
        "NO TRADING DECISION GENERATED = TRUE"
    )

    separator()

    log(
        "UNIT 4C LIVE INTEGRATION TESTS = PASS"
    )

    log(
        "RECONSTRUCTION UNIT 4C RESULT = PASS"
    )

    separator()

    return True


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    log(
        f"{APP_NAME} {APP_VERSION}"
    )

    log(
        f"STARTING {RECONSTRUCTION_UNIT}"
    )

    try:

        result = (
            run_unit_4c_live_test()
        )

    except Exception as exc:

        separator()

        log(
            "RECONSTRUCTION UNIT 4C RESULT = FAIL"
        )

        log(
            "ERROR TYPE = "
            + type(
                exc
            ).__name__
        )

        log(
            "ERROR = "
            + repr(
                exc
            )
        )

        separator()

        raise

    if not result:

        raise RuntimeError(
            "Unit 4C live integration test did not pass."
        )


if __name__ == "__main__":

    main()
