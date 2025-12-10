"""
Интеллектуальный ассистент.
Запуск: python main.py [--voice] [--cli]
"""

import os
import sys
import time
from datetime import datetime


def clear_screen():
    """Очистить экран."""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_banner():
    """Показать баннер."""
    banner = """
╔══════════════════════════════════════════╗
║     ИНТЕЛЛЕКТУАЛЬНЫЙ АССИСТЕНТ v1.0      ║
║        версия от Антона Сергеева         ║
╚══════════════════════════════════════════╝
    """
    print(banner)


def setup_environment():
    """Настройка окружения."""
    print("🔧 Настройка окружения...")

    # Создаем необходимые папки.
    folders = ['data', 'logs']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✓ Создана папка: {folder}/")

    # Проверяем зависимости.
    dependencies = [
        ('speechrecognition', 'speech_recognition'),
        ('pyttsx3', 'pyttsx3'),
        ('requests', 'requests'),
    ]

    missing_deps = []
    for pip_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✓ Установлено: {pip_name}")
        except ImportError:
            missing_deps.append(pip_name)

    if missing_deps:
        print(f"\n⚠️  Отсутствуют зависимости: {', '.join(missing_deps)}")
        print("Установите: pip install " + " ".join(missing_deps))
        return False

    return True


class SimpleAssistant:
    """Простой ассистент для быстрого старта."""

    def __init__(self, name="Алекс", use_voice=False):
        self.name = name
        self.use_voice = use_voice

        if use_voice:
            self._init_voice()
        else:
            self.speech_engine = None

        self.commands = {
            'привет': self.handle_greeting,
            'время': self.handle_time,
            'дата': self.handle_date,
            'погода': self.handle_weather,
            'калькулятор': self.handle_calculator,
            'шутка': self.handle_joke,
            'помощь': self.handle_help,
            'выход': self.handle_exit,
        }

    def _init_voice(self):
        """Инициализация голосового режима."""
        try:
            import pyttsx3
            self.speech_engine = pyttsx3.init()

            # Настройка голоса.
            voices = self.speech_engine.getProperty('voices')
            if voices:
                self.speech_engine.setProperty('voice', voices[0].id)
            self.speech_engine.setProperty('rate', 150)

            print("✓ Голосовой режим инициализирован")

        except Exception as e:
            print(f"⚠️  Ошибка инициализации голоса: {e}")
            self.use_voice = False
            self.speech_engine = None

    def speak(self, text):
        """Произнести текст."""
        print(f"🤖 {self.name}: {text}")

        if self.use_voice and self.speech_engine:
            try:
                self.speech_engine.say(text)
                self.speech_engine.runAndWait()
            except:
                pass

    def listen(self):
        """Слушать команду."""
        if self.use_voice:
            try:
                import speech_recognition as sr
                recognizer = sr.Recognizer()

                with sr.Microphone() as source:
                    print("\n🎤 Слушаю... (говорите)")
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source, timeout=3)

                    try:
                        text = recognizer.recognize_google(audio, language="ru-RU")
                        print(f"👤 Вы сказали: {text}")
                        return text.lower()
                    except sr.UnknownValueError:
                        print("❌ Не удалось распознать речь")
                        return None

            except Exception as e:
                print(f"⚠️  Ошибка распознавания: {e}")
                return None
        else:
            # Текстовый ввод.
            try:
                return input("\n👤 Вы: ").strip().lower()
            except KeyboardInterrupt:
                return "выход"
            except EOFError:
                return "выход"

    def handle_greeting(self, command=""):
        return f"Привет! Я {self.name}, ваш цифровой помощник. Чем могу помочь?"

    def handle_time(self, command=""):
        now = datetime.now()
        return f"Сейчас {now.strftime('%H:%M:%S')}"

    def handle_date(self, command=""):
        now = datetime.now()
        months = [
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
        ]
        return f"Сегодня {now.day} {months[now.month - 1]} {now.year} года"

    def handle_weather(self, command=""):
        # Простая имитация погоды.
        import random
        cities = {
            'москва': 'Москве',
            'санкт-петербург': 'Санкт-Петербурге',
            'новосибирск': 'Новосибирске',
            'екатеринбург': 'Екатеринбурге'
        }

        city = "Москве"
        for c in cities:
            if c in command:
                city = cities[c]
                break

        temp = random.randint(15, 25)
        conditions = ["солнечно ☀️", "облачно ☁️", "дождь 🌧️", "ясно 🌤️"]
        condition = random.choice(conditions)

        return f"В {city} сейчас {temp}°C, {condition}"

    def handle_calculator(self, command=""):
        try:
            # Извлекаем выражение.
            if 'сколько будет' in command:
                expr = command.replace('сколько будет', '').strip()
            elif 'посчитай' in command:
                expr = command.replace('посчитай', '').strip()
            elif 'калькулятор' in command:
                expr = command.replace('калькулятор', '').strip()
            else:
                expr = command

            # Очищаем выражение.
            expr = expr.replace(' ', '')

            # Проверяем безопасность.
            allowed_chars = set('0123456789+-*/().')
            if not all(c in allowed_chars for c in expr):
                return "Можно использовать только цифры и + - * / ( ) ."

            # Вычисляем.
            result = eval(expr)
            return f"{expr} = {result}"

        except ZeroDivisionError:
            return "Ошибка: деление на ноль"
        except:
            return "Не могу вычислить. Пример: 2+2 или 3*4"

    def handle_joke(self, command=""):
        jokes = [
            "Почему программисты не любят природу? Слишком много багов!",
            "Какой язык программирования самый романтичный? Python, потому что у него есть любовь (любовь = 'love' в переводе)!",
            "Почему Python не нужно бояться? Потому что он не кусается!",
            "Сколько программистов нужно, чтобы поменять лампочку? Ни одного, это hardware проблема!",
        ]
        import random
        return random.choice(jokes)

    def handle_help(self, command=""):
        help_text = f"""
🤖 Я {self.name}, ваш цифровой помощник!

Доступные команды:
• Привет - поздороваться
• Время - узнать текущее время
• Дата - узнать сегодняшнюю дату
• Погода [город] - узнать погоду
• Посчитай [выражение] - решить пример
• Шутка - рассказать шутку
• Помощь - показать это сообщение
• Выход - завершить работу

Примеры:
  "погода в москве"
  "посчитай 15+3*2"
  "какое время"
  "расскажи шутку"
"""
        return help_text.strip()

    def handle_exit(self, command=""):
        return "exit"

    def process_command(self, command):
        """Обработать команду."""
        if not command:
            return "Не расслышал, повторите пожалуйста"

        # Ищем подходящий обработчик.
        for key, handler in self.commands.items():
            if key in command:
                return handler(command)

        # Если команда не распознана.
        return "Не понял команду. Скажите 'помощь' для списка команд"

    def run(self):
        """Запуск ассистента."""
        clear_screen()
        show_banner()

        if self.use_voice:
            print(f"🎤 Голосовой ассистент '{self.name}' запущен!")
            print("Говорите команды или скажите 'выход' для завершения\n")
            self.speak(f"Здравствуйте, я {self.name}. Слушаю ваши команды.")
        else:
            print(f"⌨️ Текстовый ассистент '{self.name}' запущен!")
            print("Вводите команды с клавиатуры или напишите 'выход' для завершения\n")

        commands_processed = 0

        while True:
            try:
                # Получаем команду.
                command = self.listen()

                if command is None:
                    continue

                if not command.strip():
                    continue

                # Обрабатываем команду.
                response = self.process_command(command)

                if response == "exit":
                    self.speak(f"До свидания! Обработано команд: {commands_processed}")
                    break

                # Произносим/показываем ответ.
                self.speak(response)
                commands_processed += 1

            except KeyboardInterrupt:
                print(f"\n\n🤖 {self.name}: До свидания! 👋")
                break
            except Exception as e:
                print(f"\n⚠️ Ошибка: {e}")
                self.speak("Произошла ошибка, попробуйте еще раз")


def main():
    """Главная функция."""
    import argparse

    parser = argparse.ArgumentParser(description='Интеллектуальный ассистент')
    parser.add_argument('--mode', choices=['voice', 'cli'], default='cli', help='Режим работы')
    parser.add_argument('--name', type=str, default='Алекс', help='Имя ассистента')
    args = parser.parse_args()

    # Настройка окружения.
    if not setup_environment():
        print("\n⚠️  Продолжаем с ограниченной функциональностью...")

    # Создаем и запускаем ассистента.
    use_voice = args.mode == 'voice'
    assistant = SimpleAssistant(name=args.name, use_voice=use_voice)

    try:
        assistant.run()
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        print("Попробуйте запустить в текстовом режиме: python main.py --mode cli")


if __name__ == "__main__":
    main()
