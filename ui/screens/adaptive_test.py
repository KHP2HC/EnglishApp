import json
import customtkinter as ctk
from core.adaptive_test import AdaptiveTest
from data.database import get_session
from data.models import User
from datetime import datetime


class AdaptiveTestScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.load_questions()
        self.test = AdaptiveTest(self.questions)
        self.current = None
        self.build_ui()

    def load_questions(self):
        with open('data/seed/question_bank.json', 'r', encoding='utf-8') as f:
            self.questions = json.load(f)

    def build_ui(self):
        ctk.CTkLabel(self, text='Placement Test', font=('Arial', 20)).pack(pady=8)
        self.q_label = ctk.CTkLabel(self, text='', wraplength=700)
        self.q_label.pack(pady=6)
        self.choice_var = ctk.StringVar(value='')
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(pady=6)
        self.next_btn = ctk.CTkButton(self, text='Start Test', command=self.next_question)
        self.next_btn.pack(pady=8)
        self.feedback = ctk.CTkLabel(self, text='')
        self.feedback.pack(pady=6)

    def next_question(self):
        if self.current is None:
            # start
            self.current = self.test.next_question()
        else:
            # grade previous
            selected = self.choice_var.get()
            correct = (selected == self.current.get('answer'))
            self.test.record_answer(correct)
            self.feedback.configure(text='Correct' if correct else f"Wrong — answer: {self.current.get('answer')}")
            self.current = self.test.next_question()

        if not self.current:
            # finish
            level = self.test.LEVELS[self.test.current_level_index]
            self.feedback.configure(text=f'Test complete. Estimated level: {level}')
            # persist to user
            db = get_session()
            try:
                user = getattr(self.app, 'user', None)
                if user:
                    u = db.query(User).filter_by(id=user.id).first()
                    if u:
                        try:
                            # store as numeric band approximation
                            band_map = {'A1':1,'A2':2,'B1':3,'B2':4,'C1':5,'C2':6}
                            u.current_band = float(band_map.get(level, 3))
                            db.commit()
                        except Exception:
                            db.rollback()
            finally:
                db.close()
            self.next_btn.configure(text='Done', state='disabled')
            return

        # show question
        self.q_label.configure(text=self.current.get('question'))
        for w in self.options_frame.winfo_children():
            w.destroy()
        self.choice_var.set('')
        for opt in self.current.get('options', []):
            rb = ctk.CTkRadioButton(self.options_frame, text=opt, variable=self.choice_var, value=opt)
            rb.pack(anchor='w', pady=2)
        self.next_btn.configure(text='Submit')
