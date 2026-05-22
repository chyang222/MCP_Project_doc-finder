from pathlib import Path
from typing import Generator


def extract_chunks(file_path: str) -> Generator[dict, None, None]:
    """파일에서 페이지/슬라이드별 텍스트 청크를 추출합니다."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pptx":
        yield from _extract_pptx(path)
    elif suffix == ".pdf":
        yield from _extract_pdf(path)
    elif suffix == ".docx":
        yield from _extract_docx(path)
    else:
        raise ValueError(f"지원하지 않는 파일 형식: {suffix}")


def _extract_pptx(path: Path) -> Generator[dict, None, None]:
    from pptx import Presentation

    prs = Presentation(str(path))
    for slide_num, slide in enumerate(prs.slides, start=1):
        texts = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    line = para.text.strip()
                    if line:
                        texts.append(line)

        # 슬라이드 노트
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            if notes:
                texts.append(f"[노트] {notes}")

        if texts:
            yield {
                "page": slide_num,
                "text": "\n".join(texts),
                "page_label": f"슬라이드 {slide_num}",
            }


def _extract_pdf(path: Path) -> Generator[dict, None, None]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            yield {
                "page": page_num,
                "text": text,
                "page_label": f"{page_num}페이지",
            }


def _extract_docx(path: Path) -> Generator[dict, None, None]:
    from docx import Document

    doc = Document(str(path))
    chunk_texts = []
    chunk_num = 1
    char_count = 0
    CHARS_PER_CHUNK = 1000

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        chunk_texts.append(text)
        char_count += len(text)

        if char_count >= CHARS_PER_CHUNK:
            yield {
                "page": chunk_num,
                "text": "\n".join(chunk_texts),
                "page_label": f"섹션 {chunk_num}",
            }
            chunk_num += 1
            chunk_texts = []
            char_count = 0

    if chunk_texts:
        yield {
            "page": chunk_num,
            "text": "\n".join(chunk_texts),
            "page_label": f"섹션 {chunk_num}",
        }
