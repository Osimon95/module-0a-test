# ============================================================
# 0F-4H-R28-UNIT-L
# READ-ONLY STRATEGY / ACCOUNT COMPATIBILITY VALIDATION
#
# PUBLIC WEEX MARKET GET REQUESTS ENABLED
# AUTHENTICATED ACCOUNT GET REQUESTS ENABLED
#
# REAL ORDER TRANSMISSION DISABLED
# DEMO ORDER TRANSMISSION DISABLED
# POST / PUT / PATCH / DELETE BLOCKED LOCALLY
#
# THIS UNIT DOES NOT:
# - PLACE ORDERS
# - CHANGE LEVERAGE
# - CHANGE MARGIN MODE
# - CHANGE POSITION MODE
# - MODIFY ACCOUNT STATE
# ============================================================

print(
    "R28 UNIT L: MAIN.PY ENTERED",
    flush=True,
)

# ============================================================
# IMPORTS
# ============================================================

import asyncio
import base64
import hashlib
import hmac
import json
import os
import signal
import time

from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_DOWN,
)

from urllib.parse import (
    urlencode,
    urlparse,
)

import aiohttp


print(
    "R28 UNIT L: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================
# UNIT IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-L"
MODULE_VERSION = "R28-L"


# ============================================================
# STRATEGY CONSTANTS
# ============================================================

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

MARGIN_ASSET = "USDT"

PLANNED_MARGIN_TYPE = "ISOLATED"

PLANNED_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")

PYRAMID_SIZE_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1

BACKUP_SIZE_PERCENT = Decimal("5")

MAX_BACKUPS = 3

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")


# ============================================================
# ABSOLUTE EXECUTION SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

REAL_ORDER_TRANSMISSION = False
DEMO_ORDER_TRANSMISSION = False

PRIVATE_WRITE_ACCESS = False

AUTHENTICATED_READ_ACCESS = True
PUBLIC_MARKET_READ_ACCESS = True


# ============================================================
# NETWORK CONFIGURATION
# ============================================================

WEEX_HOST = "api-contract.weex.com"

BASE_URL = "https://api-contract.weex.com"


# ============================================================
# ALLOWED PUBLIC GET PATHS
# ============================================================

PUBLIC_GET_ALLOWLIST = {
    "/capi/v3/market/symbolPrice",
    "/capi/v3/market/exchangeInfo",
}


# ============================================================
# ALLOWED AUTHENTICATED GET PATHS
# ============================================================

PRIVATE_GET_ALLOWLIST = {
    "/capi/v3/account/balance",
    "/capi/v3/account/position/allPosition",
    "/capi/v3/account/symbolConfig",
}


# ============================================================
# ABSOLUTELY BLOCKED ORDER PATHS
# ============================================================

REAL_ORDER_PATHS = {
    "/capi/v3/order",
    "/capi/v3/order/placeOrder",
}

DEMO_ORDER_PATHS = {
    "/capi/v3/sim/order",
}


# ============================================================
# API CREDENTIALS
# ============================================================

API_KEY = (
    os.getenv("WEEX_API_KEY")
    or os.getenv("API_KEY")
    or ""
).strip()

API_SECRET = (
    os.getenv("WEEX_API_SECRET")
    or os.getenv("API_SECRET")
    or ""
).strip()

API_PASSPHRASE = (
    os.getenv("WEEX_API_PASSPHRASE")
    or os.getenv("API_PASSPHRASE")
    or ""
).strip()


# ============================================================
# TRANSPORT AUDIT COUNTERS
# ============================================================

AUDIT = {
    "local_post_attempts": 0,
    "local_post_blocks": 0,

    "local_put_attempts": 0,
    "local_put_blocks": 0,

    "local_patch_attempts": 0,
    "local_patch_blocks": 0,

    "local_delete_attempts": 0,
    "local_delete_blocks": 0,

    "network_gets": 0,
    "network_writes": 0,

    "network_posts": 0,
    "network_puts": 0,
    "network_patches": 0,
    "network_deletes": 0,

    "real_order_network_transmissions": 0,
    "demo_order_network_transmissions": 0,
}


# ============================================================
# RESULT STORAGE
# ============================================================

RESULTS = []

READINESS_BLOCKERS = []

READINESS_WARNINGS = []


# ============================================================
# BASIC UTILITIES
# ============================================================

def d(value, default="0"):
    try:
        if value is None:
            return Decimal(default)

        return Decimal(str(value))

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return Decimal(default)


def decimal_text(value):
    if not isinstance(value, Decimal):
        value = d(value)

    text = format(
        value,
        "f",
    )

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    if text in {
        "",
        "-0",
    }:
        return "0"

    return text


def percent_of(
    value,
    percent,
):
    return (
        value
        * percent
        / Decimal("100")
    )


def floor_to_precision(
    value,
    precision,
):
    precision = int(precision)

    quantum = Decimal(
        "1"
    ).scaleb(
        -precision
    )

    return value.quantize(
        quantum,
        rounding=ROUND_DOWN,
    )


def pass_fail(
    label,
    passed,
):
    icon = (
        "✅ PASS"
        if passed
        else "❌ FAIL"
    )

    print(
        f"{label:<62} {icon}",
        flush=True,
    )

    RESULTS.append(
        (
            label,
            bool(passed),
        )
    )

    return bool(passed)


def warning(
    message,
):
    print(
        f"⚠️ {message}",
        flush=True,
    )

    READINESS_WARNINGS.append(
        message
    )


def blocker(
    message,
):
    print(
        f"🚫 READINESS BLOCKER: {message}",
        flush=True,
    )

    READINESS_BLOCKERS.append(
        message
    )


# ============================================================
# RESPONSE NORMALIZATION
# ============================================================

def unwrap_payload(payload):
    if not isinstance(
        payload,
        dict,
    ):
        return payload

    if "data" in payload:
        code = payload.get(
            "code"
        )

        success_codes = {
            None,
            0,
            "0",
            "00000",
            200,
            "200",
        }

        if (
            code not in success_codes
            and payload.get("data") is None
        ):
            raise RuntimeError(
                "WEEX API ERROR: "
                + json.dumps(
                    payload,
                    default=str,
                )
            )

        return payload.get(
            "data"
        )

    return payload


def find_symbol_record(
    payload,
    symbol,
):
    payload = unwrap_payload(
        payload
    )

    if isinstance(
        payload,
        dict,
    ):
        if (
            str(
                payload.get(
                    "symbol",
                    ""
                )
            ).upper()
            == symbol.upper()
        ):
            return payload

        for key in (
            "symbols",
            "list",
            "rows",
        ):
            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                for item in value:
                    if (
                        isinstance(
                            item,
                            dict,
                        )
                        and str(
                            item.get(
                                "symbol",
                                ""
                            )
                        ).upper()
                        == symbol.upper()
                    ):
                        return item

    if isinstance(
        payload,
        list,
    ):
        for item in payload:
            if (
                isinstance(
                    item,
                    dict,
                )
                and str(
                    item.get(
                        "symbol",
                        ""
                    )
                ).upper()
                == symbol.upper()
            ):
                return item

    return None


def find_asset_record(
    payload,
    asset,
):
    payload = unwrap_payload(
        payload
    )

    if isinstance(
        payload,
        dict,
    ):
        if (
            str(
                payload.get(
                    "asset",
                    ""
                )
            ).upper()
            == asset.upper()
        ):
            return payload

        for key in (
            "balances",
            "assets",
            "list",
        ):
            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                for item in value:
                    if (
                        isinstance(
                            item,
                            dict,
                        )
                        and str(
                            item.get(
                                "asset",
                                ""
                            )
                        ).upper()
                        == asset.upper()
                    ):
                        return item

    if isinstance(
        payload,
        list,
    ):
        for item in payload:
            if (
                isinstance(
                    item,
                    dict,
                )
                and str(
                    item.get(
                        "asset",
                        ""
                    )
                ).upper()
                == asset.upper()
            ):
                return item

    return None


# ============================================================
# PRIVATE REQUEST SIGNING
# ============================================================

def generate_signature(
    timestamp,
    method,
    path,
    query_string="",
    body="",
):
    method = method.upper()

    if query_string:
        message = (
            str(timestamp)
            + method
            + path
            + "?"
            + query_string
            + body
        )

    else:
        message = (
            str(timestamp)
            + method
            + path
            + body
        )

    digest = hmac.new(
        API_SECRET.encode(
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


def private_headers(
    method,
    path,
    query_string="",
):
    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = generate_signature(
        timestamp=timestamp,
        method=method,
        path=path,
        query_string=query_string,
        body="",
    )

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
    }


# ============================================================
# LOCKED TRANSPORT
# ============================================================

class LockedTransport:

    def __init__(
        self,
        session,
    ):
        self.session = session

    @staticmethod
    def validate_host(
        url,
    ):
        parsed = urlparse(
            url
        )

        if (
            parsed.scheme != "https"
            or parsed.hostname != WEEX_HOST
        ):
            raise PermissionError(
                "ARBITRARY EXTERNAL HOST REJECTED"
            )

    async def request(
        self,
        method,
        path,
        params=None,
        authenticated=False,
    ):
        method = method.upper()

        # --------------------------------------------
        # WRITE METHODS ARE BLOCKED BEFORE TRANSPORT
        # --------------------------------------------

        if method == "POST":
            AUDIT[
                "local_post_attempts"
            ] += 1

            AUDIT[
                "local_post_blocks"
            ] += 1

            raise PermissionError(
                "POST REJECTED BEFORE TRANSPORT"
            )

        if method == "PUT":
            AUDIT[
                "local_put_attempts"
            ] += 1

            AUDIT[
                "local_put_blocks"
            ] += 1

            raise PermissionError(
                "PUT REJECTED BEFORE TRANSPORT"
            )

        if method == "PATCH":
            AUDIT[
                "local_patch_attempts"
            ] += 1

            AUDIT[
                "local_patch_blocks"
            ] += 1

            raise PermissionError(
                "PATCH REJECTED BEFORE TRANSPORT"
            )

        if method == "DELETE":
            AUDIT[
                "local_delete_attempts"
            ] += 1

            AUDIT[
                "local_delete_blocks"
            ] += 1

            raise PermissionError(
                "DELETE REJECTED BEFORE TRANSPORT"
            )

        if method != "GET":
            raise PermissionError(
                "ONLY GET IS PERMITTED"
            )

        # --------------------------------------------
        # GET PATH ALLOWLIST
        # --------------------------------------------

        if authenticated:
            if path not in PRIVATE_GET_ALLOWLIST:
                raise PermissionError(
                    "UNALLOWLISTED PRIVATE GET REJECTED LOCALLY"
                )

        else:
            if path not in PUBLIC_GET_ALLOWLIST:
                raise PermissionError(
                    "UNALLOWLISTED PUBLIC GET REJECTED LOCALLY"
                )

        params = (
            params
            if params is not None
            else {}
        )

        query_string = urlencode(
            params
        )

        url = (
            BASE_URL
            + path
        )

        if query_string:
            url += (
                "?"
                + query_string
            )

        self.validate_host(
            url
        )

        headers = {
            "Content-Type": "application/json",
        }

        if authenticated:
            if not (
                API_KEY
                and API_SECRET
                and API_PASSPHRASE
            ):
                raise RuntimeError(
                    "API CREDENTIALS MISSING"
                )

            headers = private_headers(
                method="GET",
                path=path,
                query_string=query_string,
            )

        print(
            (
                "R28 UNIT L: "
                + (
                    "AUTHENTICATED GET"
                    if authenticated
                    else "PUBLIC GET"
                )
                + " -> "
                + path
            ),
            flush=True,
        )

        async with self.session.get(
            url,
            headers=headers,
            timeout=aiohttp.ClientTimeout(
                total=20
            ),
        ) as response:

            text = await response.text()

            AUDIT[
                "network_gets"
            ] += 1

            if (
                response.status
                < 200
                or response.status
                >= 300
            ):
                raise RuntimeError(
                    f"HTTP {response.status}: {text[:500]}"
                )

            try:
                return json.loads(
                    text
                )

            except json.JSONDecodeError:
                raise RuntimeError(
                    "NON-JSON RESPONSE: "
                    + text[:500]
                )


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    reader,
    writer,
):
    try:
        await reader.read(
            1024
        )

        body = (
            "R28 UNIT L ACTIVE\n"
            "READ ONLY\n"
            "NETWORK WRITES LOCKED\n"
        )

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
            + body
        )

        writer.write(
            response.encode(
                "utf-8"
            )
        )

        await writer.drain()

    except Exception:
        pass

    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


async def start_health_server():
    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    server = await asyncio.start_server(
        health_handler,
        host="0.0.0.0",
        port=port,
    )

    print(
        f"R28 UNIT L: HEALTH SERVER ACTIVE ON PORT {port}",
        flush=True,
    )

    return server


# ============================================================
# SAFETY TEST HELPERS
# ============================================================

async def expect_blocked(
    coro_factory,
):
    try:
        await coro_factory()

    except PermissionError:
        return True

    except Exception:
        return False

    return False


# ============================================================
# SAFETY GATES
# ============================================================

async def run_safety_gates(
    transport,
):
    print(
        "R28 UNIT L SAFETY GATES",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    pass_fail(
        "Live Execution Disabled",
        LIVE_ORDER_EXECUTION is False,
    )

    pass_fail(
        "Demo Execution Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    pass_fail(
        "Real Order Transmission Disabled",
        REAL_ORDER_TRANSMISSION is False,
    )

    pass_fail(
        "Demo Order Transmission Disabled",
        DEMO_ORDER_TRANSMISSION is False,
    )

    pass_fail(
        "Private Write Access Disabled",
        PRIVATE_WRITE_ACCESS is False,
    )

    pass_fail(
        "Authenticated Read Access Enabled",
        AUTHENTICATED_READ_ACCESS is True,
    )

    pass_fail(
        "Public Market Read Access Enabled",
        PUBLIC_MARKET_READ_ACCESS is True,
    )

    pass_fail(
        "Private GET Allowlist Locked",
        len(
            PRIVATE_GET_ALLOWLIST
        ) == 3,
    )

    pass_fail(
        "Public GET Allowlist Locked",
        len(
            PUBLIC_GET_ALLOWLIST
        ) == 2,
    )

    pass_fail(
        "WEEX Host Locked",
        WEEX_HOST
        == "api-contract.weex.com",
    )

    credentials_present = bool(
        API_KEY
        and API_SECRET
        and API_PASSPHRASE
    )

    pass_fail(
        "API Credentials Present",
        credentials_present,
    )

    # --------------------------------------------
    # GENERIC POST BLOCK
    # --------------------------------------------

    generic_post_blocked = await expect_blocked(
        lambda: transport.request(
            "POST",
            "/capi/v3/example",
        )
    )

    pass_fail(
        "Generic POST Rejected Before Transport",
        generic_post_blocked,
    )

    # --------------------------------------------
    # PUT BLOCK
    # --------------------------------------------

    put_blocked = await expect_blocked(
        lambda: transport.request(
            "PUT",
            "/capi/v3/example",
        )
    )

    pass_fail(
        "PUT Rejected Before Transport",
        put_blocked,
    )

    # --------------------------------------------
    # PATCH BLOCK
    # --------------------------------------------

    patch_blocked = await expect_blocked(
        lambda: transport.request(
            "PATCH",
            "/capi/v3/example",
        )
    )

    pass_fail(
        "PATCH Rejected Before Transport",
        patch_blocked,
    )

    # --------------------------------------------
    # DELETE BLOCK
    # --------------------------------------------

    delete_blocked = await expect_blocked(
        lambda: transport.request(
            "DELETE",
            "/capi/v3/example",
        )
    )

    pass_fail(
        "DELETE Rejected Before Transport",
        delete_blocked,
    )

    # --------------------------------------------
    # REAL ORDER POST BLOCK
    # --------------------------------------------

    real_order_blocked = await expect_blocked(
        lambda: transport.request(
            "POST",
            "/capi/v3/order",
        )
    )

    pass_fail(
        "Real Order POST Rejected Before Transport",
        real_order_blocked,
    )

    # --------------------------------------------
    # DEMO ORDER POST BLOCK
    # --------------------------------------------

    demo_order_blocked = await expect_blocked(
        lambda: transport.request(
            "POST",
            "/capi/v3/sim/order",
        )
    )

    pass_fail(
        "Demo Order POST Rejected Before Transport",
        demo_order_blocked,
    )

    # --------------------------------------------
    # PRIVATE GET ALLOWLIST TEST
    # --------------------------------------------

    private_get_blocked = await expect_blocked(
        lambda: transport.request(
            "GET",
            "/capi/v3/account/notAllowed",
            authenticated=True,
        )
    )

    pass_fail(
        "Unallowlisted Private GET Rejected Locally",
        private_get_blocked,
    )

    # --------------------------------------------
    # EXTERNAL HOST CHECK
    # --------------------------------------------

    external_blocked = False

    try:
        transport.validate_host(
            "https://example.com/"
        )

    except PermissionError:
        external_blocked = True

    pass_fail(
        "Arbitrary External Host Rejected",
        external_blocked,
    )


# ============================================================
# LIVE READ-ONLY DATA ACQUISITION
# ============================================================

async def get_market_price(
    transport,
):
    payload = await transport.request(
        "GET",
        "/capi/v3/market/symbolPrice",
        params={
            "symbol": SYMBOL,
        },
        authenticated=False,
    )

    payload = unwrap_payload(
        payload
    )

    item = find_symbol_record(
        payload,
        SYMBOL,
    )

    if item is None:
        if isinstance(
            payload,
            dict,
        ):
            item = payload

        elif (
            isinstance(
                payload,
                list,
            )
            and payload
            and isinstance(
                payload[0],
                dict,
            )
        ):
            item = payload[0]

    if not isinstance(
        item,
        dict,
    ):
        raise RuntimeError(
            "SYMBOL PRICE RECORD NOT FOUND"
        )

    for key in (
        "price",
        "markPrice",
        "symbolPrice",
        "indexPrice",
    ):
        value = item.get(
            key
        )

        if value is not None:
            price = d(
                value
            )

            if price > 0:
                return price

    raise RuntimeError(
        "VALID SYMBOL PRICE NOT FOUND"
    )


async def get_exchange_info(
    transport,
):
    payload = await transport.request(
        "GET",
        "/capi/v3/market/exchangeInfo",
        params={
            "symbol": SYMBOL,
        },
        authenticated=False,
    )

    item = find_symbol_record(
        payload,
        SYMBOL,
    )

    if item is None:
        raise RuntimeError(
            "EXCHANGE SYMBOL INFORMATION NOT FOUND"
        )

    return item


async def get_usdt_balance(
    transport,
):
    payload = await transport.request(
        "GET",
        "/capi/v3/account/balance",
        authenticated=True,
    )

    item = find_asset_record(
        payload,
        MARGIN_ASSET,
    )

    if item is None:
        raise RuntimeError(
            "USDT BALANCE RECORD NOT FOUND"
        )

    return item


async def get_positions(
    transport,
):
    payload = await transport.request(
        "GET",
        "/capi/v3/account/position/allPosition",
        authenticated=True,
    )

    payload = unwrap_payload(
        payload
    )

    if payload is None:
        return []

    if isinstance(
        payload,
        list,
    ):
        return payload

    if isinstance(
        payload,
        dict,
    ):
        for key in (
            "positions",
            "list",
            "rows",
        ):
            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                return value

    raise RuntimeError(
        "POSITION RESPONSE STRUCTURE NOT RECOGNIZED"
    )


async def get_symbol_config(
    transport,
):
    payload = await transport.request(
        "GET",
        "/capi/v3/account/symbolConfig",
        params={
            "symbol": SYMBOL,
        },
        authenticated=True,
    )

    item = find_symbol_record(
        payload,
        SYMBOL,
    )

    if item is None:
        raise RuntimeError(
            "SYMBOL CONFIGURATION NOT FOUND"
        )

    return item


# ============================================================
# STRATEGY COMPATIBILITY AUDIT
# ============================================================

def audit_strategy_compatibility(
    mark_price,
    exchange_info,
    balance_record,
    positions,
    symbol_config,
):
    print()
    print(
        "R28 UNIT L READ-ONLY STRATEGY COMPATIBILITY",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    # ========================================================
    # ACCOUNT BALANCE
    # ========================================================

    total_balance = d(
        balance_record.get(
            "balance"
        )
    )

    available_balance = d(
        balance_record.get(
            "availableBalance",
            balance_record.get(
                "available",
                "0",
            ),
        )
    )

    frozen_balance = d(
        balance_record.get(
            "frozen"
        )
    )

    unrealized_pnl = d(
        balance_record.get(
            "unrealizePnl",
            balance_record.get(
                "unrealizedPnl",
                "0",
            ),
        )
    )

    print(
        f"R28 UNIT L: {MARGIN_ASSET} BALANCE = "
        f"{decimal_text(total_balance)}",
        flush=True,
    )

    print(
        f"R28 UNIT L: {MARGIN_ASSET} AVAILABLE = "
        f"{decimal_text(available_balance)}",
        flush=True,
    )

    print(
        f"R28 UNIT L: {MARGIN_ASSET} FROZEN = "
        f"{decimal_text(frozen_balance)}",
        flush=True,
    )

    print(
        "R28 UNIT L: ACCOUNT UNREALIZED PNL = "
        f"{decimal_text(unrealized_pnl)}",
        flush=True,
    )

    pass_fail(
        "Available Balance Is Positive",
        available_balance > 0,
    )

    # ========================================================
    # MARKET PRICE
    # ========================================================

    print(
        f"R28 UNIT L: {SYMBOL} MARK PRICE = "
        f"{decimal_text(mark_price)}",
        flush=True,
    )

    pass_fail(
        "Market Price Is Positive",
        mark_price > 0,
    )

    # ========================================================
    # EXCHANGE SYMBOL RULES
    # ========================================================

    exchange_symbol = str(
        exchange_info.get(
            "symbol",
            ""
        )
    ).upper()

    price_precision = int(
        exchange_info.get(
            "pricePrecision",
            0,
        )
    )

    quantity_precision = int(
        exchange_info.get(
            "quantityPrecision",
            0,
        )
    )

    contract_value = d(
        exchange_info.get(
            "contractVal",
            "0",
        )
    )

    min_leverage = d(
        exchange_info.get(
            "minLeverage",
            "0",
        )
    )

    max_leverage = d(
        exchange_info.get(
            "maxLeverage",
            "0",
        )
    )

    min_order_size = d(
        exchange_info.get(
            "minOrderSize",
            "0",
        )
    )

    max_order_size = d(
        exchange_info.get(
            "maxOrderSize",
            "0",
        )
    )

    max_position_size = d(
        exchange_info.get(
            "maxPositionSize",
            "0",
        )
    )

    market_open_limit = d(
        exchange_info.get(
            "marketOpenLimitSize",
            "0",
        )
    )

    print()
    print(
        "R28 UNIT L LIVE EXCHANGE CONSTRAINTS:",
        flush=True,
    )

    print(
        f"  Symbol = {exchange_symbol}",
        flush=True,
    )

    print(
        f"  Price Precision = {price_precision}",
        flush=True,
    )

    print(
        f"  Quantity Precision = {quantity_precision}",
        flush=True,
    )

    print(
        f"  Contract Value = {decimal_text(contract_value)}",
        flush=True,
    )

    print(
        f"  Minimum Order Size = {decimal_text(min_order_size)}",
        flush=True,
    )

    print(
        f"  Maximum Order Size = {decimal_text(max_order_size)}",
        flush=True,
    )

    print(
        f"  Minimum Leverage = {decimal_text(min_leverage)}x",
        flush=True,
    )

    print(
        f"  Maximum Leverage = {decimal_text(max_leverage)}x",
        flush=True,
    )

    pass_fail(
        "Exchange Symbol Matches Target",
        exchange_symbol == SYMBOL,
    )

    pass_fail(
        "Quantity Precision Valid",
        quantity_precision >= 0,
    )

    pass_fail(
        "Minimum Order Size Valid",
        min_order_size > 0,
    )

    pass_fail(
        "Exchange Leverage Range Valid",
        (
            min_leverage > 0
            and max_leverage >= min_leverage
        ),
    )

    planned_leverage_supported = (
        min_leverage
        <= PLANNED_LEVERAGE
        <= max_leverage
    )

    pass_fail(
        "Planned 100x Within Exchange Leverage Range",
        planned_leverage_supported,
    )

    if not planned_leverage_supported:
        blocker(
            "Planned 100x leverage is outside the exchange "
            "leverage range."
        )

    # ========================================================
    # ACCOUNT SYMBOL CONFIGURATION
    # ========================================================

    observed_margin_type = str(
        symbol_config.get(
            "marginType",
            ""
        )
    ).upper()

    position_mode = str(
        symbol_config.get(
            "separatedType",
            symbol_config.get(
                "positionMode",
                "",
            ),
        )
    ).upper()

    cross_leverage = d(
        symbol_config.get(
            "crossLeverage",
            "0",
        )
    )

    isolated_long_leverage = d(
        symbol_config.get(
            "isolatedLongLeverage",
            "0",
        )
    )

    isolated_short_leverage = d(
        symbol_config.get(
            "isolatedShortLeverage",
            "0",
        )
    )

    print()
    print(
        "R28 UNIT L ACCOUNT SYMBOL CONFIG:",
        flush=True,
    )

    print(
        f"  Margin Type = {observed_margin_type}",
        flush=True,
    )

    print(
        f"  Position Mode = {position_mode}",
        flush=True,
    )

    print(
        f"  Cross Leverage = {decimal_text(cross_leverage)}x",
        flush=True,
    )

    print(
        "  Isolated Long Leverage = "
        f"{decimal_text(isolated_long_leverage)}x",
        flush=True,
    )

    print(
        "  Isolated Short Leverage = "
        f"{decimal_text(isolated_short_leverage)}x",
        flush=True,
    )

    margin_match = (
        observed_margin_type
        == PLANNED_MARGIN_TYPE
    )

    pass_fail(
        "Observed Margin Type Matches Strategy",
        margin_match,
    )

    if not margin_match:
        blocker(
            "Account margin mode does not match planned ISOLATED mode."
        )

    position_mode_recognized = (
        position_mode
        in {
            "COMBINED",
            "SEPARATED",
        }
    )

    pass_fail(
        "Position Mode Recognized",
        position_mode_recognized,
    )

    if not position_mode_recognized:
        blocker(
            "WEEX position mode is not recognized."
        )

    # ========================================================
    # CURRENT 100X CONFIGURATION CHECK
    # ========================================================

    long_100_ready = (
        isolated_long_leverage
        == PLANNED_LEVERAGE
    )

    short_100_ready = (
        isolated_short_leverage
        == PLANNED_LEVERAGE
    )

    print()
    print(
        "R28 UNIT L LEVERAGE READINESS:",
        flush=True,
    )

    print(
        f"  Planned Leverage = {decimal_text(PLANNED_LEVERAGE)}x",
        flush=True,
    )

    print(
        "  Current Isolated Long = "
        f"{decimal_text(isolated_long_leverage)}x",
        flush=True,
    )

    print(
        "  Current Isolated Short = "
        f"{decimal_text(isolated_short_leverage)}x",
        flush=True,
    )

    if long_100_ready:
        print(
            "  Long 100x readiness = ✅ READY",
            flush=True,
        )

    else:
        print(
            "  Long 100x readiness = ⚠️ NOT CONFIGURED",
            flush=True,
        )

    if short_100_ready:
        print(
            "  Short 100x readiness = ✅ READY",
            flush=True,
        )

    else:
        print(
            "  Short 100x readiness = ⚠️ NOT CONFIGURED",
            flush=True,
        )

    if not long_100_ready:
        blocker(
            "Isolated LONG leverage is not currently configured "
            "to the planned 100x."
        )

    if not short_100_ready:
        blocker(
            "Isolated SHORT leverage is not currently configured "
            "to the planned 100x."
        )

    # ========================================================
    # POSITION RECONCILIATION
    # ========================================================

    active_symbol_positions = []

    for position in positions:

        if not isinstance(
            position,
            dict,
        ):
            continue

        position_symbol = str(
            position.get(
                "symbol",
                ""
            )
        ).upper()

        size = d(
            position.get(
                "size",
                position.get(
                    "positionAmt",
                    "0",
                ),
            )
        )

        if (
            position_symbol == SYMBOL
            and size != 0
        ):
            active_symbol_positions.append(
                position
            )

    print()
    print(
        f"R28 UNIT L: POSITION RECORDS = {len(positions)}",
        flush=True,
    )

    print(
        f"R28 UNIT L: ACTIVE {SYMBOL} POSITIONS = "
        f"{len(active_symbol_positions)}",
        flush=True,
    )

    no_active_position = (
        len(
            active_symbol_positions
        )
        == 0
    )

    pass_fail(
        "No Existing Target-Symbol Position Conflict",
        no_active_position,
    )

    if not no_active_position:
        blocker(
            f"An active {SYMBOL} position already exists."
        )

    # ========================================================
    # STRATEGY FUND ALLOCATION
    # ========================================================

    initial_margin = percent_of(
        available_balance,
        INITIAL_ENTRY_PERCENT,
    )

    pyramid_margin_each = percent_of(
        available_balance,
        PYRAMID_SIZE_PERCENT,
    )

    total_pyramid_margin = (
        pyramid_margin_each
        * Decimal(
            MAX_PYRAMID_ADDS
        )
    )

    backup_margin_each = percent_of(
        available_balance,
        BACKUP_SIZE_PERCENT,
    )

    total_backup_margin = (
        backup_margin_each
        * Decimal(
            MAX_BACKUPS
        )
    )

    planned_total_margin = (
        initial_margin
        + total_pyramid_margin
        + total_backup_margin
    )

    maximum_allowed_margin = percent_of(
        available_balance,
        MAX_FUND_EXPOSURE_PERCENT,
    )

    planned_total_percent = (
        INITIAL_ENTRY_PERCENT
        + (
            PYRAMID_SIZE_PERCENT
            * Decimal(
                MAX_PYRAMID_ADDS
            )
        )
        + (
            BACKUP_SIZE_PERCENT
            * Decimal(
                MAX_BACKUPS
            )
        )
    )

    print()
    print(
        "R28 UNIT L STRATEGY FUND ALLOCATION:",
        flush=True,
    )

    print(
        f"  Available Balance = "
        f"{decimal_text(available_balance)} USDT",
        flush=True,
    )

    print(
        f"  Initial Entry = {decimal_text(INITIAL_ENTRY_PERCENT)}%",
        flush=True,
    )

    print(
        f"  Initial Margin Budget = "
        f"{decimal_text(initial_margin)} USDT",
        flush=True,
    )

    print(
        f"  Pyramid Adds = {MAX_PYRAMID_ADDS}",
        flush=True,
    )

    print(
        f"  Pyramid Size Each = "
        f"{decimal_text(PYRAMID_SIZE_PERCENT)}%",
        flush=True,
    )

    print(
        f"  Backup Entries = {MAX_BACKUPS}",
        flush=True,
    )

    print(
        f"  Backup Size Each = "
        f"{decimal_text(BACKUP_SIZE_PERCENT)}%",
        flush=True,
    )

    print(
        f"  Maximum Strategy Allocation = "
        f"{decimal_text(planned_total_percent)}%",
        flush=True,
    )

    print(
        f"  Strategy Exposure Limit = "
        f"{decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%",
        flush=True,
    )

    print(
        f"  Planned Maximum Margin = "
        f"{decimal_text(planned_total_margin)} USDT",
        flush=True,
    )

    print(
        f"  Allowed Maximum Margin = "
        f"{decimal_text(maximum_allowed_margin)} USDT",
        flush=True,
    )

    fund_exposure_ok = (
        planned_total_margin
        <= maximum_allowed_margin
    )

    pass_fail(
        "Strategy Allocation Within 35% Fund Exposure Limit",
        fund_exposure_ok,
    )

    if not fund_exposure_ok:
        blocker(
            "Strategy allocation exceeds the configured "
            "35% fund exposure ceiling."
        )

    # ========================================================
    # HYPOTHETICAL INITIAL ENTRY CALCULATION
    #
    # CALCULATION ONLY.
    # NO ORDER OBJECT IS CREATED.
    # NO ORDER ENDPOINT IS CALLED.
    # ========================================================

    planned_initial_notional = (
        initial_margin
        * PLANNED_LEVERAGE
    )

    if mark_price > 0:
        raw_quantity = (
            planned_initial_notional
            / mark_price
        )

    else:
        raw_quantity = Decimal("0")

    rounded_quantity = floor_to_precision(
        raw_quantity,
        quantity_precision,
    )

    rounded_notional = (
        rounded_quantity
        * mark_price
    )

    hypothetical_margin_used = (
        rounded_notional
        / PLANNED_LEVERAGE
        if PLANNED_LEVERAGE > 0
        else Decimal("0")
    )

    print()
    print(
        "R28 UNIT L HYPOTHETICAL INITIAL ENTRY:",
        flush=True,
    )

    print(
        "  CALCULATION ONLY — NO ORDER WILL BE SENT",
        flush=True,
    )

    print(
        f"  Entry Margin Budget = "
        f"{decimal_text(initial_margin)} USDT",
        flush=True,
    )

    print(
        f"  Planned Leverage = "
        f"{decimal_text(PLANNED_LEVERAGE)}x",
        flush=True,
    )

    print(
        f"  Planned Notional = "
        f"{decimal_text(planned_initial_notional)} USDT",
        flush=True,
    )

    print(
        f"  Market Price = "
        f"{decimal_text(mark_price)}",
        flush=True,
    )

    print(
        f"  Raw Quantity = "
        f"{decimal_text(raw_quantity)} BTC",
        flush=True,
    )

    print(
        f"  Rounded Quantity = "
        f"{decimal_text(rounded_quantity)} BTC",
        flush=True,
    )

    print(
        f"  Rounded Notional = "
        f"{decimal_text(rounded_notional)} USDT",
        flush=True,
    )

    print(
        f"  Hypothetical Margin Used = "
        f"{decimal_text(hypothetical_margin_used)} USDT",
        flush=True,
    )

    quantity_meets_minimum = (
        rounded_quantity
        >= min_order_size
    )

    pass_fail(
        "Calculated Initial Quantity Meets Minimum Order Size",
        quantity_meets_minimum,
    )

    if not quantity_meets_minimum:
        blocker(
            "Calculated 5% initial entry is below WEEX "
            "minimum order size."
        )

    if max_order_size > 0:
        within_max_order = (
            rounded_quantity
            <= max_order_size
        )

    else:
        within_max_order = True

    pass_fail(
        "Calculated Initial Quantity Within Maximum Order Size",
        within_max_order,
    )

    if not within_max_order:
        blocker(
            "Calculated initial quantity exceeds WEEX "
            "maximum order size."
        )

    if market_open_limit > 0:
        within_market_open_limit = (
            rounded_quantity
            <= market_open_limit
        )

    else:
        within_market_open_limit = True

    pass_fail(
        "Calculated Quantity Within Market Open Limit",
        within_market_open_limit,
    )

    if not within_market_open_limit:
        blocker(
            "Calculated initial quantity exceeds WEEX "
            "market open limit."
        )

    if max_position_size > 0:
        within_position_limit = (
            rounded_quantity
            <= max_position_size
        )

    else:
        within_position_limit = True

    pass_fail(
        "Calculated Quantity Within Maximum Position Size",
        within_position_limit,
    )

    if not within_position_limit:
        blocker(
            "Calculated initial quantity exceeds WEEX "
            "maximum position size."
        )

    margin_rounding_safe = (
        hypothetical_margin_used
        <= initial_margin
    )

    pass_fail(
        "Rounded Quantity Does Not Exceed 5% Margin Budget",
        margin_rounding_safe,
    )

    if not margin_rounding_safe:
        blocker(
            "Rounded quantity would exceed the initial "
            "5% margin budget."
        )

    # ========================================================
    # MAXIMUM STRATEGY NOTIONAL
    # ========================================================

    maximum_strategy_notional = (
        planned_total_margin
        * PLANNED_LEVERAGE
    )

    maximum_strategy_quantity = (
        maximum_strategy_notional
        / mark_price
        if mark_price > 0
        else Decimal("0")
    )

    maximum_strategy_quantity = floor_to_precision(
        maximum_strategy_quantity,
        quantity_precision,
    )

    print()
    print(
        "R28 UNIT L MAXIMUM THEORETICAL STRATEGY EXPOSURE:",
        flush=True,
    )

    print(
        f"  Maximum Planned Margin = "
        f"{decimal_text(planned_total_margin)} USDT",
        flush=True,
    )

    print(
        f"  Maximum Planned Notional @ 100x = "
        f"{decimal_text(maximum_strategy_notional)} USDT",
        flush=True,
    )

    print(
        f"  Approx Maximum {SYMBOL} Quantity = "
        f"{decimal_text(maximum_strategy_quantity)} BTC",
        flush=True,
    )

    if max_position_size > 0:
        total_position_limit_ok = (
            maximum_strategy_quantity
            <= max_position_size
        )

    else:
        total_position_limit_ok = True

    pass_fail(
        "Maximum Strategy Quantity Within Exchange Position Limit",
        total_position_limit_ok,
    )

    if not total_position_limit_ok:
        blocker(
            "Maximum theoretical strategy position would "
            "exceed exchange position limits."
        )

    # ========================================================
    # POSITION MODE / LOCAL STRATEGY RELATION
    # ========================================================

    print()
    print(
        "R28 UNIT L POSITION-MODE COMPATIBILITY:",
        flush=True,
    )

    print(
        "  Local Strategy = ONE DIRECTION ONLY",
        flush=True,
    )

    print(
        f"  WEEX Mode = {position_mode}",
        flush=True,
    )

    if position_mode == "COMBINED":
        print(
            "  ✅ COMBINED mode is acceptable for the "
            "local one-direction-only strategy audit.",
            flush=True,
        )

    elif position_mode == "SEPARATED":
        warning(
            "WEEX reports SEPARATED position mode. "
            "Local one-direction controls must remain authoritative."
        )

    else:
        blocker(
            "Position-mode compatibility cannot be established."
        )

    # ========================================================
    # READINESS SUMMARY
    # ========================================================

    print()
    print(
        "R28 UNIT L EXECUTION-READINESS ASSESSMENT",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    print(
        f"Structural Safety Failures = "
        f"{sum(1 for _, ok in RESULTS if not ok)}",
        flush=True,
    )

    print(
        f"Readiness Blockers = {len(READINESS_BLOCKERS)}",
        flush=True,
    )

    print(
        f"Readiness Warnings = {len(READINESS_WARNINGS)}",
        flush=True,
    )

    if READINESS_BLOCKERS:

        print()
        print(
            "CURRENT EXECUTION READINESS: 🚫 NOT READY",
            flush=True,
        )

        for index, item in enumerate(
            READINESS_BLOCKERS,
            start=1,
        ):
            print(
                f"  {index}. {item}",
                flush=True,
            )

    else:

        print()
        print(
            "CURRENT EXECUTION READINESS: ✅ COMPATIBLE",
            flush=True,
        )

        print(
            "  NOTE: EXECUTION REMAINS DISABLED.",
            flush=True,
        )


# ============================================================
# TRANSPORT-BOUNDARY AUDIT
# ============================================================

def run_transport_audit():
    print()
    print(
        "R28 UNIT L TRANSPORT-BOUNDARY AUDIT",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    pass_fail(
        "Controlled Network GETs Occurred",
        AUDIT[
            "network_gets"
        ] >= 5,
    )

    pass_fail(
        "Generic POST Was Blocked Locally",
        AUDIT[
            "local_post_blocks"
        ] >= 1,
    )

    pass_fail(
        "PUT Was Blocked Locally",
        AUDIT[
            "local_put_blocks"
        ] >= 1,
    )

    pass_fail(
        "PATCH Was Blocked Locally",
        AUDIT[
            "local_patch_blocks"
        ] >= 1,
    )

    pass_fail(
        "DELETE Was Blocked Locally",
        AUDIT[
            "local_delete_blocks"
        ] >= 1,
    )

    pass_fail(
        "Network Write Count Is Zero",
        AUDIT[
            "network_writes"
        ] == 0,
    )

    pass_fail(
        "Network POST Count Is Zero",
        AUDIT[
            "network_posts"
        ] == 0,
    )

    pass_fail(
        "Network PUT Count Is Zero",
        AUDIT[
            "network_puts"
        ] == 0,
    )

    pass_fail(
        "Network PATCH Count Is Zero",
        AUDIT[
            "network_patches"
        ] == 0,
    )

    pass_fail(
        "Network DELETE Count Is Zero",
        AUDIT[
            "network_deletes"
        ] == 0,
    )

    pass_fail(
        "Real Order Transmission Never Occurred",
        AUDIT[
            "real_order_network_transmissions"
        ] == 0,
    )

    pass_fail(
        "Demo Order Transmission Never Occurred",
        AUDIT[
            "demo_order_network_transmissions"
        ] == 0,
    )

    print()
    print(
        "R28 UNIT L WRITE-LOCK AUDIT:",
        flush=True,
    )

    print(
        f"  Local POST attempts = "
        f"{AUDIT['local_post_attempts']}",
        flush=True,
    )

    print(
        f"  Local POST blocks = "
        f"{AUDIT['local_post_blocks']}",
        flush=True,
    )

    print(
        f"  Local PUT attempts = "
        f"{AUDIT['local_put_attempts']}",
        flush=True,
    )

    print(
        f"  Local PUT blocks = "
        f"{AUDIT['local_put_blocks']}",
        flush=True,
    )

    print(
        f"  Local PATCH attempts = "
        f"{AUDIT['local_patch_attempts']}",
        flush=True,
    )

    print(
        f"  Local PATCH blocks = "
        f"{AUDIT['local_patch_blocks']}",
        flush=True,
    )

    print(
        f"  Local DELETE attempts = "
        f"{AUDIT['local_delete_attempts']}",
        flush=True,
    )

    print(
        f"  Local DELETE blocks = "
        f"{AUDIT['local_delete_blocks']}",
        flush=True,
    )

    print(
        f"  Network GETs = "
        f"{AUDIT['network_gets']}",
        flush=True,
    )

    print(
        f"  Network writes = "
        f"{AUDIT['network_writes']}",
        flush=True,
    )

    print(
        "  Real order network transmissions = "
        f"{AUDIT['real_order_network_transmissions']}",
        flush=True,
    )

    print(
        "  Demo order network transmissions = "
        f"{AUDIT['demo_order_network_transmissions']}",
        flush=True,
    )


# ============================================================
# DIAGNOSTIC
# ============================================================

async def run_diagnostic(
    transport,
):
    print(
        "=" * 76,
        flush=True,
    )

    print(
        "0F-4H-R28-UNIT-L STARTING",
        flush=True,
    )

    print(
        "READ-ONLY STRATEGY / ACCOUNT COMPATIBILITY VALIDATION",
        flush=True,
    )

    print(
        "LIVE EXCHANGE CONSTRAINT DISCOVERY",
        flush=True,
    )

    print(
        "HYPOTHETICAL ENTRY SIZING ONLY",
        flush=True,
    )

    print(
        "NO ACCOUNT CONFIGURATION CHANGES",
        flush=True,
    )

    print(
        "REAL ORDER TRANSMISSION DISABLED",
        flush=True,
    )

    print(
        "DEMO ORDER TRANSMISSION DISABLED",
        flush=True,
    )

    print(
        "ALL NETWORK WRITE METHODS BLOCKED",
        flush=True,
    )

    print(
        "=" * 76,
        flush=True,
    )

    print(
        f"R28 UNIT L SYMBOL: {SYMBOL}",
        flush=True,
    )

    print(
        "R28 UNIT L STRATEGY:",
        flush=True,
    )

    print(
        f"  Planned Margin Type = {PLANNED_MARGIN_TYPE}",
        flush=True,
    )

    print(
        f"  Planned Leverage = "
        f"{decimal_text(PLANNED_LEVERAGE)}x",
        flush=True,
    )

    print(
        f"  Initial Entry = "
        f"{decimal_text(INITIAL_ENTRY_PERCENT)}%",
        flush=True,
    )

    print(
        f"  Max Pyramid Adds = {MAX_PYRAMID_ADDS}",
        flush=True,
    )

    print(
        f"  Max Backups = {MAX_BACKUPS}",
        flush=True,
    )

    print(
        f"  Max Fund Exposure = "
        f"{decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%",
        flush=True,
    )

    print()
    print(
        "R28 UNIT L NETWORK POLICY:",
        flush=True,
    )

    print(
        "  ✅ Public market GET enabled",
        flush=True,
    )

    print(
        "  ✅ Authenticated read-only GET enabled",
        flush=True,
    )

    print(
        "  ❌ Real order POST disabled",
        flush=True,
    )

    print(
        "  ❌ Demo order POST disabled",
        flush=True,
    )

    print(
        "  ❌ PUT / PATCH / DELETE disabled",
        flush=True,
    )

    print()
    print(
        "R28 UNIT L CREDENTIAL STATUS:",
        flush=True,
    )

    print(
        "  API Key: "
        + (
            "✅ PRESENT"
            if API_KEY
            else "❌ MISSING"
        ),
        flush=True,
    )

    print(
        "  API Secret: "
        + (
            "✅ PRESENT"
            if API_SECRET
            else "❌ MISSING"
        ),
        flush=True,
    )

    print(
        "  API Passphrase: "
        + (
            "✅ PRESENT"
            if API_PASSPHRASE
            else "❌ MISSING"
        ),
        flush=True,
    )

    print()

    await run_safety_gates(
        transport
    )

    print()
    print(
        "R28 UNIT L READ-ONLY DATA ACQUISITION",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    mark_price = await get_market_price(
        transport
    )

    pass_fail(
        "Public Symbol Price GET",
        mark_price > 0,
    )

    exchange_info = await get_exchange_info(
        transport
    )

    pass_fail(
        "Public Exchange Information GET",
        isinstance(
            exchange_info,
            dict,
        ),
    )

    balance_record = await get_usdt_balance(
        transport
    )

    pass_fail(
        "Authenticated Balance GET",
        isinstance(
            balance_record,
            dict,
        ),
    )

    positions = await get_positions(
        transport
    )

    pass_fail(
        "Authenticated Positions GET",
        isinstance(
            positions,
            list,
        ),
    )

    symbol_config = await get_symbol_config(
        transport
    )

    pass_fail(
        "Authenticated Symbol Config GET",
        isinstance(
            symbol_config,
            dict,
        ),
    )

    audit_strategy_compatibility(
        mark_price=mark_price,
        exchange_info=exchange_info,
        balance_record=balance_record,
        positions=positions,
        symbol_config=symbol_config,
    )

    run_transport_audit()

    # ========================================================
    # FINAL STRUCTURAL DIAGNOSTIC RESULT
    # ========================================================

    structural_failures = [
        label
        for label, passed
        in RESULTS
        if not passed
    ]

    print(
        "-" * 76,
        flush=True,
    )

    if structural_failures:

        print(
            "❌ R28 UNIT L DIAGNOSTIC FAILED",
            flush=True,
        )

        print(
            "FAILED STRUCTURAL GATES:",
            flush=True,
        )

        for label in structural_failures:
            print(
                f"  ❌ {label}",
                flush=True,
            )

    else:

        print(
            "✅ R28 UNIT L DIAGNOSTIC PASSED",
            flush=True,
        )

        print(
            "✅ READ-ONLY STRATEGY CALCULATION VALIDATED",
            flush=True,
        )

        print(
            "✅ LIVE EXCHANGE CONSTRAINTS VALIDATED",
            flush=True,
        )

        print(
            "✅ ACCOUNT / STRATEGY COMPARISON VALIDATED",
            flush=True,
        )

        print(
            "✅ HYPOTHETICAL ENTRY SIZING VALIDATED",
            flush=True,
        )

        print(
            "✅ FUND EXPOSURE LIMIT VALIDATED",
            flush=True,
        )

        print(
            "✅ TRANSPORT-BOUNDARY AUDIT PASSED",
            flush=True,
        )

    if READINESS_BLOCKERS:

        print(
            "⚠️ R28 UNIT L DETECTED EXECUTION-READINESS BLOCKERS",
            flush=True,
        )

        print(
            "⚠️ NO CORRECTION OR ACCOUNT CHANGE WAS ATTEMPTED",
            flush=True,
        )

    else:

        print(
            "✅ CURRENT READ-ONLY CONFIGURATION IS "
            "STRATEGY-COMPATIBLE",
            flush=True,
        )

        print(
            "⚠️ EXECUTION STILL REMAINS DISABLED",
            flush=True,
        )

    print(
        "🛡 NETWORK WRITE TRANSPORT LOCKED",
        flush=True,
    )

    print(
        "🛡 REAL ORDER TRANSMISSION IMPOSSIBLE",
        flush=True,
    )

    print(
        "🛡 DEMO ORDER TRANSMISSION IMPOSSIBLE",
        flush=True,
    )

    print(
        "🛡 LEVERAGE CHANGE NOT ATTEMPTED",
        flush=True,
    )

    print(
        "🛡 MARGIN MODE CHANGE NOT ATTEMPTED",
        flush=True,
    )

    print(
        "🛡 POSITION MODE CHANGE NOT ATTEMPTED",
        flush=True,
    )

    print(
        "=" * 76,
        flush=True,
    )


# ============================================================
# PERSISTENT RUNTIME
# ============================================================

async def persistent_runtime(
    stop_event,
):
    print(
        "R28 UNIT L: PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT L: AUTHENTICATED READ-ONLY LOCKS ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT L: NETWORK WRITE TRANSPORT LOCKED",
        flush=True,
    )

    if READINESS_BLOCKERS:
        print(
            "R28 UNIT L: EXECUTION READINESS = NOT READY",
            flush=True,
        )

    else:
        print(
            "R28 UNIT L: EXECUTION READINESS = COMPATIBLE "
            "(EXECUTION STILL DISABLED)",
            flush=True,
        )

    heartbeat = 0

    while not stop_event.is_set():

        heartbeat += 1

        print(
            f"R28 UNIT L: HEARTBEAT {heartbeat} ✅ ACTIVE",
            flush=True,
        )

        try:
            await asyncio.wait_for(
                stop_event.wait(),
                timeout=15,
            )

        except asyncio.TimeoutError:
            pass


# ============================================================
# MAIN RUNTIME
# ============================================================

async def main():
    print(
        "R28 UNIT L: RUNTIME STARTING",
        flush=True,
    )

    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()

    def request_shutdown():
        print(
            "R28 UNIT L: SHUTDOWN REQUESTED",
            flush=True,
        )

        stop_event.set()

    for sig in (
        signal.SIGINT,
        signal.SIGTERM,
    ):
        try:
            loop.add_signal_handler(
                sig,
                request_shutdown,
            )

        except (
            NotImplementedError,
            RuntimeError,
        ):
            pass

    health_server = None

    try:
        health_server = await start_health_server()

    except Exception as exc:
        print(
            "R28 UNIT L: HEALTH SERVER ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

    async with aiohttp.ClientSession() as session:

        transport = LockedTransport(
            session
        )

        try:
            await run_diagnostic(
                transport
            )

        except Exception as exc:

            print(
                "-" * 76,
                flush=True,
            )

            print(
                "❌ R28 UNIT L DIAGNOSTIC EXCEPTION",
                flush=True,
            )

            print(
                f"TYPE: {type(exc).__name__}",
                flush=True,
            )

            print(
                f"DETAIL: {exc}",
                flush=True,
            )

            print(
                "🛡 EXECUTION REMAINS DISABLED",
                flush=True,
            )

            print(
                "🛡 NETWORK WRITE TRANSPORT REMAINS LOCKED",
                flush=True,
            )

            print(
                "🛡 NO REAL ORDER TRANSMISSION OCCURRED",
                flush=True,
            )

            print(
                "🛡 NO DEMO ORDER TRANSMISSION OCCURRED",
                flush=True,
            )

            print(
                "=" * 76,
                flush=True,
            )

        await persistent_runtime(
            stop_event
        )

    if health_server is not None:

        health_server.close()

        await health_server.wait_closed()

    print(
        "R28 UNIT L: RUNTIME STOPPED CLEANLY",
        flush=True,
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:
        asyncio.run(
            main()
        )

    except KeyboardInterrupt:
        print(
            "R28 UNIT L: KEYBOARD INTERRUPT",
            flush=True,
        )

    except Exception as exc:
        print(
            "R28 UNIT L: FATAL RUNTIME ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )
