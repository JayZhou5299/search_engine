# -*- coding: utf-8 -*-
import scrapy
import requests
import redis
import re
import random
import time
import json

from scrapy.http import Request
from scrapy.selector import Selector
from w3lib.html import remove_tags
from scrapy_redis.spiders import RedisSpider

from VideoSpider.items import VideoItem
from VideoSpider.utils.common import get_md5
from VideoSpider import settings


class Edu51ctoSpider(RedisSpider):
    """
    51cto学院爬虫
    """
    name = 'edu_51cto'
    allowed_domains = ['edu.51cto.com']
    # start_urls = []
    redis_key = 'edu_51cto:start_urls'

    def __init__(self):
        """
        初始化相关start_urls
        """
        redis_cli = redis.Redis(host=settings.REDIS_ADDRESS, port=6379)
        res = requests.get('https://edu.51cto.com/')
        selector = Selector(text=res.text)

        # 将start_urls插入到redis中，slave端需要把这些注释掉，否则会重复抓取
        start_urls = selector.css('.ins.clearfix2 .items_cs dd a::attr(href)').extract()
        for start_url in start_urls:
            redis_cli.lpush(start_url)

    def parse(self, response):
        """
        解析待爬取url
        :param response:
        :return:
        """
        crawl_urls = response.css('.cList h3 a::attr(href)').extract()
        for crawl_url in crawl_urls:
            yield Request(url=crawl_url, callback=self.parse_detail)
        time.sleep(random.random(1, 4))
        next_url = response.css('.next a::attr(href)').extract_first()
        if next_url:
            yield Request(url=next_url, callback=self.parse)

    def parse_detail(self, response):
        """
        解析具体网页信息
        :param response:
        :return:
        """
        edu_51cto_item = VideoItem()
        url = response.url
        course_id = re.findall(r'course/(\d*)', url)
        # 如果匹配不成功直接返回0和none即可
        if course_id:
            course_id = course_id[0]

        # 可以通过网页右上角的导航栏提取出一二级分类以及标题
        classify_title_list = response.css('.roadLink a::text').extract()
        first_classify = classify_title_list[1]
        second_classify = classify_title_list[2]
        class_name = classify_title_list[3]
        price = response.css('.main.fr .price .fl.red::text').extract_first()
        if price == '免费':
            price = 0
        else:
            price = price.replace('¥', '').strip()

        learner_nums = response.css('#students .tit::text').extract_first()
        if learner_nums:
            learner_nums = re.findall(r'(\d*)', learner_nums)[0]

        abstract = response.css('.tabsCon').extract_first()
        abstract = remove_tags(abstract).replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '')

        fit_people = response.css('.tabsConItem.intro dd::text').extract()
        if len(fit_people) >= 1:
            fit_people = fit_people[1]
        else:
            fit_people = ''

        category_list = self.get_category(course_id)

        if not category_list:
            category_node_list = response.css('.lesson')
            for category_node_obj in category_node_list:
                category_obj = category_node_obj.css('a::text').extract_first()
                category_list.append(category_obj)

        category = '\t'.join(category_list)
        class_nums = len(category_list)

        institution = response.css('.lecInfo h2 a::text').extract_first()

        evaluation_score = response.css('#hasNumbers::text').extract_first()
        if evaluation_score:
            evaluation_score = int(evaluation_score) * 20
        evaluation_person, evaluation_content_list = self.get_evaluation_content_and_person(course_id)
        if evaluation_content_list:
            evaluation_content = '\t'.join(evaluation_content_list)
        else:
            evaluation_content = ''

        # 赋值item相应属性
        edu_51cto_item['url_object_id'] = get_md5(url)
        edu_51cto_item['url'] = url
        edu_51cto_item['price'] = float(price)
        edu_51cto_item['class_name'] = class_name
        if '万' in learner_nums:
            learner_nums = float(re.findall(r'(.*)万', learner_nums)[0]) * 10000
        edu_51cto_item['learner_nums'] = int(learner_nums)
        edu_51cto_item['class_nums'] = class_nums
        edu_51cto_item['category'] = category
        edu_51cto_item['abstract'] = abstract[:300]
        edu_51cto_item['data_source'] = '51CTO学院'
        edu_51cto_item['institution'] = institution
        edu_51cto_item['fit_people'] = fit_people
        edu_51cto_item['first_classify'] = first_classify
        edu_51cto_item['second_classify'] = second_classify
        edu_51cto_item['evaluation_person'] = evaluation_person
        edu_51cto_item['evaluation_score'] = float(evaluation_score)
        edu_51cto_item['evaluation_content'] = evaluation_content

        yield edu_51cto_item

    def get_category(self, course_id):
        """
        获取目录信息
        :param url:
        :return:
        """
        time.sleep(1)
        url_model = 'https://edu.51cto.com/center/course/index/lesson-list?page=%d&size=20&id=%s'
        category_list = list()
        page = 1
        while True:
            url = url_model % (page, course_id)
            res = requests.get(url)
            json_dict = json.loads(res.text)
            if json_dict['data']:
                chapter_list = json_dict['data']['lessonList']
                for chapter_obj in chapter_list:
                    if chapter_obj['type'] == 'chapter':
                        category_list.append(chapter_obj['title'])
                page += 1
            else:
                break

        return category_list

    def get_evaluation_content_and_person(self, course_id):
        """
        获取评价内容信息
        :return:
        """
        content_list = list()
        url_model = 'https://edu.51cto.com/center/appraise/index/get-appraise-list?' \
                    'page=%d&size=20&course_id=%s&level=0&category=0'
        page = 1
        while True:
            url = url_model % (page, course_id)
            res = requests.get(url)
            json_dict = json.loads(res.text)
            if json_dict['msg'] == '成功':
                data_list = json_dict['data']
                for data_obj in data_list:
                    content_list.append(json.dumps({data_obj['content'].replace('"', ''): float(data_obj['rate']) * 2},
                                                   ensure_ascii=False))

                # 如果返回数据的长度是20，代表还需要翻页
                if len(data_list) == 20:
                    page += 1
                else:
                    break
            else:
                break

        return len(content_list), content_list
