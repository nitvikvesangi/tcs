"""
ORM model registry — import every model so that:

1. SQLAlchemy's Base.metadata is fully populated (Alembic autogenerate reads this).
2. Relationship string-references resolve correctly at startup.
3. Any code that does `from app.models import Retailer, Product, ...` gets a
   single import point without having to know which sub-module a model lives in.

Import order follows FK dependency: Retailer → DarkStore → Product →
Inventory → Customer → Order → Review → Promotion → Context.
"""

from app.models.retailer import Retailer, User  # noqa: F401
from app.models.store import DarkStore  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.inventory import Inventory  # noqa: F401
from app.models.customer import Customer, CustomerEvent  # noqa: F401
from app.models.order import Order, OrderItem  # noqa: F401
from app.models.review import Review  # noqa: F401
from app.models.promotion import Promotion, PromotionPerformance  # noqa: F401
from app.models.context import Weather, Festival, Trend, CompetitorPrice  # noqa: F401

__all__ = [
    "Retailer",
    "User",
    "DarkStore",
    "Product",
    "Inventory",
    "Customer",
    "CustomerEvent",
    "Order",
    "OrderItem",
    "Review",
    "Promotion",
    "PromotionPerformance",
    "Weather",
    "Festival",
    "Trend",
    "CompetitorPrice",
]
