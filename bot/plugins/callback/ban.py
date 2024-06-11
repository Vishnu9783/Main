from contextlib import suppress
from pyrogram import Client, filters, types
from database import db


@Client.on_callback_query(filters.regex(pattern=r"^(ban_user|unban_user)_\d+"))
async def ban_user(bot: Client, message: types.CallbackQuery):
    user_id = int(message.data.split("_")[-1])

    if message.data.startswith("ban_user"):
        await db.users.update_user(user_id, {"banned": True})
        await message.answer("User Banned Successfully", show_alert=True)
        with suppress(Exception):
            await bot.send_message(
                user_id,
                f"𝖸𝗈𝗎 𝖧𝖺𝗏𝖾 𝖡𝖾𝖾𝗇 𝖡𝖺𝗇𝗇𝖾𝖽 𝖥𝗋𝗈𝗆 𝖴𝗌𝗂𝗇𝗀 𝖬𝖾. 𝖢𝗈𝗇𝗍𝖺𝖼𝗍 𝖬𝗒 [𝐎𝐰𝐧𝐞𝐫](tg://user?id={bot.owner.id}) 𝖥𝗈𝗋 𝖬𝗈𝗋𝖾 𝖣𝖾𝗍𝖺𝗂𝗅𝗌.",
            )
    else:
        await db.users.update_user(user_id, {"banned": False})
        await message.answer("User Unbanned Successfully", show_alert=True)
        with suppress(Exception):
            await bot.send_message(
                user_id,
                "You Have Been Unbanned. Now You Can Use Me.",
            )
