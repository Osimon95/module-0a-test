
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

    FINAL_BLOCKERS.append(
        name
    )

    return False


def diagnostic_check(
    name,
    condition,
    detail=None,
):
    if condition:
        log(
            f"DIAGNOSTIC PASS: {name}"
        )

        if detail:
            log(
                f"      {detail}"
            )

        return True

    log(
        f"DIAGNOSTIC FAIL: {name}"
    )

    if detail:
        log(
            f"      {detail}"
        )

    return False


def D(value):
    return Decimal(
        str(value)
    )


def quantize_down(
    value,
    step,
):
    value = D(value)
    step = D(step)

    if step <= 0:
        raise ValueError(
            "Invalid quantization step"
        )

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def decimal_to_string(value):
    if value is None:
        return None

    value = D(value)
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


def canonical_json(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def sha256_text(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def read_json_file(
    path,
    default=None,
):
    if default is None:
        default = {}

    try:
        if not os.path.exists(path):
            return default

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    except Exception as exc:
        log(
            f"READ JSON FAILED path={path} error={exc}"
        )
        return default


def write_json_file(
    path,
    data,
):
    tmp = path + ".tmp"

    with open(
        tmp,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            indent=2,
            sort_keys=True,
            default=str,
        )

    os.replace(
        tmp,
        path,
    )


def collect_ids_from_file(path):
    ids = set()

    data = read_json_file(
        path,
        default=None,
    )

    if data is None:
        return ids

    def walk(value):
        if isinstance(
            value,
            dict,
        ):
            for key, item in value.items():
                if (
                    isinstance(key, str)
                    and "id" in key.lower()
                    and isinstance(item, str)
                ):
                    ids.add(item)

                walk(item)

        elif isinstance(
            value,
            list,
        ):
            for item in value:
                walk(item)

    walk(data)

    return ids


class HealthHandler(
    BaseHTTPRequestHandler
):
    def do_GET(self):
        body = (
            f"stage={STAGE}\n"
            f"status={TEST_STATUS}\n"
        ).encode()

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/plain",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format_string,
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
        f"{STAGE}: HEALTH SERVER STARTED ON PORT {port}"
    )


def build_signature(
    timestamp,
    method,
    request_path,
    body="",
):
    api_secret = os.getenv(
        "WEEX_API_SECRET"
    )

    if not api_secret:
        raise RuntimeError(
            "WEEX_API_SECRET missing"
        )

    prehash = (
        str(timestamp)
        + method.upper()
        + request_path
        + body
    )

    digest = hmac.new(
        api_secret.encode(),
        prehash.encode(),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode()


async def weex_get(
    path,
    params=None,
    authenticated=False,
):
    params = (
        params
        or {}
    )

    from urllib.parse import urlencode

    query_string = urlencode(
        params,
        doseq=True,
    )

    request_target = path

    if query_string:
        request_target += (
            "?" + query_string
        )

    url = (
        API_BASE_URL
        + request_target
    )

    headers = {}

    if authenticated:
        api_key = os.getenv(
            "WEEX_API_KEY"
        )

        passphrase = os.getenv(
            "WEEX_API_PASSPHRASE"
        )

        if not api_key:
            raise RuntimeError(
                "WEEX_API_KEY missing"
            )

        if not passphrase:
            raise RuntimeError(
                "WEEX_API_PASSPHRASE missing"
            )

        timestamp = str(
            int(
                time.time()
                * 1000
            )
        )

        signature = build_signature(
            timestamp,
            "GET",
            request_target,
            "",
        )

        headers = {
            "ACCESS-KEY": api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": passphrase,
            "Content-Type": "application/json",
        }

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        async with session.get(
            url,
            headers=headers,
        ) as response:

            text = (
                await response.text()
            )

            if response.status >= 400:
                raise RuntimeError(
                    f"WEEX GET HTTP {response.status}: {text}"
                )

            try:
                return json.loads(
                    text
                )

            except Exception:
                return {
                    "raw": text
                }


async def weex_demo_post(
    path,
    payload,
):
    if (
        path
        != R36F14_DEMO_ORDER_ENDPOINT
    ):
        raise RuntimeError(
            "R36F.15 demo transport refused non-demo endpoint"
        )

    if not (
        R36F15_DEMO_POST_TRANSPORT_ENABLED
        and R36F15_DEMO_ORDER_SUBMISSION_ENABLED
        and R36F15_FIRST_DEMO_ORDER_ALLOWED
    ):
        raise RuntimeError(
            "R36F.15 demo transport is disabled"
        )

    if not (
        REAL_ORDER_EXECUTION is False
        and EXCHANGE_MUTATION_TRANSPORT_ENABLED is False
        and ORDER_SUBMISSION_ENABLED is False
        and LEVERAGE_MUTATION_ENABLED is False
        and MARGIN_MODE_MUTATION_ENABLED is False
        and POSITION_MUTATION_ENABLED is False
        and FIRST_REAL_ORDER_ALLOWED is False
    ):
        raise RuntimeError(
            "R36F.15 production firebreak is not intact"
        )

    api_key = os.getenv(
        "WEEX_API_KEY"
    )

    passphrase = os.getenv(
        "WEEX_API_PASSPHRASE"
    )

    if not api_key:
        raise RuntimeError(
            "WEEX_API_KEY missing"
        )

    if not passphrase:
        raise RuntimeError(
            "WEEX_API_PASSPHRASE missing"
        )

    body = canonical_json(
        payload
    )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = build_signature(
        timestamp,
        "POST",
        path,
        body,
    )

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    url = (
        API_BASE_URL
        + path
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        async with session.post(
            url,
            headers=headers,
            data=body,
        ) as response:

            text = (
                await response.text()
            )

            try:
                data = json.loads(
                    text
                )

            except Exception:
                data = {
                    "raw": text
                }

            result = {
                "http_status": response.status,
                "response": data,
                "raw_text": text,
            }

            if response.status >= 400:
                raise RuntimeError(
                    f"WEEX DEMO POST HTTP {response.status}: {text}"
                )

            return result


def r36f15_demo_journal_unresolved(
    journal,
):
    if (
        not isinstance(
            journal,
            dict,
        )
        or not journal
    ):
        return False

    return journal.get(
        "state"
    ) in {
        "PREPARED",
        "SENT_AMBIGUOUS",
    }


def r36f15_demo_journal_completed(
    journal,
):
    return bool(
        isinstance(
            journal,
            dict,
        )
        and journal.get(
            "state"
        )
        == "COMPLETED"
        and journal.get(
            "success"
        )
        is True
    )


def _r36f153_history_rows(data):
    if isinstance(
        data,
        list,
    ):
        return data

    if isinstance(
        data,
        dict,
    ):
        for key in (
            "data",
            "list",
            "rows",
            "orders",
        ):
            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                return value

    return None


async def r36f153_lookup_demo_order_by_client_id(
    client_order_id,
):
    client_order_id = str(
        client_order_id
        or ""
    ).strip()

    if not client_order_id:
        return {
            "status": "UNKNOWN",
            "reason": "MISSING_CLIENT_ORDER_ID",
            "order": None,
        }

    try:
        data = await weex_get(
            R36F14_DEMO_ORDER_HISTORY_ENDPOINT,
            params={
                "symbol": R36F14_DEMO_SYMBOL,
                "limit": 1000,
                "page": 0,
            },
            authenticated=True,
        )

    except Exception as exc:
        return {
            "status": "UNKNOWN",
            "reason": "DEMO_HISTORY_LOOKUP_FAILED",
            "error": str(exc),
            "order": None,
        }

    rows = _r36f153_history_rows(
        data
    )

    if rows is None:
        return {
            "status": "UNKNOWN",
            "reason": "DEMO_HISTORY_RESPONSE_UNRECOGNIZED",
            "order": None,
        }

    for row in rows:
        if not isinstance(
            row,
            dict,
        ):
            continue

        row_client_id = str(
            row.get(
                "clientOrderId"
            )
            or row.get(
                "newClientOrderId"
            )
            or ""
        ).strip()

        if (
            row_client_id
            == client_order_id
        ):
            return {
                "status": "FOUND",
                "reason": "CLIENT_ORDER_ID_FOUND_IN_DEMO_HISTORY",
                "order": row,
            }

    return {
        "status": "NOT_FOUND",
        "reason": "CLIENT_ORDER_ID_NOT_FOUND_IN_DEMO_HISTORY",
        "order": None,
    }


async def r36f153_reconcile_demo_journal(
    journal,
):
    if (
        not isinstance(
            journal,
            dict,
        )
        or not journal
    ):
        return {
            "resolved": True,
            "retry_allowed": True,
            "reason": "NO_JOURNAL",
            "journal": {},
            "changed": False,
        }

    state = str(
        journal.get(
            "state"
        )
        or ""
    ).strip().upper()

    if state == "COMPLETED":
        return {
            "resolved": True,
            "retry_allowed": False,
            "reason": "COMPLETED_REMAINS_TERMINAL",
            "journal": journal,
            "changed": False,
        }

    if state == "REJECTED":
        return {
            "resolved": True,
            "retry_allowed": True,
            "reason": "REJECTED_PERMITS_FRESH_RETRY",
            "journal": journal,
            "changed": False,
        }

    if state not in {
        "PREPARED",
        "SENT_AMBIGUOUS",
    }:
        return {
            "resolved": False,
            "retry_allowed": False,
            "reason": "UNKNOWN_JOURNAL_STATE_BLOCKS_RETRY",
            "journal": journal,
            "changed": False,
        }

    client_order_id = str(
        journal.get(
            "client_order_id"
        )
        or ""
    ).strip()

    if not client_order_id:
        return {
            "resolved": False,
            "retry_allowed": False,
            "reason": "MISSING_CLIENT_ID_BLOCKS_RETRY",
            "journal": journal,
            "changed": False,
        }

    lookup = (
        await r36f153_lookup_demo_order_by_client_id(
            client_order_id
        )
    )

    lookup_status = lookup.get(
        "status"
    )

    if lookup_status == "FOUND":
        order = (
            lookup.get(
                "order"
            )
            if isinstance(
                lookup.get(
                    "order"
                ),
                dict,
            )
            else {}
        )

        reconciled = {
            **journal,
            "state": "COMPLETED",
            "updated_at": now_iso(),
            "success": True,
            "reconciliation_status": "FOUND",
            "reconciliation_reason": lookup.get(
                "reason"
            ),
            "order_id": str(
                order.get(
                    "orderId",
                    journal.get(
                        "order_id",
                        "",
                    ),
                )
            ),
            "client_order_id_response": str(
                order.get(
                    "clientOrderId",
                    client_order_id,
                )
            ),
            "reconciled_order": order,
        }

        write_json_file(
            R36F15_DEMO_JOURNAL_FILE,
            reconciled,
        )

        return {
            "resolved": True,
            "retry_allowed": False,
            "reason": "AMBIGUOUS_FOUND_MARKED_COMPLETED",
            "journal": reconciled,
            "changed": True,
        }

    if lookup_status == "NOT_FOUND":
        reconciled = {
            **journal,
            "state": "REJECTED",
            "updated_at": now_iso(),
            "success": False,
            "reconciliation_status": "NOT_FOUND",
            "reconciliation_reason": lookup.get(
                "reason"
            ),
        }

        write_json_file(
            R36F15_DEMO_JOURNAL_FILE,
            reconciled,
        )

        return {
            "resolved": True,
            "retry_allowed": True,
            "reason": "AMBIGUOUS_NOT_FOUND_MARKED_REJECTED",
            "journal": reconciled,
            "changed": True,
        }

    return {
        "resolved": False,
        "retry_allowed": False,
        "reason": lookup.get(
            "reason",
            "AMBIGUOUS_UNKNOWN_BLOCKS_RETRY",
        ),
        "journal": journal,
        "lookup": lookup,
        "changed": False,
    }


async def r36f154_validate_fresh_demo_triggers(
    payload,
):
    payload = (
        payload
        if isinstance(
            payload,
            dict,
        )
        else {}
    )

    direction = str(
        payload.get(
            "positionSide"
        )
        or ""
    ).strip().upper()

    try:
        tp = D(
            payload.get(
                "tpTriggerPrice",
                "0",
            )
        )

        sl = D(
            payload.get(
                "slTriggerPrice",
                "0",
            )
        )

    except Exception as exc:
        return {
            "valid": False,
            "reason": "JIT_TRIGGER_PARSE_FAILED",
            "error": str(exc),
        }

    if direction not in {
        "LONG",
        "SHORT",
    }:
        return {
            "valid": False,
            "reason": "JIT_DIRECTION_INVALID",
            "direction": direction,
        }

    try:
        fresh_mark = D(
            await load_mark_price()
        )

    except Exception as exc:
        return {
            "valid": False,
            "reason": "JIT_FRESH_MARK_READ_FAILED",
            "error": str(exc),
        }

    if (
        fresh_mark <= 0
        or tp <= 0
        or sl <= 0
    ):
        return {
            "valid": False,
            "reason": "JIT_NON_POSITIVE_PRICE",
            "direction": direction,
            "fresh_mark_price": decimal_to_string(
                fresh_mark
            ),
            "tp_trigger_price": decimal_to_string(
                tp
            ),
            "sl_trigger_price": decimal_to_string(
                sl
            ),
        }

    if direction == "LONG":
        valid = (
            sl
            < fresh_mark
            < tp
        )

        reason = (
            "JIT_LONG_TRIGGERS_VALID"
            if valid
            else "JIT_LONG_TRIGGER_STALE_OR_CROSSED"
        )

    else:
        valid = (
            tp
            < fresh_mark
            < sl
        )

        reason = (
            "JIT_SHORT_TRIGGERS_VALID"
            if valid
            else "JIT_SHORT_TRIGGER_STALE_OR_CROSSED"
        )

    return {
        "valid": bool(
            valid
        ),
        "reason": reason,
        "direction": direction,
        "fresh_mark_price": decimal_to_string(
            fresh_mark
        ),
        "tp_trigger_price": decimal_to_string(
            tp
        ),
        "sl_trigger_price": decimal_to_string(
            sl
        ),
    }


R36F155_TARGET_DEMO_ORDER_ID = os.getenv(
    "R36F155_TARGET_DEMO_ORDER_ID",
    "792989056504955607",
).strip()

R36F155_LAST_RECONCILIATION = {}


def r36f155_order_id(row):
    if not isinstance(
        row,
        dict,
    ):
        return ""

    for key in (
        "orderId",
        "order_id",
        "id",
    ):
        value = row.get(
            key
        )

        if value is not None:
            return str(
                value
            ).strip()

    return ""


def r36f155_order_status(row):
    if not isinstance(
        row,
        dict,
    ):
        return "UNKNOWN"

    for key in (
        "status",
        "orderStatus",
        "state",
    ):
        value = row.get(
            key
        )

        if value is not None:
            return str(
                value
            ).strip().upper()

    return "UNKNOWN"


def r36f155_order_direction(row):
    if not isinstance(
        row,
        dict,
    ):
        return ""

    position_side = str(
        row.get(
            "positionSide"
        )
        or ""
    ).strip().upper()

    if position_side in {
        "LONG",
        "SHORT",
    }:
        return position_side

    side = str(
        row.get(
            "side"
        )
        or ""
    ).strip().upper()

    if side == "BUY":
        return "LONG"

    if side == "SELL":
        return "SHORT"

    return ""


def r36f155_position_direction(row):
    if not isinstance(
        row,
        dict,
    ):
        return ""

    for key in (
        "positionSide",
        "side",
    ):
        value = str(
            row.get(
                key
            )
            or ""
        ).strip().upper()

        if value in {
            "LONG",
            "SHORT",
        }:
            return value

    return ""


def r36f155_position_size(row):
    if not isinstance(
        row,
        dict,
    ):
        return D("0")

    for key in (
        "size",
        "positionSize",
        "positionAmt",
        "quantity",
        "qty",
    ):
        if key in row:
            try:
                return abs(
                    D(
                        row.get(
                            key
                        )
                        or "0"
                    )
                )

            except Exception:
                continue

    return D("0")


def r36f155_normalize_rows(data):
    if isinstance(
        data,
        list,
    ):
        return data

    if not isinstance(
        data,
        dict,
    ):
        return []

    for key in (
        "data",
        "list",
        "rows",
        "orders",
        "positions",
        "result",
    ):
        value = data.get(
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
                "list",
                "rows",
                "orders",
                "positions",
            ):
                nested = value.get(
                    nested_key
                )

                if isinstance(
                    nested,
                    list,
                ):
                    return nested

    return []


def r36f155_extract_protection_fields(
    order,
):
    result = {
        "tp_field": None,
        "tp_value": None,
        "sl_field": None,
        "sl_value": None,
    }

    if not isinstance(
        order,
        dict,
    ):
        return result

    for key in (
        "tpTriggerPrice",
        "takeProfitPrice",
        "takeProfit",
        "tpPrice",
        "presetTakeProfitPrice",
    ):
        if key in order:
            result[
                "tp_field"
            ] = key

            result[
                "tp_value"
            ] = order.get(
                key
            )

            break

    for key in (
        "slTriggerPrice",
        "stopLossPrice",
        "stopLoss",
        "slPrice",
        "presetStopLossPrice",
    ):
        if key in order:
            result[
                "sl_field"
            ] = key

            result[
                "sl_value"
            ] = order.get(
                key
            )

            break

    return result


async def r36f155_reconcile_existing_demo_exposure():
    global R36F155_LAST_RECONCILIATION

    result = {
        "stage": STAGE,
        "checked_at": now_iso(),
        "target_order_id": R36F155_TARGET_DEMO_ORDER_ID,
        "history_read_success": False,
        "position_read_success": False,
        "target_order_found": False,
        "target_order_status": "UNKNOWN",
        "target_order_direction": "",
        "target_order_symbol": "",
        "matching_position_found": False,
        "matching_position_count": 0,
        "duplicate_entry_blocked": True,
        "duplicate_block_reason": "RECONCILIATION_NOT_YET_COMPLETED",
        "safe_to_consider_new_entry": False,
        "protection_verified": False,
        "protection_reason": "NOT_CHECKED",
        "read_only": True,
        "real_order_execution": REAL_ORDER_EXECUTION,
    }

    line()

    log(
        "R36F.15.5 POST-ORDER RECONCILIATION START"
    )

    log(
        "R36F.15.5 TARGET DEMO ORDER ID = "
        + R36F155_TARGET_DEMO_ORDER_ID
    )

    try:
        history_data = await weex_get(
            R36F14_DEMO_ORDER_HISTORY_ENDPOINT,
            params={
                "symbol": R36F14_DEMO_SYMBOL,
                "limit": 1000,
                "page": 0,
            },
            authenticated=True,
        )

        history_rows = (
            r36f155_normalize_rows(
                history_data
            )
        )

        result[
            "history_read_success"
        ] = True

        result[
            "history_count"
        ] = len(
            history_rows
        )

        log(
            "R36F.15.5 DEMO ORDER HISTORY READ = PASS"
        )

        log(
            "R36F.15.5 DEMO ORDER HISTORY ROWS = "
            + str(
                len(
                    history_rows
                )
            )
        )

    except Exception as exc:
        result[
            "history_error"
        ] = str(
            exc
        )

        result[
            "duplicate_entry_block_reason"
        ] = (
            "ORDER_HISTORY_READ_FAILED_FAIL_CLOSED"
        )

        result[
            "duplicate_block_reason"
        ] = (
            "ORDER_HISTORY_READ_FAILED_FAIL_CLOSED"
        )

        log(
            "R36F.15.5 DEMO ORDER HISTORY READ = FAIL"
        )

        log(
            "R36F.15.5 DEMO ORDER HISTORY ERROR = "
            + str(
                exc
            )
        )

        R36F155_LAST_RECONCILIATION = (
            result
        )

        line()

        return result

    target_order = None

    for row in history_rows:
        if (
            isinstance(
                row,
                dict,
            )
            and r36f155_order_id(
                row
            )
            == R36F155_TARGET_DEMO_ORDER_ID
        ):
            target_order = row
            break

    if target_order is not None:
        result[
            "target_order_found"
        ] = True

        result[
            "target_order_status"
        ] = r36f155_order_status(
            target_order
        )

        result[
            "target_order_direction"
        ] = r36f155_order_direction(
            target_order
        )

        result[
            "target_order_symbol"
        ] = str(
            target_order.get(
                "symbol"
            )
            or ""
        ).strip().upper()

        result[
            "target_order_qty"
        ] = target_order.get(
            "origQty"
        )

        result[
            "target_order_executed_qty"
        ] = target_order.get(
            "executedQty"
        )

        result[
            "target_order_avg_price"
        ] = target_order.get(
            "avgPrice"
        )

        result[
            "target_order_client_id"
        ] = target_order.get(
            "clientOrderId"
        )

        result.update(
            r36f155_extract_protection_fields(
                target_order
            )
        )

        if (
            result.get(
                "tp_field"
            )
            is not None
            or result.get(
                "sl_field"
            )
            is not None
        ):
            result[
                "protection_reason"
            ] = (
                "PROTECTION_FIELDS_RETURNED_IN_ORDER_HISTORY"
            )

        else:
            result[
                "protection_reason"
            ] = (
                "TP_SL_NOT_RETURNED_BY_DEMO_ORDER_HISTORY"
            )

        log(
            "R36F.15.5 TARGET ORDER FOUND = True"
        )

        log(
            "R36F.15.5 ORDER ID = "
            + r36f155_order_id(
                target_order
            )
        )

        log(
            "R36F.15.5 ORDER SYMBOL = "
            + result[
                "target_order_symbol"
            ]
        )

        log(
            "R36F.15.5 ORDER DIRECTION = "
            + result[
                "target_order_direction"
            ]
        )

        log(
            "R36F.15.5 ORDER STATUS = "
            + result[
                "target_order_status"
            ]
        )

    else:
        log(
            "R36F.15.5 TARGET ORDER FOUND = False"
        )

    try:
        position_data = await weex_get(
            R36F14_DEMO_POSITIONS_ENDPOINT,
            authenticated=True,
        )

        position_rows = (
            r36f155_normalize_rows(
                position_data
            )
        )

        result[
            "position_read_success"
        ] = True

        result[
            "position_count"
        ] = len(
            position_rows
        )

        log(
            "R36F.15.5 DEMO POSITION READ = PASS"
        )

        log(
            "R36F.15.5 DEMO POSITION ROWS = "
            + str(
                len(
                    position_rows
                )
            )
        )

    except Exception as exc:
        result[
            "position_error"
        ] = str(
            exc
        )

        result[
            "duplicate_block_reason"
        ] = (
            "POSITION_READ_FAILED_FAIL_CLOSED"
        )

        log(
            "R36F.15.5 DEMO POSITION READ = FAIL"
        )

        log(
            "R36F.15.5 DEMO POSITION ERROR = "
            + str(
                exc
            )
        )

        R36F155_LAST_RECONCILIATION = (
            result
        )

        line()

        return result

    expected_symbol = (
        result.get(
            "target_order_symbol"
        )
        or R36F14_DEMO_SYMBOL
    )

    expected_direction = (
        result.get(
            "target_order_direction"
        )
        or ""
    )

    matching = []

    for row in position_rows:
        if not isinstance(
            row,
            dict,
        ):
            continue

        symbol = str(
            row.get(
                "symbol"
            )
            or ""
        ).strip().upper()

        direction = (
            r36f155_position_direction(
                row
            )
        )

        size = (
            r36f155_position_size(
                row
            )
        )

        if size <= 0:
            continue
        if (
            expected_symbol
            and symbol
            != expected_symbol
        ):
            continue

        if (
            expected_direction
            and direction
            and direction
            != expected_direction
        ):
            continue

        matching.append(
            row
        )

    result[
        "matching_position_found"
    ] = bool(
        matching
    )

    result[
        "matching_position_count"
    ] = len(
        matching
    )

    if matching:
        result[
            "duplicate_entry_blocked"
        ] = True

        result[
            "duplicate_block_reason"
        ] = (
            "POSITION_ALREADY_EXISTS"
        )

        result[
            "safe_to_consider_new_entry"
        ] = False

    elif result[
        "target_order_found"
    ]:
        status = result[
            "target_order_status"
        ]

        if status in {
            "NEW",
            "OPEN",
            "PENDING",
            "LIVE",
            "ACCEPTED",
            "CREATED",
            "PARTIALLY_FILLED",
            "PARTIAL_FILLED",
            "PARTIALLYFILLED",
        }:
            result[
                "duplicate_entry_blocked"
            ] = True

            result[
                "duplicate_block_reason"
            ] = (
                "OPEN_ENTRY_ORDER_ALREADY_EXISTS"
            )

        elif status == "FILLED":
            result[
                "duplicate_entry_blocked"
            ] = True

            result[
                "duplicate_block_reason"
            ] = (
                "FILLED_ORDER_FOUND_POSITION_REQUIRES_CONSERVATIVE_RECONCILIATION"
            )

        elif status == "UNKNOWN":
            result[
                "duplicate_entry_blocked"
            ] = True

            result[
                "duplicate_block_reason"
            ] = (
                "UNKNOWN_ORDER_STATUS_FAIL_CLOSED"
            )

        else:
            result[
                "duplicate_entry_blocked"
            ] = False

            result[
                "duplicate_block_reason"
            ] = (
                "TARGET_ORDER_TERMINAL_AND_NO_MATCHING_POSITION_FOUND"
            )

            result[
                "safe_to_consider_new_entry"
            ] = True

    else:
        active_demo_position = any(
            isinstance(
                row,
                dict,
            )
            and str(
                row.get(
                    "symbol"
                )
                or ""
            ).strip().upper()
            == R36F14_DEMO_SYMBOL
            and r36f155_position_size(
                row
            )
            > 0
            for row in position_rows
        )

        if active_demo_position:
            result[
                "duplicate_entry_blocked"
            ] = True

            result[
                "duplicate_block_reason"
            ] = (
                "UNTRACKED_ACTIVE_DEMO_POSITION_EXISTS"
            )

        else:
            result[
                "duplicate_entry_blocked"
            ] = False

            result[
                "duplicate_block_reason"
            ] = (
                "NO_TARGET_ORDER_OR_ACTIVE_DEMO_POSITION"
            )

            result[
                "safe_to_consider_new_entry"
            ] = True

    log(
        "R36F.15.5 DUPLICATE ENTRY BLOCKED = "
        + str(
            result[
                "duplicate_entry_blocked"
            ]
        )
    )

    log(
        "R36F.15.5 DUPLICATE BLOCK REASON = "
        + str(
            result[
                "duplicate_block_reason"
            ]
        )
    )

    log(
        "R36F.15.5 SAFE TO CONSIDER NEW ENTRY = "
        + str(
            result[
                "safe_to_consider_new_entry"
            ]
        )
    )

    log(
        "R36F.15.5 REAL MONEY EXECUTION = "
        + str(
            REAL_ORDER_EXECUTION
        )
    )

    R36F155_LAST_RECONCILIATION = (
        result
    )

    line()

    return result


R36F159_LAST_EXPOSURE_CHECK = {}


def r36f159_command_identity(
    command_preview,
):
    command = str(
        command_preview.get(
            "command"
        )
        or ""
    ).strip().upper()

    direction = str(
        command_preview.get(
            "direction"
        )
        or ""
    ).strip().upper()

    token = str(
        R36F159_COMMAND_TOKEN
        or ""
    ).strip()

    material = {
        "command": command,
        "direction": direction,
        "symbol": R36F14_DEMO_SYMBOL,
        "token": token,
        "stage": "R36F.15.9",
    }

    return sha256_text(
        canonical_json(
            material
        )
    )


def r36f159_client_order_id(
    command_preview,
):
    direction = str(
        command_preview.get(
            "direction"
        )
        or ""
    ).strip().upper()

    prefix = (
        "L"
        if direction == "LONG"
        else "S"
        if direction == "SHORT"
        else "X"
    )

    digest = (
        r36f159_command_identity(
            command_preview
        )[:16].upper()
    )

    value = (
        f"R36F159-{prefix}-{digest}"
    )

    if len(value) > 36:
        raise ValueError(
            "R36F.15.9 client id exceeds WEEX limit"
        )

    return value

# ============================================================
# R1.8.2
# ZERO-WRITE CLIENT-ID LIFECYCLE POLICY VALIDATOR
#
# PURPOSE:
# Prove that historical client IDs and active client IDs
# must not be treated as the same thing.
#
# NO WEEX POST
# NO JOURNAL WRITE
# NO STATE CHANGE
# NO REAL ORDER
# NO DEMO ORDER
# ============================================================

R182_STAGE = "R1.8.2"


def r182_client_id_lifecycle_decision(
    *,
    candidate_client_id,
    historical_client_ids,
    active_client_ids,
    history_read_ok,
    position_read_ok,
    active_positions,
    open_orders,
):
    candidate_client_id = str(
        candidate_client_id
        or ""
    ).strip()

    historical_client_ids = set(
        str(value).strip()
        for value in (
            historical_client_ids
            or []
        )
        if str(value).strip()
    )

    active_client_ids = set(
        str(value).strip()
        for value in (
            active_client_ids
            or []
        )
        if str(value).strip()
    )

    if not history_read_ok:
        return {
            "allow": False,
            "reason": "HISTORY_READ_FAILED_FAIL_CLOSED",
        }

    if not position_read_ok:
        return {
            "allow": False,
            "reason": "POSITION_READ_FAILED_FAIL_CLOSED",
        }

    if int(active_positions) > 0:
        return {
            "allow": False,
            "reason": "ACTIVE_POSITION_BLOCKS",
        }

    if int(open_orders) > 0:
        return {
            "allow": False,
            "reason": "OPEN_ORDER_BLOCKS",
        }

    if (
        candidate_client_id
        and candidate_client_id
        in active_client_ids
    ):
        return {
            "allow": False,
            "reason": "ACTIVE_CLIENT_ID_BLOCKS",
        }

    if (
        candidate_client_id
        and candidate_client_id
        in historical_client_ids
    ):
        return {
            "allow": True,
            "reason": (
                "HISTORICAL_TERMINAL_ID_DOES_NOT_BLOCK_FLAT_ACCOUNT"
            ),
        }

    return {
        "allow": True,
        "reason": "NEW_CLIENT_ID_AND_FLAT_ACCOUNT",
    }


def r182_run_zero_write_tests():
    log(
        "R1.8.2 ZERO-WRITE LIFECYCLE TEST START"
    )

    historical_id = (
        "R36F159-S-A2420AFD38532D66"
    )

    # --------------------------------------------------------
    # TEST 1
    # Historical completed ID + flat account
    # Expected: ALLOW
    # --------------------------------------------------------

    test1 = (
        r182_client_id_lifecycle_decision(
            candidate_client_id=historical_id,
            historical_client_ids=[
                historical_id,
            ],
            active_client_ids=[],
            history_read_ok=True,
            position_read_ok=True,
            active_positions=0,
            open_orders=0,
        )
    )

    test1_pass = (
        test1.get("allow") is True
        and test1.get("reason")
        == "HISTORICAL_TERMINAL_ID_DOES_NOT_BLOCK_FLAT_ACCOUNT"
    )

    log(
        "R1.8.2 TEST 1 "
        "HISTORICAL ID + FLAT = "
        + (
            "PASS"
            if test1_pass
            else "FAIL"
        )
        + " RESULT="
        + str(test1)
    )

    # --------------------------------------------------------
    # TEST 2
    # Same client ID is ACTIVE
    # Expected: BLOCK
    # --------------------------------------------------------

    test2 = (
        r182_client_id_lifecycle_decision(
            candidate_client_id=historical_id,
            historical_client_ids=[
                historical_id,
            ],
            active_client_ids=[
                historical_id,
            ],
            history_read_ok=True,
            position_read_ok=True,
            active_positions=0,
            open_orders=1,
        )
    )

    test2_pass = (
        test2.get("allow") is False
        and test2.get("reason")
        in {
            "OPEN_ORDER_BLOCKS",
            "ACTIVE_CLIENT_ID_BLOCKS",
        }
    )

    log(
        "R1.8.2 TEST 2 "
        "ACTIVE ID = "
        + (
            "PASS"
            if test2_pass
            else "FAIL"
        )
        + " RESULT="
        + str(test2)
    )

    # --------------------------------------------------------
    # TEST 3
    # Active position exists
    # Expected: BLOCK
    # --------------------------------------------------------

    test3 = (
        r182_client_id_lifecycle_decision(
            candidate_client_id=(
                "R36F159-S-NEWOPPORTUNITY"
            ),
            historical_client_ids=[],
            active_client_ids=[],
            history_read_ok=True,
            position_read_ok=True,
            active_positions=1,
            open_orders=0,
        )
    )

    test3_pass = (
        test3.get("allow") is False
        and test3.get("reason")
        == "ACTIVE_POSITION_BLOCKS"
    )

    log(
        "R1.8.2 TEST 3 "
        "ACTIVE POSITION = "
        + (
            "PASS"
            if test3_pass
            else "FAIL"
        )
        + " RESULT="
        + str(test3)
    )

    # --------------------------------------------------------
    # TEST 4
    # Exposure read failure
    # Expected: BLOCK / FAIL CLOSED
    # --------------------------------------------------------

    test4 = (
        r182_client_id_lifecycle_decision(
            candidate_client_id=historical_id,
            historical_client_ids=[
                historical_id,
            ],
            active_client_ids=[],
            history_read_ok=False,
            position_read_ok=True,
            active_positions=0,
            open_orders=0,
        )
    )

    test4_pass = (
        test4.get("allow") is False
        and test4.get("reason")
        == "HISTORY_READ_FAILED_FAIL_CLOSED"
    )

    log(
        "R1.8.2 TEST 4 "
        "READ FAILURE FAIL-CLOSED = "
        + (
            "PASS"
            if test4_pass
            else "FAIL"
        )
        + " RESULT="
        + str(test4)
    )

    # --------------------------------------------------------
    # TEST 5
    # Completely new ID + flat account
    # Expected: ALLOW
    # --------------------------------------------------------

    test5 = (
        r182_client_id_lifecycle_decision(
            candidate_client_id=(
                "R36F159-S-NEWOPPORTUNITY"
            ),
            historical_client_ids=[
                historical_id,
            ],
            active_client_ids=[],
            history_read_ok=True,
            position_read_ok=True,
            active_positions=0,
            open_orders=0,
        )
    )

    test5_pass = (
        test5.get("allow") is True
        and test5.get("reason")
        == "NEW_CLIENT_ID_AND_FLAT_ACCOUNT"
    )

    log(
        "R1.8.2 TEST 5 "
        "NEW ID + FLAT = "
        + (
            "PASS"
            if test5_pass
            else "FAIL"
        )
        + " RESULT="
        + str(test5)
    )

    overall_pass = all(
        [
            test1_pass,
            test2_pass,
            test3_pass,
            test4_pass,
            test5_pass,
        ]
    )

    log(
        "R1.8.2 ZERO-WRITE LIFECYCLE TEST = "
        + (
            "PASS"
            if overall_pass
            else "FAIL"
        )
    )

    log(
        "R1.8.2 WEEX POST = False"
    )

    log(
        "R1.8.2 JOURNAL WRITE = False"
    )

    log(
        "R1.8.2 REAL ORDER = False"
    )

    log(
        "R1.8.2 DEMO ORDER = False"
    )

    return overall_pass
def r36f159_is_open_order_status(
    status,
):
    value = str(
        status
        or ""
    ).strip().upper()

    return value in {
        "NEW",
        "PENDING",
        "OPEN",
        "CREATED",
        "PARTIALLY_FILLED",
        "PARTIAL_FILLED",
        "PARTIALLYFILLED",
        "PART_FILLED",
    }


async def r36f159_reconcile_current_demo_exposure():
    global R36F159_LAST_EXPOSURE_CHECK

    result = {
        "history_read_ok": False,
        "position_read_ok": False,
        "history_rows": 0,
        "position_rows": 0,
        "active_symbol_positions": 0,
        "open_symbol_orders": 0,
        "historical_filled_orders": 0,
        "existing_client_ids": [],        
        "active_client_ids": [],
        "duplicate_entry_blocked": True, 
        "duplicate_block_reason": "UNRESOLVED_CURRENT_DEMO_EXPOSURE",
        "safe_to_consider_new_entry": False,
    }

    line()

    log(
        "R36F.15.9 CURRENT DEMO EXPOSURE RECONCILIATION START"
    )

    try:
        history_data = await weex_get(
            R36F14_DEMO_ORDER_HISTORY_ENDPOINT,
            params={
                "symbol": R36F14_DEMO_SYMBOL,
                "limit": 1000,
                "page": 0,
            },
            authenticated=True,
        )
        r182_run_zero_write_tests()
        history_rows = (
            _r36f153_history_rows(
                history_data
            )
        )

        if history_rows is None:
            raise RuntimeError(
                "DEMO_HISTORY_RESPONSE_UNRECOGNIZED"
            )

        result[
            "history_read_ok"
        ] = True

        result[
            "history_rows"
        ] = len(
            history_rows
        )

        client_ids = []
        active_client_ids = []
        open_orders = 0
        filled_orders = 0

        for row in history_rows:
            if not isinstance(
                row,
                dict,
            ):
                continue

            symbol = str(
                row.get(
                    "symbol"
                )
                or ""
            ).strip().upper()

            if (
                symbol
                != R36F14_DEMO_SYMBOL
            ):
                continue

            client_id = str(
                row.get(
                    "clientOrderId"
                )
                or row.get(
                    "newClientOrderId"
                )
                or ""
            ).strip()

            if client_id:
                client_ids.append(
                    client_id
                )

            status = str(
                row.get(
                    "status"
                )
                or ""
            ).strip().upper()
        if r36f159_is_open_order_status(
                status
            ):
                open_orders += 1

                if client_id:
                    active_client_ids.append(
                        client_id
                    )

                if status == "FILLED":
                    filled_orders += 1
                result[
            "existing_client_ids"
        ] = sorted(
            set(
                client_ids
            )
        )

        result[
            "active_client_ids"
        ] = sorted(
            set(
                active_client_ids
            )
        )

        result[
            "open_symbol_orders"
        ] = open_orders
        

        result[
            "historical_filled_orders"
        ] = filled_orders

    except Exception as exc:
        result[
            "history_error"
        ] = str(
            exc
        )

    try:
        positions_data = await weex_get(
            R36F14_DEMO_POSITIONS_ENDPOINT,
            authenticated=True,
        )

        position_rows = (
            r36f155_normalize_rows(
                positions_data
            )
        )

        result[
            "position_read_ok"
        ] = True

        result[
            "position_rows"
        ] = len(
            position_rows
        )

        active_positions = 0
        active_position_row = None

        for row in position_rows:
            if not isinstance(row, dict):
                continue

            symbol = str(row.get("symbol") or "").strip().upper()
            if symbol and symbol != R36F14_DEMO_SYMBOL:
                continue

            position_size = r36f155_position_size(row)

            if position_size != 0:
                active_positions += 1

            if active_position_row is None:
                active_position_row = dict(row)

        result["active_symbol_positions"] = active_positions
        result["active_position_row"] = active_position_row
    
        # ====================================================
        # NB3 FRESH BACKUP RECONCILIATION BRIDGE
        # ZERO WEEX WRITES
        # ====================================================

        nb3_result = {
            "status": "IDLE",
            "reason": "NO_ACTIVE_POSITION",
            "position_row": None,
        }

        if active_position_row is None:

            print("NB3 STATUS = IDLE")
            print("NB3 REASON = NO_ACTIVE_POSITION")

        else:

            nb3_position_row = dict(active_position_row)
            nb3_position_size = r36f155_position_size(
                nb3_position_row
            )

            nb3_result = {
                "status": "POSITION_DETECTED",
                "reason": "ACTIVE_POSITION_RECONCILED",
                "position_row": nb3_position_row,
                "position_size": nb3_position_size,
            }

            print("NB3 STATUS = POSITION_DETECTED")
            print(
                "NB3 POSITION SIZE =",
                nb3_position_size
            )
            print(
                "NB3 POSITION ROW KEYS =",
                sorted(nb3_position_row.keys())
            )

        result["nb3"] = nb3_result

        print("NB3 ORDER WRITE = DISABLED")
           

    except Exception as exc:
        result[
            "position_error"
        ] = str(
            exc
        )

    if (
        not result[
            "history_read_ok"
        ]
        or not result[
            "position_read_ok"
        ]
    ):
        result[
            "duplicate_entry_blocked"
        ] = True

        result[
            "duplicate_block_reason"
        ] = (
            "CURRENT_EXPOSURE_READ_FAILED"
        )

    elif (
        result[
            "active_symbol_positions"
        ]
        > 0
    ):
        result[
            "duplicate_entry_blocked"
        ] = True

        result[
            "duplicate_block_reason"
        ] = (
            "ACTIVE_DEMO_POSITION_ALREADY_EXISTS"
        )

    elif (
        result[
            "open_symbol_orders"
        ]
        > 0
    ):
        result[
            "duplicate_entry_blocked"
        ] = True

        result[
            "duplicate_block_reason"
        ] = (
            "OPEN_DEMO_ORDER_ALREADY_EXISTS"
        )

    else:
        result[
            "duplicate_entry_blocked"
        ] = False

        result[
            "duplicate_block_reason"
        ] = (
            "NO_CURRENT_DEMO_EXPOSURE"
        )

        result[
            "safe_to_consider_new_entry"
        ] = True

    log(
        "R36F.15.9 HISTORY READ OK = "
        + str(
            result[
                "history_read_ok"
            ]
        )
    )

    log(
        "R36F.15.9 POSITION READ OK = "
        + str(
            result[
                "position_read_ok"
            ]
        )
    )

    log(
        "R36F.15.9 OPEN DEMO ORDERS = "
        + str(
            result[
                "open_symbol_orders"
            ]
        )
    )

    log(
        "R36F.15.9 ACTIVE DEMO POSITIONS = "
        + str(
            result[
                "active_symbol_positions"
            ]
        )
    )

    log(
        "R36F.15.9 DUPLICATE ENTRY BLOCKED = "
        + str(
            result[
                "duplicate_entry_blocked"
            ]
        )
    )

    R36F159_LAST_EXPOSURE_CHECK = (
        result
    )

    line()

    return result


async def r36f159_reconcile_second_demo_journal(
    journal,
):
    if (
        not isinstance(
            journal,
            dict,
        )
        or not journal
    ):
        return {
            "resolved": True,
            "retry_allowed": True,
            "reason": "NO_SECOND_DEMO_JOURNAL",
            "journal": {},
            "changed": False,
        }

    state = str(
        journal.get(
            "state"
        )
        or ""
    ).strip().upper()

    if state == "COMPLETED":
        return {
            "resolved": True,
            "retry_allowed": False,
            "reason": "SECOND_DEMO_ALREADY_COMPLETED",
            "journal": journal,
            "changed": False,
        }

    if state == "REJECTED":
        return {
            "resolved": True,
            "retry_allowed": False,
            "reason": "SECOND_DEMO_TOKEN_ALREADY_CONSUMED_REQUIRES_NEW_STAGE",
            "journal": journal,
            "changed": False,
        }

    if state not in {
        "PREPARED",
        "SENT_AMBIGUOUS",
    }:
        return {
            "resolved": False,
            "retry_allowed": False,
            "reason": "UNKNOWN_SECOND_DEMO_JOURNAL_STATE",
            "journal": journal,
            "changed": False,
        }

    client_order_id = str(
        journal.get(
            "client_order_id"
        )
        or ""
    ).strip()

    if client_order_id in set(
        exposure.get(
            "active_client_ids",
            [],
        )
    ):
        return {
            "attempted": False,
            "sent": False,
            "accepted": False,
            "reason": "R36F159_ACTIVE_CLIENT_ORDER_ID_ALREADY_EXISTS",
            "client_order_id": client_order_id,
        }
    
    lookup_status = (
        lookup.get(
            "status"
        )
    )

    if lookup_status == "FOUND":
        order = (
            lookup.get(
                "order"
            )
            if isinstance(
                lookup.get(
                    "order"
                ),
                dict,
            )
            else {}
        )

        reconciled = {
            **journal,
            "state": "COMPLETED",
            "updated_at": now_iso(),
            "success": True,
            "reconciliation_status": "FOUND",
            "reconciliation_reason": lookup.get(
                "reason"
            ),
            "order_id": str(
                order.get(
                    "orderId",
                    journal.get(
                        "order_id",
                        "",
                    ),
                )
            ),
            "client_order_id_response": str(
                order.get(
                    "clientOrderId",
                    client_order_id,
                )
            ),
            "reconciled_order": order,
        }

        write_json_file(
            R36F159_DEMO_JOURNAL_FILE,
            reconciled,
        )

        return {
            "resolved": True,
            "retry_allowed": False,
            "reason": "SECOND_DEMO_FOUND_MARKED_COMPLETED",
            "journal": reconciled,
            "changed": True,
        }

    if lookup_status == "NOT_FOUND":
        return {
            "resolved": True,
            "retry_allowed": False,
            "reason": "SECOND_DEMO_PREPARED_NOT_FOUND_TOKEN_REPLAY_BLOCKED",
            "journal": journal,
            "changed": False,
        }

    return {
        "resolved": False,
        "retry_allowed": False,
        "reason": lookup.get(
            "reason",
            "SECOND_DEMO_RECONCILIATION_UNKNOWN",
        ),
        "journal": journal,
        "lookup": lookup,
        "changed": False,
    }


# ============================================================
# R1.8 CORRECTED MAIN.PY — PART 1 END
# ============================================================# ============================================================
# R1.8 CORRECTED MAIN.PY — PART 2 START
# ============================================================

async def submit_r36f15_demo_order(
    preview,
    command_preview,
):
    if not R36F159_DEMO_ARM_REQUESTED:
        return {
            "attempted": False,
            "sent": False,
            "reason": "SECOND_DEMO_ARM_NOT_REQUESTED",
        }

    if not command_preview.get(
        "authorized_preview"
    ):
        return {
            "attempted": False,
            "sent": False,
            "reason": "TELEGRAM_COMMAND_NOT_AUTHORIZED",
        }

    if (
        not preview
        or not preview.get("payload")
    ):
        return {
            "attempted": False,
            "sent": False,
            "reason": "DEMO_PREVIEW_MISSING",
        }

    if not R36F159_COMMAND_TOKEN:
        return {
            "attempted": False,
            "sent": False,
            "reason": "SECOND_DEMO_COMMAND_TOKEN_MISSING",
        }

    existing = read_json_file(
        R36F159_DEMO_JOURNAL_FILE,
        default={},
    )

    command_identity = (
        r36f159_command_identity(
            command_preview
        )
    )

    if isinstance(existing, dict) and existing:
        existing_identity = str(
            existing.get(
                "command_identity_sha256"
            ) or ""
        ).strip()

        if (
            existing_identity
            and hmac.compare_digest(
                existing_identity,
                command_identity,
            )
        ):
            reconciliation = (
                await r36f159_reconcile_second_demo_journal(
                    existing
                )
            )

            return {
                "attempted": False,
                "sent": False,
                "accepted": False,
                "reason": "R36F159_COMMAND_REPLAY_BLOCKED",
                "reconciliation": reconciliation,
                "journal": reconciliation.get(
                    "journal",
                    existing,
                ),
            }

        existing_state = str(
            existing.get(
                "state",
                "",
            )
        ).strip().upper()

        if existing_state != "COMPLETED":
            return {
                "attempted": False,
                "sent": False,
                "accepted": False,
                "reason": "R36F159_EXISTING_SECOND_DEMO_JOURNAL_BLOCKS_NEW_TOKEN",
                "journal": existing,
            }

        log(
            "R36F.15.9 COMPLETED OLD JOURNAL "
            "DOES NOT BLOCK NEW COMMAND TOKEN"
        ) 

    exposure = (
        await r36f159_reconcile_current_demo_exposure()
    )

    if exposure.get(
        "duplicate_entry_blocked",
        True,
    ):
        return {
            "attempted": False,
            "sent": False,
            "accepted": False,
            "reason": "R36F159_CURRENT_EXPOSURE_BLOCKED",
            "duplicate_block_reason": exposure.get(
                "duplicate_block_reason"
            ),
            "exposure": exposure,
        }

    payload = dict(
        preview["payload"]
    )

    client_order_id = (
        r36f159_client_order_id(
            command_preview
        )
    )
    # ============================================================
    # R1.8.1 READ-ONLY CLIENT ORDER ID DIAGNOSTIC
    # NO STATE CHANGE / NO JOURNAL CHANGE / NO ORDER SUBMISSION
    # ============================================================

    r181_existing_client_ids = list(
        exposure.get(
            "existing_client_ids",
            [],
        )
        or []
    )

    r181_candidate_exists = (
        client_order_id
        in set(r181_existing_client_ids)
    )

    r181_old_journal = (
        read_json_file(
            R36F159_DEMO_JOURNAL_FILE
        )
        or {}
    )

    r181_old_client_order_id = str(
        r181_old_journal.get(
            "client_order_id"
        )
        or ""
    )

    r181_old_command_identity = str(
        r181_old_journal.get(
            "command_identity_sha256"
        )
        or ""
    )

    r181_old_command_token = str(
        r181_old_journal.get(
            "command_token_sha256"
        )
        or ""
    )

    r181_new_command_token = (
        sha256_text(
            R36F159_COMMAND_TOKEN
        )
    )

    log(
        "R1.8.1 DIAGNOSTIC START"
    )

    log(
        "R1.8.1 CANDIDATE CLIENT ORDER ID = "
        + str(client_order_id)
    )

    log(
        "R1.8.1 EXISTING CLIENT IDS = "
        + canonical_json(
            r181_existing_client_ids
        )
    )

    log(
        "R1.8.1 CANDIDATE EXISTS = "
        + str(r181_candidate_exists)
    )

    log(
        "R1.8.1 OLD JOURNAL STATE = "
        + str(
            r181_old_journal.get(
                "state"
            )
        )
    )

    log(
        "R1.8.1 OLD DIRECTION = "
        + str(
            r181_old_journal.get(
                "direction"
            )
        )
    )

    log(
        "R1.8.1 OLD ORDER ID = "
        + str(
            r181_old_journal.get(
                "order_id"
            )
            or r181_old_journal.get(
                "demo_order_id"
            )
        )
    )

    log(
        "R1.8.1 OLD CLIENT ORDER ID = "
        + r181_old_client_order_id
    )

    log(
        "R1.8.1 SAME CLIENT ORDER ID = "
        + str(
            r181_old_client_order_id
            == str(client_order_id)
        )
    )

    log(
        "R1.8.1 OLD COMMAND IDENTITY = "
        + r181_old_command_identity
    )

    log(
        "R1.8.1 NEW COMMAND IDENTITY = "
        + str(command_identity)
    )

    log(
        "R1.8.1 SAME COMMAND IDENTITY = "
        + str(
            r181_old_command_identity
            == str(command_identity)
        )
    )

    log(
        "R1.8.1 OLD COMMAND TOKEN = "
        + r181_old_command_token
    )

    log(
        "R1.8.1 NEW COMMAND TOKEN = "
        + r181_new_command_token
    )

    log(
        "R1.8.1 SAME COMMAND TOKEN = "
        + str(
            r181_old_command_token
            == r181_new_command_token
        )
    )

    log(
        "R1.8.1 OPEN DEMO ORDERS = "
        + str(
            exposure.get(
                "open_demo_orders",
                exposure.get(
                    "open_orders",
                    "UNKNOWN",
                ),
            )
        )
    )

    log(
        "R1.8.1 ACTIVE DEMO POSITIONS = "
        + str(
            exposure.get(
                "active_demo_positions",
                exposure.get(
                    "active_positions",
                    "UNKNOWN",
                ),
            )
        )
    )

    log(
        "R1.8.1 DUPLICATE CONDITION RESULT = "
        + str(r181_candidate_exists)
    )

    log(
        "R1.8.1 READ-ONLY DIAGNOSTIC COMPLETE"
    )
    if client_order_id in set(
        exposure.get(
            "existing_client_ids",
            [],
        )
    ):
        return {
            "attempted": False,
            "sent": False,
            "accepted": False,
            "reason": "R36F159_CLIENT_ORDER_ID_ALREADY_EXISTS",
            "client_order_id": client_order_id,
        }

    payload[
        "newClientOrderId"
    ] = client_order_id

    jit_validation = (
        await r36f154_validate_fresh_demo_triggers(
            payload
        )
    )

    log(
        "R36F.15.9 JIT DEMO TRIGGER VALIDATION = "
        + canonical_json(
            jit_validation
        )
    )

    if not jit_validation.get("valid"):
        return {
            "attempted": False,
            "sent": False,
            "accepted": False,
            "reason": "JIT_DEMO_TRIGGER_VALIDATION_BLOCKED",
            "jit_validation": jit_validation,
        }

    payload_hash = sha256_text(
        canonical_json(payload)
    )

    prepared = {
        "stage": STAGE,
        "state": "PREPARED",
        "created_at": now_iso(),
        "endpoint": R36F14_DEMO_ORDER_ENDPOINT,
        "command": str(
            command_preview.get("command")
            or ""
        ),
        "direction": str(
            command_preview.get("direction")
            or ""
        ),
        "command_token_sha256": sha256_text(
            R36F159_COMMAND_TOKEN
        ),
        "command_identity_sha256": (
            command_identity
        ),
        "client_order_id": client_order_id,
        "payload_sha256": payload_hash,
        "payload": payload,
        "pre_post_journal_verified": True,
        "real_order_execution": (
            REAL_ORDER_EXECUTION
        ),
        "demo_only": True,
    }

    write_json_file(
        R36F159_DEMO_JOURNAL_FILE,
        prepared,
    )

    reloaded = read_json_file(
        R36F159_DEMO_JOURNAL_FILE,
        default={},
    )

    reload_payload_hash = sha256_text(
        canonical_json(
            reloaded.get(
                "payload",
                {},
            )
        )
    )

    pre_post_reload_match = bool(
        reloaded.get("client_order_id")
        == client_order_id
        and reloaded.get(
            "command_identity_sha256"
        )
        == command_identity
        and reloaded.get(
            "payload_sha256"
        )
        == payload_hash
        and hmac.compare_digest(
            reload_payload_hash,
            payload_hash,
        )
    )

    log(
        "R36F.15.9 PRE_POST_JOURNAL_WRITTEN = True"
    )
    log(
        "R36F.15.9 PRE_POST_JOURNAL_RELOAD_MATCH = "
        + str(pre_post_reload_match)
    )
    log(
        "R36F.15.9 CLIENT ORDER ID = "
        + client_order_id
    )

    if not pre_post_reload_match:
        return {
            "attempted": False,
            "sent": False,
            "accepted": False,
            "reason": "R36F159_PRE_POST_JOURNAL_VERIFICATION_FAILED",
            "journal": reloaded,
        }

    try:
        transport = await weex_demo_post(
            R36F14_DEMO_ORDER_ENDPOINT,
            payload,
        )

    except Exception as exc:
        ambiguous = {
            **prepared,
            "state": "SENT_AMBIGUOUS",
            "updated_at": now_iso(),
            "error": str(exc),
        }

        write_json_file(
            R36F159_DEMO_JOURNAL_FILE,
            ambiguous,
        )

        return {
            "attempted": True,
            "sent": False,
            "accepted": False,
            "reason": "SECOND_DEMO_POST_EXCEPTION_JOURNALED_AMBIGUOUS",
            "error": str(exc),
            "journal": ambiguous,
        }

    response = (
        transport.get("response")
        if isinstance(transport, dict)
        else {}
    )

    if not isinstance(response, dict):
        response = {}

    success = bool(
        response.get("success")
    )

    completed = {
        **prepared,
        "state": (
            "COMPLETED"
            if success
            else "REJECTED"
        ),
        "updated_at": now_iso(),
        "http_status": transport.get(
            "http_status"
        ),
        "response": response,
        "success": success,
        "order_id": str(
            response.get("orderId", "")
        ),
        "client_order_id_response": str(
            response.get(
                "clientOrderId",
                "",
            )
        ),
        "error_code": str(
            response.get(
                "errorCode",
                "",
            )
        ),
        "error_message": str(
            response.get(
                "errorMessage",
                "",
            )
        ),
    }

    write_json_file(
        R36F159_DEMO_JOURNAL_FILE,
        completed,
    )

    return {
        "attempted": True,
        "sent": True,
        "accepted": success,
        "transport": transport,
        "journal": completed,
    }


async def load_mark_price():
    global MARK_PRICE

    data = await weex_get(
        "/capi/v3/market/symbolPrice",
        params={
            "symbol": SYMBOL
        },
        authenticated=False,
    )

    candidates = []

    if isinstance(data, dict):
        for key in (
            "price",
            "markPrice",
            "lastPrice",
        ):
            if key in data:
                candidates.append(
                    data[key]
                )

        nested = data.get("data")

        if isinstance(nested, dict):
            for key in (
                "price",
                "markPrice",
                "lastPrice",
            ):
                if key in nested:
                    candidates.append(
                        nested[key]
                    )

    elif isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue

            for key in (
                "price",
                "markPrice",
                "lastPrice",
            ):
                if key in item:
                    candidates.append(
                        item[key]
                    )

    for candidate in candidates:
        try:
            MARK_PRICE = D(candidate)

            if MARK_PRICE > 0:
                log(
                    "MARK PRICE = "
                    + decimal_to_string(
                        MARK_PRICE
                    )
                )
                return MARK_PRICE

        except Exception:
            continue

    raise RuntimeError(
        "Unable to determine WEEX mark price"
    )


async def load_available_balance():
    global AVAILABLE_BALANCE

    data = await weex_get(
        "/capi/v3/account/balance",
        authenticated=True,
    )

    candidates = []

    def collect(value):
        if isinstance(value, dict):
            for key, item in value.items():
                key_lower = key.lower()

                if key_lower in (
                    "availablebalance",
                    "available_balance",
                    "available",
                    "free",
                    "usdtavailable",
                ):
                    candidates.append(item)

                collect(item)

        elif isinstance(value, list):
            for item in value:
                collect(item)

    collect(data)

    for candidate in candidates:
        try:
            value = D(candidate)

            if value >= 0:
                AVAILABLE_BALANCE = value

                log(
                    "AVAILABLE BALANCE = "
                    + decimal_to_string(
                        AVAILABLE_BALANCE
                    )
                )

                return AVAILABLE_BALANCE

        except Exception:
            continue

    raise RuntimeError(
        "Unable to determine WEEX available balance"
    )

async def load_open_positions():
    global OPEN_POSITIONS

    data = await weex_get(
        R36F14_DEMO_POSITIONS_ENDPOINT,
        authenticated=True,
    )

    rows = r36f155_normalize_rows(
        data
    )

    OPEN_POSITIONS = rows

    log(
        "OPEN POSITION ROWS = "
        + str(
            len(
                OPEN_POSITIONS
            )
        )
    )

    return OPEN_POSITIONS


    log(
        "OPEN POSITION ROWS = "
        + str(
            len(
                OPEN_POSITIONS
            )
        )
    )

    return OPEN_POSITIONS


async def load_exchange_config():
    global WEEX_CONFIG

    WEEX_CONFIG = {
        "symbol": SYMBOL,
        "margin_mode": MARGIN_MODE,
        "target_long_leverage": decimal_to_string(
            LEVERAGE_LONG
        ),
        "target_short_leverage": decimal_to_string(
            LEVERAGE_SHORT
        ),
        "price_step": decimal_to_string(
            PRICE_STEP
        ),
        "quantity_step": decimal_to_string(
            QUANTITY_STEP
        ),
        "min_quantity": decimal_to_string(
            MIN_QUANTITY
        ),
    }

    return WEEX_CONFIG


async def reconcile_weex():
    global WEEX_READ_ONLY_OK

    try:
        await load_mark_price()
        await load_available_balance()
        await load_open_positions()
        await load_exchange_config()

        WEEX_READ_ONLY_OK = True

        log(
            "WEEX READ-ONLY RECONCILIATION = PASS"
        )

        return True

    except Exception as exc:
        WEEX_READ_ONLY_OK = False

        log(
            "WEEX READ-ONLY RECONCILIATION = FAIL "
            + str(exc)
        )

        return False


async def load_historical_klines():
    rows = []

    for page in range(
        MAX_HISTORICAL_PAGES
    ):
        data = await weex_get(
            "/capi/v2/market/candles",
            params={
                "symbol": PUBLIC_TICKER_SYMBOL,
                "granularity": KLINE_INTERVAL,
                "limit": HISTORICAL_LIMIT,
                "page": page,
            },
            authenticated=False,
        )

        page_rows = []

        if isinstance(data, list):
            page_rows = data

        elif isinstance(data, dict):
            for key in (
                "data",
                "rows",
                "list",
            ):
                value = data.get(key)

                if isinstance(value, list):
                    page_rows = value
                    break

        if not page_rows:
            break

        rows.extend(
            page_rows
        )

        if len(page_rows) < HISTORICAL_LIMIT:
            break

    if not rows:
        raise RuntimeError(
            "No historical klines returned"
        )

    log(
        "HISTORICAL KLINES = "
        + str(len(rows))
    )

    return rows


def candle_high(row):
    if isinstance(row, dict):
        for key in (
            "high",
            "h",
        ):
            if key in row:
                return D(
                    row[key]
                )

    if isinstance(row, (list, tuple)):
        if len(row) >= 3:
            return D(
                row[2]
            )

    raise ValueError(
        "Unable to read candle high"
    )
def candle_low(row):
    if isinstance(row, dict):
        for key in (
            "low",
            "l",
        ):
            if key in row:
                return D(
                    row[key]
                )

    if isinstance(row, (list, tuple)):
        if len(row) >= 4:
            return D(
                row[3]
            )

    raise ValueError(
        "Unable to read candle low"
    )


def historical_highs(rows):
    return [
        candle_high(row)
        for row in rows
    ]


def historical_lows(rows):
    return [
        candle_low(row)
        for row in rows
    ]


def candle_close(row):
    if isinstance(row, dict):
        for key in (
            "close",
            "c",
        ):
            if key in row:
                return D(
                    row[key]
                )

    if isinstance(row, (list, tuple)):
        if len(row) >= 5:
            return D(
                row[4]
            )

    raise ValueError(
        "Unable to read candle close"
    )


def candle_timestamp(row):
    if isinstance(row, dict):
        for key in (
            "timestamp",
            "time",
            "ts",
            "openTime",
        ):
            if key in row:
                return D(
                    row[key]
                )

    if isinstance(row, (list, tuple)):
        if len(row) >= 1:
            return D(
                row[0]
            )

    raise ValueError(
        "Unable to read candle timestamp"
    )


def chronological_rows(rows):
    parsed = []

    for row in rows:
        try:
            timestamp = candle_timestamp(
                row
            )

            close = candle_close(
                row
            )

            parsed.append(
                (
                    timestamp,
                    close,
                    row,
                )
            )

        except Exception:
            continue

    if not parsed:
        raise RuntimeError(
            "No usable historical candles"
        )

    parsed.sort(
        key=lambda item: item[0]
    )

    deduped = {}

    for timestamp, close, row in parsed:
        deduped[timestamp] = (
            close,
            row,
        )

    return [
        (
            timestamp,
            deduped[timestamp][0],
            deduped[timestamp][1],
        )
        for timestamp in sorted(
            deduped
        )
    ]


def ema_series(
    values,
    period,
):
    values = [
        D(value)
        for value in values
    ]

    if not values:
        raise ValueError(
            "EMA values missing"
        )

    multiplier = (
        Decimal("2")
        / Decimal(
            period + 1
        )
    )

    current = values[0]
    result = [current]

    for value in values[1:]:
        current = (
            (
                value - current
            )
            * multiplier
            + current
        )

        result.append(
            current
        )

    return result


def calculate_emas(closes):
    if len(closes) < EMA_SLOW:
        raise ValueError(
            "Not enough candles for EMA200"
        )

    ema19 = ema_series(
        closes,
        EMA_FAST,
    )

    ema50 = ema_series(
        closes,
        EMA_MID,
    )

    ema200 = ema_series(
        closes,
        EMA_SLOW,
    )

    return (
        ema19,
        ema50,
        ema200,
    )


def ema_structure(
    price,
    ema19,
    ema50,
    ema200,
):
    price = D(price)
    ema19 = D(ema19)
    ema50 = D(ema50)
    ema200 = D(ema200)

    if (
        price > ema19
        and ema19 > ema50
        and ema50 > ema200
    ):
        return "STRONG_BULLISH"

    if (
        price < ema19
        and ema19 < ema50
        and ema50 < ema200
    ):
        return "STRONG_BEARISH"

    if (
        ema19 > ema50
        and ema50 > ema200
    ):
        return "EARLY_BULLISH"

    if (
        ema19 < ema50
        and ema50 < ema200
    ):
        return "EARLY_BEARISH"

    return "MIXED"


def ema_direction(structure):
    if structure == "STRONG_BULLISH":
        return "LONG"

    if structure == "STRONG_BEARISH":
        return "SHORT"

    return None


def ema_separation_percent(
    ema19,
    ema50,
):
    ema19 = D(ema19)
    ema50 = D(ema50)

    if ema50 == 0:
        return Decimal("0")

    return (
        abs(
            ema19 - ema50
        )
        / ema50
        * Decimal("100")
    )


def detect_ema19_50_crossover(
    ema19_series,
    ema50_series,
):
    if (
        len(ema19_series) < 2
        or len(ema50_series) < 2
    ):
        return None

    previous_fast = ema19_series[-2]
    previous_mid = ema50_series[-2]
    current_fast = ema19_series[-1]
    current_mid = ema50_series[-1]

    if (
        previous_fast <= previous_mid
        and current_fast > current_mid
    ):
        return "BULLISH_CROSS"

    if (
        previous_fast >= previous_mid
        and current_fast < current_mid
    ):
        return "BEARISH_CROSS"

    return None


def build_ema_signal_snapshot(rows):
    ordered = chronological_rows(
        rows
    )

    closes = [
        item[1]
        for item in ordered
    ]

    (
        ema19_series,
        ema50_series,
        ema200_series,
    ) = calculate_emas(
        closes
    )

    price = closes[-1]
    ema19 = ema19_series[-1]
    ema50 = ema50_series[-1]
    ema200 = ema200_series[-1]

    structure = ema_structure(
        price,
        ema19,
        ema50,
        ema200,
    )

    direction = ema_direction(
        structure
    )

    separation = ema_separation_percent(
        ema19,
        ema50,
    )

    crossover = detect_ema19_50_crossover(
        ema19_series,
        ema50_series,
    )

    strong_enough = (
        separation
        >= MIN_EMA_19_50_SEPARATION_PERCENT
    )

    if (
        direction is not None
        and not strong_enough
    ):
        direction = None

    snapshot = {
        "price": decimal_to_string(
            price
        ),
        "ema19": decimal_to_string(
            ema19
        ),
        "ema50": decimal_to_string(
            ema50
        ),
        "ema200": decimal_to_string(
            ema200
        ),
        "structure": structure,
        "ideal_direction": direction,
        "ema19_50_separation_percent": decimal_to_string(
            separation
        ),
        "minimum_required_separation_percent": decimal_to_string(
            MIN_EMA_19_50_SEPARATION_PERCENT
        ),
        "crossover": crossover,
        "candle_count": len(
            closes
        ),
    }

    return snapshot


def normalize_telegram_command(text):
    return " ".join(
        str(
            text
            or ""
        )
        .strip()
        .upper()
        .split()
    )


def parse_telegram_trade_command(text):
    normalized = normalize_telegram_command(
        text
    )

    if normalized == TELEGRAM_BUY_COMMAND:
        return {
            "valid": True,
            "command": normalized,
            "direction": "LONG",
        }

    if normalized == TELEGRAM_SELL_COMMAND:
        return {
            "valid": True,
            "command": normalized,
            "direction": "SHORT",
        }

    return {
        "valid": False,
        "command": normalized,
        "direction": None,
    }


def validate_telegram_command_against_signal(
    command_text,
    signal_snapshot,
    long_market_eligible,
    short_market_eligible,
):
    parsed = parse_telegram_trade_command(
        command_text
    )

    result = {
        **parsed,
        "authorized_preview": False,
        "reason": None,
    }

    if not parsed["valid"]:
        result["reason"] = (
            "INVALID_TELEGRAM_COMMAND"
        )
        return result

    direction = parsed["direction"]

    ideal_direction = (
        signal_snapshot.get(
            "ideal_direction"
        )
    )

    if direction != ideal_direction:
        result["reason"] = (
            "COMMAND_DOES_NOT_MATCH_EMA_DIRECTION"
        )
        return result

    if (
        direction == "LONG"
        and not long_market_eligible
    ):
        result["reason"] = (
            "LONG_MARKET_NOT_ELIGIBLE"
        )
        return result

    if (
        direction == "SHORT"
        and not short_market_eligible
    ):
        result["reason"] = (
            "SHORT_MARKET_NOT_ELIGIBLE"
        )
        return result

    result["authorized_preview"] = True
    result["reason"] = (
        "COMMAND_MATCHES_SIGNAL_AND_MARKET"
    )

    return result


def build_ideal_condition_alert(
    signal_snapshot,
):
    direction = signal_snapshot.get(
        "ideal_direction"
    )

    if direction == "LONG":
        command = TELEGRAM_BUY_COMMAND

    elif direction == "SHORT":
        command = TELEGRAM_SELL_COMMAND

    else:
        return None

    return (
        f"{STAGE} IDEAL {direction} CONDITION | "
        f"{SYMBOL}\n"
        f"Price={signal_snapshot.get('price')} "
        f"EMA19={signal_snapshot.get('ema19')} "
        f"EMA50={signal_snapshot.get('ema50')} "
        f"EMA200={signal_snapshot.get('ema200')}\n"
        f"Structure={signal_snapshot.get('structure')} "
        f"EMA19/50 separation="
        f"{signal_snapshot.get('ema19_50_separation_percent')}%\n"
        f"Manual command: {command}\n"
        f"{STAGE} exchange execution remains disabled."
    )


async def send_r36f12_telegram_alert(
    message,
):
    if not R36F12_TELEGRAM_ALERTS_ENABLED:
        return {
            "sent": False,
            "reason": "TELEGRAM_ALERTS_DISABLED",
        }

    if not TELEGRAM_BOT_TOKEN:
        return {
            "sent": False,
            "reason": "TELEGRAM_BOT_TOKEN_MISSING",
        }

    if not TELEGRAM_CHAT_ID:
        return {
            "sent": False,
            "reason": "TELEGRAM_CHAT_ID_MISSING",
        }

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    try:
        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.post(
                url,
                json=payload,
            ) as response:

                text = (
                    await response.text()
                )

                return {
                    "sent": (
                        response.status < 400
                    ),
                    "status": response.status,
                    "response": text,
                }

    except Exception as exc:
        return {
            "sent": False,
            "reason": "TELEGRAM_SEND_EXCEPTION",
            "error": str(exc),
        }


def r36f1541_classify_demo_event(
    demo_result,
):
    demo_result = (
        demo_result
        if isinstance(
            demo_result,
            dict,
        )
        else {}
    )

    reason = str(
        demo_result.get(
            "reason"
        )
        or ""
    ).strip()

    attempted = bool(
        demo_result.get(
            "attempted",
            False,
        )
    )

    sent = bool(
        demo_result.get(
            "sent",
            False,
        )
    )

    accepted = bool(
        demo_result.get(
            "accepted",
            False,
        )
    )

    if (
        attempted
        and sent
        and accepted
    ):
        return (
            "ORDER_ACCEPTED",
            "WEEX DEMO ORDER ACCEPTED",
        )

    if (
        attempted
        and sent
        and not accepted
    ):
        return (
            "ORDER_REJECTED",
            "WEEX DEMO ORDER REJECTED",
        )

    if reason == (
        "JIT_DEMO_TRIGGER_VALIDATION_BLOCKED"
    ):
        return (
            "JIT_BLOCKED",
            "DEMO ORDER BLOCKED BY JIT TRIGGER VALIDATION",
        )

    if reason == (
        "R36F159_CURRENT_EXPOSURE_BLOCKED"
    ):
        return (
            "EXPOSURE_BLOCKED",
            "DEMO ORDER BLOCKED BY EXISTING EXPOSURE",
        )

    if reason == (
        "R36F159_COMMAND_REPLAY_BLOCKED"
    ):
        return (
            "REPLAY_BLOCKED",
            "DEMO COMMAND REPLAY BLOCKED",
        )

    if reason == (
        "SECOND_DEMO_ARM_NOT_REQUESTED"
    ):
        return (
            "ARM_NOT_REQUESTED",
            "SECOND DEMO ARM NOT REQUESTED",
        )

    if reason:
        return (
            "DEMO_NOT_SENT",
            "DEMO ORDER NOT SENT",
        )

    return (
        "NO_DEMO_EVENT",
        "NO DEMO ORDER EVENT",
    )


def r36f1541_build_event_message(
    event_code,
    event_title,
    demo_result,
    command_preview,
    signal_snapshot,
):
    demo_result = (
        demo_result
        if isinstance(
            demo_result,
            dict,
        )
        else {}
    )

    command_preview = (
        command_preview
        if isinstance(
            command_preview,
            dict,
        )
        else {}
    )

    signal_snapshot = (
        signal_snapshot
        if isinstance(
            signal_snapshot,
            dict,
        )
        else {}
    )

    lines = [
        f"{STAGE} | {event_title}",
        f"Event={event_code}",
        (
            "Direction="
            + str(
                command_preview.get(
                    "direction"
                )
                or signal_snapshot.get(
                    "ideal_direction"
                )
                or "NONE"
            )
        ),
        (
            "Command="
            + str(
                command_preview.get(
                    "command"
                )
                or "NONE"
            )
        ),
        (
            "Reason="
            + str(
                demo_result.get(
                    "reason"
                )
                or "NONE"
            )
        ),
        (
            "Attempted="
            + str(
                bool(
                    demo_result.get(
                        "attempted",
                        False,
                    )
                )
            )
        ),
        (
            "Sent="
            + str(
                bool(
                    demo_result.get(
                        "sent",
                        False,
                    )
                )
            )
        ),
        (
            "Accepted="
            + str(
                bool(
                    demo_result.get(
                        "accepted",
                        False,
                    )
                )
            )
        ),
        (
            "Price="
            + str(
                signal_snapshot.get(
                    "price"
                )
                or "UNKNOWN"
            )
        ),
    ]

    journal = demo_result.get(
        "journal"
    )

    if isinstance(journal, dict):
        order_id = str(
            journal.get(
                "order_id"
            )
            or ""
        ).strip()

        client_order_id = str(
            journal.get(
                "client_order_id"
            )
            or journal.get(
                "client_order_id_response"
            )
            or ""
        ).strip()

        if order_id:
            lines.append(
                "OrderID="
                + order_id
            )

        if client_order_id:
            lines.append(
                "ClientOrderID="
                + client_order_id
            )

    duplicate_reason = str(
        demo_result.get(
            "duplicate_block_reason"
        )
        or ""
    ).strip()

    if duplicate_reason:
        lines.append(
            "ExposureReason="
            + duplicate_reason
        )

    jit_validation = demo_result.get(
        "jit_validation"
    )

    if isinstance(
        jit_validation,
        dict,
    ):
        lines.append(
            "JIT="
            + str(
                jit_validation.get(
                    "reason"
                )
                or "UNKNOWN"
            )
        )

    lines.append(
        "REAL_ORDER_EXECUTION="
        + str(
            REAL_ORDER_EXECUTION
        )
    )

    return "\n".join(
        lines
    )


async def send_r36f1541_state_change_alert(
    demo_result,
    command_preview,
    signal_snapshot,
):
    if not (
        R36F1541_ROUTINE_TELEGRAM_ALERTS_ENABLED
    ):
        return {
            "sent": False,
            "reason": (
                "R36F1541_ROUTINE_TELEGRAM_ALERTS_DISABLED"
            ),
        }

    (
        event_code,
        event_title,
    ) = r36f1541_classify_demo_event(
        demo_result
    )

    if event_code in {
        "NO_DEMO_EVENT",
        "ARM_NOT_REQUESTED",
    }:
        return {
            "sent": False,
            "reason": (
                "R36F1541_EVENT_NOT_ALERTABLE"
            ),
            "event_code": event_code,
        }

    state = read_json_file(
        R36F1541_TELEGRAM_EVENT_STATE_FILE,
        default={},
    )

    current_identity = sha256_text(
        canonical_json(
            {
                "event_code": event_code,
                "reason": (
                    demo_result.get(
                        "reason"
                    )
                    if isinstance(
                        demo_result,
                        dict,
                    )
                    else None
                ),
                "direction": (
                    command_preview.get(
                        "direction"
                    )
                    if isinstance(
                        command_preview,
                        dict,
                    )
                    else None
                ),
                "accepted": (
                    demo_result.get(
                        "accepted"
                    )
                    if isinstance(
                        demo_result,
                        dict,
                    )
                    else None
                ),
            }
        )
    )

    previous_identity = str(
        state.get(
            "event_identity"
        )
        or ""
    ).strip()

    if (
        previous_identity
        and hmac.compare_digest(
            previous_identity,
            current_identity,
        )
    ):
        return {
            "sent": False,
            "reason": (
                "R36F1541_DUPLICATE_EVENT_SUPPRESSED"
            ),
            "event_code": event_code,
        }

    message = (
        r36f1541_build_event_message(
            event_code,
            event_title,
            demo_result,
            command_preview,
            signal_snapshot,
        )
    )

    result = (
        await send_r36f12_telegram_alert(
            message
        )
    )

    if result.get("sent"):
        write_json_file(
            R36F1541_TELEGRAM_EVENT_STATE_FILE,
            {
                "event_identity": (
                    current_identity
                ),
                "event_code": event_code,
                "updated_at": now_iso(),
            },
        )

    return {
        **result,
        "event_code": event_code,
        "event_title": event_title,
    }


def synthetic_r36f12_ema_telegram_tests():
    bullish = {
        "ideal_direction": "LONG"
    }

    bearish = {
        "ideal_direction": "SHORT"
    }

    no_direction = {
        "ideal_direction": None
    }

    cases = [
        (
            "BUY_MATCHES_LONG",
            TELEGRAM_BUY_COMMAND,
            bullish,
            True,
            False,
            True,
        ),
        (
            "SELL_MATCHES_SHORT",
            TELEGRAM_SELL_COMMAND,
            bearish,
            False,
            True,
            True,
        ),
        (
            "BUY_REJECTED_ON_SHORT",
            TELEGRAM_BUY_COMMAND,
            bearish,
            True,
            True,
            False,
        ),
        (
            "SELL_REJECTED_ON_LONG",
            TELEGRAM_SELL_COMMAND,
            bullish,
            True,
            True,
            False,
        ),
        (
            "NO_DIRECTION_REJECTS_BUY",
            TELEGRAM_BUY_COMMAND,
            no_direction,
            True,
            True,
            False,
        ),
    ]

    results = []

    for (
        name,
        command,
        signal,
        long_eligible,
        short_eligible,
        expected,
    ) in cases:

        result = (
            validate_telegram_command_against_signal(
                command,
                signal,
                long_eligible,
                short_eligible,
            )
        )

        passed = (
            result.get(
                "authorized_preview"
            )
            is expected
        )

        results.append(
            {
                "name": name,
                "passed": passed,
                "result": result,
            }
        )

    return results


# ============================================================
# HISTORICAL EXTREMA
# ============================================================

def build_extrema(values):
    values = [
        D(value)
        for value in values
    ]

    extrema = []

    if len(values) < 3:
        return extrema

    for index in range(
        1,
        len(values) - 1,
    ):
        previous_value = values[
            index - 1
        ]

        current_value = values[
            index
        ]

        next_value = values[
            index + 1
        ]

        if (
            current_value >= previous_value
            and current_value >= next_value
        ):
            extrema.append(
                current_value
            )

        elif (
            current_value <= previous_value
            and current_value <= next_value
        ):
            extrema.append(
                current_value
            )

    return extrema


def local_extrema_values(
    rows,
    side,
):
    if side == "LONG":
        values = historical_highs(
            rows
        )

    elif side == "SHORT":
        values = historical_lows(
            rows
        )

    else:
        raise ValueError(
            f"Unsupported side={side}"
        )

    return build_extrema(
        values
    )


# ============================================================
# CLUSTER EXTREMA
# ============================================================

def cluster_extrema(
    extrema,
):
    if not extrema:
        return []

    sorted_values = sorted(
        D(value)
        for value in extrema
    )

    clusters = []
    current = [
        sorted_values[0]
    ]

    for value in sorted_values[1:]:
        current_average = (
            sum(current)
            / Decimal(
                len(current)
            )
        )

        tolerance = (
            current_average
            * CLUSTER_TOLERANCE_PERCENT
            / Decimal("100")
        )

        if (
            abs(
                value
                - current_average
            )
            <= tolerance
        ):
            current.append(
                value
            )

        else:
            clusters.append(
                {
                    "minimum":
                        min(current),

                    "maximum":
                        max(current),

                    "average":
                        (
                            sum(current)
                            / Decimal(
                                len(current)
                            )
                        ),

                    "touches":
                        len(current),
                }
            )

            current = [
                value
            ]

    clusters.append(
        {
            "minimum":
                min(current),

            "maximum":
                max(current),

            "average":
                (
                    sum(current)
                    / Decimal(
                        len(current)
                    )
                ),

            "touches":
                len(current),
        }
    )

    return clusters


# ============================================================
# CLUSTER VALIDATION
# ============================================================

def validate_clusters(
    clusters,
    entry_price,
    side,
):
    entry_price = D(
        entry_price
    )

    valid = []
    invalid = []

    for cluster in clusters:
        reasons = []

        touches = cluster[
            "touches"
        ]

        average = D(
            cluster[
                "average"
            ]
        )

        if (
            touches
            < MIN_CLUSTER_TOUCHES
        ):
            reasons.append(
                "INSUFFICIENT_TOUCHES"
            )

        if side == "LONG":
            if average <= entry_price:
                reasons.append(
                    "CLUSTER_NOT_ABOVE_ENTRY"
                )

        elif side == "SHORT":
            if average >= entry_price:
                reasons.append(
                    "CLUSTER_NOT_BELOW_ENTRY"
                )

        else:
            reasons.append(
                "INVALID_DIRECTION"
            )

        result = dict(
            cluster
        )

        result["valid"] = (
            not reasons
        )

        result["reasons"] = (
            reasons
        )

        if reasons:
            invalid.append(
                result
            )

        else:
            valid.append(
                result
            )

    if side == "LONG":
        valid.sort(
            key=lambda item:
                item["average"]
        )

    elif side == "SHORT":
        valid.sort(
            key=lambda item:
                item["average"],
            reverse=True,
        )

    return (
        valid,
        invalid,
    )


# ============================================================
# R36F.15.10.1 CLUSTER DIAGNOSTICS
# ============================================================

R36F15101_TOLERANCE_GRID = (
    Decimal("0.05"),
    Decimal("0.10"),
    Decimal("0.15"),
    Decimal("0.20"),
    Decimal("0.25"),
    Decimal("0.30"),
)


def cluster_extrema_at_tolerance(
    extrema,
    tolerance_percent,
):
    tolerance_percent = D(
        tolerance_percent
    )

    if not extrema:
        return []

    sorted_values = sorted(
        D(value)
        for value in extrema
    )

    clusters = []
    current = [
        sorted_values[0]
    ]

    for value in sorted_values[1:]:
        current_average = (
            sum(current)
            / Decimal(
                len(current)
            )
        )

        tolerance = (
            current_average
            * tolerance_percent
            / Decimal("100")
        )

        if (
            abs(
                value
                - current_average
            )
            <= tolerance
        ):
            current.append(
                value
            )

        else:
            clusters.append(
                {
                    "minimum":
                        min(current),

                    "maximum":
                        max(current),

                    "average":
                        (
                            sum(current)
                            / Decimal(
                                len(current)
                            )
                        ),

                    "touches":
                        len(current),
                }
            )

            current = [
                value
            ]

    clusters.append(
        {
            "minimum":
                min(current),

            "maximum":
                max(current),

            "average":
                (
                    sum(current)
                    / Decimal(
                        len(current)
                    )
                ),

            "touches":
                len(current),
        }
    )

    return clusters


def r36f15101_side_distance_percent(
    entry_price,
    average,
    side,
):
    entry_price = D(
        entry_price
    )

    average = D(
        average
    )

    if entry_price <= 0:
        return None

    if side == "LONG":
        return (
            (
                average
                - entry_price
            )
            / entry_price
            * Decimal("100")
        )

    if side == "SHORT":
        return (
            (
                entry_price
                - average
            )
            / entry_price
            * Decimal("100")
        )

    return None


def r36f15101_cluster_span_percent(
    cluster,
):
    average = D(
        cluster["average"]
    )

    if average <= 0:
        return None

    return (
        (
            D(cluster["maximum"])
            - D(cluster["minimum"])
        )
        / average
        * Decimal("100")
    )


def r36f15101_tolerance_sweep(
    extrema,
    entry_price,
    side,
):
    results = []

    for tolerance_percent in (
        R36F15101_TOLERANCE_GRID
    ):
        clusters = (
            cluster_extrema_at_tolerance(
                extrema,
                tolerance_percent,
            )
        )

        valid, invalid = (
            validate_clusters(
                clusters,
                entry_price,
                side,
            )
        )

        results.append(
            {
                "tolerance_percent":
                    tolerance_percent,

                "cluster_count":
                    len(clusters),

                "valid_cluster_count":
                    len(valid),

                "invalid_cluster_count":
                    len(invalid),

                "approved_if_used":
                    (
                        len(valid)
                        >= REQUIRED_TP_CLUSTERS
                    ),
            }
        )

    return results


def build_cluster_diagnostics(
    rows,
    entry_price,
    side,
):
    entry_price = D(
        entry_price
    )

    if side == "LONG":
        values = historical_highs(
            rows
        )

    elif side == "SHORT":
        values = historical_lows(
            rows
        )

    else:
        raise ValueError(
            f"Unsupported side={side}"
        )

    extrema = build_extrema(
        values
    )

    clusters = cluster_extrema(
        extrema
    )

    valid, invalid = (
        validate_clusters(
            clusters,
            entry_price,
            side,
        )
    )

    diagnostics = {
        "side":
            side,

        "entry_price":
            decimal_to_string(
                entry_price
            ),

        "historical_row_count":
            len(rows),

        "extrema_count":
            len(extrema),

        "cluster_count":
            len(clusters),

        "valid_cluster_count":
            len(valid),

        "invalid_cluster_count":
            len(invalid),

        "required_valid_clusters":
            REQUIRED_TP_CLUSTERS,

        "valid_clusters":
            valid,

        "invalid_clusters":
            invalid,
    }

    if (
        len(valid)
        >= REQUIRED_TP_CLUSTERS
    ):
        diagnostics[
            "failure_reason"
        ] = None

    elif len(valid) == 1:
        diagnostics[
            "failure_reason"
        ] = (
            "ONLY_ONE_VALID_CLUSTER"
        )

    elif extrema:
        diagnostics[
            "failure_reason"
        ] = (
            "EXTREMA_EXIST_BUT_CLUSTER_REQUIREMENTS_NOT_MET"
        )

    else:
        diagnostics[
            "failure_reason"
        ] = (
            "NO_LOCAL_EXTREMA"
        )

    diagnostics[
        "tolerance_sweep"
    ] = r36f15101_tolerance_sweep(
        extrema,
        entry_price,
        side,
    )

    diagnostics[
        "valid_cluster_distances_percent"
    ] = [
        decimal_to_string(
            r36f15101_side_distance_percent(
                entry_price,
                item["average"],
                side,
            )
        )
        for item in valid
    ]

    diagnostics[
        "valid_cluster_spans_percent"
    ] = [
        decimal_to_string(
            r36f15101_cluster_span_percent(
                item
            )
        )
        for item in valid
    ]

    return diagnostics


# ============================================================
# R1.8 CORRECTED MAIN.PY — PART 2 END
# ============================================================# ============================================================
# R1.8 CORRECTED MAIN.PY — PART 3 START
# ============================================================

# ============================================================
# TP APPROVAL
# ============================================================

def evaluate_tp_approval(
    diagnostics,
):
    valid_count = int(
        diagnostics.get(
            "valid_cluster_count",
            0,
        )
    )

    if (
        valid_count
        >= REQUIRED_TP_CLUSTERS
    ):
        approval = {
            "status":
                "APPROVED",

            "approved":
                True,

            "required_valid_clusters":
                REQUIRED_TP_CLUSTERS,

            "available_valid_clusters":
                valid_count,

            "reason":
                "TWO_OR_MORE_VALID_HISTORICAL_CLUSTERS",
        }

    else:
        failure_reason = (
            diagnostics.get(
                "failure_reason"
            )
            or
            "INSUFFICIENT_VALID_HISTORICAL_CLUSTERS"
        )

        approval = {
            "status":
                "REJECTED",

            "approved":
                False,

            "required_valid_clusters":
                REQUIRED_TP_CLUSTERS,

            "available_valid_clusters":
                valid_count,

            "reason":
                failure_reason,
        }

    log(
        f"{STAGE}_TP_APPROVAL = "
        f"{approval['status']}"
    )

    log(
        f"{STAGE}_TP_APPROVAL_REASON = "
        f"{approval['reason']}"
    )

    log(
        f"{STAGE}_TP_REQUIRED_CLUSTERS = "
        f"{REQUIRED_TP_CLUSTERS}"
    )

    log(
        f"{STAGE}_TP_AVAILABLE_CLUSTERS = "
        f"{valid_count}"
    )

    return approval


# ============================================================
# VALID CLUSTERS
# ============================================================

def valid_clusters(
    rows,
    entry_price,
    side,
):
    entry_price = D(
        entry_price
    )

    extrema = local_extrema_values(
        rows,
        side,
    )

    clusters = cluster_extrema(
        extrema
    )

    valid = []

    for cluster in clusters:
        if (
            cluster["touches"]
            < MIN_CLUSTER_TOUCHES
        ):
            continue

        average = cluster[
            "average"
        ]

        if side == "LONG":
            if average <= entry_price:
                continue

        elif side == "SHORT":
            if average >= entry_price:
                continue

        else:
            raise ValueError(
                f"Unsupported side={side}"
            )

        valid.append(
            cluster
        )

    if side == "LONG":
        valid.sort(
            key=lambda c:
                c["average"]
        )

    else:
        valid.sort(
            key=lambda c:
                c["average"],
            reverse=True,
        )

    return valid


# ============================================================
# TP PRICE CALCULATION
# ============================================================

def calculate_tp_prices(
    entry_price,
    valid_cluster_list,
    direction,
):
    entry_price = D(
        entry_price
    )

    if (
        len(valid_cluster_list)
        < REQUIRED_TP_CLUSTERS
    ):
        raise RuntimeError(
            "Cannot calculate complete TP set: "
            "fewer than two valid historical clusters"
        )

    cluster1 = D(
        valid_cluster_list[
            0
        ]["average"]
    )

    cluster2 = D(
        valid_cluster_list[
            1
        ]["average"]
    )

    progress1 = (
        TP1_PROFIT_MARGIN_PERCENT
        / Decimal("100")
    )

    progress2 = (
        TP2_PROFIT_MARGIN_PERCENT
        / Decimal("100")
    )

    if direction == "LONG":
        tp1 = (
            entry_price
            + (
                cluster1
                - entry_price
            )
            * progress1
        )

        tp2 = (
            entry_price
            + (
                cluster2
                - entry_price
            )
            * progress2
        )

    elif direction == "SHORT":
        tp1 = (
            entry_price
            - (
                entry_price
                - cluster1
            )
            * progress1
        )

        tp2 = (
            entry_price
            - (
                entry_price
                - cluster2
            )
            * progress2
        )

    else:
        raise RuntimeError(
            "Invalid TP direction"
        )

    return {
        "tp1":
            quantize_down(
                tp1,
                PRICE_STEP,
            ),

        "tp2":
            quantize_down(
                tp2,
                PRICE_STEP,
            ),

        "tp3": {
            "type":
                "TRAILING",

            "allocation_percent":
                TP3_ALLOCATION_PERCENT,

            "trailing_distance_percent":
                TP3_TRAILING_DISTANCE_PERCENT,
        },

        "cluster1_average":
            cluster1,

        "cluster2_average":
            cluster2,```python
            (
                average
                - entry_price
            )
            / entry_price
            * Decimal("100")
        )

    if side == "SHORT":
        return (
            (
                entry_price
                - average
            )
            / entry_price
            * Decimal("100")
        )

    return None


def r36f15101_cluster_span_percent(
    cluster,
):
    average = D(
        cluster["average"]
    )

    if average <= 0:
        return None

    return (
        (
            D(cluster["maximum"])
            - D(cluster["minimum"])
        )
        / average
        * Decimal("100")
    )


def r36f15101_tolerance_sweep(
    extrema,
    entry_price,
    side,
):
    results = []

    for tolerance_percent in (
        R36F15101_TOLERANCE_GRID
    ):
        clusters = (
            cluster_extrema_at_tolerance(
                extrema,
                tolerance_percent,
            )
        )

        valid, invalid = (
            validate_clusters(
                clusters,
                entry_price,
                side,
            )
        )

        results.append(
            {
                "tolerance_percent":
                    tolerance_percent,

                "cluster_count":
                    len(clusters),

                "valid_cluster_count":
                    len(valid),

                "invalid_cluster_count":
                    len(invalid),

                "approved_if_used":
                    (
                        len(valid)
                        >= REQUIRED_TP_CLUSTERS
                    ),
            }
        )

    return results


def build_cluster_diagnostics(
    rows,
    entry_price,
    side,
):
    entry_price = D(
        entry_price
    )

    if side == "LONG":
        values = historical_highs(
            rows
        )

    elif side == "SHORT":
        values = historical_lows(
            rows
        )

    else:
        raise ValueError(
            f"Unsupported side={side}"
        )

    extrema = build_extrema(
        values
    )

    clusters = cluster_extrema(
        extrema
    )

    valid, invalid = (
        validate_clusters(
            clusters,
            entry_price,
            side,
        )
    )

    diagnostics = {
        "side":
            side,

        "entry_price":
            decimal_to_string(
                entry_price
            ),

        "historical_row_count":
            len(rows),

        "extrema_count":
            len(extrema),

        "cluster_count":
            len(clusters),

        "valid_cluster_count":
            len(valid),

        "invalid_cluster_count":
            len(invalid),

        "required_valid_clusters":
            REQUIRED_TP_CLUSTERS,

        "valid_clusters":
            valid,

        "invalid_clusters":
            invalid,
    }

    if (
        len(valid)
        >= REQUIRED_TP_CLUSTERS
    ):
        diagnostics[
            "failure_reason"
        ] = None

    elif len(valid) == 1:
        diagnostics[
            "failure_reason"
        ] = (
            "ONLY_ONE_VALID_CLUSTER"
        )

    elif extrema:
        diagnostics[
            "failure_reason"
        ] = (
            "EXTREMA_EXIST_BUT_CLUSTER_REQUIREMENTS_NOT_MET"
        )

    else:
        diagnostics[
            "failure_reason"
        ] = (
            "NO_LOCAL_EXTREMA"
        )

    diagnostics[
        "tolerance_sweep"
    ] = r36f15101_tolerance_sweep(
        extrema,
        entry_price,
        side,
    )

    diagnostics[
        "valid_cluster_distances_percent"
    ] = [
        decimal_to_string(
            r36f15101_side_distance_percent(
                entry_price,
                item["average"],
                side,
            )
        )
        for item in valid
    ]

    diagnostics[
        "valid_cluster_spans_percent"
    ] = [
        decimal_to_string(
            r36f15101_cluster_span_percent(
                item
            )
        )
        for item in valid
    ]

    return diagnostics


# ============================================================
# R1.8 CORRECTED MAIN.PY — PART 2 END
# ============================================================# ============================================================
# R1.8 CORRECTED MAIN.PY — PART 3 START
# ============================================================

# ============================================================
# TP APPROVAL
# ============================================================

def evaluate_tp_approval(
    diagnostics,
):
    valid_count = int(
        diagnostics.get(
            "valid_cluster_count",
            0,
        )
    )

    if (
        valid_count
        >= REQUIRED_TP_CLUSTERS
    ):
        approval = {
            "status":
                "APPROVED",

            "approved":
                True,

            "required_valid_clusters":
                REQUIRED_TP_CLUSTERS,

            "available_valid_clusters":
                valid_count,

            "reason":
                "TWO_OR_MORE_VALID_HISTORICAL_CLUSTERS",
        }

    else:
        failure_reason = (
            diagnostics.get(
                "failure_reason"
            )
            or
            "INSUFFICIENT_VALID_HISTORICAL_CLUSTERS"
        )

        approval = {
            "status":
                "REJECTED",

            "approved":
                False,

            "required_valid_clusters":
                REQUIRED_TP_CLUSTERS,

            "available_valid_clusters":
                valid_count,

            "reason":
                failure_reason,
        }

    log(
        f"{STAGE}_TP_APPROVAL = "
        f"{approval['status']}"
    )

    log(
        f"{STAGE}_TP_APPROVAL_REASON = "
        f"{approval['reason']}"
    )

    log(
        f"{STAGE}_TP_REQUIRED_CLUSTERS = "
        f"{REQUIRED_TP_CLUSTERS}"
    )

    log(
        f"{STAGE}_TP_AVAILABLE_CLUSTERS = "
        f"{valid_count}"
    )

    return approval


# ============================================================
# VALID CLUSTERS
# ============================================================

def valid_clusters(
    rows,
    entry_price,
    side,
):
    entry_price = D(
        entry_price
    )

    extrema = local_extrema_values(
        rows,
        side,
    )

    clusters = cluster_extrema(
        extrema
    )

    valid = []

    for cluster in clusters:
        if (
            cluster["touches"]
            < MIN_CLUSTER_TOUCHES
        ):
            continue

        average = cluster[
            "average"
        ]

        if side == "LONG":
            if average <= entry_price:
                continue

        elif side == "SHORT":
            if average >= entry_price:
                continue

        else:
            raise ValueError(
                f"Unsupported side={side}"
            )

        valid.append(
            cluster
        )

    if side == "LONG":
        valid.sort(
            key=lambda c:
                c["average"]
        )

    else:
        valid.sort(
            key=lambda c:
                c["average"],
            reverse=True,
        )

    return valid


# ============================================================
# TP PRICE CALCULATION
# ============================================================

def calculate_tp_prices(
    entry_price,
    valid_cluster_list,
    direction,
):
    entry_price = D(
        entry_price
    )

    if (
        len(valid_cluster_list)
        < REQUIRED_TP_CLUSTERS
    ):
        raise RuntimeError(
            "Cannot calculate complete TP set: "
            "fewer than two valid historical clusters"
        )

    cluster1 = D(
        valid_cluster_list[
            0
        ]["average"]
    )

    cluster2 = D(
        valid_cluster_list[
            1
        ]["average"]
    )

    progress1 = (
        TP1_PROFIT_MARGIN_PERCENT
        / Decimal("100")
    )

    progress2 = (
        TP2_PROFIT_MARGIN_PERCENT
        / Decimal("100")
    )

    if direction == "LONG":
        tp1 = (
            entry_price
            + (
                cluster1
                - entry_price
            )
            * progress1
        )

        tp2 = (
            entry_price
            + (
                cluster2
                - entry_price
            )
            * progress2
        )

    elif direction == "SHORT":
        tp1 = (
            entry_price
            - (
                entry_price
                - cluster1
            )
            * progress1
        )

        tp2 = (
            entry_price
            - (
                entry_price
                - cluster2
            )
            * progress2
        )

    else:
        raise RuntimeError(
            "Invalid TP direction"
        )

    return {
        "tp1":
            quantize_down(
                tp1,
                PRICE_STEP,
            ),

        "tp2":
            quantize_down(
                tp2,
                PRICE_STEP,
            ),

        "tp3": {
            "type":
                "TRAILING",

            "allocation_percent":
                TP3_ALLOCATION_PERCENT,

            "trailing_distance_percent":
                TP3_TRAILING_DISTANCE_PERCENT,
        },

        "cluster1_average":
            cluster1,

        "cluster2_average":
            cluster2,
    }


# ============================================================
# TP ENGINE
# ============================================================

def run_tp_engine(
    rows,
    entry_price,
    direction,
):
    if direction == "LONG":
        values = historical_highs(
            rows
        )

        extrema = build_extrema(
            values
        )

    elif direction == "SHORT":
        values = historical_lows(
            rows
        )

        extrema = build_extrema(
            values
        )

    else:
        raise RuntimeError(
            "Invalid direction"
        )

    clusters = cluster_extrema(
        extrema
    )

    valid, invalid = validate_clusters(
        clusters,
        entry_price,
        direction,
    )

    diagnostics = {
        "direction":
            direction,

        "entry_price":
            decimal_to_string(
                entry_price
            ),

        "extrema_count":
            len(extrema),

        "cluster_count":
            len(clusters),

        "valid_cluster_count":
            len(valid),

        "invalid_cluster_count":
            len(invalid),

        "required_valid_clusters":
            REQUIRED_TP_CLUSTERS,

        "valid_clusters":
            valid,

        "invalid_clusters":
            invalid,
    }

    approval = evaluate_tp_approval(
        diagnostics
    )

    result = {
        "diagnostics":
            diagnostics,

        "tp_approval":
            approval,

        "tp_prices":
            None,
    }

    if approval["approved"]:
        result[
            "tp_prices"
        ] = calculate_tp_prices(
            entry_price,
            valid,
            direction,
        )

    return result


# ============================================================
# R1.8 NET-ROI ADAPTIVE TP ENGINE
# ============================================================

def r18_net_roi_percent(
    entry_price,
    target_price,
    direction,
    leverage,
):
    entry_price = D(
        entry_price
    )

    target_price = D(
        target_price
    )

    leverage = D(
        leverage
    )

    if entry_price <= 0:
        raise ValueError(
            "entry_price must be positive"
        )

    if leverage <= 0:
        raise ValueError(
            "leverage must be positive"
        )

    if direction == "LONG":
        move_fraction = (
            target_price
            - entry_price
        ) / entry_price

    elif direction == "SHORT":
        move_fraction = (
            entry_price
            - target_price
        ) / entry_price

    else:
        raise ValueError(
            f"Unsupported direction={direction}"
        )

    return (
        move_fraction
        * leverage
        * Decimal("100")
    )


def r18_target_price_for_net_roi(
    entry_price,
    net_roi_percent,
    direction,
    leverage,
):
    entry_price = D(
        entry_price
    )

    net_roi_percent = D(
        net_roi_percent
    )

    leverage = D(
        leverage
    )

    if (
        entry_price <= 0
        or leverage <= 0
    ):
        return None

    move_fraction = (
        net_roi_percent
        / Decimal("100")
        / leverage
    )

    if direction == "LONG":
        target = (
            entry_price
            * (
                Decimal("1")
                + move_fraction
            )
        )

    elif direction == "SHORT":
        target = (
            entry_price
            * (
                Decimal("1")
                - move_fraction
            )
        )

    else:
        return None

    return quantize_down(
        target,
        PRICE_STEP,
    )


def r18_select_adaptive_target(
    entry_price,
    historical_cluster_price,
    minimum_net_roi_percent,
    direction,
    leverage,
):
    entry_price = D(
        entry_price
    )

    historical_cluster_price = (
        D(
            historical_cluster_price
        )
        if historical_cluster_price
        is not None
        else None
    )

    minimum_target = (
        r18_target_price_for_net_roi(
            entry_price,
            minimum_net_roi_percent,
            direction,
            leverage,
        )
    )

    if minimum_target is None:
        return None

    if historical_cluster_price is None:
        return minimum_target

    historical_cluster_price = (
        quantize_down(
            historical_cluster_price,
            PRICE_STEP,
        )
    )

    historical_roi = (
        r18_net_roi_percent(
            entry_price,
            historical_cluster_price,
            direction,
            leverage,
        )
    )

    if (
        historical_roi
        >= D(
            minimum_net_roi_percent
        )
    ):
        return (
            historical_cluster_price
        )

    return minimum_target


def r18_build_adaptive_tp_snapshot(
    entry_price,
    direction,
    valid_cluster_list,
    leverage,
):
    entry_price = D(
        entry_price
    )

    leverage = D(
        leverage
    )

    valid_cluster_list = (
        valid_cluster_list
        if isinstance(
            valid_cluster_list,
            list,
        )
        else []
    )

    cluster1 = (
        D(
            valid_cluster_list[
                0
            ][
                "average"
            ]
        )
        if len(
            valid_cluster_list
        ) >= 1
        else None
    )

    cluster2 = (
        D(
            valid_cluster_list[
                1
            ][
                "average"
            ]
        )
        if len(
            valid_cluster_list
        ) >= 2
        else None
    )

    tp1 = (
        r18_select_adaptive_target(
            entry_price,
            cluster1,
            R18_TP1_MIN_NET_ROI_PERCENT,
            direction,
            leverage,
        )
    )

    tp2 = (
        r18_select_adaptive_target(
            entry_price,
            cluster2,
            R18_TP2_MIN_NET_ROI_PERCENT,
            direction,
            leverage,
        )
    )

    if (
        tp1 is None
        or tp2 is None
    ):
        return {
            "direction":
                direction,

            "entry_price":
                decimal_to_string(
                    entry_price
                ),

            "leverage":
                decimal_to_string(
                    leverage
                ),

            "tp_approval": {
                "status":
                    "REJECTED",

                "approved":
                    False,

                "reason":
                    "R1.8_ADAPTIVE_TP_BUILD_FAILED",
            },

            "tp1":
                None,

            "tp2":
                None,

            "tp3": {
                "type":
                    "TRAILING",

                "allocation_percent":
                    R18_TP3_ALLOCATION_PERCENT,

                "trailing_distance_percent":
                    TP3_TRAILING_DISTANCE_PERCENT,
            },
        }

    tp1_roi = (
        r18_net_roi_percent(
            entry_price,
            tp1,
            direction,
            leverage,
        )
    )

    tp2_roi = (
        r18_net_roi_percent(
            entry_price,
            tp2,
            direction,
            leverage,
        )
    )

    approved = bool(
        tp1_roi
        >= R18_TP1_MIN_NET_ROI_PERCENT
        and
        tp2_roi
        >= R18_TP2_MIN_NET_ROI_PERCENT
    )

    return {
        "direction":
            direction,

        "entry_price":
            decimal_to_string(
                entry_price
            ),

        "leverage":
            decimal_to_string(
                leverage
            ),

        "tp_approval": {
            "status":
                (
                    "APPROVED"
                    if approved
                    else "REJECTED"
                ),

            "approved":
                approved,

            "reason":
                (
                    "R1.8_NET_ROI_TARGETS_APPROVED"
                    if approved
                    else
                    "R1.8_NET_ROI_TARGETS_REJECTED"
                ),
        },

        "tp1":
            decimal_to_string(
                tp1
            ),

        "tp2":
            decimal_to_string(
                tp2
            ),

        "tp1_net_roi_percent":
            decimal_to_string(
                tp1_roi
            ),

        "tp2_net_roi_percent":
            decimal_to_string(
                tp2_roi
            ),

        "tp1_minimum_net_roi_percent":
            decimal_to_string(
                R18_TP1_MIN_NET_ROI_PERCENT
            ),

        "tp2_minimum_net_roi_percent":
            decimal_to_string(
                R18_TP2_MIN_NET_ROI_PERCENT
            ),

        "cluster1_average":
            (
                decimal_to_string(
                    cluster1
                )
                if cluster1
                is not None
                else None
            ),

        "cluster2_average":
            (
                decimal_to_string(
                    cluster2
                )
                if cluster2
                is not None
                else None
            ),

        "tp3": {
            "type":
                "TRAILING",

            "allocation_percent":
                R18_TP3_ALLOCATION_PERCENT,

            "trailing_distance_percent":
                TP3_TRAILING_DISTANCE_PERCENT,
        },

        "allocation": {
            "tp1_percent":
                R18_TP1_ALLOCATION_PERCENT,

            "tp2_percent":
                R18_TP2_ALLOCATION_PERCENT,

            "tp3_percent":
                R18_TP3_ALLOCATION_PERCENT,
        },

        "primary_tp_immutable":
            R18_PRIMARY_TP_IMMUTABLE,

        "backup_tp_recalculate_on_fill":
            R18_BACKUP_TP_RECALCULATE_ON_FILL,
    }


# ============================================================
# R1.8 ADAPTIVE TP TESTS
# ============================================================

def r18_run_adaptive_tp_tests():
    long_snapshot = (
        r18_build_adaptive_tp_snapshot(
            entry_price=Decimal(
                "80000"
            ),
            direction="LONG",
            valid_cluster_list=[
                {
                    "average":
                        Decimal(
                            "80100"
                        )
                },
                {
                    "average":
                        Decimal(
                            "80200"
                        )
                },
            ],
            leverage=Decimal(
                "100"
            ),
        )
    )

    check(
        "R1.8_LONG_TP_APPROVED",
        long_snapshot[
            "tp_approval"
        ][
            "approved"
        ]
        is True,
    )

    check(
        "R1.8_LONG_TP1_NET_ROI_MINIMUM",
        D(
            long_snapshot[
                "tp1_net_roi_percent"
            ]
        )
        >=
        R18_TP1_MIN_NET_ROI_PERCENT,
    )

    check(
        "R1.8_LONG_TP2_NET_ROI_MINIMUM",
        D(
            long_snapshot[
                "tp2_net_roi_percent"
            ]
        )
        >=
        R18_TP2_MIN_NET_ROI_PERCENT,
    )

    check(
        "R1.8_LONG_ALLOCATION_25_25_50",
        (
            D(
                long_snapshot[
                    "allocation"
                ][
                    "tp1_percent"
                ]
            )
            ==
            Decimal(
                "25"
            )
            and
            D(
                long_snapshot[
                    "allocation"
                ][
                    "tp2_percent"
                ]
            )
            ==
            Decimal(
                "25"
            )
            and
            D(
                long_snapshot[
                    "allocation"
                ][
                    "tp3_percent"
                ]
            )
            ==
            Decimal(
                "50"
            )
        ),
    )

    short_snapshot = (
        r18_build_adaptive_tp_snapshot(
            entry_price=Decimal(
                "80000"
            ),
            direction="SHORT",
            valid_cluster_list=[
                {
                    "average":
                        Decimal(
                            "79900"
                        )
                },
                {
                    "average":
                        Decimal(
                            "79800"
                        )
                },
            ],
            leverage=Decimal(
                "100"
            ),
        )
    )

    check(
        "R1.8_SHORT_TP_APPROVED",
        short_snapshot[
            "tp_approval"
        ][
            "approved"
        ]
        is True,
    )

    check(
        "R1.8_SHORT_TP1_NET_ROI_MINIMUM",
        D(
            short_snapshot[
                "tp1_net_roi_percent"
            ]
        )
        >=
        R18_TP1_MIN_NET_ROI_PERCENT,
    )

    check(
        "R1.8_SHORT_TP2_NET_ROI_MINIMUM",
        D(
            short_snapshot[
                "tp2_net_roi_percent"
            ]
        )
        >=
        R18_TP2_MIN_NET_ROI_PERCENT,
    )

    check(
        "R1.8_SHORT_PRIMARY_TP_IMMUTABLE",
        short_snapshot[
            "primary_tp_immutable"
        ]
        is True,
    )

    check(
        "R1.8_SHORT_BACKUP_TP_RECALCULATE_ON_FILL",
        short_snapshot[
            "backup_tp_recalculate_on_fill"
        ]
        is True,
    )

    return {
        "long":
            long_snapshot,

        "short":
            short_snapshot,
    }


# ============================================================
# SYNTHETIC TESTS
# ============================================================

def synthetic_cluster_tests():
    long_rows = [
        [1, "100000", "100800", "99500", "100200", "1"],
        [2, "100200", "101000", "99700", "100500", "1"],
        [3, "100500", "100900", "99800", "100300", "1"],
        [4, "100300", "101100", "99900", "100700", "1"],
        [5, "100700", "101000", "100000", "100600", "1"],
        [6, "100600", "101200", "99950", "100900", "1"],
        [7, "100900", "101100", "100100", "100800", "1"],
        [8, "100800", "101300", "100200", "101000", "1"],
    ]

    short_rows = [
        [1, "81000", "81500", "80500", "80800", "1"],
        [2, "80800", "81400", "80000", "80500", "1"],
        [3, "80500", "81300", "80100", "80700", "1"],
        [4, "80500", "81300", "79900", "80300", "1"],
        [5, "80300", "81200", "80000", "80500", "1"],
        [6, "80500", "81400", "79800", "80400", "1"],
        [7, "80400", "81300", "80100", "80600", "1"],
        [8, "80600", "81500", "79950", "80800", "1"],
    ]

    long_diagnostics = (
        build_cluster_diagnostics(
            long_rows,
            Decimal("99000"),
            "LONG",
        )
    )

    long_approval = (
        evaluate_tp_approval(
            long_diagnostics
        )
    )

    check(
        "SYNTHETIC_LONG_TWO_CLUSTER_APPROVAL",
        long_approval[
            "approved"
        ] is True,
    )

    short_diagnostics = (
        build_cluster_diagnostics(
            short_rows,
            Decimal("82000"),
            "SHORT",
        )
    )

    short_approval = (
        evaluate_tp_approval(
            short_diagnostics
        )
    )

    check(
        "SYNTHETIC_SHORT_TWO_CLUSTER_APPROVAL",
        short_approval[
            "approved"
        ] is True,
    )

    return (
        long_approval,
        short_approval,
    )


def synthetic_tp_rejection_test():
    rows = [
        [1, "99000", "100000", "99500", "99500", "1"],
        [2, "99500", "100100", "99600", "99800", "1"],
        [3, "99600", "100000", "99500", "99700", "1"],
        [4, "99500", "100100", "99800", "99900", "1"],
    ]

    entry = Decimal(
        "99500"
    )

    diagnostics = (
        build_cluster_diagnostics(
            rows,
            entry,
            "LONG",
        )
    )

    approval = (
        evaluate_tp_approval(
            diagnostics
        )
    )

    check(
        "ONE_CLUSTER_TP_REJECTED",
        approval[
            "approved"
        ] is False,
    )

    check(
        "ONE_CLUSTER_APPROVAL_STATUS_REJECTED",
        approval[
            "status"
        ] == "REJECTED",
    )

    check(
        "ONE_CLUSTER_DOES_NOT_APPROVE_TP_SET",
        (
            approval[
                "available_valid_clusters"
            ]
            < REQUIRED_TP_CLUSTERS
        ),
    )

    return approval


# ============================================================
# CANARY PREVIEW
# ============================================================

def build_canary_preview():
    return {
        "stage":
            STAGE,

        "symbol":
            SYMBOL,

        "real_order_execution":
            REAL_ORDER_EXECUTION,

        "demo_order_execution":
            DEMO_ORDER_EXECUTION,

        "exchange_mutation_transport_enabled":
            EXCHANGE_MUTATION_TRANSPORT_ENABLED,

        "order_submission_enabled":
            ORDER_SUBMISSION_ENABLED,

        "first_real_order_allowed":
            FIRST_REAL_ORDER_ALLOWED,

        "submitted":
            False,

        "exchange_request_sent":
            False,
    }


# ============================================================
# WRITER HELPERS
# ============================================================

WRITER_ENDPOINT_ENTRY = (
    "/capi/v3/order"
)

WRITER_ENDPOINT_TPSL = (
    "/capi/v3/placeTpSlOrder"
)

WRITER_ENDPOINT_TRAILING = (
    "/capi/v3/algoOrder"
)


def writer_entry_side(
    direction,
):
    if direction == "LONG":
        return (
            "BUY",
            "LONG",
        )

    if direction == "SHORT":
        return (
            "SELL",
            "SHORT",
        )

    raise ValueError(
        f"Unsupported direction={direction}"
    )


def writer_close_side(
    direction,
):
    if direction == "LONG":
        return (
            "SELL",
            "LONG",
        )

    if direction == "SHORT":
        return (
            "BUY",
            "SHORT",
        )

    raise ValueError(
        f"Unsupported direction={direction}"
    )


def writer_client_id(
    direction,
    leg,
):
    value = (
        f"R36F8-{direction}-{leg}-0001"
    )

    if len(value) > 36:
        raise ValueError(
            "writer client id exceeds WEEX limit"
        )

    return value


# ============================================================
# WRITER QUANTITY ALLOCATION
# ============================================================

def writer_allocate_tp_quantities(
    total_quantity,
):
    total_quantity = quantize_down(
        total_quantity,
        QUANTITY_STEP,
    )

    if total_quantity < MIN_QUANTITY:
        raise ValueError(
            "Writer quantity below minimum"
        )

    tp1_quantity = quantize_down(
        total_quantity
        * TP1_ALLOCATION_PERCENT
        / Decimal("100"),
        QUANTITY_STEP,
    )

    tp2_quantity = quantize_down(
        total_quantity
        * TP2_ALLOCATION_PERCENT
        / Decimal("100"),
        QUANTITY_STEP,
    )

    tp3_quantity = (
        total_quantity
        - tp1_quantity
        - tp2_quantity
    )

    tp3_quantity = quantize_down(
        tp3_quantity,
        QUANTITY_STEP,
    )

    if tp3_quantity < 0:
        raise ValueError(
            "Writer TP3 quantity became negative"
        )

    return {
        "total":
            total_quantity,

        "tp1":
            tp1_quantity,

        "tp2":
            tp2_quantity,

        "tp3":
            tp3_quantity,

        "sum":
            (
                tp1_quantity
                + tp2_quantity
                + tp3_quantity
            ),
    }


# ============================================================
# R36F.15.10.4b — BALANCE READINESS + PROTECTIVE STOP
# ============================================================

try:
    TARGET_LONG_LEVERAGE
except NameError:
    TARGET_LONG_LEVERAGE = 100

try:
    TARGET_SHORT_LEVERAGE
except NameError:
    TARGET_SHORT_LEVERAGE = 100


ADJUSTED_TP1_ALLOCATION_PERCENT = Decimal("25")
ADJUSTED_TP2_ALLOCATION_PERCENT = Decimal("25")
ADJUSTED_TP3_ALLOCATION_PERCENT = Decimal("50")


def allocation_exactly_representable(
    entry_quantity,
    tp1_percent,
    tp2_percent,
    tp3_percent,
):
    entry_quantity = quantize_down(
        D(entry_quantity),
        QUANTITY_STEP,
    )

    percentages = (
        D(tp1_percent),
        D(tp2_percent),
        D(tp3_percent),
    )

    if sum(percentages) != Decimal("100"):
        return False

    quantities = [
        entry_quantity
        * percent
        / Decimal("100")
        for percent in percentages
    ]

    return bool(
        entry_quantity >= MIN_QUANTITY
        and all(
            quantity >= MIN_QUANTITY
            for quantity in quantities
        )
        and all(
            quantize_down(
                quantity,
                QUANTITY_STEP,
            ) == quantity
            for quantity in quantities
        )
        and sum(quantities)
        == entry_quantity
    )


def select_tp_allocation(
    entry_quantity,
):
    entry_quantity = quantize_down(
        D(entry_quantity),
        QUANTITY_STEP,
    )

    preferred = (
        TP1_ALLOCATION_PERCENT,
        TP2_ALLOCATION_PERCENT,
        TP3_ALLOCATION_PERCENT,
    )

    adjusted = (
        ADJUSTED_TP1_ALLOCATION_PERCENT,
        ADJUSTED_TP2_ALLOCATION_PERCENT,
        ADJUSTED_TP3_ALLOCATION_PERCENT,
    )

    if allocation_exactly_representable(
        entry_quantity,
        *preferred,
    ):
        return {
            "tp1_percent":
                preferred[0],

            "tp2_percent":
                preferred[1],

            "tp3_percent":
                preferred[2],

            "adjusted":
                False,

            "label":
                "20/20/60",
        }

    if allocation_exactly_representable(
        entry_quantity,
        *adjusted,
    ):
        return {
            "tp1_percent":
                adjusted[0],

            "tp2_percent":
                adjusted[1],

            "tp3_percent":
                adjusted[2],

            "adjusted":
                True,

            "label":
                "25/25/50",
        }

    return None


def writer_quantities(
    entry_quantity,
):
    entry_quantity = quantize_down(
        D(entry_quantity),
        QUANTITY_STEP,
    )

    allocation = select_tp_allocation(
        entry_quantity
    )

    if allocation is None:
        return (
            entry_quantity,
            Decimal("0"),
            Decimal("0"),
            Decimal("0"),
        )

    tp1 = (
        entry_quantity
        * allocation[
            "tp1_percent"
        ]
        / Decimal("100")
    )

    tp2 = (
        entry_quantity
        * allocation[
            "tp2_percent"
        ]
        / Decimal("100")
    )

    tp3 = (
        entry_quantity
        * allocation[
            "tp3_percent"
        ]
        / Decimal("100")
    )

    return (
        entry_quantity,
        tp1,
        tp2,
        tp3,
    )


def validate_writer_quantities(
    entry_quantity,
    tp1,
    tp2,
    tp3,
):
    allocation = select_tp_allocation(
        entry_quantity
    )

    if allocation is None:
        return {
            "allocation_selected":
                False,

            "all_valid":
                False,
        }

    exact_tp1 = (
        entry_quantity
        * allocation[
            "tp1_percent"
        ]
        / Decimal("100")
    )

    exact_tp2 = (
        entry_quantity
        * allocation[
            "tp2_percent"
        ]
        / Decimal("100")
    )

    exact_tp3 = (
        entry_quantity
        * allocation[
            "tp3_percent"
        ]
        / Decimal("100")
    )

    checks = {
        "allocation_selected":
            True,

        "entry_on_step":
            quantize_down(
                entry_quantity,
                QUANTITY_STEP,
            ) == entry_quantity,

        "tp1_on_step":
            quantize_down(
                tp1,
                QUANTITY_STEP,
            ) == tp1,

        "tp2_on_step":
            quantize_down(
                tp2,
                QUANTITY_STEP,
            ) == tp2,

        "tp3_on_step":
            quantize_down(




