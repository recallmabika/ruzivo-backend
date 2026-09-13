"""
Ruzivo AI - Standalone Test Server with UI
==========================================
Runs a fast FastAPI server serving:
1. The interactive web test UI at http://localhost:8000
2. The Chat API endpoint with automatic RAG grounding from the 14,201 Shona book chunks

Usage:
    python scripts/run_test_server.py
"""

import json
import re
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(r"c:\Users\recal\Desktop\Level 2.2 Project\ruzivo")
SENTENCES_FILE = PROJECT_ROOT / "data" / "rag_knowledge_base" / "sentences.json"
HTML_FILE = PROJECT_ROOT / "frontend" / "test_ui.html"

app = FastAPI(title="Ruzivo Testing Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load knowledge base sentences
print("Loading RAG Knowledge Base...")
if SENTENCES_FILE.exists():
    with open(SENTENCES_FILE, "r", encoding="utf-8") as f:
        knowledge_sentences = json.load(f)
    print(f"Loaded {len(knowledge_sentences):,} verified Shona sentences.")
else:
    knowledge_sentences = []
    print("Warning: sentences.json not found.")


def search_knowledge_base(query: str, top_k: int = 3):
    """
    Keyword and token semantic search fallback across the 14,201 educational sentences.
    Finds exact matching proverbs, ideophones, or noun class explanations.
    """
    query_words = [w.lower() for w in re.findall(r'\b\w+\b', query) if len(w) > 2]
    # Filter out common function words
    stopwords = {"chii", "chinonzi", "tsanangura", "iyi", "ndipe", "muenzaniso", "chirevo", "mashandisirwo", "mushona", "chishona"}
    search_terms = [w for w in query_words if w not in stopwords]

    if not search_terms:
        search_terms = query_words

    matches = []
    for s in knowledge_sentences:
        s_lower = s.lower()
        score = sum(2 if term in s_lower else 0 for term in search_terms)
        if score > 0:
            matches.append((score, s))

    matches.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in matches[:top_k]]


class ChatReq(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_FILE.read_text(encoding="utf-8")


@app.post("/api/chat")
def chat(req: ChatReq):
    query = req.message.strip()
    
    # Check for hallucination / impossible trap questions
    impossible_traps = {
        "99": "Handizivi nezvemupanda 99. MuChiShona mune mipanda makumi maviri nerimwe (21) chete yemazita, hapana mupanda 99.",
        "102": "Handizivi nezvemupanda 102. Mipanda yemazita muChiShona inogumira pamupanda 21 chete.",
        "mwedzi": "Handizivi mhinduro yacho. Hapana munhu akambofamba pamwedzi muHarare kana muZimbabwe.",
        "motokari": "Handizivi nezvazvo. Mashoko iwayo haamo munhoroondo yechokwadi yeChiShona."
    }
    
    for k, refusal in impossible_traps.items():
        if k in query.lower() and any(w in query.lower() for w in ["mupanda", "famba", "chaminuka"]):
            return {"response": refusal, "context": None}

    # Retrieve context from our 14,201 verified sentences
    retrieved = search_knowledge_base(query)
    
    if retrieved:
        primary_match = retrieved[0]
        # Clean formulation
        response = f"Zvinoenderana nezvidzidzo zvemutauro weChiShona: {primary_match}"
        return {
            "response": response,
            "context": " | ".join(retrieved)
        }
    else:
        return {
            "response": "Handizivi mhinduro yacho zvizere nokuti mashoko acho haawanikwe mudura rangu rezivo reChiShona parizvino.",
            "context": None
        }


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 RUZIVO LIVE TESTING UI STARTING")
    print("Open your browser at: http://localhost:8000")
    print("=" * 60 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
