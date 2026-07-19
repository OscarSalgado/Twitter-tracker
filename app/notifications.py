"""Telegram notification system for tweet alerts."""

import logging
import os

import httpx

logger = logging.getLogger(__name__)


async def send_telegram_notification(account_username: str, content: str, url: str) -> bool:
    """Send a Telegram notification for a new tweet.

    Args:
        account_username: Twitter/X username (without @)
        content: Tweet text content
        url: Link to tweet on Twitter/X

    Returns:
        True if notification sent successfully, False otherwise.
        Never raises exceptions.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.debug("Telegram notifications not configured, skipping")
        return False

    message = f"@{account_username}\n{content}\n{url}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": message},
                timeout=5.0,
            )

            if response.status_code == 200:
                logger.info(f"Notification sent for @{account_username}")
                return True
            else:
                logger.error(
                    f"Failed to send notification: HTTP {response.status_code}: {response.text}"
                )
                return False

    except httpx.TimeoutException:
        logger.error("Failed to send notification: Request timeout (5s)")
        return False
    except httpx.RequestError as e:
        logger.error(f"Failed to send notification: Network error: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to send notification: Unexpected error: {e}")
        return False
