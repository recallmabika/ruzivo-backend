"""
Ruzivo AI - Prepare Unified Fine-Tuning Dataset (Kaggle & Colab)
================================================================
Combines:
1. Shona educational Q&A (Mipanda 1-21, Nyaudzosingwi, Tsumo)
2. Negative / Abstention examples ("Handizivi") to suppress hallucinations
3. Context-grounded retrieval examples

Output:
    data/instruction_corpus/ruzivo_train_v6.jsonl
"""

import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(r"c:\Users\recal\Desktop\Level 2.2 Project\ruzivo")
BOOKS_INSTRUCTIONS = PROJECT_ROOT / "data" / "instruction_corpus" / "shona_books_instructions.jsonl"
OUT_FILE = PROJECT_ROOT / "data" / "instruction_corpus" / "ruzivo_train_v6.jsonl"


def prepare_dataset():
    records = []

    # 1. Load book instruction pairs
    if BOOKS_INSTRUCTIONS.exists():
        with open(BOOKS_INSTRUCTIONS, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                # Format into ChatML message structure
                system_prompt = "Iwe uri Ruzivo, mubatsiri wehungwaru wekunyora nekutaura muChiShona chete. Pindura mibvunzo zvizere uye nechokwadi."
                user_msg = data["instruction"]
                if data.get("input"):
                    user_msg += f"\n\n{data['input']}"

                records.append({
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg},
                        {"role": "assistant", "content": data["output"]}
                    ]
                })

    # 2. Add Anti-Hallucination ("Handizivi" Abstention) Samples
    # Critical: teaches the model when NOT to fabricate facts!
    abstention_samples = [
        ("Ndiani akatanga kufamba pamwedzi muZimbabwe muna 1800?", "Handizivi mhinduro yacho. Hapana munhu akambofamba pamwedzi muZimbabwe kana mune rimwe gore iroro."),
        ("Ndeapi mazita emakomo anopfuta moto muHarare?", "Handizivi nezvemakomo anopfuta moto muHarare nokuti muHarare kana muZimbabwe yose hamuna makomo anopfuta moto."),
        ("Tsanangura motokari inobhururuka yakagadzirwa naChaminuka muna 1500.", "Handizivi mhinduro yacho nokuti Chaminuka haana kugadzira motokari inobhururuka munguva iyoyo."),
        ("Zita ramambo wekutanga weAmerica aitaura chiShona ndiani?", "Handizivi nezvazvo, nokuti vatungamiri veAmerica vaitaura Chirungu kwete chiShona."),
        ("Tsanangura mashandisiro e mushonga unonzi Xylophonium muurwere hwe gungwa.", "Handizivi nezvemushonga iwoyo. Ndapota bvunzai chiremba kana vanamazvikokota vezvoutano."),
        ("Zvinhu zvisiri muContext zvandiri kukubvunza nezve nyaya iyi unozviziva here?", "Handizivi mhinduro yenyaya iyi nokuti mashoko acho haasi mumashoko andapihwa (Context)."),
        ("Chii chakaitika musi wekuti zuva riite girini muBulawayo?", "Handizivi nezvechiitiko ichocho. Zuva harina kumbochinja ruvara kuita girini."),
        ("Ndipe mutemo wemupanda 99 muChiShona.", "Handizivi nezvemupanda 99. MuChiShona mune mipanda 21 chete yemazita, hapana mupanda 99.")
    ]

    for q, a in abstention_samples:
        records.append({
            "messages": [
                {"role": "system", "content": "Iwe uri Ruzivo, mubatsiri wehungwaru wekunyora nekutaura muChiShona chete. Kana usingazivi chokwadi, taura kuti handizivi."},
                {"role": "user", "content": q},
                {"role": "assistant", "content": a}
            ]
        })

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"✅ Prepared {len(records):,} unified training samples in ChatML format -> {OUT_FILE}")


if __name__ == "__main__":
    prepare_dataset()
