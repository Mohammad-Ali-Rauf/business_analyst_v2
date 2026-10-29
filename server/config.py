"""Centralised runtime configuration.

All settings are read from environment variables (a local ``.env`` file is
loaded automatically) and have sensible defaults so the project runs both
inside Docker Compose and on a bare metal development machine.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# --- LLM -------------------------------------------------------------------
# Any OpenAI-compatible chat endpoint works; the defaults target OpenRouter.
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "google/gemini-3.8-flash")
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# Optional app attribution headers (used by OpenRouter rankings; harmless elsewhere).
LLM_EXTRA_HEADERS: dict[str, str] = {"X-Title": "Agile User Story Generator"}
if os.getenv("LLM_HTTP_REFERER"):
    LLM_EXTRA_HEADERS["HTTP-Referer"] = os.environ["LLM_HTTP_REFERER"]

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
