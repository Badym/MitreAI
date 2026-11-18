import logging

from app.core.exceptions import ConflictError
from app.core.security import hash_password
from app.models.user import User, UserRole, normalize_email
from app.repositories.user_repository import UserRepository

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

    async def ensure_admin_exists(self, email: str | None, password: str | None) -> None:
        if await self._users.exists_with_role(UserRole.ADMIN):
            return
        if not email or not password:
            logger.warning("Brak konta administratora. Ustaw ADMIN_EMAIL i ADMIN_PASSWORD w .env")
            return

        await self.create_user(email, password, display_name="Administrator", role=UserRole.ADMIN)
        logger.info("Utworzono konto administratora %s", normalize_email(email))
