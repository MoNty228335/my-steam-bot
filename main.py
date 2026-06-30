import asyncio
import os
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация
TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояние для формы добавления
class AddAccount(StatesGroup):
    waiting_for_data = State()

# --- БАЗА ДАННЫХ ---
async def setup_db():
    async with aiosqlite.connect("database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game TEXT,
                login TEXT,
                password TEXT,
                email TEXT,
                email_pass TEXT,
                status TEXT DEFAULT 'Active'
            )
        """)
        await db.commit()

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

# --- ЛОГИКА [➕ ДОБАВИТЬ] ---
@dp.message(F.text == "➕ ДОБАВИТЬ")
async def add_start(message: types.Message, state: FSMContext):
    await message.answer("Введите данные через пробел:\nИгра Логин Пароль Почта Пароль_почты")
    await state.set_state(AddAccount.waiting_for_data)

@dp.message(AddAccount.waiting_for_data)
async def process_data(message: types.Message, state: FSMContext):
    data = message.text.split()
    if len(data) < 5:
        await message.answer("Ошибка! Нужно ввести ровно 5 параметров через пробел.")
        return
    
    # Сохраняем в БД
    async with aiosqlite.connect("database.db") as db:
        await db.execute(
            "INSERT INTO accounts (game, login, password, email, email_pass) VALUES (?, ?, ?, ?, ?)",
            (data[0], data[1], data[2], data[3], data[4])
        )
        await db.commit()
        
    await message.answer(f"✅ Аккаунт игры {data[0]} успешно добавлен в базу!")
    await state.clear()

# --- KEEP-ALIVE ---
async def web_handler(request):
    return web.Response(text="Бот на посту!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', web_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- ЗАПУСК ---
async def main():
    await setup_db()
    await start_web_server()
    print("Тихий Страж 7.1 активирован. База данных готова.")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
