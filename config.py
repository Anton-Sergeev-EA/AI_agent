import os
from dataclasses import dataclass, field
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

@dataclass
class AssistantConfig:
    """Конфигурация ассистента."""

    # Основные настройки.
    NAME: str = "Антон"
    LANGUAGE: str = "ru-RU"
    SPEECH_RATE: int = 150
    VOLUME: float = 1.0

    # Пути к файлам.
    DB_PATH: str = "data/assistant.db"
    LOG_PATH: str = "logs/assistant.log"

    # Настройки API.
    OPENWEATHER_API_KEY: str = field(default_factory=lambda: os.getenv('OPENWEATHER_API_KEY', ''))
    NEWS_API_KEY: str = field(default_factory=lambda: os.getenv('NEWS_API_KEY', ''))

    # Настройки моделей.
    USE_SPEECH: bool = True
    USE_AI: bool = False

    # Команды активации.
    WAKE_WORDS: List[str] = field(default_factory=lambda: ["алекс", "помощник", "антон"])
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
    def from_env(cls) -> "AssistantConfig":
        """Создать конфиг из переменных окружения."""
        return cls(
            NAME=os.getenv('ASSISTANT_NAME', 'Антон'),
            OPENWEATHER_API_KEY=os.getenv('OPENWEATHER_API_KEY', ''),
            NEWS_API_KEY=os.getenv('NEWS_API_KEY', ''),
            USE_SPEECH=os.getenv('USE_SPEECH', 'True').lower() == 'true'
        )
