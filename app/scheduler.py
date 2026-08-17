import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.database import SessionLocal
from app.services.ingestion import run_ingestion

logger = logging.getLogger("agent.scheduler")


async def scheduled_scrape_job():
    db = SessionLocal()
    try:
        new_count = await run_ingestion(db)
        logger.info("Scheduled scrape complete — %d new jobs", new_count)
    finally:
        db.close()


def start_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        lambda: asyncio.create_task(scheduled_scrape_job()),
        "interval",
        minutes=settings.scrape_interval_minutes,
        id="scrape_jobs",
    )
    scheduler.start()
    return scheduler
