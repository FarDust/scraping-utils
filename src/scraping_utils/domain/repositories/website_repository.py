from abc import ABC, abstractmethod
from ..entities.website import WebsiteEntity


class WebsiteRepository(ABC):
    """Abstract repository for website entities."""

    @abstractmethod
    async def get(self) -> list[WebsiteEntity] | None:
        pass


class CrawlingError(Exception):
    """Exception raised when crawling fails."""

    def __init__(
        self, message: str, url: str | None = None, status_code: int | None = None
    ):
        self.url = url
        self.status_code = status_code
        super().__init__(message)
