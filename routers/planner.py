"""Planner router — study plan generation and retrieval.

All operations are scoped to the authenticated user.
Plan generation uses the same algorithm as the frontend planner.ts.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from core.deps import get_current_user
from core.security import AuthenticatedUser
from core.supabase_client import get_supabase, is_supabase_configured
from core.web_schemas import GeneratePlanRequest, StudyPlanResponse

router = APIRouter(prefix="/api/v1/planner", tags=["planner"])


# ── Skill allocation per exam type ──────────────────────

BASE_ALLOCATION = {
    "TOEIC": {"vocabulary": 0.35, "grammar": 0.25, "listening": 0.30, "reading": 0.10},
    "IELTS": {"vocabulary": 0.25, "grammar": 0.20, "listening": 0.20, "reading": 0.20, "writing": 0.15},
    "TOEFL": {"vocabulary": 0.20, "grammar": 0.20, "listening": 0.20, "reading": 0.20, "writing": 0.10, "speaking": 0.10},
    "VSTEP": {"vocabulary": 0.30, "grammar": 0.20, "listening": 0.20, "reading": 0.20, "writing": 0.10},
}

SKILL_LABELS = {
    "vocabulary": "SRS Vocabulary",
    "grammar": "Grammar Practice",
    "listening": "Listening Exercise",
    "reading": "Reading Practice",
    "writing": "Writing Task",
    "speaking": "Speaking Practice",
    "mock": "Mock Test",
}


def _generate_weekly_plan(
    target_exam: str,
    exam_date: str | None,
    free_time: dict | None,
) -> dict:
    """Generate a weekly study plan.

    Mirrors the algorithm in web/src/lib/planner.ts.
    """
    allocation = dict(BASE_ALLOCATION.get(target_exam, BASE_ALLOCATION["IELTS"]))

    # Adjust: boost weakest skill, reduce strongest
    entries = list(allocation.items())
    if len(entries) >= 2:
        sorted_entries = sorted(entries, key=lambda x: x[1])
        weakest = sorted_entries[0][0]
        strongest = sorted_entries[-1][0]
        allocation[weakest] += 0.05
        allocation[strongest] -= 0.05

    # Add mock tests in final 4 weeks
    days_left = 999
    if exam_date:
        try:
            exam_dt = datetime.fromisoformat(exam_date.split("T")[0])
            days_left = max(0, (exam_dt - datetime.now().date()).days)
        except (ValueError, TypeError):
            pass

    if days_left <= 28:
        # Replace some allocation with mock tests
        for skill in list(allocation.keys()):
            allocation[skill] *= 0.85
        allocation["mock"] = allocation.get("mock", 0) + 0.15

    # Distribute across days
    ft = free_time or {
        "mon": 60, "tue": 60, "wed": 60, "thu": 60, "fri": 60, "sat": 120, "sun": 120,
    }

    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    daily_tasks: dict[str, list] = {}

    for day in days:
        day_minutes = ft.get(day, 60)
        tasks = []
        for skill, fraction in allocation.items():
            minutes = max(5, int(day_minutes * fraction))
            if minutes >= 5:
                tasks.append({
                    "type": skill,
                    "minutes": minutes,
                    "label": SKILL_LABELS.get(skill, skill.title()),
                })
        daily_tasks[day] = tasks

    return daily_tasks


@router.get("", response_model=StudyPlanResponse)
def get_study_plan(
    user: AuthenticatedUser = Depends(get_current_user),
) -> StudyPlanResponse:
    """Get the current week's study plan for the authenticated user."""
    if not is_supabase_configured():
        return StudyPlanResponse(
            id="",
            user_id=user.id,
            week_start=datetime.now().strftime("%Y-%m-%d"),
            daily_tasks={},
        )

    supabase = get_supabase()

    # Calculate current week start (Monday)
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())

    result = (
        supabase.table("study_plans")
        .select("*")
        .eq("user_id", user.id)
        .gte("week_start", week_start.isoformat())
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not result.data:
        return StudyPlanResponse(
            id="",
            user_id=user.id,
            week_start=week_start.isoformat(),
            daily_tasks={},
        )

    return StudyPlanResponse(**result.data[0])


@router.post("", response_model=StudyPlanResponse)
def generate_plan(
    req: GeneratePlanRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> StudyPlanResponse:
    """Generate and save a weekly study plan."""
    if not is_supabase_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )

    supabase = get_supabase()

    # Fetch profile for defaults
    profile_result = (
        supabase.table("profiles")
        .select("*")
        .eq("id", user.id)
        .single()
        .execute()
    )

    profile = profile_result.data or {}

    target_exam = req.target_exam or profile.get("target_exam") or "IELTS"
    exam_date = req.exam_date or profile.get("exam_date")
    free_time = req.free_time or profile.get("free_time")

    daily_tasks = _generate_weekly_plan(target_exam, exam_date, free_time)

    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())

    # Upsert plan
    result = (
        supabase.table("study_plans")
        .upsert({
            "user_id": user.id,
            "week_start": week_start.isoformat(),
            "daily_tasks": daily_tasks,
        })
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save plan.",
        )

    return StudyPlanResponse(**result.data[0])
