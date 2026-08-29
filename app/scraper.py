"""Thin wrapper around scweet (open source, no paid API keys required).

scweet scrapes Twitter/X by simulating a browser, so it can read public tweets
without needing Twitter's paid API tiers or login credentials. See
README.md for the legal/ToS caveats of this approach.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

try:
    from scweet import scrap
except ImportError:
    scrap = None

from app import config

logger = logging.getLogger("tracker.scraper")


class FetchedTweet(TypedDict):
    tweet_id: str
    content: str
    url: str
    tweet_created_at: object


class TwitterScraper:
    def __init__(self) -> None:
        self._logged_in = False
        self._last_login_error: str | None = None
        self._browser = None

    @property
    def is_logged_in(self) -> bool:
        return self._logged_in

    @property
    def last_login_error(self) -> str | None:
        return self._last_login_error

    async def login(self) -> None:
        """Initialize scweet (no credentials needed for public tweets)."""
        try:
            if scrap is None:
                raise RuntimeError(
                    "scweet no está instalado. Instala con: pip install scweet"
                )

            # scweet no requiere login para tweets públicos
            self._logged_in = True
            self._last_login_error = None
            logger.info("scweet inicializado (sin login requerido para tweets públicos).")
        except Exception as exc:
            self._logged_in = False
            self._last_login_error = str(exc)
            raise

    async def resolve_user(self, username: str):
        """Resolve a Twitter username to get user info."""
        username = username.lstrip("@")
        try:
            # scweet no proporciona un método directo para resolver usuarios
            # pero podemos usar search para validar que la cuenta existe
            tweets = await self.fetch_user_tweets(username, count=1)
            if tweets:
                return {"username": username}
            raise RuntimeError(f"No se pudo encontrar la cuenta @{username}")
        except Exception as exc:
            logger.error(f"Error resolviendo usuario {username}: {exc}")
            raise

    async def fetch_user_tweets(self, username: str, count: int = 100) -> list[FetchedTweet]:
        """Fetch tweets from a specific user using scweet."""
        try:
            username = username.lstrip("@")

            # Usar scweet para descargar tweets del usuario
            tweets_df = scrap(
                username=username,
                tweets_count=count,
                save_images=False,
                resume=False,
                proxy=None,
            )

            if tweets_df is None or tweets_df.empty:
                logger.warning(f"No se encontraron tweets para @{username}")
                return []

            results: list[FetchedTweet] = []

            for _, row in tweets_df.iterrows():
                try:
                    tweet_id = str(row.get("tweet_id", row.get("id", "")))
                    content = str(row.get("text", ""))
                    url = f"https://x.com/{username}/status/{tweet_id}"

                    # Parsear fecha
                    created_at = None
                    if "created_at" in row and row["created_at"]:
                        try:
                            if isinstance(row["created_at"], str):
                                created_at = datetime.fromisoformat(
                                    row["created_at"].replace("Z", "+00:00")
                                )
                            elif isinstance(row["created_at"], datetime):
                                created_at = row["created_at"]
                        except (ValueError, TypeError):
                            created_at = None

                    if tweet_id and content:
                        results.append(
                            FetchedTweet(
                                tweet_id=tweet_id,
                                content=content,
                                url=url,
                                tweet_created_at=created_at,
                            )
                        )
                except Exception as e:
                    logger.warning(f"Error procesando tweet: {e}")
                    continue

            logger.info(f"Se descargaron {len(results)} tweets de @{username}")
            return results

        except Exception as exc:
            logger.error(f"Error descargando tweets de @{username}: {exc}")
            raise


scraper = TwitterScraper()

