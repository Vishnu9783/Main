from contextlib import suppress
from pyrogram import Client, filters, types, enums
from database import db


@Client.on_callback_query(filters.regex(pattern=r"^force_sub_add_channel"))
async def force_sub_add_channel(bot: Client, message: types.CallbackQuery):
    try:
        channel_id = await message.message.chat.ask(
            "Send the channel username or ID to add to force sub config.",
            filters=filters.text,
        )
        channel_id = channel_id.text
    except Exception as e:
        return await send_error_message(message, str(e))

    await add_channel_to_force_sub(bot, message, channel_id)


@Client.on_callback_query(filters.regex(pattern=r"^force_sub_config"))
async def force_sub_config(bot: Client, message: types.CallbackQuery):
    force_sub = (await db.config.get_config("force_sub_config")) or {}
    force_sub = force_sub.get("value", {})

    text = "Force Sub Configs:\n\n"
    buttons = []
    for i, sub in enumerate(force_sub.values(), start=1):
        channel_id = sub["channel_id"]
        buttons.append(
            [
                types.InlineKeyboardButton(
                    text=i,
                    callback_data="ignore",
                ),
                types.InlineKeyboardButton(
                    text=sub["method"].capitalize(),
                    callback_data=f"force_sub_method_{channel_id}",
                ),
                types.InlineKeyboardButton(
                    text="✅" if sub["status"] else "❌",
                    callback_data=f"force_sub_toggle_{channel_id}",
                ),
                types.InlineKeyboardButton(
                    text="🗑️",
                    callback_data=f"force_sub_delete_{channel_id}",
                ),
            ]
        )
        text += f"{i}. {sub['title']} - {'Enabled' if sub['status'] else 'Disabled'} - {sub['method'].capitalize()}\n"

    buttons.append(
        [
            types.InlineKeyboardButton(
                text="Add Channel", callback_data="force_sub_add_channel"
            )
        ]
    )
    buttons.append(
        [types.InlineKeyboardButton(text="Back to Main Menu", callback_data="start")]
    )

    await message.edit_message_text(
        text=text,
        reply_markup=types.InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
    )


# delete force sub channel
@Client.on_callback_query(filters.regex(pattern=r"^force_sub_delete_confirm_"))
async def force_sub_delete_confirm(bot: Client, message: types.CallbackQuery):
    channel_id = int(message.data.split("_")[-1])

    force_sub = (await db.config.get_config("force_sub_config")) or {}
    force_sub = force_sub.get("value", {})

    del force_sub[str(channel_id)]
    await db.config.update_config("force_sub_config", force_sub)
    return await message.edit_message_text(
        text="Channel deleted from force sub config.",
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        text="Back to Force Sub Config",
                        callback_data="force_sub_config",
                    )
                ]
            ]
        ),
    )


# delete force sub channel with confirmation
@Client.on_callback_query(filters.regex(pattern=r"^force_sub_delete_"))
async def force_sub_delete(bot: Client, message: types.CallbackQuery):
    channel_id = int(message.data.split("_")[-1])
    return await message.edit_message_text(
        text="Are you sure you want to delete this channel from force sub?",
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        text="Yes",
                        callback_data=f"force_sub_delete_confirm_{channel_id}",
                    ),
                    types.InlineKeyboardButton(
                        text="No",
                        callback_data="force_sub_config",
                    ),
                ]
            ]
        ),
    )


# toggle force sub status
@Client.on_callback_query(filters.regex(pattern=r"^force_sub_toggle_"))
async def force_sub_toggle(bot: Client, message: types.CallbackQuery):
    channel_id = int(message.data.split("_")[-1])
    force_sub = (await db.config.get_config("force_sub_config")) or {}
    force_sub = force_sub.get("value", {})

    force_sub[str(channel_id)]["status"] = not force_sub[str(channel_id)]["status"]
    await db.config.update_config("force_sub_config", force_sub)

    await force_sub_config(bot, message)


@Client.on_callback_query(filters.regex(pattern=r"^force_sub_method_"))
async def force_sub_method(bot: Client, message: types.CallbackQuery):
    channel_id = int(message.data.split("_")[-1])
    force_sub = (await db.config.get_config("force_sub_config")) or {}
    force_sub = force_sub.get("value", {})

    sub = force_sub[str(channel_id)]
    if sub["method"] == "direct":
        sub["method"] = "request"
    else:
        sub["method"] = "direct"

    force_sub[str(channel_id)] = sub
    await db.config.update_config("force_sub_config", force_sub)
    await force_sub_config(bot, message)


# Utils
def back_to_force_sub_markup():
    return types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton(
                    text="Back to Force Sub Config",
                    callback_data="force_sub_config",
                )
            ]
        ]
    )


async def send_error_message(message: types.CallbackQuery, error_text: str):
    return await message.message.reply(
        text=f"Error: {error_text}",
        reply_markup=back_to_force_sub_markup(),
    )


async def add_channel_to_force_sub(
    bot: Client, message: types.CallbackQuery, channel_id: str
):
    if channel_id.replace("@", "").replace("-", "").isdigit():
        channel_id = int(channel_id)
    else:
        channel_id = channel_id.replace("@", "")

    try:
        channel = await bot.get_chat(channel_id)
        channel_id = channel.id
    except Exception as e:
        return await send_error_message(message, str(e))

    if channel.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP]:
        return await send_error_message(message, "The provided chat is not a channel.")

    force_sub_config_data = await db.config.get_config("force_sub_config")
    force_sub_config = (
        force_sub_config_data.get("value", {}) if force_sub_config_data else {}
    )

    if force_sub_config.get("channel_id") == channel_id:
        return await message.edit_message_text(
            text="Channel already exists in force sub config.",
            reply_markup=back_to_force_sub_markup(),
        )

    force_sub_config[str(channel_id)] = {
        "channel_id": channel_id,
        "title": channel.title,
        "status": True,
        "method": "direct",
    }

    await db.config.update_config("force_sub_config", force_sub_config)

    return await message.message.reply(
        text="Channel added to force sub config.",
        reply_markup=back_to_force_sub_markup(),
    )
