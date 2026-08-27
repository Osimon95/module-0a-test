# =============================================================================
# R34A
# LIVE LEVERAGE MUTATION READINESS
#
# PURPOSE
# -------
# 1. Authenticate to WEEX using READ-ONLY GET.
# 2. Read BTCUSDT symbol configuration.
# 3. Confirm current margin mode and leverage.
# 4. Determine whether 100x correction is still required.
# 5. Construct the exact future 100x mutation payload.
# 6. Bind intent -> payload -> envelope hashes.
# 7. Persist a durable LIVE_MUTATION_READY snapshot.
#
# ABSOLUTE SAFETY RULES
# ---------------------
# - NO REAL ORDERS
# - NO DEMO ORDERS
# - NO POST REQUESTS
# - NO LEVERAGE MUTATION
# - NO ACCOUNT MUTATION
# - AUTHENTICATED GET ONLY
#
# R34A MUST NEVER MODIFY THE WEEX ACCOUNT.
# =============================================================================

import os
import time
import json
import hmac
import base64
import hashlib
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode

import requests


# =============================================================================
# SECTION 1: VERSION / IDENTITY
# =============================================================================

VERSION = "R34A"

SYMBOL = "BTCUSDT"

TARGET_LONG_LEVERAGE = "100"
TARGET_SHORT_LEVERAGE = "100"

TARGET_MARGIN_TYPE = "ISOLATED"

BASE_URL = "https://api-contract.weex.com"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

FUTURE_LEVERAGE_MUTATION_PATH = "/capi/v3/account/leverage"

STATE_FILE = os.getenv(
    "R34A_STATE_FILE",
    "/tmp/r34a_live_mutation_readiness_state.json",
)

HEALTH_PORT = int(
    os.getenv(
        "PORT",
        os.getenv("HEALTH_PORT", "10000"),
    )
)


# =============================================================================
# SECTION 2: HARD SAFETY CONSTANTS
# =============================================================================

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

NETWORK_POST_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

AUTHENTICATED_GET_ENABLED = True

SYNTHETIC_DISPATCH_ENABLED = False

LIVE_MUTATION_EXECUTION_ENABLED = False

ALLOWLISTED_GET_PATHS = {
    SYMBOL_CONFIG_PATH,
}


# =============================================================================
# SECTION 3: GLOBAL SAFETY COUNTERS
# =============================================================================

COUNTERS = {
    "authenticated_get": 0,
    "network_post": 0,
    "real_order": 0,
    "demo_order": 0,
    "leverage_mutation": 0,
    "margin_mutation": 0,
    "position_mutation": 0,
    "account_mutation": 0,
    "synthetic_dispatch": 0,
    "blocked_write": 0,
}


# =============================================================================
# SECTION 4: PHASE / RUNTIME STATE
# =============================================================================

runtime_state = {
    "version": VERSION,
    "symbol": SYMBOL,
    "phase": "BOOTING",

    "generation": 1,
    "recovery_epoch": 1,

    "authenticated_read_complete": False,
    "symbol_config_verified": False,

    "current_margin_type": None,
    "current_position_mode": None,

    "current_cross_leverage": None,
    "current_long_leverage": None,
    "current_short_leverage": None,

    "target_long_leverage": TARGET_LONG_LEVERAGE,
    "target_short_leverage": TARGET_SHORT_LEVERAGE,

    "correction_required": None,

    "intent_bound": False,
    "payload_bound": False,
    "envelope_bound": False,

    "intent_hash": None,
    "payload_hash": None,
    "envelope_hash": None,

    "authorization_consumed": False,
    "dispatch_committed": False,

    "live_mutation_ready": False,

    "real_execution": False,
    "network_writes": False,
    "leverage_mutation": False,

    "last_error": None,
}


# =============================================================================
# SECTION 5: DISPLAY HELPERS
# =============================================================================

WIDTH = 92


def line():
    print("-" * WIDTH, flush=True)


def section(title):
    line()
    print(title, flush=True)
    line()


def check(name, condition):
    result = "✅ PASS" if condition else "❌ FAIL"
    print(f"{name:<78} {result}", flush=True)

    if not condition:
        raise AssertionError(name)


# =============================================================================
# SECTION 6: HASH / CANONICAL SERIALIZATION
# =============================================================================

def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def hash_object(value):
    return sha256_text(
        canonical_json(value)
    )


# =============================================================================
# SECTION 7: CREDENTIAL ACCESS
# =============================================================================

def get_credentials():

    api_key = os.getenv("WEEX_API_KEY", "").strip()

    secret_key = (
        os.getenv("WEEX_SECRET_KEY", "").strip()
        or os.getenv("WEEX_API_SECRET", "").strip()
    )

    passphrase = (
        os.getenv("WEEX_PASSPHRASE", "").strip()
        or os.getenv("WEEX_API_PASSPHRASE", "").strip()
    )

    return api_key, secret_key, passphrase


# =============================================================================
# SECTION 8: WEEX SIGNATURE
# =============================================================================

def generate_signature(
    secret_key,
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):

    method = method.upper()

    if query_string:

        message = (
            timestamp
            + method
            + request_path
            + "?"
            + query_string
            + body
        )

    else:

        message = (
            timestamp
            + method
            + request_path
            + body
        )

    digest = hmac.new(
        secret_key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


# =============================================================================
# SECTION 9: READ-ONLY NETWORK TRANSPORT
# =============================================================================

def authenticated_get(
    request_path,
    params=None,
    timeout=15,
):

    if not AUTHENTICATED_GET_ENABLED:
        raise RuntimeError(
            "Authenticated GET disabled"
        )

    if request_path not in ALLOWLISTED_GET_PATHS:
        raise RuntimeError(
            f"GET path not allowlisted: {request_path}"
        )

    if NETWORK_POST_ENABLED:
        raise RuntimeError(
            "Safety violation: POST capability enabled"
        )

    api_key, secret_key, passphrase = get_credentials()

    if not api_key:
        raise RuntimeError(
            "WEEX_API_KEY missing"
        )

    if not secret_key:
        raise RuntimeError(
            "WEEX_SECRET_KEY / WEEX_API_SECRET missing"
        )

    if not passphrase:
        raise RuntimeError(
            "WEEX_PASSPHRASE / WEEX_API_PASSPHRASE missing"
        )

    params = params or {}

    query_string = urlencode(params)

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = generate_signature(
        secret_key=secret_key,
        timestamp=timestamp,
        method="GET",
        request_path=request_path,
        query_string=query_string,
        body="",
    )

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "locale": "en-US",
    }

    url = BASE_URL + request_path

    COUNTERS["authenticated_get"] += 1

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=timeout,
    )

    if response.status_code != 200:

        raise RuntimeError(
            f"Authenticated GET failed "
            f"HTTP={response.status_code} "
            f"BODY={response.text}"
        )

    try:
        return response.json()

    except Exception as exc:

        raise RuntimeError(
            f"Invalid JSON response: {exc}"
        )


# =============================================================================
# SECTION 10: ABSOLUTE WRITE FIREBREAK
# =============================================================================

def forbidden_post(*args, **kwargs):

    COUNTERS["blocked_write"] += 1

    raise RuntimeError(
        "R34A WRITE FIREBREAK: "
        "all POST requests are prohibited"
    )


def forbidden_order(*args, **kwargs):

    COUNTERS["blocked_write"] += 1

    raise RuntimeError(
        "R34A ORDER FIREBREAK: "
        "order execution is prohibited"
    )


def forbidden_leverage_mutation(*args, **kwargs):

    COUNTERS["blocked_write"] += 1

    raise RuntimeError(
        "R34A LEVERAGE FIREBREAK: "
        "leverage mutation is prohibited"
    )


# =============================================================================
# SECTION 11: CONFIG NORMALIZATION
# =============================================================================

def normalize_symbol_config(data):

    if isinstance(data, list):

        if not data:
            raise RuntimeError(
                "Symbol configuration response is empty"
            )

        for item in data:

            if (
                isinstance(item, dict)
                and str(
                    item.get("symbol", "")
                ).upper() == SYMBOL
            ):
                return item

        if len(data) == 1:
            return data[0]

        raise RuntimeError(
            f"{SYMBOL} not found in symbol configuration"
        )

    if isinstance(data, dict):

        # Some APIs wrap data.
        nested = data.get("data")

        if nested is not None:
            return normalize_symbol_config(
                nested
            )

        return data

    raise RuntimeError(
        "Unexpected symbol configuration format"
    )


# =============================================================================
# SECTION 12: INTENT CONSTRUCTION
# =============================================================================

def construct_mutation_intent(config):

    return {
        "version": VERSION,
        "intent_type": "LEVERAGE_CORRECTION",
        "symbol": SYMBOL,

        "current": {
            "marginType": str(
                config.get(
                    "marginType",
                    "",
                )
            ),
            "isolatedLongLeverage": str(
                config.get(
                    "isolatedLongLeverage",
                    "",
                )
            ),
            "isolatedShortLeverage": str(
                config.get(
                    "isolatedShortLeverage",
                    "",
                )
            ),
        },

        "target": {
            "marginType": TARGET_MARGIN_TYPE,
            "isolatedLongLeverage": TARGET_LONG_LEVERAGE,
            "isolatedShortLeverage": TARGET_SHORT_LEVERAGE,
        },

        "generation": runtime_state[
            "generation"
        ],

        "recoveryEpoch": runtime_state[
            "recovery_epoch"
        ],

        "networkExecutionAuthorized": False,

        "mutationAuthorized": False,

        "orderExecutionAuthorized": False,
    }


# =============================================================================
# SECTION 13: FUTURE MUTATION PAYLOAD CONSTRUCTION
# =============================================================================

def construct_future_payload():

    return {
        "symbol": SYMBOL,

        "marginType": TARGET_MARGIN_TYPE,

        "isolatedLongLeverage":
            TARGET_LONG_LEVERAGE,

        "isolatedShortLeverage":
            TARGET_SHORT_LEVERAGE,
    }


# =============================================================================
# SECTION 14: PRE-LIVE ENVELOPE
# =============================================================================

def construct_envelope(
    intent_hash,
    payload_hash,
):

    return {
        "version": VERSION,

        "method": "POST",

        "path":
            FUTURE_LEVERAGE_MUTATION_PATH,

        "symbol": SYMBOL,

        "intentHash": intent_hash,

        "payloadHash": payload_hash,

        "generation":
            runtime_state["generation"],

        "recoveryEpoch":
            runtime_state["recovery_epoch"],

        "executionMode":
            "NOT_AUTHORIZED",

        "transport":
            "BLOCKED",

        "realNetworkTransmission":
            False,
    }


# =============================================================================
# SECTION 15: DURABLE STATE
# =============================================================================

def atomic_write_json(path, value):

    directory = os.path.dirname(path)

    if directory:
        os.makedirs(
            directory,
            exist_ok=True,
        )

    temp_path = path + ".tmp"

    with open(
        temp_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            value,
            file,
            sort_keys=True,
            indent=2,
        )

        file.flush()

        os.fsync(
            file.fileno()
        )

    os.replace(
        temp_path,
        path,
    )


def persist_state():

    snapshot = dict(
        runtime_state
    )

    snapshot["counters"] = dict(
        COUNTERS
    )

    atomic_write_json(
        STATE_FILE,
        snapshot,
    )


def restore_state():

    if not os.path.exists(
        STATE_FILE
    ):
        return None

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(
            file
        )


# =============================================================================
# SECTION 16: HEALTH SERVER
# =============================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        payload = {
            "status": "ok",
            "version": VERSION,
            "symbol": SYMBOL,
            "phase":
                runtime_state["phase"],

            "live_mutation_ready":
                runtime_state[
                    "live_mutation_ready"
                ],

            "correction_required":
                runtime_state[
                    "correction_required"
                ],

            "network_writes":
                runtime_state[
                    "network_writes"
                ],

            "leverage_mutation":
                runtime_state[
                    "leverage_mutation"
                ],

            "real_execution":
                runtime_state[
                    "real_execution"
                ],

            "target_long":
                TARGET_LONG_LEVERAGE,

            "target_short":
                TARGET_SHORT_LEVERAGE,
        }

        body = json.dumps(
            payload
        ).encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(body)

    def log_message(
        self,
        format,
        *args,
    ):
        return


def start_health_server():

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

        print(
            f"{VERSION}: "
            f"HEALTH SERVER LISTENING "
            f"ON PORT {HEALTH_PORT}",
            flush=True,
        )

        return server

    except OSError as exc:

        print(
            f"{VERSION}: "
            f"HEALTH SERVER WARNING: {exc}",
            flush=True,
        )

        return None


# =============================================================================
# SECTION 17: MAIN VALIDATION
# =============================================================================

def run_validation():

    section(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    print(
        f"{VERSION}: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"{VERSION}: VERSION={VERSION}",
        flush=True,
    )

    print(
        f"{VERSION}: STATE FILE={STATE_FILE}",
        flush=True,
    )

    print(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        f"{VERSION}: REAL ORDER EXECUTION DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: DEMO ORDER EXECUTION DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: NETWORK POST DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: LEVERAGE MUTATION DISABLED",
        flush=True,
    )


    # =========================================================================
    # TEST 1
    # =========================================================================

    section(
        "R34A TEST 1: HARD SAFETY CONFIGURATION"
    )

    check(
        "Real Order Execution Disabled",
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Demo Order Execution Disabled",
        DEMO_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Network POST Disabled",
        NETWORK_POST_ENABLED
        is False,
    )

    check(
        "Leverage Mutation Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    check(
        "Margin Mutation Disabled",
        MARGIN_MUTATION_ENABLED
        is False,
    )

    check(
        "Position Mutation Disabled",
        POSITION_MUTATION_ENABLED
        is False,
    )

    check(
        "Account Mutation Disabled",
        ACCOUNT_MUTATION_ENABLED
        is False,
    )

    check(
        "Live Mutation Execution Disabled",
        LIVE_MUTATION_EXECUTION_ENABLED
        is False,
    )


    # =========================================================================
    # TEST 2
    # =========================================================================

    section(
        "R34A TEST 2: CREDENTIAL READINESS"
    )

    api_key, secret_key, passphrase = (
        get_credentials()
    )

    check(
        "API Key Present",
        bool(api_key),
    )

    check(
        "Secret Key Present",
        bool(secret_key),
    )

    check(
        "Passphrase Present",
        bool(passphrase),
    )


    # =========================================================================
    # TEST 3
    # =========================================================================

    section(
        "R34A TEST 3: ENDPOINT BINDING"
    )

    check(
        "Symbol Config Method Is GET",
        True,
    )

    check(
        "Symbol Config Path Is V3",
        SYMBOL_CONFIG_PATH
        == "/capi/v3/account/symbolConfig",
    )

    check(
        "Future Leverage Method Is POST",
        True,
    )

    check(
        "Future Leverage Path Is V3",
        FUTURE_LEVERAGE_MUTATION_PATH
        == "/capi/v3/account/leverage",
    )

    check(
        "Only Symbol Config GET Is Allowlisted",
        ALLOWLISTED_GET_PATHS
        == {
            "/capi/v3/account/symbolConfig"
        },
    )


    # =========================================================================
    # TEST 4
    # =========================================================================

    section(
        "R34A TEST 4: AUTHENTICATED READ"
    )

    raw_config = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    config = normalize_symbol_config(
        raw_config
    )

    runtime_state[
        "authenticated_read_complete"
    ] = True

    print(
        f"{VERSION}: RAW SYMBOL CONFIG="
        f"{canonical_json(config)}",
        flush=True,
    )

    check(
        "Authenticated Symbol Config Read Succeeded",
        isinstance(
            config,
            dict,
        ),
    )

    check(
        "Authenticated GET Counter Is One",
        COUNTERS[
            "authenticated_get"
        ] == 1,
    )

    check(
        "Network POST Counter Is Zero",
        COUNTERS[
            "network_post"
        ] == 0,
    )


    # =========================================================================
    # TEST 5
    # =========================================================================

    section(
        "R34A TEST 5: SYMBOL IDENTITY"
    )

    returned_symbol = str(
        config.get(
            "symbol",
            "",
        )
    ).upper()

    check(
        "Returned Symbol Is BTCUSDT",
        returned_symbol == SYMBOL,
    )

    runtime_state[
        "symbol_config_verified"
    ] = True


    # =========================================================================
    # TEST 6
    # =========================================================================

    section(
        "R34A TEST 6: LIVE ACCOUNT CONFIGURATION"
    )

    margin_type = str(
        config.get(
            "marginType",
            "",
        )
    ).upper()

    position_mode = str(
        config.get(
            "separatedType",
            "",
        )
    ).upper()

    cross_leverage = str(
        config.get(
            "crossLeverage",
            "",
        )
    )

    long_leverage = str(
        config.get(
            "isolatedLongLeverage",
            "",
        )
    )

    short_leverage = str(
        config.get(
            "isolatedShortLeverage",
            "",
        )
    )

    runtime_state[
        "current_margin_type"
    ] = margin_type

    runtime_state[
        "current_position_mode"
    ] = position_mode

    runtime_state[
        "current_cross_leverage"
    ] = cross_leverage

    runtime_state[
        "current_long_leverage"
    ] = long_leverage

    runtime_state[
        "current_short_leverage"
    ] = short_leverage

    print(
        f"{VERSION}: CURRENT MARGIN TYPE="
        f"{margin_type}",
        flush=True,
    )

    print(
        f"{VERSION}: CURRENT POSITION MODE="
        f"{position_mode}",
        flush=True,
    )

    print(
        f"{VERSION}: CURRENT CROSS LEVERAGE="
        f"{cross_leverage}x",
        flush=True,
    )

    print(
        f"{VERSION}: CURRENT ISOLATED LONG="
        f"{long_leverage}x",
        flush=True,
    )

    print(
        f"{VERSION}: CURRENT ISOLATED SHORT="
        f"{short_leverage}x",
        flush=True,
    )

    check(
        "Margin Type Is Isolated",
        margin_type
        == TARGET_MARGIN_TYPE,
    )

    check(
        "Long Leverage Is Present",
        bool(long_leverage),
    )

    check(
        "Short Leverage Is Present",
        bool(short_leverage),
    )


    # =========================================================================
    # TEST 7
    # =========================================================================

    section(
        "R34A TEST 7: 100X CORRECTION REQUIREMENT"
    )

    correction_required = not (
        long_leverage
        == TARGET_LONG_LEVERAGE
        and
        short_leverage
        == TARGET_SHORT_LEVERAGE
    )

    runtime_state[
        "correction_required"
    ] = correction_required

    if correction_required:

        print(
            f"{VERSION}: "
            f"100x CORRECTION REQUIRED",
            flush=True,
        )

    else:

        print(
            f"{VERSION}: "
            f"ACCOUNT ALREADY AT "
            f"100x LONG / 100x SHORT",
            flush=True,
        )

    check(
        "Target Long Leverage Is 100x",
        TARGET_LONG_LEVERAGE
        == "100",
    )

    check(
        "Target Short Leverage Is 100x",
        TARGET_SHORT_LEVERAGE
        == "100",
    )


    # =========================================================================
    # TEST 8
    # =========================================================================

    section(
        "R34A TEST 8: CORRECTION INTENT"
    )

    intent = construct_mutation_intent(
        config
    )

    intent_hash = hash_object(
        intent
    )

    runtime_state[
        "intent_hash"
    ] = intent_hash

    runtime_state[
        "intent_bound"
    ] = True

    print(
        f"{VERSION}: INTENT="
        f"{canonical_json(intent)}",
        flush=True,
    )

    print(
        f"{VERSION}: INTENT SHA256="
        f"{intent_hash}",
        flush=True,
    )

    check(
        "Intent Symbol Is BTCUSDT",
        intent["symbol"]
        == SYMBOL,
    )

    check(
        "Intent Target Margin Type Is Isolated",
        intent["target"][
            "marginType"
        ]
        == "ISOLATED",
    )

    check(
        "Intent Long Target Is 100x",
        intent["target"][
            "isolatedLongLeverage"
        ]
        == "100",
    )

    check(
        "Intent Short Target Is 100x",
        intent["target"][
            "isolatedShortLeverage"
        ]
        == "100",
    )

    check(
        "Intent Network Authorization Is False",
        intent[
            "networkExecutionAuthorized"
        ]
        is False,
    )

    check(
        "Intent Mutation Authorization Is False",
        intent[
            "mutationAuthorized"
        ]
        is False,
    )


    # =========================================================================
    # TEST 9
    # =========================================================================

    section(
        "R34A TEST 9: FUTURE MUTATION PAYLOAD"
    )

    payload = (
        construct_future_payload()
    )

    payload_hash = hash_object(
        payload
    )

    runtime_state[
        "payload_hash"
    ] = payload_hash

    runtime_state[
        "payload_bound"
    ] = True

    print(
        f"{VERSION}: FUTURE PAYLOAD="
        f"{canonical_json(payload)}",
        flush=True,
    )

    print(
        f"{VERSION}: PAYLOAD SHA256="
        f"{payload_hash}",
        flush=True,
    )

    check(
        "Payload Symbol Is BTCUSDT",
        payload["symbol"]
        == SYMBOL,
    )

    check(
        "Payload Margin Type Is Isolated",
        payload[
            "marginType"
        ]
        == "ISOLATED",
    )

    check(
        "Payload Long Leverage Is 100",
        payload[
            "isolatedLongLeverage"
        ]
        == "100",
    )

    check(
        "Payload Short Leverage Is 100",
        payload[
            "isolatedShortLeverage"
        ]
        == "100",
    )


    # =========================================================================
    # TEST 10
    # =========================================================================

    section(
        "R34A TEST 10: PRE-LIVE ENVELOPE"
    )

    envelope = construct_envelope(
        intent_hash,
        payload_hash,
    )

    envelope_hash = hash_object(
        envelope
    )

    runtime_state[
        "envelope_hash"
    ] = envelope_hash

    runtime_state[
        "envelope_bound"
    ] = True

    print(
        f"{VERSION}: ENVELOPE="
        f"{canonical_json(envelope)}",
        flush=True,
    )

    print(
        f"{VERSION}: ENVELOPE SHA256="
        f"{envelope_hash}",
        flush=True,
    )

    check(
        "Envelope Method Is POST",
        envelope["method"]
        == "POST",
    )

    check(
        "Envelope Path Is Exact V3 Leverage Endpoint",
        envelope["path"]
        == "/capi/v3/account/leverage",
    )

    check(
        "Envelope Transport Is Blocked",
        envelope["transport"]
        == "BLOCKED",
    )

    check(
        "Envelope Real Transmission Is False",
        envelope[
            "realNetworkTransmission"
        ]
        is False,
    )


    # =========================================================================
    # TEST 11
    # =========================================================================

    section(
        "R34A TEST 11: WRITE FIREBREAK"
    )

    try:

        forbidden_post()

        post_blocked = False

    except RuntimeError:

        post_blocked = True

    check(
        "Generic POST Is Rejected",
        post_blocked,
    )

    try:

        forbidden_order()

        order_blocked = False

    except RuntimeError:

        order_blocked = True

    check(
        "Order Execution Is Rejected",
        order_blocked,
    )

    try:

        forbidden_leverage_mutation()

        mutation_blocked = False

    except RuntimeError:

        mutation_blocked = True

    check(
        "Leverage Mutation Is Rejected",
        mutation_blocked,
    )

    check(
        "Real Order Counter Remains Zero",
        COUNTERS[
            "real_order"
        ] == 0,
    )

    check(
        "Network POST Counter Remains Zero",
        COUNTERS[
            "network_post"
        ] == 0,
    )

    check(
        "Leverage Mutation Counter Remains Zero",
        COUNTERS[
            "leverage_mutation"
        ] == 0,
    )


    # =========================================================================
    # TEST 12
    # =========================================================================

    section(
        "R34A TEST 12: AUTHORIZATION STATE"
    )

    check(
        "Authorization Is Not Consumed",
        runtime_state[
            "authorization_consumed"
        ]
        is False,
    )

    check(
        "Dispatch Is Not Committed",
        runtime_state[
            "dispatch_committed"
        ]
        is False,
    )

    check(
        "Synthetic Dispatch Counter Is Zero",
        COUNTERS[
            "synthetic_dispatch"
        ] == 0,
    )

    check(
        "No Live Mutation Authorization Exists",
        LIVE_MUTATION_EXECUTION_ENABLED
        is False,
    )


    # =========================================================================
    # TEST 13
    # =========================================================================

    section(
        "R34A TEST 13: GENERATION / RECOVERY BINDING"
    )

    check(
        "Generation Is One",
        runtime_state[
            "generation"
        ] == 1,
    )

    check(
        "Recovery Epoch Is One",
        runtime_state[
            "recovery_epoch"
        ] == 1,
    )

    check(
        "Intent Generation Matches State",
        intent[
            "generation"
        ]
        == runtime_state[
            "generation"
        ],
    )

    check(
        "Intent Recovery Epoch Matches State",
        intent[
            "recoveryEpoch"
        ]
        == runtime_state[
            "recovery_epoch"
        ],
    )

    check(
        "Envelope Generation Matches State",
        envelope[
            "generation"
        ]
        == runtime_state[
            "generation"
        ],
    )

    check(
        "Envelope Recovery Epoch Matches State",
        envelope[
            "recoveryEpoch"
        ]
        == runtime_state[
            "recovery_epoch"
        ],
    )


    # =========================================================================
    # TEST 14
    # =========================================================================

    section(
        "R34A TEST 14: LIVE MUTATION READINESS"
    )

    ready = (
        runtime_state[
            "authenticated_read_complete"
        ]
        and
        runtime_state[
            "symbol_config_verified"
        ]
        and
        margin_type
        == TARGET_MARGIN_TYPE
        and
        runtime_state[
            "intent_bound"
        ]
        and
        runtime_state[
            "payload_bound"
        ]
        and
        runtime_state[
            "envelope_bound"
        ]
        and
        NETWORK_POST_ENABLED
        is False
        and
        LEVERAGE_MUTATION_ENABLED
        is False
        and
        REAL_ORDER_EXECUTION_ENABLED
        is False
    )

    runtime_state[
        "live_mutation_ready"
    ] = ready

    runtime_state[
        "phase"
    ] = (
        "LIVE_MUTATION_READY"
        if ready
        else
        "READINESS_FAILED"
    )

    check(
        "Authenticated Read Completed",
        runtime_state[
            "authenticated_read_complete"
        ],
    )

    check(
        "Symbol Configuration Verified",
        runtime_state[
            "symbol_config_verified"
        ],
    )

    check(
        "Intent Is Bound",
        runtime_state[
            "intent_bound"
        ],
    )

    check(
        "Payload Is Bound",
        runtime_state[
            "payload_bound"
        ],
    )

    check(
        "Envelope Is Bound",
        runtime_state[
            "envelope_bound"
        ],
    )

    check(
        "Live Mutation Readiness Achieved",
        ready,
    )


    # =========================================================================
    # TEST 15
    # =========================================================================

    section(
        "R34A TEST 15: DURABLE READINESS SNAPSHOT"
    )

    persist_state()

    restored = restore_state()

    check(
        "State File Restores",
        isinstance(
            restored,
            dict,
        ),
    )

    check(
        "Restored Phase Is Live Mutation Ready",
        restored[
            "phase"
        ]
        == "LIVE_MUTATION_READY",
    )

    check(
        "Restored Intent Hash Matches",
        restored[
            "intent_hash"
        ]
        == intent_hash,
    )

    check(
        "Restored Payload Hash Matches",
        restored[
            "payload_hash"
        ]
        == payload_hash,
    )

    check(
        "Restored Envelope Hash Matches",
        restored[
            "envelope_hash"
        ]
        == envelope_hash,
    )

    check(
        "Restored Network Write Counter Is Zero",
        restored[
            "counters"
        ][
            "network_post"
        ] == 0,
    )

    check(
        "Restored Leverage Mutation Counter Is Zero",
        restored[
            "counters"
        ][
            "leverage_mutation"
        ] == 0,
    )


    # =========================================================================
    # FINAL VALIDATION
    # =========================================================================

    section(
        "R34A FINAL VALIDATION"
    )

    check(
        "Phase Is LIVE_MUTATION_READY",
        runtime_state[
            "phase"
        ]
        == "LIVE_MUTATION_READY",
    )

    check(
        "Exact 100x Long Target Bound",
        TARGET_LONG_LEVERAGE
        == "100",
    )

    check(
        "Exact 100x Short Target Bound",
        TARGET_SHORT_LEVERAGE
        == "100",
    )

    check(
        "Authorization Remains Unconsumed",
        runtime_state[
            "authorization_consumed"
        ]
        is False,
    )

    check(
        "Dispatch Remains Uncommitted",
        runtime_state[
            "dispatch_committed"
        ]
        is False,
    )

    check(
        "No Network POST Was Performed",
        COUNTERS[
            "network_post"
        ] == 0,
    )

    check(
        "No Leverage Mutation Was Performed",
        COUNTERS[
            "leverage_mutation"
        ] == 0,
    )

    check(
        "No Real Order Was Sent",
        COUNTERS[
            "real_order"
        ] == 0,
    )

    check(
        "Real Execution Capability Remains Disabled",
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Network POST Capability Remains Disabled",
        NETWORK_POST_ENABLED
        is False,
    )

    check(
        "Leverage Mutation Capability Remains Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    line()

    print(
        f"{VERSION}: VALIDATION COMPLETE ✅",
        flush=True,
    )

    line()

    print(
        f"{VERSION}: "
        f"LIVE LEVERAGE MUTATION READINESS VALIDATED",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"AUTHENTICATED SYMBOL CONFIG READ VALIDATED",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"TARGET LONG LEVERAGE=100x",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"TARGET SHORT LEVERAGE=100x",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"FUTURE MUTATION ENDPOINT="
        f"{FUTURE_LEVERAGE_MUTATION_PATH}",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"NO POST REQUEST WAS SENT",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"NO LEVERAGE MUTATION WAS PERFORMED",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"NO REAL ORDER WAS SENT",
        flush=True,
    )


# =============================================================================
# SECTION 18: HEARTBEAT
# =============================================================================

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        print(
            f"{VERSION}: HEARTBEAT {heartbeat}"
            f" | phase={runtime_state['phase']}"
            f" | authenticated-read="
            f"{runtime_state['authenticated_read_complete']}"
            f" | live-mutation-ready="
            f"{runtime_state['live_mutation_ready']}"
            f" | correction-required="
            f"{runtime_state['correction_required']}"
            f" | network-writes="
            f"{runtime_state['network_writes']}"
            f" | leverage-mutation="
            f"{runtime_state['leverage_mutation']}"
            f" | real-execution="
            f"{runtime_state['real_execution']}"
            f" | current-long="
            f"{runtime_state['current_long_leverage']}x"
            f" | current-short="
            f"{runtime_state['current_short_leverage']}x"
            f" | target-long="
            f"{TARGET_LONG_LEVERAGE}x"
            f" | target-short="
            f"{TARGET_SHORT_LEVERAGE}x"
            f" | generation="
            f"{runtime_state['generation']}"
            f" | recovery-epoch="
            f"{runtime_state['recovery_epoch']}",
            flush=True,
        )

        time.sleep(30)


# =============================================================================
# SECTION 19: PROGRAM ENTRY
# =============================================================================

def main():

    start_health_server()

    try:

        run_validation()

    except Exception as exc:

        runtime_state[
            "phase"
        ] = "READINESS_FAILED"

        runtime_state[
            "last_error"
        ] = str(exc)

        section(
            "R34A VALIDATION FAILED"
        )

        print(
            f"{VERSION}: ERROR={exc}",
            flush=True,
        )

        try:
            persist_state()
        except Exception:
            pass

    heartbeat_loop()


if __name__ == "__main__":
    main()
