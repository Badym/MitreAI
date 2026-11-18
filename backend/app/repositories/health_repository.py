from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import PyMongoError


class HealthRepository:
    def __init__(self, database: AsyncDatabase) -> None:
        self._database = database

    async def ping(self) -> bool:
        try:
            await self._database.command("ping")
        except PyMongoError:
            return False
        return True
