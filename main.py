from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
import asyncio

from clickup import new_task
from config import db, execute
import config
import utils, gpt


# bot init
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()


# command "/setname <NAME>" which will be used to mention bot
@dp.message(Command("setname"), F.chat.type == "private")
async def set_name(msg: types.Message):
    splitted = msg.text.split(maxsplit=1)
    if len(splitted) != 2:
        await msg.answer(
            f"Bot named as *{config.BOT_NAME}*", parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    config.BOT_NAME = splitted[1]

    await msg.answer(
        f"Bot named as *{config.BOT_NAME}*", parse_mode=ParseMode.MARKDOWN_V2
    )


# command "/add <USERNAME> <NAME>" will add a member which may be used at tasks
# USERNAME - username from TG (like @username) - can be extracted from message entities
# NAME - name from ClickUp
@dp.message(Command("add"), F.chat.type == "private")
async def add_member(msg: types.Message):
    # Try to extract username from message entities first
    entity_mentions = utils.extract_mentions(msg)

    # Validate command arguments (username and name)
    splitted = msg.text.split(maxsplit=2)
    if len(splitted) < 2:
        return

    # Use entity mention if available, otherwise fallback to command argument
    if entity_mentions:
        username = entity_mentions[0]  # Already normalized to lowercase
        if len(splitted) < 3:
            await msg.answer("Please provide a name for the member.")
            return
        name = splitted[2]
    else:
        if len(splitted) != 3:
            return
        username = splitted[1].lower()
        name = splitted[2]

    # Add member to database
    execute(
        "INSERT INTO members VALUES (?, ?)",
        (
            username.lower(),  # normalized to lowercase (safety net)
            name,
        ),
    )
    db.commit()

    await msg.answer(
        f"{username} was added as *{name}*", parse_mode=ParseMode.MARKDOWN_V2
    )


# command "/del <USERNAME>" will delete member from table by a TG username
# USERNAME can be extracted from message entities or provided as command argument
@dp.message(Command("del"), F.chat.type == "private")
async def del_member(msg: types.Message):
    # Try to extract username from message entities first
    entity_mentions = utils.extract_mentions(msg)

    if entity_mentions:
        username = entity_mentions[0]  # Already normalized to lowercase
    else:
        # Fallback to command argument
        splitted = msg.text.split(maxsplit=1)
        if len(splitted) != 2:
            await msg.answer("Please provide a username or mention a user.")
            return
        username = splitted[1].lower()

    execute("DELETE FROM members WHERE username = ?", (username,))
    db.commit()

    await msg.answer(f"{username} was deleted")


# command "/members" will display all added members to a table
@dp.message(Command("members"), F.chat.type == "private")
async def list_members(msg: types.Message):
    members = execute("SELECT * FROM members").fetchall()

    text = "List of members:\n"

    for username, name in members:
        text += f"*{name}* {username}\n"

    await msg.answer(text=text, parse_mode=ParseMode.MARKDOWN_V2)


# command "/saveto <FOLDER>:<LIST>" will be set folder:list where to save tasks
@dp.message(Command("saveto"), F.chat.type == "private")
async def save_to(msg: types.Message):
    splitted = msg.text.split(maxsplit=1)
    if len(splitted) != 2:
        return

    folder = splitted[1].split(":")[0]
    list = splitted[1].split(":")[1]

    execute("UPDATE data SET value=? WHERE key=?", (folder, "folder"))
    execute("UPDATE data SET value=? WHERE key=?", (list, "list"))
    db.commit()

    await msg.answer(
        f"Path updated on:\n" f"Folder: *{folder}*\n" f"List: *{list}*",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


# command "/path" display where are saving tasks
@dp.message(Command("path"), F.chat.type == "private")
async def path(msg: types.Message):
    folder = execute("SELECT value FROM data WHERE key=?", ("folder",)).fetchone()[0]
    list = execute("SELECT value FROM data WHERE key=?", ("list",)).fetchone()[0]

    await msg.answer(
        "Tasks saving to:\n" f"Folder: *{folder}*\n" f"List: *{list}*",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


# handler for input messages where bot mentioned
@dp.message(F.text.is_not(None), F.chat.type.contains("group"))
async def message_handler(msg: types.Message):
    # check if bot mentioned in message (by name or username)
    if not utils.is_bot_mentioned(msg):
        return
    
    msg_text = utils.clean_up_text(msg)
    if not msg_text:
        print("Message text is empty after clean_up_text (bot name/username removal)")
        return

    # get response from AI
    response = "Something wrong with ChatGPT response"
    try:
        response = gpt.get_response(msg_text)
    except Exception as e:
        await utils.error_msg(bot, msg, text=("Error from AI\n" "```\n" f"{e}" "\n```"))

    # try to parse json from AI-response
    try:
        parsed = utils.parse_json(response)
        print('Parsed from LLM:', parsed)
    except Exception:
        await utils.error_msg(
            bot,
            msg,
            text=("Can't convert to json this text:\n" "```\n" f"{response}" "\n```"),
        )
        print("Can't receive parsed data from ChatGPT response")
        return

    # Extract actual @mentions from message entities (more reliable than AI parsing)
    entity_mentions = utils.extract_mentions(msg)

    # Merge entity-extracted mentions with AI-parsed users
    # Prioritize entity mentions, then add AI-parsed users that aren't already included
    all_users = list(
        set(entity_mentions)
    )  # Start with entity mentions (unique, lowercase)

    # Process AI-parsed users and normalize to lowercase
    for user in parsed.get("users", []):
        if not isinstance(user, str):
            continue
        user_lower = user.lower()

        # Replace @sender with actual username (normalized to lowercase)
        if user_lower == "@sender":
            if msg.from_user.username:
                sender_username = f"@{msg.from_user.username}".lower()
                if sender_username not in all_users:
                    all_users.append(sender_username)
        elif user_lower not in all_users:
            all_users.append(user_lower)

    parsed["users"] = all_users
    print('Parsed after username patch:', parsed)

    # creating task on ClickUp
    try:
        new_task(
            parsed["name"], parsed["description"], parsed["users"], parsed["deadline"], utils.is_task_complete(msg)
        )
        await msg.react(reaction=[types.ReactionTypeEmoji(emoji="❤️")])
    except Exception as e:
        await utils.error_msg(
            bot, msg, "Error on creating new task\n" "```\n" f"{e}" "\n```"
        )


async def main():
    bot_user_entity = await bot.get_me()
    print(f"[clickuperbot] started as @{bot_user_entity.username}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
