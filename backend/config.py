import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./app.db"

    # AI Foundry Agent
    ai_foundry_agent_id: str = ""  # Agent ID for quiz generation
    ai_foundry_agent_id_feedback: str = ""  # Agent ID for feedback generation

    # Dataverse (if needed)
    dataverse_api_url: str = Field(default="", env="DATAVERSE_API_URL")
    dataverse_access_token: str = Field(default="", env="DATAVERSE_ACCESS_TOKEN")
    client_id: str = Field(default="", env="CLIENT_ID")
    client_secret: str = Field(default="", env="CLIENT_SECRET")
    tenant_id: str = Field(default="", env="TENANT_ID")
    dataverse_username: str = Field(default="", env="DATAVERSE_USERNAME")
    dataverse_password: str = Field(default="", env="DATAVERSE_PASSWORD")

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
        extra = "ignore"  # 추가 필드 무시


# Global settings instance
settings = Settings()