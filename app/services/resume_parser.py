"""
Phase 2: resume parsing. Extracts plain text from an uploaded PDF or DOCX
so it can be fed into the matching and cover-letter services.
"""
import io

from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
from docx import Document as DocxDocument


async def extract_resume_text(file: UploadFile) -> str:
    filename = (file.filename or "").lower()
    content = await file.read()

    if filename.endswith(".pdf"):
        return _extract_pdf(content)
    elif filename.endswith(".docx"):
        return _extract_docx(content)
    elif filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(400, "Unsupported file type — upload a .pdf, .docx, or .txt resume")


def _extract_pdf(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def _extract_docx(content: bytes) -> str:
    doc = DocxDocument(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs).strip()
