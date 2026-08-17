from abc import ABC, abstractmethod


class JobPosting(dict):
    """
    Normalized job posting shape every scraper must return.
    Using dict subclass keeps this lightweight; swap for a dataclass if preferred.

    Required keys: source, external_id, title, company, location,
                    salary, description, url, tags, posted_at
    """
    pass


class BaseScraper(ABC):
    """
    Every job source (RemoteOK, LinkedIn, Indeed, Rozee.pk, ...) implements
    this interface. The agent orchestrator only ever talks to `fetch_jobs`,
    so adding a new source never touches the rest of the pipeline.
    """

    source_name: str = "base"

    @abstractmethod
    async def fetch_jobs(self, keywords: list[str]) -> list[JobPosting]:
        """Fetch and normalize postings for the given keywords."""
        raise NotImplementedError
