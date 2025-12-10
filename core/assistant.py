import time
import re
from typing import Dict, Optional, Any, Callable

from config import AssistantConfig
from core.state_manager import StateManager, AssistantState
from utils.speech import SpeechHandler
from utils.logger import logger

# Импортируем навыки.
from skills.weather import WeatherSkill
from skills.calculator import CalculatorSkill
from skills.reminders import RemindersSkill
from skills.news import NewsSkill
from skills.web_search import WebSearchSkill


class IntelligentAssistant:
    """Интеллектуальный ассистент."""

    def __init__(self, config: AssistantConfig):
        self.config = config
        self.name = config.NAME

        # Инициализация компонентов.
        self.state_manager = StateManager(config)

        if config.USE_SPEECH:
            self.speech = SpeechHandler(
                language=config.LANGUAGE,
                rate=config.SPEECH_RATE
            )
        else:
            self.speech = None

        # Инициализация навыков.
        self.skills = self._init_skills()

        # Команды-триггеры.
        self.command_patterns = self._init_command_patterns()

        # Статистика.
        self.stats = {
            'commands_processed': 0,
            'errors': 0,
            'start_time': time.time()
        }

        logger.info(f"Assistant '{self.name}' initialized")

    def _init_skills(self) -> Dict[str, Any]:
        """Инициализация всех навыков."""
        skills = {}

        # Погода.
        skills['weather'] = WeatherSkill(self.config.OPENWEATHER_API_KEY)

        # Калькулятор.
        skills['calculator'] = CalculatorSkill()

        # Напоминания.
        skills['reminders'] = RemindersSkill(self.config.DB_PATH)

        # Новости.
        skills['news'] = NewsSkill(self.config.NEWS_API_KEY)

        # Веб-поиск.
        skills['web_search'] = WebSearchSkill()

        return skills

    def _init_command_patterns(self) -> Dict[str, Callable]:
        """Инициализация паттернов команд."""
        return {
            r'(погода|погоду|температура)': self._handle_weather,
            r'(посчитай|сколько будет|вычисли|калькулятор)': self._handle_calculator,
            r'(напомни|добавь напоминание|напоминания)': self._handle_reminders,
            r'(новости|что нового)': self._handle_news,
            r'(время|который час)': self._handle_time,
            r'(дата|число|какое число)': self._handle_date,
            r'(открой|запусти|включи)': self._handle_open,
            r'(найди|поищи|ищи|найти)': self._handle_search,
            r'(шутка|пошути|рассмеши)': self._handle_joke,
            r'(википедия|вики)': self._handle_wikipedia,
            r'(помощь|что ты умеешь|команды)': self._handle_help,
            r'(спасибо|благодарю)': self._handle_thanks,
            r'(как тебя зовут|твое имя)': self._handle_name,
            r'(стоп|выход|закончить)': self._handle_exit
        }

    def process_command(self, command: str) -> str:
        """Обработать команду пользователя."""
        if not command or command.strip() == "":
            return "Не расслышал, повторите пожалуйста"

        command_lower = command.lower()
        self.state_manager.set_state(AssistantState.PROCESSING)

        try:
            # Проверяем команды выхода.
            if any(word in command_lower for word in self.config.EXIT_WORDS):
                return self._handle_exit(command_lower)

            # Проверяем триггеры пробуждения.
            if not self.state_manager.is_awake():
                if any(word in command_lower for word in self.config.WAKE_WORDS):
                    self.state_manager.wake_up()
                    return f"Здравствуйте! Я {self.name}, ваш помощник. Чем могу помочь?"
                else:
                    return ""

            # Ищем совпадение с паттернами команд.
            response = ""
            for pattern, handler in self.command_patterns.items():
                if re.search(pattern, command_lower):
                    response = handler(command_lower)
                    break

            # Если команда не распознана.
            if not response:
                response = self._handle_unknown(command_lower)

            # Обновляем контекст и статистику.
            self.state_manager.update_context(command, response)
            self.stats['commands_processed'] += 1

            # Возвращаемся в состояние listening.
            self.state_manager.set_state(AssistantState.LISTENING)

            return response

        except Exception as e:
            logger.error(f"Error processing command '{command}': {e}")
            self.stats['errors'] += 1
            self.state_manager.set_state(AssistantState.ERROR)
            return f"Произошла ошибка при обработке команды: {str(e)}"

    # Обработчики команд.
    def _handle_weather(self, command: str) -> str:
        return self.skills['weather'].process(command)

    def _handle_calculator(self, command: str) -> str:
        return self.skills['calculator'].process(command)

    def _handle_reminders(self, command: str) -> str:
        return self.skills['reminders'].process(command)

    def _handle_news(self, command: str) -> str:
        return self.skills['news'].process(command)

    def _handle_time(self, command: str) -> str:
        return self.skills['web_search'].get_time()

    def _handle_date(self, command: str) -> str:
        return self.skills['web_search'].get_date()

    def _handle_open(self, command: str) -> str:
        return self.skills['web_search'].open_website(command)

    def _handle_search(self, command: str) -> str:
        query = re.sub(r'найди|поищи|ищи|найти', '', command).strip()
        return self.skills['web_search'].search_web(query)

    def _handle_joke(self, command: str) -> str:
        return self.skills['web_search'].tell_joke()

    def _handle_wikipedia(self, command: str) -> str:
        query = re.sub(r'википедия|вики', '', command).strip()
        return self.skills['web_search'].search_wikipedia(query)

    def _handle_help(self, command: str) -> str:
        help_text = """
🤖 Я умею:
• Погода (скажите "погода в Москве")
• Калькулятор ("посчитай 2+2")
• Напоминания ("напомни через 10 минут")
• Новости ("новости спорта")
• Время и дата ("который час", "какое число")
• Открыть сайты ("открой YouTube")
• Поиск в интернете ("найди кошек")
• Шутки ("расскажи шутку")
• Википедия ("википедия Python")
• Выйти ("стоп", "выход")
"""
        return help_text.strip()

    def _handle_thanks(self, command: str) -> str:
        responses = [
            "Всегда рад помочь!",
            "Пожалуйста!",
            "Обращайтесь!",
            "Рад был помочь!"
        ]
        import random
        return random.choice(responses)

    def _handle_name(self, command: str) -> str:
        return f"Меня зовут {self.name}. Я ваш цифровой помощник."

    def _handle_exit(self, command: str) -> str:
        self.state_manager.sleep()

        uptime = time.time() - self.stats['start_time']
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)

        return f"До свидания! Работал {hours} часов {minutes} минут, обработал {self.stats['commands_processed']} команд."

    def _handle_unknown(self, command: str) -> str:
        responses = [
            "Не совсем понял. Попробуйте сказать иначе.",
            "Можете повторить?",
            "Я не уверен что вы имели в виду.",
            f"Скажите 'помощь' чтобы узнать что я умею."
        ]
        import random
        return random.choice(responses)

    def run_cli(self):
        """Запуск в режиме командной строки."""
        print(f"🤖 Ассистент {self.name} запущен!")
        print("Напишите 'помощь' для списка команд или 'выход' для завершения.")
        print("Для голосового режима используйте run_voice()\n")

        self.state_manager.wake_up()

        while True:
            try:
                user_input = input("\n👤 Вы: ").strip()

                if not user_input:
                    continue

                response = self.process_command(user_input)

                if response:
                    print(f"🤖 {self.name}: {response}")

                # Проверяем команду выхода.
                if any(word in user_input.lower() for word in self.config.EXIT_WORDS):
                    break

            except KeyboardInterrupt:
                print(f"\n🤖 {self.name}: До свидания!")
                break
            except Exception as e:
                logger.error(f"CLI error: {e}")
                print(f"🤖 Ошибка: {e}")

    def run_voice(self):
        """Запуск в голосовом режиме."""
        if not self.speech:
            print("Голосовой режим отключен в конфигурации")
            return self.run_cli()

        print(f"🎤 Голосовой ассистент {self.name} запущен!")
        print("Скажите 'помощник' или 'алекс' для активации")
        print("Скажите 'стоп' для выхода\n")

        self.speech.speak(f"Здравствуйте, я {self.name}. Скажите моё имя чтобы активировать меня.")

        while True:
            try:
                # Слушаем команду.
                command = self.speech.listen(timeout=3)

                if command is None:
                    continue

                # Проверяем команду пробуждения.
                if not self.state_manager.is_awake():
                    if any(word in command for word in self.config.WAKE_WORDS):
                        self.state_manager.wake_up()
                        self.speech.speak(f"Да, я слушаю! Чем могу помочь?")
                    continue

                # Обрабатываем команду.
                response = self.process_command(command)

                if response:
                    self.speech.speak(response)

                # Проверяем команду выхода.
                if any(word in command for word in self.config.EXIT_WORDS):
                    self.state_manager.sleep()
                    time.sleep(1)  # Пауза перед завершением.
                    break

            except KeyboardInterrupt:
                self.speech.speak("До свидания!")
                break
            except Exception as e:
                logger.error(f"Voice mode error: {e}")
                self.speech.speak("Произошла ошибка")

    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику работы."""
        uptime = time.time() - self.stats['start_time']

        return {
            'name': self.name,
            'uptime_seconds': int(uptime),
            'commands_processed': self.stats['commands_processed'],
            'errors': self.stats['errors'],
            'active_skills': list(self.state_manager.active_skills),
            'state': self.state_manager.get_state().value
        }
