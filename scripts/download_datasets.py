import json
import logging
import urllib.request
import urllib.error
import zipfile
import bz2
from pathlib import Path
from typing import Optional, List, Dict, Any
from tqdm import tqdm
from datasets import load_dataset, get_dataset_config_names

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(r"c:\Users\recal\Desktop\Level 2.2 Project\ruzivo")
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

def ensure_dir(path: Path) -> None:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)

def save_to_jsonl(data: List[Dict[str, Any]], filepath: Path) -> None:
    """Save a list of dictionaries to a JSONL file."""
    logger.info(f"Saving {len(data)} records to {filepath}")
    with open(filepath, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def download_file(url: str, dest_path: Path) -> bool:
    """Download a file from a URL with a progress bar."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            file_size = int(response.headers.get("Content-Length", 0))
            
            with open(dest_path, "wb") as f, tqdm(
                desc=f"Downloading {dest_path.name}",
                total=file_size,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    pbar.update(len(chunk))
        return True
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return False

def get_jw300() -> int:
    """Download JW300 dataset for Shona."""
    output_path = RAW_DATA_DIR / "jw300_shona.jsonl"
    if output_path.exists():
        logger.info(f"JW300 already exists at {output_path}")
        return sum(1 for _ in open(output_path, encoding='utf-8'))
        
    records = []
    # Try different dataset names for JW300
    dataset_names = ["opus/jw300", "sentence-transformers/parallel-sentences-jw300"]
    ds = None
    
    for name in dataset_names:
        try:
            logger.info(f"Trying to load JW300 from {name}...")
            # Often requires lang1-lang2 config, try en-sn
            try:
                ds = load_dataset(name, "en-sn", split="train", )
                break
            except Exception:
                try:
                    ds = load_dataset(name, "sn-en", split="train", )
                    break
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"Failed loading {name}: {e}")
            
    if ds:
        idx = 0
        for item in tqdm(ds, desc="Processing JW300"):
            # Depending on the dataset format, handle accordingly
            text = ""
            if "translation" in item:
                trans = item["translation"]
                if "sn" in trans:
                    text = trans["sn"]
            elif "target" in item and "source" in item:
                # Need to figure out which one is Shona, assuming target
                text = item["target"]
            elif "text" in item:
                text = item["text"]
                
            if text:
                records.append({"text": text, "source": "jw300", "id": idx})
                idx += 1
                
        if records:
            save_to_jsonl(records, output_path)
            return len(records)
            
    logger.warning("Failed to download JW300 dataset.")
    return 0

def get_cc100() -> int:
    """Download CC100 dataset for Shona."""
    output_path = RAW_DATA_DIR / "cc100_shona.jsonl"
    if output_path.exists():
        logger.info(f"CC100 already exists at {output_path}")
        return sum(1 for _ in open(output_path, encoding='utf-8'))
        
    records = []
    
    # Approach 1: Try loading from HF with different dataset IDs
    for name in ["statmt/cc100", "cc100"]:
        try:
            logger.info(f"Trying to load CC100 from {name}...")
            ds = load_dataset(name, "sn", split="train")
            idx = 0
            for item in tqdm(ds, desc="Processing CC100"):
                records.append({"text": item["text"], "source": "cc100", "id": idx})
                idx += 1
            if records:
                save_to_jsonl(records, output_path)
                return len(records)
        except Exception as e:
            logger.debug(f"Failed loading {name}: {e}")
    
    # Approach 2: Direct download from data.statmt.org
    try:
        logger.info("Trying direct download of CC100 Shona from data.statmt.org...")
        cc100_url = "https://data.statmt.org/cc-100/sn.txt.xz"
        cc100_file = RAW_DATA_DIR / "sn.txt.xz"
        
        if download_file(cc100_url, cc100_file):
            import lzma
            logger.info("Decompressing CC100 Shona data...")
            idx = 0
            with lzma.open(cc100_file, "rt", encoding="utf-8") as f:
                for line in tqdm(f, desc="Processing CC100"):
                    line = line.strip()
                    if line:
                        records.append({"text": line, "source": "cc100", "id": idx})
                        idx += 1
            if records:
                save_to_jsonl(records, output_path)
                # Clean up compressed file
                cc100_file.unlink(missing_ok=True)
                return len(records)
    except Exception as e:
        logger.warning(f"Failed direct CC100 download: {e}")
    
    logger.warning("Failed to download CC100 dataset from all sources.")
    return 0

def get_fleurs() -> int:
    """Download FLEURS dataset for Shona."""
    output_path = RAW_DATA_DIR / "fleurs_shona.jsonl"
    if output_path.exists():
        logger.info(f"FLEURS already exists at {output_path}")
        return sum(1 for _ in open(output_path, encoding='utf-8'))
        
    records = []
    try:
        logger.info("Loading FLEURS Shona dataset...")
        ds = load_dataset("google/fleurs", "sn_zw", )
        idx = 0
        for split in ds.keys():
            for item in tqdm(ds[split], desc=f"Processing FLEURS {split}"):
                if "transcription" in item:
                    records.append({"text": item["transcription"], "source": "fleurs", "id": idx})
                    idx += 1
        save_to_jsonl(records, output_path)
        return len(records)
    except Exception as e:
        logger.warning(f"Failed to download FLEURS dataset: {e}")
        return 0

def get_masakhaner() -> int:
    """Download MasakhaNER 2.0 dataset for Shona."""
    output_path = RAW_DATA_DIR / "masakhaner_shona.jsonl"
    if output_path.exists():
        logger.info(f"MasakhaNER already exists at {output_path}")
        return sum(1 for _ in open(output_path, encoding='utf-8'))
        
    records = []
    try:
        logger.info("Loading MasakhaNER 2.0 Shona dataset...")
        ds = load_dataset("masakhane/masakhaner2", "sna", )
        idx = 0
        for split in ds.keys():
            for item in tqdm(ds[split], desc=f"Processing MasakhaNER {split}"):
                if "tokens" in item:
                    text = " ".join(item["tokens"])
                    records.append({"text": text, "source": "masakhaner2", "id": idx})
                    idx += 1
        save_to_jsonl(records, output_path)
        return len(records)
    except Exception as e:
        logger.warning(f"Failed to download MasakhaNER dataset: {e}")
        return 0

def get_masakhanews() -> int:
    """Download MasakhaNEWS dataset for Shona."""
    output_path = RAW_DATA_DIR / "masakhanews_shona.jsonl"
    if output_path.exists():
        logger.info(f"MasakhaNEWS already exists at {output_path}")
        return sum(1 for _ in open(output_path, encoding='utf-8'))
        
    records = []
    try:
        logger.info("Loading MasakhaNEWS Shona dataset...")
        ds = load_dataset("masakhane/masakhanews", "sna", )
        idx = 0
        for split in ds.keys():
            for item in tqdm(ds[split], desc=f"Processing MasakhaNEWS {split}"):
                text = f"{item.get('headline', '')}. {item.get('text', '')}".strip()
                if text:
                    records.append({"text": text, "source": "masakhanews", "id": idx})
                    idx += 1
        save_to_jsonl(records, output_path)
        return len(records)
    except Exception as e:
        logger.warning(f"Failed to download MasakhaNEWS dataset: {e}")
        return 0

def get_nllb_flores() -> int:
    """Download NLLB Seed / FLORES dataset for Shona."""
    output_path = RAW_DATA_DIR / "nllb_shona.jsonl"
    if output_path.exists():
        logger.info(f"NLLB/FLORES already exists at {output_path}")
        return sum(1 for _ in open(output_path, encoding='utf-8'))
        
    records = []
    dataset_names = ["facebook/flores", "openlanguagedata/flores_plus"]
    ds = None
    
    for name in dataset_names:
        try:
            logger.info(f"Trying to load FLORES from {name}...")
            # FLORES uses 3-letter language codes usually, Shona is sna_Latn
            ds = load_dataset(name, "sna_Latn", )
            break
        except Exception:
            pass
            
    if ds:
        idx = 0
        for split in ds.keys():
            for item in tqdm(ds[split], desc=f"Processing FLORES {split}"):
                if "sentence" in item:
                    records.append({"text": item["sentence"], "source": "flores", "id": idx})
                    idx += 1
        if records:
            save_to_jsonl(records, output_path)
            return len(records)
            
    logger.warning("Failed to download NLLB/FLORES dataset.")
    return 0

def get_wiki_dump() -> int:
    """Download Shona Wikipedia dump."""
    output_path = RAW_DATA_DIR / "snwiki-latest-pages-articles.xml.bz2"
    if output_path.exists():
        logger.info(f"Wikipedia dump already exists at {output_path}")
        return 1  # Returning 1 to signify file was processed
        
    url = "https://dumps.wikimedia.org/snwiki/latest/snwiki-latest-pages-articles.xml.bz2"
    logger.info(f"Downloading Shona Wikipedia dump from {url}...")
    success = download_file(url, output_path)
    return 1 if success else 0

def get_shona_bible() -> int:
    """Download Shona Bible from eBible."""
    output_path = RAW_DATA_DIR / "shona_bible.zip"
    if output_path.exists():
        logger.info(f"Shona Bible already exists at {output_path}")
        return 1  # Returning 1 to signify file was processed
        
    url = "https://ebible.org/Scriptures/sna-snaBSU.zip"
    logger.info(f"Downloading Shona Bible from {url}...")
    success = download_file(url, output_path)
    return 1 if success else 0

def main():
    ensure_dir(RAW_DATA_DIR)
    logger.info("Starting Shona dataset downloads...")
    
    stats = {}
    
    # 1. Hugging Face Datasets
    stats["JW300"] = get_jw300()
    stats["CC100"] = get_cc100()
    stats["FLEURS"] = get_fleurs()
    stats["MasakhaNER"] = get_masakhaner()
    stats["MasakhaNEWS"] = get_masakhanews()
    stats["NLLB_FLORES"] = get_nllb_flores()
    
    # 2. Raw File Downloads
    stats["Wikipedia Dump"] = get_wiki_dump()
    stats["eBible"] = get_shona_bible()
    
    # Summary
    logger.info("="*40)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("="*40)
    total_sentences = 0
    for name, count in stats.items():
        if name in ["Wikipedia Dump", "eBible"]:
            status = "Success" if count > 0 else "Failed"
            logger.info(f"{name}: {status}")
        else:
            logger.info(f"{name}: {count} sentences")
            total_sentences += count
            
    logger.info(f"Total sentences collected from HF: {total_sentences}")
    logger.info("All operations completed.")

if __name__ == "__main__":
    main()
