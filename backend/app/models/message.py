from datetime import datetime
from enum import StrEnum
from typing import Any

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from app.models.common import utc_now


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(Document):
    conversation_id: PydanticObjectId
    role: MessageRole
    content: str
    model: str | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None
    analysis: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "messages"
        indexes = [IndexModel([("conversation_id", ASCENDING), ("created_at", ASCENDING)])]
