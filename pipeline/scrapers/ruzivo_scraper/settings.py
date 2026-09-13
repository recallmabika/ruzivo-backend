"""
Scrapy settings for ruzivo_scraper.
"""

BOT_NAME = "ruzivo_scraper"
SPIDER_MODULES = ["ruzivo_scraper.spiders"]
NEWSPIDER_MODULE = "ruzivo_scraper.spiders"

# ── Crawl politeness ──────────────────────────────────────────────────────────
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.5

# ── Retry ─────────────────────────────────────────────────────────────────────
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# ── User agent rotation ───────────────────────────────────────────────────────
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy_user_agents.middlewares.RandomUserAgentMiddleware": 400,
}

# ── Item pipelines ────────────────────────────────────────────────────────────
ITEM_PIPELINES = {
    "ruzivo_scraper.pipelines.TextCleaningPipeline": 100,
    "ruzivo_scraper.pipelines.LanguageFilterPipeline": 200,
    "ruzivo_scraper.pipelines.DeduplicationPipeline": 300,
    "ruzivo_scraper.pipelines.JsonExportPipeline": 400,
}

# ── Output ────────────────────────────────────────────────────────────────────
FEED_EXPORT_ENCODING = "utf-8"

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL = "INFO"
LOG_FILE = "ruzivo_scraper.log"

# ── HTTP Cache (dev only — disable for production runs) ──────────────────────
HTTPCACHE_ENABLED = False
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 86400
# HTTPCACHE_DIR = ".scrapy/httpcache"
