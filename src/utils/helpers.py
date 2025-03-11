# src/utils/helpers.py
import tkinter as tk
import ttkbootstrap as ttk
import logging

class ToolTip:
    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(tw, text=self.text, justify="left", background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

def validate_number(action: str, value_if_allowed: str, text: str, prior_value: str) -> bool:
    """Валидация ввода чисел: только положительные десятичные числа с максимум 2 знаками после точки."""
    logging.debug(f"Validating: action={action}, value={value_if_allowed}, text={text}, prior={prior_value}")

    if action != "1":
        return True

    if not value_if_allowed:
        return True

    if text in "0123456789.":
        if text == ".":
            if "." in prior_value:
                logging.debug("Validation failed: Second dot")
                return False
            return True
        new_value = value_if_allowed
        if "." in new_value:
            decimal_part = new_value.split(".")[1]
            if len(decimal_part) > 2:
                logging.debug("Validation failed: Too many decimal places (max 2)")
                return False
        return (new_value.count(".") <= 1 and
                all(c in "0123456789." for c in new_value))
    logging.debug(f"Validation failed: Invalid character '{text}'")
    return False