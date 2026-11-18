from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from app.models.common import utc_now


class DocumentFile(Document):
    message_id: PydanticObjectId
    filename: str
    content_type: str
    size_bytes: int
    gridfs_id: PydanticObjectId
    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "documents"
        indexes = [IndexModel([("message_id", ASCENDING)])]
