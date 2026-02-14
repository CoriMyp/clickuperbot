import sqlite3 as sql
import dotenv
import os

dotenv.load_dotenv()


# API KEYS
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLICKUP_API_KEY = os.getenv("CLICKUP_API_KEY")


# BOT CONFIG
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = "бот"
BOT_USERNAME = "@NASHEMESTOtask_bot"
BOT_ID = 7905278318
BOT_ADMINS = [
    447050022,
    1004461367,
    477475914,  # @WhoisZack
]


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
