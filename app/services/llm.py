"""
Phase 3 starter: LLM-powered job summarization and red-flag detection
using the Groq API.
"""
import json
from loguru import logger

from groq import Groq

from app.config import settings

_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

SUMMARY_PROMPT = """You are helping a job seeker triage postings quickly.
Given the job description below, return ONLY a JSON object (no prose, no
markdown fences) with these keys:
- "summary": a 2-sentence plain-language summary of the role
- "red_flags": a short string listing any concerning signs (vague pay,
  unrealistic requirements, MLM/pyramid language, excessive urgency), or
  empty string if none

Job title: {title}
Company: {company}
Description:
{description}
"""

def summarize_job(title: str, company: str, description: str) -> dict:
    """Returns {"summary": str, "red_flags": str}. Falls back gracefully
    if no API key is configured, so the rest of the app still runs."""
    if _client is None:
        return {"summary": "(LLM summarization disabled — set GROQ_API_KEY)", "red_flags": ""}

    prompt = SUMMARY_PROMPT.format(
        title=title, company=company, description=(description or "")[:4000]
    )

    try:
        response = _client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
    except Exception as e:
        logger.warning(f"LLM summarization failed, degrading gracefully: {e}")
        return {"summary": "(LLM summarization unavailable — check GROQ_API_KEY)", "red_flags": ""}

    raw_text = response.choices[0].message.content.strip()

    try:
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"summary": raw_text, "red_flags": ""}


def draft_cover_letter(user_resume: str, job_title: str, company: str, job_description: str) -> str:
    """Phase 5: generate a tailored cover-letter draft for user review."""
    if _client is None:
        return "(Cover letter generation disabled — set GROQ_API_KEY)"

    prompt = f"""Write a concise, specific 3-paragraph cover letter for this
candidate applying to the role below. Avoid generic filler language; reference
concrete skills from the resume that match the job description.

Candidate resume:
{user_resume[:3000]}

Job title: {job_title}
Company: {company}
Job description:
{job_description[:3000]}
"""
    try:
        response = _client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
    except Exception as e:
        logger.warning(f"Cover letter generation failed, degrading gracefully: {e}")
        return "(Cover letter generation unavailable — check GROQ_API_KEY)"

    return response.choices[0].message.content.strip()


def generate_interview_prep(user_resume: str, job_title: str, company: str, job_description: str) -> str:
    """Future Enhancement: Generate likely interview questions based on the job and resume."""
    if _client is None:
        return "(Interview prep disabled — set GROQ_API_KEY)"

    prompt = f"""You are an expert technical recruiter and interview coach.
Based on the candidate's resume and the job description at {company} for the role of {job_title},
generate 5 highly probable interview questions they will be asked.

For each question, provide a brief tip on how the candidate should answer it based on their resume experience.

Candidate Resume:
{user_resume[:3000]}

Job Description:
{job_description[:3000]}
"""
    try:
        response = _client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an expert interview prep coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
    except Exception as e:
        logger.warning(f"Interview prep generation failed: {e}")
        return "(Interview prep unavailable — check GROQ_API_KEY)"

    return response.choices[0].message.content.strip()
