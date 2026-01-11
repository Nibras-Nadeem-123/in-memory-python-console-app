from fastapi import Depends
from sqlmodel import Session
from db import get_session


def get_db_session():
    """FastAPI dependency for database session.

    Returns:
        Database session generator
    """
    with get_session() as session:
        yield session
