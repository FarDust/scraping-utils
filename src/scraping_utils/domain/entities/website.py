from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class WebsiteEntity(BaseModel):
    """Domain entity representing a website and its scraped content."""

    id: str | None = None
    url: str
    scraped_at: datetime = Field(default_factory=datetime.now)

    # Core content fields
    title: str | None = None
    description: str | None = None
    content_markdown: str | None = None
    content_html: str | None = None
    content_text: str | None = None

    # Links and media
    links: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)

    # Metadata
    language: str | None = None
    status_code: int | None = None
    error_message: str | None = None
    is_successful: bool = False

    # Additional metadata (flexible for different scrapers)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Tracking
    last_modified: datetime | None = None
    content_hash: str | None = None
