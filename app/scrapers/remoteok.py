import datetime as dt
import httpx

from app.scrapers.base import BaseScraper, JobPosting

REMOTEOK_API_URL = "https://remoteok.com/api"


class RemoteOKScraper(BaseScraper):
    """
    RemoteOK exposes a public, unauthenticated JSON API — no anti-bot
    measures to fight, which makes it the ideal first source to get the
    full pipeline (scrape -> store -> match -> summarize) working end to end
    before tackling JS-heavy sites like LinkedIn with Playwright.
    """

    source_name = "remoteok"

    async def fetch_jobs(self, keywords: list[str]) -> list[JobPosting]:
        headers = {"User-Agent": "job-scraper-agent (educational project)"}
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(REMOTEOK_API_URL, headers=headers)
            resp.raise_for_status()
            raw = resp.json()

        # First element is API metadata, not a job — skip it.
        postings = raw[1:] if raw and isinstance(raw, list) else []

        keywords_lower = [k.lower() for k in keywords]
        results: list[JobPosting] = []

        for item in postings:
            tags = item.get("tags", []) or []
            text_blob = " ".join([
                str(item.get("position", "")),
                str(item.get("description", "")),
                " ".join(tags),
            ]).lower()

            if keywords_lower and not any(kw in text_blob for kw in keywords_lower):
                continue

            posted_at = None
            if item.get("date"):
                try:
                    posted_at = dt.datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
                except ValueError:
                    posted_at = None

            results.append(JobPosting(
                source=self.source_name,
                external_id=str(item.get("id")),
                title=item.get("position", "Untitled"),
                company=item.get("company", ""),
                location=item.get("location", "Remote"),
                salary=self._format_salary(item),
                description=item.get("description", ""),
                url=item.get("url", ""),
                tags=",".join(tags),
                posted_at=posted_at,
            ))

        return results

    @staticmethod
    def _format_salary(item: dict) -> str:
        lo, hi = item.get("salary_min"), item.get("salary_max")
        if lo and hi:
            return f"${lo:,} - ${hi:,}"
        return ""
