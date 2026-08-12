import asyncio
import base64
import hashlib
import hmac
import json
import os
import time
from decimal import Decimal, ROUND_DOWN
from urllib.parse import urlencode

import aiohttp
from aiohttp import web


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R15"
API_BASE_URL = "https://api-contract.weex.com"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()


# ============================================================
# ADJUSTABLE CONFIGURATION
# ============================================================

INITIAL_ENTRY_PERCENT = Decimal(
    os.getenv(
        "INITIAL_ENTRY_PERCENT",
        "5",
    )
)

LEVERAGE = Decimal(
    os.getenv(
        "LEVERAGE",
        "100",
    )
)

MAX_LEVERAGE = Decimal(
    os.getenv(
        "MAX_LEVERAGE",
        "100",
    )
)

MARGIN_TYPE = os.getenv(
    "MARGIN_TYPE",
    "ISOLATED",
).strip().upper()

MAX_PYRAMID_ADDS = int(
    os.getenv(
        "MAX_PYRAMID_ADDS",
        "1",
    )
)

PYRAMID_SIZE_PERCENT = Decimal(
    os.getenv(
        "PYRAMID_SIZE_PERCENT",
        "5",
    )
)

MAX_BACKUPS = int(
    os.getenv(
        "MAX_BACKUPS",
        "3",
    )
)

BACKUP_SIZE_PERCENT = Decimal(
    os.getenv(
        "BACKUP_SIZE_PERCENT",
        "5",
    )
)

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35",
    )
)

TP1_PERCENT = Decimal(
    os.getenv(
        "TP1_PERCENT",
        "20",
    )
)

TP2_PERCENT = Decimal(
    os.getenv(
        "TP2_PERCENT",
        "20",
    )
)

TP3_PERCENT = Decimal(
    os.getenv(
        "TP3_PERCENT",
        "60",
    )
)

TP1_TRIGGER_PERCENT = Decimal(
    os.getenv(
        "TP1_TRIGGER_PERCENT",
        "0.5",
    )
)

TP2_TRIGGER_PERCENT = Decimal(
    os.getenv(
        "TP2_TRIGGER_PERCENT",
        "1",
    )
)

TRAILING_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "TRAILING_DISTANCE_PERCENT",
        "0.2",
    )
)

BACKUP_BUFFER_PERCENT = Decimal(
    os.getenv(
        "BACKUP_BUFFER_PERCENT",
        "0.3",
    )
)

MIN_LIQ_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "MIN_LIQ_DISTANCE_PERCENT",
        "0.2",
    )
)

PLANNING_MMR_PERCENT = Decimal(
    os.getenv(
        "PLANNING_MMR_PERCENT",
        "0.5",
    )
)

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv(
        "SIGNAL_EXPIRY_SECONDS",
        "120",
    )
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv(
        "LOSS_COOLDOWN_SECONDS",
        "300",
    )
)


# ============================================================
# R15 LIVE-TRANSMISSION CONTROLS
# ============================================================

LIVE_ORDER_EXECUTION = (
    os.getenv(
        "LIVE_ORDER_EXECUTION",
        "false",
    ).lower()
    == "true"
)

R15_ONE_SHOT_ARM = (
    os.getenv(
        "R15_ONE_SHOT_ARM",
        "false",
    ).lower()
    == "true"
)

R15_ARM_TOKEN = os.getenv(
    "R15_ARM_TOKEN",
    "",
).strip()

R15_USE_MINIMUM_QUANTITY = (
    os.getenv(
        "R15_USE_MINIMUM_QUANTITY",
        "true",
    ).lower()
    == "true"
)

R15_MAX_LIVE_MARGIN_USDT = Decimal(
    os.getenv(
        "R15_MAX_LIVE_MARGIN_USDT",
        "0.10",
    )
)

ORDER_SIDE = "BUY"
POSITION_SIDE = "LONG"
ORDER_TYPE = "MARKET"


# ============================================================
# CREDENTIALS / TELEGRAM
# ============================================================

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
).strip()

WEEX_API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    "",
).strip()

WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    "",
).strip()

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)
