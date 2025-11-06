from aiogram import Bot, types
from aiogram.enums import ParseMode
import json

import config


def is_bot_mentioned(msg: types.Message) -> bool:
    """
    Checks if the message starts with the bot's name or username (case insensitive).
    """
    text = msg.text or ""
    bot_names = (config.BOT_NAME.lower(), config.BOT_USERNAME.lower())
    return text.lower().startswith(bot_names)


def clean_up_text(text: str) -> str:
    """
    Cleans up the text of the message by removing the bot's name or username.
    """
    if text.startswith(config.BOT_NAME):
        text = text.split(config.BOT_NAME, maxsplit=1)[1]
    else:
        text = text.split(config.BOT_USERNAME, maxsplit=1)[1]
    return text.strip()


def parse_json(text: str) -> dict:
    """
    Parses a JSON string and returns a dictionary.
    """
    try:
        return json.loads(text)
    except json.decoder.JSONDecodeError:
        raise Exception(f"[JSON] can't convert: {text}")


async def error_msg(bot: Bot, msg: types.Message, text: str) -> None:
    """
    Sends an error message to the admins.
    """
    await msg.react(reaction=[types.ReactionTypeEmoji(emoji="💔")])

    for admin in config.BOT_ADMINS:
        await bot.send_message(admin, text, parse_mode=ParseMode.MARKDOWN_V2)
