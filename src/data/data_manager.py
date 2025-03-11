import json
import os
import csv
import logging
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import scrolledtext
from tkinter import messagebox
from typing import Dict, Callable

class DataManager:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.history_file = os.path.join(self.base_path, "history.json")
        self.autosave_file = os.path.join(self.base_path, "autosave.json")
        self.collapsed_state_file = os.path.join(self.base_path, "collapsed_state.json")
        self.ui_state_file = os.path.join(self.base_path, "ui_state.json")
        self.history = []
        self.max_history = 10
        logging.debug(f"Initialized DataManager with base_path: {self.base_path}")

    def save(self, entries: Dict[str, str], result_text: str, lang: str) -> str:
        # entries уже содержит строки, а не объекты ttk.Entry
        data = {
            "lang": lang,
            "entries": entries,  # Убрали вызов .get(), так как entries уже содержит строки
            "results": result_text
        }
        try:
            with open(self.autosave_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return "Сохранено успешно" if lang == "ru" else "Saved successfully"
        except Exception as e:
            logging.error(f"Failed to save data: {e}")
            return f"Ошибка сохранения: {e}" if lang == "ru" else f"Save error: {e}"

    def load(self, entries: Dict[str, ttk.Entry], result_text: scrolledtext.ScrolledText, lang: str) -> tuple:
        # Возвращаем кортеж (loaded_data, status) для совместимости с app_ui.py
        try:
            if not os.path.exists(self.autosave_file) or os.path.getsize(self.autosave_file) == 0:
                return {}, "Нет сохранённых данных" if lang == "ru" else "No saved data"
            with open(self.autosave_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            loaded_entries = data.get("entries", {})
            result_text.configure(state="normal")
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, data.get("results", ""))
            result_text.configure(state="disabled")
            return loaded_entries, "Загружено успешно" if lang == "ru" else "Loaded successfully"
        except json.JSONDecodeError:
            logging.error("Failed to load data: Invalid or empty JSON file")
            return {}, "Ошибка загрузки: файл пуст или повреждён" if lang == "ru" else "Load error: file is empty or corrupted"
        except Exception as e:
            logging.error(f"Failed to load data: {e}")
            return {}, f"Ошибка загрузки: {e}" if lang == "ru" else f"Load error: {e}"

    def autosave_results(self, entries: Dict[str, ttk.Entry], result_text: str):
        # Преобразуем ttk.Entry в строки перед сохранением
        self.save({name: entry.get().strip() for name, entry in entries.items()}, result_text, "ru")

    def save_collapsed_state(self, collapsed_state: Dict[str, bool]):
        try:
            with open(self.collapsed_state_file, "w", encoding="utf-8") as f:
                json.dump(collapsed_state, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save collapsed state: {e}")

    def load_collapsed_state(self, lang: str) -> Dict[str, bool]:
        try:
            if not os.path.exists(self.collapsed_state_file) or os.path.getsize(self.collapsed_state_file) == 0:
                return {}
            with open(self.collapsed_state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.error("Failed to load collapsed state: Invalid or empty JSON file")
            return {}
        except Exception as e:
            logging.error(f"Failed to load collapsed state: {e}")
            return {}

    def save_ui_state(self, ui_state: Dict):
        try:
            with open(self.ui_state_file, "w", encoding="utf-8") as f:
                json.dump(ui_state, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save UI state: {e}")

    def load_ui_state(self) -> Dict:
        try:
            if not os.path.exists(self.ui_state_file) or os.path.getsize(self.ui_state_file) == 0:
                return {}
            with open(self.ui_state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.error("Failed to load UI state: Invalid or empty JSON file")
            return {}
        except Exception as e:
            logging.error(f"Failed to load UI state: {e}")
            return {}

    def add_to_history(self, entries: Dict[str, ttk.Entry], result_text: str):
        entry_data = {name: entry.get().strip() for name, entry in entries.items()}
        self.history.append({"entries": entry_data, "results": result_text})
        if len(self.history) > self.max_history:
            self.history.pop(0)
        logging.debug(f"Added to history. Current history length: {len(self.history)}")

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
            logging.debug(f"Saved history to {self.history_file}. History length: {len(self.history)}")
        except Exception as e:
            logging.error(f"Failed to save history: {e}")

    def load_history(self) -> list:
        try:
            if not os.path.exists(self.history_file):
                logging.debug(f"History file {self.history_file} does not exist")
                return []
            if os.path.getsize(self.history_file) == 0:
                logging.debug(f"History file {self.history_file} is empty")
                return []
            with open(self.history_file, "r", encoding="utf-8") as f:
                loaded_history = json.load(f)
                logging.debug(f"Loaded history from {self.history_file}: {loaded_history}")
                self.history = loaded_history
                return self.history
        except json.JSONDecodeError as e:
            logging.error(f"Failed to load history: Invalid JSON in {self.history_file}. Error: {e}")
            return []
        except Exception as e:
            logging.error(f"Failed to load history: {e}")
            return []

    def export_to_csv(self, result_text: str, lang: str):
        try:
            output_file = os.path.join(self.base_path, "results.csv")
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                for line in result_text.split("\n"):
                    if ":" in line:
                        metric, value = line.split(":", 1)
                        writer.writerow([metric.strip(), value.strip()])
            return "Экспорт в CSV успешен" if lang == "ru" else "Export to CSV successful"
        except Exception as e:
            logging.error(f"Failed to export to CSV: {e}")
            return f"Ошибка экспорта: {e}" if lang == "ru" else f"Export error: {e}"

    def export_inputs_to_csv(self, entries: Dict[str, ttk.Entry], lang: str):
        try:
            output_file = os.path.join(self.base_path, "input_data.csv")
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Field", "Value"])
                for name, entry in entries.items():
                    value = entry.get().strip()
                    if value:
                        writer.writerow([name, value])
            return "Экспорт входных данных в CSV успешен" if lang == "ru" else "Export of input data to CSV successful"
        except Exception as e:
            logging.error(f"Failed to export inputs to CSV: {e}")
            return f"Ошибка экспорта: {e}" if lang == "ru" else f"Export error: {e}"

    def show_history(self, root: tk.Tk, entries: Dict[str, ttk.Entry], result_text: scrolledtext.ScrolledText, lang: str, check_fields: Callable):
        history = self.load_history()
        logging.debug(f"History loaded: {history}")
        if not history or not any(history):
            messagebox.showinfo("История" if lang == "ru" else "History",
                                "История пуста" if lang == "ru" else "History is empty")
            return

        history_window = tk.Toplevel(root)
        history_window.title("История" if lang == "ru" else "History")
        history_window.geometry("400x500")

        listbox = tk.Listbox(history_window, height=10)
        listbox.pack(fill="both", expand=True, padx=5, pady=5)

        for i, record in enumerate(history):
            listbox.insert(tk.END, f"Запись {i + 1}: {len(record['entries'])} полей")

        def on_select(event):
            selection = listbox.curselection()
            if not selection:
                return
            index = selection[0]
            record = history[index]
            for name, entry in entries.items():
                entry.delete(0, tk.END)
                value = record["entries"].get(name, "")
                if value:
                    entry.insert(0, value)
            result_text.configure(state="normal")
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, record.get("results", ""))
            result_text.configure(state="disabled")
            check_fields()

        listbox.bind("<<ListboxSelect>>", on_select)