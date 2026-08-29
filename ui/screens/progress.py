import customtkinter as ctk
from data.database import get_session
from data.models import UserVocabularyProgress
from core.analytics import daily_activity_minutes
from datetime import date, datetime, timedelta
from ui.components.tooltip import Tooltip
from core.analytics import weekly_aggregates, current_streak


def _color_for_minutes(m):
    # thresholds: 0, 1-9, 10-29, 30-59, 60+
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
        user = getattr(self.app, 'user', None)
        db = get_session()
        try:
            progress_rows = db.query(UserVocabularyProgress).filter_by(user_id=getattr(user, 'id', None)).all()
            reviewed = sum(1 for row in progress_rows if row.times_seen > 0)
            mastered = sum(1 for row in progress_rows if row.times_correct >= 3)
            total = len(progress_rows)
            ctk.CTkLabel(self, text=f"Progress Overview", font=("Arial", 20)).pack(pady=10)
            ctk.CTkLabel(self, text=f"Cards reviewed: {reviewed}").pack()
            ctk.CTkLabel(self, text=f"Cards mastered: {mastered}").pack()
            ctk.CTkLabel(self, text=f"Total cards: {total}").pack()
            if total:
                ratio = round(mastered / total * 100, 1)
                ctk.CTkLabel(self, text=f"Mastery: {ratio}%").pack(pady=8)
            # Activity heatmap for last 35 days (5 weeks)
            if user:
                # show weekly aggregates and streak
                weeks = weekly_aggregates(user.id, weeks=5)
                ctk.CTkLabel(self, text=f"Weekly minutes (oldest → newest): {weeks}").pack(pady=6)
                streak = current_streak(user)
                ctk.CTkLabel(self, text=f"Current streak: {streak} days").pack()
                ctk.CTkLabel(self, text='').pack()
                activity = daily_activity_minutes(user.id, days=35)
                # grid: 5 rows (weeks) x 7 cols (Mon-Sun)
                grid_frame = ctk.CTkFrame(self)
                grid_frame.pack(pady=12)
                start = date.today() - timedelta(days=34)
                tooltip = Tooltip(self)
                for week in range(5):
                    row_frame = ctk.CTkFrame(grid_frame)
                    row_frame.pack()
                    for dow in range(7):
                        d = (start + timedelta(days=week * 7 + dow))
                        iso = d.isoformat()
                        mins = activity.get(iso, 0)
                        color = _color_for_minutes(mins)
                        lbl = ctk.CTkLabel(row_frame, text=str(d.day), width=36, height=24, fg_color=color)
                        lbl.pack(side='left', padx=2, pady=2)
                        tooltip.register(lbl, f"{mins} min on {d.isoformat()}")
                ctk.CTkLabel(self, text='Heatmap: darker = more minutes').pack(pady=6)
                # legend
                legend = ctk.CTkFrame(self)
                legend.pack(pady=6)
                for text, color in [('<10m', '#d6eadf'), ('10-29m', '#a8e6a1'), ('30-59m', '#66cc66'), ('60m+', '#2b8c2b')]:
                    item = ctk.CTkFrame(legend)
                    item.pack(side='left', padx=6)
                    ctk.CTkLabel(item, text='  ', fg_color=color, width=24, height=16).pack(side='left')
                    ctk.CTkLabel(item, text=text).pack(side='left', padx=4)
        finally:
            db.close()