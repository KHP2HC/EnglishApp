"""Dashboard — home screen with streak, daily plan, quick stats, word of the day."""

import random
from datetime import datetime, date, timedelta

import customtkinter as ctk

from core.analytics import daily_activity_minutes
from core.study_planner import StudyPlanner
from data.database import get_session
from data.models import StudyPlan, VocabularyCard, UserVocabularyProgress, StudySession
from ui.components.progress_ring import ProgressRing
from ui.components.streak_banner import StreakBanner


# Pool of "word of the day" entries (fallback when DB is empty)
_WORD_POOL = [
    ("serendipity", "/ˌsɛrənˈdɪpɪti/", "an unexpected yet happy discovery", "Finding that old photo was pure serendipity."),
    ("ephemeral", "/ɪˈfɛmərəl/", "lasting for a very short time", "Fame on social media can be ephemeral."),
    ("ubiquitous", "/juːˈbɪkwɪtəs/", "present everywhere", "Smartphones have become ubiquitous in modern life."),
    ("pragmatic", "/præɡˈmætɪk/", "dealing with things practically", "We need a pragmatic approach to solve this."),
    ("resilient", "/rɪˈzɪliənt/", "able to recover quickly from difficulties", "She is resilient and never gives up."),
    ("meticulous", "/məˈtɪkjələs/", "showing great attention to detail", "He is meticulous about his research."),
    ("eloquent", "/ˈɛləkwənt/", "fluent and persuasive in speaking or writing", "Her eloquent speech moved the audience."),
    ("diligent", "/ˈdɪlɪdʒənt/", "showing care and effort in work", "He is a diligent student who studies every day."),
]


def _level_info(xp):
    """Return (level_name, level_num, xp_into_level, xp_for_next)."""
    levels = [
        (0, "A1 Newcomer"),
        (500, "A2 Explorer"),
        (1500, "B1 Builder"),
        (3000, "B2 Achiever"),
        (5000, "C1 Expert"),
        (8000, "C2 Master"),
        (12000, "Exam Ready 🎓"),
    ]
    xp = xp or 0
    for i in range(len(levels) - 1, -1, -1):
        if xp >= levels[i][0]:
            name = levels[i][1]
            num = i + 1
            into = xp - levels[i][0]
            next_thresh = (levels[i + 1][0] - levels[i][0]) if i + 1 < len(levels) else 1000
            return name, num, into, next_thresh
    return levels[0][1], 1, 0, 500


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.user = getattr(self.app, "user", None)
        self._saved_plan = None
        self.build_ui()

    def _exam_label(self):
        exam = getattr(self.user, "target_exam", None)
        if exam is None:
            return "Not set"
        if hasattr(exam, "name"):
            return exam.name
        return str(exam)

    def _days_to_exam(self):
        exam_date = getattr(self.user, "exam_date", None)
        if not exam_date:
            return None
        try:
            if isinstance(exam_date, str):
                exam_date = datetime.fromisoformat(exam_date).date()
            return (exam_date - date.today()).days
        except Exception:
            return None

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # ── Header ──────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))

        name = getattr(self.user, "name", "Learner")
        avatar = getattr(self.user, "avatar_emoji", "😊")
        ctk.CTkLabel(
            header,
            text=f"{avatar}  Welcome back, {name}!",
            font=("Arial", 22, "bold"),
        ).pack(side="left")

        # Countdown badge
        days_left = self._days_to_exam()
        if days_left is not None:
            if days_left < 0:
                badge_text = "⚠️ Exam date passed"
                badge_color = "#E74C3C"
            elif days_left < 30:
                badge_text = f"⏰ {days_left} days to exam!"
                badge_color = "#F39C12"
            else:
                badge_text = f"📅 {days_left} days to exam"
                badge_color = "#4A90E2"
        else:
            badge_text = "📅 Set your exam date"
            badge_color = "#888888"

        ctk.CTkLabel(
            header,
            text=badge_text,
            font=("Arial", 13, "bold"),
            text_color="white",
            fg_color=badge_color,
            corner_radius=12,
            padx=12,
            pady=4,
        ).pack(side="right", padx=8)

        ctk.CTkLabel(
            header,
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font=("Arial", 12),
            text_color=("gray40", "gray70"),
        ).pack(side="right", padx=8)

        # ── Streak banner ───────────────────────────────────────────────
        streak_frame = ctk.CTkFrame(self, fg_color="transparent")
        streak_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=4)

        streak_days = getattr(self.user, "streak_days", 0) or 0
        week_activity = {}
        if self.user:
            try:
                week_activity = daily_activity_minutes(self.user.id, days=7)
            except Exception:
                pass

        self.streak_banner = StreakBanner(
            streak_frame,
            streak_days=streak_days,
            week_activity=week_activity,
        )
        self.streak_banner.pack(fill="x")

        # ── Quick stats row ─────────────────────────────────────────────
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=4)

        # Gather stats
        words_learned = 0
        xp_this_week = 0
        if self.user:
            db = get_session()
            try:
                words_learned = (
                    db.query(UserVocabularyProgress)
                    .filter_by(user_id=self.user.id)
                    .filter(UserVocabularyProgress.times_seen > 0)
                    .count()
                )
                week_ago = datetime.utcnow() - timedelta(days=7)
                sessions = (
                    db.query(StudySession)
                    .filter(StudySession.user_id == self.user.id)
                    .filter(StudySession.started_at >= week_ago)
                    .all()
                )
                xp_this_week = sum(s.xp_earned or 0 for s in sessions)
            except Exception:
                pass
            finally:
                db.close()

        current_band = getattr(self.user, "current_band", None) or "—"

        stats = [
            ("📚 Words Learned", str(words_learned)),
            ("🎯 Current Band", str(current_band)),
            ("⚡ XP This Week", str(xp_this_week)),
        ]
        for label_text, value_text in stats:
            card = ctk.CTkFrame(stats_frame, corner_radius=12)
            card.pack(side="left", padx=6, expand=True, fill="both")
            ctk.CTkLabel(
                card,
                text=label_text,
                font=("Arial", 11),
                text_color=("gray40", "gray70"),
            ).pack(pady=(8, 2))
            ctk.CTkLabel(
                card,
                text=value_text,
                font=("Arial", 20, "bold"),
            ).pack(pady=(0, 8))

        # ── Main content: daily goal + plan ─────────────────────────────
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=3, column=0, sticky="nsew", padx=16, pady=(4, 8))
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        # Left: daily goal ring
        goal_frame = ctk.CTkFrame(content, corner_radius=12)
        goal_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        ctk.CTkLabel(
            goal_frame,
            text="Daily Goal",
            font=("Arial", 14, "bold"),
        ).pack(pady=(12, 4))

        # Calculate today's minutes studied
        today_minutes = 0
        if self.user:
            try:
                activity = daily_activity_minutes(self.user.id, days=1)
                today_minutes = sum(activity.values())
            except Exception:
                pass

        daily_target = 60
        free = getattr(self.user, "daily_free_minutes", None)
        if isinstance(free, dict):
            today_key = date.today().strftime("%a").lower()
            daily_target = free.get(today_key, 60)

        ring = ProgressRing(goal_frame, progress=today_minutes, total=max(daily_target, 1), size=120)
        ring.pack(pady=8)

        ctk.CTkLabel(
            goal_frame,
            text=f"{today_minutes} / {daily_target} min",
            font=("Arial", 13),
        ).pack(pady=(0, 4))
        ctk.CTkLabel(
            goal_frame,
            text=f"Level: {_level_info(getattr(self.user, 'total_xp', 0))[0]}",
            font=("Arial", 11),
            text_color=("gray40", "gray70"),
        ).pack(pady=(0, 12))

        # Right: today's plan
        plan_frame = ctk.CTkFrame(content, corner_radius=12)
        plan_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        plan_frame.grid_rowconfigure(1, weight=1)
        plan_frame.grid_columnconfigure(0, weight=1)

        plan_header = ctk.CTkFrame(plan_frame, fg_color="transparent")
        plan_header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        ctk.CTkLabel(
            plan_header,
            text="📋 Today's Plan",
            font=("Arial", 14, "bold"),
        ).pack(side="left")
        ctk.CTkButton(
            plan_header,
            text="Open Planner",
            width=110,
            command=lambda: self.app.navigate("planner"),
        ).pack(side="right")

        self.plan_cards_frame = ctk.CTkScrollableFrame(plan_frame)
        self.plan_cards_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        self._load_plan_summary()
        self._render_plan_cards()

        # ── Word of the Day ─────────────────────────────────────────────
        wotd_frame = ctk.CTkFrame(self, corner_radius=12)
        wotd_frame.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 12))

        word, phonetic, meaning, example = self._word_of_the_day()
        ctk.CTkLabel(
            wotd_frame,
            text="📖 Word of the Day",
            font=("Arial", 13, "bold"),
            text_color=("#4A90E2", "#2E6ED4"),
        ).pack(anchor="w", padx=16, pady=(10, 2))
        ctk.CTkLabel(
            wotd_frame,
            text=word,
            font=("Arial", 20, "bold"),
        ).pack(anchor="w", padx=16, pady=2)
        ctk.CTkLabel(
            wotd_frame,
            text=f"{phonetic}  —  {meaning}",
            font=("Arial", 13),
            wraplength=800,
            justify="left",
        ).pack(anchor="w", padx=16, pady=2)
        ctk.CTkLabel(
            wotd_frame,
            text=f'"{example}"',
            font=("Arial", 12, "italic"),
            text_color=("gray40", "gray70"),
            wraplength=800,
            justify="left",
        ).pack(anchor="w", padx=16, pady=(2, 10))

    def _load_plan_summary(self):
        if not self.user:
            return
        db = get_session()
        try:
            plan_record = (
                db.query(StudyPlan)
                .filter_by(user_id=self.user.id)
                .order_by(StudyPlan.created_at.desc())
                .first()
            )
            if plan_record and plan_record.plan:
                self._saved_plan = plan_record.plan
            else:
                try:
                    planner = StudyPlanner(self.user)
                    self._saved_plan = planner.generate_plan()
                except Exception:
                    self._saved_plan = None
        finally:
            db.close()

    def _render_plan_cards(self):
        for child in self.plan_cards_frame.winfo_children():
            child.destroy()

        if getattr(self, "_saved_plan", None):
            first_week = next(iter(self._saved_plan.values()), [])
            tasks = []
            for day in first_week[:3]:
                for task in day.get("tasks", [])[:2]:
                    tasks.append(task)
        else:
            tasks = [
                {"type": "vocabulary", "minutes": 20, "detail": "Review 15 cards due today"},
                {"type": "listening", "minutes": 15, "detail": "2 short clips with notes"},
                {"type": "grammar", "minutes": 25, "detail": "Conditionals + error review"},
            ]

        icon_map = {
            "vocabulary": "🧠",
            "grammar": "📐",
            "listening": "👂",
            "reading": "📖",
            "writing": "✍️",
            "speaking": "🗣️",
            "mock": "🧪",
        }

        for idx, task in enumerate(tasks[:5]):
            ttype = task.get("type", "task")
            icon = icon_map.get(ttype, "📝")
            card = ctk.CTkFrame(self.plan_cards_frame, corner_radius=10)
            card.pack(fill="x", padx=4, pady=3)
            ctk.CTkLabel(
                card,
                text=f"{icon} {ttype.capitalize()}",
                font=("Arial", 13, "bold"),
            ).pack(anchor="w", padx=10, pady=(6, 1))
            ctk.CTkLabel(
                card,
                text=f"{task.get('minutes', 0)} min • {task.get('detail', 'Study session')}",
                font=("Arial", 11),
                text_color=("gray40", "gray70"),
                wraplength=500,
                justify="left",
            ).pack(anchor="w", padx=10, pady=(0, 6))

    def _word_of_the_day(self):
        """Pick a word of the day — from DB if available, else from pool."""
        try:
            db = get_session()
            try:
                count = db.query(VocabularyCard).count()
                if count > 0:
                    offset = random.randint(0, max(0, count - 1))
                    card = db.query(VocabularyCard).offset(offset).first()
                    if card:
                        return (
                            card.word,
                            card.phonetic or "",
                            card.meaning_en or "",
                            card.example_sentence or "",
                        )
            finally:
                db.close()
        except Exception:
            pass
        return random.choice(_WORD_POOL)
