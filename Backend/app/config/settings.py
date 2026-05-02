"""
Application Configuration
Application Configuration Module
"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # ── Application Settings ─────────────────────────────────────────
    APP_NAME: str = "JobSpy Web Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # ── Server Settings ──────────────────────────────────────────────
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    RELOAD: bool = False
    
    # ── Database Settings ────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://admin:admin@localhost:5432/jobspy_db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # ── Redis Settings ───────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # Default TTL (1 hour)
    
    # ── Cache TTL Configuration (in seconds) ──────────────────────────
    CACHE_TTL_JOBS: int = 3600  # Jobs: 1 hour
    CACHE_TTL_SEARCH_RESULTS: int = 1800  # Search results: 30 minutes
    CACHE_TTL_STATISTICS: int = 3600  # Statistics: 1 hour
    CACHE_TTL_USERS: int = 86400  # Users: 24 hours
    CACHE_TTL_SEARCH_HISTORY: int = 3600  # Search history: 1 hour
    CACHE_TTL_RECOMMENDATIONS: int = 21600  # Recommendations: 6 hours
    CACHE_TTL_TRENDING_SEARCHES: int = 43200  # Trending searches: 12 hours
    
    # ── JWT Settings ────────────────────────────────────────────────
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ── Celery Settings ────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # ── Email Settings ────────────────────────────────────────────
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"
    SENDER_EMAIL: str = "noreply@jobspy.com"
    SENDER_NAME: str = "JobSpy"
    
    # ── External APIs ────────────────────────────────────────────
    LINKEDIN_API_KEY: str = ""
    INDEED_API_KEY: str = ""
    WUZZUF_API_KEY: str = ""
    BAYT_API_KEY: str = ""
    
    # ── CORS Settings ───────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # ── Logging Settings ────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # ── Rate Limiting ───────────────────────────────────────────
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # ── Pagination ──────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # ── Scraping Settings ───────────────────────────────────────
    SCRAPING_TIMEOUT: int = 30
    SCRAPING_RETRIES: int = 3
    SCRAPING_DELAY: int = 1
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
