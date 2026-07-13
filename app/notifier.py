import logging

import httpx

from app import config

logger = logging.getLogger("tracker.notifier")

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


async def notify_new_tweet(account_username: str, content: str, url: str) -> None:
    if not (config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID):
        return

    text = f"🐦 Nuevo tuit de @{account_username}\n\n{content}\n\n{url}".strip()
    endpoint = TELEGRAM_API.format(token=config.TELEGRAM_BOT_TOKEN)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                endpoint,
                json={"chat_id": config.TELEGRAM_CHAT_ID, "text": text, "disable_web_page_preview": False},
            )
            response.raise_for_status()
    except Exception:
        logger.exception("No se pudo enviar la notificación de Telegram para @%s", account_username)
