# src/core/calculations.py
import logging
from typing import Dict, List, Tuple
from src.core.formulas import FORMULAS
import ttkbootstrap as ttk

def calculate_metrics(entries: Dict[str, ttk.Entry], lang: str) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str]]]:
    """
    Выполняет расчёты маркетинговых метрик на основе введённых данных.

    Args:
        entries (Dict[str, ttk.Entry]): Словарь с именами полей и соответствующими объектами ttk.Entry.
        lang (str): Язык интерфейса ('ru' или 'en').

    Returns:
        Tuple[List[Tuple[str, str, str]], List[Tuple[str, str]]]: Список результатов (название, значение + описание, тег стиля)
            и список уведомлений (сообщение, тег стиля).
    """
    results = []
    notifications = []
    logging.info(f"Calculating metrics for language: {lang}")

    try:
        # Извлечение значений
        values = {}
        expected_keys = [
            "ctr_impressions", "ctr_clicks", "cpc_total_cost", "cpc_clicks",
            "cpa_total_cost", "cpa_actions", "roas_revenue", "roas_total_cost",
            "cr_clicks", "cr_conversions", "ltv_avg_revenue", "ltv_purchases",
            "ltv_period", "cpl_total_cost", "cpl_leads", "rpm_revenue", "rpm_impressions"
        ]
        for key in expected_keys:
            entry = entries.get(key)
            if entry:
                value = entry.get().strip()
                try:
                    values[key] = float(value) if value else None
                except (ValueError, AttributeError) as e:
                    logging.error(f"Error extracting value for {key}: {e}")
                    values[key] = None
            else:
                values[key] = None
                logging.warning(f"No entry found for {key}")
        logging.debug(f"Extracted values: {values}")

        # Функция для определения стиля на основе значения
        def get_style(value: float, thresholds: dict) -> Tuple[str, str]:
            if value >= thresholds.get("very_good", float('inf')):
                return "very_good", "Очень хорошо" if lang == "ru" else "Very Good"
            elif value >= thresholds.get("success", float('inf')):
                return "success", "Хорошо" if lang == "ru" else "Good"
            elif value >= thresholds.get("warning", float('-inf')):
                return "warning", "Нормально" if lang == "ru" else "Normal"
            else:
                return "danger", "Плохо" if lang == "ru" else "Poor"

        # Расчёты метрик
        for formula_title, _, fields in FORMULAS[lang]:
            required_values = {entry_name: values[entry_name] for _, entry_name, _ in fields}
            all_filled = all(v is not None for v in required_values.values())
            has_zeros = any(v == 0 for v in required_values.values() if v is not None)

            if all_filled and not has_zeros:
                logging.info(f"Calculating {formula_title} with values: {required_values}")
                if formula_title in ["CTR (Кликабельность)", "CTR (Click-Through Rate)"]:
                    ctr = (required_values["ctr_clicks"] / required_values["ctr_impressions"]) * 100
                    tag, desc = get_style(ctr, {"very_good": 10, "success": 5, "warning": 2})
                    results.append((formula_title, f"{ctr:.2f}% ({desc})", tag))

                elif formula_title in ["CPC (Стоимость за клик)", "CPC (Cost Per Click)"]:
                    cpc = required_values["cpc_total_cost"] / required_values["cpc_clicks"]
                    tag, desc = get_style(cpc, {"very_good": 1, "success": 2, "warning": 5, "danger": float('inf')})
                    results.append((formula_title, f"${cpc:.2f} ({desc})", tag))

                elif formula_title in ["CPA (Стоимость за действие)", "CPA (Cost Per Action)"]:
                    cpa = required_values["cpa_total_cost"] / required_values["cpa_actions"]
                    tag, desc = get_style(cpa, {"very_good": 10, "success": 20, "warning": 50, "danger": float('inf')})
                    results.append((formula_title, f"${cpa:.2f} ({desc})", tag))

                elif formula_title in ["ROAS (Возврат затрат)", "ROAS (Return on Ad Spend)"]:
                    roas = required_values["roas_revenue"] / required_values["roas_total_cost"]
                    tag, desc = get_style(roas, {"very_good": 5, "success": 2, "warning": 1, "danger": float('-inf')})
                    results.append((formula_title, f"{roas:.2f} ({desc})", tag))

                elif formula_title in ["CR (Конверсия)", "CR (Conversion Rate)"]:
                    cr = (required_values["cr_conversions"] / required_values["cr_clicks"]) * 100
                    tag, desc = get_style(cr, {"very_good": 10, "success": 5, "warning": 2})
                    results.append((formula_title, f"{cr:.2f}% ({desc})", tag))

                elif formula_title in ["LTV (Пожизненная ценность клиента)", "LTV (Lifetime Value)"]:
                    ltv = required_values["ltv_avg_revenue"] * required_values["ltv_purchases"] * required_values["ltv_period"]
                    tag, desc = get_style(ltv, {"very_good": 1000, "success": 500, "warning": 100})
                    results.append((formula_title, f"${ltv:.2f} ({desc})", tag))

                elif formula_title in ["CPL (Стоимость за лид)", "CPL (Cost Per Lead)"]:
                    cpl = required_values["cpl_total_cost"] / required_values["cpl_leads"]
                    tag, desc = get_style(cpl, {"very_good": 5, "success": 10, "warning": 20, "danger": float('inf')})
                    results.append((formula_title, f"${cpl:.2f} ({desc})", tag))

                elif formula_title in ["RPM (Доход на тысячу показов)", "RPM (Revenue Per Mille)"]:
                    rpm = (required_values["rpm_revenue"] / required_values["rpm_impressions"]) * 1000
                    tag, desc = get_style(rpm, {"very_good": 50, "success": 20, "warning": 10})
                    results.append((formula_title, f"${rpm:.2f} ({desc})", tag))

            elif any(v is not None for v in required_values.values()):
                notifications.append((f"Незаполненные поля для {formula_title}", "warning"))

    except Exception as e:
        logging.error(f"Unexpected error in calculation: {e}")
        for title, _, _ in FORMULAS[lang]:
            results.append((title, "Ошибка", "danger"))
        notifications.append(("Неизвестная ошибка", "danger"))

    return results, notifications