from .files import FilesDB
from .users import UsersDB
from bot.config import Config
from .config import ConfigDB
from .del_schedule import DelDB

__all__ = ["FilesDB", "UsersDB"]


class Database:
    def __init__(self, uri, database_name):
        self.users = UsersDB(uri, database_name)
        self.files = FilesDB(uri, database_name)
        self.config = ConfigDB(uri, database_name)
        self.del_schedule = DelDB(uri, database_name)


db = Database(Config.DATABASE_URL, Config.DATABASE_NAME)
