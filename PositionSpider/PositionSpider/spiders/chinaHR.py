# -*- coding: utf-8 -*-
import scrapy

from PositionSpider.items import PositionItem


class ChinahrSpider(scrapy.Spider):
    name = 'chinaHR'
    allowed_domains = ['http://campus.chinahr.com/']
    start_urls = ['http://campus.chinahr.com/qz/P1/?job_type=10&city=1&industry=1100&']

    def __init__(self):
        """
        处理化start_url
        """
        pass

    def parse(self, response):
        """
        解析待爬url列表
        :param response:
        :return:
        """

        pass

    def parse_detail(self, response):
        """
        解析网页具体细节
        :param response:
        :return:
        """

        chinaHR['url_object_id'] = get_md5(url)
        chinaHR['url'] = url
        chinaHR['position_name'] = position_name
        chinaHR['salary_min'] = salary_min
        chinaHR['salary_max'] = salary_max
        # welfare以分号分割
        chinaHR['welfare'] = welfare
        chinaHR['working_place'] = working_place
        chinaHR['working_exp'] = working_exp
        chinaHR['education'] = education
        chinaHR['working_type'] = working_type
        chinaHR['position_num'] = position_num
        chinaHR['responsibility'] = responsibility.replace('\n', '').strip()
        chinaHR['data_source'] = '中华英才网'
        chinaHR['publish_time'] = datetime.datetime.now().date()
        chinaHR['other_message'] = ''
        pass
