from contextlib import suppress
import re
from pyrogram import Client, filters, types
from database import db
from bot.utils import check, human_readable_time
from bot.config import Config
import random
import string


@Client.on_message(filters.private & filters.command("genlink"))
@check
async def link_generator(client: Client, message: types.Message):
    while True:
        try:
            ask_text = "Forword message from DB Channel\nOr send the DB Channel post link\n"
            ask_text += "Or send any text directly to get the link\n\n/cancel to cancel the process"
            channel_message = await client.ask(
                text=ask_text,
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except:
            return

        if channel_message.text and channel_message.text.lower() == "/cancel":
            await message.reply_text("Process Cancelled")
            return

        msg_id, channel_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply(
                "❌ Error\n\nthis Forwarded Post Is Not From My DB Channel Or This Link Is Not Taken From DB Channel",
                quote=True,
            )
            continue

    _id = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    await db.files.add_file(
        _id,
        message.from_user.id,
        f"{msg_id}-{channel_id}",
    )

    link = f"https://t.me/{client.me.username}?start=download_{_id}"
    reply_markup = types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton(
                    "🔁 Share URL", url=f"https://telegram.me/share/url?url={link}"
                )
            ]
        ]
    )
    await channel_message.reply_text(
        f"<b>Here Is Your Link</b>\n\n{link}", quote=True, reply_markup=reply_markup
    )


async def get_message_id(client, message: types.Message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == Config.CHANNELS:
            return message.forward_from_message_id, message.forward_from_chat.id
        else:
            return 0, 0
    elif message.forward_sender_name:
        return 0, 0
    elif message.text:
        pattern = "https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern, message.text)
        if not matches:
            log = await client.send_message(
                chat_id=Config.CHANNELS,
                text=message.text.html,
                disable_web_page_preview=True,
            )
            return log.id, Config.CHANNELS
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if int(f"-100{channel_id}") == Config.CHANNELS:
                return msg_id, int(f"-100{channel_id}")
        else:
            if channel_id == Config.CHANNELS:
                return msg_id, channel_id
    else:
        return 0, 0
