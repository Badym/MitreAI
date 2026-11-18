from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.models.user import User, UserRole
from app.repositories.health_repository import HealthRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.health_service import HealthService
from app.services.user_service import UserService

# Konfiguracja i baza

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_database(request: Request) -> AsyncDatabase:
    return request.app.state.database


DatabaseDep = Annotated[AsyncDatabase, Depends(get_database)]

# Repozytoria


def get_health_repository(database: DatabaseDep) -> HealthRepository:
    return HealthRepository(database)


def get_user_repository() -> UserRepository:
    return UserRepository()


HealthRepositoryDep = Annotated[HealthRepository, Depends(get_health_repository)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]

# Serwisy


def get_health_service(repository: HealthRepositoryDep) -> HealthService:
    return HealthService(repository)


def get_auth_service(users: UserRepositoryDep, settings: SettingsDep) -> AuthService:
    return AuthService(users, settings)


def get_user_service(users: UserRepositoryDep) -> UserService:
    return UserService(users)


HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]

# Zalogowany użytkownik

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    auth_service: AuthServiceDep,
) -> User:
    if token is None:
        raise AuthenticationError("Wymagane logowanie")
    return await auth_service.get_user_by_token(token)


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def require_admin(user: CurrentUserDep) -> User:
    if user.role != UserRole.ADMIN:
        raise PermissionDeniedError("Ta operacja wymaga roli administratora")
    return user


AdminUserDep = Annotated[User, Depends(require_admin)]
