import sys
import os

# 调试脚本
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# execute(['scrapy', 'crawl', 'oschina'])
# execute(['scrapy', 'crawl', 'jobbole'])
# execute(['scrapy', 'crawl', 'linux_cn'])
# execute(['scrapy', 'crawl', 'importnew'])
execute(['scrapy', 'crawl', 'cnblogs'])

