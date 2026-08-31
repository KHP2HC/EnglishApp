"""Study sessions router — start, update, list, and complete sessions.

All operations are scoped to the authenticated user.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.deps import get_current_user
from core.security import AuthenticatedUser
from core.supabase_client import get_supabase, is_supabase_configured
from core.web_schemas import (
    StartSessionRequest,
    StudySessionResponse,
    UpdateSessionRequest,
)

router = APIRouter(prefix="/api/v1/study-sessions", tags=["study-sessions"])


@router.get("", response_model=list[StudySessionResponse])
def list_sessions(
    user: AuthenticatedUser = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=500),
) -> list[StudySessionResponse]:
    """List the authenticated user's study sessions."""
    if not is_supabase_configured():
        return []

    supabase = get_supabase()
    result = (
        supabase.table("study_sessions")
        .select("*")
        .eq("user_id", user.id)
        .order("started_at", desc=True)
        .limit(limit)
        .execute()
    )

    return [StudySessionResponse(**row) for row in (result.data or [])]


@router.post("", response_model=StudySessionResponse, status_code=status.HTTP_201_CREATED)
def start_session(
    req: StartSessionRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> StudySessionResponse:
    """Start a new study session."""
    if not is_supabase_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )

    supabase = get_supabase()
    result = (
        supabase.table("study_sessions")
        .insert({
            "user_id": user.id,
            "session_type": req.session_type,
        })
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session.",
        )

    return StudySessionResponse(**result.data[0])


@router.patch("/{session_id}", response_model=StudySessionResponse)
def update_session(
    session_id: str,
    req: UpdateSessionRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> StudySessionResponse:
    """Update (end) a study session.

    Only the session owner can update it. The user_id is derived from
    the JWT, not from the request body.
    """
    if not is_supabase_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )

    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update.",
        )

    supabase = get_supabase()

    # Update — scoped to user_id to prevent cross-user modification
    result = (
        supabase.table("study_sessions")
        .update(update_data)
        .eq("id", session_id)
        .eq("user_id", user.id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or not owned by user.",
        )

    # If XP was earned, update the user's total_xp
    if req.xp_earned:
        # Fetch current profile
        profile = (
            supabase.table("profiles")
            .select("total_xp")
            .eq("id", user.id)
            .single()
            .execute()
        )
        if profile.data:
            current_xp = profile.data.get("total_xp", 0)
            supabase.table("profiles").update({
                "total_xp": current_xp + req.xp_earned,
                "last_active": "now()",
            }).eq("id", user.id).execute()

    return StudySessionResponse(**result.data[0])


@router.get("/{session_id}", response_model=StudySessionResponse)
def get_session(
    session_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
) -> StudySessionResponse:
    """Get a single study session by ID (must be owned by the user)."""
    if not is_supabase_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )

    supabase = get_supabase()
    result = (
        supabase.table("study_sessions")
        .select("*")
        .eq("id", session_id)
        .eq("user_id", user.id)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or not owned by user.",
        )

    return StudySessionResponse(**result.data)
