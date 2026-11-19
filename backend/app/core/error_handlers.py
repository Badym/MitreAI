from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppError,
    AuthenticationError,
    ConflictError,
    InvalidRequestError,
    NotFoundError,
    PermissionDeniedError,
)

STATUS_BY_ERROR: dict[type[AppError], int] = {
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    PermissionDeniedError: status.HTTP_403_FORBIDDEN,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    InvalidRequestError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


async def handle_app_error(_: Request, error: AppError) -> JSONResponse:
    status_code = STATUS_BY_ERROR.get(type(error), status.HTTP_400_BAD_REQUEST)
    headers = {"WWW-Authenticate": "Bearer"} if isinstance(error, AuthenticationError) else None
    return JSONResponse({"detail": error.message}, status_code=status_code, headers=headers)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)
