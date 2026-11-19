from datetime import datetime
from typing import Annotated

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints

from app.models.user import UserRole

Password = Annotated[str, StringConstraints(min_length=8, max_length=128)]
DisplayName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: Password
    display_name: DisplayName
    role: UserRole = UserRole.USER


class UserUpdateRequest(BaseModel):
    display_name: DisplayName | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    password: Password | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PydanticObjectId
    email: str
    display_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None
