from app.core.config import Settings
from app.core.exceptions import InvalidRequestError


class ModelService:
    def __init__(self, settings: Settings) -> None:
        self._models = list(settings.available_models)

    @property
    def default_model(self) -> str:
        return self._models[0]

    def list_models(self) -> list[str]:
        return list(self._models)

    def resolve(self, model: str | None) -> str:
        if model is None:
            return self.default_model
        if model not in self._models:
            raise InvalidRequestError(f"Nieznany model: {model}")
        return model
