import asyncio
import logging
import os
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получаем токен из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализация БД
async def setup_db():
    async with aiosqlite.connect("database.db") as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS accounts
                            (id INTEGER PRIMARY KEY, game TEXT, login TEXT, 
                             password TEXT, email TEXT, email_pass TEXT, 
                             status TEXT, timer TEXT)''')
        await db.commit()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🔑 ДАННЫЕ"), types.KeyboardButton(text="⚡ КИКНУТЬ")],
            [types.KeyboardButton(text="📋 СТАТУС"), types.KeyboardButton(text="🔴 СТОП ВСЕХ")]
        ],
        resize_keyboard=True
    )
    await message.answer("Тихий Страж 7.1 активирован. Выберите действие:", reply_markup=keyboard)

# Веб-сервер для Render (чтобы инстанс не засыпал)
async def web_server():
    async def handle(request):
        return web.Response(text="Бот запущен!")
    
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()

# Основная функция запуска
async def main():
    await setup_db()
    await web_server()
    print("Тихий Страж 7.1 активирован. База данных готова.")
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
