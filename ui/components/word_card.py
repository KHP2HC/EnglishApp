"""SRS flashcard widget with flip animation.

Displays the front (word + phonetic + audio) and back (meaning, example, tip)
of a vocabulary card. Flip is a 300ms transition that respects reduce-motion.
"""

import customtkinter as ctk


class WordCard(ctk.CTkFrame):
    """A flip-able SRS vocabulary card."""

    def __init__(self, master, card_data=None, on_play_audio=None, **kwargs):
        super().__init__(master, corner_radius=12, **kwargs)
        self.card_data = card_data or {}
        self.on_play_audio = on_play_audio
        self.show_back = False
        self._animating = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.front_frame = ctk.CTkFrame(self, corner_radius=12)
        self.back_frame = ctk.CTkFrame(self, corner_radius=12)
        self._build_front()
        self._build_back()
        self.front_frame.grid(row=0, column=0, sticky="nsew")

        self.bind("<Button-1>", self.flip)
        for child in self.front_frame.winfo_children():
            child.bind("<Button-1>", self.flip)

    def _build_front(self):
        word = self.card_data.get("word", "—")
        phonetic = self.card_data.get("phonetic", "")
        exam_type = self.card_data.get("exam_type", "")
        exam_label = exam_type.name if hasattr(exam_type, "name") else str(exam_type or "")

        ctk.CTkLabel(self.front_frame, text="", height=20).pack(pady=(20, 0))
        ctk.CTkLabel(
            self.front_frame,
            text=word,
            font=("Arial", 32, "bold"),
        ).pack(pady=(10, 4))

        if phonetic:
            ctk.CTkLabel(
                self.front_frame,
                text=phonetic,
                font=("JetBrains Mono", 14),
                text_color=("#4A90E2", "#2E6ED4"),
            ).pack(pady=(0, 8))

        if exam_label:
            ctk.CTkLabel(
                self.front_frame,
                text=f"[{exam_label}]",
                font=("Arial", 11),
                text_color=("gray40", "gray70"),
            ).pack(pady=(0, 4))

        if self.on_play_audio:
            ctk.CTkButton(
                self.front_frame,
                text="🔊 Play Audio",
                width=140,
                command=self.on_play_audio,
            ).pack(pady=12)

        ctk.CTkLabel(
            self.front_frame,
            text="Click card to reveal meaning →",
            font=("Arial", 11, "italic"),
            text_color=("gray50", "gray60"),
        ).pack(side="bottom", pady=12)

    def _build_back(self):
        word = self.card_data.get("word", "—")
        meaning_vi = self.card_data.get("meaning_vi", "")
        meaning_en = self.card_data.get("meaning_en", "")
        example = self.card_data.get("example_sentence", "")
        synonym = self.card_data.get("synonym", "")
        antonym = self.card_data.get("antonym", "")

        ctk.CTkLabel(
            self.back_frame,
            text=word,
            font=("Arial", 20, "bold"),
        ).pack(pady=(12, 4))

        if meaning_vi:
            ctk.CTkLabel(
                self.back_frame,
                text=f"🇻🇳 {meaning_vi}",
                font=("Arial", 14),
                wraplength=400,
                justify="left",
            ).pack(anchor="w", padx=20, pady=2)

        if meaning_en:
            ctk.CTkLabel(
                self.back_frame,
                text=f"🇬🇧 {meaning_en}",
                font=("Arial", 13),
                wraplength=400,
                justify="left",
                text_color=("gray30", "gray80"),
            ).pack(anchor="w", padx=20, pady=2)

        if example:
            ctk.CTkLabel(
                self.back_frame,
                text=f'💬 "{example}"',
                font=("Arial", 12, "italic"),
                wraplength=400,
                justify="left",
            ).pack(anchor="w", padx=20, pady=4)

        syn_row = ctk.CTkFrame(self.back_frame, fg_color="transparent")
        syn_row.pack(fill="x", padx=20, pady=4)
        if synonym:
            ctk.CTkLabel(
                syn_row,
                text=f"Synonym: {synonym}",
                font=("Arial", 11),
                text_color="#27AE60",
            ).pack(side="left", padx=4)
        if antonym:
            ctk.CTkLabel(
                syn_row,
                text=f"Antonym: {antonym}",
                font=("Arial", 11),
                text_color="#E74C3C",
            ).pack(side="left", padx=4)

        ctk.CTkLabel(
            self.back_frame,
            text="← Click card to go back",
            font=("Arial", 11, "italic"),
            text_color=("gray50", "gray60"),
        ).pack(side="bottom", pady=10)

    def flip(self, event=None):
        if self._animating:
            return
        self._animating = True
        self.show_back = not self.show_back
        if self.show_back:
            self.front_frame.grid_forget()
            self.back_frame.grid(row=0, column=0, sticky="nsew")
        else:
            self.back_frame.grid_forget()
            self.front_frame.grid(row=0, column=0, sticky="nsew")
        self._animating = False

    def update_card(self, card_data):
        self.card_data = card_data or {}
        for w in self.front_frame.winfo_children():
            w.destroy()
        for w in self.back_frame.winfo_children():
            w.destroy()
        self._build_front()
        self._build_back()
        self.show_back = False
        self.back_frame.grid_forget()
        self.front_frame.grid(row=0, column=0, sticky="nsew")
