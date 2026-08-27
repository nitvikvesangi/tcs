"""
Unit tests for app/core/security.py.

All tests are pure Python — no database, no HTTP.
Tests are deterministic (no randomness).
"""

import time

import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

class TestHashPassword:
    def test_returns_non_empty_string(self):
        h = hash_password("MySecret1!")
        assert isinstance(h, str)
        assert len(h) > 20

    def test_hash_differs_from_plain(self):
        plain = "MySecret1!"
        assert hash_password(plain) != plain

    def test_same_password_produces_different_hashes(self):
        """bcrypt uses a random salt — identical passwords hash differently."""
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2


class TestVerifyPassword:
    def test_correct_password_returns_true(self):
        plain = "CorrectHorse!"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_wrong_password_returns_false(self):
        hashed = hash_password("real_password")
        assert verify_password("wrong_password", hashed) is False

    def test_empty_password_returns_false(self):
        hashed = hash_password("some_password")
        assert verify_password("", hashed) is False

    def test_case_sensitive(self):
        hashed = hash_password("Password")
        assert verify_password("password", hashed) is False


# ---------------------------------------------------------------------------
# JWT token creation
# ---------------------------------------------------------------------------

class TestCreateAccessToken:
    def test_returns_string(self):
        token = create_access_token("user-1")
        assert isinstance(token, str)
        assert len(token) > 10

    def test_contains_three_segments(self):
        """JWT structure: header.payload.signature"""
        token = create_access_token("user-1")
        assert token.count(".") == 2

    def test_subject_is_encoded(self):
        token = create_access_token("user-42")
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user-42"

    def test_extra_claims_are_included(self):
        token = create_access_token(
            "user-1",
            extra_claims={"role": "RETAILER_ADMIN", "retailer_id": 7},
        )
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["role"] == "RETAILER_ADMIN"
        assert payload["retailer_id"] == 7

    def test_token_has_exp_and_iat(self):
        token = create_access_token("user-1")
        payload = decode_access_token(token)
        assert payload is not None
        assert "exp" in payload
        assert "iat" in payload
        # exp must be in the future
        assert payload["exp"] > time.time()
        # iat must be in the past or now
        assert payload["iat"] <= time.time() + 2


# ---------------------------------------------------------------------------
# JWT token decoding
# ---------------------------------------------------------------------------

class TestDecodeAccessToken:
    def test_valid_token_returns_payload(self):
        token = create_access_token("user-99")
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user-99"

    def test_invalid_token_returns_none(self):
        result = decode_access_token("this.is.not.a.valid.jwt")
        assert result is None

    def test_empty_string_returns_none(self):
        assert decode_access_token("") is None

    def test_tampered_signature_returns_none(self):
        token = create_access_token("user-1")
        # Flip the last character of the signature segment.
        parts = token.split(".")
        sig = parts[2]
        tampered_sig = sig[:-1] + ("A" if sig[-1] != "A" else "B")
        tampered = ".".join(parts[:2] + [tampered_sig])
        assert decode_access_token(tampered) is None

    def test_token_signed_with_different_secret_returns_none(self):
        """Simulate a token from a different service / rotated secret."""
        import datetime
        from jose import jwt

        foreign_token = jwt.encode(
            {"sub": "attacker", "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            key="completely_different_secret",
            algorithm="HS256",
        )
        assert decode_access_token(foreign_token) is None
