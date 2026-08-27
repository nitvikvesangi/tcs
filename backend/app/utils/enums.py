"""
Shared enumerations used across models, schemas, services, and engines.

Centralizing these here (rather than redefining per-module) keeps the
promotion engine, inventory engine, and API contracts consistent across
all implementation phases, per the project's naming-convention rule.
"""

from enum import Enum


class UserRole(str, Enum):
    RETAILER_ADMIN = "RETAILER_ADMIN"
    STORE_MANAGER = "STORE_MANAGER"
    ANALYST = "ANALYST"


class StoreStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    TEMPORARILY_CLOSED = "TEMPORARILY_CLOSED"


class UrgencyLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ExpiryStatus(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    URGENT = "URGENT"
    CRITICAL = "CRITICAL"


class InventoryAlertType(str, Enum):
    UNDERSTOCK = "UNDERSTOCK"
    OVERSTOCK = "OVERSTOCK"
    EXPIRY = "EXPIRY"
    STOCKOUT = "STOCKOUT"
    DECLINING_DEMAND = "DECLINING_DEMAND"
    EMERGING_TREND = "EMERGING_TREND"
    COMPETITOR_PRESSURE = "COMPETITOR_PRESSURE"


class DemandTrend(str, Enum):
    INCREASING = "INCREASING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"


class CustomerSegment(str, Enum):
    BUDGET_CONSCIOUS = "BUDGET_CONSCIOUS"
    PREMIUM = "PREMIUM"
    FREQUENT_BUYER = "FREQUENT_BUYER"
    OCCASIONAL_BUYER = "OCCASIONAL_BUYER"
    NEW_CUSTOMER = "NEW_CUSTOMER"
    HIGH_VALUE_CUSTOMER = "HIGH_VALUE_CUSTOMER"


class PromotionType(str, Enum):
    PERCENTAGE_DISCOUNT = "PERCENTAGE_DISCOUNT"
    FIXED_DISCOUNT = "FIXED_DISCOUNT"
    BUNDLE = "BUNDLE"
    BUY_ONE_GET_ONE = "BUY_ONE_GET_ONE"
    CLEARANCE = "CLEARANCE"
    NO_PROMOTION = "NO_PROMOTION"


class PromotionObjective(str, Enum):
    MAXIMIZE_PROFIT = "MAXIMIZE_PROFIT"
    MAXIMIZE_SALES = "MAXIMIZE_SALES"
    CLEAR_INVENTORY = "CLEAR_INVENTORY"
    REDUCE_EXPIRY_WASTE = "REDUCE_EXPIRY_WASTE"
    INCREASE_RETENTION = "INCREASE_RETENTION"
    INCREASE_AOV = "INCREASE_AOV"
    BALANCED = "BALANCED"


class PromotionStatus(str, Enum):
    RECOMMENDED = "RECOMMENDED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class OrderStatus(str, Enum):
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"


class CustomerEventType(str, Enum):
    VIEW = "VIEW"
    SEARCH = "SEARCH"
    CART_ADD = "CART_ADD"
    PURCHASE = "PURCHASE"


class WeatherCondition(str, Enum):
    SUNNY = "SUNNY"
    RAINY = "RAINY"
    CLOUDY = "CLOUDY"
    HOT = "HOT"
    COLD = "COLD"
    STORMY = "STORMY"


class DayPart(str, Enum):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"
    NIGHT = "NIGHT"


class WeekdayType(str, Enum):
    WEEKDAY = "WEEKDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
    HOLIDAY = "HOLIDAY"


class RiskFlag(str, Enum):
    NONE = "NONE"
    EXPIRY_CRITICAL = "EXPIRY_CRITICAL"
    STOCKOUT_RISK = "STOCKOUT_RISK"
    OVERSTOCK_RISK = "OVERSTOCK_RISK"
    MARGIN_TOO_LOW = "MARGIN_TOO_LOW"
    NO_VALID_PROMOTION = "NO_VALID_PROMOTION"
