"""
Auth service — registration, login, and token verification.

Business logic lives here, not in the route handler, following the project's
API layer → Service layer → Database pattern.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.security import create_access_token, hash_password, verify_password
from app.models.retailer import Retailer, User
from app.schemas.auth import UserRegisterRequest
from app.utils.enums import UserRole

logger = get_logger(__name__)


class AuthService:
    """Stateless service; all methods accept a `db` session explicitly."""

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    @staticmethod
    def register(db: Session, data: UserRegisterRequest) -> tuple[User, str]:
        """
        Create a new User (and optionally a new Retailer) and return the
        (user, access_token) pair.

        Raises ValueError if the email is already registered.
        """
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise ValueError(f"Email '{data.email}' is already registered")

        retailer_id: int | None = None

        if data.retailer_name:
            # Create a brand-new Retailer associated with this user.
            retailer = Retailer(name=data.retailer_name, email=data.email)
            db.add(retailer)
            db.flush()  # populate retailer.id without full commit
            retailer_id = retailer.id
            logger.info("Created Retailer id=%s name=%r", retailer.id, retailer.name)

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            role=data.role if data.role else UserRole.RETAILER_ADMIN,
            retailer_id=retailer_id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Registered User id=%s email=%r role=%s", user.id, user.email, user.role)

        token = _issue_token(user)
        return user, token

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    @staticmethod
    def login(db: Session, email: str, password: str) -> tuple[User, str]:
        """
        Authenticate by email + password.

        Raises ValueError with a deliberately generic message (no username
        enumeration) on any failure.
        """
        user = (
            db.query(User)
            .filter(User.email == email, User.is_active.is_(True))
            .first()
        )
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        token = _issue_token(user)
        logger.info("Login User id=%s email=%r", user.id, user.email)
        return user, token

    # ------------------------------------------------------------------
    # Current user lookup (used by the /me dependency)
    # ------------------------------------------------------------------

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()


# ------------------------------------------------------------------
# Private helpers
# ------------------------------------------------------------------

def _issue_token(user: User) -> str:
    return create_access_token(
        subject=str(user.id),
        extra_claims={
            "email": user.email,
            "role": user.role.value,
            "retailer_id": user.retailer_id,
        },
    )
