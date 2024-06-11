from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup
from bot.config import Buttons
from bot.utils import handle_reply
from database import db


@Client.on_callback_query(filters.regex(pattern=r"^delete_file_"))
async def delete_file_cb(bot: Client, message: Message):
    key = "delete_file_cb"
    func = (
        message.reply_text
        if isinstance(message, Message)
        else message.edit_message_text
    )

    _id = message.data.split("_", 2)[2]

    await db.files.delete_file(_id)

    await handle_reply(message, key, "File deleted successfully", reply_markup=InlineKeyboardMarkup(Buttons.BACK_BUTTON))
