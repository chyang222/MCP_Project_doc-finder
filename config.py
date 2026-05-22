import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "db"
CHROMA_DIR = DATA_DIR / "chroma"

DB_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

SQLITE_PATH = str(DB_DIR / "metadata.db")
CHROMA_COLLECTION = "doc_finder"

# 인덱싱할 폴더 경로 (환경변수 or 기본값)
WATCH_FOLDER = os.environ.get("DOC_FINDER_FOLDER", str(Path.home() / "Documents"))

SUPPORTED_EXTENSIONS = {".pptx", ".pdf", ".docx"}

# 임베딩 모델 (Claude or OpenAI)
EMBEDDING_PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "openai")  # "openai" | "claude"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
