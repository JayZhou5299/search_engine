# -*- coding: utf-8 -*-

# Scrapy settings for PositionSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'PositionSpider'

SPIDER_MODULES = ['PositionSpider.spiders']
NEWSPIDER_MODULE = 'PositionSpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'PositionSpider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'PositionSpider.middlewares.PositionspiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   #  设置ip代理，需要先将scrapy原先的ip代去掉
   # 'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': None,

   # 'PositionSpider.middlewares.PositionspiderDownloaderMiddleware': 543,

    # 设置随机用户代理，必须先将scrapy原先的用户代理中间件去掉
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'PositionSpider.middlewares.RandomUserAgentMiddleWare': 1,
    # 'PositionSpider.middlewares.RandomIpProxyMiddleWare': 10
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
ITEM_PIPELINES = {
   'scrapy_redis.pipelines.RedisPipeline': 300,
   'PositionSpider.pipelines.MysqlTwistPipeline': 250,
   'PositionSpider.pipelines.ElasticSearchPipeline': 200,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
MYSQL_HOST = '182.92.193.60'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '(pwd:wyf)'
MYSQL_DB = 'search_engine'


# ip代理池
# IP_PROXY_POOL = [
#     'https://182.88.135.100:8123', 'http://171.43.13.41:9999', 'http://171.43.13.85:9999',
#     'http://171.43.13.56:9999', 'http://171.43.13.68:9999', 'http://121.31.147.12:8123',
#     'http://1.198.110.251:9999', 'http://61.142.72.154:30074', 'http://171.43.13.76:9999'
# ]

IP_PROXY_POOL = [
    'https://112.85.149.12:9999', 'https://210.5.10.87:53281', 'https://14.20.235.185:808',
    'https://171.41.81.253:9999', 'https://171.41.80.245:9999', 'https://171.41.81.144:9999'
]

# IP_PROXY_POOL = [
#     'http://116.226.58.37:39443', 'http://112.85.170.47:9999', 'http://121.224.4.168:9999',
#     'http://116.209.57.58:9999'
# ]


# 本地的chromedriver路径
CHROMEDRIVER_PATH = '/Users/hanyuzhou/Downloads/chromedriver'
# 阿里云服务器的chromedriver路径
CHROMEDRIVER_PATH = '/home/yuzhou/software/chromedriver'

# ES_ADDRESS = '60.205.224.136'
ES_ADDRESS = '39.96.16.6'

REDIS_ADDRESS = '182.92.193.60'

# slave端redis_url配置
# REDIS_URL = 'redis://182.92.193.60:6379'
# master端redis配置
# REDIS_HOST = 'localhost'
# REDIS_PORT = 6379


