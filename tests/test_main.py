from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app import config
from app.database import get_session
from app.main import app
from app.models import Account, Tweet


@pytest.fixture(autouse=True)
def mock_lifespan_dependencies():
    with patch("app.main.scraper") as mock_scraper, patch("app.main.start_scheduler"), patch(
        "app.main.stop_scheduler"
    ):
        mock_scraper.login = AsyncMock()
        yield mock_scraper


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_healthz_is_unauthenticated(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "twitter_login": "ok"}


def test_healthz_reports_twitter_login_error(client, mock_lifespan_dependencies):
    mock_lifespan_dependencies.is_logged_in = False

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "twitter_login": "error"}


def test_dashboard_requires_auth_without_credentials(client):
    response = client.get("/")

    assert response.status_code == 401


def test_dashboard_rejects_wrong_credentials(client):
    response = client.get("/", auth=("admin", "wrong-password"))

    assert response.status_code == 401


def test_dashboard_renders_empty_state_with_correct_credentials(client):
    response = client.get("/", auth=("admin", "test-password"))

    assert response.status_code == 200
    assert "Todav" in response.text


def test_dashboard_allows_anonymous_access_when_auth_disabled(client, monkeypatch):
    monkeypatch.setattr(config, "BASIC_AUTH_PASSWORD", "")

    response = client.get("/")

    assert response.status_code == 200


def test_dashboard_lists_accounts_and_recent_tweets(client):
    session = get_session()
    account = Account(username="ivan", display_name="Ivan", twitter_user_id="8")
    session.add(account)
    session.commit()
    session.add(
        Tweet(
            tweet_id="t100",
            account_id=account.id,
            content="hola con fecha",
            url="https://x.com/ivan/status/t100",
            tweet_created_at=datetime.now(timezone.utc),
        )
    )
    session.add(
        Tweet(
            tweet_id="t101",
            account_id=account.id,
            content="hola sin fecha",
            url="https://x.com/ivan/status/t101",
            tweet_created_at=None,
        )
    )
    session.commit()
    session.close()

    response = client.get("/", auth=("admin", "test-password"))

    assert response.status_code == 200
    assert "ivan" in response.text
    assert "hola con fecha" in response.text
    assert "hola sin fecha" in response.text


def test_create_account_success_redirects(client):
    with patch("app.main.add_account", new=AsyncMock(return_value=None)) as mock_add:
        response = client.post(
            "/accounts",
            data={"username": "newuser"},
            auth=("admin", "test-password"),
            follow_redirects=False,
        )

    mock_add.assert_awaited_once_with("newuser")
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_create_account_failure_returns_400(client):
    with patch("app.main.add_account", new=AsyncMock(side_effect=RuntimeError("boom"))):
        response = client.post(
            "/accounts",
            data={"username": "ghost"},
            auth=("admin", "test-password"),
            follow_redirects=False,
        )

    assert response.status_code == 400


def test_delete_account_removes_row_and_redirects(client):
    session = get_session()
    account = Account(username="jorge", display_name="Jorge", twitter_user_id="9")
    session.add(account)
    session.commit()
    account_id = account.id
    session.close()

    response = client.post(
        f"/accounts/{account_id}/delete", auth=("admin", "test-password"), follow_redirects=False
    )

    assert response.status_code == 303
    session = get_session()
    try:
        assert session.get(Account, account_id) is None
    finally:
        session.close()


def test_check_now_triggers_poll_and_redirects(client):
    with patch("app.main.poll_all_accounts", new=AsyncMock(return_value=3)) as mock_poll:
        response = client.post("/check-now", auth=("admin", "test-password"), follow_redirects=False)

    assert response.status_code == 303
    mock_poll.assert_awaited_once()


def test_lifespan_logs_and_continues_when_twitter_login_fails():
    with patch("app.main.scraper") as mock_scraper, patch("app.main.start_scheduler") as mock_start, patch(
        "app.main.stop_scheduler"
    ) as mock_stop:
        mock_scraper.login = AsyncMock(side_effect=RuntimeError("no credentials"))

        with TestClient(app):
            pass

        mock_start.assert_called_once()
        mock_stop.assert_called_once()
