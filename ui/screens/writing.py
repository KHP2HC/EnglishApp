import customtkinter as ctk
from datetime import datetime
from data.models import SessionType
from core.ai_tutor import AITutor
from core.session_manager import record_session, start_session, end_session
from ui.components.timer_widget import TimerWidget


class WritingScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.session_finalized = False
        self.tutor = AITutor(config_path='config/ai_key.bin') if AITutor.is_configured('config/ai_key.bin') else None
        self._session_id = None
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="Writing Practice", font=("Arial", 20)).pack(pady=10)
        user_id = getattr(self.app.user, 'id', None)
        try:
            self._session_id = start_session(user_id=user_id, session_type=SessionType.WRITING)
        except Exception:
            self._session_id = None
        self.timer = TimerWidget(self, minutes=20, on_finish=self._on_timer_finish)
        self.timer.pack(pady=6)
        try:
            self.timer.start()
        except Exception:
            pass
        ctk.CTkLabel(self, text="Describe a recent achievement in English learning.", wraplength=760, justify="left").pack(padx=20, pady=10)
        self.essay_entry = ctk.CTkTextbox(self, width=780, height=220)
        self.essay_entry.pack(padx=20, pady=8)
        ctk.CTkButton(self, text="Get Feedback", command=self.get_feedback).pack(pady=10)
        self.feedback_label = ctk.CTkLabel(self, text="", wraplength=760, justify="left")
        self.feedback_label.pack(pady=10)

    def get_feedback(self):
        essay = self.essay_entry.get("0.0", "end").strip()
        if not essay:
            self.feedback_label.configure(text="Please write something first.")
            return
        if not self.tutor:
            response_text = self._get_offline_feedback(essay)
            self.feedback_label.configure(text=response_text)
            self.save_session()
            return

        try:
            response_text = self.tutor.get_writing_feedback(essay, task_type='essay', exam_type='IELTS')
            if isinstance(response_text, bytes):
                response_text = response_text.decode('utf-8', errors='ignore')
            self.feedback_label.configure(text=response_text)
            self.save_session()
        except Exception as exc:
            response_text = self._get_offline_feedback(essay)
            self.feedback_label.configure(text=f"Unable to fetch AI feedback: {exc}\n\nOffline feedback:\n{response_text}")

    def _get_offline_feedback(self, essay):
        word_count = len(essay.split())
        feedback = [
            "Offline feedback:",
            f"Your response is {word_count} words long.",
            "Strengths: clear topic focus and relevant examples.",
            "Next step: add one specific detail, one linking phrase, and one more complex sentence structure.",
        ]
        return "\n".join(feedback)

    def save_session(self):
        if self.session_finalized:
            return
        user = getattr(self.app, 'user', None)
        if not user:
            return
        try:
            if getattr(self, '_session_id', None):
                end_session(self._session_id, xp_earned=25, items_studied=1, items_correct=1)
            else:
                record_session(user_id=user.id, session_type=SessionType.WRITING, xp_earned=25, items_studied=1, items_correct=1)
            self.session_finalized = True
        except Exception:
            pass

    def _on_timer_finish(self):
        try:
            if not self.session_finalized:
                self.save_session()
        except Exception:
            pass