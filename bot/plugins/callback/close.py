from pyrogram import Client, filters
from pyrogram.types import CallbackQuery


@Client.on_callback_query(filters.regex(pattern=r"^close$"))
async def close(bot: Client, message: CallbackQuery):
    await message.message.delete()
