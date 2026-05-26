import os

from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise ValueError(
            f"Required environment variable '{key}' is not set. Check your .env file."
        )
    return value


BOT_TOKEN: str = _require("BOT_TOKEN")
ORDERS_CHANNEL_ID: int = int(_require("ORDERS_CHANNEL_ID"))
YOOMONEY_WALLET: str = _require("YOOMONEY_WALLET")
