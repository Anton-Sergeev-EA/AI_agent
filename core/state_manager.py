from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import json
import os


class AssistantState(Enum):
    """Состояния ассистента."""
    SLEEPING = "sleeping"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


@dataclass
class ConversationContext:
    """Контекст разговора."""
    last_command: str = ""
    last_response: str = ""
    user_name: Optional[str] = None
    conversation_history: List[Dict] = field(default_factory=list)

    def add_interaction(self, command: str, response: str):
        """Добавить взаимодействие в историю."""
        self.last_command = command
        self.last_response = response

        from datetime import datetime
        timestamp = datetime.now().isoformat()

        self.conversation_history.append({
            'command': command,
            'response': response,
            'timestamp': timestamp
        })

        # Ограничиваем историю последними 20 сообщениями.
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь."""
        return {
            'last_command': self.last_command,
            'last_response': self.last_response,
            'user_name': self.user_name,
            'conversation_history': self.conversation_history
        }


class StateManager:
    """Менеджер состояния ассистента."""

    def __init__(self, config):
        self.state = AssistantState.SLEEPING
        self.config = config
        self.context = ConversationContext()
        self.active_skills = set(config.DEFAULT_SKILLS)
        self.user_preferences = self._load_preferences()

    def _load_preferences(self) -> Dict[str, Any]:
        """Загрузить настройки пользователя."""
        prefs_path = "data/preferences.json"

        if os.path.exists(prefs_path):
            try:
                with open(prefs_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        # Возвращаем настройки по умолчанию.
        return {
            'preferred_city': 'Москва',
            'news_category': 'general',
            'speech_rate': 150,
            'volume': 1.0
        }

    def save_preferences(self):
        """Сохранить настройки пользователя."""
        prefs_path = "data/preferences.json"

        try:
            os.makedirs(os.path.dirname(prefs_path), exist_ok=True)
            with open(prefs_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")

    def set_state(self, new_state: AssistantState):
        """Установить новое состояние."""
        old_state = self.state
        self.state = new_state

     #  if old_state != new_state:
     #      print(f"Состояние: {old_state.value} -> {new_state.value}")

    def get_state(self) -> AssistantState:
        """Получить текущее состояние."""
        return self.state

    def is_awake(self) -> bool:
        """Проверить, активен ли ассистент."""
        return self.state != AssistantState.SLEEPING

    def wake_up(self):
        """Разбудить ассистента."""
        self.set_state(AssistantState.LISTENING)

    def sleep(self):
        """Уснуть (деактивировать)."""
        self.set_state(AssistantState.SLEEPING)

    def update_context(self, command: str, response: str):
        """Обновить контекст разговора."""
        self.context.add_interaction(command, response)

    def get_last_interaction(self) -> tuple:
        """Получить последнее взаимодействие."""
        return self.context.last_command, self.context.last_response

    def enable_skill(self, skill_name: str):
        """Включить навык."""
        self.active_skills.add(skill_name)

    def disable_skill(self, skill_name: str):
        """Выключить навык."""
        if skill_name in self.active_skills:
            self.active_skills.remove(skill_name)

    def is_skill_active(self, skill_name: str) -> bool:
        """Проверить активен ли навык."""
        return skill_name in self.active_skills
