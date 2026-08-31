"""Vocabulary router — list, search, filter, and detail.

Vocabulary cards are global content (publicly readable).
No authentication required for read operations.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.supabase_client import get_supabase, is_supabase_configured
from core.web_schemas import VocabCardResponse, VocabListResponse

router = APIRouter(prefix="/api/v1/vocabulary", tags=["vocabulary"])


@router.get("", response_model=VocabListResponse)
def list_vocabulary(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, max_length=100, description="Search query"),
    cefr_level: str | None = Query(None, pattern="^(A1|A2|B1|B2|C1|C2)$"),
    category: str | None = Query(None, max_length=50),
    exam_type: str | None = Query(None, pattern="^(TOEIC|IELTS|TOEFL|VSTEP)$"),
) -> VocabListResponse:
    """List vocabulary cards with pagination, search, and filtering."""
    if not is_supabase_configured():
        return VocabListResponse(items=[], total=0, page=page, page_size=page_size, has_next=False)

    supabase = get_supabase()

    try:
        # Build query
        query = supabase.table("vocab_cards").select("*", count="exact")

        if search:
            # Use ilike for case-insensitive search on word field
            query = query.ilike("word", f"%{search}%")
        if cefr_level:
            query = query.eq("cefr_level", cefr_level)
        if category:
            query = query.eq("category", category)
        if exam_type:
            # exam_type is text[] — use contains filter
            query = query.contains("exam_type", [exam_type])

        # Get total count
        count_result = query.execute()
        total = count_result.count or 0

        # Apply pagination
        offset = (page - 1) * page_size
        result = query.range(offset, offset + page_size - 1).execute()

        items = [VocabCardResponse(**row) for row in (result.data or [])]
        has_next = (offset + page_size) < total
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is temporarily unavailable.",
        )

    return VocabListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=has_next,
    )


@router.get("/{card_id}", response_model=VocabCardResponse)
def get_vocabulary_card(card_id: str) -> VocabCardResponse:
    """Get a single vocabulary card by ID."""
    if not is_supabase_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )

    supabase = get_supabase()
    result = supabase.table("vocab_cards").select("*").eq("id", card_id).single().execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary card not found.",
        )

    return VocabCardResponse(**result.data)
