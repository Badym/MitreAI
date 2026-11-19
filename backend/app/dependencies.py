from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.llm.mock_provider import MockProvider
from app.llm.provider import LLMProvider
from app.models.user import User, UserRole
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.health_repository import HealthRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.conversation_service import ConversationService
from app.services.health_service import HealthService
from app.services.message_service import MessageService
from app.services.model_service import ModelService
from app.services.user_service import UserService

# Konfiguracja i baza

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_database(request: Request) -> AsyncDatabase:
    return request.app.state.database


DatabaseDep = Annotated[AsyncDatabase, Depends(get_database)]

# Repozytoria i integracje


def get_health_repository(database: DatabaseDep) -> HealthRepository:
    return HealthRepository(database)


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_conversation_repository() -> ConversationRepository:
    return ConversationRepository()


def get_message_repository() -> MessageRepository:
    return MessageRepository()


def get_llm_provider() -> LLMProvider:
    return MockProvider()


HealthRepositoryDep = Annotated[HealthRepository, Depends(get_health_repository)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
ConversationRepositoryDep = Annotated[ConversationRepository, Depends(get_conversation_repository)]
MessageRepositoryDep = Annotated[MessageRepository, Depends(get_message_repository)]
LLMProviderDep = Annotated[LLMProvider, Depends(get_llm_provider)]

# Serwisy


def get_health_service(repository: HealthRepositoryDep) -> HealthService:
    return HealthService(repository)


def get_auth_service(users: UserRepositoryDep, settings: SettingsDep) -> AuthService:
    return AuthService(users, settings)


def get_user_service(users: UserRepositoryDep) -> UserService:
    return UserService(users)


def get_model_service(settings: SettingsDep) -> ModelService:
    return ModelService(settings)


ModelServiceDep = Annotated[ModelService, Depends(get_model_service)]


def get_conversation_service(
    conversations: ConversationRepositoryDep,
    messages: MessageRepositoryDep,
    models: ModelServiceDep,
) -> ConversationService:
    return ConversationService(conversations, messages, models)


ConversationServiceDep = Annotated[ConversationService, Depends(get_conversation_service)]


def get_message_service(
    conversations: ConversationServiceDep,
    messages: MessageRepositoryDep,
    models: ModelServiceDep,
    provider: LLMProviderDep,
) -> MessageService:
    return MessageService(conversations, messages, models, provider)


HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]

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
