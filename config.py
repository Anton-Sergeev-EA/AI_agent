import os
from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class AssistantConfig:
    """Конфигурация ассистента."""

    # Основные настройки.
    NAME: str = "Алекс"
    LANGUAGE: str = "ru-RU"
    SPEECH_RATE: int = 150
    VOLUME: float = 1.0

    # Пути к файлам.
    DB_PATH: str = "data/assistant.db"
    LOG_PATH: str = "logs/assistant.log"

    # Настройки API.
    OPENWEATHER_API_KEY: str = ""
    NEWS_API_KEY: str = ""

    # Настройки моделей.
    USE_SPEECH: bool = True
    USE_AI: bool = False

    # Команды активации (используем field для изменяемых типов).
    WAKE_WORDS: List[str] = field(default_factory=lambda: ["алекс", "помощник", "эй"])
    EXIT_WORDS: List[str] = field(default_factory=lambda: ["стоп", "выход", "закончить"])

    # Навыки по умолчанию.
    DEFAULT_SKILLS: List[str] = field(default_factory=lambda: [
        "weather",
        "calculator",
        "time",
        "date",
        "joke",
        "news",
        "web_search",
        "reminders"
    ])

    @classmethod
    def from_env(cls):
        """Загрузка конфигурации из переменных окружения."""
        config = cls()

        # Загружаем из .env если есть.
        try:
            from dotenv import load_dotenv
            load_dotenv()

            config.NAME = os.getenv("ASSISTANT_NAME", config.NAME)
            config.OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
            config.NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

            use_speech = os.getenv("USE_SPEECH", "True")
            config.USE_SPEECH = use_speech.lower() in ["true", "1", "yes"]

            use_ai = os.getenv("USE_AI", "False")
            config.USE_AI = use_ai.lower() in ["true", "1", "yes"]

            # Загружаем списки слов
            wake_words = os.getenv("WAKE_WORDS", "")
            if wake_words:
                config.WAKE_WORDS = [w.strip() for w in wake_words.split(",") if w.strip()]

            exit_words = os.getenv("EXIT_WORDS", "")
            if exit_words:
                config.EXIT_WORDS = [w.strip() for w in exit_words.split(",") if w.strip()]

        except ImportError:
            print("⚠️  dotenv не установлен, используем настройки по умолчанию")

        return config
