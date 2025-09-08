from abc import ABC, abstractmethod
from typing import Any
from ...domain.entities.website import WebsiteEntity
from ...domain.repositories.website_repository import WebsiteRepository


class BaseScraper(WebsiteRepository, ABC):
    def __init__(self, name: str):
        self.name = name
        self._session: Any = None

    @abstractmethod
    async def get(self) -> list[WebsiteEntity]:
        return []
