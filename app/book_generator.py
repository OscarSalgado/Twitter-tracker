import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Optional

from app.database import SessionLocal
from app.models import Account, Tweet

logger = logging.getLogger("tracker.book_generator")


class ThemeClassifier:
    def __init__(self, themes_file: str = "app/themes.json"):
        self.themes = self._load_themes(themes_file)

    def _load_themes(self, themes_file: str) -> list[dict]:
        try:
            with open(themes_file) as f:
                data = json.load(f)
            return data.get("themes", [])
        except FileNotFoundError:
            logger.warning("Themes file not found: %s", themes_file)
            return []

    def classify_tweet(self, content: str) -> Optional[str]:
        content_lower = content.lower()
        for theme in self.themes:
            for keyword in theme.get("keywords", []):
                if keyword.lower() in content_lower:
                    return theme["name"]
        return None

    def get_unclassified_theme(self) -> str:
        return "Sin clasificar"


class BookGenerator:
    def __init__(self):
        self.classifier = ThemeClassifier()

    def generate(self, output_file: str = "tweets_book.md") -> str:
        session = SessionLocal()
        try:
            tweets_by_theme = self._collect_tweets_by_theme(session)
            markdown = self._build_markdown(tweets_by_theme, session)
            self._write_file(output_file, markdown)
            return output_file
        finally:
            session.close()

    def _collect_tweets_by_theme(self, session) -> dict[str, list[dict]]:
        tweets_by_theme = defaultdict(list)

        tweets = session.query(Tweet).order_by(Tweet.tweet_created_at.desc()).all()

        for tweet in tweets:
            theme = self.classifier.classify_tweet(tweet.content)
            if theme is None:
                theme = self.classifier.get_unclassified_theme()

            tweet_data = {
                "content": tweet.content,
                "author": tweet.account.username,
                "display_name": tweet.account.display_name,
                "url": tweet.url,
                "created_at": tweet.tweet_created_at,
                "fetched_at": tweet.fetched_at,
            }
            tweets_by_theme[theme].append(tweet_data)

        return tweets_by_theme

    def _build_markdown(self, tweets_by_theme: dict[str, list[dict]], session) -> str:
        total_tweets = sum(len(tweets) for tweets in tweets_by_theme.values())
        total_accounts = session.query(Account).count()

        lines = [
            "# Recopilación de Tweets",
            "",
            f"**Generado automáticamente desde Twitter Tracker**",
            "",
            "## Resumen",
            "",
            f"- **Total de tweets**: {total_tweets}",
            f"- **Total de cuentas seguidas**: {total_accounts}",
            f"- **Temáticas**: {len(tweets_by_theme)}",
            "",
            "---",
            "",
        ]

        sorted_themes = sorted(
            tweets_by_theme.items(),
            key=lambda x: x[0] != self.classifier.get_unclassified_theme(),
        )

        for theme, tweets in sorted_themes:
            lines.append(f"## {theme}")
            lines.append("")
            lines.append(f"*{len(tweets)} tweets*")
            lines.append("")

            for tweet in tweets:
                lines.extend(self._format_tweet(tweet))
                lines.append("")

        return "\n".join(lines)

    def _format_tweet(self, tweet: dict) -> list[str]:
        lines = []

        author_display = tweet["display_name"] or tweet["author"]
        lines.append(f"**@{tweet['author']}** ({author_display})")

        if tweet["created_at"]:
            lines.append(f"_Publicado: {tweet['created_at'].strftime('%d/%m/%Y %H:%M')}_")
        else:
            lines.append(f"_Recopilado: {tweet['fetched_at'].strftime('%d/%m/%Y %H:%M')}_")

        lines.append("")
        lines.append(tweet["content"])

        if tweet["url"]:
            lines.append("")
            lines.append(f"[Ver en Twitter]({tweet['url']})")

        lines.append("")
        lines.append("---")

        return lines

    def _write_file(self, output_file: str, content: str) -> None:
        path = Path(output_file)
        path.write_text(content, encoding="utf-8")
        logger.info("Book generated: %s (%d bytes)", output_file, len(content))


def generate_book(output_file: str = "tweets_book.md") -> str:
    generator = BookGenerator()
    return generator.generate(output_file)
