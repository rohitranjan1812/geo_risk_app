"""
Application Configuration
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "GeoRisk API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs
    MAPBOX_API_KEY: str = ""
    USGS_API_ENDPOINT: str = "https://earthquake.usgs.gov/fdsnws/event/1/"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
