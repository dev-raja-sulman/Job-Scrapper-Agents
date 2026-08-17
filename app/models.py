import datetime as dt

from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False)          # e.g. "remoteok"
    external_id = Column(String(200), nullable=False)     # id from the source, for dedup
    title = Column(String(300), nullable=False)
    company = Column(String(200))
    location = Column(String(200))
    salary = Column(String(100))
    description = Column(Text)
    url = Column(String(500))
    tags = Column(String(500))                            # comma-separated
    posted_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=dt.datetime.utcnow)

    matches = relationship("Match", back_populates="job")

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_source_external_id"),
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    email = Column(String(200), unique=True, nullable=False)
    resume_text = Column(Text)
    skills = Column(String(1000))                         # comma-separated for v1
    preferred_role = Column(String(200))
    preferred_location = Column(String(200))
    salary_min = Column(Integer, nullable=True)

    matches = relationship("Match", back_populates="user")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    score = Column(Float, default=0.0)                    # 0-1 similarity score
    summary = Column(Text, nullable=True)                 # LLM-generated summary
    red_flags = Column(Text, nullable=True)
    status = Column(String(30), default="new")            # new/reviewed/applied/rejected
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    user = relationship("User", back_populates="matches")
    job = relationship("Job", back_populates="matches")

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job"),
    )
