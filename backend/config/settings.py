"""
Application settings and configuration management.
Uses environment variables for configuration.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, ClassVar
from pathlib import Path
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Load .env from repository root and/or backend directory for flexible local runs.
    env_path: ClassVar[Path] = Path(__file__).resolve().parents[2] / ".env"
    model_config = ConfigDict(env_file=str(env_path), case_sensitive=False, protected_namespaces=())

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False

    # OpenAI Configuration
    openai_api_key: str
    model_name: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-3-small"

    # MongoDB Configuration
    mongo_uri: str = "mongodb://localhost:27017/ai_chatbot"
    mongo_db_name: str = "ai_chatbot"

    # CORS Configuration
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # LLM Configuration
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9

    # Vector Database Configuration
    vector_db_type: str = "chroma"
    embed_dim: int = 1536
    chroma_db_path: str = "./data/chroma_db"

    # RAG Configuration
    pdf_upload_dir: str = "./uploads"
    rag_chunk_size: int = 1024
    rag_chunk_overlap: int = 128

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Create global settings instance
settings = Settings()
