from unittest.mock import AsyncMock, MagicMock, patch

from app import config
from app.notifier import notify_new_tweet


async def test_skips_when_telegram_not_configured(monkeypatch):
    monkeypatch.setattr(config, "TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setattr(config, "TELEGRAM_CHAT_ID", "")

    with patch("app.notifier.httpx.AsyncClient") as mock_client_cls:
        await notify_new_tweet("alice", "hello", "https://x.com/alice/status/1")

    mock_client_cls.assert_not_called()


def _mock_async_client(post_result=None, post_side_effect=None):
    mock_client = AsyncMock()
    if post_side_effect is not None:
        mock_client.post = AsyncMock(side_effect=post_side_effect)
    else:
        mock_client.post = AsyncMock(return_value=post_result)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


async def test_sends_message_when_configured(monkeypatch):
    monkeypatch.setattr(config, "TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setattr(config, "TELEGRAM_CHAT_ID", "chat-id")

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_client = _mock_async_client(post_result=mock_response)

    with patch("app.notifier.httpx.AsyncClient", return_value=mock_client):
        await notify_new_tweet("alice", "hello", "https://x.com/alice/status/1")

    mock_client.post.assert_awaited_once()
    args, kwargs = mock_client.post.call_args
    assert kwargs["json"]["chat_id"] == "chat-id"
    assert "alice" in kwargs["json"]["text"]


async def test_logs_failure_without_raising(monkeypatch):
    monkeypatch.setattr(config, "TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setattr(config, "TELEGRAM_CHAT_ID", "chat-id")

    mock_client = _mock_async_client(post_side_effect=RuntimeError("network down"))

    with patch("app.notifier.httpx.AsyncClient", return_value=mock_client):
        await notify_new_tweet("alice", "hello", "https://x.com/alice/status/1")

    mock_client.post.assert_awaited_once()
