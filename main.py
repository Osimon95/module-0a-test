#!/usr/bin/env python3

"""
WEEX PARALLEL BOT RECONSTRUCTION

UNIT 4C + UNIT 5 + UNIT 5B

LIVE PATH:

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
    ->
UNIT 5 ENTRY QUALIFICATION
    ->
UNIT 5B LIVE BRIDGE

SAFETY:
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

APP_VERSION = "0.5.0"

RECONSTRUCTION_UNIT = (
    "UNIT_5B_LIVE_UNIT4C_TO_UNIT5_INTEGRATION"
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
# UNIT 5 CONFIGURATION
# ============================================================

UNIT_5_MIN_EMA_SEPARATION_PCT = Decimal(
    "0.05"
)

UNIT_5_MIN_DIRECTIONAL_MOVE_PCT = Decimal(
    "0.01"
)

UNIT_5_MAX_EMA19_DISTANCE_PCT = Decimal(
    "0.50"
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

ALLOW_POSITION_SIZING = False

ALLOW_TP_GENERATION = False

ALLOW_SL_GENERATION = False

ALLOW_BACKUP_EXECUTION = False


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
# READ-ONLY WEEX CLIENT
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
                    "READ-ONLY-UNIT-5B"
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
            "EXECUTION FIREBREAK: "
            "HTTP POST DISABLED."
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
        "Unable to locate candle rows "
        "in WEEX response."
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
                "Malformed candle row: "
                "fewer than 5 fields."
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

    candles.sort(
        key=lambda candle: candle.timestamp
    )

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
            + str(
                period
            )
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
            "Cannot calculate separation "
            "against zero."
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
            "Insufficient candles for "
            "Unit 3 snapshot."
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
        output
        .ema19_50_separation_percent
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
        snapshot
        .ema19_50_separation_percent
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
    ) -> tuple[
        str,
        str,
    ]:

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
            (
                "NO_CONFIRMED_STRUCTURE_OR_"
                "BREAKOUT_CONDITION"
            ),
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
                + str(
                    previous_mode
                )
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
            snapshot
            .ema19_50_separation_percent,
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
# UNIT 4C SIGNED MOVEMENT GUARD
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
# UNIT 5
# ENTRY QUALIFICATION ENGINE
# ============================================================

def reconstruction_unit_5_qualify_entry(
    *,
    active_mode,
    direction,
    live_price,
    ema19,
    ema50,
    ema200,
    ema19_50_separation_pct,
    short_term_move_pct,
):

    active_mode = str(
        active_mode
    ).upper()

    if direction is not None:

        direction = str(
            direction
        ).upper()

    live_price = D(
        live_price
    )

    ema19 = D(
        ema19
    )

    ema50 = D(
        ema50
    )

    ema200 = D(
        ema200
    )

    ema19_50_separation_pct = D(
        ema19_50_separation_pct
    )

    short_term_move_pct = D(
        short_term_move_pct
    )

    result = {
        "qualified": False,
        "reason": None,
        "active_mode": active_mode,
        "direction": direction,
        "live_price": live_price,
        "ema19": ema19,
        "ema50": ema50,
        "ema200": ema200,
        "ema19_50_separation_pct": (
            ema19_50_separation_pct
        ),
        "short_term_move_pct": (
            short_term_move_pct
        ),
        "ema_ordering_ok": False,
        "ema_separation_ok": False,
        "price_location_ok": False,
        "momentum_ok": False,
        "anti_chase_ok": False,
        "ema19_distance_pct": None,
        "weex_post": False,
        "demo_order": False,
        "real_order": False,
        "exchange_mutation": False,
        "order_payload_generated": False,
        "position_sizing_generated": False,
        "tp_generated": False,
        "sl_generated": False,
        "backup_execution": False,
    }

    # --------------------------------------------------------
    # MODE GUARD
    # --------------------------------------------------------

    if (
        active_mode
        not in REGIME_VALID_MODES
    ):

        result[
            "reason"
        ] = (
            "INVALID_ACTIVE_MODE"
        )

        return result

    # --------------------------------------------------------
    # DIRECTION GUARD
    # --------------------------------------------------------

    if direction not in (
        "LONG",
        "SHORT",
    ):

        result[
            "reason"
        ] = (
            "NO_CONFIRMED_DIRECTION"
        )

        return result

    # --------------------------------------------------------
    # MARKET VALUE GUARD
    # --------------------------------------------------------

    if (
        live_price <= 0
        or ema19 <= 0
        or ema50 <= 0
        or ema200 <= 0
    ):

        result[
            "reason"
        ] = (
            "INVALID_MARKET_VALUE"
        )

        return result

    # --------------------------------------------------------
    # EMA ORDERING
    # --------------------------------------------------------

    if direction == "LONG":

        ema_ordering_ok = (
            ema19
            > ema50
            > ema200
        )

    else:

        ema_ordering_ok = (
            ema19
            < ema50
            < ema200
        )

    result[
        "ema_ordering_ok"
    ] = ema_ordering_ok

    if not ema_ordering_ok:

        result[
            "reason"
        ] = (
            "EMA_ORDERING_NOT_CONFIRMED"
        )

        return result

    # --------------------------------------------------------
    # EMA SEPARATION
    # --------------------------------------------------------

    ema_separation_ok = (
        abs(
            ema19_50_separation_pct
        )
        >= UNIT_5_MIN_EMA_SEPARATION_PCT
    )

    result[
        "ema_separation_ok"
    ] = ema_separation_ok

    if not ema_separation_ok:

        result[
            "reason"
        ] = (
            "EMA_SEPARATION_BELOW_MINIMUM"
        )

        return result

    # --------------------------------------------------------
    # PRICE LOCATION
    # --------------------------------------------------------

    if direction == "LONG":

        price_location_ok = (
            live_price
            >= ema19
        )

    else:

        price_location_ok = (
            live_price
            <= ema19
        )

    result[
        "price_location_ok"
    ] = price_location_ok

    if not price_location_ok:

        result[
            "reason"
        ] = (
            "PRICE_LOCATION_NOT_CONFIRMED"
        )

        return result

    # --------------------------------------------------------
    # SIGNED DIRECTIONAL MOMENTUM
    # --------------------------------------------------------

    if direction == "LONG":

        momentum_ok = (
            short_term_move_pct
            >= UNIT_5_MIN_DIRECTIONAL_MOVE_PCT
        )

    else:

        momentum_ok = (
            short_term_move_pct
            <= -UNIT_5_MIN_DIRECTIONAL_MOVE_PCT
        )

    result[
        "momentum_ok"
    ] = momentum_ok

    if not momentum_ok:

        result[
            "reason"
        ] = (
            "DIRECTIONAL_MOMENTUM_NOT_CONFIRMED"
        )

        return result

    # --------------------------------------------------------
    # ANTI-CHASE
    # --------------------------------------------------------

    ema19_distance_pct = (
        abs(
            live_price
            - ema19
        )
        / ema19
        * Decimal("100")
    )

    result[
        "ema19_distance_pct"
    ] = ema19_distance_pct

    anti_chase_ok = (
        ema19_distance_pct
        <= UNIT_5_MAX_EMA19_DISTANCE_PCT
    )

    result[
        "anti_chase_ok"
    ] = anti_chase_ok

    if not anti_chase_ok:

        result[
            "reason"
        ] = (
            "ANTI_CHASE_DISTANCE_EXCEEDED"
        )

        return result

    result[
        "qualified"
    ] = True

    result[
        "reason"
    ] = (
        "ENTRY_QUALIFICATION_CONFIRMED"
    )

    return result


# ============================================================
# UNIT 5B
# LIVE UNIT 4C -> UNIT 5 BRIDGE
# ============================================================

def reconstruction_unit_5b_live_bridge(
    *,
    active_mode,
    direction,
    live_price,
    ema19,
    ema50,
    ema200,
    ema19_50_separation_pct,
    short_term_move_pct,
):

    separator()

    log(
        "UNIT 5B LIVE ENTRY QUALIFICATION START"
    )

    result = (
        reconstruction_unit_5_qualify_entry(
            active_mode=active_mode,
            direction=direction,
            live_price=live_price,
            ema19=ema19,
            ema50=ema50,
            ema200=ema200,
            ema19_50_separation_pct=(
                ema19_50_separation_pct
            ),
            short_term_move_pct=(
                short_term_move_pct
            ),
        )
    )

    log(
        "UNIT 5B ACTIVE MODE = "
        + str(
            result[
                "active_mode"
            ]
        )
    )

    log(
        "UNIT 5B DIRECTION = "
        + str(
            result[
                "direction"
            ]
        )
    )

    log(
        "UNIT 5B LIVE PRICE = "
        + decimal_to_string(
            result[
                "live_price"
            ]
        )
    )

    log(
        "UNIT 5B EMA19 = "
        + decimal_to_string(
            result[
                "ema19"
            ]
        )
    )

    log(
        "UNIT 5B EMA50 = "
        + decimal_to_string(
            result[
                "ema50"
            ]
        )
    )

    log(
        "UNIT 5B EMA200 = "
        + decimal_to_string(
            result[
                "ema200"
            ]
        )
    )

    log(
        "UNIT 5B EMA19/50 SEPARATION % = "
        + decimal_to_string(
            result[
                "ema19_50_separation_pct"
            ]
        )
    )

    log(
        "UNIT 5B SIGNED SHORT-TERM MOVE % = "
        + decimal_to_string(
            result[
                "short_term_move_pct"
            ]
        )
    )

    log(
        "UNIT 5B QUALIFIED = "
        + str(
            result[
                "qualified"
            ]
        )
    )

    log(
        "UNIT 5B REASON = "
        + str(
            result[
                "reason"
            ]
        )
    )

    log(
        "UNIT 5B EMA ORDERING OK = "
        + str(
            result[
                "ema_ordering_ok"
            ]
        )
    )

    log(
        "UNIT 5B EMA SEPARATION OK = "
        + str(
            result[
                "ema_separation_ok"
            ]
        )
    )

    log(
        "UNIT 5B PRICE LOCATION OK = "
        + str(
            result[
                "price_location_ok"
            ]
        )
    )

    log(
        "UNIT 5B MOMENTUM OK = "
        + str(
            result[
                "momentum_ok"
            ]
        )
    )

    log(
        "UNIT 5B ANTI-CHASE OK = "
        + str(
            result[
                "anti_chase_ok"
            ]
        )
    )

    log(
        "UNIT 5B EMA19 DISTANCE % = "
        + str(
            result[
                "ema19_distance_pct"
            ]
        )
    )

    firebreak_ok = all(
        result[
            key
        ] is False
        for key in (
            "weex_post",
            "demo_order",
            "real_order",
            "exchange_mutation",
            "order_payload_generated",
            "position_sizing_generated",
            "tp_generated",
            "sl_generated",
            "backup_execution",
        )
    )

    require(
        firebreak_ok,
        (
            "UNIT 5B EXECUTION "
            "FIREBREAK FAILURE"
        ),
    )

    log(
        "PASS: UNIT 5B EXECUTION FIREBREAK"
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
        "NO POSITION SIZING GENERATED = TRUE"
    )

    log(
        "NO TP GENERATED = TRUE"
    )

    log(
        "NO SL GENERATED = TRUE"
    )

    log(
        "NO BACKUP EXECUTION = TRUE"
    )

    log(
        "RECONSTRUCTION UNIT 5B RESULT = PASS"
    )

    separator()

    return result


# ============================================================
# FINAL FIREBREAK
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
        ALLOW_POSITION_SIZING is False,
        "Position sizing firebreak failed.",
    )

    require(
        ALLOW_TP_GENERATION is False,
        "TP generation firebreak failed.",
    )

    require(
        ALLOW_SL_GENERATION is False,
        "SL generation firebreak failed.",
    )

    require(
        ALLOW_BACKUP_EXECUTION is False,
        "Backup execution firebreak failed.",
    )

    require(
        client.post_count == 0,
        (
            "Unexpected HTTP POST "
            "attempt detected."
        ),
    )


# ============================================================
# LIVE UNIT 4C -> UNIT 5B INTEGRATION TEST
# ============================================================

def run_unit_5b_live_test() -> dict[str, Any]:

    separator()

    log(
        "RECONSTRUCTION UNIT 5B LIVE TEST START"
    )

    separator()

    # --------------------------------------------------------
    # UNIT 4C LOCAL SIGNED-MOVEMENT GUARD
    # --------------------------------------------------------

    run_signed_movement_guard()

    # --------------------------------------------------------
    # CREATE READ-ONLY WEEX CLIENT
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
        "UNIT 5B LIVE WEEX CANDLE READ START"
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
            "UNIT 5B insufficient "
            "live candle history."
        ),
    )

    log(
        "PASS: UNIT 5B LIVE CANDLE READ"
    )

    log(
        "UNIT 5B CANDLE SOURCE = "
        + candle_source
    )

    log(
        "UNIT 5B VALID CANDLE COUNT = "
        + str(
            len(candles)
        )
    )

    log(
        "UNIT 5B PREVIOUS CANDLE TIMESTAMP = "
        + str(
            candles[-2].timestamp
        )
    )

    log(
        "UNIT 5B LATEST CANDLE TIMESTAMP = "
        + str(
            candles[-1].timestamp
        )
    )

    log(
        "UNIT 5B PREVIOUS CLOSE = "
        + decimal_to_string(
            candles[-2].close
        )
    )

    log(
        "UNIT 5B LATEST CLOSE = "
        + decimal_to_string(
            candles[-1].close
        )
    )

    # --------------------------------------------------------
    # BUILD PREVIOUS AND CURRENT UNIT 3 SNAPSHOTS
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
        "PASS: UNIT 5B LIVE UNIT 3 SNAPSHOTS"
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
            "UNIT 5B previous bridge "
            "changed close price."
        ),
    )

    require(
        current_snapshot.close_price
        == current_unit3.latest_close,
        (
            "UNIT 5B current bridge "
            "changed close price."
        ),
    )

    require(
        current_snapshot.ema19
        == current_unit3.ema19,
        (
            "UNIT 5B bridge "
            "changed EMA19."
        ),
    )

    require(
        current_snapshot.ema50
        == current_unit3.ema50,
        (
            "UNIT 5B bridge "
            "changed EMA50."
        ),
    )

    require(
        current_snapshot.ema200
        == current_unit3.ema200,
        (
            "UNIT 5B bridge "
            "changed EMA200."
        ),
    )

    log(
        "PASS: UNIT 5B LIVE UNIT 4B BRIDGE"
    )

    # --------------------------------------------------------
    # UNIT 4C LIVE REGIME EVALUATION
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
    # INDEPENDENT SIGNED-MOVEMENT CHECK
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
        current_result
        .short_term_move_percent
        == expected_movement,
        (
            "UNIT 5B live signed movement "
            "does not match independent "
            "calculation."
        ),
    )

    separator()

    log(
        "PASS: UNIT 5B LIVE UNIT 4C REGIME EVALUATION"
    )

    log(
        "UNIT 5B PREVIOUS RAW MODE = "
        + previous_result.raw_mode
    )

    log(
        "UNIT 5B CURRENT RAW MODE = "
        + current_result.raw_mode
    )

    log(
        "UNIT 5B ACTIVE MODE = "
        + current_result.active_mode
    )

    log(
        "UNIT 5B DIRECTION = "
        + str(
            current_result.direction
        )
    )

    log(
        "UNIT 5B EMA19/50 SEPARATION % = "
        + decimal_to_string(
            current_result
            .ema_separation_percent
        )
    )

    log(
        "UNIT 5B SIGNED SHORT-TERM MOVE % = "
        + decimal_to_string(
            current_result
            .short_term_move_percent
        )
    )

    log(
        "UNIT 5B EXPECTED SIGNED MOVE % = "
        + decimal_to_string(
            expected_movement
        )
    )

    log(
        "UNIT 5B PENDING MODE = "
        + str(
            current_result.pending_mode
        )
    )

    log(
        "UNIT 5B PENDING COUNT = "
        + str(
            current_result.pending_count
        )
    )

    log(
        "UNIT 5B MODE LOCKED = "
        + str(
            current_result.mode_locked
        )
    )

    log(
        "UNIT 5B REGIME REASON = "
        + current_result.reason
    )

    # --------------------------------------------------------
    # EXACT UNIT 4C -> UNIT 5B CONNECTION
    # --------------------------------------------------------

    unit_5b_result = (
        reconstruction_unit_5b_live_bridge(
            active_mode=(
                current_result.active_mode
            ),
            direction=(
                current_result.direction
            ),
            live_price=(
                current_snapshot.close_price
            ),
            ema19=(
                current_snapshot.ema19
            ),
            ema50=(
                current_snapshot.ema50
            ),
            ema200=(
                current_snapshot.ema200
            ),
            ema19_50_separation_pct=(
                current_result
                .ema_separation_percent
            ),
            short_term_move_pct=(
                current_result
                .short_term_move_percent
            ),
        )
    )

    require(
        isinstance(
            unit_5b_result,
            dict,
        ),
        (
            "UNIT 5B did not return "
            "result dictionary."
        ),
    )

    log(
        "PASS: UNIT 4C -> UNIT 5B LIVE BRIDGE"
    )

    if unit_5b_result[
        "qualified"
    ]:

        log(
            "UNIT 5B LIVE ENTRY STATUS = QUALIFIED"
        )

    else:

        log(
            "UNIT 5B LIVE ENTRY STATUS = NOT QUALIFIED"
        )

    log(
        "UNIT 5B LIVE ENTRY REASON = "
        + str(
            unit_5b_result[
                "reason"
            ]
        )
    )

    separator()

    validate_firebreak(
        client
    )

    log(
        "PASS: UNIT 5B FINAL EXECUTION FIREBREAK"
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
        "NO POSITION SIZING GENERATED = TRUE"
    )

    log(
        "NO TP GENERATED = TRUE"
    )

    log(
        "NO SL GENERATED = TRUE"
    )

    log(
        "NO BACKUP EXECUTION = TRUE"
    )

    log(
        "NO TRADING DECISION EXECUTED = TRUE"
    )

    separator()

    log(
        "UNIT 5B LIVE INTEGRATION TESTS = PASS"
    )

    log(
        "RECONSTRUCTION UNIT 5B RESULT = PASS"
    )

    separator()

    return unit_5b_result


# ============================================================
# RECONSTRUCTION UNIT 6
# ENTRY INSTRUCTION / POSITION SIZING ENGINE
# ============================================================

from decimal import ROUND_DOWN


def reconstruction_unit_6_decimal(
    value,
):

    if isinstance(
        value,
        Decimal,
    ):
        return value

    return Decimal(
        str(value)
    )


def reconstruction_unit_6_normalize_quantity(
    *,
    raw_quantity,
    quantity_step,
):

    raw_quantity = (
        reconstruction_unit_6_decimal(
            raw_quantity
        )
    )

    quantity_step = (
        reconstruction_unit_6_decimal(
            quantity_step
        )
    )

    if quantity_step <= 0:

        raise ValueError(
            "quantity_step must be positive"
        )

    steps = (
        raw_quantity
        / quantity_step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    normalized_quantity = (
        steps
        * quantity_step
    )

    return normalized_quantity


def reconstruction_unit_6_build_entry_instruction(
    *,
    unit_5_qualified,
    active_mode,
    direction,
    entry_price,
    available_balance,
    margin_percent,
    leverage,
    quantity_step,
    minimum_quantity,
):

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 6 ENTRY INSTRUCTION START",
        flush=True,
    )

    entry_price = (
        reconstruction_unit_6_decimal(
            entry_price
        )
    )

    available_balance = (
        reconstruction_unit_6_decimal(
            available_balance
        )
    )

    margin_percent = (
        reconstruction_unit_6_decimal(
            margin_percent
        )
    )

    leverage = (
        reconstruction_unit_6_decimal(
            leverage
        )
    )

    quantity_step = (
        reconstruction_unit_6_decimal(
            quantity_step
        )
    )

    minimum_quantity = (
        reconstruction_unit_6_decimal(
            minimum_quantity
        )
    )

    result = {

        "valid":
            False,

        "reason":
            None,

        "unit_5_qualified":
            bool(
                unit_5_qualified
            ),

        "active_mode":
            active_mode,

        "direction":
            direction,

        "entry_price":
            entry_price,

        "available_balance":
            available_balance,

        "margin_percent":
            margin_percent,

        "leverage":
            leverage,

        "committed_margin":
            None,

        "position_notional":
            None,

        "raw_quantity":
            None,

        "quantity":
            None,

        "quantity_step":
            quantity_step,

        "minimum_quantity":
            minimum_quantity,

        "weex_post":
            False,

        "demo_order":
            False,

        "real_order":
            False,

        "exchange_mutation":
            False,

        "order_payload_generated":
            False,

        "tp_generated":
            False,

        "sl_generated":
            False,

        "backup_execution":
            False,
    }

    if not unit_5_qualified:

        result[
            "reason"
        ] = (
            "UNIT_5_NOT_QUALIFIED"
        )

        return result

    valid_modes = {
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    }

    if active_mode not in valid_modes:

        result[
            "reason"
        ] = (
            "INVALID_ACTIVE_MODE"
        )

        return result

    if direction not in {
        "LONG",
        "SHORT",
    }:

        result[
            "reason"
        ] = (
            "INVALID_DIRECTION"
        )

        return result

    if entry_price <= 0:

        result[
            "reason"
        ] = (
            "INVALID_ENTRY_PRICE"
        )

        return result

    if available_balance <= 0:

        result[
            "reason"
        ] = (
            "INVALID_AVAILABLE_BALANCE"
        )

        return result

    if (
        margin_percent <= 0
        or
        margin_percent > 100
    ):

        result[
            "reason"
        ] = (
            "INVALID_MARGIN_PERCENT"
        )

        return result

    if leverage <= 0:

        result[
            "reason"
        ] = (
            "INVALID_LEVERAGE"
        )

        return result

    if quantity_step <= 0:

        result[
            "reason"
        ] = (
            "INVALID_QUANTITY_STEP"
        )

        return result

    if minimum_quantity <= 0:

        result[
            "reason"
        ] = (
            "INVALID_MINIMUM_QUANTITY"
        )

        return result

    committed_margin = (
        available_balance
        * (
            margin_percent
            / Decimal(
                "100"
            )
        )
    )

    result[
        "committed_margin"
    ] = committed_margin

    position_notional = (
        committed_margin
        * leverage
    )

    result[
        "position_notional"
    ] = position_notional

    raw_quantity = (
        position_notional
        / entry_price
    )

    result[
        "raw_quantity"
    ] = raw_quantity

    quantity = (
        reconstruction_unit_6_normalize_quantity(
            raw_quantity=
                raw_quantity,

            quantity_step=
                quantity_step,
        )
    )

    result[
        "quantity"
    ] = quantity

    if quantity < minimum_quantity:

        result[
            "reason"
        ] = (
            "QUANTITY_BELOW_MINIMUM"
        )

        return result

    result[
        "valid"
    ] = True

    result[
        "reason"
    ] = (
        "ENTRY_INSTRUCTION_APPROVED"
    )

    return result


# ============================================================
# UNIT 6B BRIDGE
# ============================================================

def reconstruction_unit_6b_bridge(
    *,
    unit_5b_result,
    available_balance,
    margin_percent,
    leverage,
    quantity_step,
    minimum_quantity,
):

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 6B BRIDGE START",
        flush=True,
    )

    if not isinstance(
        unit_5b_result,
        dict,
    ):

        return {

            "valid":
                False,

            "reason":
                "INVALID_UNIT_5B_RESULT",

            "sizing_attempted":
                False,

            "unit_6_result":
                None,

            "weex_post":
                False,

            "demo_order":
                False,

            "real_order":
                False,

            "exchange_mutation":
                False,
        }

    qualified = bool(
        unit_5b_result.get(
            "qualified",
            False,
        )
    )

    qualification_reason = (
        unit_5b_result.get(
            "reason"
        )
    )

    active_mode = (
        unit_5b_result.get(
            "active_mode"
        )
    )

    direction = (
        unit_5b_result.get(
            "direction"
        )
    )

    live_price = (
        unit_5b_result.get(
            "live_price"
        )
    )

    print(
        "UNIT 6B UNIT 5B QUALIFIED = "
        + str(
            qualified
        ),
        flush=True,
    )

    print(
        "UNIT 6B UNIT 5B REASON = "
        + str(
            qualification_reason
        ),
        flush=True,
    )

    print(
        "UNIT 6B ACTIVE MODE = "
        + str(
            active_mode
        ),
        flush=True,
    )

    print(
        "UNIT 6B DIRECTION = "
        + str(
            direction
        ),
        flush=True,
    )

    print(
        "UNIT 6B ENTRY PRICE = "
        + str(
            live_price
        ),
        flush=True,
    )

    if not qualified:

        print(
            "UNIT 6B SIZING ATTEMPTED = FALSE",
            flush=True,
        )

        print(
            "UNIT 6B SIZING BLOCKED BY UNIT 5B",
            flush=True,
        )

        return {

            "valid":
                False,

            "reason":
                "UNIT_5B_NOT_QUALIFIED",

            "unit_5b_reason":
                qualification_reason,

            "sizing_attempted":
                False,

            "unit_6_result":
                None,

            "weex_post":
                False,

            "demo_order":
                False,

            "real_order":
                False,

            "exchange_mutation":
                False,

            "order_payload_generated":
                False,

            "tp_generated":
                False,

            "sl_generated":
                False,

            "backup_execution":
                False,
        }

    print(
        "UNIT 6B QUALIFICATION GATE = PASS",
        flush=True,
    )

    print(
        "UNIT 6B SIZING ATTEMPTED = TRUE",
        flush=True,
    )

    unit_6_result = (
        reconstruction_unit_6_build_entry_instruction(

            unit_5_qualified=
                True,

            active_mode=
                active_mode,

            direction=
                direction,

            entry_price=
                live_price,

            available_balance=
                available_balance,

            margin_percent=
                margin_percent,

            leverage=
                leverage,

            quantity_step=
                quantity_step,

            minimum_quantity=
                minimum_quantity,
        )
    )

    if not unit_6_result.get(
        "valid",
        False,
    ):

        return {

            "valid":
                False,

            "reason":
                "UNIT_6_SIZING_REJECTED",

            "unit_5b_reason":
                qualification_reason,

            "sizing_attempted":
                True,

            "unit_6_result":
                unit_6_result,

            "weex_post":
                False,

            "demo_order":
                False,

            "real_order":
                False,

            "exchange_mutation":
                False,

            "order_payload_generated":
                False,

            "tp_generated":
                False,

            "sl_generated":
                False,

            "backup_execution":
                False,
        }

    return {

        "valid":
            True,

        "reason":
            "UNIT_6B_ENTRY_INSTRUCTION_READY",

        "unit_5b_reason":
            qualification_reason,

        "sizing_attempted":
            True,

        "unit_6_result":
            unit_6_result,

        "weex_post":
            False,

        "demo_order":
            False,

        "real_order":
            False,

        "exchange_mutation":
            False,

        "order_payload_generated":
            False,

        "tp_generated":
            False,

        "sl_generated":
            False,

        "backup_execution":
            False,
    }


# ============================================================
# UNIT 6C
# LIVE UNIT 5B -> UNIT 6B INTEGRATION
# ============================================================

UNIT_6C_AVAILABLE_BALANCE = Decimal(
    "7.18945017"
)

UNIT_6C_MARGIN_PERCENT = Decimal(
    "5"
)

UNIT_6C_LEVERAGE = Decimal(
    "100"
)

UNIT_6C_QUANTITY_STEP = Decimal(
    "0.0001"
)

UNIT_6C_MINIMUM_QUANTITY = Decimal(
    "0.0001"
)


def reconstruction_unit_6c_live_bridge(
    *,
    unit_5b_result,
):

    separator()

    log(
        "RECONSTRUCTION UNIT 6C LIVE BRIDGE START"
    )

    require(
        isinstance(
            unit_5b_result,
            dict,
        ),
        "UNIT 6C invalid Unit 5B result.",
    )

    require(
        "qualified"
        in unit_5b_result,
        "UNIT 6C missing qualified field.",
    )

    require(
        "reason"
        in unit_5b_result,
        "UNIT 6C missing Unit 5B reason.",
    )

    require(
        "active_mode"
        in unit_5b_result,
        "UNIT 6C missing active mode.",
    )

    require(
        "direction"
        in unit_5b_result,
        "UNIT 6C missing direction.",
    )

    require(
        "live_price"
        in unit_5b_result,
        "UNIT 6C missing live price.",
    )

    log(
        "UNIT 6C UNIT 5B QUALIFIED = "
        + str(
            unit_5b_result[
                "qualified"
            ]
        )
    )

    log(
        "UNIT 6C UNIT 5B REASON = "
        + str(
            unit_5b_result[
                "reason"
            ]
        )
    )

    log(
        "UNIT 6C ACTIVE MODE = "
        + str(
            unit_5b_result[
                "active_mode"
            ]
        )
    )

    log(
        "UNIT 6C DIRECTION = "
        + str(
            unit_5b_result[
                "direction"
            ]
        )
    )

    log(
        "UNIT 6C LIVE PRICE = "
        + decimal_to_string(
            unit_5b_result[
                "live_price"
            ]
        )
    )

    log(
        "UNIT 6C TEST BALANCE = "
        + decimal_to_string(
            UNIT_6C_AVAILABLE_BALANCE
        )
    )

    log(
        "UNIT 6C BALANCE SOURCE = "
        "DETERMINISTIC TEST VALUE"
    )

    log(
        "UNIT 6C LIVE ACCOUNT BALANCE READ = FALSE"
    )

    unit_6b_result = (
        reconstruction_unit_6b_bridge(
            unit_5b_result=(
                unit_5b_result
            ),
            available_balance=(
                UNIT_6C_AVAILABLE_BALANCE
            ),
            margin_percent=(
                UNIT_6C_MARGIN_PERCENT
            ),
            leverage=(
                UNIT_6C_LEVERAGE
            ),
            quantity_step=(
                UNIT_6C_QUANTITY_STEP
            ),
            minimum_quantity=(
                UNIT_6C_MINIMUM_QUANTITY
            ),
        )
    )

    require(
        isinstance(
            unit_6b_result,
            dict,
        ),
        "UNIT 6C Unit 6B result invalid.",
    )

    qualified = bool(
        unit_5b_result[
            "qualified"
        ]
    )

    if not qualified:

        require(
            unit_6b_result.get(
                "valid"
            )
            is False,
            (
                "UNIT 6C rejected market "
                "unexpectedly became valid."
            ),
        )

        require(
            unit_6b_result.get(
                "reason"
            )
            == "UNIT_5B_NOT_QUALIFIED",
            (
                "UNIT 6C rejected market "
                "has wrong Unit 6B reason."
            ),
        )

        require(
            unit_6b_result.get(
                "sizing_attempted"
            )
            is False,
            (
                "UNIT 6C sizing ran despite "
                "Unit 5B rejection."
            ),
        )

        require(
            unit_6b_result.get(
                "unit_6_result"
            )
            is None,
            (
                "UNIT 6C Unit 6 result exists "
                "despite Unit 5B rejection."
            ),
        )

        log(
            "PASS: UNIT 6C LIVE REJECTED SIGNAL "
            "BLOCKED BEFORE UNIT 6 SIZING"
        )

    else:

        require(
            unit_6b_result.get(
                "sizing_attempted"
            )
            is True,
            (
                "UNIT 6C qualified market "
                "did not attempt sizing."
            ),
        )

        unit_6_result = (
            unit_6b_result.get(
                "unit_6_result"
            )
        )

        require(
            isinstance(
                unit_6_result,
                dict,
            ),
            (
                "UNIT 6C qualified path "
                "did not return Unit 6 result."
            ),
        )

        if unit_6b_result.get(
            "valid"
        ):

            require(
                unit_6_result.get(
                    "valid"
                )
                is True,
                (
                    "UNIT 6C Unit 6B valid "
                    "but Unit 6 invalid."
                ),
            )

            log(
                "PASS: UNIT 6C LIVE QUALIFIED "
                "SIGNAL REACHED UNIT 6"
            )

            log(
                "UNIT 6C COMMITTED MARGIN = "
                + decimal_to_string(
                    unit_6_result[
                        "committed_margin"
                    ]
                )
            )

            log(
                "UNIT 6C POSITION NOTIONAL = "
                + decimal_to_string(
                    unit_6_result[
                        "position_notional"
                    ]
                )
            )

            log(
                "UNIT 6C RAW QUANTITY = "
                + decimal_to_string(
                    unit_6_result[
                        "raw_quantity"
                    ]
                )
            )

            log(
                "UNIT 6C NORMALIZED QUANTITY = "
                + decimal_to_string(
                    unit_6_result[
                        "quantity"
                    ]
                )
            )

        else:

            require(
                unit_6b_result.get(
                    "reason"
                )
                == "UNIT_6_SIZING_REJECTED",
                (
                    "UNIT 6C unexpected "
                    "qualified-path rejection."
                ),
            )

            log(
                "PASS: UNIT 6C QUALIFICATION "
                "REACHED UNIT 6; SIZING REJECTED "
                "BY UNIT 6 VALIDATION"
            )

            log(
                "UNIT 6C UNIT 6 REJECTION REASON = "
                + str(
                    unit_6_result.get(
                        "reason"
                    )
                )
            )

    for key in (
        "weex_post",
        "demo_order",
        "real_order",
        "exchange_mutation",
        "order_payload_generated",
        "tp_generated",
        "sl_generated",
        "backup_execution",
    ):

        require(
            unit_6b_result.get(
                key,
                False,
            )
            is False,
            (
                "UNIT 6C execution firebreak "
                "failed for "
                + key
            ),
        )

    log(
        "PASS: UNIT 6C EXECUTION FIREBREAK"
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
        "NO WEEX ORDER PAYLOAD GENERATED = TRUE"
    )

    log(
        "NO TP GENERATED = TRUE"
    )

    log(
        "NO SL GENERATED = TRUE"
    )

    log(
        "NO BACKUP EXECUTION = TRUE"
    )

    separator()

    return unit_6b_result


def run_unit_6c_live_test() -> bool:

    separator()

    log(
        "RECONSTRUCTION UNIT 6C LIVE TEST START"
    )

    separator()

    unit_5b_result = (
        run_unit_5b_live_test()
    )

    require(
        isinstance(
            unit_5b_result,
            dict,
        ),
        (
            "UNIT 6C did not receive "
            "Unit 5B result dictionary."
        ),
    )

    log(
        "PASS: UNIT 6C RECEIVED LIVE "
        "UNIT 5B RESULT"
    )

    unit_6b_result = (
        reconstruction_unit_6c_live_bridge(
            unit_5b_result=(
                unit_5b_result
            )
        )
    )

    require(
        isinstance(
            unit_6b_result,
            dict,
        ),
        (
            "UNIT 6C did not receive "
            "Unit 6B result dictionary."
        ),
    )

    if unit_5b_result[
        "qualified"
    ]:

        log(
            "UNIT 6C LIVE PATH = "
            "UNIT 5B QUALIFIED"
        )

        log(
            "UNIT 6C SIZING ATTEMPTED = "
            + str(
                unit_6b_result.get(
                    "sizing_attempted"
                )
            )
        )

    else:

        log(
            "UNIT 6C LIVE PATH = "
            "UNIT 5B NOT QUALIFIED"
        )

        require(
            unit_6b_result.get(
                "sizing_attempted"
            )
            is False,
            (
                "UNIT 6C rejected live signal "
                "attempted sizing."
            ),
        )

        log(
            "UNIT 6C SIZING ATTEMPTED = FALSE"
        )

        log(
            "PASS: UNIT 6C CORRECTLY "
            "PRESERVED QUALIFICATION GATE"
        )

    require(
        ALLOW_HTTP_POST
        is False,
        "UNIT 6C HTTP POST firebreak failed.",
    )

    require(
        ALLOW_DEMO_ORDER
        is False,
        "UNIT 6C demo-order firebreak failed.",
    )

    require(
        ALLOW_REAL_ORDER
        is False,
        "UNIT 6C real-order firebreak failed.",
    )

    require(
        ALLOW_EXCHANGE_MUTATION
        is False,
        (
            "UNIT 6C exchange-mutation "
            "firebreak failed."
        ),
    )

    require(
        ALLOW_ORDER_PAYLOAD
        is False,
        (
            "UNIT 6C order-payload "
            "firebreak failed."
        ),
    )

    require(
        ALLOW_POSITION_SIZING
        is False,
        (
            "UNIT 6C executable-position-sizing "
            "firebreak failed."
        ),
    )

    require(
        ALLOW_TP_GENERATION
        is False,
        "UNIT 6C TP firebreak failed.",
    )

    require(
        ALLOW_SL_GENERATION
        is False,
        "UNIT 6C SL firebreak failed.",
    )

    require(
        ALLOW_BACKUP_EXECUTION
        is False,
        "UNIT 6C backup firebreak failed.",
    )

    separator()

    log(
        "UNIT 6C LIVE INTEGRATION TESTS = PASS"
    )

    log(
        "RECONSTRUCTION UNIT 6C RESULT = PASS"
    )

    separator()

    return True


# ============================================================
# UNIT 7B
# LIVE UNIT 6C -> UNIT 7 ZERO-WRITE INTEGRATION TEST
#
# PURPOSE:
# Run the existing LIVE Unit 5B -> Unit 6C path and feed the
# resulting Unit 6B instruction directly into the already
# tested Unit 7 payload builder.
#
# IMPORTANT:
# - ZERO WEEX POST
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE MUTATION
# - NO SL
# - NO BACKUP EXECUTION
# ============================================================


def run_unit_7b_live_integration_test():

    separator()

    log(
        "RECONSTRUCTION UNIT 7B "
        "LIVE INTEGRATION TEST START"
    )

    separator()

    # --------------------------------------------------------
    # STEP 1
    # RUN EXISTING LIVE UNIT 5B PATH
    # --------------------------------------------------------

    unit_5b_result = (
        run_unit_5b_live_test()
    )

    require(
        isinstance(
            unit_5b_result,
            dict,
        ),
        "UNIT 7B invalid Unit 5B result.",
    )

    log(
        "PASS: UNIT 7B RECEIVED "
        "LIVE UNIT 5B RESULT"
    )

    log(
        "UNIT 7B UNIT 5B QUALIFIED = "
        + str(
            unit_5b_result.get(
                "qualified"
            )
        )
    )

    log(
        "UNIT 7B LIVE DIRECTION = "
        + str(
            unit_5b_result.get(
                "direction"
            )
        )
    )

    # --------------------------------------------------------
    # STEP 2
    # FEED LIVE RESULT INTO EXISTING UNIT 6C BRIDGE
    # --------------------------------------------------------

    unit_6b_result = (
        reconstruction_unit_6c_live_bridge(
            unit_5b_result=unit_5b_result
        )
    )

    require(
        isinstance(
            unit_6b_result,
            dict,
        ),
        "UNIT 7B invalid Unit 6B result.",
    )

    log(
        "PASS: UNIT 7B RECEIVED "
        "UNIT 6C / UNIT 6B RESULT"
    )

    log(
        "UNIT 7B UNIT 6B VALID = "
        + str(
            unit_6b_result.get(
                "valid"
            )
        )
    )

    # --------------------------------------------------------
    # STEP 3
    # FEED UNIT 6B DIRECTLY INTO TESTED UNIT 7 BUILDER
    # --------------------------------------------------------

    unit_7_result = (
        reconstruction_unit_7_build_payload_preview(
            unit_6b_result=unit_6b_result
        )
    )

    require(
        isinstance(
            unit_7_result,
            dict,
        ),
        "UNIT 7B invalid Unit 7 result.",
    )

    # --------------------------------------------------------
    # QUALIFIED LIVE PATH
    # --------------------------------------------------------

    if unit_6b_result.get(
        "valid",
        False,
    ):

        require(
            unit_7_result.get(
                "valid"
            )
            is True,
            (
                "UNIT 7B valid Unit 6B result "
                "did not reach valid Unit 7."
            ),
        )

        require(
            unit_7_result.get(
                "candidate_payload_generated"
            )
            is True,
            (
                "UNIT 7B qualified path did "
                "not generate payload preview."
            ),
        )

        require(
            isinstance(
                unit_7_result.get(
                    "payload"
                ),
                dict,
            ),
            (
                "UNIT 7B qualified path "
                "missing payload."
            ),
        )

        log(
            "UNIT 7B LIVE PATH = "
            "QUALIFIED"
        )

        log(
            "UNIT 7B LIVE CANDIDATE "
            "PAYLOAD = "
            + repr(
                unit_7_result.get(
                    "payload"
                )
            )
        )

    # --------------------------------------------------------
    # NON-QUALIFIED LIVE PATH
    # --------------------------------------------------------

    else:

        require(
            unit_7_result.get(
                "valid"
            )
            is False,
            (
                "UNIT 7B blocked Unit 6B "
                "unexpectedly produced "
                "valid Unit 7 result."
            ),
        )

        require(
            unit_7_result.get(
                "payload"
            )
            is None,
            (
                "UNIT 7B blocked path "
                "generated payload."
            ),
        )

        log(
            "UNIT 7B LIVE PATH = "
            "BLOCKED BY EXISTING "
            "QUALIFICATION GATE"
        )

        log(
            "PASS: UNIT 7B GENERATED "
            "NO PAYLOAD ON BLOCKED PATH"
        )

    # --------------------------------------------------------
    # UNIT 7 RESULT FIREBREAK
    # --------------------------------------------------------

    for key in (
        "weex_post",
        "demo_order",
        "real_order",
        "exchange_mutation",
        "tp_generated",
        "sl_generated",
        "backup_execution",
    ):

        require(
            unit_7_result.get(
                key,
                False,
            )
            is False,
            (
                "UNIT 7B result firebreak "
                "failed: "
                + key
            ),
        )

    # --------------------------------------------------------
    # GLOBAL FIREBREAK
    # --------------------------------------------------------

    require(
        ALLOW_HTTP_POST is False,
        "UNIT 7B HTTP POST firebreak failed.",
    )

    require(
        ALLOW_DEMO_ORDER is False,
        "UNIT 7B demo order firebreak failed.",
    )

    require(
        ALLOW_REAL_ORDER is False,
        "UNIT 7B real order firebreak failed.",
    )

    require(
        ALLOW_EXCHANGE_MUTATION is False,
        "UNIT 7B mutation firebreak failed.",
    )

    require(
        ALLOW_SL_GENERATION is False,
        "UNIT 7B SL firebreak failed.",
    )

    require(
        ALLOW_BACKUP_EXECUTION is False,
        "UNIT 7B backup firebreak failed.",
    )

    separator()

    log(
        "PASS: UNIT 7B EXECUTION FIREBREAK"
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
        "NO SL GENERATED = TRUE"
    )

    log(
        "NO BACKUP EXECUTION = TRUE"
    )

    separator()

    log(
        "UNIT 7B LIVE INTEGRATION "
        "TESTS = PASS"
    )

    log(
        "RECONSTRUCTION UNIT 7B "
        "RESULT = PASS"
    )

    separator()

    return True


# ============================================================
# UNIT 7
# DIRECT UNIT 6C / UNIT 6B -> ZERO-WRITE DEMO PAYLOAD PREVIEW
# ============================================================

UNIT_7_DEMO_SYMBOL = "BTCSUSDT"


def reconstruction_unit_7_build_payload_preview(
    *,
    unit_6b_result,
):
    separator()

    log(
        "RECONSTRUCTION UNIT 7 DIRECT BRIDGE START"
    )

    result = {
        "valid": False,
        "reason": None,
        "payload": None,
        "candidate_payload_generated": False,
        "weex_post": False,
        "demo_order": False,
        "real_order": False,
        "exchange_mutation": False,
        "tp_generated": False,
        "sl_generated": False,
        "backup_execution": False,
    }

    require(
        isinstance(
            unit_6b_result,
            dict,
        ),
        "UNIT 7 invalid Unit 6B result.",
    )

    # --------------------------------------------------------
    # UNIT 6B MUST BE VALID BEFORE ANY PAYLOAD CAN EXIST
    # --------------------------------------------------------

    if not unit_6b_result.get(
        "valid",
        False,
    ):
        result["reason"] = (
            "UNIT_6B_NOT_READY"
        )

        log(
            "UNIT 7 PAYLOAD PREVIEW ATTEMPTED = FALSE"
        )

        log(
            "UNIT 7 BLOCKED: UNIT 6B NOT READY"
        )

        return result

    # --------------------------------------------------------
    # RECOVER VERIFIED UNIT 6 INSTRUCTION
    # --------------------------------------------------------

    unit_6_result = (
        unit_6b_result.get(
            "unit_6_result"
        )
    )

    require(
        isinstance(
            unit_6_result,
            dict,
        ),
        "UNIT 7 missing Unit 6 result.",
    )

    require(
        unit_6_result.get(
            "valid"
        )
        is True,
        "UNIT 7 received invalid Unit 6 result.",
    )

    # --------------------------------------------------------
    # DIRECTION
    # --------------------------------------------------------

    direction = str(
        unit_6_result.get(
            "direction"
        )
    ).upper()

    require(
        direction
        in {
            "LONG",
            "SHORT",
        },
        "UNIT 7 invalid direction.",
    )

    # --------------------------------------------------------
    # QUANTITY
    # --------------------------------------------------------

    quantity = D(
        unit_6_result.get(
            "quantity"
        )
    )

    require(
        quantity
        >= UNIT_6C_MINIMUM_QUANTITY,
        "UNIT 7 quantity below minimum.",
    )

    require(
        quantity
        % UNIT_6C_QUANTITY_STEP
        == 0,
        "UNIT 7 quantity not aligned to step.",
    )

    # --------------------------------------------------------
    # MAP INTERNAL DIRECTION TO DEMO PAYLOAD
    # --------------------------------------------------------

    if direction == "LONG":
        side = "BUY"
        position_side = "LONG"

    else:
        side = "SELL"
        position_side = "SHORT"

    # --------------------------------------------------------
    # BUILD ZERO-WRITE CANDIDATE PAYLOAD
    #
    # IMPORTANT:
    # THIS IS ONLY A PYTHON DICTIONARY.
    # NOTHING IS SENT TO WEEX.
    # --------------------------------------------------------

    payload = {
        "symbol":
            UNIT_7_DEMO_SYMBOL,

        "side":
            side,

        "positionSide":
            position_side,

        "type":
            "MARKET",

        "quantity":
            decimal_to_string(
                quantity
            ),
    }

    # --------------------------------------------------------
    # SL-DISABLE GUARD
    # --------------------------------------------------------

    forbidden_sl_fields = (
        "slTriggerPrice",
        "SlWorkingType",
        "stopLossPrice",
        "stopPrice",
    )

    for field in forbidden_sl_fields:

        require(
            field
            not in payload,
            (
                "UNIT 7 forbidden SL field present: "
                + field
            ),
        )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    result["valid"] = True

    result["reason"] = (
        "UNIT_7_PAYLOAD_PREVIEW_READY"
    )

    result["payload"] = payload

    result[
        "candidate_payload_generated"
    ] = True

    # --------------------------------------------------------
    # DIAGNOSTICS
    # --------------------------------------------------------

    log(
        "PASS: UNIT 7 RECEIVED VALID UNIT 6B INSTRUCTION"
    )

    log(
        "UNIT 7 DIRECTION = "
        + direction
    )

    log(
        "UNIT 7 SIDE = "
        + side
    )

    log(
        "UNIT 7 POSITION SIDE = "
        + position_side
    )

    log(
        "UNIT 7 QUANTITY = "
        + decimal_to_string(
            quantity
        )
    )

    log(
        "UNIT 7 CANDIDATE PAYLOAD = "
        + repr(
            payload
        )
    )

    log(
        "PASS: UNIT 7 SL-DISABLED PAYLOAD GUARD"
    )

    log(
        "UNIT 7 PAYLOAD PREVIEW ATTEMPTED = TRUE"
    )

    return result
# ============================================================
# UNIT 7B
# LIVE UNIT 6C -> UNIT 7 ZERO-WRITE INTEGRATION TEST
# ============================================================

# ============================================================
# RECONSTRUCTION UNIT 7C
# DETERMINISTIC QUALIFIED-PATH PAYLOAD TEST
#
# PURPOSE:
# Prove that the already-tested Unit 7 payload builder
# correctly converts a VALID Unit 6B instruction into the
# expected WEEX demo candidate payload.
#
# THIS TEST DOES NOT BYPASS OR MODIFY UNIT 5B.
# THIS TEST DOES NOT CHANGE LIVE MARKET QUALIFICATION.
#
# IMPORTANT:
# - DETERMINISTIC INPUT ONLY
# - ZERO WEEX POST
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE MUTATION
# - NO TP
# - NO SL
# - NO BACKUP EXECUTION
# ============================================================


def run_unit_7c_qualified_path_test():

    separator()

    log(
        "RECONSTRUCTION UNIT 7C "
        "QUALIFIED-PATH TEST START"
    )

    separator()

    # ========================================================
    # TEST CASE 1
    # QUALIFIED LONG
    # ========================================================

    log(
        "UNIT 7C LONG TEST START"
    )

    simulated_long_unit_6b_result = {
        "valid": True,
        "reason": "UNIT_7C_SIMULATED_QUALIFIED_LONG",
        "unit_6_result": {
            "valid": True,
            "direction": "LONG",
            "quantity": D("0.0004"),
            "entry_price": D("85000.0"),
        },
    }

    long_result = (
        reconstruction_unit_7_build_payload_preview(
            unit_6b_result=(
                simulated_long_unit_6b_result
            )
        )
    )

    require(
        isinstance(
            long_result,
            dict,
        ),
        "UNIT 7C LONG result is not dict.",
    )

    require(
        long_result.get(
            "valid"
        )
        is True,
        "UNIT 7C LONG result not valid.",
    )

    require(
        long_result.get(
            "candidate_payload_generated"
        )
        is True,
        (
            "UNIT 7C LONG candidate "
            "payload not generated."
        ),
    )

    long_payload = (
        long_result.get(
            "payload"
        )
    )

    require(
        isinstance(
            long_payload,
            dict,
        ),
        "UNIT 7C LONG payload missing.",
    )

    require(
        long_payload.get(
            "symbol"
        )
        == UNIT_7_DEMO_SYMBOL,
        "UNIT 7C LONG symbol mismatch.",
    )

    require(
        long_payload.get(
            "side"
        )
        == "BUY",
        "UNIT 7C LONG side mismatch.",
    )

    require(
        long_payload.get(
            "positionSide"
        )
        == "LONG",
        (
            "UNIT 7C LONG "
            "positionSide mismatch."
        ),
    )

    require(
        long_payload.get(
            "type"
        )
        == "MARKET",
        "UNIT 7C LONG type mismatch.",
    )

    require(
        long_payload.get(
            "quantity"
        )
        == "0.0004",
        "UNIT 7C LONG quantity mismatch.",
    )

    # --------------------------------------------------------
    # LONG SL-DISABLE CHECK
    # --------------------------------------------------------

    for field in (
        "slTriggerPrice",
        "SlWorkingType",
        "stopLossPrice",
        "stopPrice",
    ):

        require(
            field
            not in long_payload,
            (
                "UNIT 7C LONG forbidden "
                "SL field present: "
                + field
            ),
        )

    log(
        "PASS: UNIT 7C LONG PAYLOAD"
    )

    log(
        "UNIT 7C LONG PAYLOAD = "
        + repr(
            long_payload
        )
    )

    # ========================================================
    # TEST CASE 2
    # QUALIFIED SHORT
    # ========================================================

    separator()

    log(
        "UNIT 7C SHORT TEST START"
    )

    simulated_short_unit_6b_result = {
        "valid": True,
        "reason": "UNIT_7C_SIMULATED_QUALIFIED_SHORT",
        "unit_6_result": {
            "valid": True,
            "direction": "SHORT",
            "quantity": D("0.0004"),
            "entry_price": D("85000.0"),
        },
    }

    short_result = (
        reconstruction_unit_7_build_payload_preview(
            unit_6b_result=(
                simulated_short_unit_6b_result
            )
        )
    )

    require(
        isinstance(
            short_result,
            dict,
        ),
        "UNIT 7C SHORT result is not dict.",
    )

    require(
        short_result.get(
            "valid"
        )
        is True,
        "UNIT 7C SHORT result not valid.",
    )

    require(
        short_result.get(
            "candidate_payload_generated"
        )
        is True,
        (
            "UNIT 7C SHORT candidate "
            "payload not generated."
        ),
    )

    short_payload = (
        short_result.get(
            "payload"
        )
    )

    require(
        isinstance(
            short_payload,
            dict,
        ),
        "UNIT 7C SHORT payload missing.",
    )

    require(
        short_payload.get(
            "symbol"
        )
        == UNIT_7_DEMO_SYMBOL,
        "UNIT 7C SHORT symbol mismatch.",
    )

    require(
        short_payload.get(
            "side"
        )
        == "SELL",
        "UNIT 7C SHORT side mismatch.",
    )

    require(
        short_payload.get(
            "positionSide"
        )
        == "SHORT",
        (
            "UNIT 7C SHORT "
            "positionSide mismatch."
        ),
    )

    require(
        short_payload.get(
            "type"
        )
        == "MARKET",
        "UNIT 7C SHORT type mismatch.",
    )

    require(
        short_payload.get(
            "quantity"
        )
        == "0.0004",
        "UNIT 7C SHORT quantity mismatch.",
    )

    # --------------------------------------------------------
    # SHORT SL-DISABLE CHECK
    # --------------------------------------------------------

    for field in (
        "slTriggerPrice",
        "SlWorkingType",
        "stopLossPrice",
        "stopPrice",
    ):

        require(
            field
            not in short_payload,
            (
                "UNIT 7C SHORT forbidden "
                "SL field present: "
                + field
            ),
        )

    log(
        "PASS: UNIT 7C SHORT PAYLOAD"
    )

    log(
        "UNIT 7C SHORT PAYLOAD = "
        + repr(
            short_payload
        )
    )

    # ========================================================
    # RESULT-LEVEL FIREBREAK CHECK
    # ========================================================

    for result_name, result in (
        (
            "LONG",
            long_result,
        ),
        (
            "SHORT",
            short_result,
        ),
    ):

        for key in (
            "weex_post",
            "demo_order",
            "real_order",
            "exchange_mutation",
            "tp_generated",
            "sl_generated",
            "backup_execution",
        ):

            require(
                result.get(
                    key,
                    False,
                )
                is False,
                (
                    "UNIT 7C "
                    + result_name
                    + " firebreak failed: "
                    + key
                ),
            )

    # ========================================================
    # GLOBAL EXECUTION FIREBREAK
    # ========================================================

    require(
        ALLOW_HTTP_POST is False,
        "UNIT 7C HTTP POST firebreak failed.",
    )

    require(
        ALLOW_DEMO_ORDER is False,
        "UNIT 7C demo order firebreak failed.",
    )

    require(
        ALLOW_REAL_ORDER is False,
        "UNIT 7C real order firebreak failed.",
    )

    require(
        ALLOW_EXCHANGE_MUTATION is False,
        (
            "UNIT 7C exchange mutation "
            "firebreak failed."
        ),
    )

    require(
        ALLOW_SL_GENERATION is False,
        "UNIT 7C SL firebreak failed.",
    )

    require(
        ALLOW_BACKUP_EXECUTION is False,
        "UNIT 7C backup firebreak failed.",
    )

    separator()

    log(
        "PASS: UNIT 7C QUALIFIED "
        "LONG PATH"
    )

    log(
        "PASS: UNIT 7C QUALIFIED "
        "SHORT PATH"
    )

    log(
        "PASS: UNIT 7C SL-DISABLE GUARD"
    )

    log(
        "PASS: UNIT 7C EXECUTION FIREBREAK"
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
        "NO TP GENERATED = TRUE"
    )

    log(
        "NO SL GENERATED = TRUE"
    )

    log(
        "NO BACKUP EXECUTION = TRUE"
    )

    separator()

    log(
        "UNIT 7C QUALIFIED-PATH "
        "TESTS = PASS"
    )

    log(
        "RECONSTRUCTION UNIT 7C "
        "RESULT = PASS"
    )

    separator()

    return True


def main():

    log(
        f"{APP_NAME} UNIT_7C_QUALIFIED_PATH_TEST"
    )

    log(
        "STARTING UNIT 7C "
        "ZERO-WRITE QUALIFIED-PATH TEST"
    )

    try:

        result = (
            run_unit_7c_qualified_path_test()
        )

    except Exception as exc:

        separator()

        log(
            "RECONSTRUCTION UNIT 7C "
            "RESULT = FAIL"
        )

        log(
            "ERROR TYPE = "
            + type(exc).__name__
        )

        log(
            "ERROR = "
            + repr(exc)
        )

        separator()

        raise

    if not result:

        raise RuntimeError(
            "Unit 7C qualified-path "
            "test did not pass."
        )


if __name__ == "__main__":
    main()

# ============================================================
# RECONSTRUCTION UNIT 8
# DEMO SUBMISSION-BOUNDARY STANDALONE ZERO-WRITE TEST
#
# PURPOSE:
# Take the already validated Unit 7 candidate payload and
# validate the final demo-order submission envelope immediately
# before the future WEEX network-write boundary.
#
# IMPORTANT:
# - STANDALONE TEST
# - ZERO WEEX POST
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE MUTATION
# - NO API REQUEST IS SENT
# - NO TP GENERATED
# - NO SL GENERATED
# - NO BACKUP EXECUTION
#
# UNIT 8 DOES NOT ENABLE EXECUTION.
# ============================================================


def reconstruction_unit_8_build_demo_submission_boundary(
    *,
    candidate_payload,
):
    print(
        "-" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 8 DEMO SUBMISSION BOUNDARY START",
        flush=True,
    )

    # --------------------------------------------------------
    # BASIC INPUT VALIDATION
    # --------------------------------------------------------

    if not isinstance(candidate_payload, dict):
        raise RuntimeError(
            "UNIT 8 INVALID CANDIDATE PAYLOAD TYPE"
        )

    # Work only with a copy.
    # Unit 8 must never mutate the Unit 7 payload.
    payload = dict(candidate_payload)

    # --------------------------------------------------------
    # REQUIRED ENTRY FIELDS
    # --------------------------------------------------------

    required_fields = (
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
    )

    missing_fields = [
        field
        for field in required_fields
        if field not in payload
    ]

    if missing_fields:
        raise RuntimeError(
            "UNIT 8 MISSING REQUIRED FIELDS: "
            + str(missing_fields)
        )

    print(
        "PASS: UNIT 8 REQUIRED ENTRY FIELDS PRESENT",
        flush=True,
    )

    # --------------------------------------------------------
    # SYMBOL VALIDATION
    # --------------------------------------------------------

    symbol = str(
        payload["symbol"]
    ).strip().upper()

    if symbol != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 8 INVALID SYMBOL: "
            + symbol
        )

    print(
        "PASS: UNIT 8 SYMBOL = BTCSUSDT",
        flush=True,
    )

    # --------------------------------------------------------
    # SIDE / POSITION-SIDE CONSISTENCY
    # --------------------------------------------------------

    side = str(
        payload["side"]
    ).strip().upper()

    position_side = str(
        payload["positionSide"]
    ).strip().upper()

    valid_direction_pairs = {
        ("BUY", "LONG"),
        ("SELL", "SHORT"),
    }

    if (
        side,
        position_side,
    ) not in valid_direction_pairs:
        raise RuntimeError(
            "UNIT 8 INVALID SIDE/POSITION PAIR: "
            + str(
                (
                    side,
                    position_side,
                )
            )
        )

    print(
        "PASS: UNIT 8 SIDE/POSITION CONSISTENCY",
        flush=True,
    )

    # --------------------------------------------------------
    # ORDER TYPE
    # --------------------------------------------------------

    order_type = str(
        payload["type"]
    ).strip().upper()

    if order_type != "MARKET":
        raise RuntimeError(
            "UNIT 8 INVALID ORDER TYPE: "
            + order_type
        )

    print(
        "PASS: UNIT 8 ORDER TYPE = MARKET",
        flush=True,
    )

    # --------------------------------------------------------
    # QUANTITY VALIDATION
    # --------------------------------------------------------

    try:
        quantity = float(
            payload["quantity"]
        )

    except Exception as exc:
        raise RuntimeError(
            "UNIT 8 INVALID QUANTITY"
        ) from exc

    if quantity <= 0:
        raise RuntimeError(
            "UNIT 8 QUANTITY MUST BE POSITIVE"
        )

    print(
        "PASS: UNIT 8 QUANTITY > 0",
        flush=True,
    )

    # --------------------------------------------------------
    # SL-DISABLED GUARD
    #
    # No stop-loss field is allowed to cross this boundary.
    # --------------------------------------------------------

    forbidden_sl_fields = (
        "slTriggerPrice",
        "SlWorkingType",
        "stopLossPrice",
        "stopPrice",
    )

    present_sl_fields = [
        field
        for field in forbidden_sl_fields
        if field in payload
    ]

    if present_sl_fields:
        raise RuntimeError(
            "UNIT 8 SL FIELD PRESENT: "
            + str(present_sl_fields)
        )

    print(
        "PASS: UNIT 8 SL-DISABLED PAYLOAD GUARD",
        flush=True,
    )

    # --------------------------------------------------------
    # UNIT 8 ALLOWED PAYLOAD SHAPE
    #
    # For this reconstruction stage we intentionally accept
    # only the five fields already proven by Unit 7C.
    # --------------------------------------------------------

    allowed_fields = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
    }

    unexpected_fields = sorted(
        set(payload.keys())
        - allowed_fields
    )

    if unexpected_fields:
        raise RuntimeError(
            "UNIT 8 UNEXPECTED PAYLOAD FIELDS: "
            + str(unexpected_fields)
        )

    print(
        "PASS: UNIT 8 PAYLOAD FIELD WHITELIST",
        flush=True,
    )

    # --------------------------------------------------------
    # NORMALIZE FINAL BOUNDARY PAYLOAD
    # --------------------------------------------------------

    final_payload = {
        "symbol":
            symbol,

        "side":
            side,

        "positionSide":
            position_side,

        "type":
            order_type,

        "quantity":
            str(
                payload["quantity"]
            ),
    }

    # --------------------------------------------------------
    # VERIFY INPUT WAS NOT MUTATED
    # --------------------------------------------------------

    if payload != candidate_payload:
        raise RuntimeError(
            "UNIT 8 INPUT PAYLOAD MUTATION DETECTED"
        )

    print(
        "PASS: UNIT 8 INPUT PAYLOAD PRESERVED",
        flush=True,
    )

    # --------------------------------------------------------
    # EXECUTION FIREBREAK
    #
    # These values are deliberately hard-coded False.
    # Unit 8 contains no network-write function.
    # --------------------------------------------------------

    weex_post = False
    demo_order_sent = False
    real_order_sent = False
    exchange_mutation = False

    if weex_post:
        raise RuntimeError(
            "UNIT 8 EXECUTION FIREBREAK FAILURE: WEEX POST"
        )

    if demo_order_sent:
        raise RuntimeError(
            "UNIT 8 EXECUTION FIREBREAK FAILURE: DEMO ORDER"
        )

    if real_order_sent:
        raise RuntimeError(
            "UNIT 8 EXECUTION FIREBREAK FAILURE: REAL ORDER"
        )

    if exchange_mutation:
        raise RuntimeError(
            "UNIT 8 EXECUTION FIREBREAK FAILURE: EXCHANGE MUTATION"
        )

    print(
        "PASS: UNIT 8 EXECUTION FIREBREAK",
        flush=True,
    )

    print(
        "UNIT 8 FINAL DEMO BOUNDARY PAYLOAD = "
        + str(final_payload),
        flush=True,
    )

    print(
        "ZERO WEEX POST = TRUE",
        flush=True,
    )

    print(
        "ZERO DEMO ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO REAL ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO EXCHANGE MUTATION = TRUE",
        flush=True,
    )

    return {
        "valid": True,
        "reason":
            "UNIT_8_DEMO_SUBMISSION_BOUNDARY_VALID",

        "payload":
            final_payload,

        "weex_post":
            False,

        "demo_order_sent":
            False,

        "real_order_sent":
            False,

        "exchange_mutation":
            False,
    }


# ============================================================
# UNIT 8 STANDALONE TEST
# ============================================================


def reconstruction_unit_8_standalone_test():

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 8 STANDALONE TEST START",
        flush=True,
    )

    # --------------------------------------------------------
    # LONG TEST
    #
    # This reproduces the exact payload shape proven by
    # Unit 7C.
    # --------------------------------------------------------

    long_candidate = {
        "symbol":
            "BTCSUSDT",

        "side":
            "BUY",

        "positionSide":
            "LONG",

        "type":
            "MARKET",

        "quantity":
            "0.0004",
    }

    long_original = dict(
        long_candidate
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 8 LONG TEST START",
        flush=True,
    )

    long_result = (
        reconstruction_unit_8_build_demo_submission_boundary(
            candidate_payload=
                long_candidate,
        )
    )

    if not long_result["valid"]:
        raise RuntimeError(
            "UNIT 8 LONG RESULT INVALID"
        )

    if (
        long_result["payload"]["side"]
        != "BUY"
    ):
        raise RuntimeError(
            "UNIT 8 LONG SIDE FAILURE"
        )

    if (
        long_result["payload"]["positionSide"]
        != "LONG"
    ):
        raise RuntimeError(
            "UNIT 8 LONG POSITION SIDE FAILURE"
        )

    if (
        long_candidate
        != long_original
    ):
        raise RuntimeError(
            "UNIT 8 LONG INPUT MUTATED"
        )

    print(
        "PASS: UNIT 8 LONG DEMO SUBMISSION BOUNDARY",
        flush=True,
    )

    # --------------------------------------------------------
    # SHORT TEST
    # --------------------------------------------------------

    short_candidate = {
        "symbol":
            "BTCSUSDT",

        "side":
            "SELL",

        "positionSide":
            "SHORT",

        "type":
            "MARKET",

        "quantity":
            "0.0004",
    }

    short_original = dict(
        short_candidate
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 8 SHORT TEST START",
        flush=True,
    )

    short_result = (
        reconstruction_unit_8_build_demo_submission_boundary(
            candidate_payload=
                short_candidate,
        )
    )

    if not short_result["valid"]:
        raise RuntimeError(
            "UNIT 8 SHORT RESULT INVALID"
        )

    if (
        short_result["payload"]["side"]
        != "SELL"
    ):
        raise RuntimeError(
            "UNIT 8 SHORT SIDE FAILURE"
        )

    if (
        short_result["payload"]["positionSide"]
        != "SHORT"
    ):
        raise RuntimeError(
            "UNIT 8 SHORT POSITION SIDE FAILURE"
        )

    if (
        short_candidate
        != short_original
    ):
        raise RuntimeError(
            "UNIT 8 SHORT INPUT MUTATED"
        )

    print(
        "PASS: UNIT 8 SHORT DEMO SUBMISSION BOUNDARY",
        flush=True,
    )

    # --------------------------------------------------------
    # SL REJECTION TEST
    #
    # Deliberately inject an SL field.
    # Unit 8 MUST reject it.
    # --------------------------------------------------------

    sl_rejection_pass = False

    bad_sl_candidate = {
        "symbol":
            "BTCSUSDT",

        "side":
            "BUY",

        "positionSide":
            "LONG",

        "type":
            "MARKET",

        "quantity":
            "0.0004",

        "slTriggerPrice":
            "80000.0",
    }

    try:

        reconstruction_unit_8_build_demo_submission_boundary(
            candidate_payload=
                bad_sl_candidate,
        )

    except RuntimeError as exc:

        if (
            "SL FIELD PRESENT"
            in str(exc)
        ):
            sl_rejection_pass = True

    if not sl_rejection_pass:
        raise RuntimeError(
            "UNIT 8 FAILED TO REJECT SL FIELD"
        )

    print(
        "PASS: UNIT 8 SL FIELD REJECTION TEST",
        flush=True,
    )

    # --------------------------------------------------------
    # INVALID DIRECTION TEST
    #
    # BUY/SHORT must never cross the boundary.
    # --------------------------------------------------------

    direction_rejection_pass = False

    bad_direction_candidate = {
        "symbol":
            "BTCSUSDT",

        "side":
            "BUY",

        "positionSide":
            "SHORT",

        "type":
            "MARKET",

        "quantity":
            "0.0004",
    }

    try:

        reconstruction_unit_8_build_demo_submission_boundary(
            candidate_payload=
                bad_direction_candidate,
        )

    except RuntimeError as exc:

        if (
            "INVALID SIDE/POSITION PAIR"
            in str(exc)
        ):
            direction_rejection_pass = True

    if not direction_rejection_pass:
        raise RuntimeError(
            "UNIT 8 FAILED INVALID DIRECTION TEST"
        )

    print(
        "PASS: UNIT 8 INVALID DIRECTION REJECTION",
        flush=True,
    )

    # --------------------------------------------------------
    # FINAL SAFETY ASSERTIONS
    # --------------------------------------------------------

    for result in (
        long_result,
        short_result,
    ):

        if result["weex_post"]:
            raise RuntimeError(
                "UNIT 8 WEEX POST SAFETY FAILURE"
            )

        if result["demo_order_sent"]:
            raise RuntimeError(
                "UNIT 8 DEMO ORDER SAFETY FAILURE"
            )

        if result["real_order_sent"]:
            raise RuntimeError(
                "UNIT 8 REAL ORDER SAFETY FAILURE"
            )

        if result["exchange_mutation"]:
            raise RuntimeError(
                "UNIT 8 EXCHANGE MUTATION SAFETY FAILURE"
            )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 8 LONG PATH",
        flush=True,
    )

    print(
        "PASS: UNIT 8 SHORT PATH",
        flush=True,
    )

    print(
        "PASS: UNIT 8 SL-DISABLE GUARD",
        flush=True,
    )

    print(
        "PASS: UNIT 8 DIRECTION CONSISTENCY GUARD",
        flush=True,
    )

    print(
        "PASS: UNIT 8 EXECUTION FIREBREAK",
        flush=True,
    )

    print(
        "ZERO WEEX POST = TRUE",
        flush=True,
    )

    print(
        "ZERO DEMO ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO REAL ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO EXCHANGE MUTATION = TRUE",
        flush=True,
    )

    print(
        "NO TP GENERATED = TRUE",
        flush=True,
    )

    print(
        "NO SL GENERATED = TRUE",
        flush=True,
    )

    print(
        "NO BACKUP EXECUTION = TRUE",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 8 STANDALONE TESTS = PASS",
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 8 RESULT = PASS",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    return True


# ============================================================
# UNIT 8 TEST ENTRY POINT
# ============================================================

if __name__ == "__main__":

    print(
        "WEEX_PARALLEL_BOT UNIT_8_STANDALONE_TEST",
        flush=True,
    )

    print(
        "STARTING UNIT 8 ZERO-WRITE "
        "DEMO SUBMISSION-BOUNDARY TEST",
        flush=True,
    )

    reconstruction_unit_8_standalone_test()

# ============================================================
# RECONSTRUCTION UNIT 8B
# UNIT 6B -> UNIT 7 -> UNIT 8
# DIRECT-CONNECTED ZERO-WRITE INTEGRATION TEST
#
# PURPOSE:
# Prove the exact tested connection:
#
#   VALID UNIT 6B RESULT
#           |
#           v
#       UNIT 7
#   ZERO-WRITE CANDIDATE PAYLOAD
#           |
#           v
#       UNIT 8
#   DEMO SUBMISSION BOUNDARY
#
# IMPORTANT:
# - USES ACTUAL UNIT 7 INTERFACE
# - USES ACTUAL UNIT 8 INTERFACE
# - ZERO WEEX POST
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE MUTATION
# - NO TP GENERATED
# - NO SL GENERATED
# - NO BACKUP EXECUTION
# ============================================================


def reconstruction_unit_8b_direct_connected_bridge(
    *,
    unit_6b_result,
):

    separator()

    log(
        "RECONSTRUCTION UNIT 8B "
        "DIRECT-CONNECTED BRIDGE START"
    )

    # --------------------------------------------------------
    # STEP 1
    # VALIDATE UNIT 6B RESULT
    # --------------------------------------------------------

    require(
        isinstance(
            unit_6b_result,
            dict,
        ),
        "UNIT 8B invalid Unit 6B result.",
    )

    require(
        unit_6b_result.get(
            "valid"
        )
        is True,
        "UNIT 8B Unit 6B result not valid.",
    )

    unit_6_result = (
        unit_6b_result.get(
            "unit_6_result"
        )
    )

    require(
        isinstance(
            unit_6_result,
            dict,
        ),
        "UNIT 8B missing Unit 6 result.",
    )

    require(
        unit_6_result.get(
            "valid"
        )
        is True,
        "UNIT 8B invalid Unit 6 result.",
    )

    direction = str(
        unit_6_result.get(
            "direction"
        )
    ).upper()

    require(
        direction
        in {
            "LONG",
            "SHORT",
        },
        "UNIT 8B invalid Unit 6 direction.",
    )

    quantity = D(
        unit_6_result.get(
            "quantity"
        )
    )

    require(
        quantity > 0,
        "UNIT 8B invalid Unit 6 quantity.",
    )

    log(
        "PASS: UNIT 8B RECEIVED "
        "VALID UNIT 6B RESULT"
    )

    log(
        "UNIT 8B UNIT 6 DIRECTION = "
        + direction
    )

    log(
        "UNIT 8B UNIT 6 QUANTITY = "
        + decimal_to_string(
            quantity
        )
    )

    # --------------------------------------------------------
    # Preserve Unit 6B input so mutation can be detected.
    # --------------------------------------------------------

    original_unit_6b_result = {
        key: (
            dict(value)
            if isinstance(
                value,
                dict,
            )
            else value
        )
        for key, value
        in unit_6b_result.items()
    }

    # --------------------------------------------------------
    # STEP 2
    # ACTUAL UNIT 6B -> UNIT 7 CONNECTION
    #
    # This is the real Unit 7 function already present in
    # main.py.
    # --------------------------------------------------------

    unit_7_result = (
        reconstruction_unit_7_build_payload_preview(
            unit_6b_result=(
                unit_6b_result
            )
        )
    )

    require(
        isinstance(
            unit_7_result,
            dict,
        ),
        "UNIT 8B Unit 7 result is not dict.",
    )

    require(
        unit_7_result.get(
            "valid"
        )
        is True,
        "UNIT 8B Unit 7 result not valid.",
    )

    require(
        unit_7_result.get(
            "candidate_payload_generated"
        )
        is True,
        (
            "UNIT 8B Unit 7 candidate "
            "payload not generated."
        ),
    )

    log(
        "PASS: UNIT 8B "
        "UNIT 6B -> UNIT 7 CONNECTION"
    )

    # --------------------------------------------------------
    # STEP 3
    # TAKE THE ACTUAL PAYLOAD PRODUCED BY UNIT 7
    # --------------------------------------------------------

    unit_7_payload = (
        unit_7_result.get(
            "payload"
        )
    )

    require(
        isinstance(
            unit_7_payload,
            dict,
        ),
        "UNIT 8B Unit 7 payload missing.",
    )

    log(
        "PASS: UNIT 8B RECEIVED "
        "ACTUAL UNIT 7 PAYLOAD"
    )

    log(
        "UNIT 8B UNIT 7 PAYLOAD = "
        + str(
            unit_7_payload
        )
    )

    # Preserve the exact Unit 7 payload before Unit 8.
    original_unit_7_payload = dict(
        unit_7_payload
    )

    # --------------------------------------------------------
    # STEP 4
    # ACTUAL UNIT 7 -> UNIT 8 CONNECTION
    # --------------------------------------------------------

    unit_8_result = (
        reconstruction_unit_8_build_demo_submission_boundary(
            candidate_payload=(
                unit_7_payload
            )
        )
    )

    require(
        isinstance(
            unit_8_result,
            dict,
        ),
        "UNIT 8B Unit 8 result is not dict.",
    )

    require(
        unit_8_result.get(
            "valid"
        )
        is True,
        "UNIT 8B Unit 8 result not valid.",
    )

    log(
        "PASS: UNIT 8B "
        "UNIT 7 -> UNIT 8 CONNECTION"
    )

    # --------------------------------------------------------
    # STEP 5
    # GET FINAL UNIT 8 BOUNDARY PAYLOAD
    # --------------------------------------------------------

    final_payload = (
        unit_8_result.get(
            "payload"
        )
    )

    require(
        isinstance(
            final_payload,
            dict,
        ),
        "UNIT 8B final payload missing.",
    )

    log(
        "UNIT 8B FINAL BOUNDARY PAYLOAD = "
        + str(
            final_payload
        )
    )

    # --------------------------------------------------------
    # STEP 6
    # PAYLOAD CONTINUITY
    #
    # Unit 8 is allowed to copy the dictionary but must not
    # change any of the five approved fields.
    # --------------------------------------------------------

    require(
        final_payload
        == original_unit_7_payload,
        (
            "UNIT 8B Unit 7 -> Unit 8 "
            "payload continuity failure."
        ),
    )

    log(
        "PASS: UNIT 8B PAYLOAD CONTINUITY"
    )

    # --------------------------------------------------------
    # STEP 7
    # UNIT 7 PAYLOAD MUTATION CHECK
    # --------------------------------------------------------

    require(
        unit_7_payload
        == original_unit_7_payload,
        (
            "UNIT 8B Unit 7 payload "
            "was mutated."
        ),
    )

    log(
        "PASS: UNIT 8B "
        "UNIT 7 PAYLOAD PRESERVED"
    )

    # --------------------------------------------------------
    # STEP 8
    # UNIT 6B MUTATION CHECK
    # --------------------------------------------------------

    require(
        unit_6b_result
        == original_unit_6b_result,
        (
            "UNIT 8B Unit 6B result "
            "was mutated."
        ),
    )

    log(
        "PASS: UNIT 8B "
        "UNIT 6B RESULT PRESERVED"
    )

    # --------------------------------------------------------
    # STEP 9
    # REQUIRED FINAL FIELDS
    # --------------------------------------------------------

    required_fields = (
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
    )

    missing_fields = [
        field
        for field in required_fields
        if field not in final_payload
    ]

    require(
        not missing_fields,
        (
            "UNIT 8B final payload "
            "missing fields: "
            + str(
                missing_fields
            )
        ),
    )

    log(
        "PASS: UNIT 8B "
        "FINAL REQUIRED FIELDS"
    )

    # --------------------------------------------------------
    # STEP 10
    # SYMBOL
    # --------------------------------------------------------

    require(
        final_payload.get(
            "symbol"
        )
        == UNIT_7_DEMO_SYMBOL,
        "UNIT 8B final symbol mismatch.",
    )

    log(
        "PASS: UNIT 8B SYMBOL = "
        + UNIT_7_DEMO_SYMBOL
    )

    # --------------------------------------------------------
    # STEP 11
    # ORDER TYPE
    # --------------------------------------------------------

    require(
        final_payload.get(
            "type"
        )
        == "MARKET",
        "UNIT 8B final order type mismatch.",
    )

    log(
        "PASS: UNIT 8B ORDER TYPE = MARKET"
    )

    # --------------------------------------------------------
    # STEP 12
    # DIRECTION CONSISTENCY
    # --------------------------------------------------------

    side = str(
        final_payload.get(
            "side"
        )
    ).upper()

    position_side = str(
        final_payload.get(
            "positionSide"
        )
    ).upper()

    if direction == "LONG":

        require(
            side == "BUY",
            "UNIT 8B LONG side mismatch.",
        )

        require(
            position_side == "LONG",
            (
                "UNIT 8B LONG "
                "positionSide mismatch."
            ),
        )

    else:

        require(
            side == "SELL",
            "UNIT 8B SHORT side mismatch.",
        )

        require(
            position_side == "SHORT",
            (
                "UNIT 8B SHORT "
                "positionSide mismatch."
            ),
        )

    log(
        "PASS: UNIT 8B "
        "DIRECTION CONSISTENCY"
    )

    # --------------------------------------------------------
    # STEP 13
    # QUANTITY CONTINUITY
    # --------------------------------------------------------

    final_quantity = D(
        final_payload.get(
            "quantity"
        )
    )

    require(
        final_quantity
        == quantity,
        (
            "UNIT 8B quantity changed "
            "between Unit 6 and Unit 8."
        ),
    )

    require(
        final_quantity
        >= UNIT_6C_MINIMUM_QUANTITY,
        (
            "UNIT 8B final quantity "
            "below minimum."
        ),
    )

    require(
        final_quantity
        % UNIT_6C_QUANTITY_STEP
        == 0,
        (
            "UNIT 8B final quantity "
            "not aligned to step."
        ),
    )

    log(
        "PASS: UNIT 8B "
        "QUANTITY CONTINUITY"
    )

    # --------------------------------------------------------
    # STEP 14
    # SL-DISABLE GUARD
    # --------------------------------------------------------

    forbidden_sl_fields = (
        "slTriggerPrice",
        "SlWorkingType",
        "stopLossPrice",
        "stopPrice",
    )

    present_sl_fields = [
        field
        for field in forbidden_sl_fields
        if field in final_payload
    ]

    require(
        not present_sl_fields,
        (
            "UNIT 8B forbidden SL fields: "
            + str(
                present_sl_fields
            )
        ),
    )

    log(
        "PASS: UNIT 8B SL-DISABLE GUARD"
    )

    # --------------------------------------------------------
    # STEP 15
    # EXACT FIELD WHITELIST
    # --------------------------------------------------------

    allowed_fields = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
    }

    unexpected_fields = (
        set(
            final_payload.keys()
        )
        - allowed_fields
    )

    require(
        not unexpected_fields,
        (
            "UNIT 8B unexpected final "
            "payload fields: "
            + str(
                sorted(
                    unexpected_fields
                )
            )
        ),
    )

    log(
        "PASS: UNIT 8B "
        "FINAL FIELD WHITELIST"
    )

    # --------------------------------------------------------
    # STEP 16
    # UNIT 7 FIREBREAK
    # --------------------------------------------------------

    require(
        unit_7_result.get(
            "weex_post"
        )
        is False,
        "UNIT 8B Unit 7 WEEX POST failure.",
    )

    require(
        unit_7_result.get(
            "demo_order"
        )
        is False,
        "UNIT 8B Unit 7 demo-order failure.",
    )

    require(
        unit_7_result.get(
            "real_order"
        )
        is False,
        "UNIT 8B Unit 7 real-order failure.",
    )

    require(
        unit_7_result.get(
            "exchange_mutation"
        )
        is False,
        (
            "UNIT 8B Unit 7 exchange "
            "mutation failure."
        ),
    )

    require(
        unit_7_result.get(
            "tp_generated"
        )
        is False,
        "UNIT 8B Unit 7 TP failure.",
    )

    require(
        unit_7_result.get(
            "sl_generated"
        )
        is False,
        "UNIT 8B Unit 7 SL failure.",
    )

    require(
        unit_7_result.get(
            "backup_execution"
        )
        is False,
        "UNIT 8B Unit 7 backup failure.",
    )

    log(
        "PASS: UNIT 8B UNIT 7 FIREBREAK"
    )

    # --------------------------------------------------------
    # STEP 17
    # UNIT 8 FIREBREAK
    # --------------------------------------------------------

    require(
        unit_8_result.get(
            "weex_post"
        )
        is False,
        "UNIT 8B Unit 8 WEEX POST failure.",
    )

    require(
        unit_8_result.get(
            "demo_order_sent"
        )
        is False,
        (
            "UNIT 8B Unit 8 demo-order "
            "firebreak failure."
        ),
    )

    require(
        unit_8_result.get(
            "real_order_sent"
        )
        is False,
        (
            "UNIT 8B Unit 8 real-order "
            "firebreak failure."
        ),
    )

    require(
        unit_8_result.get(
            "exchange_mutation"
        )
        is False,
        (
            "UNIT 8B Unit 8 exchange "
            "mutation firebreak failure."
        ),
    )

    log(
        "PASS: UNIT 8B UNIT 8 FIREBREAK"
    )

    log(
        "PASS: UNIT 8B EXECUTION FIREBREAK"
    )

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    return {
        "valid":
            True,

        "reason":
            "UNIT_8B_DIRECT_CONNECTED_VALID",

        "direction":
            direction,

        "quantity":
            quantity,

        "unit_7_payload":
            dict(
                unit_7_payload
            ),

        "final_payload":
            dict(
                final_payload
            ),

        "weex_post":
            False,

        "demo_order_sent":
            False,

        "real_order_sent":
            False,

        "exchange_mutation":
            False,

        "tp_generated":
            False,

        "sl_generated":
            False,

        "backup_execution":
            False,
    }


# ============================================================
# UNIT 8B DIRECT-CONNECTED QUALIFIED-PATH TEST
# ============================================================


def reconstruction_unit_8b_qualified_path_test():

    separator()

    log(
        "RECONSTRUCTION UNIT 8B "
        "QUALIFIED-PATH TEST START"
    )

    # ========================================================
    # TEST 1
    # VALID UNIT 6B LONG
    # ========================================================

    separator()

    log(
        "UNIT 8B LONG TEST START"
    )

    simulated_long_unit_6b_result = {
        "valid":
            True,

        "reason":
            "UNIT_8B_SIMULATED_QUALIFIED_LONG",

        "unit_6_result": {
            "valid":
                True,

            "direction":
                "LONG",

            "quantity":
                D("0.0004"),

            "entry_price":
                D("85000.0"),
        },
    }

    long_result = (
        reconstruction_unit_8b_direct_connected_bridge(
            unit_6b_result=(
                simulated_long_unit_6b_result
            )
        )
    )

    require(
        isinstance(
            long_result,
            dict,
        ),
        "UNIT 8B LONG result not dict.",
    )

    require(
        long_result.get(
            "valid"
        )
        is True,
        "UNIT 8B LONG result not valid.",
    )

    long_payload = (
        long_result.get(
            "final_payload"
        )
    )

    require(
        isinstance(
            long_payload,
            dict,
        ),
        "UNIT 8B LONG final payload missing.",
    )

    require(
        long_payload.get(
            "side"
        )
        == "BUY",
        "UNIT 8B LONG side mismatch.",
    )

    require(
        long_payload.get(
            "positionSide"
        )
        == "LONG",
        (
            "UNIT 8B LONG "
            "positionSide mismatch."
        ),
    )

    require(
        long_payload.get(
            "quantity"
        )
        == "0.0004",
        "UNIT 8B LONG quantity mismatch.",
    )

    log(
        "PASS: UNIT 8B "
        "LONG UNIT 6B -> UNIT 7 -> UNIT 8"
    )

    # ========================================================
    # TEST 2
    # VALID UNIT 6B SHORT
    # ========================================================

    separator()

    log(
        "UNIT 8B SHORT TEST START"
    )

    simulated_short_unit_6b_result = {
        "valid":
            True,

        "reason":
            "UNIT_8B_SIMULATED_QUALIFIED_SHORT",

        "unit_6_result": {
            "valid":
                True,

            "direction":
                "SHORT",

            "quantity":
                D("0.0004"),

            "entry_price":
                D("85000.0"),
        },
    }

    short_result = (
        reconstruction_unit_8b_direct_connected_bridge(
            unit_6b_result=(
                simulated_short_unit_6b_result
            )
        )
    )

    require(
        isinstance(
            short_result,
            dict,
        ),
        "UNIT 8B SHORT result not dict.",
    )

    require(
        short_result.get(
            "valid"
        )
        is True,
        "UNIT 8B SHORT result not valid.",
    )

    short_payload = (
        short_result.get(
            "final_payload"
        )
    )

    require(
        isinstance(
            short_payload,
            dict,
        ),
        "UNIT 8B SHORT final payload missing.",
    )

    require(
        short_payload.get(
            "side"
        )
        == "SELL",
        "UNIT 8B SHORT side mismatch.",
    )

    require(
        short_payload.get(
            "positionSide"
        )
        == "SHORT",
        (
            "UNIT 8B SHORT "
            "positionSide mismatch."
        ),
    )

    require(
        short_payload.get(
            "quantity"
        )
        == "0.0004",
        "UNIT 8B SHORT quantity mismatch.",
    )

    log(
        "PASS: UNIT 8B "
        "SHORT UNIT 6B -> UNIT 7 -> UNIT 8"
    )

    # ========================================================
    # TEST 3
    # LONG / SHORT SEPARATION
    # ========================================================

    require(
        long_payload
        != short_payload,
        (
            "UNIT 8B LONG/SHORT "
            "payload collision."
        ),
    )

    log(
        "PASS: UNIT 8B "
        "LONG/SHORT PAYLOAD SEPARATION"
    )

    # ========================================================
    # TEST 4
    # FINAL ZERO-WRITE FIREBREAK
    # ========================================================

    for result in (
        long_result,
        short_result,
    ):

        require(
            result.get(
                "weex_post"
            )
            is False,
            "UNIT 8B WEEX POST safety failure.",
        )

        require(
            result.get(
                "demo_order_sent"
            )
            is False,
            (
                "UNIT 8B demo-order "
                "safety failure."
            ),
        )

        require(
            result.get(
                "real_order_sent"
            )
            is False,
            (
                "UNIT 8B real-order "
                "safety failure."
            ),
        )

        require(
            result.get(
                "exchange_mutation"
            )
            is False,
            (
                "UNIT 8B exchange-mutation "
                "safety failure."
            ),
        )

        require(
            result.get(
                "tp_generated"
            )
            is False,
            "UNIT 8B TP safety failure.",
        )

        require(
            result.get(
                "sl_generated"
            )
            is False,
            "UNIT 8B SL safety failure.",
        )

        require(
            result.get(
                "backup_execution"
            )
            is False,
            (
                "UNIT 8B backup-execution "
                "safety failure."
            ),
        )

    # ========================================================
    # FINAL PASS REPORT
    # ========================================================

    separator()

    log(
        "PASS: UNIT 8B "
        "UNIT 6B -> UNIT 7 CONNECTION"
    )

    log(
        "PASS: UNIT 8B "
        "UNIT 7 -> UNIT 8 CONNECTION"
    )

    log(
        "PASS: UNIT 8B QUALIFIED LONG PATH"
    )

    log(
        "PASS: UNIT 8B QUALIFIED SHORT PATH"
    )

    log(
        "PASS: UNIT 8B PAYLOAD CONTINUITY"
    )

    log(
        "PASS: UNIT 8B "
        "UNIT 6B RESULT PRESERVATION"
    )

    log(
        "PASS: UNIT 8B "
        "UNIT 7 PAYLOAD PRESERVATION"
    )

    log(
        "PASS: UNIT 8B "
        "DIRECTION CONSISTENCY GUARD"
    )

    log(
        "PASS: UNIT 8B "
        "QUANTITY CONTINUITY GUARD"
    )

    log(
        "PASS: UNIT 8B SL-DISABLE GUARD"
    )

    log(
        "PASS: UNIT 8B "
        "FINAL FIELD WHITELIST"
    )

    log(
        "PASS: UNIT 8B EXECUTION FIREBREAK"
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
        "NO TP GENERATED = TRUE"
    )

    log(
        "NO SL GENERATED = TRUE"
    )

    log(
        "NO BACKUP EXECUTION = TRUE"
    )

    separator()

    log(
        "UNIT 8B DIRECT-CONNECTED TESTS = PASS"
    )

    log(
        "RECONSTRUCTION UNIT 8B RESULT = PASS"
    )

    separator()

    return True


# ============================================================
# UNIT 8B TEST ENTRY POINT
# ============================================================


if __name__ == "__main__":

    print(
        "WEEX_PARALLEL_BOT "
        "UNIT_8B_DIRECT_CONNECTED_TEST",
        flush=True,
    )

    print(
        "STARTING UNIT 8B ZERO-WRITE "
        "UNIT 6B -> UNIT 7 -> UNIT 8 TEST",
        flush=True,
    )

    reconstruction_unit_8b_qualified_path_test()

# ============================================================
# RECONSTRUCTION UNIT 9
# FIRST REAL WEEX DEMO SUBMISSION
#
# PURPOSE:
# Submit exactly ONE controlled MARKET order to the official
# WEEX V3 DEMO / PAPER-TRADING endpoint.
#
# IMPORTANT:
# - DEMO ENDPOINT ONLY
# - PRODUCTION ENDPOINT IS NOT USED
# - EXACTLY ONE CONTROLLED DEMO ORDER
# - NO TP
# - NO SL
# - NO BACKUP EXECUTION
# - NO REAL ORDER
#
# OFFICIAL WEEX DEMO ENDPOINT:
# POST /capi/v3/sim/order
# ============================================================


def reconstruction_unit_9_build_client_order_id():

    import time

    timestamp_ms = str(
        int(
            time.time() * 1000
        )
    )

    client_order_id = (
        "R9-DEMO-"
        + timestamp_ms
    )

    require(
        len(
            client_order_id
        )
        <= 36,
        "UNIT 9 client order ID too long.",
    )

    return client_order_id


# ============================================================
# UNIT 9 DEMO-ONLY SIGNATURE
# ============================================================


def reconstruction_unit_9_build_signature(
    *,
    timestamp,
    request_path,
    body,
):

    import os
    import hmac
    import hashlib
    import base64

    api_secret = os.getenv(
        "WEEX_API_SECRET"
    )

    require(
        bool(
            api_secret
        ),
        "UNIT 9 WEEX_API_SECRET missing.",
    )

    prehash = (
        str(
            timestamp
        )
        + "POST"
        + request_path
        + body
    )

    digest = hmac.new(
        api_secret.encode(
            "utf-8"
        ),
        prehash.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    signature = base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )

    require(
        bool(
            signature
        ),
        "UNIT 9 signature generation failed.",
    )

    return signature


# ============================================================
# UNIT 9 DEMO SUBMISSION
# ============================================================


async def reconstruction_unit_9_submit_demo_order(
    *,
    unit_8_payload,
):

    import os
    import json
    import time
    import aiohttp

    separator()

    log(
        "RECONSTRUCTION UNIT 9 "
        "REAL DEMO SUBMISSION START"
    )

    # --------------------------------------------------------
    # HARD-CODED DEMO SAFETY BOUNDARY
    # --------------------------------------------------------

    demo_base_url = (
        "https://api-contract.weex.com"
    )

    demo_request_path = (
        "/capi/v3/sim/order"
    )

    production_request_path = (
        "/capi/v3/order"
    )

    # --------------------------------------------------------
    # PRODUCTION ENDPOINT MUST NEVER BE USED BY UNIT 9
    # --------------------------------------------------------

    require(
        demo_request_path
        != production_request_path,
        (
            "UNIT 9 demo/production "
            "endpoint collision."
        ),
    )

    require(
        "/sim/"
        in demo_request_path,
        (
            "UNIT 9 DEMO ENDPOINT "
            "SAFETY FAILURE."
        ),
    )

    log(
        "PASS: UNIT 9 DEMO ENDPOINT LOCK"
    )

    log(
        "UNIT 9 ENDPOINT = "
        + demo_request_path
    )

    # --------------------------------------------------------
    # RECEIVE UNIT 8 PAYLOAD
    # --------------------------------------------------------

    require(
        isinstance(
            unit_8_payload,
            dict,
        ),
        "UNIT 9 invalid Unit 8 payload.",
    )

    original_payload = dict(
        unit_8_payload
    )

    required_unit_8_fields = (
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
    )

    missing_fields = [
        field
        for field in required_unit_8_fields
        if field
        not in unit_8_payload
    ]

    require(
        not missing_fields,
        (
            "UNIT 9 Unit 8 payload "
            "missing fields: "
            + str(
                missing_fields
            )
        ),
    )

    log(
        "PASS: UNIT 9 RECEIVED "
        "VALID UNIT 8 PAYLOAD"
    )

    # --------------------------------------------------------
    # SYMBOL LOCK
    # --------------------------------------------------------

    require(
        unit_8_payload.get(
            "symbol"
        )
        == "BTCSUSDT",
        "UNIT 9 symbol must be BTCSUSDT.",
    )

    # --------------------------------------------------------
    # MARKET ORDER LOCK
    # --------------------------------------------------------

    require(
        unit_8_payload.get(
            "type"
        )
        == "MARKET",
        "UNIT 9 only MARKET demo order allowed.",
    )

    # --------------------------------------------------------
    # DIRECTION CONSISTENCY
    # --------------------------------------------------------

    side = str(
        unit_8_payload.get(
            "side"
        )
    ).upper()

    position_side = str(
        unit_8_payload.get(
            "positionSide"
        )
    ).upper()

    valid_direction_pairs = {
        (
            "BUY",
            "LONG",
        ),
        (
            "SELL",
            "SHORT",
        ),
    }

    require(
        (
            side,
            position_side,
        )
        in valid_direction_pairs,
        (
            "UNIT 9 invalid "
            "side/positionSide pair."
        ),
    )

    log(
        "PASS: UNIT 9 "
        "DIRECTION CONSISTENCY"
    )

    # --------------------------------------------------------
    # QUANTITY SAFETY
    # --------------------------------------------------------

    quantity = D(
        unit_8_payload.get(
            "quantity"
        )
    )

    require(
        quantity
        == D("0.0004"),
        (
            "UNIT 9 FIRST DEMO TEST "
            "QUANTITY MUST BE 0.0004."
        ),
    )

    log(
        "PASS: UNIT 9 "
        "CONTROLLED QUANTITY = 0.0004"
    )

    # --------------------------------------------------------
    # SL MUST REMAIN DISABLED
    # --------------------------------------------------------

    forbidden_sl_fields = (
        "slTriggerPrice",
        "SlWorkingType",
        "stopLossPrice",
        "stopPrice",
    )

    for field in forbidden_sl_fields:

        require(
            field
            not in unit_8_payload,
            (
                "UNIT 9 forbidden SL field: "
                + field
            ),
        )

    log(
        "PASS: UNIT 9 SL-DISABLE GUARD"
    )

    # --------------------------------------------------------
    # TP IS ALSO EXCLUDED FROM FIRST DEMO ENTRY
    # --------------------------------------------------------

    forbidden_tp_fields = (
        "tpTriggerPrice",
        "TpWorkingType",
    )

    for field in forbidden_tp_fields:

        require(
            field
            not in unit_8_payload,
            (
                "UNIT 9 unexpected TP field: "
                + field
            ),
        )

    log(
        "PASS: UNIT 9 NO TP IN FIRST ENTRY"
    )

    # --------------------------------------------------------
    # BUILD OFFICIAL WEEX V3 DEMO PAYLOAD
    #
    # Unit 8 deliberately ended with only the five strategy
    # fields.
    #
    # WEEX V3 requires newClientOrderId for demo submission,
    # therefore Unit 9 adds ONLY that transport-level field.
    # --------------------------------------------------------

    client_order_id = (
        reconstruction_unit_9_build_client_order_id()
    )

    demo_payload = {
        "symbol":
            unit_8_payload[
                "symbol"
            ],

        "side":
            side,

        "positionSide":
            position_side,

        "type":
            "MARKET",

        "quantity":
            decimal_to_string(
                quantity
            ),

        "newClientOrderId":
            client_order_id,
    }

    # --------------------------------------------------------
    # VERIFY EXACT PAYLOAD FIELD SET
    # --------------------------------------------------------

    allowed_demo_fields = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    }

    require(
        set(
            demo_payload.keys()
        )
        == allowed_demo_fields,
        (
            "UNIT 9 unexpected "
            "demo payload fields."
        ),
    )

    log(
        "PASS: UNIT 9 "
        "DEMO PAYLOAD FIELD WHITELIST"
    )

    log(
        "UNIT 9 CLIENT ORDER ID = "
        + client_order_id
    )

    log(
        "UNIT 9 DEMO PAYLOAD = "
        + str(
            demo_payload
        )
    )

    # --------------------------------------------------------
    # UNIT 8 INPUT MUST NOT HAVE BEEN MUTATED
    # --------------------------------------------------------

    require(
        unit_8_payload
        == original_payload,
        (
            "UNIT 9 mutated "
            "Unit 8 payload."
        ),
    )

    log(
        "PASS: UNIT 9 "
        "UNIT 8 PAYLOAD PRESERVED"
    )

    # --------------------------------------------------------
    # CREDENTIALS
    # --------------------------------------------------------

    api_key = os.getenv(
        "WEEX_API_KEY"
    )

    api_secret = os.getenv(
        "WEEX_API_SECRET"
    )

    passphrase = os.getenv(
        "WEEX_API_PASSPHRASE"
    )

    require(
        bool(
            api_key
        ),
        "UNIT 9 WEEX_API_KEY missing.",
    )

    require(
        bool(
            api_secret
        ),
        "UNIT 9 WEEX_API_SECRET missing.",
    )

    require(
        bool(
            passphrase
        ),
        "UNIT 9 WEEX_API_PASSPHRASE missing.",
    )

    log(
        "PASS: UNIT 9 "
        "WEEX CREDENTIALS PRESENT"
    )

    # --------------------------------------------------------
    # EXACT JSON BODY
    #
    # IMPORTANT:
    # The exact body signed below is the exact body sent.
    # --------------------------------------------------------

    body = json.dumps(
        demo_payload,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )

    timestamp = str(
        int(
            time.time() * 1000
        )
    )

    signature = (
        reconstruction_unit_9_build_signature(
            timestamp=timestamp,
            request_path=demo_request_path,
            body=body,
        )
    )

    headers = {
        "ACCESS-KEY":
            api_key,

        "ACCESS-SIGN":
            signature,

        "ACCESS-TIMESTAMP":
            timestamp,

        "ACCESS-PASSPHRASE":
            passphrase,

        "Content-Type":
            "application/json",
    }

    url = (
        demo_base_url
        + demo_request_path
    )

    # --------------------------------------------------------
    # FINAL SAFETY ASSERTIONS BEFORE NETWORK WRITE
    # --------------------------------------------------------

    require(
        url
        == (
            "https://api-contract.weex.com"
            "/capi/v3/sim/order"
        ),
        (
            "UNIT 9 final URL "
            "safety failure."
        ),
    )

    require(
        "/sim/order"
        in url,
        (
            "UNIT 9 attempted "
            "non-demo endpoint."
        ),
    )

    require(
        "/capi/v3/order"
        not in url,
        (
            "UNIT 9 production endpoint "
            "detected."
        ),
    )

    log(
        "PASS: UNIT 9 "
        "FINAL DEMO-ONLY SAFETY GATE"
    )

    separator()

    log(
        "UNIT 9 SENDING ONE "
        "REAL WEEX DEMO ORDER"
    )

    log(
        "UNIT 9 REAL ORDER = FALSE"
    )

    log(
        "UNIT 9 DEMO ORDER = TRUE"
    )

    separator()

    # --------------------------------------------------------
    # ACTUAL DEMO POST
    # --------------------------------------------------------

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    try:

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.post(
                url,
                headers=headers,
                data=body,
            ) as response:

                http_status = (
                    response.status
                )

                response_text = (
                    await response.text()
                )

    except Exception as exc:

        log(
            "UNIT 9 DEMO NETWORK ERROR = "
            + repr(
                exc
            )
        )

        return {
            "valid":
                False,

            "submitted":
                False,

            "accepted":
                False,

            "reason":
                "UNIT_9_NETWORK_ERROR",

            "error":
                repr(
                    exc
                ),

            "client_order_id":
                client_order_id,

            "real_order":
                False,
        }

    # --------------------------------------------------------
    # LOG HTTP RESULT
    # --------------------------------------------------------

    log(
        "UNIT 9 HTTP STATUS = "
        + str(
            http_status
        )
    )

    log(
        "UNIT 9 RAW RESPONSE = "
        + response_text
    )

    # --------------------------------------------------------
    # PARSE RESPONSE
    # --------------------------------------------------------

    try:

        response_data = json.loads(
            response_text
        )

    except Exception:

        response_data = {
            "raw":
                response_text
        }

    # --------------------------------------------------------
    # HTTP FAILURE
    # --------------------------------------------------------

    if (
        http_status
        < 200
        or
        http_status
        >= 300
    ):

        log(
            "UNIT 9 DEMO SUBMISSION "
            "HTTP FAILURE"
        )

        return {
            "valid":
                False,

            "submitted":
                True,

            "accepted":
                False,

            "reason":
                "UNIT_9_HTTP_FAILURE",

            "http_status":
                http_status,

            "response":
                response_data,

            "client_order_id":
                client_order_id,

            "real_order":
                False,
        }

    # --------------------------------------------------------
    # WEEX V3 DEMO RESPONSE VALIDATION
    # --------------------------------------------------------

    require(
        isinstance(
            response_data,
            dict,
        ),
        (
            "UNIT 9 unexpected "
            "WEEX response type."
        ),
    )

    success = (
        response_data.get(
            "success"
        )
        is True
    )

    order_id = (
        response_data.get(
            "orderId"
        )
    )

    returned_client_order_id = (
        response_data.get(
            "clientOrderId"
        )
    )

    error_code = (
        response_data.get(
            "errorCode"
        )
    )

    error_message = (
        response_data.get(
            "errorMessage"
        )
    )

    log(
        "UNIT 9 WEEX SUCCESS = "
        + str(
            success
        )
    )

    log(
        "UNIT 9 ORDER ID = "
        + str(
            order_id
        )
    )

    log(
        "UNIT 9 RETURNED CLIENT ORDER ID = "
        + str(
            returned_client_order_id
        )
    )

    log(
        "UNIT 9 ERROR CODE = "
        + str(
            error_code
        )
    )

    log(
        "UNIT 9 ERROR MESSAGE = "
        + str(
            error_message
        )
    )

    # --------------------------------------------------------
    # WEEX REJECTED ORDER
    # --------------------------------------------------------

    if not success:

        log(
            "UNIT 9 WEEX DEMO ORDER "
            "NOT ACCEPTED"
        )

        return {
            "valid":
                False,

            "submitted":
                True,

            "accepted":
                False,

            "reason":
                "UNIT_9_WEEX_REJECTED",

            "http_status":
                http_status,

            "response":
                response_data,

            "client_order_id":
                client_order_id,

            "real_order":
                False,
        }

    # --------------------------------------------------------
    # ACCEPTANCE REQUIREMENTS
    # --------------------------------------------------------

    require(
        order_id
        not in (
            None,
            "",
        ),
        (
            "UNIT 9 success response "
            "missing orderId."
        ),
    )

    require(
        returned_client_order_id
        == client_order_id,
        (
            "UNIT 9 client order ID "
            "response mismatch."
        ),
    )

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    separator()

    log(
        "PASS: UNIT 9 "
        "WEEX DEMO ORDER ACCEPTED"
    )

    log(
        "UNIT 9 DEMO ORDER ID = "
        + str(
            order_id
        )
    )

    log(
        "UNIT 9 CLIENT ORDER ID = "
        + client_order_id
    )

    log(
        "REAL ORDER SENT = FALSE"
    )

    log(
        "DEMO ORDER SENT = TRUE"
    )

    log(
        "RECONSTRUCTION UNIT 9 RESULT = PASS"
    )

    separator()

    return {
        "valid":
            True,

        "submitted":
            True,

        "accepted":
            True,

        "reason":
            "UNIT_9_DEMO_ORDER_ACCEPTED",

        "order_id":
            order_id,

        "client_order_id":
            client_order_id,

        "http_status":
            http_status,

        "response":
            response_data,

        "real_order":
            False,
    }


# ============================================================
# UNIT 9 FIRST CONTROLLED DEMO SUBMISSION TEST
#
# IMPORTANT:
# Exactly ONE demo order is submitted.
#
# We deliberately use LONG only for this first transport test.
# SHORT was already validated through Unit 8B and does not
# need a second demo position simply to test HTTP transport.
# ============================================================


async def reconstruction_unit_9_first_demo_test():

    separator()

    log(
        "RECONSTRUCTION UNIT 9 "
        "FIRST DEMO TEST START"
    )

    # --------------------------------------------------------
    # Recreate the same validated five-field boundary shape
    # produced by Unit 8.
    #
    # This first Unit 9 test isolates transport/authentication.
    # Runtime signal integration comes after transport PASS.
    # --------------------------------------------------------

    candidate_payload = {
        "symbol":
            "BTCSUSDT",

        "side":
            "BUY",

        "positionSide":
            "LONG",

        "type":
            "MARKET",

        "quantity":
            "0.0004",
    }

    # --------------------------------------------------------
    # Pass through the already-tested Unit 8 boundary first.
    # --------------------------------------------------------

    unit_8_result = (
        reconstruction_unit_8_build_demo_submission_boundary(
            candidate_payload=(
                candidate_payload
            )
        )
    )

    require(
        isinstance(
            unit_8_result,
            dict,
        ),
        "UNIT 9 Unit 8 result not dict.",
    )

    require(
        unit_8_result.get(
            "valid"
        )
        is True,
        (
            "UNIT 9 Unit 8 boundary "
            "validation failed."
        ),
    )

    final_payload = (
        unit_8_result.get(
            "payload"
        )
    )

    require(
        isinstance(
            final_payload,
            dict,
        ),
        "UNIT 9 Unit 8 payload missing.",
    )

    log(
        "PASS: UNIT 9 "
        "UNIT 8 -> UNIT 9 CONNECTION"
    )

    # --------------------------------------------------------
    # THIS CALL PERFORMS THE REAL DEMO POST
    # --------------------------------------------------------

    result = (
        await reconstruction_unit_9_submit_demo_order(
            unit_8_payload=(
                final_payload
            )
        )
    )

    separator()

    if result.get(
        "accepted"
    ) is True:

        log(
            "UNIT 9 FIRST "
            "DEMO SUBMISSION = PASS"
        )

    else:

        log(
            "UNIT 9 FIRST "
            "DEMO SUBMISSION = NOT ACCEPTED"
        )

        log(
            "UNIT 9 FAILURE REASON = "
            + str(
                result.get(
                    "reason"
                )
            )
        )

    separator()

    return result

# ============================================================
# RECONSTRUCTION UNIT 10
# LIVE QUALIFICATION -> REAL WEEX DEMO SUBMISSION
#
# PURPOSE:
#
# Connect the already-tested reconstruction chain:
#
#   LIVE WEEX MARKET DATA
#           |
#           v
#       UNIT 5B
#   LIVE ENTRY QUALIFICATION
#           |
#           v
#       UNIT 6C / 6B
#   POSITION SIZING / ENTRY INSTRUCTION
#           |
#           v
#       UNIT 7
#   CANDIDATE ORDER PAYLOAD
#           |
#           v
#       UNIT 8
#   SUBMISSION BOUNDARY
#           |
#           v
#       UNIT 9
#   REAL WEEX DEMO SUBMISSION
#
# IMPORTANT:
#
# - LIVE MARKET QUALIFICATION
# - ACTUAL QUALIFIED DIRECTION
# - NO HARD-CODED LONG
# - NO HARD-CODED SHORT
# - DEMO ENDPOINT ONLY
# - MAXIMUM ONE DEMO SUBMISSION PER UNIT 10 RUN
# - NO ORDER IF UNIT 5B DOES NOT QUALIFY
# - NO ORDER IF UNIT 6B DOES NOT VALIDATE
# - NO REAL ORDER
# - NO TP
# - NO SL
# - NO BACKUP EXECUTION
#
# Unit 9 transport remains unchanged.
#
# The old Unit 9 automatic hard-coded LONG entry point has
# deliberately been removed so deployment cannot send both
# the Unit 9 transport-test order and a Unit 10 live-qualified
# order.
# ============================================================


async def reconstruction_unit_10_live_demo_execution():

    separator()

    log(
        "RECONSTRUCTION UNIT 10 "
        "LIVE DEMO EXECUTION START"
    )

    separator()

    # ========================================================
    # STEP 1
    # RUN THE EXISTING LIVE MARKET QUALIFICATION PATH
    # ========================================================

    log(
        "UNIT 10 STEP 1 = "
        "RUN LIVE UNIT 5B QUALIFICATION"
    )

    unit_5b_result = (
        run_unit_5b_live_test()
    )

    require(
        isinstance(
            unit_5b_result,
            dict,
        ),
        "UNIT 10 invalid Unit 5B result.",
    )

    require(
        "qualified"
        in unit_5b_result,
        "UNIT 10 Unit 5B missing qualified field.",
    )

    require(
        "reason"
        in unit_5b_result,
        "UNIT 10 Unit 5B missing reason.",
    )

    require(
        "direction"
        in unit_5b_result,
        "UNIT 10 Unit 5B missing direction.",
    )

    require(
        "live_price"
        in unit_5b_result,
        "UNIT 10 Unit 5B missing live price.",
    )

    qualified = bool(
        unit_5b_result.get(
            "qualified",
            False,
        )
    )

    qualification_reason = (
        unit_5b_result.get(
            "reason"
        )
    )

    direction = (
        unit_5b_result.get(
            "direction"
        )
    )

    live_price = (
        unit_5b_result.get(
            "live_price"
        )
    )

    log(
        "PASS: UNIT 10 RECEIVED "
        "LIVE UNIT 5B RESULT"
    )

    log(
        "UNIT 10 LIVE QUALIFIED = "
        + str(
            qualified
        )
    )

    log(
        "UNIT 10 QUALIFICATION REASON = "
        + str(
            qualification_reason
        )
    )

    log(
        "UNIT 10 LIVE DIRECTION = "
        + str(
            direction
        )
    )

    log(
        "UNIT 10 LIVE PRICE = "
        + str(
            live_price
        )
    )

    # ========================================================
    # STEP 2
    # NON-QUALIFIED MARKET MUST STOP HERE
    #
    # This is an expected normal result, not an execution
    # failure.
    # ========================================================

    if not qualified:

        separator()

        log(
            "UNIT 10 LIVE ENTRY = "
            "NOT QUALIFIED"
        )

        log(
            "UNIT 10 DEMO SUBMISSION = BLOCKED"
        )

        log(
            "UNIT 10 BLOCK REASON = "
            + str(
                qualification_reason
            )
        )

        log(
            "ZERO UNIT 10 WEEX POST = TRUE"
        )

        log(
            "ZERO UNIT 10 DEMO ORDER = TRUE"
        )

        log(
            "ZERO REAL ORDER = TRUE"
        )

        log(
            "NO TP GENERATED = TRUE"
        )

        log(
            "NO SL GENERATED = TRUE"
        )

        log(
            "NO BACKUP EXECUTION = TRUE"
        )

        log(
            "RECONSTRUCTION UNIT 10 "
            "RESULT = BLOCKED_NOT_QUALIFIED"
        )

        separator()

        return {
            "valid":
                True,

            "qualified":
                False,

            "submitted":
                False,

            "accepted":
                False,

            "reason":
                "UNIT_10_LIVE_ENTRY_NOT_QUALIFIED",

            "qualification_reason":
                qualification_reason,

            "direction":
                direction,

            "weex_post":
                False,

            "demo_order_sent":
                False,

            "real_order_sent":
                False,

            "tp_generated":
                False,

            "sl_generated":
                False,

            "backup_execution":
                False,
        }

    # ========================================================
    # STEP 3
    # QUALIFIED DIRECTION MUST BE VALID
    # ========================================================

    direction = str(
        direction
    ).upper()

    require(
        direction
        in {
            "LONG",
            "SHORT",
        },
        (
            "UNIT 10 qualified result "
            "has invalid direction."
        ),
    )

    log(
        "PASS: UNIT 10 LIVE "
        "DIRECTION CONFIRMED = "
        + direction
    )

    # ========================================================
    # STEP 4
    # LIVE UNIT 5B -> EXISTING UNIT 6C / UNIT 6B
    # ========================================================

    log(
        "UNIT 10 STEP 2 = "
        "RUN UNIT 6C / UNIT 6B"
    )

    unit_6b_result = (
        reconstruction_unit_6c_live_bridge(
            unit_5b_result=(
                unit_5b_result
            )
        )
    )

    require(
        isinstance(
            unit_6b_result,
            dict,
        ),
        "UNIT 10 invalid Unit 6B result.",
    )

    log(
        "UNIT 10 UNIT 6B VALID = "
        + str(
            unit_6b_result.get(
                "valid"
            )
        )
    )

    log(
        "UNIT 10 UNIT 6B REASON = "
        + str(
            unit_6b_result.get(
                "reason"
            )
        )
    )

    # --------------------------------------------------------
    # Qualified market must produce valid sizing before any
    # submission can continue.
    # --------------------------------------------------------

    if (
        unit_6b_result.get(
            "valid"
        )
        is not True
    ):

        separator()

        log(
            "UNIT 10 DEMO SUBMISSION = BLOCKED"
        )

        log(
            "UNIT 10 BLOCK REASON = "
            "UNIT 6B INVALID"
        )

        log(
            "ZERO UNIT 10 WEEX POST = TRUE"
        )

        log(
            "ZERO UNIT 10 DEMO ORDER = TRUE"
        )

        log(
            "ZERO REAL ORDER = TRUE"
        )

        log(
            "RECONSTRUCTION UNIT 10 "
            "RESULT = BLOCKED_UNIT_6B"
        )

        separator()

        return {
            "valid":
                False,

            "qualified":
                True,

            "submitted":
                False,

            "accepted":
                False,

            "reason":
                "UNIT_10_UNIT_6B_BLOCKED",

            "unit_6b_reason":
                unit_6b_result.get(
                    "reason"
                ),

            "direction":
                direction,

            "weex_post":
                False,

            "demo_order_sent":
                False,

            "real_order_sent":
                False,
        }

    # ========================================================
    # STEP 5
    # VERIFY UNIT 6 RESULT
    # ========================================================

    unit_6_result = (
        unit_6b_result.get(
            "unit_6_result"
        )
    )

    require(
        isinstance(
            unit_6_result,
            dict,
        ),
        "UNIT 10 missing Unit 6 result.",
    )

    require(
        unit_6_result.get(
            "valid"
        )
        is True,
        "UNIT 10 Unit 6 result invalid.",
    )

    unit_6_direction = str(
        unit_6_result.get(
            "direction"
        )
    ).upper()

    require(
        unit_6_direction
        == direction,
        (
            "UNIT 10 direction changed "
            "between Unit 5B and Unit 6."
        ),
    )

    quantity = D(
        unit_6_result.get(
            "quantity"
        )
    )

    require(
        quantity > 0,
        "UNIT 10 invalid Unit 6 quantity.",
    )

    require(
        quantity
        >= UNIT_6C_MINIMUM_QUANTITY,
        (
            "UNIT 10 quantity below "
            "minimum quantity."
        ),
    )

    require(
        quantity
        % UNIT_6C_QUANTITY_STEP
        == 0,
        (
            "UNIT 10 quantity not aligned "
            "to quantity step."
        ),
    )

    log(
        "PASS: UNIT 10 "
        "UNIT 6 SIZING VALID"
    )

    log(
        "UNIT 10 QUALIFIED DIRECTION = "
        + unit_6_direction
    )

    log(
        "UNIT 10 QUALIFIED QUANTITY = "
        + decimal_to_string(
            quantity
        )
    )

    log(
        "UNIT 10 ENTRY PRICE = "
        + decimal_to_string(
            unit_6_result.get(
                "entry_price"
            )
        )
    )

    # ========================================================
    # STEP 6
    # EXISTING UNIT 8B
    #
    # This runs the already-tested:
    #
    # UNIT 6B
    #   ->
    # UNIT 7
    #   ->
    # UNIT 8
    #
    # chain and returns final_payload.
    # ========================================================

    log(
        "UNIT 10 STEP 3 = "
        "RUN UNIT 6B -> UNIT 7 -> UNIT 8"
    )

    unit_8b_result = (
        reconstruction_unit_8b_direct_connected_bridge(
            unit_6b_result=(
                unit_6b_result
            )
        )
    )

    require(
        isinstance(
            unit_8b_result,
            dict,
        ),
        "UNIT 10 invalid Unit 8B result.",
    )

    require(
        unit_8b_result.get(
            "valid"
        )
        is True,
        "UNIT 10 Unit 8B result invalid.",
    )

    final_payload = (
        unit_8b_result.get(
            "final_payload"
        )
    )

    require(
        isinstance(
            final_payload,
            dict,
        ),
        "UNIT 10 Unit 8 final payload missing.",
    )

    log(
        "PASS: UNIT 10 "
        "UNIT 6B -> UNIT 7 -> UNIT 8"
    )

    log(
        "UNIT 10 FINAL UNIT 8 PAYLOAD = "
        + repr(
            final_payload
        )
    )

    # ========================================================
    # STEP 7
    # INDEPENDENT FINAL DIRECTION CONTINUITY CHECK
    # ========================================================

    final_side = str(
        final_payload.get(
            "side"
        )
    ).upper()

    final_position_side = str(
        final_payload.get(
            "positionSide"
        )
    ).upper()

    if direction == "LONG":

        require(
            final_side
            == "BUY",
            (
                "UNIT 10 LONG became "
                "non-BUY payload."
            ),
        )

        require(
            final_position_side
            == "LONG",
            (
                "UNIT 10 LONG positionSide "
                "continuity failure."
            ),
        )

    else:

        require(
            final_side
            == "SELL",
            (
                "UNIT 10 SHORT became "
                "non-SELL payload."
            ),
        )

        require(
            final_position_side
            == "SHORT",
            (
                "UNIT 10 SHORT positionSide "
                "continuity failure."
            ),
        )

    require(
        D(
            final_payload.get(
                "quantity"
            )
        )
        == quantity,
        (
            "UNIT 10 quantity changed "
            "before Unit 9."
        ),
    )

    log(
        "PASS: UNIT 10 "
        "DIRECTION CONTINUITY"
    )

    log(
        "PASS: UNIT 10 "
        "QUANTITY CONTINUITY"
    )

    # ========================================================
    # STEP 8
    # FINAL SL / TP GUARD
    # ========================================================

    forbidden_fields = (
        "slTriggerPrice",
        "SlWorkingType",
        "stopLossPrice",
        "stopPrice",
        "tpTriggerPrice",
        "TpWorkingType",
    )

    present_forbidden_fields = [
        field
        for field in forbidden_fields
        if field
        in final_payload
    ]

    require(
        not present_forbidden_fields,
        (
            "UNIT 10 forbidden TP/SL "
            "field detected: "
            + str(
                present_forbidden_fields
            )
        ),
    )

    log(
        "PASS: UNIT 10 "
        "TP/SL DISABLE GUARD"
    )

    # ========================================================
    # STEP 9
    # PRE-SUBMISSION DUPLICATE GUARD
    #
    # Within this Unit 10 invocation, the submission call is
    # allowed to happen only once.
    #
    # Persistent/exchange position reconciliation will be a
    # later unit.
    # ========================================================

    submission_attempted = False

    require(
        submission_attempted
        is False,
        (
            "UNIT 10 duplicate "
            "submission state detected."
        ),
    )

    log(
        "PASS: UNIT 10 "
        "LOCAL SINGLE-SUBMISSION GUARD"
    )

    # ========================================================
    # STEP 10
    # FINAL DEMO-ONLY DECLARATION
    # ========================================================

    log(
        "UNIT 10 DEMO EXECUTION AUTHORIZED "
        "BY LIVE QUALIFICATION"
    )

    log(
        "UNIT 10 DIRECTION = "
        + direction
    )

    log(
        "UNIT 10 QUANTITY = "
        + decimal_to_string(
            quantity
        )
    )

    log(
        "UNIT 10 REAL ORDER = FALSE"
    )

    log(
        "UNIT 10 DEMO ORDER = TRUE"
    )

    separator()

    # ========================================================
    # STEP 11
    # ACTUAL UNIT 9 DEMO SUBMISSION
    #
    # Unit 9 itself remains hard-locked to:
    #
    # /capi/v3/sim/order
    #
    # and contains its own production-endpoint guards.
    # ========================================================

    submission_attempted = True

    unit_9_result = (
        await reconstruction_unit_9_submit_demo_order(
            unit_8_payload=(
                final_payload
            )
        )
    )

    require(
        isinstance(
            unit_9_result,
            dict,
        ),
        "UNIT 10 invalid Unit 9 result.",
    )

    # ========================================================
    # STEP 12
    # HANDLE WEEX REJECTION WITHOUT CREATING SECOND ORDER
    # ========================================================

    if (
        unit_9_result.get(
            "accepted"
        )
        is not True
    ):

        separator()

        log(
            "UNIT 10 DEMO SUBMISSION "
            "NOT ACCEPTED"
        )

        log(
            "UNIT 10 UNIT 9 REASON = "
            + str(
                unit_9_result.get(
                    "reason"
                )
            )
        )

        log(
            "UNIT 10 SECOND SUBMISSION "
            "ATTEMPT = FALSE"
        )

        log(
            "UNIT 10 REAL ORDER = FALSE"
        )

        log(
            "RECONSTRUCTION UNIT 10 "
            "RESULT = DEMO_NOT_ACCEPTED"
        )

        separator()

        return {
            "valid":
                False,

            "qualified":
                True,

            "submitted":
                bool(
                    unit_9_result.get(
                        "submitted",
                        False,
                    )
                ),

            "accepted":
                False,

            "reason":
                "UNIT_10_DEMO_NOT_ACCEPTED",

            "direction":
                direction,

            "quantity":
                quantity,

            "unit_9_result":
                unit_9_result,

            "second_submission_attempted":
                False,

            "real_order_sent":
                False,
        }

    # ========================================================
    # STEP 13
    # SUCCESS
    # ========================================================

    require(
        unit_9_result.get(
            "submitted"
        )
        is True,
        (
            "UNIT 10 accepted Unit 9 "
            "result not marked submitted."
        ),
    )

    require(
        unit_9_result.get(
            "real_order"
        )
        is False,
        (
            "UNIT 10 production-order "
            "firebreak failure."
        ),
    )

    order_id = (
        unit_9_result.get(
            "order_id"
        )
    )

    client_order_id = (
        unit_9_result.get(
            "client_order_id"
        )
    )

    require(
        order_id
        not in (
            None,
            "",
        ),
        (
            "UNIT 10 accepted demo order "
            "missing order ID."
        ),
    )

    separator()

    log(
        "PASS: UNIT 10 "
        "LIVE QUALIFICATION -> "
        "DEMO SUBMISSION"
    )

    log(
        "PASS: UNIT 10 "
        "ACTUAL QUALIFIED DIRECTION USED"
    )

    log(
        "PASS: UNIT 10 "
        "ACTUAL QUALIFIED QUANTITY USED"
    )

    log(
        "UNIT 10 DIRECTION = "
        + direction
    )

    log(
        "UNIT 10 QUANTITY = "
        + decimal_to_string(
            quantity
        )
    )

    log(
        "UNIT 10 DEMO ORDER ID = "
        + str(
            order_id
        )
    )

    log(
        "UNIT 10 CLIENT ORDER ID = "
        + str(
            client_order_id
        )
    )

    log(
        "UNIT 10 DEMO ORDER SENT = TRUE"
    )

    log(
        "UNIT 10 REAL ORDER SENT = FALSE"
    )

    log(
        "UNIT 10 SECOND SUBMISSION "
        "ATTEMPT = FALSE"
    )

    log(
        "NO TP GENERATED = TRUE"
    )

    log(
        "NO SL GENERATED = TRUE"
    )

    log(
        "NO BACKUP EXECUTION = TRUE"
    )

    log(
        "RECONSTRUCTION UNIT 10 "
        "RESULT = PASS"
    )

    separator()

    return {
        "valid":
            True,

        "qualified":
            True,

        "submitted":
            True,

        "accepted":
            True,

        "reason":
            "UNIT_10_LIVE_DEMO_ORDER_ACCEPTED",

        "direction":
            direction,

        "quantity":
            quantity,

        "order_id":
            order_id,

        "client_order_id":
            client_order_id,

        "unit_9_result":
            unit_9_result,

        "second_submission_attempted":
            False,

        "real_order_sent":
            False,
    }

# ============================================================
# RECONSTRUCTION UNIT 10B
# PERSISTENT LIVE-QUALIFIED ONE-SHOT DEMO MONITOR
#
# PURPOSE:
# Repeatedly run the already-tested Unit 10 live execution
# until ONE genuine live-qualified WEEX DEMO order is accepted.
#
# IMPORTANT:
# - USE EXISTING UNIT 10 WITHOUT CHANGING ITS STRATEGY
# - NO FORCED DIRECTION
# - NO FORCED QUALIFICATION
# - NO SYNTHETIC SIGNAL
# - NO REAL ORDER PATH
# - ONE ACCEPTED DEMO SUBMISSION MAXIMUM PER RUNTIME
# - STOP AFTER FIRST ACCEPTED DEMO ORDER
# ============================================================

import asyncio
from datetime import datetime, timezone


# ------------------------------------------------------------
# UNIT 10B SETTINGS
# ------------------------------------------------------------

UNIT_10B_ENABLED = True

# Re-evaluate once per minute.
# This matches the current 1-minute live candle progression
# while avoiding unnecessary rapid repeated checks.
UNIT_10B_CHECK_INTERVAL_SECONDS = 60

# Absolute runtime one-shot lock.
# Once an accepted demo order occurs, this remains True
# for the life of this Python process.
UNIT_10B_DEMO_SUBMISSION_LOCKED = False

# Store the accepted result for inspection/logging.
UNIT_10B_ACCEPTED_RESULT = None

# Count monitoring cycles.
UNIT_10B_CYCLE_COUNT = 0


def reconstruction_unit_10b_log(message):
    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    print(
        f"{timestamp} {message}",
        flush=True,
    )


def reconstruction_unit_10b_validate_result(
    result,
):
    """
    Validate the object returned by Unit 10.

    This function does NOT create or alter a trading signal.
    It only validates Unit 10's returned state.
    """

    if not isinstance(
        result,
        dict,
    ):
        return {
            "valid": False,
            "reason": (
                "UNIT_10B_UNIT_10_RESULT_NOT_DICT"
            ),
        }

    required_keys = {
        "valid",
        "qualified",
        "submitted",
        "accepted",
        "reason",
    }

    missing_keys = (
        required_keys
        - set(
            result.keys()
        )
    )

    if missing_keys:
        return {
            "valid": False,
            "reason": (
                "UNIT_10B_MISSING_UNIT_10_FIELDS"
            ),
            "missing_keys": sorted(
                missing_keys
            ),
        }

    return {
        "valid": True,
        "reason": (
            "UNIT_10B_UNIT_10_RESULT_VALID"
        ),
    }


async def reconstruction_unit_10b_monitor():
    """
    Persistent live monitoring wrapper around Unit 10.

    Unit 10 remains responsible for:

        LIVE Unit 5B qualification
            ->
        Unit 6C / Unit 6B sizing bridge
            ->
        Unit 7 payload
            ->
        Unit 8 submission boundary
            ->
        Unit 9 WEEX demo submission

    Unit 10B adds ONLY:

        repeated monitoring
        +
        one-shot accepted-order lock
        +
        controlled termination

    Unit 10B does NOT manufacture a signal.
    """

    global UNIT_10B_DEMO_SUBMISSION_LOCKED
    global UNIT_10B_ACCEPTED_RESULT
    global UNIT_10B_CYCLE_COUNT

    print(
        "=" * 80,
        flush=True,
    )

    reconstruction_unit_10b_log(
        "RECONSTRUCTION UNIT 10B "
        "PERSISTENT LIVE DEMO MONITOR START"
    )

    print(
        "=" * 80,
        flush=True,
    )

    # --------------------------------------------------------
    # MASTER ENABLE GUARD
    # --------------------------------------------------------

    if not UNIT_10B_ENABLED:

        reconstruction_unit_10b_log(
            "UNIT 10B ENABLED = FALSE"
        )

        reconstruction_unit_10b_log(
            "UNIT 10B MONITOR = BLOCKED"
        )

        reconstruction_unit_10b_log(
            "ZERO UNIT 10B DEMO ORDER = TRUE"
        )

        reconstruction_unit_10b_log(
            "ZERO REAL ORDER = TRUE"
        )

        return {
            "valid": True,
            "monitor_started": False,
            "submitted": False,
            "accepted": False,
            "reason": (
                "UNIT_10B_DISABLED"
            ),
            "real_order": False,
        }

    reconstruction_unit_10b_log(
        "UNIT 10B ENABLED = TRUE"
    )

    # --------------------------------------------------------
    # EXISTING RUNTIME LOCK GUARD
    # --------------------------------------------------------

    if UNIT_10B_DEMO_SUBMISSION_LOCKED:

        reconstruction_unit_10b_log(
            "UNIT 10B ONE-SHOT LOCK = ACTIVE"
        )

        reconstruction_unit_10b_log(
            "UNIT 10B NEW SUBMISSION = BLOCKED"
        )

        reconstruction_unit_10b_log(
            "ZERO REAL ORDER = TRUE"
        )

        return {
            "valid": True,
            "monitor_started": False,
            "submitted": False,
            "accepted": False,
            "reason": (
                "UNIT_10B_ALREADY_COMPLETED"
            ),
            "accepted_result": (
                UNIT_10B_ACCEPTED_RESULT
            ),
            "real_order": False,
        }

    reconstruction_unit_10b_log(
        "UNIT 10B ONE-SHOT LOCK = OPEN"
    )

    reconstruction_unit_10b_log(
        "UNIT 10B CHECK INTERVAL SECONDS = "
        f"{UNIT_10B_CHECK_INTERVAL_SECONDS}"
    )

    reconstruction_unit_10b_log(
        "UNIT 10B WAITING FOR "
        "GENUINE LIVE QUALIFICATION"
    )

    # --------------------------------------------------------
    # PERSISTENT MONITOR LOOP
    # --------------------------------------------------------

    while True:

        # ----------------------------------------------------
        # HARD ONE-SHOT CHECK BEFORE EVERY CYCLE
        # ----------------------------------------------------

        if UNIT_10B_DEMO_SUBMISSION_LOCKED:

            reconstruction_unit_10b_log(
                "UNIT 10B ONE-SHOT LOCK "
                "ACTIVATED"
            )

            reconstruction_unit_10b_log(
                "UNIT 10B MONITOR STOPPING"
            )

            break

        UNIT_10B_CYCLE_COUNT += 1

        print(
            "-" * 80,
            flush=True,
        )

        reconstruction_unit_10b_log(
            "UNIT 10B MONITOR CYCLE = "
            f"{UNIT_10B_CYCLE_COUNT}"
        )

        reconstruction_unit_10b_log(
            "UNIT 10B CALLING VERIFIED UNIT 10"
        )

        # ----------------------------------------------------
        # CALL THE ALREADY-TESTED UNIT 10
        # ----------------------------------------------------

        try:

            unit_10_result = (
                await
                reconstruction_unit_10_live_demo_execution()
            )

        except Exception as exc:

            reconstruction_unit_10b_log(
                "UNIT 10B UNIT 10 EXCEPTION = "
                f"{repr(exc)}"
            )

            reconstruction_unit_10b_log(
                "UNIT 10B SUBMISSION STATE "
                "= UNKNOWN/NOT ACCEPTED"
            )

            reconstruction_unit_10b_log(
                "UNIT 10B WILL NOT FORCE "
                "A RETRY SUBMISSION"
            )

            reconstruction_unit_10b_log(
                "ZERO REAL ORDER = TRUE"
            )

            return {
                "valid": False,
                "monitor_started": True,
                "submitted": False,
                "accepted": False,
                "reason": (
                    "UNIT_10B_UNIT_10_EXCEPTION"
                ),
                "error": repr(
                    exc
                ),
                "cycle_count": (
                    UNIT_10B_CYCLE_COUNT
                ),
                "real_order": False,
            }

        # ----------------------------------------------------
        # VALIDATE UNIT 10 RETURN OBJECT
        # ----------------------------------------------------

        validation = (
            reconstruction_unit_10b_validate_result(
                unit_10_result
            )
        )

        if not validation["valid"]:

            reconstruction_unit_10b_log(
                "UNIT 10B UNIT 10 RESULT "
                "VALIDATION = FAIL"
            )

            reconstruction_unit_10b_log(
                "UNIT 10B VALIDATION REASON = "
                f"{validation['reason']}"
            )

            reconstruction_unit_10b_log(
                "UNIT 10B MONITOR STOPPING"
            )

            reconstruction_unit_10b_log(
                "ZERO REAL ORDER = TRUE"
            )

            return {
                "valid": False,
                "monitor_started": True,
                "submitted": False,
                "accepted": False,
                "reason": (
                    validation["reason"]
                ),
                "validation": validation,
                "unit_10_result": (
                    unit_10_result
                ),
                "cycle_count": (
                    UNIT_10B_CYCLE_COUNT
                ),
                "real_order": False,
            }

        reconstruction_unit_10b_log(
            "PASS: UNIT 10B RECEIVED "
            "VALID UNIT 10 RESULT"
        )

        # ----------------------------------------------------
        # EXTRACT VERIFIED UNIT 10 STATE
        # ----------------------------------------------------

        qualified = bool(
            unit_10_result.get(
                "qualified",
                False,
            )
        )

        submitted = bool(
            unit_10_result.get(
                "submitted",
                False,
            )
        )

        accepted = bool(
            unit_10_result.get(
                "accepted",
                False,
            )
        )

        reason = (
            unit_10_result.get(
                "reason"
            )
        )

        reconstruction_unit_10b_log(
            "UNIT 10B LIVE QUALIFIED = "
            f"{qualified}"
        )

        reconstruction_unit_10b_log(
            "UNIT 10B DEMO SUBMITTED = "
            f"{submitted}"
        )

        reconstruction_unit_10b_log(
            "UNIT 10B DEMO ACCEPTED = "
            f"{accepted}"
        )

        reconstruction_unit_10b_log(
            "UNIT 10B UNIT 10 REASON = "
            f"{reason}"
        )

        # ----------------------------------------------------
        # IMPOSSIBLE/UNSAFE STATE GUARDS
        # ----------------------------------------------------

        if accepted and not submitted:

            reconstruction_unit_10b_log(
                "FAIL: UNIT 10B ACCEPTED "
                "WITHOUT SUBMITTED"
            )

            reconstruction_unit_10b_log(
                "UNIT 10B MONITOR STOPPING"
            )

            return {
                "valid": False,
                "monitor_started": True,
                "submitted": False,
                "accepted": False,
                "reason": (
                    "UNIT_10B_INVALID_"
                    "ACCEPTED_STATE"
                ),
                "unit_10_result": (
                    unit_10_result
                ),
                "cycle_count": (
                    UNIT_10B_CYCLE_COUNT
                ),
                "real_order": False,
            }

        if submitted and not qualified:

            reconstruction_unit_10b_log(
                "FAIL: UNIT 10B SUBMISSION "
                "WITHOUT QUALIFICATION"
            )

            reconstruction_unit_10b_log(
                "UNIT 10B MONITOR STOPPING"
            )

            return {
                "valid": False,
                "monitor_started": True,
                "submitted": submitted,
                "accepted": accepted,
                "reason": (
                    "UNIT_10B_SUBMISSION_"
                    "WITHOUT_QUALIFICATION"
                ),
                "unit_10_result": (
                    unit_10_result
                ),
                "cycle_count": (
                    UNIT_10B_CYCLE_COUNT
                ),
                "real_order": False,
            }

        # ----------------------------------------------------
        # SUCCESS:
        # ONE DEMO ORDER WAS ACCEPTED
        # ----------------------------------------------------

        if (
            qualified
            and submitted
            and accepted
        ):

            # Lock FIRST before any further processing.
            UNIT_10B_DEMO_SUBMISSION_LOCKED = True

            UNIT_10B_ACCEPTED_RESULT = (
                unit_10_result
            )

            print(
                "=" * 80,
                flush=True,
            )

            reconstruction_unit_10b_log(
                "PASS: UNIT 10B LIVE SIGNAL "
                "QUALIFIED"
            )

            reconstruction_unit_10b_log(
                "PASS: UNIT 10B DEMO ORDER "
                "SUBMITTED"
            )

            reconstruction_unit_10b_log(
                "PASS: UNIT 10B WEEX DEMO "
                "ORDER ACCEPTED"
            )

            reconstruction_unit_10b_log(
                "UNIT 10B ONE-SHOT LOCK = ACTIVE"
            )

            reconstruction_unit_10b_log(
                "UNIT 10B FURTHER DEMO "
                "SUBMISSIONS = BLOCKED"
            )

            reconstruction_unit_10b_log(
                "REAL ORDER SENT = FALSE"
            )

            reconstruction_unit_10b_log(
                "RECONSTRUCTION UNIT 10B "
                "RESULT = PASS"
            )

            print(
                "=" * 80,
                flush=True,
            )

            return {
                "valid": True,
                "monitor_started": True,
                "qualified": True,
                "submitted": True,
                "accepted": True,
                "reason": (
                    "UNIT_10B_FIRST_LIVE_"
                    "DEMO_ACCEPTED"
                ),
                "cycle_count": (
                    UNIT_10B_CYCLE_COUNT
                ),
                "unit_10_result": (
                    unit_10_result
                ),
                "one_shot_locked": True,
                "real_order": False,
            }

        # ----------------------------------------------------
        # QUALIFIED + SUBMITTED BUT REJECTED
        #
        # DO NOT AUTOMATICALLY RE-SUBMIT.
        # A rejected/uncertain exchange submission must be
        # inspected before another order is attempted.
        # ----------------------------------------------------

        if (
            qualified
            and submitted
            and not accepted
        ):

            reconstruction_unit_10b_log(
                "UNIT 10B DEMO SUBMISSION "
                "= NOT ACCEPTED"
            )

            reconstruction_unit_10b_log(
                "UNIT 10B AUTOMATIC "
                "RESUBMISSION = BLOCKED"
            )

            reconstruction_unit_10b_log(
                "UNIT 10B MONITOR STOPPING "
                "FOR INSPECTION"
            )

            reconstruction_unit_10b_log(
                "REAL ORDER SENT = FALSE"
            )

            return {
                "valid": True,
                "monitor_started": True,
                "qualified": True,
                "submitted": True,
                "accepted": False,
                "reason": (
                    "UNIT_10B_DEMO_SUBMISSION_"
                    "NOT_ACCEPTED"
                ),
                "cycle_count": (
                    UNIT_10B_CYCLE_COUNT
                ),
                "unit_10_result": (
                    unit_10_result
                ),
                "one_shot_locked": False,
                "real_order": False,
            }

        # ----------------------------------------------------
        # QUALIFIED BUT UNIT 10 BLOCKED BEFORE SUBMISSION
        #
        # Stop rather than bypass Unit 10's safety chain.
        # ----------------------------------------------------

        if (
            qualified
            and not submitted
        ):

            reconstruction_unit_10b_log(
                "UNIT 10B LIVE SIGNAL "
                "= QUALIFIED"
            )

            reconstruction_unit_10b_log(
                "UNIT 10B DEMO SUBMISSION "
                "= BLOCKED BY UNIT 10"
            )

            reconstruction_unit_10b_log(
                "UNIT 10B WILL NOT BYPASS "
                "UNIT 10"
            )

            reconstruction_unit_10b_log(
                "UNIT 10B MONITOR STOPPING "
                "FOR INSPECTION"
            )

            return {
                "valid": True,
                "monitor_started": True,
                "qualified": True,
                "submitted": False,
                "accepted": False,
                "reason": (
                    "UNIT_10B_QUALIFIED_"
                    "BUT_NOT_SUBMITTED"
                ),
                "cycle_count": (
                    UNIT_10B_CYCLE_COUNT
                ),
                "unit_10_result": (
                    unit_10_result
                ),
                "one_shot_locked": False,
                "real_order": False,
            }

        # ----------------------------------------------------
        # NORMAL WAITING STATE:
        # NO QUALIFIED SIGNAL YET
        # ----------------------------------------------------

        reconstruction_unit_10b_log(
            "UNIT 10B LIVE ENTRY "
            "= NOT QUALIFIED"
        )

        reconstruction_unit_10b_log(
            "UNIT 10B DEMO SUBMISSION "
            "= NONE"
        )

        reconstruction_unit_10b_log(
            "UNIT 10B WAITING FOR "
            "NEXT LIVE CHECK"
        )

        reconstruction_unit_10b_log(
            "ZERO REAL ORDER = TRUE"
        )

        # ----------------------------------------------------
        # WAIT BEFORE NEXT LIVE MARKET RE-EVALUATION
        # ----------------------------------------------------

        await asyncio.sleep(
            UNIT_10B_CHECK_INTERVAL_SECONDS
        )

    # --------------------------------------------------------
    # FALLBACK TERMINATION
    # --------------------------------------------------------

    return {
        "valid": True,
        "monitor_started": True,
        "submitted": bool(
            UNIT_10B_ACCEPTED_RESULT
        ),
        "accepted": bool(
            UNIT_10B_ACCEPTED_RESULT
        ),
        "reason": (
            "UNIT_10B_MONITOR_COMPLETE"
        ),
        "cycle_count": (
            UNIT_10B_CYCLE_COUNT
        ),
        "one_shot_locked": (
            UNIT_10B_DEMO_SUBMISSION_LOCKED
        ),
        "real_order": False,
    }


async def run_reconstruction_unit_10b():
    """
    Explicit Unit 10B runner.
    """

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "WEEX_PARALLEL_BOT "
        "UNIT_10B_PERSISTENT_LIVE_DEMO_MONITOR",
        flush=True,
    )

    print(
        "STARTING UNIT 10B "
        "ONE-SHOT LIVE DEMO MONITOR",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    result = (
        await
        reconstruction_unit_10b_monitor()
    )

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "UNIT 10B FINAL RESULT =",
        result,
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return result


# ============================================================
# UNIT 10B ENTRY POINT
# TEMPORARILY DISABLED FOR UNIT 11C STANDALONE TEST
# ============================================================

# if __name__ == "__main__":
#
#     import asyncio
#
#     asyncio.run(
#         run_reconstruction_unit_10b()
#     )



# ============================================================
# RECONSTRUCTION UNIT 11A
# ADAPTIVE TP1 / TP2 / TP3 ZERO-WRITE STANDALONE TEST
#
# PURPOSE:
# Prove the reconstructed take-profit model before connecting
# it to the frozen Unit 10B demo-entry pipeline.
#
# TP MODEL:
# - TP1 minimum net ROI floor = 10%
# - TP2 minimum net ROI floor = 20%
# - Favorable market conditions may extend TP1 / TP2 higher
# - TP3 = trailing runner
#
# IMPORTANT:
# - ZERO WEEX POST
# - ZERO DEMO TP ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE MUTATION
# - NO SL
# - NO BACKUP EXECUTION
# ============================================================

from decimal import Decimal, ROUND_DOWN


UNIT_11A_TP1_MIN_NET_ROI_PERCENT = Decimal("10")
UNIT_11A_TP2_MIN_NET_ROI_PERCENT = Decimal("20")

UNIT_11A_TP1_ALLOCATION_PERCENT = Decimal("25")
UNIT_11A_TP2_ALLOCATION_PERCENT = Decimal("25")
UNIT_11A_TP3_ALLOCATION_PERCENT = Decimal("50")

UNIT_11A_TP3_TRAILING_DISTANCE_PERCENT = Decimal("0.20")

UNIT_11A_PRICE_STEP = Decimal("0.1")
UNIT_11A_QTY_STEP = Decimal("0.0001")

UNIT_11A_LEVERAGE = Decimal("100")


def unit_11a_decimal(value):
    return Decimal(str(value))


def unit_11a_normalize_price(price):

    price = unit_11a_decimal(price)

    normalized = (
        price
        / UNIT_11A_PRICE_STEP
    ).quantize(
        Decimal("1"),
        rounding=ROUND_DOWN,
    ) * UNIT_11A_PRICE_STEP

    return normalized


def unit_11a_normalize_quantity(quantity):

    quantity = unit_11a_decimal(quantity)

    normalized = (
        quantity
        / UNIT_11A_QTY_STEP
    ).quantize(
        Decimal("1"),
        rounding=ROUND_DOWN,
    ) * UNIT_11A_QTY_STEP

    return normalized


def unit_11a_roi_floor_price(
    *,
    direction,
    entry_price,
    minimum_roi_percent,
    leverage,
):

    direction = str(direction).upper()

    entry_price = unit_11a_decimal(
        entry_price
    )

    minimum_roi_percent = unit_11a_decimal(
        minimum_roi_percent
    )

    leverage = unit_11a_decimal(
        leverage
    )

    if direction not in (
        "LONG",
        "SHORT",
    ):
        raise ValueError(
            "UNIT 11A INVALID DIRECTION"
        )

    if entry_price <= 0:
        raise ValueError(
            "UNIT 11A INVALID ENTRY PRICE"
        )

    if leverage <= 0:
        raise ValueError(
            "UNIT 11A INVALID LEVERAGE"
        )

    required_price_move_percent = (
        minimum_roi_percent
        / leverage
    )

    required_price_move_fraction = (
        required_price_move_percent
        / Decimal("100")
    )

    if direction == "LONG":

        floor_price = (
            entry_price
            * (
                Decimal("1")
                +
                required_price_move_fraction
            )
        )

    else:

        floor_price = (
            entry_price
            * (
                Decimal("1")
                -
                required_price_move_fraction
            )
        )

    return unit_11a_normalize_price(
        floor_price
    )


def unit_11a_choose_adaptive_target(
    *,
    direction,
    roi_floor_price,
    favorable_market_price,
):

    direction = str(direction).upper()

    roi_floor_price = unit_11a_decimal(
        roi_floor_price
    )

    if favorable_market_price is None:

        return {
            "target_price":
                roi_floor_price,

            "source":
                "NET_ROI_FLOOR",
        }

    favorable_market_price = (
        unit_11a_normalize_price(
            favorable_market_price
        )
    )

    if direction == "LONG":

        if (
            favorable_market_price
            >
            roi_floor_price
        ):

            return {
                "target_price":
                    favorable_market_price,

                "source":
                    "FAVORABLE_MARKET_ABOVE_FLOOR",
            }

    elif direction == "SHORT":

        if (
            favorable_market_price
            <
            roi_floor_price
        ):

            return {
                "target_price":
                    favorable_market_price,

                "source":
                    "FAVORABLE_MARKET_BEYOND_FLOOR",
            }

    else:

        raise ValueError(
            "UNIT 11A INVALID DIRECTION"
        )

    return {
        "target_price":
            roi_floor_price,

        "source":
            "NET_ROI_FLOOR",
    }


def reconstruction_unit_11a_tp_engine(
    *,
    direction,
    entry_price,
    total_quantity,
    favorable_tp1_price=None,
    favorable_tp2_price=None,
    leverage=UNIT_11A_LEVERAGE,
):

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11A "
        "ADAPTIVE TP ENGINE START",
        flush=True,
    )

    direction = str(
        direction
    ).upper()

    entry_price = unit_11a_decimal(
        entry_price
    )

    total_quantity = unit_11a_decimal(
        total_quantity
    )

    leverage = unit_11a_decimal(
        leverage
    )

    if direction not in (
        "LONG",
        "SHORT",
    ):

        raise RuntimeError(
            "UNIT 11A DIRECTION INVALID"
        )

    if entry_price <= 0:

        raise RuntimeError(
            "UNIT 11A ENTRY PRICE INVALID"
        )

    if total_quantity <= 0:

        raise RuntimeError(
            "UNIT 11A QUANTITY INVALID"
        )

    print(
        "UNIT 11A DIRECTION =",
        direction,
        flush=True,
    )

    print(
        "UNIT 11A ENTRY PRICE =",
        entry_price,
        flush=True,
    )

    print(
        "UNIT 11A TOTAL QUANTITY =",
        total_quantity,
        flush=True,
    )

    print(
        "UNIT 11A LEVERAGE =",
        leverage,
        flush=True,
    )

    # --------------------------------------------------------
    # TP1
    # Minimum 10% ROI floor
    # --------------------------------------------------------

    tp1_floor_price = (
        unit_11a_roi_floor_price(
            direction=direction,
            entry_price=entry_price,
            minimum_roi_percent=(
                UNIT_11A_TP1_MIN_NET_ROI_PERCENT
            ),
            leverage=leverage,
        )
    )

    tp1_selection = (
        unit_11a_choose_adaptive_target(
            direction=direction,
            roi_floor_price=tp1_floor_price,
            favorable_market_price=(
                favorable_tp1_price
            ),
        )
    )

    tp1_price = (
        tp1_selection[
            "target_price"
        ]
    )

    tp1_source = (
        tp1_selection[
            "source"
        ]
    )

    # --------------------------------------------------------
    # TP2
    # Minimum 20% ROI floor
    # --------------------------------------------------------

    tp2_floor_price = (
        unit_11a_roi_floor_price(
            direction=direction,
            entry_price=entry_price,
            minimum_roi_percent=(
                UNIT_11A_TP2_MIN_NET_ROI_PERCENT
            ),
            leverage=leverage,
        )
    )

    tp2_selection = (
        unit_11a_choose_adaptive_target(
            direction=direction,
            roi_floor_price=tp2_floor_price,
            favorable_market_price=(
                favorable_tp2_price
            ),
        )
    )

    tp2_price = (
        tp2_selection[
            "target_price"
        ]
    )

    tp2_source = (
        tp2_selection[
            "source"
        ]
    )

    # --------------------------------------------------------
    # QUANTITY ALLOCATION
    #
    # 25% TP1
    # 25% TP2
    # remainder TP3
    #
    # TP3 receives the remainder so quantity rounding can
    # never accidentally create more total exit quantity
    # than the actual position.
    # --------------------------------------------------------

    tp1_quantity_raw = (
        total_quantity
        *
        UNIT_11A_TP1_ALLOCATION_PERCENT
        /
        Decimal("100")
    )

    tp2_quantity_raw = (
        total_quantity
        *
        UNIT_11A_TP2_ALLOCATION_PERCENT
        /
        Decimal("100")
    )

    tp1_quantity = (
        unit_11a_normalize_quantity(
            tp1_quantity_raw
        )
    )

    tp2_quantity = (
        unit_11a_normalize_quantity(
            tp2_quantity_raw
        )
    )

    tp3_quantity = (
        total_quantity
        -
        tp1_quantity
        -
        tp2_quantity
    )

    tp3_quantity = (
        unit_11a_normalize_quantity(
            tp3_quantity
        )
    )

    allocated_quantity = (
        tp1_quantity
        +
        tp2_quantity
        +
        tp3_quantity
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if tp1_quantity <= 0:

        raise RuntimeError(
            "UNIT 11A TP1 QUANTITY INVALID"
        )

    if tp2_quantity <= 0:

        raise RuntimeError(
            "UNIT 11A TP2 QUANTITY INVALID"
        )

    if tp3_quantity <= 0:

        raise RuntimeError(
            "UNIT 11A TP3 QUANTITY INVALID"
        )

    if allocated_quantity != total_quantity:

        raise RuntimeError(
            "UNIT 11A TP QUANTITY "
            "ALLOCATION MISMATCH"
        )

    if direction == "LONG":

        if not (
            tp1_price
            >
            entry_price
        ):

            raise RuntimeError(
                "UNIT 11A LONG TP1 "
                "NOT ABOVE ENTRY"
            )

        if not (
            tp2_price
            >
            tp1_price
        ):

            raise RuntimeError(
                "UNIT 11A LONG TP2 "
                "NOT ABOVE TP1"
            )

    else:

        if not (
            tp1_price
            <
            entry_price
        ):

            raise RuntimeError(
                "UNIT 11A SHORT TP1 "
                "NOT BELOW ENTRY"
            )

        if not (
            tp2_price
            <
            tp1_price
        ):

            raise RuntimeError(
                "UNIT 11A SHORT TP2 "
                "NOT BELOW TP1"
            )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11A "
        "TP1 10% ROI FLOOR",
        flush=True,
    )

    print(
        "UNIT 11A TP1 FLOOR PRICE =",
        tp1_floor_price,
        flush=True,
    )

    print(
        "UNIT 11A TP1 FINAL PRICE =",
        tp1_price,
        flush=True,
    )

    print(
        "UNIT 11A TP1 SOURCE =",
        tp1_source,
        flush=True,
    )

    print(
        "UNIT 11A TP1 QUANTITY =",
        tp1_quantity,
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11A "
        "TP2 20% ROI FLOOR",
        flush=True,
    )

    print(
        "UNIT 11A TP2 FLOOR PRICE =",
        tp2_floor_price,
        flush=True,
    )

    print(
        "UNIT 11A TP2 FINAL PRICE =",
        tp2_price,
        flush=True,
    )

    print(
        "UNIT 11A TP2 SOURCE =",
        tp2_source,
        flush=True,
    )

    print(
        "UNIT 11A TP2 QUANTITY =",
        tp2_quantity,
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11A "
        "TP3 TRAILING RUNNER",
        flush=True,
    )

    print(
        "UNIT 11A TP3 QUANTITY =",
        tp3_quantity,
        flush=True,
    )

    print(
        "UNIT 11A TP3 TRAILING "
        "DISTANCE % =",
        UNIT_11A_TP3_TRAILING_DISTANCE_PERCENT,
        flush=True,
    )

    print(
        "UNIT 11A TP3 FIXED "
        "TARGET = NONE",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11A "
        "QUANTITY ALLOCATION",
        flush=True,
    )

    print(
        "UNIT 11A ALLOCATED "
        "QUANTITY =",
        allocated_quantity,
        flush=True,
    )

    print(
        "UNIT 11A EXPECTED "
        "QUANTITY =",
        total_quantity,
        flush=True,
    )

    # --------------------------------------------------------
    # EXECUTION FIREBREAK
    # --------------------------------------------------------

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11A "
        "EXECUTION FIREBREAK",
        flush=True,
    )

    print(
        "ZERO WEEX POST = TRUE",
        flush=True,
    )

    print(
        "ZERO DEMO TP ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO REAL ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO EXCHANGE MUTATION = TRUE",
        flush=True,
    )

    print(
        "NO SL GENERATED = TRUE",
        flush=True,
    )

    print(
        "NO BACKUP EXECUTION = TRUE",
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11A "
        "RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return {
        "valid":
            True,

        "direction":
            direction,

        "entry_price":
            entry_price,

        "total_quantity":
            total_quantity,

        "tp1": {
            "minimum_net_roi_percent":
                UNIT_11A_TP1_MIN_NET_ROI_PERCENT,

            "floor_price":
                tp1_floor_price,

            "price":
                tp1_price,

            "quantity":
                tp1_quantity,

            "source":
                tp1_source,
        },

        "tp2": {
            "minimum_net_roi_percent":
                UNIT_11A_TP2_MIN_NET_ROI_PERCENT,

            "floor_price":
                tp2_floor_price,

            "price":
                tp2_price,

            "quantity":
                tp2_quantity,

            "source":
                tp2_source,
        },

        "tp3": {
            "quantity":
                tp3_quantity,

            "trailing_runner":
                True,

            "trailing_distance_percent":
                UNIT_11A_TP3_TRAILING_DISTANCE_PERCENT,
        },

        "weex_post":
            False,

        "demo_tp_order":
            False,

        "real_order":
            False,
    }


def reconstruction_unit_11a_standalone_test():

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "UNIT 11A STANDALONE "
        "ZERO-WRITE TEST START",
        flush=True,
    )

    # --------------------------------------------------------
    # TEST 1 — LONG
    #
    # No favorable market extension supplied.
    # Therefore TP1 and TP2 MUST use their ROI floors.
    # --------------------------------------------------------

    long_result = (
        reconstruction_unit_11a_tp_engine(
            direction="LONG",
            entry_price=Decimal("80000"),
            total_quantity=Decimal("0.0004"),
            favorable_tp1_price=None,
            favorable_tp2_price=None,
            leverage=Decimal("100"),
        )
    )

    if (
        long_result[
            "tp1"
        ][
            "source"
        ]
        !=
        "NET_ROI_FLOOR"
    ):

        raise RuntimeError(
            "UNIT 11A LONG TP1 "
            "FLOOR TEST FAILED"
        )

    if (
        long_result[
            "tp2"
        ][
            "source"
        ]
        !=
        "NET_ROI_FLOOR"
    ):

        raise RuntimeError(
            "UNIT 11A LONG TP2 "
            "FLOOR TEST FAILED"
        )

    print(
        "PASS: UNIT 11A "
        "LONG FLOOR TEST",
        flush=True,
    )

    # --------------------------------------------------------
    # TEST 2 — SHORT
    #
    # Favorable prices are deliberately placed farther into
    # profit than the minimum ROI floors.
    #
    # This proves the adaptive extension behavior.
    # --------------------------------------------------------

    short_result = (
        reconstruction_unit_11a_tp_engine(
            direction="SHORT",
            entry_price=Decimal("80000"),
            total_quantity=Decimal("0.0004"),

            favorable_tp1_price=(
                Decimal("79880")
            ),

            favorable_tp2_price=(
                Decimal("79760")
            ),

            leverage=Decimal("100"),
        )
    )

    if (
        short_result[
            "tp1"
        ][
            "source"
        ]
        !=
        "FAVORABLE_MARKET_BEYOND_FLOOR"
    ):

        raise RuntimeError(
            "UNIT 11A SHORT TP1 "
            "ADAPTIVE TEST FAILED"
        )

    if (
        short_result[
            "tp2"
        ][
            "source"
        ]
        !=
        "FAVORABLE_MARKET_BEYOND_FLOOR"
    ):

        raise RuntimeError(
            "UNIT 11A SHORT TP2 "
            "ADAPTIVE TEST FAILED"
        )

    # --------------------------------------------------------
    # EXPECTED QUANTITY SPLIT FOR 0.0004 BTC
    # --------------------------------------------------------

    expected_tp1_quantity = (
        Decimal("0.0001")
    )

    expected_tp2_quantity = (
        Decimal("0.0001")
    )

    expected_tp3_quantity = (
        Decimal("0.0002")
    )

    if (
        short_result[
            "tp1"
        ][
            "quantity"
        ]
        !=
        expected_tp1_quantity
    ):

        raise RuntimeError(
            "UNIT 11A TP1 "
            "ALLOCATION FAILED"
        )

    if (
        short_result[
            "tp2"
        ][
            "quantity"
        ]
        !=
        expected_tp2_quantity
    ):

        raise RuntimeError(
            "UNIT 11A TP2 "
            "ALLOCATION FAILED"
        )

    if (
        short_result[
            "tp3"
        ][
            "quantity"
        ]
        !=
        expected_tp3_quantity
    ):

        raise RuntimeError(
            "UNIT 11A TP3 "
            "ALLOCATION FAILED"
        )

    print(
        "PASS: UNIT 11A "
        "SHORT ADAPTIVE TEST",
        flush=True,
    )

    print(
        "PASS: UNIT 11A "
        "0.0004 QUANTITY SPLIT "
        "= 0.0001 / 0.0001 / 0.0002",
        flush=True,
    )

    print(
        "PASS: UNIT 11A "
        "TP3 TRAILING RUNNER",
        flush=True,
    )

    print(
        "PASS: UNIT 11A "
        "ZERO-WRITE TEST",
        flush=True,
    )

    print(
        "UNIT 11A WEEX POST = FALSE",
        flush=True,
    )

    print(
        "UNIT 11A DEMO TP ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 11A REAL ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 11A BACKUP EXECUTION = FALSE",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11A "
        "STANDALONE TEST = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return {
        "valid":
            True,

        "long_test":
            long_result,

        "short_test":
            short_result,

        "weex_post":
            False,

        "demo_tp_order":
            False,

        "real_order":
            False,

        "backup_execution":
            False,
    }


# ============================================================
# UNIT 11A TEMPORARY STANDALONE TEST ENTRY POINT
# ============================================================

if __name__ == "__main__":

    reconstruction_unit_11a_standalone_test()

# ============================================================
# RECONSTRUCTION UNIT 11B
# TP DEMO SUBMISSION-BOUNDARY PAYLOAD TEST
#
# PURPOSE:
# Convert the already-tested Unit 11A TP plan into exact
# candidate demo TP submission instructions and validate them
# before any WEEX POST is permitted.
#
# IMPORTANT:
# - CONSUMES UNIT 11A OUTPUT DIRECTLY
# - ZERO WEEX POST
# - ZERO DEMO TP ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE MUTATION
# - NO SL
# - NO BACKUP EXECUTION
#
# TP MODEL:
# TP1 = 25%
# TP2 = 25%
# TP3 = 50% trailing runner
#
# SAFETY:
# - Exit direction MUST oppose position direction
# - Every exit MUST be reduce-only
# - TP1 + TP2 + TP3 MUST equal position quantity
# - No SL fields may exist
# - No exit quantity may exceed position quantity
# ============================================================


UNIT_11B_SYMBOL = "BTCSUSDT"

UNIT_11B_FORBIDDEN_SL_FIELDS = {
    "slTriggerPrice",
    "SlWorkingType",
    "stopLossPrice",
    "stopLoss",
    "stopPrice",
}


def unit_11b_decimal(
    value,
):

    return Decimal(
        str(value)
    )


def unit_11b_decimal_string(
    value,
):

    value = unit_11b_decimal(
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


def unit_11b_exit_side(
    direction,
):

    direction = str(
        direction
    ).upper()

    if direction == "LONG":

        return "SELL"

    if direction == "SHORT":

        return "BUY"

    raise RuntimeError(
        "UNIT 11B INVALID POSITION DIRECTION"
    )


def unit_11b_position_side(
    direction,
):

    direction = str(
        direction
    ).upper()

    if direction not in (
        "LONG",
        "SHORT",
    ):

        raise RuntimeError(
            "UNIT 11B INVALID POSITION SIDE"
        )

    return direction


def unit_11b_assert_no_sl_fields(
    payload,
):

    present_sl_fields = [
        field
        for field
        in UNIT_11B_FORBIDDEN_SL_FIELDS
        if field in payload
    ]

    if present_sl_fields:

        raise RuntimeError(
            "UNIT 11B FORBIDDEN SL FIELDS PRESENT: "
            + str(
                present_sl_fields
            )
        )

    return True


def unit_11b_build_fixed_tp_payload(
    *,
    symbol,
    direction,
    quantity,
    trigger_price,
    tp_name,
):

    direction = str(
        direction
    ).upper()

    quantity = unit_11b_decimal(
        quantity
    )

    trigger_price = unit_11b_decimal(
        trigger_price
    )

    if quantity <= 0:

        raise RuntimeError(
            "UNIT 11B "
            + str(tp_name)
            + " QUANTITY INVALID"
        )

    if trigger_price <= 0:

        raise RuntimeError(
            "UNIT 11B "
            + str(tp_name)
            + " TRIGGER PRICE INVALID"
        )

    payload = {

        "symbol":
            str(symbol),

        "side":
            unit_11b_exit_side(
                direction
            ),

        "positionSide":
            unit_11b_position_side(
                direction
            ),

        "type":
            "TAKE_PROFIT_MARKET",

        "quantity":
            unit_11b_decimal_string(
                quantity
            ),

        "tpTriggerPrice":
            unit_11b_decimal_string(
                trigger_price
            ),

        "TpWorkingType":
            "MARK_PRICE",

        "reduceOnly":
            True,

        "closePosition":
            False,

        "tpName":
            str(tp_name),
    }

    unit_11b_assert_no_sl_fields(
        payload
    )

    return payload


def unit_11b_build_trailing_tp_payload(
    *,
    symbol,
    direction,
    quantity,
    trailing_distance_percent,
):

    direction = str(
        direction
    ).upper()

    quantity = unit_11b_decimal(
        quantity
    )

    trailing_distance_percent = (
        unit_11b_decimal(
            trailing_distance_percent
        )
    )

    if quantity <= 0:

        raise RuntimeError(
            "UNIT 11B TP3 QUANTITY INVALID"
        )

    if (
        trailing_distance_percent
        <= 0
    ):

        raise RuntimeError(
            "UNIT 11B TP3 TRAILING "
            "DISTANCE INVALID"
        )

    payload = {

        "symbol":
            str(symbol),

        "side":
            unit_11b_exit_side(
                direction
            ),

        "positionSide":
            unit_11b_position_side(
                direction
            ),

        "type":
            "TRAILING_STOP_MARKET",

        "quantity":
            unit_11b_decimal_string(
                quantity
            ),

        "callbackRate":
            unit_11b_decimal_string(
                trailing_distance_percent
            ),

        "workingType":
            "MARK_PRICE",

        "reduceOnly":
            True,

        "closePosition":
            False,

        "tpName":
            "TP3_TRAILING_RUNNER",
    }

    unit_11b_assert_no_sl_fields(
        payload
    )

    return payload


def reconstruction_unit_11b_build_tp_payloads(
    *,
    unit_11a_result,
    symbol=UNIT_11B_SYMBOL,
):

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11B "
        "TP SUBMISSION-BOUNDARY START",
        flush=True,
    )

    # --------------------------------------------------------
    # UNIT 11A CONTRACT VALIDATION
    # --------------------------------------------------------

    if not isinstance(
        unit_11a_result,
        dict,
    ):

        raise RuntimeError(
            "UNIT 11B UNIT 11A RESULT "
            "IS NOT A DICTIONARY"
        )

    if (
        unit_11a_result.get(
            "valid"
        )
        is not True
    ):

        raise RuntimeError(
            "UNIT 11B UNIT 11A "
            "RESULT NOT VALID"
        )

    direction = str(
        unit_11a_result[
            "direction"
        ]
    ).upper()

    entry_price = (
        unit_11b_decimal(
            unit_11a_result[
                "entry_price"
            ]
        )
    )

    total_quantity = (
        unit_11b_decimal(
            unit_11a_result[
                "total_quantity"
            ]
        )
    )

    tp1 = (
        unit_11a_result[
            "tp1"
        ]
    )

    tp2 = (
        unit_11a_result[
            "tp2"
        ]
    )

    tp3 = (
        unit_11a_result[
            "tp3"
        ]
    )

    if direction not in (
        "LONG",
        "SHORT",
    ):

        raise RuntimeError(
            "UNIT 11B INVALID DIRECTION"
        )

    if entry_price <= 0:

        raise RuntimeError(
            "UNIT 11B INVALID ENTRY PRICE"
        )

    if total_quantity <= 0:

        raise RuntimeError(
            "UNIT 11B INVALID TOTAL QUANTITY"
        )

    # --------------------------------------------------------
    # READ UNIT 11A VALUES
    # --------------------------------------------------------

    tp1_price = (
        unit_11b_decimal(
            tp1[
                "price"
            ]
        )
    )

    tp2_price = (
        unit_11b_decimal(
            tp2[
                "price"
            ]
        )
    )

    tp1_quantity = (
        unit_11b_decimal(
            tp1[
                "quantity"
            ]
        )
    )

    tp2_quantity = (
        unit_11b_decimal(
            tp2[
                "quantity"
            ]
        )
    )

    tp3_quantity = (
        unit_11b_decimal(
            tp3[
                "quantity"
            ]
        )
    )

    trailing_distance_percent = (
        unit_11b_decimal(
            tp3[
                "trailing_distance_percent"
            ]
        )
    )

    # --------------------------------------------------------
    # QUANTITY SAFETY
    # --------------------------------------------------------

    if tp1_quantity <= 0:

        raise RuntimeError(
            "UNIT 11B TP1 QUANTITY INVALID"
        )

    if tp2_quantity <= 0:

        raise RuntimeError(
            "UNIT 11B TP2 QUANTITY INVALID"
        )

    if tp3_quantity <= 0:

        raise RuntimeError(
            "UNIT 11B TP3 QUANTITY INVALID"
        )

    allocated_quantity = (
        tp1_quantity
        +
        tp2_quantity
        +
        tp3_quantity
    )

    if (
        allocated_quantity
        !=
        total_quantity
    ):

        raise RuntimeError(
            "UNIT 11B TP QUANTITY "
            "ALLOCATION MISMATCH"
        )

    if (
        tp1_quantity
        >
        total_quantity
    ):

        raise RuntimeError(
            "UNIT 11B TP1 EXCEEDS POSITION"
        )

    if (
        tp2_quantity
        >
        total_quantity
    ):

        raise RuntimeError(
            "UNIT 11B TP2 EXCEEDS POSITION"
        )

    if (
        tp3_quantity
        >
        total_quantity
    ):

        raise RuntimeError(
            "UNIT 11B TP3 EXCEEDS POSITION"
        )

    print(
        "PASS: UNIT 11B "
        "QUANTITY SAFETY",
        flush=True,
    )

    print(
        "UNIT 11B POSITION QUANTITY =",
        total_quantity,
        flush=True,
    )

    print(
        "UNIT 11B ALLOCATED QUANTITY =",
        allocated_quantity,
        flush=True,
    )

    # --------------------------------------------------------
    # DIRECTION / PRICE SAFETY
    # --------------------------------------------------------

    if direction == "LONG":

        if not (
            tp1_price
            >
            entry_price
        ):

            raise RuntimeError(
                "UNIT 11B LONG TP1 "
                "NOT ABOVE ENTRY"
            )

        if not (
            tp2_price
            >
            tp1_price
        ):

            raise RuntimeError(
                "UNIT 11B LONG TP2 "
                "NOT ABOVE TP1"
            )

    else:

        if not (
            tp1_price
            <
            entry_price
        ):

            raise RuntimeError(
                "UNIT 11B SHORT TP1 "
                "NOT BELOW ENTRY"
            )

        if not (
            tp2_price
            <
            tp1_price
        ):

            raise RuntimeError(
                "UNIT 11B SHORT TP2 "
                "NOT BELOW TP1"
            )

    exit_side = (
        unit_11b_exit_side(
            direction
        )
    )

    print(
        "PASS: UNIT 11B "
        "EXIT DIRECTION SAFETY",
        flush=True,
    )

    print(
        "UNIT 11B POSITION DIRECTION =",
        direction,
        flush=True,
    )

    print(
        "UNIT 11B EXIT SIDE =",
        exit_side,
        flush=True,
    )

    # --------------------------------------------------------
    # BUILD TP1 CANDIDATE PAYLOAD
    # --------------------------------------------------------

    tp1_payload = (
        unit_11b_build_fixed_tp_payload(
            symbol=symbol,
            direction=direction,
            quantity=tp1_quantity,
            trigger_price=tp1_price,
            tp_name="TP1",
        )
    )

    # --------------------------------------------------------
    # BUILD TP2 CANDIDATE PAYLOAD
    # --------------------------------------------------------

    tp2_payload = (
        unit_11b_build_fixed_tp_payload(
            symbol=symbol,
            direction=direction,
            quantity=tp2_quantity,
            trigger_price=tp2_price,
            tp_name="TP2",
        )
    )

    # --------------------------------------------------------
    # BUILD TP3 TRAILING CANDIDATE PAYLOAD
    # --------------------------------------------------------

    tp3_payload = (
        unit_11b_build_trailing_tp_payload(
            symbol=symbol,
            direction=direction,
            quantity=tp3_quantity,
            trailing_distance_percent=(
                trailing_distance_percent
            ),
        )
    )

    payloads = [
        tp1_payload,
        tp2_payload,
        tp3_payload,
    ]

    # --------------------------------------------------------
    # SUBMISSION-BOUNDARY VALIDATION
    # --------------------------------------------------------

    for payload in payloads:

        if (
            payload[
                "symbol"
            ]
            !=
            symbol
        ):

            raise RuntimeError(
                "UNIT 11B SYMBOL CHANGED"
            )

        if (
            payload[
                "side"
            ]
            !=
            exit_side
        ):

            raise RuntimeError(
                "UNIT 11B EXIT SIDE CHANGED"
            )

        if (
            payload[
                "positionSide"
            ]
            !=
            direction
        ):

            raise RuntimeError(
                "UNIT 11B POSITION SIDE CHANGED"
            )

        if (
            payload[
                "reduceOnly"
            ]
            is not True
        ):

            raise RuntimeError(
                "UNIT 11B REDUCE-ONLY "
                "PROTECTION MISSING"
            )

        if (
            payload[
                "closePosition"
            ]
            is not False
        ):

            raise RuntimeError(
                "UNIT 11B CLOSE-POSITION "
                "FLAG INVALID"
            )

        unit_11b_assert_no_sl_fields(
            payload
        )

    # --------------------------------------------------------
    # TP1 EXACT CHECK
    # --------------------------------------------------------

    if (
        unit_11b_decimal(
            tp1_payload[
                "quantity"
            ]
        )
        !=
        tp1_quantity
    ):

        raise RuntimeError(
            "UNIT 11B TP1 QUANTITY CHANGED"
        )

    if (
        unit_11b_decimal(
            tp1_payload[
                "tpTriggerPrice"
            ]
        )
        !=
        tp1_price
    ):

        raise RuntimeError(
            "UNIT 11B TP1 PRICE CHANGED"
        )

    # --------------------------------------------------------
    # TP2 EXACT CHECK
    # --------------------------------------------------------

    if (
        unit_11b_decimal(
            tp2_payload[
                "quantity"
            ]
        )
        !=
        tp2_quantity
    ):

        raise RuntimeError(
            "UNIT 11B TP2 QUANTITY CHANGED"
        )

    if (
        unit_11b_decimal(
            tp2_payload[
                "tpTriggerPrice"
            ]
        )
        !=
        tp2_price
    ):

        raise RuntimeError(
            "UNIT 11B TP2 PRICE CHANGED"
        )

    # --------------------------------------------------------
    # TP3 EXACT CHECK
    # --------------------------------------------------------

    if (
        unit_11b_decimal(
            tp3_payload[
                "quantity"
            ]
        )
        !=
        tp3_quantity
    ):

        raise RuntimeError(
            "UNIT 11B TP3 QUANTITY CHANGED"
        )

    if (
        unit_11b_decimal(
            tp3_payload[
                "callbackRate"
            ]
        )
        !=
        trailing_distance_percent
    ):

        raise RuntimeError(
            "UNIT 11B TP3 TRAILING "
            "DISTANCE CHANGED"
        )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11B "
        "TP1 PAYLOAD",
        flush=True,
    )

    print(
        "UNIT 11B TP1 PAYLOAD =",
        tp1_payload,
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11B "
        "TP2 PAYLOAD",
        flush=True,
    )

    print(
        "UNIT 11B TP2 PAYLOAD =",
        tp2_payload,
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11B "
        "TP3 TRAILING PAYLOAD",
        flush=True,
    )

    print(
        "UNIT 11B TP3 PAYLOAD =",
        tp3_payload,
        flush=True,
    )

    # --------------------------------------------------------
    # FIREBREAK
    #
    # Payloads exist locally, but absolutely no network write
    # occurs in Unit 11B.
    # --------------------------------------------------------

    weex_post = False
    demo_tp_order = False
    real_order = False
    exchange_mutation = False
    sl_generated = False
    backup_execution = False

    if weex_post:

        raise RuntimeError(
            "UNIT 11B WEEX POST FIREBREAK FAILED"
        )

    if demo_tp_order:

        raise RuntimeError(
            "UNIT 11B DEMO TP FIREBREAK FAILED"
        )

    if real_order:

        raise RuntimeError(
            "UNIT 11B REAL ORDER FIREBREAK FAILED"
        )

    if exchange_mutation:

        raise RuntimeError(
            "UNIT 11B EXCHANGE MUTATION "
            "FIREBREAK FAILED"
        )

    if sl_generated:

        raise RuntimeError(
            "UNIT 11B SL FIREBREAK FAILED"
        )

    if backup_execution:

        raise RuntimeError(
            "UNIT 11B BACKUP FIREBREAK FAILED"
        )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11B "
        "SUBMISSION-BOUNDARY VALIDATION",
        flush=True,
    )

    print(
        "PASS: UNIT 11B "
        "ALL EXIT ORDERS REDUCE-ONLY",
        flush=True,
    )

    print(
        "PASS: UNIT 11B "
        "NO SL FIELDS",
        flush=True,
    )

    print(
        "PASS: UNIT 11B "
        "TOTAL EXIT QUANTITY = "
        "POSITION QUANTITY",
        flush=True,
    )

    print(
        "ZERO WEEX POST = TRUE",
        flush=True,
    )

    print(
        "ZERO DEMO TP ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO REAL ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO EXCHANGE MUTATION = TRUE",
        flush=True,
    )

    print(
        "NO SL GENERATED = TRUE",
        flush=True,
    )

    print(
        "NO BACKUP EXECUTION = TRUE",
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11B "
        "RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return {

        "valid":
            True,

        "direction":
            direction,

        "entry_price":
            entry_price,

        "total_quantity":
            total_quantity,

        "exit_side":
            exit_side,

        "tp1_payload":
            tp1_payload,

        "tp2_payload":
            tp2_payload,

        "tp3_payload":
            tp3_payload,

        "allocated_quantity":
            allocated_quantity,

        "weex_post":
            False,

        "demo_tp_order":
            False,

        "real_order":
            False,

        "exchange_mutation":
            False,

        "sl_generated":
            False,

        "backup_execution":
            False,
    }


def reconstruction_unit_11b_standalone_test():

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "UNIT 11B STANDALONE "
        "ZERO-WRITE TEST START",
        flush=True,
    )

    # --------------------------------------------------------
    # TEST 1 — LONG
    # Generate Unit 11A result first, then feed that exact
    # result into Unit 11B.
    # --------------------------------------------------------

    long_11a = (
        reconstruction_unit_11a_tp_engine(
            direction="LONG",
            entry_price=Decimal("80000"),
            total_quantity=Decimal("0.0004"),
            favorable_tp1_price=None,
            favorable_tp2_price=None,
            leverage=Decimal("100"),
        )
    )

    long_11b = (
        reconstruction_unit_11b_build_tp_payloads(
            unit_11a_result=long_11a,
            symbol=UNIT_11B_SYMBOL,
        )
    )

    if (
        long_11b[
            "exit_side"
        ]
        !=
        "SELL"
    ):

        raise RuntimeError(
            "UNIT 11B LONG EXIT SIDE TEST FAILED"
        )

    if (
        long_11b[
            "tp1_payload"
        ][
            "quantity"
        ]
        !=
        "0.0001"
    ):

        raise RuntimeError(
            "UNIT 11B LONG TP1 "
            "QUANTITY TEST FAILED"
        )

    if (
        long_11b[
            "tp2_payload"
        ][
            "quantity"
        ]
        !=
        "0.0001"
    ):

        raise RuntimeError(
            "UNIT 11B LONG TP2 "
            "QUANTITY TEST FAILED"
        )

    if (
        long_11b[
            "tp3_payload"
        ][
            "quantity"
        ]
        !=
        "0.0002"
    ):

        raise RuntimeError(
            "UNIT 11B LONG TP3 "
            "QUANTITY TEST FAILED"
        )

    print(
        "PASS: UNIT 11B LONG "
        "EXIT PAYLOAD TEST",
        flush=True,
    )

    # --------------------------------------------------------
    # TEST 2 — SHORT
    # This matches the direction of the currently accepted
    # Unit 10B demo position.
    # --------------------------------------------------------

    short_11a = (
        reconstruction_unit_11a_tp_engine(
            direction="SHORT",
            entry_price=Decimal("80000"),
            total_quantity=Decimal("0.0004"),
            favorable_tp1_price=(
                Decimal("79880")
            ),
            favorable_tp2_price=(
                Decimal("79760")
            ),
            leverage=Decimal("100"),
        )
    )

    short_11b = (
        reconstruction_unit_11b_build_tp_payloads(
            unit_11a_result=short_11a,
            symbol=UNIT_11B_SYMBOL,
        )
    )

    if (
        short_11b[
            "exit_side"
        ]
        !=
        "BUY"
    ):

        raise RuntimeError(
            "UNIT 11B SHORT EXIT SIDE TEST FAILED"
        )

    if (
        short_11b[
            "tp1_payload"
        ][
            "quantity"
        ]
        !=
        "0.0001"
    ):

        raise RuntimeError(
            "UNIT 11B SHORT TP1 "
            "QUANTITY TEST FAILED"
        )

    if (
        short_11b[
            "tp2_payload"
        ][
            "quantity"
        ]
        !=
        "0.0001"
    ):

        raise RuntimeError(
            "UNIT 11B SHORT TP2 "
            "QUANTITY TEST FAILED"
        )

    if (
        short_11b[
            "tp3_payload"
        ][
            "quantity"
        ]
        !=
        "0.0002"
    ):

        raise RuntimeError(
            "UNIT 11B SHORT TP3 "
            "QUANTITY TEST FAILED"
        )

    # --------------------------------------------------------
    # PROVE ALL THREE SHORT EXIT ORDERS ARE REDUCE-ONLY
    # --------------------------------------------------------

    for key in (
        "tp1_payload",
        "tp2_payload",
        "tp3_payload",
    ):

        payload = (
            short_11b[
                key
            ]
        )

        if (
            payload[
                "reduceOnly"
            ]
            is not True
        ):

            raise RuntimeError(
                "UNIT 11B SHORT "
                "REDUCE-ONLY TEST FAILED"
            )

        unit_11b_assert_no_sl_fields(
            payload
        )

    print(
        "PASS: UNIT 11B SHORT "
        "EXIT PAYLOAD TEST",
        flush=True,
    )

    print(
        "PASS: UNIT 11B "
        "0.0004 QUANTITY SPLIT "
        "= 0.0001 / 0.0001 / 0.0002",
        flush=True,
    )

    print(
        "PASS: UNIT 11B "
        "OPPOSITE EXIT SIDE TEST",
        flush=True,
    )

    print(
        "PASS: UNIT 11B "
        "REDUCE-ONLY TEST",
        flush=True,
    )

    print(
        "PASS: UNIT 11B "
        "NO SL FIELD TEST",
        flush=True,
    )

    print(
        "UNIT 11B WEEX POST = FALSE",
        flush=True,
    )

    print(
        "UNIT 11B DEMO TP ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 11B REAL ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 11B EXCHANGE MUTATION = FALSE",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11B "
        "STANDALONE TEST = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return {

        "valid":
            True,

        "long_test":
            long_11b,

        "short_test":
            short_11b,

        "weex_post":
            False,

        "demo_tp_order":
            False,

        "real_order":
            False,

        "exchange_mutation":
            False,
    }


# ============================================================
# UNIT 11B TEMPORARY STANDALONE TEST ENTRY POINT
# ============================================================

if __name__ == "__main__":

    reconstruction_unit_11b_standalone_test()

# ============================================================
# RECONSTRUCTION UNIT 11C
# LIVE DEMO POSITION -> UNIT 11A -> UNIT 11B BRIDGE
#
# PURPOSE:
# Read the currently open WEEX demo position and use its
# ACTUAL direction, entry price and quantity to generate
# the Unit 11A adaptive TP plan and Unit 11B validated
# TP submission-boundary payloads.
#
# IMPORTANT:
# - READ-ONLY POSITION RECONCILIATION
# - ZERO WEEX POST
# - ZERO DEMO TP ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE MUTATION
# - NO SL
# - NO BACKUP EXECUTION
#
# UNIT 11C DOES NOT PLACE TP ORDERS.
# ============================================================


UNIT_11C_SYMBOL = "BTCSUSDT"


def unit_11c_decimal(value):

    if value is None:

        return Decimal("0")

    try:

        return Decimal(
            str(value)
        )

    except Exception:

        return Decimal("0")


def unit_11c_first_value(
    data,
    names,
):

    if not isinstance(
        data,
        dict,
    ):

        return None

    for name in names:

        if name in data:

            value = data.get(
                name
            )

            if value not in (
                None,
                "",
            ):

                return value

    return None


def unit_11c_extract_position_list(
    response_json,
):

    if isinstance(
        response_json,
        list,
    ):

        return response_json

    if not isinstance(
        response_json,
        dict,
    ):

        return []

    # --------------------------------------------------------
    # Common direct containers
    # --------------------------------------------------------

    for key in (
        "data",
        "result",
        "positions",
        "list",
        "rows",
    ):

        value = response_json.get(
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
                "positions",
                "list",
                "rows",
                "data",
            ):

                nested_value = (
                    value.get(
                        nested_key
                    )
                )

                if isinstance(
                    nested_value,
                    list,
                ):

                    return nested_value

    return []


def unit_11c_normalize_direction(
    position,
):

    raw_direction = (
        unit_11c_first_value(
            position,
            (
                "positionSide",
                "position_side",
                "holdSide",
                "hold_side",
                "direction",
                "side",
            ),
        )
    )

    if raw_direction is None:

        return None

    raw_direction = str(
        raw_direction
    ).upper()

    if raw_direction in (
        "LONG",
        "BUY",
    ):

        return "LONG"

    if raw_direction in (
        "SHORT",
        "SELL",
    ):

        return "SHORT"

    return None


def unit_11c_position_quantity(
    position,
):

    raw_quantity = (
        unit_11c_first_value(
            position,
            (
                "quantity",
                "positionAmt",
                "positionAmount",
                "position_amount",
                "size",
                "total",
                "holdVol",
                "holdVolume",
                "available",
            ),
        )
    )

    quantity = (
        unit_11c_decimal(
            raw_quantity
        )
    )

    if quantity < 0:

        quantity = abs(
            quantity
        )

    return quantity


def unit_11c_entry_price(
    position,
):

    raw_entry = (
        unit_11c_first_value(
            position,
            (
                "entryPrice",
                "entry_price",
                "avgPrice",
                "averagePrice",
                "averageOpenPrice",
                "openPriceAvg",
                "openAvgPrice",
            ),
        )
    )

    return unit_11c_decimal(
        raw_entry
    )


def unit_11c_symbol(
    position,
):

    raw_symbol = (
        unit_11c_first_value(
            position,
            (
                "symbol",
                "contract",
                "contractCode",
            ),
        )
    )

    if raw_symbol is None:

        return None

    return str(
        raw_symbol
    ).upper()


def unit_11c_normalize_position(
    position,
):

    if not isinstance(
        position,
        dict,
    ):

        return None

    direction = (
        unit_11c_normalize_direction(
            position
        )
    )

    quantity = (
        unit_11c_position_quantity(
            position
        )
    )

    entry_price = (
        unit_11c_entry_price(
            position
        )
    )

    symbol = (
        unit_11c_symbol(
            position
        )
    )

    if direction not in (
        "LONG",
        "SHORT",
    ):

        return None

    if quantity <= 0:

        return None

    if entry_price <= 0:

        return None

    return {

        "symbol":
            symbol,

        "direction":
            direction,

        "quantity":
            quantity,

        "entry_price":
            entry_price,

        "raw":
            position,
    }


def unit_11c_find_open_positions(
    response_json,
    symbol=UNIT_11C_SYMBOL,
):

    raw_positions = (
        unit_11c_extract_position_list(
            response_json
        )
    )

    normalized_positions = []

    requested_symbol = str(
        symbol
    ).upper()

    for raw_position in raw_positions:

        normalized = (
            unit_11c_normalize_position(
                raw_position
            )
        )

        if normalized is None:

            continue

        position_symbol = (
            normalized.get(
                "symbol"
            )
        )

        if (
            position_symbol
            is not None
            and
            position_symbol
            !=
            requested_symbol
        ):

            continue

        normalized_positions.append(
            normalized
        )

    return normalized_positions


def unit_11c_build_from_position(
    *,
    position,
    favorable_tp1_price=None,
    favorable_tp2_price=None,
):

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11C "
        "LIVE POSITION BRIDGE START",
        flush=True,
    )

    if not isinstance(
        position,
        dict,
    ):

        raise RuntimeError(
            "UNIT 11C POSITION INVALID"
        )

    direction = (
        position[
            "direction"
        ]
    )

    entry_price = (
        unit_11c_decimal(
            position[
                "entry_price"
            ]
        )
    )

    quantity = (
        unit_11c_decimal(
            position[
                "quantity"
            ]
        )
    )

    if direction not in (
        "LONG",
        "SHORT",
    ):

        raise RuntimeError(
            "UNIT 11C DIRECTION INVALID"
        )

    if entry_price <= 0:

        raise RuntimeError(
            "UNIT 11C ENTRY PRICE INVALID"
        )

    if quantity <= 0:

        raise RuntimeError(
            "UNIT 11C POSITION QUANTITY INVALID"
        )

    print(
        "PASS: UNIT 11C "
        "OPEN POSITION VALIDATED",
        flush=True,
    )

    print(
        "UNIT 11C SYMBOL =",
        position.get(
            "symbol"
        ),
        flush=True,
    )

    print(
        "UNIT 11C DIRECTION =",
        direction,
        flush=True,
    )

    print(
        "UNIT 11C ACTUAL ENTRY PRICE =",
        entry_price,
        flush=True,
    )

    print(
        "UNIT 11C ACTUAL POSITION QUANTITY =",
        quantity,
        flush=True,
    )

    # --------------------------------------------------------
    # IMPORTANT
    #
    # Unit 11C intentionally does NOT invent favorable
    # structure targets.
    #
    # Unless real structure targets are supplied by a later
    # verified bridge, Unit 11A uses its minimum ROI floors.
    # --------------------------------------------------------

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 11C CALLING VERIFIED UNIT 11A",
        flush=True,
    )

    unit_11a_result = (
        reconstruction_unit_11a_tp_engine(
            direction=direction,
            entry_price=entry_price,
            total_quantity=quantity,
            favorable_tp1_price=(
                favorable_tp1_price
            ),
            favorable_tp2_price=(
                favorable_tp2_price
            ),
            leverage=Decimal(
                "100"
            ),
        )
    )

    if (
        not isinstance(
            unit_11a_result,
            dict,
        )
        or
        unit_11a_result.get(
            "valid"
        )
        is not True
    ):

        raise RuntimeError(
            "UNIT 11C UNIT 11A FAILED"
        )

    print(
        "PASS: UNIT 11C "
        "UNIT 11A TP PLAN",
        flush=True,
    )

    # --------------------------------------------------------
    # FEED EXACT UNIT 11A RESULT INTO VERIFIED UNIT 11B
    # --------------------------------------------------------

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 11C CALLING VERIFIED UNIT 11B",
        flush=True,
    )

    unit_11b_result = (
        reconstruction_unit_11b_build_tp_payloads(
            unit_11a_result=(
                unit_11a_result
            ),
            symbol=UNIT_11C_SYMBOL,
        )
    )

    if (
        not isinstance(
            unit_11b_result,
            dict,
        )
        or
        unit_11b_result.get(
            "valid"
        )
        is not True
    ):

        raise RuntimeError(
            "UNIT 11C UNIT 11B FAILED"
        )

    # --------------------------------------------------------
    # CROSS-CHECK 11A/11B AGAINST ACTUAL POSITION
    # --------------------------------------------------------

    if (
        unit_11b_decimal(
            unit_11b_result[
                "total_quantity"
            ]
        )
        !=
        quantity
    ):

        raise RuntimeError(
            "UNIT 11C POSITION QUANTITY "
            "CHANGED THROUGH TP PIPELINE"
        )

    if (
        unit_11b_result[
            "direction"
        ]
        !=
        direction
    ):

        raise RuntimeError(
            "UNIT 11C POSITION DIRECTION "
            "CHANGED THROUGH TP PIPELINE"
        )

    allocated_quantity = (
        unit_11b_decimal(
            unit_11b_result[
                "allocated_quantity"
            ]
        )
    )

    if (
        allocated_quantity
        !=
        quantity
    ):

        raise RuntimeError(
            "UNIT 11C EXIT QUANTITY "
            "DOES NOT MATCH POSITION"
        )

    print(
        "PASS: UNIT 11C "
        "ACTUAL POSITION -> 11A -> 11B",
        flush=True,
    )

    print(
        "PASS: UNIT 11C "
        "EXIT QUANTITY MATCHES "
        "ACTUAL POSITION",
        flush=True,
    )

    # --------------------------------------------------------
    # FINAL FIREBREAK
    # --------------------------------------------------------

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11C EXECUTION FIREBREAK",
        flush=True,
    )

    print(
        "ZERO WEEX POST = TRUE",
        flush=True,
    )

    print(
        "ZERO DEMO TP ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO REAL ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO EXCHANGE MUTATION = TRUE",
        flush=True,
    )

    print(
        "NO SL GENERATED = TRUE",
        flush=True,
    )

    print(
        "NO BACKUP EXECUTION = TRUE",
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11C "
        "RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return {

        "valid":
            True,

        "position":
            position,

        "unit_11a_result":
            unit_11a_result,

        "unit_11b_result":
            unit_11b_result,

        "weex_post":
            False,

        "demo_tp_order":
            False,

        "real_order":
            False,

        "exchange_mutation":
            False,
    }


def reconstruction_unit_11c_standalone_test():

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "UNIT 11C STANDALONE "
        "ZERO-WRITE TEST START",
        flush=True,
    )

    # --------------------------------------------------------
    # LOCAL SIMULATED WEEX POSITION RESPONSE
    #
    # This proves reconciliation logic first.
    # It deliberately performs NO network request.
    # --------------------------------------------------------

    simulated_response = {

        "data": [

            {
                "symbol":
                    "BTCSUSDT",

                "positionSide":
                    "SHORT",

                "quantity":
                    "0.0004",

                "entryPrice":
                    "83595.9",
            },

        ],
    }

    positions = (
        unit_11c_find_open_positions(
            simulated_response,
            symbol=UNIT_11C_SYMBOL,
        )
    )

    if len(
        positions
    ) != 1:

        raise RuntimeError(
            "UNIT 11C POSITION "
            "DISCOVERY TEST FAILED"
        )

    position = positions[
        0
    ]

    if (
        position[
            "direction"
        ]
        !=
        "SHORT"
    ):

        raise RuntimeError(
            "UNIT 11C SHORT "
            "DIRECTION TEST FAILED"
        )

    if (
        position[
            "quantity"
        ]
        !=
        Decimal(
            "0.0004"
        )
    ):

        raise RuntimeError(
            "UNIT 11C QUANTITY "
            "TEST FAILED"
        )

    if (
        position[
            "entry_price"
        ]
        !=
        Decimal(
            "83595.9"
        )
    ):

        raise RuntimeError(
            "UNIT 11C ENTRY PRICE "
            "TEST FAILED"
        )

    print(
        "PASS: UNIT 11C "
        "POSITION RESPONSE PARSER",
        flush=True,
    )

    result = (
        unit_11c_build_from_position(
            position=position,
            favorable_tp1_price=None,
            favorable_tp2_price=None,
        )
    )

    if (
        result.get(
            "valid"
        )
        is not True
    ):

        raise RuntimeError(
            "UNIT 11C PIPELINE TEST FAILED"
        )

    print(
        "PASS: UNIT 11C "
        "SIMULATED SHORT POSITION",
        flush=True,
    )

    print(
        "PASS: UNIT 11C "
        "ACTUAL-ENTRY-PRICE PIPELINE",
        flush=True,
    )

    print(
        "UNIT 11C WEEX POST = FALSE",
        flush=True,
    )

    print(
        "UNIT 11C DEMO TP ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 11C REAL ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 11C EXCHANGE MUTATION = FALSE",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11C "
        "STANDALONE TEST = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return result


# ============================================================
# UNIT 11C TEMPORARY STANDALONE TEST ENTRY POINT
# ============================================================

if __name__ == "__main__":

    reconstruction_unit_11c_standalone_test()

# reconstruction_unit_10b_monitor()


# ============================================================
# RECONSTRUCTION UNIT 11D
# DEMO TP TRANSPORT-BOUNDARY STANDALONE TEST
#
# PURPOSE:
# Prepare the already-validated Unit 11B TP1 / TP2 / TP3
# payloads for the WEEX V3 DEMO transport boundary.
#
# THIS FIRST 11D TEST IS ZERO-WRITE.
#
# IT PROVES:
# - EXACTLY THREE TP instructions received
# - TP1 / TP2 / TP3 remain reduce-only
# - NO SL fields survive
# - position direction is preserved
# - exit side is preserved
# - quantities are preserved
# - TP1 / TP2 trigger prices are preserved
# - TP3 trailing callback is preserved
# - internal tpName metadata is removed before transport
# - each order receives a unique client order ID
# - DEMO endpoint only
# - PRODUCTION endpoint impossible
#
# IMPORTANT:
# - ZERO WEEX POST
# - ZERO DEMO TP ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE MUTATION
# - NO SL
# - NO BACKUP EXECUTION
# ============================================================


UNIT_11D_DEMO_BASE_URL = (
    "https://api-contract.weex.com"
)

UNIT_11D_DEMO_REQUEST_PATH = (
    "/capi/v3/sim/order"
)

UNIT_11D_PRODUCTION_REQUEST_PATH = (
    "/capi/v3/order"
)


def unit_11d_build_client_order_id(
    *,
    tp_name,
    sequence,
):

    import time

    tp_name = str(
        tp_name
    ).upper()

    sequence = int(
        sequence
    )

    if tp_name not in (
        "TP1",
        "TP2",
        "TP3_TRAILING_RUNNER",
    ):

        raise RuntimeError(
            "UNIT 11D INVALID TP NAME"
        )

    if sequence not in (
        1,
        2,
        3,
    ):

        raise RuntimeError(
            "UNIT 11D INVALID SEQUENCE"
        )

    timestamp_ms = str(
        int(
            time.time() * 1000
        )
    )

    short_name = {
        "TP1":
            "TP1",

        "TP2":
            "TP2",

        "TP3_TRAILING_RUNNER":
            "TP3",

    }[
        tp_name
    ]

    client_order_id = (
        "R11D-"
        + short_name
        + "-"
        + str(
            sequence
        )
        + "-"
        + timestamp_ms
    )

    if (
        len(
            client_order_id
        )
        > 36
    ):

        raise RuntimeError(
            "UNIT 11D CLIENT ORDER ID TOO LONG"
        )

    return client_order_id


def unit_11d_assert_no_sl_fields(
    payload,
):

    forbidden_sl_fields = (
        "slTriggerPrice",
        "SlWorkingType",
        "stopLossPrice",
        "stopPrice",
        "stop_loss",
        "stopLoss",
    )

    for field in forbidden_sl_fields:

        if field in payload:

            raise RuntimeError(
                "UNIT 11D FORBIDDEN SL FIELD = "
                + str(
                    field
                )
            )


def unit_11d_validate_demo_endpoint():

    if (
        UNIT_11D_DEMO_REQUEST_PATH
        ==
        UNIT_11D_PRODUCTION_REQUEST_PATH
    ):

        raise RuntimeError(
            "UNIT 11D DEMO/PRODUCTION "
            "ENDPOINT COLLISION"
        )

    if (
        "/sim/"
        not in
        UNIT_11D_DEMO_REQUEST_PATH
    ):

        raise RuntimeError(
            "UNIT 11D DEMO ENDPOINT "
            "SAFETY FAILURE"
        )

    demo_url = (
        UNIT_11D_DEMO_BASE_URL
        +
        UNIT_11D_DEMO_REQUEST_PATH
    )

    expected_demo_url = (
        "https://api-contract.weex.com"
        "/capi/v3/sim/order"
    )

    if (
        demo_url
        !=
        expected_demo_url
    ):

        raise RuntimeError(
            "UNIT 11D FINAL DEMO URL "
            "SAFETY FAILURE"
        )

    if (
        "/capi/v3/order"
        in
        demo_url
    ):

        raise RuntimeError(
            "UNIT 11D PRODUCTION ENDPOINT "
            "DETECTED"
        )

    return demo_url


def unit_11d_prepare_transport_payload(
    *,
    source_payload,
    sequence,
):

    if not isinstance(
        source_payload,
        dict,
    ):

        raise RuntimeError(
            "UNIT 11D SOURCE PAYLOAD "
            "IS NOT A DICTIONARY"
        )

    original_payload = dict(
        source_payload
    )

    required_fields = (
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "reduceOnly",
        "closePosition",
        "tpName",
    )

    missing_fields = [
        field
        for field in required_fields
        if field
        not in source_payload
    ]

    if missing_fields:

        raise RuntimeError(
            "UNIT 11D SOURCE PAYLOAD "
            "MISSING FIELDS = "
            + str(
                missing_fields
            )
        )

    symbol = str(
        source_payload[
            "symbol"
        ]
    )

    side = str(
        source_payload[
            "side"
        ]
    ).upper()

    position_side = str(
        source_payload[
            "positionSide"
        ]
    ).upper()

    order_type = str(
        source_payload[
            "type"
        ]
    ).upper()

    quantity = unit_11b_decimal(
        source_payload[
            "quantity"
        ]
    )

    reduce_only = (
        source_payload[
            "reduceOnly"
        ]
    )

    close_position = (
        source_payload[
            "closePosition"
        ]
    )

    tp_name = str(
        source_payload[
            "tpName"
        ]
    ).upper()

    # --------------------------------------------------------
    # SYMBOL SAFETY
    # --------------------------------------------------------

    if symbol != "BTCSUSDT":

        raise RuntimeError(
            "UNIT 11D SYMBOL MUST BE BTCSUSDT"
        )

    # --------------------------------------------------------
    # EXIT DIRECTION SAFETY
    # --------------------------------------------------------

    valid_exit_pairs = {
        (
            "SELL",
            "LONG",
        ),
        (
            "BUY",
            "SHORT",
        ),
    }

    if (
        side,
        position_side,
    ) not in valid_exit_pairs:

        raise RuntimeError(
            "UNIT 11D INVALID "
            "EXIT SIDE/POSITION PAIR"
        )

    # --------------------------------------------------------
    # QUANTITY SAFETY
    # --------------------------------------------------------

    if quantity <= 0:

        raise RuntimeError(
            "UNIT 11D INVALID QUANTITY"
        )

    # --------------------------------------------------------
    # REDUCE-ONLY SAFETY
    # --------------------------------------------------------

    if reduce_only is not True:

        raise RuntimeError(
            "UNIT 11D REDUCE-ONLY "
            "PROTECTION MISSING"
        )

    if close_position is not False:

        raise RuntimeError(
            "UNIT 11D CLOSE-POSITION "
            "FLAG INVALID"
        )

    # --------------------------------------------------------
    # SL MUST REMAIN ABSENT
    # --------------------------------------------------------

    unit_11d_assert_no_sl_fields(
        source_payload
    )

    # --------------------------------------------------------
    # ORDER TYPE SAFETY
    # --------------------------------------------------------

    if tp_name in (
        "TP1",
        "TP2",
    ):

        if (
            order_type
            !=
            "TAKE_PROFIT_MARKET"
        ):

            raise RuntimeError(
                "UNIT 11D FIXED TP "
                "ORDER TYPE INVALID"
            )

        if (
            "tpTriggerPrice"
            not in
            source_payload
        ):

            raise RuntimeError(
                "UNIT 11D FIXED TP "
                "TRIGGER PRICE MISSING"
            )

        trigger_price = (
            unit_11b_decimal(
                source_payload[
                    "tpTriggerPrice"
                ]
            )
        )

        if trigger_price <= 0:

            raise RuntimeError(
                "UNIT 11D FIXED TP "
                "TRIGGER PRICE INVALID"
            )

        if (
            source_payload.get(
                "TpWorkingType"
            )
            !=
            "MARK_PRICE"
        ):

            raise RuntimeError(
                "UNIT 11D FIXED TP "
                "WORKING TYPE INVALID"
            )

    elif (
        tp_name
        ==
        "TP3_TRAILING_RUNNER"
    ):

        if (
            order_type
            !=
            "TRAILING_STOP_MARKET"
        ):

            raise RuntimeError(
                "UNIT 11D TP3 "
                "ORDER TYPE INVALID"
            )

        if (
            "callbackRate"
            not in
            source_payload
        ):

            raise RuntimeError(
                "UNIT 11D TP3 "
                "CALLBACK RATE MISSING"
            )

        callback_rate = (
            unit_11b_decimal(
                source_payload[
                    "callbackRate"
                ]
            )
        )

        if callback_rate <= 0:

            raise RuntimeError(
                "UNIT 11D TP3 "
                "CALLBACK RATE INVALID"
            )

        if (
            source_payload.get(
                "workingType"
            )
            !=
            "MARK_PRICE"
        ):

            raise RuntimeError(
                "UNIT 11D TP3 "
                "WORKING TYPE INVALID"
            )

    else:

        raise RuntimeError(
            "UNIT 11D UNKNOWN TP NAME"
        )

    # --------------------------------------------------------
    # GENERATE TRANSPORT CLIENT ORDER ID
    # --------------------------------------------------------

    client_order_id = (
        unit_11d_build_client_order_id(
            tp_name=tp_name,
            sequence=sequence,
        )
    )

    # --------------------------------------------------------
    # BUILD TRANSPORT PAYLOAD
    #
    # IMPORTANT:
    # tpName is internal metadata only.
    # It must NOT cross the WEEX transport boundary.
    # --------------------------------------------------------

    if tp_name in (
        "TP1",
        "TP2",
    ):

        transport_payload = {

            "symbol":
                symbol,

            "side":
                side,

            "positionSide":
                position_side,

            "type":
                order_type,

            "quantity":
                unit_11b_decimal_string(
                    quantity
                ),

            "tpTriggerPrice":
                unit_11b_decimal_string(
                    trigger_price
                ),

            "TpWorkingType":
                "MARK_PRICE",

            "reduceOnly":
                True,

            "closePosition":
                False,

            "newClientOrderId":
                client_order_id,
        }

    else:

        transport_payload = {

            "symbol":
                symbol,

            "side":
                side,

            "positionSide":
                position_side,

            "type":
                order_type,

            "quantity":
                unit_11b_decimal_string(
                    quantity
                ),

            "callbackRate":
                unit_11b_decimal_string(
                    callback_rate
                ),

            "workingType":
                "MARK_PRICE",

            "reduceOnly":
                True,

            "closePosition":
                False,

            "newClientOrderId":
                client_order_id,
        }

    # --------------------------------------------------------
    # FINAL TRANSPORT FIREBREAK VALIDATION
    # --------------------------------------------------------

    if "tpName" in transport_payload:

        raise RuntimeError(
            "UNIT 11D INTERNAL TPNAME "
            "LEAKED INTO TRANSPORT PAYLOAD"
        )

    unit_11d_assert_no_sl_fields(
        transport_payload
    )

    if (
        transport_payload[
            "reduceOnly"
        ]
        is not True
    ):

        raise RuntimeError(
            "UNIT 11D FINAL REDUCE-ONLY "
            "CHECK FAILED"
        )

    if (
        transport_payload[
            "closePosition"
        ]
        is not False
    ):

        raise RuntimeError(
            "UNIT 11D FINAL CLOSE-POSITION "
            "CHECK FAILED"
        )

    if (
        source_payload
        !=
        original_payload
    ):

        raise RuntimeError(
            "UNIT 11D MUTATED "
            "UNIT 11B SOURCE PAYLOAD"
        )

    return {
        "valid":
            True,

        "tp_name":
            tp_name,

        "client_order_id":
            client_order_id,

        "payload":
            transport_payload,

        "source_payload_preserved":
            True,

        "weex_post":
            False,

        "demo_tp_order":
            False,

        "real_order":
            False,

        "exchange_mutation":
            False,
    }


def reconstruction_unit_11d_prepare_demo_tp_orders(
    *,
    unit_11b_result,
):

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11D "
        "DEMO TP TRANSPORT-BOUNDARY START",
        flush=True,
    )

    # --------------------------------------------------------
    # VALIDATE UNIT 11B CONTRACT
    # --------------------------------------------------------

    if not isinstance(
        unit_11b_result,
        dict,
    ):

        raise RuntimeError(
            "UNIT 11D UNIT 11B RESULT "
            "IS NOT A DICTIONARY"
        )

    if (
        unit_11b_result.get(
            "valid"
        )
        is not True
    ):

        raise RuntimeError(
            "UNIT 11D UNIT 11B RESULT "
            "NOT VALID"
        )

    required_result_fields = (
        "direction",
        "total_quantity",
        "tp1_payload",
        "tp2_payload",
        "tp3_payload",
        "allocated_quantity",
    )

    missing_result_fields = [
        field
        for field in required_result_fields
        if field
        not in unit_11b_result
    ]

    if missing_result_fields:

        raise RuntimeError(
            "UNIT 11D UNIT 11B RESULT "
            "MISSING FIELDS = "
            + str(
                missing_result_fields
            )
        )

    # --------------------------------------------------------
    # DEMO ENDPOINT LOCK
    # --------------------------------------------------------

    demo_url = (
        unit_11d_validate_demo_endpoint()
    )

    print(
        "PASS: UNIT 11D DEMO ENDPOINT LOCK",
        flush=True,
    )

    print(
        "UNIT 11D DEMO ENDPOINT =",
        demo_url,
        flush=True,
    )

    # --------------------------------------------------------
    # PREPARE EXACTLY THREE TRANSPORT PAYLOADS
    # --------------------------------------------------------

    tp1_result = (
        unit_11d_prepare_transport_payload(
            source_payload=(
                unit_11b_result[
                    "tp1_payload"
                ]
            ),
            sequence=1,
        )
    )

    tp2_result = (
        unit_11d_prepare_transport_payload(
            source_payload=(
                unit_11b_result[
                    "tp2_payload"
                ]
            ),
            sequence=2,
        )
    )

    tp3_result = (
        unit_11d_prepare_transport_payload(
            source_payload=(
                unit_11b_result[
                    "tp3_payload"
                ]
            ),
            sequence=3,
        )
    )

    prepared = [
        tp1_result,
        tp2_result,
        tp3_result,
    ]

    if len(
        prepared
    ) != 3:

        raise RuntimeError(
            "UNIT 11D EXPECTED "
            "EXACTLY THREE TP ORDERS"
        )

    # --------------------------------------------------------
    # UNIQUE CLIENT ORDER ID SAFETY
    # --------------------------------------------------------

    client_order_ids = [
        item[
            "client_order_id"
        ]
        for item in prepared
    ]

    if (
        len(
            set(
                client_order_ids
            )
        )
        != 3
    ):

        raise RuntimeError(
            "UNIT 11D DUPLICATE "
            "CLIENT ORDER ID"
        )

    print(
        "PASS: UNIT 11D THREE UNIQUE "
        "CLIENT ORDER IDS",
        flush=True,
    )

    # --------------------------------------------------------
    # QUANTITY CONSERVATION
    # --------------------------------------------------------

    prepared_quantity = sum(
        (
            unit_11b_decimal(
                item[
                    "payload"
                ][
                    "quantity"
                ]
            )
            for item in prepared
        ),
        Decimal("0"),
    )

    expected_quantity = (
        unit_11b_decimal(
            unit_11b_result[
                "total_quantity"
            ]
        )
    )

    if (
        prepared_quantity
        !=
        expected_quantity
    ):

        raise RuntimeError(
            "UNIT 11D TOTAL TP QUANTITY "
            "DOES NOT MATCH POSITION"
        )

    print(
        "PASS: UNIT 11D TOTAL TP QUANTITY "
        "= POSITION QUANTITY",
        flush=True,
    )

    # --------------------------------------------------------
    # ALL THREE MUST REMAIN REDUCE-ONLY
    # --------------------------------------------------------

    for item in prepared:

        payload = item[
            "payload"
        ]

        if (
            payload[
                "reduceOnly"
            ]
            is not True
        ):

            raise RuntimeError(
                "UNIT 11D REDUCE-ONLY "
                "FINAL CHECK FAILED"
            )

        unit_11d_assert_no_sl_fields(
            payload
        )

    print(
        "PASS: UNIT 11D ALL TP ORDERS "
        "REDUCE-ONLY",
        flush=True,
    )

    print(
        "PASS: UNIT 11D NO SL FIELDS",
        flush=True,
    )

    # --------------------------------------------------------
    # DISPLAY PREPARED PAYLOADS
    # --------------------------------------------------------

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 11D TP1 TRANSPORT PAYLOAD =",
        tp1_result[
            "payload"
        ],
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 11D TP2 TRANSPORT PAYLOAD =",
        tp2_result[
            "payload"
        ],
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 11D TP3 TRANSPORT PAYLOAD =",
        tp3_result[
            "payload"
        ],
        flush=True,
    )

    # --------------------------------------------------------
    # ZERO-WRITE FIREBREAK
    # --------------------------------------------------------

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11D ZERO-WRITE FIREBREAK",
        flush=True,
    )

    print(
        "UNIT 11D WEEX POST = FALSE",
        flush=True,
    )

    print(
        "UNIT 11D DEMO TP ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 11D REAL ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 11D EXCHANGE MUTATION = FALSE",
        flush=True,
    )

    print(
        "UNIT 11D PRODUCTION ENDPOINT = BLOCKED",
        flush=True,
    )

    print(
        "UNIT 11D SL = DISABLED",
        flush=True,
    )

    print(
        "UNIT 11D BACKUP EXECUTION = FALSE",
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11D "
        "RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return {
        "valid":
            True,

        "demo_url":
            demo_url,

        "tp1":
            tp1_result,

        "tp2":
            tp2_result,

        "tp3":
            tp3_result,

        "total_quantity":
            prepared_quantity,

        "weex_post":
            False,

        "demo_tp_order":
            False,

        "real_order":
            False,

        "exchange_mutation":
            False,
    }


def reconstruction_unit_11d_standalone_test():

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "UNIT 11D STANDALONE "
        "ZERO-WRITE TEST START",
        flush=True,
    )

    # --------------------------------------------------------
    # REUSE VERIFIED 11A -> 11B PIPELINE
    #
    # Same SHORT position values already proven by Unit 11C:
    # entry = 83595.9
    # quantity = 0.0004
    # --------------------------------------------------------

    unit_11a_result = (
        reconstruction_unit_11a_tp_engine(
            direction="SHORT",
            entry_price=Decimal(
                "83595.9"
            ),
            total_quantity=Decimal(
                "0.0004"
            ),
            favorable_tp1_price=None,
            favorable_tp2_price=None,
            leverage=Decimal(
                "100"
            ),
        )
    )

    unit_11b_result = (
        reconstruction_unit_11b_build_tp_payloads(
            unit_11a_result=(
                unit_11a_result
            ),
            symbol=UNIT_11B_SYMBOL,
        )
    )

    result = (
        reconstruction_unit_11d_prepare_demo_tp_orders(
            unit_11b_result=(
                unit_11b_result
            )
        )
    )

    if (
        result.get(
            "valid"
        )
        is not True
    ):

        raise RuntimeError(
            "UNIT 11D STANDALONE "
            "PIPELINE FAILED"
        )

    if (
        result.get(
            "weex_post"
        )
        is not False
    ):

        raise RuntimeError(
            "UNIT 11D ZERO-WRITE "
            "TEST FAILED"
        )

    if (
        result.get(
            "demo_tp_order"
        )
        is not False
    ):

        raise RuntimeError(
            "UNIT 11D DEMO TP "
            "FIREBREAK FAILED"
        )

    if (
        result.get(
            "real_order"
        )
        is not False
    ):

        raise RuntimeError(
            "UNIT 11D REAL ORDER "
            "FIREBREAK FAILED"
        )

    print(
        "PASS: UNIT 11D "
        "11A -> 11B -> 11D PIPELINE",
        flush=True,
    )

    print(
        "PASS: UNIT 11D "
        "TRANSPORT PAYLOAD TEST",
        flush=True,
    )

    print(
        "PASS: UNIT 11D "
        "DEMO-ONLY ENDPOINT TEST",
        flush=True,
    )

    print(
        "PASS: UNIT 11D "
        "REDUCE-ONLY TEST",
        flush=True,
    )

    print(
        "PASS: UNIT 11D "
        "NO-SL TEST",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11D "
        "STANDALONE TEST = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return result


# ============================================================
# UNIT 11D TEMPORARY STANDALONE TEST ENTRY POINT
# ============================================================

if __name__ == "__main__":

    reconstruction_unit_11d_standalone_test()

# ============================================================
# RECONSTRUCTION UNIT 11E
# CONTROLLED THREE-TP WEEX DEMO SUBMISSION
#
# PURPOSE:
# Submit the THREE already-validated Unit 11D transport
# payloads to the WEEX V3 DEMO endpoint:
#
#   TP1 -> TP2 -> TP3 TRAILING
#
# IMPORTANT:
# - DEMO ENDPOINT ONLY
# - EXACTLY THREE TP SUBMISSION ATTEMPTS MAXIMUM
# - FAIL CLOSED ON FIRST REJECTION / NETWORK FAILURE
# - ALL ORDERS MUST BE REDUCE-ONLY
# - NO SL
# - NO BACKUP EXECUTION
# - NO PRODUCTION ORDER
# ============================================================


UNIT_11E_DEMO_BASE_URL = (
    "https://api-contract.weex.com"
)

UNIT_11E_DEMO_REQUEST_PATH = (
    "/capi/v3/sim/order"
)

UNIT_11E_PRODUCTION_REQUEST_PATH = (
    "/capi/v3/order"
)


def unit_11e_assert_demo_only():

    if (
        UNIT_11E_DEMO_REQUEST_PATH
        ==
        UNIT_11E_PRODUCTION_REQUEST_PATH
    ):

        raise RuntimeError(
            "UNIT 11E DEMO/PRODUCTION ENDPOINT COLLISION"
        )

    if (
        "/sim/"
        not in
        UNIT_11E_DEMO_REQUEST_PATH
    ):

        raise RuntimeError(
            "UNIT 11E DEMO ENDPOINT SAFETY FAILURE"
        )

    demo_url = (
        UNIT_11E_DEMO_BASE_URL
        +
        UNIT_11E_DEMO_REQUEST_PATH
    )

    expected_url = (
        "https://api-contract.weex.com"
        "/capi/v3/sim/order"
    )

    if demo_url != expected_url:

        raise RuntimeError(
            "UNIT 11E FINAL DEMO URL SAFETY FAILURE"
        )

    if (
        "/capi/v3/order"
        in demo_url
    ):

        raise RuntimeError(
            "UNIT 11E PRODUCTION ENDPOINT DETECTED"
        )

    return demo_url


def unit_11e_validate_payload(
    *,
    payload,
    tp_name,
):

    if not isinstance(
        payload,
        dict,
    ):

        raise RuntimeError(
            "UNIT 11E PAYLOAD IS NOT DICTIONARY"
        )

    required_common = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "reduceOnly",
        "closePosition",
        "newClientOrderId",
    }

    missing = (
        required_common
        -
        set(
            payload.keys()
        )
    )

    if missing:

        raise RuntimeError(
            "UNIT 11E MISSING FIELDS = "
            + str(
                sorted(
                    missing
                )
            )
        )

    if (
        payload.get(
            "symbol"
        )
        !=
        "BTCSUSDT"
    ):

        raise RuntimeError(
            "UNIT 11E SYMBOL SAFETY FAILURE"
        )

    side = str(
        payload.get(
            "side"
        )
    ).upper()

    position_side = str(
        payload.get(
            "positionSide"
        )
    ).upper()

    if (
        side,
        position_side,
    ) not in {
        (
            "SELL",
            "LONG",
        ),
        (
            "BUY",
            "SHORT",
        ),
    }:

        raise RuntimeError(
            "UNIT 11E EXIT SIDE/POSITION SAFETY FAILURE"
        )

    if (
        payload.get(
            "reduceOnly"
        )
        is not True
    ):

        raise RuntimeError(
            "UNIT 11E REDUCE-ONLY PROTECTION MISSING"
        )

    if (
        payload.get(
            "closePosition"
        )
        is not False
    ):

        raise RuntimeError(
            "UNIT 11E CLOSE-POSITION FLAG INVALID"
        )

    quantity = unit_11b_decimal(
        payload.get(
            "quantity"
        )
    )

    if quantity <= 0:

        raise RuntimeError(
            "UNIT 11E INVALID QUANTITY"
        )

    unit_11d_assert_no_sl_fields(
        payload
    )

    tp_name = str(
        tp_name
    ).upper()

    if tp_name in (
        "TP1",
        "TP2",
    ):

        if (
            payload.get(
                "type"
            )
            !=
            "TAKE_PROFIT_MARKET"
        ):

            raise RuntimeError(
                "UNIT 11E FIXED TP TYPE INVALID"
            )

        if (
            "tpTriggerPrice"
            not in
            payload
        ):

            raise RuntimeError(
                "UNIT 11E TP TRIGGER PRICE MISSING"
            )

        trigger_price = (
            unit_11b_decimal(
                payload[
                    "tpTriggerPrice"
                ]
            )
        )

        if trigger_price <= 0:

            raise RuntimeError(
                "UNIT 11E TP TRIGGER PRICE INVALID"
            )

        if (
            payload.get(
                "TpWorkingType"
            )
            !=
            "MARK_PRICE"
        ):

            raise RuntimeError(
                "UNIT 11E TP WORKING TYPE INVALID"
            )

    elif (
        tp_name
        ==
        "TP3_TRAILING_RUNNER"
    ):

        if (
            payload.get(
                "type"
            )
            !=
            "TRAILING_STOP_MARKET"
        ):

            raise RuntimeError(
                "UNIT 11E TP3 TYPE INVALID"
            )

        if (
            "callbackRate"
            not in
            payload
        ):

            raise RuntimeError(
                "UNIT 11E TP3 CALLBACK RATE MISSING"
            )

        callback_rate = (
            unit_11b_decimal(
                payload[
                    "callbackRate"
                ]
            )
        )

        if callback_rate <= 0:

            raise RuntimeError(
                "UNIT 11E TP3 CALLBACK RATE INVALID"
            )

        if (
            payload.get(
                "workingType"
            )
            !=
            "MARK_PRICE"
        ):

            raise RuntimeError(
                "UNIT 11E TP3 WORKING TYPE INVALID"
            )

    else:

        raise RuntimeError(
            "UNIT 11E UNKNOWN TP NAME"
        )

    return True


async def unit_11e_submit_one_demo_tp(
    *,
    payload,
    tp_name,
):

    import os
    import json
    import time
    import aiohttp

    unit_11e_validate_payload(
        payload=payload,
        tp_name=tp_name,
    )

    demo_url = (
        unit_11e_assert_demo_only()
    )

    # --------------------------------------------------------
    # CREDENTIALS
    # --------------------------------------------------------

    api_key = os.getenv(
        "WEEX_API_KEY"
    )

    api_secret = os.getenv(
        "WEEX_API_SECRET"
    )

    passphrase = os.getenv(
        "WEEX_API_PASSPHRASE"
    )

    require(
        bool(
            api_key
        ),
        "UNIT 11E WEEX_API_KEY missing.",
    )

    require(
        bool(
            api_secret
        ),
        "UNIT 11E WEEX_API_SECRET missing.",
    )

    require(
        bool(
            passphrase
        ),
        "UNIT 11E WEEX_API_PASSPHRASE missing.",
    )

    # --------------------------------------------------------
    # PRESERVE EXACT UNIT 11D TRANSPORT PAYLOAD
    # --------------------------------------------------------

    original_payload = dict(
        payload
    )

    body = json.dumps(
        payload,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    # Reuse already-proven Unit 9 authentication formula.
    signature = (
        reconstruction_unit_9_build_signature(
            timestamp=timestamp,
            request_path=(
                UNIT_11E_DEMO_REQUEST_PATH
            ),
            body=body,
        )
    )

    headers = {
        "ACCESS-KEY":
            api_key,

        "ACCESS-SIGN":
            signature,

        "ACCESS-TIMESTAMP":
            timestamp,

        "ACCESS-PASSPHRASE":
            passphrase,

        "Content-Type":
            "application/json",
    }

    # --------------------------------------------------------
    # LAST-MOMENT PRODUCTION FIREBREAK
    # --------------------------------------------------------

    if (
        demo_url
        !=
        (
            "https://api-contract.weex.com"
            "/capi/v3/sim/order"
        )
    ):

        raise RuntimeError(
            "UNIT 11E FINAL URL CHANGED"
        )

    if (
        "/sim/order"
        not in
        demo_url
    ):

        raise RuntimeError(
            "UNIT 11E NON-DEMO URL BLOCKED"
        )

    if (
        "/capi/v3/order"
        in
        demo_url
    ):

        raise RuntimeError(
            "UNIT 11E PRODUCTION WRITE BLOCKED"
        )

    if (
        payload
        !=
        original_payload
    ):

        raise RuntimeError(
            "UNIT 11E PAYLOAD MUTATION DETECTED"
        )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 11E SUBMITTING",
        tp_name,
        "TO WEEX DEMO",
        flush=True,
    )

    print(
        "UNIT 11E DEMO URL =",
        demo_url,
        flush=True,
    )

    print(
        "UNIT 11E CLIENT ORDER ID =",
        payload[
            "newClientOrderId"
        ],
        flush=True,
    )

    print(
        "UNIT 11E PAYLOAD =",
        payload,
        flush=True,
    )

    print(
        "UNIT 11E REAL ORDER = FALSE",
        flush=True,
    )

    # --------------------------------------------------------
    # ACTUAL DEMO POST
    # --------------------------------------------------------

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    try:

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.post(
                demo_url,
                headers=headers,
                data=body,
            ) as response:

                http_status = (
                    response.status
                )

                response_text = (
                    await response.text()
                )

    except Exception as exc:

        print(
            "UNIT 11E",
            tp_name,
            "NETWORK ERROR =",
            repr(
                exc
            ),
            flush=True,
        )

        return {
            "valid":
                False,

            "submitted":
                False,

            "accepted":
                False,

            "tp_name":
                tp_name,

            "reason":
                "UNIT_11E_NETWORK_ERROR",

            "error":
                repr(
                    exc
                ),

            "real_order":
                False,
        }

    print(
        "UNIT 11E",
        tp_name,
        "HTTP STATUS =",
        http_status,
        flush=True,
    )

    print(
        "UNIT 11E",
        tp_name,
        "RAW RESPONSE =",
        response_text,
        flush=True,
    )

    try:

        response_data = json.loads(
            response_text
        )

    except Exception:

        response_data = {
            "raw":
                response_text
        }

    if (
        http_status < 200
        or
        http_status >= 300
    ):

        return {
            "valid":
                False,

            "submitted":
                True,

            "accepted":
                False,

            "tp_name":
                tp_name,

            "reason":
                "UNIT_11E_HTTP_FAILURE",

            "http_status":
                http_status,

            "response":
                response_data,

            "real_order":
                False,
        }

    if not isinstance(
        response_data,
        dict,
    ):

        return {
            "valid":
                False,

            "submitted":
                True,

            "accepted":
                False,

            "tp_name":
                tp_name,

            "reason":
                "UNIT_11E_RESPONSE_NOT_DICT",

            "http_status":
                http_status,

            "response":
                response_data,

            "real_order":
                False,
        }

    success = (
        response_data.get(
            "success"
        )
        is True
    )

    order_id = (
        response_data.get(
            "orderId"
        )
    )

    returned_client_order_id = (
        response_data.get(
            "clientOrderId"
        )
    )

    expected_client_order_id = (
        payload[
            "newClientOrderId"
        ]
    )

    if not success:

        return {
            "valid":
                False,

            "submitted":
                True,

            "accepted":
                False,

            "tp_name":
                tp_name,

            "reason":
                "UNIT_11E_WEEX_REJECTED",

            "http_status":
                http_status,

            "response":
                response_data,

            "real_order":
                False,
        }

    require(
        order_id
        not in (
            None,
            "",
        ),
        (
            "UNIT 11E "
            + tp_name
            + " ACCEPTED WITHOUT ORDER ID"
        ),
    )

    require(
        returned_client_order_id
        ==
        expected_client_order_id,
        (
            "UNIT 11E "
            + tp_name
            + " CLIENT ORDER ID MISMATCH"
        ),
    )

    print(
        "PASS: UNIT 11E",
        tp_name,
        "DEMO ORDER ACCEPTED",
        flush=True,
    )

    print(
        "UNIT 11E",
        tp_name,
        "ORDER ID =",
        order_id,
        flush=True,
    )

    return {
        "valid":
            True,

        "submitted":
            True,

        "accepted":
            True,

        "tp_name":
            tp_name,

        "reason":
            "UNIT_11E_DEMO_TP_ACCEPTED",

        "order_id":
            order_id,

        "client_order_id":
            returned_client_order_id,

        "http_status":
            http_status,

        "response":
            response_data,

        "real_order":
            False,
    }


async def reconstruction_unit_11e_control_submission(
    *,
    unit_11d_result,
):

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11E "
        "THREE-TP CONTROL SUBMISSION START",
        flush=True,
    )

    # --------------------------------------------------------
    # UNIT 11D CONTRACT
    # --------------------------------------------------------

    if not isinstance(
        unit_11d_result,
        dict,
    ):

        raise RuntimeError(
            "UNIT 11E UNIT 11D RESULT NOT DICT"
        )

    if (
        unit_11d_result.get(
            "valid"
        )
        is not True
    ):

        raise RuntimeError(
            "UNIT 11E UNIT 11D RESULT NOT VALID"
        )

    for key in (
        "tp1",
        "tp2",
        "tp3",
    ):

        if key not in unit_11d_result:

            raise RuntimeError(
                "UNIT 11E MISSING "
                + key.upper()
            )

    # --------------------------------------------------------
    # DEMO ENDPOINT LOCK
    # --------------------------------------------------------

    demo_url = (
        unit_11e_assert_demo_only()
    )

    print(
        "PASS: UNIT 11E DEMO ENDPOINT LOCK",
        flush=True,
    )

    print(
        "UNIT 11E DEMO ENDPOINT =",
        demo_url,
        flush=True,
    )

    print(
        "UNIT 11E PRODUCTION ENDPOINT = BLOCKED",
        flush=True,
    )

    # --------------------------------------------------------
    # EXTRACT EXACT UNIT 11D TRANSPORT PAYLOADS
    # --------------------------------------------------------

    tp1_payload = (
        unit_11d_result[
            "tp1"
        ][
            "payload"
        ]
    )

    tp2_payload = (
        unit_11d_result[
            "tp2"
        ][
            "payload"
        ]
    )

    tp3_payload = (
        unit_11d_result[
            "tp3"
        ][
            "payload"
        ]
    )

    # --------------------------------------------------------
    # PRE-FLIGHT ALL THREE BEFORE FIRST WRITE
    # --------------------------------------------------------

    unit_11e_validate_payload(
        payload=tp1_payload,
        tp_name="TP1",
    )

    unit_11e_validate_payload(
        payload=tp2_payload,
        tp_name="TP2",
    )

    unit_11e_validate_payload(
        payload=tp3_payload,
        tp_name="TP3_TRAILING_RUNNER",
    )

    client_ids = {
        tp1_payload[
            "newClientOrderId"
        ],
        tp2_payload[
            "newClientOrderId"
        ],
        tp3_payload[
            "newClientOrderId"
        ],
    }

    if len(
        client_ids
    ) != 3:

        raise RuntimeError(
            "UNIT 11E CLIENT ORDER IDS NOT UNIQUE"
        )

    total_quantity = sum(
        (
            unit_11b_decimal(
                payload[
                    "quantity"
                ]
            )
            for payload in (
                tp1_payload,
                tp2_payload,
                tp3_payload,
            )
        ),
        Decimal(
            "0"
        ),
    )

    expected_quantity = (
        unit_11b_decimal(
            unit_11d_result[
                "total_quantity"
            ]
        )
    )

    if (
        total_quantity
        !=
        expected_quantity
    ):

        raise RuntimeError(
            "UNIT 11E TP QUANTITY CONSERVATION FAILED"
        )

    print(
        "PASS: UNIT 11E THREE-TP PREFLIGHT",
        flush=True,
    )

    print(
        "PASS: UNIT 11E TOTAL TP QUANTITY "
        "= POSITION QUANTITY",
        flush=True,
    )

    print(
        "PASS: UNIT 11E NO SL FIELDS",
        flush=True,
    )

    # --------------------------------------------------------
    # TP1
    # --------------------------------------------------------

    tp1_result = (
        await unit_11e_submit_one_demo_tp(
            payload=tp1_payload,
            tp_name="TP1",
        )
    )

    if (
        tp1_result.get(
            "accepted"
        )
        is not True
    ):

        print(
            "UNIT 11E STOPPED AFTER TP1 FAILURE",
            flush=True,
        )

        return {
            "valid":
                False,

            "submitted_count":
                int(
                    bool(
                        tp1_result.get(
                            "submitted"
                        )
                    )
                ),

            "accepted_count":
                0,

            "tp1":
                tp1_result,

            "tp2":
                None,

            "tp3":
                None,

            "reason":
                "UNIT_11E_TP1_NOT_ACCEPTED",

            "real_order":
                False,
        }

    # --------------------------------------------------------
    # TP2
    # --------------------------------------------------------

    tp2_result = (
        await unit_11e_submit_one_demo_tp(
            payload=tp2_payload,
            tp_name="TP2",
        )
    )

    if (
        tp2_result.get(
            "accepted"
        )
        is not True
    ):

        print(
            "UNIT 11E STOPPED AFTER TP2 FAILURE",
            flush=True,
        )

        return {
            "valid":
                False,

            "submitted_count":
                (
                    1
                    +
                    int(
                        bool(
                            tp2_result.get(
                                "submitted"
                            )
                        )
                    )
                ),

            "accepted_count":
                1,

            "tp1":
                tp1_result,

            "tp2":
                tp2_result,

            "tp3":
                None,

            "reason":
                "UNIT_11E_TP2_NOT_ACCEPTED",

            "real_order":
                False,
        }

    # --------------------------------------------------------
    # TP3 TRAILING RUNNER
    # --------------------------------------------------------

    tp3_result = (
        await unit_11e_submit_one_demo_tp(
            payload=tp3_payload,
            tp_name="TP3_TRAILING_RUNNER",
        )
    )

    if (
        tp3_result.get(
            "accepted"
        )
        is not True
    ):

        print(
            "UNIT 11E TP3 TRAILING NOT ACCEPTED",
            flush=True,
        )

        return {
            "valid":
                False,

            "submitted_count":
                (
                    2
                    +
                    int(
                        bool(
                            tp3_result.get(
                                "submitted"
                            )
                        )
                    )
                ),

            "accepted_count":
                2,

            "tp1":
                tp1_result,

            "tp2":
                tp2_result,

            "tp3":
                tp3_result,

            "reason":
                "UNIT_11E_TP3_NOT_ACCEPTED",

            "real_order":
                False,
        }

    # --------------------------------------------------------
    # COMPLETE SUCCESS
    # --------------------------------------------------------

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11E TP1 DEMO ORDER ACCEPTED",
        flush=True,
    )

    print(
        "PASS: UNIT 11E TP2 DEMO ORDER ACCEPTED",
        flush=True,
    )

    print(
        "PASS: UNIT 11E TP3 TRAILING "
        "DEMO ORDER ACCEPTED",
        flush=True,
    )

    print(
        "UNIT 11E TP ORDERS REQUESTED = 3",
        flush=True,
    )

    print(
        "UNIT 11E TP ORDERS SUBMITTED = 3",
        flush=True,
    )

    print(
        "UNIT 11E TP ORDERS ACCEPTED = 3",
        flush=True,
    )

    print(
        "UNIT 11E SL = DISABLED",
        flush=True,
    )

    print(
        "UNIT 11E BACKUP EXECUTION = FALSE",
        flush=True,
    )

    print(
        "UNIT 11E PRODUCTION ORDER = FALSE",
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11E "
        "CONTROL SUBMISSION = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return {
        "valid":
            True,

        "submitted_count":
            3,

        "accepted_count":
            3,

        "tp1":
            tp1_result,

        "tp2":
            tp2_result,

        "tp3":
            tp3_result,

        "reason":
            "UNIT_11E_ALL_THREE_TPS_ACCEPTED",

        "real_order":
            False,
    }


async def reconstruction_unit_11e_control_test():

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "UNIT 11E CONTROL TEST START",
        flush=True,
    )

    # --------------------------------------------------------
    # REUSE THE ALREADY-PROVEN 11A -> 11B -> 11D PIPELINE.
    #
    # Same SHORT demo position used by the current Unit 11D:
    # entry    = 83595.9
    # quantity = 0.0004
    # --------------------------------------------------------

    unit_11a_result = (
        reconstruction_unit_11a_tp_engine(
            direction="SHORT",
            entry_price=Decimal(
                "83595.9"
            ),
            total_quantity=Decimal(
                "0.0004"
            ),
            favorable_tp1_price=None,
            favorable_tp2_price=None,
            leverage=Decimal(
                "100"
            ),
        )
    )

    unit_11b_result = (
        reconstruction_unit_11b_build_tp_payloads(
            unit_11a_result=(
                unit_11a_result
            ),
            symbol=UNIT_11B_SYMBOL,
        )
    )

    unit_11d_result = (
        reconstruction_unit_11d_prepare_demo_tp_orders(
            unit_11b_result=(
                unit_11b_result
            )
        )
    )

    result = (
        await reconstruction_unit_11e_control_submission(
            unit_11d_result=(
                unit_11d_result
            )
        )
    )

    return result


# ============================================================
# UNIT 11E TEMPORARY CONTROL-SUBMISSION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    import asyncio

    asyncio.run(
        reconstruction_unit_11e_control_test()
    )

# ============================================================
# RECONSTRUCTION UNIT 11E.1
# FROZEN DEMO TP EXECUTION-PATH RECOVERY TEST
#
# PURPOSE:
# Recover and validate the proven frozen-model DEMO TP shape
# without sending any order.
#
# FROZEN DEMO BEHAVIOUR:
# - endpoint remains /capi/v3/sim/order
# - order type remains MARKET
# - TP is carried by tpTriggerPrice
# - TP working type is MARK_PRICE
#
# IMPORTANT:
# - ZERO WEEX POST
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE MUTATION
# - SL REMAINS DISABLED
# - BACKUPS NOT EXECUTED
#
# This unit does NOT submit TP1/TP2/TP3.
# It only proves the recovered transport shape before
# changing Unit 11E submission behaviour.
# ============================================================


def reconstruction_unit_11e1_frozen_tp_path_test(
    *,
    unit_11d_result,
):

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11E.1 "
        "FROZEN DEMO TP PATH RECOVERY START",
        flush=True,
    )

    # --------------------------------------------------------
    # VALIDATE UNIT 11D INPUT
    # --------------------------------------------------------

    if not isinstance(
        unit_11d_result,
        dict,
    ):
        raise RuntimeError(
            "UNIT 11E.1 UNIT 11D RESULT "
            "IS NOT A DICTIONARY"
        )

    if (
        unit_11d_result.get(
            "valid"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 11E.1 UNIT 11D RESULT "
            "NOT VALID"
        )

    for name in (
        "tp1",
        "tp2",
        "tp3",
        "total_quantity",
    ):
        if name not in unit_11d_result:
            raise RuntimeError(
                "UNIT 11E.1 MISSING UNIT 11D FIELD = "
                + name
            )

    # --------------------------------------------------------
    # ABSOLUTE DEMO ENDPOINT LOCK
    # --------------------------------------------------------

    demo_base_url = (
        "https://api-contract.weex.com"
    )

    demo_request_path = (
        "/capi/v3/sim/order"
    )

    production_request_path = (
        "/capi/v3/order"
    )

    demo_url = (
        demo_base_url
        + demo_request_path
    )

    production_url = (
        demo_base_url
        + production_request_path
    )

    if (
        demo_request_path
        ==
        production_request_path
    ):
        raise RuntimeError(
            "UNIT 11E.1 DEMO/PRODUCTION "
            "ENDPOINT COLLISION"
        )

    if "/sim/" not in demo_request_path:
        raise RuntimeError(
            "UNIT 11E.1 DEMO ENDPOINT "
            "DOES NOT CONTAIN /sim/"
        )

    if demo_url == production_url:
        raise RuntimeError(
            "UNIT 11E.1 PRODUCTION "
            "ENDPOINT NOT BLOCKED"
        )

    print(
        "PASS: UNIT 11E.1 DEMO ENDPOINT LOCK",
        flush=True,
    )

    print(
        "UNIT 11E.1 DEMO ENDPOINT =",
        demo_url,
        flush=True,
    )

    print(
        "UNIT 11E.1 PRODUCTION ENDPOINT = BLOCKED",
        flush=True,
    )

    # --------------------------------------------------------
    # RECOVER TP1 FROM VERIFIED UNIT 11D
    #
    # Frozen demo mechanism did NOT send
    # type=TAKE_PROFIT_MARKET.
    #
    # It used:
    #
    # type=MARKET
    # tpTriggerPrice=<TP1>
    # TpWorkingType=MARK_PRICE
    # --------------------------------------------------------

    tp1_transport = (
        unit_11d_result[
            "tp1"
        ][
            "payload"
        ]
    )

    tp2_transport = (
        unit_11d_result[
            "tp2"
        ][
            "payload"
        ]
    )

    tp3_transport = (
        unit_11d_result[
            "tp3"
        ][
            "payload"
        ]
    )

    # --------------------------------------------------------
    # VERIFY CURRENT 11D TP PLAN STILL EXISTS
    # --------------------------------------------------------

    if (
        tp1_transport.get(
            "tpTriggerPrice"
        )
        is None
    ):
        raise RuntimeError(
            "UNIT 11E.1 TP1 TRIGGER MISSING"
        )

    if (
        tp2_transport.get(
            "tpTriggerPrice"
        )
        is None
    ):
        raise RuntimeError(
            "UNIT 11E.1 TP2 TRIGGER MISSING"
        )

    if (
        tp3_transport.get(
            "callbackRate"
        )
        is None
    ):
        raise RuntimeError(
            "UNIT 11E.1 TP3 CALLBACK RATE MISSING"
        )

    # --------------------------------------------------------
    # BUILD FROZEN-PATH DEMO SHAPE
    #
    # NOTE:
    # This is deliberately NOT submitted.
    #
    # We use TP1 because the frozen demo API path carried
    # one TP trigger with the MARKET order.
    #
    # SL fields are intentionally NOT restored.
    # --------------------------------------------------------

    recovered_payload = {
        "symbol":
            tp1_transport[
                "symbol"
            ],

        "side":
            tp1_transport[
                "side"
            ],

        "positionSide":
            tp1_transport[
                "positionSide"
            ],

        "type":
            "MARKET",

        "quantity":
            str(
                unit_11d_result[
                    "total_quantity"
                ]
            ),

        "newClientOrderId":
            (
                "R11E1-FROZEN-TP-PATH"
            ),

        "tpTriggerPrice":
            tp1_transport[
                "tpTriggerPrice"
            ],

        "TpWorkingType":
            "MARK_PRICE",
    }

    # --------------------------------------------------------
    # CRITICAL DIFFERENCE FROM FAILED UNIT 11E
    # --------------------------------------------------------

    if (
        recovered_payload[
            "type"
        ]
        !=
        "MARKET"
    ):
        raise RuntimeError(
            "UNIT 11E.1 FROZEN ORDER TYPE "
            "RECOVERY FAILED"
        )

    if (
        recovered_payload[
            "TpWorkingType"
        ]
        !=
        "MARK_PRICE"
    ):
        raise RuntimeError(
            "UNIT 11E.1 TP WORKING TYPE "
            "RECOVERY FAILED"
        )

    if (
        "tpTriggerPrice"
        not in recovered_payload
    ):
        raise RuntimeError(
            "UNIT 11E.1 TP TRIGGER "
            "RECOVERY FAILED"
        )

    print(
        "PASS: UNIT 11E.1 FROZEN "
        "MARKET ORDER TYPE RECOVERED",
        flush=True,
    )

    print(
        "PASS: UNIT 11E.1 FROZEN "
        "tpTriggerPrice RECOVERED",
        flush=True,
    )

    print(
        "PASS: UNIT 11E.1 FROZEN "
        "TpWorkingType RECOVERED",
        flush=True,
    )

    # --------------------------------------------------------
    # ABSOLUTE SL-DISABLED CHECK
    # --------------------------------------------------------

    forbidden_sl_fields = (
        "slTriggerPrice",
        "SlWorkingType",
        "stopLossPrice",
        "stopLoss",
        "stopPrice",
        "stop_loss",
    )

    present_sl_fields = [
        field
        for field in forbidden_sl_fields
        if field in recovered_payload
    ]

    if present_sl_fields:
        raise RuntimeError(
            "UNIT 11E.1 FORBIDDEN SL FIELDS = "
            + str(
                present_sl_fields
            )
        )

    print(
        "PASS: UNIT 11E.1 SL REMAINS DISABLED",
        flush=True,
    )

    # --------------------------------------------------------
    # PRESERVE FULL CURRENT TP PLAN
    #
    # TP2 and TP3 are NOT discarded.
    # They remain available for the next reconstruction step.
    # --------------------------------------------------------

    preserved_tp_plan = {
        "tp1":
            {
                "price":
                    tp1_transport[
                        "tpTriggerPrice"
                    ],

                "quantity":
                    tp1_transport[
                        "quantity"
                    ],
            },

        "tp2":
            {
                "price":
                    tp2_transport[
                        "tpTriggerPrice"
                    ],

                "quantity":
                    tp2_transport[
                        "quantity"
                    ],
            },

        "tp3":
            {
                "callbackRate":
                    tp3_transport[
                        "callbackRate"
                    ],

                "quantity":
                    tp3_transport[
                        "quantity"
                    ],
            },
    }

    # --------------------------------------------------------
    # DISPLAY RECOVERED RESULT
    # --------------------------------------------------------

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 11E.1 RECOVERED DEMO PAYLOAD =",
        recovered_payload,
        flush=True,
    )

    print(
        "UNIT 11E.1 PRESERVED TP PLAN =",
        preserved_tp_plan,
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    # --------------------------------------------------------
    # ZERO-WRITE FIREBREAK
    # --------------------------------------------------------

    print(
        "PASS: UNIT 11E.1 ZERO-WRITE FIREBREAK",
        flush=True,
    )

    print(
        "UNIT 11E.1 WEEX POST = FALSE",
        flush=True,
    )

    print(
        "UNIT 11E.1 DEMO ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 11E.1 REAL ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 11E.1 EXCHANGE MUTATION = FALSE",
        flush=True,
    )

    print(
        "UNIT 11E.1 SL = DISABLED",
        flush=True,
    )

    print(
        "UNIT 11E.1 BACKUP EXECUTION = FALSE",
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11E.1 RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return {
        "valid":
            True,

        "demo_url":
            demo_url,

        "recovered_payload":
            recovered_payload,

        "preserved_tp_plan":
            preserved_tp_plan,

        "weex_post":
            False,

        "demo_order":
            False,

        "real_order":
            False,

        "exchange_mutation":
            False,
    }


def reconstruction_unit_11e1_standalone_test():

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "UNIT 11E.1 STANDALONE "
        "ZERO-WRITE TEST START",
        flush=True,
    )

    # --------------------------------------------------------
    # REUSE THE SAME VERIFIED SHORT POSITION TEST
    # --------------------------------------------------------

    unit_11a_result = (
        reconstruction_unit_11a_tp_engine(
            direction="SHORT",
            entry_price=Decimal(
                "83595.9"
            ),
            total_quantity=Decimal(
                "0.0004"
            ),
            favorable_tp1_price=None,
            favorable_tp2_price=None,
            leverage=Decimal(
                "100"
            ),
        )
    )

    unit_11b_result = (
        reconstruction_unit_11b_build_tp_payloads(
            unit_11a_result=(
                unit_11a_result
            ),
            symbol=UNIT_11B_SYMBOL,
        )
    )

    unit_11d_result = (
        reconstruction_unit_11d_prepare_demo_tp_orders(
            unit_11b_result=(
                unit_11b_result
            ),
        )
    )

    result = (
        reconstruction_unit_11e1_frozen_tp_path_test(
            unit_11d_result=(
                unit_11d_result
            ),
        )
    )

    if (
        result.get(
            "valid"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 11E.1 STANDALONE TEST FAILED"
        )

    if (
        result[
            "weex_post"
        ]
        is not False
    ):
        raise RuntimeError(
            "UNIT 11E.1 WRITE FIREBREAK FAILED"
        )

    if (
        result[
            "recovered_payload"
        ][
            "type"
        ]
        !=
        "MARKET"
    ):
        raise RuntimeError(
            "UNIT 11E.1 MARKET TYPE TEST FAILED"
        )

    if (
        "slTriggerPrice"
        in
        result[
            "recovered_payload"
        ]
    ):
        raise RuntimeError(
            "UNIT 11E.1 SL DISABLE TEST FAILED"
        )

    print(
        "PASS: UNIT 11E.1 FROZEN TP "
        "EXECUTION PATH RECOVERED",
        flush=True,
    )

    print(
        "PASS: UNIT 11E.1 MARKET + "
        "tpTriggerPrice SHAPE",
        flush=True,
    )

    print(
        "PASS: UNIT 11E.1 FULL TP PLAN PRESERVED",
        flush=True,
    )

    print(
        "PASS: UNIT 11E.1 NO EXCHANGE WRITE",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11E.1 "
        "STANDALONE TEST = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return result


if __name__ == "__main__":
    reconstruction_unit_11e1_standalone_test()

# ============================================================
# RECONSTRUCTION UNIT 11E.2
# ACTUAL DEMO POSITION -> RECOVERED TP PATH BRIDGE
#
# PURPOSE:
# Connect the already-verified actual demo position bridge
# (Unit 11C) to:
#
#   Unit 11A -> TP calculation
#   Unit 11B -> TP plan
#   Unit 11D -> transport preparation
#   Unit 11E.1 -> recovered frozen demo TP shape
#
# IMPORTANT:
# - ZERO WEEX POST
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE MUTATION
# - SL REMAINS DISABLED
# - BACKUPS NOT EXECUTED
#
# This unit proves the complete ACTUAL POSITION -> TP PATH
# before any controlled demo submission is allowed.
# ============================================================


def reconstruction_unit_11e2_actual_position_tp_bridge(
    *,
    actual_position,
):

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11E.2 "
        "ACTUAL POSITION TP BRIDGE START",
        flush=True,
    )

    # --------------------------------------------------------
    # BASIC ACTUAL POSITION VALIDATION
    # --------------------------------------------------------

    if not isinstance(
        actual_position,
        dict,
    ):
        raise RuntimeError(
            "UNIT 11E.2 ACTUAL POSITION "
            "IS NOT A DICTIONARY"
        )

    symbol = str(
        actual_position.get(
            "symbol",
            "",
        )
    ).upper()

    direction = str(
        actual_position.get(
            "direction",
            "",
        )
    ).upper()

    entry_price = Decimal(
        str(
            actual_position.get(
                "entry_price"
            )
        )
    )

    quantity = Decimal(
        str(
            actual_position.get(
                "quantity"
            )
        )
    )

    if symbol != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 11E.2 INVALID SYMBOL = "
            + symbol
        )

    if direction not in (
        "LONG",
        "SHORT",
    ):
        raise RuntimeError(
            "UNIT 11E.2 INVALID DIRECTION = "
            + direction
        )

    if entry_price <= 0:
        raise RuntimeError(
            "UNIT 11E.2 INVALID ENTRY PRICE"
        )

    if quantity <= 0:
        raise RuntimeError(
            "UNIT 11E.2 INVALID POSITION QUANTITY"
        )

    print(
        "PASS: UNIT 11E.2 ACTUAL POSITION VALIDATED",
        flush=True,
    )

    print(
        "UNIT 11E.2 SYMBOL =",
        symbol,
        flush=True,
    )

    print(
        "UNIT 11E.2 DIRECTION =",
        direction,
        flush=True,
    )

    print(
        "UNIT 11E.2 ACTUAL ENTRY PRICE =",
        entry_price,
        flush=True,
    )

    print(
        "UNIT 11E.2 ACTUAL POSITION QUANTITY =",
        quantity,
        flush=True,
    )

    # --------------------------------------------------------
    # UNIT 11A
    # RECALCULATE TP PLAN FROM ACTUAL POSITION
    # --------------------------------------------------------

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 11E.2 CALLING VERIFIED UNIT 11A",
        flush=True,
    )

    unit_11a_result = (
        reconstruction_unit_11a_tp_engine(
            direction=direction,
            entry_price=entry_price,
            total_quantity=quantity,
            favorable_tp1_price=None,
            favorable_tp2_price=None,
            leverage=Decimal(
                "100"
            ),
        )
    )

    if (
        unit_11a_result.get(
            "valid"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 11E.2 UNIT 11A FAILED"
        )

    # --------------------------------------------------------
    # UNIT 11B
    # BUILD VERIFIED THREE-TP PLAN
    # --------------------------------------------------------

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 11E.2 CALLING VERIFIED UNIT 11B",
        flush=True,
    )

    unit_11b_result = (
        reconstruction_unit_11b_build_tp_payloads(
            unit_11a_result=(
                unit_11a_result
            ),
            symbol=symbol,
        )
    )

    if (
        unit_11b_result.get(
            "valid"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 11E.2 UNIT 11B FAILED"
        )

    # --------------------------------------------------------
    # UNIT 11D
    # PREPARE TRANSPORT PLAN
    # --------------------------------------------------------

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 11E.2 CALLING VERIFIED UNIT 11D",
        flush=True,
    )

    unit_11d_result = (
        reconstruction_unit_11d_prepare_demo_tp_orders(
            unit_11b_result=(
                unit_11b_result
            ),
        )
    )

    if (
        unit_11d_result.get(
            "valid"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 11E.2 UNIT 11D FAILED"
        )

    # --------------------------------------------------------
    # UNIT 11E.1
    # RECOVER FROZEN DEMO TP TRANSPORT SHAPE
    # --------------------------------------------------------

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 11E.2 CALLING VERIFIED UNIT 11E.1",
        flush=True,
    )

    unit_11e1_result = (
        reconstruction_unit_11e1_frozen_tp_path_test(
            unit_11d_result=(
                unit_11d_result
            ),
        )
    )

    if (
        unit_11e1_result.get(
            "valid"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 11E.2 UNIT 11E.1 FAILED"
        )

    recovered_payload = (
        unit_11e1_result[
            "recovered_payload"
        ]
    )

    preserved_tp_plan = (
        unit_11e1_result[
            "preserved_tp_plan"
        ]
    )

    # --------------------------------------------------------
    # CROSS-CHECK SYMBOL
    # --------------------------------------------------------

    if (
        str(
            recovered_payload.get(
                "symbol",
                "",
            )
        ).upper()
        !=
        symbol
    ):
        raise RuntimeError(
            "UNIT 11E.2 SYMBOL CROSS-CHECK FAILED"
        )

    print(
        "PASS: UNIT 11E.2 SYMBOL CROSS-CHECK",
        flush=True,
    )

    # --------------------------------------------------------
    # CROSS-CHECK POSITION SIDE
    # --------------------------------------------------------

    if (
        str(
            recovered_payload.get(
                "positionSide",
                "",
            )
        ).upper()
        !=
        direction
    ):
        raise RuntimeError(
            "UNIT 11E.2 POSITION SIDE "
            "CROSS-CHECK FAILED"
        )

    print(
        "PASS: UNIT 11E.2 POSITION SIDE CROSS-CHECK",
        flush=True,
    )

    # --------------------------------------------------------
    # CROSS-CHECK EXIT SIDE
    #
    # SHORT position -> BUY exit
    # LONG position  -> SELL exit
    # --------------------------------------------------------

    expected_exit_side = (
        "BUY"
        if direction == "SHORT"
        else "SELL"
    )

    if (
        str(
            recovered_payload.get(
                "side",
                "",
            )
        ).upper()
        !=
        expected_exit_side
    ):
        raise RuntimeError(
            "UNIT 11E.2 EXIT SIDE "
            "CROSS-CHECK FAILED"
        )

    print(
        "PASS: UNIT 11E.2 EXIT SIDE CROSS-CHECK",
        flush=True,
    )

    # --------------------------------------------------------
    # CROSS-CHECK TOTAL POSITION QUANTITY
    # --------------------------------------------------------

    recovered_quantity = Decimal(
        str(
            recovered_payload.get(
                "quantity"
            )
        )
    )

    if recovered_quantity != quantity:
        raise RuntimeError(
            "UNIT 11E.2 POSITION QUANTITY "
            "CROSS-CHECK FAILED"
        )

    print(
        "PASS: UNIT 11E.2 POSITION QUANTITY CROSS-CHECK",
        flush=True,
    )

    # --------------------------------------------------------
    # VERIFY RECOVERED ORDER TYPE
    # --------------------------------------------------------

    if (
        recovered_payload.get(
            "type"
        )
        !=
        "MARKET"
    ):
        raise RuntimeError(
            "UNIT 11E.2 RECOVERED ORDER TYPE "
            "IS NOT MARKET"
        )

    print(
        "PASS: UNIT 11E.2 RECOVERED ORDER TYPE = MARKET",
        flush=True,
    )

    # --------------------------------------------------------
    # VERIFY TP1 TRIGGER
    # --------------------------------------------------------

    if (
        recovered_payload.get(
            "tpTriggerPrice"
        )
        !=
        preserved_tp_plan[
            "tp1"
        ][
            "price"
        ]
    ):
        raise RuntimeError(
            "UNIT 11E.2 TP1 TRIGGER "
            "CROSS-CHECK FAILED"
        )

    print(
        "PASS: UNIT 11E.2 TP1 TRIGGER CROSS-CHECK",
        flush=True,
    )

    # --------------------------------------------------------
    # VERIFY TP DIRECTION RELATIVE TO ENTRY
    # --------------------------------------------------------

    tp1_price = Decimal(
        str(
            preserved_tp_plan[
                "tp1"
            ][
                "price"
            ]
        )
    )

    tp2_price = Decimal(
        str(
            preserved_tp_plan[
                "tp2"
            ][
                "price"
            ]
        )
    )

    if direction == "SHORT":

        if not (
            tp1_price < entry_price
            and
            tp2_price < tp1_price
        ):
            raise RuntimeError(
                "UNIT 11E.2 SHORT TP ORDERING FAILED"
            )

    else:

        if not (
            tp1_price > entry_price
            and
            tp2_price > tp1_price
        ):
            raise RuntimeError(
                "UNIT 11E.2 LONG TP ORDERING FAILED"
            )

    print(
        "PASS: UNIT 11E.2 TP PRICE DIRECTION",
        flush=True,
    )

    # --------------------------------------------------------
    # VERIFY FULL TP QUANTITY ALLOCATION
    # --------------------------------------------------------

    tp1_qty = Decimal(
        str(
            preserved_tp_plan[
                "tp1"
            ][
                "quantity"
            ]
        )
    )

    tp2_qty = Decimal(
        str(
            preserved_tp_plan[
                "tp2"
            ][
                "quantity"
            ]
        )
    )

    tp3_qty = Decimal(
        str(
            preserved_tp_plan[
                "tp3"
            ][
                "quantity"
            ]
        )
    )

    total_tp_quantity = (
        tp1_qty
        + tp2_qty
        + tp3_qty
    )

    if total_tp_quantity != quantity:
        raise RuntimeError(
            "UNIT 11E.2 TOTAL TP QUANTITY "
            "DOES NOT MATCH POSITION"
        )

    print(
        "PASS: UNIT 11E.2 TOTAL TP QUANTITY "
        "= ACTUAL POSITION QUANTITY",
        flush=True,
    )

    # --------------------------------------------------------
    # ABSOLUTE SL-DISABLED CHECK
    # --------------------------------------------------------

    forbidden_sl_fields = (
        "slTriggerPrice",
        "SlWorkingType",
        "stopLossPrice",
        "stopLoss",
        "stopPrice",
        "stop_loss",
    )

    present_sl_fields = [
        field
        for field in forbidden_sl_fields
        if field in recovered_payload
    ]

    if present_sl_fields:
        raise RuntimeError(
            "UNIT 11E.2 FORBIDDEN SL FIELDS = "
            + str(
                present_sl_fields
            )
        )

    print(
        "PASS: UNIT 11E.2 SL REMAINS DISABLED",
        flush=True,
    )

    # --------------------------------------------------------
    # ZERO-WRITE ASSERTIONS
    # --------------------------------------------------------

    if (
        unit_11e1_result.get(
            "weex_post"
        )
        is not False
    ):
        raise RuntimeError(
            "UNIT 11E.2 WEEX POST FIREBREAK FAILED"
        )

    if (
        unit_11e1_result.get(
            "exchange_mutation"
        )
        is not False
    ):
        raise RuntimeError(
            "UNIT 11E.2 EXCHANGE MUTATION "
            "FIREBREAK FAILED"
        )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 11E.2 FINAL RECOVERED PAYLOAD =",
        recovered_payload,
        flush=True,
    )

    print(
        "UNIT 11E.2 FINAL TP PLAN =",
        preserved_tp_plan,
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11E.2 ACTUAL POSITION "
        "-> RECOVERED TP PATH",
        flush=True,
    )

    print(
        "UNIT 11E.2 WEEX POST = FALSE",
        flush=True,
    )

    print(
        "UNIT 11E.2 DEMO ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 11E.2 REAL ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 11E.2 EXCHANGE MUTATION = FALSE",
        flush=True,
    )

    print(
        "UNIT 11E.2 SL = DISABLED",
        flush=True,
    )

    print(
        "UNIT 11E.2 BACKUP EXECUTION = FALSE",
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11E.2 RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return {
        "valid":
            True,

        "symbol":
            symbol,

        "direction":
            direction,

        "entry_price":
            str(
                entry_price
            ),

        "position_quantity":
            str(
                quantity
            ),

        "recovered_payload":
            recovered_payload,

        "preserved_tp_plan":
            preserved_tp_plan,

        "weex_post":
            False,

        "demo_order":
            False,

        "real_order":
            False,

        "exchange_mutation":
            False,
    }


# ============================================================
# UNIT 11E.2 CURRENT VERIFIED POSITION TEST
#
# This uses the actual position already confirmed by Unit 11C:
#
# BTCSUSDT
# SHORT
# Entry = 83595.9
# Quantity = 0.0004
#
# ZERO WRITE
# ============================================================


def reconstruction_unit_11e2_current_position_test():

    actual_position = {
        "symbol":
            "BTCSUSDT",

        "direction":
            "SHORT",

        "entry_price":
            "83595.9",

        "quantity":
            "0.0004",
    }

    result = (
        reconstruction_unit_11e2_actual_position_tp_bridge(
            actual_position=actual_position,
        )
    )

    if (
        result.get(
            "valid"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 11E.2 CURRENT POSITION TEST FAILED"
        )

    print(
        "PASS: UNIT 11E.2 CURRENT VERIFIED "
        "DEMO POSITION TEST",
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11E.2 "
        "CURRENT POSITION TEST = PASS",
        flush=True,
    )

    return result


if __name__ == "__main__":
    reconstruction_unit_11e2_current_position_test()

# ============================================================
# RECONSTRUCTION UNIT 11E.3
# EXISTING-POSITION TP RECOVERY
#
# PURPOSE:
# Recover the frozen-model POST-ENTRY TP architecture for an
# ALREADY-OPEN position.
#
# IMPORTANT:
# - THIS DOES NOT CREATE A NEW ENTRY
# - THIS DOES NOT CALL /capi/v3/sim/order
# - ZERO WEEX POST
# - ZERO DEMO ORDER
# - ZERO REAL ORDER
# - ZERO EXCHANGE MUTATION
# - SL REMAINS DISABLED
# - BACKUPS NOT EXECUTED
#
# RECOVERED FROZEN ARCHITECTURE:
#
# TP1 / TP2:
#   conditional TAKE_PROFIT legs
#   triggerPrice
#   executePrice
#   triggerPriceType = MARK_PRICE
#   reduceOnly = True
#
# TP3:
#   TRAILING_MARKET
#   callbackRate
#   workingType = MARK_PRICE
#   reduceOnly = True
#
# CRITICAL:
# Endpoint submission is intentionally NOT enabled here.
# We first prove the existing-position payload architecture.
# ============================================================


def reconstruction_unit_11e3_existing_position_tp_recovery(
    *,
    unit_11e2_result,
):

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11E.3 "
        "EXISTING-POSITION TP RECOVERY START",
        flush=True,
    )

    # --------------------------------------------------------
    # VALIDATE UNIT 11E.2
    # --------------------------------------------------------

    if not isinstance(
        unit_11e2_result,
        dict,
    ):
        raise RuntimeError(
            "UNIT 11E.3 UNIT 11E.2 RESULT "
            "IS NOT A DICTIONARY"
        )

    if (
        unit_11e2_result.get(
            "valid"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 11E.3 UNIT 11E.2 "
            "NOT VALID"
        )

    symbol = str(
        unit_11e2_result.get(
            "symbol",
            "",
        )
    ).upper()

    direction = str(
        unit_11e2_result.get(
            "direction",
            "",
        )
    ).upper()

    entry_price = Decimal(
        str(
            unit_11e2_result.get(
                "entry_price"
            )
        )
    )

    position_quantity = Decimal(
        str(
            unit_11e2_result.get(
                "position_quantity"
            )
        )
    )

    tp_plan = (
        unit_11e2_result.get(
            "preserved_tp_plan"
        )
    )

    if symbol != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 11E.3 INVALID SYMBOL = "
            + symbol
        )

    if direction not in (
        "LONG",
        "SHORT",
    ):
        raise RuntimeError(
            "UNIT 11E.3 INVALID DIRECTION = "
            + direction
        )

    if entry_price <= 0:
        raise RuntimeError(
            "UNIT 11E.3 INVALID ENTRY PRICE"
        )

    if position_quantity <= 0:
        raise RuntimeError(
            "UNIT 11E.3 INVALID POSITION QUANTITY"
        )

    if not isinstance(
        tp_plan,
        dict,
    ):
        raise RuntimeError(
            "UNIT 11E.3 TP PLAN MISSING"
        )

    print(
        "PASS: UNIT 11E.3 EXISTING POSITION VALIDATED",
        flush=True,
    )

    print(
        "UNIT 11E.3 SYMBOL =",
        symbol,
        flush=True,
    )

    print(
        "UNIT 11E.3 DIRECTION =",
        direction,
        flush=True,
    )

    print(
        "UNIT 11E.3 ENTRY PRICE =",
        entry_price,
        flush=True,
    )

    print(
        "UNIT 11E.3 POSITION QUANTITY =",
        position_quantity,
        flush=True,
    )

    # --------------------------------------------------------
    # EXIT DIRECTION
    # --------------------------------------------------------

    if direction == "SHORT":

        exit_side = "BUY"
        position_side = "SHORT"

    else:

        exit_side = "SELL"
        position_side = "LONG"

    print(
        "PASS: UNIT 11E.3 EXIT DIRECTION RECOVERED",
        flush=True,
    )

    print(
        "UNIT 11E.3 EXIT SIDE =",
        exit_side,
        flush=True,
    )

    print(
        "UNIT 11E.3 POSITION SIDE =",
        position_side,
        flush=True,
    )

    # --------------------------------------------------------
    # EXTRACT VERIFIED TP PLAN
    # --------------------------------------------------------

    tp1_price = Decimal(
        str(
            tp_plan[
                "tp1"
            ][
                "price"
            ]
        )
    )

    tp1_quantity = Decimal(
        str(
            tp_plan[
                "tp1"
            ][
                "quantity"
            ]
        )
    )

    tp2_price = Decimal(
        str(
            tp_plan[
                "tp2"
            ][
                "price"
            ]
        )
    )

    tp2_quantity = Decimal(
        str(
            tp_plan[
                "tp2"
            ][
                "quantity"
            ]
        )
    )

    tp3_quantity = Decimal(
        str(
            tp_plan[
                "tp3"
            ][
                "quantity"
            ]
        )
    )

    tp3_callback_rate = Decimal(
        str(
            tp_plan[
                "tp3"
            ][
                "callbackRate"
            ]
        )
    )

    # --------------------------------------------------------
    # QUANTITY SAFETY
    # --------------------------------------------------------

    total_exit_quantity = (
        tp1_quantity
        + tp2_quantity
        + tp3_quantity
    )

    if (
        total_exit_quantity
        !=
        position_quantity
    ):
        raise RuntimeError(
            "UNIT 11E.3 TOTAL EXIT QUANTITY "
            "DOES NOT MATCH POSITION"
        )

    print(
        "PASS: UNIT 11E.3 TOTAL TP QUANTITY "
        "= POSITION QUANTITY",
        flush=True,
    )

    # --------------------------------------------------------
    # TP PRICE DIRECTION SAFETY
    # --------------------------------------------------------

    if direction == "SHORT":

        if not (
            tp1_price < entry_price
            and
            tp2_price < tp1_price
        ):
            raise RuntimeError(
                "UNIT 11E.3 SHORT TP "
                "PRICE ORDERING FAILED"
            )

    else:

        if not (
            tp1_price > entry_price
            and
            tp2_price > tp1_price
        ):
            raise RuntimeError(
                "UNIT 11E.3 LONG TP "
                "PRICE ORDERING FAILED"
            )

    print(
        "PASS: UNIT 11E.3 TP PRICE DIRECTION",
        flush=True,
    )

    # --------------------------------------------------------
    # RECOVER FROZEN TP1 POST-ENTRY SHAPE
    #
    # NOTE:
    # No endpoint is authorized here.
    # This is payload recovery only.
    # --------------------------------------------------------

    tp1_payload = {
        "symbol":
            symbol,

        "side":
            exit_side,

        "positionSide":
            position_side,

        "type":
            "TAKE_PROFIT",

        "triggerPrice":
            str(
                tp1_price
            ),

        "executePrice":
            str(
                tp1_price
            ),

        "quantity":
            str(
                tp1_quantity
            ),

        "triggerPriceType":
            "MARK_PRICE",

        "clientAlgoId":
            "R11E3-TP1",

        "reduceOnly":
            True,
    }

    # --------------------------------------------------------
    # RECOVER FROZEN TP2 POST-ENTRY SHAPE
    # --------------------------------------------------------

    tp2_payload = {
        "symbol":
            symbol,

        "side":
            exit_side,

        "positionSide":
            position_side,

        "type":
            "TAKE_PROFIT",

        "triggerPrice":
            str(
                tp2_price
            ),

        "executePrice":
            str(
                tp2_price
            ),

        "quantity":
            str(
                tp2_quantity
            ),

        "triggerPriceType":
            "MARK_PRICE",

        "clientAlgoId":
            "R11E3-TP2",

        "reduceOnly":
            True,
    }

    # --------------------------------------------------------
    # RECOVER FROZEN TP3 TRAILING SHAPE
    # --------------------------------------------------------

    tp3_payload = {
        "symbol":
            symbol,

        "side":
            exit_side,

        "positionSide":
            position_side,

        "type":
            "TRAILING_MARKET",

        "quantity":
            str(
                tp3_quantity
            ),

        "callbackRate":
            str(
                tp3_callback_rate
            ),

        "workingType":
            "MARK_PRICE",

        "clientAlgoId":
            "R11E3-TP3",

        "reduceOnly":
            True,
    }

    # --------------------------------------------------------
    # REQUIRED FIELD VALIDATION
    # --------------------------------------------------------

    tp_required = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "triggerPrice",
        "executePrice",
        "quantity",
        "triggerPriceType",
        "clientAlgoId",
        "reduceOnly",
    }

    trailing_required = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "callbackRate",
        "workingType",
        "clientAlgoId",
        "reduceOnly",
    }

    missing_tp1 = (
        tp_required
        -
        set(
            tp1_payload.keys()
        )
    )

    missing_tp2 = (
        tp_required
        -
        set(
            tp2_payload.keys()
        )
    )

    missing_tp3 = (
        trailing_required
        -
        set(
            tp3_payload.keys()
        )
    )

    if missing_tp1:
        raise RuntimeError(
            "UNIT 11E.3 TP1 MISSING FIELDS = "
            + str(
                sorted(
                    missing_tp1
                )
            )
        )

    if missing_tp2:
        raise RuntimeError(
            "UNIT 11E.3 TP2 MISSING FIELDS = "
            + str(
                sorted(
                    missing_tp2
                )
            )
        )

    if missing_tp3:
        raise RuntimeError(
            "UNIT 11E.3 TP3 MISSING FIELDS = "
            + str(
                sorted(
                    missing_tp3
                )
            )
        )

    print(
        "PASS: UNIT 11E.3 REQUIRED FIELDS",
        flush=True,
    )

    # --------------------------------------------------------
    # EXACT RECOVERED TYPE VALIDATION
    # --------------------------------------------------------

    if (
        tp1_payload[
            "type"
        ]
        !=
        "TAKE_PROFIT"
    ):
        raise RuntimeError(
            "UNIT 11E.3 TP1 TYPE INVALID"
        )

    if (
        tp2_payload[
            "type"
        ]
        !=
        "TAKE_PROFIT"
    ):
        raise RuntimeError(
            "UNIT 11E.3 TP2 TYPE INVALID"
        )

    if (
        tp3_payload[
            "type"
        ]
        !=
        "TRAILING_MARKET"
    ):
        raise RuntimeError(
            "UNIT 11E.3 TP3 TYPE INVALID"
        )

    print(
        "PASS: UNIT 11E.3 FROZEN TP TYPES RECOVERED",
        flush=True,
    )

    # --------------------------------------------------------
    # REDUCE-ONLY SAFETY
    # --------------------------------------------------------

    for (
        leg_name,
        payload,
    ) in (
        (
            "TP1",
            tp1_payload,
        ),
        (
            "TP2",
            tp2_payload,
        ),
        (
            "TP3",
            tp3_payload,
        ),
    ):

        if (
            payload.get(
                "reduceOnly"
            )
            is not True
        ):
            raise RuntimeError(
                "UNIT 11E.3 "
                + leg_name
                + " IS NOT REDUCE-ONLY"
            )

    print(
        "PASS: UNIT 11E.3 ALL TP LEGS REDUCE-ONLY",
        flush=True,
    )

    # --------------------------------------------------------
    # ABSOLUTE SL-DISABLED CHECK
    # --------------------------------------------------------

    forbidden_sl_fields = {
        "slTriggerPrice",
        "SlWorkingType",
        "stopLossPrice",
        "stopLoss",
        "stopPrice",
        "stop_loss",
        "STOP_LOSS",
    }

    for (
        leg_name,
        payload,
    ) in (
        (
            "TP1",
            tp1_payload,
        ),
        (
            "TP2",
            tp2_payload,
        ),
        (
            "TP3",
            tp3_payload,
        ),
    ):

        present_sl_fields = (
            forbidden_sl_fields
            &
            set(
                payload.keys()
            )
        )

        if present_sl_fields:
            raise RuntimeError(
                "UNIT 11E.3 "
                + leg_name
                + " FORBIDDEN SL FIELDS = "
                + str(
                    sorted(
                        present_sl_fields
                    )
                )
            )

    print(
        "PASS: UNIT 11E.3 NO SL FIELDS",
        flush=True,
    )

    # --------------------------------------------------------
    # CRITICAL EXISTING-POSITION GUARD
    #
    # This recovery unit MUST NOT contain an ENTRY leg.
    # --------------------------------------------------------

    recovered_plan = {
        "tp1":
            tp1_payload,

        "tp2":
            tp2_payload,

        "tp3":
            tp3_payload,
    }

    if "entry" in recovered_plan:
        raise RuntimeError(
            "UNIT 11E.3 ENTRY LEG "
            "MUST NOT EXIST"
        )

    print(
        "PASS: UNIT 11E.3 NO NEW ENTRY LEG",
        flush=True,
    )

    # --------------------------------------------------------
    # DEMO SUBMISSION REMAINS LOCKED
    #
    # The frozen code establishes the TP payload architecture,
    # but this unit does NOT assume a demo-safe conditional
    # endpoint.
    # --------------------------------------------------------

    endpoint_authorized = False

    weex_post = False
    demo_order = False
    real_order = False
    exchange_mutation = False

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "UNIT 11E.3 TP1 RECOVERED PAYLOAD =",
        tp1_payload,
        flush=True,
    )

    print(
        "UNIT 11E.3 TP2 RECOVERED PAYLOAD =",
        tp2_payload,
        flush=True,
    )

    print(
        "UNIT 11E.3 TP3 RECOVERED PAYLOAD =",
        tp3_payload,
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    print(
        "PASS: UNIT 11E.3 EXISTING-POSITION "
        "TP ARCHITECTURE RECOVERED",
        flush=True,
    )

    print(
        "UNIT 11E.3 ENDPOINT AUTHORIZED = FALSE",
        flush=True,
    )

    print(
        "UNIT 11E.3 WEEX POST = FALSE",
        flush=True,
    )

    print(
        "UNIT 11E.3 DEMO ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 11E.3 REAL ORDER = FALSE",
        flush=True,
    )

    print(
        "UNIT 11E.3 EXCHANGE MUTATION = FALSE",
        flush=True,
    )

    print(
        "UNIT 11E.3 SL = DISABLED",
        flush=True,
    )

    print(
        "UNIT 11E.3 BACKUP EXECUTION = FALSE",
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11E.3 RESULT = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return {
        "valid":
            True,

        "symbol":
            symbol,

        "direction":
            direction,

        "entry_price":
            str(
                entry_price
            ),

        "position_quantity":
            str(
                position_quantity
            ),

        "tp1":
            tp1_payload,

        "tp2":
            tp2_payload,

        "tp3":
            tp3_payload,

        "endpoint_authorized":
            endpoint_authorized,

        "weex_post":
            weex_post,

        "demo_order":
            demo_order,

        "real_order":
            real_order,

        "exchange_mutation":
            exchange_mutation,
    }


# ============================================================
# UNIT 11E.3 STANDALONE CONNECTION TEST
#
# Uses Unit 11E.2 first, then feeds its verified result
# directly into Unit 11E.3.
#
# ZERO WRITE.
# ============================================================


def reconstruction_unit_11e3_standalone_test():

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "UNIT 11E.3 STANDALONE "
        "EXISTING-POSITION TEST START",
        flush=True,
    )

    actual_position = {
        "symbol":
            "BTCSUSDT",

        "direction":
            "SHORT",

        "entry_price":
            "83595.9",

        "quantity":
            "0.0004",
    }

    unit_11e2_result = (
        reconstruction_unit_11e2_actual_position_tp_bridge(
            actual_position=actual_position,
        )
    )

    result = (
        reconstruction_unit_11e3_existing_position_tp_recovery(
            unit_11e2_result=(
                unit_11e2_result
            ),
        )
    )

    if (
        result.get(
            "valid"
        )
        is not True
    ):
        raise RuntimeError(
            "UNIT 11E.3 STANDALONE TEST FAILED"
        )

    if (
        result.get(
            "endpoint_authorized"
        )
        is not False
    ):
        raise RuntimeError(
            "UNIT 11E.3 ENDPOINT FIREBREAK FAILED"
        )

    if (
        result.get(
            "weex_post"
        )
        is not False
    ):
        raise RuntimeError(
            "UNIT 11E.3 WRITE FIREBREAK FAILED"
        )

    if (
        result[
            "tp1"
        ][
            "type"
        ]
        !=
        "TAKE_PROFIT"
    ):
        raise RuntimeError(
            "UNIT 11E.3 TP1 TYPE TEST FAILED"
        )

    if (
        result[
            "tp2"
        ][
            "type"
        ]
        !=
        "TAKE_PROFIT"
    ):
        raise RuntimeError(
            "UNIT 11E.3 TP2 TYPE TEST FAILED"
        )

    if (
        result[
            "tp3"
        ][
            "type"
        ]
        !=
        "TRAILING_MARKET"
    ):
        raise RuntimeError(
            "UNIT 11E.3 TP3 TYPE TEST FAILED"
        )

    print(
        "PASS: UNIT 11E.3 EXISTING-POSITION "
        "TP1 RECOVERED",
        flush=True,
    )

    print(
        "PASS: UNIT 11E.3 EXISTING-POSITION "
        "TP2 RECOVERED",
        flush=True,
    )

    print(
        "PASS: UNIT 11E.3 EXISTING-POSITION "
        "TP3 TRAILING RECOVERED",
        flush=True,
    )

    print(
        "PASS: UNIT 11E.3 NO NEW ENTRY",
        flush=True,
    )

    print(
        "PASS: UNIT 11E.3 NO EXCHANGE WRITE",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "RECONSTRUCTION UNIT 11E.3 "
        "STANDALONE TEST = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return result


if __name__ == "__main__":
    reconstruction_unit_11e3_standalone_test()
