import time
import logfire
from app.config import settings
from langchain_huggingface import HuggingFaceEmbeddings

BATCH_SIZE = 50
_EMBED_DIM = 384
_FALLBACK_DIM = 384

_active_mode = None
_model_type = str | None = None

def _probe_hf():
    """Try one embed call to verify sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 is reachable. Returns model or None."""


def _load_fallback():
    return

def _init():
    return

def get_embedding_dim():
    """Returns the vector embedding dimension for the active model. Call after _init function"""
    return 

def embed_batch(batch: list[str]) -> list[list[float]]:
    return

def embed_query(query: str) -> list[float]:
    return 

def embed_texts(texts: list[str]) -> list[list[float]]:
    _init()

