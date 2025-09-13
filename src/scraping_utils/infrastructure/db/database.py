"""Database connector."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base


class DatabaseConnector:
    """Exposes database connection and session management."""

    def __init__(self, database_url: str):
        self._database_url = database_url
        self._engine = None
        self._session_factory = None
        self._active_session = None

    @property
    def engine(self):
        """Get the database engine."""
        if self._engine is None:
            self._engine = create_engine(self._database_url)
        return self._engine

    @property
    def session_factory(self):
        """Get the session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(bind=self.engine)
        return self._session_factory

    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)

    def new_session(self):
        """Create a new database session."""
        return self.session_factory()

    @property
    def session(self):
        """Get the active session (only available in context manager)."""
        if self._active_session is not None:
            return self._active_session
        raise RuntimeError("No active session. Use within 'with' statement.")

    def __enter__(self):
        self._active_session = self.new_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._active_session is not None:
            self._active_session.close()
            self._active_session = None
        if self._engine:
            self._engine.dispose()
