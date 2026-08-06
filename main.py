import asyncio
import json
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import websockets
from telegram import Bot


# ============================================================
# CONFIGURATION
# ============================================================

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

SYMBOL = "BTCUSDT"
SUBSCRIPTION_CHANNEL = f"{SYMBOL}@ticker"

# Temporary hard-coded Telegram configuration
TELEGRAM_BOT_TOKEN = "8684817654:AAGI7l96augCUlSaBx1xEReq7AZFfQtJhZc"
TELEGRAM_CHAT_ID = "8587384068"

# Zero means every genuine price change triggers an alert.
MINIMUM_PERCENT_CHANGE = Decimal("0")

RECONNECT_DELAY_SECONDS = 5
MAX_RECONNECT_DELAY_SECONDS = 60


# ============================================================
# TELEGRAM FUNCTIONS
# ============================================================

def telegram_is_configured() -> bool:
    """Check whether Telegram credentials are available."""
    invalid_values = {
        "",
        "8684817654:AAGI7l96augCUlSaBx1xEReq7AZFfQtJhZc",
        "8587384068",
    }

    return (
        TELEGRAM_BOT_TOKEN not in invalid_values
        and TELEGRAM_CHAT_ID not in invalid_values
    )


async def send_telegram(bot: Bot, message: str) -> None:
    """Send a Telegram message without stopping the price bot."""
    if not telegram_is_configured():
        print(
            "TELEGRAM WARNING: Token or chat ID is missing.",
            flush=True,
        )
        return

    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )

        print("TELEGRAM MESSAGE SENT", flush=True)

    except Exception as error:
        print(
            f"TELEGRAM ERROR: {type(error).__name__}: {error}",
            flush=True,
        )


# ============================================================
# PRICE EXTRACTION
# ============================================================

def convert_to_price(value: Any) -> Optional[Decimal]:
    """Convert a possible value to a valid positive price."""
    if value is None or isinstance(value, bool):
        return None

    try:
        price = Decimal(str(value))

    except (InvalidOperation, ValueError, TypeError):
        return None

    if not price.is_finite():
        return None

    if price <= 0:
        return None

    return price


def extract_price(payload: Any) -> Optional[Decimal]:
    """Extract the latest BTC price from a WEEX ticker message."""
    price_keys = (
        "lastPrice",
        "last_price",
        "last",
        "close",
        "price",
        "markPrice",
        "mark_price",
    )

    if isinstance(payload, dict):
        for key in price_keys:
            if key in payload:
                price = convert_to_price(payload.get(key))

                if price is not None:
                    return price

        for key in ("data", "result", "ticker"):
            if key in payload:
                price = extract_price(payload.get(key))

                if price is not None:
                    return price

    elif isinstance(payload, list):
        for item in payload:
            price = extract_price(item)

            if price is not None:
                return price

    return None


# ============================================================
# PRICE CHANGE CALCULATIONS
# ============================================================

def calculate_percentage_change(
    old_price: Decimal,
    new_price: Decimal,
) -> Decimal:
    """Calculate percentage change from the previous price."""
    if old_price <= 0:
        return Decimal("0")

    return (
        (new_price - old_price)
        / old_price
        * Decimal("100")
    )


def format_price(price: Decimal) -> str:
    """Remove unnecessary zeros from a Decimal price."""
    formatted = format(price, "f")

    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")

    return formatted


def create_price_message(
    previous_price: Decimal,
    current_price: Decimal,
    percentage_change: Decimal,
) -> str:
    """Create a formatted Telegram price-change alert."""
    price_difference = current_price - previous_price

    if percentage_change > 0:
        direction = "🟢 UP"
        percentage_sign = "+"
        difference_sign = "+"

    elif percentage_change < 0:
        direction = "🔴 DOWN"
        percentage_sign = ""
        difference_sign = ""

    else:
        direction = "⚪ UNCHANGED"
        percentage_sign = ""
        difference_sign = ""

    return (
        f"📈 {SYMBOL} PRICE CHANGE\n\n"
        f"Previous: {format_price(previous_price)}\n"
        f"Current: {format_price(current_price)}\n"
        f"Difference: "
        f"{difference_sign}{format_price(price_difference)}\n"
        f"Change: "
        f"{percentage_sign}{percentage_change:.6f}%\n"
        f"Direction: {direction}"
    )


# ============================================================
# WEEX APPLICATION PING
# ============================================================

async def handle_application_ping(
    websocket: Any,
    data: Any,
) -> bool:
    """Respond to WEEX application-level ping messages."""
    if not isinstance(data, dict):
        return False

    if data.get("event") == "ping":
        pong_message = {
            "method": "PONG",
            "id": data.get("id", 1),
        }

        await websocket.send(json.dumps(pong_message))

        print("APPLICATION PONG SENT", flush=True)
        return True

    if data.get("method") == "PING":
        pong_message = {
            "method": "PONG",
            "id": data.get("id", 1),
        }

        await websocket.send(json.dumps(pong_message))

        print("APPLICATION PONG SENT", flush=True)
        return True

    if "ping" in data:
        pong_message = {
            "pong": data.get("ping"),
