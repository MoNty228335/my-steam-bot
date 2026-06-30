import aiosqlite

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

async def add_account(game, login, password, email, email_pass):
    async with aiosqlite.connect("database.db") as db:
        await db.execute(
            "INSERT INTO accounts (game, login, password, email, email_pass) VALUES (?, ?, ?, ?, ?)",
            (game, login, password, email, email_pass)
        )
        await db.commit()
