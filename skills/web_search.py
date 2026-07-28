"""
Навыки веб-поиска.
"""
import re
import random
import webbrowser
from datetime import datetime
import requests
from utils.logger import logger

try:
    import wikipedia
except ImportError:
    wikipedia = None
    logger.warning("Библиотека wikipedia не установлена. Установите: pip install wikipedia")


class WebSearchSkill:
    """Навык веб-поиска."""

    def __init__(self):
        # Список шуток на случай, если API не работает
        self.jokes = [
            "Почему программисты путают Хэллоуин и Рождество? Потому что 31 Oct = 25 Dec!",
            "Что сказал 0 числу 8? Хороший ремешок!",
            "Почему у программистов всегда холодно? Потому что они работают с Windows!",
            "Как называется ошибка в программе? Баг. А как называется ошибка в шутке? Шутка!",
            "Почему программист не может отличить кофе от чая? Потому что он всегда пьёт Java!",
            "Что говорит программист, когда видит ошибку? 'Это не баг, это фича!'",
            "Почему программисты не любят природу? Потому что там слишком много багов!",
            "Сколько программистов нужно, чтобы заменить лампочку? Ни одного — это аппаратная проблема!",
            "Почему программисты предпочитают темный режим? Потому что свет привлекает баги!",
            "Что такое идеальный программист? Тот, кто не пишет баги, а просто их документирует как фичи!"
        ]

    def get_time(self) -> str:
        """Получить текущее время."""
        now = datetime.now()
        return f"Сейчас {now.strftime('%H:%M')}"

    def get_date(self) -> str:
        """Получить текущую дату."""
        now = datetime.now()
        days = {
            0: "понедельник", 1: "вторник", 2: "среда",
            3: "четверг", 4: "пятница", 5: "суббота", 6: "воскресенье"
        }
        return f"Сегодня {days[now.weekday()]}, {now.strftime('%d %B %Y года')}"

    def get_joke(self) -> str:
        """Вернуть случайную шутку."""
        return random.choice(self.jokes)

    def search_web(self, query: str) -> str:
        """Поиск в интернете."""
        if not query:
            return "Что ищем?"

        import webbrowser
        search_url = f"https://yandex.ru/search/?text={query}"
        webbrowser.open(search_url)
        return f"Ищу в интернете: {query}"

    def open_website(self, command: str) -> str:
        """Открыть веб-сайт."""
        import webbrowser
        sites = {
            "ютуб": "https://www.youtube.com",
            "youtube": "https://www.youtube.com",
            "яндекс": "https://yandex.ru",
            "yandex": "https://yandex.ru",
            "гугл": "https://www.google.com",
            "google": "https://www.google.com",
            "вк": "https://vk.com",
            "vk": "https://vk.com",
            "телеграм": "https://web.telegram.org",
            "telegram": "https://web.telegram.org"
        }

        command_lower = command.lower()
        for name, url in sites.items():
            if name in command_lower:
                webbrowser.open(url)
                return f"Открываю {name}"

        # Если сайт не найден в списке, пробуем открыть как есть
        webbrowser.open(command)
        return f"Открываю {command}"

    def search_wikipedia(self, query: str) -> str:
        """Поиск в Википедии."""
        if not query:
            return "Что именно вы хотите найти в Википедии?"

        # Проверяем, установлена ли библиотека
        if wikipedia is None:
            return "Библиотека wikipedia не установлена. Установите: pip install wikipedia"

        try:
            # Настройка для русского языка
            wikipedia.set_lang("ru")
            
            # Пробуем получить краткую информацию
            try:
                summary = wikipedia.summary(query, sentences=3)
                return f"Согласно Википедии: {summary}"
            except wikipedia.DisambiguationError as e:
                options = ', '.join(e.options[:5])
                return f"Уточните запрос. Возможно, вы имели в виду: {options}"
            except wikipedia.PageError:
                # Пробуем поискать похожие страницы
                try:
                    results = wikipedia.search(query, results=3)
                    if results:
                        return f"Страница '{query}' не найдена. Возможно, вы искали: {', '.join(results)}"
                    else:
                        return f"Страница '{query}' не найдена в Википедии"
                except:
                    return f"Страница '{query}' не найдена в Википедии"
        except Exception as e:
            logger.error(f"Wikipedia error: {e}")
            return f"Не удалось получить информацию из Википедии: {e}"
