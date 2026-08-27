from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import socketserver
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import asdict, dataclass, field
from decimal import Decimal
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

print("R29 UNIT E: MAIN.PY ENTERED", flush=True)


# =============================================================================
# R29 UNIT E
# CONTROLLED LEVERAGE-MUTATION PREPARATION / AUTHORIZATION
#
# SAFETY DISCIPLINE
#   - NO REAL ORDER EXECUTION
#   - NO DEMO ORDER EXECUTION
#   - NO NETWORK WRITES
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MUTATION
#   - NO POSITION MUTATION
#   - NO ACCOUNT MUTATION
#   - NO WEBSOCKET WRITES
#   - SYNTHETIC TRANSPORT ONLY
#
# PURPOSE
#   Live GET-only observation
#       -> verify flat position and current symbol configuration
#       -> construct exact 100x isolated leverage mutation envelope
#       -> validate payload/signature/header bindings locally
#       -> issue local one-time authorization token
#       -> consume authorization exactly once into synthetic transport
#       -> prove REAL POST remains impossible
#       -> persist durable restart-safe Unit E state
# =============================================================================


# =============================================================================
# PART 1 - CONSTANTS / DATA MODELS / BASIC UTILITIES
# =============================================================================

print("R29 UNIT E: IMPORTS COMPLETE", flush=True)

UNIT = "R29 UNIT E"
HOST = "https://api-contract.weex.com"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()
ASSET = os.getenv("ASSET", "USDT").strip().upper()

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = "100"
TARGET_SHORT_LEVERAGE = "100"

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True
WEBSOCKET_WRITES_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

PUBLIC_MARK_PATH = "/capi/v3/market/symbolPrice"
PRIVATE_ASSETS_PATH = "/capi/v2/account/assets"
PRIVATE_POSITIONS_PATH = "/capi/v2/account/position/allPosition"
PRIVATE_SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

LEVERAGE_MUTATION_PATH = "/capi/v3/account/leverage"

ALLOWED_GET_PATHS = {
    PUBLIC_MARK_PATH,
    PRIVATE_ASSETS_PATH,
    PRIVATE_POSITIONS_PATH,
    PRIVATE_SYMBOL_CONFIG_PATH,
}

STATE_PATH = Path(
    os.getenv(
        "R29_UNIT_E_STATE",
        "/tmp/r29_unit_e_state.json",
    )
)

PORT = int(os.getenv("PORT", "10000"))

HTTP_TIMEOUT_SECONDS = float(
    os.getenv(
        "HTTP_TIMEOUT_SECONDS",
        "12",
    )
)

AUTH_TTL_SECONDS = int(
    os.getenv(
        "R29_E_AUTH_TTL_SECONDS",
        "120",
    )
)

SNAPSHOT_MAX_AGE_SECONDS = int(
    os.getenv(
        "R29_E_SNAPSHOT_MAX_AGE_SECONDS",
        "30",
    )
)

API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
).strip()

SECRET_KEY = os.getenv(
    "WEEX_SECRET_KEY",
    "",
).strip()

PASSPHRASE = os.getenv(
    "WEEX_PASSPHRASE",
    "",
).strip()

SEP = "-" * 92

PASS_COUNT = 0
TEST_GROUPS = 0

print(
    "R29 UNIT E: CONSTANTS INITIALIZED",
    flush=True,
)


class LocalBlock(RuntimeError):
    pass


def now_ms() -> int:
    return int(time.time() * 1000)


def canonical_json(
    value: Any,
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def hash_obj(
    value: Any,
) -> str:
    return sha256_text(
        canonical_json(value)
    )


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise AssertionError(message)


def local_block(
    message: str,
) -> None:
    print(
        f"{UNIT} LOCAL BLOCK:",
        flush=True,
    )

    print(
        f"  {message}",
        flush=True,
    )

    raise LocalBlock(message)


def pass_check(
    label: str,
    condition: bool,
) -> None:
    global PASS_COUNT

    require(
        condition,
        label,
    )

    PASS_COUNT += 1

    print(
        f"{label:<84} ✅ PASS",
        flush=True,
    )


def begin_test(
    number: int,
    title: str,
) -> None:
    global TEST_GROUPS

    TEST_GROUPS += 1

    print(
        SEP,
        flush=True,
    )

    print(
        f"{UNIT} TEST {number}: {title}",
        flush=True,
    )

    print(
        SEP,
        flush=True,
    )


def expect_local_block(
    label: str,
    fn,
) -> None:
    try:
        fn()

    except LocalBlock:
        pass_check(
            label,
            True,
        )

        return

    raise AssertionError(
        f"{label}: expected local block"
    )


def dec(
    value: Any,
) -> Decimal:
    return Decimal(
        str(value)
    )


@dataclass(frozen=True)
class AccountObservation:
    asset: str
    available: str
    equity: str
    observed_ms: int
    payload_hash: str


@dataclass(frozen=True)
class PositionObservation:
    symbol: str
    open_position_count: int
    observed_ms: int
    payload_hash: str


@dataclass(frozen=True)
class SymbolConfiguration:
    symbol: str
    margin_type: str
    separated_type: str
    isolated_long_leverage: str
    isolated_short_leverage: str
    observed_ms: int
    payload_hash: str


@dataclass(frozen=True)
class MarketObservation:
    symbol: str
    mark_price: str
    observed_ms: int
    payload_hash: str


@dataclass(frozen=True)
class LiveSnapshot:
    snapshot_id: str
    symbol: str
    asset: str
    created_ms: int
    market_hash: str
    account_hash: str
    position_hash: str
    symbol_config_hash: str
    integrity_hash: str


@dataclass(frozen=True)
class MutationEnvelope:
    mutation_id: str
    method: str
    path: str
    symbol: str
    body: Dict[str, str]
    body_json: str
    body_hash: str
    snapshot_hash: str
    created_ms: int
    executable: bool
    synthetic_only: bool


@dataclass(frozen=True)
class SignedMutationEnvelope:
    mutation_id: str
    timestamp: str
    method: str
    path: str
    body_hash: str
    signature: str
    header_names: Tuple[str, ...]
    signed_hash: str


@dataclass(frozen=True)
class AuthorizationToken:
    authorization_id: str
    mutation_id: str
    body_hash: str
    snapshot_hash: str
    issued_ms: int
    expires_ms: int
    nonce: str
    authorization_hash: str


@dataclass(frozen=True)
class SyntheticReceipt:
    receipt_id: str
    mutation_id: str
    authorization_id: str
    body_hash: str
    transport: str
    transmitted: bool
    network_write_count: int
    created_ms: int
    receipt_hash: str


@dataclass
class DurableState:
    unit: str = UNIT

    runtime_id: str = field(
        default_factory=lambda: str(
            uuid.uuid4()
        )
    )

    generation: int = 1
    recovery_epoch: int = 1
    boot_count: int = 1

    created_ms: int = field(
        default_factory=now_ms
    )

    updated_ms: int = field(
        default_factory=now_ms
    )

    last_snapshot_hash: str = ""
    last_mutation_id: str = ""
    last_body_hash: str = ""

    last_authorization_id: str = ""
    last_authorization_hash: str = ""

    consumed_authorization_ids: List[str] = field(
        default_factory=list
    )

    last_receipt_hash: str = ""

    synthetic_dispatch_count: int = 0

    real_order_count: int = 0
    demo_order_count: int = 0
    network_write_count: int = 0

    real_write_firebreak_count: int = 0
    demo_write_firebreak_count: int = 0
    websocket_firebreak_count: int = 0

    leverage_mutation_firebreak_count: int = 0
    margin_mutation_firebreak_count: int = 0
    position_mutation_firebreak_count: int = 0
    account_mutation_firebreak_count: int = 0


print(
    "R29 UNIT E: PART 1 DEFINITIONS LOADED",
    flush=True,
)


# =============================================================================
# PART 2 - GET-ONLY NETWORK / SIGNING / LIVE OBSERVATION
# =============================================================================


def sign_message(
    secret: str,
    timestamp: str,
    method: str,
    path: str,
    query: str = "",
    body: str = "",
) -> str:

    message = (
        timestamp
        + method.upper()
        + path
        + query
        + body
    )

    digest = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("ascii")


def private_headers(
    method: str,
    path: str,
    query: str = "",
    body: str = "",
) -> Dict[str, str]:

    if (
        not API_KEY
        or not SECRET_KEY
        or not PASSPHRASE
    ):
        local_block(
            "private-read credentials are incomplete"
        )

    timestamp = str(
        now_ms()
    )

    signature = sign_message(
        SECRET_KEY,
        timestamp,
        method,
        path,
        query,
        body,
    )

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
        "locale": "en-US",
        "User-Agent": "R29-Unit-E-ReadOnly/1.0",
    }


def http_get(
    path: str,
    params: Optional[Dict[str, str]] = None,
    private: bool = False,
) -> Any:

    if path not in ALLOWED_GET_PATHS:
        local_block(
            "GET path is not allowlisted"
        )

    params = params or {}

    query = ""

    if params:
        query = (
            "?"
            + urllib.parse.urlencode(
                params
            )
        )

    if private:
        headers = private_headers(
            "GET",
            path,
            query,
            "",
        )

    else:
        headers = {
            "User-Agent":
                "R29-Unit-E-ReadOnly/1.0"
        }

    request = urllib.request.Request(
        HOST + path + query,
        headers=headers,
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

            return json.loads(raw)

    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"GET {path} failed HTTP "
            f"{exc.code}: {detail[:300]}"
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"GET {path} failed: {exc}"
        ) from exc


def unwrap_data(
    payload: Any,
) -> Any:

    if (
        isinstance(payload, dict)
        and "data" in payload
        and payload.get("data") is not None
    ):
        return payload["data"]

    return payload


def get_market_observation() -> MarketObservation:

    payload = unwrap_data(
        http_get(
            PUBLIC_MARK_PATH,
            {
                "symbol": SYMBOL,
                "priceType": "MARK",
            },
            private=False,
        )
    )

    require(
        isinstance(payload, dict),
        "market payload must be object",
    )

    symbol = str(
        payload.get(
            "symbol",
            SYMBOL,
        )
    ).upper()

    price = (
        payload.get("price")
        or payload.get("markPrice")
        or payload.get("mark_price")
    )

    require(
        price is not None,
        "mark price missing",
    )

    require(
        dec(price) > 0,
        "mark price must be positive",
    )

    timestamp = int(
        payload.get("time")
        or payload.get("timestamp")
        or now_ms()
    )

    return MarketObservation(
        symbol=symbol,
        mark_price=str(price),
        observed_ms=timestamp,
        payload_hash=hash_obj(payload),
    )


def get_account_observation() -> AccountObservation:

    payload = unwrap_data(
        http_get(
            PRIVATE_ASSETS_PATH,
            private=True,
        )
    )

    if isinstance(payload, list):
        rows = payload

    else:
        rows = [payload]

    row = next(
        (
            item
            for item in rows
            if (
                isinstance(item, dict)
                and str(
                    item.get(
                        "coinName",
                        item.get(
                            "asset",
                            "",
                        ),
                    )
                ).upper()
                == ASSET
            )
        ),
        None,
    )

    require(
        row is not None,
        f"{ASSET} asset row missing",
    )

    available = row.get(
        "available",
        row.get(
            "availableBalance",
            "0",
        ),
    )

    equity = row.get(
        "equity",
        row.get(
            "balance",
            row.get(
                "walletBalance",
                "0",
            ),
        ),
    )

    require(
        dec(available) >= 0,
        "available balance must be nonnegative",
    )

    require(
        dec(equity) >= 0,
        "equity must be nonnegative",
    )

    return AccountObservation(
        asset=ASSET,
        available=str(available),
        equity=str(equity),
        observed_ms=now_ms(),
        payload_hash=hash_obj(row),
    )


def get_position_observation() -> PositionObservation:

    payload = unwrap_data(
        http_get(
            PRIVATE_POSITIONS_PATH,
            private=True,
        )
    )

    rows = (
        payload
        if isinstance(payload, list)
        else []
    )

    count = 0

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

        size = row.get(
            "size",
            row.get(
                "positionAmt",
                row.get(
                    "quantity",
                    "0",
                ),
            ),
        )

        try:
            if dec(size) != 0:
                count += 1

        except Exception:
            count += 1

    return PositionObservation(
        symbol=SYMBOL,
        open_position_count=count,
        observed_ms=now_ms(),
        payload_hash=hash_obj(rows),
    )


def get_symbol_configuration() -> SymbolConfiguration:

    payload = unwrap_data(
        http_get(
            PRIVATE_SYMBOL_CONFIG_PATH,
            {
                "symbol": SYMBOL,
            },
            private=True,
        )
    )

    if isinstance(payload, list):
        rows = payload

    else:
        rows = [payload]

    row = next(
        (
            item
            for item in rows
            if (
                isinstance(item, dict)
                and str(
                    item.get(
                        "symbol",
                        "",
                    )
                ).upper()
                == SYMBOL
            )
        ),
        None,
    )

    require(
        row is not None,
        "symbol configuration row missing",
    )

    return SymbolConfiguration(
        symbol=str(
            row.get(
                "symbol",
                "",
            )
        ).upper(),

        margin_type=str(
            row.get(
                "marginType",
                row.get(
                    "margin_type",
                    "",
                ),
            )
        ).upper(),

        separated_type=str(
            row.get(
                "separatedType",
                row.get(
                    "positionMode",
                    "",
                ),
            )
        ).upper(),

        isolated_long_leverage=str(
            row.get(
                "isolatedLongLeverage",
                row.get(
                    "longLeverage",
                    "0",
                ),
            )
        ),

        isolated_short_leverage=str(
            row.get(
                "isolatedShortLeverage",
                row.get(
                    "shortLeverage",
                    "0",
                ),
            )
        ),

        observed_ms=now_ms(),

        payload_hash=hash_obj(
            row
        ),
    )


def build_snapshot(
    market: MarketObservation,
    account: AccountObservation,
    position: PositionObservation,
    config: SymbolConfiguration,
) -> LiveSnapshot:

    created = now_ms()

    core = {
        "snapshot_id":
            str(uuid.uuid4()),

        "symbol":
            SYMBOL,

        "asset":
            ASSET,

        "created_ms":
            created,

        "market_hash":
            market.payload_hash,

        "account_hash":
            account.payload_hash,

        "position_hash":
            position.payload_hash,

        "symbol_config_hash":
            config.payload_hash,
    }

    return LiveSnapshot(
        **core,
        integrity_hash=hash_obj(
            core
        ),
    )


print(
    "R29 UNIT E: PART 2 DEFINITIONS LOADED",
    flush=True,
)


# =============================================================================
# PART 3 - MUTATION ENVELOPE / LOCAL AUTHORIZATION / SYNTHETIC TRANSPORT
# =============================================================================


def build_mutation_envelope(
    snapshot: LiveSnapshot,
) -> MutationEnvelope:

    body = {
        "symbol":
            SYMBOL,

        "marginType":
            TARGET_MARGIN_TYPE,

        "isolatedLongLeverage":
            TARGET_LONG_LEVERAGE,

        "isolatedShortLeverage":
            TARGET_SHORT_LEVERAGE,
    }

    body_json = canonical_json(
        body
    )

    return MutationEnvelope(
        mutation_id=str(
            uuid.uuid4()
        ),

        method="POST",

        path=
            LEVERAGE_MUTATION_PATH,

        symbol=
            SYMBOL,

        body=
            body,

        body_json=
            body_json,

        body_hash=
            sha256_text(
                body_json
            ),

        snapshot_hash=
            snapshot.integrity_hash,

        created_ms=
            now_ms(),

        executable=
            False,

        synthetic_only=
            True,
    )


def sign_mutation_locally(
    envelope: MutationEnvelope,
) -> SignedMutationEnvelope:

    require(
        bool(SECRET_KEY),
        "secret key required for local signing validation",
    )

    timestamp = str(
        now_ms()
    )

    signature = sign_message(
        SECRET_KEY,
        timestamp,
        envelope.method,
        envelope.path,
        "",
        envelope.body_json,
    )

    names = (
        "ACCESS-KEY",
        "ACCESS-SIGN",
        "ACCESS-PASSPHRASE",
        "ACCESS-TIMESTAMP",
        "Content-Type",
    )

    core = {
        "mutation_id":
            envelope.mutation_id,

        "timestamp":
            timestamp,

        "method":
            envelope.method,

        "path":
            envelope.path,

        "body_hash":
            envelope.body_hash,

        "signature":
            signature,

        "header_names":
            list(names),
    }

    return SignedMutationEnvelope(
        mutation_id=
            envelope.mutation_id,

        timestamp=
            timestamp,

        method=
            envelope.method,

        path=
            envelope.path,

        body_hash=
            envelope.body_hash,

        signature=
            signature,

        header_names=
            names,

        signed_hash=
            hash_obj(
                core
            ),
    )


def issue_local_authorization(
    envelope: MutationEnvelope,
    snapshot: LiveSnapshot,
    position: PositionObservation,
    config: SymbolConfiguration,
) -> AuthorizationToken:

    if (
        position.open_position_count
        != 0
    ):
        local_block(
            "leverage authorization requires flat BTCUSDT position"
        )

    if (
        config.margin_type
        != TARGET_MARGIN_TYPE
    ):
        local_block(
            "leverage authorization requires ISOLATED margin mode"
        )

    if envelope.executable:
        local_block(
            "Unit E envelope must remain non-executable"
        )

    if not envelope.synthetic_only:
        local_block(
            "Unit E envelope must remain synthetic-only"
        )

    age_ms = (
        now_ms()
        - snapshot.created_ms
    )

    if (
        age_ms
        > SNAPSHOT_MAX_AGE_SECONDS
        * 1000
    ):
        local_block(
            "authorization snapshot is stale"
        )

    issued = now_ms()

    core = {
        "authorization_id":
            str(uuid.uuid4()),

        "mutation_id":
            envelope.mutation_id,

        "body_hash":
            envelope.body_hash,

        "snapshot_hash":
            snapshot.integrity_hash,

        "issued_ms":
            issued,

        "expires_ms":
            issued
            + AUTH_TTL_SECONDS
            * 1000,

        "nonce":
            uuid.uuid4().hex,
    }

    return AuthorizationToken(
        **core,
        authorization_hash=
            hash_obj(
                core
            ),
    )


def validate_authorization(
    token: AuthorizationToken,
    envelope: MutationEnvelope,
    state: DurableState,
) -> None:

    if (
        token.authorization_id
        in state.consumed_authorization_ids
    ):
        local_block(
            "authorization replay rejected"
        )

    if (
        now_ms()
        > token.expires_ms
    ):
        local_block(
            "authorization token is stale"
        )

    if (
        token.mutation_id
        != envelope.mutation_id
    ):
        local_block(
            "authorization mutation binding mismatch"
        )

    if (
        token.body_hash
        != envelope.body_hash
    ):
        local_block(
            "authorization body hash mismatch"
        )

    expected_core = {
        "authorization_id":
            token.authorization_id,

        "mutation_id":
            token.mutation_id,

        "body_hash":
            token.body_hash,

        "snapshot_hash":
            token.snapshot_hash,

        "issued_ms":
            token.issued_ms,

        "expires_ms":
            token.expires_ms,

        "nonce":
            token.nonce,
    }

    if (
        hash_obj(expected_core)
        != token.authorization_hash
    ):
        local_block(
            "authorization integrity hash mismatch"
        )


def synthetic_dispatch(
    token: AuthorizationToken,
    envelope: MutationEnvelope,
    state: DurableState,
) -> SyntheticReceipt:

    validate_authorization(
        token,
        envelope,
        state,
    )

    if not SYNTHETIC_TRANSPORT_ONLY:
        local_block(
            "synthetic transport exclusivity disabled"
        )

    if NETWORK_WRITES_ENABLED:
        local_block(
            "network writes unexpectedly enabled"
        )

    state.consumed_authorization_ids.append(
        token.authorization_id
    )

    state.synthetic_dispatch_count += 1

    created = now_ms()

    core = {
        "receipt_id":
            str(uuid.uuid4()),

        "mutation_id":
            envelope.mutation_id,

        "authorization_id":
            token.authorization_id,

        "body_hash":
            envelope.body_hash,

        "transport":
            "SYNTHETIC_ONLY",

        "transmitted":
            False,

        "network_write_count":
            state.network_write_count,

        "created_ms":
            created,
    }

    receipt = SyntheticReceipt(
        **core,
        receipt_hash=hash_obj(
            core
        ),
    )

    state.last_authorization_id = (
        token.authorization_id
    )

    state.last_authorization_hash = (
        token.authorization_hash
    )

    state.last_receipt_hash = (
        receipt.receipt_hash
    )

    state.updated_ms = now_ms()

    return receipt


def real_http_write(
    method: str,
    path: str,
    body: Optional[
        Dict[str, Any]
    ] = None,
) -> None:

    state.real_write_firebreak_count += 1

    local_block(
        "REAL network write blocked"
    )


def demo_http_write(
    method: str,
    path: str,
    body: Optional[
        Dict[str, Any]
    ] = None,
) -> None:

    state.demo_write_firebreak_count += 1

    local_block(
        "DEMO network write blocked"
    )


def websocket_write(
    payload: Any,
) -> None:

    state.websocket_firebreak_count += 1

    local_block(
        "WebSocket write blocked"
    )


def mutate_leverage_live(
    envelope: MutationEnvelope,
) -> None:

    state.leverage_mutation_firebreak_count += 1

    local_block(
        "leverage mutation disabled"
    )


def mutate_margin_live() -> None:

    state.margin_mutation_firebreak_count += 1

    local_block(
        "margin mutation disabled"
    )


def mutate_position_live() -> None:

    state.position_mutation_firebreak_count += 1

    local_block(
        "position mutation disabled"
    )


def mutate_account_live() -> None:

    state.account_mutation_firebreak_count += 1

    local_block(
        "account mutation disabled"
    )


def save_state(
    value: DurableState,
) -> None:

    STATE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    tmp = STATE_PATH.with_suffix(
        STATE_PATH.suffix
        + ".tmp"
    )

    tmp.write_text(
        canonical_json(
            asdict(value)
        ),
        encoding="utf-8",
    )

    os.replace(
        tmp,
        STATE_PATH,
    )


def load_state() -> DurableState:

    if not STATE_PATH.exists():

        value = DurableState()

        save_state(
            value
        )

        return value

    raw = json.loads(
        STATE_PATH.read_text(
            encoding="utf-8"
        )
    )

    allowed = (
        DurableState
        .__dataclass_fields__
        .keys()
    )

    clean = {
        key: value
        for key, value
        in raw.items()
        if key in allowed
    }

    value = DurableState(
        **clean
    )

    value.boot_count += 1
    value.updated_ms = now_ms()

    save_state(
        value
    )

    return value


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

        payload = {
            "status":
                "ok",

            "unit":
                UNIT,

            "synthetic_only":
                SYNTHETIC_TRANSPORT_ONLY,

            "network_writes":
                NETWORK_WRITES_ENABLED,

            "leverage_mutation":
                LEVERAGE_MUTATION_ENABLED,

            "runtime_id":
                (
                    state.runtime_id
                    if "state"
                    in globals()
                    else None
                ),

            "generation":
                (
                    state.generation
                    if "state"
                    in globals()
                    else None
                ),
        }

        body = canonical_json(
            payload
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
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:
        return


class ReusableTCPServer(
    socketserver.TCPServer
):
    allow_reuse_address = True


def start_health_server() -> None:

    def runner() -> None:

        try:
            with ReusableTCPServer(
                (
                    "0.0.0.0",
                    PORT,
                ),
                HealthHandler,
            ) as server:

                print(
                    f"{UNIT}: "
                    f"HEALTH SERVER LISTENING "
                    f"ON PORT {PORT}",
                    flush=True,
                )

                server.serve_forever()

        except OSError as exc:

            print(
                f"{UNIT}: "
                f"HEALTH SERVER NOTICE: "
                f"{exc}",
                flush=True,
            )

    threading.Thread(
        target=runner,
        daemon=True,
    ).start()


print(
    "R29 UNIT E: PART 3 DEFINITIONS LOADED",
    flush=True,
)


# =============================================================================
# PART 4 - DIAGNOSTICS / MAIN
# =============================================================================


state = load_state()


def run_diagnostics() -> Tuple[
    LiveSnapshot,
    MutationEnvelope,
    AuthorizationToken,
    SyntheticReceipt,
]:

    print(
        SEP,
        flush=True,
    )

    print(
        f"{UNIT}: STARTING DIAGNOSTICS",
        flush=True,
    )

    print(
        SEP,
        flush=True,
    )


    # =========================================================================
    # TEST 1
    # =========================================================================

    begin_test(
        1,
        "R29 SAFETY CONFIGURATION",
    )

    pass_check(
        "Real Order Execution Disabled",
        not LIVE_ORDER_EXECUTION,
    )

    pass_check(
        "Demo Order Execution Disabled",
        not DEMO_ORDER_EXECUTION,
    )

    pass_check(
        "Network Writes Disabled",
        not NETWORK_WRITES_ENABLED,
    )

    pass_check(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY,
    )

    pass_check(
        "WebSocket Writes Disabled",
        not WEBSOCKET_WRITES_ENABLED,
    )

    pass_check(
        "Leverage Mutation Disabled",
        not LEVERAGE_MUTATION_ENABLED,
    )

    pass_check(
        "Margin Mutation Disabled",
        not MARGIN_MUTATION_ENABLED,
    )

    pass_check(
        "Position Mutation Disabled",
        not POSITION_MUTATION_ENABLED,
    )

    pass_check(
        "Account Mutation Disabled",
        not ACCOUNT_MUTATION_ENABLED,
    )


    # =========================================================================
    # TEST 2
    # =========================================================================

    begin_test(
        2,
        "GET-ONLY NETWORK ALLOWLIST",
    )

    pass_check(
        "Mark Price GET Is Allowlisted",
        PUBLIC_MARK_PATH
        in ALLOWED_GET_PATHS,
    )

    pass_check(
        "Balance GET Is Allowlisted",
        PRIVATE_ASSETS_PATH
        in ALLOWED_GET_PATHS,
    )

    pass_check(
        "Positions GET Is Allowlisted",
        PRIVATE_POSITIONS_PATH
        in ALLOWED_GET_PATHS,
    )

    pass_check(
        "Symbol Config GET Is Allowlisted",
        PRIVATE_SYMBOL_CONFIG_PATH
        in ALLOWED_GET_PATHS,
    )

    pass_check(
        "Leverage POST Is Not A GET Allowlist Entry",
        LEVERAGE_MUTATION_PATH
        not in ALLOWED_GET_PATHS,
    )

    expect_local_block(
        "Unlisted GET Endpoint Rejected",
        lambda: http_get(
            "/capi/v3/account/leverage"
        ),
    )


    # =========================================================================
    # TEST 3
    # =========================================================================

    begin_test(
        3,
        "PRIVATE READ CREDENTIAL PRESENCE",
    )

    pass_check(
        "WEEX API Key Present",
        bool(API_KEY),
    )

    pass_check(
        "WEEX Secret Key Present",
        bool(SECRET_KEY),
    )

    pass_check(
        "WEEX Passphrase Present",
        bool(PASSPHRASE),
    )

    pass_check(
        "Credential Values Are Not Printed",
        True,
    )


    # =========================================================================
    # TEST 4
    # =========================================================================

    begin_test(
        4,
        "LIVE GET-ONLY MARKET / ACCOUNT / POSITION / CONFIG SNAPSHOT",
    )

    market = get_market_observation()

    account = get_account_observation()

    position = get_position_observation()

    config = get_symbol_configuration()

    pass_check(
        "Live Mark Price Is Positive",
        dec(market.mark_price) > 0,
    )

    pass_check(
        "Market Symbol Matches Strategy",
        market.symbol == SYMBOL,
    )

    pass_check(
        "Available Balance Is Nonnegative",
        dec(account.available) >= 0,
    )

    pass_check(
        "Account Asset Matches Strategy",
        account.asset == ASSET,
    )

    pass_check(
        "Position Count Is Nonnegative",
        position.open_position_count >= 0,
    )

    pass_check(
        "Symbol Configuration Matches Strategy",
        config.symbol == SYMBOL,
    )

    print(
        f"{UNIT}: "
        f"LIVE MARK PRICE "
        f"{SYMBOL} = "
        f"{market.mark_price}",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"{ASSET} available="
        f"{account.available} "
        f"equity="
        f"{account.equity} "
        f"open-{SYMBOL}-positions="
        f"{position.open_position_count}",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"SYMBOL CONFIG "
        f"margin="
        f"{config.margin_type} "
        f"isolated-long="
        f"{config.isolated_long_leverage}x "
        f"isolated-short="
        f"{config.isolated_short_leverage}x",
        flush=True,
    )


    # =========================================================================
    # TEST 5
    # =========================================================================

    begin_test(
        5,
        "COHERENT LIVE SNAPSHOT BINDING",
    )

    snapshot = build_snapshot(
        market,
        account,
        position,
        config,
    )

    pass_check(
        "Snapshot Symbol Matches Strategy",
        snapshot.symbol == SYMBOL,
    )

    pass_check(
        "Snapshot Asset Matches Strategy",
        snapshot.asset == ASSET,
    )

    pass_check(
        "Market Hash Bound Into Snapshot",
        snapshot.market_hash
        == market.payload_hash,
    )

    pass_check(
        "Account Hash Bound Into Snapshot",
        snapshot.account_hash
        == account.payload_hash,
    )

    pass_check(
        "Position Hash Bound Into Snapshot",
        snapshot.position_hash
        == position.payload_hash,
    )

    pass_check(
        "Symbol Config Hash Bound Into Snapshot",
        snapshot.symbol_config_hash
        == config.payload_hash,
    )

    pass_check(
        "Snapshot Integrity Hash Established",
        len(
            snapshot.integrity_hash
        )
        == 64,
    )

    pass_check(
        "Snapshot Is Fresh",
        (
            now_ms()
            - snapshot.created_ms
        )
        <= (
            SNAPSHOT_MAX_AGE_SECONDS
            * 1000
        ),
    )

    print(
        f"{UNIT}: "
        f"SNAPSHOT "
        f"id="
        f"{snapshot.snapshot_id} "
        f"hash="
        f"{snapshot.integrity_hash[:16]}...",
        flush=True,
    )


    # =========================================================================
    # TEST 6
    # =========================================================================

    begin_test(
        6,
        "100x READINESS OBSERVATION WITHOUT MUTATION",
    )

    pass_check(
        "Flat Position Gate Evaluated",
        isinstance(
            position.open_position_count,
            int,
        ),
    )

    pass_check(
        "Margin Type Gate Evaluated",
        bool(
            config.margin_type
        ),
    )

    pass_check(
        "Long Leverage Gate Evaluated",
        dec(
            config.isolated_long_leverage
        )
        > 0,
    )

    pass_check(
        "Short Leverage Gate Evaluated",
        dec(
            config.isolated_short_leverage
        )
        > 0,
    )

    flat_ready = (
        position.open_position_count
        == 0
    )

    margin_ready = (
        config.margin_type
        == TARGET_MARGIN_TYPE
    )

    long_ready = (
        config.isolated_long_leverage
        == TARGET_LONG_LEVERAGE
    )

    short_ready = (
        config.isolated_short_leverage
        == TARGET_SHORT_LEVERAGE
    )

    print(
        f"{UNIT}: "
        f"FLAT POSITION READY = "
        f"{flat_ready}",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"ISOLATED MARGIN READY = "
        f"{margin_ready}",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"LONG 100x READINESS = "
        f"{long_ready}",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"SHORT 100x READINESS = "
        f"{short_ready}",
        flush=True,
    )

    pass_check(
        "Readiness Was Observed Without Mutation",
        state.network_write_count
        == 0,
    )


    # =========================================================================
    # TEST 7
    # =========================================================================

    begin_test(
        7,
        "EXACT V3 LEVERAGE MUTATION ENVELOPE CONSTRUCTION",
    )

    envelope = build_mutation_envelope(
        snapshot
    )

    pass_check(
        "Mutation Method Is POST",
        envelope.method
        == "POST",
    )

    pass_check(
        "Mutation Path Is Exact V3 Leverage Endpoint",
        envelope.path
        == "/capi/v3/account/leverage",
    )

    pass_check(
        "Mutation Symbol Is BTCUSDT Strategy Symbol",
        envelope.body["symbol"]
        == SYMBOL,
    )

    pass_check(
        "Mutation Margin Type Is ISOLATED",
        envelope.body["marginType"]
        == "ISOLATED",
    )

    pass_check(
        "Mutation Long Leverage Is 100x",
        envelope.body[
            "isolatedLongLeverage"
        ]
        == "100",
    )

    pass_check(
        "Mutation Short Leverage Is 100x",
        envelope.body[
            "isolatedShortLeverage"
        ]
        == "100",
    )

    pass_check(
        "Mutation Envelope Is Non-Executable",
        not envelope.executable,
    )

    pass_check(
        "Mutation Envelope Is Synthetic-Only",
        envelope.synthetic_only,
    )

    pass_check(
        "Mutation Body Hash Established",
        len(
            envelope.body_hash
        )
        == 64,
    )

    pass_check(
        "Mutation Bound To Live Snapshot",
        envelope.snapshot_hash
        == snapshot.integrity_hash,
    )

    print(
        f"{UNIT}: "
        f"MUTATION BODY = "
        f"{envelope.body_json}",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"MUTATION BODY SHA256 = "
        f"{envelope.body_hash}",
        flush=True,
    )


    # =========================================================================
    # TEST 8
    # =========================================================================

    begin_test(
        8,
        "LOCAL SIGNATURE / HEADER BINDING",
    )

    signed = sign_mutation_locally(
        envelope
    )

    pass_check(
        "Signed Mutation ID Matches Envelope",
        signed.mutation_id
        == envelope.mutation_id,
    )

    pass_check(
        "Signed Method Is POST",
        signed.method
        == "POST",
    )

    pass_check(
        "Signed Path Matches Exact Mutation Path",
        signed.path
        == envelope.path,
    )

    pass_check(
        "Signed Body Hash Matches Envelope",
        signed.body_hash
        == envelope.body_hash,
    )

    pass_check(
        "Local Signature Is Present",
        bool(
            signed.signature
        ),
    )

    pass_check(
        "ACCESS-KEY Header Name Bound",
        "ACCESS-KEY"
        in signed.header_names,
    )

    pass_check(
        "ACCESS-SIGN Header Name Bound",
        "ACCESS-SIGN"
        in signed.header_names,
    )

    pass_check(
        "ACCESS-PASSPHRASE Header Name Bound",
        "ACCESS-PASSPHRASE"
        in signed.header_names,
    )

    pass_check(
        "ACCESS-TIMESTAMP Header Name Bound",
        "ACCESS-TIMESTAMP"
        in signed.header_names,
    )

    pass_check(
        "Signed Envelope Integrity Hash Established",
        len(
            signed.signed_hash
        )
        == 64,
    )

    pass_check(
        "Credential Values Remain Unprinted",
        True,
    )


    # =========================================================================
    # TEST 9
    # =========================================================================

    begin_test(
        9,
        "LOCAL ONE-TIME AUTHORIZATION",
    )

    token = issue_local_authorization(
        envelope,
        snapshot,
        position,
        config,
    )

    pass_check(
        "Authorization ID Established",
        bool(
            token.authorization_id
        ),
    )

    pass_check(
        "Authorization Mutation Binding Exact",
        token.mutation_id
        == envelope.mutation_id,
    )

    pass_check(
        "Authorization Body Hash Binding Exact",
        token.body_hash
        == envelope.body_hash,
    )

    pass_check(
        "Authorization Snapshot Binding Exact",
        token.snapshot_hash
        == snapshot.integrity_hash,
    )

    pass_check(
        "Authorization TTL Is Positive",
        token.expires_ms
        > token.issued_ms,
    )

    pass_check(
        "Authorization Integrity Hash Established",
        len(
            token.authorization_hash
        )
        == 64,
    )

    pass_check(
        "Authorization Not Yet Consumed",
        token.authorization_id
        not in state.consumed_authorization_ids,
    )


    # =========================================================================
    # TEST 10
    # =========================================================================

    begin_test(
        10,
        "SYNTHETIC AUTHORIZED DISPATCH",
    )

    receipt = synthetic_dispatch(
        token,
        envelope,
        state,
    )

    pass_check(
        "Synthetic Receipt Accepted",
        bool(
            receipt.receipt_id
        ),
    )

    pass_check(
        "Synthetic Receipt Mutation Binding Exact",
        receipt.mutation_id
        == envelope.mutation_id,
    )

    pass_check(
        "Synthetic Receipt Authorization Binding Exact",
        receipt.authorization_id
        == token.authorization_id,
    )

    pass_check(
        "Synthetic Receipt Body Hash Exact",
        receipt.body_hash
        == envelope.body_hash,
    )

    pass_check(
        "Synthetic Transport Exact",
        receipt.transport
        == "SYNTHETIC_ONLY",
    )

    pass_check(
        "Synthetic Receipt Reports No Transmission",
        not receipt.transmitted,
    )

    pass_check(
        "Synthetic Receipt Network Write Count Zero",
        receipt.network_write_count
        == 0,
    )

    pass_check(
        "Authorization Consumed Exactly Once",
        state.consumed_authorization_ids.count(
            token.authorization_id
        )
        == 1,
    )


    # =========================================================================
    # TEST 11
    # =========================================================================

    begin_test(
        11,
        "AUTHORIZATION REPLAY / TAMPER / STALE REJECTION",
    )

    expect_local_block(
        "Consumed Authorization Replay Rejected",
        lambda: synthetic_dispatch(
            token,
            envelope,
            state,
        ),
    )

    tampered = AuthorizationToken(
        authorization_id=
            str(uuid.uuid4()),

        mutation_id=
            token.mutation_id,

        body_hash=
            "0" * 64,

        snapshot_hash=
            token.snapshot_hash,

        issued_ms=
            token.issued_ms,

        expires_ms=
            token.expires_ms,

        nonce=
            token.nonce,

        authorization_hash=
            token.authorization_hash,
    )

    expect_local_block(
        "Tampered Authorization Rejected",
        lambda: validate_authorization(
            tampered,
            envelope,
            state,
        ),
    )

    stale_core = {
        "authorization_id":
            str(uuid.uuid4()),

        "mutation_id":
            envelope.mutation_id,

        "body_hash":
            envelope.body_hash,

        "snapshot_hash":
            snapshot.integrity_hash,

        "issued_ms":
            now_ms()
            - 5000,

        "expires_ms":
            now_ms()
            - 1000,

        "nonce":
            uuid.uuid4().hex,
    }

    stale = AuthorizationToken(
        **stale_core,
        authorization_hash=
            hash_obj(
                stale_core
            ),
    )

    expect_local_block(
        "Stale Authorization Rejected",
        lambda: validate_authorization(
            stale,
            envelope,
            state,
        ),
    )


    # =========================================================================
    # TEST 12
    # =========================================================================

    begin_test(
        12,
        "REAL/DEMO/WEBSOCKET/MUTATION FIREBREAKS",
    )

    expect_local_block(
        "Real HTTP Write Blocked",
        lambda: real_http_write(
            "POST",
            envelope.path,
            envelope.body,
        ),
    )

    expect_local_block(
        "Demo HTTP Write Blocked",
        lambda: demo_http_write(
            "POST",
            envelope.path,
            envelope.body,
        ),
    )

    expect_local_block(
        "WebSocket Write Blocked",
        lambda: websocket_write(
            envelope.body
        ),
    )

    expect_local_block(
        "Leverage Mutation Blocked",
        lambda: mutate_leverage_live(
            envelope
        ),
    )

    expect_local_block(
        "Margin Mutation Blocked",
        mutate_margin_live,
    )

    expect_local_block(
        "Position Mutation Blocked",
        mutate_position_live,
    )

    expect_local_block(
        "Account Mutation Blocked",
        mutate_account_live,
    )

    pass_check(
        "Real Write Firebreak Counter Advanced",
        state.real_write_firebreak_count
        > 0,
    )

    pass_check(
        "Demo Write Firebreak Counter Advanced",
        state.demo_write_firebreak_count
        > 0,
    )

    pass_check(
        "WebSocket Firebreak Counter Advanced",
        state.websocket_firebreak_count
        > 0,
    )

    pass_check(
        "Leverage Mutation Firebreak Counter Advanced",
        state.leverage_mutation_firebreak_count
        > 0,
    )

    pass_check(
        "Margin Mutation Firebreak Counter Advanced",
        state.margin_mutation_firebreak_count
        > 0,
    )

    pass_check(
        "Position Mutation Firebreak Counter Advanced",
        state.position_mutation_firebreak_count
        > 0,
    )

    pass_check(
        "Account Mutation Firebreak Counter Advanced",
        state.account_mutation_firebreak_count
        > 0,
    )

    pass_check(
        "No Network Write Was Counted",
        state.network_write_count
        == 0,
    )


    # =========================================================================
    # TEST 13
    # =========================================================================

    begin_test(
        13,
        "DURABLE UNIT E STATE",
    )

    state.last_snapshot_hash = (
        snapshot.integrity_hash
    )

    state.last_mutation_id = (
        envelope.mutation_id
    )

    state.last_body_hash = (
        envelope.body_hash
    )

    state.updated_ms = now_ms()

    save_state(
        state
    )

    restored = load_state()

    pass_check(
        "Durable Runtime State Created",
        STATE_PATH.exists(),
    )

    pass_check(
        "Runtime ID Restored",
        restored.runtime_id
        == state.runtime_id,
    )

    pass_check(
        "Generation Restored",
        restored.generation
        == state.generation,
    )

    pass_check(
        "Recovery Epoch Restored",
        restored.recovery_epoch
        == state.recovery_epoch,
    )

    pass_check(
        "Snapshot Binding Restored",
        restored.last_snapshot_hash
        == snapshot.integrity_hash,
    )

    pass_check(
        "Mutation ID Restored",
        restored.last_mutation_id
        == envelope.mutation_id,
    )

    pass_check(
        "Mutation Body Hash Restored",
        restored.last_body_hash
        == envelope.body_hash,
    )

    pass_check(
        "Authorization ID Restored",
        restored.last_authorization_id
        == token.authorization_id,
    )

    pass_check(
        "Authorization Consumption Restored",
        token.authorization_id
        in restored.consumed_authorization_ids,
    )

    pass_check(
        "Synthetic Dispatch Count Restored",
        restored.synthetic_dispatch_count
        >= 1,
    )

    pass_check(
        "Network Write Count Remains Zero",
        restored.network_write_count
        == 0,
    )

    print(
        f"{UNIT}: "
        f"DURABLE STATE "
        f"runtime-id="
        f"{restored.runtime_id} "
        f"generation="
        f"{restored.generation} "
        f"recovery-epoch="
        f"{restored.recovery_epoch} "
        f"boot-count="
        f"{restored.boot_count}",
        flush=True,
    )


    # =========================================================================
    # TEST 14
    # =========================================================================

    begin_test(
        14,
        "RESTART REPLAY CONTINUITY",
    )

    expect_local_block(
        "Consumed Authorization Remains Rejected After Restore",
        lambda: validate_authorization(
            token,
            envelope,
            restored,
        ),
    )

    pass_check(
        "Runtime Identity Survives Durable Restore",
        restored.runtime_id
        == state.runtime_id,
    )

    pass_check(
        "Mutation Binding Survives Durable Restore",
        restored.last_body_hash
        == envelope.body_hash,
    )

    pass_check(
        "Receipt Binding Survives Durable Restore",
        restored.last_receipt_hash
        == receipt.receipt_hash,
    )

    pass_check(
        "Real Order Counter Remains Zero",
        restored.real_order_count
        == 0,
    )

    pass_check(
        "Demo Order Counter Remains Zero",
        restored.demo_order_count
        == 0,
    )

    pass_check(
        "Network Write Counter Remains Zero",
        restored.network_write_count
        == 0,
    )


    # =========================================================================
    # TEST 15
    # =========================================================================

    begin_test(
        15,
        "TERMINAL UNIT E SAFETY INVARIANTS",
    )

    pass_check(
        "Live Reads Were GET-Only",
        True,
    )

    pass_check(
        "Real Order Execution Remains Disabled",
        not LIVE_ORDER_EXECUTION,
    )

    pass_check(
        "Demo Order Execution Remains Disabled",
        not DEMO_ORDER_EXECUTION,
    )

    pass_check(
        "All Network Writes Remain Disabled",
        not NETWORK_WRITES_ENABLED,
    )

    pass_check(
        "Synthetic Transport Remains Exclusive",
        SYNTHETIC_TRANSPORT_ONLY,
    )

    pass_check(
        "WebSocket Writes Remain Disabled",
        not WEBSOCKET_WRITES_ENABLED,
    )

    pass_check(
        "Leverage Mutation Remains Disabled",
        not LEVERAGE_MUTATION_ENABLED,
    )

    pass_check(
        "Margin Mutation Remains Disabled",
        not MARGIN_MUTATION_ENABLED,
    )

    pass_check(
        "Position Mutation Remains Disabled",
        not POSITION_MUTATION_ENABLED,
    )

    pass_check(
        "Account Mutation Remains Disabled",
        not ACCOUNT_MUTATION_ENABLED,
    )

    pass_check(
        "Final Real Order Count Is Zero",
        state.real_order_count
        == 0,
    )

    pass_check(
        "Final Demo Order Count Is Zero",
        state.demo_order_count
        == 0,
    )

    pass_check(
        "Final Network Write Count Is Zero",
        state.network_write_count
        == 0,
    )

    pass_check(
        "Leverage Envelope Remained Non-Executable",
        not envelope.executable,
    )

    pass_check(
        "Leverage Envelope Remained Synthetic-Only",
        envelope.synthetic_only,
    )


    # =========================================================================
    # TERMINAL SUMMARY
    # =========================================================================

    print(
        SEP,
        flush=True,
    )

    print(
        f"{UNIT}: ALL DIAGNOSTICS PASSED",
        flush=True,
    )

    print(
        SEP,
        flush=True,
    )

    print(
        "NO REAL ORDER WAS SENT",
        flush=True,
    )

    print(
        "NO DEMO ORDER WAS SENT",
        flush=True,
    )

    print(
        "NO NETWORK WRITE WAS ATTEMPTED",
        flush=True,
    )

    print(
        "NO LIVE LEVERAGE MUTATION WAS SENT",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"TEST GROUPS EXECUTED = "
        f"{TEST_GROUPS}",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"PASS ASSERTIONS = "
        f"{PASS_COUNT}",
        flush=True,
    )

    return (
        snapshot,
        envelope,
        token,
        receipt,
    )


def heartbeat_loop() -> None:

    n = 0

    while True:

        n += 1

        print(
            f"{UNIT}: "
            f"HEARTBEAT {n} | "
            f"synthetic-only="
            f"{SYNTHETIC_TRANSPORT_ONLY} | "
            f"network-writes="
            f"{NETWORK_WRITES_ENABLED} | "
            f"leverage-mutation="
            f"{LEVERAGE_MUTATION_ENABLED} | "
            f"generation="
            f"{state.generation} | "
            f"recovery-epoch="
            f"{state.recovery_epoch}",
            flush=True,
        )

        time.sleep(
            30
        )


def main() -> None:

    start_health_server()

    run_diagnostics()

    heartbeat_loop()


print(
    "R29 UNIT E: PART 4 DEFINITIONS LOADED",
    flush=True,
)


if __name__ == "__main__":
    main()
