import asyncio

import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import app.scheduler as scheduler_module


@pytest.fixture
def isolated_scheduler(monkeypatch):
    fresh = AsyncIOScheduler()
    monkeypatch.setattr(scheduler_module, "_scheduler", fresh)
    yield fresh
    try:
        if fresh.running:
            fresh.shutdown(wait=False)
    except RuntimeError:
        pass  # this test's event loop is already closed by the time teardown runs


async def test_start_scheduler_registers_interval_job(isolated_scheduler):
    scheduler_module.start_scheduler()

    assert isolated_scheduler.running is True
    assert isolated_scheduler.get_job("poll_all_accounts") is not None


async def test_start_scheduler_is_idempotent(isolated_scheduler):
    scheduler_module.start_scheduler()
    scheduler_module.start_scheduler()

    assert isolated_scheduler.running is True


def test_stop_scheduler_is_a_noop_when_not_running(isolated_scheduler):
    scheduler_module.stop_scheduler()

    assert isolated_scheduler.running is False


async def test_stop_scheduler_shuts_down_a_running_scheduler(isolated_scheduler):
    scheduler_module.start_scheduler()

    scheduler_module.stop_scheduler()
    await asyncio.sleep(0)

    assert isolated_scheduler.running is False
