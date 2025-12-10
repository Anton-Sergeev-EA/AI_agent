import requests
import json
from typing import Dict, Optional
from utils.logger import logger


class WeatherSkill:
    """Навык: прогноз погоды."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.cities = {
            "москва": "Moscow",
            "санкт-петербург": "Saint Petersburg",
            "новосибирск": "Novosibirsk",
            "екатеринбург": "Yekaterinburg",
            "казань": "Kazan",
            "нижний новгород": "Nizhny Novgorod",
            "челябинск": "Chelyabinsk",
            "самара": "Samara",
            "омск": "Omsk",
            "ростов": "Rostov-on-Don"
        }

    def get_weather(self, city_name: str = "Москва") -> str:
        """Получить погоду для города."""

        if not self.api_key:
            return "Не установлен API ключ для погоды. Добавьте OPENWEATHER_API_KEY в .env файл"

        # Нормализация названия города.
        city_lower = city_name.lower()
        city_en = self.cities.get(city_lower, city_name)

        try:
            # Запрос к API.
            params = {
                'q': city_en,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'ru'
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Извлечение данных.
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            wind_speed = data['wind']['speed']

            result = (
                f"В {city_name} сейчас {description}. "
                f"Температура: {temp:.1f}°C (ощущается как {feels_like:.1f}°C). "
                f"Влажность: {humidity}%. "
                f"Ветер: {wind_speed} м/с."
            )

            logger.info(f"Weather for {city_name}: {temp}°C")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API error: {e}")
            return f"Не удалось получить погоду для {city_name}"
        except KeyError as e:
            logger.error(f"Weather data parsing error: {e}")
            return "Ошибка обработки данных о погоде"

    def extract_city(self, text: str) -> str:
        """Извлечь название города из текста."""
        text_lower = text.lower()

        # Проверяем наличие названий городов в тексте.
        for city_ru, city_en in self.cities.items():
            if city_ru in text_lower:
                return city_ru.capitalize()

        # Если город не найден, возвращаем Москву по умолчанию.
        return "Москва"

    def process(self, command: str) -> str:
        """Обработать команду о погоде."""
        city = self.extract_city(command)
        return self.get_weather(city)
