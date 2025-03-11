import sys
from src.ui.app_ui import AppUI
import tkinter as tk
import logging
logging.basicConfig(level=logging.DEBUG)
def main():
    root = tk.Tk()
    app = AppUI(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Приложение прервано пользователем. Завершение...")
        root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    main()