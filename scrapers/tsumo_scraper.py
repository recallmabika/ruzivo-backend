import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PROJECT_ROOT = Path(r'c:\Users\recal\Desktop\Level 2.2 Project\ruzivo')
OUTPUT_FILE = PROJECT_ROOT / 'data' / 'raw' / 'tsumo_nemadimikira.jsonl'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 RuzivoBot/1.0'
}
DELAY = 1.0
MAX_RETRIES = 3

SOURCES = [
    {
        "url": "https://zimboriginal.com/shona-proverbs-tsumo/",
        "type": "tsumo"
    },
    {
        "url": "https://zimboriginal.com/shona-idioms-madimikira/",
        "type": "dimikira"
    }
]

class TsumoScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a page with rate limiting and retries."""
        for attempt in range(MAX_RETRIES):
            try:
                time.sleep(DELAY)
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {url}: {e}")
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"Failed to fetch {url} after {MAX_RETRIES} attempts.")
                    return None
                time.sleep(DELAY * 2)
        return None

    def parse_zimboriginal_tsumo(self, soup: BeautifulSoup, url: str, item_type: str) -> List[Dict]:
        """Parse content from zimboriginal or similar sites."""
        items = []
        # Speculative selector logic based on common WP blog formats
        # e.g. <p><strong>Proverb:</strong> ... <br> <strong>Meaning:</strong> ...</p>
        
        paragraphs = soup.select('div.entry-content p, article p')
        for p in paragraphs:
            text = p.get_text(separator=' | ').strip()
            # Try to identify pairs
            if ':' in text or '-' in text:
                # Basic heuristic split
                parts = text.split(' | ', 1) if ' | ' in text else text.split(':', 1) if ':' in text else text.split('-', 1)
                if len(parts) == 2:
                    phrase = parts[0].strip()
                    meaning = parts[1].strip()
                    # Filter out short meaningless parses
                    if len(phrase) > 5 and len(meaning) > 5:
                        items.append({
                            "proverb": phrase,
                            "meaning": meaning,
                            "type": item_type,
                            "source": url
                        })
        return items

    def scrape_source(self, source_info: Dict) -> List[Dict]:
        """Scrape a particular source."""
        url = source_info['url']
        item_type = source_info['type']
        logger.info(f"Scraping {url} for {item_type}...")
        
        soup = self.fetch_page(url)
        if not soup:
            return []
            
        return self.parse_zimboriginal_tsumo(soup, url, item_type)

    def run(self) -> None:
        """Main scraping process."""
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        all_items = []
        
        for source in tqdm(SOURCES, desc="Processing Sources"):
            items = self.scrape_source(source)
            all_items.extend(items)
            logger.info(f"Found {len(items)} items from {source['url']}")

        if all_items:
            success_count = 0
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                for item in all_items:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
                    success_count += 1
            logger.info(f"Scraping completed. Successfully saved {success_count} items to {OUTPUT_FILE}.")
        else:
            logger.warning("No items were found. Selectors might need adjustment based on actual page HTML.")


def main():
    logger.info("Starting Tsumo nemadimikira Scraper...")
    scraper = TsumoScraper()
    scraper.run()
    logger.info("Tsumo nemadimikira Scraper finished.")

if __name__ == "__main__":
    main()
