#!/usr/bin/env python3
"""
Demo script to show book generation functionality.
Creates sample tweets in memory and generates a markdown book.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from app.book_generator import BookGenerator


def create_sample_tweets():
    tweets = []

    account_data = [
        ("python_dev", "Python Developer"),
        ("tech_news", "Tech News"),
        ("sports_fan", "Sports Fan"),
    ]

    sample_contents = [
        ("python_dev", "Just deployed a new Python service using FastAPI. Performance is amazing!", "Tecnología"),
        ("python_dev", "Learning about async/await patterns in Python. Mind blown!", "Tecnología"),
        ("tech_news", "New AI breakthrough: transformer models reach new performance milestone", "Tecnología"),
        ("tech_news", "Apple announces new M4 chip with incredible performance gains", "Tecnología"),
        ("sports_fan", "What an amazing football match! My team won 3-2 in extra time", "Deportes"),
        ("sports_fan", "Tennis tournament was incredible, watched the final match today", "Deportes"),
    ]

    now = datetime.now(timezone.utc)
    for i, (author, display_name) in enumerate(account_data):
        for j, (content_author, content, theme) in enumerate(sample_contents):
            if content_author == author:
                tweet = MagicMock()
                tweet.content = content
                tweet.account = MagicMock()
                tweet.account.username = author
                tweet.account.display_name = display_name
                tweet.url = f"https://x.com/{author}/status/{i * 100 + j}"
                tweet.tweet_created_at = now - timedelta(days=j)
                tweet.fetched_at = now - timedelta(hours=j)
                tweets.append(tweet)

    return tweets


def demo():
    print("📖 Twitter Tracker - Book Generator Demo\n")
    print("=" * 50)

    generator = BookGenerator()
    print("\n1. Sample Tweets:")
    print("-" * 50)

    mock_session = MagicMock()
    sample_tweets = create_sample_tweets()

    mock_session.query.return_value.order_by.return_value.all.return_value = sample_tweets
    mock_session.query.return_value.count.return_value = 3

    tweets_by_theme = generator._collect_tweets_by_theme(mock_session)

    for theme, tweets in sorted(tweets_by_theme.items()):
        print(f"\n  {theme} ({len(tweets)} tweets)")
        for tweet in tweets[:2]:
            print(f"    - @{tweet['author']}: {tweet['content'][:50]}...")

    print("\n2. Generating Markdown...")
    print("-" * 50)

    markdown = generator._build_markdown(tweets_by_theme, mock_session)

    output_file = "/tmp/demo_tweets_book.md"
    with open(output_file, "w") as f:
        f.write(markdown)

    print(f"✓ Book generated: {output_file}")
    print(f"✓ Size: {len(markdown)} bytes")
    print(f"✓ Themes: {len(tweets_by_theme)}")
    print(f"✓ Tweets: {sum(len(t) for t in tweets_by_theme.values())}")

    print("\n3. Preview (first 1000 chars):")
    print("-" * 50)
    print(markdown[:1000])
    print("\n...")

    print("\n✓ Demo completed successfully!")


if __name__ == "__main__":
    demo()
