import re
import logging

def validate_number(action: str, value: str, text: str, prior: str) -> bool:
    """Валидация ввода чисел: только положительные десятичные числа с максимум 2 знаками после точки."""
    logging.debug(f"Validating: action={action}, value={value}, text={text}, prior={prior}")

    # Разрешаем удаление символов
    if action == "0":  # 0 означает удаление
        return True

    # Разрешаем пустое поле
    if not value:
        return True

    # Явно отклоняем "0", "0.0", "0.00"
    if value in ("0", "0.0", "0.00"):
        logging.debug(f"Validation failed: Zero value '{value}' not allowed")
        return False

    # Проверяем итоговое значение
    try:
        num = float(value)
        if num < 0:
            logging.debug(f"Validation failed: Negative value '{value}'")
            return False
        # Проверяем количество знаков после точки
        if '.' in value:
            decimal_part = value.split('.')[1].rstrip('0')
            decimal_places = len(decimal_part)
            if decimal_places > 2:
                logging.debug(f"Validation failed: Too many decimal places in '{value}'")
                return False
    except ValueError:
        logging.debug(f"Validation failed: Not a number '{value}'")
        return False

    return True