# Job Scrapper Agent - System Architecture & Workflow

## 🏗️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INTERACTIVE DASHBOARD                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  HTML/CSS/JS UI (Vanilla JavaScript)                         │   │
│  │  - Profile Setup Form                                        │   │
│  │  - Resume Upload Widget                                      │   │
│  │  - Job Listing & Filtering                                   │   │
│  │  - Match Score Visualization                                 │   │
│  │  - Cover Letter Generation Modal                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                          ⬇️ HTTP/JSON ⬇️                            │
└─────────────────────────────────────────────────────────────────────┘
                              
┌─────────────────────────────────────────────────────────────────────┐
│                    FASTAPI APPLICATION SERVER                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  MIDDLEWARE LAYER                                            │   │
│  │  ├─ CORS (Cross-Origin Resource Sharing)                    │   │
│  │  ├─ Request Logging (loguru)                                │   │
│  │  └─ Error Handling                                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────┐    ┌──────────────────────┐              │
│  │  JOBS ROUTER         │    │  USERS ROUTER        │              │
│  │  ├─ GET /jobs        │    │  ├─ POST /users      │              │
│  │  ├─ POST /jobs/scrape│    │  ├─ POST /resume     │              │
│  │  └─ [Endpoints]      │    │  └─ POST /match      │              │
│  └──────────────────────┘    └──────────────────────┘              │
│           ⬇️                           ⬇️                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  BUSINESS LOGIC SERVICES                                     │   │
│  │  ├─ ingestion.py    : Scraper → Database Pipeline           │   │
│  │  ├─ matching.py     : Resume/Job Semantic Matching           │   │
│  │  ├─ llm.py          : Groq API Integration                   │   │
│  │  └─ resume_parser.py: PDF/DOCX/TXT Extraction               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│           ⬇️           ⬇️            ⬇️            ⬇️               │
└─────────────────────────────────────────────────────────────────────┘

         ⬇️              ⬇️             ⬇️             ⬇️

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  WEB SCRAPERS    │  │  DATABASE LAYER  │  │  AI/ML SERVICES  │
│  ┌──────────────┐│  │  ┌──────────────┐│  │  ┌──────────────┐│
│  │ RemoteOK API ││  │  │ SQLAlchemy   ││  │  │ ChromaDB     ││
│  │              ││  │  │ SQLite (Dev) ││  │  │ + Embeddings ││
│  │ HTTPx Client ││  │  │ Postgres (Prod)│  │  │              ││
│  │              ││  │  │              ││  │  │ SentenceXfmrs││
│  └──────────────┘│  │  └──────────────┘│  │  └──────────────┘│
│  ┌──────────────┐│  │  ┌──────────────┐│  │  ┌──────────────┐│
│  │ Playwright   ││  │  │ Tables:      ││  │  │ Groq API     ││
│  │ (Optional)   ││  │  │ • jobs       ││  │  │ (Mixtral)    ││
│  │              ││  │  │ • users      ││  │  │              ││
│  │ JS-heavy     ││  │  │ • matches    ││  │  │ LLM Services ││
│  │ site support ││  │  │              ││  │  │              ││
│  └──────────────┘│  │  └──────────────┘│  │  └──────────────┘│
└──────────────────┘  └──────────────────┘  └──────────────────┘

         ⬇️                    ⬇️                    ⬇️

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  BACKGROUND      │  │  LOCAL STORAGE   │  │  EXTERNAL APIs   │
│  SCHEDULER       │  │                  │  │                  │
│                  │  │  ├─ chroma_db/   │  │  ├─ RemoteOK     │
│  APScheduler     │  │  │  (Vector DB)  │  │  │  (Job Feed)    │
│  ┌──────────────┐│  │  │               │  │  │                │
│  │ Periodic     ││  │  ├─ database.db  │  │  ├─ Groq API      │
│  │ Scrape Job   ││  │  │  (SQLite)      │  │  │  (LLM)         │
│  │              ││  │  │               │  │  │                │
│  │ Every 6 hrs  ││  │  └─ logs/        │  │  └─ Playwright    │
│  │              ││  │     (loguru)     │  │     (JS scraping) │
│  │ Runs async   ││  │                  │  │                  │
│  └──────────────┘│  │                  │  │                  │
│                  │  │                  │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1️⃣  SCRAPING PIPELINE                                              │
└─────────────────────────────────────────────────────────────────────┘

    [Dashboard: "Scan for jobs"]
                ⬇️
    [API: POST /jobs/scrape]
                ⬇️
    ┌─────────────────────────────────────┐
    │ app/services/ingestion.py           │
    │ run_ingestion() function            │
    └─────────────────────────────────────┘
                ⬇️
    ┌─────────────────────────────────────┐
    │ app/scrapers/remoteok.py            │
    │ fetch_remoteok_jobs() function      │
    └─────────────────────────────────────┘
                ⬇️
    [RemoteOK Public API] → Fetch 50 jobs
                ⬇️
    ┌─────────────────────────────────────┐
    │ Deduplication Logic                 │
    │ Check: source + external_id         │
    │ Result: 42 new jobs (8 duplicates)  │
    └─────────────────────────────────────┘
                ⬇️
    ┌─────────────────────────────────────┐
    │ SQLAlchemy ORM                      │
    │ Insert into Job table               │
    └─────────────────────────────────────┘
                ⬇️
    [SQLite Database]
        └─ 42 new Job records created
                ⬇️
    ✅ Response: {"new_jobs_inserted": 42}


┌─────────────────────────────────────────────────────────────────────┐
│ 2️⃣  RESUME UPLOAD & PARSING PIPELINE                               │
└─────────────────────────────────────────────────────────────────────┘

    [Dashboard: "Upload Resume"]
                ⬇️
    [File Upload: resume.pdf]
                ⬇️
    [API: POST /users/{id}/resume]
                ⬇️
    ┌─────────────────────────────────────┐
    │ app/services/resume_parser.py       │
    │ parse_resume() function             │
    └─────────────────────────────────────┘
                ⬇️
    ┌─────────────────────────────────────┐
    │ File Type Detection                 │
    │ ├─ .pdf → PyPDF                     │
    │ ├─ .docx → python-docx              │
    │ └─ .txt → read directly             │
    └─────────────────────────────────────┘
                ⬇️
    [Extracted Text: 3,847 characters]
                ⬇️
    ┌─────────────────────────────────────┐
    │ Update User Profile                 │
    │ users.resume_text = extracted_text  │
    └─────────────────────────────────────┘
                ⬇️
    [SQLite Database]
        └─ User record updated
                ⬇️
    ✅ Response: {"extraction_success": true}


┌─────────────────────────────────────────────────────────────────────┐
│ 3️⃣  JOB MATCHING & RANKING PIPELINE                                │
└─────────────────────────────────────────────────────────────────────┘

    [Dashboard: "Re-rank matches"]
                ⬇️
    [API: POST /users/{id}/match?top_n=10]
                ⬇️
    ┌─────────────────────────────────────┐
    │ app/services/matching.py            │
    │ rank_jobs() function                │
    └─────────────────────────────────────┘
                ⬇️
    ┌──────────────────────────────────────┐
    │ Step 1: Text Preparation             │
    │ ├─ User:  skills + resume + role     │
    │ └─ Jobs:  title + tags + description │
    └──────────────────────────────────────┘
                ⬇️
    ┌──────────────────────────────────────┐
    │ Step 2: Vector Embedding             │
    │ SentenceTransformers (all-MiniLM)    │
    │ ├─ Embed user text → 384-dim vector  │
    │ └─ Embed job texts → 384-dim vectors │
    └──────────────────────────────────────┘
                ⬇️
    ┌──────────────────────────────────────┐
    │ Step 3: Store in ChromaDB            │
    │ Vector database for semantic search  │
    │ Upsert jobs (skip if already exist)  │
    └──────────────────────────────────────┘
                ⬇️
    ┌──────────────────────────────────────┐
    │ Step 4: Semantic Search              │
    │ Query: user_text                     │
    │ Top_N: 10 results                    │
    │ Metric: Cosine similarity            │
    └──────────────────────────────────────┘
                ⬇️
    [Top 10 Job-User Similarity Scores]
    ├─ Job#1: 0.94 ⭐⭐⭐
    ├─ Job#5: 0.91 ⭐⭐⭐
    └─ Job#2: 0.87 ⭐⭐
                ⬇️
    ✅ Matched jobs ranked by relevance


┌─────────────────────────────────────────────────────────────────────┐
│ 4️⃣  LLM SUMMARIZATION & RED-FLAG DETECTION                         │
└─────────────────────────────────────────────────────────────────────┘

    [For each of top 10 jobs]:
                ⬇️
    ┌──────────────────────────────────────┐
    │ app/services/llm.py                  │
    │ summarize_job() function             │
    └──────────────────────────────────────┘
                ⬇️
    ┌──────────────────────────────────────┐
    │ Construct Prompt                     │
    │ Job Title, Company, Description      │
    │ Request: 2-sentence summary          │
    │ Request: red flag detection          │
    └──────────────────────────────────────┘
                ⬇️
    [Groq API - Mixtral 8x7B LLM]
    ├─ Cost: free tier available
    ├─ Model: Mixtral 8x7B (MoE)
    └─ Response time: ~2-5 seconds
                ⬇️
    ┌──────────────────────────────────────┐
    │ JSON Response Parsing                │
    │ ├─ "summary": 2-sentence description │
    │ └─ "red_flags": concerns if any      │
    └──────────────────────────────────────┘
                ⬇️
    ┌──────────────────────────────────────┐
    │ Store in Match Table                 │
    │ matches.summary = result.summary     │
    │ matches.red_flags = result.red_flags │
    └──────────────────────────────────────┘
                ⬇️
    ✅ Job now has AI-generated insights


┌─────────────────────────────────────────────────────────────────────┐
│ 5️⃣  COVER LETTER GENERATION PIPELINE                               │
└─────────────────────────────────────────────────────────────────────┘

    [Dashboard: "Generate Cover Letter" button]
                ⬇️
    [API: POST /users/{id}/matches/{match_id}/cover-letter]
                ⬇️
    ┌──────────────────────────────────────┐
    │ app/services/llm.py                  │
    │ draft_cover_letter() function        │
    └──────────────────────────────────────┘
                ⬇️
    ┌──────────────────────────────────────┐
    │ Fetch Context:                       │
    │ ├─ User Resume (text)                │
    │ ├─ Job Description                   │
    │ ├─ Job Title                         │
    │ └─ Company Name                      │
    └──────────────────────────────────────┘
                ⬇️
    ┌──────────────────────────────────────┐
    │ Construct Detailed Prompt:           │
    │ "Write a cover letter for..."        │
    │ Include user's skills & experience   │
    │ Tailor to specific job description   │
    │ Professional tone, 3-4 paragraphs    │
    └──────────────────────────────────────┘
                ⬇️
    [Groq API - Mixtral 8x7B LLM]
    ├─ Temperature: 0.7 (creative)
    └─ Response time: ~3-8 seconds
                ⬇️
    ┌──────────────────────────────────────┐
    │ Generated Cover Letter (500-800 words)│
    │                                       │
    │ "Dear Hiring Manager,                │
    │                                       │
    │ I am writing to express my strong    │
    │ interest in the Senior Backend       │
    │ Engineer position at TechCorp Inc.   │
    │ ... [tailored content] ...            │
    │                                       │
    │ Best regards,                        │
    │ Alex Johnson"                        │
    └──────────────────────────────────────┘
                ⬇️
    ✅ User receives draft ready for review
```

---

## 🔄 Background Scheduler Flow

```
┌──────────────────────────────────────────────────────────────┐
│ APScheduler (Initialization)                                │
│ In: app/main.py → lifespan()                                │
└──────────────────────────────────────────────────────────────┘
        ⬇️
┌──────────────────────────────────────────────────────────────┐
│ app/scheduler.py → start_scheduler()                        │
│ ├─ Create BlockingScheduler instance                        │
│ └─ Register periodic job                                    │
└──────────────────────────────────────────────────────────────┘
        ⬇️
┌──────────────────────────────────────────────────────────────┐
│ Scheduled Job: RemoteOK Scrape                              │
│ ├─ Trigger: Interval (6 hours)                              │
│ ├─ Function: run_ingestion()                                │
│ └─ Next run: Auto-calculated                                │
└──────────────────────────────────────────────────────────────┘
        ⬇️
        [Waits 6 hours...]
        ⬇️
┌──────────────────────────────────────────────────────────────┐
│ 6:30 AM - Scheduled Job Triggered                          │
│ ├─ Fetch from RemoteOK API                                  │
│ ├─ Insert new jobs                                          │
│ ├─ Log completion                                           │
│ └─ Schedule next run for 12:30 PM                           │
└──────────────────────────────────────────────────────────────┘
        ⬇️
        [All while API continues serving requests]
        ⬇️
✅ Autonomous job collection 24/7


```

---

## 🗂️ File Structure & Responsibilities

```
job-scraper-agent/
│
├── app/                              # Main application package
│   ├── __init__.py                   # Package marker
│   ├── main.py                       # FastAPI app setup, lifespan
│   ├── config.py                     # Settings from .env
│   ├── database.py                   # SQLAlchemy engine, session
│   ├── models.py                     # Database models (Job, User, Match)
│   ├── schemas.py                    # Pydantic request/response schemas
│   ├── scheduler.py                  # APScheduler configuration
│   │
│   ├── routers/                      # API route handlers
│   │   ├── __init__.py
│   │   ├── jobs.py                   # GET /jobs, POST /jobs/scrape
│   │   └── users.py                  # User CRUD, resume upload, matching
│   │
│   ├── scrapers/                     # Web scraping modules
│   │   ├── __init__.py
│   │   ├── base.py                   # Abstract base scraper class
│   │   ├── remoteok.py               # RemoteOK API scraper
│   │   └── playwright_template.py    # Template for JS-heavy sites
│   │
│   └── services/                     # Business logic
│       ├── __init__.py
│       ├── ingestion.py              # Scraper → Database pipeline
│       ├── matching.py               # Resume/job semantic matching
│       ├── llm.py                    # Groq API integration
│       └── resume_parser.py          # PDF/DOCX/TXT parsing
│
├── static/                           # Frontend (Phase 6 dashboard)
│   └── index.html                    # Interactive job dashboard
│
├── Dockerfile                        # Docker container setup
├── docker-compose.yml                # Docker Compose (app + postgres)
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
└── README.md                         # Project documentation
```

---

## 🔐 Data Model Relationships

```
User (1) ───────────── (Many) Match (Many) ─────────── (1) Job
  ├─ id                    ├─ id                       ├─ id
  ├─ name                  ├─ user_id (FK)             ├─ source
  ├─ email (UNIQUE)        ├─ job_id (FK)              ├─ external_id
  ├─ resume_text           ├─ score [0-1]             ├─ title
  ├─ skills                ├─ summary (LLM)           ├─ company
  ├─ preferred_role        ├─ red_flags               ├─ location
  ├─ salary_min            ├─ status                  ├─ salary
  └─ created_at            └─ created_at              └─ description
                                                      ├─ url
                       UNIQUE Constraint:             ├─ tags
                       (user_id, job_id)              └─ scraped_at
```

---

## ⚙️ Key Algorithms

### **1. Semantic Similarity Matching**
```
User Profile Text:
  "I have 8 years experience with Python, FastAPI, PostgreSQL, Docker, 
   Kubernetes. Looking for Senior Backend Engineer role. AWS expertise."

Job Description:
  "Senior Backend Engineer role. Build microservices with Python/FastAPI.
   PostgreSQL and Kubernetes required. AWS and Docker experience preferred."

Process:
  1. Convert both texts to 384-dimensional vectors (SentenceTransformers)
  2. Calculate cosine similarity: cos(user_vec, job_vec)
  3. Score = (similarity + 1) / 2  → Normalized to [0, 1]
  
Result: 0.94 (94% match - very high relevance!)
```

### **2. Red Flag Detection Heuristics**
```
LLM checks for:
  ├─ "Salary not mentioned" → RED FLAG
  ├─ "Work 24/7 on-call" → RED FLAG
  ├─ "Join our growing team" + no salary → POSSIBLE RED FLAG
  ├─ "MLM", "pyramid", "get rich quick" → RED FLAG
  ├─ Requirements exceed typical experience → YELLOW FLAG
  └─ Unrealistic qualifications for role → YELLOW FLAG

Example:
  Job requires: "20 years of Kubernetes experience"
  Reality: Kubernetes only exists ~10 years
  RED FLAG: "Unrealistic requirements"
```

### **3. Cover Letter Personalization**
```
Template Prompt (simplified):
  "Given user_resume and job_description, write a professional cover letter.
   - Highlight relevant skills from resume
   - Address specific requirements from job posting
   - Show enthusiasm for the company
   - Keep to 3-4 paragraphs, professional tone"

LLM (Mixtral 8x7B):
  Reads both documents
  → Extracts key skills, achievements
  → Matches with job requirements
  → Generates tailored draft
  → Maintains professional language

Output: Ready-to-send cover letter draft!
```

---

## 🚀 Scaling Considerations

### **Current (Phase 0-6)**
- ✅ Single-machine deployment
- ✅ SQLite for development
- ✅ ChromaDB local vector storage
- ✅ Suitable for: 1-100 users, 10k+ jobs

### **Production Ready (Phase 7+)**
- Switch to PostgreSQL (better concurrency)
- Deploy to Docker/Kubernetes
- Use Pinecone/Weaviate for vector DB at scale
- Implement Redis caching
- Add API rate limiting
- Scale to: 1000+ users, millions of jobs

```
┌─────────────────────────────────────────────────────────────┐
│ Current Single-Machine Architecture                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Uvicorn (4 workers)                                  │  │
│  │ ├─ FastAPI Application                              │  │
│  │ └─ Async request handling                            │  │
│  └───────────┬──────────────────────────────┬───────────┘  │
│              │                              │               │
│       ┌──────▼────────┐           ┌────────▼─────────┐    │
│       │   SQLite DB   │           │    ChromaDB      │    │
│       │  (Local file) │           │  (Local vector)  │    │
│       └───────────────┘           └──────────────────┘    │
│              │                              │               │
│              └──────────────┬───────────────┘               │
│                             │                               │
│                    APScheduler (Background)                │
│                             │                               │
│         [Development/Small deployment]                     │
└─────────────────────────────────────────────────────────────┘
                            ⬇️
┌─────────────────────────────────────────────────────────────┐
│ Production Kubernetes Architecture (Future)                │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Ingress   │  │  Ingress   │  │  Ingress   │           │
│  │  Pod       │  │  Pod       │  │  Pod       │           │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘           │
│        └─────────┬──────────┬──────────┘                    │
│                  │          │                              │
│  ┌──────────────▼──────────▼──────────────┐               │
│  │ Service LoadBalancer (K8s Service)      │               │
│  └──────────────┬──────────────────────────┘               │
│                 │                                          │
│    ┌────────────┼────────────┐                             │
│    │            │            │                             │
│ ┌──▼──┐      ┌──▼──┐      ┌──▼──┐                          │
│ │Pod 1│      │Pod 2│      │Pod N│  (FastAPI Replicas)    │
│ │App  │      │App  │      │App  │                        │
│ └──┬──┘      └──┬──┘      └──┬──┘                          │
│    │            │            │                             │
│    └────────────┼────────────┘                             │
│                 │                                          │
│    ┌────────────┼────────────┬─────────────┐              │
│    │            │            │             │               │
│ ┌──▼──────┐ ┌──▼────────┐ ┌──▼──────────┐ │              │
│ │PostgreSQL│ │  Pinecone │ │ Redis Cache │ │  External    │
│ │ Service  │ │  (Vector) │ │   Service   │ │  Services    │
│ └──────────┘ └───────────┘ └─────────────┘ │              │
│                                             │               │
│    ┌─────────────────────────────────────┘│              │
│    │                                      │                │
│    │                                  ┌───▼──┐              │
│    │                                  │Groq  │              │
│    │                                  │API   │              │
│    │                                  └──────┘              │
│    │                                                        │
│    └──────────────► Cloud Storage (Logs, Backups)          │
│                                                              │
│         [Production Deployment]                            │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Completion Status

| Phase | Feature | Status | Implementation |
|-------|---------|--------|-----------------|
| 0 | Foundation | ✅ | Project structure, database setup |
| 1 | Autonomous Scraper | ✅ | RemoteOK API, HTTPx client |
| 2 | Intelligent Matching | ✅ | ChromaDB, SentenceTransformers |
| 3 | AI Insights | ✅ | Groq API integration, LLM service |
| 4 | Scheduled Operations | ✅ | APScheduler background jobs |
| 5 | Cover Letters | ✅ | LLM-powered draft generation |
| 6 | Interactive Dashboard | ✅ | Vanilla HTML/JS UI |
| 7 | Auto-Apply | ⏳ | Intentionally excluded (ToS concerns) |

---

This complete architecture supports a production-grade job discovery system with intelligent matching, AI-powered insights, and seamless automation! 🚀
