from datetime import datetime
from typing import Annotated, Any

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, StringConstraints

from app.models.message import MessageRole
from app.schemas.conversation import ConversationResponse

Prompt = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20000)]


class MessageCreateForm(BaseModel):
    content: Prompt
    model: str | None = None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PydanticObjectId
    conversation_id: PydanticObjectId
    role: MessageRole
    content: str
    model: str | None
    tokens_in: int | None
    tokens_out: int | None
    analysis: dict[str, Any] | None
    created_at: datetime


class SendMessageResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
    conversation: ConversationResponse
