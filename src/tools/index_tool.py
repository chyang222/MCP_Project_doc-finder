import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import config
from src.db import sqlite_db, vector_db
from src.indexer.extractor import extract_chunks
from src.indexer.embedder import get_embedding


async def index_documents(folder_path: str | None = None) -> str:
    folder = Path(folder_path) if folder_path else Path(config.WATCH_FOLDER)

    if not folder.exists():
        return f"폴더를 찾을 수 없습니다: {folder}"

    sqlite_db.init_db()

    files = [
        f for f in folder.rglob("*")
        if f.is_file() and f.suffix.lower() in config.SUPPORTED_EXTENSIONS
    ]

    if not files:
        return f"지원 파일 없음 (pptx/pdf/docx): {folder}"

    new_count = 0
    updated_count = 0
    skipped_count = 0
    errors = []

    for file_path in files:
        try:
            last_modified = file_path.stat().st_mtime
            existing = sqlite_db.get_file_record(str(file_path))

            if existing and existing["last_modified"] >= last_modified:
                skipped_count += 1
                continue

            # 기존 청크 삭제
            is_update = existing is not None
            if is_update:
                old_chroma_ids = sqlite_db.delete_chunks_by_file(existing["id"])
                vector_db.delete_chunks(old_chroma_ids)

            # 텍스트 추출
            page_chunks = list(extract_chunks(str(file_path)))
            if not page_chunks:
                continue

            # 임베딩 생성 및 벡터 저장
            chunks_with_embedding = []
            for chunk in page_chunks:
                embedding = get_embedding(chunk["text"])
                chunks_with_embedding.append({
                    **chunk,
                    "embedding": embedding,
                    "file_path": str(file_path),
                })

            chroma_ids = vector_db.add_chunks(chunks_with_embedding)

            # 메타 DB 저장
            file_id = sqlite_db.upsert_file(
                file_path=str(file_path),
                file_name=file_path.name,
                extension=file_path.suffix.lower(),
                last_modified=last_modified,
                total_pages=len(page_chunks),
            )
            sqlite_db.insert_chunks(
                file_id=file_id,
                chunks=[
                    {
                        "page": c["page"],
                        "page_label": c["page_label"],
                        "text": c["text"],
                        "chroma_id": chroma_id,
                    }
                    for c, chroma_id in zip(page_chunks, chroma_ids)
                ],
            )

            if is_update:
                updated_count += 1
            else:
                new_count += 1

        except Exception as e:
            errors.append(f"{file_path.name}: {e}")

    lines = [
        f"인덱싱 완료 - 폴더: {folder}",
        f"  신규: {new_count}개 | 업데이트: {updated_count}개 | 스킵(변경없음): {skipped_count}개",
    ]
    if errors:
        lines.append(f"  오류 {len(errors)}건:")
        lines.extend(f"    - {e}" for e in errors)

    return "\n".join(lines)
