from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from app.notifications import send_telegram_notification


async def test_skips_when_not_configured(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    with patch("app.notifications.httpx.AsyncClient") as mock_client_cls:
        result = await send_telegram_notification("alice", "hello", "https://x.com/alice/status/1")

    assert result is False
    mock_client_cls.assert_not_called()


def _make_mock_client(status_code=200, post_side_effect=None):
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.text = "error text"
    mock_client = AsyncMock()
    if post_side_effect is not None:
        mock_client.post = AsyncMock(side_effect=post_side_effect)
    else:
        mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


async def test_returns_true_on_success(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat456")

    mock_client = _make_mock_client(status_code=200)

    with patch("app.notifications.httpx.AsyncClient", return_value=mock_client):
        result = await send_telegram_notification("alice", "hello", "https://x.com/alice/status/1")

    assert result is True
    mock_client.post.assert_awaited_once()


async def test_returns_false_on_non_200(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat456")

    mock_client = _make_mock_client(status_code=400)

    with patch("app.notifications.httpx.AsyncClient", return_value=mock_client):
        result = await send_telegram_notification("alice", "hello", "https://x.com/alice/status/1")

    assert result is False


async def test_returns_false_on_timeout(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat456")

    mock_client = _make_mock_client(post_side_effect=httpx.TimeoutException("timeout"))

    with patch("app.notifications.httpx.AsyncClient", return_value=mock_client):
        result = await send_telegram_notification("alice", "hello", "https://x.com/alice/status/1")

    assert result is False


async def test_returns_false_on_request_error(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat456")

    mock_client = _make_mock_client(
        post_side_effect=httpx.RequestError("connection refused")
    )

    with patch("app.notifications.httpx.AsyncClient", return_value=mock_client):
        result = await send_telegram_notification("alice", "hello", "https://x.com/alice/status/1")

    assert result is False


async def test_returns_false_on_unexpected_error(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat456")

    mock_client = _make_mock_client(post_side_effect=RuntimeError("unexpected"))

    with patch("app.notifications.httpx.AsyncClient", return_value=mock_client):
        result = await send_telegram_notification("alice", "hello", "https://x.com/alice/status/1")

    assert result is False
