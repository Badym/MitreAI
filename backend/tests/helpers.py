from httpx import AsyncClient, Response

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin-password"
USER_PASSWORD = "haslo-testowe"

TEST_ENVIRONMENT = {
    "MONGO_DB": "mitreai_test",
    "JWT_SECRET": "test-secret-that-is-at-least-32-characters-long",
    "ADMIN_EMAIL": ADMIN_EMAIL,
    "ADMIN_PASSWORD": ADMIN_PASSWORD,
    "AVAILABLE_MODELS": '["mock-small", "mock-large"]',
}


async def login(client: AsyncClient, email: str, password: str) -> Response:
    return await client.post("/api/auth/login", data={"username": email, "password": password})


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def login_headers(client: AsyncClient, email: str, password: str) -> dict[str, str]:
    response = await login(client, email, password)
    return bearer(response.json()["access_token"])


async def create_user(
    client: AsyncClient,
    admin_headers: dict[str, str],
    email: str,
    role: str = "user",
) -> Response:
    payload = {
        "email": email,
        "password": USER_PASSWORD,
        "display_name": email.split("@")[0],
        "role": role,
    }
    return await client.post("/api/users", json=payload, headers=admin_headers)


async def create_user_headers(
    client: AsyncClient, admin_headers: dict[str, str], email: str
) -> dict[str, str]:
    await create_user(client, admin_headers, email)
    return await login_headers(client, email, USER_PASSWORD)
