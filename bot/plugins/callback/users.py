from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from database import db
import pandas as pd
import os


@Client.on_callback_query(filters.regex(pattern=r"^total_users$"))
async def total_users(bot: Client, message: CallbackQuery):
    total_users = await db.users.get_all_users()
    total_users_count = len(total_users)

    sts = await message.message.reply("Generating CSV file...")

    user_data = [
        {
            "User ID": user["_id"],
            "Banned": user["banned"],
        }
        for user in total_users
    ]
    df = pd.DataFrame(user_data)
    df.to_csv("users.csv", index=False)

    await sts.edit("Uploading CSV file...")

    await message.message.reply_document(
        document="users.csv",
        caption=f"Total Users : {total_users_count}",
    )

    os.remove("users.csv")
