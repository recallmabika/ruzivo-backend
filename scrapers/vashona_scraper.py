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
OUTPUT_FILE = PROJECT_ROOT / 'data' / 'raw' / 'vashona_dictionary.jsonl'
BASE_URL = 'https://www.vashona.com'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 RuzivoBot/1.0'
}
DELAY = 1.0
MAX_RETRIES = 3

class VaShonaScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.rp = RobotFileParser()
        self._setup_robots_txt()
        
    def _setup_robots_txt(self) -> None:
        """Fetch and parse robots.txt."""
        robots_url = urljoin(BASE_URL, '/robots.txt')
        try:
            self.rp.set_url(robots_url)
            self.rp.read()
            logger.info("Successfully loaded robots.txt")
        except Exception as e:
            logger.warning(f"Could not load robots.txt: {e}")

    def _can_fetch(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt."""
        if not self.rp.modified():
            return True
        return self.rp.can_fetch(HEADERS['User-Agent'], url)

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a page with rate limiting and retries."""
        if not self._can_fetch(url):
            logger.warning(f"Robots.txt disallows fetching {url}")
            return None

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

    def scrape_word_entry(self, word_url: str) -> Optional[Dict]:
        """Scrape data from a specific word entry page."""
        soup = self.fetch_page(word_url)
        if not soup:
            return None

        try:
            # Note: These selectors are speculative and should be adjusted based on actual site structure
            word_elem = soup.select_one('h1.word-title, .word-header h1')
            word = word_elem.text.strip() if word_elem else ''

            def_elem = soup.select_one('.definition, .word-definition')
            definition = def_elem.text.strip() if def_elem else ''

            pos_elem = soup.select_one('.part-of-speech, .pos')
            pos = pos_elem.text.strip() if pos_elem else ''

            examples = []
            for ex_elem in soup.select('.example-sentence, ul.examples li'):
                examples.append(ex_elem.text.strip())

            if word and definition:
                return {
                    "word": word,
                    "definition": definition,
                    "pos": pos,
                    "examples": examples,
                    "source": "vashona"
                }
        except Exception as e:
            logger.error(f"Error parsing word entry at {word_url}: {e}")
            
        return None

    def get_all_word_links(self) -> List[str]:
        """Discover dictionary entry links."""
        # Speculative discovery logic: crawl alphabet/pagination index
        links = []
        letters = 'abcdefghijklmnopqrstuvwxyz'
        logger.info("Discovering word URLs...")
        for letter in tqdm(letters, desc="Letters"):
            page_num = 1
            while True:
                index_url = urljoin(BASE_URL, f"/dictionary/browse/{letter}?page={page_num}")
                soup = self.fetch_page(index_url)
                if not soup:
                    break
                
                # Speculative selector for word links in list
                word_links = soup.select('.word-list a, .dictionary-index a')
                if not word_links:
                    break
                    
                for a_tag in word_links:
                    href = a_tag.get('href')
                    if href:
                        links.append(urljoin(BASE_URL, href))
                
                # Check if there is a next page
                next_page = soup.select_one('.pagination .next, a[rel="next"]')
                if not next_page:
                    break
                page_num += 1
                
        return list(set(links))

    def run(self) -> None:
        """Main scraping process."""
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # In a real run, uncomment link discovery. For demonstration, we simulate if empty.
        word_links = self.get_all_word_links()
        if not word_links:
            logger.warning("No links discovered. Selectors may need adjustment. Proceeding with dummy discovery check.")
            # For demonstration, we could add seed URLs here.
        
        success_count = 0
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for url in tqdm(word_links, desc="Scraping words"):
                entry = self.scrape_word_entry(url)
                if entry:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                    success_count += 1
                    
        logger.info(f"Scraping completed. Successfully scraped {success_count} words.")


def main():
    logger.info("Starting VaShona Scraper...")
    scraper = VaShonaScraper()
    scraper.run()
    logger.info("VaShona Scraper finished.")

if __name__ == "__main__":
    main()
