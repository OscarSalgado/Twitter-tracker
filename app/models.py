from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(128), default="")
    twitter_user_id: Mapped[str] = mapped_column(String(32), default="")
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str] = mapped_column(Text, default="")

    tweets: Mapped[list["Tweet"]] = relationship(
        back_populates="account", cascade="all, delete-orphan", order_by="desc(Tweet.tweet_created_at)"
    )


class Tweet(Base):
    __tablename__ = "tweets"
    __table_args__ = (UniqueConstraint("tweet_id", name="uq_tweet_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tweet_id: Mapped[str] = mapped_column(String(32), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    content: Mapped[str] = mapped_column(Text, default="")
    url: Mapped[str] = mapped_column(String(256), default="")
    tweet_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    notified: Mapped[bool] = mapped_column(default=False)
    topic: Mapped[str] = mapped_column(String(32), default="other", index=True)
    topic_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    account: Mapped["Account"] = relationship(back_populates="tweets")
