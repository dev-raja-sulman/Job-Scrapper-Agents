from sqlalchemy.orm import Session

from app.models import Job
from app.scrapers.remoteok import RemoteOKScraper
from app.config import settings

# Registry of active scrapers. Add new sources here as they're built
# (Phase 1 roadmap item) — the rest of the pipeline needs no changes.
SCRAPERS = [RemoteOKScraper()]


async def run_ingestion(db: Session) -> int:
    """Fetch fresh postings from every registered scraper and upsert them.
    Returns the number of NEW jobs inserted."""
    inserted = 0

    for scraper in SCRAPERS:
        postings = await scraper.fetch_jobs(settings.keyword_list)

        for posting in postings:
            exists = (
                db.query(Job)
                .filter_by(source=posting["source"], external_id=posting["external_id"])
                .first()
            )
            if exists:
                continue

            db.add(Job(**posting))
            inserted += 1

        db.commit()

    return inserted
