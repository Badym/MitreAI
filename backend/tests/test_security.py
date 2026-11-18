from datetime import timedelta

from app.core.security import (
    create_access_token,
    hash_password,
    read_token_subject,
    verify_password,
)

SECRET = "unit-test-secret-that-is-at-least-32-chars"
OTHER_SECRET = "other-secret-that-is-at-least-32-chars"


def test_password_hash_matches_only_original_password() -> None:
    password_hash = hash_password("tajne-haslo")

    assert password_hash != "tajne-haslo"
    assert verify_password("tajne-haslo", password_hash)
    assert not verify_password("inne-haslo", password_hash)


def test_token_contains_subject() -> None:
    token = create_access_token("user-1", SECRET, timedelta(minutes=5))

    assert read_token_subject(token, SECRET) == "user-1"


def test_expired_token_is_rejected() -> None:
    token = create_access_token("user-1", SECRET, timedelta(seconds=-1))

    assert read_token_subject(token, SECRET) is None


def test_token_signed_with_other_secret_is_rejected() -> None:
    token = create_access_token("user-1", OTHER_SECRET, timedelta(minutes=5))

    assert read_token_subject(token, SECRET) is None


def test_malformed_token_is_rejected() -> None:
    assert read_token_subject("to-nie-jest-token", SECRET) is None
