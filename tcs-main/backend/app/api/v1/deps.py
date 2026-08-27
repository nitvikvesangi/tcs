"""
FastAPI route-level dependencies.

get_current_user — validates the Bearer JWT and returns the active User.
get_current_active_retailer_admin — additional role guard for admin-only routes.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.retailer import User
from app.utils.enums import UserRole

# tokenUrl points to the login endpoint that issues tokens.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the JWT, look up the user, and return the active User model.

    Raises HTTP 401 on any failure (expired token, bad signature, user not
    found, user deactivated).  The error message is intentionally generic
    to avoid leaking information.
    """
    _credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise _credentials_exception

    user_id_str: str | None = payload.get("sub")
    if not user_id_str:
        raise _credentials_exception

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise _credentials_exception

    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if user is None:
        raise _credentials_exception

    return user


def get_current_retailer_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require RETAILER_ADMIN role; raise HTTP 403 otherwise."""
    if current_user.role != UserRole.RETAILER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Retailer admin role required",
        )
    return current_user
