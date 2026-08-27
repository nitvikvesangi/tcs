"""
Auth Pydantic schemas.

Covers registration, login, token response, and the current-user response.
All passwords are write-only — never returned in any response schema.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.utils.enums import UserRole


class UserRegisterRequest(BaseModel):
    """Body for POST /api/v1/auth/register."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = Field(default=None, max_length=255)
    role: UserRole = UserRole.RETAILER_ADMIN
    # Optional: name of a new Retailer to create and associate with this user.
    # If omitted, the user is created without a Retailer (admin-level account).
    retailer_name: Optional[str] = Field(default=None, max_length=255)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if v.strip() != v:
            raise ValueError("Password must not start or end with whitespace")
        return v

    model_config = {"json_schema_extra": {"example": {
        "email": "admin@freshmart.in",
        "password": "Secr3t!Pass",
        "full_name": "Priya Sharma",
        "role": "RETAILER_ADMIN",
        "retailer_name": "FreshMart",
    }}}


class LoginRequest(BaseModel):
    """Body for POST /api/v1/auth/login."""

    email: EmailStr
    password: str = Field(min_length=1)

    model_config = {"json_schema_extra": {"example": {
        "email": "admin@freshmart.in",
        "password": "Secr3t!Pass",
    }}}


class UserOut(BaseModel):
    """Serialised User returned in responses (never includes password_hash)."""

    id: int
    email: str
    full_name: Optional[str]
    role: UserRole
    retailer_id: Optional[int]
    is_active: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Response for login and register endpoints."""

    access_token: str
    token_type: str = "bearer"
    user: UserOut
