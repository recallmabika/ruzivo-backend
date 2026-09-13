"""
Ruzivo AI - Shona Dataset Downloader v3
=======================================
Uses the HF Datasets Server API for row-level text extraction (avoids
downloading multi-GB audio parquets) and direct OPUS/eBible downloads.

Usage:
    python scripts/download_datasets_v3.py
"""

import json
import logging
import urllib.request
import urllib.error
import io
import os
import sys
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(r"c:\Users\recal\Desktop\Level 2.2 Project\ruzivo")
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


def save_jsonl(data: List[Dict], filepath: Path) -> None:
    logger.info(f"Saving {len(data):,} records to {filepath.name}")
    with open(filepath, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def fetch_json(url: str, timeout: int = 60) -> Any:
    """Fetch JSON from a URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "Ruzivo-AI/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_bytes(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Ruzivo-AI/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def hf_rows_api(dataset: str, config: str, split: str, offset: int = 0, length: int = 100) -> dict:
    """Use HF Datasets Server rows API to get text without downloading audio."""
    url = (
        f"https://datasets-server.huggingface.co/rows"
        f"?dataset={dataset}&config={config}&split={split}"
        f"&offset={offset}&length={length}"
    )
    return fetch_json(url)


def hf_get_all_rows(dataset: str, config: str, split: str, max_rows: int = 100000) -> list:
    """Paginate through the HF rows API to get all rows."""
    all_rows = []
    offset = 0
    batch = 100

    while offset < max_rows:
        try:
            result = hf_rows_api(dataset, config, split, offset, batch)
            rows = result.get("rows", [])
            if not rows:
                break
            all_rows.extend(rows)
            offset += len(rows)
            total = result.get("num_rows_total", "?")
            logger.info(f"  Fetched {offset}/{total} rows from {split}...")

            if len(rows) < batch:
                break
        except Exception as e:
            logger.warning(f"  API error at offset {offset}: {e}")
            break

    return all_rows


# =====================================================================
# 1. FLEURS (text only via rows API - avoids downloading audio)
# =====================================================================
def get_fleurs() -> int:
    output = RAW_DATA_DIR / "fleurs_shona.jsonl"
    if output.exists():
        n = sum(1 for _ in open(output, encoding="utf-8"))
        logger.info(f"FLEURS exists ({n:,} records)")
        return n

    records = []
    idx = 0
    for split in ["train", "validation", "test"]:
        try:
            rows = hf_get_all_rows("google/fleurs", "sn_zw", split)
            for r in rows:
                row = r.get("row", {})
                text = row.get("transcription", row.get("raw_transcription", ""))
                if text and len(str(text).strip()) > 3:
                    records.append({"text": str(text).strip(), "source": "fleurs", "id": idx})
                    idx += 1
        except Exception as e:
            logger.warning(f"FLEURS {split} failed: {e}")

    if records:
        save_jsonl(records, output)
    return len(records)


# =====================================================================
# 2. JW300 from OPUS (direct zip download)
# =====================================================================
def get_jw300() -> int:
    output = RAW_DATA_DIR / "jw300_shona.jsonl"
    if output.exists():
        n = sum(1 for _ in open(output, encoding="utf-8"))
        logger.info(f"JW300 exists ({n:,} records)")
        return n

    records = []
    idx = 0
    urls = [
        "https://opus.nlpl.eu/download.php?f=JW300/v1/moses/en-sn.txt.zip",
        "https://opus.nlpl.eu/download.php?f=JW300/v1c/moses/en-sn.txt.zip",
        "https://opus.nlpl.eu/download.php?f=JW300%2Fv1%2Fmoses%2Fen-sn.txt.zip",
    ]

    for url in urls:
        try:
            logger.info(f"Downloading JW300 from {url[:60]}...")
            data = fetch_bytes(url, timeout=300)
            zpath = RAW_DATA_DIR / "jw300_temp.zip"
            zpath.write_bytes(data)
            logger.info(f"  Downloaded {len(data)/1024/1024:.1f} MB")

            with zipfile.ZipFile(zpath) as zf:
                logger.info(f"  Zip contents: {zf.namelist()}")
                for name in zf.namelist():
                    if name.endswith(".sn") or ".sn" in name:
                        content = zf.read(name).decode("utf-8", errors="ignore")
                        for line in content.split("\n"):
                            line = line.strip()
                            if len(line) > 5:
                                records.append({"text": line, "source": "jw300", "id": idx})
                                idx += 1
                        logger.info(f"  Extracted {idx:,} Shona sentences from {name}")

            zpath.unlink(missing_ok=True)
            if records:
                break
        except Exception as e:
            logger.warning(f"  Failed: {e}")

    if records:
        save_jsonl(records, output)
    return len(records)


# =====================================================================
# 3. MasakhaNER 2.0  (via rows API)
# =====================================================================
def get_masakhaner() -> int:
    output = RAW_DATA_DIR / "masakhaner_shona.jsonl"
    if output.exists():
        n = sum(1 for _ in open(output, encoding="utf-8"))
        logger.info(f"MasakhaNER exists ({n:,} records)")
        return n

    records = []
    idx = 0

    for config in ["sna", "shona", "sn"]:
        try:
            for split in ["train", "validation", "test"]:
                rows = hf_get_all_rows("masakhane/masakhaner2", config, split)
                for r in rows:
                    row = r.get("row", {})
                    tokens = row.get("tokens", [])
                    if tokens:
                        sentence = " ".join(tokens)
                        if len(sentence) > 5:
                            records.append({"text": sentence, "source": "masakhaner2", "id": idx})
                            idx += 1
            if records:
                break
        except Exception as e:
            logger.debug(f"Config {config} failed: {e}")

    if records:
        save_jsonl(records, output)
    return len(records)


# =====================================================================
# 4. MasakhaNEWS (via rows API)
# =====================================================================
def get_masakhanews() -> int:
    output = RAW_DATA_DIR / "masakhanews_shona.jsonl"
    if output.exists():
        n = sum(1 for _ in open(output, encoding="utf-8"))
        logger.info(f"MasakhaNEWS exists ({n:,} records)")
        return n

    records = []
    idx = 0

    for config in ["sna", "shona", "sn"]:
        try:
            for split in ["train", "validation", "test"]:
                rows = hf_get_all_rows("masakhane/masakhanews", config, split)
                for r in rows:
                    row = r.get("row", {})
                    for key in ["headline", "text"]:
                        val = row.get(key, "")
                        if val and len(str(val).strip()) > 5:
                            records.append({"text": str(val).strip(), "source": "masakhanews", "id": idx})
                            idx += 1
            if records:
                break
        except Exception as e:
            logger.debug(f"Config {config} failed: {e}")

    if records:
        save_jsonl(records, output)
    return len(records)


# =====================================================================
# 5. FLORES+ (via rows API)
# =====================================================================
def get_flores() -> int:
    output = RAW_DATA_DIR / "flores_shona.jsonl"
    if output.exists():
        n = sum(1 for _ in open(output, encoding="utf-8"))
        logger.info(f"FLORES exists ({n:,} records)")
        return n

    records = []
    idx = 0

    for dataset_name in ["openlanguagedata/flores_plus", "facebook/flores"]:
        for config in ["sna_Latn", "sna", "all"]:
            try:
                for split in ["dev", "devtest", "train", "test", "validation"]:
                    try:
                        rows = hf_get_all_rows(dataset_name, config, split, max_rows=5000)
                        for r in rows:
                            row = r.get("row", {})
                            text = ""
                            for key in ["sentence", "text", "sna_Latn"]:
                                if key in row and row[key]:
                                    text = str(row[key])
                                    break
                            if text and len(text.strip()) > 5:
                                records.append({"text": text.strip(), "source": "flores", "id": idx})
                                idx += 1
                    except Exception:
                        continue
                if records:
                    break
            except Exception:
                continue
        if records:
            break

    if records:
        save_jsonl(records, output)
    return len(records)


# =====================================================================
# 6. Shona Wikipedia (via HF preprocessed)
# =====================================================================
def get_wikipedia() -> int:
    output = RAW_DATA_DIR / "wikipedia_shona.jsonl"
    if output.exists():
        n = sum(1 for _ in open(output, encoding="utf-8"))
        logger.info(f"Wikipedia exists ({n:,} records)")
        return n

    records = []
    idx = 0

    # Use rows API for Wikipedia — much faster than full download
    for config in ["20231101.sn", "sn"]:
        try:
            logger.info(f"Trying Wikipedia config '{config}'...")
            rows = hf_get_all_rows("wikimedia/wikipedia", config, "train", max_rows=100000)
            for r in rows:
                row = r.get("row", {})
                text = row.get("text", "")
                if text and len(str(text).strip()) > 20:
                    # Split into paragraphs
                    for para in str(text).split("\n\n"):
                        para = para.strip()
                        if len(para) > 20:
                            records.append({"text": para, "source": "wikipedia_sn", "id": idx})
                            idx += 1
            if records:
                break
        except Exception as e:
            logger.debug(f"Wikipedia {config} failed: {e}")

    if records:
        save_jsonl(records, output)
    return len(records)


# =====================================================================
# 7. Shona Bible (eBible.org)
# =====================================================================
def get_bible() -> int:
    output = RAW_DATA_DIR / "bible_shona.jsonl"
    if output.exists():
        n = sum(1 for _ in open(output, encoding="utf-8"))
        logger.info(f"Bible exists ({n:,} records)")
        return n

    records = []
    idx = 0

    bible_urls = [
        "https://ebible.org/Scriptures/sna-snaBSU.zip",
        "https://ebible.org/Scriptures/snaDBL.zip",
        "https://ebible.org/Scriptures/sna.zip",
    ]

    for url in bible_urls:
        try:
            logger.info(f"Downloading Bible from {url}...")
            data = fetch_bytes(url, timeout=120)
            zpath = RAW_DATA_DIR / "bible_temp.zip"
            zpath.write_bytes(data)
            logger.info(f"  Downloaded {len(data)/1024/1024:.1f} MB")

            with zipfile.ZipFile(zpath) as zf:
                for name in zf.namelist():
                    if any(name.endswith(ext) for ext in (".usfm", ".sfm", ".txt", ".SFM", ".USFM")):
                        try:
                            content = zf.read(name).decode("utf-8", errors="ignore")
                            for line in content.split("\n"):
                                line = line.strip()
                                if line.startswith("\\") and not line.startswith("\\v "):
                                    continue
                                if line.startswith("\\v "):
                                    parts = line.split(" ", 2)
                                    line = parts[2] if len(parts) > 2 else ""
                                line = line.strip()
                                if len(line) > 10:
                                    records.append({"text": line, "source": "bible_shona", "id": idx})
                                    idx += 1
                        except Exception:
                            continue

            zpath.unlink(missing_ok=True)
            if records:
                break
        except Exception as e:
            logger.warning(f"  Failed: {e}")

    if records:
        save_jsonl(records, output)
    return len(records)


# =====================================================================
# MAIN
# =====================================================================
def main():
    print("=" * 60)
    print("  RUZIVO AI - SHONA DATASET DOWNLOADER v3")
    print("=" * 60)

    downloaders = [
        ("FLEURS (sn_zw)", get_fleurs),
        ("JW300 (OPUS)", get_jw300),
        ("MasakhaNER 2.0", get_masakhaner),
        ("MasakhaNEWS", get_masakhanews),
        ("FLORES+", get_flores),
        ("Shona Wikipedia", get_wikipedia),
        ("Shona Bible", get_bible),
    ]

    results = {}
    total = 0

    for name, func in downloaders:
        print(f"\n--- {name} ---")
        try:
            count = func()
            results[name] = count
            total += count
            print(f"  -> {count:,} sentences {'[OK]' if count > 0 else '[EMPTY]'}")
        except Exception as e:
            results[name] = 0
            print(f"  -> ERROR: {e}")

    print("\n" + "=" * 60)
    print("  DOWNLOAD SUMMARY")
    print("=" * 60)
    for name, count in results.items():
        tag = "[OK]" if count > 0 else "[FAIL]"
        print(f"  {tag:6s} {name}: {count:,}")
    print(f"\n  TOTAL: {total:,} sentences")
    print(f"  Dir:   {RAW_DATA_DIR}")
    print("=" * 60)

    print("\nFiles:")
    for f in sorted(RAW_DATA_DIR.glob("*.jsonl")):
        sz = f.stat().st_size / (1024 * 1024)
        n = sum(1 for _ in open(f, encoding="utf-8"))
        print(f"  {f.name}: {n:,} records ({sz:.1f} MB)")


if __name__ == "__main__":
    main()
