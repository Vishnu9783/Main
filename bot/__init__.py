import logging
import logging.config
from pyrogram import Client
from bot.config import Config
from bot.utils import add_admin, ensure_config, start_webserver, set_commands
import pyromod
# Get logging configurations

logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)


class Bot(Client):
    def __init__(self):
        super().__init__(
            "bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="bot/plugins"),
        )

    async def start(self):
        await super().start()

        me = await self.get_me()
        self.owner = await self.get_users(int(Config.OWNER_ID))
        self.username = f"@{me.username}"
        await set_commands(self)
        await ensure_config()
        await add_admin(self.owner.id)
        logging.info(f"Bot started as {me.first_name} [{me.id}] - @{me.username}")
        logging.info(f"Owner: {self.owner.mention}")

        if Config.WEB_SERVER:
            await start_webserver()

    async def stop(self, *args):
        await super().stop()
