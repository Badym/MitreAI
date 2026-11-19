import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.controllers import api_router
from app.core.config import Settings, get_settings
from app.core.database import create_client, init_database
from app.core.error_handlers import register_error_handlers
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(name)s - %(message)s")


async def create_initial_admin(settings: Settings) -> None:
    password = settings.admin_password.get_secret_value() if settings.admin_password else None
    await UserService(UserRepository()).ensure_admin_exists(settings.admin_email, password)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    client = create_client(settings)
    database = client[settings.mongo_db]
    await init_database(database)
    await create_initial_admin(settings)
    app.state.database = database
    try:
        yield
    finally:
        await client.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    register_error_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
