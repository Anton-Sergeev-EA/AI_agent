#!/usr/bin/env python3
"""
Прямой запуск ассистента без main.py
"""
import sys
import os

# Добавляем текущую папку в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import AssistantConfig
from core.assistant import IntelligentAssistant

def main():
    # Создаём конфиг из .env
    config = AssistantConfig.from_env()  # <-- ИЗМЕНЕНО
    
    # Создаём ассистента
    assistant = IntelligentAssistant(config)
    
    print("╔══════════════════════════════════════════╗")
    print("║     ИНТЕЛЛЕКТУАЛЬНЫЙ АССИСТЕНТ v1.0      ║")
    print("║        версия от Антона Сергеева         ║")
    print("╚══════════════════════════════════════════╝")
    print(f"\n⌨️ Текстовый ассистент '{assistant.name}' запущен!")
    print("Вводите команды с клавиатуры или напишите 'выход' для завершения\n")
    
    while True:
        try:
            command = input("👤 Вы: ").strip()
            
            if command.lower() in ['выход', 'стоп', 'exit', 'quit']:
                print(f"🤖 {assistant.name}: До свидания!")
                break
            
            if not command:
                continue
            
            response = assistant.process_command(command)
            
            if response:
                print(f"🤖 {assistant.name}: {response}")
                
        except KeyboardInterrupt:
            print("\n🤖 Алекс: До свидания!")
            break
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
