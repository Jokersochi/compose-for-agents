import os
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams, OptimizersConfigDiff

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
KNOWLEDGE_BASE_COLLECTION = "sochi_knowledge_base"

async def get_qdrant_client() -> AsyncQdrantClient:
    return AsyncQdrantClient(url=QDRANT_URL)

async def init_qdrant_collection():
    client = await get_qdrant_client()
    try:
        # Check if collection exists
        await client.get_collection(KNOWLEDGE_BASE_COLLECTION)
        print(f"Collection {KNOWLEDGE_BASE_COLLECTION} already exists.")
    except Exception:
        # Create collection if it doesn't exist.
        # Assuming OpenAI text-embedding-3-small (dim=1536) for embeddings
        await client.create_collection(
            collection_name=KNOWLEDGE_BASE_COLLECTION,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            optimizers_config=OptimizersConfigDiff(indexing_threshold=0) # Optimize after upload
        )
        print(f"Collection {KNOWLEDGE_BASE_COLLECTION} created.")
