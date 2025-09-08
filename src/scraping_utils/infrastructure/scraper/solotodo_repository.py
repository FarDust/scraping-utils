"""SoloTodo repository implementation using Firecrawl SDK."""

from scraping_utils.infrastructure.scraper.fircrawl_repository import (
    FirecrawlRepository,
)


class CrawlingError(Exception):
    """Exception raised when crawling fails."""

    pass


class SoloTodoRepository(FirecrawlRepository):
    pass
