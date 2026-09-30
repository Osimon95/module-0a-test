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

def run_unit_5b_live_test() -> bool:

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

    # --------------------------------------------------------
    # IMPORTANT QUALIFICATION CONTRACT
    #
    # A rejected entry is NOT a test failure.
    #
    # Example:
    #
    # direction=None
    # qualified=False
    # reason=NO_CONFIRMED_DIRECTION
    #
    # means the engine correctly refused to fabricate
    # a LONG or SHORT signal.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # FINAL EXECUTION FIREBREAK
    # --------------------------------------------------------

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
            run_unit_5b_live_test()
        )

    except Exception as exc:

        separator()

        log(
            "RECONSTRUCTION UNIT 5B RESULT = FAIL"
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
            "Unit 5B live integration "
            "test did not pass."
        )


if __name__ == "__main__":

    main()
