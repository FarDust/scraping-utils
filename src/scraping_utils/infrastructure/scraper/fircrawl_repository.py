"""GG.deals repository implementation using Firecrawl SDK."""

import asyncio
import hashlib
import uuid
import backoff
from datetime import datetime
from typing import Any

from firecrawl import FirecrawlApp
from firecrawl.types import ScrapeOptions
from logging import getLogger, Logger


from ...domain.entities.website import WebsiteEntity
from ...domain.repositories.website_repository import WebsiteRepository


class CrawlingError(Exception):
    """Exception raised when crawling fails."""

    pass


class FirecrawlRepository(WebsiteRepository):
    """Repository for crawling GG.deals using Firecrawl SDK."""

    retries: int = 3
    _logger: Logger = getLogger(__name__)

    def __init__(
        self,
        base_url: str,
        target_url: str,
        api_key: str | None = None,
        scrape_options: dict[str, Any] | None = None,
        limit: int = 2,
        interval: int = 60,
        timeout: int = 240,
        
    ):
        """Initialize the GG.deals repository.

        Parameters
        ----------
        base_url : str
            Firecrawl base URL
        target_url : str
            URL to crawl
        api_key : str or None, default None
            Firecrawl API key (overrides settings if provided)
        scrape_options : dict[str, Any] or None, default None
            Additional scraping options

        """
        self.base_url = base_url
        self.api_key = api_key
        self.target_url = target_url

        if self.api_key:
            self.firecrawl = FirecrawlApp(api_key=self.api_key, api_url=self.base_url)
        else:
            self.firecrawl = FirecrawlApp(api_key="dummy", api_url=self.base_url)

        self.scrape_options: ScrapeOptions = ScrapeOptions.model_validate(
            {
                "formats": ["markdown", "html"],
                "only_main_content": True,
                "remove_base64_images": True,
                "block_ads": True,
                "wait_for": 2000,
                "mobile": False,
                "skip_tls_verification": True,
            }
            if scrape_options is None
            else scrape_options
        )

        self.limit = limit
        self.interval = interval
        self.timeout = timeout

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_time=300,
        max_tries=retries,
    )
    async def _handle_crawl(self):
        self._logger.info(f"Starting crawl for: {self.target_url}")
        try:
            crawl_job = self.firecrawl.crawl(
                url=self.target_url,
                limit=self.limit,
                timeout=self.timeout,
                scrape_options=self.scrape_options,
                poll_interval=10,
            )
            self._logger.info(f"Crawl job status: {crawl_job.status}")
            return crawl_job
        except Exception as e:
            self._logger.warning(f"Error occurred while crawling: {e}")
            raise e

    async def crawl(self) -> list[WebsiteEntity]:
        retry_count = 0
        crawl_job = await self._handle_crawl()

        while "scraping" == crawl_job.status:
            crawl_job = await self._handle_crawl()

            if not crawl_job.status == "failed":
                raise CrawlingError(f"Failed to crawl URL {self.target_url}")

            if not crawl_job.data:
                raise CrawlingError(f"No data returned for URL: {self.target_url}")

            await asyncio.sleep(self.interval)

            retry_count += 1
            if retry_count > self.retries:
                raise CrawlingError(f"Max retries exceeded for URL: {self.target_url}")

        entities: list[WebsiteEntity] = []
        for document in crawl_job.data:
            if document.markdown:
                content_hash = hashlib.md5(
                    document.markdown.encode("utf-8")
                ).hexdigest()
            elif document.html:
                content_hash = hashlib.md5(document.html.encode("utf-8")).hexdigest()
            else:
                raise ValueError("No content found in document")

            assert document.metadata is not None
            entities.append(
                WebsiteEntity(
                    id=str(uuid.uuid4()),
                    url=document.metadata.url or "",
                    scraped_at=datetime.now(),
                    title=document.metadata.title,
                    description=document.metadata.description,
                    content_markdown=document.markdown,
                    content_html=document.html,
                    content_text=document.markdown,  # Keep it simple
                    links=document.links or [],
                    language=document.metadata.language,
                    status_code=document.metadata.status_code,
                    is_successful=True,
                    metadata={
                        "source": self.target_url,
                        "firecrawl_metadata": document.metadata.model_dump()
                        if document.metadata
                        else {},
                        "credits_used": crawl_job.credits_used,
                    },
                    content_hash=content_hash,
                )
            )

        return entities

    async def get(self) -> list[WebsiteEntity] | None:
        return await self.crawl()
