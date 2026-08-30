

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ==================================================================================================
# R35O - RENDER PERSISTENT DISK + TELEGRAM DURABILITY RECONCILIATION
# ==================================================================================================
#
# PURPOSE
#
#   R35O fixes the persistence problem identified in R35N.
#
#   Render persistent disk:
#
#       /var/data
#
#   R35O places all durable local state beneath:
#
#       /var/data/r35o_state
#
#   R35O verifies:
#
#       1. /var/data exists.
#       2. /var/data is writable.
#       3. durable state can be created and read back.
#       4. Telegram dedupe state is stored on the persistent disk.
#       5. a deployment marker survives process/deployment restart.
#       6. authenticated WEEX account reads still work.
#       7. BTCUSDT remains flat.
#       8. margin remains ISOLATED.
#       9. long leverage remains 100x.
#      10. short leverage remains 100x.
#
# IMPORTANT
#
#   R35O DOES NOT SEND A REAL ORDER.
#
#   REAL ORDER EXECUTION        = HARD DISABLED
#   DEMO ORDER EXECUTION        = HARD DISABLED
#   EXCHANGE NETWORK WRITES     = HARD DISABLED
#   LEVERAGE MUTATION           = HARD DISABLED
#   MARGIN MUTATION             = HARD DISABLED
#   POSITION MUTATION           = HARD DISABLED
#
#   Telegram reporting is allowed because Telegram is not an exchange mutation.
#
#   On the FIRST deployment using /var/data, the persistent marker is created.
#
#   On the NEXT restart/redeploy, R35O can prove that the same marker survived.
#
#   Until that proof exists:
#
#       FIRST_REAL_ORDER_ALLOWED = False
#
# ==================================================================================================


VERSION = "R35O"
SYMBOL = "BTCUSDT"

HEALTH_PORT = int(os.getenv("PORT", "10000"))

# --------------------------------------------------------------------------------------------------
# RENDER PERSISTENT DISK
# --------------------------------------------------------------------------------------------------

PERSISTENT_DISK_ROOT = Path(
    os.getenv("R35O_PERSISTENT_DISK_ROOT", "/var/data")
)

STATE_DIR = PERSISTENT_DISK_ROOT / "r35o_state"

STATE_FILE = STATE_DIR / "r35o_state.json"
TELEGRAM_DEDUPE_FILE = STATE_DIR / "telegram_dedupe.json"
DEPLOYMENT_MARKER_FILE = STATE_DIR / "deployment_marker.json"
WRITE_PROBE_FILE = STATE_DIR / ".r35o_write_probe"

# --------------------------------------------------------------------------------------------------
# WEEX
# --------------------------------------------------------------------------------------------------

WEEX_BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

WEEX_API_KEY = os.getenv("WEEX_API_KEY", "").strip()
WEEX_API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
WEEX_API_PASSPHRASE = os.getenv("WEEX_API_PASSPHRASE", "").strip()

# These are READ-ONLY endpoints.
BALANCE_PATH = os.getenv(
    "WEEX_BALANCE_PATH",
    "/capi/v3/account/balance",
)

POSITIONS_PATH = os.getenv(
    "WEEX_POSITIONS_PATH",
    "/capi/v3/account/positions",
)

ACCOUNT_CONFIG_PATH = os.getenv(
    "WEEX_ACCOUNT_CONFIG_PATH",
    "/capi/v3/account/settings",
)

MARK_PRICE_PATH = os.getenv(
    "WEEX_MARK_PRICE_PATH",
    "/capi/v3/market/ticker",
)

# --------------------------------------------------------------------------------------------------
# TELEGRAM
# --------------------------------------------------------------------------------------------------

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# --------------------------------------------------------------------------------------------------
# TARGET ACCOUNT CONFIGURATION
# --------------------------------------------------------------------------------------------------

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

# --------------------------------------------------------------------------------------------------
# HARD SAFETY FIREBREAKS
# --------------------------------------------------------------------------------------------------

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

FIRST_REAL_ORDER_ALLOWED = False

EXCHANGE_NETWORK_WRITES = 0
REAL_ORDERS_SENT = 0
DEMO_ORDERS_SENT = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MUTATIONS = 0
POSITION_MUTATIONS = 0


# ==================================================================================================
# UTILITIES
# ==================================================================================================


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def line() -> None:
    print("-" * 100, flush=True)


def log(message: str) -> None:
    print(f"{utc_now()} {message}", flush=True)


def result(label: str, passed: bool) -> None:
    icon = "✅ PASS" if passed else "❌ FAIL"
    print(f"{label:<82} {icon}", flush=True)


def safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None

    if isinstance(value, bool):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value: Any) -> Optional[int]:
    number = safe_float(value)

    if number is None:
        return None

    try:
        return int(number)
    except (TypeError, ValueError):
        return None


def normalized_upper(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip().upper()


def read_json_file(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default

        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    except Exception as exc:
        log(f"{VERSION}: READ FILE FAILED path={path} error={exc}")
        return default


def atomic_write_json(path: Path, payload: Any) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        temporary = path.with_suffix(path.suffix + ".tmp")

        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(
                payload,
                handle,
                indent=2,
                sort_keys=True,
            )
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary, path)

        return True

    except Exception as exc:
        log(f"{VERSION}: ATOMIC WRITE FAILED path={path} error={exc}")
        return False


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        if self.path in ("/", "/health", "/healthz"):
            body = json.dumps(
                {
                    "service": VERSION,
                    "status": "ok",
                    "symbol": SYMBOL,
                    "real_order_execution": False,
                    "exchange_network_writes": EXCHANGE_NETWORK_WRITES,
                }
            ).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        return


def start_health_server() -> None:

    def run() -> None:
        server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)

        log(
            f"{VERSION}: HEALTH SERVER STARTED ON PORT "
            f"{HEALTH_PORT}"
        )

        server.serve_forever()

    thread = threading.Thread(
        target=run,
        daemon=True,
    )

    thread.start()


# ==================================================================================================
# RENDER DISK VERIFICATION
# ==================================================================================================


def verify_persistent_disk() -> Dict[str, Any]:

    result_data: Dict[str, Any] = {
        "root": str(PERSISTENT_DISK_ROOT),
        "state_dir": str(STATE_DIR),
        "root_exists": False,
        "state_dir_created": False,
        "write_ok": False,
        "readback_ok": False,
        "local_durable": False,
    }

    try:
        result_data["root_exists"] = PERSISTENT_DISK_ROOT.exists()

        STATE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        result_data["state_dir_created"] = STATE_DIR.exists()

        probe_value = {
            "version": VERSION,
            "timestamp": utc_now(),
            "probe": hashlib.sha256(
                f"{VERSION}:{time.time_ns()}".encode()
            ).hexdigest(),
        }

        write_ok = atomic_write_json(
            WRITE_PROBE_FILE,
            probe_value,
        )

        result_data["write_ok"] = write_ok

        read_back = read_json_file(
            WRITE_PROBE_FILE,
            {},
        )

        readback_ok = (
            isinstance(read_back, dict)
            and read_back.get("probe") == probe_value["probe"]
        )

        result_data["readback_ok"] = readback_ok

        result_data["local_durable"] = bool(
            result_data["root_exists"]
            and result_data["state_dir_created"]
            and write_ok
            and readback_ok
            and str(STATE_DIR).startswith("/var/data/")
        )

    except Exception as exc:
        result_data["error"] = str(exc)

    return result_data


# ==================================================================================================
# CROSS-RESTART / CROSS-DEPLOYMENT DURABILITY PROOF
# ==================================================================================================


def reconcile_deployment_marker() -> Dict[str, Any]:

    previous = read_json_file(
        DEPLOYMENT_MARKER_FILE,
        None,
    )

    previous_marker_exists = isinstance(previous, dict)

    previous_id = None
    previous_seen_count = 0

    if previous_marker_exists:
        previous_id = previous.get("marker_id")
        previous_seen_count = safe_int(
            previous.get("seen_count")
        ) or 0

    if previous_marker_exists and previous_id:
        marker_id = str(previous_id)
        seen_count = previous_seen_count + 1
        survived_restart = True

    else:
        marker_id = hashlib.sha256(
            f"{VERSION}:{time.time_ns()}:{os.getpid()}".encode()
        ).hexdigest()

        seen_count = 1
        survived_restart = False

    marker = {
        "version": VERSION,
        "marker_id": marker_id,
        "created_at": (
            previous.get("created_at")
            if previous_marker_exists
            else utc_now()
        ),
        "last_seen_at": utc_now(),
        "seen_count": seen_count,
    }

    persisted = atomic_write_json(
        DEPLOYMENT_MARKER_FILE,
        marker,
    )

    return {
        "previous_marker_exists": previous_marker_exists,
        "marker_id": marker_id,
        "seen_count": seen_count,
        "marker_persisted": persisted,
        "survived_restart": (
            survived_restart and persisted
        ),
    }


# ==================================================================================================
# TELEGRAM DURABLE DEDUPLICATION
# ==================================================================================================


def load_telegram_dedupe() -> Dict[str, Any]:
    data = read_json_file(
        TELEGRAM_DEDUPE_FILE,
        {},
    )

    if not isinstance(data, dict):
        data = {}

    messages = data.get("messages")

    if not isinstance(messages, dict):
        messages = {}

    return {
        "version": VERSION,
        "messages": messages,
    }


def save_telegram_dedupe(
    data: Dict[str, Any],
) -> bool:
    return atomic_write_json(
        TELEGRAM_DEDUPE_FILE,
        data,
    )


def telegram_message_key(message: str) -> str:
    return hashlib.sha256(
        message.encode("utf-8")
    ).hexdigest()


def telegram_was_sent(message: str) -> bool:
    state = load_telegram_dedupe()
    key = telegram_message_key(message)

    return key in state["messages"]


def mark_telegram_sent(message: str) -> bool:
    state = load_telegram_dedupe()

    key = telegram_message_key(message)

    state["messages"][key] = {
        "sent_at": utc_now(),
        "sha256": key,
    }

    # Prevent unbounded growth.
    messages = state["messages"]

    if len(messages) > 500:
        ordered = sorted(
            messages.items(),
            key=lambda item: item[1].get(
                "sent_at",
                "",
            ),
        )

        for old_key, _ in ordered[:-500]:
            messages.pop(
                old_key,
                None,
            )

    return save_telegram_dedupe(state)


def verify_telegram_dedupe_storage() -> bool:

    try:
        state = load_telegram_dedupe()

        state.setdefault(
            "messages",
            {},
        )

        state["last_storage_probe"] = {
            "version": VERSION,
            "timestamp": utc_now(),
        }

        if not save_telegram_dedupe(state):
            return False

        read_back = load_telegram_dedupe()

        return (
            TELEGRAM_DEDUPE_FILE.exists()
            and str(TELEGRAM_DEDUPE_FILE).startswith(
                "/var/data/"
            )
            and isinstance(
                read_back.get("messages"),
                dict,
            )
        )

    except Exception:
        return False


# ==================================================================================================
# TELEGRAM REPORTING
# ==================================================================================================
#
# Telegram POST is permitted only because it is a REPORTING operation.
#
# It is NOT:
#
#   - a WEEX request
#   - an exchange order
#   - a leverage mutation
#   - a position mutation
#
# ==================================================================================================


def send_telegram_report(
    message: str,
    dedupe: bool = True,
) -> Tuple[bool, str]:

    if not TELEGRAM_BOT_TOKEN:
        return False, "TELEGRAM_BOT_TOKEN_MISSING"

    if not TELEGRAM_CHAT_ID:
        return False, "TELEGRAM_CHAT_ID_MISSING"

    if dedupe and telegram_was_sent(message):
        return True, "DUPLICATE_SUPPRESSED"

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    payload = urllib.parse.urlencode(
        {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        url=url,
        data=payload,
        method="POST",
        headers={
            "Content-Type":
                "application/x-www-form-urlencoded",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            response_body = response.read().decode(
                "utf-8",
                errors="replace",
            )

            parsed = json.loads(response_body)

            if not parsed.get("ok"):
                return False, "TELEGRAM_API_REJECTED"

        if dedupe:
            if not mark_telegram_sent(message):
                return (
                    False,
                    "TELEGRAM_SENT_BUT_DEDUPE_PERSIST_FAILED",
                )

        return True, "SENT"

    except Exception as exc:
        return False, f"TELEGRAM_FAILED:{exc}"


# ==================================================================================================
# HTTP READ BOUNDARY
# ==================================================================================================


def public_get_json(
    path: str,
    query: Optional[Dict[str, Any]] = None,
) -> Any:

    if not path.startswith("/"):
        raise ValueError("WEEX path must start with /")

    query_string = ""

    if query:
        query_string = "?" + urllib.parse.urlencode(
            {
                key: str(value)
                for key, value in query.items()
                if value is not None
            }
        )

    url = WEEX_BASE_URL + path + query_string

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}/1.0",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=15,
    ) as response:

        raw = response.read().decode(
            "utf-8",
            errors="replace",
        )

    return json.loads(raw)


def authenticated_get_json(
    path: str,
    query: Optional[Dict[str, Any]] = None,
) -> Any:

    if not WEEX_API_KEY:
        raise RuntimeError("WEEX_API_KEY missing")

    if not WEEX_API_SECRET:
        raise RuntimeError("WEEX_API_SECRET missing")

    if not WEEX_API_PASSPHRASE:
        raise RuntimeError(
            "WEEX_API_PASSPHRASE missing"
        )

    if not path.startswith("/"):
        raise ValueError(
            "WEEX path must start with /"
        )

    query_string = ""

    if query:
        query_string = urllib.parse.urlencode(
            {
                key: str(value)
                for key, value in query.items()
                if value is not None
            }
        )

    request_path = path

    if query_string:
        request_path += "?" + query_string

    timestamp = str(int(time.time() * 1000))

    method = "GET"
    body = ""

    prehash = (
        timestamp
        + method
        + request_path
        + body
    )

    signature = base64.b64encode(
        hmac.new(
            WEEX_API_SECRET.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}/1.0",
    }

    request = urllib.request.Request(
        url=WEEX_BASE_URL + request_path,
        method="GET",
        headers=headers,
    )

    with urllib.request.urlopen(
        request,
        timeout=15,
    ) as response:

        raw = response.read().decode(
            "utf-8",
            errors="replace",
        )

    return json.loads(raw)


# ==================================================================================================
# GENERIC JSON WALKERS
# ==================================================================================================


def walk_json(value: Any):

    if isinstance(value, dict):

        yield value

        for child in value.values():
            yield from walk_json(child)

    elif isinstance(value, list):

        for child in value:
            yield from walk_json(child)


def first_numeric_by_keys(
    payload: Any,
    keys: List[str],
) -> Optional[float]:

    lowered = {
        key.lower()
        for key in keys
    }

    for node in walk_json(payload):

        for key, value in node.items():

            if str(key).lower() in lowered:

                number = safe_float(value)

                if number is not None:
                    return number

    return None


def first_string_by_keys(
    payload: Any,
    keys: List[str],
) -> Optional[str]:

    lowered = {
        key.lower()
        for key in keys
    }

    for node in walk_json(payload):

        for key, value in node.items():

            if str(key).lower() in lowered:

                if value is not None:
                    return str(value)

    return None


# ==================================================================================================
# WEEX BALANCE
# ==================================================================================================


def read_balance() -> Tuple[Optional[float], Any]:

    payload = authenticated_get_json(
        BALANCE_PATH,
        {
            "coin": "USDT",
        },
    )

    balance = first_numeric_by_keys(
        payload,
        [
            "available",
            "availableBalance",
            "availableEquity",
            "availableAmount",
            "free",
            "balance",
        ],
    )

    return balance, payload


# ==================================================================================================
# WEEX POSITIONS
# ==================================================================================================


def read_positions() -> Tuple[Optional[int], Any]:

    candidates = [
        {"symbol": SYMBOL},
        None,
    ]

    last_error: Optional[Exception] = None

    for query in candidates:

        try:
            payload = authenticated_get_json(
                POSITIONS_PATH,
                query,
            )

            active_positions = 0

            for node in walk_json(payload):

                symbol_value = (
                    node.get("symbol")
                    or node.get("contract")
                    or node.get("instrumentId")
                )

                if symbol_value is not None:

                    if normalized_upper(
                        symbol_value
                    ) != SYMBOL:
                        continue

                quantity = first_numeric_by_keys(
                    node,
                    [
                        "size",
                        "quantity",
                        "qty",
                        "positionAmt",
                        "positionSize",
                        "holdVol",
                        "total",
                    ],
                )

                if quantity is not None:

                    if abs(quantity) > 0:
                        active_positions += 1

            return active_positions, payload

        except Exception as exc:
            last_error = exc

    if last_error:
        raise last_error

    raise RuntimeError(
        "Positions could not be read"
    )


# ==================================================================================================
# ACCOUNT CONFIGURATION
# ==================================================================================================


def read_account_configuration() -> Tuple[
    Optional[str],
    Optional[int],
    Optional[int],
    Any,
]:

    payload = authenticated_get_json(
        ACCOUNT_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    margin_mode = first_string_by_keys(
        payload,
        [
            "marginMode",
            "marginType",
            "margin_mode",
            "margin_type",
        ],
    )

    long_leverage = first_numeric_by_keys(
        payload,
        [
            "longLeverage",
            "long_leverage",
            "leverageLong",
            "buyLeverage",
        ],
    )

    short_leverage = first_numeric_by_keys(
        payload,
        [
            "shortLeverage",
            "short_leverage",
            "leverageShort",
            "sellLeverage",
        ],
    )

    # Some WEEX responses may expose one common leverage field.
    common_leverage = first_numeric_by_keys(
        payload,
        [
            "leverage",
        ],
    )

    if long_leverage is None:
        long_leverage = common_leverage

    if short_leverage is None:
        short_leverage = common_leverage

    return (
        normalized_upper(margin_mode)
        if margin_mode
        else None,
        int(long_leverage)
        if long_leverage is not None
        else None,
        int(short_leverage)
        if short_leverage is not None
        else None,
        payload,
    )


# ==================================================================================================
# PUBLIC MARK PRICE
# ==================================================================================================


def read_mark_price() -> Tuple[Optional[float], Any]:

    payload = public_get_json(
        MARK_PRICE_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    mark_price = first_numeric_by_keys(
        payload,
        [
            "markPrice",
            "mark_price",
            "last",
            "lastPrice",
            "close",
            "price",
        ],
    )

    return mark_price, payload


# ==================================================================================================
# STATE
# ==================================================================================================


def save_runtime_state(
    state: Dict[str, Any],
) -> bool:

    state["version"] = VERSION
    state["updated_at"] = utc_now()

    return atomic_write_json(
        STATE_FILE,
        state,
    )


# ==================================================================================================
# MAIN
# ==================================================================================================


def main() -> None:

    global FIRST_REAL_ORDER_ALLOWED

    start_health_server()

    time.sleep(0.2)

    line()
    log(f"{VERSION}: MAIN.PY ENTERED")
    line()

    log(f"{VERSION}: SYMBOL={SYMBOL}")
    log(f"{VERSION}: VERSION={VERSION}")
    log(f"{VERSION}: HEALTH PORT={HEALTH_PORT}")

    log(
        f"{VERSION}: PERSISTENT DISK ROOT="
        f"{PERSISTENT_DISK_ROOT}"
    )

    log(
        f"{VERSION}: STATE DIR="
        f"{STATE_DIR}"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"{VERSION}: DEMO ORDER EXECUTION="
        f"{DEMO_ORDER_EXECUTION}"
    )

    log(
        f"{VERSION}: EXCHANGE NETWORK WRITES ENABLED="
        f"{EXCHANGE_NETWORK_WRITES_ENABLED}"
    )

    line()

    # ==============================================================================================
    # TEST 1 - HARD SAFETY FIREBREAK
    # ==============================================================================================

    log(
        f"{VERSION} TEST 1: HARD SAFETY FIREBREAK"
    )

    line()

    result(
        "Real Order Execution Is Hard Disabled",
        REAL_ORDER_EXECUTION is False,
    )

    result(
        "Demo Order Execution Is Hard Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    result(
        "Exchange Network Writes Are Hard Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    result(
        "Leverage Mutation Is Hard Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    result(
        "Margin Mutation Is Hard Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    result(
        "Position Mutation Is Hard Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    result(
        "First Real Order Is Hard Forbidden",
        FIRST_REAL_ORDER_ALLOWED is False,
    )

    line()

    # ==============================================================================================
    # TEST 2 - RENDER PERSISTENT DISK
    # ==============================================================================================

    log(
        f"{VERSION} TEST 2: RENDER PERSISTENT DISK"
    )

    line()

    disk = verify_persistent_disk()

    result(
        "/var/data Exists",
        disk["root_exists"],
    )

    result(
        "Persistent State Directory Exists",
        disk["state_dir_created"],
    )

    result(
        "Persistent Disk Accepts Durable Write",
        disk["write_ok"],
    )

    result(
        "Persistent Disk Write Reads Back Correctly",
        disk["readback_ok"],
    )

    result(
        "R35O State Is Located Under /var/data",
        disk["local_durable"],
    )

    log(
        f"{VERSION}: PERSISTENT ROOT="
        f"{disk['root']}"
    )

    log(
        f"{VERSION}: PERSISTENT STATE DIR="
        f"{disk['state_dir']}"
    )

    line()

    # ==============================================================================================
    # TEST 3 - CROSS RESTART MARKER
    # ==============================================================================================

    log(
        f"{VERSION} TEST 3: CROSS-RESTART DURABILITY MARKER"
    )

    line()

    marker = reconcile_deployment_marker()

    result(
        "Deployment Marker Persisted",
        marker["marker_persisted"],
    )

    result(
        "Previous Deployment Marker Was Found",
        marker["previous_marker_exists"],
    )

    result(
        "Persistent Marker Survived A Restart",
        marker["survived_restart"],
    )

    log(
        f"{VERSION}: DURABLE MARKER ID="
        f"{marker['marker_id']}"
    )

    log(
        f"{VERSION}: DURABLE MARKER SEEN COUNT="
        f"{marker['seen_count']}"
    )

    if marker["survived_restart"]:
        log(
            f"{VERSION}: CROSS-DEPLOY DURABILITY "
            f"PROOF=CONFIRMED"
        )
    else:
        log(
            f"{VERSION}: CROSS-DEPLOY DURABILITY "
            f"PROOF=PENDING_NEXT_RESTART"
        )

    line()

    # ==============================================================================================
    # TEST 4 - TELEGRAM DEDUPE STORAGE
    # ==============================================================================================

    log(
        f"{VERSION} TEST 4: TELEGRAM DURABLE DEDUPE"
    )

    line()

    telegram_local_durable = (
        verify_telegram_dedupe_storage()
    )

    telegram_cross_deploy_durable = bool(
        telegram_local_durable
        and marker["survived_restart"]
    )

    result(
        "Telegram Dedupe File Uses /var/data",
        str(TELEGRAM_DEDUPE_FILE).startswith(
            "/var/data/"
        ),
    )

    result(
        "Telegram Dedupe State Is Writable",
        telegram_local_durable,
    )

    result(
        "Telegram Local Durable Storage Confirmed",
        telegram_local_durable,
    )

    result(
        "Telegram Cross-Deploy Durability Confirmed",
        telegram_cross_deploy_durable,
    )

    log(
        f"{VERSION}: TELEGRAM DEDUPE FILE="
        f"{TELEGRAM_DEDUPE_FILE}"
    )

    line()

    # ==============================================================================================
    # TEST 5 - CREDENTIAL ENVIRONMENT
    # ==============================================================================================

    log(
        f"{VERSION} TEST 5: WEEX CREDENTIAL ENVIRONMENT"
    )

    line()

    credentials_ok = bool(
        WEEX_API_KEY
        and WEEX_API_SECRET
        and WEEX_API_PASSPHRASE
    )

    result(
        "WEEX_API_KEY Is Present",
        bool(WEEX_API_KEY),
    )

    result(
        "WEEX_API_SECRET Is Present",
        bool(WEEX_API_SECRET),
    )

    result(
        "WEEX_API_PASSPHRASE Is Present",
        bool(WEEX_API_PASSPHRASE),
    )

    result(
        "Authenticated Read Credential Set Is Complete",
        credentials_ok,
    )

    line()

    # ==============================================================================================
    # TEST 6 - BALANCE
    # ==============================================================================================

    log(
        f"{VERSION} TEST 6: AUTHENTICATED BALANCE READ"
    )

    line()

    balance: Optional[float] = None
    balance_read_ok = False

    if credentials_ok:

        try:
            balance, _ = read_balance()

            balance_read_ok = (
                balance is not None
                and balance >= 0
            )

        except Exception as exc:
            log(
                f"{VERSION}: BALANCE READ FAILED: {exc}"
            )

    result(
        "Authenticated WEEX Balance Read Succeeded",
        balance_read_ok,
    )

    if balance is not None:
        log(
            f"{VERSION}: BALANCE={balance}"
        )
    else:
        log(
            f"{VERSION}: BALANCE=UNKNOWN"
        )

    line()

    # ==============================================================================================
    # TEST 7 - POSITIONS
    # ==============================================================================================

    log(
        f"{VERSION} TEST 7: BTCUSDT POSITION RECONCILIATION"
    )

    line()

    open_positions: Optional[int] = None
    position_read_ok = False

    if credentials_ok:

        try:
            open_positions, _ = read_positions()

            position_read_ok = (
                open_positions is not None
            )

        except Exception as exc:
            log(
                f"{VERSION}: POSITION READ FAILED: {exc}"
            )

    result(
        "Authenticated Position Read Succeeded",
        position_read_ok,
    )

    result(
        "BTCUSDT Has Zero Open Positions",
        open_positions == 0,
    )

    log(
        f"{VERSION}: OPEN POSITIONS="
        f"{open_positions if open_positions is not None else 'UNKNOWN'}"
    )

    line()

    # ==============================================================================================
    # TEST 8 - ACCOUNT CONFIGURATION
    # ==============================================================================================

    log(
        f"{VERSION} TEST 8: ACCOUNT CONFIGURATION RECONCILIATION"
    )

    line()

    margin_mode: Optional[str] = None
    long_leverage: Optional[int] = None
    short_leverage: Optional[int] = None

    config_read_ok = False

    if credentials_ok:

        try:

            (
                margin_mode,
                long_leverage,
                short_leverage,
                _,
            ) = read_account_configuration()

            config_read_ok = True

        except Exception as exc:
            log(
                f"{VERSION}: ACCOUNT CONFIG READ FAILED: "
                f"{exc}"
            )

    result(
        "Authenticated Account Configuration Read Succeeded",
        config_read_ok,
    )

    result(
        "Margin Mode Is ISOLATED",
        margin_mode == TARGET_MARGIN_MODE,
    )

    result(
        "Long Leverage Is 100x",
        long_leverage == TARGET_LONG_LEVERAGE,
    )

    result(
        "Short Leverage Is 100x",
        short_leverage == TARGET_SHORT_LEVERAGE,
    )

    log(
        f"{VERSION}: MARGIN MODE="
        f"{margin_mode or 'UNKNOWN'}"
    )

    log(
        f"{VERSION}: LONG LEVERAGE="
        f"{str(long_leverage) + 'x' if long_leverage is not None else 'UNKNOWN'}"
    )

    log(
        f"{VERSION}: SHORT LEVERAGE="
        f"{str(short_leverage) + 'x' if short_leverage is not None else 'UNKNOWN'}"
    )

    line()

    # ==============================================================================================
    # TEST 9 - MARK PRICE
    # ==============================================================================================

    log(
        f"{VERSION} TEST 9: PUBLIC MARK PRICE"
    )

    line()

    mark_price: Optional[float] = None
    mark_price_read_ok = False

    try:
        mark_price, _ = read_mark_price()

        mark_price_read_ok = bool(
            mark_price is not None
            and mark_price > 0
        )

    except Exception as exc:
        log(
            f"{VERSION}: MARK PRICE READ FAILED: {exc}"
        )

    result(
        "BTCUSDT Mark Price Was Read",
        mark_price_read_ok,
    )

    if mark_price is not None:
        log(
            f"{VERSION}: MARK PRICE={mark_price}"
        )
    else:
        log(
            f"{VERSION}: MARK PRICE=UNKNOWN"
        )

    line()

    # ==============================================================================================
    # TEST 10 - ACTIVATION ENVIRONMENT RECONCILIATION
    # ==============================================================================================

    log(
        f"{VERSION} TEST 10: ACTIVATION ENVIRONMENT RECONCILIATION"
    )

    line()

    blockers: List[str] = []

    if not disk["local_durable"]:
        blockers.append(
            "PERSISTENT_DISK_NOT_READY"
        )

    if not telegram_local_durable:
        blockers.append(
            "TELEGRAM_DEDUPE_LOCAL_STORAGE_FAILED"
        )

    if not telegram_cross_deploy_durable:
        blockers.append(
            "TELEGRAM_DEDUPE_NOT_CROSS_DEPLOY_DURABLE"
        )

    if not credentials_ok:
        blockers.append(
            "WEEX_CREDENTIAL_ENVIRONMENT_INCOMPLETE"
        )

    if not balance_read_ok:
        blockers.append(
            "AUTHENTICATED_WEEX_READ_FAILED"
        )

    if not position_read_ok:
        blockers.append(
            "POSITION_RECONCILIATION_FAILED"
        )

    if open_positions != 0:
        blockers.append(
            "BTCUSDT_NOT_FLAT"
        )

    if margin_mode != TARGET_MARGIN_MODE:
        blockers.append(
            "MARGIN_MODE_MISMATCH"
        )

    if long_leverage != TARGET_LONG_LEVERAGE:
        blockers.append(
            "LONG_LEVERAGE_MISMATCH"
        )

    if short_leverage != TARGET_SHORT_LEVERAGE:
        blockers.append(
            "SHORT_LEVERAGE_MISMATCH"
        )

    if not mark_price_read_ok:
        blockers.append(
            "MARK_PRICE_READ_FAILED"
        )

    activation_environment_ok = (
        len(blockers) == 0
    )

    # ----------------------------------------------------------------------------------------------
    # CRITICAL R35O SAFETY RULE
    #
    # Even if every reconciliation check passes, R35O remains a NON-EXECUTION build.
    #
    # Therefore:
    #
    #     FIRST_REAL_ORDER_ALLOWED = False
    #
    # This unit proves the environment.
    # It does not promote the real writer.
    # ----------------------------------------------------------------------------------------------

    FIRST_REAL_ORDER_ALLOWED = False

    result(
        "Activation Environment Is Fully Reconciled",
        activation_environment_ok,
    )

    result(
        "Exchange Network Write Count Remains Zero",
        EXCHANGE_NETWORK_WRITES == 0,
    )

    result(
        "Real Order Count Remains Zero",
        REAL_ORDERS_SENT == 0,
    )

    result(
        "First Real Order Remains Forbidden In R35O",
        FIRST_REAL_ORDER_ALLOWED is False,
    )

    activation_env = (
        "MATCH"
        if activation_environment_ok
        else "MISMATCH"
    )

    line()

    # ==============================================================================================
    # TEST 11 - DURABLE STATE COMMIT
    # ==============================================================================================

    log(
        f"{VERSION} TEST 11: DURABLE STATE COMMIT"
    )

    line()

    runtime_state = {
        "symbol": SYMBOL,
        "persistent_disk_root": str(
            PERSISTENT_DISK_ROOT
        ),
        "state_dir": str(STATE_DIR),
        "telegram_dedupe_file": str(
            TELEGRAM_DEDUPE_FILE
        ),
        "telegram_local_durable":
            telegram_local_durable,
        "telegram_cross_deploy_durable":
            telegram_cross_deploy_durable,
        "deployment_marker_id":
            marker["marker_id"],
        "deployment_marker_seen_count":
            marker["seen_count"],
        "balance": balance,
        "mark_price": mark_price,
        "open_positions": open_positions,
        "margin_mode": margin_mode,
        "long_leverage": long_leverage,
        "short_leverage": short_leverage,
        "activation_env": activation_env,
        "activation_environment_ok":
            activation_environment_ok,
        "real_order_execution":
            REAL_ORDER_EXECUTION,
        "first_real_order_allowed":
            FIRST_REAL_ORDER_ALLOWED,
        "exchange_network_writes":
            EXCHANGE_NETWORK_WRITES,
        "blockers": blockers,
    }

    durable_commit_ok = save_runtime_state(
        runtime_state
    )

    result(
        "R35O Runtime State Was Persisted To /var/data",
        durable_commit_ok,
    )

    line()

    # ==============================================================================================
    # TEST 12 - FINAL SAFETY RECONCILIATION
    # ==============================================================================================

    log(
        f"{VERSION} TEST 12: FINAL SAFETY RECONCILIATION"
    )

    line()

    result(
        "Exchange Network Writes Remain Zero",
        EXCHANGE_NETWORK_WRITES == 0,
    )

    result(
        "Real Orders Sent Remain Zero",
        REAL_ORDERS_SENT == 0,
    )

    result(
        "Demo Orders Sent Remain Zero",
        DEMO_ORDERS_SENT == 0,
    )

    result(
        "Leverage Mutations Remain Zero",
        LEVERAGE_MUTATIONS == 0,
    )

    result(
        "Margin Mutations Remain Zero",
        MARGIN_MUTATIONS == 0,
    )

    result(
        "Position Mutations Remain Zero",
        POSITION_MUTATIONS == 0,
    )

    result(
        "R35O Cannot Send First Real Order",
        FIRST_REAL_ORDER_ALLOWED is False,
    )

    line()

    # ==============================================================================================
    # FINAL REPORT
    # ==============================================================================================

    report_lines = [
        f"⚙️ {VERSION} ACTIVATION ENV RECONCILIATION",
        f"SYMBOL={SYMBOL}",
        (
            "BALANCE="
            + (
                str(balance)
                if balance is not None
                else "UNKNOWN"
            )
        ),
        (
            "MARK_PRICE="
            + (
                str(mark_price)
                if mark_price is not None
                else "UNKNOWN"
            )
        ),
        (
            "OPEN_POSITIONS="
            + (
                str(open_positions)
                if open_positions is not None
                else "UNKNOWN"
            )
        ),
        f"MARGIN_MODE={margin_mode or 'UNKNOWN'}",
        (
            "LONG_LEVERAGE="
            + (
                f"{long_leverage}x"
                if long_leverage is not None
                else "UNKNOWN"
            )
        ),
        (
            "SHORT_LEVERAGE="
            + (
                f"{short_leverage}x"
                if short_leverage is not None
                else "UNKNOWN"
            )
        ),
        f"PERSISTENT_DISK_ROOT={PERSISTENT_DISK_ROOT}",
        f"STATE_DIR={STATE_DIR}",
        (
            "TELEGRAM_LOCAL_DURABLE="
            f"{telegram_local_durable}"
        ),
        (
            "TELEGRAM_CROSS_DEPLOY_DURABLE="
            f"{telegram_cross_deploy_durable}"
        ),
        (
            "DURABLE_MARKER_SEEN_COUNT="
            f"{marker['seen_count']}"
        ),
        f"ACTIVATION_ENV={activation_env}",
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
            f"{EXCHANGE_NETWORK_WRITES}"
        ),
        (
            "BLOCKERS="
            + (
                ",".join(blockers)
                if blockers
                else "NONE"
            )
        ),
    ]

    final_report = "\n".join(
        report_lines
    )

    print(
        final_report,
        flush=True,
    )

    line()

    # Telegram reporting happens only after durable local state has been established.
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:

        telegram_ok, telegram_status = (
            send_telegram_report(
                final_report,
                dedupe=True,
            )
        )

        result(
            "Telegram Final Report Operation Completed",
            telegram_ok,
        )

        log(
            f"{VERSION}: TELEGRAM STATUS="
            f"{telegram_status}"
        )

    else:
        log(
            f"{VERSION}: TELEGRAM REPORT SKIPPED "
            f"BECAUSE TELEGRAM ENVIRONMENT IS INCOMPLETE"
        )

    line()

    log(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    log(
        f"{VERSION}: NO REAL ORDER WAS SENT"
    )

    log(
        f"{VERSION}: EXCHANGE NETWORK WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )

    line()

    # ==============================================================================================
    # HEARTBEAT
    # ==============================================================================================

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{VERSION}: HEARTBEAT={heartbeat} "
            f"PHASE=PERSISTENT_DISK_RECONCILIATION_COMPLETE "
            f"ACTIVATION_ENV={activation_env} "
            f"TELEGRAM_LOCAL_DURABLE={telegram_local_durable} "
            f"TELEGRAM_CROSS_DEPLOY_DURABLE={telegram_cross_deploy_durable} "
            f"REAL_ORDER_EXECUTION=False "
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}"
        )

        time.sleep(30)


# ==================================================================================================
# ENTRY POINT
# ==================================================================================================


if __name__ == "__main__":
    main()
