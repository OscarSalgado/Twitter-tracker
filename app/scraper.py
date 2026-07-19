"""Thin wrapper around twikit (open source, no paid API keys required).

twikit logs in as a regular Twitter/X account, the same way a browser would,
so it can read public tweets without needing Twitter's paid API tiers. See
README.md for the legal/ToS caveats of this approach.
"""

import logging
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import TypedDict

from twikit import Client

from app import config

logger = logging.getLogger("tracker.scraper")


class FetchedTweet(TypedDict):
    tweet_id: str
    content: str
    url: str
    tweet_created_at: object


class TwitterScraper:
    def __init__(self) -> None:
        self._client = Client(language="en-US")
        self._logged_in = False
        self._last_login_error: str | None = None

    @property
    def is_logged_in(self) -> bool:
        return self._logged_in

    @property
    def last_login_error(self) -> str | None:
        return self._last_login_error

    async def login(self) -> None:
        try:
            cookies_path = Path(config.COOKIES_FILE)
            if cookies_path.exists():
                try:
                    self._client.load_cookies(str(cookies_path))
                    self._logged_in = True
                    self._last_login_error = None
                    logger.info("Sesión de Twitter restaurada desde cookies guardadas.")
                    return
                except Exception:
                    logger.warning("No se pudieron reutilizar las cookies guardadas, se hará login de nuevo.")

            if not (config.TWITTER_USERNAME and config.TWITTER_PASSWORD):
                raise RuntimeError(
                    "Faltan credenciales de Twitter. Configura TWITTER_USERNAME, TWITTER_EMAIL y "
                    "TWITTER_PASSWORD en el archivo .env."
                )

            await self._client.login(
                auth_info_1=config.TWITTER_USERNAME,
                auth_info_2=config.TWITTER_EMAIL or None,
                password=config.TWITTER_PASSWORD,
            )
            cookies_path.parent.mkdir(parents=True, exist_ok=True)
            self._client.save_cookies(str(cookies_path))
            self._logged_in = True
            self._last_login_error = None
            logger.info("Login en Twitter completado y cookies guardadas.")
        except Exception as exc:
            self._logged_in = False
            self._last_login_error = str(exc)
            raise

    async def resolve_user(self, username: str):
        return await self._client.get_user_by_screen_name(username.lstrip("@"))

    async def fetch_user_tweets(self, user_id: str, count: int) -> list[FetchedTweet]:
        tweets = await self._client.get_user_tweets(user_id, "Tweets", count=count)
        results: list[FetchedTweet] = []
        for tweet in tweets:
            screen_name = getattr(tweet.user, "screen_name", "") if tweet.user else ""
            created_at = None
            if tweet.created_at:
                try:
                    created_at = parsedate_to_datetime(tweet.created_at)
                except (TypeError, ValueError):
                    created_at = None
            results.append(
                FetchedTweet(
                    tweet_id=str(tweet.id),
                    content=tweet.full_text or "",
                    url=f"https://x.com/{screen_name}/status/{tweet.id}" if screen_name else "",
                    tweet_created_at=created_at,
                )
            )
        return results


scraper = TwitterScraper()
