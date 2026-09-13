import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Any
from tqdm import tqdm

# Configure stdout for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(r'c:\Users\recal\Desktop\Level 2.2 Project\ruzivo')

class ShonaCleaner:
    """
    A comprehensive text cleaning pipeline for Shona language data.
    """
    def __init__(self):
        # 300 Common English words for contamination detection
        self.english_words: Set[str] = {
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
            "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
            "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
            "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
            "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
            "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
            "even", "new", "want", "because", "any", "these", "give", "day", "most", "us",
            "are", "is", "was", "were", "been", "has", "had", "does", "did", "doing",
            "am", "shall", "should", "may", "might", "must", "can't", "don't", "won't", "isn't",
            "aren't", "wasn't", "weren't", "hasn't", "haven't", "hadn't", "doesn't", "didn't", "couldn't", "shouldn't",
            "wouldn't", "mightn't", "mustn't", "it's", "he's", "she's", "that's", "there's", "what's", "who's",
            "where", "why", "how", "many", "much", "more", "most", "few", "less", "least",
            "very", "too", "quite", "really", "almost", "always", "never", "sometimes", "often", "usually",
            "here", "there", "every", "everywhere", "somewhere", "nowhere", "anywhere", "everything", "something", "nothing",
            "anything", "everyone", "someone", "no one", "anyone", "everybody", "somebody", "nobody", "anybody", "yes",
            "no", "ok", "okay", "yeah", "nope", "please", "thank", "thanks", "hello", "hi",
            "bye", "goodbye", "morning", "afternoon", "evening", "night", "today", "tomorrow", "yesterday", "week",
            "month", "year", "century", "decade", "millennium", "second", "minute", "hour", "clock", "watch",
            "time", "date", "calendar", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
            "november", "december", "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "eleven", "twelve", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
            "eighty", "ninety", "hundred", "thousand", "million", "billion", "first", "second", "third", "last",
            "next", "previous", "before", "after", "during", "while", "until", "since", "from", "to",
            "between", "among", "through", "across", "over", "under", "above", "below", "beside", "behind",
            "front", "back", "left", "right", "top", "bottom", "up", "down", "in", "out",
            "inside", "outside", "on", "off", "with", "without", "by", "about", "against", "for",
            "of", "at", "as", "like", "unlike", "same", "different", "similar", "opposite", "such",
            "so", "too", "very", "much", "many", "more", "most", "less", "least", "few",
            "fewer", "fewest", "all", "both", "half", "quarter", "whole", "part", "some", "any",
            "none", "every", "each", "other", "another", "such", "what", "which", "who", "whom"
        }

        # 200+ Common Shona words for language quality checks
        self.shona_words: Set[str] = {
            "ndi", "uri", "ari", "tiri", "muri", "vari", "kuti", "zvino", "asi", "kana",
            "nekuti", "pamwe", "here", "chete", "zvakare", "uye", "kunyange", "kudai", "saka", "nokuda",
            "vanhu", "munhu", "mwana", "baba", "amai", "imba", "mvura", "zuva", "usiku", "mangwanani",
            "masikati", "nyika", "rudo", "moto", "shiri", "hove", "mbudzi", "mombe", "sadza", "doro",
            "mukadzi", "murume", "musikana", "mukomana", "vakadzi", "varume", "vasikana", "vakomana", "imbwa", "katsi",
            "huku", "nguruve", "zvinhu", "chinhu", "chikoro", "munda", "muti", "miti", "sango", "rwizi",
            "gomo", "makomo", "matombo", "ivhu", "mhepo", "denga", "nzira", "motokari", "bhazi", "chitima",
            "ndege", "bhasikoro", "mari", "basa", "musha", "dhorobha", "guta", "mambo", "ishe", "sabhuku",
            "nyama", "chingwa", "mukaka", "tii", "shuga", "munyu", "mhiripiri", "banga", "bhanditi", "bhatye",
            "bhutsu", "jira", "hembe", "ngowani", "wachi", "foni", "redhiyo", "ruzivo", "mufaro", "kusuwa",
            "hasha", "kutya", "ushingi", "simba", "utera", "hupenyu", "rufu", "nzara", "nyota", "kurwara",
            "hutano", "mushonga", "chiremba", "nesi", "chipatara", "mufundisi", "kereke", "chitendero", "mwari", "ngirozi",
            "mweya", "dhimoni", "uroyi", "muroyi", "n'anga", "chivanhu", "tsika", "magumo", "mavambo", "mukati",
            "panze", "mberi", "kumashure", "kumusoro", "kuzasi", "pedyo", "kure", "nhasi", "nezuro", "mangwana",
            "svondo", "mwedzi", "gore", "nguva", "sekondi", "miniti", "awa", "chimwe", "zvimwe", "zvese",
            "vese", "tose", "mose", "ndoga", "oga", "toga", "moga", "poga", "zvega", "ini",
            "iwe", "iye", "isu", "imi", "ivo", "angu", "ako", "ake", "edu", "enyu",
            "avo", "mumba", "pachikoro", "kubasa", "kumunda", "kutsime", "parwizi", "kugomo", "musango", "pachiteshi",
            "kumusha", "kumba", "zvikuru", "zvishoma", "zvakanaka", "zvakaipa", "zvinonaka", "zvinovava", "zvinotapira", "zvinopisa",
            "zvinotonhora", "kurema", "kureruka", "kutsva", "kusakara", "kudyara", "kukohwa", "kurima", "kufudza", "kubika",
            "kudya", "kunwa", "kugeza", "kupfeka", "kubvisa", "kurara", "kumuka", "kufamba", "kumhanya", "kusvetuka",
            "kutaura", "kunyarara", "kuseka", "kuchema", "kuimba", "kutamba", "kushanda", "kuzorora", "kudzidza", "kufunga",
            "kuziva", "kukanganwa", "kurangarira", "kubvunza", "kupindura", "kubatsira", "kunetsa", "kupa", "kutora", "kuba",
            "kutenga", "kutengesa", "kubhadhara", "kurasika", "kuwana", "kutsvaga", "kurasira", "kuunganidza", "kugovera", "kuchengeta",
            "kurasa", "kudzoka", "kuenda", "kuuya", "kusvika", "kubva", "kupinda", "kubuda", "kukura", "kuchembera"
        }

        # Shona n-gram patterns for quality scoring
        self.shona_patterns = ['sv', 'zv', 'ch', 'sh', 'dz', 'mh', 'nh', 'nz', 'mb', 'nd', 'ng']
        self.shona_prefixes = ['va', 'mu', 'chi', 'ma', 'zvi', 'ru', 'ka', 'tu', 'u', 'ku', 'pa', 'ku', 'mu']

        # Precompile regexes
        self.re_boilerplate = re.compile(
            r'(https?://\S+|www\.\S+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|@[a-zA-Z0-9_]+|<[^>]+>)'
        )
        self.re_whitespace = re.compile(r'\s+')
        self.re_non_alpha = re.compile(r'[^a-zA-Z\s\']')

    def remove_english_contamination(self, text: str) -> bool:
        """
        Detects if a sentence is predominantly English.
        Returns True if the text should be kept (not contaminated), False otherwise.
        """
        words = self.re_non_alpha.sub('', text.lower()).split()
        if not words:
            return False

        eng_count = sum(1 for w in words if w in self.english_words)
        
        # If > 40% of words are common English words, flag as contaminated
        if (eng_count / len(words)) > 0.4:
            return False
            
        return True

    def normalize_orthography(self, text: str) -> str:
        """
        Standardizes Shona orthography.
        """
        # Normalize Unicode to NFC form
        text = unicodedata.normalize('NFC', text)
        
        # Standardize quotes and apostrophes
        text = text.replace('‘', "'").replace('’', "'").replace('`', "'")
        text = text.replace('“', '"').replace('”', '"')
        
        # Dialectal standardizations (simplified mapping, carefully applied)
        # Note: In a production system, this requires more context so we don't over-normalize.
        # Here we just clean up excessive whitespace and fix simple OCR issues like l -> I if surrounded by caps etc.
        # But we'll stick to safe standardizations.
        
        # Remove excessive whitespace
        text = self.re_whitespace.sub(' ', text).strip()
        
        return text

    def remove_boilerplate(self, text: str) -> str:
        """
        Removes web boilerplate, URLs, emails, HTML.
        """
        text = self.re_boilerplate.sub('', text)
        text = self.re_whitespace.sub(' ', text).strip()
        return text

    def filter_quality(self, text: str) -> bool:
        """
        Filters out low-quality text based on length, caps, numbers, etc.
        Returns True if the text is good quality, False if it should be removed.
        """
        words = text.split()
        num_words = len(words)
        
        # Length check
        if num_words < 5 or num_words > 200:
            return False
            
        # All caps or all numbers
        if text.isupper() or text.isdigit():
            return False
            
        # Excessive punctuation check
        num_chars = len(text)
        num_punct = sum(1 for c in text if not c.isalnum() and not c.isspace())
        if num_chars > 0 and (num_punct / num_chars) > 0.2:
            return False
            
        return True

    def detect_shona_quality(self, text: str) -> float:
        """
        Scores how 'Shona' a sentence is (0.0 to 1.0).
        """
        words = self.re_non_alpha.sub('', text.lower()).split()
        if not words:
            return 0.0

        score = 0.0
        max_possible_score = len(words) * 2

        for w in words:
            # Check for exact Shona word matches
            if w in self.shona_words:
                score += 2.0
            else:
                # Check for Shona morphological patterns
                matched = False
                for prefix in self.shona_prefixes:
                    if w.startswith(prefix) and len(w) > len(prefix) + 2:
                        score += 0.5
                        matched = True
                        break
                
                for pattern in self.shona_patterns:
                    if pattern in w:
                        score += 0.5
                        matched = True
                        break
                
                # Penalize non-Shona-like words (e.g., words with 'x', 'q', 'c' not in 'ch')
                if not matched and any(c in w for c in 'xq'):
                    score -= 1.0

        normalized_score = max(0.0, min(1.0, score / max_possible_score))
        return normalized_score

    def remove_duplicates(self, sentences: List[str]) -> List[str]:
        """
        Deduplicates sentences efficiently using exact matching and normalized token sets.
        """
        seen_exact = set()
        seen_signatures = set()
        final_sentences = []

        for sentence in sentences:
            # Exact match check
            normalized_str = sentence.strip().lower()
            if normalized_str in seen_exact:
                continue
            seen_exact.add(normalized_str)

            # Fast signature check using sorted tokens
            tokens = [t for t in normalized_str.split() if len(t) > 1]
            if len(tokens) >= 3:
                sig = " ".join(sorted(tokens))
                if sig in seen_signatures:
                    continue
                seen_signatures.add(sig)

            final_sentences.append(sentence)

        return final_sentences


def clean_corpus(input_dir: Path, output_dir: Path) -> None:
    """
    Main pipeline to clean the Shona corpus.
    """
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    cleaner = ShonaCleaner()
    
    files = list(input_dir.glob('*.jsonl'))
    if not files:
        print(f"No .jsonl files found in {input_dir}")
        return

    stats = {
        'total_lines_read': 0,
        'total_lines_written': 0,
        'rejected_english': 0,
        'rejected_quality': 0,
        'rejected_duplicates': 0,
        'source_stats': {}
    }

    for file_path in tqdm(files, desc="Processing files"):
        source = file_path.stem
        stats['source_stats'][source] = {'read': 0, 'written': 0}
        
        out_file_path = output_dir / f"{source}_clean.jsonl"
        
        lines_to_process = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stats['total_lines_read'] += 1
                stats['source_stats'][source]['read'] += 1
                try:
                    data = json.loads(line)
                    text = data.get('text', '')
                    if text:
                        lines_to_process.append(text)
                except json.JSONDecodeError:
                    continue

        # Pipeline execution
        cleaned_batch = []
        for text in lines_to_process:
            # 1. Boilerplate
            text = cleaner.remove_boilerplate(text)
            
            # 2. Orthography
            text = cleaner.normalize_orthography(text)
            
            # 3. Quality filter
            if not cleaner.filter_quality(text):
                stats['rejected_quality'] += 1
                continue
                
            # 4. English contamination
            if not cleaner.remove_english_contamination(text):
                stats['rejected_english'] += 1
                continue
                
            # 5. Shona quality score (optional filter, here we just keep it as metadata)
            quality_score = cleaner.detect_shona_quality(text)
            if quality_score < 0.1:  # Extremely low Shona-ness
                stats['rejected_english'] += 1
                continue
                
            cleaned_batch.append(text)

        # 6. Deduplication
        initial_len = len(cleaned_batch)
        cleaned_batch = cleaner.remove_duplicates(cleaned_batch)
        stats['rejected_duplicates'] += (initial_len - len(cleaned_batch))

        # Write output
        with open(out_file_path, 'w', encoding='utf-8') as f:
            for text in cleaned_batch:
                stats['total_lines_written'] += 1
                stats['source_stats'][source]['written'] += 1
                quality_score = cleaner.detect_shona_quality(text)
                
                out_data = {
                    'text': text,
                    'meta': {
                        'shona_quality_score': round(quality_score, 3)
                    }
                }
                f.write(json.dumps(out_data, ensure_ascii=False) + '\n')

    # Print Report
    print("\n" + "="*50)
    print("🧹 SHONA CORPUS CLEANING REPORT")
    print("="*50)
    print(f"Total Sentences Read:    {stats['total_lines_read']:,}")
    print(f"Total Sentences Written: {stats['total_lines_written']:,}")
    
    if stats['total_lines_read'] > 0:
        retention = (stats['total_lines_written'] / stats['total_lines_read']) * 100
        print(f"Retention Rate:          {retention:.2f}%")
        
    print("\nRejection Statistics:")
    print(f" - Low Quality/Format:   {stats['rejected_quality']:,}")
    print(f" - English Contaminated: {stats['rejected_english']:,}")
    print(f" - Duplicates Removed:   {stats['rejected_duplicates']:,}")
    
    print("\nPer-Source Statistics:")
    for source, s_stats in stats['source_stats'].items():
        read = s_stats['read']
        written = s_stats['written']
        pct = (written / read * 100) if read > 0 else 0
        print(f" - {source}: {read:,} -> {written:,} ({pct:.1f}%)")
    print("="*50)

if __name__ == "__main__":
    input_directory = PROJECT_ROOT / 'data' / 'raw'
    output_directory = PROJECT_ROOT / 'data' / 'cleaned'
    clean_corpus(input_directory, output_directory)
