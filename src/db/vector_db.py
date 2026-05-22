import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import config

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        import chromadb

        _client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
        _collection = _client.get_or_create_collection(
            name=config.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_chunks(chunks: list[dict]) -> list[str]:
    """임베딩과 함께 청크를 저장합니다. chroma_id 리스트를 반환합니다."""
    collection = _get_collection()
    ids = [str(uuid.uuid4()) for _ in chunks]

    collection.add(
        ids=ids,
        embeddings=[c["embedding"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{"file_path": c["file_path"], "page": c["page"]} for c in chunks],
    )
    return ids


def delete_chunks(chroma_ids: list[str]):
    if not chroma_ids:
        return
    collection = _get_collection()
    collection.delete(ids=chroma_ids)


def search(query_embedding: list[float], top_k: int = 5) -> list[dict]:
    collection = _get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    ids = results["ids"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    for chroma_id, distance, metadata in zip(ids, distances, metadatas):
        hits.append({
            "chroma_id": chroma_id,
            "score": round(1 - distance, 4),  # cosine: 거리 → 유사도
            "file_path": metadata["file_path"],
            "page": metadata["page"],
        })
    return hits
