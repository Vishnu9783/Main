from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from database import db
import pandas as pd
import os


@Client.on_callback_query(filters.regex(pattern=r"^banned_users$"))
async def banned_users(bot: Client, message: CallbackQuery):
    banned_users = await db.users.get_all_banned_users()
    banned_users_count = len(banned_users)

    sts = await message.message.reply("Generating CSV file...")

    user_data = [
        {
            "User ID": user["_id"],
            "Banned": user["banned"],
        }
        for user in banned_users
    ]
    df = pd.DataFrame(user_data)
    df.to_csv("banned_users.csv", index=False)

    await sts.edit("Uploading CSV file...")

    await message.message.reply_document(
        document="banned_users.csv",
        caption=f"Total Banned Users : {banned_users_count}",
    )

    os.remove("banned_users.csv")
