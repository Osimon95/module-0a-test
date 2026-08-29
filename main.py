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
def auth_headers(
    method: str,
    path: str,
    query: str = "",
    body: str = "",
) -> Dict[str, str]:

    timestamp, signature = sign_weex(
        method,
        path,
        query,
        body,
    )

    return {

        "ACCESS-KEY":
            API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-PASSPHRASE":
            API_PASSPHRASE,

        "ACCESS-TIMESTAMP":
            timestamp,

        "Content-Type":
            "application/json",

        "locale":
            "en-US",

        "User-Agent":
            f"{VERSION}-read-only-validator/1.0",
    }


# ==================================================================================================
# READ-ONLY HTTP TRANSPORT
# ==================================================================================================

def http_get_json(
    path: str,
    params: Optional[
        Dict[str, str]
    ] = None,
    authenticated: bool = False,
) -> Any:

    params = (
        params
        or {}
    )

    query = urllib.parse.urlencode(
        params
    )

    url = (
        BASE_URL
        + path
        + (
            (
                "?"
                + query
            )
            if query
            else ""
        )
    )

    headers: Dict[
        str,
        str,
    ] = {

        "User-Agent":
            f"{VERSION}-read-only-validator/1.0",
    }

    if authenticated:

        if not all(
            credential_status().values()
        ):

            raise RuntimeError(
                "WEEX authenticated read credentials are incomplete"
            )

        headers.update(
            auth_headers(
                "GET",
                path,
                query,
                "",
            )
        )

    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            if (
                response.status < 200
                or response.status >= 300
            ):

                raise RuntimeError(
                    f"HTTP {response.status}: "
                    f"{raw[:300]}"
                )

            return json.loads(
                raw
            )

    except urllib.error.HTTPError as exc:

        body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"HTTP {exc.code}: "
            f"{body[:500]}"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            f"NETWORK ERROR: "
            f"{exc.reason}"
        ) from exc


# ==================================================================================================
# PRIVATE RESPONSE NORMALIZATION
# ==================================================================================================

def extract_usdt_balance(
    payload: Any,
) -> Optional[float]:

    items: List[Any]

    if isinstance(
        payload,
        list,
    ):

        items = payload

    elif isinstance(
        payload,
        dict,
    ):

        data = payload.get(
            "data",
            payload,
        )

        if isinstance(
            data,
            list,
        ):

            items = data

        elif isinstance(
            data,
            dict,
        ):

            items = [
                data
            ]

        else:

            items = []

    else:

        items = []

    for item in items:

        if not isinstance(
            item,
            dict,
        ):

            continue

        asset = str(
            item.get(
                "asset",
                item.get(
                    "coin",
                    "",
                ),
            )
        ).upper()

        if asset == "USDT":

            candidate = item.get(
                "availableBalance",
                item.get(
                    "available",
                    item.get(
                        "balance"
                    ),
                ),
            )

            try:

                return float(
                    candidate
                )

            except (
                TypeError,
                ValueError,
            ):

                return None

    return None


def normalize_list(
    payload: Any,
) -> List[
    Dict[str, Any]
]:

    if isinstance(
        payload,
        list,
    ):

        return [
            item
            for item
            in payload
            if isinstance(
                item,
                dict,
            )
        ]

    if isinstance(
        payload,
        dict,
    ):

        data = payload.get(
            "data",
            payload,
        )

        if isinstance(
            data,
            list,
        ):

            return [
                item
                for item
                in data
                if isinstance(
                    item,
                    dict,
                )
            ]

        if isinstance(
            data,
            dict,
        ):

            return [
                data
            ]

    return []


# ==================================================================================================
# AUTHENTICATED ACCOUNT READS
# ==================================================================================================

def read_authenticated_state(
) -> Dict[str, Any]:

    result: Dict[
        str,
        Any,
    ] = {

        "ok":
            False,

        "balance":
            None,

        "positions":
            [],

        "symbol_config":
            None,

        "errors":
            [],
    }

    # ----------------------------------------------------------------------------------------------
    # BALANCE
    # ----------------------------------------------------------------------------------------------

    try:

        balance_payload = http_get_json(
            BALANCE_PATH,
            authenticated=True,
        )

        balance = extract_usdt_balance(
            balance_payload
        )

        if balance is None:

            raise RuntimeError(
                "USDT available balance was not found in V3 balance response"
            )

        result[
            "balance"
        ] = balance

    except Exception as exc:

        result[
            "errors"
        ].append(
            f"balance: {exc}"
        )

    # ----------------------------------------------------------------------------------------------
    # POSITIONS
    # ----------------------------------------------------------------------------------------------

    try:

        positions_payload = http_get_json(
            POSITIONS_PATH,
            authenticated=True,
        )

        positions = normalize_list(
            positions_payload
        )

        result[
            "positions"
        ] = [

            position

            for position
            in positions

            if str(
                position.get(
                    "symbol",
                    "",
                )
            ).upper()
            == SYMBOL
        ]

    except Exception as exc:

        result[
            "errors"
        ].append(
            f"positions: {exc}"
        )

    # ----------------------------------------------------------------------------------------------
    # SYMBOL CONFIG
    # ----------------------------------------------------------------------------------------------

    try:

        config_payload = http_get_json(
            SYMBOL_CONFIG_PATH,
            {
                "symbol":
                    SYMBOL,
            },
            authenticated=True,
        )

        configs = normalize_list(
            config_payload
        )

        config = next(
            (
                item
                for item
                in configs
                if str(
                    item.get(
                        "symbol",
                        "",
                    )
                ).upper()
                == SYMBOL
            ),
            None,
        )

        if config is None:

            raise RuntimeError(
                f"{SYMBOL} symbol configuration not found"
            )

        result[
            "symbol_config"
        ] = config

    except Exception as exc:

        result[
            "errors"
        ].append(
            f"symbolConfig: {exc}"
        )

    result[
        "ok"
    ] = (

        result[
            "balance"
        ]
        is not None

        and isinstance(
            result[
                "positions"
            ],
            list,
        )

        and isinstance(
            result[
                "symbol_config"
            ],
            dict,
        )

        and not result[
            "errors"
        ]
    )

    return result


# ==================================================================================================
# PUBLIC MARK PRICE
# ==================================================================================================

def read_mark_price(
) -> float:

    payload = http_get_json(
        MARK_PRICE_PATH,
        {
            "symbol":
                SYMBOL,

            "priceType":
                "MARK",
        },
        authenticated=False,
    )

    if isinstance(
        payload,
        dict,
    ):

        data = payload.get(
            "data",
            payload,
        )

        if isinstance(
            data,
            dict,
        ):

            value = data.get(
                "price",
                data.get(
                    "markPrice"
                ),
            )

            if value is not None:

                return float(
                    value
                )

    raise RuntimeError(
        "mark price missing from WEEX response"
    )


# ==================================================================================================
# EXCHANGE RECONCILIATION
# ==================================================================================================

def make_reconciliation(
    account: Dict[str, Any],
    mark_price: float,
) -> Dict[str, Any]:

    body = {

        "version":
            VERSION,

        "symbol":
            SYMBOL,

        "generation":
            STATE.generation,

        "epoch":
            STATE.epoch,

        "read_only":
            True,

        "exchange_network_writes":
            STATE.exchange_network_writes,

        "balance":
            account[
                "balance"
            ],

        "open_positions":
            len(
                account[
                    "positions"
                ]
            ),

        "symbol_config":
            account[
                "symbol_config"
            ],

        "mark_price":
            mark_price,
    }

    rec_hash = sha256_text(
        canonical_json(
            body
        )
    )

    result = dict(
        body
    )

    result[
        "reconciliation_hash"
    ] = rec_hash

    result[
        "reconciliation_id"
    ] = (
        "rec-"
        + rec_hash[:20]
    )

    return result


# ==================================================================================================
# CONTROLLED LIVE ACTIVATION GATE
# ==================================================================================================

def live_gate_can_arm(
    account_ok: bool,
    reconciliation: Optional[
        Dict[str, Any]
    ],
) -> bool:

    return bool(

        account_ok

        and reconciliation

        and reconciliation.get(
            "symbol"
        )
        == SYMBOL

        and reconciliation.get(
            "read_only"
        )
        is True

        and reconciliation.get(
            "exchange_network_writes"
        )
        == 0

        and STATE.exchange_network_writes
        == 0

        and not STATE.kill_switch

        and not STATE.ambiguous_outcome

        and EXCHANGE_WRITER_ENABLED
        is False

        and EXCHANGE_NETWORK_WRITES_ENABLED
        is False

        and REAL_ORDER_EXECUTION
        is False

        and FIRST_REAL_ORDER_ALLOWED
        is False
    )


def arm_live_gate(
    account_ok: bool,
    reconciliation: Optional[
        Dict[str, Any]
    ],
) -> bool:

    allowed = live_gate_can_arm(
        account_ok,
        reconciliation,
    )

    STATE.authenticated_reads_ok = bool(
        account_ok
    )

    STATE.exchange_reconciled = bool(
        reconciliation
        and reconciliation.get(
            "read_only"
        )
        is True
    )

    STATE.live_mode_armed = bool(
        allowed
    )

    STORE.save(
        STATE
    )

    return allowed


# ==================================================================================================
# BOUND ORDER INTENT
# ==================================================================================================

def create_intent(
    mark_price: float,
) -> Dict[str, Any]:

    raw = {

        "version":
            VERSION,

        "symbol":
            SYMBOL,

        "generation":
            STATE.generation,

        "epoch":
            STATE.epoch,

        "side":
            "BUY",

        "positionSide":
            "LONG",

        "type":
            "MARKET",

        "quantity":
            "0.0005",

        "reference_mark_price":
            str(
                mark_price
            ),

        "validation_run_nonce":
            RUN_NONCE,

        "synthetic_only":
            True,

        "transmission_allowed":
            False,

        "exchange_network_write_allowed":
            False,
    }

    intent_hash = sha256_text(
        canonical_json(
            raw
        )
    )

    intent = dict(
        raw
    )

    intent[
        "intent_hash"
    ] = intent_hash

    intent[
        "intent_id"
    ] = (
        "int-"
        + intent_hash[:20]
    )

    return intent


def verify_intent(
    intent: Dict[str, Any],
) -> bool:

    body = {

        key: value

        for key, value
        in intent.items()

        if key
        not in {
            "intent_hash",
            "intent_id",
        }
    }

    expected = sha256_text(
        canonical_json(
            body
        )
    )

    return (

        intent.get(
            "intent_hash"
        )
        == expected

        and intent.get(
            "intent_id"
        )
        == (
            "int-"
            + expected[:20]
        )
    )


# ==================================================================================================
# ONE-TIME AUTHORIZATION
# ==================================================================================================

def create_authorization(
    intent: Dict[str, Any],
) -> Dict[str, Any]:

    raw = {

        "version":
            VERSION,

        "symbol":
            SYMBOL,

        "intent_id":
            intent[
                "intent_id"
            ],

        "intent_hash":
            intent[
                "intent_hash"
            ],

        "generation":
            STATE.generation,

        "epoch":
            STATE.epoch,

        "one_time":
            True,

        "transmission_allowed":
            False,

        "writer_enabled":
            False,
    }

    auth_hash = sha256_text(
        canonical_json(
            raw
        )
    )

    authorization = dict(
        raw
    )

    authorization[
        "authorization_hash"
    ] = auth_hash

    authorization[
        "authorization_id"
    ] = (
        "auth-"
        + auth_hash[:20]
    )

    return authorization


# ==================================================================================================
# IDEMPOTENT CLIENT ORDER ID
# ==================================================================================================

def deterministic_client_order_id(
    intent: Dict[str, Any],
) -> str:

    seed = (
        f"{VERSION}|"
        f"{SYMBOL}|"
        f"{intent['intent_id']}|"
        f"{intent['intent_hash']}"
    )

    return (
        "r35i-"
        + sha256_text(
            seed
        )[:20]
    )


# ==================================================================================================
# NON-TRANSMITTABLE LOCAL WRITER SIGNATURE
# ==================================================================================================

def fake_writer_signature(
    intent: Dict[str, Any],
    authorization: Dict[str, Any],
    client_order_id: str,
) -> str:

    # R35I deliberately does NOT sign an exchange-transmittable
    # order request with the real WEEX API secret.
    #
    # This deterministic local value validates envelope binding only.
    # It is always redacted in report previews.

    seed = canonical_json(
        {

            "intent_hash":
                intent[
                    "intent_hash"
                ],

            "authorization_hash":
                authorization[
                    "authorization_hash"
                ],

            "client_order_id":
                client_order_id,

            "network_writes":
                False,
        }
    )

    digest = hashlib.sha256(
        seed.encode(
            "utf-8"
        )
    ).digest()

    return base64.b64encode(
        digest
    ).decode(
        "ascii"
    )


# ==================================================================================================
# WRITER ENVELOPE
# ==================================================================================================

def create_writer_envelope(
    intent: Dict[str, Any],
    authorization: Dict[str, Any],
    reconciliation: Dict[str, Any],
    client_order_id: str,
) -> Dict[str, Any]:

    payload = {

        "symbol":
            SYMBOL,

        "side":
            "BUY",

        "positionSide":
            "LONG",

        "type":
            "MARKET",

        "quantity":
            intent[
                "quantity"
            ],

        "newClientOrderId":
            client_order_id,
    }

    headers = {

        "ACCESS-KEY":
            (
                API_KEY
                if API_KEY
                else "not-present"
            ),

        "ACCESS-SIGN":
            fake_writer_signature(
                intent,
                authorization,
                client_order_id,
            ),

        "ACCESS-PASSPHRASE":
            (
                API_PASSPHRASE
                if API_PASSPHRASE
                else "not-present"
            ),

        "ACCESS-TIMESTAMP":
            "1760000000000",

        "Content-Type":
            "application/json",

        "locale":
            "en-US",
    }

    raw = {

        "method":
            "POST",

        "request_path":
            ORDER_PATH,

        "url":
            BASE_URL
            + ORDER_PATH,

        "payload":
            payload,

        "headers":
            headers,

        "intent_id":
            intent[
                "intent_id"
            ],

        "intent_hash":
            intent[
                "intent_hash"
            ],

        "authorization_id":
            authorization[
                "authorization_id"
            ],

        "authorization_hash":
            authorization[
                "authorization_hash"
            ],

        "reconciliation_id":
            reconciliation[
                "reconciliation_id"
            ],

        "reconciliation_hash":
            reconciliation[
                "reconciliation_hash"
            ],

        "live_mode_armed":
            STATE.live_mode_armed,

        "exchange_writer_enabled":
            EXCHANGE_WRITER_ENABLED,

        "exchange_network_writes_enabled":
            EXCHANGE_NETWORK_WRITES_ENABLED,

        "real_order_execution":
            REAL_ORDER_EXECUTION,

        "first_real_order_allowed":
            FIRST_REAL_ORDER_ALLOWED,

        "transmitted":
            False,
    }

    env_hash = sha256_text(
        canonical_json(
            raw
        )
    )

    result = dict(
        raw
    )

    result[
        "envelope_hash"
    ] = env_hash

    return result


def redacted_writer_preview(
    envelope: Dict[str, Any],
) -> Dict[str, Any]:

    preview = json.loads(
        json.dumps(
            envelope
        )
    )

    headers = preview.get(
        "headers",
        {},
    )

    for key in (
        "ACCESS-KEY",
        "ACCESS-SIGN",
        "ACCESS-PASSPHRASE",
    ):

        if key in headers:

            headers[
                key
            ] = "<redacted>"

    return preview


# ==================================================================================================
# SYNTHETIC DISPATCH
# ==================================================================================================

def synthetic_dispatch(
    intent: Dict[str, Any],
    authorization: Dict[str, Any],
    envelope: Dict[str, Any],
    client_order_id: str,
) -> Dict[str, Any]:

    if not SYNTHETIC_DISPATCH_ONLY:

        raise RuntimeError(
            "R35I synthetic-only invariant violated"
        )

    if (
        EXCHANGE_WRITER_ENABLED
        or EXCHANGE_NETWORK_WRITES_ENABLED
        or REAL_ORDER_EXECUTION
    ):

        raise RuntimeError(
            "R35I firebreak invariant violated"
        )

    if (
        intent[
            "intent_id"
        ]
        in STATE.consumed_intents
    ):

        raise RuntimeError(
            "intent replay rejected"
        )

    if (
        authorization[
            "authorization_id"
        ]
        in STATE.consumed_authorizations
    ):

        raise RuntimeError(
            "authorization replay rejected"
        )

    if (
        client_order_id
        in STATE.used_client_order_ids
    ):

        raise RuntimeError(
            "client order id replay rejected"
        )

    receipt_body = {

        "version":
            VERSION,

        "symbol":
            SYMBOL,

        "intent_id":
            intent[
                "intent_id"
            ],

        "authorization_id":
            authorization[
                "authorization_id"
            ],

        "client_order_id":
            client_order_id,

        "envelope_hash":
            envelope[
                "envelope_hash"
            ],

        "synthetic":
            True,

        "transmitted":
            False,

        "exchange_network_write":
            False,

        "real_order":
            False,
    }

    receipt_hash = sha256_text(
        canonical_json(
            receipt_body
        )
    )

    receipt = dict(
        receipt_body
    )

    receipt[
        "receipt_hash"
    ] = receipt_hash

    receipt[
        "receipt_id"
    ] = (
        "rcpt-"
        + receipt_hash[:20]
    )

    STATE.consumed_intents.append(
        intent[
            "intent_id"
        ]
    )

    STATE.consumed_authorizations.append(
        authorization[
            "authorization_id"
        ]
    )

    STATE.used_client_order_ids.append(
        client_order_id
    )

    STATE.durable_receipts.append(
        receipt
    )

    STORE.append(
        STATE,
        "SYNTHETIC_DISPATCH",
        receipt,
    )

    return receipt


# ==================================================================================================
# TELEGRAM REPORTING
# ==================================================================================================

def telegram_preview(
    text: str,
) -> Dict[str, Any]:

    return {

        "method":
            "POST",

        "operation":
            "sendMessage",

        "report_only":
            True,

        "exchange_mutation":
            False,

        "execution_control":
            False,

        "bot_token":
            (
                "<redacted>"
                if TELEGRAM_BOT_TOKEN
                else "<not-present>"
            ),

        "chat_id_present":
            bool(
                TELEGRAM_CHAT_ID
            ),

        "text_length":
            len(
                text
            ),
    }


def send_telegram_once(
    text: str,
) -> bool:

    if (
        STATE.telegram_reports_this_run
        >= 1
    ):

        return False

    if (
        not TELEGRAM_ENABLED
        or not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):

        return False

    # Telegram is the ONLY non-GET network call in R35I.
    #
    # It targets api.telegram.org only.
    #
    # It is reporting-only and cannot mutate WEEX,
    # enable the writer, arm execution, or place an order.

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    encoded = urllib.parse.urlencode(
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
        url=url,
        data=encoded,
        method="POST",
        headers={

            "Content-Type":
                "application/x-www-form-urlencoded",

            "User-Agent":
                f"{VERSION}/1.0",
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            response.read()

            if (
                200
                <= response.status
                < 300
            ):

                STATE.telegram_reports_this_run += 1

                return True

    except Exception as exc:

        log(
            f"{VERSION}: "
            f"TELEGRAM DELIVERY NOTICE: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

    return False


# ==================================================================================================
# RUN RESET
# ==================================================================================================

def reset_run_transients(
) -> None:

    # Never erase durable replay protection here.
    #
    # Only reset the validation gate state for this process run.

    STATE.live_mode_armed = False

    STATE.authenticated_reads_ok = False

    STATE.exchange_reconciled = False

    STATE.telegram_reports_this_run = 0

    STORE.save(
        STATE
    )


# ==================================================================================================
# MAIN VALIDATION
# ==================================================================================================

def main(
) -> None:

    global STATE

    start_health_server()

    reset_run_transients()

    failures: List[
        str
    ] = []

    section(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    log(
        f"{VERSION}: SYMBOL={SYMBOL}"
    )

    log(
        f"{VERSION}: VERSION={VERSION}"
    )

    log(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}"
    )

    log(
        f"{VERSION}: STATE DIR={STATE_DIR}"
    )

    log(
        f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: EXCHANGE NETWORK WRITES DISABLED"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION DISABLED"
    )

    log(
        f"{VERSION}: DEMO ORDER EXECUTION DISABLED"
    )


    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    section(
        f"{VERSION} TEST 1: HARD SAFETY CONSTANTS"
    )

    checks = [

        verdict(
            "Synthetic Dispatch Only Is Enabled",
            SYNTHETIC_DISPATCH_ONLY,
        ),

        verdict(
            "Exchange Writer Is Disabled",
            EXCHANGE_WRITER_ENABLED
            is False,
        ),

        verdict(
            "Exchange Network Writes Are Disabled",
            EXCHANGE_NETWORK_WRITES_ENABLED
            is False,
        ),

        verdict(
            "Real Order Execution Is Disabled",
            REAL_ORDER_EXECUTION
            is False,
        ),

        verdict(
            "Demo Order Execution Is Disabled",
            DEMO_ORDER_EXECUTION
            is False,
        ),

        verdict(
            "First Real Order Is Forbidden",
            FIRST_REAL_ORDER_ALLOWED
            is False,
        ),
    ]

    if not all(
        checks
    ):

        failures.append(
            "TEST 1"
        )


    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    section(
        f"{VERSION} TEST 2: CREDENTIAL READINESS"
    )

    creds = credential_status()

    checks = [

        verdict(
            "WEEX API Key Is Present",
            creds[
                "api_key"
            ],
        ),

        verdict(
            "WEEX API Secret Is Present",
            creds[
                "api_secret"
            ],
        ),

        verdict(
            "WEEX API Passphrase Is Present",
            creds[
                "api_passphrase"
            ],
        ),
    ]

    if not all(
        checks
    ):

        failures.append(
            "TEST 2"
        )


    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    section(
        f"{VERSION} TEST 3: AUTHENTICATED WEEX READS"
    )

    if all(
        creds.values()
    ):

        account = read_authenticated_state()

    else:

        account = {

            "ok":
                False,

            "balance":
                None,

            "positions":
                [],

            "symbol_config":
                None,

            "errors":
                [
                    "credentials incomplete"
                ],
        }

    position_read_ok = not any(
        str(
            error
        ).startswith(
            "positions:"
        )
        for error
        in account[
            "errors"
        ]
    )

    checks = [

        verdict(
            "V3 Account Balance Read Succeeded",
            account[
                "balance"
            ]
            is not None,
        ),

        verdict(
            "V3 All Positions Read Succeeded",
            position_read_ok,
        ),

        verdict(
            "V3 Symbol Configuration Read Succeeded",
            isinstance(
                account[
                    "symbol_config"
                ],
                dict,
            ),
        ),

        verdict(
            "Authenticated WEEX Read Set Is Complete",
            bool(
                account[
                    "ok"
                ]
            ),
        ),
    ]

    if account[
        "errors"
    ]:

        for error in account[
            "errors"
        ]:

            log(
                f"{VERSION}: "
                f"AUTH READ ERROR="
                f"{error}"
            )

    if (
        account[
            "balance"
        ]
        is not None
    ):

        log(
            f"{VERSION}: "
            f"AVAILABLE USDT="
            f"{account['balance']}"
        )

    log(
        f"{VERSION}: "
        f"OPEN {SYMBOL} POSITIONS="
        f"{len(account['positions'])}"
    )

    if not all(
        checks
    ):

        failures.append(
            "TEST 3"
        )


    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    section(
        f"{VERSION} TEST 4: PUBLIC MARK PRICE"
    )

    mark_price: Optional[
        float
    ] = None

    try:

        mark_price = read_mark_price()

        mark_ok = (
            mark_price
            > 0
        )

    except Exception as exc:

        log(
            f"{VERSION}: "
            f"MARK PRICE ERROR="
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        mark_ok = False

    if not verdict(
        f"{SYMBOL} Mark Price Was Read",
        mark_ok,
    ):

        failures.append(
            "TEST 4"
        )

    if (
        mark_price
        is not None
    ):

        log(
            f"{VERSION}: "
            f"MARK PRICE="
            f"{mark_price}"
        )


    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    section(
        f"{VERSION} TEST 5: EXCHANGE STATE RECONCILIATION"
    )

    reconciliation: Optional[
        Dict[str, Any]
    ] = None

    if (
        account[
            "ok"
        ]
        and mark_price
        is not None
    ):

        reconciliation = make_reconciliation(
            account,
            mark_price,
        )

    checks = [

        verdict(
            "Exchange Reconciliation Was Created",
            reconciliation
            is not None,
        ),

        verdict(
            f"Exchange Reconciliation Is Bound To {SYMBOL}",
            bool(
                reconciliation
                and reconciliation.get(
                    "symbol"
                )
                == SYMBOL
            ),
        ),

        verdict(
            "Reconciliation Is Read Only",
            bool(
                reconciliation
                and reconciliation.get(
                    "read_only"
                )
                is True
            ),
        ),

        verdict(
            "Reconciliation Exchange Write Count Is Zero",
            bool(
                reconciliation
                and reconciliation.get(
                    "exchange_network_writes"
                )
                == 0
            ),
        ),
    ]

    if not all(
        checks
    ):

        failures.append(
            "TEST 5"
        )


    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    section(
        f"{VERSION} TEST 6: CONTROLLED LIVE ACTIVATION GATE"
    )

    gate_armed = arm_live_gate(
        bool(
            account[
                "ok"
            ]
        ),
        reconciliation,
    )

    checks = [

        verdict(
            "Live Gate Arming Validation Succeeded",
            gate_armed,
        ),

        verdict(
            "Live Gate Does Not Enable Exchange Writer",
            EXCHANGE_WRITER_ENABLED
            is False,
        ),

        verdict(
            "Live Gate Does Not Enable Exchange Writes",
            EXCHANGE_NETWORK_WRITES_ENABLED
            is False,
        ),

        verdict(
            "Live Gate Does Not Enable Real Orders",
            REAL_ORDER_EXECUTION
            is False,
        ),

        verdict(
            "First Real Order Remains Forbidden",
            FIRST_REAL_ORDER_ALLOWED
            is False,
        ),
    ]

    if not all(
        checks
    ):

        failures.append(
            "TEST 6"
        )


    # ==============================================================================================
    # LOCAL FIREBREAK INPUT
    # ==============================================================================================

    # Tests 7-17 remain strictly synthetic.
    #
    # If authenticated reads fail, the local reconciliation below is used
    # ONLY to exercise the non-transmittable firebreak path.
    #
    # It does NOT cause TEST 5 or TEST 6 to pass.

    effective_mark = (
        mark_price
        if mark_price
        is not None
        else 0.0
    )

    local_rec = (
        reconciliation
        or {

            "reconciliation_id":
                "rec-unavailable",

            "reconciliation_hash":
                sha256_text(
                    "unavailable"
                ),

            "symbol":
                SYMBOL,

            "read_only":
                True,

            "exchange_network_writes":
                0,
        }
    )


    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    section(
        f"{VERSION} TEST 7: BOUND ORDER INTENT"
    )

    intent = create_intent(
        effective_mark
    )

    checks = [

        verdict(
            "Intent Was Created",
            bool(
                intent
            ),
        ),

        verdict(
            f"Intent Is Bound To {SYMBOL}",
            intent.get(
                "symbol"
            )
            == SYMBOL,
        ),

        verdict(
            "Intent Is Synthetic Only",
            intent.get(
                "synthetic_only"
            )
            is True,
        ),

        verdict(
            "Intent Forbids Transmission",
            intent.get(
                "transmission_allowed"
            )
            is False,
        ),

        verdict(
            "Intent Forbids Exchange Network Write",
            intent.get(
                "exchange_network_write_allowed"
            )
            is False,
        ),
    ]

    if not all(
        checks
    ):

        failures.append(
            "TEST 7"
        )


    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    section(
        f"{VERSION} TEST 8: INTENT INTEGRITY BINDING"
    )

    intent_valid = verify_intent(
        intent
    )

    checks = [

        verdict(
            "Intent Hash Is Valid",
            intent_valid,
        ),

        verdict(
            "Intent ID Is Bound To Intent Hash",
            intent[
                "intent_id"
            ]
            == (
                "int-"
                + intent[
                    "intent_hash"
                ][:20]
            ),
        ),
    ]

    if not all(
        checks
    ):

        failures.append(
            "TEST 8"
        )


    # ==============================================================================================
    # TEST 9
    # ==============================================================================================

    section(
        f"{VERSION} TEST 9: ONE-TIME AUTHORIZATION"
    )

    authorization = create_authorization(
        intent
    )

    checks = [

        verdict(
            "Authorization Was Created",
            bool(
                authorization
            ),
        ),

        verdict(
            "Authorization Is Bound To Intent",
            authorization[
                "intent_hash"
            ]
            == intent[
                "intent_hash"
            ],
        ),

        verdict(
            "Authorization Is One-Time",
            authorization.get(
                "one_time"
            )
            is True,
        ),

        verdict(
            "Authorization Does Not Permit Transmission",
            authorization.get(
                "transmission_allowed"
            )
            is False,
        ),

        verdict(
            "Authorization Does Not Enable Writer",
            authorization.get(
                "writer_enabled"
            )
            is False,
        ),
    ]

    if not all(
        checks
    ):

        failures.append(
            "TEST 9"
        )


    # ==============================================================================================
    # TEST 10
    # ==============================================================================================

    section(
        f"{VERSION} TEST 10: IDEMPOTENT CLIENT ORDER ID"
    )

    client_order_id = deterministic_client_order_id(
        intent
    )

    client_order_id_again = deterministic_client_order_id(
        intent
    )

    not_used_before = (
        client_order_id
        not in STATE.used_client_order_ids
    )

    checks = [

        verdict(
            "Client Order ID Is Deterministic",
            client_order_id
            == client_order_id_again,
        ),

        verdict(
            "Client Order ID Uses R35I Prefix",
            client_order_id.startswith(
                "r35i-"
            ),
        ),

        verdict(
            "Client Order ID Has Not Yet Been Consumed",
            not_used_before,
        ),
    ]

    log(
        f"{VERSION}: "
        f"CLIENT ORDER ID="
        f"{client_order_id}"
    )

    if not all(
        checks
    ):

        failures.append(
            "TEST 10"
        )

    # Preserve replay protection across repeated R35I validation runs.
    #
    # If this exact deterministic validation ID was already consumed,
    # advance the local validation epoch and create a fresh intent.

    if not not_used_before:

        STATE.epoch += 1

        STORE.append(
            STATE,
            "VALIDATION_EPOCH_ADVANCE",
            {

                "reason":
                    "prior synthetic validation consumed deterministic id",

                "epoch":
                    STATE.epoch,
            },
        )

        intent = create_intent(
            effective_mark
        )

        authorization = create_authorization(
            intent
        )

        client_order_id = deterministic_client_order_id(
            intent
        )


    # ==============================================================================================
    # TEST 11
    # ==============================================================================================

    section(
        f"{VERSION} TEST 11: SECRET-SAFE WRITER ENVELOPE"
    )

    envelope = create_writer_envelope(
        intent,
        authorization,
        local_rec,
        client_order_id,
    )

    preview = redacted_writer_preview(
        envelope
    )

    checks = [

        verdict(
            "Writer Envelope Uses POST",
            envelope.get(
                "method"
            )
            == "POST",
        ),

        verdict(
            "Writer Envelope Uses Exact V3 Order Path",
            envelope.get(
                "request_path"
            )
            == ORDER_PATH,
        ),

        verdict(
            "Writer Envelope Is Bound To Intent",
            envelope.get(
                "intent_hash"
            )
            == intent[
                "intent_hash"
            ],
        ),

        verdict(
            "Writer Envelope Is Bound To Authorization",
            envelope.get(
                "authorization_hash"
            )
            == authorization[
                "authorization_hash"
            ],
        ),

        verdict(
            "Writer Envelope Is Bound To Reconciliation",
            envelope.get(
                "reconciliation_hash"
            )
            == local_rec[
                "reconciliation_hash"
            ],
        ),

        verdict(
            "Writer Envelope Marks Transmitted False",
            envelope.get(
                "transmitted"
            )
            is False,
        ),

        verdict(
            "Writer Preview Redacts Access Key",
            preview[
                "headers"
            ].get(
                "ACCESS-KEY"
            )
            == "<redacted>",
        ),

        verdict(
            "Writer Preview Redacts Signature",
            preview[
                "headers"
            ].get(
                "ACCESS-SIGN"
            )
            == "<redacted>",
        ),

        verdict(
            "Writer Preview Redacts Passphrase",
            preview[
                "headers"
            ].get(
                "ACCESS-PASSPHRASE"
            )
            == "<redacted>",
        ),
    ]

    log(
        f"{VERSION}: "
        f"WRITER PREVIEW="
        f"{canonical_json(preview)}"
    )

    if not all(
        checks
    ):

        failures.append(
            "TEST 11"
        )


    # ==============================================================================================
    # TEST 12
    # ==============================================================================================

    section(
        f"{VERSION} TEST 12: EXCHANGE NETWORK FIREBREAK"
    )

    checks = [

        verdict(
            "Exchange Writer Is Still Disabled",
            EXCHANGE_WRITER_ENABLED
            is False,
        ),

        verdict(
            "Exchange Network Writes Are Still Disabled",
            EXCHANGE_NETWORK_WRITES_ENABLED
            is False,
        ),

        verdict(
            "Real Order Execution Is Still Disabled",
            REAL_ORDER_EXECUTION
            is False,
        ),

        verdict(
            "First Real Order Is Still Forbidden",
            FIRST_REAL_ORDER_ALLOWED
            is False,
        ),

        verdict(
            "Envelope Was Not Transmitted",
            envelope.get(
                "transmitted"
            )
            is False,
        ),
    ]

    if not all(
        checks
    ):

        failures.append(
            "TEST 12"
        )


    # ==============================================================================================
    # TEST 13
    # ==============================================================================================

    section(
        f"{VERSION} TEST 13: SYNTHETIC DISPATCH"
    )

    receipt: Optional[
        Dict[str, Any]
    ] = None

    try:

        receipt = synthetic_dispatch(
            intent,
            authorization,
            envelope,
            client_order_id,
        )

        dispatch_ok = True

    except Exception as exc:

        log(
            f"{VERSION}: "
            f"SYNTHETIC DISPATCH ERROR="
            f"{exc}"
        )

        dispatch_ok = False

    checks = [

        verdict(
            "Synthetic Dispatch Produced Receipt",
            dispatch_ok
            and receipt
            is not None,
        ),

        verdict(
            "Synthetic Receipt Marks Transmitted False",
            bool(
                receipt
                and receipt.get(
                    "transmitted"
                )
                is False
            ),
        ),

        verdict(
            "Synthetic Receipt Marks Exchange Write False",
            bool(
                receipt
                and receipt.get(
                    "exchange_network_write"
                )
                is False
            ),
        ),

        verdict(
            "Synthetic Receipt Marks Real Order False",
            bool(
                receipt
                and receipt.get(
                    "real_order"
                )
                is False
            ),
        ),

        verdict(
            "Synthetic Dispatch Makes No Exchange Network Write",
            STATE.exchange_network_writes
            == 0,
        ),
    ]

    if not all(
        checks
    ):

        failures.append(
            "TEST 13"
        )


    # ==============================================================================================
    # TEST 14
    # ==============================================================================================

    section(
        f"{VERSION} TEST 14: INTENT REPLAY PROTECTION"
    )

    replay_rejected = False

    try:

        synthetic_dispatch(
            intent,
            authorization,
            envelope,
            client_order_id,
        )

    except Exception:

        replay_rejected = True

    if not verdict(
        "Consumed Intent Replay Is Rejected",
        replay_rejected,
    ):

        failures.append(
            "TEST 14"
        )


    # ==============================================================================================
    # TEST 15
    # ==============================================================================================

    section(
        f"{VERSION} TEST 15: AUTHORIZATION REPLAY PROTECTION"
    )

    if not verdict(
        "Authorization Is Persistently Consumed",
        authorization[
            "authorization_id"
        ]
        in STATE.consumed_authorizations,
    ):

        failures.append(
            "TEST 15"
        )


    # ==============================================================================================
    # TEST 16
    # ==============================================================================================

    section(
        f"{VERSION} TEST 16: CLIENT ORDER ID REPLAY PROTECTION"
    )

    if not verdict(
        "Client Order ID Is Persistently Used",
        client_order_id
        in STATE.used_client_order_ids,
    ):

        failures.append(
            "TEST 16"
        )


    # ==============================================================================================
    # TEST 17
    # ==============================================================================================

    section(
        f"{VERSION} TEST 17: DURABLE RECEIPT"
    )

    durable_receipt_ok = bool(

        receipt

        and any(
            existing.get(
                "receipt_id"
            )
            == receipt.get(
                "receipt_id"
            )
            for existing
            in STATE.durable_receipts
        )
    )

    if not verdict(
        "Durable Receipt Exists",
        durable_receipt_ok,
    ):

        failures.append(
            "TEST 17"
        )


    # ==============================================================================================
    # TEST 18
    # ==============================================================================================

    section(
        f"{VERSION} TEST 18: KILL SWITCH BOUNDARY"
    )

    old_kill = (
        STATE.kill_switch
    )

    STATE.kill_switch = True

    kill_rejects = not live_gate_can_arm(
        bool(
            account[
                "ok"
            ]
        ),
        reconciliation,
    )

    STATE.kill_switch = (
        old_kill
    )

    checks = [

        verdict(
            "Kill Switch Rejects Live Gate Arming",
            kill_rejects,
        ),

        verdict(
            "Kill Switch Makes No Exchange Write",
            STATE.exchange_network_writes
            == 0,
        ),
    ]

    if not all(
        checks
    ):

        failures.append(
            "TEST 18"
        )


    # ==============================================================================================
    # TEST 19
    # ==============================================================================================

    section(
        f"{VERSION} TEST 19: AMBIGUOUS OUTCOME BLOCK"
    )

    old_ambiguous = (
        STATE.ambiguous_outcome
    )

    STATE.ambiguous_outcome = True

    ambiguous_rejects = not live_gate_can_arm(
        bool(
            account[
                "ok"
            ]
        ),
        reconciliation,
    )

    STATE.ambiguous_outcome = (
        old_ambiguous
    )

    if not verdict(
        "Ambiguous Outcome Blocks Live Gate",
        ambiguous_rejects,
    ):

        failures.append(
            "TEST 19"
        )


    # ==============================================================================================
    # TEST 20
    # ==============================================================================================

    section(
        f"{VERSION} TEST 20: DURABLE RESTART PROTECTION"
    )

    STORE.save(
        STATE
    )

    restarted = STORE.load()

    checks = [

        verdict(
            "Live Activation Gate State Survives Restart",
            restarted.live_mode_armed
            == STATE.live_mode_armed,
        ),

        verdict(
            "Consumed Intent Survives Restart",
            intent[
                "intent_id"
            ]
            in restarted.consumed_intents,
        ),

        verdict(
            "Consumed Authorization Survives Restart",
            authorization[
                "authorization_id"
            ]
            in restarted.consumed_authorizations,
        ),

        verdict(
            "Used Client Order ID Survives Restart",
            client_order_id
            in restarted.used_client_order_ids,
        ),

        verdict(
            "Durable Receipt Survives Restart",
            bool(
                receipt
                and any(
                    existing.get(
                        "receipt_id"
                    )
                    == receipt.get(
                        "receipt_id"
                    )
                    for existing
                    in restarted.durable_receipts
                )
            ),
        ),

        verdict(
            "Restart Keeps Exchange Write Count At Zero",
            restarted.exchange_network_writes
            == 0,
        ),
    ]

    if not all(
        checks
    ):

        failures.append(
            "TEST 20"
        )

    STATE = restarted


# ==================================================================================================
# END R35I PART 3 OF 4
# ==================================================================================================
    # ==============================================================================================
    # TEST 21
    # ==============================================================================================

    section(
        f"{VERSION} TEST 21: TELEGRAM REPORTING BOUNDARY"
    )

    tg_probe = telegram_preview(
        "R35I validation report"
    )

    checks = [

        verdict(
            "Telegram Uses POST Only For Reporting",
            tg_probe.get(
                "method"
            )
            == "POST",
        ),

        verdict(
            "Telegram Operation Is sendMessage",
            tg_probe.get(
                "operation"
            )
            == "sendMessage",
        ),

        verdict(
            "Telegram Request Is Report Only",
            tg_probe.get(
                "report_only"
            )
            is True,
        ),

        verdict(
            "Telegram Request Is Not Exchange Mutation",
            tg_probe.get(
                "exchange_mutation"
            )
            is False,
        ),

        verdict(
            "Telegram Cannot Control Execution",
            tg_probe.get(
                "execution_control"
            )
            is False,
        ),

        verdict(
            "Telegram Preview Does Not Expose Bot Token",
            tg_probe.get(
                "bot_token"
            )
            in {
                "<redacted>",
                "<not-present>",
            },
        ),
    ]

    if not all(
        checks
    ):

        failures.append(
            "TEST 21"
        )


    # ==============================================================================================
    # TEST 22
    # ==============================================================================================

    section(
        f"{VERSION} TEST 22: FINAL TELEGRAM DELIVERY READINESS"
    )

    tg_ready = (

        TELEGRAM_ENABLED

        and bool(
            TELEGRAM_BOT_TOKEN
        )

        and bool(
            TELEGRAM_CHAT_ID
        )
    )

    checks = [

        verdict(
            "Telegram Reporting Is Enabled",
            TELEGRAM_ENABLED,
        ),

        verdict(
            "Telegram Bot Token Is Present",
            bool(
                TELEGRAM_BOT_TOKEN
            ),
        ),

        verdict(
            "Telegram Chat ID Is Present",
            bool(
                TELEGRAM_CHAT_ID
            ),
        ),

        verdict(
            "Telegram Delivery Is Deferred Until Final Verification",
            STATE.telegram_reports_this_run
            == 0,
        ),
    ]

    if not all(
        checks
    ):

        # Telegram configuration is reporting readiness only.
        #
        # It never grants order permission and never enables
        # the WEEX writer.

        failures.append(
            "TEST 22"
        )


    # ==============================================================================================
    # TEST 23
    # ==============================================================================================

    section(
        f"{VERSION} TEST 23: JOURNAL INTEGRITY"
    )

    STORE.append(
        STATE,
        "VALIDATION_CHECKPOINT",
        {

            "authenticated_reads_ok":
                bool(
                    account[
                        "ok"
                    ]
                ),

            "live_mode_armed":
                STATE.live_mode_armed,

            "exchange_network_writes":
                STATE.exchange_network_writes,
        },
    )

    journal_ok, journal_count = STORE.verify_journal()

    checks = [

        verdict(
            "Durable Journal Contains Records",
            journal_count
            > 0,
        ),

        verdict(
            "Durable Journal Hash Chain Is Valid",
            journal_ok,
        ),

        verdict(
            "Journal Sequence Is Monotonic",
            STATE.journal_sequence
            >= journal_count,
        ),
    ]

    if not all(
        checks
    ):

        failures.append(
            "TEST 23"
        )


    # ==============================================================================================
    # FINAL VALIDATION STATE
    # ==============================================================================================

    validation_passed = (
        len(
            failures
        )
        == 0
    )

    report_lines = [

        (
            f"✅ {VERSION} VALIDATION REPORT"
            if validation_passed
            else f"❌ {VERSION} VALIDATION REPORT"
        ),

        "",

        f"Symbol: {SYMBOL}",

        (
            "Authenticated WEEX reads: PASS"
            if account[
                "ok"
            ]
            else "Authenticated WEEX reads: FAIL"
        ),

        (
            f"Balance: {account['balance']}"
            if account[
                "balance"
            ]
            is not None
            else "Balance: unavailable"
        ),

        (
            f"Mark price: {mark_price}"
            if mark_price
            is not None
            else "Mark price: unavailable"
        ),

        (
            f"Open positions: {len(account['positions'])}"
            if account[
                "ok"
            ]
            else "Open positions: unverified"
        ),

        (
            "Journal integrity: PASS"
            if journal_ok
            else "Journal integrity: FAIL"
        ),

        f"Journal sequence: {STATE.journal_sequence}",

        f"Exchange network writes: {STATE.exchange_network_writes}",

        "Real order execution: DISABLED",

        "Demo order execution: DISABLED",

        "First real order: FORBIDDEN",

        "Telegram reports this run: 1 maximum",

        (
            "Status: VALIDATION PASSED"
            if validation_passed
            else "Status: VALIDATION FAILED"
        ),
    ]

    if failures:

        report_lines.append(
            "Failed tests: "
            + ", ".join(
                failures
            )
        )

    report = "\n".join(
        report_lines
    )


    # ==============================================================================================
    # FINAL CONSOLE REPORT
    # ==============================================================================================

    section(
        f"{VERSION}: VALIDATION SUMMARY"
    )

    for line in report_lines:

        log(
            line
        )


    # ==============================================================================================
    # SINGLE FINAL TELEGRAM REPORT
    # ==============================================================================================
    #
    # Telegram is intentionally deferred until every validation test
    # has finished.
    #
    # Maximum:
    #
    #     ONE Telegram sendMessage POST per process run.
    #
    # This POST is directed only to api.telegram.org.
    #
    # It cannot:
    #
    #     - enable WEEX writes
    #     - arm order execution
    #     - modify exchange state
    #     - send an order
    #     - change leverage
    #     - change margin mode
    #     - modify a position
    #
    # ==============================================================================================

    if tg_ready:

        delivered = send_telegram_once(
            report
        )

        log(
            f"{VERSION}: "
            f"TELEGRAM FINAL REPORT="
            f"{'DELIVERED' if delivered else 'NOT DELIVERED'}"
        )

    else:

        log(
            f"{VERSION}: "
            f"TELEGRAM FINAL REPORT="
            f"NOT CONFIGURED"
        )


    # ==============================================================================================
    # FINAL DURABLE STATE SAVE
    # ==============================================================================================

    STORE.save(
        STATE
    )

    log(
        LINE
    )


# ==================================================================================================
# PROGRAM ENTRY
# ==================================================================================================

if __name__ == "__main__":

    main()
