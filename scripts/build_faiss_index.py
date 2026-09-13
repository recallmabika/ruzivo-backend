"""
Ruzivo AI — Build FAISS Index for Shona RAG
===========================================
Generates a FAISS index using SentenceTransformer (LaBSE) over all
14,201 cleaned Shona educational sentences (Mipanda, Nyaudzosingwi, Tsumo).

Usage:
    python scripts/build_faiss_index.py
"""

import json
import sys
from pathlib import Path
import numpy as np

# Configure console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(r"c:\Users\recal\Desktop\Level 2.2 Project\ruzivo")
KB_DIR = PROJECT_ROOT / "data" / "rag_knowledge_base"
SENTENCES_FILE = KB_DIR / "sentences.json"
INDEX_OUT = KB_DIR / "shona_labse.index"


def build_index():
    try:
        import faiss
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install: pip install faiss-cpu sentence-transformers")
        return

    if not SENTENCES_FILE.exists():
        print(f"Error: {SENTENCES_FILE} does not exist. Run build_instruction_rag_corpus.py first.")
        return

    print("=" * 60)
    print("  RUZIVO AI — FAISS VECTOR INDEX BUILDER (LaBSE)")
    print("=" * 60)

    with open(SENTENCES_FILE, "r", encoding="utf-8") as f:
        sentences = json.load(f)

    print(f"Loaded {len(sentences):,} sentences from {SENTENCES_FILE.name}")
    print("Loading embedding model: sentence-transformers/LaBSE...")
    embedder = SentenceTransformer("sentence-transformers/LaBSE")

    print(f"Encoding {len(sentences):,} sentences (this may take a few minutes on CPU)...")
    embeddings = embedder.encode(
        sentences,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True
    ).astype("float32")

    dim = embeddings.shape[1]
    print(f"Embedding dimension: {dim}")

    # Inner Product on normalized vectors = Cosine Similarity
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_OUT))
    print(f"✅ Successfully saved FAISS index to: {INDEX_OUT} ({INDEX_OUT.stat().st_size / (1024 * 1024):.2f} MB)")
    print("=" * 60)


if __name__ == "__main__":
    build_index()
