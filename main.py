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

# Percentage movement needed before an alert is sent.
#
# Example:
#
# BTC_ALERT_THRESHOLD = 0.01
#
# means:
#
# 0.01%
#
# At BTC = $65,000:
#
# 0.01% ≈ $6.50
#
# IMPORTANT:
# The movement is measured from the LAST ALERT PRICE,
# not from the immediately preceding websocket tick.

ALERT_THRESHOLD_PERCENT = Decimal(
    os.getenv(
        "BTC_ALERT_THRESHOLD",
        "0.01",
    )
)


# ============================================================
# RECONNECT SETTINGS
# ============================================================

RECONNECT_DELAY_SECONDS = 5

MAX_RECONNECT_DELAY_SECONDS = 60


# ============================================================
# TELEGRAM
# ============================================================

def telegram_is_configured() -> bool:

    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    )


async def send_telegram(
    bot: Bot,
    message: str,
) -> None:

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
# PRICE EXTRACTION
# ============================================================

def extract_price(
    message: Any,
) -> Optional[Decimal]:

    try:

        if not isinstance(message, dict):
            return None

        # WEEX V3 ticker format:
        #
        # {
        #     "e": "ticker",
        #     "s": "BTCUSDT",
        #     "d": [
        #         {
        #             "c": "65000.0"
        #         }
        #     ]
        # }

        data = message.get("d")

        if isinstance(data, list) and data:

            ticker = data[0]

            if isinstance(ticker, dict):

                value = ticker.get("c")

                if value is not None:

                    price = Decimal(
                        str(value)
                    )

                    if price > 0:
                        return price


        # Fallback support in case WEEX
        # returns another structure.

        possible_fields = [
            "lastPrice",
            "last",
            "price",
            "c",
        ]

        for field in possible_fields:

            value = message.get(field)

            if value is None:
                continue

            try:

                price = Decimal(
                    str(value)
                )

                if price > 0:
                    return price

            except (
                InvalidOperation,
                ValueError,
                TypeError,
            ):
                continue

    except Exception as error:

        print(
            f"PRICE PARSE ERROR: {error}",
            flush=True,
        )

    return None


# ============================================================
# PERCENTAGE CALCULATION
# ============================================================

def calculate_percentage_change(
    reference_price: Decimal,
    current_price: Decimal,
) -> Decimal:

    if reference_price == 0:

        return Decimal("0")

    return (
        (
            current_price
            - reference_price
        )
        / reference_price
    ) * Decimal("100")


# ============================================================
# MAIN WEBSOCKET ENGINE
# ============================================================

async def run_websocket(
    bot: Bot,
) -> None:

    reconnect_delay = RECONNECT_DELAY_SECONDS

    connection_notification_sent = False


    # ========================================================
    # IMPORTANT FIX
    #
    # reference_price stays unchanged while BTC moves.
    #
    # It is ONLY changed after an alert is sent.
    #
    # Therefore:
    #
    # 65000
    # 65001
    # 65002
    # 65003
    # 65004
    # 65005
    # 65006.5
    #
    # can accumulate into a 0.01% movement.
    #
    # Previously, if the reference was reset every tick,
    # these tiny movements could never reach the threshold.
    # ========================================================

    reference_price: Optional[Decimal] = None


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
                # SUBSCRIBE
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
                    f"SUBSCRIBED TO "
                    f"{SUBSCRIPTION_CHANNEL}",
                    flush=True,
                )


                # --------------------------------------------
                # TELEGRAM CONNECTION MESSAGE
                # --------------------------------------------

                if not connection_notification_sent:

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


                reconnect_delay = (
                    RECONNECT_DELAY_SECONDS
                )


                # --------------------------------------------
                # RECEIVE MESSAGES
                # --------------------------------------------

                async for raw_message in websocket:

                    try:

                        message = json.loads(
                            raw_message
                        )

                    except json.JSONDecodeError:

                        print(
                            "INVALID JSON:",
                            raw_message,
                            flush=True,
                        )

                        continue


                    # ========================================
                    # APPLICATION PING
                    # ========================================

                    if (
                        isinstance(message, dict)
                        and (
                            message.get("event")
                            == "ping"
                            or
                            message.get("type")
                            == "ping"
                        )
                    ):

                        pong_message = {

                            "method": "PONG",

                            "id": 1,
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

                        continue


                    # ========================================
                    # SUBSCRIPTION CONFIRMATION
                    # ========================================

                    if (
                        isinstance(message, dict)
                        and
                        message.get("id") == 1
                        and
                        message.get("result") is True
                    ):

                        print(
                            "SUBSCRIPTION CONFIRMED",
                            flush=True,
                        )

                        continue


                    # ========================================
                    # EXTRACT BTC PRICE
                    # ========================================

                    price = extract_price(
                        message
                    )


                    if price is None:

                        continue


                    # ========================================
                    # SET STARTING REFERENCE PRICE
                    # ========================================

                    if reference_price is None:

                        reference_price = price


                        print(
                            f"{SYMBOL} STARTING "
                            f"REFERENCE PRICE: "
                            f"{reference_price}",
                            flush=True,
                        )


                        await send_telegram(
                            bot,
                            (
                                f"📈 {SYMBOL} "
                                f"starting price\n"
                                f"{reference_price}"
                            ),
                        )


                        continue


                    # ========================================
                    # CALCULATE ACCUMULATED MOVEMENT
                    # ========================================

                    percentage_change = (
                        calculate_percentage_change(
                            reference_price,
                            price,
                        )
                    )


                    absolute_change = abs(
                        percentage_change
                    )


                    # ========================================
                    # DEBUG LOG
                    #
                    # This lets us SEE whether the threshold
                    # calculation is working.
                    # ========================================

                    print(
                        f"{SYMBOL} PRICE: {price} | "
                        f"REFERENCE: {reference_price} | "
                        f"MOVE: "
                        f"{percentage_change:.6f}% | "
                        f"THRESHOLD: "
                        f"{ALERT_THRESHOLD_PERCENT}%",
                        flush=True,
                    )


                    # ========================================
                    # THRESHOLD NOT YET REACHED
                    # ========================================

                    if (
                        absolute_change
                        <
                        ALERT_THRESHOLD_PERCENT
                    ):

                        continue


                    # ========================================
                    # DETERMINE DIRECTION
                    # ========================================

                    if percentage_change > 0:

                        direction = "🟢 UP"

                    else:

                        direction = "🔴 DOWN"


                    # ========================================
                    # SEND ALERT
                    # ========================================

                    alert_message = (
                        f"{direction}\n"
                        f"{SYMBOL}\n\n"
                        f"Reference: "
                        f"{reference_price}\n"
                        f"Current: {price}\n"
                        f"Change: "
                        f"{percentage_change:.4f}%"
                    )


                    await send_telegram(
                        bot,
                        alert_message,
                    )


                    print(
                        "ALERT TRIGGERED: "
                        f"{percentage_change:.6f}%",
                        flush=True,
                    )


                    # ========================================
                    # CRITICAL:
                    #
                    # Reset reference ONLY AFTER ALERT.
                    # ========================================

                    reference_price = price


                    print(
                        "NEW REFERENCE PRICE: "
                        f"{reference_price}",
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

    if telegram_is_configured():

        print(
            "TELEGRAM CONFIG: READY",
            flush=True,
        )

    else:

        print(
            "TELEGRAM CONFIG: MISSING",
            flush=True,)
        
