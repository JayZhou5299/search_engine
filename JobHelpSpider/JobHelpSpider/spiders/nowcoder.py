# -*- coding: utf-8 -*-
import scrapy
import time
import redis
import re
import random
import datetime

from scrapy import Request
from urllib import parse
from w3lib.html import remove_tags
from scrapy_redis.spiders import RedisSpider


from JobHelpSpider.items import JobWantedInformation
from JobHelpSpider.utils.common import get_md5
from JobHelpSpider import settings
from JobHelpSpider.utils.common import remove_t_r_n


# class NowcoderSpider(scrapy.Spider):
class NowcoderSpider(RedisSpider):
    name = 'nowcoder'
    allowed_domains = ['www.nowcoder.com']
    redis_key = 'nowcoder:start_urls'
    # start_urls = ['https://www.nowcoder.com/discuss?type=2&order=0&pageSize=30&query=&page=1',
    #               'https://www.nowcoder.com/discuss?type=7&order=0&pageSize=30&query=&page=1']

    def __init__(self):
        """
        初始化向redis中添加start_urls
        """
        redis_cli = redis.Redis(host=settings.REDIS_ADDRESS, port=6379)
        if redis_cli.exists(self.redis_key) == 0:
            redis_cli.lpush(self.redis_key,
                            'https://www.nowcoder.com/discuss?type=2&order=0&pageSize=30&query=&page=1',
                            'https://www.nowcoder.com/discuss?type=7&order=0&pageSize=30&query=&page=1')

    def parse(self, response):
        """
        解析待爬取的url
        :param response:
        :return:
        """
        time.sleep(random.randint(1, 4))
        crawl_node_list = response.css('.discuss-main')
        for crawl_node_obj in crawl_node_list:
            crawl_url = crawl_node_obj.css('a::attr(href)').extract_first()
            yield Request(url=parse.urljoin('https://www.nowcoder.com', crawl_url),
                          callback=self.parse_detail)

        next_url = response.css('.js-next-pager a::attr(href)').extract_first()
        if 'javascript:void(0)' != next_url:
            yield Request(url=parse.urljoin('https://www.nowcoder.com', next_url),
                          callback=self.parse)

    def parse_detail(self, response):
        """
        解析网页具体细节
        :param response:
        :return:
        """
        nowcoder_item = JobWantedInformation()
        publish_time = response.css('.post-time::text').extract_first()
        url = response.url
        if '今天' in publish_time:
            str_time = datetime.datetime.now().strftime('%Y-%m-%d')
            publish_time = datetime.datetime.strptime(str_time, '%Y-%m-%d').date()
        else:
            str_time = re.findall(r'(\d{4}-\d{2}-\d{2})', publish_time)
            publish_time = datetime.datetime.strptime(str_time[0], '%Y-%m-%d').date()

        content = response.css('.post-topic-main').extract_first()
        if content:
            content = remove_t_r_n(remove_tags(content))
            abstract = content[:300]

        title = response.css('.discuss-title::text').extract_first()

        nowcoder_item['url_object_id'] = get_md5(url)
        nowcoder_item['url'] = url
        nowcoder_item['title'] = remove_t_r_n(title)
        nowcoder_item['publish_time'] = publish_time
        nowcoder_item['content'] = content
        nowcoder_item['data_source'] = 'nowcoder'
        nowcoder_item['abstract'] = abstract

        yield nowcoder_item
