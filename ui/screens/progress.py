"""Progress screen — heatmap, charts, error journal, weak-area review."""

from datetime import date, datetime, timedelta
from collections import defaultdict

import customtkinter as ctk

from data.database import get_session
from data.models import UserVocabularyProgress, StudySession, ErrorJournalEntry
from core.analytics import daily_activity_minutes, weekly_aggregates, current_streak
from ui.components.tooltip import Tooltip


def _color_for_minutes(m):
    if m <= 0:
        return "#eeeeee"
    if m < 10:
        return "#d6eadf"
    if m < 30:
        return "#a8e6a1"
    if m < 60:
        return "#66cc66"
    return "#2b8c2b"


class ProgressScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.build_ui()

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        ctk.CTkLabel(
            header, text="📊 Progress Overview", font=("Arial", 22, "bold")
        ).pack(side="left")

        # Tab selector
        self.tab_var = ctk.StringVar(value="Overview")
        tab_frame = ctk.CTkFrame(header, fg_color="transparent")
        tab_frame.pack(side="right", padx=8)
        for tab_name in ["Overview", "Charts", "Error Journal"]:
            ctk.CTkButton(
                tab_frame,
                text=tab_name,
                width=110,
                command=lambda t=tab_name: self._switch_tab(t),
                fg_color=("#4A90E2" if tab_name == "Overview" else "transparent"),
            ).pack(side="left", padx=2)

        # Body
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=1, column=0, sticky="nsew", padx=12, pady=(4, 10))
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_columnconfigure(0, weight=1)

        self._show_overview()

    def _switch_tab(self, tab_name):
        for w in self.body.winfo_children():
            w.destroy()
        if tab_name == "Overview":
            self._show_overview()
        elif tab_name == "Charts":
            self._show_charts()
        elif tab_name == "Error Journal":
            self._show_error_journal()

    # ── Overview tab ──────────────────────────────────────────────────

    def _show_overview(self):
        scroll = ctk.CTkScrollableFrame(self.body)
        scroll.grid(row=0, column=0, sticky="nsew")

        user = getattr(self.app, "user", None)
        db = get_session()
        try:
            progress_rows = (
                db.query(UserVocabularyProgress)
                .filter_by(user_id=getattr(user, "id", None))
                .all()
            )
            reviewed = sum(1 for r in progress_rows if r.times_seen > 0)
            mastered = sum(1 for r in progress_rows if r.times_correct >= 3)
            total = len(progress_rows)

            ctk.CTkLabel(
                scroll, text=f"Cards reviewed: {reviewed}", font=("Arial", 14)
            ).pack(anchor="w", pady=2)
            ctk.CTkLabel(
                scroll, text=f"Cards mastered: {mastered}", font=("Arial", 14)
            ).pack(anchor="w", pady=2)
            ctk.CTkLabel(
                scroll, text=f"Total cards tracked: {total}", font=("Arial", 14)
            ).pack(anchor="w", pady=2)
            if total:
                ratio = round(mastered / total * 100, 1)
                ctk.CTkLabel(
                    scroll,
                    text=f"Mastery: {ratio}%",
                    font=("Arial", 14, "bold"),
                    text_color="#27AE60",
                ).pack(anchor="w", pady=4)

            # Streak
            if user:
                streak = current_streak(user)
                ctk.CTkLabel(
                    scroll,
                    text=f"🔥 Current streak: {streak} days",
                    font=("Arial", 14, "bold"),
                ).pack(anchor="w", pady=(8, 2))

            # Activity heatmap (last 35 days = 5 weeks)
            ctk.CTkLabel(
                scroll,
                text="Activity Heatmap (last 5 weeks)",
                font=("Arial", 14, "bold"),
            ).pack(anchor="w", pady=(10, 4))

            if user:
                activity = daily_activity_minutes(user.id, days=35)
                grid_frame = ctk.CTkFrame(scroll, fg_color="transparent")
                grid_frame.pack(pady=4)
                start = date.today() - timedelta(days=34)
                tooltip = Tooltip(scroll)
                for week in range(5):
                    row_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
                    row_frame.pack()
                    for dow in range(7):
                        d = start + timedelta(days=week * 7 + dow)
                        iso = d.isoformat()
                        mins = activity.get(iso, 0)
                        color = _color_for_minutes(mins)
                        lbl = ctk.CTkLabel(
                            row_frame,
                            text=str(d.day),
                            width=36,
                            height=24,
                            fg_color=color,
                            corner_radius=4,
                        )
                        lbl.pack(side="left", padx=2, pady=2)
                        tooltip.register(lbl, f"{mins} min on {d.isoformat()}")

                # Legend
                legend = ctk.CTkFrame(scroll, fg_color="transparent")
                legend.pack(pady=6)
                for text, color in [
                    ("0m", "#eeeeee"),
                    ("<10m", "#d6eadf"),
                    ("10-29m", "#a8e6a1"),
                    ("30-59m", "#66cc66"),
                    ("60m+", "#2b8c2b"),
                ]:
                    item = ctk.CTkFrame(legend, fg_color="transparent")
                    item.pack(side="left", padx=6)
                    ctk.CTkLabel(
                        item, text="  ", fg_color=color, width=24, height=16, corner_radius=3
                    ).pack(side="left")
                    ctk.CTkLabel(item, text=text, font=("Arial", 10)).pack(side="left", padx=4)

                # Weekly aggregates
                weeks = weekly_aggregates(user.id, weeks=5)
                ctk.CTkLabel(
                    scroll,
                    text=f"Weekly minutes (oldest → newest): {weeks}",
                    font=("Arial", 12),
                    text_color=("gray40", "gray70"),
                ).pack(anchor="w", pady=6)
        finally:
            db.close()

    # ── Charts tab ────────────────────────────────────────────────────

    def _show_charts(self):
        scroll = ctk.CTkScrollableFrame(self.body)
        scroll.grid(row=0, column=0, sticky="nsew")

        user = getattr(self.app, "user", None)
        if not user:
            ctk.CTkLabel(scroll, text="No user data available.").pack(pady=20)
            return

        try:
            import matplotlib
            matplotlib.use("TkAgg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except Exception as exc:
            ctk.CTkLabel(
                scroll, text=f"Matplotlib unavailable: {exc}"
            ).pack(pady=20)
            return

        db = get_session()
        try:
            # ── Chart 1: Time per skill (bar chart, last 30 days) ──────
            thirty_ago = datetime.utcnow() - timedelta(days=30)
            sessions = (
                db.query(StudySession)
                .filter(StudySession.user_id == user.id)
                .filter(StudySession.started_at >= thirty_ago)
                .all()
            )

            skill_minutes = defaultdict(int)
            for s in sessions:
                if s.started_at and s.ended_at:
                    try:
                        delta = s.ended_at - s.started_at
                        mins = int(delta.total_seconds() / 60)
                    except Exception:
                        mins = 0
                    stype = s.session_type
                    label = stype.name if hasattr(stype, "name") else str(stype)
                    skill_minutes[label] += max(0, mins)

            fig1, ax1 = plt.subplots(figsize=(7, 3.5))
            if skill_minutes:
                labels = list(skill_minutes.keys())
                values = list(skill_minutes.values())
                colors = ["#4A90E2", "#27AE60", "#F39C12", "#E74C3C", "#9B59B6", "#1ABC9C", "#34495E"]
                ax1.bar(labels, values, color=colors[: len(labels)])
                ax1.set_ylabel("Minutes")
                ax1.set_title("Time Spent per Skill (Last 30 Days)")
            else:
                ax1.text(0.5, 0.5, "No session data yet", ha="center", va="center", transform=ax1.transAxes)
                ax1.set_title("Time Spent per Skill (Last 30 Days)")
            fig1.tight_layout()
            canvas1 = FigureCanvasTkAgg(fig1, master=scroll)
            canvas1.draw()
            canvas1.get_tk_widget().pack(pady=8)

            # ── Chart 2: Skill radar chart ──────────────────────────────
            progress_rows = (
                db.query(UserVocabularyProgress)
                .filter_by(user_id=user.id)
                .all()
            )
            # Build skill scores from SRS easiness per category
            skill_scores = defaultdict(list)
            # We don't have per-skill SRS, so use session accuracy per type
            for s in sessions:
                stype = s.session_type
                label = stype.name if hasattr(stype, "name") else str(stype)
                if s.items_studied and s.items_studied > 0:
                    acc = (s.items_correct or 0) / s.items_studied * 100
                    skill_scores[label].append(acc)

            radar_labels = ["VOCABULARY", "READING", "LISTENING", "WRITING", "SPEAKING", "GRAMMAR"]
            radar_values = []
            for label in radar_labels:
                vals = skill_scores.get(label, [])
                radar_values.append(sum(vals) / len(vals) if vals else 0)

            fig2, ax2 = plt.subplots(figsize=(5, 4), subplot_kw=dict(polar=True))
            angles = [n / float(len(radar_labels)) * 2 * 3.14159 for n in range(len(radar_labels))]
            angles += angles[:1]
            radar_values += radar_values[:1]
            ax2.plot(angles, radar_values, color="#4A90E2", linewidth=2)
            ax2.fill(angles, radar_values, color="#4A90E2", alpha=0.25)
            ax2.set_xticks(angles[:-1])
            ax2.set_xticklabels([l.capitalize() for l in radar_labels], fontsize=9)
            ax2.set_ylim(0, 100)
            ax2.set_title("Skill Balance (Accuracy %)", pad=20)
            fig2.tight_layout()
            canvas2 = FigureCanvasTkAgg(fig2, master=scroll)
            canvas2.draw()
            canvas2.get_tk_widget().pack(pady=8)

            # ── Chart 3: Band estimate over time (line chart) ───────────
            mock_sessions = (
                db.query(StudySession)
                .filter(StudySession.user_id == user.id)
                .filter(StudySession.session_type == "MOCK")
                .order_by(StudySession.started_at.asc())
                .all()
            )
            fig3, ax3 = plt.subplots(figsize=(7, 3))
            if mock_sessions:
                dates = []
                bands = []
                for s in mock_sessions:
                    if s.started_at and s.items_studied and s.items_studied > 0:
                        pct = (s.items_correct or 0) / s.items_studied * 100
                        # Convert to band estimate
                        if pct >= 90:
                            band = 6
                        elif pct >= 80:
                            band = 5
                        elif pct >= 65:
                            band = 4
                        elif pct >= 50:
                            band = 3
                        elif pct >= 35:
                            band = 2
                        else:
                            band = 1
                        dates.append(s.started_at.date())
                        bands.append(band)
                if dates:
                    ax3.plot(dates, bands, marker="o", color="#27AE60", linewidth=2)
                    ax3.set_ylabel("Band Estimate")
                    ax3.set_title("Band Estimate Over Time (Mock Tests)")
                    ax3.set_ylim(0, 7)
                    ax3.set_yticks([1, 2, 3, 4, 5, 6])
                    ax3.set_yticklabels(["A1", "A2", "B1", "B2", "C1", "C2"])
                else:
                    ax3.text(0.5, 0.5, "No mock test data yet", ha="center", va="center", transform=ax3.transAxes)
                    ax3.set_title("Band Estimate Over Time")
            else:
                ax3.text(0.5, 0.5, "No mock test data yet", ha="center", va="center", transform=ax3.transAxes)
                ax3.set_title("Band Estimate Over Time")
            fig3.tight_layout()
            canvas3 = FigureCanvasTkAgg(fig3, master=scroll)
            canvas3.draw()
            canvas3.get_tk_widget().pack(pady=8)

        finally:
            db.close()

    # ── Error Journal tab ─────────────────────────────────────────────

    def _show_error_journal(self):
        frame = ctk.CTkFrame(self.body)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # Header with filter + review button
        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        ctk.CTkLabel(
            top, text="Error Journal", font=("Arial", 16, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            top,
            text="🔄 Review Weak Areas",
            fg_color="#F39C12",
            command=self._review_weak_areas,
        ).pack(side="right", padx=4)

        # Error list
        scroll = ctk.CTkScrollableFrame(frame)
        scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 10))

        user = getattr(self.app, "user", None)
        if not user:
            ctk.CTkLabel(scroll, text="No user loaded.").pack(pady=20)
            return

        db = get_session()
        try:
            errors = (
                db.query(ErrorJournalEntry)
                .filter_by(user_id=user.id)
                .order_by(ErrorJournalEntry.created_at.desc())
                .limit(200)
                .all()
            )
            if not errors:
                ctk.CTkLabel(
                    scroll,
                    text="No errors logged yet. Complete exercises to build your error journal.",
                    font=("Arial", 13),
                    text_color=("gray40", "gray70"),
                ).pack(pady=20)
                return

            for err in errors:
                card = ctk.CTkFrame(scroll, corner_radius=8)
                card.pack(fill="x", padx=4, pady=3)
                ctk.CTkLabel(
                    card,
                    text=f"📂 {err.error_category or 'Unknown'}",
                    font=("Arial", 12, "bold"),
                    text_color="#E74C3C",
                ).pack(anchor="w", padx=10, pady=(6, 1))
                ctk.CTkLabel(
                    card,
                    text=f"Q: {err.question_snapshot or ''}",
                    font=("Arial", 11),
                    wraplength=600,
                    justify="left",
                ).pack(anchor="w", padx=10, pady=1)
                ctk.CTkLabel(
                    card,
                    text=f"Your answer: {err.user_answer or ''}  →  Correct: {err.correct_answer or ''}",
                    font=("Arial", 11),
                    text_color=("gray40", "gray70"),
                    wraplength=600,
                    justify="left",
                ).pack(anchor="w", padx=10, pady=(1, 6))
        finally:
            db.close()

    def _review_weak_areas(self):
        """Navigate to vocabulary or grammar for weak-area review."""
        user = getattr(self.app, "user", None)
        if not user:
            return
        db = get_session()
        try:
            errors = (
                db.query(ErrorJournalEntry)
                .filter_by(user_id=user.id)
                .order_by(ErrorJournalEntry.created_at.desc())
                .limit(50)
                .all()
            )
            if not errors:
                return
            # Find most common error category
            cat_counts = defaultdict(int)
            for e in errors:
                cat_counts[e.error_category or ""] += 1
            top_cat = max(cat_counts, key=cat_counts.get) if cat_counts else ""
            if top_cat.startswith("grammar"):
                self.app.navigate("grammar")
            else:
                self.app.navigate("vocabulary")
        finally:
            db.close()