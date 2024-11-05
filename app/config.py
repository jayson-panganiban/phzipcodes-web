from pathlib import Path
from typing import List

from pydantic import BaseModel, Field


class Settings(BaseModel):
    # App settings
    APP_NAME: str = "Philippine Zipcodes"
    DEBUG: bool = True
    API_VERSION: str = "1.0.0"

    # Security settings
    ALLOWED_HOSTS: List[str] = Field(default=["*"])

    # Path settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    STATIC_DIR: Path = BASE_DIR / "static"

    # API settings
    SEARCH_DELAY_MS: int = 300

    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    model_config = {"case_sensitive": True, "env_file": ".env", "extra": "ignore"}


settings = Settings()
