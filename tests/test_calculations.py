# tests/test_calculations.py
import unittest
import ttkbootstrap as ttk
from src.core.calculations import calculate_metrics
from src.core.formulas import FORMULAS
import logging
from io import StringIO
from contextlib import redirect_stderr

class TestCalculateMetrics(unittest.TestCase):
    def setUp(self):
        # Создаём тестовые ttk.Entry объекты
        self.entries = {
            "ctr_impressions": ttk.Entry(),
            "ctr_clicks": ttk.Entry(),
            "cpc_total_cost": ttk.Entry(),
            "cpc_clicks": ttk.Entry(),
            "cpa_total_cost": ttk.Entry(),
            "cpa_actions": ttk.Entry(),
            "roas_revenue": ttk.Entry(),
            "roas_total_cost": ttk.Entry(),
            "cr_clicks": ttk.Entry(),
            "cr_conversions": ttk.Entry(),
            "ltv_avg_revenue": ttk.Entry(),
            "ltv_purchases": ttk.Entry(),
            "ltv_period": ttk.Entry(),
            "cpl_total_cost": ttk.Entry(),
            "cpl_leads": ttk.Entry(),
            "rpm_revenue": ttk.Entry(),
            "rpm_impressions": ttk.Entry()
        }
        # Настройка перехвата логов
        self.log_stream = StringIO()
        self.log_handler = logging.StreamHandler(self.log_stream)
        logging.getLogger().addHandler(self.log_handler)
        # Убедимся, что корневой логгер настроен
        logging.getLogger().setLevel(logging.DEBUG)

    def tearDown(self):
        # Очистка после тестов
        logging.getLogger().removeHandler(self.log_handler)
        self.log_stream.close()

    def set_entry_values(self, values: dict):
        """Устанавливает значения в поля ввода."""
        for key, value in values.items():
            self.entries[key].delete(0, ttk.END)
            self.entries[key].insert(0, str(value))

    def test_calculate_ctr(self):
        self.set_entry_values({"ctr_impressions": 1000, "ctr_clicks": 100})
        results, notifications = calculate_metrics(self.entries, "ru")
        self.assertTrue(any(r[0] == "CTR (Кликабельность)" and "10.00%" in r[1] and "Очень хорошо" in r[1] for r in results))

    def test_calculate_cpc(self):
        self.set_entry_values({"cpc_total_cost": 100, "cpc_clicks": 50})
        results, notifications = calculate_metrics(self.entries, "ru")
        self.assertTrue(any(r[0] == "CPC (Стоимость за клик)" and "2.00" in r[1] and "Нормально" in r[1] for r in results))

    def test_calculate_cpa(self):
        self.set_entry_values({"cpa_total_cost": 200, "cpa_actions": 10})
        results, notifications = calculate_metrics(self.entries, "ru")
        self.assertTrue(any(r[0] == "CPA (Стоимость за действие)" and "20.00" in r[1] and "Нормально" in r[1] for r in results))

    def test_calculate_roas(self):
        self.set_entry_values({"roas_revenue": 500, "roas_total_cost": 100})
        results, notifications = calculate_metrics(self.entries, "ru")
        self.assertTrue(any(r[0] == "ROAS (Возврат затрат)" and "5.00" in r[1] and "Очень хорошо" in r[1] for r in results))

    def test_calculate_cr(self):
        self.set_entry_values({"cr_clicks": 100, "cr_conversions": 20})
        results, notifications = calculate_metrics(self.entries, "ru")
        self.assertTrue(any(r[0] == "CR (Конверсия)" and "20.00%" in r[1] and "Очень хорошо" in r[1] for r in results))

    def test_calculate_ltv(self):
        self.set_entry_values({"ltv_avg_revenue": 50, "ltv_purchases": 3, "ltv_period": 2})
        results, notifications = calculate_metrics(self.entries, "ru")
        self.assertTrue(any(r[0] == "LTV (Пожизненная ценность клиента)" and "300.00" in r[1] and "Нормально" in r[1] for r in results))

    def test_calculate_cpl(self):
        self.set_entry_values({"cpl_total_cost": 100, "cpl_leads": 20})
        results, notifications = calculate_metrics(self.entries, "ru")
        self.assertTrue(any(r[0] == "CPL (Стоимость за лид)" and "5.00" in r[1] and "Хорошо" in r[1] for r in results))

    def test_calculate_rpm(self):
        self.set_entry_values({"rpm_revenue": 100, "rpm_impressions": 10000})
        results, notifications = calculate_metrics(self.entries, "ru")
        self.assertTrue(any(r[0] == "RPM (Доход на тысячу показов)" and "10.00" in r[1] and "Нормально" in r[1] for r in results))

    def test_missing_fields(self):
        self.set_entry_values({"ctr_impressions": 1000})
        results, notifications = calculate_metrics(self.entries, "ru")
        self.assertTrue(any("Незаполненные поля для CTR (Кликабельность)" in n[0] for n in notifications))

    def test_invalid_input(self):
        self.set_entry_values({"ctr_impressions": "invalid", "ctr_clicks": 100})
        results, notifications = calculate_metrics(self.entries, "ru")
        self.assertEqual(len(results), 0)
        log_output = self.log_stream.getvalue()
        self.assertIn("could not convert string to float", log_output)

    def test_zero_values(self):
        self.set_entry_values({"ctr_impressions": 1000, "ctr_clicks": 0})
        results, notifications = calculate_metrics(self.entries, "ru")
        self.assertEqual(len(results), 0)
        log_output = self.log_stream.getvalue()
        self.assertIn("Zero value", log_output)

        self.set_entry_values({"ctr_impressions": 1000, "ctr_clicks": "0.0"})
        results, notifications = calculate_metrics(self.entries, "ru")
        self.assertEqual(len(results), 0)
        log_output = self.log_stream.getvalue()
        self.assertIn("Zero value", log_output)

if __name__ == "__main__":
    unittest.main()