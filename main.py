from bot import Bot
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.utils import process_delete_schedule

if __name__ == "__main__":
    os.makedirs("downloads", exist_ok=True)
    sc = AsyncIOScheduler()
    sc.start()
    app = Bot()
    app.sc = sc
    sc.add_job(process_delete_schedule, "interval", seconds=10, args=(app,))
    app.run()
