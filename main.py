#!/usr/bin/env python3

import os
import json
from datetime import datetime, timezone


STAGE = "R36F.15.6"

TARGET_ORDER_ID = os.getenv(
    "R36F156_TARGET_DEMO_ORDER_ID",
    "792989056504955607",
).strip()

TARGET_CLIENT_ID = os.getenv(
    "R36F156_TARGET_CLIENT_ID",
    "R36F8-LONG-D14-0001",
).strip()

JOURNAL_FILE = os.getenv(
    "R36F15_DEMO_JOURNAL_FILE",
    "/var/data/r36f_state/r36f15_demo_dispatch_journal.json",
).strip()



def now_iso():
    return datetime.now(timezone.utc).isoformat()


def line():
    print("-" * 100, flush=True)


def log(message):
    print(
        now_iso(),
        message,
        flush=True,
    )


def load_json(path):

    if not os.path.exists(path):
        return None

    try:
        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    except Exception as exc:

        log(
            "R36F.15.6 JOURNAL READ ERROR = "
            + str(exc)
        )

        return None


def normalize_records(data):

    if data is None:
        return []

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in (
            "records",
            "entries",
            "orders",
            "journal",
            "items",
            "data",
        ):

            value = data.get(key)

            if isinstance(value, list):
                return value

        return [data]

    return []


def extract_payload(record):

    if not isinstance(record, dict):
        return None

    candidates = [
        record.get("payload"),
        record.get("request_payload"),
        record.get("demo_payload"),
        record.get("order_payload"),
        record.get("prepared_payload"),
        record.get("request"),
    ]

    for candidate in candidates:

        if isinstance(candidate, dict):
            return candidate

    return None


def find_target(records):

    candidates = []

    for record in records:

        if not isinstance(record, dict):
            continue

        payload = extract_payload(record) or {}

        order_id = str(
            record.get("orderId")
            or record.get("order_id")
            or record.get("demo_order_id")
            or record.get("exchange_order_id")
            or ""
        ).strip()

        client_id = str(
            record.get("clientOrderId")
            or record.get("client_order_id")
            or record.get("newClientOrderId")
            or payload.get("newClientOrderId")
            or ""
        ).strip()

        if (
            order_id == TARGET_ORDER_ID
            or client_id == TARGET_CLIENT_ID
        ):
            candidates.append(record)

    return candidates


def inspect_record(record):

    payload = extract_payload(record)

    if payload is None:
        return {
            "payload_found": False,
            "tp_present": False,
            "sl_present": False,
            "tp_value": None,
            "sl_value": None,
            "tp_working_type": None,
            "sl_working_type": None,
        }

    tp = payload.get(
        "tpTriggerPrice"
    )

    sl = payload.get(
        "slTriggerPrice"
    )

    return {
        "payload_found":
            True,

        "tp_present":
            tp not in (
                None,
                "",
                "0",
                0,
            ),

        "sl_present":
            sl not in (
                None,
                "",
                "0",
                0,
            ),

        "tp_value":
            tp,

        "sl_value":
            sl,

        "tp_working_type":
            payload.get(
                "TpWorkingType"
            ),

        "sl_working_type":
            payload.get(
                "SlWorkingType"
            ),
    }


def main():

    line()

    log(
        "R36F.15.6 DURABLE PROTECTION EVIDENCE START"
    )

    log(
        "R36F.15.6 TARGET ORDER ID = "
        + TARGET_ORDER_ID
    )

    log(
        "R36F.15.6 TARGET CLIENT ID = "
        + TARGET_CLIENT_ID
    )

    log(
        "R36F.15.6 JOURNAL FILE = "
        + JOURNAL_FILE
    )

    journal = load_json(
        JOURNAL_FILE
    )

    journal_exists = (
        journal is not None
    )

    log(
        "R36F.15.6 JOURNAL FOUND = "
        + str(journal_exists)
    )

    if not journal_exists:

        log(
            "R36F.15.6 PROTECTION VERIFIED = False"
        )

        log(
            "R36F.15.6 REASON = DURABLE_DEMO_JOURNAL_NOT_FOUND"
        )

        log(
            "R36F.15.6 SAFE TO ASSUME TP_SL_ACTIVE = False"
        )

        log(
            "R36F.15.6 REAL MONEY EXECUTION = False"
        )

        line()

        return

    records = normalize_records(
        journal
    )

    log(
        "R36F.15.6 JOURNAL RECORD COUNT = "
        + str(len(records))
    )

    matches = find_target(
        records
    )

    log(
        "R36F.15.6 TARGET JOURNAL RECORDS = "
        + str(len(matches))
    )

    if not matches:

        log(
            "R36F.15.6 PROTECTION VERIFIED = False"
        )

        log(
            "R36F.15.6 REASON = TARGET_ORDER_NOT_FOUND_IN_DURABLE_JOURNAL"
        )

        log(
            "R36F.15.6 SAFE TO ASSUME TP_SL_ACTIVE = False"
        )

        log(
            "R36F.15.6 REAL MONEY EXECUTION = False"
        )

        line()

        return

    best = None
    best_result = None

    for record in matches:

        result = inspect_record(
            record
        )

        if (
            best is None
            or (
                result["tp_present"]
                and
                result["sl_present"]
            )
        ):

            best = record
            best_result = result

        if (
            result["tp_present"]
            and
            result["sl_present"]
        ):
            break

    state = str(
        best.get("state")
        or best.get("status")
        or best.get("journal_state")
        or ""
    ).upper()

    log(
        "R36F.15.6 JOURNAL STATE = "
        + str(state)
    )

    log(
        "R36F.15.6 REQUEST PAYLOAD FOUND = "
        + str(
            best_result[
                "payload_found"
            ]
        )
    )

    log(
        "R36F.15.6 TP FIELD PRESENT = "
        + str(
            best_result[
                "tp_present"
            ]
        )
    )

    log(
        "R36F.15.6 TP TRIGGER PRICE = "
        + str(
            best_result[
                "tp_value"
            ]
        )
    )

    log(
        "R36F.15.6 TP WORKING TYPE = "
        + str(
            best_result[
                "tp_working_type"
            ]
        )
    )

    log(
        "R36F.15.6 SL FIELD PRESENT = "
        + str(
            best_result[
                "sl_present"
            ]
        )
    )

    log(
        "R36F.15.6 SL TRIGGER PRICE = "
        + str(
            best_result[
                "sl_value"
            ]
        )
    )

    log(
        "R36F.15.6 SL WORKING TYPE = "
        + str(
            best_result[
                "sl_working_type"
            ]
        )
    )

    request_protection_evidence = (
        best_result[
            "payload_found"
        ]
        and
        best_result[
            "tp_present"
        ]
        and
        best_result[
            "sl_present"
        ]
    )

    log(
        "R36F.15.6 REQUEST PROTECTION EVIDENCE = "
        + str(
            request_protection_evidence
        )
    )

    if request_protection_evidence:

        log(
            "R36F.15.6 DEMO POST INCLUDED TP_SL = True"
        )

        log(
            "R36F.15.6 PROTECTION REQUEST VERIFIED = True"
        )

        log(
            "R36F.15.6 EXCHANGE-SIDE ACTIVE PROTECTION VERIFIED = False"
        )

        log(
            "R36F.15.6 REASON = REQUEST_PAYLOAD_PROVES_TP_SL_WERE_SUBMITTED_BUT_DOCUMENTED_DEMO_READ_API_CANNOT_CONFIRM_CURRENT_ACTIVE_STATE"
        )

    else:

        log(
            "R36F.15.6 DEMO POST INCLUDED TP_SL = False"
        )

        log(
            "R36F.15.6 PROTECTION REQUEST VERIFIED = False"
        )

        log(
            "R36F.15.6 EXCHANGE-SIDE ACTIVE PROTECTION VERIFIED = False"
        )

        log(
            "R36F.15.6 REASON = DURABLE_JOURNAL_DOES_NOT_PROVE_TP_SL_SUBMISSION"
        )

    log(
        "R36F.15.6 SAFE TO ASSUME TP_SL_ACTIVE = False"
    )

    log(
        "R36F.15.6 NEW DEMO ORDER ALLOWED = False"
    )

    log(
        "R36F.15.6 REAL MONEY EXECUTION = False"
    )

    line()

    log(
        "R36F.15.6 TEST COMPLETE"
    )

    line()


if __name__ == "__main__":

    main()
