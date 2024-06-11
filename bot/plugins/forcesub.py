from pyrogram import Client, StopPropagation, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import UserNotParticipant
from bot.config import Script
from bot.plugins.on_start_file import get_file
from bot.utils import get_admins, is_user_in_request_join
from database import db


@Client.on_message(filters.private & filters.incoming, group=-1)
async def forcesub(c: Client, m: Message):
    admins = await get_admins()
    if m.text and not m.text.startswith("/") and m.chat.id not in admins:
        return await m.reply(Script.NOT_ALLOWED_TEXT, quote=True)

    if m.text and len(m.text.split()) > 1:
        command = m.text.split()[1]
    else:
        command = ""

    if m.chat.id in admins:
        return await m.continue_propagation()
    else:
        if m.text and m.text.split()[0] != "/start":
            return await m.reply(Script.ARROGANT_REPLY, quote=True)

    out = await m.reply("Loading...")
    force_sub = (await db.config.get_config("force_sub_config")) or {}
    force_sub = force_sub.get("value", {})

    if not force_sub:
        await out.delete()
        await m.continue_propagation()
        return

    channel_status = await check_channels(c, m.from_user.id, force_sub)
    not_joined_channels = [ch for ch in channel_status if not ch["joined"]]

    if not_joined_channels:
        text = await create_channel_status_file(channel_status)
        buttons = []
        for i, channel in enumerate(channel_status, start=1):
            if not channel["joined"]:
                buttons.append(
                    InlineKeyboardButton(text=f"Join Channel {i}", url=channel["link"])
                )

        markup = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]

        markup.append(
            [
                InlineKeyboardButton(
                    text="🔄 Refresh", callback_data=f"refresh_{command}"
                )
            ]
        )
        await m.reply(
            text=text
            + "\nYou are not yet joined our channel. First join and then press the refresh button 🤤",
            reply_markup=InlineKeyboardMarkup(markup),
            quote=True,
        )
        await out.delete()
        raise StopPropagation

    await out.delete()
    await m.continue_propagation()


@Client.on_callback_query(filters.regex("^refresh"))
async def refresh_cb(c: Client, m):
    command = m.data.split("_", 1)[1] if len(m.data.split("_")) > 1 else ""
    await m.message.edit("Loading...")
    force_sub = (await db.config.get_config("force_sub_config")) or {}
    force_sub = force_sub.get("value", [])

    channel_status = await check_channels(c, m.from_user.id, force_sub)
    not_joined_channels = [ch for ch in channel_status if not ch["joined"]]

    if not_joined_channels:
        markup = [
            [InlineKeyboardButton(text=f"Join {i['name']}", url=i["link"])]
            for i in not_joined_channels
        ]
        markup.append(
            [
                InlineKeyboardButton(
                    text="🔄 Refresh", callback_data=f"refresh_{command}"
                )
            ]
        )
        filename = await create_channel_status_file(channel_status)
        await m.message.edit(
            text=f"Please join the following channels to use this bot:\n\n{filename}\n"
            "You are not yet joined our channel. First join and then press the refresh button 🤤",
            reply_markup=InlineKeyboardMarkup(markup),
        )
        return
    await m.message.edit("**You are Authorized 😎**\n\nNow you can use me 😉")

    if command:
        m.message.from_user = m.from_user
        m = m.message
        m.text = f"/start {command}"
        m.command = ["start", command]
        await get_file(c, m)


async def create_channel_status_file(channel_status):
    text = "Channel Status:\n\n"
    for i, channel in enumerate(channel_status, start=1):
        text += f"{i}. Channel {i} - {'✅ Joined' if channel['joined'] else '❌ Not Joined'}\n"
    return text


async def get_invite_link(bot, channel_id, method):
    return await bot.create_chat_invite_link(
        channel_id, creates_join_request=(method == "request")
    )


async def get_channel_status(channel_name, invite_link, joined):
    return {
        "name": channel_name,
        "joined": joined,
        "link": invite_link.invite_link,
    }


async def check_channels(bot: Client, user_id: int, force_sub: dict):

    channel_status = []

    for sub in force_sub.values():
        if not sub["status"]:
            continue

        channel_id = sub["channel_id"]
        channel_name = sub["title"]
        method = sub["method"]

        try:
            invite_link = await get_invite_link(bot, channel_id, method)
            chat = await bot.get_chat(channel_id)
        except Exception as e:
            print(e)
            continue

        try:
            is_requested = await is_user_in_request_join(channel_id, user_id)
            if method == "request" and not chat.username and is_requested:
                joined = is_requested
            else:
                await bot.get_chat_member(channel_id, user_id)
                joined = True
        except UserNotParticipant:
            joined = False
        except Exception as e:
            print(e)
            joined = False

        channel_status.append(
            await get_channel_status(channel_name, invite_link, joined)
        )

    return channel_status
