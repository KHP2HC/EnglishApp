"""Progress router — learning statistics and activity data.

All operations are scoped to the authenticated user.
Derived values (XP, accuracy, etc.) are calculated server-side.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query

from core.deps import get_current_user
from core.security import AuthenticatedUser
from core.supabase_client import get_supabase, is_supabase_configured
from core.web_schemas import DailyActivityResponse, ProgressStatsResponse

router = APIRouter(prefix="/api/v1/progress", tags=["progress"])


@router.get("/stats", response_model=ProgressStatsResponse)
def get_progress_stats(
    user: AuthenticatedUser = Depends(get_current_user),
) -> ProgressStatsResponse:
    """Get aggregated progress statistics for the authenticated user."""
    if not is_supabase_configured():
        return ProgressStatsResponse()

    supabase = get_supabase()

    # Fetch vocab progress
    vocab_result = (
        supabase.table("vocab_progress")
        .select("times_seen, times_correct")
        .eq("user_id", user.id)
        .execute()
    )
    vocab = vocab_result.data or []

    words_learned = sum(1 for v in vocab if v.get("times_seen", 0) > 0)
    words_mastered = sum(1 for v in vocab if v.get("times_correct", 0) >= 3)

    # Fetch sessions
    sessions_result = (
        supabase.table("study_sessions")
        .select("*")
        .eq("user_id", user.id)
        .order("started_at", desc=True)
        .limit(100)
        .execute()
    )
    sessions = sessions_result.data or []

    total_xp = sum(s.get("xp_earned", 0) for s in sessions)

    # Time per skill (last 30 days)
    thirty_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
    recent_sessions = [s for s in sessions if s.get("started_at", "") >= thirty_ago]

    time_by_skill: dict[str, int] = {}
    skill_accuracy: dict[str, dict] = {}

    for s in recent_sessions:
        skill = s.get("session_type", "OTHER")
        started = s.get("started_at")
        ended = s.get("ended_at")
        if started and ended:
            try:
                mins = int(
                    (datetime.fromisoformat(ended.replace("Z", "+00:00"))
                     - datetime.fromisoformat(started.replace("Z", "+00:00"))).total_seconds() / 60
                )
            except (ValueError, TypeError):
                mins = 25
        else:
            mins = 25

        time_by_skill[skill] = time_by_skill.get(skill, 0) + max(0, mins)

        if skill not in skill_accuracy:
            skill_accuracy[skill] = {"correct": 0, "total": 0}
        skill_accuracy[skill]["total"] += s.get("items_total", 0)
        skill_accuracy[skill]["correct"] += s.get("items_correct", 0)

    return ProgressStatsResponse(
        words_learned=words_learned,
        words_mastered=words_mastered,
        total_xp=total_xp,
        total_sessions=len(sessions),
        time_by_skill=time_by_skill,
        skill_accuracy=skill_accuracy,
        recent_sessions=recent_sessions,
    )


@router.get("/activity", response_model=DailyActivityResponse)
def get_daily_activity(
    user: AuthenticatedUser = Depends(get_current_user),
    days: int = Query(365, ge=1, le=365),
) -> DailyActivityResponse:
    """Get daily activity data for the heatmap (last N days)."""
    if not is_supabase_configured():
        return DailyActivityResponse()

    supabase = get_supabase()
    start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

    result = (
        supabase.table("study_sessions")
        .select("started_at, ended_at")
        .eq("user_id", user.id)
        .gte("started_at", start_date)
        .execute()
    )

    activity: dict[str, int] = {}

    # Initialize all days to 0
    for i in range(days):
        d = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        activity[d] = 0

    for s in (result.data or []):
        started = s.get("started_at")
        if not started:
            continue
        try:
            day = datetime.fromisoformat(started.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except ValueError:
            continue

        ended = s.get("ended_at")
        if ended:
            try:
                mins = int(
                    (datetime.fromisoformat(ended.replace("Z", "+00:00"))
                     - datetime.fromisoformat(started.replace("Z", "+00:00"))).total_seconds() / 60
                )
            except (ValueError, TypeError):
                mins = 25
        else:
            mins = 25

        activity[day] = activity.get(day, 0) + max(0, mins)

    return DailyActivityResponse(activity=activity)
