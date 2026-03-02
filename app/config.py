"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "personal_finance_tracker"
    
    # JWT Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_days: int = 30

    @property
    def secret_key(self) -> str:
        return self.jwt_secret_key

    @property
    def algorithm(self) -> str:
        return self.jwt_algorithm

    @property
    def access_token_expire_minutes(self) -> int:
        return self.jwt_expiration_days * 24 * 60
    
    # Application Configuration
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
