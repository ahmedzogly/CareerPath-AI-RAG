"""Create semantic embeddings locally with Sentence Transformers."""
from functools import lru_cache
from typing import List
from sentence_transformers import SentenceTransformer

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

@lru_cache(maxsize=1)
def get_embedding_model(model_name: str = DEFAULT_EMBEDDING_MODEL) -> SentenceTransformer:
    return SentenceTransformer(model_name)


def embed_texts(texts: List[str], model_name: str = DEFAULT_EMBEDDING_MODEL) -> List[List[float]]:
    model = get_embedding_model(model_name)
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=False).tolist()
