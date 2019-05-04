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
from PositionSpider.utils.common import remove_r_n_t
from PositionSpider import settings


class LiepinSpider(RedisSpider):
    name = 'liepin'
    allowed_domains = ['www.liepin.com']
    # start_urls = ['https://www.liepin.com/it']
    redis_key = 'liepin:start_urls'

    def __init__(self):
        """
        初始化向redis中添加start_urls
        """
        redis_cli = redis.Redis(host=settings.REDIS_ADDRESS, port=6379)
        # master端开启即可
        # redis_cli.lpush(self.redis_key, 'https://www.liepin.com/it')

    def parse(self, response):
        """
        提取爬取相关的模块
        :param response:
        :return:
        """
        it_classify_node = response.css('.float-left dd')
        for it_classify_node_obj in it_classify_node:
            relative_url_list = it_classify_node_obj.css('a::attr(href)').extract()
            job_classify_list = it_classify_node_obj.css('a::text').extract()

            # 需要将城市改为全国，所以要对相对url进行替换
            for relative_url_obj in relative_url_list:
                time.sleep(random.randint(2, 4))
                job_classify = job_classify_list[relative_url_list.index(relative_url_obj)]

                # 需要将相关地理信息修改为全国
                relative_url = re.sub(r'&dqs=(\d*)', '', relative_url_obj)
                yield Request(url=parse.urljoin('https://www.liepin.com', relative_url),
                              callback=self.parse_crawl_urls, meta={'job_classify': job_classify})

    def parse_crawl_urls(self, response):
        """
        获取待爬取的url
        :param response:
        :return:
        """
        crawl_urls = response.css('h3 a::attr(href)').extract()
        for crawl_url in crawl_urls:
            time.sleep(random.randint(1, 2))
            yield Request(url=parse.urljoin('https://www.liepin.com', crawl_url),
                          callback=self.parse_detail,
                          meta={'job_classify': response.meta['job_classify']})

        # 如果没有下一页直接return即可
        no_next_tag = response.css('.last.disabled')
        if no_next_tag:
            return

        # 下一页的url在翻页node的倒数第三个
        next_url = response.css('.pagerbar a::attr(href)').extract()[-3]
        time.sleep(random.randint(2, 4))
        yield Request(url=parse.urljoin('https://www.liepin.com', next_url),
                      callback=self.parse_crawl_urls,
                      meta={'job_classify': response.meta['job_classify']})

    def parse_detail(self, response):
        """
        解析网页细节
        :param response:
        :return:
        """
        liepin_item = PositionItem()
        url = response.url
        position_name = response.css('h1::text').extract_first()

        # 获取salary失败的直接return
        salary = response.css('.job-item-title::text').extract_first()
        if not salary:
            salary = response.css('.job-main-title::text').extract_first()
            if not salary:
                return

        salary_list = re.findall(r'(\d*)-(\d*)万', salary)[0]
        salary_min = float(salary_list[0]) * 10000 / 12
        salary_max = float(salary_list[1]) * 10000 / 12

        welfare_list = response.css('.comp-tag-list span::text').extract()
        if welfare_list:
            welfare = ';'.join(welfare_list)
        else:
            welfare = '无'
        working_place = response.css('.basic-infor a::text').extract_first()

        other_message_list = response.css('.job-qualifications span::text').extract()
        working_exp = other_message_list[1]
        education = other_message_list[0]

        abstract = response.css('.job-description').extract_first()
        if abstract:
            abstract = remove_r_n_t(remove_tags(abstract))

        company_name = response.css('.company-logo p a::text').extract_first()

        liepin_item['url_object_id'] = get_md5(url)
        liepin_item['url'] = url
        liepin_item['position_name'] = position_name
        liepin_item['salary_min'] = salary_min
        liepin_item['salary_max'] = salary_max
        # welfare以分号分割
        liepin_item['welfare'] = welfare
        liepin_item['working_place'] = working_place
        liepin_item['working_exp'] = working_exp
        liepin_item['education'] = education
        liepin_item['abstract'] = abstract.replace('\n', '').replace('\t', '').replace('\r',
                                                                                     '').replace(
            ' ', '')[:200]
        liepin_item['data_source'] = '猎聘网'
        liepin_item['company_name'] = company_name.strip()
        liepin_item['job_classify'] = response.meta['job_classify']

        yield liepin_item
