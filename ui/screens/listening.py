import customtkinter as ctk
from datetime import datetime
from data.database import get_session
from data.models import StudySession, SessionType
from core.session_manager import record_session, start_session, end_session
from ui.components.timer_widget import TimerWidget


class ListeningScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.session_finalized = False
        self.prompt = "Listen to the sentence and choose the correct interpretation."
        self.options = [
            "The man is tired and wants to rest.",
            "The man is running late for work.",
            "The man is hungry and looking for food.",
            "The man is going on vacation."
        ]
        self.selected = ctk.StringVar(value=self.options[0])
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="Listening Practice", font=("Arial", 20)).pack(pady=10)
        # timer for listening practice
        user_id = getattr(self.app.user, 'id', None)
        try:
            self._session_id = start_session(user_id=user_id, session_type=SessionType.LISTENING)
        except Exception:
            self._session_id = None
        self.timer = TimerWidget(self, minutes=5, on_finish=self._on_timer_finish)
        self.timer.pack(pady=6)
        try:
            self.timer.start()
        except Exception:
            pass
        ctk.CTkLabel(self, text=self.prompt, wraplength=760, justify="left").pack(padx=20, pady=10)
        for option in self.options:
            ctk.CTkRadioButton(self, text=option, variable=self.selected, value=option).pack(anchor="w", padx=30, pady=2)
        ctk.CTkButton(self, text="Submit Answer", command=self.submit_answer).pack(pady=15)
        self.feedback_label = ctk.CTkLabel(self, text="", wraplength=760, justify="left")
        self.feedback_label.pack(pady=10)

    def submit_answer(self):
        correct = "The man is running late for work."
        answer = self.selected.get()
        if answer == correct:
            message = "Correct! The sentence conveys that the man is late."
        else:
            message = f"Not quite. The best answer is: {correct}."
        self.feedback_label.configure(text=message)
        self.save_session()

    def save_session(self):
        if self.session_finalized:
            return
        user = getattr(self.app, 'user', None)
        if not user:
            return
        try:
            items_correct = 1 if self.selected.get() == "The man is running late for work." else 0
            if getattr(self, '_session_id', None):
                end_session(self._session_id, xp_earned=8, items_studied=1, items_correct=items_correct)
            else:
                record_session(user_id=user.id, session_type=SessionType.LISTENING, xp_earned=8, items_studied=1, items_correct=items_correct)
            self.session_finalized = True
        except Exception:
            pass

    def _on_timer_finish(self):
        # called when timer ends
        try:
            if not self.session_finalized:
                if getattr(self, '_session_id', None):
                    end_session(self._session_id, xp_earned=8, items_studied=1, items_correct=0)
                else:
                    user = getattr(self.app, 'user', None)
                    if user:
                        record_session(user_id=user.id, session_type=SessionType.LISTENING, xp_earned=8, items_studied=1, items_correct=0)
                self.session_finalized = True
        except Exception:
            pass