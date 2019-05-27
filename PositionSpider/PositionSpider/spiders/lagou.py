# -*- coding: utf-8 -*-
import scrapy
import re
import time
import redis
import random

from urllib import request
from http import cookiejar
from scrapy import Request
from urllib import parse
from w3lib.html import remove_tags
from scrapy_redis.spiders import RedisSpider


from PositionSpider.items import PositionItem
from PositionSpider.utils.common import get_md5
from PositionSpider import settings

"""
获取cookie信息
"""
cookie_str = ''
# 声明一个CookieJar对象实例来保存cookie
cookie = cookiejar.CookieJar()
# 利用urllib.request库的HTTPCookieProcessor对象来创建cookie处理器,也就CookieHandler
handler = request.HTTPCookieProcessor(cookie)
# 通过CookieHandler创建opener
opener = request.build_opener(handler)
# 此处的open方法打开网页
response = opener.open('https://www.lagou.com/jobs/5570192.html')
# 打印cookie信息
for item in cookie:
    cookie_str += '%s:%s;' % (item.name, item.value)


class LagouSpider(RedisSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    # start_urls = ['http://www.lagou.com/']
    redis_key = 'lagou:start_urls'

    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 1,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cookie': cookie_str,
            'Connection': 'keep-alive',
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/',
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        }
    }

    def __init__(self):
        """
        初始化向redis中添加start_urls
        """
        redis_cli = redis.Redis(host=settings.REDIS_ADDRESS, port=6379)
        # master端开启即可
        redis_cli.lpush(self.redis_key, 'http://www.lagou.com/')

    def parse(self, response):
        """
        提取抓取的相关模块
        :param response:
        :return:
        """
        all_classify_node = response.css('.menu_main')

        # it相关的只是前四个分类，分别为技术，产品，设计，运维与最后一个分类，小游戏开发
        it_classify_node = [all_classify_node[0], all_classify_node[1],
                            all_classify_node[2], all_classify_node[3], all_classify_node[7]]

        for it_classify_node_obj in it_classify_node:
            url_list = it_classify_node_obj.css('a::attr(href)').extract()
            job_classify_list = it_classify_node_obj.css('a::text').extract()
            for url_obj in url_list:
                time.sleep(random.randint(4, 7))
                job_classify = job_classify_list[url_list.index(url_obj)]
                yield Request(url=url_obj, callback=self.parse_crawl_urls,
                              meta={'job_classify': job_classify})

    def parse_crawl_urls(self, response):
        """
        提取待抓取url
        :param response:
        :return:
        """
        crawl_urls = response.css('.content_left .position_link::attr(href)').extract()
        for crawl_url in crawl_urls:
            time.sleep(random.randint(5, 7))
            yield Request(url=crawl_url, callback=self.parse_detail,
                          meta={'job_classify': response.meta['job_classify']})

        # 如果没有下一页直接return即可
        no_next_tag = response.css('.pager_next_disabled')
        if no_next_tag:
            return

        # 最后一个元素是下一页的标签
        next_url = response.css('.page_no::attr(href)').extract()[-1]
        time.sleep(random.randint(5, 7))
        yield Request(url=next_url, callback=self.parse_crawl_urls,
                      meta={'job_classify': response.meta['job_classify']})

    def parse_detail(self, response):
        """
        提取网页具体细节
        :param response:
        :return:
        """
        lagou_item = PositionItem()
        url = response.url
        position_name = response.css('.job-name .name::text').extract_first()

        # 获取other_message_list失败的直接return
        other_message_list = response.css('.job_request span::text').extract()
        if not other_message_list:
            return

        salary_list = re.findall(r'(\d*)k', other_message_list[0])
        salary_min = float(salary_list[0]) * 1000
        salary_max = float(salary_list[1]) * 1000

        welfare = response.css('.job-advantage p::text').extract_first()

        working_place = other_message_list[1].replace('/', '')
        working_exp = other_message_list[2].replace('/', '')
        education = other_message_list[3]

        abstract = response.css('.job_bt').extract_first()
        if abstract:
            abstract = remove_tags(abstract)

        company_name = response.css('.fl-cn::text').extract_first()

        lagou_item['url_object_id'] = get_md5(url)
        lagou_item['url'] = url
        lagou_item['position_name'] = position_name
        lagou_item['salary_min'] = salary_min
        lagou_item['salary_max'] = salary_max
        # welfare以分号分割
        lagou_item['welfare'] = welfare
        lagou_item['working_place'] = working_place
        lagou_item['working_exp'] = working_exp
        lagou_item['education'] = education
        lagou_item['abstract'] = abstract.replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '')[:200]
        lagou_item['data_source'] = '拉勾网'
        lagou_item['company_name'] = company_name.strip()
        lagou_item['job_classify'] = response.meta['job_classify']

        yield lagou_item


