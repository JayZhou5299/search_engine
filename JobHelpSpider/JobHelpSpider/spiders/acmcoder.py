# -*- coding: utf-8 -*-
import scrapy
import time
import re
import random
import redis
import datetime

from scrapy import Request
from urllib import parse
from w3lib.html import remove_tags
from scrapy_redis.spiders import RedisSpider

from JobHelpSpider.items import JobWantedInformation
from JobHelpSpider.utils.common import get_md5
from JobHelpSpider.utils.common import remove_t_r_n
from JobHelpSpider import settings


# class AcmcoderSpider(scrapy.Spider):
class AcmcoderSpider(RedisSpider):
    name = 'acmcoder'
    allowed_domains = ['discuss.acmcoder.com']
    # start_urls = ['http://discuss.acmcoder.com/index?tab=job&page=1']
    redis_key = 'acmcoder:start_urls'

    def __init__(self):
        """
        初始化向redis中添加start_urls
        """
        redis_cli = redis.Redis(host=settings.REDIS_ADDRESS, port=6379)
        # master端需要打开下面的注释
        # redis_cli.lpush(self.redis_key, 'http://discuss.acmcoder.com/index?tab=job&page=1')

    def parse(self, response):
        """
        解析待爬取的url
        :param response:
        :return:
        """
        time.sleep(random.randint(1, 4))
        # 如果包含没有数据的tag，直接返回即可
        no_data_tag = response.css('#content .inner p')
        if no_data_tag:
            return

        crawl_url_list = response.css('.topic_title_wrapper .topic_title::attr(href)').extract()
        for crawl_url_obj in crawl_url_list:
            yield Request(url=parse.urljoin('http://discuss.acmcoder.com', crawl_url_obj),
                          callback=self.parse_detail)

        page_num = re.findall(r'page=(\d*)', response.url)
        if page_num:
            page_num = int(page_num[0]) + 1
        else:
            page_num = 1

        # 翻页
        next_url = re.sub(r'page=(\d*)', 'page=%d' % page_num, response.url)
        if next_url:
            yield Request(url=next_url, callback=self.parse)

    def parse_detail(self, response):
        """
        解析网页具体细节
        :param response:
        :return:
        """
        acmcoder_item = JobWantedInformation()
        publish_time = response.css('.changes span::text').extract_first()
        url = response.url
        if '今天' in publish_time:
            str_time = datetime.datetime.now().strftime('%Y-%m-%d')
            publish_time = datetime.datetime.strptime(str_time, '%Y-%m-%d').date()
        else:
            str_time = re.findall(r'(\d{4}-\d{2}-\d{2})', publish_time)
            publish_time = datetime.datetime.strptime(str_time[0], '%Y-%m-%d').date()

        content = response.css('.topic_content').extract_first()
        if content:
            content = remove_t_r_n(remove_tags(content))
            abstract = content[:300]

        title = response.css('.topic_full_title::text').extract_first()

        acmcoder_item['url_object_id'] = get_md5(url)
        acmcoder_item['url'] = url
        acmcoder_item['title'] = remove_t_r_n(title)
        acmcoder_item['publish_time'] = publish_time
        acmcoder_item['content'] = content
        acmcoder_item['data_source'] = 'acmcoder'
        acmcoder_item['abstract'] = abstract

        yield acmcoder_item
