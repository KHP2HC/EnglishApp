import customtkinter as ctk
import random

from core.content_fetcher import ContentFetcher
from core.reading_test import (
    TFNG_OPTIONS,
    YNNG_OPTIONS,
    grade,
    iter_questions,
    load_test,
    load_tests,
)
from core.session_manager import end_session, record_session, start_session
from data.models import SessionType
from ui.components.timer_widget import TimerWidget


class ReadingScreen(ctk.CTkFrame):
    """IELTS-style Academic Reading test: multiple passages and question types."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.content_fetcher = ContentFetcher()
        self._session_id = None
        self.session_finalized = False

        # Backward-compatible attributes used by _load_article / older tests.
        self.passage = ""
        self.question = ""
        self.options = []
        self.selected = ctk.StringVar(value="")
        self.feedback_label = None

        self.test = load_test()
        # load full test list for selector compatibility
        try:
            self.tests = load_tests() or [self.test]
        except Exception:
            self.tests = [self.test]
        # choose a random test on load to provide variety
        try:
            self.test_index = random.randrange(len(self.tests))
        except Exception:
            self.test_index = 0
        self.passages = self.test.get("passages", [])
        self.current_passage = 0
        self.answers = {q["id"]: ctk.StringVar(value="") for q in iter_questions(self.test)}
        self.timer = None
        self.nav_buttons = []

        self._build_ui()
        self._start_session()

    def _select_test(self, selection):
        """Handler for test selector dropdown. Rebuilds the UI for the chosen test."""
        try:
            # selection is like "Test N" — extract N
            idx = int(str(selection).split()[1]) - 1
        except Exception:
            idx = 0
        if idx < 0 or idx >= len(self.tests):
            idx = 0
        self.test_index = idx
        self.test = self.tests[idx]
        # rebuild passages / answers state
        self.passages = self.test.get("passages", [])
        self.answers = {q["id"]: ctk.StringVar(value="") for q in iter_questions(self.test)}
        # destroy and rebuild UI
        for widget in self.winfo_children():
            widget.destroy()
        try:
            if getattr(self, 'timer', None):
                self.timer.stop()
        except Exception:
            pass
        self._build_ui()
        self._start_session()

    # ------------------------------------------------------------------
    # Backward-compatible live-article helper (kept for existing tests).
    # ------------------------------------------------------------------
    def _load_article(self):
        article = self.content_fetcher.fetch_articles(difficulty="B1")[0]
        self.passage = article.get("body", "")
        self.question = f"What is the main idea of the article '{article.get('title', 'the passage')}'?"
        self.options = [
            "The article highlights an example of ongoing practice and progress.",
            "The article mainly discusses weather changes.",
            "The article is a story about travel.",
            "The article describes a cooking recipe.",
        ]
        self.correct_option = self.options[0]
        if getattr(self, "selected", None) is not None:
            self.selected.set(self.options[0])
        return article

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        header.grid_columnconfigure(2, weight=1)
        ctk.CTkLabel(header, text=self.test.get("title", "IELTS Reading Test"), font=("Arial", 22, "bold")).grid(row=0, column=0, sticky="w")
        # Test selector dropdown
        test_names = [f"Test {i + 1}" for i in range(len(self.tests))]
        self.test_selector = ctk.CTkComboBox(
            header,
            values=test_names,
            command=self._select_test,
            width=120,
            state="readonly",
        )
        self.test_selector.set(f"Test {self.test_index + 1}")
        self.test_selector.grid(row=0, column=1, sticky="w", padx=8)
        self.timer = TimerWidget(header, minutes=self.test.get("time_minutes", 60), on_finish=self._on_time_up, fg_color="transparent")
        self.timer.grid(row=0, column=2, sticky="e", padx=8)
        self.submit_btn = ctk.CTkButton(header, text="Submit Test", command=self.submit_test, width=130)
        self.submit_btn.grid(row=0, column=3, sticky="e")

        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.grid(row=1, column=0, sticky="ew", padx=12, pady=4)
        self.nav_buttons = []
        self._default_btn_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        for idx, passage in enumerate(self.passages):
            btn = ctk.CTkButton(
                nav,
                text=f"Passage {passage.get('number', idx + 1)}",
                width=120,
                command=lambda i=idx: self._show_passage(i),
            )
            btn.pack(side="left", padx=4)
            self.nav_buttons.append(btn)
        self.progress_label = ctk.CTkLabel(nav, text="", font=("Arial", 12))
        self.progress_label.pack(side="right", padx=8)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=2, column=0, sticky="nsew", padx=12, pady=(4, 10))
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)

        self.passage_frame = ctk.CTkScrollableFrame(body, label_text="Reading Passage")
        self.passage_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.questions_frame = ctk.CTkScrollableFrame(body, label_text="Questions")
        self.questions_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        if self.timer is not None:
            try:
                self.timer.start()
            except Exception:
                pass
        self._show_passage(0)

    def _start_session(self):
        user_id = getattr(getattr(self.app, "user", None), "id", None)
        try:
            self._session_id = start_session(user_id=user_id, session_type=SessionType.READING)
        except Exception:
            self._session_id = None

    def _show_passage(self, idx):
        if not self.passages:
            return
        self.current_passage = idx
        passage = self.passages[idx]

        for i, btn in enumerate(self.nav_buttons):
            btn.configure(fg_color=("gray75", "gray25") if i == idx else self._default_btn_color)

        for widget in self.passage_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(
            self.passage_frame,
            text=f"Passage {passage.get('number', idx + 1)}: {passage.get('title', '')}",
            font=("Arial", 16, "bold"),
            wraplength=520,
            justify="left",
        ).pack(anchor="w", pady=(2, 6))
        if passage.get("instructions"):
            ctk.CTkLabel(self.passage_frame, text=passage["instructions"], font=("Arial", 11, "italic"), wraplength=520, justify="left", text_color=("gray40", "gray70")).pack(anchor="w", pady=(0, 8))
        for para in passage.get("text", "").split("\n\n"):
            ctk.CTkLabel(self.passage_frame, text=para.strip(), wraplength=520, justify="left").pack(anchor="w", pady=6)

        for widget in self.questions_frame.winfo_children():
            widget.destroy()
        for question in passage.get("questions", []):
            self._render_question(question)
        self._update_progress()

    def _render_question(self, question):
        qid = question["id"]
        number = question.get("number", "")
        qtype = question.get("type", "mcq")
        var = self.answers[qid]

        block = ctk.CTkFrame(self.questions_frame)
        block.pack(fill="x", pady=6, padx=2)
        ctk.CTkLabel(block, text=f"{number}. {question.get('text', '')}", wraplength=360, justify="left", font=("Arial", 13)).pack(anchor="w", padx=8, pady=(6, 4))

        if qtype == "completion":
            entry = ctk.CTkEntry(block, textvariable=var, placeholder_text="Type your answer")
            entry.pack(anchor="w", fill="x", padx=8, pady=(0, 8))
            entry.bind("<KeyRelease>", lambda _e: self._update_progress())
            limit = question.get("max_words")
            if limit:
                ctk.CTkLabel(block, text=f"Write no more than {limit} word{'s' if limit > 1 else ''}.", font=("Arial", 10, "italic"), text_color=("gray40", "gray70")).pack(anchor="w", padx=8, pady=(0, 6))
            return

        if qtype == "tfng":
            options = TFNG_OPTIONS
        elif qtype == "ynng":
            options = YNNG_OPTIONS
        else:
            options = question.get("options", [])

        for option in options:
            ctk.CTkRadioButton(block, text=option, variable=var, value=option, command=self._update_progress).pack(anchor="w", padx=16, pady=2)

    def _update_progress(self):
        answered = sum(1 for var in self.answers.values() if var.get().strip())
        total = len(self.answers)
        if getattr(self, "progress_label", None) is not None:
            self.progress_label.configure(text=f"Answered: {answered}/{total}")

    # ------------------------------------------------------------------
    # Grading and results
    # ------------------------------------------------------------------
    def _on_time_up(self):
        self.submit_test()

    def submit_test(self):
        if self.session_finalized:
            return
        if self.timer is not None:
            try:
                self.timer.stop()
            except Exception:
                pass
        answers = {qid: var.get() for qid, var in self.answers.items()}
        result = grade(self.test, answers)
        self._save_session(result)
        self._show_results(result)
        return result

    def _show_results(self, result):
        for widget in self.winfo_children():
            widget.destroy()
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        ctk.CTkLabel(header, text="Test Results", font=("Arial", 22, "bold")).pack(side="left")
        ctk.CTkButton(header, text="Retake Test", width=120, command=self._retake).pack(side="right")

        summary = ctk.CTkFrame(self)
        summary.grid(row=1, column=0, sticky="ew", padx=12, pady=6)
        ctk.CTkLabel(summary, text=f"Score: {result['raw']} / {result['total']}", font=("Arial", 16)).pack(side="left", padx=16, pady=10)
        ctk.CTkLabel(summary, text=f"Estimated Band: {result['band']:.1f}", font=("Arial", 16, "bold")).pack(side="left", padx=16, pady=10)

        review = ctk.CTkScrollableFrame(self, label_text="Answer Review")
        review.grid(row=2, column=0, sticky="nsew", padx=12, pady=(4, 10))
        for item in result["review"]:
            row = ctk.CTkFrame(review)
            row.pack(fill="x", pady=4, padx=2)
            mark = "\u2713" if item["is_correct"] else "\u2717"
            colour = ("green", "#2ecc71") if item["is_correct"] else ("red", "#e74c3c")
            ctk.CTkLabel(row, text=f"{mark} {item['number']}. {item['text']}", wraplength=760, justify="left", text_color=colour, font=("Arial", 13)).pack(anchor="w", padx=8, pady=(6, 2))
            correct_answer = item["correct_answer"]
            if isinstance(correct_answer, list):
                correct_answer = " / ".join(correct_answer)
            user_answer = item["user_answer"] or "(no answer)"
            ctk.CTkLabel(row, text=f"Your answer: {user_answer}    Correct: {correct_answer}", wraplength=760, justify="left", font=("Arial", 12)).pack(anchor="w", padx=8, pady=2)
            if item.get("explanation"):
                ctk.CTkLabel(row, text=item["explanation"], wraplength=760, justify="left", font=("Arial", 11, "italic"), text_color=("gray40", "gray70")).pack(anchor="w", padx=8, pady=(0, 6))

    def _retake(self):
        for var in self.answers.values():
            var.set("")
        self.session_finalized = False
        for widget in self.winfo_children():
            widget.destroy()
        self.current_passage = 0
        self._build_ui()
        self._start_session()

    def _save_session(self, result):
        if self.session_finalized:
            return
        user = getattr(self.app, "user", None)
        if not user:
            self.session_finalized = True
            return
        raw = result["raw"]
        total = result["total"]
        xp = raw * 5
        try:
            if getattr(self, "_session_id", None):
                end_session(self._session_id, xp_earned=xp, items_studied=total, items_correct=raw)
            else:
                user_id = getattr(self.app.user, "id", None)
                record_session(user_id=user_id, session_type=SessionType.READING, xp_earned=xp, items_studied=total, items_correct=raw)
            self.session_finalized = True
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Legacy single-question API (kept so older callers/tests still work).
    # ------------------------------------------------------------------
    def submit_answer(self):
        correct = getattr(self, "correct_option", self.options[0] if self.options else "")
        answer = self.selected.get()
        message = "Correct!" if answer == correct else f"Not quite. The best answer is: {correct}."
        if getattr(self, "feedback_label", None) is not None:
            self.feedback_label.configure(text=message)
        return message