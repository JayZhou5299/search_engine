# -*- coding: utf-8 -*-

# Scrapy settings for ArticleSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'ArticleSpider'

SPIDER_MODULES = ['ArticleSpider.spiders']
NEWSPIDER_MODULE = 'ArticleSpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ArticleSpider (+http://www.yourdomain.com)'

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
#    'ArticleSpider.middlewares.ArticlespiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'ArticleSpider.middlewares.JSPageMiddleware': 1,
   'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
   'ArticleSpider.middlewares.RandomUserAgentMiddleWare': 1
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   # 'ArticleSpider.pipelines.ArticlespiderPipeline': 300,
   'ArticleSpider.pipelines.MysqlTwistPipeline': 300,
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
MYSQL_HOST = '60.205.224.136'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_DB = 'search_engine_test'

# 由于jobbole中各个域名不同，所以需要进行配置
JOBBOLE_LIST_ONE = [['http://blog.jobbole.com/tag/machinelearning/', 'http://blog.jobbole.com/tag/git/',
                     'http://blog.jobbole.com/tag/algorithm/', 'http://blog.jobbole.com/tag/测试/',
                     'http://blog.jobbole.com/tag/安全/', 'http://blog.jobbole.com/tag/vim/',
                     'http://blog.jobbole.com/tag/database/', 'http://blog.jobbole.com/tag/linux/',
                     'http://blog.jobbole.com/tag/unix/', 'http://blog.jobbole.com/tag/net/'], r'.*tag/(.*?)/']

JOBBOLE_LIST_TWO = [['http://android.jobbole.com/all-posts/', 'http://ios.jobbole.com/all-posts/',
                     'http://python.jobbole.com/', 'http://web.jobbole.com/all-posts/'], r'http://(.*).jobbole.*']

JOBBOLE_LIST_THREE = [['http://blog.jobbole.com/category/c-cpp/', 'http://blog.jobbole.com/category/php-programmer/',
                       'http://blog.jobbole.com/category/ruby/', 'http://blog.jobbole.com/category/go/'], r'.*category/(.*)/.*']

