import customtkinter as ctk
from datetime import datetime
from core.study_planner import StudyPlanner
from data.database import get_session
from data.models import StudyPlan


class PlannerScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.saved_plan = None
        self.build_ui()
        self.load_saved_plan()

    def build_ui(self):
        ctk.CTkLabel(self, text='Study Planner', font=('Arial', 20)).pack(pady=10)
        ctk.CTkLabel(self, text='Generate weekly study tasks based on your availability and exam date.').pack(pady=4)
        self.generate_btn = ctk.CTkButton(self, text='Generate Study Plan', command=self.generate_plan)
        self.generate_btn.pack(pady=10)
        self.message_label = ctk.CTkLabel(self, text='', wraplength=760, justify='left')
        self.message_label.pack(pady=6)
        self.plan_frame = ctk.CTkScrollableFrame(self, width=820, height=500)
        self.plan_frame.pack(padx=10, pady=10, fill='both', expand=True)

    def load_saved_plan(self):
        user = getattr(self.app, 'user', None)
        if not user:
            self.message_label.configure(text='Please complete onboarding to create a study plan.')
            return
        db = get_session()
        try:
            record = db.query(StudyPlan).filter_by(user_id=user.id).order_by(StudyPlan.created_at.desc()).first()
            if record and record.plan:
                self.saved_plan = record.plan
                self.message_label.configure(text=f'Loaded saved plan from {record.created_at.date()}')
                self.render_plan(self.saved_plan)
            else:
                self.message_label.configure(text='No saved plan found yet.')
        finally:
            db.close()

    def generate_plan(self):
        user = getattr(self.app, 'user', None)
        if not user:
            self.message_label.configure(text='Please complete onboarding to generate a plan.')
            return
        planner = StudyPlanner(user)
        try:
            plan = planner.generate_plan()
        except Exception as exc:
            self.message_label.configure(text=f'Unable to generate plan: {exc}')
            return
        db = get_session()
        try:
            record = StudyPlan(
                user_id=user.id,
                week_start=datetime.utcnow().date(),
                daily_tasks=plan,
                plan=plan,
                created_at=datetime.utcnow(),
            )
            db.add(record)
            db.commit()
            self.saved_plan = plan
            self.message_label.configure(text='Study plan generated and saved.')
            self.render_plan(plan)
        finally:
            db.close()

    def render_plan(self, plan):
        for w in self.plan_frame.winfo_children():
            w.destroy()
        for week_start, days in plan.items():
            week_frame = ctk.CTkFrame(self.plan_frame)
            week_frame.pack(fill='x', pady=8, padx=10)
            ctk.CTkLabel(week_frame, text=f'Week starting {week_start}', font=('Arial', 16)).pack(anchor='w', pady=4)
            for day in days:
                day_label = ctk.CTkLabel(week_frame, text=f"{day['date']}:")
                day_label.pack(anchor='w', padx=12)
                for task in day.get('tasks', []):
                    ctk.CTkLabel(week_frame, text=f"  • {task['type'].capitalize()}: {task['minutes']} min").pack(anchor='w', padx=24)
