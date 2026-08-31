"""Daily streak banner with weekly heatmap row.

Shows fire emoji + streak count and a 7-day mini-heatmap indicating
which days the user was active.
"""

from datetime import date, timedelta

import customtkinter as ctk


def _heat_color(active, intensity=1):
    """Return a color for a day cell based on activity."""
    if not active:
        return ("#e0e0e0", "#2a2a2a")
    # intensity 1-3 → progressively darker green
    colors = [
        ("#d6eadf", "#1a3a1a"),
        ("#a8e6a1", "#2b8c2b"),
        ("#66cc66", "#2b8c2b"),
    ]
    idx = min(intensity - 1, len(colors) - 1)
    return colors[idx]


class StreakBanner(ctk.CTkFrame):
    """Streak display with 7-day heatmap row."""

    def __init__(self, master, streak_days=0, week_activity=None, **kwargs):
        super().__init__(master, corner_radius=12, **kwargs)
        self.streak_days = streak_days
        self.week_activity = week_activity or {}  # {iso_date: minutes}

        self._build()

    def _build(self):
        # Streak label
        streak_text = f"🔥 {self.streak_days} day streak!"
        ctk.CTkLabel(
            self,
            text=streak_text,
            font=("Arial", 18, "bold"),
        ).pack(side="left", padx=16, pady=10)

        # Weekly heatmap
        heat_frame = ctk.CTkFrame(self, fg_color="transparent")
        heat_frame.pack(side="right", padx=16, pady=8)

        today = date.today()
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            iso = d.isoformat()
            minutes = self.week_activity.get(iso, 0)
            active = minutes > 0
            intensity = 1
            if minutes >= 30:
                intensity = 2
            if minutes >= 60:
                intensity = 3
            color = _heat_color(active, intensity)

            cell = ctk.CTkFrame(heat_frame, width=28, height=28, corner_radius=6, fg_color=color[0])
            cell.pack(side="left", padx=2)
            day_label = d.strftime("%a")[0]  # M, T, W...
            ctk.CTkLabel(
                cell,
                text=day_label,
                font=("Arial", 9),
                text_color=color[1],
            ).pack(expand=True)

    def update_streak(self, streak_days, week_activity=None):
        self.streak_days = streak_days
        if week_activity is not None:
            self.week_activity = week_activity
        for w in self.winfo_children():
            w.destroy()
        self._build()
