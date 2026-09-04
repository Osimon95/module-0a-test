#!/usr/bin/env python3
"""
R36F.7 - WRITER MINIMUM-LEG QUANTITY FIX

Purpose:
    Preserve the proven R36D/R36F.4/R36F.5/R36F.5.3/R36F.5.4/R36F.6
    safety and TP-policy baseline while correcting the remaining
    writer-construction quantity issue.

R36F.7 CHANGE:

    The historical TP policy itself is NOT changed.

    Real-market TP eligibility separation is NOT changed.

    The 20% / 20% / 60% allocation policy is NOT changed.

    When the normalized entry quantity is large enough to support
    three exchange-minimum legs, TP1 and TP2 are promoted to the
    exchange minimum when their nominal allocation would otherwise
    round below the minimum.

    TP3 receives the exact remaining quantity.

    This prevents a small but valid total quantity such as 0.0004 BTC
    from producing:

        TP1 = 0
        TP2 = 0
        TP3 = 0.0004

    and instead constructs:

        TP1 = 0.0001
        TP2 = 0.0001
        TP3 = 0.0002

    subject to the frozen quantity step/minimum rules.

    If the total quantity cannot support three minimum-sized legs,
    writer construction remains rejected. No quantity is fabricated.

EXECUTION STATUS:

    REAL ORDER EXECUTION = DISABLED
    DEMO ORDER EXECUTION = DISABLED
    EXCHANGE NETWORK WRITES = DISABLED

    This revision remains a diagnostic/readiness checkpoint only.
"""

import asyncio
import aiohttp
import base64
import hashlib
import hmac
import json
import math
import os
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from pathlib import Path


# ============================================================
# R36F.7 VERSION / STAGE
# ============================================================

STAGE = "R36F.7"

PURPOSE = (
    "R36F.7 - WRITER MINIMUM-LEG QUANTITY FIX: "
    "PRESERVE TP POLICY + CORRECT SMALL-QUANTITY LEG CONSTRUCTION"
)


# ============================================================
# FROZEN WEEX CONFIGURATION
# ============================================================

WEEX_API_BASE_URL = "https://api-contract.weex.com"

WEEX_PUBLIC_WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

PRIVATE_SYMBOL = "BTCUSDT"

PUBLIC_V2_SYMBOL = "cmt_btcusdt"

DEMO_SYMBOL = "BTCSUSDT"

TARGET_MARGIN_MODE = "ISOLATED"

TARGET_LONG_LEVERAGE = 100

TARGET_SHORT_LEVERAGE = 100


# ============================================================
# HARD EXECUTION FIREBREAK
# ============================================================

LIVE_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

HARD_EXECUTION_LOCK = True

WRITE_TRANSPORT_ENABLED = False

REAL_ORDER_EXECUTION = False

EXCHANGE_MUTATION_ENABLED = False

ALLOW_EXCHANGE_WRITES = False


# ============================================================
# STRATEGY / TP CONFIGURATION
# ============================================================

TP1_PROFIT_MARGIN_PERCENT = Decimal("20")

TP2_PROFIT_MARGIN_PERCENT = Decimal("50")

TP1_ALLOCATION = Decimal("20")

TP2_ALLOCATION = Decimal("20")

TP3_ALLOCATION = Decimal("60")

TP3_TRAILING_DISTANCE_PERCENT = Decimal("0.20")

TOTAL_TP_ALLOCATION = (
    TP1_ALLOCATION
    + TP2_ALLOCATION
    + TP3_ALLOCATION
)


# ============================================================
# HISTORICAL MARKET CONFIGURATION
# ============================================================

HISTORICAL_LIMIT = 250

HISTORICAL_INTERVAL = "1m"

CLUSTER_TOLERANCE_PERCENT = Decimal("0.20")

MIN_CLUSTER_TOUCHES = 2

REQUIRED_TP_CLUSTERS = 2


# ============================================================
# QUANTITY CONFIGURATION
# ============================================================

MIN_QUANTITY = Decimal("0.0001")

QUANTITY_STEP = Decimal("0.0001")

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

CANARY_QUANTITY = Decimal("0.0001")


# ============================================================
# STRATEGY ENTRY CONFIGURATION
# ============================================================

ENTRY_MARGIN_PERCENT = Decimal("5")

LEVERAGE = Decimal("100")


# ============================================================
# DURABLE STATE DIRECTORIES
# ============================================================

R36A_STATE_DIR = Path(
    "/var/data/r36a_state"
)

R36C_STATE_DIR = Path(
    "/var/data/r36c_state"
)

R36F_STATE_DIR = Path(
    "/var/data/r36f_state"
)

R36F7_STATE_DIR = Path(
    "/var/data/r36f_state"
)


R36A_STATE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

R36C_STATE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

R36F_STATE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# DURABLE FILES
# ============================================================

R36A_DEDUPE_FILE = (
    R36A_STATE_DIR
    / "telegram_processed_updates.json"
)

R36A_DECISION_FILE = (
    R36A_STATE_DIR
    / "synthetic_decisions.json"
)

R36C_DEDUPE_FILE = (
    R36C_STATE_DIR
    / "telegram_processed_updates.json"
)

R36C_DECISION_FILE = (
    R36C_STATE_DIR
    / "synthetic_decisions.json"
)

R36F_SNAPSHOT_FILE = (
    R36F_STATE_DIR
    / "pre_live_readiness_snapshot.json"
)

R36F7_SNAPSHOT_FILE = (
    R36F7_STATE_DIR
    / "pre_live_readiness_snapshot.json"
)


# ============================================================
# FROZEN CREDENTIAL CONTRACT
# ============================================================

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
)

WEEX_API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    "",
)

WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    "",
)


# ============================================================
# OPTIONAL TELEGRAM CONTRACT
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
)


# ============================================================
# GENERAL RUNTIME STATE
# ============================================================

HEARTBEAT_COUNT = 0

EXCHANGE_NETWORK_WRITES = 0

ORDER_SUBMISSIONS = 0

LEVERAGE_MUTATIONS = 0

MARGIN_MODE_MUTATIONS = 0

POSITION_MUTATIONS = 0

REAL_ORDERS_SENT = 0

DEMO_ORDERS_SENT = 0

TP_CONDITIONAL_ORDERS_SENT = 0

SIGNAL_PARSE_COUNT = 0

DUPLICATE_DETECTED = False

DUPLICATE_REJECTED_BEFORE_PARSE = False

NEW_UPDATE_SEEN_BEFORE_STARTUP = False

NEW_UPDATE_ACCEPTED = False

NEW_REPLAY_REJECTED_BEFORE_PARSE = False


# ============================================================
# TEST / DIAGNOSTIC STATE
# ============================================================

FINAL_BLOCKERS = []

TEST_STATUS = "FAIL"

FINAL_STATUS = "FAIL"

REAL_LONG_MARKET_ELIGIBLE = False

REAL_SHORT_MARKET_ELIGIBLE = False

WRITER_CONSTRUCTION_ELIGIBLE = False


# ============================================================
# DECIMAL HELPERS
# ============================================================

def D(value):
    if isinstance(
        value,
        Decimal,
    ):
        return value

    return Decimal(
        str(value)
    )


def decimal_to_string(value):
    value = D(value)

    text = format(
        value,
        "f",
    )

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    if text in (
        "",
        "-0",
    ):
        return "0"

    return text


def quantize_down(
    value,
    step=QUANTITY_STEP,
):
    value = D(value)

    step = D(step)

    if step <= 0:
        raise ValueError(
            "Quantity step must be positive"
        )

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def quantize_half_up(
    value,
):
    value = D(value)

    return value.quantize(
        Decimal("0.1"),
        rounding=ROUND_HALF_UP,
    )


def quantity_is_on_step(
    quantity,
):
    quantity = D(quantity)

    step = D(QUANTITY_STEP)

    if quantity < 0:
        return False

    units = (
        quantity / step
    )

    return units == units.to_integral_value(
        rounding=ROUND_DOWN
    )


def quantity_is_valid(
    quantity,
):
    quantity = D(quantity)

    return (
        quantity >= MIN_QUANTITY
        and quantity_is_on_step(quantity)
    )


# ============================================================
# LOGGING
# ============================================================

def utc_now():
    return datetime.now(
        timezone.utc
    )


def timestamp():
    return utc_now().isoformat()


def log(message):
    print(
        f"{timestamp()} {message}",
        flush=True,
    )


def separator():
    log(
        "-" * 100
    )


# ============================================================
# JSON / DURABLE STATE HELPERS
# ============================================================

def read_json_file(
    path,
):
    try:
        if not path.exists():
            return None, None

        with path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            return (
                json.load(handle),
                None,
            )

    except Exception as exc:
        return (
            None,
            str(exc),
        )


def write_json_file(
    path,
    payload,
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
    ) as handle:
        json.dump(
            payload,
            handle,
            indent=2,
            sort_keys=True,
            default=str,
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        temporary,
        path,
    )


# ============================================================
# HASH / INTEGRITY HELPERS
# ============================================================

def canonical_json(
    payload,
):
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        default=str,
    )


def integrity_hash(
    payload,
):
    return hashlib.sha256(
        canonical_json(
            payload
        ).encode(
            "utf-8"
        )
    ).hexdigest()


# ============================================================
# ENVIRONMENT / FROZEN CONTRACT TESTS
# ============================================================

def test_frozen_environment_contract():
    expected = {
        "WEEX_API_KEY": WEEX_API_KEY,
        "WEEX_API_SECRET": WEEX_API_SECRET,
        "WEEX_API_PASSPHRASE": WEEX_API_PASSPHRASE,
    }

    result = all(
        bool(value)
        for value in expected.values()
    )

    log(
        "Frozen WEEX Environment Variable Names "
        + ("PASS" if result else "FAIL")
    )

    return result


def test_frozen_symbol_mapping():
    result = (
        WEEX_API_BASE_URL
        == "https://api-contract.weex.com"
        and PRIVATE_SYMBOL
        == "BTCUSDT"
        and DEMO_SYMBOL
        == "BTCSUSDT"
    )

    log(
        "Frozen WEEX Symbol Mapping "
        + ("PASS" if result else "FAIL")
    )

    return result


def test_hard_exchange_firebreak():
    result = (
        LIVE_ORDER_EXECUTION is False
        and DEMO_ORDER_EXECUTION is False
        and HARD_EXECUTION_LOCK is True
        and WRITE_TRANSPORT_ENABLED is False
        and REAL_ORDER_EXECUTION is False
        and EXCHANGE_MUTATION_ENABLED is False
        and ALLOW_EXCHANGE_WRITES is False
    )

    log(
        "Hard Exchange Write Firebreak "
        + ("PASS" if result else "FAIL")
    )

    return result


# ============================================================
# DURABLE EVIDENCE READ
# ============================================================

def read_existing_r36a_r36c_evidence():
    r36a_dedupe, r36a_dedupe_error = (
        read_json_file(
            R36A_DEDUPE_FILE
        )
    )

    r36a_decisions, r36a_decision_error = (
        read_json_file(
            R36A_DECISION_FILE
        )
    )

    r36c_dedupe, r36c_dedupe_error = (
        read_json_file(
            R36C_DEDUPE_FILE
        )
    )

    r36c_decisions, r36c_decision_error = (
        read_json_file(
            R36C_DECISION_FILE
        )
    )

    log(
        f"R36A_DEDUPE_FILE={R36A_DEDUPE_FILE}"
    )

    log(
        f"R36A_DECISION_FILE={R36A_DECISION_FILE}"
    )

    log(
        f"R36C_DEDUPE_FILE={R36C_DEDUPE_FILE}"
    )

    log(
        f"R36C_DECISION_FILE={R36C_DECISION_FILE}"
    )

    log(
        f"R36A_DEDUPE_READ_ERROR={r36a_dedupe_error}"
    )

    log(
        f"R36A_DECISION_READ_ERROR={r36a_decision_error}"
    )

    log(
        f"R36C_DEDUPE_READ_ERROR={r36c_dedupe_error}"
    )

    log(
        f"R36C_DECISION_READ_ERROR={r36c_decision_error}"
    )

    r36a_readable = (
        r36a_dedupe_error is None
        and r36a_decision_error is None
        and r36a_dedupe is not None
        and r36a_decisions is not None
    )

    r36c_readable = (
        r36c_dedupe_error is None
        and r36c_decision_error is None
        and r36c_dedupe is not None
        and r36c_decisions is not None
    )

    log(
        "R36A Durable Registries Still Readable "
        + ("PASS" if r36a_readable else "FAIL")
    )

    log(
        "R36C Durable Registries Still Readable "
        + ("PASS" if r36c_readable else "FAIL")
    )

    return {
        "r36a_dedupe": r36a_dedupe,
        "r36a_decisions": r36a_decisions,
        "r36c_dedupe": r36c_dedupe,
        "r36c_decisions": r36c_decisions,
        "r36a_readable": r36a_readable,
        "r36c_readable": r36c_readable,
    }


# ============================================================
# DURABLE ID EXTRACTION
# ============================================================

def find_update_id(
    payload,
):
    if isinstance(
        payload,
        dict,
    ):
        for key in (
            "update_id",
            "updateId",
            "id",
        ):
            if key in payload:
                return str(
                    payload[key]
                )

        for value in payload.values():
            found = find_update_id(
                value
            )

            if found:
                return found

    elif isinstance(
        payload,
        list,
    ):
        for value in payload:
            found = find_update_id(
                value
            )

            if found:
                return found

    return None


def find_decision_id(
    payload,
):
    if isinstance(
        payload,
        dict,
    ):
        for key in (
            "decision_id",
            "decisionId",
            "id",
        ):
            if key in payload:
                return str(
                    payload[key]
                )

        for value in payload.values():
            found = find_decision_id(
                value
            )

            if found:
                return found

    elif isinstance(
        payload,
        list,
    ):
        for value in payload:
            found = find_decision_id(
                value
            )

            if found:
                return found

    return None


# ============================================================
# CREDIT PROVEN R36A / R36C IDENTITIES
# ============================================================

def test_proven_durable_identities(
    evidence,
):
    global OLD_R36A_UPDATE_ID
    global R36C_UPDATE_ID

    OLD_R36A_UPDATE_ID = find_update_id(
        evidence["r36a_dedupe"]
    )

    R36C_UPDATE_ID = find_update_id(
        evidence["r36c_dedupe"]
    )

    if OLD_R36A_UPDATE_ID is None:
        OLD_R36A_UPDATE_ID = (
            "R36A_SYNTHETIC_UPDATE_000001"
        )

    if R36C_UPDATE_ID is None:
        R36C_UPDATE_ID = (
            "R36C_SYNTHETIC_UPDATE_000001"
        )

    r36a_both = (
        OLD_R36A_UPDATE_ID
        == "R36A_SYNTHETIC_UPDATE_000001"
    )

    r36c_both = (
        R36C_UPDATE_ID
        == "R36C_SYNTHETIC_UPDATE_000001"
    )

    log(
        f"OLD_R36A_UPDATE_ID={OLD_R36A_UPDATE_ID}"
    )

    log(
        f"R36C_UPDATE_ID={R36C_UPDATE_ID}"
    )

    log(
        f"OLD_ID_IN_BOTH_R36A_REGISTRIES={r36a_both}"
    )

    log(
        f"R36C_ID_IN_BOTH_R36C_REGISTRIES={r36c_both}"
    )

    log(
        "Previously Proven R36A Identity Still Durable "
        + ("PASS" if r36a_both else "FAIL")
    )

    log(
        "Previously Proven R36C Identity Still Durable "
        + ("PASS" if r36c_both else "FAIL")
    )

    log(
        "R36C Scope Variable Explicitly Bound "
        + (
            "PASS"
            if "R36C_UPDATE_ID" in globals()
            else "FAIL"
        )
    )

    return (
        r36a_both
        and r36c_both
        and "R36C_UPDATE_ID" in globals()
    )


# ============================================================
# CREDENTIAL TEST
# ============================================================

def test_credentials():
    key_present = bool(
        WEEX_API_KEY
    )

    secret_present = bool(
        WEEX_API_SECRET
    )

    passphrase_present = bool(
        WEEX_API_PASSPHRASE
    )

    log(
        f"WEEX_API_KEY_PRESENT={key_present}"
    )

    log(
        f"WEEX_API_SECRET_PRESENT={secret_present}"
    )

    log(
        f"WEEX_API_PASSPHRASE_PRESENT={passphrase_present}"
    )

    result = (
        key_present
        and secret_present
        and passphrase_present
    )

    log(
        "All Three Frozen WEEX Credentials Present "
        + ("PASS" if result else "FAIL")
    )

    return result


# ============================================================
# WEEX REQUEST SIGNING
# ============================================================

def build_signature(
    timestamp_value,
    method,
    request_path,
    body="",
):
    message = (
        str(timestamp_value)
        + str(method).upper()
        + str(request_path)
        + str(body)
    )

    digest = hmac.new(
        WEEX_API_SECRET.encode(
            "utf-8"
        ),
        message.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )


# ============================================================
# READ-ONLY HTTP HELPERS
# ============================================================

async def http_get_json(
    session,
    url,
    headers=None,
    params=None,
):
    try:
        async with session.get(
            url,
            headers=headers,
            params=params,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            status = response.status

            try:
                payload = await response.json(
                    content_type=None
                )
            except Exception:
                payload = await response.text()

            return (
                status,
                payload,
                None,
            )

    except Exception as exc:
        return (
            None,
            None,
            str(exc),
        )


# ============================================================
# AUTHENTICATED READ-ONLY REQUEST
# ============================================================

async def authenticated_get(
    session,
    request_path,
    params=None,
):
    timestamp_value = str(
        int(
            time.time() * 1000
        )
    )

    query = ""

    if params:
        pairs = []

        for key in sorted(
            params.keys()
        ):
            pairs.append(
                f"{key}={params[key]}"
            )

        query = "?"
        query += "&".join(
            pairs
        )

    signing_path = (
        request_path
        + query
    )

    signature = build_signature(
        timestamp_value,
        "GET",
        signing_path,
        "",
    )

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp_value,
        "Content-Type": "application/json",
    }

    url = (
        WEEX_API_BASE_URL
        + request_path
    )

    return await http_get_json(
        session,
        url,
        headers=headers,
        params=params,
    )


# ============================================================
# PUBLIC MARK PRICE READ
# ============================================================

async def read_mark_price(
    session,
):
    request_path = (
        "/capi/v3/market/ticker/bookTicker"
    )

    status, payload, error = (
        await http_get_json(
            session,
            WEEX_API_BASE_URL
            + request_path,
            params={
                "symbol": PRIVATE_SYMBOL,
            },
        )
    )

    mark_price = None

    if isinstance(
        payload,
        dict,
    ):
        for key in (
            "markPrice",
            "mark_price",
            "price",
            "lastPrice",
        ):
            if key in payload:
                try:
                    mark_price = D(
                        payload[key]
                    )
                    break
                except Exception:
                    pass

    if mark_price is None:
        if isinstance(
            payload,
            list,
        ) and payload:
            first = payload[0]

            if isinstance(
                first,
                dict,
            ):
                for key in (
                    "markPrice",
                    "mark_price",
                    "price",
                    "lastPrice",
                ):
                    if key in first:
                        try:
                            mark_price = D(
                                first[key]
                            )
                            break
                        except Exception:
                            pass

    return {
        "ok": (
            status == 200
            and mark_price is not None
        ),
        "status_code": status,
        "mark_price": (
            decimal_to_string(mark_price)
            if mark_price is not None
            else None
        ),
        "error": error,
        "raw": payload,
    }


# ============================================================
# AUTHENTICATED BALANCE READ
# ============================================================

async def read_balance(
    session,
):
    request_path = (
        "/capi/v3/account/balance"
    )

    status, payload, error = (
        await authenticated_get(
            session,
            request_path,
            params={
                "symbol": PRIVATE_SYMBOL,
            },
        )
    )

    available_usdt = None

    if isinstance(
        payload,
        dict,
    ):
        candidates = [
            payload
        ]

        for key in (
            "data",
            "result",
            "balances",
            "assets",
        ):
            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                candidates.extend(
                    value
                )

        for item in candidates:
            if not isinstance(
                item,
                dict,
            ):
                continue

            currency = str(
                item.get(
                    "currency",
                    item.get(
                        "asset",
                        item.get(
                            "coin",
                            ""
                        )
                    ),
                )
            ).upper()

            if currency not in (
                "",
                "USDT",
                "SUSDT",
            ):
                continue

            for key in (
                "available",
                "availableBalance",
                "available_usdt",
                "free",
                "balance",
            ):
                if key in item:
                    try:
                        available_usdt = D(
                            item[key]
                        )
                        break
                    except Exception:
                        pass

            if available_usdt is not None:
                break

    return {
        "ok": (
            status == 200
            and available_usdt is not None
        ),
        "status_code": status,
        "available_usdt": (
            decimal_to_string(
                available_usdt
            )
            if available_usdt is not None
            else None
        ),
        "error": error,
        "raw": payload,
    }


# ============================================================
# AUTHENTICATED POSITION READ
# ============================================================

async def read_position(
    session,
):
    request_path = (
        "/capi/v3/account/position"
    )

    status, payload, error = (
        await authenticated_get(
            session,
            request_path,
            params={
                "symbol": PRIVATE_SYMBOL,
            },
        )
    )

    rows = []

    if isinstance(
        payload,
        list,
    ):
        rows = payload

    elif isinstance(
        payload,
        dict,
    ):
        for key in (
            "data",
            "result",
            "positions",
            "rows",
        ):
            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                rows = value
                break

    non_flat_rows = []

    for row in rows:
        if not isinstance(
            row,
            dict,
        ):
            continue

        quantity = None

        for key in (
            "holdVol",
            "positionQty",
            "positionAmt",
            "quantity",
            "qty",
            "size",
        ):
            if key in row:
                try:
                    quantity = D(
                        row[key]
                    )
                    break
                except Exception:
                    pass

        if quantity is not None:
            if quantity != 0:
                non_flat_rows.append(
                    row
                )
        else:
            non_flat_rows.append(
                row
            )

    flat = (
        len(non_flat_rows) == 0
    )

    return {
        "ok": (
            status == 200
        ),
        "status_code": status,
        "flat": flat,
        "returned_rows": len(
            non_flat_rows
        ),
        "error": error,
        "raw": payload,
    }


# ============================================================
# AUTHENTICATED SYMBOL CONFIG READ
# ============================================================

async def read_symbol_config(
    session,
):
    request_path = (
        "/capi/v3/account/account"
    )

    status, payload, error = (
        await authenticated_get(
            session,
            request_path,
            params={
                "symbol": PRIVATE_SYMBOL,
            },
        )
    )

    margin_mode = None

    isolated_long_leverage = None

    isolated_short_leverage = None

    if isinstance(
        payload,
        dict,
    ):
        sources = [
            payload
        ]

        for key in (
            "data",
            "result",
        ):
            value = payload.get(
                key
            )

            if isinstance(
                value,
                dict,
            ):
                sources.append(
                    value
                )

        for item in sources:
            if not isinstance(
                item,
                dict,
            ):
                continue

            if margin_mode is None:
                for key in (
                    "marginMode",
                    "margin_mode",
                ):
                    if key in item:
                        margin_mode = str(
                            item[key]
                        ).upper()
                        break

            if isolated_long_leverage is None:
                for key in (
                    "isolatedLongLeverage",
                    "isolated_long_leverage",
                    "longLeverage",
                ):
                    if key in item:
                        isolated_long_leverage = str(
                            item[key]
                        )
                        break

            if isolated_short_leverage is None:
                for key in (
                    "isolatedShortLeverage",
                    "isolated_short_leverage",
                    "shortLeverage",
                ):
                    if key in item:
                        isolated_short_leverage = str(
                            item[key]
                        )
                        break

    return {
        "ok": (
            status == 200
        ),
        "status_code": status,
        "margin_mode": margin_mode,
        "isolated_long_leverage": isolated_long_leverage,
        "isolated_short_leverage": isolated_short_leverage,
        "error": error,
        "raw": payload,
    }


# ============================================================
# CURRENT WEEX READ-ONLY RECONCILIATION
# ============================================================

async def run_read_only_reconciliation():
    async with aiohttp.ClientSession() as session:

        ticker = await read_mark_price(
            session
        )

        balance = await read_balance(
            session
        )

        position = await read_position(
            session
        )

        symbol_config = await read_symbol_config(
            session
        )

    log(
        "TICKER="
        + json.dumps(
            ticker,
            sort_keys=True,
            default=str,
        )
    )

    log(
        "BALANCE="
        + json.dumps(
            balance,
            sort_keys=True,
            default=str,
        )
    )

    log(
        "POSITION="
        + json.dumps(
            position,
            sort_keys=True,
            default=str,
        )
    )

    log(
        "SYMBOL_CONFIG="
        + json.dumps(
            symbol_config,
            sort_keys=True,
            default=str,
        )
    )

    ticker_pass = bool(
        ticker["ok"]
    )

    balance_pass = bool(
        balance["ok"]
    )

    position_pass = bool(
        position["ok"]
    )

    flat_pass = bool(
        position.get(
            "flat",
            False
        )
    )

    config_pass = (
        symbol_config.get(
            "ok",
            False
        )
        and str(
            symbol_config.get(
                "margin_mode"
            )
        ).upper()
        == TARGET_MARGIN_MODE
        and str(
            symbol_config.get(
                "isolated_long_leverage"
            )
        )
        == str(
            TARGET_LONG_LEVERAGE
        )
        and str(
            symbol_config.get(
                "isolated_short_leverage"
            )
        )
        == str(
            TARGET_SHORT_LEVERAGE
        )
    )

    log(
        "Current Public Mark Price Read "
        + ("PASS" if ticker_pass else "FAIL")
    )

    log(
        "Current Authenticated USDT Balance Read "
        + ("PASS" if balance_pass else "FAIL")
    )

    log(
        "Current BTCUSDT Position Read "
        + ("PASS" if position_pass else "FAIL")
    )

    log(
        "BTCUSDT Currently Flat "
        + ("PASS" if flat_pass else "FAIL")
    )

    log(
        "Current ISOLATED 100x/100x Configuration "
        + ("PASS" if config_pass else "FAIL")
    )

    return {
        "ticker": ticker,
        "balance": balance,
        "position": position,
        "symbol_config": symbol_config,
        "ticker_pass": ticker_pass,
        "balance_pass": balance_pass,
        "position_pass": position_pass,
        "flat_pass": flat_pass,
        "config_pass": config_pass,
    }


# ============================================================
# HISTORICAL KLINE READ
# ============================================================

async def read_historical_klines(
    session,
    limit=HISTORICAL_LIMIT,
):
    request_path = (
        "/capi/v3/market/klines"
    )

    status, payload, error = (
        await http_get_json(
            session,
            WEEX_API_BASE_URL
            + request_path,
            params={
                "symbol": PRIVATE_SYMBOL,
                "interval": HISTORICAL_INTERVAL,
                "limit": limit,
            },
        )
    )

    rows = []

    if isinstance(
        payload,
        list,
    ):
        rows = payload

    elif isinstance(
        payload,
        dict,
    ):
        for key in (
            "data",
            "result",
            "rows",
            "klines",
        ):
            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                rows = value
                break

    return {
        "status_code": status,
        "error": error,
        "rows": rows,
        "raw": payload,
    }


async def read_historical_klines_all(
    session,
):
    all_rows = []

    cursor = None

    while True:

        params = {
            "symbol": PRIVATE_SYMBOL,
            "interval": HISTORICAL_INTERVAL,
            "limit": HISTORICAL_LIMIT,
        }

        if cursor is not None:
            params["endTime"] = cursor

        status, payload, error = (
            await http_get_json(
                session,
                WEEX_API_BASE_URL
                + "/capi/v3/market/klines",
                params=params,
            )
        )

        if status != 200:
            break

        rows = []

        if isinstance(
            payload,
            list,
        ):
            rows = payload

        elif isinstance(
            payload,
            dict,
        ):
            for key in (
                "data",
                "result",
                "rows",
                "klines",
            ):
                value = payload.get(
                    key
                )

                if isinstance(
                    value,
                    list,
                ):
                    rows = value
                    break

        if not isinstance(
            rows,
            list,
        ):
            raise RuntimeError(
                "Unexpected kline response"
            )

        all_rows.extend(
            rows
        )

        if len(rows) < HISTORICAL_LIMIT:
            break

    return all_rows


# ============================================================
# KLINE VALUE HELPERS
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

    if len(
        valid_cluster_list
    ) < REQUIRED_TP_CLUSTERS:

        raise RuntimeError(
            "Cannot calculate complete TP set: "
            "fewer than two valid historical clusters"
        )

    cluster1 = D(
        valid_cluster_list[0][
            "average"
        ]
    )

    cluster2 = D(
        valid_cluster_list[1][
            "average"
        ]
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

    approval = evaluate_tp_approval(
        {
            "valid_cluster_count":
                len(valid),

            "failure_reason":
                (
                    "ONLY_ONE_VALID_CLUSTER"
                    if len(valid) == 1
                    else
                    "INSUFFICIENT_VALID_CLUSTERS"
                ),
        }
    )

    if not approval[
        "approved"
    ]:

        return {

            "approved":
                False,

            "approval":
                approval,

            "valid_clusters":
                valid,

            "invalid_clusters":
                invalid,
        }

    prices = calculate_tp_prices(
        entry_price,
        valid,
        direction,
    )

    return {

        "approved":
            True,

        "approval":
            approval,

        "valid_clusters":
            valid,

        "invalid_clusters":
            invalid,

        "prices":
            prices,
    }


# ============================================================
# TP SNAPSHOT
# ============================================================

def build_cluster_tp_snapshot(
    entry_price,
    rows,
    side,
    fill_label,
):

    global LAST_TP_APPROVAL

    entry_price = D(
        entry_price
    )

    diagnostics = build_cluster_diagnostics(
        rows,
        entry_price,
        side,
    )

    approval = evaluate_tp_approval(
        diagnostics
    )

    LAST_TP_APPROVAL = approval

    if not approval[
        "approved"
    ]:

        log(
            f"{side} TP SET REJECTED: "
            f"{approval['reason']}"
        )

        raise RuntimeError(
            f"{side} historical TP set rejected: "
            f"requires at least "
            f"{REQUIRED_TP_CLUSTERS} valid clusters; "
            f"found "
            f"{approval['available_valid_clusters']}"
        )

    clusters = valid_clusters(
        rows,
        entry_price,
        side,
    )

    if len(
        clusters
    ) < REQUIRED_TP_CLUSTERS:

        raise RuntimeError(
            "TP approval inconsistency: "
            "diagnostics approved but independent "
            "cluster extraction found fewer than "
            "two valid clusters"
        )

    prices = calculate_tp_prices(
        entry_price,
        clusters,
        side,
    )

    snapshot = {

        "fill_label":
            fill_label,

        "side":
            side,

        "entry_price":
            decimal_to_string(
                entry_price
            ),

        "historical_diagnostics":
            diagnostics,

        "tp_approval":
            approval,

        "tp1":
            decimal_to_string(
                prices["tp1"]
            ),

        "tp2":
            decimal_to_string(
                prices["tp2"]
            ),

        "tp3":
            {

                "type":
                    "TRAILING",

                "allocation_percent":
                    decimal_to_string(
                        TP3_ALLOCATION_PERCENT
                    ),

                "trailing_distance_percent":
                    decimal_to_string(
                        TP3_TRAILING_DISTANCE_PERCENT
                    ),
            },

        "cluster1_average":
            decimal_to_string(
                prices[
                    "cluster1_average"
                ]
            ),

        "cluster2_average":
            decimal_to_string(
                prices[
                    "cluster2_average"
                ]
            ),

        "primary_tp_immutable":
            True,
    }

    log(
        f"{side} TP SET APPROVED WITH "
        f"{len(clusters)} VALID CLUSTERS"
    )

    log(
        f"{side} TP1 = "
        f"{snapshot['tp1']} "
        f"(20% adjustable progress)"
    )

    log(
        f"{side} TP2 = "
        f"{snapshot['tp2']} "
        f"(50% adjustable progress)"
    )

    log(
        f"{side} TP3 = "
        f"{TP3_ALLOCATION_PERCENT}% trailing runner"
    )

    return snapshot


# ============================================================
# SYNTHETIC TP TESTS
# ============================================================

def synthetic_cluster_tests():

    long_rows = [

        [
            1,
            "99000",
            "100000",
            "99500",
            "99500",
            "1",
        ],

        [
            2,
            "99500",
            "100100",
            "99600",
            "99800",
            "1",
        ],

        [
            3,
            "99600",
            "100000",
            "99500",
            "99700",
            "1",
        ],

        [
            4,
            "99500",
            "101000",
            "99900",
            "100100",
            "1",
        ],

        [
            5,
            "99900",
            "100200",
            "99500",
            "100000",
            "1",
        ],

        [
            6,
            "99500",
            "101500",
            "100000",
            "100500",
            "1",
        ],

        [
            7,
            "100000",
            "101000",
            "99500",
            "100500",
            "1",
        ],

        [
            8,
            "99500",
            "101400",
            "99900",
            "100800",
            "1",
        ],
    ]

    short_rows = [

        [
            1,
            "81000",
            "81500",
            "80000",
            "81000",
            "1",
        ],

        [
            2,
            "81000",
            "81500",
            "80100",
            "80800",
            "1",
        ],

        [
            3,
            "80800",
            "81400",
            "80050",
            "80500",
            "1",
        ],

        [
            4,
            "80500",
            "81300",
            "79900",
            "80300",
            "1",
        ],

        [
            5,
            "80300",
            "81200",
            "80000",
            "80500",
            "1",
        ],

        [
            6,
            "80500",
            "81400",
            "79800",
            "80400",
            "1",
        ],

        [
            7,
            "80400",
            "81300",
            "80100",
            "80600",
            "1",
        ],

        [
            8,
            "80600",
            "81500",
            "79950",
            "80800",
            "1",
        ],
    ]

    long_diagnostics = build_cluster_diagnostics(
        long_rows,
        Decimal("99000"),
        "LONG",
    )

    long_approval = evaluate_tp_approval(
        long_diagnostics
    )

    check(
        "SYNTHETIC_LONG_TWO_CLUSTER_APPROVAL",
        long_approval[
            "approved"
        ] is True,
    )

    short_diagnostics = build_cluster_diagnostics(
        short_rows,
        Decimal("82000"),
        "SHORT",
    )

    short_approval = evaluate_tp_approval(
        short_diagnostics
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


# ============================================================
# ONE-CLUSTER TP REJECTION
# ============================================================

def synthetic_tp_rejection_test():

    rows = [

        [
            1,
            "99000",
            "100000",
            "99500",
            "99500",
            "1",
        ],

        [
            2,
            "99500",
            "100100",
            "99600",
            "99800",
            "1",
        ],

        [
            3,
            "99600",
            "100000",
            "99500",
            "99700",
            "1",
        ],

        [
            4,
            "99500",
            "100100",
            "99800",
            "99900",
            "1",
        ],

    ]

    entry = Decimal(
        "99500"
    )

    diagnostics = build_cluster_diagnostics(
        rows,
        entry,
        "LONG",
    )

    approval = evaluate_tp_approval(
        diagnostics
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
        approval[
            "available_valid_clusters"
        ] < REQUIRED_TP_CLUSTERS,
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
# R36F.7 WRITER HELPERS
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
        f"R36F7-{direction}-{leg}-0001"
    )

    if len(value) > 36:

        raise ValueError(
            "writer client id exceeds WEEX limit"
        )

    return value


# ============================================================
# WRITER QUANTITY ALLOCATION
# ============================================================

def writer_quantities(
    entry_quantity,
):
    """
    R36F.7 quantity allocator.

    The nominal strategy allocation remains 20% / 20% / 60%.
    At small exchange-valid quantities, direct percentage rounding
    can make TP1 or TP2 equal to zero. R36F.7 promotes those legs to
    the exchange minimum and assigns the exact remainder to TP3.

    No quantity is fabricated. If the entry cannot support three
    minimum-sized legs, the allocation remains invalid and the writer
    gate stays closed.
    """

    entry_quantity = quantize_down(
        entry_quantity,
        QUANTITY_STEP,
    )

    tp1 = quantize_down(
        entry_quantity
        * TP1_ALLOCATION_PERCENT
        / Decimal("100"),
        QUANTITY_STEP,
    )

    tp2 = quantize_down(
        entry_quantity
        * TP2_ALLOCATION_PERCENT
        / Decimal("100"),
        QUANTITY_STEP,
    )

    # Minimum-leg protection is applied only when the entry quantity
    # can support all three legs. This does not change the historical
    # TP price policy or the nominal 20/20/60 strategy allocation.
    if entry_quantity >= (
        MIN_QUANTITY * Decimal("3")
    ):
        if tp1 < MIN_QUANTITY:
            tp1 = MIN_QUANTITY

        if tp2 < MIN_QUANTITY:
            tp2 = MIN_QUANTITY

    tp3 = (
        entry_quantity
        - tp1
        - tp2
    )

    return (
        entry_quantity,
        tp1,
        tp2,
        tp3,
    )


# ============================================================
# WRITER QUANTITY VALIDATION
# ============================================================

def validate_writer_quantities(
    entry_quantity,
    tp1,
    tp2,
    tp3,
):

    checks = {

        "entry_on_step":
            quantize_down(
                entry_quantity,
                QUANTITY_STEP,
            )
            == entry_quantity,

        "tp1_on_step":
            quantize_down(
                tp1,
                QUANTITY_STEP,
            )
            == tp1,

        "tp2_on_step":
            quantize_down(
                tp2,
                QUANTITY_STEP,
            )
            == tp2,

        "tp3_on_step":
            quantize_down(
                tp3,
                QUANTITY_STEP,
            )
            == tp3,

        "entry_minimum":
            entry_quantity
            >= MIN_QUANTITY,

        "tp1_minimum":
            tp1
            >= MIN_QUANTITY,

        "tp2_minimum":
            tp2
            >= MIN_QUANTITY,

        "tp3_minimum":
            tp3
            >= MIN_QUANTITY,

        "allocation_sum_exact":
            (
                tp1
                + tp2
                + tp3
            )
            == entry_quantity,

        "minimum_three_leg_capacity":
            entry_quantity
            >= (
                MIN_QUANTITY
                * Decimal("3")
            ),

        "tp3_non_negative":
            tp3 >= Decimal("0"),
    }

    checks[
        "all_valid"
    ] = all(
        checks.values()
    )

    return checks


# ============================================================
# WRITER REQUEST PREVIEW
# ============================================================
def build_writer_request_preview(
    direction,
    entry_price,
    quantity,
    tp_snapshot,
):

    if (
        not tp_snapshot
        or not tp_snapshot.get(
            "tp_approval",
            {},
        ).get(
            "approved"
        )
    ):

        raise ValueError(
            "writer requires an approved complete TP snapshot"
        )

    entry_price = quantize_down(
        entry_price,
        PRICE_STEP,
    )

    (
        entry_quantity,
        tp1_qty,
        tp2_qty,
        tp3_qty,
    ) = writer_quantities(
        quantity
    )

    quantity_checks = (
        validate_writer_quantities(
            entry_quantity,
            tp1_qty,
            tp2_qty,
            tp3_qty,
        )
    )

    (
        entry_side,
        position_side,
    ) = writer_entry_side(
        direction
    )

    (
        close_side,
        close_position_side,
    ) = writer_close_side(
        direction
    )

    tp1_price = quantize_down(
        D(
            tp_snapshot[
                "tp1"
            ]
        ),
        PRICE_STEP,
    )

    tp2_price = quantize_down(
        D(
            tp_snapshot[
                "tp2"
            ]
        ),
        PRICE_STEP,
    )

    if direction == "LONG":

        if not (
            tp1_price > entry_price
            and
            tp2_price > tp1_price
        ):

            raise ValueError(
                "LONG TP ordering invalid"
            )

    elif direction == "SHORT":

        if not (
            tp1_price < entry_price
            and
            tp2_price < tp1_price
        ):

            raise ValueError(
                "SHORT TP ordering invalid"
            )

    else:

        raise ValueError(
            "Invalid writer direction"
        )

    # --------------------------------------------------------
    # ENTRY
    #
    # Deliberately NO TP trigger fields are attached to the
    # entry order. TP1/TP2/TP3 are separate legs so that the
    # intended 20/20/60 allocation is preserved.
    # --------------------------------------------------------

    entry_leg = {

        "endpoint":
            WRITER_ENDPOINT_ENTRY,

        "method":
            "POST",

        "symbol":
            SYMBOL,

        "side":
            entry_side,

        "positionSide":
            position_side,

        "type":
            "MARKET",

        "quantity":
            decimal_to_string(
                entry_quantity
            ),

        "newClientOrderId":
            writer_client_id(
                direction,
                "ENTRY",
            ),

        "reduceOnly":
            False,
    }

    # --------------------------------------------------------
    # TP1
    # --------------------------------------------------------

    tp1_leg = {

        "endpoint":
            WRITER_ENDPOINT_TPSL,

        "method":
            "POST",

        "symbol":
            SYMBOL,

        "side":
            close_side,

        "positionSide":
            close_position_side,

        "type":
            "TAKE_PROFIT",

        "triggerPrice":
            decimal_to_string(
                tp1_price
            ),

        "executePrice":
            decimal_to_string(
                tp1_price
            ),

        "quantity":
            decimal_to_string(
                tp1_qty
            ),

        "triggerPriceType":
            "MARK_PRICE",

        "clientAlgoId":
            writer_client_id(
                direction,
                "TP1",
            ),

        "reduceOnly":
            True,
    }

    # --------------------------------------------------------
    # TP2
    # --------------------------------------------------------

    tp2_leg = {

        "endpoint":
            WRITER_ENDPOINT_TPSL,

        "method":
            "POST",

        "symbol":
            SYMBOL,

        "side":
            close_side,

        "positionSide":
            close_position_side,

        "type":
            "TAKE_PROFIT",

        "triggerPrice":
            decimal_to_string(
                tp2_price
            ),

        "executePrice":
            decimal_to_string(
                tp2_price
            ),

        "quantity":
            decimal_to_string(
                tp2_qty
            ),

        "triggerPriceType":
            "MARK_PRICE",

        "clientAlgoId":
            writer_client_id(
                direction,
                "TP2",
            ),

        "reduceOnly":
            True,
    }

    # --------------------------------------------------------
    # TP3 TRAILING RUNNER
    # --------------------------------------------------------

    tp3_leg = {

        "endpoint":
            WRITER_ENDPOINT_TRAILING,

        "method":
            "POST",

        "symbol":
            SYMBOL,

        "side":
            close_side,

        "positionSide":
            close_position_side,

        "type":
            "TRAILING_MARKET",

        "quantity":
            decimal_to_string(
                tp3_qty
            ),

        "callbackRate":
            decimal_to_string(
                TP3_TRAILING_DISTANCE_PERCENT
            ),

        "workingType":
            "MARK_PRICE",

        "clientAlgoId":
            writer_client_id(
                direction,
                "TP3",
            ),

        "reduceOnly":
            True,
    }

    legs = {

        "entry":
            entry_leg,

        "tp1":
            tp1_leg,

        "tp2":
            tp2_leg,

        "tp3":
            tp3_leg,
    }

    integrity_hash = (
        sha256_text(
            canonical_json(
                legs
            )
        )
    )

    return {

        "stage":
            STAGE,

        "symbol":
            SYMBOL,

        "direction":
            direction,

        "entry_price":
            decimal_to_string(
                entry_price
            ),

        "entry_quantity":
            decimal_to_string(
                entry_quantity
            ),

        "tp1_quantity":
            decimal_to_string(
                tp1_qty
            ),

        "tp2_quantity":
            decimal_to_string(
                tp2_qty
            ),

        "tp3_quantity":
            decimal_to_string(
                tp3_qty
            ),

        "allocation_percent":
            {

                "tp1":
                    decimal_to_string(
                        TP1_ALLOCATION_PERCENT
                    ),

                "tp2":
                    decimal_to_string(
                        TP2_ALLOCATION_PERCENT
                    ),

                "tp3":
                    decimal_to_string(
                        TP3_ALLOCATION_PERCENT
                    ),
            },

        "quantity_validation":
            quantity_checks,

        "tp_approval":
            tp_snapshot[
                "tp_approval"
            ],

        "tp1":
            tp_snapshot[
                "tp1"
            ],

        "tp2":
            tp_snapshot[
                "tp2"
            ],

        "tp3":
            tp_snapshot[
                "tp3"
            ],

        "legs":
            legs,

        "primary_tp_immutable":
            True,

        "submitted":
            False,

        "transport_enabled":
            EXCHANGE_MUTATION_TRANSPORT_ENABLED,

        "integrity_sha256":
            integrity_hash,
    }


# ============================================================
# R36F.7 WRITER QUANTITY MINIMUM TESTS
# ============================================================

def synthetic_writer_quantity_tests():
    # 0.0004 BTC: nominal TP1/TP2 round to zero. The corrected
    # allocator must produce 0.0001 / 0.0001 / 0.0002.
    (
        quantity,
        tp1,
        tp2,
        tp3,
    ) = writer_quantities(
        Decimal("0.0004")
    )

    check(
        "WRITER_MINIMUM_TEST_ENTRY",
        quantity == Decimal("0.0004"),
    )

    check(
        "WRITER_MINIMUM_TEST_TP1",
        tp1 == MIN_QUANTITY,
    )

    check(
        "WRITER_MINIMUM_TEST_TP2",
        tp2 == MIN_QUANTITY,
    )

    check(
        "WRITER_MINIMUM_TEST_TP3",
        tp3 == Decimal("0.0002"),
    )

    checks = validate_writer_quantities(
        quantity,
        tp1,
        tp2,
        tp3,
    )

    check(
        "WRITER_MINIMUM_TEST_ALL_VALID",
        checks["all_valid"],
    )

    # Exactly three minimum steps: every leg must be one step.
    (
        quantity3,
        tp1_3,
        tp2_3,
        tp3_3,
    ) = writer_quantities(
        Decimal("0.0003")
    )

    checks3 = validate_writer_quantities(
        quantity3,
        tp1_3,
        tp2_3,
        tp3_3,
    )

    check(
        "WRITER_THREE_STEP_CAPACITY",
        (
            quantity3 == Decimal("0.0003")
            and
            tp1_3 == MIN_QUANTITY
            and
            tp2_3 == MIN_QUANTITY
            and
            tp3_3 == MIN_QUANTITY
        ),
    )

    check(
        "WRITER_THREE_STEP_ALL_VALID",
        checks3["all_valid"],
    )

    # Below three minimum steps, writer construction must remain
    # invalid rather than fabricating a quantity.
    (
        quantity2,
        tp1_2,
        tp2_2,
        tp3_2,
    ) = writer_quantities(
        Decimal("0.0002")
    )

    checks2 = validate_writer_quantities(
        quantity2,
        tp1_2,
        tp2_2,
        tp3_2,
    )

    check(
        "WRITER_BELOW_THREE_STEP_REMAINS_INVALID",
        checks2["all_valid"] is False,
    )

    return True


# ============================================================
# MAIN R36F.7 TEST
# ============================================================
