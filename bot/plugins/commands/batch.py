import random
import string
import pyrogram
from bot.utils import check
from database import db


@pyrogram.Client.on_message(
    pyrogram.filters.command(["batch"])
    & pyrogram.filters.private
    & pyrogram.filters.incoming
)
@check
async def batch(bot: pyrogram.Client, message: pyrogram.types.Message):
    ask_text = "𝖲𝖾𝗇𝖽 𝖬𝖾 𝖳𝗁𝖾 𝖥𝗂𝗋𝗌𝗍 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝗈𝗋 𝖥𝗂𝗅𝖾 𝖫𝗂𝗇𝗄 𝖳𝗈 𝖠𝖽𝖽 𝖳𝗈 𝖳𝗁𝖾 𝖡𝖺𝗍𝖼𝗁\n\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: https://t.me/MPlayLink/245\n\n"

    ask = await message.chat.ask(ask_text, filters=pyrogram.filters.text)

    if not ask.text.startswith("https"):
        return await ask.reply_text(
            "𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖨𝖣 𝗈𝗋 𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾",
            reply_markup=pyrogram.types.ReplyKeyboardRemove(),
        )

    channel_id, message_id = ask.text.split("/")[-2:]
    message_id = int(message_id)

    if channel_id.isdigit():
        channel_id = int(f"-100{channel_id}")
    else:
        channel_id = channel_id.replace("@", "")

    try:
        first_message = await bot.get_messages(channel_id, message_id)
    except Exception:
        return await ask.reply_text(
            "𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖨𝖣 𝗈𝗋 𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾",
            reply_markup=pyrogram.types.ReplyKeyboardRemove(),
        )

    ask = await message.chat.ask(
        "𝖲𝖾𝗇𝖽 𝖬𝖾 𝖳𝗁𝖾 𝖫𝖺𝗌𝗍 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝗈𝗋 𝖥𝗂𝗅𝖾 𝖫𝗂𝗇𝗄", filters=pyrogram.filters.text
    )

    channel_id, message_id = ask.text.split("/")[-2:]
    message_id = int(message_id)
    if channel_id.isdigit():
        channel_id = int(f"-100{channel_id}")
    else:
        channel_id = channel_id.replace("@", "")

    try:
        last_message = await bot.get_messages(channel_id, message_id)
    except Exception:
        return await ask.reply_text(
            "𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖨𝖣 𝗈𝗋 𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾",
            reply_markup=pyrogram.types.ReplyKeyboardRemove(),
        )

    if first_message.chat.id != last_message.chat.id:
        return await ask.reply_text(
            "𝖳𝗁𝖾 𝖥𝗂𝗋𝗌𝗍 𝖠𝗇𝖽 𝖫𝖺𝗌𝗍 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖲𝗁𝗈𝗎𝗅𝖽 𝖡𝖾 𝖥𝗋𝗈𝗆 𝖳𝗁𝖾 𝖲𝖺𝗆𝖾 𝖢𝗁𝖺𝗇𝗇𝖾𝗅",
            reply_markup=pyrogram.types.ReplyKeyboardRemove(),
        )

    if first_message.id > last_message.id:
        return await ask.reply_text(
            "𝖳𝗁𝖾 𝖫𝖺𝗌𝗍 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖲𝗁𝗈𝗎𝗅𝖽 𝖡𝖾 𝖠𝖿𝗍𝖾𝗋 𝖳𝗁𝖾 𝖥𝗂𝗋𝗌𝗍 𝖬𝖾𝗌𝗌𝖺𝗀𝖾",
            reply_markup=pyrogram.types.ReplyKeyboardRemove(),
        )

    files = [
        file
        for file in await bot.get_messages(
            first_message.chat.id, range(first_message.id, last_message.id + 1)
        )
        if file.media
    ]
    if not files:
        return await ask.reply_text(
            "𝖭𝗈 𝖥𝗂𝗅𝖾𝗌 𝖶𝖾𝗋𝖾 𝖠𝖽𝖽𝖾𝖽 𝖳𝗈 𝖳𝗁𝖾 𝖡𝖺𝗍𝖼𝗁",
            reply_markup=pyrogram.types.ReplyKeyboardRemove(),
        )

    if len(files) > 20:
        return await ask.reply_text(
            "𝖸𝗈𝗎 𝖢𝖺𝗇 𝖮𝗇𝗅𝗒 𝖠𝖽𝖽 𝖠 𝖬𝖺𝗑𝗂𝗆𝗎𝗆 𝖮𝖿 20 𝖥𝗂𝗅𝖾𝗌 𝖳𝗈 𝖠 𝖡𝖺𝗍𝖼𝗁",
            reply_markup=pyrogram.types.ReplyKeyboardRemove(),
        )

    temp = await ask.reply_text(
        "𝐶𝑟𝑒𝑎𝑡𝑖𝑛𝑔 𝐵𝑎𝑡𝑐ℎ...", reply_markup=pyrogram.types.ReplyKeyboardRemove()
    )

    batch_files = []
    for file in files:
        file: pyrogram.types.Message
        log = file
        data = {
            "message_id": log.id,
            "chat_id": log.chat.id,
        }
        batch_files.append(data)

    _id = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    await db.files.add_batch_file(
        _id,
        message.from_user.id,
        batch_files,
    )
    url = f"https://t.me/{bot.me.username}"
    file_link = f"{url}?start=batch_{_id}"

    await ask.reply_text(
        f"𝐘𝐨𝐮𝐫 𝐁𝐚𝐭𝐜𝐡 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐂𝐫𝐞𝐚𝐭𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲. 𝐘𝐨𝐮 𝐂𝐚𝐧 𝐀𝐜𝐜𝐞𝐬𝐬 𝐈𝐓 𝐅𝐫𝐨𝐦 \n\n`{file_link}`",
        disable_web_page_preview=True,
        reply_markup=pyrogram.types.InlineKeyboardMarkup(
            [
                [pyrogram.types.InlineKeyboardButton("Oᴘᴇɴ Bᴀᴛᴄʜ", url=file_link)],
                [
                    pyrogram.types.InlineKeyboardButton(
                        "Sʜᴀʀᴇ Bᴀᴛᴄʜ", url=f"https://t.me/share/url?url={file_link}"
                    )
                ],
            ]
        ),
    )
    await temp.delete()
