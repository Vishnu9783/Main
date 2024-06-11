from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config
from bot.utils import check, handle_floodwait
from database import db
import random
import string


# Define the main event handler
@Client.on_message(filters.media & (filters.private | filters.group), group=1)
@check
async def on_media(bot: Client, message: Message):
    await handle_media_message(message)


# Function to handle media messages
async def handle_media_message(message):
    sts = await message.reply_text("Processing...", quote=True)
    await process_media(message, sts)


async def get_shortened_link(message, file_id):
    username = message._client.me.username
    return f"https://t.me/{username}?start=download_{file_id}"


# Function to process media files
async def process_media(message, sts):
    _id = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    text = message.caption.html if message.caption else ""

    log: Message = await handle_floodwait(message.copy, Config.CHANNELS, caption=text)

    await db.files.add_file(
        _id,
        message.from_user.id,
        f"{log.id}-{log.chat.id}",
    )

    file_link = await get_shortened_link(log, _id)

    short_link = file_link
    text += f"\n\n**URL:** {short_link}"

    await handle_floodwait(
        log.copy,
        chat_id=message.from_user.id,
        caption=text,
        # reply_markup=markup,
    )
    await log.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📂 Open",
                        url=f"https://t.me/{message._client.me.username}?start=download_{_id}",
                    ),
                    InlineKeyboardButton(
                        "🔁 Share",
                        url=f"https://telegram.me/share/url?url={short_link}",
                    ),
                ]
            ]
        ),
    )

    await sts.delete()
