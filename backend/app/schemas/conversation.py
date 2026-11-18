from datetime import datetime
from typing import Annotated

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, StringConstraints

Title = Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)]
NonEmptyTitle = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]


class ConversationCreateRequest(BaseModel):
    title: Title = ""
    model: str | None = None


class ConversationUpdateRequest(BaseModel):
    title: NonEmptyTitle | None = None
    model: str | None = None
    is_archived: bool | None = None


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PydanticObjectId
    title: str
    model: str
    created_at: datetime
    updated_at: datetime
    is_archived: bool
