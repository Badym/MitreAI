import logging

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.models.user import User, UserRole, normalize_email
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdateRequest

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def create_user(
        self,
        email: str,
        password: str,
        display_name: str,
        role: UserRole = UserRole.USER,
    ) -> User:
        email = normalize_email(email)
        if await self._users.get_by_email(email) is not None:
            raise ConflictError("Użytkownik o tym adresie e-mail już istnieje")

        user = User(
            email=email,
            password_hash=hash_password(password),
            display_name=display_name,
            role=role,
        )
        return await self._users.create(user)

    async def list_users(self) -> list[User]:
        return await self._users.list_all()

    async def get_user(self, user_id: str) -> User:
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("Nie znaleziono użytkownika")
        return user

    async def update_user(
        self, user_id: str, changes: UserUpdateRequest, acting_admin: User
    ) -> User:
        user = await self.get_user(user_id)
        if user.id == acting_admin.id:
            self._protect_own_admin_access(changes)

        if changes.display_name is not None:
            user.display_name = changes.display_name
        if changes.role is not None:
            user.role = changes.role
        if changes.is_active is not None:
            user.is_active = changes.is_active
        if changes.password is not None:
            user.password_hash = hash_password(changes.password)

        return await self._users.save(user)

    async def ensure_admin_exists(self, email: str | None, password: str | None) -> None:
        if await self._users.exists_with_role(UserRole.ADMIN):
            return
        if not email or not password:
            logger.warning("Brak konta administratora. Ustaw ADMIN_EMAIL i ADMIN_PASSWORD w .env")
            return

        await self.create_user(email, password, display_name="Administrator", role=UserRole.ADMIN)
        logger.info("Utworzono konto administratora %s", normalize_email(email))

    @staticmethod
    def _protect_own_admin_access(changes: UserUpdateRequest) -> None:
        loses_admin_role = changes.role is not None and changes.role != UserRole.ADMIN
        if changes.is_active is False or loses_admin_role:
            raise ConflictError(
                "Nie możesz zablokować własnego konta ani odebrać sobie roli administratora"
            )
