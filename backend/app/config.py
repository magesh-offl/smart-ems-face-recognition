"""Application Configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # MongoDB
    MONGO_DB_URL: str = "mongodb://127.0.0.1:27017"
    MONGO_DB_NAME: str = "smart_ems_db"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_ENV: str = "development"
    
    # JWT Configuration (set real value in .env)
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # API Key (set real value in .env)
    API_KEY: str = "change-me-in-production"
    
    # Super Admin Configuration
    SUPER_ADMIN_EMAIL: str = "superadmin@ems.com"
    SUPER_ADMIN_PASSWORD: str = ""  # Empty means generate random
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
