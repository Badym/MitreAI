from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel

from app.models.common import utc_now


class Conversation(Document):
    user_id: PydanticObjectId
    title: str = ""
    model: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    is_archived: bool = False

    class Settings:
        name = "conversations"
        indexes = [IndexModel([("user_id", ASCENDING), ("updated_at", DESCENDING)])]
