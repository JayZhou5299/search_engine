# -*- coding: utf-8 -*-
import scrapy
import re
import time
import random
import redis


from scrapy import Request
from urllib import parse
from w3lib.html import remove_tags
from scrapy_redis.spiders import RedisSpider

from PositionSpider.items import PositionItem
from PositionSpider.utils.common import get_md5
from PositionSpider import settings


class BossSpider(RedisSpider):
    name = 'Boss'
    allowed_domains = ['www.zhipin.com']
    # start_urls = ['http://www.zhipin.com/']
    redis_key = 'Boss:start_urls'

    def __init__(self):
        """
        初始化向redis中添加start_urls
        """
        redis_cli = redis.Redis(host=settings.REDIS_ADDRESS, port=6379)
        # master端开启即可
        # redis_cli.lpush(self.redis_key, 'http://www.zhipin.com/')

    def parse(self, response):
        """
        提取爬取相关的模块
        :param response:
        :return:
        """
        all_classify_node = response.css('.menu-sub')
        # it相关的只是前四个分类，分别为技术，产品，设计，运维
        it_classify_node = all_classify_node[:4]
        for it_classify_node_obj in it_classify_node:
            relative_url_list = it_classify_node_obj.css('a::attr(href)').extract()
            job_classify_list = it_classify_node_obj.css('a::text').extract()

            # 需要将城市改为全国，所以要对相对url进行替换
            for relative_url_obj in relative_url_list:
                relative_url = re.sub(r'c(\d*)-', 'c100010000-', relative_url_obj)
                job_classify = job_classify_list[relative_url_list.index(relative_url_obj)]
                time.sleep(random.randint(2, 4))
                yield Request(url=parse.urljoin('https://www.zhipin.com', relative_url),
                              callback=self.parse_crawl_urls, meta={'job_classify': job_classify})

    def parse_crawl_urls(self, response):
        """
        获取待爬取的url
        :param response:
        :return:
        """
        crawl_urls = response.css('.info-primary a::attr(href)').extract()
        for crawl_url in crawl_urls:
            time.sleep(random.randint(1, 3))
            yield Request(url=parse.urljoin('http://www.zhipin.com/', crawl_url),
                          callback=self.parse_detail,
                          meta={'job_classify': response.meta['job_classify']})

        # 如果没有下一页直接return即可
        no_next_tag = response.css('.next.disabled')
        if no_next_tag:
            return

        next_url = response.css('.next::attr(href)').extract_first()
        time.sleep(random.randint(2, 4))
        yield Request(url=parse.urljoin('http://www.zhipin.com/', next_url),
                      callback=self.parse_crawl_urls,
                      meta={'job_classify': response.meta['job_classify']})

    def parse_detail(self, response):
        """
        解析网页细节
        :param response: 
        :return: 
        """
        boss_item = PositionItem()
        url = response.url
        position_name = response.css('.job-primary h1::text').extract_first()

        # 获取salary失败的直接return
        salary = response.css('.salary::text').extract_first()
        if not salary:
            return
        
        salary_list = re.findall(r'(\d*)k', salary)
        salary_min = float(salary_list[0]) * 1000
        salary_max = float(salary_list[1]) * 1000

        welfare_list = response.css('.info-primary .tag-all span::text').extract()
        if welfare_list:
            welfare = ';'.join(welfare_list)
        else:
            welfare = '无'

        other_message_node = response.css('.info-primary p')[0]
        other_message_list = other_message_node.css('::text').extract()
        working_place = other_message_list[0]
        working_exp = other_message_list[1]
        education = other_message_list[2]

        abstract = response.css('.job-sec .text').extract_first()
        if abstract:
            abstract = remove_tags(abstract)

        company_name = response.css('.sider-company .company-info a::attr(title)').extract_first()

        boss_item['url_object_id'] = get_md5(url)
        boss_item['url'] = url
        boss_item['position_name'] = position_name
        boss_item['salary_min'] = salary_min
        boss_item['salary_max'] = salary_max
        # welfare以分号分割
        boss_item['welfare'] = welfare
        boss_item['working_place'] = working_place
        boss_item['working_exp'] = working_exp
        boss_item['education'] = education
        boss_item['abstract'] = abstract.replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '')[:200]
        boss_item['data_source'] = 'Boss直聘'
        boss_item['company_name'] = company_name.strip()
        boss_item['job_classify'] = response.meta['job_classify']

        yield boss_item
