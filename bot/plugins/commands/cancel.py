import pyrogram

from bot.utils import handle_reply


@pyrogram.Client.on_message(pyrogram.filters.regex(pattern=r"^Cancel$"))
async def cancel(bot, message):
    key = "cancel"
    await handle_reply(message, key, "Cancelled", reply_markup=pyrogram.types.ReplyKeyboardRemove())