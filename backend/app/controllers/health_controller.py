from fastapi import APIRouter, Response, status

from app.dependencies import HealthServiceDep
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "",
    summary="Stan aplikacji i połączenia z bazą",
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": HealthResponse}},
)
async def get_health(service: HealthServiceDep, response: Response) -> HealthResponse:
    result = await service.check()
    if result.status != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return result
