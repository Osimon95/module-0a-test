
#!/usr/bin/env python3

import os
import json
from datetime import datetime, timezone


STAGE = "R36F.15.6.1"

ROOTS = [
    "/var/data",
    "/var/data/r36f_state",
]

TARGET_ORDER_ID = "792989056504955607"
TARGET_CLIENT_ID = "R36F8-LONG-D14-0001"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def log(message):
    print(now_iso(), message, flush=True)


def line():
    print("-" * 100, flush=True)


def safe_read_text(path):

    try:
        with open(
            path,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as f:

            return f.read()

    except Exception as exc:

        return None


def looks_relevant(path, text):

    name = os.path.basename(path).lower()

    name_match = any(
        token in name
        for token in (
            "journal",
            "demo",
            "order",
            "r36f15",
            "r36f",
            "snapshot",
        )
    )

    content_match = False

    if text:

        content_match = (
            TARGET_ORDER_ID in text
            or
            TARGET_CLIENT_ID in text
        )

    return (
        name_match
        or
        content_match
    )


def inspect_file(path):

    try:

        size = os.path.getsize(
            path
        )

    except Exception:

        size = None

    text = safe_read_text(
        path
    )

    relevant = looks_relevant(
        path,
        text,
    )

    contains_order = bool(
        text
        and
        TARGET_ORDER_ID in text
    )

    contains_client = bool(
        text
        and
        TARGET_CLIENT_ID in text
    )

    if relevant:

        log(
            "R36F.15.6.1 FILE = "
            + path
        )

        log(
            "R36F.15.6.1 FILE SIZE = "
            + str(size)
        )

        log(
            "R36F.15.6.1 CONTAINS TARGET ORDER ID = "
            + str(
                contains_order
            )
        )

        log(
            "R36F.15.6.1 CONTAINS TARGET CLIENT ID = "
            + str(
                contains_client
            )
        )

        if (
            contains_order
            or
            contains_client
        ):

            log(
                "R36F.15.6.1 *** TARGET EVIDENCE FILE FOUND ***"
            )

        line()

    return {
        "path":
            path,

        "size":
            size,

        "relevant":
            relevant,

        "contains_order":
            contains_order,

        "contains_client":
            contains_client,
    }


def walk_root(root):

    results = []

    if not os.path.exists(
        root
    ):

        log(
            "R36F.15.6.1 ROOT NOT FOUND = "
            + root
        )

        return results

    log(
        "R36F.15.6.1 ROOT FOUND = "
        + root
    )

    for current_root, dirs, files in os.walk(
        root
    ):

        log(
            "R36F.15.6.1 DIRECTORY = "
            + current_root
        )

        for filename in sorted(
            files
        ):

            path = os.path.join(
                current_root,
                filename,
            )

            result = inspect_file(
                path
            )

            results.append(
                result
            )

    return results


def main():

    line()

    log(
        "R36F.15.6.1 DURABLE FILE DISCOVERY START"
    )

    log(
        "R36F.15.6.1 TARGET ORDER ID = "
        + TARGET_ORDER_ID
    )

    log(
        "R36F.15.6.1 TARGET CLIENT ID = "
        + TARGET_CLIENT_ID
    )

    line()

    all_results = []

    visited = set()

    for root in ROOTS:

        real_root = os.path.realpath(
            root
        )

        if real_root in visited:
            continue

        visited.add(
            real_root
        )

        all_results.extend(
            walk_root(
                root
            )
        )

    relevant_files = [
        x
        for x in all_results
        if x.get(
            "relevant"
        )
    ]

    target_files = [
        x
        for x in all_results
        if (
            x.get(
                "contains_order"
            )
            or
            x.get(
                "contains_client"
            )
        )
    ]

    line()

    log(
        "R36F.15.6.1 TOTAL FILES INSPECTED = "
        + str(
            len(
                all_results
            )
        )
    )

    log(
        "R36F.15.6.1 RELEVANT FILE COUNT = "
        + str(
            len(
                relevant_files
            )
        )
    )

    log(
        "R36F.15.6.1 TARGET EVIDENCE FILE COUNT = "
        + str(
            len(
                target_files
            )
        )
    )

    if target_files:

        log(
            "R36F.15.6.1 TARGET EVIDENCE FOUND = True"
        )

        for item in target_files:

            log(
                "R36F.15.6.1 TARGET FILE PATH = "
                + str(
                    item.get(
                        "path"
                    )
                )
            )

    else:

        log(
            "R36F.15.6.1 TARGET EVIDENCE FOUND = False"
        )

        log(
            "R36F.15.6.1 REASON = TARGET_ORDER_NOT_FOUND_IN_CURRENT_PERSISTENT_FILES"
        )

    log(
        "R36F.15.6.1 HTTP REQUESTS SENT = 0"
    )

    log(
        "R36F.15.6.1 DEMO ORDERS SENT = 0"
    )

    log(
        "R36F.15.6.1 REAL ORDERS SENT = 0"
    )

    line()

    log(
        "R36F.15.6.1 TEST COMPLETE"
    )

    line()


if __name__ == "__main__":
    main()
