#!/usr/bin/env python3
"""
R36F.15.9-MERGED

Frozen baseline:
    R36F.15.5-MERGED

Purpose:
    Preserve the proven R36F.15.5-MERGED architecture while adding
    the R36F.15.8 fresh-command / anti-replay / durable pre-POST
    journal / restart-survivability protections required before a
    second controlled WEEX demo trade.

Critical safety:
    - Production real-money execution remains disabled.
    - Production exchange mutation remains disabled.
    - Demo execution requires all frozen strategy gates.
    - Demo execution additionally requires the R36F.15.9 second-demo
      arm phrase and a fresh one-shot command token.
    - A durable second-demo PREPARED record is written before POST.
    - Request payload hash is verified after reload before POST.
    - Restart/replay of the same second-demo command token is blocked.
    - Current WEEX demo position/open-order reconciliation runs before
      considering a second entry.
    - Historical first-demo FILLED evidence is preserved but is not by
      itself treated as an active position.
"""

import os
import sys
import json
import time
import hmac
import hashlib
import base64
import asyncio
import threading
import traceback
from decimal import Decimal, ROUND_DOWN, ROUND_UP
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode

try:
    import aiohttp
except Exception:
    aiohttp = None

try:
    from telegram import Bot
except Exception:
    Bot = None


STAGE = "R36F.15.9-MERGED"

REAL_ORDER_EXECUTION = False
DEMO = False
WRITE_TRANSPORT_ENABLED = False
PRODUCTION_EXCHANGE_MUTATION_ENABLED = False

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True

PORT = int(
    os.getenv(
        "PORT",
        "10000"
    )
)

WEEX_BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api.weex.com"
).rstrip("/")

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    ""
).strip()

WEEX_API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    ""
).strip()

WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    ""
).strip()

SYMBOL = os.getenv(
    "R36F12_SYMBOL",
    "BTCUSDT"
).strip().upper()

PUBLIC_SYMBOL = os.getenv(
    "R36F12_PUBLIC_SYMBOL",
    "cmt_btcusdt"
).strip()

R36F14_DEMO_SYMBOL = os.getenv(
    "R36F14_DEMO_SYMBOL",
    "BTCSUSDT"
).strip().upper()

R36F14_DEMO_BALANCE_ENDPOINT = (
    "/capi/v3/sim/balance"
)

R36F14_DEMO_POSITIONS_ENDPOINT = (
    "/capi/v3/sim/position/allPosition"
)

R36F14_DEMO_ORDER_HISTORY_ENDPOINT = (
    "/capi/v3/sim/order/history"
)

R36F14_DEMO_ORDER_ENDPOINT = (
    "/capi/v3/sim/order"
)

QTY_STEP = Decimal(
    os.getenv(
        "R36F12_QTY_STEP",
        "0.0001"
    )
)

MIN_QTY = Decimal(
    os.getenv(
        "R36F12_MIN_QTY",
        "0.0001"
    )
)

PRICE_STEP = Decimal(
    os.getenv(
        "R36F12_PRICE_STEP",
        "0.1"
    )
)

ENTRY_BALANCE_PERCENT = Decimal(
    os.getenv(
        "R36F12_ENTRY_BALANCE_PERCENT",
        "5"
    )
)

PYRAMID_MAX_ADDS = int(
    os.getenv(
        "R36F12_PYRAMID_MAX_ADDS",
        "1"
    )
)

PYRAMID_ADD_BALANCE_PERCENT = Decimal(
    os.getenv(
        "R36F12_PYRAMID_ADD_BALANCE_PERCENT",
        "5"
    )
)

BACKUP_MAX_ORDERS = int(
    os.getenv(
        "R36F12_BACKUP_MAX_ORDERS",
        "3"
    )
)

BACKUP_BALANCE_PERCENT = Decimal(
    os.getenv(
        "R36F12_BACKUP_BALANCE_PERCENT",
        "5"
    )
)

BACKUP_BUFFER_PERCENT = Decimal(
    os.getenv(
        "R36F12_BACKUP_BUFFER_PERCENT",
        "0.3"
    )
)

EXPOSURE_CAP_PERCENT = Decimal(
    os.getenv(
        "R36F12_EXPOSURE_CAP_PERCENT",
        "35"
    )
)

TP1_PROGRESS_PERCENT = Decimal(
    os.getenv(
        "R36F12_TP1_PROGRESS_PERCENT",
        "20"
    )
)

TP2_PROGRESS_PERCENT = Decimal(
    os.getenv(
        "R36F12_TP2_PROGRESS_PERCENT",
        "50"
    )
)

TRAILING_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "R36F12_TRAILING_DISTANCE_PERCENT",
        "0.20"
    )
)

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv(
        "R36F12_SIGNAL_EXPIRY_SECONDS",
        "120"
    )
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv(
        "R36F12_LOSS_COOLDOWN_SECONDS",
        "300"
    )
)

CLUSTER_TOLERANCE_PERCENT = Decimal(
    os.getenv(
        "R36F12_CLUSTER_TOLERANCE_PERCENT",
        "0.20"
    )
)

MIN_CLUSTER_TOUCHES = int(
    os.getenv(
        "R36F12_MIN_CLUSTER_TOUCHES",
        "2"
    )
)

HISTORICAL_LIMIT = int(
    os.getenv(
        "R36F12_HISTORICAL_LIMIT",
        "1000"
    )
)

INTERVAL = os.getenv(
    "R36F12_INTERVAL",
    "1m"
).strip()

R36F151_REEVALUATION_SECONDS = int(
    os.getenv(
        "R36F151_REEVALUATION_SECONDS",
        "60"
    )
)

R36F12_TELEGRAM_ALERT_ENABLED = (
    os.getenv(
        "R36F12_TELEGRAM_ALERT_ENABLED",
        "false"
    )
    .strip()
    .lower()
    in {
        "1",
        "true",
        "yes",
        "on"
    }
)

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    ""
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    ""
).strip()

R36F12_TELEGRAM_COMMAND_TEXT = os.getenv(
    "R36F12_TELEGRAM_COMMAND_TEXT",
    ""
).strip()

R36F15_DEMO_ARM = (
    os.getenv(
        "R36F15_DEMO_ARM",
        "false"
    )
    .strip()
    .lower()
    in {
        "1",
        "true",
        "yes",
        "on"
    }
)

R36F15_DEMO_JOURNAL_FILE = os.getenv(
    "R36F15_DEMO_JOURNAL_FILE",
    "/var/data/r36f_state/r36f15_demo_dispatch_journal.json"
).strip()

R36F155_TARGET_DEMO_ORDER_ID = os.getenv(
    "R36F155_TARGET_DEMO_ORDER_ID",
    "792989056504955607"
).strip()

R36F155_LAST_RECONCILIATION = {}

R36F159_DEMO_ARM_PHRASE = (
    "ARM_SECOND_WEEX_DEMO_ORDER"
)

R36F159_DEMO_ARM = os.getenv(
    "R36F159_DEMO_ARM",
    ""
).strip()

R36F159_COMMAND_TOKEN = os.getenv(
    "R36F159_COMMAND_TOKEN",
    ""
).strip()

R36F159_SECOND_DEMO_JOURNAL_FILE = os.getenv(
    "R36F159_SECOND_DEMO_JOURNAL_FILE",
    "/var/data/r36f_state/r36f159_second_demo_journal.json"
).strip()

R36F159_LAST_CURRENT_EXPOSURE = {}

R36F159_SECOND_DEMO_ENABLED = (
    R36F159_DEMO_ARM
    ==
    R36F159_DEMO_ARM_PHRASE
)

R36F159_COMMAND_TOKEN_PRESENT = bool(
    R36F159_COMMAND_TOKEN
)

R36F159_SECOND_DEMO_POST_COUNT = 0

R36F159_REAL_MONEY_POST_COUNT = 0

R36F159_PRODUCTION_MUTATION_COUNT = 0


def now_iso():
    return datetime.now(
        timezone.utc
    ).isoformat()


def now_ms():
    return int(
        time.time()
        * 1000
    )


def log(
    message
):
    print(
        now_iso(),
        message,
        flush=True
    )


def line():
    print(
        "-" * 100,
        flush=True
    )


def D(
    value,
    default="0"
):
    try:
        if isinstance(
            value,
            Decimal
        ):
            return value

        if value is None:
            return Decimal(
                str(default)
            )

        return Decimal(
            str(value)
        )

    except Exception:
        return Decimal(
            str(default)
        )


def decimal_string(
    value
):
    value = D(
        value
    )

    text = format(
        value,
        "f"
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


def canonical_json(
    value
):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )


def sha256_text(
    value
):
    return hashlib.sha256(
        str(
            value
        ).encode(
            "utf-8"
        )
    ).hexdigest()


def atomic_write_json(
    path,
    value
):
    directory = os.path.dirname(
        path
    )

    if directory:
        os.makedirs(
            directory,
            exist_ok=True
        )

    temp_path = (
        path
        + ".tmp"
    )

    with open(
        temp_path,
        "w",
        encoding="utf-8"
    ) as handle:
        json.dump(
            value,
            handle,
            sort_keys=True,
            indent=2
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        temp_path,
        path
    )


def read_json_file(
    path
):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as handle:
        return json.load(
            handle
        )


def normalize_command_text(
    value
):
    return " ".join(
        str(
            value
            or ""
        )
        .strip()
        .upper()
        .split()
    )


def r36f159_command_token_identity():
    if not R36F159_COMMAND_TOKEN_PRESENT:
        return ""

    material = {
        "stage":
            STAGE,

        "symbol":
            R36F14_DEMO_SYMBOL,

        "token":
            R36F159_COMMAND_TOKEN
    }

    return sha256_text(
        canonical_json(
            material
        )
    )


def r36f159_build_command_hash(
    normalized_command,
    token_identity
):
    material = {
        "stage":
            STAGE,

        "symbol":
            R36F14_DEMO_SYMBOL,

        "command":
            normalize_command_text(
                normalized_command
            ),

        "token_identity":
            token_identity
    }

    return sha256_text(
        canonical_json(
            material
        )
    )


def r36f159_build_client_order_id(
    direction,
    command_hash
):
    prefix = (
        "R36F159-"
        + str(
            direction
            or "UNKNOWN"
        )
        .strip()
        .upper()
        + "-"
    )

    return (
        prefix
        + command_hash[:12].upper()
    )


def r36f159_read_second_demo_journal():
    if not os.path.exists(
        R36F159_SECOND_DEMO_JOURNAL_FILE
    ):
        return {}

    try:
        value = read_json_file(
            R36F159_SECOND_DEMO_JOURNAL_FILE
        )

        if isinstance(
            value,
            dict
        ):
            return value

    except Exception as exc:
        log(
            "R36F.15.9 SECOND DEMO JOURNAL READ ERROR = "
            + repr(
                exc
            )
        )

    return {}


def r36f159_request_payload_hash(
    payload
):
    return sha256_text(
        canonical_json(
            payload
        )
    )


def r36f159_second_demo_preflight(
    payload,
    direction,
    command_preview
):
    result = {
        "ok":
            False,

        "reason":
            None,

        "journal_written":
            False,

        "journal_reload_match":
            False,

        "request_hash_match":
            False,

        "restart_survivability":
            False,

        "client_order_id":
            None,

        "request_hash":
            None,

        "token_identity":
            None,

        "command_hash":
            None
    }

    if not R36F159_SECOND_DEMO_ENABLED:
        result[
            "reason"
        ] = (
            "R36F159_SECOND_DEMO_ARM_NOT_ENABLED"
        )

        return result

    if not R36F159_COMMAND_TOKEN_PRESENT:
        result[
            "reason"
        ] = (
            "R36F159_COMMAND_TOKEN_MISSING"
        )

        return result

    if not isinstance(
        payload,
        dict
    ):
        result[
            "reason"
        ] = (
            "R36F159_PAYLOAD_MISSING"
        )

        return result

    normalized_command = normalize_command_text(
        (
            command_preview
            or {}
        ).get(
            "raw_command"
        )
        or R36F12_TELEGRAM_COMMAND_TEXT
    )

    if not normalized_command:
        result[
            "reason"
        ] = (
            "R36F159_COMMAND_TEXT_MISSING"
        )

        return result

    token_identity = (
        r36f159_command_token_identity()
    )

    command_hash = (
        r36f159_build_command_hash(
            normalized_command,
            token_identity
        )
    )

    existing = (
        r36f159_read_second_demo_journal()
    )

    existing_token_identity = str(
        existing.get(
            "token_identity"
        )
        or ""
    )

    existing_command_hash = str(
        existing.get(
            "command_hash"
        )
        or ""
    )

    existing_state = str(
        existing.get(
            "state"
        )
        or ""
    )

    if (
        existing_token_identity
        and
        hmac.compare_digest(
            token_identity,
            existing_token_identity
        )
    ):
        result[
            "reason"
        ] = (
            "R36F159_COMMAND_TOKEN_REPLAY_BLOCKED"
        )

        result[
            "restart_survivability"
        ] = True

        result[
            "existing_state"
        ] = (
            existing_state
        )

        return result

    if (
        existing_command_hash
        and
        hmac.compare_digest(
            command_hash,
            existing_command_hash
        )
    ):
        result[
            "reason"
        ] = (
            "R36F159_COMMAND_HASH_REPLAY_BLOCKED"
        )

        result[
            "restart_survivability"
        ] = True

        result[
            "existing_state"
        ] = (
            existing_state
        )

        return result

    client_order_id = (
        r36f159_build_client_order_id(
            direction,
            command_hash
        )
    )

    payload = dict(
        payload
    )

    payload[
        "clientOrderId"
    ] = client_order_id

    request_hash = (
        r36f159_request_payload_hash(
            payload
        )
    )

    record = {
        "stage":
            STAGE,

        "state":
            "PREPARED_NOT_SENT",

        "created_at":
            now_iso(),

        "created_at_ms":
            now_ms(),

        "symbol":
            R36F14_DEMO_SYMBOL,

        "direction":
            direction,

        "command":
            normalized_command,

        "token_identity":
            token_identity,

        "command_hash":
            command_hash,

        "client_order_id":
            client_order_id,

        "payload":
            payload,

        "request_hash":
            request_hash,

        "real_order_execution":
            False,

        "production_mutation":
            False
    }

    atomic_write_json(
        R36F159_SECOND_DEMO_JOURNAL_FILE,
        record
    )

    result[
        "journal_written"
    ] = os.path.exists(
        R36F159_SECOND_DEMO_JOURNAL_FILE
    )

    try:
        reloaded = read_json_file(
            R36F159_SECOND_DEMO_JOURNAL_FILE
        )

    except Exception as exc:
        result[
            "reason"
        ] = (
            "R36F159_JOURNAL_RELOAD_FAILED:"
            + repr(
                exc
            )
        )

        return result

    reload_payload = reloaded.get(
        "payload"
    )

    reload_hash = str(
        reloaded.get(
            "request_hash"
        )
        or ""
    )

    reload_token_identity = str(
        reloaded.get(
            "token_identity"
        )
        or ""
    )

    reload_command_hash = str(
        reloaded.get(
            "command_hash"
        )
        or ""
    )

    reload_client_order_id = str(
        reloaded.get(
            "client_order_id"
        )
        or ""
    )

    payload_match = (
        isinstance(
            reload_payload,
            dict
        )
        and
        canonical_json(
            reload_payload
        )
        ==
        canonical_json(
            payload
        )
    )

    recomputed_hash = (
        r36f159_request_payload_hash(
            reload_payload
        )
        if isinstance(
            reload_payload,
            dict
        )
        else ""
    )

    hash_match = (
        bool(
            reload_hash
        )
        and
        hmac.compare_digest(
            reload_hash,
            request_hash
        )
        and
        bool(
            recomputed_hash
        )
        and
        hmac.compare_digest(
            recomputed_hash,
            request_hash
        )
    )

    token_match = hmac.compare_digest(
        reload_token_identity,
        token_identity
    )

    command_hash_match = hmac.compare_digest(
        reload_command_hash,
        command_hash
    )

    client_id_match = hmac.compare_digest(
        reload_client_order_id,
        client_order_id
    )

    restart_survivability = all(
        [
            result[
                "journal_written"
            ],
            payload_match,
            hash_match,
            token_match,
            command_hash_match,
            client_id_match,
            str(
                reloaded.get(
                    "state"
                )
                or ""
            )
            ==
            "PREPARED_NOT_SENT"
        ]
    )

    result.update(
        {
            "ok":
                restart_survivability,

            "reason":
                (
                    None
                    if restart_survivability
                    else
                    "R36F159_PREFLIGHT_VERIFICATION_FAILED"
                ),

            "journal_reload_match":
                payload_match,

            "request_hash_match":
                hash_match,

            "restart_survivability":
                restart_survivability,

            "client_order_id":
                client_order_id,

            "request_hash":
                request_hash,

            "token_identity":
                token_identity,

            "command_hash":
                command_hash,

            "payload":
                payload
        }
    )

    return result


def r36f159_mark_second_demo_journal(
    state,
    extra=None
):
    record = (
        r36f159_read_second_demo_journal()
    )

    if not record:
        return False

    record[
        "state"
    ] = str(
        state
    )

    record[
        "updated_at"
    ] = now_iso()

    record[
        "updated_at_ms"
    ] = now_ms()

    if isinstance(
        extra,
        dict
    ):
        record.update(
            extra
        )

    atomic_write_json(
        R36F159_SECOND_DEMO_JOURNAL_FILE,
        record
    )

    return True


def r36f155_order_id(
    row
):
    if not isinstance(
        row,
        dict
    ):
        return ""

    for key in (
        "orderId",
        "order_id",
        "id"
    ):
        value = row.get(
            key
        )

        if value not in (
            None,
            ""
        ):
            return str(
                value
            )

    return ""


def r36f155_order_status(
    row
):
    if not isinstance(
        row,
        dict
    ):
        return ""

    return str(
        row.get(
            "status"
        )
        or
        row.get(
            "state"
        )
        or
        ""
    ).strip().upper()


def r36f155_order_direction(
    row
):
    if not isinstance(
        row,
        dict
    ):
        return None

    position_side = str(
        row.get(
            "positionSide"
        )
        or
        row.get(
            "position_side"
        )
        or
        ""
    ).strip().upper()

    if position_side in {
        "LONG",
        "SHORT"
    }:
        return position_side

    side = str(
        row.get(
            "side"
        )
        or
        ""
    ).strip().upper()

    if side in {
        "BUY",
        "LONG"
    }:
        return "LONG"

    if side in {
        "SELL",
        "SHORT"
    }:
        return "SHORT"

    return None


def r36f155_position_direction(
    row
):
    if not isinstance(
        row,
        dict
    ):
        return None

    for key in (
        "positionSide",
        "holdSide",
        "side",
        "direction"
    ):
        value = str(
            row.get(
                key
            )
            or
            ""
        ).strip().upper()

        if value in {
            "LONG",
            "BUY"
        }:
            return "LONG"

        if value in {
            "SHORT",
            "SELL"
        }:
            return "SHORT"

    return None


def r36f155_position_size(
    row
):
    if not isinstance(
        row,
        dict
    ):
        return D(
            "0"
        )

    for key in (
        "positionAmt",
        "total",
        "size",
        "qty",
        "quantity",
        "available"
    ):
        if row.get(
            key
        ) not in (
            None,
            ""
        ):
            try:
                return abs(
                    D(
                        row.get(
                            key
                        )
                    )
                )

            except Exception:
                continue

    return D(
        "0"
    )


def r36f155_normalize_rows(
    data
):
    if isinstance(
        data,
        list
    ):
        return data

    if not isinstance(
        data,
        dict
    ):
        return []

    for key in (
        "data",
        "rows",
        "list",
        "result",
        "orders",
        "positions"
    ):
        value = data.get(
            key
        )

        if isinstance(
            value,
            list
        ):
            return value

        if isinstance(
            value,
            dict
        ):
            for nested_key in (
                "rows",
                "list",
                "data",
                "orders",
                "positions"
            ):
                nested = value.get(
                    nested_key
                )

                if isinstance(
                    nested,
                    list
                ):
                    return nested

    return []


def r36f155_extract_protection_fields(
    order
):
    if not isinstance(
        order,
        dict
    ):
        return {
            "tp_field":
                None,

            "tp_value":
                None,

            "sl_field":
                None,

            "sl_value":
                None
        }

    tp_candidates = (
        "tpTriggerPrice",
        "takeProfitPrice",
        "takeProfit",
        "tpPrice",
        "tp"
    )

    sl_candidates = (
        "slTriggerPrice",
        "stopLossPrice",
        "stopLoss",
        "slPrice",
        "sl"
    )

    tp_field = None
    tp_value = None

    sl_field = None
    sl_value = None

    for key in tp_candidates:
        if order.get(
            key
        ) not in (
            None,
            ""
        ):
            tp_field = key
            tp_value = order.get(
                key
            )
            break

    for key in sl_candidates:
        if order.get(
            key
        ) not in (
            None,
            ""
        ):
            sl_field = key
            sl_value = order.get(
                key
            )
            break

    return {
        "tp_field":
            tp_field,

        "tp_value":
            tp_value,

        "sl_field":
            sl_field,

        "sl_value":
            sl_value
    }


class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self
    ):
        body = json.dumps(
            {
                "stage":
                    STAGE,

                "status":
                    "running",

                "real_execution":
                    REAL_ORDER_EXECUTION,

                "demo":
                    DEMO,

                "write_transport":
                    WRITE_TRANSPORT_ENABLED,

                "production_mutation":
                    PRODUCTION_EXCHANGE_MUTATION_ENABLED,

                "r36f159_second_demo_arm":
                    R36F159_SECOND_DEMO_ENABLED
            }
        ).encode(
            "utf-8"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(
                len(
                    body
                )
            )
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format,
        *args
    ):
        return


def start_health_server():

    def run():
        try:
            server = HTTPServer(
                (
                    "0.0.0.0",
                    PORT
                ),
                HealthHandler
            )

            log(
                STAGE
                + ": HEALTH SERVER STARTED ON PORT "
                + str(
                    PORT
                )
            )

            server.serve_forever()

        except Exception as exc:
            log(
                STAGE
                + ": HEALTH SERVER ERROR = "
                + repr(
                    exc
                )
            )

    thread = threading.Thread(
        target=run,
        daemon=True
    )

    thread.start()


def weex_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body=""
):
    prehash = (
        str(
            timestamp
        )
        +
        str(
            method
        ).upper()
        +
        str(
            request_path
        )
    )

    if query_string:
        prehash += (
            "?"
            +
            query_string
        )

    prehash += str(
        body
        or ""
    )

    digest = hmac.new(
        WEEX_API_SECRET.encode(
            "utf-8"
        ),
        prehash.encode(
            "utf-8"
        ),
        hashlib.sha256
    ).digest()

    return base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )


def weex_headers(
    timestamp,
    method,
    request_path,
    query_string="",
    body=""
):
    return {
        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            weex_signature(
                timestamp,
                method,
                request_path,
                query_string,
                body
            ),

        "ACCESS-TIMESTAMP":
            str(
                timestamp
            ),

        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,

        "Content-Type":
            "application/json",

        "locale":
            "en-US"
    }


async def weex_get(
    request_path,
    params=None,
    timeout_seconds=15
):
    if aiohttp is None:
        raise RuntimeError(
            "aiohttp is not available"
        )

    if not request_path.startswith(
        "/"
    ):
        raise RuntimeError(
            "WEEX GET request_path must start with /"
        )

    params = (
        params
        if isinstance(
            params,
            dict
        )
        else {}
    )

    query_string = urlencode(
        params
    )

    timestamp = now_ms()

    headers = weex_headers(
        timestamp,
        "GET",
        request_path,
        query_string,
        ""
    )

    url = (
        WEEX_BASE_URL
        +
        request_path
    )

    if query_string:
        url += (
            "?"
            +
            query_string
        )

    timeout = aiohttp.ClientTimeout(
        total=timeout_seconds
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:
        async with session.get(
            url,
            headers=headers
        ) as response:
            text = await response.text()

            try:
                data = json.loads(
                    text
                )

            except Exception:
                data = {
                    "_raw":
                        text
                }

            if response.status < 200 or response.status >= 300:
                raise RuntimeError(
                    "WEEX GET HTTP "
                    + str(
                        response.status
                    )
                    + ": "
                    + text
                )

            return data


async def weex_public_get(
    request_path,
    params=None,
    timeout_seconds=15
):
    if aiohttp is None:
        raise RuntimeError(
            "aiohttp is not available"
        )

    params = (
        params
        if isinstance(
            params,
            dict
        )
        else {}
    )

    query_string = urlencode(
        params
    )

    url = (
        WEEX_BASE_URL
        +
        request_path
    )

    if query_string:
        url += (
            "?"
            +
            query_string
        )

    timeout = aiohttp.ClientTimeout(
        total=timeout_seconds
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:
        async with session.get(
            url
        ) as response:
            text = await response.text()

            try:
                data = json.loads(
                    text
                )

            except Exception:
                data = {
                    "_raw":
                        text
                }

            if response.status < 200 or response.status >= 300:
                raise RuntimeError(
                    "WEEX PUBLIC GET HTTP "
                    + str(
                        response.status
                    )
                    + ": "
                    + text
                )

            return data


async def weex_demo_post(
    request_path,
    payload,
    timeout_seconds=15
):
    global R36F159_SECOND_DEMO_POST_COUNT
    global R36F159_REAL_MONEY_POST_COUNT
    global R36F159_PRODUCTION_MUTATION_COUNT

    if aiohttp is None:
        raise RuntimeError(
            "aiohttp is not available"
        )

    if request_path != R36F14_DEMO_ORDER_ENDPOINT:
        R36F159_PRODUCTION_MUTATION_COUNT += 1

        raise RuntimeError(
            "R36F.15.9 FIREBREAK: "
            "only WEEX demo order endpoint is allowed"
        )

    if not request_path.startswith(
        "/capi/v3/sim/"
    ):
        R36F159_PRODUCTION_MUTATION_COUNT += 1

        raise RuntimeError(
            "R36F.15.9 FIREBREAK: "
            "production exchange mutation forbidden"
        )

    if REAL_ORDER_EXECUTION:
        R36F159_REAL_MONEY_POST_COUNT += 1

        raise RuntimeError(
            "R36F.15.9 FIREBREAK: "
            "real order execution must remain disabled"
        )

    body = canonical_json(
        payload
    )

    timestamp = now_ms()

    headers = weex_headers(
        timestamp,
        "POST",
        request_path,
        "",
        body
    )

    url = (
        WEEX_BASE_URL
        +
        request_path
    )

    timeout = aiohttp.ClientTimeout(
        total=timeout_seconds
    )

    R36F159_SECOND_DEMO_POST_COUNT += 1

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:
        async with session.post(
            url,
            data=body,
            headers=headers
        ) as response:
            text = await response.text()

            try:
                data = json.loads(
                    text
                )

            except Exception:
                data = {
                    "_raw":
                        text
                }

            return {
                "http_status":
                    response.status,

                "data":
                    data,

                "raw":
                    text
            }


def r36f153_history_rows(
    data
):
    return r36f155_normalize_rows(
        data
    )


async def r36f153_lookup_demo_order_by_client_id(
    client_order_id
):
    if not client_order_id:
        return None

    try:
        data = await weex_get(
            R36F14_DEMO_ORDER_HISTORY_ENDPOINT,
            {
                "symbol":
                    R36F14_DEMO_SYMBOL,

                "limit":
                    1000,

                "page":
                    0
            }
        )

    except Exception as exc:
        log(
            "R36F.15.3 DEMO HISTORY LOOKUP ERROR = "
            + repr(
                exc
            )
        )

        return None

    rows = r36f153_history_rows(
        data
    )

    for row in rows:
        if not isinstance(
            row,
            dict
        ):
            continue

        row_client_id = str(
            row.get(
                "clientOrderId"
            )
            or
            row.get(
                "client_order_id"
            )
            or
            ""
        ).strip()

        if (
            row_client_id
            and
            row_client_id
            ==
            str(
                client_order_id
            )
        ):
            return row

    return None


async def r36f153_reconcile_demo_journal(
    journal
):
    if not isinstance(
        journal,
        dict
    ):
        return {
            "status":
                "NO_JOURNAL",

            "terminal":
                False,

            "unresolved":
                False,

            "order":
                None
        }

    state = str(
        journal.get(
            "state"
        )
        or
        ""
    ).strip().upper()

    client_order_id = str(
        journal.get(
            "client_order_id"
        )
        or
        ""
    ).strip()

    if state in {
        "COMPLETED",
        "REJECTED"
    }:
        return {
            "status":
                state,

            "terminal":
                True,

            "unresolved":
                False,

            "order":
                journal.get(
                    "response"
                )
        }

    if state in {
        "PREPARED",
        "AMBIGUOUS",
        "PREPARED_NOT_SENT"
    }:
        row = await r36f153_lookup_demo_order_by_client_id(
            client_order_id
        )

        if row is not None:
            return {
                "status":
                    "FOUND",

                "terminal":
                    True,

                "unresolved":
                    False,

                "order":
                    row
            }

        return {
            "status":
                "NOT_FOUND",

            "terminal":
                False,

            "unresolved":
                (
                    state
                    ==
                    "AMBIGUOUS"
                ),

            "order":
                None
        }

    return {
        "status":
            (
                state
                or
                "UNKNOWN"
            ),

        "terminal":
            False,

        "unresolved":
            True,

        "order":
            None
    }


async def r36f155_reconcile_existing_demo_exposure():
    global R36F155_LAST_RECONCILIATION

    result = {
        "target_order_found":
            False,

        "target_order_status":
            None,

        "target_order_direction":
            None,

        "target_order_symbol":
            None,

        "target_order_original_qty":
            None,

        "target_order_executed_qty":
            None,

        "target_order_avg_price":
            None,

        "target_order_client_id":
            None,

        "matching_position_found":
            False,

        "matching_position_count":
            0,

        "demo_position_rows":
            0,

        "duplicate_entry_blocked":
            True,

        "duplicate_block_reason":
            "RECONCILIATION_NOT_COMPLETED",

        "safe_to_consider_new_entry":
            False,

        "protection_verified":
            False,

        "protection_reason":
            "NOT_CHECKED",

        "history_read_ok":
            False,

        "position_read_ok":
            False
    }

    line()

    log(
        "R36F.15.5 POST-ORDER RECONCILIATION START"
    )

    log(
        "R36F.15.5 TARGET DEMO ORDER ID = "
        + R36F155_TARGET_DEMO_ORDER_ID
    )

    history_rows = []

    try:
        history_data = await weex_get(
            R36F14_DEMO_ORDER_HISTORY_ENDPOINT,
            {
                "symbol":
                    R36F14_DEMO_SYMBOL,

                "limit":
                    1000,

                "page":
                    0
            }
        )

        history_rows = r36f155_normalize_rows(
            history_data
        )

        result[
            "history_read_ok"
        ] = True

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
        log(
            "R36F.15.5 DEMO ORDER HISTORY READ = FAIL"
        )

        log(
            "R36F.15.5 DEMO ORDER HISTORY ERROR = "
            + repr(
                exc
            )
        )

    target_order = None

    for row in history_rows:
        if (
            r36f155_order_id(
                row
            )
            ==
            R36F155_TARGET_DEMO_ORDER_ID
        ):
            target_order = row
            break

    if target_order is not None:
        result[
            "target_order_found"
        ] = True

        result[
            "target_order_status"
        ] = (
            r36f155_order_status(
                target_order
            )
        )

        result[
            "target_order_direction"
        ] = (
            r36f155_order_direction(
                target_order
            )
        )

        result[
            "target_order_symbol"
        ] = str(
            target_order.get(
                "symbol"
            )
            or
            ""
        )

        result[
            "target_order_original_qty"
        ] = (
            target_order.get(
                "origQty"
            )
            or
            target_order.get(
                "quantity"
            )
            or
            target_order.get(
                "qty"
            )
        )

        result[
            "target_order_executed_qty"
        ] = (
            target_order.get(
                "executedQty"
            )
            or
            target_order.get(
                "filledQty"
            )
            or
            target_order.get(
                "filled"
            )
        )

        result[
            "target_order_avg_price"
        ] = (
            target_order.get(
                "avgPrice"
            )
            or
            target_order.get(
                "priceAvg"
            )
        )

        result[
            "target_order_client_id"
        ] = (
            target_order.get(
                "clientOrderId"
            )
            or
            target_order.get(
                "client_order_id"
            )
        )

        log(
            "R36F.15.5 TARGET ORDER FOUND = True"
        )

        log(
            "R36F.15.5 ORDER ID = "
            + str(
                R36F155_TARGET_DEMO_ORDER_ID
            )
        )

        log(
            "R36F.15.5 ORDER SYMBOL = "
            + str(
                result[
                    "target_order_symbol"
                ]
            )
        )

        log(
            "R36F.15.5 ORDER DIRECTION = "
            + str(
                result[
                    "target_order_direction"
                ]
            )
        )

        log(
            "R36F.15.5 ORDER STATUS = "
            + str(
                result[
                    "target_order_status"
                ]
            )
        )

        log(
            "R36F.15.5 ORDER ORIGINAL QTY = "
            + str(
                result[
                    "target_order_original_qty"
                ]
            )
        )

        log(
            "R36F.15.5 ORDER EXECUTED QTY = "
            + str(
                result[
                    "target_order_executed_qty"
                ]
            )
        )

        log(
            "R36F.15.5 ORDER AVG PRICE = "
            + str(
                result[
                    "target_order_avg_price"
                ]
            )
        )

        protection = (
            r36f155_extract_protection_fields(
                target_order
            )
        )

        log(
            "R36F.15.5 ORDER TP FIELD = "
            + str(
                protection[
                    "tp_field"
                ]
            )
        )

        log(
            "R36F.15.5 ORDER TP VALUE = "
            + str(
                protection[
                    "tp_value"
                ]
            )
        )

        log(
            "R36F.15.5 ORDER SL FIELD = "
            + str(
                protection[
                    "sl_field"
                ]
            )
        )

        log(
            "R36F.15.5 ORDER SL VALUE = "
            + str(
                protection[
                    "sl_value"
                ]
            )
        )

        if (
            protection[
                "tp_field"
            ]
            and
            protection[
                "sl_field"
            ]
        ):
            result[
                "protection_reason"
            ] = (
                "TP_SL_FIELDS_RETURNED_BY_DEMO_ORDER_HISTORY"
            )

        else:
            result[
                "protection_reason"
            ] = (
                "TP_SL_NOT_RETURNED_BY_DEMO_ORDER_HISTORY"
            )

    else:
        log(
            "R36F.15.5 TARGET ORDER FOUND = False"
        )

    positions = []

    try:
        position_data = await weex_get(
            R36F14_DEMO_POSITIONS_ENDPOINT,
            {
                "symbol":
                    R36F14_DEMO_SYMBOL
            }
        )

        positions = r36f155_normalize_rows(
            position_data
        )

        result[
            "position_read_ok"
        ] = True

        result[
            "demo_position_rows"
        ] = len(
            positions
        )

        log(
            "R36F.15.5 DEMO POSITION READ = PASS"
        )

        log(
            "R36F.15.5 DEMO POSITION ROWS = "
            + str(
                len(
                    positions
                )
            )
        )

    except Exception as exc:
        log(
            "R36F.15.5 DEMO POSITION READ = FAIL"
        )

        log(
            "R36F.15.5 DEMO POSITION ERROR = "
            + repr(
                exc
            )
        )

    target_direction = (
        result[
            "target_order_direction"
        ]
        or
        "LONG"
    )

    matching_positions = []

    for row in positions:
        if not isinstance(
            row,
            dict
        ):
            continue

        symbol = str(
            row.get(
                "symbol"
            )
            or
            ""
        ).strip().upper()

        direction = (
            r36f155_position_direction(
                row
            )
        )

        size = r36f155_position_size(
            row
        )

        if (
            symbol
            ==
            R36F14_DEMO_SYMBOL
            and
            direction
            ==
            target_direction
            and
            size
            >
            0
        ):
            matching_positions.append(
                row
            )

    result[
        "matching_position_count"
    ] = len(
        matching_positions
    )

    result[
        "matching_position_found"
    ] = bool(
        matching_positions
    )

    log(
        "R36F.15.5 MATCHING POSITION FOUND = "
        + str(
            result[
                "matching_position_found"
            ]
        )
    )

    log(
        "R36F.15.5 MATCHING POSITION COUNT = "
        + str(
            result[
                "matching_position_count"
            ]
        )
    )

    if not (
        result[
            "history_read_ok"
        ]
        and
        result[
            "position_read_ok"
        ]
    ):
        result[
            "duplicate_entry_blocked"
        ] = True

        result[
            "duplicate_block_reason"
        ] = (
            "READ_ONLY_RECONCILIATION_INCOMPLETE"
        )

    elif result[
        "matching_position_found"
    ]:
        result[
            "duplicate_entry_blocked"
        ] = True

        result[
            "duplicate_block_reason"
        ] = (
            "POSITION_ALREADY_EXISTS"
        )

    elif result[
        "target_order_found"
    ]:
        status = str(
            result[
                "target_order_status"
            ]
            or
            ""
        ).upper()

        if status in {
            "NEW",
            "PENDING",
            "OPEN",
            "PARTIALLY_FILLED",
            "PARTIAL_FILLED",
            "PARTIALLYFILLED"
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

        else:
            result[
                "duplicate_entry_blocked"
            ] = False

            result[
                "duplicate_block_reason"
            ] = (
                "TARGET_ORDER_TERMINAL_NO_ACTIVE_POSITION"
            )

            result[
                "safe_to_consider_new_entry"
            ] = True

    else:
        active_positions = []

        for row in positions:
            if not isinstance(
                row,
                dict
            ):
                continue

            if r36f155_position_size(
                row
            ) > 0:
                active_positions.append(
                    row
                )

        if active_positions:
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
                "NO_EXISTING_DEMO_EXPOSURE_FOUND"
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
        "R36F.15.5 PROTECTION VERIFIED = "
        + str(
            result[
                "protection_verified"
            ]
        )
    )

    log(
        "R36F.15.5 PROTECTION REASON = "
        + str(
            result[
                "protection_reason"
            ]
        )
    )

    log(
        "R36F.15.5 REAL MONEY EXECUTION = False"
    )

    R36F155_LAST_RECONCILIATION = (
        dict(
            result
        )
    )

    line()

    return result


async def r36f159_reconcile_current_demo_exposure():
    global R36F159_LAST_CURRENT_EXPOSURE

    result = {
        "history_read_ok":
            False,

        "position_read_ok":
            False,

        "history_rows":
            0,

        "position_rows":
            0,

        "active_demo_positions":
            0,

        "open_demo_orders":
            0,

        "duplicate_entry_blocked":
            True,

        "duplicate_block_reason":
            "CURRENT_EXPOSURE_RECONCILIATION_NOT_COMPLETED",

        "safe_to_consider_new_entry":
            False
    }

    line()

    log(
        "R36F.15.9 CURRENT DEMO EXPOSURE RECONCILIATION START"
    )

    history_rows = []

    try:
        history_data = await weex_get(
            R36F14_DEMO_ORDER_HISTORY_ENDPOINT,
            {
                "symbol":
                    R36F14_DEMO_SYMBOL,

                "limit":
                    1000,

                "page":
                    0
            }
        )

        history_rows = r36f155_normalize_rows(
            history_data
        )

        result[
            "history_read_ok"
        ] = True

        result[
            "history_rows"
        ] = len(
            history_rows
        )

        log(
            "R36F.15.9 HISTORY READ OK = True"
        )

        log(
            "R36F.15.9 HISTORY ROWS = "
            + str(
                len(
                    history_rows
                )
            )
        )

    except Exception as exc:
        log(
            "R36F.15.9 HISTORY READ OK = False"
        )

        log(
            "R36F.15.9 HISTORY READ ERROR = "
            + repr(
                exc
            )
        )

    position_rows = []

    try:
        position_data = await weex_get(
            R36F14_DEMO_POSITIONS_ENDPOINT,
            {
                "symbol":
                    R36F14_DEMO_SYMBOL
            }
        )

        position_rows = r36f155_normalize_rows(
            position_data
        )

        result[
            "position_read_ok"
        ] = True

        result[
            "position_rows"
        ] = len(
            position_rows
        )

        log(
            "R36F.15.9 POSITION READ OK = True"
        )

        log(
            "R36F.15.9 POSITION ROWS = "
            + str(
                len(
                    position_rows
                )
            )
        )

    except Exception as exc:
        log(
            "R36F.15.9 POSITION READ OK = False"
        )

        log(
            "R36F.15.9 POSITION READ ERROR = "
            + repr(
                exc
            )
        )

    active_positions = []

    for row in position_rows:
        if not isinstance(
            row,
            dict
        ):
            continue

        symbol = str(
            row.get(
                "symbol"
            )
            or
            ""
        ).strip().upper()

        size = r36f155_position_size(
            row
        )

        if (
            symbol
            ==
            R36F14_DEMO_SYMBOL
            and
            size
            >
            0
        ):
            active_positions.append(
                row
            )

    result[
        "active_demo_positions"
    ] = len(
        active_positions
    )

    open_statuses = {
        "NEW",
        "PENDING",
        "OPEN",
        "PARTIALLY_FILLED",
        "PARTIAL_FILLED",
        "PARTIALLYFILLED",
        "CREATED",
        "ACCEPTED",
        "WORKING"
    }

    open_orders = []

    for row in history_rows:
        if not isinstance(
            row,
            dict
        ):
            continue

        symbol = str(
            row.get(
                "symbol"
            )
            or
            ""
        ).strip().upper()

        status = r36f155_order_status(
            row
        )

        if (
            symbol
            ==
            R36F14_DEMO_SYMBOL
            and
            status
            in
            open_statuses
        ):
            open_orders.append(
                row
            )

    result[
        "open_demo_orders"
    ] = len(
        open_orders
    )

    if not (
        result[
            "history_read_ok"
        ]
        and
        result[
            "position_read_ok"
        ]
    ):
        result[
            "duplicate_entry_blocked"
        ] = True

        result[
            "duplicate_block_reason"
        ] = (
            "CURRENT_EXPOSURE_READ_INCOMPLETE"
        )

    elif active_positions:
        result[
            "duplicate_entry_blocked"
        ] = True

        result[
            "duplicate_block_reason"
        ] = (
            "CURRENT_ACTIVE_DEMO_POSITION_EXISTS"
        )

    elif open_orders:
        result[
            "duplicate_entry_blocked"
        ] = True

        result[
            "duplicate_block_reason"
        ] = (
            "CURRENT_OPEN_DEMO_ORDER_EXISTS"
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
        "R36F.15.9 ACTIVE DEMO POSITIONS = "
        + str(
            result[
                "active_demo_positions"
            ]
        )
    )

    log(
        "R36F.15.9 OPEN DEMO ORDERS = "
        + str(
            result[
                "open_demo_orders"
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

    log(
        "R36F.15.9 DUPLICATE BLOCK REASON = "
        + str(
            result[
                "duplicate_block_reason"
            ]
        )
    )

    log(
        "R36F.15.9 SAFE TO CONSIDER NEW ENTRY = "
        + str(
            result[
                "safe_to_consider_new_entry"
            ]
        )
    )

    R36F159_LAST_CURRENT_EXPOSURE = dict(
        result
    )

    line()

    return result


def r36f159_second_demo_journal_replay_status():
    journal = r36f159_read_second_demo_journal()

    if not journal:
        return {
            "journal_found":
                False,

            "replay_blocked":
                False,

            "reason":
                "NO_SECOND_DEMO_JOURNAL"
        }

    current_token_identity = (
        r36f159_command_token_identity()
    )

    stored_token_identity = str(
        journal.get(
            "token_identity"
        )
        or ""
    )

    state = str(
        journal.get(
            "state"
        )
        or ""
    ).strip().upper()

    token_matches = (
        bool(
            current_token_identity
        )
        and
        bool(
            stored_token_identity
        )
        and
        hmac.compare_digest(
            current_token_identity,
            stored_token_identity
        )
    )

    replay_blocked = (
        token_matches
        and
        state
        in {
            "PREPARED_NOT_SENT",
            "POST_ATTEMPTED",
            "AMBIGUOUS",
            "COMPLETED",
            "ACCEPTED",
            "REJECTED"
        }
    )

    return {
        "journal_found":
            True,

        "state":
            state,

        "token_matches":
            token_matches,

        "replay_blocked":
            replay_blocked,

        "reason":
            (
                "SECOND_DEMO_COMMAND_TOKEN_ALREADY_CONSUMED"
                if replay_blocked
                else
                "SECOND_DEMO_JOURNAL_PRESENT_DIFFERENT_TOKEN_OR_NONBLOCKING_STATE"
            )
    }


def normalize_price_down(
    price
):
    value = D(
        price
    )

    if PRICE_STEP <= 0:
        return value

    steps = (
        value
        /
        PRICE_STEP
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return (
        steps
        *
        PRICE_STEP
    )


def normalize_price_up(
    price
):
    value = D(
        price
    )

    if PRICE_STEP <= 0:
        return value

    steps = (
        value
        /
        PRICE_STEP
    ).to_integral_value(
        rounding=ROUND_UP
    )

    return (
        steps
        *
        PRICE_STEP
    )


def normalize_qty_down(
    qty
):
    value = D(
        qty
    )

    if QTY_STEP <= 0:
        return value

    steps = (
        value
        /
        QTY_STEP
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return (
        steps
        *
        QTY_STEP
    )


def normalized_min_qty():
    value = normalize_qty_down(
        MIN_QTY
    )

    if value < MIN_QTY:
        value += QTY_STEP

    return value


def percent_of(
    value,
    percent
):
    return (
        D(
            value
        )
        *
        D(
            percent
        )
        /
        D(
            "100"
        )
    )


def safe_bool(
    value
):
    if isinstance(
        value,
        bool
    ):
        return value

    return str(
        value
    ).strip().lower() in {
        "1",
        "true",
        "yes",
        "on"
    }


def first_number(
    value
):
    if isinstance(
        value,
        (
            int,
            float,
            Decimal
        )
    ):
        return D(
            value
        )

    if isinstance(
        value,
        str
    ):
        try:
            return D(
                value
            )

        except Exception:
            return None

    return None


def recursive_find_numbers(
    value,
    keys
):
    keys = {
        str(
            key
        ).lower()
        for key in keys
    }

    found = []

    if isinstance(
        value,
        dict
    ):
        for key, item in value.items():
            if str(
                key
            ).lower() in keys:
                number = first_number(
                    item
                )

                if number is not None:
                    found.append(
                        number
                    )

            found.extend(
                recursive_find_numbers(
                    item,
                    keys
                )
            )

    elif isinstance(
        value,
        list
    ):
        for item in value:
            found.extend(
                recursive_find_numbers(
                    item,
                    keys
                )
            )

    return found


def recursive_find_strings(
    value,
    keys
):
    keys = {
        str(
            key
        ).lower()
        for key in keys
    }

    found = []

    if isinstance(
        value,
        dict
    ):
        for key, item in value.items():
            if str(
                key
            ).lower() in keys:
                if item is not None:
                    found.append(
                        str(
                            item
                        )
                    )

            found.extend(
                recursive_find_strings(
                    item,
                    keys
                )
            )

    elif isinstance(
        value,
        list
    ):
        for item in value:
            found.extend(
                recursive_find_strings(
                    item,
                    keys
                )
            )

    return found


def response_success_hint(
    response
):
    if not isinstance(
        response,
        dict
    ):
        return False

    for key in (
        "success",
        "ok"
    ):
        if key in response:
            value = response.get(
                key
            )

            if isinstance(
                value,
                bool
            ):
                return value

            if str(
                value
            ).strip().lower() in {
                "true",
                "1",
                "yes"
            }:
                return True

    code_candidates = recursive_find_strings(
        response,
        {
            "code",
            "errorCode",
            "status"
        }
    )

    for code in code_candidates:
        normalized = str(
            code
        ).strip().upper()

        if normalized in {
            "0",
            "00000",
            "SUCCESS",
            "OK",
            "200"
        }:
            return True

    order_ids = recursive_find_strings(
        response,
        {
            "orderId",
            "order_id"
        }
    )

    return bool(
        order_ids
    )


def extract_order_id(
    response
):
    values = recursive_find_strings(
        response,
        {
            "orderId",
            "order_id"
        }
    )

    if values:
        return values[0]

    return None


def extract_client_order_id(
    response
):
    values = recursive_find_strings(
        response,
        {
            "clientOrderId",
            "client_order_id"
        }
    )

    if values:
        return values[0]

    return None


def ema(
    values,
    period
):
    if not values:
        return None

    if len(
        values
    ) < period:
        return None

    multiplier = (
        D(
            "2"
        )
        /
        D(
            str(
                period
                +
                1
            )
        )
    )

    current = (
        sum(
            values[
                :period
            ]
        )
        /
        D(
            str(
                period
            )
        )
    )

    for value in values[
        period:
    ]:
        current = (
            (
                value
                -
                current
            )
            *
            multiplier
            +
            current
        )

    return current


def ema_structure(
    ema19,
    ema50,
    ema200
):
    if (
        ema19 is None
        or
        ema50 is None
        or
        ema200 is None
    ):
        return {
            "structure":
                "UNKNOWN",

            "ideal_direction":
                None,

            "separation_percent":
                None
        }

    separation = (
        abs(
            ema19
            -
            ema50
        )
        /
        ema50
        *
        D(
            "100"
        )
        if ema50
        else
        D(
            "0"
        )
    )

    if (
        ema19
        >
        ema50
        >
        ema200
    ):
        return {
            "structure":
                "STRONG_BULLISH",

            "ideal_direction":
                "LONG",

            "separation_percent":
                separation
        }

    if (
        ema19
        <
        ema50
        <
        ema200
    ):
        return {
            "structure":
                "STRONG_BEARISH",

            "ideal_direction":
                "SHORT",

            "separation_percent":
                separation
        }

    if (
        ema19
        >
        ema50
        and
        ema50
        <=
        ema200
    ):
        return {
            "structure":
                "EARLY_BULLISH",

            "ideal_direction":
                None,

            "separation_percent":
                separation
        }

    if (
        ema19
        <
        ema50
        and
        ema50
        >=
        ema200
    ):
        return {
            "structure":
                "EARLY_BEARISH",

            "ideal_direction":
                None,

            "separation_percent":
                separation
        }

    return {
        "structure":
            "MIXED",

        "ideal_direction":
            None,

        "separation_percent":
            separation
    }


def normalize_candles(
    data
):
    candidates = []

    if isinstance(
        data,
        list
    ):
        candidates = data

    elif isinstance(
        data,
        dict
    ):
        for key in (
            "data",
            "rows",
            "list",
            "candles",
            "result"
        ):
            value = data.get(
                key
            )

            if isinstance(
                value,
                list
            ):
                candidates = value
                break

            if isinstance(
                value,
                dict
            ):
                for nested_key in (
                    "rows",
                    "list",
                    "data",
                    "candles"
                ):
                    nested = value.get(
                        nested_key
                    )

                    if isinstance(
                        nested,
                        list
                    ):
                        candidates = nested
                        break

                if candidates:
                    break

    normalized = []

    for row in candidates:
        timestamp = None
        open_price = None
        high = None
        low = None
        close = None
        volume = None

        if isinstance(
            row,
            list
        ):
            if len(
                row
            ) >= 5:
                timestamp = row[0]
                open_price = row[1]
                high = row[2]
                low = row[3]
                close = row[4]

                if len(
                    row
                ) > 5:
                    volume = row[5]

        elif isinstance(
            row,
            dict
        ):
            timestamp = (
                row.get(
                    "timestamp"
                )
                or
                row.get(
                    "time"
                )
                or
                row.get(
                    "ts"
                )
            )

            open_price = (
                row.get(
                    "open"
                )
                or
                row.get(
                    "o"
                )
            )

            high = (
                row.get(
                    "high"
                )
                or
                row.get(
                    "h"
                )
            )

            low = (
                row.get(
                    "low"
                )
                or
                row.get(
                    "l"
                )
            )

            close = (
                row.get(
                    "close"
                )
                or
                row.get(
                    "c"
                )
            )

            volume = (
                row.get(
                    "volume"
                )
                or
                row.get(
                    "v"
                )
            )

        try:
            if (
                high is None
                or
                low is None
                or
                close is None
            ):
                continue

            normalized.append(
                {
                    "timestamp":
                        timestamp,

                    "open":
                        D(
                            open_price
                            if open_price is not None
                            else close
                        ),

                    "high":
                        D(
                            high
                        ),

                    "low":
                        D(
                            low
                        ),

                    "close":
                        D(
                            close
                        ),

                    "volume":
                        D(
                            volume
                            if volume is not None
                            else "0"
                        )
                }
            )

        except Exception:
            continue

    def sort_key(
        row
    ):
        value = row.get(
            "timestamp"
        )

        try:
            return int(
                value
            )

        except Exception:
            return 0

    normalized.sort(
        key=sort_key
    )

    return normalized


def local_extrema(
    candles
):
    highs = []
    lows = []

    if len(
        candles
    ) < 3:
        return highs, lows

    for index in range(
        1,
        len(
            candles
        )
        -
        1
    ):
        previous_row = candles[
            index
            -
            1
        ]

        row = candles[
            index
        ]

        next_row = candles[
            index
            +
            1
        ]

        if (
            row[
                "high"
            ]
            >=
            previous_row[
                "high"
            ]
            and
            row[
                "high"
            ]
            >=
            next_row[
                "high"
            ]
        ):
            highs.append(
                row[
                    "high"
                ]
            )

        if (
            row[
                "low"
            ]
            <=
            previous_row[
                "low"
            ]
            and
            row[
                "low"
            ]
            <=
            next_row[
                "low"
            ]
        ):
            lows.append(
                row[
                    "low"
                ]
            )

    return highs, lows


def cluster_prices(
    values,
    tolerance_percent=CLUSTER_TOLERANCE_PERCENT
):
    if not values:
        return []

    sorted_values = sorted(
        [
            D(
                value
            )
            for value in values
        ]
    )

    clusters = []

    current = [
        sorted_values[0]
    ]

    for value in sorted_values[
        1:
    ]:
        average = (
            sum(
                current
            )
            /
            D(
                str(
                    len(
                        current
                    )
                )
            )
        )

        tolerance = percent_of(
            average,
            tolerance_percent
        )

        if abs(
            value
            -
            average
        ) <= tolerance:
            current.append(
                value
            )

        else:
            clusters.append(
                current
            )

            current = [
                value
            ]

    clusters.append(
        current
    )

    result = []

    for cluster in clusters:
        average = (
            sum(
                cluster
            )
            /
            D(
                str(
                    len(
                        cluster
                    )
                )
            )
        )

        result.append(
            {
                "values":
                    cluster,

                "average":
                    average,

                "touches":
                    len(
                        cluster
                    )
            }
        )

    return result


async def fetch_klines():
    endpoints = [
        (
            "/capi/v2/market/klines",
            {
                "symbol":
                    PUBLIC_SYMBOL,

                "interval":
                    INTERVAL,

                "limit":
                    HISTORICAL_LIMIT
            }
        ),
        (
            "/capi/v2/market/candles",
            {
                "symbol":
                    PUBLIC_SYMBOL,

                "interval":
                    INTERVAL,

                "limit":
                    HISTORICAL_LIMIT
            }
        )
    ]

    errors = []

    for path, params in endpoints:
        try:
            data = await weex_public_get(
                path,
                params
            )

            candles = normalize_candles(
                data
            )

            if candles:
                return candles

        except Exception as exc:
            errors.append(
                repr(
                    exc
                )
            )

    raise RuntimeError(
        "Unable to fetch WEEX public klines: "
        + " | ".join(
            errors
        )
    )


async def fetch_mark_price():
    endpoints = [
        (
            "/capi/v2/market/ticker",
            {
                "symbol":
                    PUBLIC_SYMBOL
            }
        ),
        (
            "/capi/v2/market/tickers",
            {
                "symbol":
                    PUBLIC_SYMBOL
            }
        )
    ]

    errors = []

    for path, params in endpoints:
        try:
            data = await weex_public_get(
                path,
                params
            )

            candidates = recursive_find_numbers(
                data,
                {
                    "markPrice",
                    "mark_price",
                    "last",
                    "lastPrice",
                    "close"
                }
            )

            for candidate in candidates:
                if candidate > 0:
                    return candidate

        except Exception as exc:
            errors.append(
                repr(
                    exc
                )
            )

    raise RuntimeError(
        "Unable to fetch mark price: "
        + " | ".join(
            errors
        )
    )


def extract_available_balance(
    data
):
    candidates = recursive_find_numbers(
        data,
        {
            "available",
            "availableBalance",
            "available_balance",
            "availableAmount",
            "availableMargin"
        }
    )

    positives = [
        value
        for value in candidates
        if value >= 0
    ]

    if positives:
        return positives[0]

    return None


async def load_available_balance():
    endpoints = [
        (
            "/capi/v3/account/assets",
            {
                "symbol":
                    SYMBOL
            }
        ),
        (
            "/capi/v3/account/balance",
            {
                "asset":
                    "USDT"
            }
        )
    ]

    errors = []

    for path, params in endpoints:
        try:
            data = await weex_get(
                path,
                params
            )

            balance = extract_available_balance(
                data
            )

            if balance is not None:
                return balance, data

        except Exception as exc:
            errors.append(
                repr(
                    exc
                )
            )

    raise RuntimeError(
        "Available-balance read failed: "
        + " | ".join(
            errors
        )
    )
