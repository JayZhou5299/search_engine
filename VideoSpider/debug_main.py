import sys
import os

# 调试脚本
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# execute(['scrapy', 'crawl', 'heima'])
# execute(['scrapy', 'crawl', 'tencent_class'])
# execute(['scrapy', 'crawl', 'baidu_chuanke'])
execute(['scrapy', 'crawl', 'imooc'])
# execute(['scrapy', 'crawl', 'edu_51cto'])

