import asyncio
import os
import logging
import asyncpg
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
DATABASE_URL = os.environ.get("DATABASE_URL") # Берется из настроек Render
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class AddAccount(StatesGroup):
    waiting_for_data = State()

# --- БАЗА ДАННЫХ (SUPABASE/POSTGRES) ---
async def get_db_conn():
    return await asyncpg.connect(DATABASE_URL)

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
    await message.answer("Тихий Страж 7.1 (Cloud) активирован.", reply_markup=get_main_kb())

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
    
    conn = await get_db_conn()
    await conn.execute("INSERT INTO accounts (game, login, password, email, email_pass) VALUES ($1, $2, $3, $4, $5)", *data)
    await conn.close()
    await message.answer("✅ Аккаунт успешно сохранен в облако!")
    await state.clear()

# --- ЛОГИКА [СТАТУС И УДАЛЕНИЕ] ---
@dp.message(F.text == "📋 СТАТУС")
async def show_status(message: types.Message):
    conn = await get_db_conn()
    rows = await conn.fetch("SELECT id, game, login FROM accounts")
    await conn.close()
    
    if not rows: return await message.answer("База пуста.")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{r['game']} | {r['login']}", callback_data=f"acc_{r['id']}")] for r in rows
    ])
    await message.answer("Список аккаунтов:", reply_markup=kb)

@dp.callback_query(F.data.startswith("acc_"))
async def manage_account(callback: types.CallbackQuery):
    acc_id = callback.data.split("_")[1]
    conn = await get_db_conn()
    acc = await conn.fetchrow("SELECT * FROM accounts WHERE id = $1", int(acc_id))
    await conn.close()
    
    if acc:
        info = f"🎮 {acc['game']}\n👤 Логин: {acc['login']}\n🔑 Пароль: {acc['password']}\n📧 Почта: {acc['email']}\n🔐 Пароль почты: {acc['email_pass']}"
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🗑 Удалить аккаунт", callback_data=f"del_{acc_id}")]])
        await callback.message.answer(f"📋 Данные аккаунта:\n\n{info}", reply_markup=kb)

@dp.callback_query(F.data.startswith("del_"))
async def delete_account(callback: types.CallbackQuery):
    acc_id = callback.data.split("_")[1]
    conn = await get_db_conn()
    await conn.execute("DELETE FROM accounts WHERE id = $1", int(acc_id))
    await conn.close()
    await callback.message.answer(f"✅ Аккаунт ID {acc_id} удален.")

# --- ЗАПУСК ---
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Бот на посту!"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080)))
    await site.start()

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
