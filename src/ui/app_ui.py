import tkinter as tk
from tkinter import scrolledtext, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import logging
from src.ui.tooltip import ToolTip
import matplotlib.pyplot as plt
import pyperclip
from typing import Dict, Callable
from src.core.calculations import calculate_metrics
from src.core.formulas import FORMULAS
from src.data.data_manager import DataManager
from src.utils.helpers import validate_number
from src.visualization.charts import show_chart  # Импортируем новую функцию
import re


class AppUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Digital Marketing Metrics")
        self.entries: Dict[str, ttk.Entry] = {}
        self.formula_indicators: Dict[str, ttk.Label] = {}
        self.formula_progress: Dict[str, ttk.Label] = {}
        self.collapse_buttons: Dict[str, ttk.Button] = {}
        self.separators: Dict[str, ttk.Separator] = {}  # Словарь для хранения разделителей
        self.current_theme = "solar"
        self.current_lang = "ru"
        self.last_width = 0
        self.last_height = 0
        self.collapsed_state: Dict[str, bool] = {}
        self.update_pending = False
        self.is_single_column = False
        self.after_id = None
        self.last_results = []
        self.chart_canvas = None
        self.chart_fig = None
        self.chart_window = None
        self.chart_type = tk.StringVar(value="bar")

        logging.basicConfig(
            filename='D:/Projects/Python/DigitalMarketingMetrics/DigitalMarketingMetrics.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        self.style = ttk.Style(self.current_theme)
        self.data_manager = DataManager(self._get_base_path())
        self.vcmd = (self.root.register(validate_number), "%d", "%P", "%S", "%s")

        self._load_ui_state()
        self._setup_ui()
        self.collapsed_state = self.data_manager.load_collapsed_state(self.current_lang)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.bind("<Configure>", self._on_configure)

    def _get_base_path(self) -> str:
        import sys
        import os
        return sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    def _load_ui_state(self):
        ui_state = self.data_manager.load_ui_state()
        if ui_state:
            self.current_theme = ui_state.get("theme", "solar")
            self.current_lang = ui_state.get("language", "ru")
            geometry = ui_state.get("geometry", "600x700")
            position = ui_state.get("position", None)
            self.root.geometry(geometry)
            if position:
                self.root.geometry(f"+{position['x']}+{position['y']}")
            self.collapsed_state = ui_state.get("collapsed_state", {})
        else:
            self.root.geometry("600x700")
        self.root.minsize(400, 500)
        self.root.maxsize(1000, 1200)

    def _save_ui_state(self):
        geometry = f"{self.root.winfo_width()}x{self.root.winfo_height()}"
        position = {"x": self.root.winfo_x(), "y": self.root.winfo_y()}
        ui_state = {
            "theme": self.current_theme,
            "language": self.current_lang,
            "geometry": geometry,
            "position": position,
            "collapsed_state": self.collapsed_state
        }
        self.data_manager.save_ui_state(ui_state)

    def _setup_ui(self):
        self.top_frame = ttk.Frame(self.root, padding=5)
        self.top_frame.pack(side="top", fill="x")
        self._create_top_controls()

        self.center_frame = ttk.Frame(self.root)
        self.center_frame.pack(side="top", fill="both", expand=True)
        self._create_input_area()
        self._create_buttons()
        self._create_result_area()

        self.bottom_frame = ttk.Frame(self.root, padding=5)
        self.bottom_frame.pack(side="bottom", fill="x")
        self._create_bottom_controls()

        self.root.update_idletasks()
        self.update_layout()

    def _create_top_controls(self):
        available_themes = ttk.Style().theme_names()
        self.theme_var = tk.StringVar(value=self.current_theme)
        ttk.OptionMenu(self.top_frame, self.theme_var, self.current_theme, *available_themes,
                       command=self._switch_theme, bootstyle="info-outline").pack(side="left", padx=5)
        self.lang_var = tk.StringVar(value=self.current_lang)
        self.lang_menu = ttk.OptionMenu(self.top_frame, self.lang_var, self.current_lang, "ru", "en",
                                        command=self._switch_language, bootstyle="success-outline")
        self.lang_menu.pack(side="left", padx=5)
        ttk.Button(self.top_frame, text="История" if self.current_lang == "ru" else "History",
                   command=self._show_history, bootstyle="secondary").pack(side="right", padx=5)

    def _create_input_area(self):
        self.main_frame = ttk.Frame(self.center_frame, padding=5)
        self.main_frame.pack(side="top", fill="both", expand=True)
        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0, bg=self.style.colors.bg)
        self.v_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview,
                                         bootstyle="round-primary")
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)
        self.v_scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.input_frame = ttk.Frame(self.canvas, padding=5)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.input_frame, anchor="nw")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        self.input_frame.bind("<Configure>", self._update_scrollregion)
        self.input_frame.bind("<Enter>", lambda e: self.canvas.focus_set())

    def _on_mousewheel(self, event):
        if self.canvas.yview() == (0.0, 1.0):
            return
        delta = -1 if (event.num == 4 or event.delta > 0) else 1
        self.canvas.yview_scroll(int(delta * 2), "units")
        return "break"

    def _update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())
        self.canvas.update_idletasks()

    def _create_buttons(self):
        self.button_frame = ttk.Frame(self.center_frame, padding=5)
        self.button_frame.pack(side="top", fill="x")
        self.calculate_button = ttk.Button(self.button_frame,
                                          text="Рассчитать" if self.current_lang == "ru" else "Calculate",
                                          command=self.calculate, bootstyle="success", state="disabled")
        self.calculate_button.pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="Очистить" if self.current_lang == "ru" else "Clear",
                   command=self.clear, bootstyle="danger").pack(side="left", padx=5)

    def _create_result_area(self):
        self.result_frame = ttk.Frame(self.center_frame, padding=5)
        self.result_frame.pack(side="top", fill="both", expand=True)
        self.result_header_frame = ttk.Frame(self.result_frame)
        self.result_header_frame.pack(fill="x")
        ttk.Label(self.result_header_frame, text="Результаты:" if self.current_lang == "ru" else "Results:",
                  font=("Roboto", 12, "bold"), bootstyle="info").pack(side="left")
        ttk.Button(self.result_header_frame, text="Показать график" if self.current_lang == "ru" else "Show Chart",
                   command=self.show_chart, bootstyle="info").pack(side="left", padx=5)
        ttk.Button(self.result_header_frame, text="Копировать результаты" if self.current_lang == "ru" else "Copy Results",
                   command=self.copy_results, bootstyle="info").pack(side="left", padx=5)
        self.status_text = tk.Text(self.result_header_frame, height=2, wrap=tk.WORD, font=("Roboto", 9),
                                   bg=self.style.colors.inputbg, fg=self.style.colors.inputfg, borderwidth=1, relief="flat")
        self.status_text.pack(side="right", padx=5, fill="x", expand=True)
        self.status_text.configure(state="disabled")
        self.result_text = scrolledtext.ScrolledText(self.result_frame, height=10, wrap=tk.WORD,
                                                     font=("Roboto", 10), bg=self.style.colors.inputbg,
                                                     fg=self.style.colors.inputfg, borderwidth=1, relief="flat")
        self.result_text.tag_configure("success", foreground="green")
        self.result_text.tag_configure("warning", foreground="yellow")
        self.result_text.tag_configure("danger", foreground="red")
        self.result_text.tag_configure("very_good", foreground="#00cc00")
        self.status_text.tag_configure("success", foreground="green")
        self.status_text.tag_configure("warning", foreground="yellow")
        self.status_text.tag_configure("danger", foreground="red")
        self.status_text.tag_configure("very_good", foreground="#00cc00")
        self.result_text.pack(fill="both", expand=True)
        self.result_text.configure(state="disabled")

    def _create_bottom_controls(self):
        save_button = ttk.Button(self.bottom_frame, text="Сохранить в файл" if self.current_lang == "ru" else "Save to File",
                                 command=self.save, bootstyle="primary", width=15)
        load_button = ttk.Button(self.bottom_frame, text="Загрузить из файла" if self.current_lang == "ru" else "Load from File",
                                 command=self.load, bootstyle="warning", width=15)
        self.footer_items = [save_button, load_button]
        self._update_footer_layout()

    def _validate_entry(self, value: str) -> bool:
        if not value or value.endswith("."):
            return False
        pattern = r'^(0\.\d{1,2}|[1-9]\d*(\.\d{1,2})?)$'
        if not re.match(pattern, value):
            return False
        try:
            num = float(value)
            if num <= 0:
                return False
            return True
        except ValueError:
            return False

    def _update_entry_style(self, entry: ttk.Entry, value: str):
        entry.configure(bootstyle="info" if self._validate_entry(value) else "danger")

    def _get_field_names(self, fields: list) -> list:
        return [field[0].rstrip(':') for field in fields]

    def _calculate_example(self, formula_title: str, fields: list) -> str:
        field_names = self._get_field_names(fields)
        num_fields = len(field_names)
        translations = {
            "ru": {
                "CTR (Кликабельность)": f"CTR = ({field_names[1]} / {field_names[0]}) × 100%" if num_fields >= 2 else "Формула не применима",
                "CPC (Стоимость за клик)": f"CPC = {field_names[0]} / {field_names[1]}" if num_fields >= 2 else "Формула не применима",
                "CPA (Стоимость за действие)": f"CPA = {field_names[0]} / {field_names[1]}" if num_fields >= 2 else "Формула не применима",
                "ROAS (Возврат затрат)": f"ROAS = {field_names[0]} / {field_names[1]}" if num_fields >= 2 else "Формула не применима",
                "CR (Конверсия)": f"CR = ({field_names[1]} / {field_names[0]}) × 100%" if num_fields >= 2 else "Формула не применима",
                "LTV (Пожизненная ценность клиента)": f"LTV = {field_names[0]} × {field_names[1]} × {field_names[2]}" if num_fields >= 3 else "Формула не применима",
                "CPL (Стоимость за лид)": f"CPL = {field_names[0]} / {field_names[1]}" if num_fields >= 2 else "Формула не применима",
                "RPM (Доход на тысячу показов)": f"RPM = ({field_names[0]} / {field_names[1]}) × 1000" if num_fields >= 2 else "Формула не применима"
            },
            "en": {
                "CTR (Click-Through Rate)": f"CTR = ({field_names[1]} / {field_names[0]}) × 100%" if num_fields >= 2 else "Formula not applicable",
                "CPC (Cost Per Click)": f"CPC = {field_names[0]} / {field_names[1]}" if num_fields >= 2 else "Formula not applicable",
                "CPA (Cost Per Action)": f"CPA = {field_names[0]} / {field_names[1]}" if num_fields >= 2 else "Formula not applicable",
                "ROAS (Return on Ad Spend)": f"ROAS = {field_names[0]} / {field_names[1]}" if num_fields >= 2 else "Formula not applicable",
                "CR (Conversion Rate)": f"CR = ({field_names[1]} / {field_names[0]}) × 100%" if num_fields >= 2 else "Formula not applicable",
                "LTV (Lifetime Value)": f"LTV = {field_names[0]} × {field_names[1]} × {field_names[2]}" if num_fields >= 3 else "Formula not applicable",
                "CPL (Cost Per Lead)": f"CPL = {field_names[0]} / {field_names[1]}" if num_fields >= 2 else "Formula not applicable",
                "RPM (Revenue Per Mille)": f"RPM = ({field_names[0]} / {field_names[1]}) × 1000" if num_fields >= 2 else "Formula not applicable"
            }
        }
        return translations[self.current_lang].get(formula_title, "Формула не определена" if self.current_lang == "ru" else "Formula not defined")

    def _get_font_size(self, base_size: int) -> int:
        window_width = self.root.winfo_width()
        scale_factor = window_width / 600
        return max(11, min(12, int(base_size * scale_factor)))

    def update_layout(self, force_update=False):
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        new_is_single_column = window_width <= 480

        if not self.entries or self.is_single_column != new_is_single_column or force_update:
            current_values = {name: entry.get() for name, entry in self.entries.items() if isinstance(entry, ttk.Entry)}
            self.entries.clear()
            self.formula_indicators.clear()
            self.formula_progress.clear()
            self.collapse_buttons.clear()
            # Очищаем старые разделители
            for sep in self.separators.values():
                sep.destroy()
            self.separators.clear()
            for widget in self.input_frame.winfo_children():
                widget.destroy()

            row = 0
            for formula_title, formula_desc, fields in FORMULAS[self.current_lang]:
                # Начало формулы
                title_frame = ttk.Frame(self.input_frame)
                title_frame.grid(row=row, column=0, columnspan=4, pady=(5, 2), sticky="ew")
                # Используем grid для точного размещения
                collapse_button = ttk.Button(title_frame,
                                             text="▲" if self.collapsed_state.get(formula_title, False) else "▼",
                                             width=2, command=lambda ft=formula_title: self._toggle_collapse(ft))
                collapse_button.grid(row=0, column=0, padx=(0, 2), sticky="w")
                self.collapse_buttons[formula_title] = collapse_button
                title_label = ttk.Label(title_frame, text=formula_title,
                                        font=("Roboto", self._get_font_size(14), "bold"), bootstyle="primary-bold")
                title_label.grid(row=0, column=1, padx=(2, 2), sticky="w")  # Заголовок идёт после кнопки
                indicator = ttk.Label(title_frame, text="*" if self.current_lang == "ru" else "*",
                                      font=("Roboto", self._get_font_size(14)), bootstyle="warning")
                indicator.grid(row=0, column=2, padx=(2, 2), sticky="w")  # Индикатор сразу после заголовка
                self.formula_indicators[formula_title] = indicator
                progress = ttk.Label(title_frame, text=f"0/{len(fields)}", font=("Roboto", self._get_font_size(12)))
                progress.grid(row=0, column=3, padx=(0, 2), sticky="w")  # Прогресс сразу после индикатора
                self.formula_progress[formula_title] = progress
                # Убираем растяжение заголовка
                title_frame.grid_columnconfigure(1, weight=0)  # Отключаем растяжение для заголовка
                title_frame.grid_columnconfigure(2, weight=0)  # Отключаем растяжение для индикатора
                title_frame.grid_columnconfigure(3, weight=0)  # Отключаем растяжение для прогресса
                row += 1

                example = self._calculate_example(formula_title, fields)
                example_label = ttk.Label(self.input_frame, text=example,
                                          font=("Roboto", self._get_font_size(12), "italic"),
                                          bootstyle="secondary", wraplength=window_width - 50)  # Адаптивная обертка
                example_label.grid(row=row, column=0, columnspan=4, pady=(0, 5), sticky="ew")
                row += 1

                # Если формула развёрнута, добавляем описание и поля ввода
                if not self.collapsed_state.get(formula_title, False):
                    desc_label = ttk.Label(self.input_frame, text=formula_desc,
                                           font=("Roboto", self._get_font_size(12), "italic"),
                                           bootstyle="secondary", wraplength=window_width - 50)  # Адаптивная обертка
                    desc_label.grid(row=row, column=0, columnspan=4, pady=2, sticky="ew")
                    row += 1

                    if new_is_single_column:
                        # В узком режиме каждое поле на отдельной строке
                        for label_text, entry_name, tooltip in fields:
                            ttk.Label(self.input_frame, text=label_text, font=("Roboto", self._get_font_size(12))).grid(
                                row=row, column=0, padx=5, pady=2, sticky="w")
                            entry = ttk.Entry(self.input_frame, bootstyle="info")
                            entry.grid(row=row, column=1, columnspan=3, padx=5, pady=2, sticky="ew")  # Растягиваем поле
                            if entry_name in current_values:
                                entry.insert(0, current_values[entry_name])
                            entry.configure(validate="key", validatecommand=self.vcmd)
                            new_tooltip = f"{tooltip}\nФормат: Число > 0 (например, 0.1 или 5.5)" if self.current_lang == "ru" else f"{tooltip}\nFormat: Number > 0 (e.g., 0.1 or 5.5)"
                            ToolTip(entry, new_tooltip)
                            print(f"Применён ToolTip для {entry_name} с текстом: {new_tooltip}")  # Отладочный вывод
                            self.entries[entry_name] = entry
                            entry.bind("<KeyRelease>", lambda event, e=entry: self._on_entry_change(event, e))
                            entry.bind("<FocusOut>", lambda event, e=entry: self._on_entry_change(event, e))
                            row += 1
                    else:
                        # В широком режиме первые два поля на одной строке
                        field_row = row
                        ttk.Label(self.input_frame, text=fields[0][0], font=("Roboto", self._get_font_size(12))).grid(
                            row=field_row, column=0, padx=5, pady=2, sticky="w")
                        entry1 = ttk.Entry(self.input_frame, bootstyle="info")
                        entry1.grid(row=field_row, column=1, padx=5, pady=2, sticky="ew")  # Растягиваем поле
                        if fields[0][1] in current_values:
                            entry1.insert(0, current_values[fields[0][1]])
                        entry1.configure(validate="key", validatecommand=self.vcmd)
                        new_tooltip = f"{fields[0][2]}\nФормат: Число > 0 (например, 0.1 или 5.5)" if self.current_lang == "ru" else f"{fields[0][2]}\nFormat: Number > 0 (e.g., 0.1 or 5.5)"
                        ToolTip(entry1, new_tooltip)
                        print(f"Применён ToolTip для {fields[0][1]} с текстом: {new_tooltip}")  # Отладочный вывод
                        self.entries[fields[0][1]] = entry1
                        entry1.bind("<KeyRelease>", lambda event, e=entry1: self._on_entry_change(event, e))
                        entry1.bind("<FocusOut>", lambda event, e=entry1: self._on_entry_change(event, e))

                        ttk.Label(self.input_frame, text=fields[1][0], font=("Roboto", self._get_font_size(12))).grid(
                            row=field_row, column=2, padx=5, pady=2, sticky="w")
                        entry2 = ttk.Entry(self.input_frame, bootstyle="info")
                        entry2.grid(row=field_row, column=3, padx=5, pady=2, sticky="ew")
                        if fields[1][1] in current_values:
                            entry2.insert(0, current_values[fields[1][1]])
                        entry2.configure(validate="key", validatecommand=self.vcmd)
                        new_tooltip = f"{fields[1][2]}\nФормат: Число > 0 (например, 0.1 или 5.5)" if self.current_lang == "ru" else f"{fields[1][2]}\nFormat: Number > 0 (e.g., 0.1 or 5.5)"
                        ToolTip(entry2, new_tooltip)
                        print(f"Применён ToolTip для {fields[1][1]} с текстом: {new_tooltip}")  # Отладочный вывод
                        self.entries[fields[1][1]] = entry2
                        entry2.bind("<KeyRelease>", lambda event, e=entry2: self._on_entry_change(event, e))
                        entry2.bind("<FocusOut>", lambda event, e=entry2: self._on_entry_change(event, e))

                        # Если есть третье поле, добавляем его на следующей строке
                        if len(fields) > 2:
                            field_row += 1
                            ttk.Label(self.input_frame, text=fields[2][0],
                                      font=("Roboto", self._get_font_size(12))).grid(row=field_row, column=0, padx=5,
                                                                                     pady=2, sticky="w")
                            entry3 = ttk.Entry(self.input_frame, bootstyle="info")
                            entry3.grid(row=field_row, column=1, columnspan=3, padx=5, pady=2, sticky="ew")
                            if fields[2][1] in current_values:
                                entry3.insert(0, current_values[fields[2][1]])
                            entry3.configure(validate="key", validatecommand=self.vcmd)
                            new_tooltip = f"{fields[2][2]}\nФормат: Число > 0 (например, 0.1 или 5.5)" if self.current_lang == "ru" else f"{fields[2][2]}\nFormat: Number > 0 (e.g., 0.1 or 5.5)"
                            ToolTip(entry3, new_tooltip)
                            print(f"Применён ToolTip для {fields[2][1]} с текстом: {new_tooltip}")  # Отладочный вывод
                            self.entries[fields[2][1]] = entry3
                            entry3.bind("<KeyRelease>", lambda event, e=entry3: self._on_entry_change(event, e))
                            entry3.bind("<FocusOut>", lambda event, e=entry3: self._on_entry_change(event, e))

                        # Обновляем row на основе последней строки полей
                        row = field_row + 1

                # Добавляем разделитель после всей формулы
                separator = ttk.Separator(self.input_frame, orient="horizontal")
                separator.grid(row=row, column=0, columnspan=4, sticky="ew", pady=5)
                self.separators[formula_title] = separator
                row += 1  # Увеличиваем row после разделителя

            self.is_single_column = new_is_single_column

        # Настраиваем веса колонок для адаптивности
        for child in self.input_frame.winfo_children():
            if isinstance(child, ttk.Entry):
                child.grid_configure(sticky="ew")
            elif isinstance(child, ttk.Label) and not isinstance(child, ttk.Separator):
                child.grid_configure(sticky="w")
            elif isinstance(child, ttk.Separator) or isinstance(child, ttk.Frame):
                child.grid_configure(sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=0)
        self.input_frame.grid_columnconfigure(1, weight=1)  # Растяжение первого поля
        self.input_frame.grid_columnconfigure(2, weight=0)
        self.input_frame.grid_columnconfigure(3, weight=1)  # Растяжение второго поля
        self._update_scrollregion()
        self._check_fields()

        result_text_height = max(5, min(15, window_height // 60))
        self.result_text.configure(height=result_text_height)

    def _update_footer_layout(self):
        self.bottom_frame.update_idletasks()
        available_width = self.root.winfo_width() - 10
        current_width, row, col = 0, 0, 0
        for item in self.footer_items:
            item_width = item.winfo_reqwidth() + 10
            if current_width + item_width > available_width:
                row += 1
                col = 0
                current_width = 0
            item.grid(row=row, column=col, padx=5, pady=2, sticky="ew")
            current_width += item_width
            col += 1
        for i in range(col):
            self.bottom_frame.grid_columnconfigure(i, weight=1)

    def _on_entry_change(self, event, entry: ttk.Entry):
        value = entry.get().strip()
        self._update_entry_style(entry, value)
        self._check_fields()

    def _switch_theme(self, event=None):
        self.current_theme = self.theme_var.get()
        self.style.theme_use(self.current_theme)
        self.root.configure(bg=self.style.colors.bg)
        self.canvas.configure(bg=self.style.colors.bg)
        self.result_text.configure(bg=self.style.colors.inputbg, fg=self.style.colors.inputfg)
        self.status_text.configure(bg=self.style.colors.inputbg, fg=self.style.colors.inputfg)
        self._save_ui_state()

    def _switch_language(self, event):
        self.current_lang = self.lang_var.get()
        self._update_texts()
        self.update_layout(force_update=True)
        self._save_ui_state()

    def _check_fields(self, *args):
        if not self.entries:
            self.calculate_button.configure(state="disabled")
            return

        fully_filled_formulas = []
        for formula_title, _, fields in FORMULAS[self.current_lang]:
            filled_fields = 0
            total_fields = len(fields)
            for _, entry_name, _ in fields:
                if entry_name in self.entries and isinstance(self.entries[entry_name], ttk.Entry):
                    value = self.entries[entry_name].get().strip()
                    if value and self._validate_entry(value):
                        filled_fields += 1
                    self._update_entry_style(self.entries[entry_name], value)
            if filled_fields == total_fields:
                fully_filled_formulas.append(formula_title)
            indicator = self.formula_indicators.get(formula_title)
            progress = self.formula_progress.get(formula_title)
            if indicator and progress:
                filled = filled_fields == total_fields
                indicator.configure(text="✓" if self.current_lang == "ru" else "✓" if filled else "*" if self.current_lang == "ru" else "*",
                                    bootstyle="success" if filled else "warning")
                progress.configure(text=f"{filled_fields}/{total_fields}")
                title_label = indicator.master.winfo_children()[1]
                title_label.configure(bootstyle="success-bold" if filled else "primary-bold")

        self.calculate_button.configure(state="normal" if fully_filled_formulas else "disabled")
        logging.debug(f"Fully filled formulas: {fully_filled_formulas}")

    def _on_configure(self, event):
        if event.widget == self.root and (abs(event.width - self.last_width) > 10 or abs(event.height - self.last_height) > 10):
            self.last_width = event.width
            self.last_height = event.height
            if not self.update_pending:
                self.update_pending = True
                self.after_id = self.root.after(100, self._debounced_update)

    def _debounced_update(self):
        self.update_layout()
        self._update_footer_layout()
        self.update_pending = False
        self._save_ui_state()

    def _toggle_collapse(self, formula_title: str):
        self.collapsed_state[formula_title] = not self.collapsed_state.get(formula_title, False)
        self.update_layout(force_update=True)
        self._save_ui_state()
        self.data_manager.save_collapsed_state(self.collapsed_state)

    def calculate(self):
        if not self.entries:
            self.status_text.configure(state="normal")
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END,
                                    "Нет данных для расчёта\n" if self.current_lang == "ru" else "No data for calculation\n")
            self.status_text.configure(state="disabled")
            return

        invalid_fields = []
        zero_fields = []
        for entry_name, entry in self.entries.items():
            if not isinstance(entry, ttk.Entry):
                continue
            value = entry.get().strip()
            if value:
                try:
                    num = float(value)
                    if num == 0:
                        zero_fields.append(entry_name)
                        continue
                except ValueError:
                    pass
                if not self._validate_entry(value):
                    invalid_fields.append(entry_name)
        if invalid_fields or zero_fields:
            msg = ""
            if invalid_fields:
                msg += "Исправьте значения в полях: " + ", ".join(invalid_fields)
            if zero_fields:
                if msg:
                    msg += "\n"
                msg += "Значения не могут быть равны 0 в полях: " + ", ".join(zero_fields)
            self.status_text.configure(state="normal")
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, msg + "\n", "danger")
            self.status_text.configure(state="disabled")
            return

        results, notifications = calculate_metrics(self.entries, self.current_lang)
        self.last_results = results
        self._display_results(results, notifications)
        self.data_manager.add_to_history(self.entries, self.result_text.get(1.0, tk.END).strip())
        self.data_manager.save_history()

    def _display_results(self, results, notifications):
        self.result_text.configure(state="normal")
        self.result_text.delete(1.0, tk.END)
        if results:
            for title, value, tag in results:
                self.result_text.insert(tk.END, f"{title}: ", "default")
                self.result_text.insert(tk.END, f"{value}\n", tag)
        else:
            self.result_text.insert(tk.END, "Нет рассчитанных метрик" if self.current_lang == "ru" else "No calculated metrics", "warning")
        self.result_text.configure(state="disabled")

        self.status_text.configure(state="normal")
        self.status_text.delete(1.0, tk.END)
        from datetime import datetime
        timestamp = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        self.status_text.insert(tk.END, f"Последний расчёт: {timestamp}\n" if self.current_lang == "ru" else f"Last calculation: {timestamp}\n")
        if notifications:
            for i, (msg, tag) in enumerate(notifications):
                self.status_text.insert(tk.END, msg, tag)
                if i < len(notifications) - 1:
                    self.status_text.insert(tk.END, " | ")
        self.status_text.configure(state="disabled")

    def show_chart(self):
        if not hasattr(self, "last_results") or not self.last_results:
            self.status_text.configure(state="normal")
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END,
                                    "Нет данных для графика\n" if self.current_lang == "ru" else "No data for chart\n",
                                    "warning")
            self.status_text.configure(state="disabled")
            return

        self.chart_window = tk.Toplevel(self.root)
        self.chart_window.title("График метрик" if self.current_lang == "ru" else "Metrics Chart")
        self.chart_window.geometry("800x600")

        control_frame = ttk.Frame(self.chart_window, padding=5)
        control_frame.pack(fill="x")

        ttk.Label(control_frame, text="Тип графика:" if self.current_lang == "ru" else "Chart Type:").pack(side="left",
                                                                                                           padx=5)
        chart_types = [
            ("Столбчатая диаграмма", "bar"),
            ("Линейный график", "line"),
            ("Круговая диаграмма", "pie"),
            ("Гистограмма", "histogram")
        ]
        ttk.OptionMenu(control_frame, self.chart_type, "bar", *[t[1] for t in chart_types],
                       command=lambda x: self._update_chart()).pack(side="left", padx=5)

        self.checkbox_frame = ttk.Frame(control_frame, padding=5)
        self.checkbox_frame.pack(side="left", fill="x", expand=True)

        self.metric_vars = {}
        for title, _, _ in self.last_results:
            self.metric_vars[title] = tk.IntVar(value=1)
            ttk.Checkbutton(self.checkbox_frame, text=title, variable=self.metric_vars[title]).pack(side="left", padx=2)

        update_button = ttk.Button(control_frame,
                                   text="Обновить график" if self.current_lang == "ru" else "Update Chart",
                                   command=self._update_chart, bootstyle="success")
        update_button.pack(side="right", padx=5)

        save_button = ttk.Button(control_frame, text="Сохранить график" if self.current_lang == "ru" else "Save Chart",
                                 command=self._save_chart, bootstyle="primary")
        save_button.pack(side="right", padx=5)

        self.chart_frame = ttk.Frame(self.chart_window)
        self.chart_frame.pack(fill="both", expand=True)

        self._update_chart()

    def _update_chart(self):
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
            self.chart_canvas = None
        if self.chart_fig:
            plt.close(self.chart_fig)
            self.chart_fig = None

        selected_metrics = [title for title, _, _ in self.last_results if self.metric_vars[title].get() == 1]
        logging.debug(f"Selected metrics: {selected_metrics}")
        if not selected_metrics:
            self.status_text.configure(state="normal")
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END,
                                    "Выберите хотя бы одну метрику\n" if self.current_lang == "ru" else "Select at least one metric\n",
                                    "warning")
            self.status_text.configure(state="disabled")
            return

        # Используем новую функцию из charts.py
        self.chart_canvas, self.chart_fig = show_chart(
            parent=self.chart_frame,
            results=self.last_results,
            chart_type=self.chart_type.get(),
            selected_metrics=selected_metrics,
            lang=self.current_lang,
            custom_colors=['#FF9999', '#66B3FF', '#99FF99', '#FF99FF', '#FFCC99'],  # Пользовательские цвета
            font_size=10,
            figsize=(10, 5)
        )

        if not self.chart_canvas or not self.chart_fig:
            self.status_text.configure(state="normal")
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END,
                                    "Ошибка отображения графика\n" if self.current_lang == "ru" else "Chart display error\n",
                                    "danger")
            self.status_text.configure(state="disabled")

    def _save_chart(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg"), ("All files", "*.*")],
            title="Сохранить график как" if self.current_lang == "ru" else "Save Chart As"
        )
        if file_path:
            if self.chart_fig:
                if file_path.endswith('.pdf'):
                    self.chart_fig.savefig(file_path, format='pdf', dpi=300, bbox_inches='tight')
                elif file_path.endswith('.svg'):
                    self.chart_fig.savefig(file_path, format='svg', bbox_inches='tight')
                else:
                    self.chart_fig.savefig(file_path, dpi=300, bbox_inches='tight')
                self.status_text.configure(state="normal")
                self.status_text.delete(1.0, tk.END)
                self.status_text.insert(tk.END, "График сохранён как {}\n".format(file_path) if self.current_lang == "ru" else "Chart saved as {}\n".format(file_path), "success")
                self.status_text.configure(state="disabled")

    def copy_results(self):
        try:
            result_text = self.result_text.get(1.0, tk.END).strip()
            if result_text:
                pyperclip.copy(result_text)
                self.status_text.configure(state="normal")
                self.status_text.delete(1.0, tk.END)
                self.status_text.insert(tk.END, "Результаты скопированы в буфер обмена\n" if self.current_lang == "ru" else "Results copied to clipboard\n", "success")
            else:
                self.status_text.configure(state="normal")
                self.status_text.delete(1.0, tk.END)
                self.status_text.insert(tk.END, "Нет результатов для копирования\n" if self.current_lang == "ru" else "No results to copy\n", "warning")
            self.status_text.configure(state="disabled")
        except Exception as e:
            self.status_text.configure(state="normal")
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"Ошибка копирования: {e}\n" if self.current_lang == "ru" else f"Copy error: {e}\n", "danger")
            self.status_text.configure(state="disabled")

    def clear(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Entry):
                entry.delete(0, tk.END)
                self._update_entry_style(entry, "")
        self.result_text.configure(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.configure(state="disabled")
        self.status_text.configure(state="normal")
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, "Все поля очищены" if self.current_lang == "ru" else "All fields cleared")
        self.status_text.configure(state="disabled")
        self._check_fields()

    def save(self):
        try:
            logging.debug(f"Entries before save: {self.entries}")
            entries_data = {name: entry.get().strip() for name, entry in self.entries.items() if isinstance(entry, ttk.Entry)}
            logging.debug(f"Filtered entries_data for save: {entries_data}")
            status = self.data_manager.save(entries_data, self.result_text.get(1.0, tk.END).strip(), self.current_lang)
            self.status_text.configure(state="normal")
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, status, "success" if "успешно" in status or "successfully" in status else "warning")
        except IOError as e:
            self.status_text.configure(state="normal")
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"Ошибка сохранения: {e}\n" if self.current_lang == "ru" else f"Save error: {e}\n", "danger")
        finally:
            self.status_text.configure(state="disabled")

    def load(self):
        try:
            logging.debug("Starting load operation")
            loaded_data, status = self.data_manager.load(self.entries, self.result_text, self.current_lang)
            logging.debug(f"Loaded data: {loaded_data}, Status: {status}")
            if not loaded_data and not status:
                raise ValueError("Файл пуст или содержит некорректные данные")
            if "файл пуст" in status.lower() or "empty file" in status.lower():
                self.status_text.configure(state="normal")
                self.status_text.delete(1.0, tk.END)
                self.status_text.insert(tk.END, status + "\n", "warning")
            elif "некорректные данные" in status.lower() or "invalid data" in status.lower():
                self.status_text.configure(state="normal")
                self.status_text.delete(1.0, tk.END)
                self.status_text.insert(tk.END, status + "\n", "danger")
            else:
                logging.debug(f"Entries before update: {self.entries}")
                for entry_name, value in loaded_data.items():
                    if entry_name in self.entries and isinstance(self.entries[entry_name], ttk.Entry):
                        self.entries[entry_name].delete(0, tk.END)
                        self.entries[entry_name].insert(0, value)
                logging.debug(f"Entries after update: {self.entries}")
                self._check_fields()
                self.status_text.configure(state="normal")
                self.status_text.delete(1.0, tk.END)
                self.status_text.insert(tk.END, status, "success")
        except FileNotFoundError as e:
            self.status_text.configure(state="normal")
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"Файл не найден: {e}\n" if self.current_lang == "ru" else f"File not found: {e}\n", "danger")
        except IOError as e:
            self.status_text.configure(state="normal")
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"Ошибка ввода-вывода: {e}\n" if self.current_lang == "ru" else f"IO error: {e}\n", "danger")
        except ValueError as e:
            self.status_text.configure(state="normal")
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"Ошибка данных: {e}\n" if self.current_lang == "ru" else f"Data error: {e}\n", "danger")
        finally:
            self.status_text.configure(state="disabled")

    def _show_history(self):
        self.data_manager.show_history(self.root, self.entries, self.result_text, self.current_lang, self._check_fields)

    def _update_texts(self):
        self.lang_menu.configure(text="ru" if self.current_lang == "ru" else "en")
        self.calculate_button.configure(text="Рассчитать" if self.current_lang == "ru" else "Calculate")
        self.button_frame.winfo_children()[1].configure(text="Очистить" if self.current_lang == "ru" else "Clear")
        self.result_header_frame.winfo_children()[1].configure(text="Показать график" if self.current_lang == "ru" else "Show Chart")
        self.result_header_frame.winfo_children()[2].configure(text="Копировать результаты" if self.current_lang == "ru" else "Copy Results")
        for i, text in enumerate([
            "Сохранить в файл", "Загрузить из файла"
        ] if self.current_lang == "ru" else [
            "Save to File", "Load from File"
        ]):
            self.footer_items[i].configure(text=text)
        self.top_frame.winfo_children()[2].configure(text="История" if self.current_lang == "ru" else "History")
        self.result_header_frame.winfo_children()[0].configure(text="Результаты:" if self.current_lang == "ru" else "Results:")

    def _on_closing(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
        self.data_manager.save_collapsed_state(self.collapsed_state)
        self.data_manager.save_history()
        self._save_ui_state()
        self.root.destroy()
        import sys
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()