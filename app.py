import customtkinter as ctk
from ui.screens.dashboard import DashboardScreen
from ui.screens.vocabulary import VocabularyScreen
from ui.screens.progress import ProgressScreen
from ui.screens.reading import ReadingScreen
from ui.screens.listening import ListeningScreen
from ui.screens.writing import WritingScreen
from ui.screens.speaking import SpeakingScreen
from ui.screens.planner import PlannerScreen
from ui.screens.settings import SettingsScreen
from ui.screens.adaptive_test import AdaptiveTestScreen
from ui.screens.onboarding import OnboardingWizard
from ui.components.nav_sidebar import Sidebar

class App(ctk.CTk):
    def __init__(self, start_page='dashboard'):
        super().__init__()
        self.title("EnglishCoach Pro")
        self.geometry("1200x700")
        self.theme_mode = "dark"
        ctk.set_appearance_mode(self.theme_mode)
        ctk.set_default_color_theme("blue")
        
        # main container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # sidebar
        self.sidebar = Sidebar(self, self.navigate)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=5, pady=5)
        
        # main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # current screen
        self.current_screen = None
        self.current_page = None
        self.navigate(start_page)
    
    def set_theme_mode(self, mode):
        mode = mode.lower()
        if mode not in ["light", "dark", "system"]:
            return
        self.theme_mode = mode
        ctk.set_appearance_mode(self.theme_mode)
        if getattr(self, 'sidebar', None):
            self.sidebar.refresh_theme()
        if getattr(self, 'current_screen', None):
            try:
                self.current_screen.configure(fg_color="transparent")
            except Exception:
                pass
    
    def navigate(self, page):
        # clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.current_page = page
        # create new screen
        if page == "dashboard":
            screen = DashboardScreen(self.main_frame, self)
        elif page == "vocabulary":
            screen = VocabularyScreen(self.main_frame, self)
        elif page == "progress":
            screen = ProgressScreen(self.main_frame, self)
        elif page == "reading":
            screen = ReadingScreen(self.main_frame, self)
        elif page == "listening":
            screen = ListeningScreen(self.main_frame, self)
        elif page == "writing":
            screen = WritingScreen(self.main_frame, self)
        elif page == "speaking":
            screen = SpeakingScreen(self.main_frame, self)
        elif page == "placement":
            screen = AdaptiveTestScreen(self.main_frame, self)
        elif page == "planner":
            screen = PlannerScreen(self.main_frame, self)
        elif page == "settings":
            screen = SettingsScreen(self.main_frame, self)
        elif page == "onboarding":
            screen = OnboardingWizard(self.main_frame, self)
        else:
            screen = ctk.CTkFrame(self.main_frame)
            label = ctk.CTkLabel(screen, text=f"{page.capitalize()} (Coming Soon)", font=("Arial", 24))
            label.pack(pady=20)
        screen.pack(fill="both", expand=True)
        self.current_screen = screen
        if getattr(self, 'sidebar', None):
            self.sidebar.set_active_page(page)
        try:
            self.after_cancel(getattr(self, '_notification_job', None))
        except Exception:
            pass

    def notify(self, message, duration=4000):
        toast = ctk.CTkLabel(self, text=message, fg_color="#333333", text_color="white", corner_radius=10, padx=10, pady=6)
        toast.place(relx=0.5, rely=0.03, anchor="n")
        try:
            self.after_cancel(getattr(self, '_notification_job', None))
        except Exception:
            pass
        self._notification_job = self.after(duration, lambda: toast.destroy())
