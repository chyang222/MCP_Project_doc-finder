import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import config


def get_embedding(text: str) -> list[float]:
    if config.EMBEDDING_PROVIDER == "openai":
        return _openai_embedding(text)
    else:
        raise NotImplementedError(f"지원하지 않는 임베딩 provider: {config.EMBEDDING_PROVIDER}")


def _openai_embedding(text: str) -> list[float]:
    from openai import OpenAI

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text[:8000],  # 토큰 제한
    )
    return response.data[0].embedding
