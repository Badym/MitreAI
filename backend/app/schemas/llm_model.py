from pydantic import BaseModel


class ModelResponse(BaseModel):
    id: str
    is_default: bool
