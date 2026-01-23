# bot.py - основной файл бота для Render
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN
from excel_parser import ПарсерРасписания
from database import db
from keep_alive import keep_alive

# ============ НАСТРОЙКА ============

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Проверяем токен
if BOT_TOKEN == "NOT_SET":
    logger.error("❌ ОШИБКА: BOT_TOKEN не установлен!")
    logger.error("❌ На Render добавьте BOT_TOKEN в Environment Variables")
    exit(1)

# Создаем объекты бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
парсер = ПарсерРасписания()

# ============ КЛАВИАТУРА ============

def создать_клавиатуру():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Сегодня"), KeyboardButton(text="📅 Завтра")],
            [KeyboardButton(text="🔵 Числитель"), KeyboardButton(text="🔴 Знаменатель")],
            [KeyboardButton(text="📊 Неделя"), KeyboardButton(text="🔄 Замены")],
            [KeyboardButton(text="🔔 Подписка"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )

# ============ КОМАНДЫ ============

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    
    # Добавляем в БД
    db.add_subscriber(user_id=user_id, username=username, first_name=first_name)
    
    await message.answer(
        f"👋 Привет, {first_name}!\n\n"
        f"🤖 Я бот с расписанием для группы ИС1-21/ИС1-22\n"
        f"📅 Показываю расписание пар\n"
        f"🔄 Слежу за заменами\n"
        f"🔔 Есть ежедневная рассылка\n\n"
        f"💡 Используй кнопки ниже!",
        reply_markup=создать_клавиатуру()
    )

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    help_text = (
        "📚 **Помощь по боту**\n\n"
        "🔘 **Кнопки:**\n"
        "• 📅 Сегодня - расписание на сегодня\n"
        "• 📅 Завтра - на завтра\n"
        "• 🔵 Числитель - принудительно числитель\n"
        "• 🔴 Знаменатель - принудительно знаменатель\n"
        "• 📊 Неделя - информация о неделе\n"
        "• 🔄 Замены - показать замены\n"
        "• 🔔 Подписка - управление рассылкой\n"
        "• ❓ Помощь - это сообщение\n\n"
        "📝 **Рассылка:**\n"
        "Автоматически в 7:00 утра\n"
        "Подписаться: /subscribe\n"
        "Отписаться: /unsubscribe\n\n"
        "🔄 **Замены:**\n"
        "Обновляются с сайта sttec\n"
        "Команда: /update"
    )
    await message.answer(help_text, reply_markup=создать_клавиатуру())

@dp.message(Command("today"))
async def today_cmd(message: types.Message):
    расписание = парсер.получить_расписание_с_заменами()
    await message.answer(расписание, reply_markup=создать_клавиатуру())

@dp.message(Command("tomorrow"))
async def tomorrow_cmd(message: types.Message):
    from datetime import timedelta
    
    дни = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    сегодня_idx = datetime.now().weekday()
    завтра_idx = (сегодня_idx + 1) % 7
    завтра_день = дни[завтра_idx]
    завтра_дата = datetime.now() + timedelta(days=1)
    
    расписание = парсер.получить_расписание_с_заменами(завтра_день, для_даты=завтра_дата)
    await message.answer(расписание, reply_markup=создать_клавиатуру())

@dp.message(Command("week"))
async def week_cmd(message: types.Message):
    информация = парсер.получить_информацию_о_неделе()
    await message.answer(информация, reply_markup=создать_клавиатуру())

@dp.message(Command("subscribe"))
async def subscribe_cmd(message: types.Message):
    user_id = message.from_user.id
    if db.is_subscriber(user_id):
        await message.answer("✅ Вы уже подписаны на рассылку!", reply_markup=создать_клавиатуру())
    else:
        db.add_subscriber(user_id=user_id)
        await message.answer("✅ Вы подписались на ежедневную рассылку в 7:00!", reply_markup=создать_клавиатуру())

@dp.message(Command("unsubscribe"))
async def unsubscribe_cmd(message: types.Message):
    user_id = message.from_user.id
    if db.remove_subscriber(user_id):
        await message.answer("❌ Вы отписались от рассылки.", reply_markup=создать_клавиатуру())
    else:
        await message.answer("ℹ️ Вы не были подписаны.", reply_markup=создать_клавиатуру())

# ============ ОБРАБОТКА КНОПОК ============

@dp.message()
async def handle_buttons(message: types.Message):
    текст = message.text
    
    if текст == "📅 Сегодня":
        await today_cmd(message)
    
    elif текст == "📅 Завтра":
        await tomorrow_cmd(message)
    
    elif текст == "🔵 Числитель":
        день = парсер.получить_сегодняшний_день()
        расписание = парсер.получить_расписание_принудительно(день, "числитель")
        await message.answer(расписание, reply_markup=создать_клавиатуру())
    
    elif текст == "🔴 Знаменатель":
        день = парсер.получить_сегодняшний_день()
        расписание = парсер.получить_расписание_принудительно(день, "знаменатель")
        await message.answer(расписание, reply_markup=создать_клавиатуру())
    
    elif текст == "📊 Неделя":
        await week_cmd(message)
    
    elif текст == "🔄 Замены":
        if парсер.есть_замены():
            замены = парсер.получить_текст_замен()
        else:
            замены = "📝 Замен пока нет\nИспользуйте /update для обновления"
        await message.answer(замены, reply_markup=создать_клавиатуру())
    
    elif текст == "🔔 Подписка":
        user_id = message.from_user.id
        count = db.get_subscribers_count()
        if db.is_subscriber(user_id):
            текст = f"✅ Вы подписаны\n👥 Всего подписчиков: {count}"
        else:
            текст = f"❌ Вы не подписаны\n👥 Всего подписчиков: {count}\nПодписаться: /subscribe"
        await message.answer(текст, reply_markup=создать_клавиатуру())
    
    elif текст == "❓ Помощь":
        await help_cmd(message)
    
    else:
        await message.answer("🤔 Используйте кнопки ниже", reply_markup=создать_клавиатуру())

# ============ ЗАПУСК ============

async def start_bot():
    """Запускаем Telegram бота"""
    print("=" * 50)
    print("🤖 ЗАПУСК ТЕЛЕГРАМ БОТА")
    print("=" * 50)
    
    # Инициализация
    парсер.загрузить_расписание()
    print(f"✅ Расписание загружено")
    print(f"✅ Подписчиков: {db.get_subscribers_count()}")
    print(f"✅ Токен: {BOT_TOKEN[:10]}...")
    
    # Запускаем keep-alive сервер
    print("🌐 Запуск keep-alive сервера...")
    await keep_alive.start()
    
    print("🚀 Бот запущен и готов к работе!")
    print("=" * 50)
    
    # Запускаем бота
    await dp.start_polling(bot)

async def main():
    """Основная функция"""
    try:
        await start_bot()
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        await keep_alive.stop()

if __name__ == '__main__':
    # Проверяем зависимости
    try:
        import aiogram
        print(f"✅ Aiogram {aiogram.__version__}")
    except ImportError:
        print("❌ Установите: pip install aiogram aiohttp")
        exit(1)
    
    # Запускаем
    asyncio.run(main())