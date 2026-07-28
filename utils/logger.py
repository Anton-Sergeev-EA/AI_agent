import logging
import sys
from datetime import datetime
import os
import logging


def setup_logger(name: str = "assistant", log_file: str = "logs/assistant.log"):
    """Настройка системы логирования."""

    # Создаем папку для логов если её нет.
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Создаем логгер.
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Форматтер.
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # КОНСОЛЬНЫЙ ХЕНДЛЕР - ОТКЛЮЧАЕМ (убираем вывод в терминал)
    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setLevel(logging.INFO)
    # console_handler.setFormatter(formatter)
    # logger.addHandler(console_handler)

    # Файловый хендлер - оставляем (всё пишется в файл)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Глобальный логгер.
logger = setup_logger()

