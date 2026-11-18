from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

JWT_ALGORITHM = "HS256"

_password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hasher.verify(password, password_hash)


# Sprawdzany, gdy konto nie istnieje, żeby czas odpowiedzi nie zdradzał, czy e-mail jest w bazie.
DUMMY_PASSWORD_HASH = hash_password("dummy-password")


def create_access_token(subject: str, secret: str, lifetime: timedelta) -> str:
    issued_at = datetime.now(UTC)
    payload = {"sub": subject, "iat": issued_at, "exp": issued_at + lifetime}
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def read_token_subject(token: str, secret: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
    except jwt.InvalidTokenError:
        return None
    return payload["sub"]
