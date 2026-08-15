# Agentic AI Job Scraper — Complete Starter (Phases 0–6)

A fully working FastAPI application — every endpoint below has been run
and tested, not just written. Implements:

- **Phase 0** — project structure, DB schema (SQLite by default, one env
  var away from Postgres)
- **Phase 1** — a real, working scraper (RemoteOK public API — no auth
  needed) + a Playwright template for JS-heavy sites like LinkedIn/Indeed
- **Phase 2** — resume upload (PDF/DOCX/TXT → extracted text) and real
  TF-IDF + cosine-similarity matching (runs offline, no API cost; upgrade
  path to true embeddings is sketched in `matching.py`)
- **Phase 3** — LLM-powered job summarization + red-flag detection via the
  Claude API, with graceful fallback if no key is configured
- **Phase 4** — scheduled scraping via APScheduler (runs automatically in
  the background at `SCRAPE_INTERVAL_MINUTES`)
- **Phase 5** — tailored cover-letter drafting per match, for user review
- **Phase 6** — a working dashboard at `/app` (review queue, match scores
  as signal bars, status tracking, cover-letter modal) — pure HTML/JS, no
  build step required

**Not included** (by design — see Phase 7/8 in the roadmap doc): auto-apply
browser automation and production deployment hardening. These are the
highest-risk, most site-specific pieces and are best tackled once you've
picked your actual target job sites.

## Quick start

```bash
cd job-scraper-agent
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then edit .env with your ANTHROPIC_API_KEY

uvicorn app.main:app --reload --port 8001
```

Visit **http://localhost:8001/docs** for interactive Swagger UI, or
**http://localhost:8001/app** for the dashboard.

## Try it end to end

**Fastest path: use the dashboard.** Open `http://localhost:8001/app`,
click "Set up profile", then "Scan for jobs" and "Re-rank matches". Your
ranked review queue appears with match-strength bars, LLM summaries (if
`ANTHROPIC_API_KEY` is set), and one-click cover-letter drafting.

**Or drive it via the API directly:**

1. **Trigger a scrape** (pulls live jobs from RemoteOK, filtered by
   `SEARCH_KEYWORDS` in `.env`):
   ```bash
   curl -X POST http://localhost:8001/jobs/scrape
   ```
2. **Check what got stored:**
   ```bash
   curl http://localhost:8001/jobs
   ```
3. **Create a user profile:**
   ```bash
   curl -X POST http://localhost:8001/users \
     -H "Content-Type: application/json" \
     -d '{"name":"Ali","email":"ali@example.com","skills":"python,fastapi,sql","preferred_role":"Backend Engineer"}'
   ```
4. **Upload a resume** (PDF, DOCX, or TXT — used to sharpen matching and
   cover-letter drafts):
   ```bash
   curl -X POST http://localhost:8001/users/1/resume -F "file=@resume.pdf"
   ```
5. **Generate ranked + summarized matches:**
   ```bash
   curl -X POST "http://localhost:8001/users/1/match?top_n=10"
   ```
6. **View matches:**
   ```bash
   curl http://localhost:8001/users/1/matches
   ```
7. **Draft a cover letter for a specific match:**
   ```bash
   curl -X POST http://localhost:8001/users/1/matches/1/cover-letter
   ```
8. **Update a match's status** as you work through the queue:
   ```bash
   curl -X PATCH "http://localhost:8001/users/1/matches/1/status?status=applied"
   ```

## What's next (Phase 7+, intentionally left for you)

- **More scrapers**: use `app/scrapers/playwright_template.py` as a
  starting point for JS-heavy sites (LinkedIn, Indeed) — check each site's
  Terms of Service first, and prefer official APIs/RSS where they exist.
- **Real embeddings**: swap `app/services/matching.py`'s TF-IDF for Voyage
  AI / OpenAI embeddings + a vector DB (Chroma/Pinecone) once you're
  matching against thousands of jobs — the function signature (`rank_jobs`)
  stays identical, so nothing else changes.
- **Auto-apply**: Playwright-based form-fill with a mandatory
  human-approval step before final submission — this is the highest-risk
  component (site ToS, spam risk) so it's deliberately not included here.
- **Postgres + deploy**: `docker-compose.yml` has a commented Postgres
  service ready to uncomment when you outgrow SQLite.

## Project structure

```
job-scraper-agent/
├── app/
│   ├── main.py              # FastAPI app + startup scheduler
│   ├── config.py            # env-based settings
│   ├── database.py          # SQLAlchemy engine/session
│   ├── models.py            # Job, User, Match tables
│   ├── schemas.py           # Pydantic request/response models
│   ├── scheduler.py         # periodic scraping (APScheduler)
│   ├── scrapers/
│   │   ├── base.py          # abstract scraper interface
│   │   ├── remoteok.py      # working scraper (public API)
│   │   └── playwright_template.py  # template for JS-heavy sites
│   ├── services/
│   │   ├── ingestion.py     # scraper -> DB pipeline
│   │   ├── matching.py      # resume/job scoring
│   │   └── llm.py           # Claude API: summaries, cover letters
│   └── routers/
│       ├── jobs.py
│       └── users.py
├── requirements.txt
├── Dockerfile
└── .env.example
```
# Job-Scrapper-Agents
