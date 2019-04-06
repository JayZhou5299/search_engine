import sys
import os

# 启动spider的脚本
from scrapy.cmdline import execute
from optparse import OptionParser

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def get_options():
    """
    从命令行获取参数
    :return:
    """
    usage = "usage: %prog [options] <input_matrix>"
    parser = OptionParser(usage)
    parser.add_option("-s", "--spider",
                      dest="spider",
                      type='string',
                      help="spider_name")
    (options, args) = parser.parse_args()
    return options


if __name__ == '__main__':
    user_input = get_options()
    if user_input.spider:
        execute(['scrapy', 'crawl', user_input.spider])
    else:
        print('输入格式错误, [提示]python -s (爬虫名称)     eg: python -s imooc,     '
              '（目前支持的spider_name有baidu_chuanke, tencent_class, imooc, edu_51cto）')

