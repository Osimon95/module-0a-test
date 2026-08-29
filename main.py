

from __future__ import annotations

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
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ==================================================================================================
# R35O - DURABLE TELEGRAM DEDUPE + ACTIVATION ENVIRONMENT RECONCILIATION
# ==================================================================================================
#
# PURPOSE
#   R35O fixes the remaining R35N blocker: Telegram report deduplication must be durable across
#   process restarts and Render deploy replacements before any future real-order activation can be
#   considered.
#
# SAFETY MODEL
#   - REAL ORDER EXECUTION HARD DISABLED
#   - DEMO ORDER EXECUTION HARD DISABLED
#   - EXCHANGE NETWORK WRITES HARD DISABLED
#   - LEVERAGE / MARGIN / POSITION / ORDER MUTATIONS HARD DISABLED
#   - ONLY PUBLIC GET + AUTHENTICATED GET ARE PERMITTED AGAINST WEEX
#   - TELEGRAM POST IS REPORTING ONLY; IT IS NOT AN EXCHANGE MUTATION
#   - FIRST REAL ORDER HARD FORBIDDEN IN R35O
#   - FAIL CLOSED IF DURABLE STORAGE CANNOT BE PROVED
#
# IMPORTANT RENDER CONFIGURATION
#   Mount a Render Persistent Disk and point R35O_DURABLE_DIR at the mount path.
#   Recommended mount path: /var/data
#   Recommended env:        R35O_DURABLE_DIR=/var/data/r35o_state
#
#   R35O deliberately refuses to label /tmp as cross-deploy durable.
# ==================================================================================================

VERSION = "R35O"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper() or "BTCUSDT"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

HEALTH_PORT = int(os.getenv("PORT", "10000"))

WEEX_BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

WEEX_PUBLIC_BASE_URL = os.getenv(
    "WEEX_PUBLIC_BASE_URL",
    WEEX_BASE_URL,
).rstrip("/")

HTTP_TIMEOUT_SECONDS = float(
    os.getenv(
        "HTTP_TIMEOUT_SECONDS",
        "12",
    )
)

# --------------------------------------------------------------------------------------------------
# CREDENTIALS
# --------------------------------------------------------------------------------------------------

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
).strip()

WEEX_API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    "",
).strip()

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

TELEGRAM_REPORTING_ENABLED = (
    os.getenv(
        "TELEGRAM_REPORTING_ENABLED",
        "true",
    )
    .strip()
    .lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)

# --------------------------------------------------------------------------------------------------
# DURABLE STATE
# --------------------------------------------------------------------------------------------------

DURABLE_DIR = Path(
    os.getenv(
        "R35O_DURABLE_DIR",
        "/var/data/r35o_state",
    )
).expanduser()

DEDUPE_FILE = (
    DURABLE_DIR
    / "telegram_dedupe.json"
)

PROBE_FILE = (
    DURABLE_DIR
    / "r35o_durability_probe.json"
)

# --------------------------------------------------------------------------------------------------
# HARD SAFETY FIREBREAKS
# --------------------------------------------------------------------------------------------------
#
# These are constants.
#
# They CANNOT be enabled through an environment variable.
# --------------------------------------------------------------------------------------------------

REAL_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

EXCHANGE_NETWORK_WRITES = False

EXCHANGE_MUTATION_TRANSPORT = False

LEVERAGE_MUTATION = False

MARGIN_MUTATION = False

POSITION_MUTATION = False

FIRST_REAL_ORDER_ALLOWED = False

# --------------------------------------------------------------------------------------------------
# COUNTERS
# --------------------------------------------------------------------------------------------------

AUTHENTICATED_GET_COUNT = 0

PUBLIC_GET_COUNT = 0

EXCHANGE_NETWORK_WRITE_COUNT = 0

TELEGRAM_POST_COUNT = 0

_PRINT_LOCK = threading.Lock()

_STATE_LOCK = threading.Lock()


# ==================================================================================================
# BASIC HELPERS
# ==================================================================================================

def utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


# --------------------------------------------------------------------------------------------------

def log(
    message: str,
) -> None:

    with _PRINT_LOCK:

        print(
            f"{utc_now()} {message}",
            flush=True,
        )


# --------------------------------------------------------------------------------------------------

def divider() -> None:

    log(
        "-" * 100
    )


# --------------------------------------------------------------------------------------------------

def check(
    name: str,
    condition: bool,
) -> bool:

    status = (
        "✅ PASS"
        if condition
        else "❌ FAIL"
    )

    print(
        f"{name:<86} {status}",
        flush=True,
    )

    return condition


# --------------------------------------------------------------------------------------------------

def canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


# --------------------------------------------------------------------------------------------------

def sha256_text(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


# ==================================================================================================
# ATOMIC DURABLE FILE WRITE
# ==================================================================================================

def atomic_write_json(
    path: Path,
    data: Dict[str, Any],
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = json.dumps(
        data,
        sort_keys=True,
        indent=2,
    ).encode(
        "utf-8"
    )

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(
            path.parent
        ),
    )

    temp_path = Path(
        temp_name
    )

    try:

        with os.fdopen(
            fd,
            "wb",
            closefd=True,
        ) as fh:

            fh.write(
                payload
            )

            fh.flush()

            os.fsync(
                fh.fileno()
            )

        os.replace(
            temp_path,
            path,
        )

        try:

            dir_fd = os.open(
                str(
                    path.parent
                ),
                os.O_RDONLY,
            )

            try:

                os.fsync(
                    dir_fd
                )

            finally:

                os.close(
                    dir_fd
                )

        except OSError:

            pass

    finally:

        if temp_path.exists():

            try:

                temp_path.unlink()

            except OSError:

                pass


# --------------------------------------------------------------------------------------------------

def read_json(
    path: Path,
) -> Dict[str, Any]:

    with path.open(
        "r",
        encoding="utf-8",
    ) as fh:

        value = json.load(
            fh
        )

    if not isinstance(
        value,
        dict,
    ):

        raise ValueError(
            f"Expected JSON object at {path}"
        )

    return value


# ==================================================================================================
# PERSISTENT DISK VERIFICATION
# ==================================================================================================

def path_is_obviously_ephemeral(
    path: Path,
) -> bool:

    resolved = str(
        path.resolve(
            strict=False
        )
    )

    ephemeral_prefixes = (
        "/tmp",
        "/var/tmp",
        "/dev/shm",
    )

    return any(
        resolved == prefix
        or resolved.startswith(
            prefix + "/"
        )
        for prefix
        in ephemeral_prefixes
    )


# --------------------------------------------------------------------------------------------------

def persistent_mount_evidence(
    path: Path,
) -> Tuple[
    bool,
    str,
]:

    resolved = str(
        path.resolve(
            strict=False
        )
    )

    configured_mount = (
        os.getenv(
            "R35O_PERSISTENT_DISK_MOUNT_PATH",
            "/var/data",
        ).strip()
        or "/var/data"
    )

    mount_resolved = str(
        Path(
            configured_mount
        )
        .expanduser()
        .resolve(
            strict=False
        )
    )

    if path_is_obviously_ephemeral(
        path
    ):

        return (
            False,
            "EPHEMERAL_PATH",
        )

    underneath_configured_mount = (
        resolved
        == mount_resolved
        or resolved.startswith(
            mount_resolved
            + "/"
        )
    )

    if not underneath_configured_mount:

        return (
            False,
            "OUTSIDE_CONFIGURED_PERSISTENT_MOUNT",
        )

    return (
        True,
        (
            "CONFIGURED_PERSISTENT_MOUNT="
            f"{mount_resolved}"
        ),
    )


# ==================================================================================================
# DURABILITY RESULT
# ==================================================================================================

@dataclass
class DurabilityResult:

    local_durable: bool = False

    cross_deploy_durable: bool = False

    write_ok: bool = False

    reopen_ok: bool = False

    duplicate_rejected: bool = False

    mount_evidence: str = "UNKNOWN"

    error: str = ""


# ==================================================================================================
# TELEGRAM DEDUPE STORE
# ==================================================================================================

class TelegramDedupeStore:

    def __init__(
        self,
        path: Path,
    ):

        self.path = path


    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def _blank() -> Dict[
        str,
        Any,
    ]:

        return {

            "schema":
                "r35o.telegram.dedupe.v1",

            "version":
                VERSION,

            "keys":
                {},

            "updated_at":
                None,
        }


    # ----------------------------------------------------------------------------------------------

    def load(
        self,
    ) -> Dict[
        str,
        Any,
    ]:

        if not self.path.exists():

            return self._blank()

        data = read_json(
            self.path
        )

        if (
            data.get(
                "schema"
            )
            !=
            "r35o.telegram.dedupe.v1"
        ):

            raise ValueError(
                "Unexpected Telegram dedupe schema"
            )

        keys = data.get(
            "keys"
        )

        if not isinstance(
            keys,
            dict,
        ):

            raise ValueError(
                "Telegram dedupe keys must be an object"
            )

        return data


    # ----------------------------------------------------------------------------------------------

    def contains(
        self,
        key: str,
    ) -> bool:

        with _STATE_LOCK:

            return (
                key
                in
                self.load()[
                    "keys"
                ]
            )


    # ----------------------------------------------------------------------------------------------

    def record_once(
        self,
        key: str,
        metadata: Dict[
            str,
            Any,
        ],
    ) -> bool:

        with _STATE_LOCK:

            state = self.load()

            if (
                key
                in
                state["keys"]
            ):

                return False

            state[
                "keys"
            ][
                key
            ] = {

                "recorded_at":
                    utc_now(),

                "metadata":
                    metadata,
            }

            state[
                "updated_at"
            ] = utc_now()

            atomic_write_json(
                self.path,
                state,
            )

            return True


# ==================================================================================================
# DURABILITY PROOF
# ==================================================================================================

def prove_telegram_dedupe_durability(
) -> DurabilityResult:

    result = DurabilityResult()

    try:

        mount_ok, mount_evidence = (
            persistent_mount_evidence(
                DURABLE_DIR
            )
        )

        result.mount_evidence = (
            mount_evidence
        )

        DURABLE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        probe = {

            "schema":
                "r35o.durability.probe.v1",

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "nonce":
                sha256_text(
                    (
                        f"{VERSION}|"
                        f"{SYMBOL}|"
                        f"{time.time_ns()}"
                    )
                )[
                    :24
                ],

            "written_at":
                utc_now(),
        }

        probe[
            "sha256"
        ] = sha256_text(

            canonical_json(

                {
                    key: value

                    for key, value
                    in probe.items()

                    if key
                    != "sha256"
                }

            )

        )

        atomic_write_json(
            PROBE_FILE,
            probe,
        )

        result.write_ok = (
            PROBE_FILE.exists()
        )

        reopened_probe = read_json(
            PROBE_FILE
        )

        expected_hash = sha256_text(

            canonical_json(

                {
                    key: value

                    for key, value
                    in reopened_probe.items()

                    if key
                    != "sha256"
                }

            )

        )

        result.reopen_ok = (

            reopened_probe.get(
                "sha256"
            )
            ==
            expected_hash
            ==
            probe[
                "sha256"
            ]

        )

        test_key = (

            "R35O_DURABILITY_PROBE:"
            f"{probe['nonce']}"

        )

        store_a = TelegramDedupeStore(
            DEDUPE_FILE
        )

        inserted = store_a.record_once(

            test_key,

            {

                "purpose":
                    "durability_probe",

                "symbol":
                    SYMBOL,

            },

        )

        # Fresh object simulates a process-level reopen.

        store_b = TelegramDedupeStore(
            DEDUPE_FILE
        )

        survived_reopen = (
            store_b.contains(
                test_key
            )
        )

        duplicate_inserted = (
            store_b.record_once(

                test_key,

                {

                    "purpose":
                        "duplicate_probe",

                },

            )
        )

        result.duplicate_rejected = (

            inserted
            and
            survived_reopen
            and
            not duplicate_inserted

        )

        result.local_durable = (

            result.write_ok
            and
            result.reopen_ok
            and
            result.duplicate_rejected

        )

        result.cross_deploy_durable = (

            result.local_durable
            and
            mount_ok

        )

    except Exception as exc:

        result.error = (
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        result.local_durable = False

        result.cross_deploy_durable = False

    return result


# ==================================================================================================
# WEEX V3 SIGNATURE
# ==================================================================================================

def build_signature(
    timestamp_ms: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    suffix = (
        request_path
    )

    if query_string:

        suffix += (
            "?"
            + query_string
        )

    prehash = (

        f"{timestamp_ms}"
        f"{method.upper()}"
        f"{suffix}"
        f"{body}"

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
# AUTHENTICATED WEEX GET ONLY
# ==================================================================================================

def authenticated_get(
    path: str,
    query: Optional[
        Dict[
            str,
            str,
        ]
    ] = None,
) -> Any:

    global AUTHENTICATED_GET_COUNT

    if not (

        WEEX_API_KEY
        and
        WEEX_API_SECRET
        and
        WEEX_API_PASSPHRASE

    ):

        raise RuntimeError(

            "Missing WEEX_API_KEY / "
            "WEEX_API_SECRET / "
            "WEEX_API_PASSPHRASE"

        )

    query = (
        query
        or {}
    )

    query_string = (
        urllib.parse.urlencode(
            query
        )
    )

    url = (

        WEEX_BASE_URL
        + path

        + (
            "?"
            + query_string

            if query_string

            else ""
        )

    )

    timestamp_ms = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = build_signature(

        timestamp_ms,

        "GET",

        path,

        query_string,

        "",

    )

    request = urllib.request.Request(

        url,

        method="GET",

        headers={

            "ACCESS-KEY":
                WEEX_API_KEY,

            "ACCESS-SIGN":
                signature,

            "ACCESS-PASSPHRASE":
                WEEX_API_PASSPHRASE,

            "ACCESS-TIMESTAMP":
                timestamp_ms,

            "Content-Type":
                "application/json",

            "Accept":
                "application/json",

            "User-Agent":
                f"{VERSION}/read-only",
        },

    )

    with urllib.request.urlopen(

        request,

        timeout=HTTP_TIMEOUT_SECONDS,

    ) as response:

        payload = (
            response
            .read()
            .decode(
                "utf-8"
            )
        )

    AUTHENTICATED_GET_COUNT += 1

    return json.loads(
        payload
    )


# ==================================================================================================
# PUBLIC WEEX GET ONLY
# ==================================================================================================

def public_get_json(
    path: str,
    query: Optional[
        Dict[
            str,
            str,
        ]
    ] = None,
) -> Any:

    global PUBLIC_GET_COUNT

    query = (
        query
        or {}
    )

    query_string = (
        urllib.parse.urlencode(
            query
        )
    )

    url = (

        WEEX_PUBLIC_BASE_URL
        + path

        + (
            "?"
            + query_string

            if query_string

            else ""
        )

    )

    request = urllib.request.Request(

        url,

        method="GET",

        headers={

            "Accept":
                "application/json",

            "User-Agent":
                f"{VERSION}/public-read-only",

        },

    )

    with urllib.request.urlopen(

        request,

        timeout=HTTP_TIMEOUT_SECONDS,

    ) as response:

        payload = (
            response
            .read()
            .decode(
                "utf-8"
            )
        )

    PUBLIC_GET_COUNT += 1

    return json.loads(
        payload
    )


# ==================================================================================================
# RESPONSE HELPERS
# ==================================================================================================

def unwrap_data(
    payload: Any,
) -> Any:

    if isinstance(
        payload,
        dict,
    ):

        for key in (
            "data",
            "result",
        ):

            if key in payload:

                return payload[
                    key
                ]

    return payload


# --------------------------------------------------------------------------------------------------

def find_usdt_balance(
    payload: Any,
) -> Optional[
    float
]:

    data = unwrap_data(
        payload
    )

    rows: List[
        Any
    ]

    if isinstance(
        data,
        list,
    ):

        rows = data

    elif isinstance(
        data,
        dict,
    ):

        rows = [
            data
        ]

    else:

        return None

    for row in rows:

        if not isinstance(
            row,
            dict,
        ):

            continue

        asset = str(

            row.get(

                "asset",

                row.get(
                    "coin",
                    "",
                ),

            )

        ).upper()

        if asset != "USDT":

            continue

        raw = row.get(

            "availableBalance",

            row.get(

                "available",

                row.get(
                    "balance"
                ),

            ),

        )

        try:

            return float(
                raw
            )

        except (
            TypeError,
            ValueError,
        ):

            return None

    return None


# --------------------------------------------------------------------------------------------------

def parse_positions(
    payload: Any,
) -> Tuple[
    int,
    List[
        Dict[
            str,
            Any,
        ]
    ],
]:

    data = unwrap_data(
        payload
    )

    if isinstance(
        data,
        dict,
    ):

        candidates = (

            data.get(
                "positions"
            )

            or data.get(
                "list"
            )

            or data.get(
                "items"
            )

            or []

        )

    else:

        candidates = data

    if not isinstance(
        candidates,
        list,
    ):

        return (
            0,
            [],
        )

    active: List[
        Dict[
            str,
            Any,
        ]
    ] = []

    for row in candidates:

        if not isinstance(
            row,
            dict,
        ):

            continue

        if str(
            row.get(
                "symbol",
                "",
            )
        ).upper() != SYMBOL:

            continue

        raw_size = row.get(

            "size",

            row.get(

                "positionAmt",

                row.get(
                    "positionSize",
                    0,
                ),

            ),

        )

        try:

            size = abs(
                float(
                    raw_size
                    or 0
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            size = 0.0

        if size > 0:

            active.append(
                row
            )

    return (
        len(
            active
        ),
        active,
    )


# --------------------------------------------------------------------------------------------------

def parse_symbol_config(
    payload: Any,
) -> Tuple[
    Optional[
        str
    ],
    Optional[
        int
    ],
    Optional[
        int
    ],
]:

    data = unwrap_data(
        payload
    )

    rows: List[
        Any
    ]

    if isinstance(
        data,
        list,
    ):

        rows = data

    elif isinstance(
        data,
        dict,
    ):

        if isinstance(
            data.get(
                "list"
            ),
            list,
        ):

            rows = data[
                "list"
            ]

        else:

            rows = [
                data
            ]

    else:

        rows = []

    for row in rows:

        if not isinstance(
            row,
            dict,
        ):

            continue

        if str(
            row.get(
                "symbol",
                "",
            )
        ).upper() != SYMBOL:

            continue

        margin = str(

            row.get(

                "marginType",

                row.get(
                    "marginMode",
                    "",
                ),

            )

        ).upper() or None

        long_raw = row.get(

            "isolatedLongLeverage",

            row.get(
                "longLeverage"
            ),

        )

        short_raw = row.get(

            "isolatedShortLeverage",

            row.get(
                "shortLeverage"
            ),

        )

        try:

            long_lev = (

                int(
                    float(
                        long_raw
                    )
                )

                if long_raw
                is not None

                else None

            )

        except (
            TypeError,
            ValueError,
        ):

            long_lev = None

        try:

            short_lev = (

                int(
                    float(
                        short_raw
                    )
                )

                if short_raw
                is not None

                else None

            )

        except (
            TypeError,
            ValueError,
        ):

            short_lev = None

        return (

            margin,

            long_lev,

            short_lev,

        )

    return (
        None,
        None,
        None,
    )


# ==================================================================================================
# MARK PRICE
# ==================================================================================================

def extract_mark_price(
    payload: Any,
) -> Optional[
    float
]:

    data = unwrap_data(
        payload
    )

    def candidates_from(
        obj: Any,
    ) -> List[
        Any
    ]:

        if isinstance(
            obj,
            list,
        ):

            return obj

        if isinstance(
            obj,
            dict,
        ):

            for key in (
                "list",
                "items",
                "rows",
            ):

                if isinstance(
                    obj.get(
                        key
                    ),
                    list,
                ):

                    return obj[
                        key
                    ]

            return [
                obj
            ]

        return []

    for row in candidates_from(
        data
    ):

        if not isinstance(
            row,
            dict,
        ):

            continue

        symbol = str(

            row.get(
                "symbol",
                SYMBOL,
            )

        ).upper()

        if symbol != SYMBOL:

            continue

        for key in (

            "markPrice",
            "mark_price",
            "price",
            "lastPrice",
            "last",

        ):

            if key not in row:

                continue

            try:

                value = float(
                    row[
                        key
                    ]
                )

                if value > 0:

                    return value

            except (
                TypeError,
                ValueError,
            ):

                pass

    return None


# --------------------------------------------------------------------------------------------------

def read_mark_price(
) -> Tuple[
    Optional[
        float
    ],
    str,
]:

    candidates = [

        (
            "/capi/v3/market/ticker",
            {
                "symbol":
                    SYMBOL
            },
        ),

        (
            "/capi/v3/market/tickers",
            {
                "symbol":
                    SYMBOL
            },
        ),

        (
            "/capi/v3/market/markPrice",
            {
                "symbol":
                    SYMBOL
            },
        ),

    ]

    errors: List[
        str
    ] = []

    for path, query in candidates:

        try:

            payload = public_get_json(
                path,
                query,
            )

            price = extract_mark_price(
                payload
            )

            if price is not None:

                return (
                    price,
                    path,
                )

            errors.append(
                f"{path}:NO_PRICE"
            )

        except Exception as exc:

            errors.append(

                f"{path}:"
                f"{type(exc).__name__}"

            )

    return (
        None,
        ";".join(
            errors
        ),
    )


# ==================================================================================================
# TELEGRAM REPORTING
# ==================================================================================================

def telegram_send_report_once(
    event_key: str,
    text: str,
    store: TelegramDedupeStore,
) -> Tuple[
    bool,
    str,
]:

    global TELEGRAM_POST_COUNT

    if not TELEGRAM_REPORTING_ENABLED:

        return (
            False,
            "TELEGRAM_REPORTING_DISABLED",
        )

    if (
        not TELEGRAM_BOT_TOKEN
        or
        not TELEGRAM_CHAT_ID
    ):

        return (
            False,
            "TELEGRAM_CREDENTIALS_MISSING",
        )

    dedupe_key = sha256_text(

        f"{VERSION}|"
        f"{SYMBOL}|"
        f"{event_key}|"
        f"{text}"

    )

    inserted = store.record_once(

        dedupe_key,

        {

            "event_key":
                event_key,

            "symbol":
                SYMBOL,

            "text_sha256":
                sha256_text(
                    text
                ),

        },

    )

    if not inserted:

        return (
            False,
            "DUPLICATE_SUPPRESSED",
        )

    url = (

        "https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}"
        "/sendMessage"

    )

    body = urllib.parse.urlencode(

        {

            "chat_id":
                TELEGRAM_CHAT_ID,

            "text":
                text,

        }

    ).encode(
        "utf-8"
    )

    request = urllib.request.Request(

        url,

        data=body,

        method="POST",

        headers={

            "Content-Type":
                "application/x-www-form-urlencoded",

            "User-Agent":
                f"{VERSION}/report-only",

        },

    )

    try:

        with urllib.request.urlopen(

            request,

            timeout=HTTP_TIMEOUT_SECONDS,

        ) as response:

            response.read()

        TELEGRAM_POST_COUNT += 1

        return (
            True,
            "SENT",
        )

    except Exception as exc:

        return (

            False,

            (
                "SEND_FAILED_DEDUPE_RETAINED:"
                f"{type(exc).__name__}"
            ),

        )


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ) -> None:

        if self.path not in (

            "/",
            "/health",
            "/healthz",

        ):

            self.send_response(
                404
            )

            self.end_headers()

            return

        body = json.dumps(

            {

                "ok":
                    True,

                "version":
                    VERSION,

                "symbol":
                    SYMBOL,

                "real_order_execution":
                    REAL_ORDER_EXECUTION,

                "exchange_network_writes":
                    EXCHANGE_NETWORK_WRITE_COUNT,

            }

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
                    body
                )
            ),
        )

        self.end_headers()

        self.wfile.write(
            body
        )


    # ----------------------------------------------------------------------------------------------

    def log_message(
        self,
        fmt: str,
        *args: Any,
    ) -> None:

        return


# --------------------------------------------------------------------------------------------------

def start_health_server(
) -> None:

    def runner(
    ) -> None:

        server = HTTPServer(

            (
                "0.0.0.0",
                HEALTH_PORT,
            ),

            HealthHandler,

        )

        log(

            f"{VERSION}: "
            "HEALTH SERVER STARTED "
            f"ON PORT {HEALTH_PORT}"

        )

        server.serve_forever()

    thread = threading.Thread(

        target=runner,

        name="health-server",

        daemon=True,

    )

    thread.start()


# ==================================================================================================
# SAFE ERROR
# ==================================================================================================

def safe_error(
    exc: Exception,
) -> str:

    if isinstance(
        exc,
        urllib.error.HTTPError,
    ):

        try:

            body = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )[
                    :300
                ]
            )

        except Exception:

            body = ""

        return (

            f"HTTPError "
            f"{exc.code}: "
            f"{body}"

        )

    return (

        f"{type(exc).__name__}: "
        f"{exc}"

    )


# ==================================================================================================
# MAIN VALIDATION
# ==================================================================================================

def run(
) -> None:

    start_health_server()

    time.sleep(
        0.15
    )

    divider()

    log(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    divider()

    log(
        f"{VERSION}: SYMBOL={SYMBOL}"
    )

    log(
        f"{VERSION}: VERSION={VERSION}"
    )

    log(
        f"{VERSION}: DURABLE DIR={DURABLE_DIR}"
    )

    log(
        f"{VERSION}: DEDUPE FILE={DEDUPE_FILE}"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION={REAL_ORDER_EXECUTION}"
    )

    log(
        f"{VERSION}: DEMO ORDER EXECUTION={DEMO_ORDER_EXECUTION}"
    )

    log(
        f"{VERSION}: EXCHANGE NETWORK WRITES={EXCHANGE_NETWORK_WRITES}"
    )

    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    divider()

    log(
        f"{VERSION} TEST 1: HARD SAFETY FIREBREAK"
    )

    divider()

    safety_ok = all(

        [

            check(
                "Real Order Execution Is Hard Disabled",
                REAL_ORDER_EXECUTION is False,
            ),

            check(
                "Demo Order Execution Is Hard Disabled",
                DEMO_ORDER_EXECUTION is False,
            ),

            check(
                "Exchange Network Writes Are Hard Disabled",
                EXCHANGE_NETWORK_WRITES is False,
            ),

            check(
                "Exchange Mutation Transport Is Hard Disabled",
                EXCHANGE_MUTATION_TRANSPORT is False,
            ),

            check(
                "Leverage Mutation Is Hard Disabled",
                LEVERAGE_MUTATION is False,
            ),

            check(
                "Margin Mutation Is Hard Disabled",
                MARGIN_MUTATION is False,
            ),

            check(
                "Position Mutation Is Hard Disabled",
                POSITION_MUTATION is False,
            ),

            check(
                "First Real Order Is Hard Forbidden",
                FIRST_REAL_ORDER_ALLOWED is False,
            ),

        ]

    )

    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    divider()

    log(
        f"{VERSION} TEST 2: TELEGRAM DURABLE STORAGE PATH"
    )

    divider()

    durability = (
        prove_telegram_dedupe_durability()
    )

    check(
        "Durable Directory Is Not /tmp Or Another Explicit Ephemeral Path",
        not path_is_obviously_ephemeral(
            DURABLE_DIR
        ),
    )

    check(
        "Durability Probe Write Succeeded",
        durability.write_ok,
    )

    check(
        "Durability Probe Reopened With Matching Hash",
        durability.reopen_ok,
    )

    check(
        "Telegram Dedupe Rejects Duplicate After Fresh Store Reopen",
        durability.duplicate_rejected,
    )

    check(
        "Telegram Dedupe Is Locally Durable",
        durability.local_durable,
    )

    check(
        "Telegram Dedupe Is Cross-Deploy Durable By Configured Persistent Mount",
        durability.cross_deploy_durable,
    )

    log(

        f"{VERSION}: "
        "DURABILITY MOUNT EVIDENCE="
        f"{durability.mount_evidence}"

    )

    if durability.error:

        log(

            f"{VERSION}: "
            "DURABILITY ERROR="
            f"{durability.error}"

        )

    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    divider()

    log(
        f"{VERSION} TEST 3: WEEX CREDENTIAL PRESENCE"
    )

    divider()

    credentials_ok = all(

        [

            check(
                "WEEX_API_KEY Is Present",
                bool(
                    WEEX_API_KEY
                ),
            ),

            check(
                "WEEX_API_SECRET Is Present",
                bool(
                    WEEX_API_SECRET
                ),
            ),

            check(
                "WEEX_API_PASSPHRASE Is Present",
                bool(
                    WEEX_API_PASSPHRASE
                ),
            ),

        ]

    )

    balance: Optional[
        float
    ] = None

    open_positions: Optional[
        int
    ] = None

    margin_mode: Optional[
        str
    ] = None

    long_leverage: Optional[
        int
    ] = None

    short_leverage: Optional[
        int
    ] = None

    auth_read_ok = False

    auth_error = ""

    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    divider()

    log(
        f"{VERSION} TEST 4: AUTHENTICATED WEEX READ-ONLY RECONCILIATION"
    )

    divider()

    if credentials_ok:

        try:

            balance_payload = authenticated_get(
                "/capi/v3/account/balance"
            )

            positions_payload = authenticated_get(
                "/capi/v3/account/position/allPosition"
            )

            config_payload = authenticated_get(

                "/capi/v3/account/symbolConfig",

                {
                    "symbol":
                        SYMBOL
                },

            )

            balance = find_usdt_balance(
                balance_payload
            )

            open_positions, _ = parse_positions(
                positions_payload
            )

            (
                margin_mode,
                long_leverage,
                short_leverage,
            ) = parse_symbol_config(
                config_payload
            )

            auth_read_ok = all(

                [

                    balance
                    is not None,

                    open_positions
                    is not None,

                    margin_mode
                    is not None,

                    long_leverage
                    is not None,

                    short_leverage
                    is not None,

                ]

            )

        except Exception as exc:

            auth_error = safe_error(
                exc
            )

            auth_read_ok = False

    check(
        "Authenticated WEEX Read Completed",
        auth_read_ok,
    )

    check(
        "Available USDT Balance Was Read",
        balance is not None,
    )

    check(
        "BTCUSDT Open Position Count Was Read",
        open_positions is not None,
    )

    check(
        "BTCUSDT Margin Mode Was Read",
        margin_mode is not None,
    )

    check(
        "BTCUSDT Long Leverage Was Read",
        long_leverage is not None,
    )

    check(
        "BTCUSDT Short Leverage Was Read",
        short_leverage is not None,
    )

    if auth_error:

        log(

            f"{VERSION}: "
            "AUTH READ ERROR="
            f"{auth_error}"

        )

    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    divider()

    log(
        f"{VERSION} TEST 5: PUBLIC MARK PRICE READ"
    )

    divider()

    mark_price, mark_source = (
        read_mark_price()
    )

    mark_price_ok = (

        mark_price is not None
        and
        mark_price > 0

    )

    check(
        "BTCUSDT Mark Price Was Read",
        mark_price_ok,
    )

    log(

        f"{VERSION}: "
        "MARK PRICE SOURCE="
        f"{mark_source}"

    )

    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    divider()

    log(
        f"{VERSION} TEST 6: EXCHANGE CONFIGURATION MATCH"
    )

    divider()

    exchange_env_ok = all(

        [

            auth_read_ok,

            mark_price_ok,

            open_positions
            == 0,

            margin_mode
            == TARGET_MARGIN_MODE,

            long_leverage
            == TARGET_LONG_LEVERAGE,

            short_leverage
            == TARGET_SHORT_LEVERAGE,

        ]

    )

    check(
        "Open Positions Are Zero",
        open_positions == 0,
    )

    check(
        "Margin Mode Is ISOLATED",
        margin_mode == TARGET_MARGIN_MODE,
    )

    check(
        "Long Leverage Is 100x",
        long_leverage == TARGET_LONG_LEVERAGE,
    )

    check(
        "Short Leverage Is 100x",
        short_leverage == TARGET_SHORT_LEVERAGE,
    )

    check(
        "Exchange Activation Environment Matches Target",
        exchange_env_ok,
    )

    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    divider()

    log(
        f"{VERSION} TEST 7: TELEGRAM REPORTING BOUNDARY"
    )

    divider()

    telegram_store = (
        TelegramDedupeStore(
            DEDUPE_FILE
        )
    )

    telegram_boundary_ok = all(

        [

            check(
                "Telegram Reporting Uses A Separate Non-WEEX Host",
                True,
            ),

            check(
                "Telegram Reporting Cannot Enable Real Order Execution",
                REAL_ORDER_EXECUTION is False,
            ),

            check(
                "Telegram Reporting Cannot Increment Exchange Write Count",
                EXCHANGE_NETWORK_WRITE_COUNT == 0,
            ),

            check(
                "Telegram Dedupe Store Is Durable Before Reporting",
                durability.cross_deploy_durable,
            ),

        ]

    )

    # ==============================================================================================
    # BLOCKERS
    # ==============================================================================================

    blockers: List[
        str
    ] = []

    if not safety_ok:

        blockers.append(
            "SAFETY_FIREBREAK_FAILED"
        )

    if not auth_read_ok:

        blockers.append(
            "AUTHENTICATED_WEEX_READ_FAILED"
        )

    if not mark_price_ok:

        blockers.append(
            "MARK_PRICE_READ_FAILED"
        )

    if open_positions not in (
        0,
    ):

        blockers.append(
            "OPEN_POSITIONS_NOT_ZERO"
        )

    if (
        margin_mode
        != TARGET_MARGIN_MODE
    ):

        blockers.append(
            "MARGIN_MODE_MISMATCH"
        )

    if (
        long_leverage
        != TARGET_LONG_LEVERAGE
    ):

        blockers.append(
            "LONG_LEVERAGE_MISMATCH"
        )

    if (
        short_leverage
        != TARGET_SHORT_LEVERAGE
    ):

        blockers.append(
            "SHORT_LEVERAGE_MISMATCH"
        )

    if not durability.local_durable:

        blockers.append(
            "TELEGRAM_DEDUPE_LOCAL_STORAGE_FAILED"
        )

    if not durability.cross_deploy_durable:

        blockers.append(
            "TELEGRAM_DEDUPE_NOT_CROSS_DEPLOY_DURABLE"
        )

    if not telegram_boundary_ok:

        blockers.append(
            "TELEGRAM_REPORTING_BOUNDARY_FAILED"
        )

    activation_env_match = (
        len(
            blockers
        )
        == 0
    )

    if not activation_env_match:

        blockers.append(
            "ACTIVATION_ENV_MISMATCH"
        )

    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    divider()

    log(
        f"{VERSION} TEST 8: FINAL R35O ACTIVATION GATE"
    )

    divider()

    check(
        "Exchange Network Write Count Remains Zero",
        EXCHANGE_NETWORK_WRITE_COUNT == 0,
    )

    check(
        "Real Order Execution Remains Disabled",
        REAL_ORDER_EXECUTION is False,
    )

    check(
        "First Real Order Remains Forbidden In R35O",
        FIRST_REAL_ORDER_ALLOWED is False,
    )

    check(
        "Activation Environment Fully Reconciles",
        activation_env_match,
    )

    # ==============================================================================================
    # FINAL REPORT
    # ==============================================================================================

    report_lines = [

        f"{VERSION} ACTIVATION ENV RECONCILIATION",

        f"SYMBOL={SYMBOL}",

        (
            "BALANCE="
            f"{balance if balance is not None else 'UNKNOWN'}"
        ),

        (
            "MARK_PRICE="
            f"{mark_price if mark_price is not None else 'UNKNOWN'}"
        ),

        (
            "OPEN_POSITIONS="
            f"{open_positions if open_positions is not None else 'UNKNOWN'}"
        ),

        (
            "MARGIN_MODE="
            f"{margin_mode if margin_mode is not None else 'UNKNOWN'}"
        ),

        (
            "LONG_LEVERAGE="
            + (
                str(
                    long_leverage
                )
                + "x"

                if long_leverage
                is not None

                else "UNKNOWN"
            )
        ),

        (
            "SHORT_LEVERAGE="
            + (
                str(
                    short_leverage
                )
                + "x"

                if short_leverage
                is not None

                else "UNKNOWN"
            )
        ),

        (
            "AUTHENTICATED_WEEX_READ_OK="
            f"{auth_read_ok}"
        ),

        (
            "MARK_PRICE_READ_OK="
            f"{mark_price_ok}"
        ),

        (
            "TELEGRAM_LOCAL_DURABLE="
            f"{durability.local_durable}"
        ),

        (
            "TELEGRAM_CROSS_DEPLOY_DURABLE="
            f"{durability.cross_deploy_durable}"
        ),

        (
            "ACTIVATION_ENV="
            + (
                "MATCH"

                if activation_env_match

                else "MISMATCH"
            )
        ),

        (
            "REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        ),

        (
            "FIRST_REAL_ORDER_ALLOWED="
            f"{FIRST_REAL_ORDER_ALLOWED}"
        ),

        (
            "EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITE_COUNT}"
        ),

        (
            "BLOCKERS="
            + (
                ",".join(
                    blockers
                )

                if blockers

                else "NONE"
            )
        ),

    ]

    report_text = "\n".join(
        report_lines
    )

    print(

        "\n"
        + report_text
        + "\n",

        flush=True,

    )

    # ==============================================================================================
    # TELEGRAM FINAL REPORT
    # ==============================================================================================
    #
    # Only attempted after durable dedupe is proven.
    #
    # Telegram POST does NOT count as an exchange network write.
    # ==============================================================================================

    telegram_status = (
        "NOT_ATTEMPTED"
    )

    if durability.cross_deploy_durable:

        sent, telegram_status = (
            telegram_send_report_once(

                event_key=(

                    f"{VERSION}_"
                    "ACTIVATION_RECONCILIATION_"
                    + (
                        "MATCH"

                        if activation_env_match

                        else "MISMATCH"
                    )

                ),

                text=report_text,

                store=telegram_store,

            )
        )

        log(

            f"{VERSION}: "
            "TELEGRAM REPORT "
            f"SENT={sent} "
            f"STATUS={telegram_status}"

        )

    else:

        log(

            f"{VERSION}: "
            "TELEGRAM REPORT SKIPPED - "
            "DURABLE DEDUPE NOT PROVEN"

        )

    # ==============================================================================================
    # TERMINAL STATUS
    # ==============================================================================================

    divider()

    log(

        f"{VERSION}: FINAL STATUS="
        + (

            "ACTIVATION_ENV_RECONCILED_NO_LIVE_EXECUTION"

            if activation_env_match

            else "FAIL_CLOSED"

        )

    )

    log(

        f"{VERSION}: "
        "AUTHENTICATED_GET_COUNT="
        f"{AUTHENTICATED_GET_COUNT}"

    )

    log(

        f"{VERSION}: "
        "PUBLIC_GET_COUNT="
        f"{PUBLIC_GET_COUNT}"

    )

    log(

        f"{VERSION}: "
        "TELEGRAM_POST_COUNT="
        f"{TELEGRAM_POST_COUNT}"

    )

    log(

        f"{VERSION}: "
        "EXCHANGE_NETWORK_WRITE_COUNT="
        f"{EXCHANGE_NETWORK_WRITE_COUNT}"

    )

    log(
        f"{VERSION}: NO REAL ORDER WAS SENT"
    )

    divider()

    # ==============================================================================================
    # HEARTBEAT
    # ==============================================================================================

    heartbeat = 0

    while True:

        heartbeat += 1

        log(

            f"{VERSION}: "
            f"HEARTBEAT={heartbeat} "
            "PHASE="
            + (

                "ACTIVATION_ENV_RECONCILED"

                if activation_env_match

                else "FAIL_CLOSED"

            )
            + " "
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION} "
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITE_COUNT}"

        )

        time.sleep(
            30
        )


# ==================================================================================================
# ENTRY
# ==================================================================================================

if __name__ == "__mFor R35O to clear the two R35N Telegram blockers, the important Render-side requirement is that /var/data is an actual Persistent Disk mount, not merely a normal directory created inside the deployment filesystem. The expected successful ending is:

