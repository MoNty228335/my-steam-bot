import asyncio
import logging
from aiogram import Bot, Dispatcher
import aiosqlite 

# ВСТАВЬ СЮДА СВОЙ ТОКЕН МЕЖДУ КАВЫЧЕК
TOKEN = "7661253341:AAFBZegyYKmJoyXbSZbdx8-QUZwMgfhkYcI"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def setup_db():
    async with aiosqlite.connect("database.db") as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS accounts 
                            (id INTEGER PRIMARY KEY, game TEXT, login TEXT, 
                             password TEXT, email TEXT, email_pass TEXT, 
                             status TEXT, timer TEXT)''')
        await db.commit()

async def main():
    await setup_db()
    print("Тихий Страж 7.1 активирован. База данных готова.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
