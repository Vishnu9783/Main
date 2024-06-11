from motor.motor_asyncio import AsyncIOMotorClient


class FilesDB:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db["files"]

    async def add_file(
        self,
        id,
        user_id,
        log,
    ):
        file = {
            "_id": id,
            "user_id": user_id,
            "log": log,
        }
        return await self.col.insert_one(file)

    async def get_file_by_id(self, file_id):
        return await self.col.find_one({"_id": file_id})

    async def get_user_files_count(self, user_id):
        return await self.col.count_documents({"user_id": user_id})

    async def add_batch_file(self, id, user_id, files):
        batch = {
            "_id": id,
            "user_id": user_id,
            "files": files,
        }
        return await self.col.insert_one(batch)

    async def get_batch(self, batch_id):
        return await self.col.find_one({"_id": batch_id})

    async def delete_file_by_log(self, log):
        return await self.col.delete_one({"log": log})
    
    async def delete_file_by_id(self, file_id):
        return await self.col.delete_one({"_id": file_id})

    async def get_file_by_log(self, log):
        return await self.col.find_one({"log": log})
    
    async def get_batch(self, batch_id):
        return await self.col.find_one({"_id": batch_id})

    async def filter_file(self, log):
        file =  await self.col.find_one({"log": log})
        if not file:
            file_id = log.split("-", 1)[0]
            # search in log field for file_id with any chat_id
            file = await self.col.find_one({"log": {"$regex": f"^{file_id}-"}})
        return file