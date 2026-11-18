from app.llm.provider import ModelReply
from app.models.message import Message


class MockProvider:
    async def generate(self, model: str, history: list[Message]) -> ModelReply:
        return ModelReply(content=f"Odpowiedź z modelu {model}")
