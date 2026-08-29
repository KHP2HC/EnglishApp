import customtkinter as ctk
from datetime import datetime, date
from ui.components.progress_ring import ProgressRing
from data.database import get_session
from data.models import StudyPlan
from core.study_planner import StudyPlanner


def _level_info(xp):
    # simple linear level thresholds: 1000 XP per level
    level = int(xp // 1000)
    xp_into = int(xp % 1000)
    next_threshold = 1000
    return level, xp_into, next_threshold


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        # app.user should be set by main startup
        self.user = getattr(self.app, "user", None)
        self.build_ui()

    def _exam_label(self):
        exam = getattr(self.user, 'target_exam', None)
        if exam is None:
            return 'Not set'
        if hasattr(exam, 'name'):
            return exam.name
        return str(exam)

    def build_ui(self):
        # Top: greeting + date + countdown
        header = ctk.CTkLabel(self, text=f"Welcome back, {getattr(self.user, 'name', 'Learner')}", font=("Arial", 20))
        header.pack(pady=8)
        today_label = ctk.CTkLabel(self, text=datetime.now().strftime("%A, %B %d, %Y"))
        today_label.pack(pady=2)
        exam_date = getattr(self.user, 'exam_date', None)
        if exam_date:
            try:
                days_left = (exam_date - date.today()).days
                countdown = f"{days_left} days to exam"
            except Exception:
                countdown = "Exam date not set"
        else:
            countdown = "Set your exam date in onboarding"
        ctk.CTkLabel(self, text=countdown, font=("Arial", 14, "bold")).pack(pady=4)
        streak = ctk.CTkLabel(self, text=f"Streak: {getattr(self.user, 'streak_days', 0)} days")
        streak.pack()
        xp = getattr(self.user, 'total_xp', 0) or 0
        level, xp_into, next_thresh = _level_info(xp)
        ctk.CTkLabel(self, text=f"Level {level} — Total XP: {xp}").pack(pady=6)
        ring = ProgressRing(self, progress=xp_into, total=next_thresh, size=120)
        ring.pack(pady=12)
        exam_text = self._exam_label()
        ctk.CTkLabel(self, text=f"Target exam: {exam_text}").pack(pady=4)
        if getattr(self.user, 'exam_date', None):
            ctk.CTkLabel(self, text=f"Exam date: {self.user.exam_date}").pack(pady=4)
        ctk.CTkLabel(self, text="Today's plan").pack(pady=6)
        self.plan_label = ctk.CTkLabel(self, text='Generate a plan in Planner to see your weekly study tasks.', wraplength=760, justify='left')
        self.plan_label.pack(pady=4)
        self.plan_cards_frame = ctk.CTkScrollableFrame(self, width=760, height=180)
        self.plan_cards_frame.pack(padx=10, pady=6, fill='x')
        self._load_plan_summary()
        self._render_plan_cards()

        action_frame = ctk.CTkFrame(self)
        action_frame.pack(pady=8)
        ctk.CTkButton(action_frame, text='Open Planner', command=lambda: self.app.navigate('planner')).pack(side='left', padx=8)
        ctk.CTkButton(action_frame, text='Start Placement Test', command=lambda: self.app.navigate('placement')).pack(side='left', padx=8)

        self.word_label = ctk.CTkLabel(self, text=f"Word of the day: {self._word_of_the_day()}", wraplength=760, justify='left')
        self.word_label.pack(pady=4)

    def _load_plan_summary(self):
        if not self.user:
            return
        db = get_session()
        try:
            plan_record = db.query(StudyPlan).filter_by(user_id=self.user.id).order_by(StudyPlan.created_at.desc()).first()
            if plan_record and plan_record.plan:
                total_minutes = 0
                for week in plan_record.plan.values():
                    for day in week:
                        for task in day.get('tasks', []):
                            total_minutes += int(task.get('minutes', 0))
                self.plan_label.configure(text=f"Saved study plan from {plan_record.created_at.date()}: {total_minutes} min planned this week.")
                self._saved_plan = plan_record.plan
            else:
                try:
                    planner = StudyPlanner(self.user)
                    generated_plan = planner.generate_plan()
                    first_week = next(iter(generated_plan.values()), [])
                    total_minutes = sum(int(task.get('minutes', 0)) for day in first_week for task in day.get('tasks', []))
                    self.plan_label.configure(text=f"Suggested plan generated from your profile: {total_minutes} min for the next week.")
                    self._saved_plan = generated_plan
                except Exception:
                    self.plan_label.configure(text='Generate a plan in Planner to see your weekly study tasks.')
                    self._saved_plan = None
        finally:
            db.close()

    def _render_plan_cards(self):
        for child in self.plan_cards_frame.winfo_children():
            child.destroy()

        if getattr(self, '_saved_plan', None):
            first_week = next(iter(self._saved_plan.values()), [])
            tasks = []
            for day in first_week[:3]:
                for task in day.get('tasks', [])[:2]:
                    tasks.append(task)
        else:
            tasks = [
                {'type': 'Vocabulary', 'minutes': 20, 'detail': 'Review 15 cards due today'},
                {'type': 'Listening', 'minutes': 15, 'detail': '2 short clips with notes'},
                {'type': 'Grammar', 'minutes': 25, 'detail': 'Conditionals + error review'}
            ]

        for idx, task in enumerate(tasks[:4]):
            card = ctk.CTkFrame(self.plan_cards_frame, corner_radius=12)
            card.pack(fill='x', padx=6, pady=4)
            ctk.CTkLabel(card, text=f"{idx+1}. {task.get('type', 'Task').capitalize()}", font=("Arial", 14, "bold")).pack(anchor='w', padx=10, pady=(8, 2))
            ctk.CTkLabel(card, text=f"{task.get('minutes', 0)} min • {task.get('detail', 'Study session')}", wraplength=700, justify='left').pack(anchor='w', padx=10, pady=(0, 8))
    def _word_of_the_day(self):
        return 'serendipity – an unexpected yet happy discovery.'
