import asyncio
import os
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# Настройка
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class AddAccount(StatesGroup):
    waiting_for_data = State()

# --- БАЗА ДАННЫХ ---
async def setup_db():
    async with aiosqlite.connect("database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game TEXT, login TEXT, password TEXT, email TEXT, email_pass TEXT
            )
        """)
        await db.commit()

# --- КЛАВИАТУРА ---
def get_main_kb():
    kb = [
        [KeyboardButton(text="🔑 ДАННЫЕ"), KeyboardButton(text="⚡ КИКНУТЬ")],
        [KeyboardButton(text="➕ ДОБАВИТЬ"), KeyboardButton(text="📋 СТАТУС")],
        [KeyboardButton(text="🔴 СТОП ВСЕХ")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Тихий Страж 7.1 активирован.", reply_markup=get_main_kb())

# --- ЛОГИКА [ДОБАВИТЬ] ---
@dp.message(F.text == "➕ ДОБАВИТЬ")
async def add_start(message: types.Message, state: FSMContext):
    await message.answer("Введите через пробел:\nИгра Логин Пароль Почта Пароль_почты")
    await state.set_state(AddAccount.waiting_for_data)

@dp.message(AddAccount.waiting_for_data)
async def process_data(message: types.Message, state: FSMContext):
    data = message.text.split()
    if len(data) < 5:
        return await message.answer("Ошибка! Нужно ввести 5 параметров.")
    async with aiosqlite.connect("database.db") as db:
        await db.execute("INSERT INTO accounts (game, login, password, email, email_pass) VALUES (?, ?, ?, ?, ?)", data)
        await db.commit()
    await message.answer("✅ Аккаунт успешно сохранен!")
    await state.clear()

# --- ЛОГИКА [СТАТУС И УДАЛЕНИЕ] ---
@dp.message(F.text == "📋 СТАТУС")
async def show_status(message: types.Message):
    async with aiosqlite.connect("database.db") as db:
        cursor = await db.execute("SELECT id, game, login FROM accounts")
        rows = await cursor.fetchall()
        if not rows: return await message.answer("База пуста.")
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{row[1]} | {row[2]}", callback_data=f"acc_{row[0]}")] for row in rows
        ])
        await message.answer("Список аккаунтов:", reply_markup=kb)

@dp.callback_query(F.data.startswith("acc_"))
async def manage_account(callback: types.CallbackQuery):
    acc_id = callback.data.split("_")[1]
    async with aiosqlite.connect("database.db") as db:
        async with db.execute("SELECT * FROM accounts WHERE id = ?", (acc_id,)) as cursor:
            acc = await cursor.fetchone()
    
    if acc:
        info = f"🎮 {acc[1]}\n👤 Логин: {acc[2]}\n🔑 Пароль: {acc[3]}\n📧 Почта: {acc[4]}\n🔐 Пароль почты: {acc[5]}"
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🗑 Удалить аккаунт", callback_data=f"del_{acc_id}")]])
        await callback.message.answer(f"📋 Данные аккаунта:\n\n{info}", reply_markup=kb)

@dp.callback_query(F.data.startswith("del_"))
async def delete_account(callback: types.CallbackQuery):
    acc_id = callback.data.split("_")[1]
    async with aiosqlite.connect("database.db") as db:
        await db.execute("DELETE FROM accounts WHERE id = ?", (acc_id,))
        await db.commit()
    await callback.message.answer(f"✅ Аккаунт ID {acc_id} удален.")

# --- KEEP-ALIVE & ЗАПУСК ---
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Бот на посту!"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080)))
    await site.start()

async def main():
    await setup_db()
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
