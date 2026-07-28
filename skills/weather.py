"""
Навык: погода.
"""
import requests
import re
from utils.logger import logger


class WeatherSkill:
    """Навык получения погоды."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def process(self, command: str) -> str:
        """Обработать запрос погоды."""
        if not self.api_key:
            return "Не установлен API ключ для погоды. Добавьте OPENWEATHER_API_KEY в .env файл"

        # Извлекаем город из команды
        city = self._extract_city(command)
        
        if not city:
            return "Пожалуйста, укажите город. Например: 'погода в Москве' или 'какая погода в Санкт-Петербурге?'"

        # Получаем погоду
        return self._get_weather(city)

    def _extract_city(self, command: str) -> str:
        """Извлечь название города из команды."""
        command_lower = command.lower()
        
        # Шаблоны для поиска города
        patterns = [
            r'(?:погода|температура|какая погода)(?:\s+в\s+|\s+для\s+|\s+в\s+городе\s+)([а-яА-ЯёЁ\s\-]+)',
            r'(?:в|для)\s+([а-яА-ЯёЁ\s\-]+)',
            r'погода\s+([а-яА-ЯёЁ\s\-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command_lower)
            if match:
                city = match.group(1).strip()
                # Убираем лишние слова в конце
                city = re.sub(r'\s+(сейчас|сегодня|завтра|на\s+сегодня|на\s+завтра).*$', '', city)
                # Убираем вопросительные знаки и точки
                city = re.sub(r'[?.,!]', '', city)
                if city:
                    return city.strip()
        
        return ""

    def _get_weather(self, city: str) -> str:
        """Получить погоду для города."""
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'lang': 'ru',
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                weather_desc = data['weather'][0]['description']
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']
                city_name = data['name']
                
                return (f"В {city_name} сейчас {temp:.0f}°C, ощущается как {feels_like:.0f}°C, "
                       f"{weather_desc}. Влажность {humidity}%, ветер {wind_speed:.1f} м/с")
                       
            elif response.status_code == 404:
                return f"Город '{city}' не найден. Проверьте название города."
            else:
                error_msg = response.json().get('message', 'Неизвестная ошибка')
                return f"Ошибка получения погоды: {error_msg}"
                
        except requests.exceptions.Timeout:
            return "Превышено время ожидания ответа от сервера погоды."
        except requests.exceptions.ConnectionError:
            return "Нет подключения к интернету. Проверьте соединение."
        except Exception as e:
            logger.error(f"Weather error: {e}")
            return f"Не удалось получить погоду для {city}"

    def get_weather_by_coords(self, lat: float, lon: float) -> str:
        """Получить погоду по координатам."""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'lang': 'ru',
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                weather_desc = data['weather'][0]['description']
                city_name = data.get('name', 'неизвестном городе')
                
                return (f"В {city_name} сейчас {temp:.0f}°C, ощущается как {feels_like:.0f}°C, "
                       f"{weather_desc}")
            else:
                return "Не удалось получить погоду по координатам"
                
        except Exception as e:
            logger.error(f"Weather by coords error: {e}")
            return "Ошибка получения погоды по координатам"
