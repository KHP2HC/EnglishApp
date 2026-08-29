import os
import webbrowser
import asyncio
import customtkinter as ctk
from tkinter import filedialog
from data.models import SessionType
from core.pronunciation import PronunciationCoach
from core.session_manager import record_session, start_session, end_session


class SpeakingScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.target_sentence = "The future belongs to those who prepare for it today."
        self.audio_path = None
        self.correct_audio_path = None
        self.session_saved = False
        self.coach = PronunciationCoach()
        self._session_id = None
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="Pronunciation Coach", font=("Arial", 20)).pack(pady=10)
        user_id = getattr(self.app.user, 'id', None)
        try:
            self._session_id = start_session(user_id=user_id, session_type=SessionType.SPEAKING)
        except Exception:
            self._session_id = None

        ctk.CTkLabel(
            self,
            text="Upload your recorded speech and compare it to the target phrase below.",
            wraplength=760,
            justify="left"
        ).pack(padx=20, pady=8)

        self.target_label = ctk.CTkLabel(
            self,
            text=self.target_sentence,
            wraplength=760,
            justify="left",
            font=("Arial", 14, "italic")
        )
        self.target_label.pack(padx=20, pady=12)

        ctk.CTkButton(self, text="Upload Audio Recording", command=self.upload_audio).pack(pady=8)
        self.file_label = ctk.CTkLabel(self, text="No file selected.", wraplength=760, justify="left")
        self.file_label.pack(pady=4)

        ctk.CTkButton(self, text="Evaluate Recording", command=self.evaluate_recording).pack(pady=10)
        self.play_button = ctk.CTkButton(self, text="Play Correct Pronunciation", command=self.play_correct_pronunciation, state="disabled")
        self.play_button.pack(pady=4)

        self.feedback_label = ctk.CTkLabel(self, text="", wraplength=760, justify="left")
        self.feedback_label.pack(pady=12)

        self.tip_label = ctk.CTkLabel(
            self,
            text="Tip: Use a clear audio file with one speaker, and record in a quiet room.",
            wraplength=760,
            justify="left",
            text_color="#a6a6a6"
        )
        self.tip_label.pack(pady=4)

    def upload_audio(self):
        path = filedialog.askopenfilename(
            title="Choose your speech recording",
            filetypes=[("Audio files", "*.wav *.mp3 *.m4a *.ogg *.flac"), ("All files", "*.*")],
        )
        if not path:
            return
        self.audio_path = path
        self.file_label.configure(text=f"Selected: {os.path.basename(path)}")
        self.feedback_label.configure(text="Audio loaded. Press Evaluate Recording to score your pronunciation.")

    def evaluate_recording(self):
        if not self.audio_path:
            self.feedback_label.configure(text="Please upload an audio recording first.")
            return

        self.feedback_label.configure(text="Evaluating your pronunciation... this may take a moment.")
        try:
            result = self._run_async(self.coach.evaluate(self.target_sentence, self.audio_path))
            self._display_result(result)
            self.save_session()
        except Exception as exc:
            self.feedback_label.configure(text=f"Unable to evaluate audio: {exc}")

    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def _display_result(self, result):
        spoken_text = result.get("spoken_text", "")
        accuracy = result.get("accuracy", 0.0)
        mismatches = result.get("mismatches", [])
        detailed_feedback = result.get("detailed_feedback", "")
        self.correct_audio_path = result.get("audio_file")

        accuracy_pct = int(accuracy * 100)
        mismatch_text = ", ".join(mismatches) if mismatches else "None"
        feedback = (
            f"Recognized text: {spoken_text}\n"
            f"Pronunciation score: {accuracy_pct}%\n"
            f"Mismatched words: {mismatch_text}\n\n"
            f"Detailed feedback:\n{detailed_feedback or 'Great effort — keep practicing for smoother fluency.'}"
        )
        self.feedback_label.configure(text=feedback)
        audio_available = bool(self.correct_audio_path and os.path.isfile(self.correct_audio_path))
        self.play_button.configure(state="normal" if audio_available else "disabled")

    def play_correct_pronunciation(self):
        if not self.correct_audio_path or not os.path.isfile(self.correct_audio_path):
            self.feedback_label.configure(text="No generated pronunciation audio available yet.")
            return
        try:
            if os.name == "nt":
                os.startfile(self.correct_audio_path)
            else:
                webbrowser.open(f"file://{os.path.abspath(self.correct_audio_path)}")
        except Exception as exc:
            self.feedback_label.configure(text=f"Unable to play audio: {exc}")

    def save_session(self):
        if self.session_saved:
            return
        user = getattr(self.app, 'user', None)
        if not user:
            return

        try:
            if getattr(self, '_session_id', None):
                end_session(self._session_id, xp_earned=20, items_studied=1, items_correct=1)
            else:
                record_session(user_id=user.id, session_type=SessionType.SPEAKING, xp_earned=20, items_studied=1, items_correct=1)
            self.session_saved = True
        except Exception:
            pass
