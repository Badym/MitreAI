from dataclasses import dataclass
from typing import Any, Protocol

from app.models.message import Message


@dataclass(frozen=True)
class ModelReply:
    content: str
    tokens_in: int | None = None
    tokens_out: int | None = None
    analysis: dict[str, Any] | None = None


class LLMProvider(Protocol):
    async def generate(self, model: str, history: list[Message]) -> ModelReply: ...
