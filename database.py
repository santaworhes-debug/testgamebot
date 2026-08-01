import aiosqlite
from config import DATABASE_PATH

class Database:
    def __init__(self):
        self.path = DATABASE_PATH

    async def init(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                hp INTEGER DEFAULT 100,
                max_hp INTEGER DEFAULT 100,
                attack INTEGER DEFAULT 10,
                defense INTEGER DEFAULT 5,
                gold INTEGER DEFAULT 100,
                last_battle TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            await db.execute('''CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_id TEXT,
                quantity INTEGER DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES players(user_id)
            )''')
            await db.commit()

    async def get_player(self, user_id: int) -> dict:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM players WHERE user_id=?", (user_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def create_player(self, user_id: int, username: str):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT OR IGNORE INTO players (user_id, username) VALUES (?, ?)", (user_id, username))
            await db.commit()

    async def update_player(self, user_id: int, **kwargs):
        set_clause = ", ".join(f"{k}=?" for k in kwargs)
        values = list(kwargs.values()) + [user_id]
        async with aiosqlite.connect(self.path) as db:
            await db.execute(f"UPDATE players SET {set_clause} WHERE user_id=?", values)
            await db.commit()

    async def get_inventory(self, user_id: int) -> list:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM inventory WHERE user_id=?", (user_id,))
            return [dict(row) for row in await cursor.fetchall()]

    async def add_item(self, user_id: int, item_id: str, quantity: int = 1):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?) ON CONFLICT DO UPDATE SET quantity=quantity+?", (user_id, item_id, quantity, quantity))
            await db.commit()