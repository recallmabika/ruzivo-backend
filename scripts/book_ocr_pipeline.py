"""
Ruzivo AI — Book OCR and Text Extraction Pipeline
=================================================
Extracts text from scanned book PDFs and images for the Ruzivo Shona AI project.

Supports:
  - PDF files (both text-based and scanned/image-based)
  - Image files (JPG, PNG, TIFF)
  - DOCX files (Microsoft Word)
  - TXT files (plain text, just copies)

Usage:
    python book_ocr_pipeline.py --input <path_to_books_folder> --output <output_folder>
    python book_ocr_pipeline.py  # Uses default paths

Dependencies:
    pip install PyMuPDF pytesseract Pillow python-docx tqdm

Note: Tesseract OCR must be installed on your system.
    - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
    - After install, ensure tesseract.exe is on PATH or set TESSERACT_PATH below.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Reconfigure stdout/stderr to UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm not available
    def tqdm(iterable, **kwargs):
        return iterable

# Optional: Set Tesseract path if not on system PATH
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

PROJECT_ROOT = Path(r"c:\Users\recal\Desktop\Level 2.2 Project\ruzivo")
DEFAULT_INPUT = PROJECT_ROOT / "data" / "books_ocr"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "raw"

# Supported file extensions
PDF_EXTENSIONS = {".pdf"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"}
DOCX_EXTENSIONS = {".docx"}
TEXT_EXTENSIONS = {".txt"}
ALL_EXTENSIONS = PDF_EXTENSIONS | IMAGE_EXTENSIONS | DOCX_EXTENSIONS | TEXT_EXTENSIONS


def extract_text_from_pdf(pdf_path: Path) -> list[dict]:
    """
    Extract text from a PDF file.

    First tries direct text extraction (for text-based PDFs).
    If a page has no extractable text, falls back to OCR via Tesseract.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        List of dicts with keys: text, page, source, method
    """
    results = []
    doc = fitz.open(str(pdf_path))

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Try direct text extraction first
        text = page.get_text("text").strip()

        if len(text) > 20:
            # Text-based PDF — direct extraction worked
            results.append({
                "text": text,
                "page": page_num + 1,
                "source": pdf_path.stem,
                "method": "direct_extraction"
            })
        else:
            # Scanned page — fall back to OCR
            try:
                import pytesseract

                # Render page as image at 300 DPI for good OCR quality
                mat = fitz.Matrix(300 / 72, 300 / 72)
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # OCR with Tesseract (using Shona language pack if available, else English)
                try:
                    ocr_text = pytesseract.image_to_string(img, lang="sna")
                except Exception:
                    # Fall back to English OCR if Shona language pack not installed
                    ocr_text = pytesseract.image_to_string(img, lang="eng")

                ocr_text = ocr_text.strip()
                if ocr_text:
                    results.append({
                        "text": ocr_text,
                        "page": page_num + 1,
                        "source": pdf_path.stem,
                        "method": "ocr_tesseract"
                    })
            except ImportError:
                print(f"  ⚠ Page {page_num + 1}: No text found and pytesseract not installed. Skipping OCR.")
            except Exception as e:
                print(f"  ⚠ Page {page_num + 1}: OCR failed: {e}")

    doc.close()
    return results


def extract_text_from_image(image_path: Path) -> list[dict]:
    """
    Extract text from an image file using OCR.

    Args:
        image_path: Path to the image file.

    Returns:
        List of dicts with keys: text, page, source, method
    """
    try:
        import pytesseract
    except ImportError:
        print(f"  ⚠ pytesseract not installed. Cannot OCR {image_path.name}")
        return []

    try:
        img = Image.open(str(image_path))

        try:
            ocr_text = pytesseract.image_to_string(img, lang="sna")
        except Exception:
            ocr_text = pytesseract.image_to_string(img, lang="eng")

        ocr_text = ocr_text.strip()
        if ocr_text:
            return [{
                "text": ocr_text,
                "page": 1,
                "source": image_path.stem,
                "method": "ocr_tesseract"
            }]
    except Exception as e:
        print(f"  ⚠ Failed to OCR {image_path.name}: {e}")

    return []


def extract_text_from_docx(docx_path: Path) -> list[dict]:
    """
    Extract text from a Microsoft Word (.docx) file.

    Args:
        docx_path: Path to the DOCX file.

    Returns:
        List of dicts with keys: text, page, source, method
    """
    try:
        from docx import Document
    except ImportError:
        print(f"  ⚠ python-docx not installed. Cannot read {docx_path.name}")
        return []

    try:
        doc = Document(str(docx_path))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        full_text = "\n".join(paragraphs)

        if full_text:
            return [{
                "text": full_text,
                "page": 1,
                "source": docx_path.stem,
                "method": "python_docx"
            }]
    except Exception as e:
        print(f"  ⚠ Failed to read {docx_path.name}: {e}")

    return []


def extract_text_from_txt(txt_path: Path) -> list[dict]:
    """
    Read text from a plain text file.

    Args:
        txt_path: Path to the TXT file.

    Returns:
        List of dicts with keys: text, page, source, method
    """
    try:
        # Try multiple encodings
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                text = txt_path.read_text(encoding=encoding).strip()
                if text:
                    return [{
                        "text": text,
                        "page": 1,
                        "source": txt_path.stem,
                        "method": "plain_text"
                    }]
                break
            except UnicodeDecodeError:
                continue
    except Exception as e:
        print(f"  ⚠ Failed to read {txt_path.name}: {e}")

    return []


def split_into_sentences(text: str) -> list[str]:
    """
    Split a block of text into individual sentences.

    Uses simple heuristics suitable for Shona text:
    - Split on period, question mark, exclamation mark followed by space or newline
    - Also split on newlines (paragraphs)

    Args:
        text: The input text block.

    Returns:
        List of sentences.
    """
    import re

    # First split on newlines to get paragraphs
    paragraphs = text.split("\n")

    sentences = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Split on sentence-ending punctuation followed by space
        parts = re.split(r'(?<=[.!?])\s+', para)
        for part in parts:
            part = part.strip()
            if len(part) > 5:  # Minimum sentence length
                sentences.append(part)

    return sentences


def process_books(
    input_dir: Path,
    output_dir: Path,
    split_sentences: bool = True
) -> None:
    """
    Process all book files in the input directory and extract text.

    Args:
        input_dir: Directory containing book files (PDFs, images, DOCX, TXT).
        output_dir: Directory to save extracted text as JSONL.
        split_sentences: If True, split extracted text into individual sentences.
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all supported files
    files = []
    for ext in ALL_EXTENSIONS:
        files.extend(input_dir.glob(f"**/*{ext}"))

    if not files:
        print(f"\n⚠ No supported files found in {input_dir}")
        print(f"  Supported formats: {', '.join(sorted(ALL_EXTENSIONS))}")
        print(f"\n📁 Place your book files (PDFs, images, DOCX, TXT) in:")
        print(f"   {input_dir}")
        print(f"\n   Then run this script again.")
        return

    print(f"\n📚 Found {len(files)} file(s) to process:")
    for f in files:
        print(f"   • {f.name} ({f.suffix})")

    # Process each file
    all_results = []
    stats = {}

    for file_path in tqdm(files, desc="Processing books"):
        print(f"\n📖 Processing: {file_path.name}")

        ext = file_path.suffix.lower()
        if ext in PDF_EXTENSIONS:
            results = extract_text_from_pdf(file_path)
        elif ext in IMAGE_EXTENSIONS:
            results = extract_text_from_image(file_path)
        elif ext in DOCX_EXTENSIONS:
            results = extract_text_from_docx(file_path)
        elif ext in TEXT_EXTENSIONS:
            results = extract_text_from_txt(file_path)
        else:
            continue

        # Split into sentences if requested
        if split_sentences:
            sentence_results = []
            for r in results:
                sents = split_into_sentences(r["text"])
                for sent in sents:
                    sentence_results.append({
                        "text": sent,
                        "page": r["page"],
                        "source": r["source"],
                        "method": r["method"]
                    })
            results = sentence_results

        stats[file_path.name] = len(results)
        all_results.extend(results)
        print(f"   ✓ Extracted {len(results)} {'sentences' if split_sentences else 'pages'}")

    # Save all results
    output_file = output_dir / "books_extracted.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for i, item in enumerate(all_results):
            item["id"] = i
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # Print summary
    print("\n" + "=" * 60)
    print("📊 BOOK EXTRACTION SUMMARY")
    print("=" * 60)
    for name, count in stats.items():
        print(f"   {name}: {count:,} sentences")
    print(f"\n   TOTAL: {len(all_results):,} sentences")
    print(f"   Output: {output_file}")
    print("=" * 60)


def main():
    """Main entry point for the book OCR pipeline."""
    parser = argparse.ArgumentParser(
        description="Ruzivo AI — Book OCR and Text Extraction Pipeline"
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Input directory containing book files (default: {DEFAULT_INPUT})"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output directory for extracted text (default: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        "--no-split",
        action="store_true",
        help="Don't split text into individual sentences"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("📚 RUZIVO AI — BOOK OCR & TEXT EXTRACTION PIPELINE")
    print("=" * 60)
    print(f"Input directory:  {args.input}")
    print(f"Output directory: {args.output}")

    process_books(
        input_dir=args.input,
        output_dir=args.output,
        split_sentences=not args.no_split
    )


if __name__ == "__main__":
    main()
