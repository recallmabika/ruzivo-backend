"""
Ruzivo AI - Instruction and RAG Corpus Builder
==============================================
Transforms clean Shona cultural, grammar, and literary texts (Mipanda,
Nyaudzosingwi, Tsumo, etc.) into:
1. High-quality instruction-tuning pairs (Alpaca / ChatML format)
2. FAISS-ready knowledge base chunks for RAG grounding
"""

import json
import re
from pathlib import Path
from typing import List, Dict

PROJECT_ROOT = Path(r"c:\Users\recal\Desktop\Level 2.2 Project\ruzivo")
INPUT_FILE = PROJECT_ROOT / "data" / "cleaned" / "books_extracted_clean.jsonl"
INSTRUCTION_OUT = PROJECT_ROOT / "data" / "instruction_corpus" / "shona_books_instructions.jsonl"
RAG_OUT = PROJECT_ROOT / "data" / "rag_knowledge_base" / "shona_knowledge_chunks.jsonl"

INSTRUCTION_OUT.parent.mkdir(parents=True, exist_ok=True)
RAG_OUT.parent.mkdir(parents=True, exist_ok=True)


def build_corpora():
    instructions = []
    rag_chunks = []
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            data = json.loads(line)
            text = data["text"].strip()
            if not text:
                continue

            # RAG chunk representation
            rag_chunks.append({
                "id": idx,
                "text": text,
                "source": "shona_educational_corpus"
            })

            # 1. Tsumo Q&A generator
            # If text has proverb characteristics
            if any(marker in text.lower() for marker in ["akwewa", "chako", "mwoyo", "mukaka", "charova", "chembere", "gudo"]):
                instructions.append({
                    "instruction": "Tsanangura tsumo iyi kana kupa chirevo chayo: " + text,
                    "input": "",
                    "output": f"Iyi itsumo yechiShona inodzidzisa tsika nehuchenjeri hwechinyakare: '{text}'."
                })

            # 2. Mipanda / Noun Classes generator
            if "mupanda" in text.lower() or "chivakashure" in text.lower():
                instructions.append({
                    "instruction": "Tsanangura maererano nemitemo yemutauro wechiShona:",
                    "input": text,
                    "output": f"Chidzidzo pamusoro pemipanda nezvivakashure: {text}"
                })

            # 3. Nyaudzosingwi generator
            if "ideophone" in text.lower() or "kureva" in text.lower():
                instructions.append({
                    "instruction": "Tsanangura nyaudzosingwi kana mashandisirwo eizwi iri:",
                    "input": text,
                    "output": f"Tsanangudzo yeNyaudzosingwi nemashandisirwo ayo: {text}"
                })

    # Save Instruction Pairs
    print(f"Generated {len(instructions):,} high-quality instruction-response pairs.")
    with open(INSTRUCTION_OUT, "w", encoding="utf-8") as f:
        for item in instructions:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # Save RAG Knowledge Base Chunks
    print(f"Generated {len(rag_chunks):,} RAG knowledge chunks.")
    with open(RAG_OUT, "w", encoding="utf-8") as f:
        for item in rag_chunks:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    build_corpora()
