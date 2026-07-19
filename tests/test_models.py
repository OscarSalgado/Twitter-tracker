from datetime import datetime, timezone

from app.database import get_session
from app.models import Account, Tweet, utcnow


def test_utcnow_returns_timezone_aware_datetime():
    now = utcnow()
    assert now.tzinfo is not None


def test_account_tweet_relationship_defaults_and_cascade_delete():
    session = get_session()
    try:
        account = Account(username="alice", display_name="Alice", twitter_user_id="1")
        session.add(account)
        session.commit()

        tweet = Tweet(
            tweet_id="t1",
            account_id=account.id,
            content="hi",
            url="https://x.com/alice/status/t1",
            tweet_created_at=datetime.now(timezone.utc),
        )
        session.add(tweet)
        session.commit()
        session.refresh(account)

        assert tweet.notified is False
        assert len(account.tweets) == 1

        session.delete(account)
        session.commit()

        assert session.query(Tweet).filter_by(tweet_id="t1").first() is None
    finally:
        session.close()
