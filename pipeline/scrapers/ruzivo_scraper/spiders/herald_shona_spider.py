"""
Herald Online — Shona-Tagged Articles Spider
=============================================
Source  : https://www.heraldonline.co.zw/
Target  : Articles tagged with Shona language markers beyond Kwayedza
Language: Shona (sn) — filtered by langdetect post-download
Output  : data/raw/text/herald_shona.jsonl

The Herald Online publishes some Shona content outside the Kwayedza
section (opinion pieces, community submissions, cultural features).
This spider targets those by scraping the main archive and applying
language detection — keeping only confirmed Shona articles.
"""

import re
from datetime import datetime, timezone
from urllib.parse import urljoin

import scrapy

from ruzivo_scraper.items import ShonaTextItem


class HeraldShonaSpider(scrapy.Spider):
    name = "herald_shona"
    allowed_domains = ["heraldonline.co.zw"]

    # ── Seed URLs — Herald sections most likely to carry Shona articles ───
    start_urls = [
        # Kwayedza main (belt-and-suspenders — catches anything missed by
        # the dedicated kwayedza spider)
        "https://www.heraldonline.co.zw/category/kwayedza/",
        # Opinion and community sections (sometimes bilingual)
        "https://www.heraldonline.co.zw/tag/shona/",
        "https://www.heraldonline.co.zw/tag/chiShona/",
        "https://www.heraldonline.co.zw/tag/indigenous-languages/",
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 3.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DEPTH_LIMIT": 15,
    }

    _BODY_SELECTORS = [
        ".entry-content",
        ".post-content",
        ".td-post-content",
        ".tdb-block-inner",
        "article .content",
        ".article-body",
    ]

    _SKIP_PATTERNS = re.compile(
        r"/(category|tag|author|page|wp-|feed|search|attachment|"
        r"contact|about|advertise|single-category)/",
        re.IGNORECASE,
    )

    _BASE = "https://heraldonline.co.zw"

    def parse(self, response):
        """Parse listing/tag page: collect article links + paginate."""

        links = response.css(
            "h1 a::attr(href), h2 a::attr(href), h3 a::attr(href), "
            ".entry-title a::attr(href), .td-module-title a::attr(href), "
            "article a::attr(href)"
        ).getall()

        seen = set()
        for href in links:
            url = urljoin(response.url, href)
            if (
                url not in seen
                and "heraldonline.co.zw" in url
                and not self._SKIP_PATTERNS.search(url)
                and url.rstrip("/") != self._BASE
            ):
                seen.add(url)
                yield scrapy.Request(url, callback=self.parse_article)

        # Pagination
        next_page = response.css(
            "a.next.page-numbers::attr(href), "
            ".nav-next a::attr(href)"
        ).get()
        if next_page:
            yield scrapy.Request(
                urljoin(response.url, next_page), callback=self.parse
            )

    def parse_article(self, response):
        """Parse article — language detection happens in the pipeline."""

        title = (
            response.css("h1.entry-title::text, h1.tdb-title-text::text, h1::text")
            .get(default="")
            .strip()
        )
        if not title:
            title = response.css(
                "meta[property='og:title']::attr(content)"
            ).get(default="")

        body = ""
        for selector in self._BODY_SELECTORS:
            raw = response.css(
                f"{selector} p::text, {selector} p *::text"
            ).getall()
            body = " ".join(t.strip() for t in raw if t.strip())
            if len(body.split()) >= 20:
                break

        if len(body.split()) < 20:
            body = response.css(
                "meta[property='og:description']::attr(content)"
            ).get(default="")

        if not body.strip():
            return

        date = response.css(
            "time::attr(datetime), "
            "meta[property='article:published_time']::attr(content)"
        ).get(default="")

        yield ShonaTextItem(
            source="herald_shona",
            section="general",
            url=response.url,
            title=title,
            body=body,
            date=date,
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
