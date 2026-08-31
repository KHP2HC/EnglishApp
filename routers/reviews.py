"""Reviews router — SRS vocabulary review operations.

All operations are scoped to the authenticated user. The user_id is
always derived from the validated JWT, never from request bodies.

The backend owns all SRS state changes. The frontend displays results.
"""

from __future__ import annotations

import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from core.deps import get_current_user
from core.security import AuthenticatedUser
from core.supabase_client import get_supabase, is_supabase_configured
from core.web_schemas import (
    DueCardsResponse,
    RateCardRequest,
    RateCardResponse,
    StartCardRequest,
    VocabCardResponse,
    VocabProgressResponse,
)
from core.srs_engine import SRSEngine

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


def _calc_xp(quality: int) -> int:
    """Calculate XP earned for a review."""
    return 3 + (5 if quality >= 3 else 0)


@router.get("/due", response_model=DueCardsResponse)
def get_due_cards(
    user: AuthenticatedUser = Depends(get_current_user),
) -> DueCardsResponse:
    """Get due review cards and new cards for the authenticated user."""
    if not is_supabase_configured():
        return DueCardsResponse()

    supabase = get_supabase()
    today = datetime.date.today().isoformat()

    # Get progress rows that are due (or have no next_review_at yet)
    progress_result = (
        supabase.table("vocab_progress")
        .select("*, card:vocab_cards(*)")
        .eq("user_id", user.id)
        .or_(f"next_review_at.lte.{today}T23:59:59,next_review_at.is.null")
        .limit(50)
        .execute()
    )

    review_cards: list[VocabProgressResponse] = []
    existing_card_ids: set[str] = set()

    for row in (progress_result.data or []):
        card_data = row.get("card")
        card = VocabCardResponse(**card_data) if card_data else None
        review_cards.append(
            VocabProgressResponse(
                id=row["id"],
                user_id=row["user_id"],
                card_id=row["card_id"],
                interval_days=row.get("interval_days", 1),
                easiness=row.get("easiness", 2.5),
                repetitions=row.get("repetitions", 0),
                next_review_at=row.get("next_review_at"),
                last_quality=row.get("last_quality"),
                times_seen=row.get("times_seen", 0),
                times_correct=row.get("times_correct", 0),
                card=card,
            )
        )
        existing_card_ids.add(row["card_id"])

    # Get new cards (no progress yet) — limit to 20
    new_result = (
        supabase.table("vocab_cards")
        .select("*")
        .limit(20)
        .execute()
    )

    new_cards: list[VocabCardResponse] = []
    for row in (new_result.data or []):
        if row["id"] not in existing_card_ids:
            new_cards.append(VocabCardResponse(**row))

    return DueCardsResponse(review_cards=review_cards, new_cards=new_cards)


@router.post("/start", response_model=VocabProgressResponse)
def start_card(
    req: StartCardRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> VocabProgressResponse:
    """Start SRS progress for a new card.

    Creates a vocab_progress row for the authenticated user + card.
    Returns 409 if progress already exists.
    """
    if not is_supabase_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )

    supabase = get_supabase()

    # Check if progress already exists
    existing = (
        supabase.table("vocab_progress")
        .select("*")
        .eq("user_id", user.id)
        .eq("card_id", req.card_id)
        .execute()
    )
    if existing.data:
        row = existing.data[0]
        return VocabProgressResponse(**row)

    # Verify card exists
    card_result = (
        supabase.table("vocab_cards")
        .select("*")
        .eq("id", req.card_id)
        .single()
        .execute()
    )
    if not card_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary card not found.",
        )

    # Create progress row
    today = datetime.date.today().isoformat()
    insert_data = {
        "user_id": user.id,
        "card_id": req.card_id,
        "interval_days": 1,
        "easiness": 2.5,
        "repetitions": 0,
        "next_review_at": today,
        "times_seen": 0,
        "times_correct": 0,
    }
    result = supabase.table("vocab_progress").insert(insert_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create progress record.",
        )

    return VocabProgressResponse(**result.data[0])


@router.post("/rate", response_model=RateCardResponse)
def rate_card(
    req: RateCardRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> RateCardResponse:
    """Rate a vocabulary card and update its SRS schedule.

    The backend owns all SRS state changes. The quality score (0-5)
    is validated and applied via the SM-2 algorithm.
    """
    if not is_supabase_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )

    supabase = get_supabase()

    # Fetch the progress row — scoped to authenticated user
    result = (
        supabase.table("vocab_progress")
        .select("*")
        .eq("user_id", user.id)
        .eq("card_id", req.card_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card progress not found. Call /reviews/start first.",
        )

    progress_data = result.data[0]

    # Build a progress-like object for SRSEngine
    class _Progress:
        pass

    progress = _Progress()
    progress.srs_interval = progress_data.get("interval_days", 1)
    progress.srs_easiness = progress_data.get("easiness", 2.5)
    progress.srs_repetitions = progress_data.get("repetitions", 0)
    progress.next_review_date = (
        datetime.date.fromisoformat(progress_data["next_review_at"][:10])
        if progress_data.get("next_review_at")
        else datetime.date.today()
    )
    progress.last_quality = progress_data.get("last_quality")
    progress.times_seen = progress_data.get("times_seen", 0)
    progress.times_correct = progress_data.get("times_correct", 0)

    # Apply SM-2 update
    updated = SRSEngine.update_card(progress, req.quality)

    # Persist the update
    next_review_at = (
        datetime.datetime.combine(updated.next_review_date, datetime.time.min).isoformat()
    )
    update_data = {
        "interval_days": updated.srs_interval,
        "easiness": updated.srs_easiness,
        "repetitions": updated.srs_repetitions,
        "next_review_at": next_review_at,
        "last_quality": updated.last_quality,
        "times_seen": updated.times_seen,
        "times_correct": updated.times_correct,
    }

    supabase.table("vocab_progress").update(update_data).eq("id", progress_data["id"]).execute()

    xp = _calc_xp(req.quality)

    return RateCardResponse(
        id=progress_data["id"],
        interval_days=updated.srs_interval,
        easiness=updated.srs_easiness,
        repetitions=updated.srs_repetitions,
        next_review_at=next_review_at,
        last_quality=updated.last_quality,
        times_seen=updated.times_seen,
        times_correct=updated.times_correct,
        xp_earned=xp,
    )
