from httpx import AsyncClient, Response

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin-password"

TEST_ENVIRONMENT = {
    "MONGO_DB": "mitreai_test",
    "JWT_SECRET": "test-secret-that-is-at-least-32-characters-long",
    "ADMIN_EMAIL": ADMIN_EMAIL,
    "ADMIN_PASSWORD": ADMIN_PASSWORD,
}


async def login(client: AsyncClient, email: str, password: str) -> Response:
    return await client.post("/api/auth/login", data={"username": email, "password": password})


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
