from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Buttons
from database import db


@Client.on_message(filters.command("user") & filters.private & filters.incoming)
async def user(bot: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text(
            "Usage: /user [user_id]",
            reply_markup=InlineKeyboardMarkup(Buttons.BACK_BUTTON),
            disable_web_page_preview=True,
        )

    user_id = message.text.split(None, 1)[1]

    if not user_id.isdigit():
        await message.reply_text(
            "Usage: /user [user_id]",
            reply_markup=InlineKeyboardMarkup(Buttons.BACK_BUTTON),
            disable_web_page_preview=True,
        )

    user = await db.users.get_user(int(user_id))

    if not user:
        await message.reply_text(
            "User Not Found!",
            reply_markup=InlineKeyboardMarkup(Buttons.BACK_BUTTON),
            disable_web_page_preview=True,
        )

    total_files = user["files_received"]

    text = f"""
**User Details**

User ID: `{user['_id']}`

Total Files Received: `{total_files}`

Banned: `{user['banned']}`
"""

    markup = []

    if user["banned"]:
        markup.append(
            [
                InlineKeyboardButton(
                    "Unban User", callback_data=f"unban_user_{user['_id']}"
                )
            ]
        )
    else:
        markup.append(
            [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{user['_id']}")]
        )

    markup.extend(
        (
            [
                InlineKeyboardButton(
                    "Delete User", callback_data=f"delete_user_{user['_id']}"
                )
            ],
            [InlineKeyboardButton("Back", callback_data="admin")],
        )
    )
    await message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(markup),
        disable_web_page_preview=True,
    )
