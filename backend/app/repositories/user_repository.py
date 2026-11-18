from beanie import PydanticObjectId
from bson import ObjectId

from app.models.user import User, UserRole


class UserRepository:
    async def get_by_id(self, user_id: str) -> User | None:
        if not ObjectId.is_valid(user_id):
            return None
        return await User.get(PydanticObjectId(user_id))

    async def get_by_email(self, email: str) -> User | None:
        return await User.find_one(User.email == email)

    async def exists_with_role(self, role: UserRole) -> bool:
        return await User.find_one(User.role == role) is not None

    async def create(self, user: User) -> User:
        return await user.insert()

    async def save(self, user: User) -> User:
        return await user.save()
