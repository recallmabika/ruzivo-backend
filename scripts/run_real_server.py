import http.server
import json
import re
import sys
import time
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(r"c:\Users\recal\Desktop\Level 2.2 Project\ruzivo")
SENTENCES_FILE = PROJECT_ROOT / "data" / "rag_knowledge_base" / "sentences.json"
HTML_FILE = PROJECT_ROOT / "frontend" / "test_ui.html"
ADAPTER_PATH = PROJECT_ROOT / "backend" / "models" / "ruzivo-llm-v6"
BASE_MODEL_NAME = "Qwen/Qwen2.5-1.5B"

print("=" * 60)
print("  RUZIVO AI - REAL INFERENCE SERVER (v6 + RAG)")
print("=" * 60)

knowledge_sentences = []
if SENTENCES_FILE.exists():
    with open(SENTENCES_FILE, "r", encoding="utf-8") as f:
        knowledge_sentences = json.load(f)
    print(f"[RAG] Loaded {len(knowledge_sentences):,} Shona educational sentences.")
else:
    print("[RAG] Warning: sentences.json not found.")

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

print(f"[Model] Loading Tokenizer from {ADAPTER_PATH}...")
tokenizer = AutoTokenizer.from_pretrained(str(ADAPTER_PATH), trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print(f"[Model] Loading Base Model: {BASE_MODEL_NAME} (bfloat16 on CPU)...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_NAME,
    torch_dtype=torch.bfloat16,
    device_map="cpu",
    low_cpu_mem_usage=True
)

print(f"[Model] Loading v6 LoRA Adapter from {ADAPTER_PATH}...")
model = PeftModel.from_pretrained(base_model, str(ADAPTER_PATH))
model.eval()
print("[Model] Neural Model v6 successfully loaded and ready for inference!")

def generate_shona_response(query: str, context: str = "") -> str:
    system_msg = (
        "Iwe uri Ruzivo, mubatsiri wehungwaru wekunyora nekutaura muChiShona chete. "
        "Pindura mibvunzo zvizere uye nechokwadi chete. "
        "Kana paine mashoko eContext akapihwa, shandisa mashoko iwayo chete. "
        "Kana usingazivi mhinduro yacho kana kuti chinhu chacho chisipo muChiShona, taura pachena kuti 'Handizivi' pane kuedza kufungidzira."
    )

    if context:
        user_content = f"Mashoko anobatsira (Context):\n{context}\n\nMubvunzo:\n{query}"
    else:
        user_content = query

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_content}
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(prompt, return_tensors="pt")

    t0 = time.time()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
    elapsed = time.time() - t0

    generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
    response_text = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
    print(f"[Inference] Generated {len(generated_ids)} tokens in {elapsed:.2f}s: {response_text[:80]}...")
    return response_text


class RealInferenceHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
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

            print(f"\n[Request] User prompt: {query}")

            retrieved = search_knowledge_base(query, top_k=2)
            context_str = "\n".join(retrieved) if retrieved else ""

            bot_reply = generate_shona_response(query, context=context_str)

            response_data = {
                "response": bot_reply,
                "context": " | ".join(retrieved) if retrieved else None
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))


def run():
    server = http.server.HTTPServer(("0.0.0.0", 8080), RealInferenceHandler)
    print("\n" + "=" * 60)
    print("  Server running at http://localhost:8080")
    print("  Open your browser and test real neural responses with ruzivo-llm-v6!")
    print("=" * 60 + "\n")
    server.serve_forever()

if __name__ == "__main__":
    run()
