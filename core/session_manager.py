from datetime import datetime, timedelta
from data.database import get_session
from data.models import StudySession, User


def record_session(user_id, session_type, xp_earned=0, items_studied=0, items_correct=0):
    """Create a StudySession, update user XP, streak and last_active.

    - `session_type` should be a SessionType enum value.
    """
    db = get_session()
    try:
        user = db.query(User).filter_by(id=user_id).first() if user_id else None
        score = 0.0
        try:
            if items_studied:
                score = float(items_correct) / float(items_studied)
        except Exception:
            score = 0.0

        session = StudySession(
            user_id=user_id,
            session_type=session_type,
            started_at=datetime.utcnow(),
            ended_at=datetime.utcnow(),
            score=score,
            xp_earned=int(xp_earned),
            items_studied=int(items_studied),
            items_correct=int(items_correct),
        )
        db.add(session)

        if user:
            user.total_xp = (user.total_xp or 0) + int(xp_earned)
            # update streak: if last_active is yesterday -> increment, if today -> keep, else reset to 1
            now = datetime.utcnow()
            if user.last_active:
                try:
                    last_date = user.last_active.date()
                except Exception:
                    last_date = None
            else:
                last_date = None

            today = now.date()
            if last_date == today:
                pass
            elif last_date == today - timedelta(days=1):
                user.streak_days = (user.streak_days or 0) + 1
            else:
                user.streak_days = 1
            user.last_active = now

        db.commit()
    finally:
        db.close()


def start_session(user_id, session_type):
    """Create a StudySession row with started_at now and return its id."""
    db = get_session()
    try:
        session = StudySession(user_id=user_id, session_type=session_type, started_at=datetime.utcnow(), ended_at=None, score=None)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session.id
    finally:
        db.close()


def end_session(session_id, xp_earned=0, items_studied=0, items_correct=0):
    """Finalize an existing StudySession and update user XP/streak."""
    db = get_session()
    try:
        s = db.query(StudySession).filter_by(id=session_id).first()
        if not s:
            return
        s.ended_at = datetime.utcnow()
        s.xp_earned = int(xp_earned)
        s.items_studied = int(items_studied)
        s.items_correct = int(items_correct)
        try:
            if items_studied:
                s.score = float(items_correct) / float(items_studied)
            else:
                s.score = 0.0
        except Exception:
            s.score = 0.0

        user = db.query(User).filter_by(id=s.user_id).first() if s.user_id else None
        if user:
            user.total_xp = (user.total_xp or 0) + int(xp_earned)
            now = datetime.utcnow()
            if user.last_active:
                try:
                    last_date = user.last_active.date()
                except Exception:
                    last_date = None
            else:
                last_date = None
            today = now.date()
            if last_date == today:
                pass
            elif last_date == today - timedelta(days=1):
                user.streak_days = (user.streak_days or 0) + 1
            else:
                user.streak_days = 1
            user.last_active = now

        db.commit()
    finally:
        db.close()
