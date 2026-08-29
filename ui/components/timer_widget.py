import customtkinter as ctk


class TimerWidget(ctk.CTkFrame):
    def __init__(self, master, minutes=25, on_finish=None, **kwargs):
        super().__init__(master, **kwargs)
        self.minutes = minutes
        self.seconds_left = int(minutes * 60)
        self.on_finish = on_finish
        self._job = None
        self._running = False
        self.label = ctk.CTkLabel(self, text=self._format_time())
        self.label.pack(side='left', padx=8)
        self.start_btn = ctk.CTkButton(self, text='Start', command=self.start)
        self.start_btn.pack(side='left', padx=4)
        self.stop_btn = ctk.CTkButton(self, text='Stop', command=self.stop)
        self.stop_btn.pack(side='left', padx=4)

    def _format_time(self):
        m, s = divmod(self.seconds_left, 60)
        return f"{m:02d}:{s:02d}"

    def _tick(self):
        if not self._running:
            return
        if self.seconds_left <= 0:
            self.label.configure(text='00:00')
            self._running = False
            if callable(self.on_finish):
                try:
                    self.on_finish()
                except Exception:
                    pass
            return
        self.seconds_left -= 1
        self.label.configure(text=self._format_time())
        self._job = self.after(1000, self._tick)

    def start(self, minutes=None):
        if minutes is not None:
            self.minutes = minutes
            self.seconds_left = int(minutes * 60)
        if self._running:
            return
        self._running = True
        self._tick()

    def stop(self):
        self._running = False
        if self._job:
            try:
                self.after_cancel(self._job)
            except Exception:
                pass
            self._job = None
