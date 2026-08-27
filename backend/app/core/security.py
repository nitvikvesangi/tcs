"""
Security utilities: password hashing and JWT token creation/verification.

Implemented fully in Phase 0 because it has no dependency on database
models and is needed as a stable contract for the auth service built in
Phase 1.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    extra_claims: Optional[dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token.

    `subject` is typically the user id. `extra_claims` can carry things
    like role or retailer_id for authorization checks downstream.
    """
    to_encode: dict[str, Any] = {"sub": str(subject)}
    if extra_claims:
        to_encode.update(extra_claims)

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    to_encode["iat"] = datetime.now(timezone.utc)

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """Decode and validate a JWT. Returns the payload, or None if invalid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
