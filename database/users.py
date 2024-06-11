from motor.motor_asyncio import AsyncIOMotorClient


class UsersDB:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db["users"]

    async def add_user(self, user_id):
        user = {"_id": user_id, "banned": False, "files_received": 0}
        await self.col.insert_one(user)

    async def get_user(self, user_id):
        return await self.col.find_one({"_id": user_id})

    async def get_all_users(self):
        return await self.col.find({}).to_list(None)

    async def update_user(self, user_id, data, tag="set"):
        return await self.col.update_one({"_id": user_id}, {f"${tag}": data})

    async def ban_user(self, user_id):
        return await self.col.update_one({"_id": user_id}, {"$set": {"banned": True}})

    async def unban_user(self, user_id):
        return await self.col.update_one({"_id": user_id}, {"$set": {"banned": False}})

    async def is_user_banned(self, user_id):
        user = await self.get_user(user_id)
        return False if user is None else user["banned"]

    async def get_all_banned_users(self):
        return await self.col.find({"banned": True}).to_list(None)

    async def delete_user(self, user_id):
        return await self.col.delete_one({"_id": user_id})
