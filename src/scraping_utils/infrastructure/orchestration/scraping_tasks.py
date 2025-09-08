"""Web scraping tasks for Airflow.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Type, Any
from urllib.parse import urlparse

from scraping_utils.infrastructure.scraper.fircrawl_repository import (
    FirecrawlRepository,
)

from ..scraper.solotodo_repository import SoloTodoRepository
from ..scraper.gg_deals_repository import GGDealsRepository
from ...core.settings import Settings
from ...domain.entities.website import WebsiteEntity

logger = logging.getLogger(__name__)


def scrape_website(url: str, output_dir: str = "./data") -> str:
    """Crawl website and save as JSON file.

    Parameters
    ----------
    url : str
        Website URL to crawl
    output_dir : str, default "./data"
        Directory to save results

    Returns
    -------
    str
        Path to the saved JSON file

    """
    logger.info(f"Crawl task called for: {url}")

    # Parse domain to determine repository
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()

    # Load settings
    settings = Settings()

    # Repository mapping for known domains
    repository_map: dict[str, Type[FirecrawlRepository]] = {
        "solotodo.cl": SoloTodoRepository,
        "www.solotodo.cl": SoloTodoRepository,
        "gg.deals": GGDealsRepository,
        "www.gg.deals": GGDealsRepository,
    }

    # Select repository
    if domain in repository_map:
        repository_class = repository_map[domain]
        logger.info(f"Using {repository_class.__name__} for {domain}")
    else:
        repository_class = FirecrawlRepository
        logger.info(f"Using FirecrawlRepository for {domain}")

    # Create repository and crawl
    repository = repository_class(
        base_url=settings.firecrawl.base_url,
        target_url=url,
        api_key=settings.firecrawl.api_key,
    )

    website_entities: list[WebsiteEntity] | None = asyncio.run(repository.get())
    assert website_entities is not None
    if not website_entities:
        website_entities = []
    logger.info(f"Crawl completed. Found {len(website_entities)} pages")

    # Create output directory and file path
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain_safe = domain.replace(".", "_")
    output_file = Path(output_dir) / f"crawl_{domain_safe}_{timestamp}.json"

    # Convert entities to dict for JSON serialization
    crawl_data: list[dict[str, Any]] = [
        entity.model_dump(
            mode="json"
        )  # Use mode='json' to serialize datetime as strings
        for entity in website_entities
    ]

    # Save to JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(crawl_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to: {output_file}")
    return str(output_file)
