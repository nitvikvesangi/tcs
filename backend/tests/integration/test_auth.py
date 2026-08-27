"""
Integration tests for the auth endpoints.

Tests:
  POST /api/v1/auth/register
    - success (201 + token)
    - duplicate email (400)

  POST /api/v1/auth/login
    - success (200 + token)
    - wrong password (401)
    - unknown email (401)

  GET /api/v1/auth/me
    - with valid token (200 + user profile)
    - without token (401)
    - with invalid token (401)
    - with tampered token (401)

Uses the `client` fixture from conftest.py (SQLite, rolled back per test).
"""

import pytest


REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/auth/me"

VALID_USER = {
    "email": "priya@freshmart.in",
    "password": "Secr3t!Pass",
    "full_name": "Priya Sharma",
    "retailer_name": "FreshMart",
}


# ---------------------------------------------------------------------------
# POST /register
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_success_returns_201_with_token(self, client):
        resp = client.post(REGISTER_URL, json=VALID_USER)
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert body["user"]["email"] == VALID_USER["email"]
        assert body["user"]["full_name"] == VALID_USER["full_name"]
        assert "password" not in body["user"]
        assert "password_hash" not in body["user"]

    def test_register_creates_retailer_in_user_response(self, client):
        resp = client.post(REGISTER_URL, json=VALID_USER)
        assert resp.status_code == 201
        user = resp.json()["user"]
        # retailer_id is not None because retailer_name was supplied
        assert user["retailer_id"] is not None

    def test_register_without_retailer_name(self, client):
        data = {**VALID_USER, "email": "solo@test.com"}
        del data["retailer_name"]  # omit retailer_name
        resp = client.post(REGISTER_URL, json=data)
        assert resp.status_code == 201
        user = resp.json()["user"]
        assert user["retailer_id"] is None

    def test_register_duplicate_email_returns_400(self, client):
        client.post(REGISTER_URL, json=VALID_USER)
        resp = client.post(REGISTER_URL, json=VALID_USER)
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    def test_register_invalid_email_returns_422(self, client):
        resp = client.post(REGISTER_URL, json={**VALID_USER, "email": "not-an-email"})
        assert resp.status_code == 422

    def test_register_short_password_returns_422(self, client):
        resp = client.post(REGISTER_URL, json={**VALID_USER, "password": "short"})
        assert resp.status_code == 422

    def test_register_missing_email_returns_422(self, client):
        data = {k: v for k, v in VALID_USER.items() if k != "email"}
        resp = client.post(REGISTER_URL, json=data)
        assert resp.status_code == 422

    def test_register_token_is_decodable(self, client):
        resp = client.post(REGISTER_URL, json=VALID_USER)
        token = resp.json()["access_token"]
        from app.core.security import decode_access_token
        payload = decode_access_token(token)
        assert payload is not None
        assert "sub" in payload


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------

class TestLogin:
    def _register(self, client):
        """Helper: register and return the raw response."""
        return client.post(REGISTER_URL, json=VALID_USER)

    def test_login_success_returns_200_with_token(self, client):
        self._register(client)
        resp = client.post(LOGIN_URL, json={
            "email": VALID_USER["email"],
            "password": VALID_USER["password"],
        })
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert body["user"]["email"] == VALID_USER["email"]

    def test_login_wrong_password_returns_401(self, client):
        self._register(client)
        resp = client.post(LOGIN_URL, json={
            "email": VALID_USER["email"],
            "password": "WrongPassword!",
        })
        assert resp.status_code == 401

    def test_login_unknown_email_returns_401(self, client):
        resp = client.post(LOGIN_URL, json={
            "email": "nobody@nowhere.com",
            "password": "SomePass123",
        })
        assert resp.status_code == 401

    def test_login_returns_401_not_404_for_unknown_user(self, client):
        """No user enumeration — same status code for wrong email vs wrong password."""
        resp = client.post(LOGIN_URL, json={
            "email": "ghost@example.com",
            "password": "password",
        })
        assert resp.status_code == 401

    def test_login_missing_email_returns_422(self, client):
        resp = client.post(LOGIN_URL, json={"password": "pass"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /me
# ---------------------------------------------------------------------------

class TestMe:
    def _get_token(self, client):
        resp = client.post(REGISTER_URL, json=VALID_USER)
        assert resp.status_code == 201
        return resp.json()["access_token"]

    def test_me_with_valid_token_returns_user(self, client):
        token = self._get_token(client)
        resp = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["email"] == VALID_USER["email"]
        assert body["full_name"] == VALID_USER["full_name"]
        assert body["is_active"] is True

    def test_me_without_token_returns_401(self, client):
        resp = client.get(ME_URL)
        assert resp.status_code == 401

    def test_me_with_invalid_token_returns_401(self, client):
        resp = client.get(ME_URL, headers={"Authorization": "Bearer totally.invalid.token"})
        assert resp.status_code == 401

    def test_me_with_tampered_token_returns_401(self, client):
        token = self._get_token(client)
        parts = token.split(".")
        tampered = parts[0] + "." + parts[1] + ".tampered_signature"
        resp = client.get(ME_URL, headers={"Authorization": f"Bearer {tampered}"})
        assert resp.status_code == 401

    def test_me_response_does_not_contain_password(self, client):
        token = self._get_token(client)
        resp = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
        body = resp.json()
        assert "password" not in body
        assert "password_hash" not in body

    def test_me_role_is_retailer_admin(self, client):
        token = self._get_token(client)
        resp = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
        assert resp.json()["role"] == "RETAILER_ADMIN"
