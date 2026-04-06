import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_PATH       = "data/faiss.index"
META_PATH        = "data/faiss_meta.json"

# ── Singleton model loader ─────────────────────────────────────
_embed_model = None

def get_embed_model() -> SentenceTransformer:
    """
    Load embedding model once and reuse.
    First call downloads ~90MB — cached locally after that.
    """
    global _embed_model
    if _embed_model is None:
        print(f"Loading embedding model: {EMBED_MODEL_NAME}...")
        _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
        print("Embedding model ready")
    return _embed_model


def get_embedding(text: str) -> np.ndarray:
    """Get normalized embedding for a single text string."""
    model  = get_embed_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.astype("float32")


def get_embeddings_batch(texts: list) -> np.ndarray:
    """Get embeddings for a list of texts — faster than one by one."""
    model   = get_embed_model()
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )
    return vectors.astype("float32")


def build_vector_store(documents: list) -> None:
    """
    Build FAISS index from a list of document dicts.
    Each document must have 'title' and 'content' keys.
    """
    os.makedirs("data", exist_ok=True)

    texts = [f"{d['title']}\n{d['content']}" for d in documents]

    print(f"Generating embeddings for {len(texts)} documents...")
    matrix = get_embeddings_batch(texts)

    # Inner product on L2-normalized vectors = cosine similarity
    dim   = matrix.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(matrix)

    # Save index and metadata
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    print(f"FAISS index built: {len(documents)} documents | dim={dim}")


def search_vector_store(query: str, k: int = 3) -> list:
    """
    Semantic search — returns top-k most relevant documents.
    """
    if not os.path.exists(INDEX_PATH):
        print("FAISS index not found — building now...")
        ensure_index_exists()

    index = faiss.read_index(INDEX_PATH)

    with open(META_PATH, encoding="utf-8") as f:
        metadata = json.load(f)

    q_vector = get_embedding(query).reshape(1, -1)
    scores, indices = index.search(q_vector, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if 0 <= idx < len(metadata):
            doc = metadata[idx].copy()
            doc["relevance_score"] = round(float(score), 4)
            results.append(doc)

    return results


def ensure_index_exists() -> None:
    """Auto-build FAISS index from RAG documents if missing."""
    if not os.path.exists(INDEX_PATH):
        rag_path = "data/rag_documents.json"
        if not os.path.exists(rag_path):
            print("RAG documents not found. Run: python data/generate_data.py")
            return
        with open(rag_path, encoding="utf-8") as f:
            docs = json.load(f)
        build_vector_store(docs)


def rebuild_index() -> None:
    """Force rebuild — useful when documents are updated."""
    if os.path.exists(INDEX_PATH):
        os.remove(INDEX_PATH)
    if os.path.exists(META_PATH):
        os.remove(META_PATH)
    ensure_index_exists()