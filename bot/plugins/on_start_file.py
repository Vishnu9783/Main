import datetime
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from bot.utils import human_readable_time
from database import db
from asyncio import sleep


async def get_file(bot: Client, message: Message):
    user_chat_id = message.from_user.id

    message_delete_time = await get_config_value("message_delete_time")
    file_delete_time = await get_config_value("file_delete_time")

    command = message.command[1]

    if command.startswith("download_"):
        file_id = command.split("_", 1)[1]
        file = await db.files.col.find_one({"_id": file_id})

        if not file:
            await message.reply_text("File Not Found")
            return
        await db.users.update_user(user_chat_id, {"files_received": 1}, "inc")
        file_message = await handle_file(
            bot, user_chat_id, file, message_delete_time, file_delete_time
        )
        if not file_message:
            await message.reply_text("File Not Found")

    elif command.startswith("batch_"):
        await batch_handler(bot, message, message_delete_time, file_delete_time)

    await schedule_deletion(message.chat.id, message.id, file_delete_time)


async def get_config_value(key: str, default: int = 0):
    config = await db.config.get_config(key)
    return config.get("value", default)


async def schedule_deletion(chat_id: int, message_id: int, delete_time: int):
    if delete_time > 0:
        time = datetime.datetime.now() + datetime.timedelta(seconds=delete_time)
        await db.del_schedule.add_schedule(chat_id, message_id, time)


async def handle_file(
    bot: Client,
    user_chat_id: int,
    file: dict,
    message_delete_time: int,
    file_delete_time: int,
):
    message_id, chat_id = map(int, file["log"].split("-", 1))
    message = await bot.get_messages(chat_id, message_id)

    if message.empty:
        return None

    caption = message.caption.html if message.caption else ""
    file_message = await copy_message(message, user_chat_id, caption=caption[:1000], reply_markup=None)

    temp_message = await file_message.reply_text(
        f"Your 📁 file will auto delete in ⏰ {human_readable_time(message_delete_time)}.↗ Forward it anywhere or save it privately before downloading."
    )

    await schedule_deletion(temp_message.chat.id, temp_message.id, message_delete_time)
    await schedule_deletion(file_message.chat.id, file_message.id, file_delete_time)

    return file_message


async def batch_handler(
    bot: Client, message: Message, message_delete_time: int, file_delete_time: int
):
    user_chat_id = message.from_user.id
    _, batch_id = message.command[1].split("_", 1)

    batch = await db.files.get_batch(batch_id)
    if not batch:
        await message.reply_text("Invalid Batch ID")
        return

    del_files = []
    total_files = len(batch["files"])
    await db.users.update_user(user_chat_id, {"files_received": total_files}, "inc")
    for file in batch["files"]:
        message_id, chat_id = file["message_id"], file["chat_id"]
        message = await bot.get_messages(chat_id, message_id)

        if message.empty:
            continue

        caption = message.caption.html if message.caption else ""
        caption = caption[:1000]
        try:
            file_message = await copy_message(
                message, user_chat_id, caption=caption, reply_markup=None
            )
        except FloodWait as e:
            await sleep(e.value)
            file_message = await copy_message(
                message, user_chat_id, caption=caption, reply_markup=None
            )

        del_files.append(file_message.id)
        await sleep(1)

    temp_message = await message.reply_text(
        f"Your 📁 files will auto delete in ⏰ {human_readable_time(file_delete_time)}.↗ Forward them anywhere or save them privately before downloading."
    )

    await schedule_deletion(temp_message.chat.id, temp_message.id, message_delete_time)

    for file_message_id in del_files:
        await schedule_deletion(user_chat_id, file_message_id, file_delete_time)


async def copy_message(message: Message, chat_id: int, **kwargs):
    return await message.copy(chat_id=chat_id, **kwargs)
