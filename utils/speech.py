import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
from typing import Optional, Callable


class SpeechHandler:
    """Обработчик речи: распознавание и синтез."""

    def __init__(self, language: str = "ru-RU", rate: int = 150):
        self.language = language
        self.rate = rate

        # Инициализация распознавателя.
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

        # Инициализация синтезатора.
        self.tts_engine = pyttsx3.init()
        self.setup_voice()

        # Очередь для асинхронного воспроизведения.
        self.speech_queue = queue.Queue()
        self.is_speaking = False

        # Запускаем поток для воспроизведения речи.
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()

    def setup_voice(self):
        """Настройка голоса."""
        voices = self.tts_engine.getProperty('voices')

        # Пытаемся найти русский голос.
        for voice in voices:
            if 'russian' in voice.name.lower() or 'russian' in voice.id.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        else:
            # Если русский не найден, берем первый доступный.
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)

        self.tts_engine.setProperty('rate', self.rate)
        self.tts_engine.setProperty('volume', 1.0)

    def speak(self, text: str, block: bool = False):
        """Произнести текст."""
        print(f"🤖 Ассистент: {text}")

        if block:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        else:
            self.speech_queue.put(text)

    def _speech_worker(self):
        """Фоновый поток для воспроизведения речи."""
        while True:
            try:
                text = self.speech_queue.get(timeout=1)
                self.is_speaking = True
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                self.is_speaking = False
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Ошибка воспроизведения речи: {e}")
                self.is_speaking = False

    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """Слушать и распознавать речь."""
        try:
            with sr.Microphone() as source:
                print("🎤 Слушаю...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                try:
                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit
                    )
                except sr.WaitTimeoutError:
                    return None

                print("🔍 Распознаю...")
                text = self.recognizer.recognize_google(audio, language=self.language)
                print(f"👤 Вы сказали: {text}")
                return text.lower()

        except sr.UnknownValueError:
            print("❌ Не удалось распознать речь")
            return None
        except sr.RequestError as e:
            print(f"❌ Ошибка сервиса распознавания: {e}")
            return None
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return None

    def stop(self):
        """Остановить синтез речи."""
        self.tts_engine.stop()
