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
from dataclasses import asdict, dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ==================================================================================================
# R35I - CONTROLLED FIRST-ORDER BOUNDARY VALIDATION (NO REAL ORDER EXECUTION)
# ==================================================================================================
#
# IMPORTANT SAFETY GUARANTEES
#   * WEEX authenticated/public READS are allowed.
#   * WEEX POST/PUT/PATCH/DELETE are NEVER transmitted by this program.
#   * Real order execution is hard-disabled.
#   * Demo order execution is hard-disabled.
#   * The first real order remains forbidden.
#   * Order dispatch is synthetic only.
#   * Telegram POST is reporting-only and cannot control execution.
#   * Telegram sends at most one consolidated report per process run.
#
# R35I FIX
#   * Uses current WEEX V3 private-read endpoints.
#   * Signs GET query strings exactly as: timestamp + METHOD + path + "?" + query.
#   * Uses the same exact encoded query in both the signature and request URL.
#   * Live gate arms only after credentials + all required private reads + reconciliation succeed.
#   * A failed authenticated read fails closed and cannot arm the live gate.
# ==================================================================================================

VERSION = "R35I"

SYMBOL = (
    os.getenv(
        "SYMBOL",
        "BTCUSDT",
    )
    .strip()
    .upper()
    or "BTCUSDT"
)

BASE_URL = os.getenv(
    "WEEX_CONTRACT_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

HEALTH_PORT = int(
    os.getenv(
        "PORT",
        os.getenv(
            "HEALTH_PORT",
            "10000",
        ),
    )
)

STATE_DIR = Path(
    os.getenv(
        "R35I_STATE_DIR",
        "/tmp/r35i_state",
    )
)

STATE_FILE = STATE_DIR / "state.json"

JOURNAL_FILE = STATE_DIR / "journal.jsonl"


# ==================================================================================================
# CREDENTIALS
# ==================================================================================================

API_KEY = os.getenv(
    "WEEX_API_KEY",
    os.getenv(
        "API_KEY",
        "",
    ),
).strip()

API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    os.getenv(
        "SECRET_KEY",
        os.getenv(
            "API_SECRET",
            "",
        ),
    ),
).strip()

API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    os.getenv(
        "ACCESS_PASSPHRASE",
        os.getenv(
            "API_PASSPHRASE",
            "",
        ),
    ),
).strip()


# ==================================================================================================
# TELEGRAM REPORTING
# ==================================================================================================

TELEGRAM_ENABLED = (
    os.getenv(
        "TELEGRAM_ENABLED",
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

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


# ==================================================================================================
# RUNTIME
# ==================================================================================================

REQUEST_TIMEOUT_SECONDS = float(
    os.getenv(
        "R35I_REQUEST_TIMEOUT",
        "12",
    )
)

RUN_NONCE = str(
    time.time_ns()
)


# ==================================================================================================
# HARD SAFETY LOCKS
# ==================================================================================================
#
# DO NOT CONVERT THESE TO ENVIRONMENT TOGGLES IN R35I.
#
# R35I is still a validation release.
#
# Exchange authenticated GET operations are permitted.
# Exchange mutation operations remain physically disabled.
#
# ==================================================================================================

EXCHANGE_WRITER_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

REAL_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

FIRST_REAL_ORDER_ALLOWED = False

SYNTHETIC_DISPATCH_ONLY = True


# ==================================================================================================
# WEEX V3 ENDPOINTS
# ==================================================================================================

BALANCE_PATH = (
    "/capi/v3/account/balance"
)

POSITIONS_PATH = (
    "/capi/v3/account/position/allPosition"
)

SYMBOL_CONFIG_PATH = (
    "/capi/v3/account/symbolConfig"
)

MARK_PRICE_PATH = (
    "/capi/v3/market/symbolPrice"
)

ORDER_PATH = (
    "/capi/v3/order"
)


LINE = "-" * 100


# ==================================================================================================
# BASIC HELPERS
# ==================================================================================================

def utc_stamp() -> str:

    now = time.time()

    whole = int(
        now
    )

    micros = int(
        (now - whole)
        * 1_000_000
    )

    return (
        time.strftime(
            "%Y-%m-%dT%H:%M:%S",
            time.gmtime(
                whole
            ),
        )
        + f".{micros:06d}Z"
    )


def log(
    message: str = "",
) -> None:

    print(
        f"{utc_stamp()} {message}",
        flush=True,
    )


def section(
    title: str,
) -> None:

    log(
        LINE
    )

    log(
        title
    )

    log(
        LINE
    )


def verdict(
    label: str,
    ok: bool,
) -> bool:

    result = (
        "✅ PASS"
        if ok
        else "❌ FAIL"
    )

    log(
        f"{label:<84} {result}"
    )

    return ok


def canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )


def sha256_text(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def atomic_json_write(
    path: Path,
    payload: Dict[str, Any],
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    tmp = path.with_suffix(
        path.suffix
        + ".tmp"
    )

    data = json.dumps(
        payload,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )

    with tmp.open(
        "w",
        encoding="utf-8",
    ) as fh:

        fh.write(
            data
        )

        fh.flush()

        os.fsync(
            fh.fileno()
        )

    os.replace(
        tmp,
        path,
    )


# ==================================================================================================
# DURABLE STATE
# ==================================================================================================

@dataclass
class StrategyState:

    version: str = VERSION

    symbol: str = SYMBOL

    generation: int = 1

    epoch: int = 1

    live_mode_armed: bool = False

    kill_switch: bool = False

    ambiguous_outcome: bool = False

    authenticated_reads_ok: bool = False

    exchange_reconciled: bool = False

    exchange_network_writes: int = 0

    consumed_intents: List[str] = field(
        default_factory=list
    )

    consumed_authorizations: List[str] = field(
        default_factory=list
    )

    used_client_order_ids: List[str] = field(
        default_factory=list
    )

    durable_receipts: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    journal_sequence: int = 0

    last_journal_hash: str = (
        "0" * 64
    )

    telegram_reports_this_run: int = 0


# ==================================================================================================
# DURABLE STORE
# ==================================================================================================

class DurableStore:

    def __init__(
        self,
        state_file: Path,
        journal_file: Path,
    ) -> None:

        self.state_file = (
            state_file
        )

        self.journal_file = (
            journal_file
        )

        self.lock = (
            threading.RLock()
        )

        STATE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )


    def load(
        self,
    ) -> StrategyState:

        with self.lock:

            if not self.state_file.exists():

                return StrategyState()

            try:

                raw = json.loads(
                    self.state_file.read_text(
                        encoding="utf-8"
                    )
                )

                allowed = {
                    name
                    for name
                    in StrategyState.__dataclass_fields__
                }

                clean = {
                    key: value
                    for key, value
                    in raw.items()
                    if key in allowed
                }

                state = StrategyState(
                    **clean
                )

                if (
                    state.version
                    != VERSION
                    or state.symbol
                    != SYMBOL
                ):

                    return StrategyState()

                state.telegram_reports_this_run = 0

                return state

            except Exception as exc:

                log(
                    f"{VERSION}: "
                    f"STATE LOAD FAILED CLOSED: "
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

                return StrategyState(
                    kill_switch=True,
                    ambiguous_outcome=True,
                )


    def save(
        self,
        state: StrategyState,
    ) -> None:

        with self.lock:

            atomic_json_write(
                self.state_file,
                asdict(
                    state
                ),
            )


    def append(
        self,
        state: StrategyState,
        event: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:

        with self.lock:

            seq = (
                state.journal_sequence
                + 1
            )

            body = {

                "version":
                    VERSION,

                "symbol":
                    SYMBOL,

                "sequence":
                    seq,

                "event":
                    event,

                "details":
                    details,

                "previous_hash":
                    state.last_journal_hash,
            }

            record_hash = sha256_text(
                canonical_json(
                    body
                )
            )

            record = dict(
                body
            )

            record[
                "record_hash"
            ] = record_hash

            self.journal_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self.journal_file.open(
                "a",
                encoding="utf-8",
            ) as fh:

                fh.write(
                    canonical_json(
                        record
                    )
                    + "\n"
                )

                fh.flush()

                os.fsync(
                    fh.fileno()
                )

            state.journal_sequence = (
                seq
            )

            state.last_journal_hash = (
                record_hash
            )

            self.save(
                state
            )

            return record


    def verify_journal(
        self,
    ) -> Tuple[
        bool,
        int,
    ]:

        with self.lock:

            if not self.journal_file.exists():

                return (
                    True,
                    0,
                )

            previous = (
                "0" * 64
            )

            count = 0

            try:

                with self.journal_file.open(
                    "r",
                    encoding="utf-8",
                ) as fh:

                    for raw_line in fh:

                        line = (
                            raw_line.strip()
                        )

                        if not line:

                            continue

                        record = json.loads(
                            line
                        )

                        expected_hash = (
                            record.get(
                                "record_hash",
                                "",
                            )
                        )

                        body = {
                            key: value
                            for key, value
                            in record.items()
                            if key
                            != "record_hash"
                        }

                        if (
                            body.get(
                                "previous_hash"
                            )
                            != previous
                        ):

                            return (
                                False,
                                count,
                            )

                        actual_hash = sha256_text(
                            canonical_json(
                                body
                            )
                        )

                        if (
                            actual_hash
                            != expected_hash
                        ):

                            return (
                                False,
                                count,
                            )

                        previous = (
                            expected_hash
                        )

                        count += 1

                return (
                    True,
                    count,
                )

            except Exception:

                return (
                    False,
                    count,
                )


STORE = DurableStore(
    STATE_FILE,
    JOURNAL_FILE,
)

STATE = STORE.load()


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ) -> None:

        payload = {

            "ok":
                True,

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "exchangeNetworkWrites":
                STATE.exchange_network_writes,

            "realOrderExecution":
                REAL_ORDER_EXECUTION,

            "liveModeArmed":
                STATE.live_mode_armed,
        }

        body = json.dumps(
            payload,
            separators=(
                ",",
                ":",
            ),
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


    def log_message(
        self,
        fmt: str,
        *args: Any,
    ) -> None:

        return


def start_health_server(
) -> None:

    try:

        server = HTTPServer(
            (
                "0.0.0.0",
                HEALTH_PORT,
            ),
            HealthHandler,
        )

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )

        thread.start()

        log(
            f"{VERSION}: "
            f"HEALTH SERVER STARTED "
            f"ON PORT {HEALTH_PORT}"
        )

    except OSError as exc:

        log(
            f"{VERSION}: "
            f"HEALTH SERVER NOTICE: "
            f"{exc}"
        )


# ==================================================================================================
# CREDENTIAL VALIDATION
# ==================================================================================================

def credential_status(
) -> Dict[str, bool]:

    return {

        "api_key":
            bool(
                API_KEY
            ),

        "api_secret":
            bool(
                API_SECRET
            ),

        "api_passphrase":
            bool(
                API_PASSPHRASE
            ),
    }


# ==================================================================================================
# WEEX V3 SIGNATURE
# ==================================================================================================

def sign_weex(
    method: str,
    path: str,
    query: str = "",
    body: str = "",
) -> Tuple[
    str,
    str,
]:

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    method_upper = (
        method.upper()
    )

    if query:

        prehash = (
            timestamp
            + method_upper
            + path
            + "?"
            + query
            + body
        )

    else:

        prehash = (
            timestamp
            + method_upper
            + path
            + body
        )

    digest = hmac.new(
        API_SECRET.encode(
            "utf-8"
        ),
        prehash.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    signature = base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )

    return (
        timestamp,
        signature,
    )


# ==================================================================================================
# END R35I PART 1 OF 4
# ==================================================================================================
