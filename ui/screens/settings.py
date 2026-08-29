import customtkinter as ctk
from data.database import get_session
from data.models import User


class SettingsScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.user = getattr(self.app, 'user', None)
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="Settings", font=("Arial", 20)).pack(pady=10)
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Name")
        self.name_entry.pack(pady=10)
        self.name_entry.insert(0, getattr(self.user, 'name', ''))

        self.daily_goal = ctk.CTkEntry(self, placeholder_text="Daily goal minutes")
        self.daily_goal.pack(pady=10)
        self.daily_goal.insert(0, str(getattr(self.user, 'daily_free_minutes', {}).get('mon', 60)))

        self.theme_var = ctk.StringVar(value=(getattr(self.user, 'theme_mode', None) or getattr(self.app, 'theme_mode', 'dark')).capitalize())
        ctk.CTkLabel(self, text="Theme").pack(pady=4)
        self.theme_menu = ctk.CTkOptionMenu(self, values=["Dark", "Light", "System"], variable=self.theme_var, command=self.change_theme)
        self.theme_menu.pack(pady=6)

        ctk.CTkButton(self, text="Save Settings", command=self.save_settings).pack(pady=15)
        self.feedback_label = ctk.CTkLabel(self, text="", wraplength=760, justify="left")
        self.feedback_label.pack(pady=10)

    def change_theme(self, value):
        if not getattr(self.app, 'set_theme_mode', None):
            return
        self.app.set_theme_mode(value)
        self.feedback_label.configure(text=f"Theme changed to {value}.")
        if self.user:
            try:
                self.user.theme_mode = value.lower()
            except Exception:
                pass

    def save_settings(self):
        if not self.user:
            self.feedback_label.configure(text="No user loaded.")
            return
        try:
            minutes = int(self.daily_goal.get())
        except ValueError:
            self.feedback_label.configure(text="Enter a valid number for daily goal.")
            return
        db = get_session()
        try:
            user = db.query(User).filter_by(id=self.user.id).first()
            if user:
                user.name = self.name_entry.get().strip() or user.name
                user.daily_free_minutes['mon'] = minutes
                user.theme_mode = self.theme_var.get().lower()
                db.commit()
                self.app.set_theme_mode(user.theme_mode)
                self.feedback_label.configure(text="Settings saved.")
        finally:
            db.close()