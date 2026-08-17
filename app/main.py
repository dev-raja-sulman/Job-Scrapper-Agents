from loguru import logger
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import jobs, users
from app.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (fine for dev; use Alembic migrations in prod)
    Base.metadata.create_all(bind=engine)
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="Agentic AI Job Scraper",
    description="Autonomous job discovery, matching, and application assistant.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this to your actual frontend origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(users.router)

# Phase 6 dashboard — served at /app, talks to the API above via fetch()
app.mount("/app", StaticFiles(directory="static", html=True), name="dashboard")


@app.get("/")
def root():
    return {"status": "ok", "service": "agentic-job-scraper", "dashboard": "/app"}


@app.get("/health")
def health():
    return {"status": "healthy"}
