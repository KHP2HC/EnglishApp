"""Settings screen — profile, goals, theme, API key, language."""

import os

import customtkinter as ctk

from core.i18n import available_languages, get_language, set_language, t
from data.database import get_session
from data.models import User


class SettingsScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.user = getattr(self.app, "user", None)
        self.build_ui()

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        ctk.CTkLabel(self, text="⚙️ Settings", font=("Arial", 22, "bold")).grid(
            row=0, column=0, sticky="w", padx=16, pady=(12, 4)
        )

        scroll = ctk.CTkScrollableFrame(self)
        scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 10))

        # ── Profile section ────────────────────────────────────────────
        self._section_label(scroll, "Profile")
        profile_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        profile_frame.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(profile_frame, text="Name").pack(anchor="w", padx=10, pady=(8, 0))
        self.name_entry = ctk.CTkEntry(profile_frame, placeholder_text="Your name")
        self.name_entry.pack(fill="x", padx=10, pady=2)
        self.name_entry.insert(0, getattr(self.user, "name", ""))

        ctk.CTkLabel(profile_frame, text="Avatar emoji").pack(anchor="w", padx=10, pady=(8, 0))
        self.avatar_entry = ctk.CTkEntry(profile_frame, width=60)
        self.avatar_entry.pack(anchor="w", padx=10, pady=2)
        self.avatar_entry.insert(0, getattr(self.user, "avatar_emoji", "😊"))

        # ── Exam & Goals ───────────────────────────────────────────────
        self._section_label(scroll, "Exam & Goals")
        goals_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        goals_frame.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(goals_frame, text="Daily goal minutes (Monday)").pack(anchor="w", padx=10, pady=(8, 0))
        self.daily_goal = ctk.CTkEntry(goals_frame, placeholder_text="60")
        self.daily_goal.pack(anchor="w", padx=10, pady=2)
        self.daily_goal.insert(0, str(getattr(self.user, "daily_free_minutes", {}).get("mon", 60)))

        # ── Appearance ─────────────────────────────────────────────────
        self._section_label(scroll, "Appearance")
        appearance_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        appearance_frame.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(appearance_frame, text="Theme").pack(anchor="w", padx=10, pady=(8, 0))
        self.theme_var = ctk.StringVar(
            value=(getattr(self.user, "theme_mode", None) or "dark").capitalize()
        )
        self.theme_menu = ctk.CTkOptionMenu(
            appearance_frame,
            values=["Dark", "Light", "System"],
            variable=self.theme_var,
            command=self.change_theme,
        )
        self.theme_menu.pack(anchor="w", padx=10, pady=2)

        ctk.CTkLabel(appearance_frame, text="Language / Ngôn ngữ").pack(anchor="w", padx=10, pady=(8, 0))
        current_lang = get_language()
        lang_options = list(available_languages().values())
        self.lang_var = ctk.StringVar(
            value=available_languages().get(current_lang, "English")
        )
        self.lang_menu = ctk.CTkOptionMenu(
            appearance_frame,
            values=lang_options,
            variable=self.lang_var,
            command=self._on_lang_change,
        )
        self.lang_menu.pack(anchor="w", padx=10, pady=2)

        # ── AI / API Key ───────────────────────────────────────────────
        self._section_label(scroll, "AI Writing Feedback (Claude API)")
        api_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        api_frame.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(
            api_frame,
            text="Enter your Anthropic Claude API key. It will be encrypted and stored locally on this machine.",
            wraplength=700,
            justify="left",
            font=("Arial", 11),
            text_color=("gray40", "gray70"),
        ).pack(anchor="w", padx=10, pady=(8, 4))

        self.api_key_entry = ctk.CTkEntry(
            api_frame,
            placeholder_text="sk-ant-...",
            show="*",
            width=400,
        )
        self.api_key_entry.pack(anchor="w", padx=10, pady=2)

        # Check if key is already configured
        key_status = "Not configured"
        try:
            from core.ai_tutor import AITutor
            config_path = self._get_config_path()
            if AITutor.is_configured(config_path):
                key_status = "✅ Configured (encrypted)"
        except Exception:
            pass
        self.api_status_label = ctk.CTkLabel(
            api_frame,
            text=f"Status: {key_status}",
            font=("Arial", 11),
            text_color=("gray40", "gray70"),
        )
        self.api_status_label.pack(anchor="w", padx=10, pady=2)

        ctk.CTkButton(
            api_frame,
            text="Save API Key",
            width=120,
            command=self._save_api_key,
        ).pack(anchor="w", padx=10, pady=4)

        ctk.CTkButton(
            api_frame,
            text="Remove API Key",
            width=120,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            command=self._remove_api_key,
        ).pack(anchor="w", padx=10, pady=2)

        # ── Save button ────────────────────────────────────────────────
        ctk.CTkButton(
            scroll,
            text="Save Settings",
            font=("Arial", 14, "bold"),
            height=36,
            command=self.save_settings,
        ).pack(pady=16)

        self.feedback_label = ctk.CTkLabel(scroll, text="", wraplength=700, justify="left")
        self.feedback_label.pack(pady=4)

    def _section_label(self, parent, text):
        ctk.CTkLabel(
            parent,
            text=text,
            font=("Arial", 14, "bold"),
            text_color=("#4A90E2", "#2E6ED4"),
        ).pack(anchor="w", padx=10, pady=(12, 2))

    def _get_config_path(self):
        """Return the path for the encrypted API key file."""
        app_data = os.path.join(os.environ.get("APPDATA", os.getcwd()), "EnglishCoachPro")
        os.makedirs(app_data, exist_ok=True)
        return os.path.join(app_data, "ai_key.bin")

    def change_theme(self, value):
        if not getattr(self.app, "set_theme_mode", None):
            return
        self.app.set_theme_mode(value)
        self.feedback_label.configure(text=f"Theme changed to {value}.")
        if self.user:
            try:
                self.user.theme_mode = value.lower()
            except Exception:
                pass

    def _on_lang_change(self, value):
        lang_map = {v: k for k, v in available_languages().items()}
        code = lang_map.get(value, "en")
        set_language(code)
        self.feedback_label.configure(text=f"Language set to {value}. Restart for full effect.")

    def _save_api_key(self):
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            self.feedback_label.configure(text="Please enter an API key first.")
            return
        try:
            from cryptography.fernet import Fernet
            import hashlib
            import base64

            try:
                import winreg
            except Exception:
                winreg = None

            # Derive machine-specific key
            machine_id = None
            try:
                if winreg:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
                    machine_id, _ = winreg.QueryValueEx(key, "MachineGuid")
            except Exception:
                machine_id = None
            if not machine_id:
                machine_id = os.environ.get("COMPUTERNAME", "unknown")

            digest = hashlib.sha256(machine_id.encode("utf-8")).digest()
            fernet_key = base64.urlsafe_b64encode(digest)
            fernet = Fernet(fernet_key)

            config_path = self._get_config_path()
            encrypted = fernet.encrypt(api_key.encode())
            with open(config_path, "wb") as f:
                f.write(encrypted)

            self.api_status_label.configure(text="Status: ✅ Configured (encrypted)")
            self.feedback_label.configure(text="API key saved and encrypted.")
            self.api_key_entry.delete(0, "end")
        except Exception as exc:
            self.feedback_label.configure(text=f"Failed to save API key: {exc}")

    def _remove_api_key(self):
        try:
            config_path = self._get_config_path()
            if os.path.exists(config_path):
                os.remove(config_path)
            self.api_status_label.configure(text="Status: Not configured")
            self.feedback_label.configure(text="API key removed.")
        except Exception as exc:
            self.feedback_label.configure(text=f"Failed to remove API key: {exc}")

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
                user.avatar_emoji = self.avatar_entry.get().strip() or "😊"
                if not isinstance(user.daily_free_minutes, dict):
                    user.daily_free_minutes = {}
                user.daily_free_minutes["mon"] = minutes
                user.theme_mode = self.theme_var.get().lower()
                db.commit()
                self.app.set_theme_mode(user.theme_mode)
                self.feedback_label.configure(text="✅ Settings saved.")
        finally:
            db.close()