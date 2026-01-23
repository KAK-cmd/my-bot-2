# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ Ошибка: токен не найден! Проверьте переменную окружения BOT_TOKEN")
    # Для Render это нормально - токен должен быть в Environment Variables
    # Не выходим из программы, чтобы Render не думал что бот упал
    # Просто выводим предупреждение
    print("⚠️  Предупреждение: BOT_TOKEN не установлен")
    print("⚠️  На Render добавьте BOT_TOKEN в Environment Variables")
    BOT_TOKEN = "NOT_SET"  # Заглушка для запуска