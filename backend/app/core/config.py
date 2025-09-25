"""
Application configuration using Pydantic settings
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    # Basic app config
    APP_NAME: str = "Integraite API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./integraite.db")
    
    # Security
    SECRET_KEY: str = Field(default="thiswillbechangedinproduction")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # CORS
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:5173", "https://api.integraite.pro", "https://integraite.pro", "https://www.integraite.pro"])
    
    # External APIs
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None)
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None)
    SENDGRID_API_KEY: Optional[str] = Field(default=None)
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379")
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None)
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None)
    MICROSOFT_CLIENT_ID: Optional[str] = Field(default=None)
    MICROSOFT_CLIENT_SECRET: Optional[str] = Field(default=None)
    
    # File uploads
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    UPLOAD_DIR: str = Field(default="uploads")
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100)
    RATE_LIMIT_WINDOW: int = Field(default=60)  # seconds
    
    # Multi-tenancy
    DEFAULT_ORGANIZATION_PLAN: str = Field(default="free")
    MAX_AGENTS_FREE_PLAN: int = Field(default=5)
    MAX_AGENTS_TEAM_PLAN: int = Field(default=50)


# Global settings instance
settings = Settings()
