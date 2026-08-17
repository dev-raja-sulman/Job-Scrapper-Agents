from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Job, Match
from app.schemas import UserCreate, UserOut, MatchOut
from app.services.matching import rank_jobs
from app.services.llm import summarize_job, draft_cover_letter
from app.services.resume_parser import extract_resume_text

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(email=payload.email).first()
    if existing:
        raise HTTPException(400, "User with this email already exists")

    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/match", response_model=list[MatchOut])
def generate_matches(user_id: int, top_n: int = 10, db: Session = Depends(get_db)):
    """Phase 2/3: rank all jobs against the user's skills, summarize the
    top N with the LLM, and persist as Match rows."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    all_jobs = db.query(Job).all()
    ranked = rank_jobs(user, all_jobs, top_n=top_n)

    results = []
    for job, score in ranked:
        match = db.query(Match).filter_by(user_id=user.id, job_id=job.id).first()
        if not match:
            llm_result = summarize_job(job.title, job.company or "", job.description or "")
            match = Match(
                user_id=user.id,
                job_id=job.id,
                score=score,
                summary=llm_result.get("summary", ""),
                red_flags=llm_result.get("red_flags", ""),
                status="new",
            )
            db.add(match)
        else:
            match.score = score

        results.append(match)

    db.commit()
    for m in results:
        db.refresh(m)

    return results


@router.get("/{user_id}/matches", response_model=list[MatchOut])
def list_matches(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Match)
        .filter_by(user_id=user_id)
        .order_by(Match.score.desc())
        .all()
    )


@router.post("/{user_id}/resume", response_model=UserOut)
async def upload_resume(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Phase 2: upload a PDF/DOCX/TXT resume — extracted text is stored on
    the user and used by matching + cover-letter generation."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    text = await extract_resume_text(file)
    if not text.strip():
        raise HTTPException(422, "Could not extract any text from that file")

    user.resume_text = text
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/matches/{match_id}/cover-letter")
def generate_cover_letter(user_id: int, match_id: int, db: Session = Depends(get_db)):
    """Phase 5: draft a tailored cover letter for a specific match, for the
    user to review and edit before sending."""
    user = db.get(User, user_id)
    match = db.get(Match, match_id)
    if not user or not match or match.user_id != user_id:
        raise HTTPException(404, "User or match not found")

    job = match.job
    letter = draft_cover_letter(
        user_resume=user.resume_text or "",
        job_title=job.title,
        company=job.company or "",
        job_description=job.description or "",
    )
    return {"match_id": match_id, "cover_letter": letter}


@router.post("/{user_id}/matches/{match_id}/auto-apply")
async def trigger_auto_apply(user_id: int, match_id: int, db: Session = Depends(get_db)):
    """Phase 7: Trigger the Playwright auto-apply copilot."""
    from app.services.auto_apply import auto_apply_copilot
    
    user = db.get(User, user_id)
    match = db.get(Match, match_id)
    if not user or not match or match.user_id != user_id:
        raise HTTPException(404, "User or match not found")

    job = match.job
    if not job.url:
        raise HTTPException(400, "Job has no URL to apply to")
        
    # Generate cover letter if not already stored (we just draft it here quickly)
    letter = draft_cover_letter(
        user_resume=user.resume_text or "",
        job_title=job.title,
        company=job.company or "",
        job_description=job.description or "",
    )
    
    screenshot_url = await auto_apply_copilot(
        job_url=job.url,
        user_name=user.name,
        user_email=user.email,
        cover_letter=letter
    )
    
    if not screenshot_url:
        raise HTTPException(500, "Failed to run auto-apply copilot (is Playwright installed?)")
        
    return {"match_id": match_id, "screenshot_url": screenshot_url}


@router.post("/{user_id}/matches/{match_id}/interview-prep")
def get_interview_prep(user_id: int, match_id: int, db: Session = Depends(get_db)):
    """Generate interview preparation questions for a specific match."""
    from app.services.llm import generate_interview_prep
    
    user = db.get(User, user_id)
    match = db.get(Match, match_id)
    if not user or not match or match.user_id != user_id:
        raise HTTPException(404, "User or match not found")

    job = match.job
    prep = generate_interview_prep(
        user_resume=user.resume_text or "",
        job_title=job.title,
        company=job.company or "",
        job_description=job.description or "",
    )
    return {"match_id": match_id, "prep_notes": prep}


@router.patch("/{user_id}/matches/{match_id}/status")
def update_match_status(user_id: int, match_id: int, status: str, db: Session = Depends(get_db)):
    """Update a match's status as the user works through their review queue:
    new -> reviewed -> applied -> rejected."""
    allowed = {"new", "reviewed", "applied", "rejected"}
    if status not in allowed:
        raise HTTPException(400, f"status must be one of {sorted(allowed)}")

    match = db.get(Match, match_id)
    if not match or match.user_id != user_id:
        raise HTTPException(404, "Match not found")

    match.status = status
    db.commit()
    db.refresh(match)
    return match
