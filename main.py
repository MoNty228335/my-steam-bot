import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
import aiosqlite

# Получаем токен из системных настроек Render
BOT_TOKEN = os.environ.get("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def setup_db():
    async with aiosqlite.connect("database.db") as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS accounts 
                          (id INTEGER PRIMARY KEY, game TEXT, login TEXT, 
                           password TEXT, email TEXT, email_pass TEXT, 
                           status TEXT, timer TEXT)''')
        await db.commit()

async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()

async def main():
    await setup_db()
    # Запускаем веб-сервер для Render
    await web_server()
    print("Тихий Страж 7.1 активирован. База данных готова.")
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
