import datetime
from app import App
from data.database import init_db, get_session
from data.seed import load_seed_data
from data.models import User, ExamType


def _normalize_user_profile(user):
    if not user:
        return None
    if getattr(user, 'target_exam', None) is None:
        user.target_exam = ExamType.IELTS
    elif not isinstance(user.target_exam, ExamType):
        if isinstance(user.target_exam, str):
            try:
                user.target_exam = ExamType[user.target_exam.upper()]
            except Exception:
                try:
                    user.target_exam = ExamType(user.target_exam)
                except Exception:
                    user.target_exam = ExamType.IELTS
        else:
            user.target_exam = ExamType.IELTS
    if getattr(user, 'daily_free_minutes', None) is None:
        user.daily_free_minutes = {'mon': 60, 'tue': 60, 'wed': 60, 'thu': 60, 'fri': 60, 'sat': 120, 'sun': 120}
    if getattr(user, 'daily_schedule', None) is None:
        user.daily_schedule = {
            'mon': {'morning': 30, 'afternoon': 20, 'evening': 10},
            'tue': {'morning': 30, 'afternoon': 20, 'evening': 10},
            'wed': {'morning': 30, 'afternoon': 20, 'evening': 10},
            'thu': {'morning': 30, 'afternoon': 20, 'evening': 10},
            'fri': {'morning': 30, 'afternoon': 20, 'evening': 10},
            'sat': {'morning': 45, 'afternoon': 45, 'evening': 30},
            'sun': {'morning': 45, 'afternoon': 45, 'evening': 30},
        }
    if getattr(user, 'preferred_session_time', None) is None:
        user.preferred_session_time = 'MORNING'
    if getattr(user, 'theme_mode', None) is None:
        user.theme_mode = 'dark'
    return user


def get_existing_user():
    db = get_session()
    try:
        user = db.query(User).first()
        return _normalize_user_profile(user)
    finally:
        db.close()


def main():
    init_db()
    load_seed_data()
    user = get_existing_user()
    start_page = 'onboarding' if user is None else 'dashboard'
    app = App(start_page=start_page)
    app.user = user
    theme_mode = getattr(user, 'theme_mode', None) or 'dark'
    app.set_theme_mode(theme_mode)
    app.navigate(start_page)
    if user is None:
        app.notify('Complete onboarding to personalize your study plan.', duration=5000)
    app.mainloop()


if __name__ == '__main__':
    main()
