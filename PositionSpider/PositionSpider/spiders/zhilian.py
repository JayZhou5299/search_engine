# -*- coding: utf-8 -*-
import scrapy
import json
import re
import datetime
import time
import requests
import random

from scrapy.http import Request
from PositionSpider.items import PositionItem
from PositionSpider.utils.common import get_md5

class ZhilianSpider(scrapy.Spider):
    name = 'zhilian'
    allowed_domains = ['www.zhaopin.com', 'jobs.zhaopin.com', 'fe-api.zhaopin.com']
    start_urls = ['http://www.zhaopin.com/']

    def parse(self, response):
        """
        获取需要爬取的岗位列表
        :param response:
        :return:
        """
        # 爬取url模版
        crawl_url_model = 'https://fe-api.zhaopin.com/c/i/sou?start=%d&pageSize=90&cityId=489&' \
                           'workExperience=-1&education=-1&companyType=-1&employmentType=-1' \
                           '&jobWelfareTag=-1&kw=%s&kt=3&_v=%s&' \
                           'x-zp-page-request-id=%s'
        # 只需要爬取互联网相关的即可
        crawl_div_node = response.css('.zp-jobNavigater__pop--container')[0]
        crawl_name_list = crawl_div_node.css('a::text').extract()
        crawl_name_list = ['PHP']

        for crawl_name_obj in crawl_name_list:
            # 用来获取数据总条数
            start_crawl_url = crawl_url_model % (0, crawl_name_obj, random.random, random.random)
            res = requests.get(start_crawl_url)
            json_dict = json.loads(res.text)
            # 第一次请求获取总数量的同时将顺便获取到的数据也yield到parse_detail函数中去
            if json_dict and json_dict['code'] == 200:
                total_num = json_dict['data']['numTotal']
                result_list = json_dict['data']['results']
                for result_obj in result_list:
                    yield Request(url=result_obj['positionURL'], callback=self.parse_detail)

                # 从最后一页向前遍历解析
                if total_num:
                    page_end = int(total_num / 90)

                    while True:
                        if page_end == 0:
                            break
                        else:
                            request_url = crawl_url_model % (page_end * 90, crawl_name_obj, random.random(), random.random())
                            yield Request(url=request_url, callback=self.parse_crawl_list)
                            page_end -= 1

    def parse_crawl_list(self, response):
        """
        处理爬取的列表
        :param response:
        :return:
        """
        json_dict = json.loads(response.text)
        if json_dict:
            result_list = json_dict['data']['results']
            for result_obj in result_list:
                # time.sleep(random.randint(1, 5))
                yield Request(url=result_obj['positionURL'], callback=self.parse_detail)

    def parse_detail(self, response):
        """
        解析具体网页细节信息
        :param response:
        :return:
        """
        zhilian_item = PositionItem()
        # 失效的职位直接返回即可
        unvaild_tag = response.css('.unvalid-job-img')
        if unvaild_tag:
            return

        url = response.url
        position_name = response.css('.info-h3::text').extract_first().replace('\n', '').strip()
        if '实习' in position_name:
            working_type = '实习'
        else:
            working_type = '全职'
        salary = response.css('.info-money strong::text').extract_first()
        if salary:
            salary = re.findall(r'(\d*)-(\d*)', salary)
            salary_min = int(salary[0][0])
            salary_max = int(salary[0][1])

        info_list = response.css('.info-three span')
        if info_list:
            working_place = info_list[0].css('a::text').extract_first()
            working_exp = re.findall(r'(\d)-', info_list[1].css('::text').extract_first())
            if working_exp:
                working_exp = int(working_exp[0])
            else:
                working_exp = 0
            education = info_list[2].css('::text').extract_first()
            position_num = info_list[3].css('::text').extract_first()
            if position_num:
                position_num = int(re.findall(r'(\d*)人', position_num)[0])

            welfare = re.findall(r'JobWelfareTab = (.*?);', response.text)
            if welfare:
                welfare = welfare[0]
            else:
                welfare = ''

        responsibility = response.css('.pos-ul span::text').extract()
        if responsibility:
            responsibility = ';'.join(responsibility)
        else:
            responsibility = response.css('.responsibility div::text').extract()
            if responsibility:
                responsibility = ';'.join(responsibility)

        zhilian_item['url_object_id'] = get_md5(url)
        zhilian_item['url'] = url
        zhilian_item['position_name'] = position_name
        zhilian_item['salary_min'] = salary_min
        zhilian_item['salary_max'] = salary_max
        # welfare以分号分割
        zhilian_item['welfare'] = welfare
        zhilian_item['working_place'] = working_place
        zhilian_item['working_exp'] = working_exp
        zhilian_item['education'] = education
        zhilian_item['working_type'] = working_type
        zhilian_item['position_num'] = position_num
        zhilian_item['responsibility'] = responsibility.replace('\n', '').strip()
        zhilian_item['data_source'] = '智联招聘'
        zhilian_item['publish_time'] = datetime.datetime.now().date()
        zhilian_item['other_message'] = ''

        yield zhilian_item
