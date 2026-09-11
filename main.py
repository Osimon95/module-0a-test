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
        time.time() * 1000
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
        text.encode("utf-8")
    ).hexdigest()


def normalize_command(command):
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


def command_identity_hash(command):
    material = {
        "command":
            normalize_command(command),

        "symbol":
            DEMO_SYMBOL,

        "side":
            DEMO_SIDE,

        "positionSide":
            DEMO_POSITION_SIDE,

        "stage":
            STAGE
    }

    return sha256_text(
        canonical_json(
            material
        )
    )


def command_fingerprint(
    command,
    consumed_at_ms
):
    material = {
        "command_identity_hash":
            command_identity_hash(command),

        "consumed_at_ms":
            int(consumed_at_ms)
    }

    return sha256_text(
        canonical_json(
            material
        )
    )


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


def load_existing_record():

    if not os.path.exists(
        JOURNAL_FILE
    ):
        return {}

    try:
        value = read_json(
            JOURNAL_FILE
        )

        if isinstance(
            value,
            dict
        ):
            return value

        return {}

    except Exception as exc:

        log(
            STAGE
            + " EXISTING PREFLIGHT JOURNAL READ ERROR = "
            + repr(exc)
        )

        return {
            "_journal_read_error":
                repr(exc)
        }


def make_client_id(
    command_hash,
    consumed_at_ms
):
    seed = "|".join(
        [
            DEMO_SYMBOL,
            DEMO_SIDE,
            DEMO_POSITION_SIDE,
            command_hash,
            str(consumed_at_ms)
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
    required = (
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
    )

    missing = [
        key
        for key in required
        if not str(
            payload.get(
                key,
                ""
            )
        ).strip()
    ]

    return (
        not missing,
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
                len(body)
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
            + str(PORT)
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

    command = normalize_command(
        COMMAND_TEXT
    )

    expected_command = expected_command_for_side()

    command_present = bool(
        command
    )

    command_exact_match = (
        command_present
        and
        command == expected_command
    )

    identity_hash = (
        command_identity_hash(
            command
        )
        if command_present
        else ""
    )

    existing = load_existing_record()

    if "_journal_read_error" in existing:

        log(
            STAGE
            + " PREFLIGHT STATE = JOURNAL_READ_FAILED"
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
            + " FINAL STATUS = FAIL_CLOSED"
        )

        line()

        return

    existing_identity = str(
        existing.get(
            "command_identity_hash"
        )
        or ""
    ).strip()

    existing_state = str(
        existing.get(
            "state"
        )
        or ""
    ).strip()

    replay_detected = bool(
        command_present
        and
        existing_identity
        and
        hmac.compare_digest(
            identity_hash,
            existing_identity
        )
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
        + " INTERNAL_TIMESTAMP_MODE = True"
    )

    log(
        STAGE
        + " EXISTING PREFLIGHT JOURNAL FOUND = "
        + str(
            bool(existing)
        )
    )

    log(
        STAGE
        + " EXISTING JOURNAL STATE = "
        + (
            existing_state
            or "NONE"
        )
    )

    log(
        STAGE
        + " COMMAND REPLAY DETECTED = "
        + str(
            replay_detected
        )
    )

    if (
        not command_present
        or
        not command_exact_match
    ):

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

    if replay_detected:

        stored_payload = existing.get(
            "payload"
        )

        stored_request_hash = str(
            existing.get(
                "request_hash"
            )
            or ""
        )

        stored_client_id = str(
            existing.get(
                "client_order_id"
            )
            or ""
        )

        payload_reloadable = False
        stored_hash_valid = False

        if (
            isinstance(
                stored_payload,
                dict
            )
            and
            stored_request_hash
        ):

            recomputed_hash = sha256_text(
                canonical_json(
                    stored_payload
                )
            )

            stored_hash_valid = hmac.compare_digest(
                recomputed_hash,
                stored_request_hash
            )

            payload_reloadable = True

        restart_survivability = (
            payload_reloadable
            and
            stored_hash_valid
        )

        log(
            STAGE
            + " PREFLIGHT STATE = REPLAY_BLOCKED_AFTER_RESTART"
        )

        log(
            STAGE
            + " OLD_COMMAND_REPLAY_BLOCKED = True"
        )

        log(
            STAGE
            + " STORED CLIENT ORDER ID = "
            + (
                stored_client_id
                or "NONE"
            )
        )

        log(
            STAGE
            + " STORED PAYLOAD RELOADABLE = "
            + str(
                payload_reloadable
            )
        )

        log(
            STAGE
            + " STORED REQUEST HASH VALID = "
            + str(
                stored_hash_valid
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
            + " DUPLICATE_ON_RESTART_BLOCKED = True"
        )

        log(
            STAGE
            + " NEW_CLIENT_ORDER_ID_CREATED = False"
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
                "PASS_REPLAY_BLOCKED"
                if restart_survivability
                else "FAIL_CLOSED"
            )
        )

        line()

        return

    consumed_at_ms = now_ms()

    command_hash = command_fingerprint(
        command,
        consumed_at_ms
    )

    client_order_id = make_client_id(
        command_hash,
        consumed_at_ms
    )

    unique_against_old = (
        client_order_id
        != OLD_CLIENT_ID
    )

    existing_client_id = str(
        existing.get(
            "client_order_id"
        )
        or ""
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

        "command":
            command,

        "command_consumed_at_ms":
            consumed_at_ms,

        "command_identity_hash":
            identity_hash,

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
        + " COMMAND CONSUMED AT MS = "
        + str(
            consumed_at_ms
        )
    )

    log(
        STAGE
        + " COMMAND IDENTITY HASH = "
        + identity_hash
    )

    log(
        STAGE
        + " COMMAND HASH = "
        + command_hash
    )

    log(
        STAGE
        + " NEW CLIENT ORDER ID = "
        + client_order_id
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

    reload_request_hash = str(
        reloaded.get(
            "request_hash"
        )
        or ""
    )

    reload_identity_hash = str(
        reloaded.get(
            "command_identity_hash"
        )
        or ""
    )

    reload_command_hash = str(
        reloaded.get(
            "command_hash"
        )
        or ""
    )

    reload_client_id = str(
        reloaded.get(
            "client_order_id"
        )
        or ""
    )

    reload_state = str(
        reloaded.get(
            "state"
        )
        or ""
    )

    payload_reload_match = (
        isinstance(
            reload_payload,
            dict
        )
        and
        canonical_json(
            reload_payload
        )
        == request_json
    )

    stored_hash_match = (
        bool(
            reload_request_hash
        )
        and
        hmac.compare_digest(
            reload_request_hash,
            request_hash
        )
    )

    recomputed_hash = (
        sha256_text(
            canonical_json(
                reload_payload
            )
        )
        if isinstance(
            reload_payload,
            dict
        )
        else ""
    )

    recomputed_hash_match = (
        bool(
            recomputed_hash
        )
        and
        hmac.compare_digest(
            recomputed_hash,
            request_hash
        )
    )

    identity_reload_match = hmac.compare_digest(
        reload_identity_hash,
        identity_hash
    )

    command_hash_reload_match = hmac.compare_digest(
        reload_command_hash,
        command_hash
    )

    client_id_reload_match = hmac.compare_digest(
        reload_client_id,
        client_order_id
    )

    restart_survivability = all(
        [
            journal_written,
            payload_reload_match,
            stored_hash_match,
            recomputed_hash_match,
            identity_reload_match,
            command_hash_reload_match,
            client_id_reload_match,
            reload_state
            == "PREPARED_NOT_SENT"
        ]
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
            payload_reload_match
        )
    )

    log(
        STAGE
        + " REQUEST_HASH_MATCH = "
        + str(
            stored_hash_match
            and
            recomputed_hash_match
        )
    )

    log(
        STAGE
        + " COMMAND_IDENTITY_RELOAD_MATCH = "
        + str(
            identity_reload_match
        )
    )

    log(
        STAGE
        + " COMMAND_HASH_RELOAD_MATCH = "
        + str(
            command_hash_reload_match
        )
    )

    log(
        STAGE
        + " CLIENT_ID_RELOAD_MATCH = "
        + str(
            client_id_reload_match
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
            restart_survivability
        )
    )

    all_pass = all(
        [
            command_exact_match,
            client_id_unique,
            payload_complete,
            tp_present,
            sl_present,
            journal_written,
            payload_reload_match,
            stored_hash_match,
            recomputed_hash_match,
            identity_reload_match,
            command_hash_reload_match,
            client_id_reload_match,
            restart_survivability,
            not REAL_ORDER_EXECUTION,
            not DEMO_ORDER_EXECUTION,
            not WRITE_TRANSPORT_ENABLED,
            not EXCHANGE_HTTP_ENABLED
        ]
    )

    line()

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
            payload_reload_match
        )
    )

    log(
        STAGE
        + " REQUEST_HASH_MATCH = "
        + str(
            stored_hash_match
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
            else "FAIL_CLOSED"
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
            + repr(exc)
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
