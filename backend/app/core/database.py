from beanie import init_beanie
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import Settings
from app.models import DOCUMENT_MODELS


def create_client(settings: Settings) -> AsyncMongoClient:
    return AsyncMongoClient(
        settings.mongo_url,
        tz_aware=True,
        serverSelectionTimeoutMS=settings.mongo_timeout_ms,
    )


async def init_database(database: AsyncDatabase) -> None:
    await init_beanie(database=database, document_models=DOCUMENT_MODELS)
