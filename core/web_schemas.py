"""Pydantic schemas for the Web API.

These schemas match the canonical Supabase PostgreSQL schema defined in
supabase/migrations/. All UUIDs, timestamps, and constraints mirror
the database definitions.

Backend validation is authoritative — frontend validation is convenience only.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ── Profile ────────────────────────────────────────────


class ProfileUpdate(BaseModel):
    """Request body for updating a user profile."""

    name: Optional[str] = Field(None, max_length=100)
    avatar_emoji: Optional[str] = Field(None, max_length=4)
    target_exam: Optional[str] = Field(None, pattern="^(TOEIC|IELTS|TOEFL|VSTEP)$")
    target_score: Optional[float] = Field(None, ge=0, le=999.9)
    current_band: Optional[float] = Field(None, ge=0, le=99.9)
    skill_bands: Optional[dict] = None
    exam_date: Optional[date] = None
    free_time: Optional[dict] = None
    daily_schedule: Optional[dict] = None
    session_time: Optional[str] = Field(None, pattern="^(MORNING|AFTERNOON|EVENING)$")
    theme_mode: Optional[str] = Field(None, max_length=20)
    onboarded: Optional[bool] = None


class ProfileResponse(BaseModel):
    """Response model for profile data."""

    id: str
    name: str = ""
    avatar_emoji: str = "🧑"
    target_exam: Optional[str] = None
    target_score: Optional[float] = None
    current_band: Optional[float] = None
    skill_bands: dict = Field(default_factory=dict)
    exam_date: Optional[str] = None
    free_time: dict = Field(default_factory=dict)
    daily_schedule: dict = Field(default_factory=dict)
    session_time: str = "MORNING"
    theme_mode: str = "dark"
    streak_days: int = 0
    total_xp: int = 0
    last_active: Optional[str] = None
    onboarded: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ── Vocabulary ─────────────────────────────────────────


class VocabCardResponse(BaseModel):
    """Response model for a vocabulary card."""

    id: str
    word: str
    phonetic: Optional[str] = None
    synonym: Optional[str] = None
    antonym: Optional[str] = None
    meaning_en: str
    meaning_vi: str
    example_sentence: Optional[str] = None
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    exam_type: list[str] = Field(default_factory=list)
    cefr_level: Optional[str] = None
    category: str = "general"


class VocabListResponse(BaseModel):
    """Paginated vocabulary list response."""

    items: list[VocabCardResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


# ── SRS / Reviews ──────────────────────────────────────


class VocabProgressResponse(BaseModel):
    """Response model for vocabulary progress (SRS state)."""

    id: str
    user_id: str
    card_id: str
    interval_days: int = 1
    easiness: float = 2.5
    repetitions: int = 0
    next_review_at: Optional[str] = None
    last_quality: Optional[int] = None
    times_seen: int = 0
    times_correct: int = 0
    card: Optional[VocabCardResponse] = None


class DueCardsResponse(BaseModel):
    """Response model for due cards (review + new)."""

    review_cards: list[VocabProgressResponse] = Field(default_factory=list)
    new_cards: list[VocabCardResponse] = Field(default_factory=list)


class StartCardRequest(BaseModel):
    """Request body for starting a new card's SRS progress."""

    card_id: str


class RateCardRequest(BaseModel):
    """Request body for rating a card via SRS."""

    card_id: str
    quality: int = Field(..., ge=0, le=5, description="0=Again, 2=Hard, 3=Good, 5=Easy")

    @field_validator("quality")
    @classmethod
    def _validate_quality(cls, v: int) -> int:
        if v not in (0, 1, 2, 3, 4, 5):
            raise ValueError("Quality must be one of: 0, 1, 2, 3, 4, 5")
        return v


class RateCardResponse(BaseModel):
    """Response model after rating a card."""

    id: str
    interval_days: int
    easiness: float
    repetitions: int
    next_review_at: Optional[str] = None
    last_quality: int
    times_seen: int
    times_correct: int
    xp_earned: int


# ── Study Sessions ─────────────────────────────────────


class StartSessionRequest(BaseModel):
    """Request body for starting a study session."""

    session_type: str = Field(..., pattern="^(VOCABULARY|GRAMMAR|LISTENING|READING|WRITING|SPEAKING|MOCK)$")


class UpdateSessionRequest(BaseModel):
    """Request body for updating (ending) a study session."""

    ended_at: Optional[str] = None
    xp_earned: Optional[int] = Field(None, ge=0)
    items_total: Optional[int] = Field(None, ge=0)
    items_correct: Optional[int] = Field(None, ge=0)


class StudySessionResponse(BaseModel):
    """Response model for a study session."""

    id: str
    user_id: str
    started_at: str
    ended_at: Optional[str] = None
    session_type: str
    xp_earned: int = 0
    items_total: int = 0
    items_correct: int = 0
    created_at: Optional[str] = None


# ── Progress ───────────────────────────────────────────


class ProgressStatsResponse(BaseModel):
    """Response model for progress statistics."""

    words_learned: int = 0
    words_mastered: int = 0
    total_xp: int = 0
    total_sessions: int = 0
    time_by_skill: dict = Field(default_factory=dict)
    skill_accuracy: dict = Field(default_factory=dict)
    recent_sessions: list[dict] = Field(default_factory=list)


class DailyActivityResponse(BaseModel):
    """Response model for daily activity heatmap data."""

    activity: dict[str, int] = Field(default_factory=dict)


# ── Error Journal ──────────────────────────────────────


class CreateErrorRequest(BaseModel):
    """Request body for creating an error journal entry."""

    session_id: Optional[str] = None
    error_category: Optional[str] = Field(None, max_length=200)
    skill: Optional[str] = Field(None, max_length=100)
    question_snapshot: Optional[str] = None
    user_answer: Optional[str] = None
    correct_answer: Optional[str] = None


class ErrorJournalResponse(BaseModel):
    """Response model for an error journal entry."""

    id: str
    user_id: str
    session_id: Optional[str] = None
    error_category: Optional[str] = None
    skill: Optional[str] = None
    question_snapshot: Optional[str] = None
    user_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    created_at: Optional[str] = None


# ── Planner ────────────────────────────────────────────


class StudyPlanResponse(BaseModel):
    """Response model for a study plan."""

    id: str
    user_id: str
    week_start: str
    daily_tasks: dict = Field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class GeneratePlanRequest(BaseModel):
    """Request body for generating a study plan (optional overrides)."""

    target_exam: Optional[str] = Field(None, pattern="^(TOEIC|IELTS|TOEFL|VSTEP)$")
    target_score: Optional[float] = None
    current_band: Optional[float] = None
    exam_date: Optional[str] = None
    free_time: Optional[dict] = None


# ── Writing ────────────────────────────────────────────


class WritingSubmitRequest(BaseModel):
    """Request body for submitting a writing task."""

    task_prompt: str = Field(..., max_length=5000)
    user_essay: str = Field(..., max_length=50000)
    exam_type: Optional[str] = "IELTS"


class WritingSubmissionResponse(BaseModel):
    """Response model for a writing submission."""

    id: str
    user_id: str
    task_prompt: Optional[str] = None
    user_essay: Optional[str] = None
    ai_feedback: Optional[dict] = None
    band_estimate: Optional[float] = None
    created_at: Optional[str] = None


# ── Health ─────────────────────────────────────────────


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"


# ── Generic ────────────────────────────────────────────


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


# ── Reading Tests (existing, preserved) ─────────────────


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
