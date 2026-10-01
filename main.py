# ============================================================
# CLEAN WEEX BOT RECONSTRUCTION
# UNIT 1
# IMMUTABLE CONFIGURATION + READ-ONLY SAFETY FOUNDATION
#
# PURPOSE:
# Establish the trusted foundation for the new reconstruction.
#
# DESIGN RULE:
# UNIT 1 CANNOT PLACE, MODIFY, OR CANCEL ANY ORDER.
#
# THERE IS:
# - NO POST REQUEST FUNCTION
# - NO DEMO ORDER FUNCTION
# - NO REAL ORDER FUNCTION
# - NO TP SUBMISSION
# - NO SL SUBMISSION
# - NO BACKUP EXECUTION
#
# READ-ONLY FOUNDATION ONLY.
# ============================================================


import os
import time
import hmac
import hashlib
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

import requests


# ============================================================
# UNIT 1 VERSION
# ============================================================

CLEAN_BOT_VERSION = "CLEAN-R1.0"
CLEAN_UNIT = "UNIT-1"


# ============================================================
# EXCHANGE CONFIGURATION
# ============================================================

WEEX_BASE_URL = "https://api-contract.weex.com"

WEEX_DEMO_SYMBOL = "BTCSUSDT"

WEEX_POSITION_ENDPOINT = (
    "/capi/v3/sim/position/allPosition"
)


# ============================================================
# STRATEGY CONSTANTS
#
# These are configuration only.
# Unit 1 does NOT execute them.
# ============================================================

TARGET_LEVERAGE = Decimal("100")

QTY_STEP = Decimal("0.0001")

MIN_QTY = Decimal("0.0001")

PRICE_STEP = Decimal("0.1")

INITIAL_MARGIN_PERCENT = Decimal("5")

BACKUP_MARGIN_PERCENT = Decimal("5")

BACKUP_BUFFER_PERCENT = Decimal("0.30")

MAX_BACKUPS = 3

TP1_ALLOCATION_PERCENT = Decimal("25")

TP2_ALLOCATION_PERCENT = Decimal("25")

TP3_ALLOCATION_PERCENT = Decimal("50")

TP3_TRAILING_DISTANCE_PERCENT = Decimal("0.20")


# ============================================================
# EXECUTION POLICY
#
# These constants document the architecture.
#
# There is deliberately NO execution implementation in Unit 1.
# ============================================================

DEMO_MODE = True

REAL_ORDER_EXECUTION = False

STOP_LOSS_ENABLED = False

INITIAL_ENTRY_REQUIRES_ZERO_POSITION = True

FAIL_CLOSED_ON_UNKNOWN_POSITION = True


# ============================================================
# CREDENTIAL LOADING
#
# Read-only authentication still requires WEEX credentials.
#
# Never print credential values.
# ============================================================

WEEX_API_KEY = (
    os.getenv("WEEX_API_KEY")
    or os.getenv("API_KEY")
)

WEEX_SECRET_KEY = (
    os.getenv("WEEX_SECRET_KEY")
    or os.getenv("SECRET_KEY")
)

WEEX_PASSPHRASE = (
    os.getenv("WEEX_PASSPHRASE")
    or os.getenv("PASSPHRASE")
)


# ============================================================
# BASIC LOGGING
# ============================================================

def clean_log(*parts):
    print(
        time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.gmtime(),
        ),
        *parts,
        flush=True,
    )


# ============================================================
# DECIMAL SAFETY
# ============================================================

def clean_decimal(
    value,
    *,
    default=None,
):

    try:

        result = Decimal(
            str(value)
        )

        if not result.is_finite():
            raise InvalidOperation

        return result

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):

        return default


# ============================================================
# CREDENTIAL VALIDATION
#
# IMPORTANT:
# Presence only.
# Credential contents are NEVER logged.
# ============================================================

def clean_validate_credentials():

    missing = []

    if not WEEX_API_KEY:
        missing.append(
            "WEEX_API_KEY"
        )

    if not WEEX_SECRET_KEY:
        missing.append(
            "WEEX_SECRET_KEY"
        )

    if not WEEX_PASSPHRASE:
        missing.append(
            "WEEX_PASSPHRASE"
        )

    if missing:

        return {
            "valid": False,
            "missing": missing,
        }

    return {
        "valid": True,
        "missing": [],
    }


# ============================================================
# READ-ONLY ENDPOINT POLICY
#
# This is deliberately restrictive.
#
# Unit 1 is allowed to access ONLY endpoints explicitly
# registered here.
# ============================================================

READ_ONLY_ENDPOINTS = frozenset(
    {
        WEEX_POSITION_ENDPOINT,
    }
)


def clean_validate_read_only_endpoint(
    endpoint,
):

    if endpoint not in READ_ONLY_ENDPOINTS:

        raise RuntimeError(
            "CLEAN UNIT 1 BLOCKED NON-READ-ONLY ENDPOINT: "
            + str(endpoint)
        )

    return True


# ============================================================
# AUTHENTICATED GET SIGNATURE
#
# GET ONLY.
#
# No generalized request method is created because that could
# later accidentally permit POST through the same transport.
# ============================================================

def clean_build_get_signature(
    *,
    timestamp_ms,
    endpoint,
    query_string="",
):

    clean_validate_read_only_endpoint(
        endpoint
    )

    if not WEEX_SECRET_KEY:

        raise RuntimeError(
            "WEEX SECRET KEY MISSING"
        )

    request_path = endpoint

    if query_string:

        request_path += (
            "?"
            + query_string
        )

    message = (
        str(timestamp_ms)
        + "GET"
        + request_path
    )

    signature = hmac.new(
        WEEX_SECRET_KEY.encode(
            "utf-8"
        ),
        message.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).hexdigest()

    return signature


# ============================================================
# AUTHENTICATED GET HEADERS
# ============================================================

def clean_build_get_headers(
    *,
    timestamp_ms,
    signature,
):

    credentials = (
        clean_validate_credentials()
    )

    if not credentials[
        "valid"
    ]:

        raise RuntimeError(
            "WEEX CREDENTIALS MISSING: "
            + ", ".join(
                credentials[
                    "missing"
                ]
            )
        )

    return {
        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-TIMESTAMP":
            str(
                timestamp_ms
            ),

        "ACCESS-PASSPHRASE":
            WEEX_PASSPHRASE,

        "Content-Type":
            "application/json",
    }


# ============================================================
# SINGLE READ-ONLY TRANSPORT
#
# CRITICAL ARCHITECTURE RULE:
#
# This function physically supports GET only.
#
# There is no "method" argument.
# Therefore callers cannot change GET to POST.
# ============================================================

def clean_authenticated_get(
    *,
    endpoint,
    params=None,
    timeout_seconds=10,
):

    clean_validate_read_only_endpoint(
        endpoint
    )

    credentials = (
        clean_validate_credentials()
    )

    if not credentials[
        "valid"
    ]:

        return {
            "success": False,
            "confirmed": False,
            "reason":
                "CREDENTIALS_MISSING",
            "missing":
                credentials[
                    "missing"
                ],
        }

    if params is None:
        params = {}

    query_string = urlencode(
        params
    )

    timestamp_ms = int(
        time.time()
        * 1000
    )

    try:

        signature = (
            clean_build_get_signature(
                timestamp_ms=
                    timestamp_ms,

                endpoint=
                    endpoint,

                query_string=
                    query_string,
            )
        )

        headers = (
            clean_build_get_headers(
                timestamp_ms=
                    timestamp_ms,

                signature=
                    signature,
            )
        )

        url = (
            WEEX_BASE_URL
            + endpoint
        )

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout_seconds,
        )

    except requests.RequestException as exc:

        return {
            "success": False,
            "confirmed": False,
            "reason":
                "NETWORK_ERROR",
            "error":
                repr(exc),
        }

    except Exception as exc:

        return {
            "success": False,
            "confirmed": False,
            "reason":
                "READ_ONLY_GET_ERROR",
            "error":
                repr(exc),
        }

    try:

        payload = response.json()

    except Exception:

        payload = None

    if response.status_code != 200:

        return {
            "success": False,
            "confirmed": False,
            "reason":
                "HTTP_ERROR",
            "http_status":
                response.status_code,
            "payload":
                payload,
        }

    if payload is None:

        return {
            "success": False,
            "confirmed": False,
            "reason":
                "INVALID_JSON",
            "http_status":
                response.status_code,
        }

    return {
        "success": True,
        "confirmed": True,
        "reason":
            "AUTHENTICATED_GET_SUCCESS",
        "http_status":
            response.status_code,
        "payload":
            payload,
    }


# ============================================================
# UNIT 1 POSITION ENDPOINT CONNECTIVITY TEST
#
# READ ONLY.
#
# IMPORTANT:
# Unit 1 does NOT interpret whether the account is flat.
#
# That responsibility belongs to Unit 2.
#
# Unit 1 proves only:
# credentials
# endpoint lock
# authentication
# GET transport
# response
# ============================================================

def clean_unit_1_position_get_test():

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "CLEAN RECONSTRUCTION UNIT 1 START",
        flush=True,
    )

    print(
        "BOT VERSION =",
        CLEAN_BOT_VERSION,
        flush=True,
    )

    print(
        "MODE = DEMO",
        flush=True,
    )

    print(
        "REAL ORDER EXECUTION = FALSE",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    credentials = (
        clean_validate_credentials()
    )

    if credentials[
        "valid"
    ]:

        print(
            "PASS: UNIT 1 "
            "CREDENTIALS PRESENT",
            flush=True,
        )

    else:

        print(
            "FAIL: UNIT 1 "
            "CREDENTIALS MISSING =",
            credentials[
                "missing"
            ],
            flush=True,
        )

        return {
            "valid": False,
            "reason":
                "CREDENTIALS_MISSING",
        }

    clean_validate_read_only_endpoint(
        WEEX_POSITION_ENDPOINT
    )

    print(
        "PASS: UNIT 1 "
        "READ-ONLY ENDPOINT LOCK",
        flush=True,
    )

    print(
        "UNIT 1 REQUEST METHOD = GET",
        flush=True,
    )

    print(
        "UNIT 1 POSITION ENDPOINT =",
        WEEX_POSITION_ENDPOINT,
        flush=True,
    )

    result = (
        clean_authenticated_get(
            endpoint=
                WEEX_POSITION_ENDPOINT
        )
    )

    print(
        "UNIT 1 HTTP STATUS =",
        result.get(
            "http_status"
        ),
        flush=True,
    )

    if not result.get(
        "success"
    ):

        print(
            "FAIL: UNIT 1 "
            "AUTHENTICATED GET",
            flush=True,
        )

        print(
            "UNIT 1 REASON =",
            result.get(
                "reason"
            ),
            flush=True,
        )

        print(
            "UNIT 1 ERROR =",
            result.get(
                "error"
            ),
            flush=True,
        )

        return {
            "valid": False,
            "reason":
                result.get(
                    "reason"
                ),
        }

    print(
        "PASS: UNIT 1 "
        "AUTHENTICATED GET",
        flush=True,
    )

    print(
        "PASS: UNIT 1 "
        "WEEX RESPONSE RECEIVED",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    # --------------------------------------------------------
    # STRUCTURAL SAFETY ASSERTIONS
    # --------------------------------------------------------

    assert (
        REAL_ORDER_EXECUTION
        is False
    )

    assert (
        DEMO_MODE
        is True
    )

    assert (
        STOP_LOSS_ENABLED
        is False
    )

    assert (
        WEEX_POSITION_ENDPOINT
        in READ_ONLY_ENDPOINTS
    )

    print(
        "PASS: UNIT 1 "
        "DEMO MODE LOCK",
        flush=True,
    )

    print(
        "PASS: UNIT 1 "
        "REAL ORDER LOCK",
        flush=True,
    )

    print(
        "PASS: UNIT 1 "
        "GET-ONLY TRANSPORT",
        flush=True,
    )

    print(
        "PASS: UNIT 1 "
        "NO ORDER SUBMISSION FUNCTION",
        flush=True,
    )

    print(
        "PASS: UNIT 1 "
        "NO TP SUBMISSION",
        flush=True,
    )

    print(
        "PASS: UNIT 1 "
        "NO SL SUBMISSION",
        flush=True,
    )

    print(
        "PASS: UNIT 1 "
        "NO BACKUP EXECUTION",
        flush=True,
    )

    print(
        "ZERO WEEX POST = TRUE",
        flush=True,
    )

    print(
        "ZERO DEMO ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO REAL ORDER = TRUE",
        flush=True,
    )

    print(
        "ZERO EXCHANGE MUTATION = TRUE",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    print(
        "CLEAN RECONSTRUCTION UNIT 1 = PASS",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    return {
        "valid": True,
        "read_only": True,
        "authenticated_get": True,
        "exchange_mutation": False,
        "payload":
            result.get(
                "payload"
            ),
    }


# ============================================================
# UNIT 1 ENTRY POINT
# ============================================================

if __name__ == "__main__":

    clean_unit_1_position_get_test()
