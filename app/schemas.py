import datetime as dt
from pydantic import BaseModel, EmailStr, ConfigDict


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    title: str
    company: str | None = None
    location: str | None = None
    salary: str | None = None
    url: str | None = None
    tags: str | None = None
    posted_at: dt.datetime | None = None


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    resume_text: str | None = None
    skills: str | None = None            # comma-separated, e.g. "python,fastapi,sql"
    preferred_role: str | None = None
    preferred_location: str | None = None
    salary_min: int | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    preferred_role: str | None = None


class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    score: float
    summary: str | None = None
    red_flags: str | None = None
    status: str
    job: JobOut
