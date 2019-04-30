# -*- coding: utf-8 -*-
import scrapy
import json
import re
import time
import requests
import random
import redis

from scrapy.http import Request
from PositionSpider.items import PositionItem
from PositionSpider.utils.common import get_md5
from w3lib.html import remove_tags
from scrapy_redis.spiders import RedisSpider


from PositionSpider.utils.common import remove_r_n_t
from PositionSpider import settings


class ZhilianSpider(RedisSpider):
    name = 'zhilian'
    allowed_domains = ['www.zhaopin.com', 'jobs.zhaopin.com', 'fe-api.zhaopin.com']
    start_urls = ['http://www.zhaopin.com/']

    def __init__(self):
        """
        初始化向redis中添加start_urls
        """
        redis_cli = redis.Redis(host=settings.REDIS_ADDRESS, port=6379)
        if redis_cli.exists(self.redis_key) == 0:
            redis_cli.lpush(self.redis_key, 'http://www.zhaopin.com/')

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

        for crawl_name_obj in crawl_name_list:
            # 用来获取数据总条数
            start_crawl_url = crawl_url_model % (0, crawl_name_obj, random.random(), random.random())
            res = requests.get(start_crawl_url)
            json_dict = json.loads(res.text)
            # 第一次请求获取总数量的同时将顺便获取到的数据也yield到parse_detail函数中去
            if json_dict and json_dict['code'] == 200:
                total_num = json_dict['data']['numTotal']
                result_list = json_dict['data']['results']
                for result_obj in result_list:
                    yield Request(url=result_obj['positionURL'], callback=self.parse_detail,
                                  meta={'job_classify': crawl_name_obj})

                # 从最后一页向前遍历解析
                if total_num:
                    page_end = int(total_num / 90)

                    while True:
                        if page_end == 0:
                            break
                        else:
                            request_url = crawl_url_model % (page_end * 90, crawl_name_obj,
                                                             random.random(), random.random())
                            yield Request(url=request_url, callback=self.parse_crawl_list,
                                          meta={'job_classify': crawl_name_obj})
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
                yield Request(url=result_obj['positionURL'], callback=self.parse_detail,
                              meta={'job_classify': response.meta['job_classify']})

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

        # 有新旧detail网页之分，所以抓取方式有不同
        position_name = response.css('.info-h3::text')
        if not position_name:
            position_name = response.css('.summary-plane__title::text')

        position_name = position_name.extract_first().replace('\n', '').strip()
        company_name = response.css('.company__title::text').extract_first()

        salary = response.css('.summary-plane__salary::text').extract_first()
        if salary:
            salary = re.split('-', salary)
            salary_min = salary[0]
            salary_max = salary[1]
            if '万' in salary_min:
                salary_min = float(re.findall(r'(.*)万', salary_min)[0])
                salary_min = salary_min * 10000
            else:
                salary_min = float(re.findall(r'(.*)千', salary_min)[0])
                salary_min = salary_min * 1000

            if '万' in salary_max:
                salary_max = float(re.findall(r'(.*)万', salary_max)[0])
                salary_max = salary_max * 10000
            else:
                salary_max = float(re.findall(r'(.*)千', salary_max)[0])
                salary_max = salary_max * 1000

        info_list = response.css('.summary-plane__info li')
        if info_list:
            working_place = info_list[0].css('a::text').extract_first()
            working_exp = re.findall(r'(\d)-', info_list[1].css('::text').extract_first())
            if working_exp:
                working_exp = int(working_exp[0])
            else:
                working_exp = 0
            education = info_list[2].css('::text').extract_first()

            welfare_list = response.css('.highlights__content-item::text').extract()
            if welfare_list:
                welfare = ';'.join(welfare_list)
            else:
                welfare = '无'
        else:
            welfare = '无'

        abstract = remove_r_n_t(remove_tags(response.css('.describtion').extract_first()))

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
        zhilian_item['abstract'] = abstract[:250]
        zhilian_item['data_source'] = '智联招聘'
        zhilian_item['company_name'] = company_name
        zhilian_item['job_classify'] = response.meta['job_classify']

        yield zhilian_item
