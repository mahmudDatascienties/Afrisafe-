"""Tests for JWT creation and verification."""

from __future__ import annotations

import time

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_access_token_decodes():
    token = create_access_token(42, extra_claims={"role": "user"})
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert payload["role"] == "user"


def test_refresh_token_decodes():
    token = create_refresh_token(7)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "7"
    assert payload["type"] == "refresh"


def test_invalid_token_returns_none():
    assert decode_token("not.a.valid.token") is None


def test_password_hash_and_verify():
    hashed = hash_password("mysecret")
    assert hashed != "mysecret"
    assert verify_password("mysecret", hashed) is True
    assert verify_password("wrong", hashed) is False
