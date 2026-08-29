import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, navigate_callback):
        super().__init__(master, width=60, corner_radius=0)
        self.navigate = navigate_callback
        self.pack_propagate(False)
        # buttons with emoji icons
        icons = [
            ("🏠", "dashboard"),
            ("🧠", "vocabulary"),
            ("📖", "reading"),
            ("👂", "listening"),
            ("✍️", "writing"),
            ("🗣️", "speaking"),
            ("📊", "progress"),
            ("🗓️", "planner"),
            ("🧪", "placement"),
            ("⚙️", "settings")
        ]
        self.buttons = []
        self.page_map = []
        for emoji, page in icons:
            btn = ctk.CTkButton(self, text=emoji, font=("Segoe UI Emoji", 24),
                                fg_color="transparent", text_color=self._icon_text_color(),
                                hover_color=self._hover_color(),
                                command=lambda p=page: self.navigate(p))
            btn.pack(pady=10)
            self.buttons.append(btn)
            self.page_map.append((btn, page))
        self.set_active_page("dashboard")

    def _icon_text_color(self):
        appearance = ctk.get_appearance_mode().lower()
        return "white" if appearance == "dark" else "black"

    def _hover_color(self):
        appearance = ctk.get_appearance_mode().lower()
        return "#444444" if appearance == "dark" else "#dddddd"

    def set_active_page(self, page):
        for btn, btn_page in self.page_map:
            is_active = btn_page == page
            btn.configure(fg_color="#4b7bec" if is_active else "transparent", text_color="white" if is_active else self._icon_text_color())

    def refresh_theme(self):
        for btn, _ in self.page_map:
            btn.configure(text_color=self._icon_text_color(), hover_color=self._hover_color())
        try:
            self.set_active_page(getattr(self, 'active_page', 'dashboard'))
        except Exception:
            pass
