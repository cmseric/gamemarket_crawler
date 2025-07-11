# -*- coding: utf-8 -*-
"""
Scrapy设置文件
"""

import os
from datetime import datetime

# Scrapy基础设置
BOT_NAME = 'gamemarket_crawler'
SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'

# 遵守robots.txt协议
ROBOTSTXT_OBEY = True

# 并发设置
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 8

# 下载延迟设置 (合规要求)
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_TIMEOUT = 30

# 重试设置
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# 移除Playwright配置，使用标准HTTP下载器
# 在Windows环境下，Playwright与asyncio reactor存在兼容性问题
# DOWNLOAD_HANDLERS = {
#     "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
#     "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
# }

# 使用标准reactor，避免Playwright兼容性问题
# TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Playwright设置（暂时禁用）
# PLAYWRIGHT_LAUNCH_OPTIONS = {
#     "headless": True,
#     "args": [
#         "--no-sandbox",
#         "--disable-setuid-sandbox",
#         "--disable-dev-shm-usage",
#         "--disable-accelerated-2d-canvas",
#         "--no-first-run",
#         "--no-zygote",
#         "--disable-gpu"
#     ]
# }

# 请求头设置
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# 中间件设置
DOWNLOADER_MIDDLEWARES = {
    'scraper.middlewares.RandomUserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

# 管道设置
ITEM_PIPELINES = {
    'scraper.pipelines.DataValidationPipeline': 300,
    'scraper.pipelines.DataCleaningPipeline': 400,
    'scraper.pipelines.MongoDBPipeline': 500,
    'scraper.pipelines.MySQLPipeline': 600,
}

# Redis设置 (分布式爬虫)
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
REDIS_ENCODING = 'utf-8'

# 数据库设置
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'gamemarket')

MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'gamemarket')

# 日志设置
LOG_LEVEL = 'INFO'
LOG_FILE = f'data/logs/crawler_{datetime.now().strftime("%Y%m%d")}.log'

# 缓存设置
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'data/cache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 自动限速
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# 代理设置
PROXY_ENABLED = os.getenv('PROXY_ENABLED', 'False').lower() == 'true'
PROXY_LIST_FILE = 'config/proxies.txt'
PROXY_MODE = 0  # 0=随机, 1=轮询

# 用户代理设置
USER_AGENT_LIST_FILE = 'config/user_agents.txt'

# 数据导出设置
FEED_EXPORT_ENCODING = 'utf-8'
FEEDS = {
    'data/export/%(name)s_%(time)s.json': {
        'format': 'json',
        'encoding': 'utf8',
        'indent': 2,
    },
}

# 自定义设置
CRAWL_DATE = datetime.now().strftime('%Y-%m-%d')
MAX_PAGES_PER_SPIDER = 100  # 每个爬虫最大页数限制 