from pyrogram import Client, filters
from pyrogram.types import Message
from bot.config import Config, CONST
from bot.utils import check
from database import db
import psutil  # You'll need to install this package if not already installed
from datetime import datetime, timedelta
import shutil


cpu_usage = psutil.cpu_percent()
ram_usage = psutil.virtual_memory().percent
total_disk, used_disk, free_disk = shutil.disk_usage("/")


@Client.on_message(
    filters.command("stats")
    & filters.private
    & filters.incoming
)
@Client.on_callback_query(filters.regex(pattern=r"^stats$"))
@check
async def stats(bot: Client, message: Message):
    total_files = await db.files.col.count_documents({})
    total_users = await db.users.col.count_documents({})
    current_datetime = datetime.now()

    uptime = (current_datetime - CONST.START_TIME).total_seconds()
    uptime = str(timedelta(seconds=int(uptime)))
    date = current_datetime.strftime("%d-%B-%Y")
    time = current_datetime.strftime("%I:%M:%S %p")
    day = current_datetime.strftime("%A")
    utc = "+0530"

    bot_statistics = {
        "cpu_usage": f"{cpu_usage:.1f}%",
        "ram_usage": f"{ram_usage:.1f}%",
        "disk_size": f"{total_disk / (1024 ** 3):.2f}GB",
        "disk_used": f"{used_disk / (1024 ** 3):.2f}GB",
        "free_disk": f"{free_disk / (1024 ** 3):.2f}GB",
        "uptime": f"{uptime}",
        "disk_usage": f"{used_disk / total_disk * 100:.1f}%"
    }

    text = f"""
╭──[ 🌟 𝗦𝗧𝗔𝗧𝗨𝗦 🌟 ]──〄
│
├⏰ Dᴀᴛᴇ : {date}
├⌚ Tɪᴍᴇ : {time}
├📅 Dᴀʏ : {day}
├🧭 UTC : {utc}
│
├───[🧰 Bᴏᴛ Sᴛᴀᴛɪsᴛɪᴄs 🧰]────⍟
│
├⏰ Bᴏᴛ Uᴘᴛɪᴍᴇ : {bot_statistics['uptime']}
├🗄 Dɪꜱᴋ Sɪᴢᴇ : {bot_statistics['disk_size']}
├🗂 Dɪꜱᴋ Uꜱᴇᴅ : {bot_statistics['disk_used']}
├📂 Fʀᴇᴇ Dɪꜱᴋ : {bot_statistics['free_disk']}
├🖥️ CPU : {bot_statistics['cpu_usage']}
├🚀 Rᴀᴍ : {bot_statistics['ram_usage']}
├🗄 Dɪsᴋ : {bot_statistics['disk_usage']}
│
├───[📑 Dᴀᴛᴀ Usᴀɢᴇ 📑]───⍟
│
├📥 Tᴏᴛᴀʟ Uᴘʟᴏᴀᴅ Fɪʟᴇs : {total_files}
├📤 Tᴏᴛᴀʟ Usᴇʀs : {total_users}
│
╰────────────────────⍟
"""

    await message.reply_text(text) if isinstance(
        message, Message
    ) else await message.message.reply(text)
