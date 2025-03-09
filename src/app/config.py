from pathlib import Path
from typing import Final

from pydantic import BaseModel


class Settings(BaseModel):
    # App settings
    APP_NAME: Final[str] = "Philippine Zipcodes"
    VERSION: Final[str] = "1.0.0"

    # Security settings
    ALLOWED_HOSTS: list[str] = [""]
    CORS_ORIGINS: list[str] = ["*"]
    SECURITY_HEADERS: dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "interest-cohort=()",
        "Content-Security-Policy": "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'",
    }

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
