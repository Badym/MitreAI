import os
from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from tests.fakes import FakeLLMProvider
from tests.helpers import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    TEST_ENVIRONMENT,
    create_user_headers,
    login_headers,
)

os.environ.update(TEST_ENVIRONMENT)
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")

from app.dependencies import get_llm_provider  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture
def llm_provider() -> FakeLLMProvider:
    return FakeLLMProvider()


@pytest.fixture
async def app(llm_provider: FakeLLMProvider) -> AsyncIterator[FastAPI]:
    application = create_app()
    application.dependency_overrides[get_llm_provider] = lambda: llm_provider
    async with application.router.lifespan_context(application):
        yield application
        database = application.state.database
        assert database.name.endswith("_test"), "Testy mogą czyścić tylko bazę *_test"
        await database.client.drop_database(database.name)


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client


@pytest.fixture
async def admin_headers(client: AsyncClient) -> dict[str, str]:
    return await login_headers(client, ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture
async def user_headers(client: AsyncClient, admin_headers: dict[str, str]) -> dict[str, str]:
    return await create_user_headers(client, admin_headers, "jan@example.com")


@pytest.fixture
async def other_user_headers(client: AsyncClient, admin_headers: dict[str, str]) -> dict[str, str]:
    return await create_user_headers(client, admin_headers, "ola@example.com")
