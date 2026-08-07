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


# ============================================================
# TELEGRAM CONFIGURATION
# ============================================================

# Add these in Render Environment Variables:
#
# TELEGRAM_BOT_TOKEN
# TELEGRAM_CHAT_ID

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


# ============================================================
# BTC PRICE ALERT CONFIGURATION
# ============================================================

# 0.1 means 0.1%
#
# Example:
#
# Reference price = 65000
#
# 0.1% movement = approximately $65
#
# UP trigger   = approximately 65065
# DOWN trigger = approximately 64935

BTC_ALERT_THRESHOLD_PERCENT = Decimal(
    os.getenv(
        "BTC_ALERT_THRESHOLD_PERCENT",
        "0.1",
    )
)


# ============================================================
# RECONNECT CONFIGURATION
# ============================================================

RECONNECT_DELAY_SECONDS = 5

MAX_RECONNECT_DELAY_SECONDS = 60


# ============================================================
# GLOBAL STATE
# ============================================================

connection_notification_sent = False

reference_price: Optional[Decimal] = None


# ============================================================
# TELEGRAM STATUS
# ============================================================

def telegram_is_configured() -> bool:

    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    )


def display_telegram_status() -> None:

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
            f"TELEGRAM ERROR: "
            f"{type(error).__name__}: {error}",
            flush=True,
        )


# ============================================================
# PRICE CONVERSION
# ============================================================

def decimal_price(
    value: Any,
) -> Optional[Decimal]:

    if value is None:

        return None

    try:

        price = Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):

        return None


    if price <= 0:

        return None


    return price


# ============================================================
# PRICE EXTRACTION
# ============================================================

def extract_price(
    message: Any,
) -> Optional[Decimal]:

    if not isinstance(
        message,
        dict,
    ):

        return None


    # --------------------------------------------------------
    # Direct price fields
    # --------------------------------------------------------

    for field in (
        "lastPrice",
        "last",
        "price",
        "close",
    ):

        if field in message:

            price = decimal_price(
                message.get(field)
            )

            if price is not None:

                return price


    # --------------------------------------------------------
    # data can be dictionary
    # --------------------------------------------------------

    data = message.get(
        "data"
    )


    if isinstance(
        data,
        dict,
    ):

        for field in (
            "lastPrice",
            "last",
            "price",
            "close",
        ):

            if field in data:

                price = decimal_price(
                    data.get(field)
                )

                if price is not None:

                    return price


    # --------------------------------------------------------
    # data can also be list
    # --------------------------------------------------------

    if isinstance(
        data,
        list,
    ):

        for item in data:

            if not isinstance(
                item,
                dict,
            ):

                continue


            for field in (
                "lastPrice",
                "last",
                "price",
                "close",
            ):

                if field in item:

                    price = decimal_price(
                        item.get(field)
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


    difference = abs(
        new_price
        - old_price
    )


    percentage = (
        difference
        / old_price
    ) * Decimal("100")


    return percentage


# ============================================================
# BTC ALERT ENGINE
# ============================================================

async def process_price(
    bot: Bot,
    price: Decimal,
) -> None:

    global reference_price


    # --------------------------------------------------------
    # First valid BTC price
    # becomes our reference price.
    # --------------------------------------------------------

    if reference_price is None:

        reference_price = price


        print(
            f"{SYMBOL} REFERENCE PRICE: "
            f"{reference_price}",
            flush=True,
        )


        await send_telegram(
            bot,
            (
                f"📈 {SYMBOL} starting price: "
                f"{reference_price}\n\n"
                f"Alert threshold: "
                f"{BTC_ALERT_THRESHOLD_PERCENT}%"
            ),
        )


        return


    # --------------------------------------------------------
    # Ignore identical ticker values
    # --------------------------------------------------------

    if price == reference_price:

        return


    # --------------------------------------------------------
    # Calculate accumulated movement from reference
    # --------------------------------------------------------

    percentage_change = (
        calculate_percentage_change(
            reference_price,
            price,
        )
    )


    print(
        f"{SYMBOL} PRICE: {price} "
        f"| REFERENCE: {reference_price} "
        f"| CHANGE: "
        f"{percentage_change:.6f}%",
        flush=True,
    )


    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Do NOT change reference_price here.
    #
    # The movement must accumulate until
    # the 0.1% threshold is reached.
    # --------------------------------------------------------

    if (
        percentage_change
        < BTC_ALERT_THRESHOLD_PERCENT
    ):

        return


    # --------------------------------------------------------
    # Threshold reached
    # --------------------------------------------------------

    previous_reference = (
        reference_price
    )


    if price > previous_reference:

        direction = "🟢 UP"

    else:

        direction = "🔴 DOWN"


    signed_change = (
        (
            price
            - previous_reference
        )
        / previous_reference
    ) * Decimal("100")


    alert_message = (
        f"{direction}\n"
        f"{SYMBOL}\n\n"
        f"Reference: "
        f"{previous_reference}\n"
        f"Current: "
        f"{price}\n"
        f"Change: "
        f"{signed_change:.4f}%\n\n"
        f"Threshold: "
        f"{BTC_ALERT_THRESHOLD_PERCENT}%"
    )


    await send_telegram(
        bot,
        alert_message,
    )


    print(
        f"BTC ALERT TRIGGERED: "
        f"{signed_change:.4f}%",
        flush=True,
    )


    # --------------------------------------------------------
    # RESET REFERENCE PRICE
    #
    # The alert price now becomes the
    # starting/reference price for the
    # next accumulated 0.1% move.
    # --------------------------------------------------------

    reference_price = price


    print(
        f"NEW REFERENCE PRICE: "
        f"{reference_price}",
        flush=True,
    )


# ============================================================
# WEBSOCKET HANDLER
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
                # Subscribe to BTC ticker
                # --------------------------------------------

                subscribe_message = {

                    "method":
                    "SUBSCRIBE",

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
                    f"SUBSCRIBED TO "
                    f"{SUBSCRIPTION_CHANNEL}",
                    flush=True,
                )


                # --------------------------------------------
                # Send connection notification only once
                # per application process
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
                            f"{BTC_ALERT_THRESHOLD_PERCENT}%"
                        ),
                    )


                    connection_notification_sent = True


                # Successful connection resets
                # reconnect delay.

                reconnect_delay = (
                    RECONNECT_DELAY_SECONDS
                )


                # --------------------------------------------
                # Receive websocket messages
                # --------------------------------------------

                async for raw_message in websocket:

                    try:

                        # ------------------------------------
                        # WEEX application ping
                        # ------------------------------------

                        if raw_message == "ping":

                            await websocket.send(
                                "pong"
                            )

                            print(
                                "APPLICATION PONG SENT",
                                flush=True,
                            )

                            continue


                        # ------------------------------------
                        # Parse JSON
                        # ------------------------------------

                        message = json.loads(
                            raw_message
                        )


                        # ------------------------------------
                        # Subscription confirmation
                        # ------------------------------------

                        if isinstance(
                            message,
                            dict,
                        ):

                            message_id = (
                                message.get("id")
                            )


                            if message_id == 1:

                                print(
                                    "SUBSCRIPTION CONFIRMED",
                                    flush=True,
                                )

                                continue


                        # ------------------------------------
                        # Extract valid BTC price
                        # ------------------------------------

                        price = extract_price(
                            message
                        )


                        if price is None:

                            continue


                        print(
                            f"{SYMBOL} PRICE: "
                            f"{price}",
                            flush=True,
                        )


                        # ------------------------------------
                        # Send price to 0.1% alert engine
                        # ------------------------------------

                        await process_price(
                            bot,
                            price,
                        )


                    except json.JSONDecodeError:

                        # Some websocket messages
                        # may not be JSON.

                        continue


                    except Exception as error:

                        print(
                            "MESSAGE ERROR: "
                            f"{type(error).__name__}: "
                            f"{error}",
                            flush=True,
                        )


        except Exception as error:

            print(
                "CONNECTION ERROR: "
                f"{type(error).__name__}: "
                f"{error}",
                flush=True,
            )


            print(
                f"RECONNECTING IN "
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

    display_telegram_status()


    print(
        "BTC ALERT THRESHOLD: "
        f"{BTC_ALERT_THRESHOLD_PERCENT}%",
        flush=True,
    )


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

    asyncio.run(
        main())
