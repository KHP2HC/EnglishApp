from datetime import datetime, timedelta, date
from collections import defaultdict
from data.database import get_session
from data.models import StudySession


def daily_activity_minutes(user_id, days=35):
    """Return a dict mapping date (ISO string) -> minutes studied for the past `days` days."""
    end = date.today()
    start = end - timedelta(days=days - 1)
    db = get_session()
    try:
        q = db.query(StudySession).filter(StudySession.user_id == user_id)
        q = q.filter(StudySession.started_at >= datetime.combine(start, datetime.min.time()))
        sessions = q.all()
        totals = defaultdict(int)
        for s in sessions:
            if not s.started_at or not s.ended_at:
                continue
            try:
                delta = s.ended_at - s.started_at
                mins = int(delta.total_seconds() / 60)
            except Exception:
                mins = 0
            day = s.started_at.date()
            if day < start or day > end:
                continue
            totals[day.isoformat()] += max(0, mins)
        # ensure all days present
        out = {}
        for i in range(days):
            d = (start + timedelta(days=i))
            out[d.isoformat()] = totals.get(d.isoformat(), 0)
        return out
    finally:
        db.close()


def weekly_aggregates(user_id, weeks=5):
    """Return list of weekly total minutes for the past `weeks` weeks (oldest first)."""
    days = weeks * 7
    daily = daily_activity_minutes(user_id, days=days)
    start = date.today() - timedelta(days=days - 1)
    weeks_out = []
    for w in range(weeks):
        total = 0
        for d in range(7):
            day = (start + timedelta(days=w * 7 + d)).isoformat()
            total += daily.get(day, 0)
        weeks_out.append(total)
    return weeks_out


def current_streak(user):
    """Compute current streak days from user's last_active and streak_days stored.

    If `user.last_active` is None, returns 0.
    """
    if not user or not getattr(user, 'last_active', None):
        return 0
    # use stored streak as authoritative; ensure it's not stale
    return getattr(user, 'streak_days', 0) or 0

