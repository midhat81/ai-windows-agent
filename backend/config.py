"""
Backend Configuration
Settings for API, LLM, and executor
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # CORS Settings
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # LLM Settings
    LLM_MODEL: str = "llama3.2:3b"
    OLLAMA_HOST: str = "http://localhost:11434"
    
    # Executor Settings
    DEFAULT_DRY_RUN: bool = False
    REQUIRE_CONFIRMATION: bool = True
    
    # History Settings
    MAX_HISTORY_SIZE: int = 1000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()