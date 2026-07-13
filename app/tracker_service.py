import logging
from datetime import datetime, timezone

from app import config
from app.database import get_session
from app.models import Account, Tweet
from app.notifier import notify_new_tweet
from app.scraper import scraper

logger = logging.getLogger("tracker.service")


async def add_account(username: str) -> Account:
    username = username.strip().lstrip("@")
    session = get_session()
    try:
        existing = session.query(Account).filter_by(username=username).first()
        if existing:
            return existing

        user = await scraper.resolve_user(username)
        account = Account(
            username=username,
            display_name=getattr(user, "name", username),
            twitter_user_id=str(user.id),
        )
        session.add(account)
        session.commit()
        session.refresh(account)
        return account
    finally:
        session.close()


def remove_account(account_id: int) -> None:
    session = get_session()
    try:
        account = session.get(Account, account_id)
        if account:
            session.delete(account)
            session.commit()
    finally:
        session.close()


async def poll_account(session, account: Account) -> int:
    new_count = 0
    try:
        fetched = await scraper.fetch_user_tweets(
            account.twitter_user_id, config.TWEETS_PER_ACCOUNT_PER_POLL
        )
    except Exception as exc:
        logger.exception("Fallo al consultar tuits de @%s", account.username)
        account.last_error = str(exc)
        account.last_checked_at = datetime.now(timezone.utc)
        session.commit()
        return 0

    existing_ids = {
        row.tweet_id
        for row in session.query(Tweet.tweet_id).filter_by(account_id=account.id).all()
    }

    for item in fetched:
        if item["tweet_id"] in existing_ids:
            continue
        tweet = Tweet(
            tweet_id=item["tweet_id"],
            account_id=account.id,
            content=item["content"],
            url=item["url"],
            tweet_created_at=item["tweet_created_at"],
        )
        session.add(tweet)
        new_count += 1
        await notify_new_tweet(account.username, item["content"], item["url"])
        tweet.notified = True

    account.last_error = ""
    account.last_checked_at = datetime.now(timezone.utc)
    session.commit()
    return new_count


async def poll_all_accounts() -> int:
    session = get_session()
    total_new = 0
    try:
        accounts = session.query(Account).all()
        for account in accounts:
            total_new += await poll_account(session, account)
    finally:
        session.close()
    logger.info("Ronda de sondeo completada: %d tuits nuevos.", total_new)
    return total_new
