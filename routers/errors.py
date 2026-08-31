"""Errors router — error journal CRUD.

All operations are scoped to the authenticated user.
Users can never access another user's errors.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.deps import get_current_user
from core.security import AuthenticatedUser
from core.supabase_client import get_supabase, is_supabase_configured
from core.web_schemas import CreateErrorRequest, ErrorJournalResponse

router = APIRouter(prefix="/api/v1/errors", tags=["errors"])


@router.get("", response_model=list[ErrorJournalResponse])
def list_errors(
    user: AuthenticatedUser = Depends(get_current_user),
    limit: int = Query(200, ge=1, le=500),
    skill: str | None = Query(None, max_length=100),
) -> list[ErrorJournalResponse]:
    """List the authenticated user's error journal entries."""
    if not is_supabase_configured():
        return []

    supabase = get_supabase()
    query = (
        supabase.table("error_journal")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .limit(limit)
    )

    if skill:
        query = query.eq("skill", skill)

    result = query.execute()
    return [ErrorJournalResponse(**row) for row in (result.data or [])]


@router.post("", response_model=ErrorJournalResponse, status_code=status.HTTP_201_CREATED)
def create_error(
    req: CreateErrorRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> ErrorJournalResponse:
    """Create a new error journal entry."""
    if not is_supabase_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )

    supabase = get_supabase()
    insert_data = {
        "user_id": user.id,
        "session_id": req.session_id,
        "error_category": req.error_category,
        "skill": req.skill,
        "question_snapshot": req.question_snapshot,
        "user_answer": req.user_answer,
        "correct_answer": req.correct_answer,
    }
    # Remove None values to let DB defaults apply
    insert_data = {k: v for k, v in insert_data.items() if v is not None}

    result = supabase.table("error_journal").insert(insert_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create error entry.",
        )

    return ErrorJournalResponse(**result.data[0])


@router.delete("/{error_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_error(
    error_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
) -> None:
    """Delete an error journal entry (must be owned by the user)."""
    if not is_supabase_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )

    supabase = get_supabase()
    result = (
        supabase.table("error_journal")
        .delete()
        .eq("id", error_id)
        .eq("user_id", user.id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error entry not found or not owned by user.",
        )
