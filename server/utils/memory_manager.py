from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams, CollectionStatus
from langchain_community.embeddings import HuggingFaceEmbeddings 
import time
import uuid
from dotenv import load_dotenv

load_dotenv()

qdrant_client = QdrantClient(host="localhost", port=6333)

def ensure_collection(client: QdrantClient, name: str, vector_size: int = 384):
    # Check if collection exists
    try:
        info = client.get_collection(name)
        if info.config.params.vectors.size != vector_size:
            print("Vector size mismatch. Updating is not supported — please handle manually.")
    except Exception:
        client.recreate_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            ),
        )

collection_name = "user_memory"
ensure_collection(qdrant_client, collection_name)

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def save_memory_for_token(token: str, text: str):
    vector = embedding.embed_query(text)  # get embedding vector
    point_id = str(uuid.uuid4())
    
    point = models.PointStruct(
        id=point_id,
        vector=vector,
        payload={
            "token": token,
            "timestamp": int(time.time()),
            "text": text
        }
    )
    
    qdrant_client.upload_points(
        collection_name=collection_name,
        points=[point],
        wait=True
    )


def get_last_n_memories(token: str, n=5):
    filter_ = models.Filter(
        must=[
            models.FieldCondition(
                key="token",
                match=models.MatchValue(value=token)
            )
        ]
    )

    try:
        points, _ = qdrant_client.scroll(
            collection_name=collection_name,
            scroll_filter=filter_,
            limit=100
        )

        if not points:
            return []

        sorted_points = sorted(
            points,
            key=lambda p: p.payload.get("timestamp", 0),
            reverse=True
        )[:n]
        sorted_points.reverse()

        return [p.payload.get("text", "") for p in sorted_points]

    except Exception as e:
        print(f"[memory_manager] Error fetching memories: {e}")
        return []