# -*- coding: utf-8 -*-
import scrapy
import re
import requests
import random
import time
import redis
import json
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy_redis.spiders import RedisSpider


from VideoSpider import settings
from VideoSpider.utils.common import get_md5
from VideoSpider.items import VideoItem


class BaiduChuankeSpider(RedisSpider):
    name = 'baidu_chuanke'
    allowed_domains = ['chuanke.baidu.com']
    # start_urls = []
    redis_key = 'baidu_chuanke:start_urls'

    def __init__(self):
        """
        初始化目录字典，key为相对url，value为一级目录和二级目录(以\t分割)
        """
        redis_cli = redis.Redis(host=settings.REDIS_ADDRESS, port=6379)

        self.category_dict = settings.BAIDU_CHUANKE_MAP
        start_urls = ['https://chuanke.baidu.com/course/%s_____.html'
                           % category_obj for category_obj in self.category_dict.keys()]
        # master端将这个循环打开
        # for start_url in start_urls:
        #     redis_cli.lpush(self.redis_key, start_url)

    def parse(self, response):
        """
        解析网页
        :param response:
        :return:
        """
        category_key = re.findall(r'course/(\d*)_____.html', response.url)[0]
        classify_list = self.category_dict[category_key].split('\t')
        crawl_urls = response.css('.item-pic a::attr(href)').extract()
        learn_nums_list = response.css('.number em::text').extract()

        for crawl_url in crawl_urls:
            time.sleep(random.randint(1, 2))
            yield Request(url='https:%s' % crawl_url, meta={'first_classify': classify_list[0],
                                                           'second_classify': classify_list[1],
                                                           'learn_nums_list': learn_nums_list,
                                                           'index': crawl_urls.index(crawl_url)},
                          callback=self.parse_detail)

        next_url = response.css('.next::attr(href)').extract_first()
        if next_url:
            yield Request(url=next_url, callback=self.parse)

    def parse_detail(self, response):
        """
        解析具体网页信息
        :param response:
        :return:
        """
        baidu_chuanke_item = VideoItem()

        evaluation_score = response.css('.rate::text').extract_first()
        # 如果没有分数代表该课程是有问题的课程，直接return
        if evaluation_score:
            evaluation_score = float(evaluation_score)
        else:
            return

        class_name = response.css('.class-name::text').extract_first()
        url = response.url
        learner_nums = response.meta['learn_nums_list'][response.meta['index']]
        if '万' in learner_nums:
            learner_nums = re.findall(r'(.*)万', learner_nums)[0]
            learner_nums = float(learner_nums) * 10000

        price = response.css('.text.money::text').extract_first()
        if price == '免费':
            price = 0

        fit_people = response.css('.con-intro tr td .item::text').extract()

        # 有时候取的值是空
        if fit_people:
            fit_people = fit_people[0]
        else:
            fit_people = ''
        abstract_list = response.css('.con-intro p::text').extract()
        abstract = ''.join(abstract_list).replace('\n', '').replace('\t', '').strip()
        if abstract == '':
            abstract_list = response.css('.con-intro p span::text').extract()
            abstract = ''.join(abstract_list).replace('\n', '').replace('\t', '').strip()
            if abstract == '':
                abstract = response.css('#brief-detail span::text').extract_first()
                if not abstract:
                    abstract = ''

        category_list = response.css('.chapter-title::text').extract()
        category = '\t'.join(category_list)
        class_nums = len(category_list)
        institution = response.css('.yahei::text').extract_first()
        first_classify = response.meta['first_classify']
        second_classify = response.meta['second_classify']

        evaluation_person = response.css('#vote-list-tab span::text').extract_first()

        # 有时候取的值为空
        if evaluation_person:
            evaluation_person = int(evaluation_person)
        else:
            evaluation_person = 0

        evaluation_content = self.get_evaluation_content(response.url)

        # 赋值item相应属性
        baidu_chuanke_item['url_object_id'] = get_md5(url)
        baidu_chuanke_item['url'] = url
        baidu_chuanke_item['price'] = float(price)
        baidu_chuanke_item['class_name'] = class_name
        if isinstance(learner_nums, str) and '万' in learner_nums:
            learner_nums = float(re.findall(r'(.*)万', learner_nums)[0]) * 10000
        baidu_chuanke_item['learner_nums'] = int(learner_nums)
        baidu_chuanke_item['class_nums'] = class_nums
        baidu_chuanke_item['category'] = category
        baidu_chuanke_item['abstract'] = abstract.replace('\t', '').replace('\n', '').strip()[:300]
        baidu_chuanke_item['data_source'] = '百度传课'
        baidu_chuanke_item['institution'] = institution
        baidu_chuanke_item['fit_people'] = fit_people
        baidu_chuanke_item['first_classify'] = first_classify
        baidu_chuanke_item['second_classify'] = second_classify
        baidu_chuanke_item['evaluation_person'] = evaluation_person
        baidu_chuanke_item['evaluation_score'] = float(evaluation_score)
        baidu_chuanke_item['evaluation_content'] = evaluation_content

        yield baidu_chuanke_item
        # pass

    def get_evaluation_content(self, url):
        """
        获取评价主题内容及score
        :param url: eg:https://chuanke.baidu.com/v3377987-128943-328097.html
        :return:
        """
        sid = re.findall(r'v(\d*)-', url)[0]
        courseid = re.findall(r'-(\d*)-', url)[0]
        url_model = 'https://chuanke.baidu.com/?mod=course&act=show&do=comment&sid=%s&' \
              'courseid=%s&appraise=0&comment_flag=0&page=%d&r=%s'
        page = 1
        content_list = list()
        while True:
            time.sleep(1)
            res = requests.get(url_model % (sid, courseid, page, random.random()))
            selector = Selector(text=res.content)

            # 需要将评分和评论内容放在一起进行抓取
            comment_node_list = selector.css('.course-comment-list .item')

            if comment_node_list:
                for comment_node_obj in comment_node_list:
                    comment = comment_node_obj.css('.info::text').extract_first()
                    if not comment:
                        continue
                    score = comment_node_obj.css('.item .praise::text').extract_first()
                    if '好评' in score:
                        score = 10
                    elif '中评' in score:
                        score = 5
                    else:
                        score = 0
                    content_list.append(json.dumps({comment.replace('"', ''): score}, ensure_ascii=False))

                page += 1

            else:
                break

        return '\t'.join(content_list)
