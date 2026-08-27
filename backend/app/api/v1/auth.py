"""
Auth router — POST /register, POST /login, GET /me.

Thin handlers: all business logic delegated to AuthService.
Error handling converts service-layer ValueError into HTTP 400/401.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.retailer import User
from app.schemas.auth import LoginRequest, TokenResponse, UserOut, UserRegisterRequest
from app.services.auth import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(
    data: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Create a new User.  Optionally creates a new Retailer if `retailer_name`
    is supplied.  Returns a JWT token immediately so the client can proceed
    without a separate login step.
    """
    try:
        user, token = AuthService.register(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Obtain a JWT access token",
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate with email + password.  Returns a JWT access token.

    The `token_type` is always `"bearer"`.  Send the token as:
    `Authorization: Bearer <access_token>` on subsequent requests.
    """
    try:
        user, token = AuthService.login(db, data.email, data.password)
    except ValueError:
        # Use 401 not 400 for login failures (RFC 7235).
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get(
    "/me",
    response_model=UserOut,
    summary="Return the authenticated user's profile",
)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    """
    Return the profile of the user identified by the Bearer token.

    HTTP 401 is raised by `get_current_user` if the token is missing,
    expired, or otherwise invalid.
    """
    return UserOut.model_validate(current_user)
