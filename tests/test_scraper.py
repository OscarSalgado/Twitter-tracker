from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from app import config
from app.scraper import TwitterScraper


@pytest.fixture
def scraper(tmp_path, monkeypatch):
    cookies_file = tmp_path / "cookies.json"
    monkeypatch.setattr(config, "COOKIES_FILE", str(cookies_file))
    instance = TwitterScraper()
    instance._client = MagicMock()
    return instance


async def test_login_restores_from_existing_cookies(scraper):
    Path(config.COOKIES_FILE).write_text("{}")
    scraper._client.load_cookies = MagicMock()

    await scraper.login()

    scraper._client.load_cookies.assert_called_once_with(config.COOKIES_FILE)
    assert scraper._logged_in is True


async def test_login_falls_back_to_fresh_login_when_cookies_are_corrupt(scraper, monkeypatch):
    Path(config.COOKIES_FILE).write_text("not valid json")
    scraper._client.load_cookies = MagicMock(side_effect=RuntimeError("bad cookie jar"))
    scraper._client.login = AsyncMock()
    scraper._client.save_cookies = MagicMock()
    monkeypatch.setattr(config, "TWITTER_USERNAME", "user")
    monkeypatch.setattr(config, "TWITTER_EMAIL", "user@example.com")
    monkeypatch.setattr(config, "TWITTER_PASSWORD", "secret")

    await scraper.login()

    scraper._client.login.assert_awaited_once()
    scraper._client.save_cookies.assert_called_once_with(config.COOKIES_FILE)
    assert scraper._logged_in is True


async def test_login_raises_without_credentials(scraper, monkeypatch):
    monkeypatch.setattr(config, "TWITTER_USERNAME", "")
    monkeypatch.setattr(config, "TWITTER_PASSWORD", "")

    with pytest.raises(RuntimeError):
        await scraper.login()


async def test_login_success_without_existing_cookies(scraper, monkeypatch):
    monkeypatch.setattr(config, "TWITTER_USERNAME", "user")
    monkeypatch.setattr(config, "TWITTER_EMAIL", "")
    monkeypatch.setattr(config, "TWITTER_PASSWORD", "secret")
    scraper._client.login = AsyncMock()
    scraper._client.save_cookies = MagicMock()

    await scraper.login()

    scraper._client.login.assert_awaited_once_with(auth_info_1="user", auth_info_2=None, password="secret")
    assert scraper._logged_in is True


async def test_login_failure_marks_scraper_logged_out_with_error(scraper, monkeypatch):
    monkeypatch.setattr(config, "TWITTER_USERNAME", "")
    monkeypatch.setattr(config, "TWITTER_PASSWORD", "")

    with pytest.raises(RuntimeError):
        await scraper.login()

    assert scraper.is_logged_in is False
    assert scraper.last_login_error is not None
    assert "credenciales" in scraper.last_login_error.lower()


async def test_resolve_user_strips_at_and_delegates(scraper):
    scraper._client.get_user_by_screen_name = AsyncMock(return_value="user-obj")

    result = await scraper.resolve_user("@alice")

    scraper._client.get_user_by_screen_name.assert_awaited_once_with("alice")
    assert result == "user-obj"


async def test_fetch_user_tweets_parses_valid_and_malformed_entries(scraper):
    tweet_with_user = MagicMock()
    tweet_with_user.id = 123
    tweet_with_user.full_text = "hello"
    tweet_with_user.created_at = "Wed Oct 10 20:19:24 +0000 2018"
    tweet_with_user.user = MagicMock(screen_name="alice")

    tweet_no_user_no_date = MagicMock()
    tweet_no_user_no_date.id = 456
    tweet_no_user_no_date.full_text = ""
    tweet_no_user_no_date.created_at = ""
    tweet_no_user_no_date.user = None

    tweet_bad_date = MagicMock()
    tweet_bad_date.id = 789
    tweet_bad_date.full_text = "broken date"
    tweet_bad_date.created_at = "not-a-date"
    tweet_bad_date.user = MagicMock(screen_name="bob")

    scraper._client.get_user_tweets = AsyncMock(
        return_value=[tweet_with_user, tweet_no_user_no_date, tweet_bad_date]
    )

    results = await scraper.fetch_user_tweets("999", 20)

    scraper._client.get_user_tweets.assert_awaited_once_with("999", "Tweets", count=20)

    assert results[0]["tweet_id"] == "123"
    assert results[0]["url"] == "https://x.com/alice/status/123"
    assert results[0]["tweet_created_at"] is not None

    assert results[1]["tweet_id"] == "456"
    assert results[1]["content"] == ""
    assert results[1]["url"] == ""
    assert results[1]["tweet_created_at"] is None

    assert results[2]["tweet_id"] == "789"
    assert results[2]["url"] == "https://x.com/bob/status/789"
    assert results[2]["tweet_created_at"] is None
