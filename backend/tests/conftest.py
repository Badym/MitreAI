import os
from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from tests.helpers import TEST_ENVIRONMENT

os.environ.update(TEST_ENVIRONMENT)
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")

from app.main import create_app  # noqa: E402


@pytest.fixture
async def app() -> AsyncIterator[FastAPI]:
    application = create_app()
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
