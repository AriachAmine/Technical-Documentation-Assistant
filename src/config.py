"""
Configuration management for the Technical Documentation Assistant.
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = Field(default="Technical Documentation Assistant", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")

    # API
    api_host: str = Field(default="127.0.0.1", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")

    # Groq API
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", env="GROQ_MODEL")
    temperature: float = Field(default=0.1, env="TEMPERATURE")
    max_completion_tokens: int = Field(default=2000, env="MAX_COMPLETION_TOKENS")

    # Vector Database
    chroma_persist_directory: str = Field(default="./chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")

    # Processing
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    max_tokens: int = Field(default=4000, env="MAX_TOKENS")

    # Supported file types
    supported_extensions: List[str] = [
        ".md", ".markdown", ".html", ".htm", ".pdf", ".txt", ".json", ".yaml", ".yml"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
