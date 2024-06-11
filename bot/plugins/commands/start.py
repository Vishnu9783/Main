from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup
from bot.config import Config, Script, Buttons
from bot.plugins.on_start_file import get_file
from bot.utils import add_new_user, get_admins, handle_reply
from database import db


@Client.on_message(filters.command("start") & filters.private & filters.incoming)
@Client.on_callback_query(filters.regex(pattern=r"^start$"))
async def start(bot: Client, message: Message):
    chat_id = message.from_user.id
    admins = await get_admins()
    is_new_user = await add_new_user(message.from_user.id)
    banned_users = await db.users.get_all_banned_users()
    banned_users_ids = [user["_id"] for user in banned_users]

    if chat_id in banned_users_ids:
        return await message.reply_text("You are banned from using this bot.")

    if is_new_user:
        text = Script.NEW_USER_MESSAGE.format(
            mention=message.from_user.mention, user_id=message.from_user.id
        )
        await bot.send_message(Config.LOG_CHANNEL, text)

    if isinstance(message, Message) and len(message.command) > 1:
        return await get_file(bot, message)

    if chat_id not in admins:
        text = Script.START_MESSAGE.format(first_name=message.from_user.first_name)
        await handle_reply(
            message, text, reply_markup=InlineKeyboardMarkup(Buttons.USER_START_BUTTONS)
        )
        return

    text = Script.START_MESSAGE.format(first_name=message.from_user.first_name)
    await handle_reply(
        message, text, reply_markup=InlineKeyboardMarkup(Buttons.START_BUTTONS)
    )
