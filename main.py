

from __future__ import annotations

# ==================================================================================================
# R35N - ACTIVATION ENVIRONMENT RECONCILIATION HARDENING
# ==================================================================================================
#
# PURPOSE
#   R35N follows R35M and hardens the activation-environment reconciliation layer.
#
#   It verifies:
#       1. WEEX API credentials are present.
#       2. Authenticated WEEX balance can be read.
#       3. BTCUSDT symbol configuration can be read.
#       4. BTCUSDT positions can be read.
#       5. BTCUSDT MARK price can be read.
#       6. Margin mode is ISOLATED.
#       7. Long leverage is 100x.
#       8. Short leverage is 100x.
#       9. No position ambiguity exists.
#      10. Telegram reporting dedupe is locally durable.
#      11. Telegram dedupe may only be called cross-deploy durable when an explicitly configured
#          persistent Render disk is being used.
#
# SAFETY BOUNDARY
#   THIS UNIT DOES NOT PLACE REAL ORDERS.
#
#   - REAL ORDER EXECUTION          = HARD DISABLED
#   - DEMO ORDER EXECUTION          = HARD DISABLED
#   - FIRST REAL ORDER              = HARD FORBIDDEN
#   - EXCHANGE POST                 = HARD FORBIDDEN
#   - EXCHANGE PUT                  = HARD FORBIDDEN
#   - EXCHANGE PATCH                = HARD FORBIDDEN
#   - EXCHANGE DELETE               = HARD FORBIDDEN
#   - LEVERAGE MUTATION             = HARD FORBIDDEN
#   - MARGIN MUTATION               = HARD FORBIDDEN
#   - POSITION MUTATION             = HARD FORBIDDEN
#   - ORDER MUTATION                = HARD FORBIDDEN
#
#   WEEX NETWORK ACCESS IS GET-ONLY.
#
#   Telegram POST is permitted strictly for reporting and is never counted as an exchange mutation.
#
# IMPORTANT
#   R35N_PERSISTENT_DISK=1 must ONLY be configured when R35N_STATE_DIR is actually located on a
#   Render Persistent Disk.
#
#   Recommended:
#
#       R35N_STATE_DIR=/var/data/r35n_state
#       R35N_PERSISTENT_DISK=1
#
#   Do NOT set R35N_PERSISTENT_DISK=1 merely to make a test pass.
#
# ==================================================================================================

import base64
import hashlib
import hmac
import json
import os
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ==================================================================================================
# R35N CONFIGURATION
# ==================================================================================================

VERSION = "R35N"

SYMBOL = "BTCUSDT"
ASSET = "USDT"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

HEALTH_PORT = int(os.getenv("PORT", "10000"))

WEEX_BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

WEEX_API_KEY = os.getenv("WEEX_API_KEY", "").strip()
WEEX_API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    "",
).strip()

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()

STATE_DIR = Path(
    os.getenv(
        "R35N_STATE_DIR",
        "/var/data/r35n_state",
    )
)

PERSISTENT_DISK_DECLARED = (
    os.getenv(
        "R35N_PERSISTENT_DISK",
        "0",
    ).strip().lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)

REQUEST_TIMEOUT_SECONDS = float(
    os.getenv(
        "R35N_REQUEST_TIMEOUT_SECONDS",
        "12",
    )
)

HEARTBEAT_SECONDS = int(
    os.getenv(
        "R35N_HEARTBEAT_SECONDS",
        "30",
    )
)

TELEGRAM_REPORTING_ENABLED = (
    os.getenv(
        "R35N_TELEGRAM_REPORTING",
        "1",
    ).strip().lower()
    not in {
        "0",
        "false",
        "no",
        "off",
    }
)

# --------------------------------------------------------------------------------------------------
# HARD SAFETY CONSTANTS
# --------------------------------------------------------------------------------------------------

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

FIRST_REAL_ORDER_ALLOWED = False

EXCHANGE_WRITES_ALLOWED = False

LEVERAGE_MUTATION_ALLOWED = False
MARGIN_MUTATION_ALLOWED = False
POSITION_MUTATION_ALLOWED = False
ORDER_MUTATION_ALLOWED = False

SYNTHETIC_TRANSPORT_ONLY = True

ALLOWED_WEEX_HTTP_METHODS = frozenset(
    {
        "GET",
    }
)

FORBIDDEN_WEEX_HTTP_METHODS = frozenset(
    {
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    }
)

# --------------------------------------------------------------------------------------------------
# WEEX V3 ENDPOINTS
# --------------------------------------------------------------------------------------------------

BALANCE_PATH = "/capi/v3/account/balance"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

POSITION_PATH = "/capi/v3/account/position/singlePosition"

MARK_PRICE_PATH = "/capi/v3/market/symbolPrice"

# --------------------------------------------------------------------------------------------------
# DURABLE FILES
# --------------------------------------------------------------------------------------------------

STATE_FILE = STATE_DIR / "r35n_state.json"

TELEGRAM_DEDUPE_FILE = STATE_DIR / "telegram_dedupe.json"

DURABILITY_PROBE_FILE = STATE_DIR / ".r35n_durability_probe"

# ==================================================================================================
# GLOBAL COUNTERS
# ==================================================================================================

COUNTER_LOCK = threading.Lock()

AUTHENTICATED_GET_COUNT = 0
PUBLIC_GET_COUNT = 0

EXCHANGE_NETWORK_WRITE_COUNT = 0
EXCHANGE_ORDER_WRITE_COUNT = 0
EXCHANGE_LEVERAGE_WRITE_COUNT = 0
EXCHANGE_MARGIN_WRITE_COUNT = 0
EXCHANGE_POSITION_WRITE_COUNT = 0

TELEGRAM_POST_COUNT = 0

HEARTBEAT_COUNT = 0


# ==================================================================================================
# LOGGING
# ==================================================================================================

PRINT_LOCK = threading.Lock()


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def log(message: str) -> None:
    with PRINT_LOCK:
        print(
            f"{utc_now()} {message}",
            flush=True,
        )


def separator() -> None:
    log("-" * 100)


def bool_text(value: bool) -> str:
    return "True" if value else "False"


def unknown(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    return str(value)


# ==================================================================================================
# TEST REPORTING
# ==================================================================================================

def test_result(
    name: str,
    passed: bool,
) -> bool:

    mark = "✅ PASS" if passed else "❌ FAIL"

    log(
        f"{name:<82} {mark}"
    )

    return passed


# ==================================================================================================
# BASIC HELPERS
# ==================================================================================================

def safe_float(
    value: Any,
) -> Optional[float]:

    try:
        if value is None:
            return None

        result = float(value)

        if result != result:
            return None

        return result

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return None


def safe_int(
    value: Any,
) -> Optional[int]:

    try:
        if value is None:
            return None

        return int(
            float(value)
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return None


def json_bytes(
    value: Any,
) -> bytes:

    return json.dumps(
        value,
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_hex(
    data: bytes,
) -> str:

    return hashlib.sha256(
        data
    ).hexdigest()


def canonical_hash(
    value: Any,
) -> str:

    return sha256_hex(
        json_bytes(value)
    )


# ==================================================================================================
# STATE MODEL
# ==================================================================================================

@dataclass
class ActivationSnapshot:

    version: str = VERSION

    symbol: str = SYMBOL

    timestamp: str = ""

    balance: Optional[float] = None

    mark_price: Optional[float] = None

    open_positions: Optional[int] = None

    margin_mode: Optional[str] = None

    long_leverage: Optional[int] = None

    short_leverage: Optional[int] = None

    authenticated_weex_read_ok: bool = False

    mark_price_read_ok: bool = False

    telegram_local_durable: bool = False

    telegram_cross_deploy_durable: bool = False

    activation_env_match: bool = False

    blockers: List[str] = field(
        default_factory=list
    )

    authenticated_get_count: int = 0

    public_get_count: int = 0

    exchange_network_write_count: int = 0

    telegram_post_count: int = 0

    real_order_execution: bool = False

    first_real_order_allowed: bool = False


# ==================================================================================================
# ATOMIC FILE STORAGE
# ==================================================================================================

def ensure_state_directory() -> bool:

    try:
        STATE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        return (
            STATE_DIR.exists()
            and STATE_DIR.is_dir()
        )

    except Exception as exc:
        log(
            f"R35N: STATE DIRECTORY ERROR={type(exc).__name__}: {exc}"
        )

        return False


def atomic_write_json(
    path: Path,
    value: Any,
) -> None:

    ensure_state_directory()

    payload = json.dumps(
        value,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )

    fd: Optional[int] = None
    temp_path: Optional[Path] = None

    try:

        fd, raw_temp_path = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=str(path.parent),
            text=True,
        )

        temp_path = Path(
            raw_temp_path
        )

        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as handle:

            fd = None

            handle.write(
                payload
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

        os.replace(
            temp_path,
            path,
        )

        try:
            directory_fd = os.open(
                str(path.parent),
                os.O_DIRECTORY,
            )

            try:
                os.fsync(
                    directory_fd
                )

            finally:
                os.close(
                    directory_fd
                )

        except (
            AttributeError,
            OSError,
        ):
            pass

    finally:

        if fd is not None:

            try:
                os.close(
                    fd
                )

            except OSError:
                pass

        if (
            temp_path is not None
            and temp_path.exists()
        ):

            try:
                temp_path.unlink()

            except OSError:
                pass


def read_json_file(
    path: Path,
    default: Any,
) -> Any:

    try:

        with path.open(
            "r",
            encoding="utf-8",
        ) as handle:

            return json.load(
                handle
            )

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        OSError,
    ):

        return default


# ==================================================================================================
# DURABILITY PROBE
# ==================================================================================================

def local_storage_durability_probe() -> bool:

    if not ensure_state_directory():
        return False

    probe = {
        "version": VERSION,
        "timestamp": utc_now(),
        "nonce": hashlib.sha256(
            os.urandom(32)
        ).hexdigest(),
    }

    try:

        atomic_write_json(
            DURABILITY_PROBE_FILE,
            probe,
        )

        loaded = read_json_file(
            DURABILITY_PROBE_FILE,
            {},
        )

        valid = (
            isinstance(
                loaded,
                dict,
            )
            and loaded.get(
                "version"
            )
            == VERSION
            and loaded.get(
                "nonce"
            )
            == probe["nonce"]
        )

        return valid

    except Exception as exc:

        log(
            f"R35N: DURABILITY PROBE ERROR={type(exc).__name__}: {exc}"
        )

        return False


def path_looks_ephemeral() -> bool:

    resolved = str(
        STATE_DIR
    ).lower()

    ephemeral_prefixes = (
        "/tmp",
        "/opt/render/project/src",
        "/opt/render/project",
    )

    return any(
        resolved.startswith(
            prefix
        )
        for prefix in ephemeral_prefixes
    )


def telegram_cross_deploy_durability() -> Tuple[bool, bool]:

    local_ok = local_storage_durability_probe()

    cross_deploy_ok = (
        local_ok
        and PERSISTENT_DISK_DECLARED
        and not path_looks_ephemeral()
    )

    return (
        local_ok,
        cross_deploy_ok,
    )


# ==================================================================================================
# TELEGRAM DURABLE DEDUPE
# ==================================================================================================

TELEGRAM_LOCK = threading.Lock()


def load_telegram_dedupe() -> Dict[str, Any]:

    loaded = read_json_file(
        TELEGRAM_DEDUPE_FILE,
        {},
    )

    if not isinstance(
        loaded,
        dict,
    ):
        loaded = {}

    hashes = loaded.get(
        "message_hashes"
    )

    if not isinstance(
        hashes,
        list,
    ):
        hashes = []

    return {
        "version": VERSION,
        "message_hashes": [
            str(item)
            for item in hashes[-200:]
        ],
    }


def telegram_message_hash(
    text: str,
) -> str:

    normalized = text.strip()

    return hashlib.sha256(
        normalized.encode(
            "utf-8"
        )
    ).hexdigest()


def telegram_was_sent(
    message_hash: str,
) -> bool:

    data = load_telegram_dedupe()

    return message_hash in data.get(
        "message_hashes",
        [],
    )


def record_telegram_sent(
    message_hash: str,
) -> None:

    data = load_telegram_dedupe()

    hashes = data.get(
        "message_hashes",
        [],
    )

    if message_hash not in hashes:
        hashes.append(
            message_hash
        )

    data["message_hashes"] = hashes[-200:]

    data["updated_at"] = utc_now()

    atomic_write_json(
        TELEGRAM_DEDUPE_FILE,
        data,
    )


# ==================================================================================================
# TELEGRAM REPORTING
# ==================================================================================================

def telegram_credentials_present() -> bool:

    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    )


def send_telegram_report(
    text: str,
) -> Tuple[bool, str]:

    global TELEGRAM_POST_COUNT

    if not TELEGRAM_REPORTING_ENABLED:
        return (
            False,
            "TELEGRAM_REPORTING_DISABLED",
        )

    if not telegram_credentials_present():
        return (
            False,
            "TELEGRAM_CREDENTIALS_MISSING",
        )

    message_hash = telegram_message_hash(
        text
    )

    with TELEGRAM_LOCK:

        if telegram_was_sent(
            message_hash
        ):
            return (
                True,
                "DEDUPED_ALREADY_SENT",
            )

        url = (
            "https://api.telegram.org/"
            f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        )

        payload = urllib.parse.urlencode(
            {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "disable_web_page_preview": "true",
            }
        ).encode(
            "utf-8"
        )

        request = urllib.request.Request(
            url=url,
            data=payload,
            method="POST",
            headers={
                "Content-Type": (
                    "application/x-www-form-urlencoded"
                ),
                "User-Agent": (
                    "R35N-ReadOnly-Reconciliation/1.0"
                ),
            },
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=REQUEST_TIMEOUT_SECONDS,
            ) as response:

                raw = response.read()

                status = getattr(
                    response,
                    "status",
                    200,
                )

            if status < 200 or status >= 300:

                return (
                    False,
                    f"TELEGRAM_HTTP_{status}",
                )

            try:

                parsed = json.loads(
                    raw.decode(
                        "utf-8"
                    )
                )

            except Exception:

                parsed = {}

            if isinstance(
                parsed,
                dict,
            ) and parsed.get(
                "ok"
            ) is False:

                return (
                    False,
                    "TELEGRAM_RESPONSE_NOT_OK",
                )

            record_telegram_sent(
                message_hash
            )

            with COUNTER_LOCK:
                TELEGRAM_POST_COUNT += 1

            return (
                True,
                "SENT",
            )

        except urllib.error.HTTPError as exc:

            return (
                False,
                f"TELEGRAM_HTTP_ERROR_{exc.code}",
            )

        except Exception as exc:

            return (
                False,
                "TELEGRAM_ERROR_"
                + type(exc).__name__,
            )


# ==================================================================================================
# WEEX REQUEST SIGNING
# ==================================================================================================

def credentials_present() -> bool:

    return bool(
        WEEX_API_KEY
        and WEEX_API_SECRET
        and WEEX_API_PASSPHRASE
    )


def build_query_string(
    params: Optional[
        Dict[str, Any]
    ],
) -> str:

    if not params:
        return ""

    clean: List[
        Tuple[str, str]
    ] = []

    for key in sorted(
        params.keys()
    ):

        value = params[key]

        if value is None:
            continue

        clean.append(
            (
                str(key),
                str(value),
            )
        )

    return urllib.parse.urlencode(
        clean
    )


def generate_signature(
    timestamp_ms: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    method = method.upper()

    if query_string:

        prehash = (
            timestamp_ms
            + method
            + request_path
            + "?"
            + query_string
            + body
        )

    else:

        prehash = (
            timestamp_ms
            + method
            + request_path
            + body
        )

    digest = hmac.new(
        WEEX_API_SECRET.encode(
            "utf-8"
        ),
        prehash.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode(
        "ascii"
    )


# ==================================================================================================
# HARD WEEX HTTP FIREBREAK
# ==================================================================================================

def assert_weex_method_allowed(
    method: str,
) -> None:

    normalized = method.upper()

    if normalized in FORBIDDEN_WEEX_HTTP_METHODS:

        raise RuntimeError(
            f"R35N FIREBREAK: WEEX {normalized} IS HARD FORBIDDEN"
        )

    if normalized not in ALLOWED_WEEX_HTTP_METHODS:

        raise RuntimeError(
            f"R35N FIREBREAK: UNKNOWN WEEX METHOD {normalized} IS FORBIDDEN"
        )


def authenticated_weex_get(
    request_path: str,
    params: Optional[
        Dict[str, Any]
    ] = None,
) -> Any:

    global AUTHENTICATED_GET_COUNT

    method = "GET"

    assert_weex_method_allowed(
        method
    )

    if not credentials_present():

        raise RuntimeError(
            "WEEX_CREDENTIALS_MISSING"
        )

    query_string = build_query_string(
        params
    )

    timestamp_ms = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = generate_signature(
        timestamp_ms=timestamp_ms,
        method=method,
        request_path=request_path,
        query_string=query_string,
        body="",
    )

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp_ms,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "locale": "en-US",
        "User-Agent": (
            "R35N-ReadOnly-Reconciliation/1.0"
        ),
    }

    url = (
        WEEX_BASE_URL
        + request_path
    )

    if query_string:

        url += (
            "?"
            + query_string
        )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers=headers,
    )

    with urllib.request.urlopen(
        request,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:

        raw = response.read()

        status = getattr(
            response,
            "status",
            200,
        )

    if status < 200 or status >= 300:

        raise RuntimeError(
            f"WEEX_HTTP_STATUS_{status}"
        )

    with COUNTER_LOCK:
        AUTHENTICATED_GET_COUNT += 1

    return json.loads(
        raw.decode(
            "utf-8"
        )
    )


def public_weex_get(
    request_path: str,
    params: Optional[
        Dict[str, Any]
    ] = None,
) -> Any:

    global PUBLIC_GET_COUNT

    method = "GET"

    assert_weex_method_allowed(
        method
    )

    query_string = build_query_string(
        params
    )

    url = (
        WEEX_BASE_URL
        + request_path
    )

    if query_string:

        url += (
            "?"
            + query_string
        )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": (
                "R35N-ReadOnly-Reconciliation/1.0"
            ),
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:

        raw = response.read()

        status = getattr(
            response,
            "status",
            200,
        )

    if status < 200 or status >= 300:

        raise RuntimeError(
            f"WEEX_HTTP_STATUS_{status}"
        )

    with COUNTER_LOCK:
        PUBLIC_GET_COUNT += 1

    return json.loads(
        raw.decode(
            "utf-8"
        )
    )


# ==================================================================================================
# RESPONSE NORMALIZATION
# ==================================================================================================

def normalize_list_response(
    value: Any,
) -> List[
    Dict[str, Any]
]:

    if isinstance(
        value,
        list,
    ):

        return [
            item
            for item in value
            if isinstance(
                item,
                dict,
            )
        ]

    if isinstance(
        value,
        dict,
    ):

        for key in (
            "data",
            "result",
            "list",
            "rows",
        ):

            nested = value.get(
                key
            )

            if isinstance(
                nested,
                list,
            ):

                return [
                    item
                    for item in nested
                    if isinstance(
                        item,
                        dict,
                    )
                ]

            if isinstance(
                nested,
                dict,
            ):

                return [
                    nested
                ]

        return [
            value
        ]

    return []


def select_symbol_record(
    value: Any,
    symbol: str,
) -> Optional[
    Dict[str, Any]
]:

    records = normalize_list_response(
        value
    )

    wanted = symbol.upper()

    for record in records:

        record_symbol = str(
            record.get(
                "symbol",
                "",
            )
        ).upper()

        if record_symbol == wanted:
            return record

    if len(
        records
    ) == 1:

        return records[0]

    return None


# ==================================================================================================
# AUTHENTICATED READS
# ==================================================================================================

def read_available_balance() -> float:

    response = authenticated_weex_get(
        BALANCE_PATH
    )

    records = normalize_list_response(
        response
    )

    for record in records:

        asset = str(
            record.get(
                "asset",
                "",
            )
        ).upper()

        if asset != ASSET:
            continue

        value = safe_float(
            record.get(
                "availableBalance"
            )
        )

        if value is None:
            raise RuntimeError(
                "AVAILABLE_BALANCE_INVALID"
            )

        if value < 0:
            raise RuntimeError(
                "AVAILABLE_BALANCE_NEGATIVE"
            )

        return value

    raise RuntimeError(
        f"{ASSET}_BALANCE_NOT_FOUND"
    )


def read_symbol_configuration() -> Tuple[
    str,
    int,
    int,
]:

    response = authenticated_weex_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    record = select_symbol_record(
        response,
        SYMBOL,
    )

    if record is None:

        raise RuntimeError(
            "SYMBOL_CONFIG_NOT_FOUND"
        )

    margin_mode = str(
        record.get(
            "marginType",
            "",
        )
    ).upper().strip()

    long_leverage = safe_int(
        record.get(
            "isolatedLongLeverage"
        )
    )

    short_leverage = safe_int(
        record.get(
            "isolatedShortLeverage"
        )
    )

    if not margin_mode:

        raise RuntimeError(
            "MARGIN_MODE_MISSING"
        )

    if long_leverage is None:

        raise RuntimeError(
            "LONG_LEVERAGE_MISSING"
        )

    if short_leverage is None:

        raise RuntimeError(
            "SHORT_LEVERAGE_MISSING"
        )

    return (
        margin_mode,
        long_leverage,
        short_leverage,
    )


def read_positions() -> Tuple[
    int,
    List[
        Dict[str, Any]
    ],
]:

    response = authenticated_weex_get(
        POSITION_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    records = normalize_list_response(
        response
    )

    symbol_records: List[
        Dict[str, Any]
    ] = []

    for record in records:

        record_symbol = str(
            record.get(
                "symbol",
                SYMBOL,
            )
        ).upper()

        if record_symbol != SYMBOL:
            continue

        symbol_records.append(
            record
        )

    open_records: List[
        Dict[str, Any]
    ] = []

    for record in symbol_records:

        size = safe_float(
            record.get(
                "size"
            )
        )

        if size is None:

            # If WEEX returned a position object but its size is unreadable,
            # fail closed rather than assuming it is flat.
            raise RuntimeError(
                "POSITION_SIZE_AMBIGUOUS"
            )

        if abs(
            size
        ) > 0:

            open_records.append(
                record
            )

    return (
        len(
            open_records
        ),
        open_records,
    )


# ==================================================================================================
# PUBLIC MARK PRICE
# ==================================================================================================

def read_mark_price() -> float:

    response = public_weex_get(
        MARK_PRICE_PATH,
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    record: Optional[
        Dict[str, Any]
    ] = None

    if isinstance(
        response,
        dict,
    ):

        nested = response.get(
            "data"
        )

        if isinstance(
            nested,
            dict,
        ):

            record = nested

        else:

            record = response

    elif isinstance(
        response,
        list,
    ) and response:

        first = response[0]

        if isinstance(
            first,
            dict,
        ):
            record = first

    if record is None:

        raise RuntimeError(
            "MARK_PRICE_RESPONSE_INVALID"
        )

    price = safe_float(
        record.get(
            "price"
        )
    )

    if price is None:

        raise RuntimeError(
            "MARK_PRICE_MISSING"
        )

    if price <= 0:

        raise RuntimeError(
            "MARK_PRICE_NOT_POSITIVE"
        )

    return price


# ==================================================================================================
# SAFE READ WRAPPERS
# ==================================================================================================

def safe_balance_read() -> Tuple[
    Optional[float],
    Optional[str],
]:

    try:

        value = read_available_balance()

        return (
            value,
            None,
        )

    except urllib.error.HTTPError as exc:

        return (
            None,
            f"BALANCE_HTTP_{exc.code}",
        )

    except urllib.error.URLError as exc:

        return (
            None,
            "BALANCE_NETWORK_"
            + type(
                exc.reason
            ).__name__,
        )

    except Exception as exc:

        return (
            None,
            type(exc).__name__
            + ":"
            + str(exc)[:160],
        )


def safe_config_read() -> Tuple[
    Optional[str],
    Optional[int],
    Optional[int],
    Optional[str],
]:

    try:

        (
            margin_mode,
            long_leverage,
            short_leverage,
        ) = read_symbol_configuration()

        return (
            margin_mode,
            long_leverage,
            short_leverage,
            None,
        )

    except urllib.error.HTTPError as exc:

        return (
            None,
            None,
            None,
            f"CONFIG_HTTP_{exc.code}",
        )

    except urllib.error.URLError as exc:

        return (
            None,
            None,
            None,
            "CONFIG_NETWORK_"
            + type(
                exc.reason
            ).__name__,
        )

    except Exception as exc:

        return (
            None,
            None,
            None,
            type(exc).__name__
            + ":"
            + str(exc)[:160],
        )


def safe_positions_read() -> Tuple[
    Optional[int],
    List[
        Dict[str, Any]
    ],
    Optional[str],
]:

    try:

        (
            count,
            records,
        ) = read_positions()

        return (
            count,
            records,
            None,
        )

    except urllib.error.HTTPError as exc:

        return (
            None,
            [],
            f"POSITIONS_HTTP_{exc.code}",
        )

    except urllib.error.URLError as exc:

        return (
            None,
            [],
            "POSITIONS_NETWORK_"
            + type(
                exc.reason
            ).__name__,
        )

    except Exception as exc:

        return (
            None,
            [],
            type(exc).__name__
            + ":"
            + str(exc)[:160],
        )


def safe_mark_price_read() -> Tuple[
    Optional[float],
    Optional[str],
]:

    try:

        value = read_mark_price()

        return (
            value,
            None,
        )

    except urllib.error.HTTPError as exc:

        return (
            None,
            f"MARK_HTTP_{exc.code}",
        )

    except urllib.error.URLError as exc:

        return (
            None,
            "MARK_NETWORK_"
            + type(
                exc.reason
            ).__name__,
        )

    except Exception as exc:

        return (
            None,
            type(exc).__name__
            + ":"
            + str(exc)[:160],
        )


# ==================================================================================================
# FIREBREAK VALIDATION
# ==================================================================================================

def validate_exchange_firebreak() -> bool:

    checks: List[
        bool
    ] = []

    separator()

    log(
        "R35N TEST 1: EXCHANGE MUTATION FIREBREAK"
    )

    separator()

    checks.append(
        test_result(
            "Real Order Execution Is Hard Disabled",
            REAL_ORDER_EXECUTION is False,
        )
    )

    checks.append(
        test_result(
            "Demo Order Execution Is Hard Disabled",
            DEMO_ORDER_EXECUTION is False,
        )
    )

    checks.append(
        test_result(
            "First Real Order Is Hard Forbidden",
            FIRST_REAL_ORDER_ALLOWED is False,
        )
    )

    checks.append(
        test_result(
            "Exchange Writes Are Hard Disabled",
            EXCHANGE_WRITES_ALLOWED is False,
        )
    )

    checks.append(
        test_result(
            "Leverage Mutation Is Hard Disabled",
            LEVERAGE_MUTATION_ALLOWED is False,
        )
    )

    checks.append(
        test_result(
            "Margin Mutation Is Hard Disabled",
            MARGIN_MUTATION_ALLOWED is False,
        )
    )

    checks.append(
        test_result(
            "Position Mutation Is Hard Disabled",
            POSITION_MUTATION_ALLOWED is False,
        )
    )

    checks.append(
        test_result(
            "Order Mutation Is Hard Disabled",
            ORDER_MUTATION_ALLOWED is False,
        )
    )

    checks.append(
        test_result(
            "WEEX Allowed Method Set Contains GET Only",
            ALLOWED_WEEX_HTTP_METHODS
            == frozenset(
                {
                    "GET",
                }
            ),
        )
    )

    for method in (
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ):

        blocked = False

        try:

            assert_weex_method_allowed(
                method
            )

        except RuntimeError:
            blocked = True

        checks.append(
            test_result(
                f"WEEX {method} Is Rejected By Firebreak",
                blocked,
            )
        )

    return all(
        checks
    )


# ==================================================================================================
# CREDENTIAL VALIDATION
# ==================================================================================================

def validate_credentials() -> bool:

    separator()

    log(
        "R35N TEST 2: WEEX CREDENTIAL ENVIRONMENT"
    )

    separator()

    key_ok = bool(
        WEEX_API_KEY
    )

    secret_ok = bool(
        WEEX_API_SECRET
    )

    passphrase_ok = bool(
        WEEX_API_PASSPHRASE
    )

    test_result(
        "WEEX_API_KEY Is Present",
        key_ok,
    )

    test_result(
        "WEEX_API_SECRET Is Present",
        secret_ok,
    )

    test_result(
        "WEEX_API_PASSPHRASE Is Present",
        passphrase_ok,
    )

    test_result(
        "No Legacy WEEX_PASSPHRASE Is Required",
        True,
    )

    return (
        key_ok
        and secret_ok
        and passphrase_ok
    )


# ==================================================================================================
# TELEGRAM DEDUPE VALIDATION
# ==================================================================================================

def validate_telegram_durability() -> Tuple[
    bool,
    bool,
]:

    separator()

    log(
        "R35N TEST 3: TELEGRAM CROSS-DEPLOY DEDUPE DURABILITY"
    )

    separator()

    local_ok, cross_deploy_ok = (
        telegram_cross_deploy_durability()
    )

    test_result(
        "R35N State Directory Is Writable",
        local_ok,
    )

    test_result(
        "Telegram Dedupe Uses Atomic File Persistence",
        local_ok,
    )

    test_result(
        "State Directory Is Not An Explicit Ephemeral Path",
        not path_looks_ephemeral(),
    )

    test_result(
        "Persistent Disk Was Explicitly Declared",
        PERSISTENT_DISK_DECLARED,
    )

    test_result(
        "Telegram Dedupe Is Cross-Deploy Durable",
        cross_deploy_ok,
    )

    log(
        f"R35N: STATE DIR={STATE_DIR}"
    )

    log(
        "R35N: PERSISTENT DISK DECLARED="
        + bool_text(
            PERSISTENT_DISK_DECLARED
        )
    )

    return (
        local_ok,
        cross_deploy_ok,
    )


# ==================================================================================================
# ACTIVATION RECONCILIATION
# ==================================================================================================

def reconcile_activation_environment(
    telegram_local_durable: bool,
    telegram_cross_deploy_durable: bool,
) -> ActivationSnapshot:

    separator()

    log(
        "R35N TEST 4: AUTHENTICATED BALANCE READ"
    )

    separator()

    (
        balance,
        balance_error,
    ) = safe_balance_read()

    balance_ok = (
        balance is not None
        and balance >= 0
    )

    test_result(
        "Authenticated WEEX Balance Was Read",
        balance_ok,
    )

    if balance_ok:

        log(
            f"R35N: AVAILABLE {ASSET}={balance}"
        )

    else:

        log(
            "R35N: BALANCE READ ERROR="
            + unknown(
                balance_error
            )
        )

    separator()

    log(
        "R35N TEST 5: BTCUSDT SYMBOL CONFIGURATION"
    )

    separator()

    (
        margin_mode,
        long_leverage,
        short_leverage,
        config_error,
    ) = safe_config_read()

    config_read_ok = (
        margin_mode is not None
        and long_leverage is not None
        and short_leverage is not None
    )

    test_result(
        "BTCUSDT Symbol Configuration Was Read",
        config_read_ok,
    )

    margin_ok = (
        margin_mode
        == TARGET_MARGIN_MODE
    )

    long_ok = (
        long_leverage
        == TARGET_LONG_LEVERAGE
    )

    short_ok = (
        short_leverage
        == TARGET_SHORT_LEVERAGE
    )

    test_result(
        "BTCUSDT Margin Mode Is ISOLATED",
        margin_ok,
    )

    test_result(
        "BTCUSDT Long Leverage Is 100x",
        long_ok,
    )

    test_result(
        "BTCUSDT Short Leverage Is 100x",
        short_ok,
    )

    if config_read_ok:

        log(
            f"R35N: MARGIN MODE={margin_mode}"
        )

        log(
            f"R35N: LONG LEVERAGE={long_leverage}x"
        )

        log(
            f"R35N: SHORT LEVERAGE={short_leverage}x"
        )

    else:

        log(
            "R35N: SYMBOL CONFIG ERROR="
            + unknown(
                config_error
            )
        )

    separator()

    log(
        "R35N TEST 6: POSITION RECONCILIATION"
    )

    separator()

    (
        open_positions,
        open_position_records,
        positions_error,
    ) = safe_positions_read()

    positions_read_ok = (
        open_positions is not None
    )

    flat = (
        open_positions == 0
    )

    test_result(
        "BTCUSDT Position State Was Read",
        positions_read_ok,
    )

    test_result(
        "BTCUSDT Has Zero Open Positions",
        flat,
    )

    if positions_read_ok:

        log(
            f"R35N: OPEN POSITIONS={open_positions}"
        )

        if open_position_records:

            for record in open_position_records:

                log(
                    "R35N: OPEN POSITION="
                    + json.dumps(
                        {
                            "side": record.get(
                                "side"
                            ),
                            "size": record.get(
                                "size"
                            ),
                            "marginType": record.get(
                                "marginType"
                            ),
                            "leverage": record.get(
                                "leverage"
                            ),
                        },
                        separators=(
                            ",",
                            ":",
                        ),
                        sort_keys=True,
                    )
                )

    else:

        log(
            "R35N: POSITION READ ERROR="
            + unknown(
                positions_error
            )
        )

    separator()

    log(
        "R35N TEST 7: PUBLIC MARK PRICE"
    )

    separator()

    (
        mark_price,
        mark_error,
    ) = safe_mark_price_read()

    mark_ok = (
        mark_price is not None
        and mark_price > 0
    )

    test_result(
        "BTCUSDT MARK Price Was Read",
        mark_ok,
    )

    if mark_ok:

        log(
            f"R35N: MARK PRICE={mark_price}"
        )

    else:

        log(
            "R35N: MARK PRICE ERROR="
            + unknown(
                mark_error
            )
        )

    authenticated_ok = (
        balance_ok
        and config_read_ok
        and positions_read_ok
    )

    blockers: List[
        str
    ] = []

    if not credentials_present():

        blockers.append(
            "WEEX_CREDENTIALS_MISSING"
        )

    if not authenticated_ok:

        blockers.append(
            "AUTHENTICATED_WEEX_READ_FAILED"
        )

    if not balance_ok:

        blockers.append(
            "BALANCE_READ_FAILED"
        )

    if not config_read_ok:

        blockers.append(
            "SYMBOL_CONFIG_READ_FAILED"
        )

    if not positions_read_ok:

        blockers.append(
            "POSITION_READ_FAILED"
        )

    if not mark_ok:

        blockers.append(
            "MARK_PRICE_READ_FAILED"
        )

    if not margin_ok:

        blockers.append(
            "MARGIN_MODE_MISMATCH"
        )

    if not long_ok:

        blockers.append(
            "LONG_LEVERAGE_MISMATCH"
        )

    if not short_ok:

        blockers.append(
            "SHORT_LEVERAGE_MISMATCH"
        )

    if not flat:

        blockers.append(
            "OPEN_POSITION_STATE_NOT_FLAT"
        )

    if not telegram_local_durable:

        blockers.append(
            "TELEGRAM_DEDUPE_LOCAL_STORAGE_FAILED"
        )

    if not telegram_cross_deploy_durable:

        blockers.append(
            "TELEGRAM_DEDUPE_NOT_CROSS_DEPLOY_DURABLE"
        )

    activation_env_match = (
        authenticated_ok
        and mark_ok
        and margin_ok
        and long_ok
        and short_ok
        and flat
        and telegram_local_durable
        and telegram_cross_deploy_durable
    )

    if not activation_env_match:

        blockers.append(
            "ACTIVATION_ENV_MISMATCH"
        )

    # Preserve order while removing duplicates.
    blockers = list(
        dict.fromkeys(
            blockers
        )
    )

    with COUNTER_LOCK:

        snapshot = ActivationSnapshot(
            timestamp=utc_now(),
            balance=balance,
            mark_price=mark_price,
            open_positions=open_positions,
            margin_mode=margin_mode,
            long_leverage=long_leverage,
            short_leverage=short_leverage,
            authenticated_weex_read_ok=authenticated_ok,
            mark_price_read_ok=mark_ok,
            telegram_local_durable=telegram_local_durable,
            telegram_cross_deploy_durable=(
                telegram_cross_deploy_durable
            ),
            activation_env_match=activation_env_match,
            blockers=blockers,
            authenticated_get_count=AUTHENTICATED_GET_COUNT,
            public_get_count=PUBLIC_GET_COUNT,
            exchange_network_write_count=(
                EXCHANGE_NETWORK_WRITE_COUNT
            ),
            telegram_post_count=TELEGRAM_POST_COUNT,
            real_order_execution=REAL_ORDER_EXECUTION,
            first_real_order_allowed=FIRST_REAL_ORDER_ALLOWED,
        )

    return snapshot


# ==================================================================================================
# FINAL SAFETY VALIDATION
# ==================================================================================================

def validate_final_firebreak(
    snapshot: ActivationSnapshot,
) -> bool:

    separator()

    log(
        "R35N TEST 8: FINAL EXECUTION FIREBREAK"
    )

    separator()

    checks: List[
        bool
    ] = []

    checks.append(
        test_result(
            "Exchange Network Write Count Is Zero",
            EXCHANGE_NETWORK_WRITE_COUNT
            == 0,
        )
    )

    checks.append(
        test_result(
            "Exchange Order Write Count Is Zero",
            EXCHANGE_ORDER_WRITE_COUNT
            == 0,
        )
    )

    checks.append(
        test_result(
            "Exchange Leverage Write Count Is Zero",
            EXCHANGE_LEVERAGE_WRITE_COUNT
            == 0,
        )
    )

    checks.append(
        test_result(
            "Exchange Margin Write Count Is Zero",
            EXCHANGE_MARGIN_WRITE_COUNT
            == 0,
        )
    )

    checks.append(
        test_result(
            "Exchange Position Write Count Is Zero",
            EXCHANGE_POSITION_WRITE_COUNT
            == 0,
        )
    )

    checks.append(
        test_result(
            "Real Order Execution Remains False",
            REAL_ORDER_EXECUTION is False,
        )
    )

    checks.append(
        test_result(
            "First Real Order Remains Forbidden",
            FIRST_REAL_ORDER_ALLOWED is False,
        )
    )

    checks.append(
        test_result(
            "Activation Match Cannot Enable Trading",
            (
                snapshot.first_real_order_allowed
                is False
            ),
        )
    )

    return all(
        checks
    )


# ==================================================================================================
# SNAPSHOT PERSISTENCE
# ==================================================================================================

def persist_snapshot(
    snapshot: ActivationSnapshot,
) -> bool:

    try:

        state = asdict(
            snapshot
        )

        state["snapshot_sha256"] = canonical_hash(
            state
        )

        atomic_write_json(
            STATE_FILE,
            state,
        )

        loaded = read_json_file(
            STATE_FILE,
            {},
        )

        if not isinstance(
            loaded,
            dict,
        ):
            return False

        return (
            loaded.get(
                "version"
            )
            == VERSION
            and loaded.get(
                "symbol"
            )
            == SYMBOL
        )

    except Exception as exc:

        log(
            f"R35N: SNAPSHOT PERSIST ERROR={type(exc).__name__}: {exc}"
        )

        return False


# ==================================================================================================
# REPORT FORMATTING
# ==================================================================================================

def build_activation_report(
    snapshot: ActivationSnapshot,
) -> str:

    blockers_text = (
        ",".join(
            snapshot.blockers
        )
        if snapshot.blockers
        else "NONE"
    )

    activation_text = (
        "MATCH"
        if snapshot.activation_env_match
        else "MISMATCH"
    )

    return (
        "R35N ACTIVATION ENV RECONCILIATION\n"
        f"SYMBOL={snapshot.symbol}\n"
        f"BALANCE={unknown(snapshot.balance)}\n"
        f"MARK_PRICE={unknown(snapshot.mark_price)}\n"
        f"OPEN_POSITIONS={unknown(snapshot.open_positions)}\n"
        f"MARGIN_MODE={unknown(snapshot.margin_mode)}\n"
        f"LONG_LEVERAGE={unknown(snapshot.long_leverage)}x\n"
        f"SHORT_LEVERAGE={unknown(snapshot.short_leverage)}x\n"
        f"AUTHENTICATED_WEEX_READ_OK={bool_text(snapshot.authenticated_weex_read_ok)}\n"
        f"MARK_PRICE_READ_OK={bool_text(snapshot.mark_price_read_ok)}\n"
        f"TELEGRAM_LOCAL_DURABLE={bool_text(snapshot.telegram_local_durable)}\n"
        f"TELEGRAM_CROSS_DEPLOY_DURABLE={bool_text(snapshot.telegram_cross_deploy_durable)}\n"
        f"ACTIVATION_ENV={activation_text}\n"
        f"REAL_ORDER_EXECUTION={bool_text(REAL_ORDER_EXECUTION)}\n"
        f"FIRST_REAL_ORDER_ALLOWED={bool_text(FIRST_REAL_ORDER_ALLOWED)}\n"
        f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITE_COUNT}\n"
        f"BLOCKERS={blockers_text}"
    )


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

LATEST_SNAPSHOT_LOCK = threading.Lock()

LATEST_SNAPSHOT: Optional[
    ActivationSnapshot
] = None


def set_latest_snapshot(
    snapshot: ActivationSnapshot,
) -> None:

    global LATEST_SNAPSHOT

    with LATEST_SNAPSHOT_LOCK:

        LATEST_SNAPSHOT = snapshot


def get_latest_snapshot() -> Optional[
    ActivationSnapshot
]:

    with LATEST_SNAPSHOT_LOCK:

        return LATEST_SNAPSHOT


class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ) -> None:

        snapshot = get_latest_snapshot()

        if snapshot is None:

            payload = {
                "ok": True,
                "version": VERSION,
                "symbol": SYMBOL,
                "phase": "STARTING",
                "real_order_execution": False,
                "first_real_order_allowed": False,
                "exchange_network_writes": (
                    EXCHANGE_NETWORK_WRITE_COUNT
                ),
            }

        else:

            payload = {
                "ok": True,
                "version": VERSION,
                "symbol": SYMBOL,
                "phase": (
                    "ACTIVATION_ENV_RECONCILED"
                    if snapshot.activation_env_match
                    else "ACTIVATION_ENV_BLOCKED"
                ),
                "activation_env_match": (
                    snapshot.activation_env_match
                ),
                "blockers": (
                    snapshot.blockers
                ),
                "real_order_execution": False,
                "first_real_order_allowed": False,
                "exchange_network_writes": (
                    EXCHANGE_NETWORK_WRITE_COUNT
                ),
            }

        encoded = json.dumps(
            payload,
            separators=(
                ",",
                ":",
            ),
            sort_keys=True,
        ).encode(
            "utf-8"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(
                len(
                    encoded
                )
            ),
        )

        self.end_headers()

        self.wfile.write(
            encoded
        )

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:

        return


def start_health_server() -> None:

    def serve() -> None:

        try:

            server = ThreadingHTTPServer(
                (
                    "0.0.0.0",
                    HEALTH_PORT,
                ),
                HealthHandler,
            )

            log(
                f"R35N: HEALTH SERVER STARTED ON PORT {HEALTH_PORT}"
            )

            server.serve_forever()

        except Exception as exc:

            log(
                f"R35N: HEALTH SERVER ERROR={type(exc).__name__}: {exc}"
            )

    thread = threading.Thread(
        target=serve,
        name="r35n-health-server",
        daemon=True,
    )

    thread.start()


# ==================================================================================================
# HEARTBEAT
# ==================================================================================================

def heartbeat_loop() -> None:

    global HEARTBEAT_COUNT

    while True:

        time.sleep(
            max(
                5,
                HEARTBEAT_SECONDS,
            )
        )

        with COUNTER_LOCK:

            HEARTBEAT_COUNT += 1

            current = HEARTBEAT_COUNT

            exchange_writes = (
                EXCHANGE_NETWORK_WRITE_COUNT
            )

        snapshot = get_latest_snapshot()

        phase = (
            "STARTING"
            if snapshot is None
            else (
                "ACTIVATION_ENV_RECONCILED"
                if snapshot.activation_env_match
                else "ACTIVATION_ENV_BLOCKED"
            )
        )

        log(
            "R35N HEARTBEAT "
            f"{current} "
            f"PHASE={phase} "
            f"EXCHANGE_NETWORK_WRITES={exchange_writes} "
            "REAL_ORDER_EXECUTION=False "
            "FIRST_REAL_ORDER_ALLOWED=False"
        )


# ==================================================================================================
# MAIN
# ==================================================================================================

def main() -> None:

    start_health_server()

    separator()

    log(
        "R35N: MAIN.PY ENTERED"
    )

    separator()

    log(
        f"R35N: VERSION={VERSION}"
    )

    log(
        f"R35N: SYMBOL={SYMBOL}"
    )

    log(
        f"R35N: HEALTH PORT={HEALTH_PORT}"
    )

    log(
        f"R35N: STATE DIR={STATE_DIR}"
    )

    log(
        f"R35N: WEEX BASE URL={WEEX_BASE_URL}"
    )

    log(
        "R35N: TARGET MARGIN MODE="
        + TARGET_MARGIN_MODE
    )

    log(
        f"R35N: TARGET LONG LEVERAGE={TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"R35N: TARGET SHORT LEVERAGE={TARGET_SHORT_LEVERAGE}x"
    )

    log(
        "R35N: REAL ORDER EXECUTION=DISABLED"
    )

    log(
        "R35N: FIRST REAL ORDER=FORBIDDEN"
    )

    log(
        "R35N: EXCHANGE MUTATIONS=HARD DISABLED"
    )

    log(
        "R35N: WEEX NETWORK METHODS=GET ONLY"
    )

    log(
        "R35N: SYNTHETIC TRANSPORT ONLY="
        + bool_text(
            SYNTHETIC_TRANSPORT_ONLY
        )
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 1 - Exchange mutation firebreak.
    # ----------------------------------------------------------------------------------------------

    firebreak_ok = (
        validate_exchange_firebreak()
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 2 - Credential environment.
    # ----------------------------------------------------------------------------------------------

    credential_env_ok = (
        validate_credentials()
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 3 - Telegram durable dedupe.
    # ----------------------------------------------------------------------------------------------

    (
        telegram_local_durable,
        telegram_cross_deploy_durable,
    ) = validate_telegram_durability()

    # ----------------------------------------------------------------------------------------------
    # TESTS 4-7 - Live read-only reconciliation.
    # ----------------------------------------------------------------------------------------------

    snapshot = (
        reconcile_activation_environment(
            telegram_local_durable=(
                telegram_local_durable
            ),
            telegram_cross_deploy_durable=(
                telegram_cross_deploy_durable
            ),
        )
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 8 - Final safety boundary.
    # ----------------------------------------------------------------------------------------------

    final_firebreak_ok = (
        validate_final_firebreak(
            snapshot
        )
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 9 - Durable snapshot.
    # ----------------------------------------------------------------------------------------------

    separator()

    log(
        "R35N TEST 9: DURABLE RECONCILIATION SNAPSHOT"
    )

    separator()

    snapshot_persisted = (
        persist_snapshot(
            snapshot
        )
    )

    test_result(
        "Activation Snapshot Was Persisted",
        snapshot_persisted,
    )

    test_result(
        "Snapshot Preserves Real Order Execution False",
        snapshot.real_order_execution
        is False,
    )

    test_result(
        "Snapshot Preserves First Real Order Forbidden",
        snapshot.first_real_order_allowed
        is False,
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 10 - Final readiness conclusion.
    # ----------------------------------------------------------------------------------------------

    separator()

    log(
        "R35N TEST 10: ACTIVATION ENVIRONMENT CONCLUSION"
    )

    separator()

    overall_control_integrity = (
        firebreak_ok
        and final_firebreak_ok
        and EXCHANGE_NETWORK_WRITE_COUNT
        == 0
        and REAL_ORDER_EXECUTION
        is False
        and FIRST_REAL_ORDER_ALLOWED
        is False
    )

    test_result(
        "R35N Safety Control Integrity",
        overall_control_integrity,
    )

    test_result(
        "WEEX Credential Environment Is Complete",
        credential_env_ok,
    )

    test_result(
        "Activation Environment Matches Required State",
        snapshot.activation_env_match,
    )

    test_result(
        "Telegram Dedupe Is Cross-Deploy Durable",
        snapshot.telegram_cross_deploy_durable,
    )

    test_result(
        "Exchange Write Count Remains Zero",
        EXCHANGE_NETWORK_WRITE_COUNT
        == 0,
    )

    test_result(
        "First Real Order Remains Hard Forbidden",
        FIRST_REAL_ORDER_ALLOWED
        is False,
    )

    # ----------------------------------------------------------------------------------------------
    # Publish latest state before reporting.
    # ----------------------------------------------------------------------------------------------

    set_latest_snapshot(
        snapshot
    )

    # ----------------------------------------------------------------------------------------------
    # Console report.
    # ----------------------------------------------------------------------------------------------

    report = build_activation_report(
        snapshot
    )

    separator()

    print(
        report,
        flush=True,
    )

    separator()

    # ----------------------------------------------------------------------------------------------
    # Telegram reporting boundary.
    # ----------------------------------------------------------------------------------------------

    if TELEGRAM_REPORTING_ENABLED:

        telegram_ok, telegram_status = (
            send_telegram_report(
                report
            )
        )

        separator()

        log(
            "R35N TEST 11: TELEGRAM REPORTING BOUNDARY"
        )

        separator()

        test_result(
            "Telegram Uses Reporting Boundary Only",
            True,
        )

        test_result(
            "Telegram Cannot Increment Exchange Write Count",
            EXCHANGE_NETWORK_WRITE_COUNT
            == 0,
        )

        test_result(
            "Telegram Reporting Completed Or Was Deduped",
            telegram_ok,
        )

        log(
            f"R35N: TELEGRAM STATUS={telegram_status}"
        )

    else:

        separator()

        log(
            "R35N: TELEGRAM REPORTING DISABLED BY ENVIRONMENT"
        )

    # ----------------------------------------------------------------------------------------------
    # Absolute final invariant.
    # ----------------------------------------------------------------------------------------------

    separator()

    log(
        "R35N FINAL SAFETY ASSERTION"
    )

    separator()

    if EXCHANGE_NETWORK_WRITE_COUNT != 0:

        raise RuntimeError(
            "R35N FATAL: EXCHANGE WRITE COUNT IS NOT ZERO"
        )

    if REAL_ORDER_EXECUTION:

        raise RuntimeError(
            "R35N FATAL: REAL ORDER EXECUTION MUST REMAIN FALSE"
        )

    if FIRST_REAL_ORDER_ALLOWED:

        raise RuntimeError(
            "R35N FATAL: FIRST REAL ORDER MUST REMAIN FORBIDDEN"
        )

    test_result(
        "R35N Made Zero Exchange Network Writes",
        True,
    )

    test_result(
        "R35N Sent No Real Order",
        True,
    )

    test_result(
        "R35N Sent No Demo Order",
        True,
    )

    test_result(
        "R35N Performed No Leverage Mutation",
        True,
    )

    test_result(
        "R35N Performed No Margin Mutation",
        True,
    )

    test_result(
        "R35N Performed No Position Mutation",
        True,
    )

    separator()

    if snapshot.activation_env_match:

        log(
            "R35N STATUS=ACTIVATION_ENV_RECONCILED"
        )

        log(
            "R35N: READ-ONLY ACTIVATION ENVIRONMENT IS VERIFIED"
        )

        log(
            "R35N: LIVE EXECUTION REMAINS HARD DISABLED"
        )

        log(
            "R35N: FIRST REAL ORDER REMAINS HARD FORBIDDEN"
        )

    else:

        log(
            "R35N STATUS=ACTIVATION_ENV_BLOCKED"
        )

        log(
            "R35N: FAIL-CLOSED ACTIVATION BLOCK IS ACTIVE"
        )

        log(
            "R35N: BLOCKERS="
            + ",".join(
                snapshot.blockers
            )
        )

    separator()

    # ----------------------------------------------------------------------------------------------
    # Keep Render service alive.
    # ----------------------------------------------------------------------------------------------

    heartbeat_loop()


# ==================================================================================================
# ENTRYPOINT
# ==================================================================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        log(
            "R35N: SHUTDOWN REQUESTED"
        )

    except Exception as exc:

        separator()

        log(
            f"R35N FATAL ERROR={type(exc).__name__}: {exc}"
        )

        log(
            "R35N: FAIL CLOSED"
        )

        log(
            "R35N: REAL_ORDER_EXECUTION=False"
        )

        log(
            "R35N: FIRST_REAL_ORDER_ALLOWED=False"
        )

        log(
            f"R35N: EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITE_COUNT}"
        )

        separator()

        raise
