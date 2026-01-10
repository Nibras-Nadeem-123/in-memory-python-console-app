from sqlmodel import create_engine, Session, text
from contextlib import contextmanager
from typing import Generator
from .config import settings


# Create database engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=settings.log_level == "DEBUG"
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide database session with automatic cleanup.

    Yields:
        Session object for database operations

    Guarantees:
        - Session is automatically committed on success
        - Session is automatically rolled back on error
        - Session is closed after use
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def check_connection() -> bool:
    """Check if database connection is working.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        with get_session() as session:
            session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
