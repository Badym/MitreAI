from fastapi import APIRouter

from app.dependencies import CurrentUserDep, ModelServiceDep
from app.schemas.llm_model import ModelResponse

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", summary="Lista dostępnych modeli")
async def list_models(model_service: ModelServiceDep, _: CurrentUserDep) -> list[ModelResponse]:
    return model_service.list_models()
