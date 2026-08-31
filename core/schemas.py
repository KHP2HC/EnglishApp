"""Pydantic schemas for API request/response validation.

Backend validation is authoritative. Frontend validation is a
convenience only — all inputs are validated here with:
- string length limits
- numeric bounds
- enum validation
- required fields
- sensible defaults
"""

from __future__ import annotations


from pydantic import BaseModel, Field, field_validator

# ── SRS / Vocabulary ────────────────────────────────────


class SRSRating(BaseModel):
    """Request body for rating a vocabulary card via SRS."""

    card_id: int = Field(..., ge=1, description="ID of the vocabulary progress card")
    quality: int = Field(
        ...,
        ge=0,
        le=5,
        description="SRS quality rating (0=Again, 2=Hard, 3=Good, 5=Easy)",
    )

    @field_validator("quality")
    @classmethod
    def _validate_quality(cls, v: int) -> int:
        # SM-2 quality values: 0, 1, 2, 3, 4, 5
        if v not in (0, 1, 2, 3, 4, 5):
            raise ValueError("Quality must be one of: 0, 1, 2, 3, 4, 5")
        return v


# ── Reading Tests ───────────────────────────────────────


class ReadingAnswers(BaseModel):
    """Request body for submitting reading test answers."""

    answers: dict[str, str] = Field(
        ...,
        min_length=0,
        max_length=200,
        description="Mapping of question ID to user answer",
    )


class ReadingTestSummary(BaseModel):
    """Response model for reading test list items."""

    id: str
    title: str = "Practice Test"


# ── Health ─────────────────────────────────────────────


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"


# ── Generic ────────────────────────────────────────────


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
