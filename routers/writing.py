"""Writing router — writing submission management.

All operations are scoped to the authenticated user.
AI feedback is generated server-side; no AI keys are exposed to the frontend.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.deps import get_current_user
from core.security import AuthenticatedUser
from core.supabase_client import get_supabase, is_supabase_configured
from core.web_schemas import WritingSubmissionResponse, WritingSubmitRequest

router = APIRouter(prefix="/api/v1/writing", tags=["writing"])


@router.get("", response_model=list[WritingSubmissionResponse])
def list_submissions(
    user: AuthenticatedUser = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
) -> list[WritingSubmissionResponse]:
    """List the authenticated user's writing submissions."""
    if not is_supabase_configured():
        return []

    supabase = get_supabase()
    result = (
        supabase.table("writing_submissions")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return [WritingSubmissionResponse(**row) for row in (result.data or [])]


@router.post("", response_model=WritingSubmissionResponse, status_code=status.HTTP_201_CREATED)
def submit_writing(
    req: WritingSubmitRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> WritingSubmissionResponse:
    """Submit a writing task for AI feedback.

    The AI feedback is generated server-side. If the AI service is not
    configured, the submission is still saved with null feedback.
    """
    if not is_supabase_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )

    supabase = get_supabase()

    # Try to get AI feedback (if configured)
    ai_feedback = None
    band_estimate = None

    try:
        ai_feedback = _generate_feedback(req.task_prompt, req.user_essay, req.exam_type)
        if ai_feedback and isinstance(ai_feedback, dict):
            band_estimate = ai_feedback.get("band_estimate")
    except Exception:
        # AI feedback is optional — save submission without feedback
        pass

    # Save submission
    insert_data = {
        "user_id": user.id,
        "task_prompt": req.task_prompt,
        "user_essay": req.user_essay,
        "ai_feedback": ai_feedback,
        "band_estimate": band_estimate,
    }

    result = supabase.table("writing_submissions").insert(insert_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save submission.",
        )

    return WritingSubmissionResponse(**result.data[0])


def _generate_feedback(prompt: str, essay: str, exam_type: str | None) -> dict | None:
    """Generate AI feedback for a writing submission.

    Uses Anthropic Claude API if ANTHROPIC_API_KEY is configured.
    Returns None if the API key is not set.
    """
    import os

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    # Use httpx to call the Anthropic API
    import httpx

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    word_count = len(essay.split())
    system_prompt = (
        f"You are an expert IELTS/TOEFL writing examiner. "
        f"Evaluate the following essay and provide structured feedback. "
        f"Return JSON with: band_estimate (float), task_achievement, "
        f"coherence, lexical_resource, grammar_range, overall_tip."
    )

    user_message = f"Task prompt: {prompt}\n\nEssay ({word_count} words):\n{essay}"

    try:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2000,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_message}],
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data.get("content", [{}])[0].get("text", "")

        # Try to parse JSON from the response
        import json

        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return {"raw_feedback": text, "band_estimate": None}
    except Exception:
        return None
