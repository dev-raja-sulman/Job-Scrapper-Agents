"""
Template for scraping JS-heavy job boards (LinkedIn, Indeed, Rozee.pk) that
don't expose a public API. NOT wired into the app by default — uncomment
`playwright` in requirements.txt and run `playwright install chromium` first.

IMPORTANT: Check each site's robots.txt and Terms of Service before scraping.
Many sites explicitly forbid automated scraping — prefer official APIs or
RSS feeds where they exist, and always rate-limit your requests.

Usage sketch:
    scraper = GenericPlaywrightScraper(
        search_url_template="https://example.com/jobs?q={keyword}",
        card_selector=".job-card",
    )
    jobs = await scraper.fetch_jobs(["python", "backend"])
"""
import datetime as dt

from app.scrapers.base import BaseScraper, JobPosting


class GenericPlaywrightScraper(BaseScraper):
    source_name = "generic_playwright"

    def __init__(self, search_url_template: str, card_selector: str):
        self.search_url_template = search_url_template
        self.card_selector = card_selector

    async def fetch_jobs(self, keywords: list[str]) -> list[JobPosting]:
        # Lazy import so the base app runs without playwright installed.
        from playwright.async_api import async_playwright

        results: list[JobPosting] = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()

            for keyword in keywords:
                url = self.search_url_template.format(keyword=keyword)
                await page.goto(url, wait_until="networkidle")

                cards = await page.query_selector_all(self.card_selector)
                for card in cards:
                    # NOTE: selectors below are placeholders — inspect the
                    # target site's DOM and adjust per source.
                    title_el = await card.query_selector(".job-title")
                    company_el = await card.query_selector(".job-company")
                    link_el = await card.query_selector("a")

                    title = (await title_el.inner_text()) if title_el else "Untitled"
                    company = (await company_el.inner_text()) if company_el else ""
                    href = (await link_el.get_attribute("href")) if link_el else ""

                    results.append(JobPosting(
                        source=self.source_name,
                        external_id=href or title,
                        title=title.strip(),
                        company=company.strip(),
                        location="",
                        salary="",
                        description="",
                        url=href or "",
                        tags="",
                        posted_at=dt.datetime.utcnow(),
                    ))

            await browser.close()

        return results
