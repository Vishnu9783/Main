import string
import random
from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config
from bot.utils import handle_floodwait
from database import db


async def on_channel_media(bot: Client, message: Message):
    message = await process_update_new_channel_message(bot, message)
    if not message:
        return

    if message.sticker:
        return

    media = process_media(message)
    if not media:
        return

    log = message

    _id = generate_unique_id()
    await db.files.add_file(
        _id,
        Config.OWNER_ID,
        f"{log.id}-{log.chat.id}",
    )

    short_link = await get_shortened_link(log, _id)

    await update_message_reply_markup(message, short_link)


async def process_update_new_channel_message(bot, message):
    message = message.message
    if not message.media or message.fwd_from:
        return None

    channel_id = int(f"-100{message.peer_id.channel_id}")
    if channel_id != Config.CHANNELS:
        print(f"Channel {channel_id} != Config.CHANNELS")
        return None
    message.peer_id.channel_id = f"-100{message.peer_id.channel_id}"
    return await bot.get_messages(message.peer_id.channel_id, message.id)


def process_media(message):
    media = getattr(message, message.media.value)
    return media or None


def generate_unique_id():
    return "".join(random.choice(string.ascii_lowercase) for _ in range(10))


def get_filename(media):
    return media.file_name if getattr(media, "file_name", None) else "Not Available"


async def get_shortened_link(message, _id):
    username = message._client.me.username
    return f"https://t.me/{username}?start=download_{_id}"


async def update_message_reply_markup(message: Message, short_link):
    await handle_floodwait(
        message.edit_reply_markup,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📥 Open",
                        url=short_link,
                    ),
                    InlineKeyboardButton(
                        "🔁 Share",
                        url=f"https://telegram.me/share/url?url={short_link}",
                    ),
                ],
            ]
        ),
    )
