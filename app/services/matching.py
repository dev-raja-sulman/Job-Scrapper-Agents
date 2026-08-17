"""
Phase 2: resume/job matching using Vector Embeddings + ChromaDB.

This replaces the old TF-IDF implementation with real semantic embeddings 
(SentenceTransformers) and a local Vector Database (ChromaDB), providing
production-grade semantic search capabilities.
"""
import chromadb
from chromadb.utils import embedding_functions

from app.models import Job, User


# Initialize ChromaDB client and collection
chroma_client = chromadb.PersistentClient(path="./chroma_db")
# Using the default sentence-transformers model (all-MiniLM-L6-v2)
emb_fn = embedding_functions.DefaultEmbeddingFunction()

collection = chroma_client.get_or_create_collection(
    name="jobs",
    embedding_function=emb_fn,
    metadata={"hnsw:space": "cosine"} # Use cosine similarity
)


def _job_text(job: Job) -> str:
    return " ".join(filter(None, [job.title, job.tags, job.description]))


def _user_text(user: User) -> str:
    skills = (user.skills or "").replace(",", " ")
    return " ".join(filter(None, [skills, skills, user.preferred_role, user.resume_text]))


def upsert_jobs(jobs: list[Job]):
    """Ensure jobs are in the vector database."""
    if not jobs:
        return
    
    # Only insert jobs that aren't already in the collection to save time
    existing = collection.get(ids=[str(j.id) for j in jobs])
    existing_ids = set(existing.get("ids", []))
    
    new_jobs = [j for j in jobs if str(j.id) not in existing_ids]
    if not new_jobs:
        return

    ids = [str(j.id) for j in new_jobs]
    documents = [_job_text(j) for j in new_jobs]
    metadatas = [{"title": j.title, "company": j.company or ""} for j in new_jobs]
    
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)


def rank_jobs(user: User, jobs: list[Job], top_n: int = 20) -> list[tuple[Job, float]]:
    """Score every job against the user's profile using vector search."""
    if not jobs:
        return []

    user_text = _user_text(user).strip()
    if not user_text:
        return [(job, 0.0) for job in jobs[:top_n]]

    # Ensure all jobs are embedded in the vector DB
    upsert_jobs(jobs)

    # Query the vector DB
    results = collection.query(
        query_texts=[user_text],
        n_results=min(top_n, len(jobs))
    )

    if not results["ids"] or not results["ids"][0]:
        return []

    top_ids = results["ids"][0]
    distances = results["distances"][0]
    
    job_map = {str(j.id): j for j in jobs}
    scored = []
    
    for jid, dist in zip(top_ids, distances):
        if jid in job_map:
            # ChromaDB with cosine space returns distance = 1 - similarity
            similarity = 1.0 - dist
            scored.append((job_map[jid], round(float(similarity), 3)))
            
    return scored


def score_job(user: User, job: Job) -> float:
    """Single-job convenience wrapper around rank_jobs."""
    ranked = rank_jobs(user, [job], top_n=1)
    return ranked[0][1] if ranked else 0.0
