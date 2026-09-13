import faiss
import json
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from huggingface_hub import snapshot_download
from app.config import settings

class RAGService:
    def __init__(self):
        self.index = None
        self.sentences = None
        self.embedder = None

    def load(self):
        self.embedder = SentenceTransformer("sentence-transformers/LaBSE")
        local_dir = Path(__file__).resolve().parent.parent.parent / "data" / "rag_knowledge_base"
        
        index_file = local_dir / "shona_labse.index"
        sentences_file = local_dir / "sentences.json"

        if index_file.exists() and sentences_file.exists():
            self.index = faiss.read_index(str(index_file))
            with open(sentences_file, "r", encoding="utf-8") as f:
                self.sentences = json.load(f)
            return

        cache_dir = "/tmp/ruzivo_rag"
        os.makedirs(cache_dir, exist_ok=True)
        try:
            snapshot_download(
                repo_id=settings.RAG_DATASET_ID,
                repo_type="dataset",
                local_dir=cache_dir,
                token=settings.HF_TOKEN
            )
            self.index = faiss.read_index(f"{cache_dir}/shona_labse.index")
            with open(f"{cache_dir}/sentences.json", "r", encoding="utf-8") as f:
                self.sentences = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load remote RAG index: {e}")
            self.sentences = []
            self.index = None

    def retrieve(self, query: str, top_k: int = 5) -> str:
        if not self.index or not self.sentences or not self.embedder:
            return ""

        query_embedding = self.embedder.encode(
            [query], normalize_embeddings=True
        ).astype("float32")
        scores, indices = self.index.search(query_embedding, top_k)
        results = [
            self.sentences[idx]
            for i, idx in enumerate(indices[0])
            if idx < len(self.sentences) and scores[0][i] > 0.4
        ]
        return "\n".join(results) if results else ""

rag_service = RAGService()
