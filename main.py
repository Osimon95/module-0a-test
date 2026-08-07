import asyncio
import json
import os
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

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


# ============================================================
# PRICE ALERT SETTINGS
# ============================================================

# 0.05% threshold for faster testing.
#
# Example:
# BTC = 65000
# 0.05% movement ≈ $32.50
#
# You can later change this in Render Environment Variables
# without changing the code.

ALERT_THRESHOLD_PERCENT = Decimal(
    os.getenv(
        "BTC_ALERT_THRESHOLD",
        "0.05",
    )
)


# ============================================================
# RECONNECT SETTINGS
# ============================================================

RECONNECT_DELAY_SECONDS = 5
MAX_RECONNECT_DELAY_SECONDS = 60


# ============================================================
# GLOBAL STATE
# ============================================================

reference_price: Optional[Decimal] = None

last_received_price: Optional[Decimal] = None

connection_notification_sent = False


# ============================================================
# TELEGRAM CONFIG CHECK
# ============================================================

def telegram_is_configured() -> bool:
    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    )


def display_configuration() -> None:

    if telegram_is_configured():
        print(
            "TELEGRAM CONFIG: READY",
            flush=True,
        )
    else:
        print(
            "TELEGRAM CONFIG: MISSING",
            flush=True,
        )

    print(
        f"BTC ALERT THRESHOLD: "
        f"{ALERT_THRESHOLD_PERCENT}%",
        flush=True,
    )


# ============================================================
# TELEGRAM MESSAGE FUNCTION
# ============================================================

async def send_telegram(
    bot: Bot,
    message: str,
) -> None:

    if not telegram_is_configured():

        print(
            "TELEGRAM WARNING: "
            "Token or chat ID is missing.",
            flush=True,
        )

        return

    try:

        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )

        print(
            "TELEGRAM MESSAGE SENT",
            flush=True,
        )

    except Exception as error:

        print(
            "TELEGRAM ERROR:",
            repr(error),
            flush=True,
        )


# ============================================================
# DECIMAL CONVERSION
# ============================================================

def convert_to_decimal(
    value: Any,
) -> Optional[Decimal]:

    if value is None:
        return None

    try:

        price = Decimal(str(value))

        if price <= 0:
            return None

        return price

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):

        return None


# ============================================================
# PRICE EXTRACTION
# ============================================================

def extract_price(
    message: Any,
) -> Optional[Decimal]:

    if not isinstance(message, dict):
        return None

    candidates = []

    # --------------------------------------------------------
    # Direct price fields
    # --------------------------------------------------------

    candidates.extend(
        [
            message.get("lastPrice"),
            message.get("last"),
            message.get("price"),
            message.get("close"),
        ]
    )

    # --------------------------------------------------------
    # data field
    # --------------------------------------------------------

    data = message.get("data")

    if isinstance(data, dict):

        candidates.extend(
            [
                data.get("lastPrice"),
                data.get("last"),
                data.get("price"),
                data.get("close"),
            ]
        )

    elif isinstance(data, list):

        for item in data:

            if isinstance(item, dict):

                candidates.extend(
                    [
                        item.get("lastPrice"),
                        item.get("last"),
                        item.get("price"),
                        item.get("close"),
                    ]
                )

    # --------------------------------------------------------
    # Convert candidates
    # --------------------------------------------------------

    for candidate in candidates:

        price = convert_to_decimal(
            candidate
        )

        if price is not None:
            return price

    return None


# ============================================================
# PERCENTAGE CHANGE
# ============================================================

def calculate_percentage_change(
    old_price: Decimal,
    new_price: Decimal,
) -> Decimal:

    if old_price == 0:
        return Decimal("0")

    return (
        (new_price - old_price)
        / old_price
    ) * Decimal("100")


# ============================================================
# PRICE PROCESSING
# ============================================================

async def process_price(
    bot: Bot,
    price: Decimal,
) -> None:

    global reference_price
    global last_received_price

    # Ignore duplicate ticker prices.
    if (
        last_received_price is not None
        and price == last_received_price
    ):
        return

    last_received_price = price

    print(
        f"{SYMBOL} PRICE: {price}",
        flush=True,
    )

    # --------------------------------------------------------
    # First valid price becomes reference price
    # --------------------------------------------------------

    if reference_price is None:

        reference_price = price

        print(
            f"REFERENCE PRICE SET: "
            f"{reference_price}",
            flush=True,
        )

        await send_telegram(
            bot,
            (
                f"📈 {SYMBOL} starting price\n"
                f"{reference_price}\n\n"
                f"Alert threshold: "
                f"{ALERT_THRESHOLD_PERCENT}%"
            ),
        )

        return

    # --------------------------------------------------------
    # Calculate movement FROM FIXED REFERENCE
    # --------------------------------------------------------

    change_percent = (
        calculate_percentage_change(
            reference_price,
            price,
        )
    )

    absolute_change = abs(
        change_percent
    )

    print(
        "CHANGE FROM REFERENCE: "
        f"{change_percent:.6f}%",
        flush=True,
    )

    # --------------------------------------------------------
    # Threshold not reached
    # --------------------------------------------------------

    if (
        absolute_change
        < ALERT_THRESHOLD_PERCENT
    ):

        return

    # --------------------------------------------------------
    # Threshold reached
    # --------------------------------------------------------

    print(
        "ALERT TRIGGERED",
        flush=True,
    )

    old_reference = reference_price

    if change_percent > 0:

        direction = "🟢 UP"

    else:

        direction = "🔴 DOWN"

    message = (
        f"{direction}\n"
        f"{SYMBOL}\n\n"
        f"Reference: {old_reference}\n"
        f"Current: {price}\n"
        f"Change: {change_percent:.4f}%\n"
        f"Threshold: "
        f"{ALERT_THRESHOLD_PERCENT}%"
    )

    await send_telegram(
        bot,
        message,
    )

    # --------------------------------------------------------
    # Reset reference ONLY after successful threshold event
    # --------------------------------------------------------

    reference_price = price

    print(
        f"NEW REFERENCE PRICE: "
        f"{reference_price}",
        flush=True,
    )


# ============================================================
# WEBSOCKET MESSAGE PROCESSOR
# ============================================================

async def process_message(
    bot: Bot,
    websocket,
    raw_message: Any,
) -> None:

    # --------------------------------------------------------
    # Plain-text heartbeat
    # --------------------------------------------------------

    if isinstance(
        raw_message,
        bytes,
    ):

        raw_message = (
            raw_message.decode(
                "utf-8",
                errors="ignore",
            )
        )

    text = str(
        raw_message
    ).strip()

    if text.lower() == "ping":

        await websocket.send(
            "pong"
        )

        print(
            "APPLICATION PONG SENT",
            flush=True,
        )

        return

    # --------------------------------------------------------
    # JSON decoding
    # --------------------------------------------------------

    try:

        message = json.loads(
            text
        )

    except json.JSONDecodeError:

        print(
            "NON-JSON MESSAGE:",
            text[:200],
            flush=True,
        )

        return

    # --------------------------------------------------------
    # JSON heartbeat
    # --------------------------------------------------------

    if isinstance(
        message,
        dict,
    ):

        event = str(
            message.get(
                "event",
                "",
            )
        ).lower()

        method = str(
            message.get(
                "method",
                "",
            )
        ).lower()

        if (
            event == "ping"
            or method == "ping"
        ):

            pong_message = {
                "event": "pong"
            }

            await websocket.send(
                json.dumps(
                    pong_message
                )
            )

            print(
                "APPLICATION PONG SENT",
                flush=True,
            )

            return

    # --------------------------------------------------------
    # Subscription confirmation
    # --------------------------------------------------------

    if isinstance(
        message,
        dict,
    ):

        if (
            message.get("id") == 1
            or str(
                message.get(
                    "event",
                    "",
                )
            ).lower()
            in (
                "subscribe",
                "subscribed",
            )
        ):

            print(
                "SUBSCRIPTION CONFIRMED",
                flush=True,
            )

    # --------------------------------------------------------
    # Extract BTC price
    # --------------------------------------------------------

    price = extract_price(
        message
    )

    if price is not None:

        await process_price(
            bot,
            price,
        )


# ============================================================
# WEEX WEBSOCKET LOOP
# ============================================================

async def run_websocket(
    bot: Bot,
) -> None:

    global connection_notification_sent

    reconnect_delay = (
        RECONNECT_DELAY_SECONDS
    )

    while True:

        try:

            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent":
                    "WEEX-BTC-Bot/1.0"
                },
                ping_interval=None,
                ping_timeout=None,
                close_timeout=10,
            ) as websocket:

                print(
                    "CONNECTED TO WEEX",
                    flush=True,
                )

                # --------------------------------------------
                # Subscribe
                # --------------------------------------------

                subscribe_message = {
                    "method": "SUBSCRIBE",
                    "params": [
                        SUBSCRIPTION_CHANNEL
                    ],
                    "id": 1,
                }

                await websocket.send(
                    json.dumps(
                        subscribe_message
                    )
                )

                print(
                    "SUBSCRIBED TO "
                    f"{SUBSCRIPTION_CHANNEL}",
                    flush=True,
                )

                # --------------------------------------------
                # Telegram connection notification
                # --------------------------------------------

                if (
                    not
                    connection_notification_sent
                ):

                    await send_telegram(
                        bot,
                        (
                            "✅ WEEX bot connected\n"
                            f"Watching {SYMBOL}\n"
                            f"Alert threshold: "
                            f"{ALERT_THRESHOLD_PERCENT}%"
                        ),
                    )

                    connection_notification_sent = True

                # --------------------------------------------
                # Reset reconnect delay after connection
                # --------------------------------------------

                reconnect_delay = (
                    RECONNECT_DELAY_SECONDS
                )

                # --------------------------------------------
                # Receive messages
                # --------------------------------------------

                async for raw_message in websocket:

                    try:

                        await process_message(
                            bot,
                            websocket,
                            raw_message,
                        )

                    except Exception as error:

                        print(
                            "MESSAGE PROCESSING ERROR:",
                            repr(error),
                            flush=True,
                        )

        except Exception as error:

            print(
                "CONNECTION ERROR:",
                f"{type(error).__name__}: "
                f"{error}",
                flush=True,
            )

            print(
                "RECONNECTING IN "
                f"{reconnect_delay} SECONDS",
                flush=True,
            )

            await asyncio.sleep(
                reconnect_delay
            )

            reconnect_delay = min(
                reconnect_delay * 2,
                MAX_RECONNECT_DELAY_SECONDS,
            )


# ============================================================
# MAIN
# ============================================================

async def main() -> None:

    display_configuration()

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN
    )

    await run_websocket(
        bot
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "BOT STOPPED",
            flush=True,)
        

