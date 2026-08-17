<div align="center">
  <h1>🚀 Agentic AI Job Scraper</h1>
  <p><strong>Autonomous Job Discovery, Matching, and Application Assistant</strong></p>
</div>

---

A fully functional, end-to-end FastAPI application designed to streamline the job search process using Agentic AI. This platform automates job scraping, intelligent resume matching using TF-IDF, and AI-powered job summarization and cover letter drafting using the **Groq API**.

## ✨ Features (Phases 0–6 Implemented)

- **Phase 0: Solid Foundation** — Clean project structure with a scalable database schema (SQLite by default, easily upgradeable to Postgres).
- **Phase 1: Autonomous Scraper** — A real, working scraper for the RemoteOK public API, plus a Playwright template for JS-heavy sites like LinkedIn or Indeed.
- **Phase 2: Intelligent Matching** — Resume parsing (PDF/DOCX/TXT) with offline TF-IDF and cosine-similarity matching to rank jobs against your skills. No API costs for matching.
- **Phase 3: AI Summarization & Insights** — LLM-powered job summarization and red-flag detection (e.g., vague pay, unrealistic requirements) powered by the **Groq API** (Mixtral 8x7B). Falls back gracefully if no API key is provided.
- **Phase 4: Scheduled Operations** — Automated background scraping using `APScheduler` at customizable intervals.
- **Phase 5: Automated Cover Letters** — Tailored cover-letter drafting based on the specific job description and your resume.
- **Phase 6: Interactive Dashboard** — A zero-build vanilla HTML/JS dashboard at `/app` featuring a review queue, visual match scores, LLM insights, and a cover-letter generation modal.

> **Note:** Auto-apply browser automation (Phase 7) is intentionally excluded from the base project due to site-specific Terms of Service and varying anti-bot measures.

---

## 🛠️ Technology Stack

- **Backend Framework:** FastAPI, Uvicorn
- **Database:** SQLAlchemy (SQLite, Postgres-ready)
- **AI & NLP:** Groq API (Mixtral 8x7B), Scikit-Learn (TF-IDF, Cosine Similarity)
- **Background Tasks:** APScheduler
- **Document Processing:** PyPDF, python-docx
- **Frontend:** Vanilla HTML/JS/CSS (served statically via FastAPI)

---

## 🚀 Quick Start

### 1. Clone & Setup Environment

```bash
# Navigate to the project directory
cd job-scraper-agent

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Open `.env` and configure your **Groq API Key**:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --port 8001
```

- 🌐 **Interactive Dashboard:** [http://localhost:8001/app](http://localhost:8001/app)
- 📖 **API Documentation (Swagger UI):** [http://localhost:8001/docs](http://localhost:8001/docs)

---

## 🎯 Usage Guide

### Method A: The Dashboard (Recommended)

1. Open [http://localhost:8001/app](http://localhost:8001/app) in your browser.
2. Click **Set up profile** to add your details and upload your resume.
3. Click **Scan for jobs** to trigger the scraper.
4. Click **Re-rank matches** to see jobs scored against your profile.
5. Review jobs, check for LLM-identified red flags, and click to generate tailored cover letters!

### Method B: REST API Direct Usage

If you prefer the terminal, you can drive the entire workflow via cURL:

1. **Trigger a scrape** (pulls live jobs from RemoteOK, filtered by `.env` keywords):
   ```bash
   curl -X POST http://localhost:8001/jobs/scrape
   ```
2. **View scraped jobs:**
   ```bash
   curl http://localhost:8001/jobs
   ```
3. **Create a user profile:**
   ```bash
   curl -X POST http://localhost:8001/users \
     -H "Content-Type: application/json" \
     -d '{"name":"Ali","email":"ali@example.com","skills":"python,fastapi,sql","preferred_role":"Backend Engineer"}'
   ```
4. **Upload a resume** (PDF/DOCX/TXT) to enhance matching and cover letters:
   ```bash
   curl -X POST http://localhost:8001/users/1/resume -F "file=@resume.pdf"
   ```
5. **Generate ranked matches with AI summaries:**
   ```bash
   curl -X POST "http://localhost:8001/users/1/match?top_n=10"
   ```
6. **Draft a tailored cover letter for a match:**
   ```bash
   curl -X POST http://localhost:8001/users/1/matches/1/cover-letter
   ```

---

## 🗺️ Roadmap & Next Steps (Phase 7+)

- [ ] **Advanced Scrapers:** Use `app/scrapers/playwright_template.py` to build scrapers for JS-heavy sites like LinkedIn or Indeed. *(Ensure compliance with site ToS).*
- [ ] **Vector Embeddings:** Swap `app/services/matching.py`'s TF-IDF for true embeddings (e.g., SentenceTransformers, OpenAI) and a vector database (Chroma/Pinecone) to scale matching to thousands of jobs.
- [ ] **Interview Prep Module:** Fully integrate the `generate_interview_prep` function to provide targeted Q&A practice.
- [ ] **Production Deployment:** Switch the database to Postgres (uncomment in `docker-compose.yml`) and deploy via Docker.

---

## 📂 Project Structure

```text
job-scraper-agent/
├── app/
│   ├── main.py              # FastAPI application & startup scheduler
│   ├── config.py            # Environment-based configuration
│   ├── database.py          # SQLAlchemy engine and session management
│   ├── models.py            # Database tables (Job, User, Match)
│   ├── schemas.py           # Pydantic request/response validation models
│   ├── scheduler.py         # Periodic scraping setup (APScheduler)
│   ├── scrapers/            # Web scraping modules
│   │   ├── base.py          
│   │   ├── remoteok.py      
│   │   └── playwright_template.py 
│   ├── services/            # Core business logic
│   │   ├── ingestion.py     # Scraper -> Database pipeline
│   │   ├── matching.py      # Resume/Job scoring logic
│   │   └── llm.py           # Groq API: Summaries, cover letters, interview prep
│   └── routers/             # API Endpoints
│       ├── jobs.py
│       └── users.py
├── static/                  # Vanilla frontend dashboard files
├── requirements.txt         # Project dependencies
├── Dockerfile               # Containerization definition
├── docker-compose.yml       # Multi-container orchestration (Ready for Postgres)
└── .env.example             # Environment variable template
```
# Job-Scrapper-Agents
