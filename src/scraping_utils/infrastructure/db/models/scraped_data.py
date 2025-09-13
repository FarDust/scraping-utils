"""SQLAlchemy models for web scraping data."""

import uuid
from sqlalchemy import Column, String, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator, CHAR


class GUID(TypeDecorator):
    """Cross-database UUID type for SQLAlchemy 1.4.

    Uses PostgreSQL UUID when available, otherwise CHAR(36) for SQLite.
    This approach is compatible with SQLAlchemy 1.4 constraints from Airflow.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgreSQLUUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            return uuid.UUID(value)


Base = declarative_base()


class ScrapedData(Base):
    """Model for storing scraped web data.

    Requirements:
    - ID (UUID)
    - Source (URL)
    - Extracted text (free length text)
    - Insertion date
    """

    __tablename__ = "scraped_data"

    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the scraped data record",
    )

    source = Column(
        String(2048), nullable=False, comment="Source URL of the scraped content"
    )

    source_reverse = Column(
        String(2048),
        nullable=True,
        comment="Reversed source URL for better search performance on domain queries",
    )

    extracted_text = Column(
        Text, nullable=True, comment="Extracted text content from the web page"
    )

    insertion_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Date and time when the record was inserted",
    )

    # Indexes for better performance
    __table_args__ = (
        Index("idx_scraped_data_source", "source"),
        Index("idx_scraped_data_source_reverse", "source_reverse"),
        Index("idx_scraped_data_insertion_date", "insertion_date"),
    )

    def set_source(self, url: str) -> None:
        """Set the source URL and automatically populate the reverse source.

        The source_reverse field contains the domain in reverse order for efficient
        domain-based queries. For example:
        - https://www.example.com -> com.example.www
        - https://sub.domain.com/path -> com.domain.sub

        Parameters
        ----------
        url : str
            The source URL to set

        """
        from urllib.parse import urlparse

        self.source = url

        # Parse URL to extract domain
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Remove port if present (e.g., example.com:8080 -> example.com)
        if ":" in domain:
            domain = domain.split(":")[0]

        # Split domain parts and reverse them
        domain_parts = domain.split(".")
        reversed_domain = ".".join(reversed(domain_parts))

        self.source_reverse = reversed_domain

    def __repr__(self) -> str:
        return f"<ScrapedData(id={self.id}, source='{self.source[:50]}...', insertion_date={self.insertion_date})>"
