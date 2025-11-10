"""Application configuration management."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./georisk.db"
    database_url_sync: str = "sqlite:///./georisk.db"
    
    # Secret key for session management
    secret_key: str = "change-this-in-production-minimum-32-characters"
    debug: bool = False
    
    # CORS
    backend_cors_origins: str = '["http://localhost:3000","http://localhost"]'
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(self.backend_cors_origins, str):
            import json
            try:
                return json.loads(self.backend_cors_origins)
            except json.JSONDecodeError:
                return [self.backend_cors_origins]
        return self.backend_cors_origins
    
    # Application
    environment: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api"
    
    # Application metadata
    app_name: str = "Geo Risk Assessment API"
    app_version: str = "1.0.0"
    

settings = Settings()
