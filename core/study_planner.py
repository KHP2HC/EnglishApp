from datetime import datetime, timedelta

from data.models import ExamType

class StudyPlanner:
    DEFAULT_FREE_MINUTES = {
        'mon': 60, 'tue': 60, 'wed': 60, 'thu': 60, 'fri': 60, 'sat': 120, 'sun': 120
    }

    def __init__(self, user):
        self.user = user
        today = datetime.now().date()
        exam_date = getattr(user, 'exam_date', None)
        if isinstance(exam_date, str):
            try:
                exam_date = datetime.fromisoformat(exam_date).date()
            except Exception:
                exam_date = None
        if exam_date:
            self.days_remaining = max(0, (exam_date - today).days)
        else:
            self.days_remaining = 28
        free_minutes = getattr(user, 'daily_free_minutes', None) or {}
        self.free_minutes = {k.lower(): int(v) for k, v in (free_minutes.items() if isinstance(free_minutes, dict) else {})}
        schedule = getattr(user, 'daily_schedule', None) or {}
        self.daily_minutes = {}
        for day, default in self.DEFAULT_FREE_MINUTES.items():
            slots = schedule.get(day, {}) if isinstance(schedule, dict) else {}
            if isinstance(slots, dict):
                slot_total = 0
                for key in ('morning', 'afternoon', 'evening'):
                    try:
                        slot_total += int(slots.get(key, 0) or 0)
                    except Exception:
                        pass
                self.daily_minutes[day] = slot_total or self.free_minutes.get(day, default)
            else:
                self.daily_minutes[day] = self.free_minutes.get(day, default)
        self.total_hours = sum(self.daily_minutes.get(day, self.DEFAULT_FREE_MINUTES[day]) for day in self.DEFAULT_FREE_MINUTES) * (self.days_remaining / 7) / 60
        self.weights = self._skill_weights()

    def _normalize_exam_name(self, exam):
        if exam is None:
            return None
        if hasattr(exam, 'name'):
            return exam.name
        if isinstance(exam, str):
            try:
                return ExamType[exam.upper()].name
            except Exception:
                return exam.upper()
        return str(exam).upper()

    def _skill_weights(self):
        exam = getattr(self.user, 'target_exam', None)
        current_band = getattr(self.user, 'current_band', None)
        exam_name = self._normalize_exam_name(exam)

        base_weights = {'vocabulary': 0.35, 'reading': 0.25, 'listening': 0.2, 'writing': 0.1, 'speaking': 0.1}
        if exam_name:
            if exam_name == 'IELTS':
                base_weights = {'vocabulary': 0.25, 'reading': 0.25, 'listening': 0.25, 'writing': 0.15, 'speaking': 0.1}
            elif exam_name == 'TOEFL':
                base_weights = {'vocabulary': 0.2, 'reading': 0.3, 'listening': 0.3, 'writing': 0.1, 'speaking': 0.1}
            elif exam_name == 'TOEIC':
                base_weights = {'vocabulary': 0.25, 'reading': 0.2, 'listening': 0.35, 'writing': 0.1, 'speaking': 0.1}
            else:
                base_weights = {'vocabulary': 0.3, 'reading': 0.25, 'listening': 0.2, 'writing': 0.15, 'speaking': 0.1}

        if current_band is not None:
            try:
                band = float(current_band)
            except Exception:
                band = None
            if band is not None:
                if band <= 2.0:
                    base_weights = {'vocabulary': 0.38, 'reading': 0.22, 'listening': 0.2, 'writing': 0.1, 'speaking': 0.1}
                elif band <= 3.0:
                    base_weights = {'vocabulary': 0.32, 'reading': 0.24, 'listening': 0.22, 'writing': 0.12, 'speaking': 0.1}
                elif band >= 5.0:
                    base_weights = {'vocabulary': 0.22, 'reading': 0.23, 'listening': 0.2, 'writing': 0.18, 'speaking': 0.17}

        return base_weights

    def generate_plan(self):
        plan = {}
        days = max(7, self.days_remaining)
        weeks = (days + 6) // 7
        start_date = datetime.now().date()
        for week in range(weeks):
            week_start = start_date + timedelta(weeks=week)
            daily_tasks = self._generate_week(week_start)
            plan[week_start.isoformat()] = daily_tasks
        return plan

    def generate_structured_plan(self):
        weeks = []
        start_date = datetime.now().date()
        for week in range(max(1, (self.days_remaining + 6) // 7)):
            week_start = start_date + timedelta(weeks=week)
            weeks.append({
                'week_start': week_start.isoformat(),
                'daily_tasks': self._generate_week(week_start)
            })
        return weeks

    def _generate_week(self, week_start):
        daily = []
        for d in range(7):
            day_date = week_start + timedelta(days=d)
            if self.days_remaining and (day_date - datetime.now().date()).days >= self.days_remaining:
                break
            weekday_key = day_date.strftime('%a').lower()
            minutes = self.daily_minutes.get(weekday_key, self.DEFAULT_FREE_MINUTES.get(weekday_key, 60))
            tasks = []
            for skill, weight in self.weights.items():
                allocated = max(5, int(minutes * weight))
                lesson_count = max(1, int(round(allocated / 20)))
                tasks.append({'type': skill, 'minutes': allocated, 'lesson_count': lesson_count})
            daily.append({'date': day_date.isoformat(), 'tasks': tasks})
        return daily