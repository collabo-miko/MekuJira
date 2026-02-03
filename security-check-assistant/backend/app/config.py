"""Application configuration."""
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI API Key (required for self-hosted PageIndex)
    openai_api_key: str = ""

    # PageIndex settings (self-hosted)
    pageindex_model: str = "gpt-4o-2024-11-20"
    pageindex_max_pages_per_node: int = 10
    pageindex_max_tokens_per_node: int = 20000

    # PageIndex cloud API (optional, for backward compatibility)
    pageindex_api_key: str = ""
    pageindex_use_cloud: bool = False

    # Confidence thresholds
    confidence_strict: float = 0.95
    confidence_moderate: float = 0.85
    confidence_standard: float = 0.70
    default_confidence_threshold: float = 0.70

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/knowledge.db"

    # File paths
    data_dir: Path = Path("./data")
    documents_dir: Path = Path("./data/documents")
    uploads_dir: Path = Path("./data/uploads")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
