import customtkinter as ctk


class ProgressRing(ctk.CTkCanvas):
    def __init__(self, master, progress=0, total=60, size=100):
        super().__init__(master, width=size, height=size, highlightthickness=0)
        self.progress = progress
        self.total = total
        self.size = size
        self.draw()

    def draw(self):
        self.delete("all")
        angle = 360 * (self.progress / max(self.total, 1))
        # draw arc
        self.create_arc((10,10,self.size-10,self.size-10), start=90, extent=-angle,
                        outline="#4A90E2", width=10, style="arc")
        # text center
        self.create_text(self.size/2, self.size/2, text=f"{self.progress}m", fill="white", font=("Arial", 20))