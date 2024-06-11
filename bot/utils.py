import asyncio
import datetime
import logging
import math
from aiohttp import web
from bot.config import Script
from database import db
from pyrogram import types, Client, errors
import functools
from collections import OrderedDict


async def start_webserver():
    routes = web.RouteTableDef()

    @routes.get("/", allow_head=True)
    async def root_route_handler(request):
        res = {
            "status": "running",
        }
        return web.json_response(res)

    async def web_server():
        web_app = web.Application(client_max_size=30000000)
        web_app.add_routes(routes)
        return web_app

    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, "0.0.0.0", 8000).start()
    logging.info("Web server started")


async def add_new_user(user_id):
    if not await db.users.col.find_one({"_id": user_id}):
        await db.users.add_user(user_id)
        return True


async def set_commands(app: Client):
    commands = [
        types.BotCommand("start", "Start bot"),
        types.BotCommand("batch", "Batch upload files"),
        types.BotCommand("addadmin", "Add an admin"),
        types.BotCommand("removeadmin", "Remove an admin"),
        types.BotCommand("admins", "Get a list of admins"),
        types.BotCommand("broadcast", "Broadcast a message"),
        types.BotCommand("delete", "Delete a file"),
        types.BotCommand("genlink", "Generate a link"),
        types.BotCommand("stats", "Get bot stats"),
        types.BotCommand("user", "Get user details"),
        types.BotCommand("help", "Help message"),
        types.BotCommand("admin", "Admin commands"),
    ]
    await app.set_bot_commands(commands)


async def handle_floodwait(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except errors.FloodWait as e:
        await asyncio.sleep(e.value)
        return await func(*args, **kwargs)


def get_caption(**kwargs):
    caption = Script.DEFAULT_CAPTION
    text = caption.format(**kwargs)
    return text


def get_func(ins):
    if isinstance(ins, types.Message):
        return ins.reply_text
    else:
        return ins.edit_message_text


def get_channel_id(message, n=1, s=" "):
    if isinstance(message, types.Message):
        channel_id = None
    elif len(message.data.split(s)) > n:
        channel_id = message.data.split(s)[n]
        if channel_id == "None":
            channel_id = None
        else:
            channel_id = int(channel_id)
    else:
        channel_id = None
    return channel_id


def human_size(bytes):
    if bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(bytes, 1024)))
    p = math.pow(1024, i)
    s = round(bytes / p, 2)
    return f"{s} {size_name[i]}"


def get_file_details(message):
    media = getattr(message, message.media.value)
    filename = media.file_name if getattr(media, "file_name", None) else "Not Available"
    file_size = media.file_size
    file_unique_id = media.file_unique_id
    file_type = (
        media.mime_type if getattr(media, "mime_type", None) else "Not Available"
    )
    file_caption = message.caption.html if message.caption else ""
    file_extension = filename.split(".")[-1]
    duration = None
    if file_type.startswith("video") and getattr(media, "duration", None):
        duration = media.duration
        duration = datetime.timedelta(seconds=duration)
    return (
        filename,
        file_size,
        file_unique_id,
        file_type,
        file_caption,
        file_extension,
        duration,
    )


async def handle_reply(message, text, **kwargs):
    kwargs.pop("caption", None)
    kwargs.pop("text", None)
    if isinstance(message, types.Message):
        await message.reply_text(text=text, **kwargs)

    elif isinstance(message, types.CallbackQuery):
        message: types.CallbackQuery
        kwargs.pop("quote", None)
        if message.message.photo:
            await message.message.delete()
            await message.message.reply(text=text, **kwargs)
        else:
            await message.edit_message_text(text=text, **kwargs)


async def get_admins():
    config = await db.config.get_config("ADMINS")
    return config["value"] if config else []


async def add_admin(user_id):
    config = await db.config.get_config("ADMINS")
    if config:
        admins = config["value"]
        if user_id not in admins:
            admins.append(user_id)
            await db.config.update_config("ADMINS", admins)
            return True
    else:
        await db.config.add_config("ADMINS", [user_id])
        return True

    return False


async def remove_admin(user_id):
    config = await db.config.get_config("ADMINS")
    if config:
        admins = config["value"]
        if user_id in admins:
            admins.remove(user_id)
            await db.config.update_config("ADMINS", admins)
            return True
    return False


async def ensure_config_entry(key, default_value):
    if not await db.config.get_config(key):
        await db.config.add_config(key, default_value)


async def ensure_config():
    await ensure_config_entry("ADMINS", [])
    await ensure_config_entry("message_delete_time", 0)
    await ensure_config_entry("file_delete_time", 0)
    await ensure_config_entry("force_sub_config", {})
    await ensure_config_entry("request_joins", {})


async def add_request_join(chat_id, user_id):
    request_joins = await db.config.get_config("request_joins")
    request_joins = request_joins.get("value", {})
    if str(chat_id) not in request_joins:
        request_joins[str(chat_id)] = []
    if user_id not in request_joins[str(chat_id)]:
        request_joins[str(chat_id)].append(user_id)
        await db.config.update_config("request_joins", request_joins)
        return True
    return False


async def is_user_in_request_join(chat_id, user_id):
    request_joins = await db.config.get_config("request_joins")
    request_joins = request_joins.get("value", {})
    if str(chat_id) in request_joins:
        if user_id in request_joins[str(chat_id)]:
            return True
    return False


async def process_delete_schedule(bot):
    schedules = await db.del_schedule.filter_schedules({"status": False})
    for schedule in schedules:
        sc = bot.sc
        sc.add_job(
            process_delete_schedule_single,
            args=(bot, schedule),
            trigger="date",
            run_date=datetime.datetime.now() + datetime.timedelta(seconds=5),
        )


async def process_delete_schedule_single(bot, schedule):
    chat_id = schedule["chat_id"]
    message_id = schedule["message_id"]
    time = schedule["time"]
    if time < datetime.datetime.now():
        try:
            await bot.delete_messages(chat_id, message_id)
        except errors.MessageDeleteForbidden:
            pass
        await db.del_schedule.update_schedule(chat_id, message_id, True)


def check(func):
    """Check if user is admin or not"""

    @functools.wraps(func)
    async def wrapper(client: Client, message):
        chat_id = getattr(message.from_user, "id", None)
        admins = await get_admins()

        if chat_id not in admins:
            return

        banned_users = await db.users.get_all_banned_users()
        banned_users_ids = [user["_id"] for user in banned_users]
        if chat_id in banned_users_ids:
            return

        return await func(client, message)

    return wrapper


INTERVALS = OrderedDict(
    [
        ("millennium", 31536000000),  # 60 * 60 * 24 * 365 * 1000
        ("century", 3153600000),  # 60 * 60 * 24 * 365 * 100
        ("year", 31536000),  # 60 * 60 * 24 * 365
        ("month", 2592000),  # 60 * 60 * 24 * 28 (assuming 28 days in a month)
        ("week", 604800),  # 60 * 60 * 24 * 7
        ("day", 86400),  # 60 * 60 * 24
        ("hr", 3600),  # 60 * 60
        ("min", 60),
        ("sec", 1),
    ]
)


def human_readable_time(seconds, decimals=0):
    """Human-readable time from seconds (ie. 5 days and 2 hours).

    Examples:
        >>> human_time(15)
        '15 seconds'
        >>> human_time(3600)
        '1 hour'
        >>> human_time(3720)
        '1 hour and 2 minutes'
        >>> human_time(266400)
        '3 days and 2 hours'
        >>> human_time(-1.5)
        '-1.5 seconds'
        >>> human_time(0)
        '0 seconds'
        >>> human_time(0.1)
        '100 milliseconds'
        >>> human_time(1)
        '1 second'
        >>> human_time(1.234, 2)
        '1.23 seconds'

    Args:
        seconds (int or float): Duration in seconds.
        decimals (int): Number of decimals.

    Returns:
        str: Human-readable time.
    """
    if (
        seconds < 0
        or seconds != 0
        and not 0 < seconds < 1
        and 1 < seconds < INTERVALS["min"]
    ):
        input_is_int = isinstance(seconds, int)
        return f"{str(seconds if input_is_int else round(seconds, decimals))} sec"
    elif seconds == 0:
        return "0 s"
    elif 0 < seconds < 1:
        # Return in milliseconds.
        ms = int(seconds * 1000)
        return "%i ms%s" % (ms, "s" if ms != 1 else "")
    res = []
    for interval, count in INTERVALS.items():
        quotient, remainder = divmod(seconds, count)
        if quotient >= 1:
            seconds = remainder
            if quotient > 1:
                # Plurals.
                if interval == "millennium":
                    interval = "millennia"
                elif interval == "century":
                    interval = "centuries"
                else:
                    interval += "s"
            res.append("%i %s" % (int(quotient), interval))
        if remainder == 0:
            break

    return f"{res[0]} {res[1]}" if len(res) >= 2 else res[0]
