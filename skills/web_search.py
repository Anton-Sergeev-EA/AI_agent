import webbrowser
import wikipedia
import pyjokes
from datetime import datetime
import os
from utils.logger import logger


class WebSearchSkill:
    """Навык: веб-поиск и полезные функции."""

    def __init__(self):
        # Настраиваем Википедию.
        wikipedia.set_lang("ru")

        # Карта сайтов для быстрого открытия.
        self.websites = {
            'youtube': 'https://youtube.com',
            'google': 'https://google.com',
            'яндекс': 'https://yandex.ru',
            'вконтакте': 'https://vk.com',
            'почта': 'https://mail.google.com',
            'github': 'https://github.com',
            'переводчик': 'https://translate.google.com'
        }

    def search_web(self, query: str) -> str:
        """Поиск в интернете."""
        try:
            search_url = f"https://www.google.com/search?q={query}"
            webbrowser.open(search_url)
            return f"Ищу в интернете: {query}"
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return f"Не удалось выполнить поиск: {query}"

    def search_wikipedia(self, query: str) -> str:
        """Поиск в Википедии."""
        try:
            summary = wikipedia.summary(query, sentences=2)
            return f"Согласно Википедии: {summary}"
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Уточните запрос. Возможные варианты: {', '.join(e.options[:3])}"
        except wikipedia.exceptions.PageError:
            return f"В Википедии нет статьи по запросу: {query}"
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return "Не удалось получить информацию из Википедии"

    def tell_joke(self) -> str:
        """Рассказать шутку."""
        try:
            joke = pyjokes.get_joke(language='ru')
            if not joke:
                joke = pyjokes.get_joke(language='en')
                joke = f"(На английском) {joke}"
            return joke
        except:
            return "Почему программисты не любят природу? Слишком много багов!"

    def get_time(self) -> str:
        """Получить текущее время."""
        now = datetime.now()
        return f"Сейчас {now.strftime('%H:%M')}"

    def get_date(self) -> str:
        """Получить текущую дату."""
        now = datetime.now()
        days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
        months = [
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
        ]

        weekday = days[now.weekday()]
        day = now.day
        month = months[now.month - 1]
        year = now.year

        return f"Сегодня {weekday}, {day} {month} {year} года"

    def open_website(self, site_name: str) -> str:
        """Открыть веб-сайт."""
        site_lower = site_name.lower()

        for keyword, url in self.websites.items():
            if keyword in site_lower:
                webbrowser.open(url)
                return f"Открываю {keyword}"

        # Если сайт не найден в списке, пробуем открыть как URL.
        if site_lower.startswith(('http://', 'https://')):
            webbrowser.open(site_lower)
            return f"Открываю {site_lower}"

        return f"Не знаю как открыть {site_name}"

    def process(self, command: str) -> str:
        """Обработать команду веб-поиска."""
        command_lower = command.lower()

        if 'шутка' in command_lower or 'пошути' in command_lower:
            return self.tell_joke()

        elif 'время' in command_lower:
            return self.get_time()

        elif 'дата' in command_lower or 'число' in command_lower:
            return self.get_date()

        elif 'открой' in command_lower:
            site = command_lower.replace('открой', '').strip()
            return self.open_website(site)

        elif 'найди в интернете' in command_lower or 'поищи' in command_lower:
            query = command_lower.replace('найди в интернете', '').replace('поищи', '').strip()
            return self.search_web(query)

        elif 'википедия' in command_lower:
            query = command_lower.replace('википедия', '').strip()
            return self.search_wikipedia(query)

        else:
            return "Скажите что искать или что открыть"
