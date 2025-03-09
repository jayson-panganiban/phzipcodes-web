import os
from pathlib import Path
from typing import Final

from pydantic import BaseModel

# Simple environment detection
is_development = os.getenv("APP_ENV", "").lower() in ("dev", "development", "testing")


# Base configuration class
class Settings(BaseModel):
    # App settings
    APP_NAME: Final[str] = "Philippine Zipcodes"
    VERSION: Final[str] = "1.0.0"

    # Security settings - conditionally include localhost
    ALLOWED_HOSTS: list[str] = (
        ["phzipcodes.com", "www.phzipcodes.com", "localhost", "127.0.0.1"]
        if is_development
        else ["phzipcodes.com", "www.phzipcodes.com"]
    )

    CORS_ORIGINS: list[str] = (
        [
            "https://phzipcodes.com",
            "https://www.phzipcodes.com",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
        if is_development
        else ["https://phzipcodes.com", "https://www.phzipcodes.com"]
    )

    # Simplify security headers conditionally
    SECURITY_HEADERS: dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=(), interest-cohort=()",
        # Relaxed CSP for development, stricter for production
        "Content-Security-Policy": (
            "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'"
            if is_development
            else "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self'; font-src 'self'; connect-src 'self'"
        ),
    }

    # Add HSTS only in production
    if not is_development:
        SECURITY_HEADERS["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

    # Path settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    STATIC_DIR: Path = BASE_DIR / "static"

    # API settings
    SEARCH_DELAY_MS: Final[int] = 300
    CACHE_TTL: Final[int] = 3600
    CACHE_ENABLED: bool = True

    model_config = {"arbitrary_types_allowed": True, "frozen": True}


settings = Settings()
