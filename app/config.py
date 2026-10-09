"""Configuration management for TraceLens."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Config:
    """TraceLens configuration from environment variables."""

    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not set. Please configure .env file with your Gemini API key."
        )

    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Embedding Model
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "384"))

    # Retrieval Configuration
    TOP_K: int = int(os.getenv("TOP_K", "10"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def setup_logging(cls) -> None:
        """Configure logging based on settings."""
        logging.basicConfig(
            level=cls.LOG_LEVEL,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


# Initialize logging
Config.setup_logging()
