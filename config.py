# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ Ошибка: нет токена в .env файле!")
    exit(1)

print("✅ Config загружен")