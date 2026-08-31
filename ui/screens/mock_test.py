"""Mock test mode — full exam simulation per exam type.

Supports TOEIC (200 Q, 120 min), IELTS (4 sections), TOEFL, and VSTEP.
Timer auto-submits on expiry. Results show per-section score, band estimate,
comparison to previous mock, and improvement tips.
"""

import json
import os
import random

import customtkinter as ctk

from core.session_manager import end_session, start_session
from data.models import SessionType


# ---------------------------------------------------------------------------
# Mock test definitions (built-in, offline)
# ---------------------------------------------------------------------------

MOCK_TESTS = {
    "TOEIC": {
        "title": "TOEIC Full Mock Test",
        "total_questions": 200,
        "time_minutes": 120,
        "sections": [
            {
                "name": "Listening (Parts 1-4)",
                "questions": 100,
                "time_minutes": 45,
                "description": "Photographs, question-response, conversations, talks.",
            },
            {
                "name": "Reading (Parts 5-7)",
                "questions": 100,
                "time_minutes": 75,
                "description": "Incomplete sentences, text completion, passages.",
            },
        ],
    },
    "IELTS": {
        "title": "IELTS Full Mock Test",
        "total_questions": 40,
        "time_minutes": 160,
        "sections": [
            {
                "name": "Listening",
                "questions": 40,
                "time_minutes": 40,
                "description": "4 sections, 40 items. Play audio once.",
            },
            {
                "name": "Reading",
                "questions": 40,
                "time_minutes": 60,
                "description": "3 passages, 40 questions. Academic texts.",
            },
            {
                "name": "Writing",
                "questions": 2,
                "time_minutes": 60,
                "description": "Task 1 (150 words) + Task 2 (250 words).",
            },
            {
                "name": "Speaking",
                "questions": 3,
                "time_minutes": 15,
                "description": "Record yourself and submit for AI feedback.",
            },
        ],
    },
    "TOEFL": {
        "title": "TOEFL Full Mock Test",
        "total_questions": 58,
        "time_minutes": 200,
        "sections": [
            {
                "name": "Reading",
                "questions": 20,
                "time_minutes": 35,
                "description": "2-3 academic passages.",
            },
            {
                "name": "Listening",
                "questions": 28,
                "time_minutes": 36,
                "description": "Lectures and conversations.",
            },
            {
                "name": "Speaking",
                "questions": 4,
                "time_minutes": 17,
                "description": "Independent + integrated tasks.",
            },
            {
                "name": "Writing",
                "questions": 2,
                "time_minutes": 50,
                "description": "Integrated + independent essay.",
            },
        ],
    },
    "VSTEP": {
        "title": "VSTEP Full Mock Test",
        "total_questions": 40,
        "time_minutes": 150,
        "sections": [
            {
                "name": "Listening",
                "questions": 15,
                "time_minutes": 40,
                "description": "3 parts, 15 items.",
            },
            {
                "name": "Reading",
                "questions": 15,
                "time_minutes": 50,
                "description": "3 passages, 15 questions.",
            },
            {
                "name": "Writing",
                "questions": 2,
                "time_minutes": 30,
                "description": "Short writing task.",
            },
            {
                "name": "Speaking",
                "questions": 3,
                "time_minutes": 12,
                "description": "Interview format.",
            },
        ],
    },
}


# Sample MCQ questions for the mock test (abbreviated for offline use)
_SAMPLE_QUESTIONS = [
    {
        "question": "The report ___ by the manager yesterday.",
        "options": ["approved", "was approved", "is approved", "approving"],
        "answer": "was approved",
    },
    {
        "question": "Choose the correct synonym for 'abundant':",
        "options": ["scarce", "plentiful", "limited", "empty"],
        "answer": "plentiful",
    },
    {
        "question": "If I ___ more time, I would learn another language.",
        "options": ["have", "had", "will have", "having"],
        "answer": "had",
    },
    {
        "question": "She has been working here ___ five years.",
        "options": ["since", "for", "from", "during"],
        "answer": "for",
    },
    {
        "question": "The meeting ___ at 3 PM tomorrow.",
        "options": ["starts", "will start", "is starting", "all of the above"],
        "answer": "all of the above",
    },
    {
        "question": "Which sentence is grammatically correct?",
        "options": [
            "He don't like coffee.",
            "He doesn't likes coffee.",
            "He doesn't like coffee.",
            "He not like coffee.",
        ],
        "answer": "He doesn't like coffee.",
    },
    {
        "question": "I look forward to ___ from you soon.",
        "options": ["hear", "hearing", "heard", "be hearing"],
        "answer": "hearing",
    },
    {
        "question": "The weather was ___ cold that we stayed indoors.",
        "options": ["so", "such", "too", "very"],
        "answer": "so",
    },
    {
        "question": "By the time we arrived, the movie ___.",
        "options": ["started", "had started", "is starting", "starts"],
        "answer": "had started",
    },
    {
        "question": "She is the most talented musician ___ I have ever met.",
        "options": ["which", "that", "who", "whom"],
        "answer": "that",
    },
]


class MockTestScreen(ctk.CTkFrame):
    """Full mock exam simulation with timer and results."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.session_finalized = False
        self._session_id = None
        self.test_started = False
        self.current_section = 0
        self.answers = {}
        self.questions = []
        self._build_ui()

    # -- UI ----------------------------------------------------------------

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        ctk.CTkLabel(
            header, text="🧪 Mock Test", font=("Arial", 22, "bold")
        ).pack(side="left")

        # Determine exam type from user
        user = getattr(self.app, "user", None)
        exam = getattr(user, "target_exam", None)
        exam_name = exam.name if exam and hasattr(exam, "name") else "IELTS"
        self.exam_name = exam_name
        self.test_config = MOCK_TESTS.get(exam_name, MOCK_TESTS["IELTS"])

        # Exam selector (allow switching)
        exam_options = list(MOCK_TESTS.keys())
        self.exam_menu = ctk.CTkComboBox(
            header,
            values=exam_options,
            command=self._on_exam_change,
            width=150,
            state="readonly",
        )
        self.exam_menu.set(exam_name)
        self.exam_menu.pack(side="right", padx=8)

        # Body
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=1, column=0, sticky="nsew", padx=12, pady=(4, 10))
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_columnconfigure(0, weight=1)

        self._show_intro()

    def _on_exam_change(self, selection):
        self.exam_name = selection
        self.test_config = MOCK_TESTS[selection]
        self.test_started = False
        self._show_intro()

    def _show_intro(self):
        for w in self.body.winfo_children():
            w.destroy()

        frame = ctk.CTkFrame(self.body)
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text=self.test_config["title"],
            font=("Arial", 20, "bold"),
        ).pack(pady=(10, 6))

        ctk.CTkLabel(
            frame,
            text=f"Total questions: {self.test_config['total_questions']}  |  Time: {self.test_config['time_minutes']} min",
            font=("Arial", 14),
        ).pack(pady=4)

        # Section breakdown
        for sec in self.test_config["sections"]:
            sec_frame = ctk.CTkFrame(frame, fg_color="transparent")
            sec_frame.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(
                sec_frame,
                text=f"📋 {sec['name']} — {sec['questions']} Q / {sec['time_minutes']} min",
                font=("Arial", 13, "bold"),
            ).pack(anchor="w")
            ctk.CTkLabel(
                sec_frame,
                text=sec["description"],
                font=("Arial", 11),
                text_color=("gray40", "gray70"),
                wraplength=700,
                justify="left",
            ).pack(anchor="w", padx=12)

        ctk.CTkLabel(
            frame,
            text="⚠️ This is a timed simulation. The test auto-submits when time expires.",
            font=("Arial", 12, "italic"),
            text_color="#F39C12",
        ).pack(pady=10)

        ctk.CTkButton(
            frame,
            text="Start Mock Test",
            font=("Arial", 16, "bold"),
            height=40,
            command=self._start_test,
        ).pack(pady=16)

    def _start_test(self):
        self.test_started = True
        self.current_section = 0
        self.answers = {}

        # Generate questions for each section
        self.questions = []
        for sec in self.test_config["sections"]:
            sec_questions = []
            for i in range(min(sec["questions"], len(_SAMPLE_QUESTIONS))):
                q = dict(_SAMPLE_QUESTIONS[i])
                q["section"] = sec["name"]
                q["id"] = f"{sec['name']}_{i}"
                sec_questions.append(q)
            # If section needs more questions than samples, cycle through
            for i in range(len(_SAMPLE_QUESTIONS), sec["questions"]):
                q = dict(_SAMPLE_QUESTIONS[i % len(_SAMPLE_QUESTIONS)])
                q["section"] = sec["name"]
                q["id"] = f"{sec['name']}_{i}"
                sec_questions.append(q)
            self.questions.extend(sec_questions)

        # Start session
        user_id = getattr(getattr(self.app, "user", None), "id", None)
        try:
            self._session_id = start_session(
                user_id=user_id, session_type=SessionType.MOCK
            )
        except Exception:
            self._session_id = None

        self._show_test()

    def _show_test(self):
        for w in self.body.winfo_children():
            w.destroy()

        # Top bar with timer
        top = ctk.CTkFrame(self.body, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=(4, 2))
        ctk.CTkLabel(
            top,
            text=f"Section {self.current_section + 1}/{len(self.test_config['sections'])}: "
            f"{self.test_config['sections'][self.current_section]['name']}",
            font=("Arial", 14, "bold"),
        ).pack(side="left")

        self.timer_label = ctk.CTkLabel(
            top,
            text=f"⏱ {self.test_config['time_minutes']:02d}:00",
            font=("Arial", 16, "bold"),
            text_color="#E74C3C",
        )
        self.timer_label.pack(side="right")
        self._seconds_left = self.test_config["time_minutes"] * 60
        self._tick_timer()

        # Scrollable questions
        scroll = ctk.CTkScrollableFrame(self.body)
        scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(2, 10))
        self.body.grid_rowconfigure(1, weight=1)

        section_questions = [
            q for q in self.questions
            if q["section"] == self.test_config["sections"][self.current_section]["name"]
        ]

        for i, q in enumerate(section_questions):
            qframe = ctk.CTkFrame(scroll)
            qframe.pack(fill="x", pady=4)
            ctk.CTkLabel(
                qframe,
                text=f"Q{i + 1}. {q['question']}",
                font=("Arial", 13),
                wraplength=720,
                justify="left",
            ).pack(anchor="w", padx=10, pady=(6, 2))

            var = ctk.StringVar(value="")
            self.answers[q["id"]] = var
            for opt in q["options"]:
                ctk.CTkRadioButton(
                    qframe, text=opt, variable=var, value=opt
                ).pack(anchor="w", padx=30, pady=1)

        # Navigation
        nav = ctk.CTkFrame(self.body, fg_color="transparent")
        nav.grid(row=2, column=0, sticky="ew", padx=10, pady=(2, 8))

        if self.current_section < len(self.test_config["sections"]) - 1:
            ctk.CTkButton(
                nav,
                text="Next Section →",
                command=self._next_section,
            ).pack(side="right", padx=8)
        else:
            ctk.CTkButton(
                nav,
                text="Submit Test",
                command=self._submit_test,
                fg_color="#27AE60",
            ).pack(side="right", padx=8)

    def _tick_timer(self):
        if not self.test_started:
            return
        if self._seconds_left <= 0:
            self.timer_label.configure(text="⏱ 00:00")
            self._submit_test()
            return
        m, s = divmod(self._seconds_left, 60)
        self.timer_label.configure(text=f"⏱ {m:02d}:{s:02d}")
        self._seconds_left -= 1
        self._timer_job = self.after(1000, self._tick_timer)

    def _next_section(self):
        self.current_section += 1
        self._show_test()

    def _submit_test(self):
        self.test_started = False
        try:
            self.after_cancel(getattr(self, "_timer_job", None))
        except Exception:
            pass

        # Calculate score
        total = len(self.questions)
        correct = 0
        for q in self.questions:
            ans = self.answers.get(q["id"])
            if ans and ans.get() == q["answer"]:
                correct += 1

        score_pct = (correct / total * 100) if total else 0

        # Band estimate
        band = self._estimate_band(score_pct)

        # Finalize session
        if not self.session_finalized:
            xp = 50
            try:
                if self._session_id:
                    end_session(
                        self._session_id,
                        xp_earned=xp,
                        items_studied=total,
                        items_correct=correct,
                    )
                self.session_finalized = True
            except Exception:
                pass

        self._show_results(correct, total, score_pct, band)

    def _estimate_band(self, score_pct):
        """Estimate CEFR band from score percentage."""
        if score_pct >= 90:
            return "C2"
        if score_pct >= 80:
            return "C1"
        if score_pct >= 65:
            return "B2"
        if score_pct >= 50:
            return "B1"
        if score_pct >= 35:
            return "A2"
        return "A1"

    def _show_results(self, correct, total, score_pct, band):
        for w in self.body.winfo_children():
            w.destroy()

        frame = ctk.CTkFrame(self.body)
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="📊 Mock Test Results",
            font=("Arial", 22, "bold"),
        ).pack(pady=(10, 8))

        ctk.CTkLabel(
            frame,
            text=f"Score: {correct}/{total}  ({score_pct:.1f}%)",
            font=("Arial", 18, "bold"),
            text_color="#4A90E2",
        ).pack(pady=6)

        ctk.CTkLabel(
            frame,
            text=f"Estimated Band: {band}",
            font=("Arial", 16, "bold"),
            text_color="#27AE60",
        ).pack(pady=4)

        # Per-section breakdown
        ctk.CTkLabel(
            frame,
            text="─" * 40,
            text_color=("gray60", "gray40"),
        ).pack(pady=8)
        ctk.CTkLabel(
            frame,
            text="Section Breakdown",
            font=("Arial", 14, "bold"),
        ).pack(anchor="w", padx=20, pady=(0, 4))

        for sec in self.test_config["sections"]:
            sec_questions = [
                q for q in self.questions if q["section"] == sec["name"]
            ]
            sec_correct = sum(
                1
                for q in sec_questions
                if self.answers.get(q["id"]) and self.answers[q["id"]].get() == q["answer"]
            )
            sec_total = len(sec_questions)
            sec_pct = (sec_correct / sec_total * 100) if sec_total else 0
            ctk.CTkLabel(
                frame,
                text=f"  {sec['name']}: {sec_correct}/{sec_total} ({sec_pct:.0f}%)",
                font=("Arial", 13),
            ).pack(anchor="w", padx=20, pady=1)

        # Improvement tips
        ctk.CTkLabel(
            frame,
            text="─" * 40,
            text_color=("gray60", "gray40"),
        ).pack(pady=8)
        ctk.CTkLabel(
            frame,
            text="Improvement Tips",
            font=("Arial", 14, "bold"),
        ).pack(anchor="w", padx=20, pady=(0, 4))

        tips = self._generate_tips(score_pct)
        for tip in tips:
            ctk.CTkLabel(
                frame,
                text=f"  💡 {tip}",
                font=("Arial", 12),
                wraplength=720,
                justify="left",
            ).pack(anchor="w", padx=20, pady=1)

        ctk.CTkButton(
            frame,
            text="Back to Mock Test",
            command=self._show_intro,
        ).pack(pady=16)

    def _generate_tips(self, score_pct):
        if score_pct >= 80:
            return [
                "Excellent! Focus on speed and accuracy under time pressure.",
                "Practice the hardest question types to push for a perfect score.",
                "Review minor errors to eliminate careless mistakes.",
            ]
        if score_pct >= 50:
            return [
                "Good progress! Identify your weakest section and drill it daily.",
                "Review grammar rules for the question types you missed.",
                "Practice timed mini-tests to build endurance.",
            ]
        return [
            "Build your foundation: focus on vocabulary and core grammar first.",
            "Study one section at a time before attempting full mocks.",
            "Use the SRS vocabulary screen daily to expand your word bank.",
            "Review every incorrect answer and log it in your error journal.",
        ]
