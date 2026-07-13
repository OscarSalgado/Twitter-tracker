import os
import tempfile

_tmp_dir = tempfile.mkdtemp(prefix="twitter-tracker-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_dir}/test.db"
os.environ["BASIC_AUTH_USER"] = "admin"
os.environ["BASIC_AUTH_PASSWORD"] = "test-password"
os.environ["TWITTER_USERNAME"] = ""
os.environ["TWITTER_EMAIL"] = ""
os.environ["TWITTER_PASSWORD"] = ""
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["TELEGRAM_CHAT_ID"] = ""
os.environ["POLL_INTERVAL_MINUTES"] = "15"

import pytest

from app.database import Base, engine, init_db


@pytest.fixture(autouse=True)
def clean_db():
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)
