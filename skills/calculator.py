import re
import math
from utils.logger import logger


class CalculatorSkill:
    """Навык: калькулятор."""

    def __init__(self):
        self.safe_globals = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'pow': pow,
            '__builtins__': {}
        }

        # Безопасные математические функции.
        self.safe_globals.update({
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'pi': math.pi,
            'e': math.e
        })

    def calculate(self, expression: str) -> str:
        """Вычислить математическое выражение."""
        try:
            # Очищаем выражение.
            expr = expression.lower()

            # Заменяем русские слова на операторы.
            replacements = {
                'плюс': '+',
                'минус': '-',
                'умножить на': '*',
                'разделить на': '/',
                'делить на': '/',
                'в степени': '**',
                'степени': '**',
                'корень из': 'sqrt',
                'квадратный корень из': 'sqrt',
                'синус': 'sin',
                'косинус': 'cos',
                'тангенс': 'tan',
                'логарифм': 'log'
            }

            for rus, eng in replacements.items():
                expr = expr.replace(rus, eng)

            # Удаляем лишние слова.
            expr = re.sub(r'[^\d+\-*/().sqrt sincostanlog^]', '', expr)

            # Заменяем ^ на ** для возведения в степень.
            expr = expr.replace('^', '**')

            # Проверяем безопасность выражения.
            if not self._is_safe(expr):
                return "Выражение содержит небезопасные символы"

            # Вычисляем.
            result = eval(expr, {"__builtins__": {}}, self.safe_globals)

            logger.info(f"Calculator: {expression} = {result}")
            return f"Результат: {result}"

        except ZeroDivisionError:
            return "Ошибка: деление на ноль"
        except Exception as e:
            logger.error(f"Calculator error: {e}")
            return f"Не удалось вычислить выражение: {expression}"

    def _is_safe(self, expr: str) -> bool:
        """Проверка выражения на безопасность."""
        # Разрешенные символы.
        safe_pattern = r'^[\d+\-*/().\ssqrt sincostanlog]+$'

        # Проверяем наличие потенциально опасных конструкций.
        dangerous = ['import', 'exec', 'eval', 'open', 'file', '__']

        if not re.match(safe_pattern, expr.replace(' ', '')):
            return False

        for danger in dangerous:
            if danger in expr.lower():
                return False

        return True

    def process(self, command: str) -> str:
        """Обработать команду калькулятора."""
        # Извлекаем выражение из команды.
        triggers = ['посчитай', 'сколько будет', 'вычисли', 'калькулятор']

        for trigger in triggers:
            if trigger in command.lower():
                expression = command.lower().split(trigger)[-1].strip()
                return self.calculate(expression)

        # Если триггеры не найдены, пытаемся вычислить напрямую.
        return self.calculate(command)
