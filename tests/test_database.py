from sqlalchemy import inspect

from app.database import engine, get_session, init_db
from app.models import Account


def test_init_db_creates_expected_tables():
    init_db()
    tables = inspect(engine).get_table_names()
    assert "accounts" in tables
    assert "tweets" in tables


def test_get_session_returns_usable_session():
    session = get_session()
    try:
        assert session.query(Account).count() == 0
    finally:
        session.close()
