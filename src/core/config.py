from typing import Any, Dict, Optional, List
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator, field_validator
from pathlib import Path
import os
import json


class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str
    VERSION: str
    API_V1_STR: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Admin credentials
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    # Database
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    DB_ECHO: bool = False

    # Application
    APP_HOST: str
    APP_PORT: int

    # CORS
    BACKEND_CORS_ORIGINS: List[str]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return json.loads(v)
        return v

    @property
    def get_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"  # Allow extra fields in environment variables

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = self.get_database_url


settings = Settings()
