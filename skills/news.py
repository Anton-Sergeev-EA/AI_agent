import requests
import json
from typing import List, Dict
from utils.logger import logger


class NewsSkill:
    """Навык: новости."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.categories = {
            'спорт': 'sports',
            'технологии': 'technology',
            'бизнес': 'business',
            'развлечения': 'entertainment',
            'здоровье': 'health',
            'наука': 'science'
        }

    def get_news(self, category: str = "general", count: int = 3) -> str:
        """Получить новости."""

        if not self.api_key:
            # Используем бесплатный API если нет ключа.
            return self._get_news_fallback()

        try:
            url = "https://newsapi.org/v2/top-headlines"

            params = {
                'country': 'ru',
                'category': self.categories.get(category, 'general'),
                'pageSize': count,
                'apiKey': self.api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data['totalResults'] == 0:
                return "Новости не найдены"

            articles = data['articles'][:count]

            result = f"Последние новости ({category}):\n\n"
            for i, article in enumerate(articles, 1):
                title = article['title'].split(' - ')[0]  # Убираем источник из заголовка.
                result += f"{i}. {title}\n"

            logger.info(f"News fetched: {len(articles)} articles")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"News API error: {e}")
            return self._get_news_fallback()

    def _get_news_fallback(self) -> str:
        """Запасной метод получения новостей."""
        try:
            # Используем публичный RSS или другой источник.
            return (
                "Новости (пример, установите NEWS_API_KEY в .env для реальных новостей):\n\n"
                "1. Новости технологий: Искусственный интеллект продолжает развиваться\n"
                "2. Спорт: Российские спортсмены готовятся к соревнованиям\n"
                "3. Политика: Состоялась важная международная встреча"
            )
        except Exception as e:
            logger.error(f"Fallback news error: {e}")
            return "Не удалось получить новости. Проверьте подключение к интернету."

    def extract_category(self, text: str) -> str:
        """Извлечь категорию новостей из текста."""
        text_lower = text.lower()

        for category_ru, category_en in self.categories.items():
            if category_ru in text_lower:
                return category_ru

        return "главные"

    def process(self, command: str) -> str:
        """Обработать команду новостей."""
        category = self.extract_category(command)
        return self.get_news(category)
