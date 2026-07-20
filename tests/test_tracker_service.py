from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app import tracker_service
from app.database import get_session
from app.models import Account, Tweet


async def test_add_account_new_resolves_and_persists():
    fake_user = MagicMock(id=42)
    fake_user.name = "Alice"
    with patch("app.tracker_service.scraper") as mock_scraper:
        mock_scraper.resolve_user = AsyncMock(return_value=fake_user)
        account = await tracker_service.add_account("@alice")

    assert account.username == "alice"
    assert account.twitter_user_id == "42"
    assert account.display_name == "Alice"


async def test_add_account_already_tracked_skips_resolve():
    session = get_session()
    try:
        session.add(Account(username="bob", display_name="Bob", twitter_user_id="1"))
        session.commit()
    finally:
        session.close()

    with patch("app.tracker_service.scraper") as mock_scraper:
        mock_scraper.resolve_user = AsyncMock()
        account = await tracker_service.add_account("bob")

    mock_scraper.resolve_user.assert_not_called()
    assert account.username == "bob"


async def test_add_account_unresolvable_username_propagates_error():
    with patch("app.tracker_service.scraper") as mock_scraper:
        mock_scraper.resolve_user = AsyncMock(side_effect=RuntimeError("not found"))
        with pytest.raises(RuntimeError):
            await tracker_service.add_account("ghost")


def test_remove_account_deletes_existing_row():
    session = get_session()
    try:
        account = Account(username="carol", display_name="Carol", twitter_user_id="2")
        session.add(account)
        session.commit()
        account_id = account.id
    finally:
        session.close()

    tracker_service.remove_account(account_id)

    session = get_session()
    try:
        assert session.get(Account, account_id) is None
    finally:
        session.close()


def test_remove_account_missing_id_is_a_noop():
    tracker_service.remove_account(999999)


async def test_poll_account_stores_new_tweets_and_notifies():
    session = get_session()
    account = Account(username="dave", display_name="Dave", twitter_user_id="3")
    session.add(account)
    session.commit()

    fetched = [
        {
            "tweet_id": "1",
            "content": "hi",
            "url": "https://x.com/dave/status/1",
            "tweet_created_at": datetime.now(timezone.utc),
        }
    ]
    with patch("app.tracker_service.scraper") as mock_scraper, patch(
        "app.tracker_service.notify_new_tweet", new=AsyncMock()
    ) as mock_notify:
        mock_scraper.fetch_user_tweets = AsyncMock(return_value=fetched)
        new_count = await tracker_service.poll_account(session, account)

    assert new_count == 1
    mock_notify.assert_awaited_once()
    stored = session.query(Tweet).filter_by(account_id=account.id).all()
    assert len(stored) == 1
    assert stored[0].notified is True
    assert account.last_error == ""
    assert account.last_checked_at is not None
    session.close()


async def test_poll_account_skips_already_stored_tweets():
    session = get_session()
    account = Account(username="erin", display_name="Erin", twitter_user_id="4")
    session.add(account)
    session.commit()
    session.add(
        Tweet(tweet_id="dup", account_id=account.id, content="old", url="https://x.com/erin/status/dup")
    )
    session.commit()

    fetched = [{"tweet_id": "dup", "content": "old", "url": "https://x.com/erin/status/dup", "tweet_created_at": None}]
    with patch("app.tracker_service.scraper") as mock_scraper, patch(
        "app.tracker_service.notify_new_tweet", new=AsyncMock()
    ) as mock_notify:
        mock_scraper.fetch_user_tweets = AsyncMock(return_value=fetched)
        new_count = await tracker_service.poll_account(session, account)

    assert new_count == 0
    mock_notify.assert_not_awaited()
    session.close()


async def test_poll_account_records_fetch_failure_on_account():
    session = get_session()
    account = Account(username="frank", display_name="Frank", twitter_user_id="5")
    session.add(account)
    session.commit()

    with patch("app.tracker_service.scraper") as mock_scraper:
        mock_scraper.fetch_user_tweets = AsyncMock(side_effect=RuntimeError("rate limited"))
        new_count = await tracker_service.poll_account(session, account)

    assert new_count == 0
    assert account.last_error == "rate limited"
    assert account.last_checked_at is not None
    session.close()


async def test_poll_all_accounts_aggregates_across_accounts():
    session = get_session()
    session.add_all(
        [
            Account(username="gina", display_name="Gina", twitter_user_id="6"),
            Account(username="hank", display_name="Hank", twitter_user_id="7"),
        ]
    )
    session.commit()
    session.close()

    async def fake_poll_account(_session, _account):
        return 1

    with patch("app.tracker_service.scraper") as mock_scraper, patch(
        "app.tracker_service.poll_account", new=AsyncMock(side_effect=fake_poll_account)
    ):
        mock_scraper.is_logged_in = True
        total = await tracker_service.poll_all_accounts()

    assert total == 2


async def test_poll_all_accounts_logs_in_when_not_already_logged_in():
    with patch("app.tracker_service.scraper") as mock_scraper, patch(
        "app.tracker_service.poll_account", new=AsyncMock(return_value=0)
    ):
        mock_scraper.is_logged_in = False
        mock_scraper.login = AsyncMock()
        total = await tracker_service.poll_all_accounts()

    mock_scraper.login.assert_awaited_once()
    assert total == 0


async def test_poll_all_accounts_skips_poll_when_login_retry_fails():
    with patch("app.tracker_service.scraper") as mock_scraper, patch(
        "app.tracker_service.poll_account", new=AsyncMock(return_value=1)
    ) as mock_poll_account:
        mock_scraper.is_logged_in = False
        mock_scraper.login = AsyncMock(side_effect=RuntimeError("no credentials"))
        total = await tracker_service.poll_all_accounts()

    mock_scraper.login.assert_awaited_once()
    mock_poll_account.assert_not_awaited()
    assert total == 0
