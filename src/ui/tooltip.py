import tkinter as tk
from tkinter import ttk

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Убираем обрамление окна
        tw.wm_attributes("-topmost", True)  # Окно всегда сверху
        tw.wm_attributes("-alpha", 0.95)  # Лёгкая прозрачность
        tw.wm_geometry(f"+{x}+{y}")
        # Создаём красивую рамку с закруглёнными углами
        frame = ttk.Frame(tw, style="Tooltip.TFrame")
        frame.pack(padx=1, pady=1)
        label = ttk.Label(frame, text=self.text, font=("Roboto", 10),
                          foreground="#ffffff", background="#2c3e50",
                          wraplength=300, padding=(8, 4))
        label.pack()
        # Настраиваем стиль для красивого вида
        style = ttk.Style()
        style.configure("Tooltip.TFrame", background="#2c3e50", borderwidth=1, relief="solid")
        # Предотвращаем взаимодействие с подсказкой
        label.bind("<Enter>", lambda e: "break")  # Не даём подсказке перехватывать события
        label.bind("<Leave>", lambda e: self.hide_tip())

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None