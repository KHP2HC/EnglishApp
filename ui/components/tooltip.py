import tkinter as tk
import customtkinter as ctk


class Tooltip:
    def __init__(self, parent, delay=200):
        self.parent = parent
        self.delay = delay
        self._after_id = None
        self._toplevel = None
        self._text = ''

    def register(self, widget, text):
        def enter(e):
            self._text = text
            self._after_id = widget.after(self.delay, lambda: self._show(widget))

        def leave(e):
            if self._after_id:
                try:
                    widget.after_cancel(self._after_id)
                except Exception:
                    pass
                self._after_id = None
            self._hide()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def _show(self, widget):
        if self._toplevel:
            self._hide()
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + 20
        self._toplevel = tk.Toplevel(self.parent)
        self._toplevel.wm_overrideredirect(True)
        self._toplevel.attributes('-topmost', True)
        lbl = ctk.CTkLabel(self._toplevel, text=self._text, fg_color='#333333', text_color='white')
        lbl.pack(padx=6, pady=3)

    def _hide(self):
        if self._toplevel:
            try:
                self._toplevel.destroy()
            except Exception:
                pass
            self._toplevel = None
