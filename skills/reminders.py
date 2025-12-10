import sqlite3
from datetime import datetime, timedelta
import re
from typing import List, Dict, Any
from utils.logger import logger


class RemindersSkill:
    """Навык: напоминания."""

    def __init__(self, db_path: str = "data/assistant.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Инициализация базы данных для напоминаний."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    time TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    is_completed BOOLEAN DEFAULT 0
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("Reminders database initialized")

        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    def add_reminder(self, text: str, reminder_time: str) -> str:
        """Добавить напоминание."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                "INSERT INTO reminders (text, time, created_at) VALUES (?, ?, ?)",
                (text, reminder_time, created_at)
            )

            conn.commit()
            reminder_id = cursor.lastrowid
            conn.close()

            logger.info(f"Reminder added: {text} at {reminder_time}")
            return f"Напоминание добавлено: '{text}' на {reminder_time}"

        except Exception as e:
            logger.error(f"Add reminder error: {e}")
            return f"Ошибка добавления напоминания: {e}"

    def parse_time(self, text: str) -> str:
        """Разобрать время из текста."""
        now = datetime.now()

        # Через X минут/часов.
        minutes_match = re.search(r'через\s*(\d+)\s*минут', text.lower())
        hours_match = re.search(r'через\s*(\d+)\s*час', text.lower())

        if minutes_match:
            minutes = int(minutes_match.group(1))
            reminder_time = now + timedelta(minutes=minutes)
            return reminder_time.strftime("%H:%M")

        if hours_match:
            hours = int(hours_match.group(1))
            reminder_time = now + timedelta(hours=hours)
            return reminder_time.strftime("%H:%M")

        # Конкретное время (в 15:30, в 3 часа).
        time_match = re.search(r'в\s*(\d{1,2})(?::(\d{2}))?\s*(часов|часа|час)?', text.lower())
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0

            # Ограничиваем значения.
            hour = min(max(hour, 0), 23)
            minute = min(max(minute, 0), 59)

            reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Если указанное время уже прошло сегодня, ставим на завтра.
            if reminder_time < now:
                reminder_time += timedelta(days=1)

            return reminder_time.strftime("%H:%M")

        # Если время не распознано, ставим через 1 час по умолчанию.
        default_time = now + timedelta(hours=1)
        return default_time.strftime("%H:%M")

    def get_pending_reminders(self) -> List[Dict[str, Any]]:
        """Получить активные напоминания."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, text, time FROM reminders WHERE is_completed = 0 ORDER BY time"
            )

            reminders = []
            for row in cursor.fetchall():
                reminders.append({
                    'id': row[0],
                    'text': row[1],
                    'time': row[2]
                })

            conn.close()
            return reminders

        except Exception as e:
            logger.error(f"Get reminders error: {e}")
            return []

    def mark_completed(self, reminder_id: int) -> bool:
        """Отметить напоминание как выполненное."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE reminders SET is_completed = 1 WHERE id = ?",
                (reminder_id,)
            )

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Mark completed error: {e}")
            return False

    def process(self, command: str) -> str:
        """Обработать команду напоминания."""
        command_lower = command.lower()

        if 'добавь напоминание' in command_lower or 'напомни' in command_lower:
            # Извлекаем текст напоминания.
            text = command_lower.replace('добавь напоминание', '').replace('напомни', '').strip()

            if text:
                time_str = self.parse_time(command_lower)
                return self.add_reminder(text, time_str)
            else:
                return "Что нужно напомнить?"

        elif 'покажи напоминания' in command_lower or 'список напоминаний' in command_lower:
            reminders = self.get_pending_reminders()

            if not reminders:
                return "Нет активных напоминаний"

            response = "Активные напоминания:\n"
            for i, reminder in enumerate(reminders, 1):
                response += f"{i}. {reminder['text']} в {reminder['time']}\n"

            return response.strip()

        else:
            return "Скажите 'добавь напоминание' или 'покажи напоминания'"
