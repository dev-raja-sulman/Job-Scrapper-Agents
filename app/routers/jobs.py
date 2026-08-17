from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Job
from app.schemas import JobOut
from app.services.ingestion import run_ingestion

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobOut])
def list_jobs(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.scraped_at.desc()).limit(limit).all()


@router.post("/scrape")
async def trigger_scrape(db: Session = Depends(get_db)):
    """Manually trigger a scraping run (in production this also runs on a
    schedule — see app/scheduler.py)."""
    new_count = await run_ingestion(db)
    return {"new_jobs_inserted": new_count}
