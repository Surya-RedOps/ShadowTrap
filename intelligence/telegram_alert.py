import os
import requests
from dotenv import load_dotenv
from core.logger import logger

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_alert(message: str):
    if not BOT_TOKEN or not CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        r = requests.post(url, json=payload, timeout=5)
        logger.info(f"TELEGRAM_LOG: response {r.status_code} - {r.text}")
    except Exception as e:
        logger.error(f"TELEGRAM_LOG: error {e}")
        pass
