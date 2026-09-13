"""
Ruzivo AI — Robust Shona Dataset Downloader
============================================
Downloads Shona language datasets using direct HTTP/parquet downloads
instead of the unreliable HF `datasets` library on Windows.

Usage:
    python scripts/download_datasets_v2.py
"""

import json
import logging
import urllib.request
import urllib.error
import io
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(r"c:\Users\recal\Desktop\Level 2.2 Project\ruzivo")
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Suppress symlink warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


def save_to_jsonl(data: List[Dict[str, Any]], filepath: Path) -> None:
    """Save a list of dictionaries to a JSONL file."""
    logger.info(f"Saving {len(data):,} records to {filepath}")
    with open(filepath, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def download_bytes(url: str) -> bytes:
    """Download URL content as bytes."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Ruzivo-AI-Project)"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


# ─────────────────────────────────────────────────────────────────────────────
# 1. FLEURS  (google/fleurs, config sn_zw)
# ─────────────────────────────────────────────────────────────────────────────
def get_fleurs() -> int:
    """Download FLEURS Shona transcriptions via direct parquet download."""
    output_path = RAW_DATA_DIR / "fleurs_shona.jsonl"
    if output_path.exists():
        count = sum(1 for _ in open(output_path, encoding="utf-8"))
        logger.info(f"FLEURS already exists ({count:,} records)")
        return count

    try:
        import pyarrow.parquet as pq

        base = "https://huggingface.co/datasets/google/fleurs/resolve/main/parquet-data/sn_zw"
        records = []
        idx = 0

        for split in ["train", "validation", "test"]:
            url = f"{base}/{split}-00000-of-00001.parquet"
            logger.info(f"Downloading FLEURS {split}...")
            try:
                data = download_bytes(url)
                table = pq.read_table(io.BytesIO(data))
                df = table.to_pandas()
                for _, row in df.iterrows():
                    text = str(row.get("transcription", row.get("raw_transcription", "")))
                    if text and len(text.strip()) > 3:
                        records.append({"text": text.strip(), "source": "fleurs", "id": idx})
                        idx += 1
                logger.info(f"  {split}: {len(df)} rows")
            except Exception as e:
                logger.warning(f"  Failed {split}: {e}")

        if records:
            save_to_jsonl(records, output_path)
        return len(records)
    except Exception as e:
        logger.error(f"FLEURS download failed: {e}")
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# 2. MasakhaNER 2.0  (masakhane/masakhaner2, config sna)
# ─────────────────────────────────────────────────────────────────────────────
def get_masakhaner() -> int:
    """Download MasakhaNER 2.0 Shona data."""
    output_path = RAW_DATA_DIR / "masakhaner_shona.jsonl"
    if output_path.exists():
        count = sum(1 for _ in open(output_path, encoding="utf-8"))
        logger.info(f"MasakhaNER already exists ({count:,} records)")
        return count

    try:
        from datasets import load_dataset
        records = []
        idx = 0

        # Try different config names
        for config in ["sna", "shona", "sn"]:
            try:
                logger.info(f"Trying MasakhaNER config '{config}'...")
                ds = load_dataset("masakhane/masakhaner2", config)
                for split in ds.keys():
                    for item in ds[split]:
                        tokens = item.get("tokens", [])
                        if tokens:
                            sentence = " ".join(tokens)
                            records.append({"text": sentence, "source": "masakhaner2", "id": idx})
                            idx += 1
                break
            except Exception:
                continue

        if records:
            save_to_jsonl(records, output_path)
        else:
            logger.warning("MasakhaNER: No Shona config found.")
        return len(records)
    except Exception as e:
        logger.error(f"MasakhaNER download failed: {e}")
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# 3. MasakhaNEWS  (masakhane/masakhanews, config sna)
# ─────────────────────────────────────────────────────────────────────────────
def get_masakhanews() -> int:
    """Download MasakhaNEWS Shona data."""
    output_path = RAW_DATA_DIR / "masakhanews_shona.jsonl"
    if output_path.exists():
        count = sum(1 for _ in open(output_path, encoding="utf-8"))
        logger.info(f"MasakhaNEWS already exists ({count:,} records)")
        return count

    try:
        from datasets import load_dataset
        records = []
        idx = 0

        for config in ["sna", "shona", "sn"]:
            try:
                logger.info(f"Trying MasakhaNEWS config '{config}'...")
                ds = load_dataset("masakhane/masakhanews", config)
                for split in ds.keys():
                    for item in ds[split]:
                        headline = item.get("headline", "")
                        text = item.get("text", "")
                        if headline:
                            records.append({"text": headline.strip(), "source": "masakhanews", "id": idx})
                            idx += 1
                        if text:
                            records.append({"text": text.strip(), "source": "masakhanews", "id": idx})
                            idx += 1
                break
            except Exception:
                continue

        if records:
            save_to_jsonl(records, output_path)
        else:
            logger.warning("MasakhaNEWS: No Shona config found.")
        return len(records)
    except Exception as e:
        logger.error(f"MasakhaNEWS download failed: {e}")
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# 4. FLORES+ / NLLB  (openlanguagedata/flores_plus, sna_Latn)
# ─────────────────────────────────────────────────────────────────────────────
def get_flores() -> int:
    """Download FLORES+ Shona sentences."""
    output_path = RAW_DATA_DIR / "flores_shona.jsonl"
    if output_path.exists():
        count = sum(1 for _ in open(output_path, encoding="utf-8"))
        logger.info(f"FLORES already exists ({count:,} records)")
        return count

    try:
        from datasets import load_dataset
        records = []
        idx = 0

        for name in ["openlanguagedata/flores_plus", "facebook/flores"]:
            for config in ["sna_Latn", "sna", "sn", "all"]:
                try:
                    logger.info(f"Trying FLORES from {name}, config '{config}'...")
                    ds = load_dataset(name, config)
                    for split in ds.keys():
                        for item in ds[split]:
                            # FLORES stores sentences with language as column name
                            text = ""
                            for key in ["sentence", "text", "sna_Latn", "sentence_sna_Latn"]:
                                if key in item and item[key]:
                                    text = str(item[key])
                                    break
                            if not text:
                                # Try all columns for one that has Shona text
                                for k, v in item.items():
                                    if isinstance(v, str) and len(v) > 10:
                                        text = v
                                        break
                            if text and len(text.strip()) > 5:
                                records.append({"text": text.strip(), "source": "flores", "id": idx})
                                idx += 1
                    if records:
                        break
                except Exception:
                    continue
            if records:
                break

        if records:
            save_to_jsonl(records, output_path)
        else:
            logger.warning("FLORES: No Shona data found.")
        return len(records)
    except Exception as e:
        logger.error(f"FLORES download failed: {e}")
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# 5. Shona Wikipedia dump
# ─────────────────────────────────────────────────────────────────────────────
def get_wikipedia() -> int:
    """Download Shona Wikipedia text from HF preprocessed dataset."""
    output_path = RAW_DATA_DIR / "wikipedia_shona.jsonl"
    if output_path.exists():
        count = sum(1 for _ in open(output_path, encoding="utf-8"))
        logger.info(f"Wikipedia already exists ({count:,} records)")
        return count

    try:
        from datasets import load_dataset
        records = []
        idx = 0

        # Try the preprocessed Wikipedia datasets on HF
        for name in ["wikimedia/wikipedia", "wikipedia"]:
            for config in ["20231101.sn", "sn"]:
                try:
                    logger.info(f"Trying Wikipedia from {name}, config '{config}'...")
                    ds = load_dataset(name, config, split="train")
                    for item in ds:
                        text = item.get("text", "")
                        if text and len(text.strip()) > 20:
                            # Split long articles into paragraphs
                            paragraphs = text.strip().split("\n\n")
                            for para in paragraphs:
                                para = para.strip()
                                if len(para) > 20:
                                    records.append({"text": para, "source": "wikipedia_sn", "id": idx})
                                    idx += 1
                    if records:
                        break
                except Exception as e:
                    logger.debug(f"Failed {name}/{config}: {e}")
                    continue
            if records:
                break

        if records:
            save_to_jsonl(records, output_path)
        else:
            logger.warning("Wikipedia: No Shona dump found via HF. Try manual download from dumps.wikimedia.org/snwiki/")
        return len(records)
    except Exception as e:
        logger.error(f"Wikipedia download failed: {e}")
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# 6. Shona Bible (eBible.org)
# ─────────────────────────────────────────────────────────────────────────────
def get_bible() -> int:
    """Download Shona Bible text from eBible.org."""
    output_path = RAW_DATA_DIR / "bible_shona.jsonl"
    if output_path.exists():
        count = sum(1 for _ in open(output_path, encoding="utf-8"))
        logger.info(f"Bible already exists ({count:,} records)")
        return count

    import zipfile

    records = []
    idx = 0

    # Try multiple Shona Bible editions on eBible
    bible_urls = [
        "https://ebible.org/Scriptures/sna-snaBSU.zip",
        "https://ebible.org/Scriptures/snaDBL.zip",
    ]

    for url in bible_urls:
        try:
            logger.info(f"Trying Bible download from {url}...")
            data = download_bytes(url)
            zip_path = RAW_DATA_DIR / "bible_temp.zip"
            zip_path.write_bytes(data)

            with zipfile.ZipFile(zip_path, "r") as zf:
                for name in zf.namelist():
                    # Look for text files (USFM, SFM, or TXT)
                    if name.endswith((".usfm", ".sfm", ".txt", ".SFM", ".USFM")):
                        try:
                            content = zf.read(name).decode("utf-8", errors="ignore")
                            # Extract verse text — skip USFM markers
                            for line in content.split("\n"):
                                line = line.strip()
                                # Skip USFM markers like \id, \h, \c, \v etc
                                if line.startswith("\\") and not line.startswith("\\v "):
                                    continue
                                # Remove verse number marker
                                if line.startswith("\\v "):
                                    line = line.split(" ", 2)[-1] if len(line.split(" ", 2)) > 2 else ""
                                line = line.strip()
                                if len(line) > 10:
                                    records.append({"text": line, "source": "bible_shona", "id": idx})
                                    idx += 1
                        except Exception:
                            continue

            zip_path.unlink(missing_ok=True)
            if records:
                break
        except Exception as e:
            logger.warning(f"  Failed: {e}")

    if records:
        save_to_jsonl(records, output_path)
    else:
        logger.warning("Bible: Could not download Shona Bible from eBible.org")
    return len(records)


# ─────────────────────────────────────────────────────────────────────────────
# 7. OPUS JW300 (direct download)
# ─────────────────────────────────────────────────────────────────────────────
def get_jw300() -> int:
    """Download JW300 Shona data from OPUS."""
    output_path = RAW_DATA_DIR / "jw300_shona.jsonl"
    if output_path.exists():
        count = sum(1 for _ in open(output_path, encoding="utf-8"))
        logger.info(f"JW300 already exists ({count:,} records)")
        return count

    import zipfile

    records = []
    idx = 0

    # OPUS hosts JW300 — try direct download of Shona monolingual or en-sn pair
    urls = [
        "https://opus.nlpl.eu/download.php?f=JW300/v1/moses/en-sn.txt.zip",
        "https://opus.nlpl.eu/download.php?f=JW300/v1c/moses/en-sn.txt.zip",
    ]

    for url in urls:
        try:
            logger.info(f"Downloading JW300 from OPUS: {url}")
            data = download_bytes(url)
            zip_path = RAW_DATA_DIR / "jw300_temp.zip"
            zip_path.write_bytes(data)

            with zipfile.ZipFile(zip_path, "r") as zf:
                for name in zf.namelist():
                    # Look for the Shona side file (*.sn)
                    if name.endswith(".sn") or "sn" in name.lower():
                        logger.info(f"  Extracting {name}...")
                        content = zf.read(name).decode("utf-8", errors="ignore")
                        for line in content.split("\n"):
                            line = line.strip()
                            if len(line) > 5:
                                records.append({"text": line, "source": "jw300", "id": idx})
                                idx += 1

            zip_path.unlink(missing_ok=True)
            if records:
                break
        except Exception as e:
            logger.warning(f"  Failed: {e}")

    if records:
        save_to_jsonl(records, output_path)
    else:
        logger.warning("JW300: Could not download from OPUS")
    return len(records)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("  RUZIVO AI — SHONA DATASET DOWNLOADER v2")
    print("=" * 65)

    results = {}

    downloaders = [
        ("FLEURS (google/fleurs sn_zw)", get_fleurs),
        ("JW300 (OPUS en-sn)", get_jw300),
        ("MasakhaNER 2.0 (sna)", get_masakhaner),
        ("MasakhaNEWS (sna)", get_masakhanews),
        ("FLORES+ (sna_Latn)", get_flores),
        ("Shona Wikipedia", get_wikipedia),
        ("Shona Bible (eBible)", get_bible),
    ]

    total = 0
    for name, func in downloaders:
        print(f"\n{'─' * 50}")
        print(f"📥 {name}")
        print(f"{'─' * 50}")
        try:
            count = func()
            results[name] = count
            total += count
            if count > 0:
                print(f"  ✅ {count:,} sentences")
            else:
                print(f"  ⚠️  0 sentences (failed or empty)")
        except Exception as e:
            results[name] = 0
            print(f"  ❌ Error: {e}")

    # Summary
    print("\n" + "=" * 65)
    print("  📊 DOWNLOAD SUMMARY")
    print("=" * 65)
    for name, count in results.items():
        status = "✅" if count > 0 else "❌"
        print(f"  {status} {name}: {count:,} sentences")
    print(f"\n  TOTAL: {total:,} sentences")
    print(f"  Output: {RAW_DATA_DIR}")
    print("=" * 65)

    # List files created
    print("\n📁 Files created:")
    for f in sorted(RAW_DATA_DIR.glob("*.jsonl")):
        size_mb = f.stat().st_size / (1024 * 1024)
        lines = sum(1 for _ in open(f, encoding="utf-8"))
        print(f"  {f.name}: {lines:,} records ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
