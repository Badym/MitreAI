from datetime import datetime
from enum import StrEnum

from beanie import Document
from pydantic import EmailStr, Field
from pymongo import ASCENDING, IndexModel

from app.models.common import utc_now


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


class User(Document):
    email: EmailStr
    password_hash: str
    display_name: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = Field(default_factory=utc_now)
    last_login_at: datetime | None = None

    class Settings:
        name = "users"
        indexes = [IndexModel([("email", ASCENDING)], unique=True)]
