# =============================================================================
# R34D - CONTROLLED LEVERAGE CORRECTION ENVELOPE VALIDATION
# =============================================================================
#
# PURPOSE
# -------
# 1. Perform exactly one authenticated READ-ONLY GET against WEEX.
# 2. Observe current BTCUSDT margin / leverage configuration.
# 3. Reconcile observed leverage against the 100x / 100x target.
# 4. Construct the exact V3 leverage-correction POST payload.
# 5. Canonicalize, hash, sign, and bind the correction envelope.
# 6. Create and consume a one-time SYNTHETIC authorization.
# 7. Validate replay rejection.
# 8. Intercept the synthetic dispatch before the network boundary.
# 9. Perform ZERO exchange writes.
# 10. Perform ZERO real leverage mutations.
#
# IMPORTANT
# ---------
# THIS VERSION CANNOT SEND THE LEVERAGE POST.
#
# POST / PUT / PATCH / DELETE TRANSPORTS ARE HARD-BLOCKED.
#
# =============================================================================

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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


# =============================================================================
# R34D PART 1: IMMUTABLE CONFIGURATION
# =============================================================================

VERSION = "R34D"

SYMBOL = "BTCUSDT"

BASE_URL = "https://api-contract.weex.com"

READ_PATH = "/capi/v3/account/symbolConfig"

LEVERAGE_PATH = "/capi/v3/account/leverage"

TARGET_MARGIN_TYPE = "ISOLATED"

TARGET_LONG_LEVERAGE = "100"

TARGET_SHORT_LEVERAGE = "100"

HEALTH_PORT = int(os.getenv("PORT", "10000"))

HTTP_TIMEOUT_SECONDS = 15

HEARTBEAT_SECONDS = 30


# -----------------------------------------------------------------------------
# HARD SAFETY CONSTANTS
# -----------------------------------------------------------------------------

SYNTHETIC_ONLY = True

AUTHENTICATED_READ_ONLY_ENABLED = True

REAL_ORDER_EXECUTION_ENABLED = False

DEMO_ORDER_EXECUTION_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False

MARGIN_MUTATION_ENABLED = False

POSITION_MUTATION_ENABLED = False

ACCOUNT_MUTATION_ENABLED = False

HTTP_POST_ENABLED = False

HTTP_PUT_ENABLED = False

HTTP_PATCH_ENABLED = False

HTTP_DELETE_ENABLED = False


# -----------------------------------------------------------------------------
# ENVIRONMENT CREDENTIALS
# -----------------------------------------------------------------------------

API_KEY = (
    os.getenv("WEEX_API_KEY")
    or os.getenv("API_KEY")
    or ""
).strip()

SECRET_KEY = (
    os.getenv("WEEX_SECRET_KEY")
    or os.getenv("WEEX_API_SECRET")
    or os.getenv("API_SECRET")
    or os.getenv("SECRET_KEY")
    or ""
).strip()

PASSPHRASE = (
    os.getenv("WEEX_PASSPHRASE")
    or os.getenv("API_PASSPHRASE")
    or ""
).strip()


# -----------------------------------------------------------------------------
# TERMINAL STATE
# -----------------------------------------------------------------------------

state = {
    "version": VERSION,
    "phase": "BOOTING",

    "authenticated_get_count": 0,
    "network_write_count": 0,

    "real_order_count": 0,
    "demo_order_count": 0,

    "leverage_mutation_count": 0,
    "margin_mutation_count": 0,
    "position_mutation_count": 0,
    "account_mutation_count": 0,

    "synthetic_dispatch_count": 0,
    "synthetic_authorization_count": 0,
    "authorization_consumed_count": 0,
    "replay_block_count": 0,

    "observed_symbol": None,
    "observed_margin": None,
    "observed_position_mode": None,
    "observed_cross": None,
    "observed_long": None,
    "observed_short": None,

    "correction_required": None,

    "payload_hash": None,
    "envelope_hash": None,
    "authorization_hash": None,
    "receipt_hash": None,

    "authorization_consumed": False,

    "result": "PENDING",
}


# =============================================================================
# OUTPUT HELPERS
# =============================================================================

LINE = "-" * 100


def section(title):
    print(LINE, flush=True)
    print(title, flush=True)
    print(LINE, flush=True)


def check(label, condition):
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"{label:<82} {status}", flush=True)

    if not condition:
        raise RuntimeError(
            f"R34D VALIDATION FAILURE: {label}"
        )


def sha256_text(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def safe_int(value):
    try:
        return int(float(str(value)))
    except Exception:
        return None


# =============================================================================
# R34D PART 2: HEALTH SERVER + CRYPTOGRAPHIC HELPERS
# =============================================================================


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        body = json.dumps(
            {
                "status": "ok",
                "version": VERSION,
                "phase": state["phase"],
                "symbol": SYMBOL,

                "synthetic_only": SYNTHETIC_ONLY,
                "authenticated_read_only": (
                    AUTHENTICATED_READ_ONLY_ENABLED
                ),

                "network_writes_enabled": (
                    EXCHANGE_NETWORK_WRITES_ENABLED
                ),

                "leverage_mutation_enabled": (
                    LEVERAGE_MUTATION_ENABLED
                ),

                "observed_long": state["observed_long"],
                "observed_short": state["observed_short"],

                "target_long": TARGET_LONG_LEVERAGE,
                "target_short": TARGET_SHORT_LEVERAGE,

                "correction_required": (
                    state["correction_required"]
                ),

                "result": state["result"],
            },
            separators=(",", ":"),
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

    def log_message(self, fmt, *args):
        return


def start_health_server():

    def worker():

        server = ThreadingHTTPServer(
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler,
        )

        print(
            f"{VERSION}: HEALTH SERVER LISTENING "
            f"ON PORT {HEALTH_PORT}",
            flush=True,
        )

        server.serve_forever()

    thread = threading.Thread(
        target=worker,
        daemon=True,
    )

    thread.start()


# -----------------------------------------------------------------------------
# WEEX V3 SIGNATURE
#
# Signature:
#
# timestamp
# + METHOD
# + requestPath
# + ("?" + queryString when present)
# + body
#
# HMAC-SHA256 -> Base64
# -----------------------------------------------------------------------------


def generate_signature(
    secret_key,
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):

    method = method.upper()

    message = (
        str(timestamp)
        + method
        + request_path
    )

    if query_string:
        message += "?" + query_string

    if body:
        message += body

    digest = hmac.new(
        secret_key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


def build_authenticated_headers(
    method,
    request_path,
    query_string="",
    body="",
):

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = generate_signature(
        SECRET_KEY,
        timestamp,
        method,
        request_path,
        query_string,
        body,
    )

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "locale": "en-US",
        "User-Agent": f"{VERSION}-read-only-validation",
    }

    return timestamp, signature, headers


# =============================================================================
# AUTHENTICATED READ-ONLY TRANSPORT
# =============================================================================


def authenticated_get_symbol_config():

    if not AUTHENTICATED_READ_ONLY_ENABLED:
        raise RuntimeError(
            "Authenticated read-only mode is disabled."
        )

    if not API_KEY:
        raise RuntimeError(
            "WEEX API key is missing."
        )

    if not SECRET_KEY:
        raise RuntimeError(
            "WEEX secret key is missing."
        )

    if not PASSPHRASE:
        raise RuntimeError(
            "WEEX passphrase is missing."
        )

    query_string = urllib.parse.urlencode(
        {
            "symbol": SYMBOL,
        }
    )

    url = (
        BASE_URL
        + READ_PATH
        + "?"
        + query_string
    )

    _, _, headers = build_authenticated_headers(
        method="GET",
        request_path=READ_PATH,
        query_string=query_string,
        body="",
    )

    request = urllib.request.Request(
        url=url,
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

            state["authenticated_get_count"] += 1

            return json.loads(raw)

    except urllib.error.HTTPError as exc:

        body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"WEEX HTTP {exc.code}: {body}"
        )

    except urllib.error.URLError as exc:

        raise RuntimeError(
            f"WEEX network read error: {exc}"
        )


# =============================================================================
# LIVE CONFIG NORMALIZATION
# =============================================================================


def normalize_symbol_config(response):

    data = response

    # Common direct list:
    #
    # [
    #   {
    #       "symbol": "BTCUSDT",
    #       ...
    #   }
    # ]

    if isinstance(data, list):

        for item in data:

            if (
                isinstance(item, dict)
                and str(
                    item.get("symbol", "")
                ).upper() == SYMBOL
            ):
                return item

        if data and isinstance(data[0], dict):
            return data[0]

    # Some APIs wrap data inside:
    #
    # {"data": [...]}
    #
    # or
    #
    # {"data": {...}}

    if isinstance(data, dict):

        nested = data.get("data")

        if isinstance(nested, list):

            for item in nested:

                if (
                    isinstance(item, dict)
                    and str(
                        item.get("symbol", "")
                    ).upper() == SYMBOL
                ):
                    return item

            if (
                nested
                and isinstance(
                    nested[0],
                    dict,
                )
            ):
                return nested[0]

        if isinstance(nested, dict):
            return nested

        if "symbol" in data:
            return data

    raise RuntimeError(
        "Could not normalize symbol configuration."
    )


# =============================================================================
# WRITE FIREBREAK
# =============================================================================


class WriteTransportBlocked(RuntimeError):
    pass


def blocked_network_write(
    method,
    path,
    body=None,
):

    method = method.upper()

    raise WriteTransportBlocked(
        f"{VERSION}: BLOCKED {method} {path} - "
        "NETWORK WRITES ARE DISABLED"
    )


def http_post(*args, **kwargs):

    if not HTTP_POST_ENABLED:
        raise WriteTransportBlocked(
            f"{VERSION}: HTTP POST DISABLED"
        )

    raise WriteTransportBlocked(
        f"{VERSION}: POST transport unavailable"
    )


def http_put(*args, **kwargs):

    if not HTTP_PUT_ENABLED:
        raise WriteTransportBlocked(
            f"{VERSION}: HTTP PUT DISABLED"
        )

    raise WriteTransportBlocked(
        f"{VERSION}: PUT transport unavailable"
    )


def http_patch(*args, **kwargs):

    if not HTTP_PATCH_ENABLED:
        raise WriteTransportBlocked(
            f"{VERSION}: HTTP PATCH DISABLED"
        )

    raise WriteTransportBlocked(
        f"{VERSION}: PATCH transport unavailable"
    )


def http_delete(*args, **kwargs):

    if not HTTP_DELETE_ENABLED:
        raise WriteTransportBlocked(
            f"{VERSION}: HTTP DELETE DISABLED"
        )

    raise WriteTransportBlocked(
        f"{VERSION}: DELETE transport unavailable"
    )


# =============================================================================
# SYNTHETIC CORRECTION OBJECTS
# =============================================================================


def construct_correction_payload():

    return {
        "symbol": SYMBOL,
        "marginType": TARGET_MARGIN_TYPE,
        "isolatedLongLeverage": (
            TARGET_LONG_LEVERAGE
        ),
        "isolatedShortLeverage": (
            TARGET_SHORT_LEVERAGE
        ),
    }


def construct_synthetic_envelope(
    payload,
):

    body = canonical_json(payload)

    timestamp = str(
        int(time.time() * 1000)
    )

    synthetic_signature = generate_signature(
        SECRET_KEY,
        timestamp,
        "POST",
        LEVERAGE_PATH,
        "",
        body,
    )

    envelope = {
        "version": VERSION,

        "transport": "SYNTHETIC",

        "method": "POST",

        "path": LEVERAGE_PATH,

        "timestamp": timestamp,

        "contentType": "application/json",

        "body": body,

        "payloadHash": sha256_text(body),

        "signature": synthetic_signature,

        "networkTransmissionAllowed": False,

        "exchangeWriteAllowed": False,

        "leverageMutationAllowed": False,
    }

    return envelope


def construct_authorization(
    envelope,
):

    envelope_text = canonical_json(
        envelope
    )

    envelope_hash = sha256_text(
        envelope_text
    )

    authorization = {
        "version": VERSION,

        "authorizationType": (
            "SYNTHETIC_CORRECTION_AUTHORIZATION"
        ),

        "symbol": SYMBOL,

        "method": envelope["method"],

        "path": envelope["path"],

        "payloadHash": envelope[
            "payloadHash"
        ],

        "envelopeHash": envelope_hash,

        "syntheticOnly": True,

        "networkWriteAllowed": False,

        "mutationAllowed": False,

        "consumed": False,
    }

    return authorization


def consume_authorization(
    authorization,
    envelope,
):

    if state["authorization_consumed"]:

        state["replay_block_count"] += 1

        raise RuntimeError(
            "Synthetic authorization replay rejected."
        )

    expected_envelope_hash = sha256_text(
        canonical_json(envelope)
    )

    check(
        "Authorization Symbol Matches Envelope Symbol",
        authorization["symbol"] == SYMBOL,
    )

    check(
        "Authorization Method Matches Envelope Method",
        authorization["method"]
        == envelope["method"],
    )

    check(
        "Authorization Path Matches Envelope Path",
        authorization["path"]
        == envelope["path"],
    )

    check(
        "Authorization Payload Hash Matches Envelope",
        authorization["payloadHash"]
        == envelope["payloadHash"],
    )

    check(
        "Authorization Envelope Hash Matches",
        authorization["envelopeHash"]
        == expected_envelope_hash,
    )

    check(
        "Authorization Is Synthetic Only",
        authorization["syntheticOnly"]
        is True,
    )

    check(
        "Authorization Declares Network Write Disabled",
        authorization["networkWriteAllowed"]
        is False,
    )

    check(
        "Authorization Declares Mutation Disabled",
        authorization["mutationAllowed"]
        is False,
    )

    authorization["consumed"] = True

    state["authorization_consumed"] = True

    state[
        "synthetic_authorization_count"
    ] += 1

    state[
        "authorization_consumed_count"
    ] += 1

    return authorization


def synthetic_dispatch(
    envelope,
    authorization,
):

    if not SYNTHETIC_ONLY:
        raise RuntimeError(
            "Synthetic-only protection is not enabled."
        )

    if EXCHANGE_NETWORK_WRITES_ENABLED:
        raise RuntimeError(
            "Network writes unexpectedly enabled."
        )

    if LEVERAGE_MUTATION_ENABLED:
        raise RuntimeError(
            "Leverage mutation unexpectedly enabled."
        )

    if envelope["method"] != "POST":
        raise RuntimeError(
            "Unexpected correction method."
        )

    if envelope["path"] != LEVERAGE_PATH:
        raise RuntimeError(
            "Unexpected correction endpoint."
        )

    if not authorization["consumed"]:
        raise RuntimeError(
            "Authorization was not consumed."
        )

    if not state["authorization_consumed"]:
        raise RuntimeError(
            "State does not show consumed authorization."
        )

    # -------------------------------------------------------------------------
    # THIS IS THE FINAL FIREBREAK.
    #
    # No urllib POST request exists here.
    # No requests.post() exists here.
    # No socket write exists here.
    #
    # The request is intercepted locally.
    # -------------------------------------------------------------------------

    state[
        "synthetic_dispatch_count"
    ] += 1

    receipt = {
        "version": VERSION,

        "transport": "SYNTHETIC",

        "intercepted": True,

        "transmitted": False,

        "exchangeContactedForWrite": False,

        "networkWritePerformed": False,

        "leverageMutationPerformed": False,

        "method": envelope["method"],

        "path": envelope["path"],

        "payloadHash": envelope[
            "payloadHash"
        ],

        "envelopeHash": authorization[
            "envelopeHash"
        ],

        "authorizationConsumed": True,

        "syntheticDispatchNumber": state[
            "synthetic_dispatch_count"
        ],
    }

    return receipt


# =============================================================================
# R34D PART 3: VALIDATION
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
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED",
        flush=True,
    )

    print(
        f"{VERSION}: STANDARD LIBRARY HTTP ENABLED",
        flush=True,
    )

    print(
        f"{VERSION}: requests PACKAGE NOT REQUIRED",
        flush=True,
    )

    print(
        f"{VERSION}: NETWORK WRITES DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: LEVERAGE MUTATION DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: LIVE LEVERAGE POST DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: CORRECTION ENDPOINT="
        f"{LEVERAGE_PATH}",
        flush=True,
    )

    start_health_server()

    time.sleep(0.05)

    # =========================================================================
    # TEST 1
    # =========================================================================

    section(
        "R34D TEST 1: IMMUTABLE SAFETY CONFIGURATION"
    )

    check(
        "Synthetic Only Is Enabled",
        SYNTHETIC_ONLY is True,
    )

    check(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY_ENABLED
        is True,
    )

    check(
        "Real Order Execution Is Disabled",
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Network Writes Are Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    check(
        "Margin Mutation Is Disabled",
        MARGIN_MUTATION_ENABLED
        is False,
    )

    check(
        "Position Mutation Is Disabled",
        POSITION_MUTATION_ENABLED
        is False,
    )

    check(
        "Account Mutation Is Disabled",
        ACCOUNT_MUTATION_ENABLED
        is False,
    )

    # =========================================================================
    # TEST 2
    # =========================================================================

    section(
        "R34D TEST 2: WRITE TRANSPORT FIREBREAK"
    )

    check(
        "HTTP POST Is Disabled",
        HTTP_POST_ENABLED is False,
    )

    check(
        "HTTP PUT Is Disabled",
        HTTP_PUT_ENABLED is False,
    )

    check(
        "HTTP PATCH Is Disabled",
        HTTP_PATCH_ENABLED is False,
    )

    check(
        "HTTP DELETE Is Disabled",
        HTTP_DELETE_ENABLED is False,
    )

    post_blocked = False

    try:
        http_post(
            LEVERAGE_PATH,
            {},
        )
    except WriteTransportBlocked:
        post_blocked = True

    check(
        "POST Transport Firebreak Rejects Dispatch",
        post_blocked,
    )

    raw_write_blocked = False

    try:
        blocked_network_write(
            "POST",
            LEVERAGE_PATH,
            {},
        )
    except WriteTransportBlocked:
        raw_write_blocked = True

    check(
        "Raw Network Write Firebreak Rejects Dispatch",
        raw_write_blocked,
    )

    check(
        "Network Write Counter Remains Zero",
        state["network_write_count"] == 0,
    )

    # =========================================================================
    # TEST 3
    # =========================================================================

    section(
        "R34D TEST 3: AUTHENTICATED READ CREDENTIAL READINESS"
    )

    check(
        "API Key Is Present",
        bool(API_KEY),
    )

    check(
        "Secret Key Is Present",
        bool(SECRET_KEY),
    )

    check(
        "Passphrase Is Present",
        bool(PASSPHRASE),
    )

    # =========================================================================
    # TEST 4
    # =========================================================================

    section(
        "R34D TEST 4: LIVE READ-ONLY SYMBOL OBSERVATION"
    )

    response = authenticated_get_symbol_config()

    config = normalize_symbol_config(
        response
    )

    state["observed_symbol"] = str(
        config.get(
            "symbol",
            SYMBOL,
        )
    ).upper()

    state["observed_margin"] = str(
        config.get(
            "marginType",
            "",
        )
    ).upper()

    state["observed_position_mode"] = str(
        config.get(
            "separatedType",
            config.get(
                "positionMode",
                "",
            ),
        )
    ).upper()

    state["observed_cross"] = safe_int(
        config.get(
            "crossLeverage"
        )
    )

    state["observed_long"] = safe_int(
        config.get(
            "isolatedLongLeverage"
        )
    )

    state["observed_short"] = safe_int(
        config.get(
            "isolatedShortLeverage"
        )
    )

    check(
        "Authenticated Symbol Configuration Returned",
        isinstance(
            config,
            dict,
        ),
    )

    print(
        f"{VERSION}: OBSERVED SYMBOL="
        f"{state['observed_symbol']}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED MARGIN="
        f"{state['observed_margin']}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED POSITION MODE="
        f"{state['observed_position_mode']}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED CROSS="
        f"{state['observed_cross']}x",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED LONG="
        f"{state['observed_long']}x",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED SHORT="
        f"{state['observed_short']}x",
        flush=True,
    )

    check(
        "Observed Symbol Matches Target Symbol",
        state["observed_symbol"] == SYMBOL,
    )

    check(
        "Observed Margin Type Is Present",
        bool(
            state["observed_margin"]
        ),
    )

    check(
        "Observed Long Leverage Is Present",
        state["observed_long"]
        is not None,
    )

    check(
        "Observed Short Leverage Is Present",
        state["observed_short"]
        is not None,
    )

    check(
        "Exactly One Authenticated GET Was Used",
        state[
            "authenticated_get_count"
        ] == 1,
    )

    check(
        "Network Write Counter Remains Zero",
        state[
            "network_write_count"
        ] == 0,
    )

    # =========================================================================
    # TEST 5
    # =========================================================================

    section(
        "R34D TEST 5: TARGET / OBSERVED RECONCILIATION"
    )

    target_long_int = int(
        TARGET_LONG_LEVERAGE
    )

    target_short_int = int(
        TARGET_SHORT_LEVERAGE
    )

    state["correction_required"] = (
        state["observed_margin"]
        != TARGET_MARGIN_TYPE
        or state["observed_long"]
        != target_long_int
        or state["observed_short"]
        != target_short_int
    )

    print(
        f"{VERSION}: TARGET MARGIN="
        f"{TARGET_MARGIN_TYPE}",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: CORRECTION REQUIRED="
        f"{state['correction_required']}",
        flush=True,
    )

    check(
        "Target Margin Type Is ISOLATED",
        TARGET_MARGIN_TYPE
        == "ISOLATED",
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

    check(
        "Correction Requirement Was Determined",
        isinstance(
            state["correction_required"],
            bool,
        ),
    )

    # =========================================================================
    # TEST 6
    # =========================================================================

    section(
        "R34D TEST 6: EXACT V3 CORRECTION PAYLOAD"
    )

    payload = construct_correction_payload()

    body = canonical_json(
        payload
    )

    payload_hash = sha256_text(
        body
    )

    state["payload_hash"] = (
        payload_hash
    )

    print(
        f"{VERSION}: CORRECTION PAYLOAD="
        f"{body}",
        flush=True,
    )

    print(
        f"{VERSION}: PAYLOAD SHA256="
        f"{payload_hash}",
        flush=True,
    )

    check(
        "Correction Symbol Is BTCUSDT",
        payload["symbol"]
        == SYMBOL,
    )

    check(
        "Correction Margin Type Is ISOLATED",
        payload["marginType"]
        == "ISOLATED",
    )

    check(
        "Correction Long Leverage Is 100x",
        payload[
            "isolatedLongLeverage"
        ] == "100",
    )

    check(
        "Correction Short Leverage Is 100x",
        payload[
            "isolatedShortLeverage"
        ] == "100",
    )

    check(
        "Payload Contains Exactly Four Fields",
        set(payload.keys())
        == {
            "symbol",
            "marginType",
            "isolatedLongLeverage",
            "isolatedShortLeverage",
        },
    )

    # =========================================================================
    # TEST 7
    # =========================================================================

    section(
        "R34D TEST 7: EXACT SYNTHETIC POST ENVELOPE"
    )

    envelope = construct_synthetic_envelope(
        payload
    )

    envelope_hash = sha256_text(
        canonical_json(
            envelope
        )
    )

    state["envelope_hash"] = (
        envelope_hash
    )

    print(
        f"{VERSION}: ENVELOPE METHOD="
        f"{envelope['method']}",
        flush=True,
    )

    print(
        f"{VERSION}: ENVELOPE PATH="
        f"{envelope['path']}",
        flush=True,
    )

    print(
        f"{VERSION}: ENVELOPE SHA256="
        f"{envelope_hash}",
        flush=True,
    )

    check(
        "Envelope Transport Is Synthetic",
        envelope["transport"]
        == "SYNTHETIC",
    )

    check(
        "Envelope Method Is POST",
        envelope["method"]
        == "POST",
    )

    check(
        "Envelope Uses Exact V3 Leverage Endpoint",
        envelope["path"]
        == "/capi/v3/account/leverage",
    )

    check(
        "Envelope Payload Hash Matches Payload",
        envelope["payloadHash"]
        == payload_hash,
    )

    check(
        "Envelope Contains Signature",
        bool(
            envelope["signature"]
        ),
    )

    check(
        "Envelope Declares No Network Transmission",
        envelope[
            "networkTransmissionAllowed"
        ] is False,
    )

    check(
        "Envelope Declares No Exchange Write",
        envelope[
            "exchangeWriteAllowed"
        ] is False,
    )

    check(
        "Envelope Declares No Leverage Mutation",
        envelope[
            "leverageMutationAllowed"
        ] is False,
    )

    # =========================================================================
    # TEST 8
    # =========================================================================

    section(
        "R34D TEST 8: SYNTHETIC SIGNATURE REPRODUCTION"
    )

    reproduced_signature = generate_signature(
        SECRET_KEY,
        envelope["timestamp"],
        envelope["method"],
        envelope["path"],
        "",
        envelope["body"],
    )

    check(
        "Envelope Signature Reproduces Exactly",
        reproduced_signature
        == envelope["signature"],
    )

    check(
        "Signed Body Matches Canonical Payload",
        envelope["body"]
        == body,
    )

    check(
        "Signed Payload Hash Matches Canonical Body",
        sha256_text(
            envelope["body"]
        ) == payload_hash,
    )

    # =========================================================================
    # TEST 9
    # =========================================================================

    section(
        "R34D TEST 9: ONE-TIME SYNTHETIC AUTHORIZATION"
    )

    authorization = construct_authorization(
        envelope
    )

    authorization_text = canonical_json(
        authorization
    )

    authorization_hash = sha256_text(
        authorization_text
    )

    state[
        "authorization_hash"
    ] = authorization_hash

    print(
        f"{VERSION}: AUTHORIZATION SHA256="
        f"{authorization_hash}",
        flush=True,
    )

    check(
        "Authorization Is Initially Unconsumed",
        authorization["consumed"]
        is False,
    )

    check(
        "Authorization Is Synthetic Only",
        authorization["syntheticOnly"]
        is True,
    )

    check(
        "Authorization Network Write Is False",
        authorization[
            "networkWriteAllowed"
        ] is False,
    )

    check(
        "Authorization Mutation Is False",
        authorization[
            "mutationAllowed"
        ] is False,
    )

    authorization = consume_authorization(
        authorization,
        envelope,
    )

    check(
        "Authorization Was Consumed",
        authorization["consumed"]
        is True,
    )

    check(
        "Authorization Consumption Counter Is One",
        state[
            "authorization_consumed_count"
        ] == 1,
    )

    # =========================================================================
    # TEST 10
    # =========================================================================

    section(
        "R34D TEST 10: SYNTHETIC DISPATCH INTERCEPTION"
    )

    receipt = synthetic_dispatch(
        envelope,
        authorization,
    )

    receipt_hash = sha256_text(
        canonical_json(
            receipt
        )
    )

    state["receipt_hash"] = (
        receipt_hash
    )

    print(
        f"{VERSION}: SYNTHETIC RECEIPT SHA256="
        f"{receipt_hash}",
        flush=True,
    )

    check(
        "Synthetic Dispatch Was Intercepted",
        receipt["intercepted"]
        is True,
    )

    check(
        "Synthetic Receipt Confirms No Transmission",
        receipt["transmitted"]
        is False,
    )

    check(
        "Synthetic Receipt Confirms No Exchange Write",
        receipt[
            "exchangeContactedForWrite"
        ] is False,
    )

    check(
        "Synthetic Receipt Confirms No Network Write",
        receipt[
            "networkWritePerformed"
        ] is False,
    )

    check(
        "Synthetic Receipt Confirms No Leverage Mutation",
        receipt[
            "leverageMutationPerformed"
        ] is False,
    )

    check(
        "Synthetic Receipt Preserves Payload Hash",
        receipt["payloadHash"]
        == payload_hash,
    )

    check(
        "Synthetic Dispatch Counter Is One",
        state[
            "synthetic_dispatch_count"
        ] == 1,
    )

    # =========================================================================
    # TEST 11
    # =========================================================================

    section(
        "R34D TEST 11: AUTHORIZATION REPLAY REJECTION"
    )

    replay_rejected = False

    try:

        consume_authorization(
            authorization,
            envelope,
        )

    except RuntimeError:
        replay_rejected = True

    check(
        "Consumed Authorization Replay Is Rejected",
        replay_rejected,
    )

    check(
        "Replay Block Counter Is One",
        state[
            "replay_block_count"
        ] == 1,
    )

    check(
        "Authorization Consumption Counter Remains One",
        state[
            "authorization_consumed_count"
        ] == 1,
    )

    check(
        "Synthetic Dispatch Counter Remains One",
        state[
            "synthetic_dispatch_count"
        ] == 1,
    )

    # =========================================================================
    # TEST 12
    # =========================================================================

    section(
        "R34D TEST 12: TERMINAL WRITE-LOCK COUNTERS"
    )

    check(
        "Authenticated GET Counter Is One",
        state[
            "authenticated_get_count"
        ] == 1,
    )

    check(
        "Network Write Counter Is Zero",
        state[
            "network_write_count"
        ] == 0,
    )

    check(
        "Real Order Counter Is Zero",
        state[
            "real_order_count"
        ] == 0,
    )

    check(
        "Demo Order Counter Is Zero",
        state[
            "demo_order_count"
        ] == 0,
    )

    check(
        "Leverage Mutation Counter Is Zero",
        state[
            "leverage_mutation_count"
        ] == 0,
    )

    check(
        "Margin Mutation Counter Is Zero",
        state[
            "margin_mutation_count"
        ] == 0,
    )

    check(
        "Position Mutation Counter Is Zero",
        state[
            "position_mutation_count"
        ] == 0,
    )

    check(
        "Account Mutation Counter Is Zero",
        state[
            "account_mutation_count"
        ] == 0,
    )

    # =========================================================================
    # TEST 13
    # =========================================================================

    section(
        "R34D TEST 13: FINAL CONTROLLED-CORRECTION SAFETY SEAL"
    )

    check(
        "Synthetic-Only Mode Remains Enabled",
        SYNTHETIC_ONLY is True,
    )

    check(
        "Authenticated Read-Only Remains Enabled",
        AUTHENTICATED_READ_ONLY_ENABLED
        is True,
    )

    check(
        "Real Execution Remains Disabled",
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Network Writes Remain Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "Leverage Mutation Remains Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    check(
        "HTTP POST Remains Disabled",
        HTTP_POST_ENABLED
        is False,
    )

    check(
        "HTTP PUT Remains Disabled",
        HTTP_PUT_ENABLED
        is False,
    )

    check(
        "HTTP PATCH Remains Disabled",
        HTTP_PATCH_ENABLED
        is False,
    )

    check(
        "HTTP DELETE Remains Disabled",
        HTTP_DELETE_ENABLED
        is False,
    )

    check(
        "Exact V3 Leverage Endpoint Remains Bound",
        envelope["path"]
        == LEVERAGE_PATH,
    )

    check(
        "Exact 100x Long Target Remains Bound",
        payload[
            "isolatedLongLeverage"
        ] == "100",
    )

    check(
        "Exact 100x Short Target Remains Bound",
        payload[
            "isolatedShortLeverage"
        ] == "100",
    )

    state["phase"] = (
        "CORRECTION_ENVELOPE_VALIDATED"
    )

    state["result"] = "PASSED"

    # =========================================================================
    # SUMMARY
    # =========================================================================

    section(
        "R34D VALIDATION SUMMARY"
    )

    print(
        f"{VERSION}: AUTHENTICATED GETS="
        f"{state['authenticated_get_count']}",
        flush=True,
    )

    print(
        f"{VERSION}: NETWORK WRITES="
        f"{state['network_write_count']}",
        flush=True,
    )

    print(
        f"{VERSION}: REAL ORDERS="
        f"{state['real_order_count']}",
        flush=True,
    )

    print(
        f"{VERSION}: LEVERAGE MUTATIONS="
        f"{state['leverage_mutation_count']}",
        flush=True,
    )

    print(
        f"{VERSION}: SYNTHETIC AUTHORIZATIONS="
        f"{state['synthetic_authorization_count']}",
        flush=True,
    )

    print(
        f"{VERSION}: AUTHORIZATION CONSUMED="
        f"{state['authorization_consumed_count']}",
        flush=True,
    )

    print(
        f"{VERSION}: REPLAYS BLOCKED="
        f"{state['replay_block_count']}",
        flush=True,
    )

    print(
        f"{VERSION}: SYNTHETIC DISPATCHES="
        f"{state['synthetic_dispatch_count']}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED MARGIN="
        f"{state['observed_margin']}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED LONG="
        f"{state['observed_long']}x",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED SHORT="
        f"{state['observed_short']}x",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: CORRECTION REQUIRED="
        f"{state['correction_required']}",
        flush=True,
    )

    print(
        f"{VERSION}: ENDPOINT="
        f"{LEVERAGE_PATH}",
        flush=True,
    )

    print(
        f"{VERSION}: PAYLOAD HASH="
        f"{state['payload_hash']}",
        flush=True,
    )

    print(
        f"{VERSION}: ENVELOPE HASH="
        f"{state['envelope_hash']}",
        flush=True,
    )

    print(
        f"{VERSION}: AUTHORIZATION HASH="
        f"{state['authorization_hash']}",
        flush=True,
    )

    print(
        f"{VERSION}: RECEIPT HASH="
        f"{state['receipt_hash']}",
        flush=True,
    )

    print(
        f"{VERSION}: PHASE="
        f"{state['phase']}",
        flush=True,
    )

    print(
        f"{VERSION}: RESULT="
        f"{state['result']}",
        flush=True,
    )

    print(
        f"{VERSION}: NO REAL ORDER WAS SENT",
        flush=True,
    )

    print(
        f"{VERSION}: NO EXCHANGE WRITE WAS SENT",
        flush=True,
    )

    print(
        f"{VERSION}: NO LEVERAGE MUTATION WAS PERFORMED",
        flush=True,
    )

    print(
        f"{VERSION}: LIVE LEVERAGE POST REMAINS DISABLED",
        flush=True,
    )

    print(
        LINE,
        flush=True,
    )


# =============================================================================
# R34D PART 4: HEARTBEAT / PERSISTENT RUNTIME
# =============================================================================


def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        print(
            f"{VERSION}: HEARTBEAT {heartbeat}"
            f" | phase={state['phase']}"
            f" | synthetic-only={SYNTHETIC_ONLY}"
            f" | authenticated-read-only="
            f"{AUTHENTICATED_READ_ONLY_ENABLED}"
            f" | authenticated-get="
            f"{state['authenticated_get_count']}"
            f" | synthetic-auth="
            f"{state['synthetic_authorization_count']}"
            f" | authorization-consumed="
            f"{state['authorization_consumed_count']}"
            f" | replay-blocked="
            f"{state['replay_block_count']}"
            f" | synthetic-dispatch="
            f"{state['synthetic_dispatch_count']}"
            f" | real-execution="
            f"{REAL_ORDER_EXECUTION_ENABLED}"
            f" | network-writes="
            f"{EXCHANGE_NETWORK_WRITES_ENABLED}"
            f" | leverage-mutation="
            f"{LEVERAGE_MUTATION_ENABLED}"
            f" | correction-required="
            f"{state['correction_required']}"
            f" | observed-margin="
            f"{state['observed_margin']}"
            f" | observed-long="
            f"{state['observed_long']}x"
            f" | observed-short="
            f"{state['observed_short']}x"
            f" | target-long="
            f"{TARGET_LONG_LEVERAGE}x"
            f" | target-short="
            f"{TARGET_SHORT_LEVERAGE}x",
            flush=True,
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )


def main():

    try:

        run_validation()

    except Exception as exc:

        state["phase"] = (
            "VALIDATION_FAILED"
        )

        state["result"] = "FAILED"

        section(
            "R34D VALIDATION FAILURE"
        )

        print(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        print(
            f"{VERSION}: NETWORK WRITES="
            f"{state['network_write_count']}",
            flush=True,
        )

        print(
            f"{VERSION}: LEVERAGE MUTATIONS="
            f"{state['leverage_mutation_count']}",
            flush=True,
        )

        print(
            f"{VERSION}: NO EXCHANGE WRITE WAS SENT",
            flush=True,
        )

        print(
            f"{VERSION}: NO LEVERAGE MUTATION WAS PERFORMED",
            flush=True,
        )

        print(
            LINE,
            flush=True,
        )

    heartbeat_loop()


if __name__ == "__main__":
    main()
