from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import AuthServiceDep, CurrentUserDep
from app.schemas.auth import TokenResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    summary="Logowanie e-mailem i hasłem",
    description="Pole `username` to adres e-mail. Zwraca token JWT do nagłówka Authorization.",
)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
) -> TokenResponse:
    token = await auth_service.login(form.username, form.password)
    return TokenResponse(access_token=token)


@router.get("/me", summary="Dane zalogowanego użytkownika")
async def get_me(user: CurrentUserDep) -> UserResponse:
    return UserResponse.model_validate(user)
