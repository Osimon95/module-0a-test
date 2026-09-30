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
