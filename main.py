
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
            "sl_trigger_price": None,
        }

    if direction == "LONG":
        valid = (
            fresh_mark < tp
        )

        reason = (
            "JIT_LONG_TP_VALID_SL_DISABLED"
            if valid
            else "JIT_LONG_TP_STALE_OR_CROSSED"
        )

    else:
        valid = (
            tp < fresh_mark
        )

        reason = (
            "JIT_SHORT_TP_VALID_SL_DISABLED"
            if valid
            else "JIT_SHORT_TP_STALE_OR_CROSSED"
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
        "sl_trigger_price": None,
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
            open_orders=0,
        )
    )

    test2_pass = (
        test2.get("allow") is False
        and test2.get("reason")
        == "ACTIVE_CLIENT_ID_BLOCKS"
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
                "R36F159-L-NEWTEST000000001"
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
    # Fresh client ID + flat account
    # Expected: ALLOW
    # --------------------------------------------------------

    test4 = (
        r182_client_id_lifecycle_decision(
            candidate_client_id=(
                "R36F159-L-FRESH00000000001"
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

    test4_pass = (
        test4.get("allow") is True
        and test4.get("reason")
        == "NEW_CLIENT_ID_AND_FLAT_ACCOUNT"
    )

    log(
        "R1.8.2 TEST 4 "
        "FRESH ID + FLAT = "
        + (
            "PASS"
            if test4_pass
            else "FAIL"
        )
        + " RESULT="
        + str(test4)
    )

    overall = all(
        [
            test1_pass,
            test2_pass,
            test3_pass,
            test4_pass,
        ]
    )

    log(
        "R1.8.2 ZERO-WRITE LIFECYCLE TEST = "
        + (
            "PASS"
            if overall
            else "FAIL"
        )
    )

    return overall


# ============================================================
# END OF PART 1/6
# NEXT: PART 2 CONTINUES DIRECTLY FROM HERE
# ============================================================

# ============================================================
# R1.8 CORRECTED MAIN.PY — PART 2 START
# ============================================================

def r36f159_test_recurring_opportunity_gate():
    print("==========================================")
    print("R36F159 RECURRING OPPORTUNITY UNIT TEST START")
    print("==========================================")

    def evaluate(existing_state, existing_identity, new_identity):
        existing_state = str(
            existing_state or ""
        ).strip().upper()

        existing_identity = str(
            existing_identity or ""
        ).strip()

        new_identity = str(
            new_identity or ""
        ).strip()

        if not existing_identity:
            return {
                "allow": True,
                "reason": "NO_EXISTING_IDENTITY",
            }

        if hmac.compare_digest(
            existing_identity,
            new_identity,
        ):
            return {
                "allow": False,
                "reason": "SAME_OPPORTUNITY_REPLAY_BLOCKED",
            }

        if existing_state == "COMPLETED":
            return {
                "allow": True,
                "reason": "PREVIOUS_COMPLETED_NEW_OPPORTUNITY",
            }

        return {
            "allow": False,
            "reason": "PREVIOUS_OPPORTUNITY_UNRESOLVED",
        }

    old_identity = sha256_text(
        "OLD_COMPLETED_OPPORTUNITY"
    )

    new_identity = sha256_text(
        "NEW_MARKET_OPPORTUNITY"
    )

    test_1 = evaluate(
        "COMPLETED",
        old_identity,
        old_identity,
    )

    test_2 = evaluate(
        "COMPLETED",
        old_identity,
        new_identity,
    )

    test_3 = evaluate(
        "PREPARED",
        old_identity,
        new_identity,
    )

    test_4 = evaluate(
        "",
        "",
        new_identity,
    )

    pass_1 = (
        test_1["allow"] is False
        and test_1["reason"]
        == "SAME_OPPORTUNITY_REPLAY_BLOCKED"
    )

    pass_2 = (
        test_2["allow"] is True
        and test_2["reason"]
        == "PREVIOUS_COMPLETED_NEW_OPPORTUNITY"
    )

    pass_3 = (
        test_3["allow"] is False
        and test_3["reason"]
        == "PREVIOUS_OPPORTUNITY_UNRESOLVED"
    )

    pass_4 = (
        test_4["allow"] is True
        and test_4["reason"]
        == "NO_EXISTING_IDENTITY"
    )

    overall_pass = all(
        [
            pass_1,
            pass_2,
            pass_3,
            pass_4,
        ]
    )

    print(
        "TEST 1 SAME COMPLETED OPPORTUNITY =",
        "PASS" if pass_1 else "FAIL",
        test_1,
    )

    print(
        "TEST 2 NEW AFTER COMPLETED =",
        "PASS" if pass_2 else "FAIL",
        test_2,
    )

    print(
        "TEST 3 NEW AFTER UNRESOLVED =",
        "PASS" if pass_3 else "FAIL",
        test_3,
    )

    print(
        "TEST 4 FIRST OPPORTUNITY =",
        "PASS" if pass_4 else "FAIL",
        test_4,
    )

    print(
        "R36F159 RECURRING OPPORTUNITY UNIT TEST =",
        "PASS" if overall_pass else "FAIL",
    )

    print("R36F159 TEST WEEX POST = False")
    print("R36F159 TEST DEMO ORDER = False")
    print("R36F159 TEST REAL ORDER = False")
    print("==========================================")

    return overall_pass


if os.getenv(
    "RUN_R36F159_RECURRING_TEST",
    "0",
).strip() == "1":
    r36f159_test_recurring_opportunity_gate()


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
        "R1.8.1 DIAGNOSTIC END"
    )

    payload[
        "clientOrderId"
    ] = client_order_id

    payload[
        "newClientOrderId"
    ] = client_order_id

    payload_hash = sha256_text(
        canonical_json(
            payload
        )
    )

    jit = (
        await r36f154_validate_fresh_demo_triggers(
            payload
        )
    )

    if not jit.get(
        "valid"
    ):
        return {
            "attempted": False,
            "sent": False,
            "accepted": False,
            "reason": "R36F154_JIT_TRIGGER_VALIDATION_FAILED",
            "jit": jit,
        }

    prepared = {
        "stage": STAGE,
        "state": "PREPARED",
        "prepared_at": now_iso(),
        "updated_at": now_iso(),
        "success": False,
        "direction": command_preview.get(
            "direction"
        ),
        "command": command_preview.get(
            "command"
        ),
        "command_identity_sha256": command_identity,
        "command_token_sha256": sha256_text(
            R36F159_COMMAND_TOKEN
        ),
        "client_order_id": client_order_id,
        "payload_sha256": payload_hash,
        "payload": payload,
        "jit_validation": jit,
    }

    write_json_file(
        R36F159_DEMO_JOURNAL_FILE,
        prepared,
    )

    try:
        response = await weex_demo_post(
            R36F14_DEMO_ORDER_ENDPOINT,
            payload,
        )

    except Exception as exc:
        ambiguous = {
            **prepared,
            "state": "SENT_AMBIGUOUS",
            "updated_at": now_iso(),
            "success": False,
            "error": str(exc),
        }

        write_json_file(
            R36F159_DEMO_JOURNAL_FILE,
            ambiguous,
        )

        return {
            "attempted": True,
            "sent": True,
            "accepted": False,
            "reason": "R36F159_DEMO_POST_AMBIGUOUS",
            "error": str(exc),
            "journal": ambiguous,
        }

    response_data = (
        response.get(
            "response"
        )
        if isinstance(
            response,
            dict,
        )
        else {}
    )

    if not isinstance(
        response_data,
        dict,
    ):
        response_data = {}

    response_code = str(
        response_data.get(
            "code"
        )
        or ""
    ).strip()

    response_message = str(
        response_data.get(
            "msg"
        )
        or response_data.get(
            "message"
        )
        or ""
    ).strip()

    response_data_body = (
        response_data.get(
            "data"
        )
        if isinstance(
            response_data.get(
                "data"
            ),
            dict,
        )
        else {}
    )

    response_order_id = str(
        response_data_body.get(
            "orderId"
        )
        or response_data.get(
            "orderId"
        )
        or ""
    ).strip()

    response_client_id = str(
        response_data_body.get(
            "clientOrderId"
        )
        or response_data.get(
            "clientOrderId"
        )
        or client_order_id
    ).strip()

    accepted = bool(
        response_order_id
        or response_code
        in {
            "0",
            "00000",
            "200",
        }
    )

    if accepted:
        completed = {
            **prepared,
            "state": "COMPLETED",
            "updated_at": now_iso(),
            "success": True,
            "order_id": response_order_id,
            "client_order_id_response": response_client_id,
            "response_code": response_code,
            "response_message": response_message,
            "response": response_data,
        }

        write_json_file(
            R36F159_DEMO_JOURNAL_FILE,
            completed,
        )

        return {
            "attempted": True,
            "sent": True,
            "accepted": True,
            "reason": "R36F159_SECOND_DEMO_ACCEPTED",
            "order_id": response_order_id,
            "client_order_id": response_client_id,
            "journal": completed,
            "response": response,
        }

    rejected = {
        **prepared,
        "state": "REJECTED",
        "updated_at": now_iso(),
        "success": False,
        "response_code": response_code,
        "response_message": response_message,
        "response": response_data,
    }

    write_json_file(
        R36F159_DEMO_JOURNAL_FILE,
        rejected,
    )

    return {
        "attempted": True,
        "sent": True,
        "accepted": False,
        "reason": "R36F159_SECOND_DEMO_REJECTED",
        "journal": rejected,
        "response": response,
    }


def ema_series(
    values,
    period,
):
    values = [
        D(value)
        for value in values
    ]

    if not values:
        return []

    alpha = (
        D("2")
        / D(
            period + 1
        )
    )

    result = [
        values[0]
    ]

    for value in values[1:]:
        previous = result[-1]

        current = (
            (
                value
                * alpha
            )
            + (
                previous
                * (
                    D("1")
                    - alpha
                )
            )
        )

        result.append(
            current
        )

    return result


def calculate_ema_signal(
    candles,
):
    if not candles:
        return {
            "valid": False,
            "reason": "NO_CANDLES",
            "direction": None,
        }

    closes = []

    for candle in candles:
        try:
            closes.append(
                D(
                    candle[
                        "close"
                    ]
                )
            )

        except Exception:
            continue

    if len(closes) < EMA_SLOW:
        return {
            "valid": False,
            "reason": "INSUFFICIENT_EMA_HISTORY",
            "direction": None,
            "candle_count": len(
                closes
            ),
        }

    fast_series = ema_series(
        closes,
        EMA_FAST,
    )

    mid_series = ema_series(
        closes,
        EMA_MID,
    )

    slow_series = ema_series(
        closes,
        EMA_SLOW,
    )

    ema_fast = fast_series[-1]
    ema_mid = mid_series[-1]
    ema_slow = slow_series[-1]

    separation = D("0")

    if ema_mid > 0:
        separation = (
            abs(
                ema_fast
                - ema_mid
            )
            / ema_mid
            * D("100")
        )

    direction = None

    if (
        ema_fast
        > ema_mid
        > ema_slow
        and separation
        >= MIN_EMA_19_50_SEPARATION_PERCENT
    ):
        direction = "LONG"

    elif (
        ema_fast
        < ema_mid
        < ema_slow
        and separation
        >= MIN_EMA_19_50_SEPARATION_PERCENT
    ):
        direction = "SHORT"

    return {
        "valid": True,
        "reason": (
            "EMA_DIRECTION_AVAILABLE"
            if direction
            else "EMA_DIRECTION_NOT_CONFIRMED"
        ),
        "direction": direction,
        "ema19": decimal_to_string(
            ema_fast
        ),
        "ema50": decimal_to_string(
            ema_mid
        ),
        "ema200": decimal_to_string(
            ema_slow
        ),
        "ema19_50_separation_percent":
            decimal_to_string(
                separation
            ),
        "candle_count": len(
            closes
        ),
    }


def build_telegram_command_preview(
    ema_snapshot,
    long_diagnostics,
    short_diagnostics,
):
    direction = (
        ema_snapshot.get(
            "direction"
        )
        if isinstance(
            ema_snapshot,
            dict,
        )
        else None
    )

    if direction == "LONG":
        command = TELEGRAM_BUY_COMMAND
        diagnostics = (
            long_diagnostics
            if isinstance(
                long_diagnostics,
                dict,
            )
            else {}
        )

    elif direction == "SHORT":
        command = TELEGRAM_SELL_COMMAND
        diagnostics = (
            short_diagnostics
            if isinstance(
                short_diagnostics,
                dict,
            )
            else {}
        )

    else:
        return {
            "authorized_preview": False,
            "reason": "EMA_DIRECTION_NOT_AVAILABLE",
            "direction": None,
            "command": None,
        }

    market_eligible = bool(
        diagnostics.get(
            "market_eligible",
            False,
        )
    )

    return {
        "authorized_preview":
            market_eligible,
        "reason": (
            "EMA_AND_TP_MARKET_ELIGIBLE"
            if market_eligible
            else "TP_MARKET_NOT_ELIGIBLE"
        ),
        "direction": direction,
        "command": command,
    }


def normalize_candle_row(
    row,
):
    if isinstance(
        row,
        dict,
    ):
        timestamp = (
            row.get("timestamp")
            or row.get("time")
            or row.get("ts")
            or row.get("openTime")
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

    elif (
        isinstance(
            row,
            (list, tuple),
        )
        and len(row) >= 5
    ):
        timestamp = row[0]
        open_price = row[1]
        high_price = row[2]
        low_price = row[3]
        close_price = row[4]

    else:
        return None

    try:
        timestamp = int(
            D(timestamp)
        )

        return {
            "timestamp": timestamp,
            "open": D(
                open_price
            ),
            "high": D(
                high_price
            ),
            "low": D(
                low_price
            ),
            "close": D(
                close_price
            ),
        }

    except Exception:
        return None


def extract_candle_rows(
    data,
):
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
        "candles",
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
                "candles",
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


async def load_historical_candles():
    all_rows = []

    end_time = None

    for page in range(
        MAX_HISTORICAL_PAGES
    ):
        params = {
            "symbol":
                PUBLIC_TICKER_SYMBOL,
            "interval":
                KLINE_INTERVAL,
            "limit":
                HISTORICAL_LIMIT,
        }

        if end_time is not None:
            params[
                "endTime"
            ] = end_time

        data = await weex_get(
            "/capi/v2/market/candles",
            params=params,
            authenticated=False,
        )

        rows = extract_candle_rows(
            data
        )

        if not rows:
            break

        normalized = []

        for row in rows:
            candle = (
                normalize_candle_row(
                    row
                )
            )

            if candle is not None:
                normalized.append(
                    candle
                )

        if not normalized:
            break

        all_rows.extend(
            normalized
        )

        oldest_timestamp = min(
            candle[
                "timestamp"
            ]
            for candle in normalized
        )

        end_time = (
            oldest_timestamp
            - 1
        )

        if len(
            normalized
        ) < HISTORICAL_LIMIT:
            break

    unique = {}

    for candle in all_rows:
        unique[
            candle["timestamp"]
        ] = candle

    candles = sorted(
        unique.values(),
        key=lambda item:
            item["timestamp"],
    )

    return candles


async def load_mark_price():
    data = await weex_get(
        "/capi/v2/market/ticker",
        params={
            "symbol":
                PUBLIC_TICKER_SYMBOL,
        },
        authenticated=False,
    )

    candidates = []

    if isinstance(
        data,
        dict,
    ):
        candidates.append(
            data
        )

        nested = data.get(
            "data"
        )

        if isinstance(
            nested,
            dict,
        ):
            candidates.append(
                nested
            )

        elif isinstance(
            nested,
            list,
        ):
            candidates.extend(
                item
                for item in nested
                if isinstance(
                    item,
                    dict,
                )
            )

    elif isinstance(
        data,
        list,
    ):
        candidates.extend(
            item
            for item in data
            if isinstance(
                item,
                dict,
            )
        )

    for item in candidates:
        for key in (
            "markPrice",
            "mark_price",
            "last",
            "lastPrice",
            "close",
        ):
            value = item.get(
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

    raise RuntimeError(
        "Unable to extract WEEX mark price"
    )


def cluster_prices(
    prices,
):
    values = sorted(
        D(value)
        for value in prices
        if D(value) > 0
    )

    if not values:
        return []

    tolerance_fraction = (
        CLUSTER_TOLERANCE_PERCENT
        / D("100")
    )

    clusters = []

    for price in values:
        placed = False

        for cluster in clusters:
            average = (
                sum(
                    cluster
                )
                / D(
                    len(cluster)
                )
            )

            if average <= 0:
                continue

            difference = (
                abs(
                    price
                    - average
                )
                / average
            )

            if (
                difference
                <= tolerance_fraction
            ):
                cluster.append(
                    price
                )

                placed = True
                break

        if not placed:
            clusters.append(
                [price]
            )

    results = []

    for cluster in clusters:
        average = (
            sum(
                cluster
            )
            / D(
                len(cluster)
            )
        )

        results.append(
            {
                "average": average,
                "touches": len(
                    cluster
                ),
                "minimum": min(
                    cluster
                ),
                "maximum": max(
                    cluster
                ),
            }
        )

    return results


def calculate_tp_diagnostics(
    direction,
    mark_price,
    candles,
):
    direction = str(
        direction
        or ""
    ).strip().upper()

    mark_price = D(
        mark_price
    )

    if direction not in {
        "LONG",
        "SHORT",
    }:
        return {
            "market_eligible": False,
            "reason": "INVALID_DIRECTION",
            "valid_clusters": [],
        }

    if mark_price <= 0:
        return {
            "market_eligible": False,
            "reason": "INVALID_MARK_PRICE",
            "valid_clusters": [],
        }

    candidate_prices = []

    for candle in candles:
        try:
            if direction == "LONG":
                candidate = D(
                    candle[
                        "high"
                    ]
                )

                if candidate > mark_price:
                    candidate_prices.append(
                        candidate
                    )

            else:
                candidate = D(
                    candle[
                        "low"
                    ]
                )

                if candidate < mark_price:
                    candidate_prices.append(
                        candidate
                    )

        except Exception:
            continue

    clusters = cluster_prices(
        candidate_prices
    )

    valid_clusters = [
        cluster
        for cluster in clusters
        if cluster[
            "touches"
        ] >= MIN_CLUSTER_TOUCHES
    ]

    if direction == "LONG":
        valid_clusters = sorted(
            valid_clusters,
            key=lambda item:
                item["average"],
        )

    else:
        valid_clusters = sorted(
            valid_clusters,
            key=lambda item:
                item["average"],
            reverse=True,
        )

    market_eligible = (
        len(
            valid_clusters
        )
        >= REQUIRED_TP_CLUSTERS
    )

    return {
        "market_eligible":
            market_eligible,
        "reason": (
            "ENOUGH_VALID_CLUSTERS"
            if market_eligible
            else "ONLY_"
            + str(
                len(
                    valid_clusters
                )
            )
            + "_VALID_CLUSTER"
        ),
        "valid_clusters":
            valid_clusters,
        "valid_cluster_count":
            len(
                valid_clusters
            ),
    }


def select_tp_snapshot(
    direction,
    diagnostics,
):
    diagnostics = (
        diagnostics
        if isinstance(
            diagnostics,
            dict,
        )
        else {}
    )

    valid_clusters = (
        diagnostics.get(
            "valid_clusters"
        )
        or []
    )

    if len(
        valid_clusters
    ) < 2:
        return {
            "valid": False,
            "reason":
                "INSUFFICIENT_VALID_CLUSTERS",
            "direction":
                direction,
        }

    tp1 = quantize_down(
        valid_clusters[0][
            "average"
        ],
        PRICE_STEP,
    )

    tp2 = quantize_down(
        valid_clusters[1][
            "average"
        ],
        PRICE_STEP,
    )

    return {
        "valid": True,
        "reason":
            "TWO_CLUSTER_TP_SELECTED",
        "direction":
            direction,
        "tp1": tp1,
        "tp2": tp2,
        "tp3_mode":
            "TRAILING_RUNNER",
        "tp3_trailing_distance_percent":
            TP3_TRAILING_DISTANCE_PERCENT,
    }


def calculate_entry_quantity(
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

    margin = (
        available_balance
        * ENTRY_MARGIN_PERCENT
        / D("100")
    )

    notional = (
        margin
        * leverage
    )

    raw_quantity = (
        notional
        / mark_price
    )

    return quantize_down(
        raw_quantity,
        QUANTITY_STEP,
    )


def calculate_protective_stop(
    direction,
    mark_price,
):
    direction = str(
        direction
        or ""
    ).strip().upper()

    mark_price = D(
        mark_price
    )

    distance_fraction = (
        R36F13_PROTECTIVE_STOP_DISTANCE_PERCENT
        / D("100")
    )

    if direction == "LONG":
        raw_stop = (
            mark_price
            * (
                D("1")
                - distance_fraction
            )
        )

    elif direction == "SHORT":
        raw_stop = (
            mark_price
            * (
                D("1")
                + distance_fraction
            )
        )

    else:
        raise ValueError(
            "Invalid protective stop direction"
        )

    return quantize_down(
        raw_stop,
        PRICE_STEP,
    )


def calculate_stop_distance_percent(
    direction,
    mark_price,
    stop_price,
):
    direction = str(
        direction
        or ""
    ).strip().upper()

    mark_price = D(
        mark_price
    )

    stop_price = D(
        stop_price
    )

    if mark_price <= 0:
        return D("0")

    if direction == "LONG":
        distance = (
            mark_price
            - stop_price
        )

    elif direction == "SHORT":
        distance = (
            stop_price
            - mark_price
        )

    else:
        return D("0")

    if distance < 0:
        return D("0")

    return (
        distance
        / mark_price
        * D("100")
    )


def build_stop_risk_preview(
    direction,
    mark_price,
    stop_price,
):
    distance_percent = (
        calculate_stop_distance_percent(
            direction,
            mark_price,
            stop_price,
        )
    )

    within_envelope = (
        distance_percent
        > 0
        and distance_percent
        <= R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT
    )

    return {
        "valid":
            within_envelope,
        "reason": (
            "STOP_WITHIN_RISK_ENVELOPE"
            if within_envelope
            else "STOP_OUTSIDE_RISK_ENVELOPE"
        ),
        "distance_percent":
            distance_percent,
        "maximum_distance_percent":
            R36F131_MAX_PROTECTIVE_STOP_DISTANCE_PERCENT,
    }


def build_stop_loss_budget_preview(
    available_balance,
    quantity,
    mark_price,
    stop_price,
):
    available_balance = D(
        available_balance
    )

    quantity = D(
        quantity
    )

    mark_price = D(
        mark_price
    )

    stop_price = D(
        stop_price
    )

    loss_per_unit = abs(
        mark_price
        - stop_price
    )

    estimated_loss = (
        loss_per_unit
        * quantity
    )

    maximum_loss = (
        available_balance
        * R36F132_MAX_ACCOUNT_LOSS_PERCENT
        / D("100")
    )

    valid = (
        estimated_loss
        > 0
        and maximum_loss
        > 0
        and estimated_loss
        <= maximum_loss
    )

    return {
        "valid": valid,
        "reason": (
            "STOP_LOSS_WITHIN_ACCOUNT_BUDGET"
            if valid
            else "STOP_LOSS_EXCEEDS_ACCOUNT_BUDGET"
        ),
        "estimated_loss":
            estimated_loss,
        "maximum_loss":
            maximum_loss,
    }


def allocate_tp_quantities(
    total_quantity,
):
    total_quantity = D(
        total_quantity
    )

    if total_quantity <= 0:
        return {
            "valid": False,
            "reason":
                "NON_POSITIVE_TOTAL_QUANTITY",
        }

    tp1_quantity = quantize_down(
        total_quantity
        * TP1_ALLOCATION_PERCENT
        / D("100"),
        QUANTITY_STEP,
    )

    tp2_quantity = quantize_down(
        total_quantity
        * TP2_ALLOCATION_PERCENT
        / D("100"),
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

    valid = all(
        quantity >= MIN_QUANTITY
        for quantity in (
            tp1_quantity,
            tp2_quantity,
            tp3_quantity,
        )
    )

    return {
        "valid": valid,
        "reason": (
            "TP_QUANTITIES_REPRESENTABLE"
            if valid
            else "TP_QUANTITIES_BELOW_EXCHANGE_MINIMUM"
        ),
        "tp1_quantity":
            tp1_quantity,
        "tp2_quantity":
            tp2_quantity,
        "tp3_quantity":
            tp3_quantity,
    }


async def load_available_demo_balance():
    data = await weex_get(
        R36F14_DEMO_BALANCE_ENDPOINT,
        authenticated=True,
    )

    rows = []

    if isinstance(
        data,
        list,
    ):
        rows = data

    elif isinstance(
        data,
        dict,
    ):
        nested = data.get(
            "data"
        )

        if isinstance(
            nested,
            list,
        ):
            rows = nested

        elif isinstance(
            nested,
            dict,
        ):
            rows = [
                nested
            ]

        else:
            rows = [
                data
            ]

    for row in rows:
        if not isinstance(
            row,
            dict,
        ):
            continue

        asset = str(
            row.get(
                "asset"
            )
            or row.get(
                "marginCoin"
            )
            or row.get(
                "coin"
            )
            or ""
        ).strip().upper()

        if (
            asset
            and asset
            != R36F14_DEMO_ASSET
        ):
            continue

        for key in (
            "availableBalance",
            "available",
            "availableMargin",
            "balance",
        ):
            value = row.get(
                key
            )

            if value is None:
                continue

            try:
                balance = D(
                    value
                )

                if balance >= 0:
                    return balance

            except Exception:
                continue

    raise RuntimeError(
        "Unable to extract WEEX demo available balance"
    )


def build_market_snapshot(
    mark_price,
    candles,
):
    ema_snapshot = (
        calculate_ema_signal(
            candles
        )
    )

    long_diagnostics = (
        calculate_tp_diagnostics(
            "LONG",
            mark_price,
            candles,
        )
    )

    short_diagnostics = (
        calculate_tp_diagnostics(
            "SHORT",
            mark_price,
            candles,
        )
    )

    command_preview = (
        build_telegram_command_preview(
            ema_snapshot,
            long_diagnostics,
            short_diagnostics,
        )
    )

    return {
        "mark_price":
            mark_price,
        "ema_snapshot":
            ema_snapshot,
        "long_diagnostics":
            long_diagnostics,
        "short_diagnostics":
            short_diagnostics,
        "command_preview":
            command_preview,
    }


def select_direction_snapshot(
    direction,
    long_diagnostics,
    short_diagnostics,
):
    direction = str(
        direction
        or ""
    ).strip().upper()

    if direction == "LONG":
        diagnostics = (
            long_diagnostics
        )

    elif direction == "SHORT":
        diagnostics = (
            short_diagnostics
        )

    else:
        return {
            "valid": False,
            "reason":
                "INVALID_SELECTED_DIRECTION",
            "direction":
                direction,
        }

    return select_tp_snapshot(
        direction,
        diagnostics,
    )


def build_entry_authorization_preview(
    direction,
    available_balance,
    mark_price,
    selected_snapshot,
):
    direction = str(
        direction
        or ""
    ).strip().upper()

    leverage = (
        LEVERAGE_LONG
        if direction == "LONG"
        else LEVERAGE_SHORT
    )

    quantity = (
        calculate_entry_quantity(
            available_balance,
            mark_price,
            leverage,
        )
    )

    if quantity < MIN_QUANTITY:
        return {
            "valid": False,
            "reason":
                "ENTRY_QUANTITY_BELOW_MINIMUM",
            "direction":
                direction,
            "quantity":
                quantity,
        }

    allocation = (
        allocate_tp_quantities(
            quantity
        )
    )

    if not allocation.get(
        "valid"
    ):
        return {
            "valid": False,
            "reason":
                allocation.get(
                    "reason"
                ),
            "direction":
                direction,
            "quantity":
                quantity,
            "allocation":
                allocation,
        }

    stop_price = (
        calculate_protective_stop(
            direction,
            mark_price,
        )
    )

    risk_preview = (
        build_stop_risk_preview(
            direction,
            mark_price,
            stop_price,
        )
    )

    if not risk_preview.get(
        "valid"
    ):
        return {
            "valid": False,
            "reason":
                risk_preview.get(
                    "reason"
                ),
            "direction":
                direction,
            "quantity":
                quantity,
            "stop_price":
                stop_price,
            "risk_preview":
                risk_preview,
        }

    budget_preview = (
        build_stop_loss_budget_preview(
            available_balance,
            quantity,
            mark_price,
            stop_price,
        )
    )

    if not budget_preview.get(
        "valid"
    ):
        return {
            "valid": False,
            "reason":
                budget_preview.get(
                    "reason"
                ),
            "direction":
                direction,
            "quantity":
                quantity,
            "stop_price":
                stop_price,
            "risk_preview":
                risk_preview,
            "budget_preview":
                budget_preview,
        }

    if not (
        isinstance(
            selected_snapshot,
            dict,
        )
        and selected_snapshot.get(
            "valid"
        )
    ):
        return {
            "valid": False,
            "reason":
                "SELECTED_TP_SNAPSHOT_INVALID",
            "direction":
                direction,
            "quantity":
                quantity,
        }

    return {
        "valid": True,
        "reason":
            "ENTRY_AUTHORIZATION_PREVIEW_VALID",
        "direction":
            direction,
        "quantity":
            quantity,
        "mark_price":
            mark_price,
        "leverage":
            leverage,
        "stop_price":
            stop_price,
        "tp1":
            selected_snapshot.get(
                "tp1"
            ),
        "tp2":
            selected_snapshot.get(
                "tp2"
            ),
        "tp3_mode":
            selected_snapshot.get(
                "tp3_mode"
            ),
        "allocation":
            allocation,
        "risk_preview":
            risk_preview,
        "budget_preview":
            budget_preview,
    }


def build_demo_payload(
    authorization_preview,
):
    preview = (
        authorization_preview
        if isinstance(
            authorization_preview,
            dict,
        )
        else {}
    )

    if not preview.get(
        "valid"
    ):
        return {
            "valid": False,
            "reason":
                "AUTHORIZATION_PREVIEW_INVALID",
            "payload": None,
        }

    direction = str(
        preview.get(
            "direction"
        )
        or ""
    ).strip().upper()

    side = (
        "BUY"
        if direction == "LONG"
        else "SELL"
        if direction == "SHORT"
        else ""
    )

    if not side:
        return {
            "valid": False,
            "reason":
                "INVALID_DIRECTION",
            "payload": None,
        }

    payload = {
        "symbol":
            R36F14_DEMO_SYMBOL,
        "side":
            side,
        "positionSide":
            direction,
        "type":
            "MARKET",
        "quantity":
            decimal_to_string(
                preview.get(
                    "quantity"
                )
            ),
        "tpTriggerPrice":
            decimal_to_string(
                preview.get(
                    "tp1"
                )
            ),
        "slTriggerPrice":
            decimal_to_string(
                preview.get(
                    "stop_price"
                )
            ),
        "TpWorkingType":
            "MARK_PRICE",
        "SlWorkingType":
            "MARK_PRICE",
    }

    return {
        "valid": True,
        "reason":
            "DEMO_PAYLOAD_BUILT",
        "payload":
            payload,
    }


async def build_fresh_demo_preview():
    mark_price = (
        await load_mark_price()
    )

    candles = (
        await load_historical_candles()
    )

    available_balance = (
        await load_available_demo_balance()
    )

    market_snapshot = (
        build_market_snapshot(
            mark_price,
            candles,
        )
    )

    command_preview = (
        market_snapshot.get(
            "command_preview"
        )
        or {}
    )

    direction = (
        command_preview.get(
            "direction"
        )
    )

    if not command_preview.get(
        "authorized_preview"
    ):
        return {
            "valid": False,
            "reason":
                command_preview.get(
                    "reason",
                    "COMMAND_NOT_AUTHORIZED",
                ),
            "market_snapshot":
                market_snapshot,
            "command_preview":
                command_preview,
        }

    selected_snapshot = (
        select_direction_snapshot(
            direction,
            market_snapshot.get(
                "long_diagnostics",
                {},
            ),
            market_snapshot.get(
                "short_diagnostics",
                {},
            ),
        )
    )

    authorization_preview = (
        build_entry_authorization_preview(
            direction,
            available_balance,
            mark_price,
            selected_snapshot,
        )
    )

    if not authorization_preview.get(
        "valid"
    ):
        return {
            "valid": False,
            "reason":
                authorization_preview.get(
                    "reason"
                ),
            "market_snapshot":
                market_snapshot,
            "command_preview":
                command_preview,
            "selected_snapshot":
                selected_snapshot,
            "authorization_preview":
                authorization_preview,
        }

    demo_preview = (
        build_demo_payload(
            authorization_preview
        )
    )

    return {
        "valid":
            bool(
                demo_preview.get(
                    "valid"
                )
            ),
        "reason":
            demo_preview.get(
                "reason"
            ),
        "market_snapshot":
            market_snapshot,
        "command_preview":
            command_preview,
        "selected_snapshot":
            selected_snapshot,
        "authorization_preview":
            authorization_preview,
        "payload":
            demo_preview.get(
                "payload"
            ),
    }


async def r36f151_runtime_cycle():
    global MARK_PRICE
    global AVAILABLE_BALANCE
    global LONG_DIAGNOSTICS
    global SHORT_DIAGNOSTICS
    global EMA_SIGNAL_SNAPSHOT
    global TELEGRAM_COMMAND_PREVIEW

    line()

    log(
        "R36F.15.1 FRESH MARKET REEVALUATION START"
    )

    try:
        MARK_PRICE = (
            await load_mark_price()
        )

        candles = (
            await load_historical_candles()
        )

        AVAILABLE_BALANCE = (
            await load_available_demo_balance()
        )

    except Exception as exc:
        log(
            "R36F.15.1 MARKET/ACCOUNT REFRESH FAILED = "
            + str(exc)
        )

        return {
            "valid": False,
            "reason":
                "MARKET_ACCOUNT_REFRESH_FAILED",
            "error":
                str(exc),
        }

    market_snapshot = (
        build_market_snapshot(
            MARK_PRICE,
            candles,
        )
    )

    EMA_SIGNAL_SNAPSHOT = (
        market_snapshot.get(
            "ema_snapshot"
        )
        or {}
    )

    LONG_DIAGNOSTICS = (
        market_snapshot.get(
            "long_diagnostics"
        )
        or {}
    )

    SHORT_DIAGNOSTICS = (
        market_snapshot.get(
            "short_diagnostics"
        )
        or {}
    )

    TELEGRAM_COMMAND_PREVIEW = (
        market_snapshot.get(
            "command_preview"
        )
        or {}
    )

    log(
        "R36F.15.1 MARK PRICE = "
        + decimal_to_string(
            MARK_PRICE
        )
    )

    log(
        "R36F.15.1 AVAILABLE BALANCE = "
        + decimal_to_string(
            AVAILABLE_BALANCE
        )
    )

    log(
        "R36F.15.1 EMA SNAPSHOT = "
        + canonical_json(
            EMA_SIGNAL_SNAPSHOT
        )
    )

    log(
        "R36F.15.1 LONG VALID CLUSTERS = "
        + str(
            LONG_DIAGNOSTICS.get(
                "valid_cluster_count",
                0,
            )
        )
    )

    log(
        "R36F.15.1 SHORT VALID CLUSTERS = "
        + str(
            SHORT_DIAGNOSTICS.get(
                "valid_cluster_count",
                0,
            )
        )
    )

    log(
        "R36F.15.1 TELEGRAM COMMAND PREVIEW = "
        + canonical_json(
            TELEGRAM_COMMAND_PREVIEW
        )
    )

    direction = (
        TELEGRAM_COMMAND_PREVIEW.get(
            "direction"
        )
    )

    if not TELEGRAM_COMMAND_PREVIEW.get(
        "authorized_preview"
    ):
        log(
            "R36F.15.1 TRADE NOT ELIGIBLE = "
            + str(
                TELEGRAM_COMMAND_PREVIEW.get(
                    "reason"
                )
            )
        )

        return {
            "valid": False,
            "reason":
                "TRADE_NOT_ELIGIBLE",
            "market_snapshot":
                market_snapshot,
        }

    selected_snapshot = (
        select_direction_snapshot(
            direction,
            LONG_DIAGNOSTICS,
            SHORT_DIAGNOSTICS,
        )
    )

    if not selected_snapshot.get(
        "valid"
    ):
        log(
            "R36F.15.1 SELECTED TP SNAPSHOT INVALID"
        )

        return {
            "valid": False,
            "reason":
                "SELECTED_TP_SNAPSHOT_INVALID",
            "selected_snapshot":
                selected_snapshot,
        }

    authorization_preview = (
        build_entry_authorization_preview(
            direction,
            AVAILABLE_BALANCE,
            MARK_PRICE,
            selected_snapshot,
        )
    )

    if not authorization_preview.get(
        "valid"
    ):
        log(
            "R36F.15.1 ENTRY AUTHORIZATION NOT ELIGIBLE = "
            + str(
                authorization_preview.get(
                    "reason"
                )
            )
        )

        return {
            "valid": False,
            "reason":
                "TRADE_NOT_ELIGIBLE",
            "authorization_preview":
                authorization_preview,
        }

    demo_preview = (
        build_demo_payload(
            authorization_preview
        )
    )

    if not demo_preview.get(
        "valid"
    ):
        log(
            "R36F.15.1 DEMO PREVIEW BUILD FAILED"
        )

        return {
            "valid": False,
            "reason":
                "DEMO_PREVIEW_BUILD_FAILED",
            "demo_preview":
                demo_preview,
        }

    result = (
        await submit_r36f15_demo_order(
            demo_preview,
            TELEGRAM_COMMAND_PREVIEW,
        )
    )

    log(
        "R36F.15.1 DEMO RESULT = "
        + canonical_json(
            result
        )
    )

    return {
        "valid": True,
        "reason":
            "RUNTIME_CYCLE_COMPLETED",
        "result":
            result,
        "selected_snapshot":
            selected_snapshot,
        "authorization_preview":
            authorization_preview,
        "demo_preview":
            demo_preview,
    }


async def r36f151_runtime_loop():
    while True:
        try:
            await r36f151_runtime_cycle()

        except Exception as exc:
            log(
                "R36F.15.1 RUNTIME LOOP ERROR = "
                + str(exc)
            )

        await asyncio.sleep(
            R36F151_REEVALUATION_SECONDS
        )


# ============================================================
# R1.8 CORRECTED MAIN.PY — PART 2 END
# ============================================================
