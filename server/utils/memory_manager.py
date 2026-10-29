"""Session-scoped conversational memory backed by Qdrant.

Every request stores the user's feature description and the generated user
story document as vector points tagged with the caller's session token. The
last N exchanges are replayed into the prompt so follow-up requests can build
on earlier stories.
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from functools import lru_cache

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams

from config import (
    EMBEDDING_MODEL,
    EMBEDDING_SIZE,
    MEMORY_COLLECTION,
    MEMORY_TOP_K,
    QDRANT_URL,
)

logger = logging.getLogger(__name__)

_client = QdrantClient(url=QDRANT_URL)
_encoder_lock = threading.Lock()


@lru_cache(maxsize=1)
def _get_encoder():
    """Load the sentence-transformer lazily so startup stays fast."""
    # Imported lazily: loading the model allocates a few hundred MB of memory.
    from sentence_transformers import SentenceTransformer

    with _encoder_lock:
        logger.info("Loading embedding model %s", EMBEDDING_MODEL)
        return SentenceTransformer(EMBEDDING_MODEL)


def _ensure_collection() -> None:
    if _client.collection_exists(collection_name=MEMORY_COLLECTION):
        return
    logger.info("Creating Qdrant collection %s", MEMORY_COLLECTION)
    _client.create_collection(
        collection_name=MEMORY_COLLECTION,
        vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
    )


def _embed(text: str) -> list[float]:
    return _get_encoder().encode(text, normalize_embeddings=True).tolist()


def save_memory_for_token(token: str, text: str, role: str = "user") -> None:
    """Persist a single memory entry for the given session token."""
    if not text.strip():
        return

    try:
        _ensure_collection()
        point = models.PointStruct(
            id=str(uuid.uuid4()),
            vector=_embed(text),
            payload={
                "token": token,
                "role": role,
                "timestamp": int(time.time()),
                "text": text,
            },
        )
        _client.upload_points(
            collection_name=MEMORY_COLLECTION,
            points=[point],
            wait=True,
        )
    except Exception:
        # Memory is a best-effort enhancement: never fail the request because
        # the vector store is unavailable.
        logger.exception("Failed to persist memory for session %s", token)


def get_last_n_memories(token: str, n: int = MEMORY_TOP_K) -> list[str]:
    """Return the most recent memories for a session, oldest first."""
    try:
        _ensure_collection()
        scroll_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="token",
                    match=models.MatchValue(value=token),
                )
            ]
        )

        points, _ = _client.scroll(
            collection_name=MEMORY_COLLECTION,
            scroll_filter=scroll_filter,
            limit=200,
        )
        if not points:
            return []

        points.sort(key=lambda p: p.payload.get("timestamp", 0))
        latest = points[-n:]

        lines = []
        for point in latest:
            payload = point.payload or {}
            role = "User" if payload.get("role") != "assistant" else "Assistant"
            lines.append(f"{role}: {payload.get('text', '')}")
        return lines

    except Exception:
        logger.exception("Failed to fetch memories for session %s", token)
        return []


def clear_memories_for_token(token: str) -> None:
    """Forget everything stored for a session token."""
    try:
        _client.delete(
            collection_name=MEMORY_COLLECTION,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="token",
                            match=models.MatchValue(value=token),
                        )
                    ]
                )
            ),
        )
    except Exception:
        logger.exception("Failed to clear memories for session %s", token)
