import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./app.db"

    # AI Foundry Agent
    ai_foundry_agent_id: str = ""  # Agent ID for quiz generation
    ai_foundry_agent_id_feedback: str = ""  # Agent ID for feedback generation

    # Environment
    environment: str = "development"

    # FastAPI
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()