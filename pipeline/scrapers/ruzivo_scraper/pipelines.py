"""
Ruzivo Scrapy Item Pipelines
=============================
Order of execution:
  1. TextCleaningPipeline   — fix encoding, strip noise, count words
  2. LanguageFilterPipeline — detect language, drop non-Shona
  3. DeduplicationPipeline  — drop exact-body duplicates (in-memory per run)
  4. JsonExportPipeline     — append to .jsonl in data/raw/text/
"""

import json
import re
from pathlib import Path

import ftfy
from langdetect import detect, LangDetectException
from loguru import logger
from scrapy.exceptions import DropItem


# ── 1. Text Cleaning ──────────────────────────────────────────────────────────

class TextCleaningPipeline:
    """Fix encoding, normalise whitespace, enforce minimum word count."""

    MIN_WORDS = 30  # articles shorter than this are not useful for training

    # Patterns to strip
    _AD_PATTERNS = re.compile(
        r"(READ (MORE|ALSO)[:\-].*?[\.\n]|"        # "Read more: ..."
        r"ALSO READ[:\-].*?[\.\n]|"
        r"Subscribe to our.*?[\.\n]|"              # subscription nags
        r"Follow us on.*?[\.\n]|"
        r"WhatsApp.*?[\.\n]|"
        r"Copyright.*?Zimbabwe.*?[\.\n]|"
        r"\bAdvertisement\b.*?[\.\n])",
        re.IGNORECASE | re.DOTALL,
    )

    def process_item(self, item, spider):
        body = item.get("body", "")
        title = item.get("title", "")

        # Fix mojibake / encoding issues
        body = ftfy.fix_text(body)
        title = ftfy.fix_text(title)

        # Strip editorial noise
        body = self._AD_PATTERNS.sub("", body)

        # Normalise whitespace
        body = re.sub(r"\s+", " ", body).strip()
        title = re.sub(r"\s+", " ", title).strip()

        word_count = len(body.split())
        if word_count < self.MIN_WORDS:
            raise DropItem(
                f"[clean] Too short ({word_count} words): {item.get('url')}"
            )

        item["body"] = body
        item["title"] = title
        item["word_count"] = word_count
        return item


# ── 2. Language Detection & Filtering ────────────────────────────────────────

class LanguageFilterPipeline:
    """
    Detect article language and drop non-Shona articles.

    langdetect does not have a dedicated 'sn' (Shona) model.
    In practice, Shona text is often misclassified as 'af' (Afrikaans),
    'sw' (Swahili), 'mg' (Malagasy), or 'so' (Somali).

    Strategy:
    - For kwayedza source: trust the source, keep everything not clearly English
    - For herald_shona source: apply stricter language detection
    - Anything confidently classified as 'en' with no Shona markers is dropped
    """

    # Shona function words and common particles
    # If a text contains these, it is very likely Shona regardless of langdetect
    _SHONA_MARKERS = re.compile(
        r"\b(kuti|uye|apo|pane|nemusi|zvake|munhu|kuita|vakati|"
        r"vanoti|vakaitwa|pakaitika|kusiya|zvino|mushure|"
        r"mujeri|dare|mhosva|vanodaro|vakaudza|wakati|zvimwe|"
        r"musha|mwana|baba|amai|sekuru|ambuya|hurumende|nyika|"
        r"nzvimbo|mwedzi|gore|zuva|nguva|nhengo|bonde|mvura)\b",
        re.IGNORECASE,
    )

    _CLEARLY_ENGLISH = re.compile(
        r"\b(the|and|that|have|for|not|with|you|this|but|his|they|"
        r"from|she|will|one|all|would|there|their|what|about|which)\b",
        re.IGNORECASE,
    )

    def process_item(self, item, spider):
        body = item.get("body", "")
        source = item.get("source", "")

        # Count Shona markers
        shona_hits = len(self._SHONA_MARKERS.findall(body))
        english_hits = len(self._CLEARLY_ENGLISH.findall(body))

        # If strong Shona signal, keep regardless of langdetect
        if shona_hits >= 3:
            item["language"] = "sn"
            return item

        # Trusted Shona-only source — be lenient
        if source == "kwayedza":
            try:
                lang = detect(body)
            except LangDetectException:
                lang = "unknown"
            # Drop only if confidently English with no Shona markers
            if lang == "en" and shona_hits == 0:
                raise DropItem(
                    f"[lang] Confirmed English from kwayedza, skipping: {item.get('url')}"
                )
            item["language"] = lang
            return item

        # Mixed-source spider — stricter filter
        if english_hits > shona_hits * 3 and shona_hits < 2:
            raise DropItem(
                f"[lang] Likely English ({english_hits} en / {shona_hits} sn): "
                f"{item.get('url')}"
            )

        try:
            lang = detect(body)
        except LangDetectException:
            lang = "unknown"

        if lang == "en" and shona_hits == 0:
            raise DropItem(
                f"[lang] Confirmed English, no Shona markers: {item.get('url')}"
            )

        item["language"] = lang
        return item


# ── 3. Deduplication ──────────────────────────────────────────────────────────

class DeduplicationPipeline:
    """In-memory URL deduplication within a single crawl run."""

    def __init__(self):
        self._seen_urls: set = set()

    def process_item(self, item, spider):
        url = item.get("url", "")
        if url in self._seen_urls:
            raise DropItem(f"[dedup] Duplicate URL: {url}")
        self._seen_urls.add(url)
        return item


# ── 4. JSON Export ────────────────────────────────────────────────────────────

class JsonExportPipeline:
    """
    Write each accepted item as a JSON line to data/raw/text/<source>.jsonl.
    Creates the file if it does not exist; appends if it does.
    """

    _OUTPUT_DIR = Path("../../data/raw/text")

    def __init__(self):
        self._files: dict = {}
        self._counts: dict = {}

    def open_spider(self, spider):
        self._OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"[export] Output directory: {self._OUTPUT_DIR.resolve()}")

    def close_spider(self, spider):
        for source, f in self._files.items():
            count = self._counts.get(source, 0)
            logger.info(f"[export] {source}: {count} articles written")
            f.close()

    def process_item(self, item, spider):
        source = item.get("source", "unknown")
        if source not in self._files:
            path = self._OUTPUT_DIR / f"{source}.jsonl"
            self._files[source] = open(path, "a", encoding="utf-8")
            self._counts[source] = 0
            logger.info(f"[export] Opened {path}")

        self._files[source].write(
            json.dumps(dict(item), ensure_ascii=False) + "\n"
        )
        self._counts[source] = self._counts.get(source, 0) + 1
        return item
