# -*- coding: utf-8 -*-

# Scrapy settings for CrawlDemos project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# scrapy默认采用的是深度优先算法

BOT_NAME = 'CrawlDemos'

SPIDER_MODULES = ['CrawlDemos.spiders']
NEWSPIDER_MODULE = 'CrawlDemos.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'CrawlDemos (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# 当COOKIES_ENABLED是注释的时候scrapy默认没有开启cookie
# 当COOKIES_ENABLED没有注释设置为False的时候scrapy默认使用了settings里面的cookie
# 当COOKIES_ENABLED设置为True的时候scrapy就会把settings的cookie关掉，使用自定义cookie
# 需要使用自定义中间件的cookie时，需要设置为True或者注释掉
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
"""Spider默认启用的中间件(500～700之间选择最为妥当)
'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': 50,
'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 500,
'scrapy.spidermiddlewares.referer.RefererMiddleware': 700,
'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': 800,
'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
"""
# SPIDER_MIDDLEWARES = {
#    'CrawlDemos.spider_middlewares.middlewares.CrawldemosSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
"""Scrapy默认启用的下载中间件
'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': 100,
'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 300,
'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 400,
'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 550,
'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 580,
'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 590,
'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
'scrapy.downloadermiddlewares.chunked.ChunkedTransferMiddleware': 830,
'scrapy.downloadermiddlewares.stats.DownloaderStats': 850,
'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 900
"""
DOWNLOADER_MIDDLEWARES = {
    # 必须先关闭系统自带的UserAgent中间件，再启用自己的随机UserAgent中间件
    # 在settings中不需要再设置UserAgent
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "CrawlDemos.download_middlewares.useragent_middleware.CustomUserAgentMiddleware": 400,

    # 自定义重试方法
    # "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
    # "CrawlDemos.download_middlewares.retry_middleware.CustomRetryMiddleWare": 500,

    # 自定义代理IP
    # "CrawlDemos.download_middlewares.proxy_middleware.CustomProxyMiddleware": 542,

    # 自定义Cookies
    # "CrawlDemos.download_middlewares.cookie_middleware.CustomCookieMiddleWare": 543,

    # 'CrawlDemos.download_middlewares.download_middleware.CustomDownloaderMiddleware': 543,

    # 自定义的Chrome来爬取网页
    "CrawlDemos.download_middlewares.chrome.ChromeDownloaderMiddleware": 544,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
# 设置图片下载路径（如不设置，将不会下载图片）
IMAGES_STORE = 'D:\\test'
# 过期天数
IMAGES_EXPIRES = 90
# 针对图片生成缩略图
# IMAGES_THUMBS = {
#     'small': (50, 50),
#     'big': (270, 270),
# }
# 过滤图片高度小于170、宽度小于260的图片
# IMAGES_MIN_HEIGHT = 170
# IMAGES_MIN_WIDTH = 260

ITEM_PIPELINES = {
    'CrawlDemos.pipelines.pipelines.CrawlDemosPipeline': 300,
    # 'CrawlDemos.pipelines.async_db.AsyncDbPipelines': 301,
    # 'CrawlDemos.pipelines.image_pipelines.CustomImagePipelines': 302,
    'CrawlDemos.pipelines.nest_item_pipelines.NestItemPipelines': 303,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# scrapy-redis需要设置以下信息（Scrapy默认的全局并发限制对同时爬取大量网站的情况并不适用）
# 默认 Item 并发数：100
# CONCURRENT_ITEMS = 100
# # 默认 Request 并发数：16
# CONCURRENT_REQUESTS = 16
# # 默认每个域名的并发数：8
# CONCURRENT_REQUESTS_PER_DOMAIN = 8
# # 每个IP的最大并发数：0表示忽略
# CONCURRENT_REQUESTS_PER_IP = 0

# 使用scrapy-redis里面的去重组件.
# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 使用scrapy-redis里面的调度器
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 允许暂停后,能保存进度
# SCHEDULER_PERSIST = True

# 指定排序爬取地址时使用的队列，
# 默认的 按优先级排序(Scrapy默认)，由sorted set实现的一种非FIFO、LIFO方式。
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'
# 可选的 按先进先出排序（FIFO）
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderQueue'
# 可选的 按后进先出排序（LIFO）
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderStack'
