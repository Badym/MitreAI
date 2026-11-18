from httpx import ASGITransport, AsyncClient

from app.dependencies import get_health_repository
from app.main import create_app


class FakeHealthRepository:
    def __init__(self, reachable: bool) -> None:
        self._reachable = reachable

    async def ping(self) -> bool:
        return self._reachable


def build_client(database_reachable: bool) -> AsyncClient:
    app = create_app()
    app.dependency_overrides[get_health_repository] = lambda: FakeHealthRepository(
        database_reachable
    )
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def test_health_returns_ok_when_database_reachable() -> None:
    async with build_client(database_reachable=True) as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


async def test_health_returns_503_when_database_unavailable() -> None:
    async with build_client(database_reachable=False) as client:
        response = await client.get("/api/health")

    assert response.status_code == 503
    assert response.json() == {"status": "error", "database": "unavailable"}


async def test_swagger_is_served_under_api_prefix() -> None:
    async with build_client(database_reachable=True) as client:
        response = await client.get("/api/openapi.json")

    assert response.status_code == 200
    assert "/api/health" in response.json()["paths"]
