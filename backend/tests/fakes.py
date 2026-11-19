from app.llm.provider import ModelReply
from app.models.message import Message


def fake_reply(model: str) -> str:
    return f"Testowa odpowiedź modelu {model}"


class FakeLLMProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str]]]] = []

    async def generate(self, model: str, history: list[Message]) -> ModelReply:
        self.calls.append((model, [(message.role, message.content) for message in history]))
        return ModelReply(content=fake_reply(model))
