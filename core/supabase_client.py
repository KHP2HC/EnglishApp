"""Supabase client for backend database access.

Provides a service-role Supabase client for server-side database operations.
The service-role key bypasses RLS, so ALL queries must include explicit
user_id filters derived from the validated JWT — never from client input.

Usage:
    from core.supabase_client import get_supabase

    supabase = get_supabase()
    result = supabase.table("vocab_progress").select("*").eq("user_id", user.id).execute()
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from supabase import Client, create_client

from core.config import get_settings

logger = logging.getLogger("englishcoach.supabase")


@lru_cache
def get_supabase() -> Client:
    """Return a cached Supabase service-role client.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    Falls back to anon key if service role is not configured (development).
    """
    settings = get_settings()

    if not settings.SUPABASE_URL:
        logger.warning(
            "SUPABASE_URL is not configured — database operations will fail. "
            "Set SUPABASE_URL in your .env file."
        )

    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
    if not key:
        logger.warning(
            "No Supabase key configured — database operations will fail. "
            "Set SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY in your .env file."
        )

    client = create_client(
        settings.SUPABASE_URL or "https://placeholder.supabase.co",
        key or "placeholder-key",
    )
    return client


def is_supabase_configured() -> bool:
    """Check if Supabase is properly configured."""
    settings = get_settings()
    return bool(settings.SUPABASE_URL and (settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY))


def execute_query(func):
    """Decorator that wraps a database function and handles errors.

    Catches PostgrestAPIError and other exceptions, logging them
    and raising a generic HTTPException.
    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error("Database operation failed: %s", e, exc_info=True)
            raise

    return wrapper
