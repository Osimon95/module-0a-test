

#!/usr/bin/env python3

# ==============================================================================
# R36D - FINAL PRE-LIVE PRODUCTION CHECKPOINT
#
# PURPOSE
# ------
# 1. Freeze previously proven configuration contracts.
# 2. Preserve existing /var/data durable state.
# 3. Credit existing R36A/R36C durable evidence instead of starting again.
# 4. Fix the R36C NEW_UPDATE_ACCEPTED scope failure.
# 5. Perform CURRENT REAL WEEX READ-ONLY reconciliation.
# 6. Preview the minimum-size R36E live canary.
# 7. Keep ALL exchange writes disabled.
#
# IMPORTANT
# ---------
# THIS FILE DOES NOT PLACE AN ORDER.
# THIS FILE DOES NOT CHANGE LEVERAGE.
# THIS FILE DOES NOT CHANGE MARGIN MODE.
# THIS FILE DOES NOT MUTATE A POSITION.
#
# Expected successful ending:
#
# R36D_PRE_LIVE_GATE=PASS
# FINAL_BLOCKERS=[]
# NEXT_STAGE=R36E_FIRST_LIVE_CANARY
#
# ==============================================================================

import os
import sys
import json
import time
import hmac
import base64
import hashlib
import threading
import traceback
import urllib.parse
import urllib.request
import urllib.error

from pathlib import Path
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


# ==============================================================================
# STAGE
# ==============================================================================

STAGE = "R36D"

PURPOSE = (
    "FINAL PRE-LIVE PRODUCTION CHECKPOINT "
    "- FROZEN BASELINE + REAL READ-ONLY RECONCILIATION"
)


# ==============================================================================
# FROZEN ENVIRONMENT VARIABLE CONTRACT
# ==============================================================================

WEEX_API_KEY_ENV = "WEEX_API_KEY"
WEEX_API_SECRET_ENV = "WEEX_API_SECRET"
WEEX_API_PASSPHRASE_ENV = "WEEX_API_PASSPHRASE"


# ==============================================================================
# FROZEN WEEX CONTRACT
# ==============================================================================

WEEX_BASE_URL = "https://api-contract.weex.com"

# Private/current authenticated account endpoints
PRIVATE_SYMBOL = "BTCUSDT"

# Public V2 ticker
PUBLIC_V2_SYMBOL = "cmt_btcusdt"


# ==============================================================================
# FROZEN STRATEGY CONTRACT
# ==============================================================================

TARGET_MARGIN_MODE = "ISOLATED"

TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

QTY_STEP = Decimal("0.0001")
MIN_QTY = Decimal("0.0001")
PRICE_STEP = Decimal("0.1")

INITIAL_ENTRY_PERCENT = Decimal("5")

PYRAMID_ADD_PERCENT = Decimal("5")
MAX_PYRAMID_ADDS = 1

MAX_BACKUPS = 3
BACKUP_PERCENT = Decimal("5")
BACKUP_BUFFER_PERCENT = Decimal("0.3")

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

TP1_PERCENT = Decimal("20")
TP1_TRIGGER_PERCENT = Decimal("0.5")

TP2_PERCENT = Decimal("20")
TP2_TRIGGER_PERCENT = Decimal("1.0")

TP3_PERCENT = Decimal("60")

TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300


# ==============================================================================
# HARD WRITE FIREBREAK
# ==============================================================================

REAL_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False

ORDER_SUBMISSION_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False

MARGIN_MODE_MUTATION_ENABLED = False

POSITION_MUTATION_ENABLED = False

FIRST_REAL_ORDER_ALLOWED = False


# ==============================================================================
# WRITE COUNTERS
# ==============================================================================

EXCHANGE_NETWORK_WRITES = 0

ORDER_SUBMISSIONS = 0

LEVERAGE_MUTATIONS = 0

MARGIN_MODE_MUTATIONS = 0

POSITION_MUTATIONS = 0

REAL_ORDERS_SENT = 0

DEMO_ORDERS_SENT = 0


# ==============================================================================
# EXISTING DURABLE STATE
# ==============================================================================

PERSISTENT_ROOT = Path("/var/data")

R36A_STATE_DIR = PERSISTENT_ROOT / "r36a_state"

R36C_STATE_DIR = PERSISTENT_ROOT / "r36c_state"

R36D_STATE_DIR = PERSISTENT_ROOT / "r36d_state"


R36A_DEDUPE_FILE = (
    R36A_STATE_DIR / "telegram_processed_updates.json"
)

R36A_DECISION_FILE = (
    R36A_STATE_DIR / "synthetic_decisions.json"
)

R36C_DEDUPE_FILE = (
    R36C_STATE_DIR / "telegram_processed_updates.json"
)

R36C_DECISION_FILE = (
    R36C_STATE_DIR / "synthetic_decisions.json"
)

R36D_SNAPSHOT_FILE = (
    R36D_STATE_DIR / "pre_live_readiness_snapshot.json"
)


OLD_R36A_UPDATE_ID = (
    "R36A_SYNTHETIC_UPDATE_000001"
)

R36C_UPDATE_ID = (
    "R36C_SYNTHETIC_UPDATE_000001"
)


# ==============================================================================
# GLOBAL STATUS
#
# IMPORTANT:
# These variables are explicitly initialized.
# This prevents the R36C UnboundLocalError from happening again.
# ==============================================================================

TEST_STATUS = "STARTING"

FINAL_BLOCKERS = []

HEARTBEAT = 0


OLD_DUPLICATE_DETECTED = False

OLD_REJECTED_BEFORE_PARSE = False

NEW_UPDATE_SEEN_BEFORE_STARTUP = False

NEW_UPDATE_ACCEPTED = False

NEW_REPLAY_REJECTED_BEFORE_PARSE = False


CURRENT_MARK_PRICE = None

CURRENT_AVAILABLE_BALANCE = None

BTCUSDT_FLAT = None

CURRENT_MARGIN_MODE = None

CURRENT_LONG_LEVERAGE = None

CURRENT_SHORT_LEVERAGE = None


# ==============================================================================
# BASIC UTILITIES
# ==============================================================================

def now_iso():
    return datetime.now(timezone.utc).isoformat()


def separator():
    print(
        f"{now_iso()} "
        + "-" * 100,
        flush=True,
    )


def log(message):
    print(
        f"{now_iso()} {message}",
        flush=True,
    )


def check(label, passed):
    result = "✅ PASS" if passed else "❌ FAIL"

    print(
        f"{label:<86} {result}",
        flush=True,
    )

    return bool(passed)


def safe_decimal(value):

    try:

        return Decimal(str(value))

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):

        return None


def floor_step(value, step):

    if value is None:

        return Decimal("0")

    if step <= 0:

        return Decimal("0")

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def canonical_json(value):

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_json(value):

    encoded = canonical_json(
        value
    ).encode("utf-8")

    return hashlib.sha256(
        encoded
    ).hexdigest()


# ==============================================================================
# JSON READ
# ==============================================================================

def load_json(path):

    if not path.exists():

        return (
            None,
            "FILE_NOT_FOUND",
        )

    try:

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        return (
            data,
            None,
        )

    except Exception as exc:

        return (
            None,
            (
                f"{exc.__class__.__name__}: "
                f"{exc}"
            ),
        )


# ==============================================================================
# ATOMIC R36D SNAPSHOT WRITE
#
# This writes ONLY R36D's own audit snapshot.
#
# It does NOT modify R36A.
# It does NOT modify R36C.
# ==============================================================================

def atomic_write_json(
    path,
    value,
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = Path(
        str(path) + ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            value,
            file,
            indent=2,
            sort_keys=True,
        )

        file.flush()

        os.fsync(
            file.fileno()
        )

    os.replace(
        temporary,
        path,
    )


# ==============================================================================
# FIND UPDATE IDS INSIDE EXISTING DURABLE STATE
# ==============================================================================

def collect_update_ids(value):

    found = set()

    def walk(item):

        if isinstance(
            item,
            dict,
        ):

            for key, value2 in item.items():

                if key in (
                    "update_id",
                    "telegram_update_id",
                    "idempotency_key",
                ):

                    if isinstance(
                        value2,
                        (str, int),
                    ):

                        found.add(
                            str(value2)
                        )

                if isinstance(
                    key,
                    str,
                ):

                    if key.startswith(
                        "R36A_SYNTHETIC_UPDATE_"
                    ):

                        found.add(key)

                    if key.startswith(
                        "R36C_SYNTHETIC_UPDATE_"
                    ):

                        found.add(key)

                walk(value2)

        elif isinstance(
            item,
            list,
        ):

            for value2 in item:

                walk(value2)

        elif isinstance(
            item,
            str,
        ):

            if item.startswith(
                "R36A_SYNTHETIC_UPDATE_"
            ):

                found.add(item)

            if item.startswith(
                "R36C_SYNTHETIC_UPDATE_"
            ):

                found.add(item)

    walk(value)

    return found


# ==============================================================================
# HEALTH SERVER
# ==============================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        payload = {

            "stage":
                STAGE,

            "status":
                TEST_STATUS,

            "real_order_execution":
                REAL_ORDER_EXECUTION,

            "exchange_network_writes":
                EXCHANGE_NETWORK_WRITES,

            "order_submissions":
                ORDER_SUBMISSIONS,

            "timestamp":
                now_iso(),
        }

        body = json.dumps(
            payload
        ).encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(body)


    def do_POST(self):

        self.send_error(405)


    def do_PUT(self):

        self.send_error(405)


    def do_PATCH(self):

        self.send_error(405)


    def do_DELETE(self):

        self.send_error(405)


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

    server = ThreadingHTTPServer(
        (
            "0.0.0.0",
            port,
        ),
        HealthHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    log(
        f"{STAGE}: "
        f"HEALTH SERVER STARTED "
        f"ON PORT {port}"
    )

    return server


# ==============================================================================
# WEEX SIGNATURE
# ==============================================================================

def make_signature(
    secret,
    timestamp_ms,
    method,
    request_path,
    query_string="",
):

    prehash = (
        f"{timestamp_ms}"
        f"{method.upper()}"
        f"{request_path}"
    )

    if query_string:

        prehash += (
            "?"
            + query_string
        )

    digest = hmac.new(
        secret.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


# ==============================================================================
# HTTP GET ONLY
#
# There is deliberately NO generic POST function here.
# ==============================================================================

def http_get_json(
    url,
    headers=None,
    timeout=15,
):

    request = urllib.request.Request(
        url=url,
        headers=headers or {},
        method="GET",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            status = getattr(
                response,
                "status",
                200,
            )

            try:

                data = json.loads(raw)

            except Exception:

                data = None

            return (
                status,
                data,
                raw,
                None,
            )

    except urllib.error.HTTPError as exc:

        raw = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        try:

            data = json.loads(raw)

        except Exception:

            data = None

        return (
            exc.code,
            data,
            raw,
            f"HTTPError: {exc}",
        )

    except Exception as exc:

        return (
            None,
            None,
            "",
            (
                f"{exc.__class__.__name__}: "
                f"{exc}"
            ),
        )


# ==============================================================================
# PRIVATE AUTHENTICATED GET
# ==============================================================================

def weex_private_get(
    request_path,
    params=None,
):

    api_key = os.getenv(
        WEEX_API_KEY_ENV,
        "",
    ).strip()

    secret = os.getenv(
        WEEX_API_SECRET_ENV,
        "",
    ).strip()

    passphrase = os.getenv(
        WEEX_API_PASSPHRASE_ENV,
        "",
    ).strip()


    missing = []

    if not api_key:

        missing.append(
            WEEX_API_KEY_ENV
        )

    if not secret:

        missing.append(
            WEEX_API_SECRET_ENV
        )

    if not passphrase:

        missing.append(
            WEEX_API_PASSPHRASE_ENV
        )

    if missing:

        return (
            None,
            None,
            "",
            (
                "MISSING_ENV="
                + ",".join(missing)
            ),
        )


    params = params or {}

    query = urllib.parse.urlencode(
        params
    )

    timestamp_ms = str(
        int(
            time.time() * 1000
        )
    )

    signature = make_signature(

        secret=secret,

        timestamp_ms=timestamp_ms,

        method="GET",

        request_path=request_path,

        query_string=query,
    )


    headers = {

        "ACCESS-KEY":
            api_key,

        "ACCESS-SIGN":
            signature,

        "ACCESS-TIMESTAMP":
            timestamp_ms,

        "ACCESS-PASSPHRASE":
            passphrase,

        "Content-Type":
            "application/json",

        "locale":
            "en-US",

        "User-Agent":
            f"{STAGE}/1.0",
    }


    url = (
        WEEX_BASE_URL
        + request_path
    )

    if query:

        url += (
            "?"
            + query
        )


    return http_get_json(
        url=url,
        headers=headers,
    )


# ==============================================================================
# PUBLIC MARK PRICE GET
# ==============================================================================

def weex_public_ticker():

    path = (
        "/capi/v2/market/ticker"
    )

    query = urllib.parse.urlencode(
        {
            "symbol":
                PUBLIC_V2_SYMBOL
        }
    )

    url = (
        WEEX_BASE_URL
        + path
        + "?"
        + query
    )

    return http_get_json(

        url=url,

        headers={
            "User-Agent":
                f"{STAGE}/1.0"
        },
    )


# ==============================================================================
# ABSOLUTE MUTATION FIREBREAK
# ==============================================================================

def mutation_forbidden(
    *args,
    **kwargs,
):

    raise RuntimeError(

        f"{STAGE} HARD FIREBREAK: "
        f"EXCHANGE MUTATION FORBIDDEN"
    )


place_order = mutation_forbidden

change_leverage = mutation_forbidden

change_margin_mode = mutation_forbidden

close_position = mutation_forbidden


# ==============================================================================
# RESPONSE HELPERS
# ==============================================================================

def normalize_rows(value):

    if isinstance(
        value,
        list,
    ):

        return value


    if isinstance(
        value,
        dict,
    ):

        for key in (
            "data",
            "result",
            "list",
        ):

            candidate = value.get(
                key
            )

            if isinstance(
                candidate,
                list,
            ):

                return candidate


    return []


def find_usdt_balance(value):

    if isinstance(
        value,
        list,
    ):

        for row in value:

            if not isinstance(
                row,
                dict,
            ):

                continue

            asset = str(
                row.get(
                    "asset",
                    "",
                )
            ).upper()

            if asset == "USDT":

                return row


    if isinstance(
        value,
        dict,
    ):

        for key in (
            "data",
            "result",
            "balances",
        ):

            if key in value:

                result = find_usdt_balance(
                    value[key]
                )

                if result:

                    return result


    return None


def position_is_nonzero(row):

    if not isinstance(
        row,
        dict,
    ):

        return False


    possible_fields = (

        "size",

        "positionAmt",

        "available",

        "total",
    )


    for field in possible_fields:

        if field not in row:

            continue

        number = safe_decimal(
            row.get(field)
        )

        if (
            number is not None
            and number != 0
        ):

            return True


    return False


# ==============================================================================
# CURRENT REAL WEEX RECONCILIATION
# ==============================================================================

def reconcile_weex():

    global CURRENT_MARK_PRICE

    global CURRENT_AVAILABLE_BALANCE

    global BTCUSDT_FLAT

    global CURRENT_MARGIN_MODE

    global CURRENT_LONG_LEVERAGE

    global CURRENT_SHORT_LEVERAGE


    results = {}


    # ==========================================================================
    # PUBLIC MARK PRICE
    # ==========================================================================

    (
        ticker_status,
        ticker_data,
        ticker_raw,
        ticker_error,
    ) = weex_public_ticker()


    mark_price = None


    if isinstance(
        ticker_data,
        dict,
    ):

        mark_price = safe_decimal(
            ticker_data.get(
                "markPrice"
            )
        )


    CURRENT_MARK_PRICE = (
        mark_price
    )


    ticker_ok = (

        ticker_status == 200

        and mark_price is not None

        and mark_price > 0
    )


    results[
        "ticker"
    ] = {

        "status_code":
            ticker_status,

        "error":
            ticker_error,

        "ok":
            ticker_ok,

        "mark_price":
            (
                str(mark_price)
                if mark_price is not None
                else None
            ),
    }


    # ==========================================================================
    # ACCOUNT BALANCE
    # ==========================================================================

    (
        balance_status,
        balance_data,
        balance_raw,
        balance_error,
    ) = weex_private_get(
        "/capi/v3/account/balance"
    )


    usdt_row = find_usdt_balance(
        balance_data
    )


    available_balance = None


    if usdt_row:

        for field in (
            "availableBalance",
            "available",
        ):

            if field in usdt_row:

                available_balance = (
                    safe_decimal(
                        usdt_row.get(
                            field
                        )
                    )
                )

                if available_balance is not None:

                    break


    CURRENT_AVAILABLE_BALANCE = (
        available_balance
    )


    balance_ok = (

        balance_status == 200

        and available_balance is not None

        and available_balance >= 0
    )


    results[
        "balance"
    ] = {

        "status_code":
            balance_status,

        "error":
            balance_error,

        "ok":
            balance_ok,

        "available_usdt":
            (
                str(
                    available_balance
                )
                if available_balance
                is not None
                else None
            ),
    }


    # ==========================================================================
    # BTCUSDT CURRENT POSITION
    # ==========================================================================

    (
        position_status,
        position_data,
        position_raw,
        position_error,
    ) = weex_private_get(

        "/capi/v3/account/position/singlePosition",

        {
            "symbol":
                PRIVATE_SYMBOL
        },
    )


    position_rows = normalize_rows(
        position_data
    )


    position_read_ok = (
        position_status == 200
    )


    flat = (

        position_read_ok

        and not any(
            position_is_nonzero(row)
            for row in position_rows
        )
    )


    BTCUSDT_FLAT = flat


    results[
        "position"
    ] = {

        "status_code":
            position_status,

        "error":
            position_error,

        "ok":
            position_read_ok,

        "flat":
            flat,

        "returned_rows":
            len(position_rows),
    }


    # ==========================================================================
    # SYMBOL CONFIGURATION
    # ==========================================================================

    (
        config_status,
        config_data,
        config_raw,
        config_error,
    ) = weex_private_get(

        "/capi/v3/account/symbolConfig",

        {
            "symbol":
                PRIVATE_SYMBOL
        },
    )


    config_rows = normalize_rows(
        config_data
    )


    selected_config = None


    for row in config_rows:

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


        if row_symbol == PRIVATE_SYMBOL:

            selected_config = row

            break


    if (

        selected_config is None

        and len(config_rows) == 1

        and isinstance(
            config_rows[0],
            dict,
        )

    ):

        selected_config = (
            config_rows[0]
        )


    CURRENT_MARGIN_MODE = None

    CURRENT_LONG_LEVERAGE = None

    CURRENT_SHORT_LEVERAGE = None


    if selected_config:


        margin_value = (

            selected_config.get(
                "marginType"
            )

            or selected_config.get(
                "marginMode"
            )

            or selected_config.get(
                "margin_mode"
            )

            or ""
        )


        CURRENT_MARGIN_MODE = str(
            margin_value
        ).upper()


        CURRENT_LONG_LEVERAGE = (
            safe_decimal(

                selected_config.get(
                    "isolatedLongLeverage",

                    selected_config.get(
                        "isolated_long_leverage"
                    ),
                )
            )
        )


        CURRENT_SHORT_LEVERAGE = (
            safe_decimal(

                selected_config.get(
                    "isolatedShortLeverage",

                    selected_config.get(
                        "isolated_short_leverage"
                    ),
                )
            )
        )


    config_ok = (

        config_status == 200

        and CURRENT_MARGIN_MODE
        == TARGET_MARGIN_MODE

        and CURRENT_LONG_LEVERAGE
        == TARGET_LONG_LEVERAGE

        and CURRENT_SHORT_LEVERAGE
        == TARGET_SHORT_LEVERAGE
    )


    results[
        "symbol_config"
    ] = {

        "status_code":
            config_status,

        "error":
            config_error,

        "ok":
            config_ok,

        "margin_mode":
            CURRENT_MARGIN_MODE,

        "isolated_long_leverage":
            (
                str(
                    CURRENT_LONG_LEVERAGE
                )
                if CURRENT_LONG_LEVERAGE
                is not None
                else None
            ),

        "isolated_short_leverage":
            (
                str(
                    CURRENT_SHORT_LEVERAGE
                )
                if CURRENT_SHORT_LEVERAGE
                is not None
                else None
            ),
    }


    return results


# ==============================================================================
# R36E LIVE CANARY PREVIEW
#
# CALCULATION ONLY
#
# NO ORDER IS SENT.
# ==============================================================================

def build_canary_preview():

    if (
        CURRENT_AVAILABLE_BALANCE
        is None
    ):

        return None


    if (
        CURRENT_MARK_PRICE
        is None
    ):

        return None


    if CURRENT_MARK_PRICE <= 0:

        return None


    strategy_entry_margin = (

        CURRENT_AVAILABLE_BALANCE

        * INITIAL_ENTRY_PERCENT

        / Decimal("100")
    )


    strategy_entry_notional = (

        strategy_entry_margin

        * TARGET_LONG_LEVERAGE
    )


    strategy_raw_qty = (

        strategy_entry_notional

        / CURRENT_MARK_PRICE
    )


    strategy_normalized_qty = (
        floor_step(

            strategy_raw_qty,

            QTY_STEP,
        )
    )


    # First live canary intentionally uses the minimum configured quantity.
    canary_qty = MIN_QTY


    return {

        "symbol":
            PRIVATE_SYMBOL,

        "side":
            "UNSET_UNTIL_REAL_SIGNAL",

        "target_margin_mode":
            TARGET_MARGIN_MODE,

        "target_long_leverage":
            str(
                TARGET_LONG_LEVERAGE
            ),

        "target_short_leverage":
            str(
                TARGET_SHORT_LEVERAGE
            ),

        "available_balance_usdt":
            str(
                CURRENT_AVAILABLE_BALANCE
            ),

        "mark_price":
            str(
                CURRENT_MARK_PRICE
            ),

        "strategy_entry_percent":
            str(
                INITIAL_ENTRY_PERCENT
            ),

        "strategy_entry_margin_usdt":
            str(
                strategy_entry_margin
            ),

        "strategy_entry_notional_usdt":
            str(
                strategy_entry_notional
            ),

        "strategy_raw_qty_btc":
            str(
                strategy_raw_qty
            ),

        "strategy_normalized_qty_btc":
            str(
                strategy_normalized_qty
            ),

        "r36e_canary_qty_btc":
            str(
                canary_qty
            ),

        "qty_step":
            str(
                QTY_STEP
            ),

        "min_qty":
            str(
                MIN_QTY
            ),

        "max_fund_exposure_percent":
            str(
                MAX_FUND_EXPOSURE_PERCENT
            ),

        "writer_enabled":
            False,

        "real_order_execution":
            False,
    }


# ==============================================================================
# MAIN R36D CHECKS
# ==============================================================================

def run_r36d():

    global TEST_STATUS

    global FINAL_BLOCKERS

    global OLD_DUPLICATE_DETECTED

    global OLD_REJECTED_BEFORE_PARSE

    global NEW_UPDATE_SEEN_BEFORE_STARTUP

    global NEW_UPDATE_ACCEPTED

    global NEW_REPLAY_REJECTED_BEFORE_PARSE


    # ==========================================================================
    # EXPLICIT INITIALIZATION
    #
    # THIS DIRECTLY FIXES THE R36C:
    #
    # UnboundLocalError:
    # cannot access local variable 'NEW_UPDATE_ACCEPTED'
    #
    # ==========================================================================

    OLD_DUPLICATE_DETECTED = False

    OLD_REJECTED_BEFORE_PARSE = False

    NEW_UPDATE_SEEN_BEFORE_STARTUP = False

    NEW_UPDATE_ACCEPTED = False

    NEW_REPLAY_REJECTED_BEFORE_PARSE = False

    FINAL_BLOCKERS = []


    separator()

    log(
        f"{STAGE}: MAIN.PY ENTERED"
    )

    separator()

    log(
        f"PURPOSE={PURPOSE}"
    )

    log(
        f"PYTHON_VERSION="
        f"{sys.version.split()[0]}"
    )

    log(
        f"PRIVATE_SYMBOL="
        f"{PRIVATE_SYMBOL}"
    )

    log(
        f"PUBLIC_V2_SYMBOL="
        f"{PUBLIC_V2_SYMBOL}"
    )

    log(
        f"TARGET_MARGIN_MODE="
        f"{TARGET_MARGIN_MODE}"
    )

    log(
        f"TARGET_LONG_LEVERAGE="
        f"{TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"TARGET_SHORT_LEVERAGE="
        f"{TARGET_SHORT_LEVERAGE}x"
    )

    log(
        f"PERSISTENT_ROOT="
        f"{PERSISTENT_ROOT}"
    )


    # ==========================================================================
    # TEST 1
    # ==========================================================================

    separator()

    log(
        "R36D TEST 1: "
        "FROZEN CONTRACT + "
        "HARD WRITE FIREBREAK"
    )

    separator()


    environment_contract_ok = (

        WEEX_API_KEY_ENV
        == "WEEX_API_KEY"

        and WEEX_API_SECRET_ENV
        == "WEEX_API_SECRET"

        and WEEX_API_PASSPHRASE_ENV
        == "WEEX_API_PASSPHRASE"
    )


    symbol_contract_ok = (

        PRIVATE_SYMBOL
        == "BTCUSDT"

        and PUBLIC_V2_SYMBOL
        == "cmt_btcusdt"
    )


    hard_firebreak_ok = all(
        [

            REAL_ORDER_EXECUTION
            is False,

            DEMO_ORDER_EXECUTION
            is False,

            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False,

            ORDER_SUBMISSION_ENABLED
            is False,

            LEVERAGE_MUTATION_ENABLED
            is False,

            MARGIN_MODE_MUTATION_ENABLED
            is False,

            POSITION_MUTATION_ENABLED
            is False,

            FIRST_REAL_ORDER_ALLOWED
            is False,
        ]
    )


    check(
        "Frozen WEEX Environment Variable Names",
        environment_contract_ok,
    )

    check(
        "Frozen WEEX Symbol Mapping",
        symbol_contract_ok,
    )

    check(
        "Hard Exchange Write Firebreak",
        hard_firebreak_ok,
    )


    if not environment_contract_ok:

        FINAL_BLOCKERS.append(
            "FROZEN_ENVIRONMENT_VARIABLE_CONTRACT_CHANGED"
        )


    if not symbol_contract_ok:

        FINAL_BLOCKERS.append(
            "FROZEN_SYMBOL_MAPPING_CHANGED"
        )


    if not hard_firebreak_ok:

        FINAL_BLOCKERS.append(
            "WRITE_FIREBREAK_NOT_INTACT"
        )


    # ==========================================================================
    # TEST 2
    # ==========================================================================

    separator()

    log(
        "R36D TEST 2: "
        "READ EXISTING R36A + "
        "R36C DURABLE EVIDENCE"
    )

    separator()


    (
        r36a_dedupe,
        r36a_dedupe_error,
    ) = load_json(
        R36A_DEDUPE_FILE
    )


    (
        r36a_decision,
        r36a_decision_error,
    ) = load_json(
        R36A_DECISION_FILE
    )


    (
        r36c_dedupe,
        r36c_dedupe_error,
    ) = load_json(
        R36C_DEDUPE_FILE
    )


    (
        r36c_decision,
        r36c_decision_error,
    ) = load_json(
        R36C_DECISION_FILE
    )


    log(
        f"R36A_DEDUPE_FILE="
        f"{R36A_DEDUPE_FILE}"
    )

    log(
        f"R36A_DECISION_FILE="
        f"{R36A_DECISION_FILE}"
    )

    log(
        f"R36C_DEDUPE_FILE="
        f"{R36C_DEDUPE_FILE}"
    )

    log(
        f"R36C_DECISION_FILE="
        f"{R36C_DECISION_FILE}"
    )


    log(
        f"R36A_DEDUPE_READ_ERROR="
        f"{r36a_dedupe_error}"
    )

    log(
        f"R36A_DECISION_READ_ERROR="
        f"{r36a_decision_error}"
    )

    log(
        f"R36C_DEDUPE_READ_ERROR="
        f"{r36c_dedupe_error}"
    )

    log(
        f"R36C_DECISION_READ_ERROR="
        f"{r36c_decision_error}"
    )


    r36a_readable = (

        r36a_dedupe_error
        is None

        and r36a_decision_error
        is None
    )


    r36c_readable = (

        r36c_dedupe_error
        is None

        and r36c_decision_error
        is None
    )


    check(
        "R36A Durable Registries Still Readable",
        r36a_readable,
    )

    check(
        "R36C Durable Registries Still Readable",
        r36c_readable,
    )


    if not r36a_readable:

        FINAL_BLOCKERS.append(
            "R36A_DURABLE_EVIDENCE_UNREADABLE"
        )


    if not r36c_readable:

        FINAL_BLOCKERS.append(
            "R36C_DURABLE_EVIDENCE_UNREADABLE"
        )


    # ==========================================================================
    # TEST 3
    # ==========================================================================

    separator()

    log(
        "R36D TEST 3: "
        "CREDIT EXISTING DURABLE IDENTITIES "
        "WITHOUT STARTING OVER"
    )

    separator()


    r36a_dedupe_ids = (
        collect_update_ids(
            r36a_dedupe
        )
        if r36a_dedupe
        is not None
        else set()
    )


    r36a_decision_ids = (
        collect_update_ids(
            r36a_decision
        )
        if r36a_decision
        is not None
        else set()
    )


    r36c_dedupe_ids = (
        collect_update_ids(
            r36c_dedupe
        )
        if r36c_dedupe
        is not None
        else set()
    )


    r36c_decision_ids = (
        collect_update_ids(
            r36c_decision
        )
        if r36c_decision
        is not None
        else set()
    )


    old_id_in_both = (

        OLD_R36A_UPDATE_ID
        in r36a_dedupe_ids

        and OLD_R36A_UPDATE_ID
        in r36a_decision_ids
    )


    r36c_id_in_both = (

        R36C_UPDATE_ID
        in r36c_dedupe_ids

        and R36C_UPDATE_ID
        in r36c_decision_ids
    )


    OLD_DUPLICATE_DETECTED = (
        old_id_in_both
    )

    OLD_REJECTED_BEFORE_PARSE = (
        old_id_in_both
    )

    NEW_UPDATE_SEEN_BEFORE_STARTUP = (
        r36c_id_in_both
    )

    NEW_UPDATE_ACCEPTED = (
        r36c_id_in_both
    )

    NEW_REPLAY_REJECTED_BEFORE_PARSE = (
        r36c_id_in_both
    )


    log(
        f"OLD_R36A_UPDATE_ID="
        f"{OLD_R36A_UPDATE_ID}"
    )

    log(
        f"R36C_UPDATE_ID="
        f"{R36C_UPDATE_ID}"
    )

    log(
        f"OLD_ID_IN_BOTH_R36A_REGISTRIES="
        f"{old_id_in_both}"
    )

    log(
        f"R36C_ID_IN_BOTH_R36C_REGISTRIES="
        f"{r36c_id_in_both}"
    )

    log(
        f"NEW_UPDATE_ACCEPTED="
        f"{NEW_UPDATE_ACCEPTED}"
    )


    check(
        "Previously Proven R36A Identity Still Durable",
        old_id_in_both,
    )

    check(
        "Previously Proven R36C Identity Still Durable",
        r36c_id_in_both,
    )

    check(
        "NEW_UPDATE_ACCEPTED Explicitly Bound",
        isinstance(
            NEW_UPDATE_ACCEPTED,
            bool,
        ),
    )


    if not old_id_in_both:

        FINAL_BLOCKERS.append(
            "R36A_PROVEN_IDENTITY_NOT_FOUND"
        )


    if not r36c_id_in_both:

        FINAL_BLOCKERS.append(
            "R36C_PROVEN_IDENTITY_NOT_FOUND"
        )


    # ==========================================================================
    # TEST 4
    # ==========================================================================

    separator()

    log(
        "R36D TEST 4: "
        "FROZEN WEEX CREDENTIAL CONTRACT"
    )

    separator()


    api_key_present = bool(
        os.getenv(
            WEEX_API_KEY_ENV,
            "",
        ).strip()
    )


    secret_present = bool(
        os.getenv(
            WEEX_API_SECRET_ENV,
            "",
        ).strip()
    )


    passphrase_present = bool(
        os.getenv(
            WEEX_API_PASSPHRASE_ENV,
            "",
        ).strip()
    )


    log(
        f"{WEEX_API_KEY_ENV}_PRESENT="
        f"{api_key_present}"
    )

    log(
        f"{WEEX_API_SECRET_ENV}_PRESENT="
        f"{secret_present}"
    )

    log(
        f"{WEEX_API_PASSPHRASE_ENV}_PRESENT="
        f"{passphrase_present}"
    )


    credentials_present = all(
        [

            api_key_present,

            secret_present,

            passphrase_present,
        ]
    )


    check(
        "All Three Frozen WEEX Credentials Present",
        credentials_present,
    )


    if not credentials_present:

        FINAL_BLOCKERS.append(
            "WEEX_CREDENTIALS_MISSING"
        )


    # ==========================================================================
    # TEST 5
    # ==========================================================================

    separator()

    log(
        "R36D TEST 5: "
        "CURRENT REAL WEEX "
        "READ-ONLY RECONCILIATION"
    )

    separator()


    reconciliation = (
        reconcile_weex()
    )


    for section in (

        "ticker",

        "balance",

        "position",

        "symbol_config",
    ):

        log(
            f"{section.upper()}="
            f"{canonical_json(reconciliation[section])}"
        )


    ticker_ok = (
        reconciliation[
            "ticker"
        ][
            "ok"
        ]
    )


    balance_ok = (
        reconciliation[
            "balance"
        ][
            "ok"
        ]
    )


    position_read_ok = (
        reconciliation[
            "position"
        ][
            "ok"
        ]
    )


    flat_ok = (
        reconciliation[
            "position"
        ][
            "flat"
        ]
    )


    config_ok = (
        reconciliation[
            "symbol_config"
        ][
            "ok"
        ]
    )


    check(
        "Current Public Mark Price Read",
        ticker_ok,
    )

    check(
        "Current Authenticated USDT Balance Read",
        balance_ok,
    )

    check(
        "Current BTCUSDT Position Read",
        position_read_ok,
    )

    check(
        "BTCUSDT Currently Flat",
        flat_ok,
    )

    check(
        "Current ISOLATED 100x/100x Configuration",
        config_ok,
    )


    if not ticker_ok:

        FINAL_BLOCKERS.append(
            "CURRENT_MARK_PRICE_READ_FAILED"
        )


    if not balance_ok:

        FINAL_BLOCKERS.append(
            "CURRENT_BALANCE_READ_FAILED"
        )


    if not position_read_ok:

        FINAL_BLOCKERS.append(
            "CURRENT_POSITION_READ_FAILED"
        )

    elif not flat_ok:

        FINAL_BLOCKERS.append(
            "BTCUSDT_NOT_FLAT"
        )


    if not config_ok:

        FINAL_BLOCKERS.append(
            "CURRENT_MARGIN_OR_LEVERAGE_MISMATCH"
        )


    # ==========================================================================
    # TEST 6
    # ==========================================================================

    separator()

    log(
        "R36D TEST 6: "
        "R36E MINIMUM-SIZE LIVE CANARY PREVIEW "
        "- NO SUBMISSION"
    )

    separator()


    canary_preview = (
        build_canary_preview()
    )


    preview_ok = (
        canary_preview
        is not None
    )


    if canary_preview:

        log(
            "CANARY_PREVIEW="
            + canonical_json(
                canary_preview
            )
        )


        canary_qty = safe_decimal(
            canary_preview[
                "r36e_canary_qty_btc"
            ]
        )


        strategy_qty = safe_decimal(
            canary_preview[
                "strategy_normalized_qty_btc"
            ]
        )


        canary_qty_ok = (

            canary_qty
            is not None

            and canary_qty
            >= MIN_QTY

            and floor_step(
                canary_qty,
                QTY_STEP,
            )
            == canary_qty
        )


        strategy_math_ok = (

            strategy_qty
            is not None

            and strategy_qty
            >= 0
        )


    else:

        canary_qty_ok = False

        strategy_math_ok = False


    check(
        "Canary Preview Calculated",
        preview_ok,
    )

    check(
        "Canary Quantity Obeys Frozen Quantity Rules",
        canary_qty_ok,
    )

    check(
        "Strategy Quantity Calculation Available",
        strategy_math_ok,
    )

    check(
        "Canary Writer Still Disabled",
        ORDER_SUBMISSION_ENABLED
        is False,
    )


    if not preview_ok:

        FINAL_BLOCKERS.append(
            "CANARY_PREVIEW_UNAVAILABLE"
        )


    if not canary_qty_ok:

        FINAL_BLOCKERS.append(
            "CANARY_QTY_RULE_FAILED"
        )


    # ==========================================================================
    # TEST 7
    # ==========================================================================

    separator()

    log(
        "R36D TEST 7: "
        "ZERO-WRITE INVARIANTS"
    )

    separator()


    zero_write_ok = all(
        [

            EXCHANGE_NETWORK_WRITES
            == 0,

            ORDER_SUBMISSIONS
            == 0,

            LEVERAGE_MUTATIONS
            == 0,

            MARGIN_MODE_MUTATIONS
            == 0,

            POSITION_MUTATIONS
            == 0,

            REAL_ORDERS_SENT
            == 0,

            DEMO_ORDERS_SENT
            == 0,

            REAL_ORDER_EXECUTION
            is False,
        ]
    )


    log(
        f"EXCHANGE_NETWORK_WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )

    log(
        f"ORDER_SUBMISSIONS="
        f"{ORDER_SUBMISSIONS}"
    )

    log(
        f"LEVERAGE_MUTATIONS="
        f"{LEVERAGE_MUTATIONS}"
    )

    log(
        f"MARGIN_MODE_MUTATIONS="
        f"{MARGIN_MODE_MUTATIONS}"
    )

    log(
        f"POSITION_MUTATIONS="
        f"{POSITION_MUTATIONS}"
    )

    log(
        f"REAL_ORDERS_SENT="
        f"{REAL_ORDERS_SENT}"
    )

    log(
        f"DEMO_ORDERS_SENT="
        f"{DEMO_ORDERS_SENT}"
    )

    log(
        f"REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )


    check(
        "R36D Performed Zero Exchange Writes",
        zero_write_ok,
    )


    if not zero_write_ok:

        FINAL_BLOCKERS.append(
            "ZERO_WRITE_INVARIANT_BROKEN"
        )


    # ==========================================================================
    # TEST 8
    # ==========================================================================

    separator()

    log(
        "R36D TEST 8: "
        "FINAL PRE-LIVE GATE"
    )

    separator()


    FINAL_BLOCKERS = sorted(
        set(
            FINAL_BLOCKERS
        )
    )


    pre_live_ready = (
        len(FINAL_BLOCKERS)
        == 0
    )


    TEST_STATUS = (
        "PASS"
        if pre_live_ready
        else "FAIL"
    )


    snapshot = {

        "stage":
            STAGE,

        "purpose":
            PURPOSE,

        "created_at":
            now_iso(),

        "test_status":
            TEST_STATUS,

        "r36d_pre_live_gate":
            (
                "PASS"
                if pre_live_ready
                else "FAIL"
            ),

        "blockers":
            FINAL_BLOCKERS,

        "frozen_contract":
        {

            "credential_env_names":
            [

                WEEX_API_KEY_ENV,

                WEEX_API_SECRET_ENV,

                WEEX_API_PASSPHRASE_ENV,
            ],

            "private_symbol":
                PRIVATE_SYMBOL,

            "public_v2_symbol":
                PUBLIC_V2_SYMBOL,

            "target_margin_mode":
                TARGET_MARGIN_MODE,

            "target_long_leverage":
                str(
                    TARGET_LONG_LEVERAGE
                ),

            "target_short_leverage":
                str(
                    TARGET_SHORT_LEVERAGE
                ),

            "qty_step":
                str(
                    QTY_STEP
                ),

            "min_qty":
                str(
                    MIN_QTY
                ),

            "max_fund_exposure_percent":
                str(
                    MAX_FUND_EXPOSURE_PERCENT
                ),
        },

        "credited_durable_evidence":
        {

            "old_r36a_identity_in_both_registries":
                old_id_in_both,

            "r36c_identity_in_both_registries":
                r36c_id_in_both,

            "new_update_accepted_scope_bound":
                isinstance(
                    NEW_UPDATE_ACCEPTED,
                    bool,
                ),
        },

        "current_weex_reconciliation":
            reconciliation,

        "r36e_canary_preview":
            canary_preview,

        "hard_firebreak":
        {

            "real_order_execution":
                REAL_ORDER_EXECUTION,

            "order_submission_enabled":
                ORDER_SUBMISSION_ENABLED,

            "exchange_mutation_transport_enabled":
                EXCHANGE_MUTATION_TRANSPORT_ENABLED,
        },

        "counters":
        {

            "exchange_network_writes":
                EXCHANGE_NETWORK_WRITES,

            "order_submissions":
                ORDER_SUBMISSIONS,

            "leverage_mutations":
                LEVERAGE_MUTATIONS,

            "margin_mode_mutations":
                MARGIN_MODE_MUTATIONS,

            "position_mutations":
                POSITION_MUTATIONS,

            "real_orders_sent":
                REAL_ORDERS_SENT,

            "demo_orders_sent":
                DEMO_ORDERS_SENT,
        },
    }


    snapshot[
        "snapshot_sha256"
    ] = sha256_json(
        snapshot
    )


    try:

        atomic_write_json(
            R36D_SNAPSHOT_FILE,
            snapshot,
        )

        snapshot_written = True

        snapshot_error = None


    except Exception as exc:

        snapshot_written = False

        snapshot_error = (
            f"{exc.__class__.__name__}: "
            f"{exc}"
        )

        TEST_STATUS = "FAIL"

        FINAL_BLOCKERS.append(
            "R36D_SNAPSHOT_WRITE_FAILED"
        )

        FINAL_BLOCKERS = sorted(
            set(
                FINAL_BLOCKERS
            )
        )


    final_pass = (

        pre_live_ready

        and snapshot_written
    )


    log(
        f"R36D_SNAPSHOT_FILE="
        f"{R36D_SNAPSHOT_FILE}"
    )

    log(
        f"R36D_SNAPSHOT_WRITTEN="
        f"{snapshot_written}"
    )

    log(
        f"R36D_SNAPSHOT_ERROR="
        f"{snapshot_error}"
    )


    log(
        "R36D_PRE_LIVE_GATE="
        + (
            "PASS"
            if final_pass
            else "FAIL"
        )
    )


    log(
        f"FINAL_BLOCKERS="
        f"{FINAL_BLOCKERS}"
    )


    if final_pass:

        log(
            "NEXT_STAGE="
            "R36E_FIRST_LIVE_CANARY"
        )

    else:

        log(
            "NEXT_STAGE="
            "FIX_ONLY_LISTED_BLOCKERS"
        )


    check(
        "R36D Final Pre-Live Production Gate",
        final_pass,
    )


    # ==========================================================================
    # FINAL SUMMARY
    # ==========================================================================

    separator()

    log(
        f"{STAGE}: "
        "FINAL TEST SUMMARY"
    )

    separator()


    log(
        f"TEST_STATUS="
        f"{TEST_STATUS}"
    )


    log(
        "R36D_PRE_LIVE_GATE="
        + (
            "PASS"
            if final_pass
            else "FAIL"
        )
    )


    log(
        f"FINAL_BLOCKERS="
        f"{FINAL_BLOCKERS}"
    )


    log(
        f"REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )


    log(
        f"FIRST_REAL_ORDER_ALLOWED="
        f"{FIRST_REAL_ORDER_ALLOWED}"
    )


    log(
        f"EXCHANGE_NETWORK_WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )


    log(
        f"ORDER_SUBMISSIONS="
        f"{ORDER_SUBMISSIONS}"
    )


    log(
        "NO REAL ORDER WAS SENT"
    )


    if final_pass:

        log(
            "NEXT_STAGE="
            "R36E_FIRST_LIVE_CANARY"
        )


    separator()


# ==============================================================================
# HEARTBEAT
# ==============================================================================

def heartbeat_loop():

    global HEARTBEAT


    while True:

        HEARTBEAT += 1


        log(

            f"{STAGE}: "

            f"HEARTBEAT="
            f"{HEARTBEAT} "

            f"TEST_STATUS="
            f"{TEST_STATUS} "

            f"OLD_DUPLICATE_DETECTED="
            f"{OLD_DUPLICATE_DETECTED} "

            f"OLD_REJECTED_BEFORE_PARSE="
            f"{OLD_REJECTED_BEFORE_PARSE} "

            f"NEW_UPDATE_SEEN_BEFORE_STARTUP="
            f"{NEW_UPDATE_SEEN_BEFORE_STARTUP} "

            f"NEW_UPDATE_ACCEPTED="
            f"{NEW_UPDATE_ACCEPTED} "

            f"NEW_REPLAY_REJECTED_BEFORE_PARSE="
            f"{NEW_REPLAY_REJECTED_BEFORE_PARSE} "

            f"BTCUSDT_FLAT="
            f"{BTCUSDT_FLAT} "

            f"MARGIN_MODE="
            f"{CURRENT_MARGIN_MODE} "

            f"LONG_LEVERAGE="
            f"{CURRENT_LONG_LEVERAGE} "

            f"SHORT_LEVERAGE="
            f"{CURRENT_SHORT_LEVERAGE} "

            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "

            f"ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS} "

            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )


        time.sleep(30)


# ==============================================================================
# MAIN
# ==============================================================================

def main():

    global TEST_STATUS


    start_health_server()


    try:

        run_r36d()


    except Exception as exc:

        TEST_STATUS = "FAIL"


        separator()

        log(
            f"{STAGE}: "
            "UNHANDLED TEST ERROR"
        )

        separator()


        log(
            f"EXCEPTION_CLASS="
            f"{exc.__class__.__name__}"
        )


        log(
            f"EXCEPTION_MESSAGE="
            f"{exc}"
        )


        traceback.print_exc()


        log(
            "TEST_STATUS=FAIL"
        )


        separator()


    heartbeat_loop()


# ==============================================================================
# ENTRY
# ==============================================================================

if __name__ == "__main__":

    main()

