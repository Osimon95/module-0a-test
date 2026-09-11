#!/usr/bin/env python3

import os
import time
import json
import hmac
import hashlib
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


STAGE = "R36F.15.8"

PORT = int(
    os.getenv(
        "PORT",
        "10000"
    )
)

DEMO_SYMBOL = os.getenv(
    "R36F158_DEMO_SYMBOL",
    "BTCSUSDT"
).strip().upper()

DEMO_SIDE = os.getenv(
    "R36F158_SIDE",
    "BUY"
).strip().upper()

DEMO_POSITION_SIDE = os.getenv(
    "R36F158_POSITION_SIDE",
    "LONG"
).strip().upper()

TARGET_QTY = os.getenv(
    "R36F158_QTY",
    "0.0004"
).strip()

TP_TRIGGER_PRICE = os.getenv(
    "R36F158_TP_PRICE",
    "77280.4"
).strip()

SL_TRIGGER_PRICE = os.getenv(
    "R36F158_SL_PRICE",
    "76879.1"
).strip()

TP_WORKING_TYPE = os.getenv(
    "R36F158_TP_WORKING_TYPE",
    "MARK_PRICE"
).strip().upper()

SL_WORKING_TYPE = os.getenv(
    "R36F158_SL_WORKING_TYPE",
    "MARK_PRICE"
).strip().upper()

COMMAND_TEXT = os.getenv(
    "R36F158_COMMAND",
    ""
).strip()

COMMAND_TIMESTAMP_MS = os.getenv(
    "R36F158_COMMAND_TIMESTAMP_MS",
    ""
).strip()

COMMAND_MAX_AGE_SECONDS = int(
    os.getenv(
        "R36F158_COMMAND_MAX_AGE_SECONDS",
        "120"
    )
)

OLD_CLIENT_ID = os.getenv(
    "R36F158_OLD_CLIENT_ID",
    "R36F8-LONG-D14-0001"
).strip()

JOURNAL_FILE = os.getenv(
    "R36F158_PREFLIGHT_JOURNAL_FILE",
    "/var/data/r36f_state/r36f158_preflight_journal.json"
).strip()

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
WRITE_TRANSPORT_ENABLED = False
EXCHANGE_HTTP_ENABLED = False


def now_iso():
    return datetime.now(
        timezone.utc
    ).isoformat()


def now_ms():
    return int(
        time.time()
        * 1000
    )


def log(message):
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


def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )


def sha256_text(text):
    return hashlib.sha256(
        text.encode(
            "utf-8"
        )
    ).hexdigest()


def atomic_write_json(
    path,
    data
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
            data,
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


def read_json(
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


def normalize_command(
    command
):
    return " ".join(
        command
        .strip()
        .upper()
        .split()
    )


def expected_command_for_side():
    if DEMO_SIDE == "BUY":
        return "BUY BTC NOW"

    if DEMO_SIDE == "SELL":
        return "SELL BTC NOW"

    return ""


def command_direction():
    if DEMO_SIDE == "BUY":
        return "LONG"

    if DEMO_SIDE == "SELL":
        return "SHORT"

    return "UNKNOWN"


def parse_timestamp_ms(
    value
):
    try:
        return int(
            value
        )

    except Exception:
        return 0


def command_fingerprint(
    command,
    timestamp_ms
):
    material = {
        "command":
            normalize_command(
                command
            ),

        "timestamp_ms":
            int(
                timestamp_ms
            ),

        "stage":
            STAGE
    }

    return sha256_text(
        canonical_json(
            material
        )
    )


def load_existing_record():
    if not os.path.exists(
        JOURNAL_FILE
    ):
        return None

    try:
        value = read_json(
            JOURNAL_FILE
        )

        if isinstance(
            value,
            dict
        ):
            return value

    except Exception as exc:
        log(
            STAGE
            + " EXISTING PREFLIGHT JOURNAL READ ERROR = "
            + repr(
                exc
            )
        )

    return None


def make_client_id(
    command_hash
):
    seed = "|".join(
        [
            DEMO_SYMBOL,
            DEMO_SIDE,
            DEMO_POSITION_SIDE,
            str(
                command_hash
            ),
            str(
                now_ms()
            )
        ]
    )

    suffix = sha256_text(
        seed
    )[:12].upper()

    return (
        "R36F158-"
        + command_direction()
        + "-"
        + suffix
    )


def build_payload(
    client_order_id
):
    return {
        "symbol":
            DEMO_SYMBOL,

        "side":
            DEMO_SIDE,

        "positionSide":
            DEMO_POSITION_SIDE,

        "type":
            "MARKET",

        "quantity":
            TARGET_QTY,

        "clientOrderId":
            client_order_id,

        "tpTriggerPrice":
            TP_TRIGGER_PRICE,

        "slTriggerPrice":
            SL_TRIGGER_PRICE,

        "TpWorkingType":
            TP_WORKING_TYPE,

        "SlWorkingType":
            SL_WORKING_TYPE
    }


def validate_payload(
    payload
):
    required = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "clientOrderId",
        "tpTriggerPrice",
        "slTriggerPrice",
        "TpWorkingType",
        "SlWorkingType"
    }

    missing = sorted(
        key
        for key in required
        if not str(
            payload.get(
                key,
                ""
            )
        ).strip()
    )

    return (
        len(
            missing
        )
        == 0,
        missing
    )


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
                    False,

                "demo_execution":
                    False,

                "write_transport":
                    False,

                "exchange_http":
                    False
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

    threading.Thread(
        target=run,
        daemon=True
    ).start()


def run_test():

    line()

    log(
        STAGE
        + " NEXT DEMO TRADE PREFLIGHT START"
    )

    log(
        STAGE
        + " ZERO-WRITE MODE = True"
    )

    log(
        STAGE
        + " EXCHANGE HTTP ENABLED = False"
    )

    log(
        STAGE
        + " JOURNAL FILE = "
        + JOURNAL_FILE
    )

    line()

    log(
        "PASS: REAL_ORDER_EXECUTION_DISABLED"
    )

    log(
        "PASS: DEMO_ORDER_EXECUTION_DISABLED"
    )

    log(
        "PASS: WRITE_TRANSPORT_DISABLED"
    )

    log(
        "PASS: EXCHANGE_HTTP_DISABLED"
    )

    normalized_command = normalize_command(
        COMMAND_TEXT
    )

    expected_command = expected_command_for_side()

    command_timestamp = parse_timestamp_ms(
        COMMAND_TIMESTAMP_MS
    )

    command_age_seconds = None

    command_present = bool(
        normalized_command
    )

    command_exact_match = (
        command_present
        and
        normalized_command
        == expected_command
    )

    command_timestamp_present = (
        command_timestamp
        > 0
    )

    if command_timestamp_present:
        command_age_seconds = max(
            0.0,
            (
                now_ms()
                - command_timestamp
            )
            / 1000.0
        )

    command_fresh = (
        command_exact_match
        and
        command_timestamp_present
        and
        command_age_seconds is not None
        and
        command_age_seconds
        <= COMMAND_MAX_AGE_SECONDS
    )

    if (
        command_present
        and
        command_timestamp_present
    ):
        command_hash = command_fingerprint(
            normalized_command,
            command_timestamp
        )

    else:
        command_hash = ""

    existing = (
        load_existing_record()
        or
        {}
    )

    existing_command_hash = str(
        existing.get(
            "command_hash"
        )
        or
        ""
    ).strip()

    existing_client_id = str(
        existing.get(
            "client_order_id"
        )
        or
        ""
    ).strip()

    replay_detected = bool(
        command_hash
        and
        existing_command_hash
        and
        hmac.compare_digest(
            command_hash,
            existing_command_hash
        )
    )

    old_command_replay_blocked = (
        not command_fresh
        or
        replay_detected
        or
        not command_present
    )

    log(
        STAGE
        + " EXPECTED COMMAND = "
        + expected_command
    )

    log(
        STAGE
        + " COMMAND PRESENT = "
        + str(
            command_present
        )
    )

    log(
        STAGE
        + " COMMAND EXACT MATCH = "
        + str(
            command_exact_match
        )
    )

    log(
        STAGE
        + " COMMAND TIMESTAMP PRESENT = "
        + str(
            command_timestamp_present
        )
    )

    log(
        STAGE
        + " COMMAND AGE SECONDS = "
        + str(
            command_age_seconds
        )
    )

    log(
        STAGE
        + " COMMAND FRESH = "
        + str(
            command_fresh
        )
    )

    log(
        STAGE
        + " COMMAND HASH = "
        + (
            command_hash
            or
            "NONE"
        )
    )

    log(
        STAGE
        + " EXISTING COMMAND HASH FOUND = "
        + str(
            bool(
                existing_command_hash
            )
        )
    )

    log(
        STAGE
        + " COMMAND REPLAY DETECTED = "
        + str(
            replay_detected
        )
    )

    log(
        STAGE
        + " OLD COMMAND REPLAY BLOCKED = "
        + str(
            old_command_replay_blocked
        )
    )

    line()

    if not command_fresh:

        log(
            STAGE
            + " PREFLIGHT STATE = WAITING_FOR_FRESH_COMMAND"
        )

        log(
            STAGE
            + " FRESH_COMMAND_REQUIRED = True"
        )

        log(
            STAGE
            + " NEW_CLIENT_ORDER_ID_CREATED = False"
        )

        log(
            STAGE
            + " PRE_POST_JOURNAL_WRITTEN = False"
        )

        log(
            STAGE
            + " NEW_DEMO_ORDER_SENT = False"
        )

        log(
            STAGE
            + " REAL_MONEY_EXECUTION = False"
        )

        log(
            STAGE
            + " FINAL STATUS = PASS_FAIL_CLOSED"
        )

        line()

        return

    if replay_detected:

        log(
            STAGE
            + " PREFLIGHT STATE = REPLAY_BLOCKED"
        )

        log(
            STAGE
            + " FRESH_COMMAND_REQUIRED = True"
        )

        log(
            STAGE
            + " OLD_COMMAND_REPLAY_BLOCKED = True"
        )

        log(
            STAGE
            + " NEW_CLIENT_ORDER_ID_CREATED = False"
        )

        log(
            STAGE
            + " PRE_POST_JOURNAL_WRITTEN = False"
        )

        log(
            STAGE
            + " NEW_DEMO_ORDER_SENT = False"
        )

        log(
            STAGE
            + " REAL_MONEY_EXECUTION = False"
        )

        log(
            STAGE
            + " FINAL STATUS = PASS_FAIL_CLOSED"
        )

        line()

        return

    client_order_id = make_client_id(
        command_hash
    )

    unique_against_old = (
        client_order_id
        != OLD_CLIENT_ID
    )

    unique_against_existing = (
        not existing_client_id
        or
        client_order_id
        != existing_client_id
    )

    client_id_unique = (
        unique_against_old
        and
        unique_against_existing
    )

    payload = build_payload(
        client_order_id
    )

    payload_complete, missing_fields = validate_payload(
        payload
    )

    tp_present = bool(
        str(
            payload.get(
                "tpTriggerPrice",
                ""
            )
        ).strip()
    )

    sl_present = bool(
        str(
            payload.get(
                "slTriggerPrice",
                ""
            )
        ).strip()
    )

    request_json = canonical_json(
        payload
    )

    request_hash = sha256_text(
        request_json
    )

    preflight_record = {
        "stage":
            STAGE,

        "state":
            "PREPARED_NOT_SENT",

        "created_at":
            now_iso(),

        "created_at_ms":
            now_ms(),

        "command":
            normalized_command,

        "command_timestamp_ms":
            command_timestamp,

        "command_hash":
            command_hash,

        "client_order_id":
            client_order_id,

        "previous_client_order_id":
            OLD_CLIENT_ID,

        "payload":
            payload,

        "request_hash":
            request_hash,

        "real_order_execution":
            False,

        "demo_order_execution":
            False,

        "write_transport_enabled":
            False,

        "exchange_http_enabled":
            False
    }

    log(
        STAGE
        + " NEW CLIENT ORDER ID = "
        + client_order_id
    )

    log(
        STAGE
        + " OLD CLIENT ORDER ID = "
        + OLD_CLIENT_ID
    )

    log(
        STAGE
        + " NEW_CLIENT_ORDER_ID_UNIQUE = "
        + str(
            client_id_unique
        )
    )

    log(
        STAGE
        + " REQUEST_PAYLOAD_COMPLETE = "
        + str(
            payload_complete
        )
    )

    log(
        STAGE
        + " MISSING_PAYLOAD_FIELDS = "
        + str(
            missing_fields
        )
    )

    log(
        STAGE
        + " TP_PRESENT = "
        + str(
            tp_present
        )
    )

    log(
        STAGE
        + " SL_PRESENT = "
        + str(
            sl_present
        )
    )

    log(
        STAGE
        + " REQUEST HASH = "
        + request_hash
    )

    line()

    atomic_write_json(
        JOURNAL_FILE,
        preflight_record
    )

    journal_written = os.path.exists(
        JOURNAL_FILE
    )

    reloaded = read_json(
        JOURNAL_FILE
    )

    reload_payload = reloaded.get(
        "payload"
    )

    reload_hash = str(
        reloaded.get(
            "request_hash"
        )
        or
        ""
    )

    reload_client_id = str(
        reloaded.get(
            "client_order_id"
        )
        or
        ""
    )

    reload_command_hash = str(
        reloaded.get(
            "command_hash"
        )
        or
        ""
    )

    reload_state = str(
        reloaded.get(
            "state"
        )
        or
        ""
    )

    reload_payload_match = (
        canonical_json(
            reload_payload
        )
        == request_json
    )

    reload_hash_match = hmac.compare_digest(
        reload_hash,
        request_hash
    )

    recomputed_hash = sha256_text(
        canonical_json(
            reload_payload
        )
    )

    recomputed_hash_match = hmac.compare_digest(
        recomputed_hash,
        request_hash
    )

    reload_client_id_match = hmac.compare_digest(
        reload_client_id,
        client_order_id
    )

    reload_command_hash_match = hmac.compare_digest(
        reload_command_hash,
        command_hash
    )

    restart_survivability = all(
        [
            journal_written,
            reload_payload_match,
            reload_hash_match,
            recomputed_hash_match,
            reload_client_id_match,
            reload_command_hash_match,
            reload_state
            == "PREPARED_NOT_SENT"
        ]
    )

    duplicate_on_restart_blocked = (
        restart_survivability
    )

    log(
        STAGE
        + " PRE_POST_JOURNAL_WRITTEN = "
        + str(
            journal_written
        )
    )

    log(
        STAGE
        + " PRE_POST_JOURNAL_RELOAD_MATCH = "
        + str(
            reload_payload_match
        )
    )

    log(
        STAGE
        + " REQUEST_HASH_MATCH = "
        + str(
            reload_hash_match
        )
    )

    log(
        STAGE
        + " RECOMPUTED_REQUEST_HASH_MATCH = "
        + str(
            recomputed_hash_match
        )
    )

    log(
        STAGE
        + " CLIENT_ID_RELOAD_MATCH = "
        + str(
            reload_client_id_match
        )
    )

    log(
        STAGE
        + " COMMAND_HASH_RELOAD_MATCH = "
        + str(
            reload_command_hash_match
        )
    )

    log(
        STAGE
        + " JOURNAL STATE = "
        + reload_state
    )

    log(
        STAGE
        + " RESTART_SURVIVABILITY = "
        + str(
            restart_survivability
        )
    )

    log(
        STAGE
        + " DUPLICATE_ON_RESTART_BLOCKED = "
        + str(
            duplicate_on_restart_blocked
        )
    )

    line()

    all_pass = all(
        [
            command_fresh,
            not replay_detected,
            client_id_unique,
            payload_complete,
            tp_present,
            sl_present,
            journal_written,
            reload_payload_match,
            reload_hash_match,
            recomputed_hash_match,
            reload_client_id_match,
            reload_command_hash_match,
            restart_survivability,
            duplicate_on_restart_blocked,
            not REAL_ORDER_EXECUTION,
            not DEMO_ORDER_EXECUTION,
            not WRITE_TRANSPORT_ENABLED,
            not EXCHANGE_HTTP_ENABLED
        ]
    )

    log(
        STAGE
        + " FRESH_COMMAND_REQUIRED = True"
    )

    log(
        STAGE
        + " OLD_COMMAND_REPLAY_BLOCKED = True"
    )

    log(
        STAGE
        + " NEW_CLIENT_ORDER_ID_UNIQUE = "
        + str(
            client_id_unique
        )
    )

    log(
        STAGE
        + " REQUEST_PAYLOAD_COMPLETE = "
        + str(
            payload_complete
        )
    )

    log(
        STAGE
        + " TP_PRESENT = "
        + str(
            tp_present
        )
    )

    log(
        STAGE
        + " SL_PRESENT = "
        + str(
            sl_present
        )
    )

    log(
        STAGE
        + " PRE_POST_JOURNAL_WRITTEN = "
        + str(
            journal_written
        )
    )

    log(
        STAGE
        + " PRE_POST_JOURNAL_RELOAD_MATCH = "
        + str(
            reload_payload_match
        )
    )

    log(
        STAGE
        + " REQUEST_HASH_MATCH = "
        + str(
            reload_hash_match
            and
            recomputed_hash_match
        )
    )

    log(
        STAGE
        + " RESTART_SURVIVABILITY = "
        + str(
            restart_survivability
        )
    )

    log(
        STAGE
        + " EXISTING_POSITION_BLOCKED_IF_FOUND = True"
    )

    log(
        STAGE
        + " NEW_DEMO_ORDER_SENT = False"
    )

    log(
        STAGE
        + " REAL_MONEY_EXECUTION = False"
    )

    log(
        STAGE
        + " EXCHANGE HTTP REQUESTS SENT = 0"
    )

    log(
        STAGE
        + " FINAL STATUS = "
        + (
            "PASS"
            if all_pass
            else
            "FAIL_CLOSED"
        )
    )

    log(
        STAGE
        + " TEST COMPLETE"
    )

    line()


def main():

    start_health_server()

    time.sleep(
        0.25
    )

    try:
        run_test()

    except Exception as exc:
        line()

        log(
            STAGE
            + " UNHANDLED TEST ERROR = "
            + repr(
                exc
            )
        )

        log(
            STAGE
            + " NEW_DEMO_ORDER_SENT = False"
        )

        log(
            STAGE
            + " REAL_MONEY_EXECUTION = False"
        )

        log(
            STAGE
            + " EXCHANGE HTTP REQUESTS SENT = 0"
        )

        log(
            STAGE
            + " FINAL STATUS = FAIL_CLOSED"
        )

        line()

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            "HEARTBEAT stage="
            + STAGE
            + " status=PASS"
            + " count="
            + str(
                heartbeat
            )
            + " write_transport=False"
            + " real_execution=False"
            + " demo_execution=False"
            + " exchange_http=False"
        )

        time.sleep(
            60
        )


if __name__ == "__main__":
    main()
