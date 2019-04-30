# -*- coding: utf-8 -*-
import scrapy
import re
import redis
import json
import time
import random
import requests

from urllib import parse
from scrapy import Request
from w3lib.html import remove_tags
from scrapy_redis.spiders import RedisSpider


from VideoSpider.items import VideoItem
from VideoSpider.utils.common import get_md5
from VideoSpider import settings


class HeimaSpider(RedisSpider):
    name = 'heima'
    allowed_domains = ['www.itheima.com', 'yun.itheima.com']
    # start_urls = ['http://yun.itheima.com/course/']
    redis_key = 'heima:start_urls'

    def __init__(self):
        """
        初始化start_urls到redis
        """
        redis_cli = redis.Redis(host=settings.REDIS_ADDRESS, port=6379)
        # master端需要将这个打开
        # redis_cli.lpush('http://yun.itheima.com/course/')

    def parse(self, response):
        """
        解析网页
        :param response:
        :return:
        """
        # 获取起始url
        start_url_list = response.css('.kind a::attr(href)').extract()
        for start_url_obj in start_url_list:
            time.sleep(random.randint(2, 5))
            yield Request(url=parse.urljoin('http://yun.itheima.com', start_url_obj),
                          callback=self.parse_crawl_list)

    def parse_crawl_list(self, response):
        """
        解析抓取的url列表
        :param response:
        :return:
        """
        crawl_url_list = response.css('.bdtxt a::attr(href)').extract()
        for crawl_url_obj in crawl_url_list:
            time.sleep(random.randint(2, 4))
            yield Request(url=parse.urljoin('http://yun.itheima.com', crawl_url_obj),
                          callback=self.parse_detail)

        next_url = response.css('.next::attr(href)').extract_first()
        if next_url:
            time.sleep(random.randint(2, 4))
            yield Request(url=parse.urljoin('http://yun.itheima.com', next_url),
                          callback=self.parse_crawl_list)

    def get_evaluation_content(self, cid):
        """
        获取该课程的评论内容
        :param cid: 课程编号
        :return:
        """
        start_num = 0
        res_list = list()
        while True:
            data = {
                'start': start_num * 5,
                'cid': cid,
            }
            time.sleep(random.randint(1))
            res = requests.post('http://yun.itheima.com/course/getcommentajax.html', data)
            if res.text:
                json_dict = json.loads(res.text)
                content_list = json_dict['list']
                # 由于没有打分系统，所以直接给6分做一个平均
                for content_obj in content_list:
                    res_list.append(json.dumps({content_obj['content']: 6}, ensure_ascii=False))
                start_num += 1
            else:
                break

        return '\t'.join(res_list)

    def parse_detail(self, response):
        """
        解析具体网页的细节
        :param response:
        :return:
        """
        heima_item = VideoItem()

        url = response.url
        bread_list = response.css('.breadcrumb a::text').extract()
        if bread_list:
            first_classify = bread_list[1]
            second_classify = bread_list[2]

        learner_nums = response.css('.li3::text').extract_first()
        if learner_nums:
            learner_nums = re.findall(r'(\d*)', learner_nums)[0]

        class_name = response.css('.vname::text').extract_first()
        abstract = response.css('.course').extract_first()
        if abstract:
            abstract = remove_tags(abstract).replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')

        cid = re.findall(r'course/(\d*)', url)[0]
        evaluation_content = self.get_evaluation_content(cid)

        # 赋值item相应属性
        heima_item['url_object_id'] = get_md5(url)
        heima_item['url'] = url
        heima_item['price'] = 0.0
        heima_item['class_name'] = class_name
        heima_item['learner_nums'] = int(learner_nums)
        heima_item['abstract'] = abstract
        heima_item['data_source'] = '黑马程序员'
        heima_item['institution'] = '黑马程序员'
        heima_item['first_classify'] = first_classify
        heima_item['second_classify'] = second_classify
        heima_item['evaluation_content'] = evaluation_content

        yield heima_item
