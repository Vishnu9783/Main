from motor.motor_asyncio import AsyncIOMotorClient


class DelDB:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db["del_schedule"]

    async def add_schedule(self, chat_id, message_id, time, status=False):
        await self.col.insert_one(
            {
                "chat_id": chat_id,
                "message_id": message_id,
                "time": time,
                "status": status,
            }
        )

    async def filter_schedules(self, query):
        return await self.col.find(query).to_list(None)

    async def update_schedule(self, chat_id, message_id, status=True):
        await self.col.update_one(
            {"chat_id": chat_id, "message_id": message_id},
            {"$set": {"status": status}},
        )
