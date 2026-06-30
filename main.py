import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация
TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- КНОПКИ ---
def get_main_kb():
    kb = [
        [KeyboardButton(text="🔑 ДАННЫЕ"), KeyboardButton(text="⚡ КИКНУТЬ")],
        [KeyboardButton(text="➕ ДОБАВИТЬ"), KeyboardButton(text="📋 СТАТУС")],
        [KeyboardButton(text="🔴 СТОП ВСЕХ")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Тихий Страж 7.1 активирован. Выберите действие:", reply_markup=get_main_kb())

# --- KEEP-ALIVE (Для Render) ---
async def web_handler(request):
    return web.Response(text="Бот на посту!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', web_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    # Используем порт из переменных окружения Render
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Веб-сервер запущен на порту {port}")

# --- ОСНОВНОЙ ЗАПУСК ---
async def main():
    # Запускаем веб-сервер для удержания инстанса
    await start_web_server()
    # Запускаем бота
    print("Тихий Страж 7.1 активирован. Ожидание обновлений...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
