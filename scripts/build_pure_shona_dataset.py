"""
Ruzivo AI — Pure ChiShona Dataset Builder
==========================================
Extracts and creates 100% PURE ChiShona Q&A instruction pairs and RAG entries.
Removes:
  - English parentheses (e.g., '(ideophone of Putting in safe place)')
  - English translations following colons
  - Mixed language artifacts

Outputs:
  - data/instruction_corpus/pure_shona_instructions.jsonl (For Colab training)
  - data/rag_knowledge_base/pure_shona_kb.jsonl (For RAG grounding)
"""

import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(r"c:\Users\recal\Desktop\Level 2.2 Project\ruzivo")
BOOKS_DIR = PROJECT_ROOT / "data" / "books_ocr"
INSTRUCT_OUT = PROJECT_ROOT / "data" / "instruction_corpus" / "pure_shona_instructions.jsonl"
KB_OUT = PROJECT_ROOT / "data" / "rag_knowledge_base" / "pure_shona_kb.jsonl"

SYSTEM_PROMPT = (
    "Iwe uri Ruzivo, mubatsiri wehungwaru wekunyora nekutaura muChiShona chete. "
    "Pindura mibvunzo zvizere, nechokwadi, uye pasina kushandisa mutauro weChirungu. "
    "Kana usingazivi mhinduro, taura pachena kuti 'Handizivi'."
)


def extract_pure_nyaudzosingwi():
    path = BOOKS_DIR / "648101854-Nyaudzosingwi.txt"
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8", errors="ignore")
    # Clean lines
    lines = text.split("\n")
    results = []

    current_entry = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("•"):
            if current_entry:
                results.append(current_entry)
            current_entry = line[1:].strip()
        else:
            current_entry += " " + line
    if current_entry:
        results.append(current_entry)

    pairs = []
    for item in results:
        # Match pattern: word (English explanation) Shona example
        match = re.search(r"^([^(]+?)\s*\(([^)]+)\)\.?\s*(.*)$", item)
        if match:
            word = match.group(1).strip()
            shona_example = match.group(3).strip()

            # Clean English out of shona_example if any (strip text after colons or English sentences)
            if ":" in shona_example:
                shona_part = shona_example.split(":")[0].strip()
                if len(shona_part.split()) >= 3:
                    shona_example = shona_part

            # Remove English words like 'the nail was gripped by the pincers'
            shona_example = re.sub(r'[a-zA-Z\s]+:[a-zA-Z\s]+', '', shona_example)

            if len(word) >= 2 and len(word.split()) <= 4:
                # Pure Shona response
                if shona_example and len(shona_example) > 5:
                    answer = f"Izwi rekuti '{word}' inyaudzosingwi inoshandiswa kuratidza chiito kana mamiriro ezvinhu. Muenzaniso wayo wekushandisa ndeuyu: '{shona_example}'."
                else:
                    answer = f"Izwi rekuti '{word}' inyaudzosingwi inoshandiswa kuratidza chiito, kurira, kana manzwiro muChiShona."

                pairs.append({
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Tsanangura nyaudzosingwi iyi uye mashandisirwo ayo: {word}"},
                        {"role": "assistant", "content": answer}
                    ],
                    "raw_text": answer
                })

    return pairs


def extract_pure_tsumo():
    paths = [BOOKS_DIR / "431120508-TSUMO.txt", BOOKS_DIR / "576008136-Tsumo.txt"]
    pairs = []

    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line in text.split("\n"):
            line = line.strip()
            # Match numbered lines: 1. Afirwa haaringwi kumeso
            match = re.search(r"^\d+[\.\)]\s*(.+)$", line)
            if match:
                proverb = match.group(1).strip()
                # Ensure no English
                if len(proverb) > 10 and not any(eng in proverb.lower() for eng in ["the", "is", "of", "and", "in"]):
                    answer = f"Iyi itsumo yeChiShona inodzidzisa tsika, hunhu nehuchenjeri hwechivanhu: '{proverb}'."
                    pairs.append({
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"Tsanangura tsumo iyi: {proverb}"},
                            {"role": "assistant", "content": answer}
                        ],
                        "raw_text": f"Tsumo: {proverb}. {answer}"
                    })

    return pairs


def extract_pure_mipanda():
    path = BOOKS_DIR / "649864977-MIPANDA-YEMAZITA-1.txt"
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8", errors="ignore")
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]

    pairs = []
    # Noun class rule QA pairs
    qa_rules = [
        ("Ko muChiShona mune mipanda yemazita mangani?", "MuChiShona mune mipanda yemazita inosvika makumi maviri nerimwe (21) inoshandiswa kuisa nekupatsanura mazita maererano nezvivakashure nesungawirirano yawo."),
        ("Chii chinonzi mupanda muChiShona?", "Mupanda iboka kana chikwata chinopinda mazita akafanana maererano nezvivakashure, sungawirirano, kana zvazvinoreva."),
        ("Chii chinonzi chivakashure chezita?", "Chivakashure chimedu cheshoko chinouya pakutanga pedzitsi rezita, chinotaridza mupanda wacho somuenzaniso chivakashure 'mu-' pazita rekuti 'mukomana'."),
        ("Chii chinonzi sungawirirano?", "Sungawirirano itsika yemutauro weChiShona inoita kuti zviito, zvipauro, nezviverengo zvienderane nezita riri kutaurwa nezvaro mumutsara."),
        ("Ipa mienzaniso yemazita emumupanda 1.", "Mumupanda 1 munopinda mazita evanhu ari muushoma ane chivakashure 'mu-', somuenzaniso: mukomana, musikana, mufundisi, murimi."),
        ("Ipa mienzaniso yemazita emumupanda 2.", "Mupanda 2 ndiyo uzhinji hwemupanda 1 une chivakashure 'va-', somuenzaniso: vakomana, vasikana, vafundisi, varimi."),
        ("Ipa mienzaniso yemazita emumupanda 3 ne 4.", "Mupanda 3 une mazita muushoma ane chivakashure 'mu-' chisingarevi munhu, somuenzaniso 'muti'. Uzhinji hwawo unopinda mumupanda 4 une chivakashure 'mi-', somuenzaniso 'miti'."),
        ("Ipa mienzaniso yemazita emumupanda 7 ne 8.", "Mupanda 7 une chivakashure 'chi-' (somuenzaniso: chigaro, chikoro). Uzhinji hwawo unopinda mumupanda 8 une chivakashure 'zvi-' (zvigaro, zvikoro)."),
        ("Ipa mienzaniso yemazita emumupanda 15.", "Mumupanda 15 munopinda mazita ezviito ane chivakashure 'ku-', somuenzaniso: kutamba, kudya, kuseka, kufamba, kudzidza.")
    ]

    for q, a in qa_rules:
        pairs.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": q},
                {"role": "assistant", "content": a}
            ],
            "raw_text": f"{q} {a}"
        })

    return pairs


def build_pure_datasets():
    print("=" * 60)
    print("  BUILDING 100% PURE CHISHONA DATASET (NO ENGLISH)")
    print("=" * 60)

    nyaudzo_data = extract_pure_nyaudzosingwi()
    print(f"• Pure Nyaudzosingwi entries: {len(nyaudzo_data):,}")

    tsumo_data = extract_pure_tsumo()
    print(f"• Pure Tsumo entries:         {len(tsumo_data):,}")

    mipanda_data = extract_pure_mipanda()
    print(f"• Pure Mipanda Q&A:          {len(mipanda_data):,}")

    # Anti-hallucination samples
    abstention_samples = [
        ("Ndiani akatanga kufamba pamwedzi muZimbabwe muna 1800?", "Handizivi mhinduro yacho. Hapana munhu akambofamba pamwedzi muZimbabwe kana mune rimwe gore iroro."),
        ("Ndeapi mazita emakomo anopfuta moto muHarare?", "Handizivi nezvemakomo anopfuta moto muHarare nokuti muHarare kana muZimbabwe yose hamuna makomo anopfuta moto."),
        ("Tsanangura motokari inobhururuka yakagadzirwa naChaminuka muna 1500.", "Handizivi mhinduro yacho nokuti Chaminuka haana kugadzira motokari inobhururuka munguva iyoyo."),
        ("Zita ramambo wekutanga weAmerica aitaura chiShona ndiani?", "Handizivi nezvazvo, nokuti vatungamiri veAmerica vaitaura Chirungu kwete chiShona."),
        ("Tsanangura mashandisiro e mushonga unonzi Xylophonium muurwere hwe gungwa.", "Handizivi nezvemushonga iwoyo. Ndapota bvunzai chiremba kana vanamazvikokota vezvoutano."),
        ("Zvinhu zvisiri muContext zvandiri kukubvunza nezve nyaya iyi unozviziva here?", "Handizivi mhinduro yenyaya iyi nokuti mashoko acho haasi mumashoko andapihwa (Context)."),
        ("Chii chakaitika musi wekuti zuva riite girini muBulawayo?", "Handizivi nezvechiitiko ichocho. Zuva harina kumbochinja ruvara kuita girini."),
        ("Ndipe mutemo wemupanda 99 muChiShona.", "Handizivi nezvemupanda 99. MuChiShona mune mipanda 21 chete yemazita, hapana mupanda 99."),
        ("Ndipe mutemo wemupanda 102 muChiShona.", "Handizivi nezvemupanda 102. Mipanda yemazita muChiShona inogumira pamupanda 21 chete.")
    ]

    negatives = []
    for q, a in abstention_samples:
        negatives.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": q},
                {"role": "assistant", "content": a}
            ],
            "raw_text": f"{q} {a}"
        })

    all_data = nyaudzo_data + tsumo_data + mipanda_data + negatives

    # Save to JSONL for training
    with open(INSTRUCT_OUT, "w", encoding="utf-8") as f:
        for item in all_data:
            f.write(json.dumps({"messages": item["messages"]}, ensure_ascii=False) + "\n")

    # Save to KB for RAG
    with open(KB_OUT, "w", encoding="utf-8") as f:
        for i, item in enumerate(all_data):
            f.write(json.dumps({"id": i, "text": item["raw_text"]}, ensure_ascii=False) + "\n")

    print("=" * 60)
    print(f"✅ Total 100% Pure Shona Training Pairs: {len(all_data):,}")
    print(f"📁 Output Training: {INSTRUCT_OUT}")
    print(f"📁 Output RAG KB:   {KB_OUT}")
    print("=" * 60)


if __name__ == "__main__":
    build_pure_datasets()
