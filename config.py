# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    print("⚠️ ВНИМАНИЕ: BOT_TOKEN не найден!")
    print("⚠️ На Render добавьте BOT_TOKEN в Environment Variables")
    BOT_TOKEN = "NOT_SET"
else:
    print(f"✅ Токен получен ({BOT_TOKEN[:10]}...)")