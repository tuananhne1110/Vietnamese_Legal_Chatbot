import logging
from typing import Optional

from qdrant_client import QdrantClient

from backend.configs.settings import settings

logger = logging.getLogger(__name__)

# Setup Qdrant client from settings
def _setup_qdrant_client():
    qdrant_config = settings.retrieval_settings.qdrant_config
    if qdrant_config.qdrant_url:
        return QdrantClient(url=qdrant_config.qdrant_url, api_key=qdrant_config.qdrant_api_key)
    else:
        return QdrantClient(host=qdrant_config.qdrant_host, port=qdrant_config.qdrant_port)

qdrant_client = _setup_qdrant_client()


def search_qdrant(collection_name, query_embedding, query, limit=5):
    print("###" + query + "###")

    # Simplified: Only use vector search without filtering
    try:
        vector_search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True
        )
        if hasattr(vector_search_results, 'points'):
            return vector_search_results.points
        else:
            return vector_search_results
    except Exception as e:
        print(f"Error in vector search: {e}")
        return []


def search_qdrant_by_id(collection_name, doc_id, limit=1):
    """Truy vấn Qdrant lấy các chunk theo id."""
    filter_condition = {
        "must": [
            {"key": "id", "match": {"value": doc_id}}
        ]
    }
    results, _ = qdrant_client.scroll(
        collection_name=collection_name,
        scroll_filter=filter_condition,
        limit=limit,
        with_payload=True,
        with_vectors=False
    )
    return results
