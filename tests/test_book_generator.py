from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.book_generator import BookGenerator, ThemeClassifier, generate_book
from app.models import Account, Tweet


@pytest.fixture
def classifier():
    return ThemeClassifier("app/themes.json")


@pytest.fixture
def generator():
    return BookGenerator()


class TestThemeClassifier:
    def test_classify_tweet_with_matching_keyword(self, classifier):
        content = "Just discovered a new Python library for machine learning"
        theme = classifier.classify_tweet(content)
        assert theme == "Tecnología"

    def test_classify_tweet_case_insensitive(self, classifier):
        content = "TECH startup raising Series A funding"
        theme = classifier.classify_tweet(content)
        assert theme == "Tecnología"

    def test_classify_tweet_no_match(self, classifier):
        content = "Having a wonderful day at home"
        theme = classifier.classify_tweet(content)
        assert theme is None

    def test_get_unclassified_theme(self, classifier):
        assert classifier.get_unclassified_theme() == "Sin clasificar"


class TestBookGenerator:
    def test_format_tweet_with_url(self, generator):
        tweet = {
            "content": "Test tweet content",
            "author": "testuser",
            "display_name": "Test User",
            "url": "https://x.com/testuser/status/123",
            "created_at": datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc),
            "fetched_at": datetime(2024, 1, 15, 11, 0, tzinfo=timezone.utc),
        }
        lines = generator._format_tweet(tweet)
        text = "\n".join(lines)
        assert "@testuser" in text
        assert "Test tweet content" in text
        assert "https://x.com/testuser/status/123" in text

    def test_format_tweet_without_url(self, generator):
        tweet = {
            "content": "Test tweet",
            "author": "testuser",
            "display_name": "Test User",
            "url": "",
            "created_at": datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc),
            "fetched_at": datetime(2024, 1, 15, 11, 0, tzinfo=timezone.utc),
        }
        lines = generator._format_tweet(tweet)
        text = "\n".join(lines)
        assert "@testuser" in text
        assert "Test tweet" in text
        assert "http" not in text

    def test_collect_tweets_by_theme(self, generator):
        mock_session = MagicMock()
        mock_tweet1 = MagicMock(spec=Tweet)
        mock_tweet1.content = "Python programming tutorial"
        mock_tweet1.account.username = "user1"
        mock_tweet1.account.display_name = "User One"
        mock_tweet1.url = "https://x.com/user1/1"
        mock_tweet1.tweet_created_at = datetime(2024, 1, 15, tzinfo=timezone.utc)
        mock_tweet1.fetched_at = datetime(2024, 1, 15, tzinfo=timezone.utc)

        mock_tweet2 = MagicMock(spec=Tweet)
        mock_tweet2.content = "Just had coffee"
        mock_tweet2.account.username = "user2"
        mock_tweet2.account.display_name = "User Two"
        mock_tweet2.url = "https://x.com/user2/1"
        mock_tweet2.tweet_created_at = datetime(2024, 1, 14, tzinfo=timezone.utc)
        mock_tweet2.fetched_at = datetime(2024, 1, 14, tzinfo=timezone.utc)

        mock_session.query.return_value.order_by.return_value.all.return_value = [
            mock_tweet1,
            mock_tweet2,
        ]

        tweets_by_theme = generator._collect_tweets_by_theme(mock_session)

        assert "Tecnología" in tweets_by_theme
        assert "Sin clasificar" in tweets_by_theme
        assert len(tweets_by_theme["Tecnología"]) == 1
        assert len(tweets_by_theme["Sin clasificar"]) == 1

    @patch("app.book_generator.SessionLocal")
    def test_generate_creates_file(self, mock_session_local, tmp_path, generator):
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        mock_tweet = MagicMock(spec=Tweet)
        mock_tweet.content = "Test tweet"
        mock_tweet.account.username = "testuser"
        mock_tweet.account.display_name = "Test User"
        mock_tweet.url = "https://x.com/testuser/1"
        mock_tweet.tweet_created_at = datetime(2024, 1, 15, tzinfo=timezone.utc)
        mock_tweet.fetched_at = datetime(2024, 1, 15, tzinfo=timezone.utc)

        mock_session.query.return_value.order_by.return_value.all.return_value = [
            mock_tweet
        ]
        mock_session.query.return_value.count.return_value = 1

        output_file = str(tmp_path / "test_book.md")
        result = generator.generate(output_file)

        assert result == output_file
        assert Path(output_file).exists()
        content = Path(output_file).read_text()
        assert "Recopilación de Tweets" in content
        assert "Test tweet" in content

    def test_build_markdown_structure(self, generator):
        tweets_by_theme = {
            "Tecnología": [
                {
                    "content": "Tweet 1",
                    "author": "user1",
                    "display_name": "User 1",
                    "url": "https://x.com/user1/1",
                    "created_at": datetime(2024, 1, 15, tzinfo=timezone.utc),
                    "fetched_at": datetime(2024, 1, 15, tzinfo=timezone.utc),
                }
            ],
            "Sin clasificar": [
                {
                    "content": "Tweet 2",
                    "author": "user2",
                    "display_name": "User 2",
                    "url": "https://x.com/user2/1",
                    "created_at": datetime(2024, 1, 14, tzinfo=timezone.utc),
                    "fetched_at": datetime(2024, 1, 14, tzinfo=timezone.utc),
                }
            ],
        }

        mock_session = MagicMock()
        mock_session.query.return_value.count.return_value = 2

        markdown = generator._build_markdown(tweets_by_theme, mock_session)

        assert "# Recopilación de Tweets" in markdown
        assert "## Tecnología" in markdown
        assert "## Sin clasificar" in markdown
        assert "**Total de tweets**: 2" in markdown
        assert "**Total de cuentas seguidas**: 2" in markdown
        assert "Tweet 1" in markdown
        assert "Tweet 2" in markdown


def test_generate_book_function():
    with patch("app.book_generator.BookGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate.return_value = "test_book.md"

        result = generate_book("test_book.md")

        assert result == "test_book.md"
        mock_generator_class.assert_called_once()
        mock_generator.generate.assert_called_once_with("test_book.md")


def test_theme_classifier_handles_missing_themes_file():
    classifier = ThemeClassifier("nonexistent/path/themes.json")

    result = classifier.classify_tweet("test content")

    assert result is None
    assert classifier.themes == []


def test_format_tweet_without_created_at_uses_fetched_at():
    generator = BookGenerator()

    tweet = {
        "content": "Test tweet",
        "author": "testuser",
        "display_name": "Test User",
        "url": "https://x.com/testuser/status/123",
        "created_at": None,
        "fetched_at": datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc),
    }
    lines = generator._format_tweet(tweet)
    text = "\n".join(lines)

    assert "Recopilado" in text
    assert "15/01/2024" in text
