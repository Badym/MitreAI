from app.repositories.health_repository import HealthRepository
from app.schemas.health import HealthResponse


class HealthService:
    def __init__(self, repository: HealthRepository) -> None:
        self._repository = repository

    async def check(self) -> HealthResponse:
        if await self._repository.ping():
            return HealthResponse(status="ok", database="ok")
        return HealthResponse(status="error", database="unavailable")
