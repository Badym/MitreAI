from httpx import AsyncClient

from app.models.message import Message


async def create_conversation(client: AsyncClient, headers: dict[str, str], **payload: str) -> dict:
    response = await client.post("/api/conversations", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


async def test_new_conversation_gets_default_model(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    conversation = await create_conversation(client, user_headers)

    assert conversation["model"] == "mock-small"
    assert conversation["title"] == ""
    assert conversation["is_archived"] is False


async def test_unknown_model_returns_422(client: AsyncClient, user_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/conversations", json={"model": "gpt-x"}, headers=user_headers
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Nieznany model: gpt-x"}


async def test_list_shows_only_own_conversations_newest_first(
    client: AsyncClient,
    user_headers: dict[str, str],
    other_user_headers: dict[str, str],
) -> None:
    first = await create_conversation(client, user_headers, title="Pierwsza")
    second = await create_conversation(client, user_headers, title="Druga")
    await create_conversation(client, other_user_headers, title="Cudza")

    response = await client.get("/api/conversations", headers=user_headers)

    assert [item["id"] for item in response.json()] == [second["id"], first["id"]]


async def test_other_user_cannot_access_conversation(
    client: AsyncClient,
    user_headers: dict[str, str],
    other_user_headers: dict[str, str],
) -> None:
    conversation_id = (await create_conversation(client, user_headers))["id"]
    url = f"/api/conversations/{conversation_id}"

    responses = [
        await client.get(url, headers=other_user_headers),
        await client.patch(url, json={"title": "Moja"}, headers=other_user_headers),
        await client.delete(url, headers=other_user_headers),
    ]

    assert [response.status_code for response in responses] == [404, 404, 404]
    assert (await client.get(url, headers=user_headers)).status_code == 200


async def test_update_title_model_and_archive(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    conversation_id = (await create_conversation(client, user_headers))["id"]

    response = await client.patch(
        f"/api/conversations/{conversation_id}",
        json={"title": "  Sterownik PLC  ", "model": "mock-large", "is_archived": True},
        headers=user_headers,
    )
    active = await client.get("/api/conversations", headers=user_headers)
    archived = await client.get("/api/conversations?archived=true", headers=user_headers)

    assert response.status_code == 200
    assert response.json()["title"] == "Sterownik PLC"
    assert response.json()["model"] == "mock-large"
    assert active.json() == []
    assert [item["id"] for item in archived.json()] == [conversation_id]


async def test_delete_removes_conversation_with_messages(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    conversation_id = (await create_conversation(client, user_headers))["id"]
    await client.post(
        f"/api/conversations/{conversation_id}/messages",
        data={"content": "Opis komponentu"},
        headers=user_headers,
    )

    response = await client.delete(f"/api/conversations/{conversation_id}", headers=user_headers)

    assert response.status_code == 204
    get_after = await client.get(f"/api/conversations/{conversation_id}", headers=user_headers)
    assert get_after.status_code == 404
    assert await Message.find_all().count() == 0
