# ============================================================
# R1.8 CORRECTED MAIN.PY — PART 1 START
# ============================================================

#!/usr/bin/env python3
"""
R36F.15.2 - SELECTED TP SNAPSHOT SCOPE FIX FOR CONTROLLED WEEX DEMO

Purpose:
    Preserve the proven R36D/R36F.4/R36F.5.4/R36F.8 safety baseline
    while correcting ONLY the remaining pre-live readiness classification:

        A market may have a valid historical TP set but still be unable to
        represent the frozen 20% / 20% / 60% TP quantity split because the
        planned entry quantity is below the strict exchange-representable
        minimum. That condition is normal TRADE INELIGIBILITY, not a writer
        capability failure and not a FINAL_BLOCKER.

R36F.15.2 CHANGE:

    1. Preserve the complete R36F.15.1 continuous fresh-market reevaluation pipeline.
    2. Fix ONLY the stale selected_tp_snapshot reference in the eligible writer/demo path.
    3. Use the already-selected direction-specific selected_snapshot consistently for demo preview construction.
    4. Add an explicit blocker if the eligible writer/demo construction pipeline raises an unexpected exception.
    5. Preserve normal TRADE_NOT_ELIGIBLE states as non-final-blocking market conditions.
    6. Preserve EMA, two-cluster TP, 20/20/60 quantity allocation, protective stop, stop-risk envelope, stop-loss budget, backup configuration, exactly-once demo journal, and all real-money firebreaks unchanged.

R36F.15.1 CHANGE:

    1. Keep the full R36F.15 startup validation and demo execution chain unchanged.
    2. After each runtime interval, rerun the complete fresh market/account pipeline.
    3. Refetch mark price and up to the existing 1000 one-minute historical candles.
    4. Recalculate EMA19/EMA50/EMA200 and LONG/SHORT historical TP clusters.
    5. Revalidate the configured Telegram command against the fresh EMA direction
       and fresh direction-specific TP market eligibility.
    6. Rebuild quantity, protective-stop, stop-risk-envelope and stop-loss-budget
       authorization previews from the fresh market snapshot.
    7. Permit WEEX demo transport only through the existing R36F.15 arm and full
       authorization chain.
    8. Preserve the durable demo dispatch journal so one completed first demo order
       cannot be submitted again on later reevaluation cycles or restart.
    9. Keep every production / real-money mutation switch hard-disabled.
   10. Make the runtime interval configurable with R36F151_REEVALUATION_SECONDS,
       default 60 seconds and minimum 15 seconds.
"""

import asyncio
import aiohttp
import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_DOWN
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread


STAGE = "R36F.15.10.5"

PURPOSE = (
    "R36F.15.10.5 MINIMAL REGIME-TO-DEMO MERGER: preserve the proven "
    "R36F.15.10.4b classifier, three-confirmation controller, active-trade "
    "mode lock and 60-second reevaluation unchanged; add only regime-specific "
    "SCALP/NORMAL/BREAKOUT authorization into the existing frozen WEEX demo "
    "writer, JIT validation, journal/replay and exposure safeguards. "
    "Production real-money execution remains hard-disabled."
)


API_BASE_URL = "https://api-contract.weex.com"
SYMBOL = "BTCUSDT"
PUBLIC_TICKER_SYMBOL = "cmt_btcusdt"
KLINE_INTERVAL = "1m"
HISTORICAL_LIMIT = 250
MAX_HISTORICAL_PAGES = 4

R36F151_REEVALUATION_SECONDS = max(
    15,
    int(os.getenv("R36F151_REEVALUATION_SECONDS", "60")),
)


PRICE_STEP = Decimal("0.1")
QUANTITY_STEP = Decimal("0.0001")
MIN_QUANTITY = Decimal("0.0001")

ENTRY_MARGIN_PERCENT = Decimal("5")
LEVERAGE_LONG = Decimal("100")
LEVERAGE_SHORT = Decimal("100")
MARGIN_MODE = "ISOLATED"
PYRAMID_ADD_PERCENT = Decimal("5")
MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3
BACKUP_MARGIN_PERCENT = Decimal("5")
BACKUP_BUFFER_PERCENT = Decimal("0.3")
MAX_FUND_EXPOSURE_PERCENT = Decimal("35")
SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300
ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True

EMA_FAST = 19
EMA_MID = 50
EMA_SLOW = 200
EMA_CONFIRMATION_CANDLES = 1
MIN_EMA_19_50_SEPARATION_PERCENT = Decimal("0.01")


TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()

R36F12_TELEGRAM_ALERTS_ENABLED = (
    os.getenv(
        "R36F12_TELEGRAM_ALERTS_ENABLED",
        "false",
    ).strip().lower()
    in {"1", "true", "yes", "on"}
)

R36F1541_ROUTINE_TELEGRAM_ALERTS_ENABLED = (
    os.getenv(
        "R36F1541_ROUTINE_TELEGRAM_ALERTS_ENABLED",
        "false",
    ).strip().lower()
    in {"1", "true", "yes", "on"}
)


TELEGRAM_BUY_COMMAND = "BUY BTC NOW"
TELEGRAM_SELL_COMMAND = "SELL BTC NOW"

TP1_PROFIT_MARGIN_PERCENT = Decimal("20")
TP2_PROFIT_MARGIN_PERCENT = Decimal("50")
TP3_PROFIT_MARGIN_PERCENT = Decimal("60")

TP1_ALLOCATION_PERCENT = Decimal("20")
TP2_ALLOCATION_PERCENT = Decimal("20")
TP3_ALLOCATION_PERCENT = Decimal("60")

TP3_TRAILING_DISTANCE_PERCENT = Decimal("0.20")
CLUSTER_TOLERANCE_PERCENT = Decimal("0.20")
MIN_CLUSTER_TOUCHES = 2
REQUIRED_TP_CLUSTERS = 2


REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
FIRST_REAL_ORDER_ALLOWED = False


CANARY_MAX_ENTRY_QUANTITY = Decimal("0.0004")
CANARY_ARM_PHRASE = "ARM_FIRST_LIVE_CANARY"

CANARY_ARM_REQUESTED = (
    os.getenv(
        "R36F12_LIVE_CANARY_ARM",
        "",
    ).strip()
    == CANARY_ARM_PHRASE
)

CANARY_STOP_PRICE_TEXT = os.getenv(
    "R36F12_CANARY_STOP_PRICE",
    "",
).strip()

CANARY_STOP_WORKING_TYPE = "MARK_PRICE"


R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT",
        "0.50",
    )
)

if R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT <= 0:
    raise ValueError(
        "R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT must be positive"
    )


R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT",
        "0.75",
    )
)

if R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT <= 0:
    raise ValueError(
        "R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT must be positive"
    )


R36F132_MAX_ACCOUNT_LOSS_PERCENT = Decimal(
    os.getenv(
        "R36F132_MAX_ACCOUNT_LOSS_PERCENT",
        "2.50",
    )
)

if R36F132_MAX_ACCOUNT_LOSS_PERCENT <= 0:
    raise ValueError(
        "R36F132_MAX_ACCOUNT_LOSS_PERCENT must be positive"
    )


R36F14_DEMO_SYMBOL = os.getenv(
    "R36F14_DEMO_SYMBOL",
    "BTCSUSDT",
).strip().upper()

R36F14_DEMO_ASSET = os.getenv(
    "R36F14_DEMO_ASSET",
    "SUSDT",
).strip().upper()

R36F14_DEMO_BALANCE_ENDPOINT = "/capi/v3/sim/balance"
R36F14_DEMO_POSITIONS_ENDPOINT = "/capi/v3/sim/position/allPosition"
R36F14_DEMO_ORDER_HISTORY_ENDPOINT = "/capi/v3/sim/order/history"
R36F14_DEMO_ORDER_ENDPOINT = "/capi/v3/sim/order"

R36F14_DEMO_READS_ENABLED = True
R36F14_DEMO_POST_TRANSPORT_ENABLED = False
R36F14_DEMO_ORDER_SUBMISSION_ENABLED = False
R36F14_FIRST_DEMO_ORDER_ALLOWED = False


R36F159_DEMO_ARM_PHRASE = "ARM_SECOND_WEEX_DEMO_ORDER"

R36F159_DEMO_ARM_REQUESTED = (
    os.getenv(
        "R36F159_DEMO_ARM",
        "",
    ).strip()
    == R36F159_DEMO_ARM_PHRASE
)

R36F15_DEMO_ARM_REQUESTED = (
    R36F159_DEMO_ARM_REQUESTED
)

R36F159_COMMAND_TOKEN = os.getenv(
    "R36F159_COMMAND_TOKEN",
    "",
).strip()

R36F15_DEMO_POST_TRANSPORT_ENABLED = True
R36F15_DEMO_ORDER_SUBMISSION_ENABLED = True
R36F15_FIRST_DEMO_ORDER_ALLOWED = True

R36F15_RECONCILE_DELAY_SECONDS = Decimal(
    os.getenv(
        "R36F15_RECONCILE_DELAY_SECONDS",
        "1.0",
    )
)


R36A_STATE_DIR = "/var/data/r36a_state"
R36C_STATE_DIR = "/var/data/r36c_state"
R36D_STATE_DIR = "/var/data/r36d_state"
R36F_STATE_DIR = "/var/data/r36f_state"

os.makedirs(
    R36F_STATE_DIR,
    exist_ok=True,
)


R36A_DEDUPE_FILE = os.path.join(
    R36A_STATE_DIR,
    "telegram_processed_updates.json",
)

R36A_DECISION_FILE = os.path.join(
    R36A_STATE_DIR,
    "synthetic_decisions.json",
)

R36C_DEDUPE_FILE = os.path.join(
    R36C_STATE_DIR,
    "telegram_processed_updates.json",
)

R36C_DECISION_FILE = os.path.join(
    R36C_STATE_DIR,
    "synthetic_decisions.json",
)

R36D_SNAPSHOT_FILE = os.path.join(
    R36D_STATE_DIR,
    "pre_live_readiness_snapshot.json",
)

R36F_SNAPSHOT_FILE = os.path.join(
    R36F_STATE_DIR,
    "pre_live_readiness_snapshot.json",
)

R36F12_CANARY_JOURNAL_FILE = os.path.join(
    R36F_STATE_DIR,
    "first_live_canary_dispatch_journal.json",
)

R36F12_TELEGRAM_SIGNAL_FILE = os.path.join(
    R36F_STATE_DIR,
    "r36f12_ema_telegram_signal_snapshot.json",
)

R36F12_TELEGRAM_COMMAND_FILE = os.path.join(
    R36F_STATE_DIR,
    "r36f12_telegram_command_preview.json",
)

R36F15_DEMO_JOURNAL_FILE = os.path.join(
    R36F_STATE_DIR,
    "r36f15_demo_dispatch_journal.json",
)

R36F159_DEMO_JOURNAL_FILE = os.path.join(
    R36F_STATE_DIR,
    "r36f159_second_demo_dispatch_journal.json",
)

R36F1541_TELEGRAM_EVENT_STATE_FILE = os.path.join(
    R36F_STATE_DIR,
    "r36f1541_telegram_event_state.json",
)


OLD_R36A_UPDATE_ID = "R36A_SYNTHETIC_UPDATE_000001"
R36C_UPDATE_ID = "R36C_SYNTHETIC_UPDATE_000001"


TEST_STATUS = "NOT_STARTED"
HEARTBEAT_COUNT = 0
DURABLE_EVIDENCE_OK = False
R36A_EVIDENCE_OK = False
R36C_EVIDENCE_OK = False
R36D_EVIDENCE_OK = False
WEEX_READ_ONLY_OK = False
ZERO_WRITE_INVARIANT_OK = False
FINAL_GATE_OK = False
FINAL_BLOCKERS = []

MARK_PRICE = None
AVAILABLE_BALANCE = None
OPEN_POSITIONS = []
WEEX_CONFIG = {}
SHORT_DIAGNOSTICS = {}
LONG_DIAGNOSTICS = {}
LAST_TP_APPROVAL = None
EMA_SIGNAL_SNAPSHOT = {}
TELEGRAM_COMMAND_PREVIEW = {}


def now_iso():
    return datetime.now(
        timezone.utc
    ).isoformat()


def line():
    print(
        "----------------------------------------------------------------------------------------------------",
        flush=True,
    )


def log(message):
    print(
        f"{now_iso()} {message}",
        flush=True,
    )


def check(
    name,
    condition,
    detail=None,
):
    if condition:
        log(
            f"PASS: {name}"
        )

        if detail:
            log(
                f"      {detail}"
            )

        return True

    log(
        f"FAIL: {name}"
    )

    if detail:
        log(
            f"      {detail}"
        )

    return False


def D(value):
    if isinstance(
        value,
        Decimal,
    ):
        return value

    return Decimal(
        str(value)
    )


def quantize_down(
    value,
    step,
):
    value = D(
        value
    )

    step = D(
        step
    )

    if step <= 0:
        raise ValueError(
            "step must be positive"
        )

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


def quantize_price(
    value,
):
    return quantize_down(
        value,
        PRICE_STEP,
    )


def quantize_quantity(
    value,
):
    return quantize_down(
        value,
        QUANTITY_STEP,
    )


def decimal_to_string(
    value,
):
    value = D(
        value
    )

    text = format(
        value,
        "f",
    )

    if "." in text:
        text = text.rstrip(
            "0"
        ).rstrip(
            "."
        )

    return (
        text
        if text
        else "0"
    )


def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )


def sha256_text(value):
    return hashlib.sha256(
        str(value).encode(
            "utf-8"
        )
    ).hexdigest()


def hmac_sha256_hex(
    secret,
    message,
):
    return hmac.new(
        str(secret).encode(
            "utf-8"
        ),
        str(message).encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).hexdigest()


def safe_int(
    value,
    default=0,
):
    try:
        return int(
            value
        )
    except Exception:
        return default


def safe_decimal(
    value,
    default=None,
):
    try:
        if value is None:
            return default

        return D(
            value
        )

    except Exception:
        return default


def ensure_parent_directory(
    file_path,
):
    parent = os.path.dirname(
        file_path
    )

    if parent:
        os.makedirs(
            parent,
            exist_ok=True,
        )


def read_json_file(
    file_path,
    default=None,
):
    if default is None:
        default = {}

    try:
        if not os.path.exists(
            file_path
        ):
            return default

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as handle:
            data = json.load(
                handle
            )

        return data

    except Exception as exc:
        log(
            "JSON READ ERROR "
            + str(file_path)
            + " = "
            + str(exc)
        )

        return default


def write_json_file(
    file_path,
    value,
):
    ensure_parent_directory(
        file_path
    )

    temporary_path = (
        file_path
        + ".tmp"
    )

    with open(
        temporary_path,
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            value,
            handle,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
        )

        handle.flush()

        try:
            os.fsync(
                handle.fileno()
            )
        except Exception:
            pass

    os.replace(
        temporary_path,
        file_path,
    )


def normalize_side(
    value,
):
    text = str(
        value or ""
    ).strip().upper()

    if text in {
        "BUY",
        "LONG",
    }:
        return "LONG"

    if text in {
        "SELL",
        "SHORT",
    }:
        return "SHORT"

    return None


def opposite_side(
    side,
):
    side = normalize_side(
        side
    )

    if side == "LONG":
        return "SHORT"

    if side == "SHORT":
        return "LONG"

    return None


def normalize_symbol(
    value,
):
    return str(
        value or ""
    ).strip().upper()


def normalize_status(
    value,
):
    return str(
        value or ""
    ).strip().upper()


def percent_of(
    value,
    percent,
):
    return (
        D(value)
        * D(percent)
        / D("100")
    )


def percent_distance(
    first,
    second,
):
    first = D(
        first
    )

    second = D(
        second
    )

    if first == 0:
        return None

    return (
        abs(
            second - first
        )
        / abs(first)
        * D("100")
    )


def clamp_decimal(
    value,
    minimum,
    maximum,
):
    value = D(
        value
    )

    minimum = D(
        minimum
    )

    maximum = D(
        maximum
    )

    if value < minimum:
        return minimum

    if value > maximum:
        return maximum

    return value


def is_positive_decimal(
    value,
):
    try:
        return (
            D(value)
            > 0
        )

    except Exception:
        return False


def utc_timestamp_ms():
    return str(
        int(
            time.time()
            * 1000
        )
    )


def utc_timestamp_seconds():
    return int(
        time.time()
    )


def parse_iso_datetime(
    value,
):
    if not value:
        return None

    try:
        text = str(
            value
        ).strip()

        if text.endswith(
            "Z"
        ):
            text = (
                text[:-1]
                + "+00:00"
            )

        parsed = datetime.fromisoformat(
            text
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.astimezone(
            timezone.utc
        )

    except Exception:
        return None


def seconds_since_iso(
    value,
):
    parsed = parse_iso_datetime(
        value
    )

    if parsed is None:
        return None

    return (
        datetime.now(
            timezone.utc
        )
        - parsed
    ).total_seconds()


def direction_to_order_side(
    direction,
):
    direction = normalize_side(
        direction
    )

    if direction == "LONG":
        return "BUY"

    if direction == "SHORT":
        return "SELL"

    return None


def order_side_to_direction(
    side,
):
    return normalize_side(
        side
    )


def direction_matches_command(
    direction,
    command,
):
    direction = normalize_side(
        direction
    )

    command = str(
        command or ""
    ).strip().upper()

    if (
        direction == "LONG"
        and command
        == TELEGRAM_BUY_COMMAND
    ):
        return True

    if (
        direction == "SHORT"
        and command
        == TELEGRAM_SELL_COMMAND
    ):
        return True

    return False


def extract_first_present(
    row,
    keys,
    default=None,
):
    if not isinstance(
        row,
        dict,
    ):
        return default

    for key in keys:
        if key not in row:
            continue

        value = row.get(
            key
        )

        if value is not None:
            return value

    return default


def normalize_rows(
    payload,
):
    if payload is None:
        return []

    if isinstance(
        payload,
        list,
    ):
        return payload

    if not isinstance(
        payload,
        dict,
    ):
        return []

    for key in (
        "data",
        "rows",
        "list",
        "items",
        "result",
    ):
        candidate = payload.get(
            key
        )

        if isinstance(
            candidate,
            list,
        ):
            return candidate

        if isinstance(
            candidate,
            dict,
        ):
            nested = normalize_rows(
                candidate
            )

            if nested:
                return nested

    return []
def extract_order_id(
    payload,
):
    if not isinstance(
        payload,
        dict,
    ):
        return None

    for key in (
        "orderId",
        "order_id",
        "id",
    ):
        value = payload.get(
            key
        )

        if value:
            return str(
                value
            )

    data = payload.get(
        "data"
    )

    if isinstance(
        data,
        dict,
    ):
        return extract_order_id(
            data
        )

    return None


def extract_client_order_id(
    row,
):
    if not isinstance(
        row,
        dict,
    ):
        return ""

    return str(
        row.get(
            "clientOrderId"
        )
        or row.get(
            "newClientOrderId"
        )
        or row.get(
            "clientOid"
        )
        or ""
    ).strip()


def r36f_is_backup_client_order_id(
    value,
):
    value = str(
        value or ""
    ).strip().upper()

    return (
        value.startswith(
            "R36FB1-"
        )
        or value.startswith(
            "R36FB2-"
        )
        or value.startswith(
            "R36FB3-"
        )
    )


def r36f_backup_number_from_client_id(
    value,
):
    value = str(
        value or ""
    ).strip().upper()

    for backup_number in (
        1,
        2,
        3,
    ):
        prefix = (
            "R36FB"
            + str(
                backup_number
            )
            + "-"
        )

        if value.startswith(
            prefix
        ):
            return backup_number

    return None


def r36f_filled_backup_numbers_from_history(
    history_rows,
):
    completed = set()

    for row in (
        history_rows
        or []
    ):
        if not isinstance(
            row,
            dict,
        ):
            continue

        symbol = normalize_symbol(
            row.get(
                "symbol"
            )
        )

        if (
            symbol
            and symbol
            != R36F14_DEMO_SYMBOL
        ):
            continue

        status = normalize_status(
            row.get(
                "status"
            )
        )

        if status != "FILLED":
            continue

        client_order_id = (
            extract_client_order_id(
                row
            )
        )

        backup_number = (
            r36f_backup_number_from_client_id(
                client_order_id
            )
        )

        if backup_number in {
            1,
            2,
            3,
        }:
            completed.add(
                backup_number
            )

    consecutive = 0

    for backup_number in (
        1,
        2,
        3,
    ):
        if backup_number not in completed:
            break

        consecutive = backup_number

    return consecutive


def r36f_backup_history_ids(
    history_rows,
):
    ids = []

    for row in (
        history_rows
        or []
    ):
        if not isinstance(
            row,
            dict,
        ):
            continue

        client_order_id = (
            extract_client_order_id(
                row
            )
        )

        if r36f_is_backup_client_order_id(
            client_order_id
        ):
            ids.append(
                client_order_id
            )

    return sorted(
        set(
            ids
        )
    )


def r36f_backup_order_is_open(
    history_rows,
    client_order_id,
):
    client_order_id = str(
        client_order_id
        or ""
    ).strip()

    if not client_order_id:
        return False

    for row in (
        history_rows
        or []
    ):
        if not isinstance(
            row,
            dict,
        ):
            continue

        if (
            extract_client_order_id(
                row
            )
            != client_order_id
        ):
            continue

        status = normalize_status(
            row.get(
                "status"
            )
        )

        if status in {
            "NEW",
            "PENDING",
            "OPEN",
            "CREATED",
            "PARTIALLY_FILLED",
            "PARTIAL_FILLED",
            "PARTIALLYFILLED",
            "PART_FILLED",
        }:
            return True

    return False


def r36f_backup_order_is_filled(
    history_rows,
    client_order_id,
):
    client_order_id = str(
        client_order_id
        or ""
    ).strip()

    if not client_order_id:
        return False

    for row in (
        history_rows
        or []
    ):
        if not isinstance(
            row,
            dict,
        ):
            continue

        if (
            extract_client_order_id(
                row
            )
            != client_order_id
        ):
            continue

        if (
            normalize_status(
                row.get(
                    "status"
                )
            )
            == "FILLED"
        ):
            return True

    return False


def r36f_backup_order_exists(
    history_rows,
    client_order_id,
):
    client_order_id = str(
        client_order_id
        or ""
    ).strip()

    if not client_order_id:
        return False

    for row in (
        history_rows
        or []
    ):
        if not isinstance(
            row,
            dict,
        ):
            continue

        if (
            extract_client_order_id(
                row
            )
            == client_order_id
        ):
            return True

    return False


def r36f_position_quantity(
    row,
):
    if not isinstance(
        row,
        dict,
    ):
        return D("0")

    for key in (
        "positionAmt",
        "positionAmount",
        "position_size",
        "positionSize",
        "size",
        "quantity",
        "qty",
        "holdVol",
        "available",
        "total",
    ):
        value = row.get(
            key
        )

        if value is None:
            continue

        try:
            quantity = abs(
                D(value)
            )

            if quantity > 0:
                return quantity

        except Exception:
            continue

    return D("0")


def r36f_position_direction(
    row,
):
    if not isinstance(
        row,
        dict,
    ):
        return None

    for key in (
        "positionSide",
        "side",
        "holdSide",
        "direction",
    ):
        direction = normalize_side(
            row.get(
                key
            )
        )

        if direction:
            return direction

    for key in (
        "positionAmt",
        "positionAmount",
        "position_size",
        "positionSize",
        "size",
    ):
        value = row.get(
            key
        )

        if value is None:
            continue

        try:
            quantity = D(
                value
            )

            if quantity > 0:
                return "LONG"

            if quantity < 0:
                return "SHORT"

        except Exception:
            continue

    return None


def r36f_position_liquidation_price(
    row,
):
    if not isinstance(
        row,
        dict,
    ):
        return None

    for key in (
        "liquidatePrice",
        "liquidationPrice",
        "liquidation_price",
        "liqPrice",
    ):
        value = row.get(
            key
        )

        if value is None:
            continue

        try:
            price = D(
                value
            )

            if price > 0:
                return price

        except Exception:
            continue

    return None


def r36f_active_demo_position(
    position_rows,
):
    for row in (
        position_rows
        or []
    ):
        if not isinstance(
            row,
            dict,
        ):
            continue

        symbol = normalize_symbol(
            row.get(
                "symbol"
            )
        )

        if (
            symbol
            and symbol
            != R36F14_DEMO_SYMBOL
        ):
            continue

        if (
            r36f_position_quantity(
                row
            )
            > 0
        ):
            return dict(
                row
            )

    return None


def r36f_backup_quantity_from_balance(
    available_balance,
    mark_price,
    leverage,
):
    available_balance = D(
        available_balance
    )

    mark_price = D(
        mark_price
    )

    leverage = D(
        leverage
    )

    if (
        available_balance <= 0
        or mark_price <= 0
        or leverage <= 0
    ):
        return D("0")

    backup_margin = (
        available_balance
        * BACKUP_MARGIN_PERCENT
        / D("100")
    )

    notional = (
        backup_margin
        * leverage
    )

    raw_quantity = (
        notional
        / mark_price
    )

    quantity = quantize_down(
        raw_quantity,
        QUANTITY_STEP,
    )

    if (
        quantity
        < MIN_QUANTITY
    ):
        return D("0")

    return quantity


def r36f_backup_journal_file():
    return os.path.join(
        R36F_STATE_DIR,
        "r36f_backup_demo_dispatch_journal.json",
    )


def r36f_backup_journal_read():
    return read_json_file(
        r36f_backup_journal_file(),
        default={},
    )


def r36f_backup_journal_write(
    value,
):
    write_json_file(
        r36f_backup_journal_file(),
        value,
    )


def r36f_backup_journal_matches(
    journal,
    client_order_id,
):
    if not isinstance(
        journal,
        dict,
    ):
        return False

    return (
        str(
            journal.get(
                "client_order_id"
            )
            or ""
        ).strip()
        == str(
            client_order_id
            or ""
        ).strip()
    )


def r36f_backup_journal_terminal(
    journal,
):
    if not isinstance(
        journal,
        dict,
    ):
        return True

    state = normalize_status(
        journal.get(
            "state"
        )
    )

    return state in {
        "",
        "COMPLETED",
        "FILLED",
        "REJECTED",
        "FAILED",
        "CANCELLED",
        "CANCELED",
    }


def r36f_backup_journal_blocks(
    journal,
    client_order_id,
):
    if not isinstance(
        journal,
        dict,
    ):
        return False

    if not journal:
        return False

    if r36f_backup_journal_matches(
        journal,
        client_order_id,
    ):
        return not r36f_backup_journal_terminal(
            journal
        )

    return not r36f_backup_journal_terminal(
        journal
    )


def r36f_backup_prepared_journal(
    *,
    preview,
    position_quantity_before,
    completed_backups,
):
    payload = dict(
        preview.get(
            "payload"
        )
        or {}
    )

    client_order_id = str(
        preview.get(
            "client_order_id"
        )
        or payload.get(
            "newClientOrderId"
        )
        or ""
    ).strip()

    return {
        "stage": STAGE,
        "state": "PREPARED",
        "created_at": now_iso(),
        "endpoint":
            R36F14_DEMO_ORDER_ENDPOINT,
        "demo_only": True,
        "real_order_execution": False,
        "backup_number":
            preview.get(
                "backup_number"
            ),
        "direction":
            preview.get(
                "side"
            ),
        "client_order_id":
            client_order_id,
        "position_quantity_before":
            decimal_to_string(
                position_quantity_before
            ),
        "completed_backups_before":
            int(
                completed_backups
            ),
        "payload":
            payload,
        "payload_sha256":
            sha256_text(
                canonical_json(
                    payload
                )
            ),
    }


def r36f_backup_mark_journal(
    journal,
    *,
    state,
    **extra,
):
    updated = dict(
        journal
        or {}
    )

    updated[
        "state"
    ] = str(
        state
    )

    updated[
        "updated_at"
    ] = now_iso()

    for key, value in (
        extra.items()
    ):
        updated[
            key
        ] = value

    r36f_backup_journal_write(
        updated
    )

    return updated


def r36f_backup_demo_transport_enabled():
    return bool(
        R36F159_DEMO_ARM_REQUESTED
        and R36F15_DEMO_POST_TRANSPORT_ENABLED
        and R36F15_DEMO_ORDER_SUBMISSION_ENABLED
        and R36F15_FIRST_DEMO_ORDER_ALLOWED
        and not REAL_ORDER_EXECUTION
        and not EXCHANGE_MUTATION_TRANSPORT_ENABLED
        and not ORDER_SUBMISSION_ENABLED
        and not POSITION_MUTATION_ENABLED
    )


def r36f_backup_runtime_gate():
    if REAL_ORDER_EXECUTION:
        return {
            "allow": False,
            "reason":
                "REAL_ORDER_EXECUTION_MUST_REMAIN_FALSE",
        }

    if EXCHANGE_MUTATION_TRANSPORT_ENABLED:
        return {
            "allow": False,
            "reason":
                "REAL_EXCHANGE_MUTATION_TRANSPORT_MUST_REMAIN_FALSE",
        }

    if ORDER_SUBMISSION_ENABLED:
        return {
            "allow": False,
            "reason":
                "REAL_ORDER_SUBMISSION_MUST_REMAIN_FALSE",
        }

    if POSITION_MUTATION_ENABLED:
        return {
            "allow": False,
            "reason":
                "REAL_POSITION_MUTATION_MUST_REMAIN_FALSE",
        }

    if not R36F159_DEMO_ARM_REQUESTED:
        return {
            "allow": False,
            "reason":
                "SECOND_DEMO_ARM_NOT_REQUESTED",
        }

    if not R36F15_DEMO_POST_TRANSPORT_ENABLED:
        return {
            "allow": False,
            "reason":
                "DEMO_POST_TRANSPORT_DISABLED",
        }

    if not R36F15_DEMO_ORDER_SUBMISSION_ENABLED:
        return {
            "allow": False,
            "reason":
                "DEMO_ORDER_SUBMISSION_DISABLED",
        }

    return {
        "allow": True,
        "reason":
            "BACKUP_DEMO_RUNTIME_GATE_APPROVED",
    }


def r36f_backup_reconciliation_summary(
    *,
    history_rows,
    position_rows,
):
    active_position = (
        r36f_active_demo_position(
            position_rows
        )
    )

    completed_backups = (
        r36f_filled_backup_numbers_from_history(
            history_rows
        )
    )

    return {
        "active_position":
            active_position,
        "active_position_quantity":
            decimal_to_string(
                r36f_position_quantity(
                    active_position
                )
            )
            if active_position
            else "0",
        "active_position_direction":
            r36f_position_direction(
                active_position
            )
            if active_position
            else None,
        "completed_backups":
            completed_backups,
        "backup_history_ids":
            r36f_backup_history_ids(
                history_rows
            ),
    }


def r36f_backup_expected_next_number(
    completed_backups,
):
    completed_backups = safe_int(
        completed_backups,
        0,
    )

    if completed_backups < 0:
        completed_backups = 0

    if (
        completed_backups
        >= MAX_BACKUPS
    ):
        return None

    return (
        completed_backups
        + 1
    )


def r36f_backup_progression_valid(
    completed_backups,
):
    completed_backups = safe_int(
        completed_backups,
        0,
    )

    return (
        0
        <= completed_backups
        <= MAX_BACKUPS
    )


def r36f_backup_position_after_fill_increased(
    before_quantity,
    after_quantity,
):
    try:
        return (
            D(after_quantity)
            > D(before_quantity)
        )

    except Exception:
        return False


def r36f_backup_log_summary(
    result,
):
    if not isinstance(
        result,
        dict,
    ):
        log(
            "R36F BACKUP BRIDGE RESULT = INVALID"
        )
        return

    log(
        "R36F BACKUP BRIDGE STATUS = "
        + str(
            result.get(
                "status"
            )
        )
    )

    log(
        "R36F BACKUP BRIDGE REASON = "
        + str(
            result.get(
                "reason"
            )
        )
    )

    log(
        "R36F BACKUP COMPLETED = "
        + str(
            result.get(
                "completed_backups"
            )
        )
    )

    log(
        "R36F BACKUP NEXT = "
        + str(
            result.get(
                "backup_number"
            )
        )
    )

    log(
        "R36F BACKUP ORDER SENT = "
        + str(
            result.get(
                "sent",
                False,
            )
        )
    )

    log(
        "R36F BACKUP REAL ORDER = False"
    )


class HealthHandler(
    BaseHTTPRequestHandler
):
    def do_GET(
        self,
    ):
        body = json.dumps(
            {
                "stage": STAGE,
                "status":
                    TEST_STATUS,
                "heartbeat_count":
                    HEARTBEAT_COUNT,
                "real_order_execution":
                    REAL_ORDER_EXECUTION,
                "demo_arm":
                    R36F159_DEMO_ARM_REQUESTED,
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
                len(
                    body
                )
            ),
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format,
        *args,
    ):
        return


def start_health_server():
    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    server = HTTPServer(
        (
            "0.0.0.0",
            port,
        ),
        HealthHandler,
    )

    thread = Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    log(
        STAGE
        + ": HEALTH SERVER STARTED ON PORT "
        + str(
            port
        )
    )

    return server
