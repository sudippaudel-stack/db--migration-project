"""
Database connection manager service.
Handles SQLAlchemy engine and session management for legacy and new databases.
"""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from config.settings import settings
from models.legacy.base import LegacyBase
from models.new.base import NewBase
from utils.logger import logger


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self):
        """Initialize database manager."""
        self._legacy_engine: Engine | None = None
        self._new_engine: Engine | None = None
        self._legacy_session_factory: sessionmaker | None = None
        self._new_session_factory: sessionmaker | None = None

    def _create_engine(self, db_url: str, pool_size: int = 10) -> Engine:
        """
        Create SQLAlchemy engine with connection pooling.

        Args:
            db_url: Database URL
            pool_size: Connection pool size

        Returns:
            SQLAlchemy Engine instance
        """
        engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,   # Recycle connections after 1 hour
            echo=False,          # Set to True for SQL query logging
        )

        # Add event listener for connection
        @event.listens_for(engine, "connect")
        def _receive_connect(dbapi_conn, _connection_record):
            """Set connection parameters on connect."""
            # Set timezone to UTC
            with dbapi_conn.cursor() as cursor:
                cursor.execute("SET time_zone = '+00:00'")
                cursor.execute("SET sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE'")

        return engine

    @property
    def legacy_engine(self) -> Engine:
        """Get or create legacy database engine."""
        if self._legacy_engine is None:
            logger.debug("Creating legacy database engine")
            self._legacy_engine = self._create_engine(settings.legacy_db_url)
        return self._legacy_engine

    @property
    def new_engine(self) -> Engine:
        """Get or create new database engine."""
        if self._new_engine is None:
            logger.debug("Creating new database engine")
            self._new_engine = self._create_engine(settings.new_db_url)
        return self._new_engine

    @property
    def legacy_session_factory(self) -> sessionmaker:
        """Get or create legacy session factory."""
        if self._legacy_session_factory is None:
            self._legacy_session_factory = sessionmaker(
                bind=self.legacy_engine,
                expire_on_commit=False,
            )
        return self._legacy_session_factory

    @property
    def new_session_factory(self) -> sessionmaker:
        """Get or create new session factory."""
        if self._new_session_factory is None:
            self._new_session_factory = sessionmaker(
                bind=self.new_engine,
                expire_on_commit=False,
            )
        return self._new_session_factory

    @contextmanager
    def legacy_session(self) -> Generator[Session, None, None]:
        """
        Context manager for legacy database session.

        Yields:
            SQLAlchemy Session for legacy database

        Example:
            with db_manager.legacy_session() as session:
                results = session.query(LegacyBeneficiary).all()
        """
        session = self.legacy_session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Legacy database session error: {e}")
            raise
        finally:
            session.close()

    @contextmanager
    def new_session(self) -> Generator[Session, None, None]:
        """
        Context manager for new database session.

        Yields:
            SQLAlchemy Session for new database

        Example:
            with db_manager.new_session() as session:
                results = session.query(NewBeneficiary).all()
        """
        session = self.new_session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"New database session error: {e}")
            raise
        finally:
            session.close()

    def test_connection(self, database: str = "both") -> bool:
        """
        Test database connection.

        Args:
            database: Which database to test ("legacy", "new", or "both")

        Returns:
            True if connection successful, False otherwise
        """
        success = True

        if database in ("legacy", "both"):
            try:
                with self.legacy_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.success(f"✓ Connected to legacy database: {settings.legacy_db}")
            except Exception as e:
                logger.error(f"✗ Failed to connect to legacy database: {e}")
                success = False

        if database in ("new", "both"):
            try:
                with self.new_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.success(f"✓ Connected to new database: {settings.new_db}")
            except Exception as e:
                logger.error(f"✗ Failed to connect to new database: {e}")
                success = False

        return success

    def create_tables(self, database: str = "both") -> None:
        """
        Create tables in database.

        Args:
            database: Which database to create tables in ("legacy", "new", or "both")
        """
        if database in ("legacy", "both"):
            logger.info("Creating legacy database tables...")
            LegacyBase.metadata.create_all(self.legacy_engine)
            logger.success("Legacy tables created")

        if database in ("new", "both"):
            logger.info("Creating new database tables...")
            NewBase.metadata.create_all(self.new_engine)
            logger.success("New tables created")

    def drop_tables(self, database: str, confirm: bool = False) -> None:
        """
        Drop all tables in database.

        Args:
            database: Which database to drop tables from ("legacy" or "new")
            confirm: Confirmation flag (required to prevent accidental drops)
        """
        if not confirm:
            logger.warning("Drop tables requires confirmation flag")
            return

        if database == "legacy":
            logger.warning("Dropping legacy database tables...")
            LegacyBase.metadata.drop_all(self.legacy_engine)
            logger.info("Legacy tables dropped")
        elif database == "new":
            logger.warning("Dropping new database tables...")
            NewBase.metadata.drop_all(self.new_engine)
            logger.info("New tables dropped")

    def get_table_count(self, database: str, table_name: str) -> int:
        """
        Get row count for a table.

        Args:
            database: Which database ("legacy" or "new")
            table_name: Name of the table

        Returns:
            Number of rows in the table
        """
        try:
            if database == "legacy":
                with self.legacy_engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    return result.scalar() or 0
            elif database == "new":
                with self.new_engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error getting count for {table_name}: {e}")
            return 0

    def truncate_table(self, database: str, table_name: str, confirm: bool = False) -> None:
        """
        Truncate a table (delete all rows).

        Args:
            database: Which database ("legacy" or "new")
            table_name: Name of the table to truncate
            confirm: Confirmation flag (required to prevent accidental truncation)
        """
        if not confirm:
            logger.warning("Truncate table requires confirmation flag")
            return

        try:
            if database == "legacy":
                with self.legacy_engine.connect() as conn:
                    conn.execute(text(f"TRUNCATE TABLE {table_name}"))
                    conn.commit()
                logger.success(f"Truncated legacy table: {table_name}")
            elif database == "new":
                with self.new_engine.connect() as conn:
                    conn.execute(text(f"TRUNCATE TABLE {table_name}"))
                    conn.commit()
                logger.success(f"Truncated new table: {table_name}")
        except Exception as e:
            logger.error(f"Error truncating {table_name}: {e}")
            raise

    def close(self) -> None:
        """Close all database connections."""
        if self._legacy_engine:
            self._legacy_engine.dispose()
            logger.debug("Legacy database engine disposed")

        if self._new_engine:
            self._new_engine.dispose()
            logger.debug("New database engine disposed")


# Global database manager instance
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    return db_manager
