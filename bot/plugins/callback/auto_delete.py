from contextlib import suppress
from pyrogram import Client, filters, types
from database import db
from bot.utils import human_readable_time

@Client.on_callback_query(filters.regex(pattern=r"^auto_delete_config"))
async def auto_delete_config(bot: Client, message: types.CallbackQuery):
    message_delete_time = (await db.config.get_config("message_delete_time")) or {}
    file_delete_time = (await db.config.get_config("file_delete_time")) or {}

    text = "Auto Delete Configurations\n\n"

    text += (
        f"Message Delete Time : {human_readable_time(message_delete_time.get('value', 0))}\n"
    )
    text += f"File Delete Time : {human_readable_time(file_delete_time.get('value', 0))}\n"

    buttons = []

    buttons.append(
        [
            types.InlineKeyboardButton(
                "Set Message Delete Time",
                callback_data="set_message_delete_time",
            ),
        ]
    )

    buttons.append(
        [
            types.InlineKeyboardButton(
                "Set File Delete Time", callback_data="set_file_delete_time"
            ),
        ]
    )

    buttons.append(
        [
            types.InlineKeyboardButton("Back", callback_data="start"),
        ]
    )

    await message.message.edit_text(
        text, reply_markup=types.InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex(pattern=r"^set_message_delete_time"))
async def set_message_delete_time(bot: Client, message: types.CallbackQuery):

    try:
        ask_message = await message.message.chat.ask(
            "Enter Message Delete Time In Seconds"
        )
        time = ask_message.text
    except Exception as e:
        await message.message.reply_text(str(e))
        return

    try:
        time = int(time)
    except ValueError:
        await message.message.reply_text("Invalid Time")
        return

    await db.config.update_config("message_delete_time", time)
    buttons = [
        [
            types.InlineKeyboardButton("Back", callback_data="auto_delete_config"),
        ]
    ]
    await message.message.reply_text(
        "Message Delete Time Updated", reply_markup=types.InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex(pattern=r"^set_file_delete_time"))
async def set_file_delete_time(bot: Client, message: types.CallbackQuery):

    try:
        ask_message = await message.message.chat.ask(
            "Enter File Delete Time In Seconds"
        )
        time = ask_message.text
    except Exception as e:
        await message.message.reply_text(str(e))
        return

    try:
        time = int(time)
    except ValueError:
        await message.message.reply_text("Invalid Time")
        return

    await db.config.update_config("file_delete_time", time)
    buttons = [
        [
            types.InlineKeyboardButton("Back", callback_data="auto_delete_config"),
        ]
    ]
    await message.message.reply_text(
        "File Delete Time Updated", reply_markup=types.InlineKeyboardMarkup(buttons)
    )
