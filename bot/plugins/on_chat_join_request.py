from pyrogram import Client, types

from bot.utils import add_request_join
from database import db


@Client.on_chat_join_request()
async def new_chat_member_main(app: Client, message: types.ChatJoinRequest):
    force_sub = (await db.config.get_config("force_sub_config")) or {}
    force_sub = force_sub.get("value", {})
    if not force_sub:
        return
    if str(message.chat.id) not in force_sub:
        return
    sub = force_sub[str(message.chat.id)]
    if not sub["status"]:
        return
    if sub["method"] == "direct":
        await message.approve()
        return
    if sub["method"] == "request":
        await add_request_join(message.chat.id, message.from_user.id)
