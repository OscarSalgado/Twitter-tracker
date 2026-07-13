import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app import config
from app.tracker_service import poll_all_accounts

logger = logging.getLogger("tracker.scheduler")

_scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    if _scheduler.running:
        return
    _scheduler.add_job(
        poll_all_accounts,
        "interval",
        minutes=config.POLL_INTERVAL_MINUTES,
        id="poll_all_accounts",
        next_run_time=None,
    )
    _scheduler.start()
    asyncio.get_event_loop().call_later(5, lambda: asyncio.ensure_future(poll_all_accounts()))
    logger.info("Scheduler iniciado: sondeo cada %d minutos.", config.POLL_INTERVAL_MINUTES)


def stop_scheduler() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
