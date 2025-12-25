"""Application configuration management."""
import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Database Query Tool"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Alternative frontend port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # Database
    sqlite_path: Path = Path.home() / ".db_query" / "db_query.db"
    
    # OpenAI (for NL2SQL)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    
    # Encryption
    encryption_key_path: Path = Path.home() / ".db_query" / "secret.key"
    
    # Query limits
    max_query_result_rows: int = 1000
    metadata_cache_ttl_hours: int = 1
    query_history_limit: int = 50
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    def validate_openai_key(self) -> None:
        """Validate OpenAI API key is set for NL2SQL features."""
        if not self.openai_api_key:
            raise ValueError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY environment variable to use NL2SQL features."
            )


# Global settings instance
settings = Settings()
