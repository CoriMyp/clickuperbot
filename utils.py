from aiogram import Bot, types
from aiogram.enums import ParseMode, MessageEntityType
import json

import config


def is_bot_mentioned(msg: types.Message) -> bool:
    """
    Checks if the bot is mentioned in the message.
    First checks for bot mention via entities, then falls back to text-based check.
    """
    # Check if bot is mentioned via entities (most reliable)
    if msg.entities:
        bot_username_lower = config.BOT_USERNAME.lower()
        for entity in msg.entities:
            if entity.type == MessageEntityType.MENTION:
                mention_text_lower = entity.extract_from(msg.text).lower()
                if mention_text_lower == bot_username_lower:
                    return True

    # Fallback to text-based check (for bot name)
    text = msg.text or ""
    bot_name_lower = config.BOT_NAME.lower()
    return text.lower().startswith(bot_name_lower)


def clean_up_text(msg: types.Message) -> str:
    """
    Cleans up the text of the message by removing the bot's name or username.
    Uses entities to accurately identify and remove bot mentions.
    """
    text = msg.text or ""
    bot_username_lower = config.BOT_USERNAME.lower()

    # Remove bot mentions found via entities (most accurate)
    if msg.entities:
        mentions_to_remove = []
        for entity in msg.entities:
            if entity.type == MessageEntityType.MENTION:
                mention_text = entity.extract_from(msg.text).lower()
                if mention_text == bot_username_lower:
                    # Extract the exact mention text (handles UTF-16 correctly)
                    exact_mention = entity.extract_from(msg.text)
                    mentions_to_remove.append(exact_mention)

        # Remove bot mentions from text
        for mention in mentions_to_remove:
            # Replace only the first occurrence to avoid removing wrong instances
            text = text.replace(mention, "", 1)

    # Fallback: remove bot name/username from start (for cases without entities)
    if text.startswith(config.BOT_USERNAME):
        text = text.replace(config.BOT_USERNAME, "", 1)
    # remove bot name (any case)
    for bot_name in [config.BOT_NAME, config.BOT_NAME.lower()]:
        if text.startswith(bot_name):
            text = text.replace(bot_name, "", 1)

    # clear spaces
    return text.strip()


def extract_mentions(msg: types.Message) -> list[str]:
    """
    Extract all @mentions from message entities (normalized to lowercase).
    Returns a list of usernames with @ prefix.
    """
    mentions = []
    if msg.entities:
        for entity in msg.entities:
            if entity.type == MessageEntityType.MENTION:
                mention_text = entity.extract_from(msg.text)
                mentions.append(mention_text.lower())
    return mentions


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
