import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.db import sqlite_db, vector_db
from src.indexer.embedder import get_embedding


async def search_documents(query: str, top_k: int = 5) -> str:
    sqlite_db.init_db()

    query_embedding = get_embedding(query)
    hits = vector_db.search(query_embedding, top_k=top_k)

    if not hits:
        return "관련 문서를 찾지 못했습니다. 먼저 index_documents를 실행해주세요."

    lines = [f'"{query}" 검색 결과 (상위 {len(hits)}건)\n']

    for rank, hit in enumerate(hits, start=1):
        meta = sqlite_db.get_chunk_by_chroma_id(hit["chroma_id"])
        if not meta:
            continue

        lines.append(
            f"{rank}. [{meta['file_name']}] {meta['page_label']} "
            f"(유사도: {hit['score']:.2%})"
        )
        lines.append(f"   경로: {meta['file_path']}")
        preview = meta["text"][:150].replace("\n", " ")
        lines.append(f"   내용 미리보기: {preview}...")
        lines.append("")

    return "\n".join(lines)
