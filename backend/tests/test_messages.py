from httpx import AsyncClient, Response

PROMPT = "Sterownik PLC S7-1200 z dostępem przez VPN"


async def new_conversation_id(client: AsyncClient, headers: dict[str, str]) -> str:
    response = await client.post("/api/conversations", json={}, headers=headers)
    return response.json()["id"]


async def send(
    client: AsyncClient, headers: dict[str, str], conversation_id: str, **form: str
) -> Response:
    return await client.post(
        f"/api/conversations/{conversation_id}/messages", data=form, headers=headers
    )


async def test_send_message_returns_mock_reply(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    conversation_id = await new_conversation_id(client, user_headers)

    response = await send(client, user_headers, conversation_id, content=PROMPT)

    assert response.status_code == 201
    body = response.json()
    assert body["user_message"]["role"] == "user"
    assert body["user_message"]["content"] == PROMPT
    assert body["assistant_message"]["role"] == "assistant"
    assert body["assistant_message"]["content"] == "Odpowiedź z modelu mock-small"
    assert body["assistant_message"]["model"] == "mock-small"
    assert body["conversation"]["title"] == PROMPT


async def test_long_prompt_gives_shortened_title(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    conversation_id = await new_conversation_id(client, user_headers)

    response = await send(client, user_headers, conversation_id, content="a" * 100)

    title = response.json()["conversation"]["title"]
    assert len(title) == 60
    assert title.endswith("…")


async def test_selected_model_answers_and_becomes_conversation_model(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    conversation_id = await new_conversation_id(client, user_headers)

    response = await send(client, user_headers, conversation_id, content=PROMPT, model="mock-large")

    body = response.json()
    assert body["assistant_message"]["content"] == "Odpowiedź z modelu mock-large"
    assert body["conversation"]["model"] == "mock-large"


async def test_unknown_model_returns_422(client: AsyncClient, user_headers: dict[str, str]) -> None:
    conversation_id = await new_conversation_id(client, user_headers)

    response = await send(client, user_headers, conversation_id, content=PROMPT, model="gpt-x")

    assert response.status_code == 422


async def test_blank_prompt_returns_422(client: AsyncClient, user_headers: dict[str, str]) -> None:
    conversation_id = await new_conversation_id(client, user_headers)

    response = await send(client, user_headers, conversation_id, content="   ")

    assert response.status_code == 422


async def test_messages_are_listed_in_order(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    conversation_id = await new_conversation_id(client, user_headers)
    await send(client, user_headers, conversation_id, content="Pierwsze pytanie")
    await send(client, user_headers, conversation_id, content="Drugie pytanie")

    response = await client.get(
        f"/api/conversations/{conversation_id}/messages", headers=user_headers
    )

    messages = [(item["role"], item["content"]) for item in response.json()]
    assert messages == [
        ("user", "Pierwsze pytanie"),
        ("assistant", "Odpowiedź z modelu mock-small"),
        ("user", "Drugie pytanie"),
        ("assistant", "Odpowiedź z modelu mock-small"),
    ]


async def test_new_message_moves_conversation_to_top(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    older_id = await new_conversation_id(client, user_headers)
    await new_conversation_id(client, user_headers)

    await send(client, user_headers, older_id, content=PROMPT)
    response = await client.get("/api/conversations", headers=user_headers)

    assert response.json()[0]["id"] == older_id


async def test_cannot_use_other_users_conversation(
    client: AsyncClient,
    user_headers: dict[str, str],
    other_user_headers: dict[str, str],
) -> None:
    conversation_id = await new_conversation_id(client, user_headers)

    sent = await send(client, other_user_headers, conversation_id, content=PROMPT)
    listed = await client.get(
        f"/api/conversations/{conversation_id}/messages", headers=other_user_headers
    )

    assert sent.status_code == 404
    assert listed.status_code == 404


async def test_models_endpoint_lists_models_with_default(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    response = await client.get("/api/models", headers=user_headers)
    anonymous = await client.get("/api/models")

    assert response.json() == [
        {"id": "mock-small", "is_default": True},
        {"id": "mock-large", "is_default": False},
    ]
    assert anonymous.status_code == 401
