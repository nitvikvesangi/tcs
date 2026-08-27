"""
FastAPI application entrypoint.

Phase 0: scaffolding.
Phase 1: auth router wired in.

Each subsequent phase adds its own router here without touching existing lines.
"""

from app.api.v1.auth import router as auth_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.stores import router as stores_router
from app.api.v1.promotions import router as promotions_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.chat import router as chat_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-Driven Quick Commerce Promotion, Inventory and Retail "
        "Intelligence Platform — backend API."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------
# Routers — grows phase by phase; existing lines are never removed.
# ----------------------------------------------------------------------

# Phase 1: authentication
app.include_router(auth_router, prefix=settings.API_V1_PREFIX + "/auth", tags=["auth"])

# Phase 2: inventory
app.include_router(inventory_router, prefix=settings.API_V1_PREFIX + "/inventory", tags=["inventory"])
app.include_router(stores_router, prefix=settings.API_V1_PREFIX + "/stores", tags=["stores"])

# Phase 3: analytics
app.include_router(analytics_router, prefix=settings.API_V1_PREFIX + "/analytics", tags=["analytics"])

# Phase 4: promotions
app.include_router(promotions_router, prefix=settings.API_V1_PREFIX + "/promotions", tags=["promotions"])

# Phase 5: chat
app.include_router(chat_router, prefix=settings.API_V1_PREFIX + "/chat", tags=["chat"])


@app.get("/", tags=["health"])
def root() -> dict:
    return {
        "service": settings.APP_NAME,
        "status": "ok",
        "env": settings.APP_ENV,
        "demo_mode": settings.is_demo_mode,
    }


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "healthy"}


@app.on_event("startup")
def on_startup() -> None:
    logger.info("Starting %s (env=%s, demo_mode=%s)", settings.APP_NAME, settings.APP_ENV, settings.is_demo_mode)


@app.on_event("shutdown")
def on_shutdown() -> None:
    logger.info("Shutting down %s", settings.APP_NAME)
