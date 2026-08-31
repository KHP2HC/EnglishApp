"""Profile router — user profile management.

All operations are scoped to the authenticated user. The user_id is
always derived from the validated JWT, never from request bodies.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from core.deps import get_current_user
from core.security import AuthenticatedUser
from core.supabase_client import get_supabase, is_supabase_configured
from core.web_schemas import ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(user: AuthenticatedUser = Depends(get_current_user)) -> ProfileResponse:
    """Get the authenticated user's profile."""
    if not is_supabase_configured():
        return ProfileResponse(id=user.id, name=user.email or "Learner")

    supabase = get_supabase()
    result = supabase.table("profiles").select("*").eq("id", user.id).single().execute()

    if not result.data:
        # Profile may not exist yet — create it
        insert_result = supabase.table("profiles").insert({
            "id": user.id,
            "name": (user.email or "Learner").split("@")[0],
        }).execute()
        return ProfileResponse(**insert_result.data[0])

    return ProfileResponse(**result.data)


@router.patch("", response_model=ProfileResponse)
def update_profile(
    updates: ProfileUpdate,
    user: AuthenticatedUser = Depends(get_current_user),
) -> ProfileResponse:
    """Update the authenticated user's profile."""
    if not is_supabase_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )

    # Only include non-None fields
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update.",
        )

    supabase = get_supabase()
    result = (
        supabase.table("profiles")
        .update(update_data)
        .eq("id", user.id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )

    return ProfileResponse(**result.data[0])
