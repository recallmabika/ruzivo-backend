"""
Kwayedza Shona Newspaper Spider
================================
Source  : https://www.heraldonline.co.zw/category/kwayedza/
          (kwayedza.co.zw redirects here)
Language: Shona (sn)
Content : News articles across all editorial sections
Output  : data/raw/text/kwayedza.jsonl
"""

import re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlencode

import scrapy

from ruzivo_scraper.items import ShonaTextItem


class KwayedzaSpider(scrapy.Spider):
    name = "kwayedza"
    allowed_domains = ["heraldonline.co.zw", "kwayedza.co.zw"]

    # ── All Kwayedza editorial sections ──────────────────────────────────────
    _BASE = "https://heraldonline.co.zw"
    _SECTIONS = [
        # Main category listing
        f"{_BASE}/category/kwayedza/",
        # Tag-based sections (Shona section names)
        f"{_BASE}/single-category/?tag=nhau-dzemuno&category=kwayedza",
        f"{_BASE}/single-category/?tag=nhau-dzevarimi&category=kwayedza",
        f"{_BASE}/single-category/?tag=nhau-dzedzidzo&category=kwayedza",
        f"{_BASE}/single-category/?tag=nhau-dzemitambo&category=kwayedza",
        f"{_BASE}/single-category/?tag=nhau-dzematare&category=kwayedza",
        f"{_BASE}/single-category/?tag=nhau-dzeutano&category=kwayedza",
        f"{_BASE}/single-category/?tag=denhe-reruzivo&category=kwayedza",
        f"{_BASE}/single-category/?tag=tishamwaridzane&category=kwayedza",
        f"{_BASE}/single-category/?tag=zvakanangana-nemadzimai&category=kwayedza",
        f"{_BASE}/single-category/?tag=kwayedza-dzidza&category=kwayedza",
    ]

    start_urls = _SECTIONS

    # Custom settings for this spider (override global settings)
    custom_settings = {
        "DOWNLOAD_DELAY": 2.5,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "DEPTH_LIMIT": 20,  # max pagination depth
    }

    # ── CSS selectors for article body (WordPress theme fallbacks) ────────────
    _BODY_SELECTORS = [
        ".entry-content",
        ".post-content",
        ".td-post-content",
        ".tdb-block-inner",
        "article .content",
        ".article-body",
        ".post-body",
        "div[class*='entry']",
        "div[class*='content']",
    ]

    # ── Patterns ──────────────────────────────────────────────────────────────
    # Article URLs on heraldonline look like /some-shona-slug/
    # We exclude admin, category, tag, page, media, and search URLs
    _SKIP_PATTERNS = re.compile(
        r"/(category|tag|author|page|wp-|feed|search|attachment|"
        r"contact|about|advertise|single-category)/",
        re.IGNORECASE,
    )

    def parse(self, response):
        """Parse a category/listing page: follow article links + paginate."""

        # ── Extract article links from listing page ───────────────────────
        article_links = response.css(
            "h1 a::attr(href), h2 a::attr(href), h3 a::attr(href), "
            ".entry-title a::attr(href), .td-module-title a::attr(href), "
            "article a::attr(href)"
        ).getall()

        seen = set()
        for href in article_links:
            url = urljoin(response.url, href)
            if (
                url not in seen
                and "heraldonline.co.zw" in url
                and not self._SKIP_PATTERNS.search(url)
                and url.rstrip("/") != self._BASE
            ):
                seen.add(url)
                yield scrapy.Request(url, callback=self.parse_article)

        # ── WordPress pagination ──────────────────────────────────────────
        # Handles both /page/N/ and ?page=N formats
        next_page = response.css(
            "a.next.page-numbers::attr(href), "
            ".nav-next a::attr(href), "
            "a[aria-label='Next Page']::attr(href)"
        ).get()

        if next_page:
            yield scrapy.Request(
                urljoin(response.url, next_page), callback=self.parse
            )

    def parse_article(self, response):
        """Parse a single article page and yield a ShonaTextItem."""

        # ── Title ─────────────────────────────────────────────────────────
        title = (
            response.css("h1.entry-title::text, h1.tdb-title-text::text, h1::text")
            .get(default="")
            .strip()
        )
        if not title:
            title = response.css("meta[property='og:title']::attr(content)").get(
                default=""
            )

        # ── Body text — try selectors in priority order ───────────────────
        body = ""
        for selector in self._BODY_SELECTORS:
            raw = response.css(f"{selector} p::text, {selector} p *::text").getall()
            body = " ".join(t.strip() for t in raw if t.strip())
            if len(body.split()) >= 20:
                break

        # Fallback: og:description meta tag
        if len(body.split()) < 20:
            body = response.css(
                "meta[property='og:description']::attr(content)"
            ).get(default="")

        if not body.strip():
            self.logger.debug(f"Empty body, skipping: {response.url}")
            return

        # ── Date ──────────────────────────────────────────────────────────
        date = (
            response.css(
                "time::attr(datetime), "
                "meta[property='article:published_time']::attr(content), "
                ".td-post-date time::attr(datetime)"
            ).get(default="")
        )

        # ── Detect section from URL ───────────────────────────────────────
        section = "general"
        for tag in [
            "nhau-dzemuno", "nhau-dzevarimi", "nhau-dzedzidzo",
            "nhau-dzemitambo", "nhau-dzematare", "nhau-dzeutano",
            "denhe-reruzivo", "tishamwaridzane",
            "zvakanangana-nemadzimai", "kwayedza-dzidza",
        ]:
            if tag in response.url:
                section = tag
                break

        yield ShonaTextItem(
            source="kwayedza",
            section=section,
            url=response.url,
            title=title,
            body=body,
            date=date,
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
