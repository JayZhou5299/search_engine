# -*- coding: utf-8 -*-

# Scrapy settings for VideoSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'VideoSpider'

SPIDER_MODULES = ['VideoSpider.spiders']
NEWSPIDER_MODULE = 'VideoSpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'VideoSpider (+http://www.yourdomain.com)'

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
#    'VideoSpider.middlewares.VideospiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'VideoSpider.middlewares.VideospiderDownloaderMiddleware': 543,

    # 设置随机用户代理，必须先将scrapy原先的用户代理中间件去掉
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'VideoSpider.middlewares.RandomUserAgentMiddleWare': 1
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'VideoSpider.pipelines.MysqlTwistPipeline': 300,
   'VideoSpider.pipelines.ElasticSearchPipeline': 200,
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
MYSQL_DB = 'search_engine'


# 本地的chromedriver路径
CHROMEDRIVER_PATH = '/Users/hanyuzhou/Downloads/chromedriver'
# 阿里云服务器的chromedriver路径
CHROMEDRIVER_PATH = '/home/yuzhou/software/chromedriver'


# 网易云课堂start_urls           eg:'url后缀': '一级目录-二级目录'
# NETEASE_CLOUD_CLASS = {'480000003121007': '编程语言-Python', '480000003132004': '编程语言-PHP',
#                        '480000003130011': '编程语言-Java', '480000003130012': '编程语言-C',
#                        '480000003121008': '编程语言-C++', '480000003119009': '编程语言-C#',
#                        '480000003129017': '编程语言-R', '480000003122008': '前端开发-语言基础',
#                        '480000003129019': '前端开发-前端框架', '480000003131013': '前端开发-开发实践',
#                        '480000003131010': '后端开发-Java Web', '480000003126017': '后端开发-Python',
#                        '480000003120006': '后端开发-PHP Web', '480000003125016': '后端开发-.NET',
#                        '480000003120005': '移动开发-Android', '480000003134005': '移动开发-Unity3D',
#                        '480000003128007': '移动开发-IOS', '480000003124005': '移动开发-微信开发',
#                        '480000003127009': '网络与安全-软件工程与方法', '480000003125015': '网络与安全-网络与通讯',
#                        '480000003119008': '网络与安全-测试运维', '480000003121006': '网络与安全-信息安全',
#                        '480000003124008': '数据科学-数据分析', '480000003124009': '数据科学-数据挖掘',
#                        '480000003123021': '数据科学-数据基础', '480000003129020': '人工智能-语言数学基础',
#                        '480000003124010': '人工智能-算法基础', '480000003129021': '人工智能-应用技术',
#                        '480000003130014': '人工智能-应用领域', '480000003119011': '大数据-语言工具基础',
#                        '480000003122009': '大数据-大数据开发', '480000003121009': '大数据-大数据应用',
#                        '480000003132006': '区块链-区块链'}
NETEASE_CLOUD_CLASS = ['480000003131009', '480000003120007', '480000003126016', '480000003130010',
                       '480000003121005', '480000003127010', '480000003130013', '480000003134007',
                       '480000003132006', '480000003132007', '480000003130008', '480000003128006',
                       '480000003130009']

# 百度传课start_urls   eg: https://chuanke.baidu.com/course/72351176527446016_____.html
BAIDU_CHUANKE_MAP = {'72351176561000448': '编程语言\tC/C++', '72351176695218176': '编程语言\tVC/MFC',
                     '72351176577777664': '编程语言\tJAVA', '72351176594554880': '编程语言\tPython',
                     '72351176544223232': '编程语言\tPHP', '72351176628109312': '编程语言\t脚本语言',
                     '72351176728772608': '编程语言\tObjective-C', '72351236791271424': '常用软件\tPhotoshop',
                     '72351236791533568': '常用软件\t3Dmax', '72351236791599104': '常用软件\tIllustrator',
                     '72351236791402496': '常用软件\tFlash', '72351236791336960': '常用软件\tDreamweaver',
                     '72351236791468032': '常用软件\tMaya', '72351236791795712': '常用软件\tAxure',
                     '72351236707319808': '设计制作\t平面设计', '72351236774428672': '设计制作\t网站制作',
                     '72351236841537536': '设计制作\t页面设计', '72351236724097024': '设计制作\t游戏设计',
                     '72351236824760320': '设计制作\t三维设计', '72351236673765376': '设计制作\tCG动画',
                     '72351180855967744': '数据库\tOracle', '72351180872744960': '数据库\tSQL Server',
                     '72351180839190528': '数据库\tMySQL', '72351189429125120': '系统运维\tLinux',
                     '72351189445902336': '系统运维\tWindows', '72351189613674496': '系统运维\tVmware',
                     '72351189479456768': '系统运维\t网络管理', '72351189529788416': '系统运维\tExchange',
                     '72351202314027008': '移动互联网\tAndroid', '72351202330804224': '移动互联网\tIOS',
                     '72351202364358656': '移动互联网\tWebapp', '72351210903961600': '产品运营\t产品设计',
                     '72351210920738816': '产品运营\t网站编辑', '72351210954293248': '产品运营\t数据分析',
                     '72351210937516032': '产品运营\t策划', '72351240951955456': '其他\t网络安全',
                     '72351245246922752': '其他\t嵌入式培训', '72351228067053568': '其他\t移动通信',
                     '72351185184489472': '其他\t云计算', '72351185117380608': '其他\t系统架构',}

# 慕课网实战课程的相对url与分类的映射
IMOOC_MAP = {'vuejs': '前端开发\tVue.js', 'miniprogram': '前端开发\t小程序',
             'html': '前端开发\tHTML/CSS', 'javascript': '前端开发\tJavaScript',
             'reactjs': '前端开发\tReact.JS', 'angular': '前端开发\tAngular',
             'nodejs': '前端开发\tNode.js', 'jquery': '前端开发\tjQuery',
             'webapp': '前端开发\tWebApp', 'fetool': '前端开发\t前端工具',

             'swoole': '后端开发\tSwoole', 'java': '后端开发\tJava',
             'springboot': '后端开发\tSpringBoot', 'ssm': '后端开发\tSSM',
             'python': '后端开发\tPython', 'crawler': '后端开发\t爬虫',
             'django': '后端开发\tDjango', 'flask': '后端开发\tFlask',
             'tornado': '后端开发\tTornado', 'go': '后端开发\tGo',
             'php': '后端开发\tPHP', 'c': '后端开发\tC',
             'cplusplus': '后端开发\tC++',

             'android': '移动开发\tAndroid', 'ios': '移动开发\tiOS',
             'reactnative': '移动开发\tReactnative', 'ionic': '移动开发\tIonic',

             'algorithmds': '算法&数学\t算法与数据结构', 'maths': '算法&数学\t数学',
             'suanfa': '算法&数学\t算法', 'datastructure': '算法&数学\t数据结构',

             'wff': '前沿技术\t微服务', 'blockchain': '前沿技术\t区块链',
             'machine': '前沿技术\t机器学习', 'deep': '前沿技术\t深度学习',
             'pcvision': '前沿技术\t计算机视觉', 'nlp': '前沿技术\t自然语言处理',
             'datafxwj': '前沿技术\t数据分析&挖掘',

             'bigdata': '云计算&大数据\t大数据', 'hadoop': '云计算&大数据\tHadoop',
             'spark': '云计算&大数据\tSpark', 'hbase': '云计算&大数据\tHbase',
             'flink': '云计算&大数据\tFlink', 'storm': '云计算&大数据\tStorm',
             'aliyun': '云计算&大数据\t阿里云', 'docker': '云计算&大数据\tDocker',
             'kubernetes': '云计算&大数据\tKubernetes',

             'dba': '运维&测试\t运维', 'oma': '运维&测试\t自动化运维',
             'zjj': '运维&测试\t中间件', 'linux': '运维&测试\tLinux',
             'test': '运维&测试\t测试', 'gntest': '运维&测试\t功能测试',
             'xntest': '运维&测试\t性能测试', 'zdhtest': '运维&测试\t自动化测试',
             'jktest': '运维&测试\t接口测试', 'ydtest': '运维&测试\t移动测试',

             'mysql': '数据库\tMySQL', 'redis': '数据库\tRedis',
             'mongodb': '数据库\tMongoDB', 'nosql': '数据库\tNoSql',

             'dxdh': 'UI设计&多媒体\t动效动画', 'uijc': 'UI设计&多媒体\t设计基础',
             'uitool': 'UI设计&多媒体\t设计工具', 'uiapp': 'UI设计&多媒体\tAPPUI设计',
             }
