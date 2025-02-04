from pathlib import Path
from typing import Final

from pydantic import BaseModel


class Settings(BaseModel):
    # App settings
    APP_NAME: Final[str] = "Philippine Zipcodes"
    VERSION: Final[str] = "1.0.0"
    DEBUG: bool = True

    # Security settings
    ALLOWED_HOSTS: list[str] = ["*"]

    # Path settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    STATIC_DIR: Path = BASE_DIR / "static"

    # API settings
    SEARCH_DELAY_MS: Final[int] = 300
    CACHE_TTL: Final[int] = 3600
    CACHE_ENABLED: bool = True

    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


settings = Settings()
