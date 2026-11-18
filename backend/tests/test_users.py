from httpx import AsyncClient

from tests.helpers import USER_PASSWORD, create_user, login

MISSING_ID = "6a0000000000000000000000"


async def test_admin_creates_user_who_can_log_in(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    response = await create_user(client, admin_headers, "Jan@Example.com")

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "jan@example.com"
    assert body["role"] == "user"
    assert body["is_active"] is True
    assert "password_hash" not in body
    assert (await login(client, "jan@example.com", USER_PASSWORD)).status_code == 200


async def test_duplicate_email_returns_409(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    await create_user(client, admin_headers, "jan@example.com")

    response = await create_user(client, admin_headers, "JAN@example.com")

    assert response.status_code == 409


async def test_too_short_password_returns_422(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    payload = {"email": "jan@example.com", "password": "krotkie", "display_name": "Jan"}

    response = await client.post("/api/users", json=payload, headers=admin_headers)

    assert response.status_code == 422


async def test_regular_user_cannot_manage_accounts(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    create = await create_user(client, user_headers, "ktos@example.com")
    listing = await client.get("/api/users", headers=user_headers)

    assert create.status_code == 403
    assert listing.status_code == 403
    assert listing.json() == {"detail": "Ta operacja wymaga roli administratora"}


async def test_anonymous_cannot_list_users(client: AsyncClient) -> None:
    response = await client.get("/api/users")

    assert response.status_code == 401


async def test_admin_lists_users_oldest_first(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    await create_user(client, admin_headers, "jan@example.com")

    response = await client.get("/api/users", headers=admin_headers)

    assert [user["email"] for user in response.json()] == ["admin@example.com", "jan@example.com"]


async def test_admin_deactivates_user(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    user_id = (await create_user(client, admin_headers, "jan@example.com")).json()["id"]

    response = await client.patch(
        f"/api/users/{user_id}", json={"is_active": False}, headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert (await login(client, "jan@example.com", USER_PASSWORD)).status_code == 401


async def test_admin_resets_password(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    user_id = (await create_user(client, admin_headers, "jan@example.com")).json()["id"]

    await client.patch(
        f"/api/users/{user_id}", json={"password": "nowe-haslo-123"}, headers=admin_headers
    )

    assert (await login(client, "jan@example.com", USER_PASSWORD)).status_code == 401
    assert (await login(client, "jan@example.com", "nowe-haslo-123")).status_code == 200


async def test_admin_cannot_lock_themselves_out(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    admin_id = (await client.get("/api/auth/me", headers=admin_headers)).json()["id"]

    deactivate = await client.patch(
        f"/api/users/{admin_id}", json={"is_active": False}, headers=admin_headers
    )
    demote = await client.patch(
        f"/api/users/{admin_id}", json={"role": "user"}, headers=admin_headers
    )

    assert deactivate.status_code == 409
    assert demote.status_code == 409


async def test_unknown_user_returns_404(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    missing = await client.get(f"/api/users/{MISSING_ID}", headers=admin_headers)
    malformed = await client.get("/api/users/nie-ma-takiego", headers=admin_headers)

    assert missing.status_code == 404
    assert malformed.status_code == 404
