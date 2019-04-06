# -*- coding: utf-8 -*-
import scrapy
import re

from scrapy import Request
from urllib import parse

from PositionSpider.items import PositionItem


class BossSpider(scrapy.Spider):
    name = 'Boss'
    allowed_domains = ['www.zhipin.com']
    start_urls = ['http://www.zhipin.com/']

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

            # 需要将城市改为全国，所以要对相对url进行替换
            for relative_url_obj in relative_url_list:
                relative_url = re.sub(r'c(\d*)-', 'c100010000-', relative_url_obj)
                url = 'https://www.zhipin.com%s%s' % (relative_url, 'e_102')
                yield Request(url=url, callback=self.parse_crawl_urls)

    def parse_crawl_urls(self, response):
        """
        获取待爬取的url
        :param response:
        :return:
        """
        pass

    def parse_detail(self, response):
        """
        解析网页细节
        :param response: 
        :return: 
        """
        
        Boss_item['url_object_id'] = get_md5(url)
        Boss_item['url'] = url
        Boss_item['position_name'] = position_name
        Boss_item['salary_min'] = salary_min
        Boss_item['salary_max'] = salary_max
        # welfare以分号分割
        Boss_item['welfare'] = welfare
        Boss_item['working_place'] = working_place
        Boss_item['working_exp'] = working_exp
        Boss_item['education'] = education
        Boss_item['working_type'] = working_type
        Boss_item['position_num'] = position_num
        Boss_item['responsibility'] = responsibility.replace('\n', '').strip()
        Boss_item['data_source'] = '中华英才网'
        Boss_item['publish_time'] = datetime.datetime.now().date()
        Boss_item['other_message'] = ''
        pass