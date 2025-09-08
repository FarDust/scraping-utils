"""File processing tasks for Airflow.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any

from ...core.settings import Settings
from ...domain.entities.website import WebsiteEntity
from ..db.database import DatabaseConnector
from ..db.models.scraped_data import ScrapedData

logger = logging.getLogger(__name__)


def process_file(file_path: str) -> str:
    """Read JSON file from scrape_website and save to database.

    Parameters
    ----------
    file_path : str
        Path to the JSON file to process

    Returns
    -------
    str
        Status message

    """
    logger.info(f"Processing file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    entities = []
    if isinstance(data, list):
        entities = [WebsiteEntity.model_validate(item) for item in data]
    else:
        entities = [WebsiteEntity.model_validate(data)]

    settings = Settings()
    db_connector = DatabaseConnector(settings.db.url)

    with db_connector as db:
        for entity in entities:
            record = ScrapedData()
            record.id = uuid.uuid4()
            record.set_source(entity.url)
            record.extracted_text = (
                entity.content_text or entity.content_markdown or entity.title or ""
            )
            record.insertion_date = datetime.now()

            db.session.add(record)

        db.session.commit()

    logger.info(f"Saved {len(entities)} records from {file_path}")
    return f"Processed {len(entities)} records"


def process_detected_files(**context: Any) -> list[str]:
    """Process detected files task for Airflow.

    Returns
    -------
    list[str]
        List of processed file results

    """
    logger.info("Process detected files task called")

    # Get files from context
    files = context.get("files", [])
    if not files:
        return []

    results: list[str] = []
    for file_path in files:
        try:
            result = process_file(str(file_path))
            results.append(result)
        except Exception as e:
            results.append(f"Failed: {e}")

    return results
