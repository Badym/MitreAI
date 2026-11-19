from app.llm.mock_provider import MockProvider


async def test_mock_provider_answers_with_model_name() -> None:
    reply = await MockProvider().generate("mock-small", history=[])

    assert reply.content == "Odpowiedź z modelu mock-small"
    assert reply.analysis is None
