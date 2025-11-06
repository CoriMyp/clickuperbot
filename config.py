import sqlite3 as sql


# API KEYS
OPENAI_API_KEY = "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"
CLICKUP_API_KEY = "pk_95600051_OAUZ04UD3OHDCJROXIIX0YUIWG6UDY6E"


# BOT CONFIG
BOT_TOKEN = "7905278318:AAFcxeKoyLmJ_V_CNrzHVVOutkmQAw6rN9M"
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
