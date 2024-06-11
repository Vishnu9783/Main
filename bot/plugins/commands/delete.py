from pyrogram import Client, filters
from pyrogram.types import Message
from database import db
from bot.utils import check


@Client.on_message(
    filters.command(["delete", "d"]) & filters.private & filters.incoming
)
@check
async def delete_file_command(bot: Client, message: Message):
    deleted_from_db = False
    try:
        ask = await message.chat.ask(
            "Send me the file stored link to delete\n\n/cancel to cancel",
        )
    except Exception as e:
        print(e)
        return

    if ask.text == "/cancel":
        await ask.reply_text("Action Cancelled")
        return

    if not ask.text:
        await ask.reply_text("No input found")
        return

    urls = ask.text.split()
    deleted_links = []

    "https://t.me/test264bot?start=batch_lmvmxlkypk"
    for url in urls:
        deleted_from_db = False
        try:
            _id = url.split("_")[-1]
        except IndexError:
            continue

        file = await db.files.get_file_by_id(_id)

        if not file:
            await ask.reply_text(
                f"{url} not found in database", disable_web_page_preview=True
            )
            continue

        await db.files.delete_file_by_id(file["_id"])
        deleted_from_db = True

        res = {
            "user_id": file["user_id"],
            "url": url,
            "deleted_from_db": deleted_from_db,
        }
        deleted_links.append(res)

    text = ""
    for link in deleted_links:
        text += f"URL: {link['url']} - [user](tg://user?id={link['user_id']})\n"
        text += f"Deleted: {link['deleted_from_db']}\n\n"

    if len(text) > 4096:
        await ask.reply_document(
            text.encode("utf-8"),
            caption="Deleted Links",
            disable_notification=True,
        )
    else:
        await ask.reply_text(text, disable_web_page_preview=True)
