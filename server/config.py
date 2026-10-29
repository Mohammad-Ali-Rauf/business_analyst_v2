"""Centralised runtime configuration.

All settings are read from environment variables (a local ``.env`` file is
loaded automatically) and have sensible defaults so the project runs both
inside Docker Compose and on a bare metal development machine.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# --- LLM -------------------------------------------------------------------
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# --- Speech to text --------------------------------------------------------
WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
MAX_AUDIO_BYTES: int = int(os.getenv("MAX_AUDIO_BYTES", str(25 * 1024 * 1024)))

# --- Vector memory ---------------------------------------------------------
QDRANT_URL: str = os.getenv("QDRANT_URL", "http://qdrant:6333")
MEMORY_COLLECTION: str = os.getenv("MEMORY_COLLECTION", "user_memory")
MEMORY_TOP_K: int = int(os.getenv("MEMORY_TOP_K", "5"))
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_SIZE: int = int(os.getenv("EMBEDDING_SIZE", "384"))

# --- API -------------------------------------------------------------------
ALLOWED_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]
