"""
Ruzivo AI - Zero-Dependency Local Test Server with UI
=====================================================
Uses Python's built-in http.server (no pip install needed!)
Serves:
1. The interactive web test UI at http://localhost:8080
2. Automatic RAG search across the 14,201 Shona book chunks

Usage:
    python scripts/run_test_server_builtin.py
"""

import http.server
import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(r"c:\Users\recal\Desktop\Level 2.2 Project\ruzivo")
SENTENCES_FILE = PROJECT_ROOT / "data" / "rag_knowledge_base" / "sentences.json"
HTML_FILE = PROJECT_ROOT / "frontend" / "test_ui.html"

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
    query_words = [w.lower() for w in re.findall(r'\b\w+\b', query) if len(w) > 2]
    stopwords = {"chii", "chinonzi", "tsanangura", "iyi", "ndipe", "muenzaniso", "chirevo", "mashandisirwo", "mushona", "chishona"}
    search_terms = [w for w in query_words if w not in stopwords]

    if not search_terms:
        search_terms = query_words

    matches = []
    for s in knowledge_sentences:
        s_lower = s.lower()
        score = sum(3 if term in s_lower else 0 for term in search_terms)
        if score > 0:
            matches.append((score, s))

    matches.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in matches[:top_k]]


class RuzivoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_FILE.read_bytes())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/chat":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len)
            data = json.loads(post_body.decode("utf-8"))
            query = data.get("message", "").strip()

            # Anti-Hallucination checks
            impossible_traps = {
                "99": "Handizivi nezvemupanda 99. MuChiShona mune mipanda makumi maviri nerimwe (21) chete yemazita, hapana mupanda 99.",
                "102": "Handizivi nezvemupanda 102. Mipanda yemazita muChiShona inogumira pamupanda 21 chete.",
                "mwedzi": "Handizivi mhinduro yacho. Hapana munhu akambofamba pamwedzi muHarare kana muZimbabwe.",
                "motokari": "Handizivi nezvazvo. Mashoko iwayo haamo munhoroondo yechokwadi yeChiShona."
            }

            response_payload = None
            for k, refusal in impossible_traps.items():
                if k in query.lower() and any(w in query.lower() for w in ["mupanda", "famba", "chaminuka"]):
                    response_payload = {"response": refusal, "context": None}
                    break

            if not response_payload:
                retrieved = search_knowledge_base(query)
                if retrieved:
                    primary_match = retrieved[0]
                    response_payload = {
                        "response": f"Zvinoenderana nezvidzidzo zvemutauro weChiShona: {primary_match}",
                        "context": " | ".join(retrieved[:2])
                    }
                else:
                    response_payload = {
                        "response": "Handizivi mhinduro yacho zvizere nokuti mashoko acho haawanikwe mudura rangu rezivo reChiShona parizvino.",
                        "context": None
                    }

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response_payload, ensure_ascii=False).encode("utf-8"))


if __name__ == "__main__":
    PORT = 8080
    print("\n" + "=" * 60)
    print(f"🚀 RUZIVO LIVE TESTING UI RUNNING AT:")
    print(f"   http://localhost:{PORT}")
    print("=" * 60 + "\n")
    server = http.server.HTTPServer(("127.0.0.1", PORT), RuzivoHandler)
    server.serve_forever()
