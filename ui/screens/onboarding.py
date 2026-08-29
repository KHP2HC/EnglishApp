import customtkinter as ctk
from datetime import datetime, date, timedelta
from data.database import get_session
from data.models import User, ExamType


class OnboardingWizard(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.step = 1
        self.data = {
            'name': '',
            'avatar_emoji': '😊',
            'exam_type': ExamType.IELTS,
            'target_score': None,
            'exam_date': (date.today() + timedelta(days=90)).isoformat(),
            'daily_free_minutes': {'mon':60,'tue':60,'wed':60,'thu':60,'fri':60,'sat':120,'sun':120},
            'daily_schedule': {
                'mon': {'morning': 30, 'afternoon': 20, 'evening': 10},
                'tue': {'morning': 30, 'afternoon': 20, 'evening': 10},
                'wed': {'morning': 30, 'afternoon': 20, 'evening': 10},
                'thu': {'morning': 30, 'afternoon': 20, 'evening': 10},
                'fri': {'morning': 30, 'afternoon': 20, 'evening': 10},
                'sat': {'morning': 45, 'afternoon': 45, 'evening': 30},
                'sun': {'morning': 45, 'afternoon': 45, 'evening': 30},
            },
            'preferred_session_time': 'MORNING'
        }
        self._build_step()

    def _normalize_exam_type(self, value):
        if isinstance(value, ExamType):
            return value
        if isinstance(value, str):
            try:
                return ExamType[value.upper()]
            except Exception:
                try:
                    return ExamType(value)
                except Exception:
                    return ExamType.IELTS
        return ExamType.IELTS

    def _clear(self):
        for w in list(self.winfo_children()):
            w.destroy()

    def _build_step(self):
        self._clear()
        if self.step == 1:
            self._step_profile()
        elif self.step == 2:
            self._step_target()
        elif self.step == 3:
            self._step_exam_date()
        elif self.step == 4:
            self._step_free_time()
        else:
            self._step_finish()

    def _nav_buttons(self, back=False, next_label='Next'):
        frame = ctk.CTkFrame(self)
        frame.pack(pady=12)
        ctk.CTkButton(frame, text=next_label, command=self._next).pack(side='left', padx=8)

    def _step_profile(self):
        ctk.CTkLabel(self, text='Welcome — let\'s set up your profile', font=('Arial',18)).pack(pady=8)
        ctk.CTkLabel(self, text='Name').pack(pady=4)
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.insert(0, self.data.get('name', ''))
        self.name_entry.pack(pady=4)

        ctk.CTkLabel(self, text='Avatar (emoji)').pack(pady=4)
        self.avatar_entry = ctk.CTkEntry(self)
        self.avatar_entry.insert(0, self.data.get('avatar_emoji', '😊'))
        self.avatar_entry.pack(pady=4)

        self._nav_buttons(back=False, next_label='Next')

    def _step_target(self):
        ctk.CTkLabel(self, text='Set your exam target', font=('Arial',18)).pack(pady=8)
        ctk.CTkLabel(self, text='Exam type').pack()
        exam_options = [e.name for e in ExamType]
        self.exam_menu = ctk.CTkOptionMenu(self, values=exam_options, command=self._on_exam_change)
        normalized_exam = self._normalize_exam_type(self.data.get('exam_type', ExamType.IELTS))
        self.exam_menu.set(normalized_exam.name)
        self.exam_menu.pack(pady=6)

        ctk.CTkLabel(self, text='Target score').pack(pady=4)
        # slider range differs per exam; default for IELTS 0.0-9.0
        self.target_var = ctk.DoubleVar(value=self.data.get('target_score') or 6.0)
        self.target_slider = ctk.CTkSlider(self, from_=0.0, to=9.0, number_of_steps=90, variable=self.target_var)
        self.target_slider.pack(pady=6)
        self.target_label = ctk.CTkLabel(self, text=lambda: f"Target: {self.target_var.get():.1f}")
        # update label manually
        self.target_label.configure(text=f"Target: {self.target_var.get():.1f}")

        def update_label(var, indx, mode):
            self.target_label.configure(text=f"Target: {self.target_var.get():.1f}")

        self.target_var.trace_add('write', update_label)
        self.target_label.pack()
        self._nav_buttons()

    def _on_exam_change(self, value):
        # adjust slider ranges for exams
        exam = ExamType[value]
        if exam == ExamType.IELTS:
            self.target_slider.configure(from_=0.0, to=9.0, number_of_steps=90)
            self.target_var.set(6.0)
        elif exam == ExamType.TOEIC:
            self.target_slider.configure(from_=10, to=990, number_of_steps=98)
            self.target_var.set(600)
        elif exam == ExamType.TOEFL:
            self.target_slider.configure(from_=0, to=120, number_of_steps=120)
            self.target_var.set(80)
        elif exam == ExamType.VSTEP:
            self.target_slider.configure(from_=1, to=6, number_of_steps=5)
            self.target_var.set(3)

    def _step_exam_date(self):
        ctk.CTkLabel(self, text='When is your exam?', font=('Arial',18)).pack(pady=8)
        ctk.CTkLabel(self, text='Enter date (YYYY-MM-DD)').pack()
        self.date_entry = ctk.CTkEntry(self)
        self.date_entry.insert(0, self.data.get('exam_date'))
        self.date_entry.pack(pady=6)
        self.countdown_label = ctk.CTkLabel(self, text='')
        self.countdown_label.pack(pady=6)

        def update_countdown(*_):
            try:
                d = datetime.fromisoformat(self.date_entry.get()).date()
                days = (d - date.today()).days
                if days < 0:
                    msg = 'Exam date has passed — update your target date to stay on track.'
                elif days < 30:
                    msg = f'{days} days until exam — focus on high-yield review and light daily practice.'
                else:
                    msg = f'{days} days until exam'
                self.countdown_label.configure(text=msg)
            except Exception:
                self.countdown_label.configure(text='Invalid date')

        self.date_entry.bind('<KeyRelease>', lambda e: update_countdown())
        update_countdown()
        self._nav_buttons()

    def _step_free_time(self):
        ctk.CTkLabel(self, text='Weekly availability', font=('Arial',18)).pack(pady=8)
        days = ['mon','tue','wed','thu','fri','sat','sun']
        self.free_entries = {}
        for d in days:
            row = ctk.CTkFrame(self)
            row.pack(fill='x', padx=20, pady=2)
            ctk.CTkLabel(row, text=d.capitalize(), width=80).pack(side='left')
            schedule = self.data.get('daily_schedule', {}).get(d, {'morning': 30, 'afternoon': 20, 'evening': 10})
            morning_entry = ctk.CTkEntry(row, width=45)
            afternoon_entry = ctk.CTkEntry(row, width=45)
            evening_entry = ctk.CTkEntry(row, width=45)
            morning_entry.insert(0, str(schedule.get('morning', 0)))
            afternoon_entry.insert(0, str(schedule.get('afternoon', 0)))
            evening_entry.insert(0, str(schedule.get('evening', 0)))
            ctk.CTkLabel(row, text='Morning').pack(side='left', padx=6)
            morning_entry.pack(side='left', padx=2)
            ctk.CTkLabel(row, text='Afternoon').pack(side='left', padx=6)
            afternoon_entry.pack(side='left', padx=2)
            ctk.CTkLabel(row, text='Evening').pack(side='left', padx=6)
            evening_entry.pack(side='left', padx=2)
            slot = ctk.CTkOptionMenu(row, values=['MORNING','AFTERNOON','EVENING'])
            slot.set(self.data.get('preferred_session_time', 'MORNING'))
            slot.pack(side='left', padx=6)
            self.free_entries[d] = (morning_entry, afternoon_entry, evening_entry, slot)
        self._nav_buttons(next_label='Finish')

    def _step_finish(self):
        ctk.CTkLabel(self, text='Ready to start', font=('Arial',18)).pack(pady=8)
        summary = ctk.CTkLabel(self, text='Choose how you want to begin your prep.', wraplength=700)
        summary.pack(pady=6)
        ctk.CTkButton(self, text='Start Placement Test', command=lambda: self._save_and_finish('placement')).pack(pady=8)
        ctk.CTkButton(self, text='Skip for now', command=lambda: self._save_and_finish('dashboard')).pack(pady=4)

    def _next(self):
        # persist current step data into self.data
        if self.step == 1:
            self.data['name'] = self.name_entry.get().strip()
            self.data['avatar_emoji'] = self.avatar_entry.get().strip() or '😊'
        elif self.step == 2:
            ex = self.exam_menu.get()
            self.data['exam_type'] = self._normalize_exam_type(ex)
            self.data['target_score'] = float(self.target_var.get())
        elif self.step == 3:
            self.data['exam_date'] = self.date_entry.get().strip()
        elif self.step == 4:
            daily_schedule = {}
            for d, (morning_entry, afternoon_entry, evening_entry, slot) in self.free_entries.items():
                try:
                    morning = int(morning_entry.get())
                except Exception:
                    morning = 0
                try:
                    afternoon = int(afternoon_entry.get())
                except Exception:
                    afternoon = 0
                try:
                    evening = int(evening_entry.get())
                except Exception:
                    evening = 0
                total = morning + afternoon + evening
                daily_schedule[d] = {'morning': morning, 'afternoon': afternoon, 'evening': evening}
                self.data['daily_free_minutes'][d] = total
                self.data['preferred_session_time'] = slot.get()
            self.data['daily_schedule'] = daily_schedule
        # advance
        self.step += 1
        self._build_step()

    def _back(self):
        if self.step > 1:
            self.step -= 1
        self._build_step()

    def _save_and_finish(self, next_page='dashboard'):
        # save to DB (create or update user)
        db = get_session()
        try:
            user = None
            if getattr(self.app, 'user', None):
                user = db.query(User).filter_by(id=self.app.user.id).first()
            if not user:
                user = User(name=self.data['name'] or 'Learner')
                db.add(user)

            exam_date_raw = self.data.get('exam_date', '').strip()
            try:
                exam_date = datetime.fromisoformat(exam_date_raw).date()
            except Exception:
                exam_date = date.today() + timedelta(days=90)

            user.name = self.data.get('name') or user.name
            user.avatar_emoji = self.data.get('avatar_emoji', user.avatar_emoji)
            user.target_exam = self._normalize_exam_type(self.data.get('exam_type', user.target_exam))
            user.target_score = float(self.data.get('target_score') or user.target_score or 0)
            user.exam_date = exam_date
            user.daily_free_minutes = self.data.get('daily_free_minutes', user.daily_free_minutes or {})
            user.daily_schedule = self.data.get('daily_schedule', user.daily_schedule or {})
            user.preferred_session_time = self.data.get('preferred_session_time', user.preferred_session_time or 'MORNING')
            db.commit()
            db.refresh(user)
            self.app.user = user
        finally:
            db.close()
        self.app.navigate(next_page)