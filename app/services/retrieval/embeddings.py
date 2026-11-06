import time
import logfire
from app.config import settings
from langchain_huggingface import HuggingFaceEmbeddings

BATCH_SIZE = 50
_EMBED_DIM = 384
_FALLBACK_DIM = 768

_active_model = None
_model_type: str | None = None

def _probe_sentence_transformer():
    """Try one embed call to verify sentence-transformers/all-MiniLM-L6-v2 is reachable. Returns model or None."""
    try:
        logfire.info("Attempting to load HuggingFaceEmbeddings (all-MiniLM-L6-v2)...")
        model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        logfire.info("Model loaded. Performing probe query...")
        query = "What is capital of France?"
        query_vector = model.embed_query(query)

        documents = [
            "Paris is the capital of France.",
            "The capital of Germany is Berlin.",
            "London is the capital of the UK."
        ]
        doc_vectors = model.embed_documents(documents)

        logfire.info("All MiniLM L6 V2 model is ready (384-dim)")
        return model 
        
    except Exception as e:
        logfire.warning(f"All MiniLM L6 V2 failed: {e}. Will use another sentence-transformer fallback")
        return None



def _load_fallback():
    from sentence_transformers import SentenceTransformer
    logfire.info("Loading sentence-transformer fallback (all-mpnet-base-v2, 768-dim).")
    return SentenceTransformer("all-mpnet-base-v2")

def _init():
    global _active_model, _model_type

    if _active_model is not None:
        return

    model = _probe_sentence_transformer()

    if model:
        _active_model = model
        _model_type = "main-sentence-transformer"
    else:
        _active_model = _load_fallback()
        _model_type = "fallback"

def get_embedding_dim():
    """Returns the vector embedding dimension for the active model. Call after _init function"""
    _init()
    return _EMBED_DIM if _model_type == "main-sentence-transformer" else _FALLBACK_DIM

def _embed_batch(batch: list[str]) -> list[list[float]]:
    if _model_type == "main-sentence-transformer":
        for attempt in range(4):
            try:
                return _active_model.embed_documents(batch)
            except Exception as e:
                err = str(e).lower()
                is_rate_limit = any(x in err for x in ("429","rate","quota","resource_exhausted"))
                if is_rate_limit and attempt < 3:
                    wait = 2 ** attempt
                    logfire.warning(
                        f"Main embedding model is rate limited - retrying in {wait}s"
                        f"(attempt {attempt + 1}/4)."
                    )
                    time.sleep(wait)
                else:
                    logfire.error(f"Main Embedding failed: {e}")
                    raise
        raise RuntimeError("Main Embedding model is rate limited and still persisted after 4 attempts.")
    else:
        return _active_model.encode(batch, show_progress_bar=False).tolist()


def embed_query(query: str) -> list[float]:
    _init()
    if _model_type == "main-sentence-transformer":
        return _active_model.embed_query(query)
    return _active_model.encode([query])[0].tolist()

def embed_texts(texts: list[str]) -> list[list[float]]:
    _init()
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        with logfire.span("Embed batch", model=_model_type, start=i, size=len(batch)):
            all_embeddings.extend(_embed_batch(batch))
    return all_embeddings
