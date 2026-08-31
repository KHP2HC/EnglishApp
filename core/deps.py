"""Shared FastAPI dependencies for EnglishCoach Pro.

Centralizes database session, authentication, and other cross-cutting
dependencies so they can be reused across routers and tests.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from core.security import (
    AuthenticatedUser,
    get_current_user,
    get_current_user_id,
    require_admin,
)
from data.database import SessionLocal

__all__ = [
    "get_db",
    "get_current_user",
    "get_current_user_id",
    "require_admin",
    "AuthenticatedUser",
]


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed.

    Usage:
        @app.get("/items")
        def list_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
