import sqlite3 as sql


# API KEYS
OPENAI_API_KEY = "***"
CLICKUP_API_KEY = "***"


# BOT CONFIG
BOT_TOKEN = "***"
BOT_NAME = "бот"
BOT_USERNAME = "***"
BOT_ID = 000
BOT_ADMINS = []


# db init
db = sql.connect("data.db")
execute = db.cursor().execute

execute(
    """CREATE TABLE IF NOT EXISTS members(
    username TEXT,
    name TEXT
)"""
)

execute(
    """CREATE TABLE IF NOT EXISTS data(
    key TEXT,
    value TEXT
)"""
)

if execute("SELECT key FROM data WHERE key='folder'").fetchone() is None:
    execute("INSERT OR IGNORE INTO data(key, value) VALUES (?, ?)", ("folder", ""))
    execute("INSERT OR IGNORE INTO data(key, value) VALUES (?, ?)", ("list", ""))

db.commit()
