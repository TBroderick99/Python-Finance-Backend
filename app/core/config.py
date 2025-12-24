"""
Application configuration settings using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    APP_NAME: str = "Stock Market Finance App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./stock_market.db"
    
    # API Keys (for external stock data providers)
    ALPHA_VANTAGE_API_KEY: str = ""
    YAHOO_FINANCE_ENABLED: bool = True
    
    # CORS settings
    CORS_ORIGINS: list[str] = ["http://localhost:8501", "http://127.0.0.1:8501"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
