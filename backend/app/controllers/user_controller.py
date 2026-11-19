from fastapi import APIRouter, status

from app.dependencies import AdminUserDep, UserServiceDep
from app.schemas.user import UserCreateRequest, UserResponse, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Załóż konto (tylko admin)",
)
async def create_user(
    request: UserCreateRequest,
    user_service: UserServiceDep,
    _: AdminUserDep,
) -> UserResponse:
    user = await user_service.create_user(
        request.email, request.password, request.display_name, request.role
    )
    return UserResponse.model_validate(user)


@router.get("", summary="Lista kont (tylko admin)")
async def list_users(user_service: UserServiceDep, _: AdminUserDep) -> list[UserResponse]:
    users = await user_service.list_users()
    return [UserResponse.model_validate(user) for user in users]


@router.get("/{user_id}", summary="Szczegóły konta (tylko admin)")
async def get_user(user_id: str, user_service: UserServiceDep, _: AdminUserDep) -> UserResponse:
    return UserResponse.model_validate(await user_service.get_user(user_id))


@router.patch(
    "/{user_id}",
    summary="Zmień nazwę, rolę, aktywność lub hasło (tylko admin)",
    description="Wysyłasz tylko pola, które chcesz zmienić.",
)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    user_service: UserServiceDep,
    admin: AdminUserDep,
) -> UserResponse:
    user = await user_service.update_user(user_id, request, acting_admin=admin)
    return UserResponse.model_validate(user)
