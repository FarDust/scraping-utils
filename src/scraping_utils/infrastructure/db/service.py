"""Database service factory and utilities.

This module provides factory functions for creating properly configured
database services following dependency injection principles.
"""

from typing import Generator
from sqlalchemy.orm import Session
from ...core.settings import Settings
from .database import DatabaseConnector


class DatabaseService:
    """High-level database service that provides convenient access to database operations.

    This service acts as a facade over the DatabaseConnector, providing
    application-level database operations.
    """

    def __init__(self, connector: DatabaseConnector) -> None:
        """Initialize the database service.

        Parameters
        ----------
        connector : DatabaseConnector
            DatabaseConnector instance

        """
        self._connector = connector

    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session.

        Yields
        ------
        Session
            SQLAlchemy session instance

        """
        yield from self._connector.get_session()

    def initialize_database(self) -> None:
        """Initialize the database by creating all tables."""
        self._connector.create_tables()

    def close(self) -> None:
        """Close database connections."""
        self._connector.close()


def create_database_service(settings: Settings | None = None) -> DatabaseService:
    """Create a properly configured DatabaseService.

    Parameters
    ----------
    settings : Settings or None, default None
        Optional settings instance. If None, creates a new Settings instance.

    Returns
    -------
    DatabaseService
        Configured DatabaseService instance

    """
    if settings is None:
        settings = Settings()

    connector = DatabaseConnector(settings.db)
    return DatabaseService(connector)


def create_database_connector(settings: Settings | None = None) -> DatabaseConnector:
    """Create a properly configured DatabaseConnector.

    Parameters
    ----------
    settings : Settings or None, default None
        Optional settings instance. If None, creates a new Settings instance.

    Returns
    -------
    DatabaseConnector
        Configured DatabaseConnector instance

    """
    if settings is None:
        settings = Settings()

    return DatabaseConnector(settings.db)
