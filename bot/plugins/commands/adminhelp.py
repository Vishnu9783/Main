from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from bot.config import Config
from bot.utils import check


@Client.on_message(filters.command("admin") & filters.private & filters.incoming)
@Client.on_callback_query(filters.regex(pattern=r"^admin$"))
@check
async def admin(bot: Client, message: Message):
    text = "Admin Commands\n\n"
    text += " /stats - To Get Bot Stats\n"
    text += " /user - To Get User Details\n"
    text += " /delete - To Delete A File\n"
    text += " /broadcast - To Broadcast A Message\n"
    text += " /genlink - To Generate A Link\n"
    text += "\nOwner Only Commands\n\n"
    text += " /addadmin - To Add An Admin\n"
    text += " /removeadmin - To Remove An Admin\n"
    text += " /admins - To Get A List Of Admins\n"
    buttons = [
        [
            InlineKeyboardButton("Banned Users", callback_data="banned_users"),
            InlineKeyboardButton("Total Users", callback_data="total_users"),
        ],
        [
            InlineKeyboardButton("Stats", callback_data="stats"),
        ],
    ]

    func = (
        message.reply_text
        if isinstance(message, Message)
        else message.edit_message_text
    )
    await func(
        text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True
    )
