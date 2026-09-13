"""
Scrapy items for Ruzivo corpus pipeline.
"""
import scrapy


class ShonaTextItem(scrapy.Item):
    source = scrapy.Field()       # "kwayedza" | "herald_shona"
    section = scrapy.Field()      # editorial section slug e.g. "nhau-dzemuno"
    url = scrapy.Field()          # canonical article URL
    title = scrapy.Field()        # article headline
    body = scrapy.Field()         # full article body text
    date = scrapy.Field()         # ISO 8601 publish date string
    language = scrapy.Field()     # detected language code (set by pipeline)
    word_count = scrapy.Field()   # word count (set by pipeline)
    scraped_at = scrapy.Field()   # ISO 8601 scrape timestamp
