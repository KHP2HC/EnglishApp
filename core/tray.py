"""System tray integration for Windows.

Provides:
- Minimize to system tray
- Daily streak reminder notification at user's preferred time
- Word of the Day notification at 8:00 AM daily
- Restore from tray on click
"""

import os
import threading
from datetime import datetime, date

try:
    import pystray
    from PIL import Image, ImageDraw
    _HAS_TRAY = True
except Exception:
    _HAS_TRAY = False

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    _HAS_SCHEDULER = True
except Exception:
    _HAS_SCHEDULER = False


def _create_icon_image():
    """Create a simple icon for the system tray."""
    try:
        img = Image.new("RGB", (64, 64), color=(74, 144, 226))
        draw = ImageDraw.Draw(img)
        draw.text((18, 18), "E", fill="white")
        return img
    except Exception:
        return None


class TrayIntegration:
    """Manages system tray icon, notifications, and scheduled reminders."""

    def __init__(self, app, user=None):
        self.app = app
        self.user = user
        self.icon = None
        self.scheduler = None

    def setup(self):
        """Initialize tray icon and scheduler. Call after app is ready."""
        if not _HAS_TRAY:
            return False

        image = _create_icon_image()
        if image is None:
            return False

        menu = pystray.Menu(
            pystray.MenuItem("Show Window", self._on_show, default=True),
            pystray.MenuItem("Word of the Day", self._on_word_notification),
            pystray.MenuItem("Exit", self._on_exit),
        )

        self.icon = pystray.Icon(
            "EnglishCoachPro",
            image,
            "EnglishCoach Pro",
            menu,
        )

        # Start scheduler for daily reminders
        if _HAS_SCHEDULER:
            self._setup_scheduler()

        # Run tray icon in a separate thread
        threading.Thread(target=self.icon.run, daemon=True).start()
        return True

    def _setup_scheduler(self):
        """Set up APScheduler for daily reminders."""
        if not _HAS_SCHEDULER:
            return
        self.scheduler = BackgroundScheduler()

        # Word of the Day at 8:00 AM
        self.scheduler.add_job(
            self._word_of_day_job,
            trigger="cron",
            hour=8,
            minute=0,
            id="word_of_day",
            replace_existing=True,
        )

        # Streak reminder at user's preferred time
        preferred_time = getattr(self.user, "preferred_session_time", "MORNING")
        hour = 9  # default morning
        if preferred_time == "AFTERNOON":
            hour = 14
        elif preferred_time == "EVENING":
            hour = 19

        self.scheduler.add_job(
            self._streak_reminder_job,
            trigger="cron",
            hour=hour,
            minute=0,
            id="streak_reminder",
            replace_existing=True,
        )

        self.scheduler.start()

    def _word_of_day_job(self):
        """Push word of the day notification."""
        try:
            word = self._get_word_of_day()
            self._notify(f"📖 Word of the Day: {word}")
        except Exception:
            pass

    def _streak_reminder_job(self):
        """Push streak reminder notification."""
        try:
            streak = getattr(self.user, "streak_days", 0) or 0
            self._notify(f"🔥 Your streak is at risk! Study for 15 minutes today. (Current: {streak} days)")
        except Exception:
            pass

    def _get_word_of_day(self):
        """Fetch a random word from the database."""
        try:
            from data.database import get_session
            from data.models import VocabularyCard
            import random

            db = get_session()
            try:
                count = db.query(VocabularyCard).count()
                if count > 0:
                    offset = random.randint(0, count - 1)
                    card = db.query(VocabularyCard).offset(offset).first()
                    if card:
                        return f"{card.word} — {card.meaning_en or ''}"
            finally:
                db.close()
        except Exception:
            pass
        return "serendipity — an unexpected happy discovery"

    def _notify(self, message):
        """Show a notification via the tray icon."""
        if self.icon:
            try:
                self.icon.notify(message, "EnglishCoach Pro")
            except Exception:
                pass

    def _on_show(self, icon=None, item=None):
        """Restore the main window."""
        try:
            if self.app:
                self.app.after(0, lambda: (self.app.deiconify(), self.app.lift()))
        except Exception:
            pass

    def _on_word_notification(self, icon=None, item=None):
        """Manually trigger word of the day."""
        word = self._get_word_of_day()
        self._notify(f"📖 Word of the Day: {word}")

    def _on_exit(self, icon=None, item=None):
        """Exit the application."""
        try:
            if self.scheduler:
                self.scheduler.shutdown(wait=False)
        except Exception:
            pass
        try:
            if self.app:
                self.app.after(0, self.app.destroy)
        except Exception:
            pass
        if icon:
            icon.stop()

    def minimize_to_tray(self):
        """Hide the main window and keep running in tray."""
        try:
            if self.app:
                self.app.withdraw()
        except Exception:
            pass

    def shutdown(self):
        """Clean shutdown of tray and scheduler."""
        try:
            if self.scheduler:
                self.scheduler.shutdown(wait=False)
        except Exception:
            pass
        try:
            if self.icon:
                self.icon.stop()
        except Exception:
            pass
