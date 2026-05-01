"""
JobSpy Web Application - Main Entry Point
Main FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import init_db, close_db
from app.routers import auth, jobs, saved_jobs, alerts, users, stats

# Import DI container
from app.presentation.api.v1.dependencies import wire_container, reset_container

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug Mode: {settings.DEBUG}")
    logger.info(f"🗄️  Database: {settings.DATABASE_URL}")
    
    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️  Database initialization warning: {e}")
    
    # Wire DI container to routers
    try:
        wire_container([
            "app.routers.jobs",
            "app.routers.auth",
            "app.routers.alerts",
            "app.routers.saved_jobs",
            "app.routers.stats",
            "app.routers.users",
        ])
        logger.info("✅ Dependency Injection container wired successfully")
    except Exception as e:
        logger.error(f"❌ Failed to wire DI container: {e}")
        # Continue anyway - old code will still work
    
    yield
    
    # Shutdown
    logger.info(f"🛑 Shutting down {settings.APP_NAME}")
    
    # Reset DI container
    try:
        reset_container()
        logger.info("✅ DI container reset successfully")
    except Exception as e:
        logger.warning(f"⚠️  DI container reset warning: {e}")
    
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="JobSpy Web Application - A Comprehensive Job Search Platform",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# ── Middleware Configuration ─────────────────────────────────────────
# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# ── Health Check Endpoint ────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "redoc": "/api/redoc",
    }


# ── Error Handlers ───────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "error": str(exc) if settings.DEBUG else "An error occurred",
        },
    )


# ── Router Registration ──────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(saved_jobs.router)
app.include_router(alerts.router)
app.include_router(users.router)
app.include_router(stats.router)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
