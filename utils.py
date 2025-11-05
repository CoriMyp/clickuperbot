from aiogram import Bot, types
from aiogram.enums import ParseMode
import json

import config


def is_bot_mentioned(msg: types.Message):
	if msg.text.startswith((config.BOT_NAME, config.BOT_USERNAME)):
		return True
	return None


def clean_up_text(text: str):
	if text.startswith(config.BOT_NAME):
		text = text.split(config.BOT_NAME, maxsplit=1)[1]
	else:
		text = text.split(config.BOT_USERNAME, maxsplit=1)[1]
	return text.strip()


def parse_json(text: str):
	try:
		return json.loads(text)
	except json.decoder.JSONDecodeError:
		raise Exception(f"[JSON] can't convert: {text}")
	

async def error_msg(bot: Bot, msg: types.Message, text):
	await msg.react(reaction=[types.ReactionTypeEmoji(emoji="💔")])

	for admin in config.BOT_ADMINS:
		await bot.send_message(admin, text,
		parse_mode=ParseMode.MARKDOWN_V2)
