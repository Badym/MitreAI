from datetime import timedelta

from app.core.config import Settings
from app.core.exceptions import AuthenticationError
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    read_token_subject,
    verify_password,
)
from app.models.common import utc_now
from app.models.user import User, normalize_email
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, users: UserRepository, settings: Settings) -> None:
        self._users = users
        self._secret = settings.jwt_secret.get_secret_value()
        self._token_lifetime = timedelta(minutes=settings.jwt_expire_minutes)

    async def login(self, email: str, password: str) -> str:
        user = await self._users.get_by_email(normalize_email(email))
        password_hash = user.password_hash if user else DUMMY_PASSWORD_HASH
        password_matches = verify_password(password, password_hash)

        if user is None or not password_matches:
            raise AuthenticationError("Nieprawidłowy e-mail lub hasło")
        if not user.is_active:
            raise AuthenticationError("Konto jest nieaktywne")

        user.last_login_at = utc_now()
        await self._users.save(user)
        return create_access_token(str(user.id), self._secret, self._token_lifetime)

    async def get_user_by_token(self, token: str) -> User:
        user_id = read_token_subject(token, self._secret)
        user = await self._users.get_by_id(user_id) if user_id else None

        if user is None or not user.is_active:
            raise AuthenticationError("Sesja wygasła lub jest nieprawidłowa")
        return user
