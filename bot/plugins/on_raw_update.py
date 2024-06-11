from pyrogram import Client, ContinuePropagation
from pyrogram.raw.types import UpdateNewChannelMessage

from bot.plugins.on_channel_media import on_channel_media


@Client.on_raw_update()
async def on_raw_update(bot, update, users, chats):
    if isinstance(update, UpdateNewChannelMessage):
        await on_channel_media(bot, update)
    else:
        raise ContinuePropagation
