"""Grammar lesson viewer with exercises.

Renders grammar lessons (Markdown-style) inside CTk frames and provides
multiple-choice exercises with immediate feedback and error-journal logging.
"""

import random

import customtkinter as ctk

from core.session_manager import end_session, record_session, start_session
from data.models import SessionType


# ---------------------------------------------------------------------------
# Built-in grammar lessons (no internet required)
# ---------------------------------------------------------------------------

GRAMMAR_LESSONS = [
    {
        "id": "present_simple",
        "title": "Present Simple",
        "level": "A1",
        "summary": "Used for habits, routines, facts and general truths.",
        "body": (
            "Structure: Subject + base verb (add -s/-es for he/she/it).\n\n"
            "Examples:\n"
            "  • I work every day.\n"
            "  • She plays tennis on weekends.\n"
            "  • Water boils at 100°C.\n\n"
            "Negative:  do/does + not + base verb\n"
            "  • He does not (doesn't) like coffee.\n\n"
            "Question:  Do/Does + subject + base verb\n"
            "  • Do you speak English?\n"
        ),
        "exercises": [
            {
                "question": "She ___ to school by bus every morning.",
                "options": ["go", "goes", "going", "went"],
                "answer": "goes",
                "explanation": "Third-person singular adds -es: she goes.",
            },
            {
                "question": "___ they play football on Sundays?",
                "options": ["Do", "Does", "Is", "Are"],
                "answer": "Do",
                "explanation": "Plural subject uses 'Do' for questions.",
            },
            {
                "question": "Water ___ at 100 degrees Celsius.",
                "options": ["boil", "boils", "is boiling", "boiled"],
                "answer": "boils",
                "explanation": "General truth → Present Simple, third-person -s.",
            },
        ],
    },
    {
        "id": "present_continuous",
        "title": "Present Continuous",
        "level": "A2",
        "summary": "Used for actions happening now or around now.",
        "body": (
            "Structure: am/is/are + verb-ing\n\n"
            "Examples:\n"
            "  • I am studying for my exam.\n"
            "  • They are watching a movie.\n"
            "  • She is not (isn't) sleeping.\n\n"
            "Spelling: drop silent e → make (making); double consonant → run (running).\n"
        ),
        "exercises": [
            {
                "question": "Look! The baby ___ now.",
                "options": ["sleeps", "is sleeping", "sleep", "sleeping"],
                "answer": "is sleeping",
                "explanation": "'now' signals Present Continuous: is sleeping.",
            },
            {
                "question": "I ___ a book at the moment.",
                "options": ["read", "am reading", "reads", "reading"],
                "answer": "am reading",
                "explanation": "'at the moment' → Present Continuous: am reading.",
            },
        ],
    },
    {
        "id": "past_simple",
        "title": "Past Simple",
        "level": "A2",
        "summary": "Used for completed actions in the past.",
        "body": (
            "Regular: add -ed (work → worked).\n"
            "Irregular: go → went, see → saw, buy → bought.\n\n"
            "Negative: did not (didn't) + base verb\n"
            "Question: Did + subject + base verb\n\n"
            "Time markers: yesterday, last week, in 2010, two days ago.\n"
        ),
        "exercises": [
            {
                "question": "We ___ to Paris last summer.",
                "options": ["go", "went", "gone", "going"],
                "answer": "went",
                "explanation": "'last summer' → Past Simple: went (irregular).",
            },
            {
                "question": "She didn't ___ the homework.",
                "options": ["did", "does", "do", "done"],
                "answer": "do",
                "explanation": "After didn't, use the base form: do.",
            },
            {
                "question": "___ you see the news yesterday?",
                "options": ["Do", "Did", "Was", "Were"],
                "answer": "Did",
                "explanation": "Past Simple question: Did + subject + base verb.",
            },
        ],
    },
    {
        "id": "conditionals",
        "title": "Conditionals (0, 1st, 2nd)",
        "level": "B1",
        "summary": "If-clauses for real and hypothetical situations.",
        "body": (
            "Zero (facts):     If + present, present\n"
            "  • If you heat ice, it melts.\n\n"
            "First (likely):    If + present, will + base\n"
            "  • If it rains, I will stay home.\n\n"
            "Second (unlikely): If + past, would + base\n"
            "  • If I had money, I would travel the world.\n"
        ),
        "exercises": [
            {
                "question": "If I ___ rich, I would buy a house.",
                "options": ["am", "was", "were", "be"],
                "answer": "were",
                "explanation": "Second conditional uses 'were' for all subjects.",
            },
            {
                "question": "If you heat water to 100°C, it ___.",
                "options": ["will boil", "boils", "boiled", "is boiling"],
                "answer": "boils",
                "explanation": "Zero conditional: If + present, present.",
            },
            {
                "question": "If she studies hard, she ___ the exam.",
                "options": ["passes", "will pass", "would pass", "passed"],
                "answer": "will pass",
                "explanation": "First conditional: If + present, will + base.",
            },
        ],
    },
    {
        "id": "passive_voice",
        "title": "Passive Voice",
        "level": "B2",
        "summary": "Focus on the action or recipient, not the doer.",
        "body": (
            "Structure: be + past participle\n\n"
            "  • Active:  They built the house in 1990.\n"
            "  • Passive: The house was built in 1990.\n\n"
            "Tense changes affect the 'be' verb:\n"
            "  Present: is/are done   | Past: was/were done\n"
            "  Future: will be done    | Perfect: has/have been done\n"
        ),
        "exercises": [
            {
                "question": "The book ___ by millions of readers.",
                "options": ["reads", "is read", "read", "reading"],
                "answer": "is read",
                "explanation": "Present passive: is + past participle (read).",
            },
            {
                "question": "The bridge ___ in 1985.",
                "options": ["built", "was built", "is built", "builds"],
                "answer": "was built",
                "explanation": "Past passive: was + past participle.",
            },
        ],
    },
    {
        "id": "articles",
        "title": "Articles (a / an / the)",
        "level": "A2",
        "summary": "Definite and indefinite articles.",
        "body": (
            "a   → before consonant sounds:  a book, a university\n"
            "an  → before vowel sounds:      an apple, an hour\n"
            "the → specific or unique:        the sun, the President\n\n"
            "No article for general plurals or uncountables:\n"
            "  • I like music.  (not 'the music' in general)\n"
        ),
        "exercises": [
            {
                "question": "I saw ___ elephant at the zoo.",
                "options": ["a", "an", "the", "—"],
                "answer": "an",
                "explanation": "'elephant' starts with a vowel sound → an.",
            },
            {
                "question": "Can you pass me ___ salt, please?",
                "options": ["a", "an", "the", "—"],
                "answer": "the",
                "explanation": "Specific salt on the table → the.",
            },
            {
                "question": "She is ___ honest person.",
                "options": ["a", "an", "the", "—"],
                "answer": "an",
                "explanation": "'honest' has a silent h (vowel sound) → an.",
            },
        ],
    },
]


class GrammarScreen(ctk.CTkFrame):
    """Grammar lesson viewer + MCQ exercises with error-journal logging."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.lessons = list(GRAMMAR_LESSONS)
        self.current_lesson_index = 0
        self.current_exercise_index = 0
        self.session_finalized = False
        self._session_id = None
        self.items_correct = 0
        self.items_studied = 0
        self._build_ui()
        self._start_session()

    # -- session -----------------------------------------------------------

    def _start_session(self):
        user_id = getattr(getattr(self.app, "user", None), "id", None)
        try:
            self._session_id = start_session(
                user_id=user_id, session_type=SessionType.GRAMMAR
            )
        except Exception:
            self._session_id = None

    def _finalize_session(self):
        if self.session_finalized:
            return
        xp = self.items_correct * 10 + max(0, self.items_studied - self.items_correct) * 2
        try:
            if self._session_id:
                end_session(
                    self._session_id,
                    xp_earned=xp,
                    items_studied=self.items_studied,
                    items_correct=self.items_correct,
                )
            else:
                user = getattr(self.app, "user", None)
                if user:
                    record_session(
                        user_id=user.id,
                        session_type=SessionType.GRAMMAR,
                        xp_earned=xp,
                        items_studied=self.items_studied,
                        items_correct=self.items_correct,
                    )
            self.session_finalized = True
        except Exception:
            pass

    # -- UI ----------------------------------------------------------------

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        ctk.CTkLabel(header, text="📖 Grammar", font=("Arial", 22, "bold")).pack(
            side="left"
        )

        # Lesson selector
        lesson_titles = [f"{l['level']} — {l['title']}" for l in self.lessons]
        self.lesson_menu = ctk.CTkComboBox(
            header,
            values=lesson_titles,
            command=self._on_lesson_select,
            width=280,
            state="readonly",
        )
        self.lesson_menu.set(lesson_titles[0])
        self.lesson_menu.pack(side="right", padx=8)

        # Body: scrollable
        self.body = ctk.CTkScrollableFrame(self)
        self.body.grid(row=1, column=0, sticky="nsew", padx=12, pady=(4, 10))
        self._show_lesson(0)

    def _on_lesson_select(self, selection):
        try:
            idx = [
                f"{l['level']} — {l['title']}" for l in self.lessons
            ].index(selection)
        except ValueError:
            idx = 0
        self._show_lesson(idx)

    def _show_lesson(self, index):
        self.current_lesson_index = index
        self.current_exercise_index = 0
        lesson = self.lessons[index]

        for w in self.body.winfo_children():
            w.destroy()

        # Lesson title + level badge
        title_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(
            title_frame,
            text=lesson["title"],
            font=("Arial", 18, "bold"),
        ).pack(side="left")
        ctk.CTkLabel(
            title_frame,
            text=f"  [{lesson['level']}]",
            font=("Arial", 12, "bold"),
            text_color="#4A90E2",
        ).pack(side="left", padx=8)

        ctk.CTkLabel(
            self.body,
            text=lesson["summary"],
            font=("Arial", 12, "italic"),
            text_color=("gray40", "gray70"),
            wraplength=740,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        # Lesson body — render line by line
        for line in lesson["body"].split("\n"):
            if not line.strip():
                ctk.CTkLabel(self.body, text="").pack()
                continue
            ctk.CTkLabel(
                self.body,
                text=line,
                font=("JetBrains Mono", 13),
                wraplength=740,
                justify="left",
            ).pack(anchor="w", pady=1)

        # Exercises section
        ctk.CTkLabel(
            self.body,
            text="─" * 40,
            text_color=("gray60", "gray40"),
        ).pack(pady=(12, 4))
        ctk.CTkLabel(
            self.body,
            text="Exercises",
            font=("Arial", 16, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        self._render_exercises(lesson["exercises"])

        # Finish button
        ctk.CTkButton(
            self.body,
            text="Finish Session",
            command=self._finalize_session,
        ).pack(pady=12)

    def _render_exercises(self, exercises):
        self._exercise_vars = []
        self._exercise_frames = []
        self._exercise_feedbacks = []

        for i, ex in enumerate(exercises):
            frame = ctk.CTkFrame(self.body)
            frame.pack(fill="x", pady=6)
            self._exercise_frames.append(frame)

            ctk.CTkLabel(
                frame,
                text=f"Q{i + 1}. {ex['question']}",
                font=("Arial", 14),
                wraplength=720,
                justify="left",
            ).pack(anchor="w", padx=10, pady=(8, 4))

            var = ctk.StringVar(value="")
            self._exercise_vars.append(var)
            for opt in ex["options"]:
                ctk.CTkRadioButton(
                    frame,
                    text=opt,
                    variable=var,
                    value=opt,
                ).pack(anchor="w", padx=30, pady=1)

            fb = ctk.CTkLabel(frame, text="", wraplength=720, justify="left")
            fb.pack(anchor="w", padx=10, pady=(2, 8))
            self._exercise_feedbacks.append(fb)

            ctk.CTkButton(
                frame,
                text="Check",
                width=80,
                command=lambda idx=i: self._check_exercise(idx),
            ).pack(anchor="w", padx=10, pady=(0, 8))

    def _check_exercise(self, idx):
        if idx >= len(self._exercise_vars):
            return
        lesson = self.lessons[self.current_lesson_index]
        ex = lesson["exercises"][idx]
        user_answer = self._exercise_vars[idx].get()
        fb = self._exercise_feedbacks[idx]

        if not user_answer:
            fb.configure(text="Please select an answer.", text_color="#F39C12")
            return

        self.items_studied += 1
        if user_answer == ex["answer"]:
            self.items_correct += 1
            fb.configure(
                text=f"✅ Correct! {ex['explanation']}",
                text_color="#27AE60",
            )
        else:
            fb.configure(
                text=f"❌ Incorrect. Answer: {ex['answer']}. {ex['explanation']}",
                text_color="#E74C3C",
            )
            self._log_error(lesson, ex, user_answer)

    def _log_error(self, lesson, exercise, user_answer):
        try:
            from data.database import get_session
            from data.models import ErrorJournalEntry

            user = getattr(self.app, "user", None)
            if not user:
                return
            db = get_session()
            try:
                entry = ErrorJournalEntry(
                    user_id=user.id,
                    session_id=self._session_id,
                    error_category=f"grammar:{lesson['id']}",
                    question_snapshot=exercise["question"],
                    user_answer=user_answer,
                    correct_answer=exercise["answer"],
                    content=exercise.get("explanation", ""),
                )
                db.add(entry)
                db.commit()
            finally:
                db.close()
        except Exception:
            pass
