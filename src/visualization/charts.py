# src/visualization/charts.py
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import ttkbootstrap as ttk
from typing import Dict, List, Tuple, Optional
import logging

def show_chart(
    parent: ttk.Frame,
    results: List[Tuple[str, str, str]],
    chart_type: str,
    selected_metrics: List[str],
    lang: str,
    custom_colors: Optional[List[str]] = None,
    font_size: int = 10,
    figsize: Tuple[int, int] = (10, 5)
) -> Tuple[Optional[FigureCanvasTkAgg], Optional[plt.Figure]]:
    """
    Отображает график метрик в заданном родительском окне.

    Args:
        parent (ttk.Frame): Родительский фрейм для отображения графика.
        results (List[Tuple[str, str, str]]): Список результатов (название, значение, тег стиля).
        chart_type (str): Тип графика ('bar', 'line', 'pie', 'histogram').
        selected_metrics (List[str]): Список выбранных метрик для отображения.
        lang (str): Язык интерфейса ('ru' или 'en').
        custom_colors (Optional[List[str]]): Список пользовательских цветов для графика.
        font_size (int): Размер шрифта для текста на графике.
        figsize (Tuple[int, int]): Размер фигуры (ширина, высота).

    Returns:
        Tuple[Optional[FigureCanvasTkAgg], Optional[plt.Figure]]: Кортеж из канваса и фигуры matplotlib.
    """
    # Очистка старого содержимого
    for widget in parent.winfo_children():
        widget.destroy()

    if not selected_metrics:
        logging.warning("No metrics selected for chart.")
        return None, None

    # Фильтрация значений для выбранных метрик
    metric_values = {title: value for title, value, _ in results if title in selected_metrics}
    values = [metric_values[title] for title in selected_metrics]
    logging.debug(f"Values for chart: {values}")

    # Извлечение числовых значений
    numeric_values = []
    for value in values:
        try:
            numeric_part = value.replace("%", "").replace("$", "").strip().split()[0]
            numeric_values.append(float(numeric_part))
        except (ValueError, IndexError):
            numeric_values.append(0)

    logging.debug(f"Numeric values: {numeric_values}")

    if len(selected_metrics) != len(numeric_values):
        logging.error("Chart data synchronization error.")
        return None, None

    # Нормализация значений (для столбчатых и линейных графиков)
    max_value = max(numeric_values) if numeric_values else 1
    normalized_values = [v / max_value * 100 if max_value > 0 else 0 for v in numeric_values]
    logging.debug(f"Normalized values: {normalized_values}")

    # Настройка стилей
    default_colors = custom_colors or ['#FF9999', '#99FF99', '#9999FF', '#FF99FF', '#99FFFF']
    plt.rcParams.update({'font.size': font_size})

    # Создание графика
    fig, ax = plt.subplots(figsize=figsize)

    # Выбор типа графика
    if chart_type == "bar":
        bars = ax.bar(
            selected_metrics,
            normalized_values,
            color=[default_colors[i % len(default_colors)] for i in range(len(selected_metrics))]
        )
        for bar, orig_value in zip(bars, numeric_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, f'{orig_value:.2f}',
                    ha='center', va='bottom')
        ax.set_ylim(0, 110)
        ax.set_ylabel("Нормализованное значение (%)" if lang == "ru" else "Normalized Value (%)")

    elif chart_type == "line":
        ax.plot(
            selected_metrics,
            normalized_values,
            marker='o',
            color=default_colors[0],
            label='Normalized Values',
            linestyle='--',
            linewidth=2
        )
        for i, (x, y) in enumerate(zip(selected_metrics, normalized_values)):
            ax.text(x, y, f'{numeric_values[i]:.2f}', ha='center', va='bottom')
        ax.legend()
        ax.set_ylim(0, 110)
        ax.set_ylabel("Нормализованное значение (%)" if lang == "ru" else "Normalized Value (%)")

    elif chart_type == "pie":
        ax.pie(
            numeric_values,
            labels=selected_metrics,
            colors=[default_colors[i % len(default_colors)] for i in range(len(selected_metrics))],
            autopct='%1.1f%%',
            startangle=140
        )
        ax.axis('equal')  # Круговая диаграмма должна быть круглой

    elif chart_type == "histogram":
        ax.hist(
            numeric_values,
            bins=min(len(numeric_values), 10),
            color=default_colors[0],
            edgecolor='black'
        )
        ax.set_xlabel("Значения" if lang == "ru" else "Values")
        ax.set_ylabel("Частота" if lang == "ru" else "Frequency")

    else:
        logging.error(f"Unsupported chart type: {chart_type}")
        return None, None

    # Общие настройки графика
    ax.set_title("Метрики (Нормализованные)" if lang == "ru" else "Metrics (Normalized)")
    plt.xticks(rotation=45, ha="right")

    # Создание канваса
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # Добавление панели инструментов
    toolbar = NavigationToolbar2Tk(canvas, parent)
    toolbar.update()

    # Корректировка компоновки
    plt.tight_layout()

    return canvas, fig