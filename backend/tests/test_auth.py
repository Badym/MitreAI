import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.core.config import get_settings
from app.core.exceptions import ConflictError
from app.main import create_initial_admin
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from tests.helpers import ADMIN_EMAIL, ADMIN_PASSWORD, bearer, login


async def test_admin_created_on_startup_can_log_in(client: AsyncClient) -> None:
    response = await login(client, ADMIN_EMAIL, ADMIN_PASSWORD)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


async def test_admin_is_not_duplicated_on_restart(app: FastAPI) -> None:
    await create_initial_admin(get_settings())

    assert await User.find(User.role == UserRole.ADMIN).count() == 1


async def test_login_ignores_email_letter_case(client: AsyncClient) -> None:
    response = await login(client, "ADMIN@Example.com", ADMIN_PASSWORD)

    assert response.status_code == 200


async def test_login_with_wrong_password_returns_401(client: AsyncClient) -> None:
    response = await login(client, ADMIN_EMAIL, "zle-haslo")

    assert response.status_code == 401
    assert response.json() == {"detail": "Nieprawidłowy e-mail lub hasło"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


async def test_login_with_unknown_email_returns_same_error(client: AsyncClient) -> None:
    unknown = await login(client, "nikt@example.com", ADMIN_PASSWORD)
    wrong_password = await login(client, ADMIN_EMAIL, "zle-haslo")

    assert unknown.status_code == 401
    assert unknown.json() == wrong_password.json()


async def test_me_returns_current_user_without_password_hash(client: AsyncClient) -> None:
    token = (await login(client, ADMIN_EMAIL, ADMIN_PASSWORD)).json()["access_token"]

    response = await client.get("/api/auth/me", headers=bearer(token))

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == ADMIN_EMAIL
    assert body["role"] == "admin"
    assert body["last_login_at"] is not None
    assert "password_hash" not in body


async def test_me_requires_token(client: AsyncClient) -> None:
    response = await client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Wymagane logowanie"}


async def test_me_rejects_invalid_token(client: AsyncClient) -> None:
    response = await client.get("/api/auth/me", headers=bearer("to-nie-jest-token"))

    assert response.status_code == 401


async def test_deactivated_user_loses_access(client: AsyncClient) -> None:
    user_service = UserService(UserRepository())
    user = await user_service.create_user("jan@example.com", "haslo-jana", "Jan")
    token = (await login(client, "jan@example.com", "haslo-jana")).json()["access_token"]

    user.is_active = False
    await user.save()

    me = await client.get("/api/auth/me", headers=bearer(token))
    relogin = await login(client, "jan@example.com", "haslo-jana")
    assert me.status_code == 401
    assert relogin.status_code == 401
    assert relogin.json() == {"detail": "Konto jest nieaktywne"}


async def test_create_user_rejects_duplicate_email(app: FastAPI) -> None:
    user_service = UserService(UserRepository())
    await user_service.create_user("ola@example.com", "haslo-oli", "Ola")

    with pytest.raises(ConflictError):
        await user_service.create_user("OLA@example.com", "inne-haslo", "Ola 2")
