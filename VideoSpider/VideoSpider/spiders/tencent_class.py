# -*- coding: utf-8 -*-
"""
腾讯课堂爬虫
"""
import scrapy
import re
import time
import json
import redis
import random
import requests
from scrapy.http import Request
from fake_useragent import UserAgent
from urllib import request
from http import cookiejar

from scrapy_redis.spiders import RedisSpider


from VideoSpider.items import VideoItem
from VideoSpider.utils.common import get_md5
from VideoSpider import settings


GET_CATEGORY_URL = 'https://ke.qq.com/cgi-bin/get_cat_info?bkn=&r=0'


class TecentClassSpider(RedisSpider):
    name = 'tencent_class'
    allowed_domains = ['ke.qq.com']
    # start_urls = ['https://ke.qq.com/course/list?mt=1001&st=2002&tt=3007']
    # start_urls = []
    redis_key = 'tencent_class:start_urls'

    def __init__(self):
        """
        获取课程的目录信息
        """
        redis_cli = redis.Redis(host=settings.REDIS_ADDRESS, port=6379)

        self.category_dict = dict()
        self.get_category_dict()
        self.ua = UserAgent()

        # master端需要打开下面的循环
        # for relative_url in self.category_dict.keys():
        #     redis_cli.lpush(self.redis_key, ('https://ke.qq.com/course/list?mt=1001%s' % relative_url))
            # self.start_urls.append('https://ke.qq.com/course/list?mt=1001%s' % relative_url)

    def get_category_dict(self):
        """
        获取目录字典，key为相对url，value为'一级分类,二级分类'
        :return:
        """
        res = json.loads(requests.get(GET_CATEGORY_URL).text)

        # 获取目录信息的字典
        category_info_dict = res['result']['catInfo']['1001']['s']

        for st, value_dict in category_info_dict.items():
            first_classify = value_dict['n']

            for tt, value_obj in value_dict['t'].items():
                second_classify = value_obj['n']
                relative_url = '&st=%s&tt=%s' % (st, tt)
                self.category_dict[relative_url] = '%s,%s' % (first_classify, second_classify)

    def parse(self, response):
        """
        提取要爬取的细节url
        :param response:
        :return:
        """
        crawl_urls = response.css('.course-card-list-multi-wrap .course-card-item .item-tt-link::attr(href)').extract()

        # 对不同的url格式做不同的处理
        if 'page' in response.url:
            category_key = re.findall(r'(&st.*)&page', response.url)[0]
        else:
            category_key = re.findall(r'(&st.*$)', response.url)[0]

        classify_list = self.category_dict[category_key].split(',')
        for crawl_url in crawl_urls:
            yield Request(url='https:' + crawl_url, callback=self.parse_detail,
                          meta={'first_classify': classify_list[0],
                                'second_classify': classify_list[1]})

        next_url = response.css('.page-next-btn::attr(href)').extract_first()
        if next_url:
            yield Request(url=next_url, callback=self.parse)

    def parse_detail(self, response):
        """
        解析具体网页
        :param response:
        :return:
        """
        tencent_class_item = VideoItem()
        url = response.url
        # 免费的和付费的课程详情页是不一样的，需要分情况解析
        price = response.css('.course-price-info .price::text').extract_first()

        # 付费情况
        if price and price != '免费':
            class_name = response.css('.title-main::text').extract_first()
            learner_nums = response.css('.statistics-apply::text').extract_first()
            learner_nums = int(re.findall(r'(\d*)人', learner_nums)[0])
            price = float(price.replace('¥', ''))

        # 免费情况
        else:
            price = 0
            class_name = response.css('.course-title h3::text').extract_first()
            learner_nums = response.css('.hint-data::text').extract()

            # 如果长度小于2直接返回
            if len(learner_nums) < 2:
                return
            else:
                learner_nums = learner_nums[1]
            if '万' in learner_nums:
                learner_nums = int(re.findall(r'(\d*)万', learner_nums)[0]) * 10000

        # 公共处理的部分
        category_list = self.get_category_list(url, response)
        category = '\t'.join(category_list)
        class_nums = len(category_list)
        abstract = response.css('.tb-course td::text').extract_first()
        institution = response.css('.js-agency-name::text').extract_first().replace('\n', '').replace(' ', '')
        fit_people = ''
        first_classify = response.meta['first_classify']
        second_classify = response.meta['second_classify']
        print (response.css('.js-comment-total::text').extract_first())
        evaluation_person, evaluation_score = self.get_evaluation_sum_and_score(response.url)
        evaluation_content = self.get_evaluation_content(response.url)

        # 赋值item相应属性
        tencent_class_item['url_object_id'] = get_md5(url)
        tencent_class_item['url'] = url
        tencent_class_item['price'] = float(price)
        tencent_class_item['class_name'] = class_name
        tencent_class_item['learner_nums'] = int(learner_nums)
        tencent_class_item['class_nums'] = int(class_nums)
        tencent_class_item['category'] = category
        tencent_class_item['abstract'] = abstract[:300]
        tencent_class_item['data_source'] = '腾讯课堂'
        tencent_class_item['institution'] = institution
        tencent_class_item['fit_people'] = fit_people
        tencent_class_item['first_classify'] = first_classify
        tencent_class_item['second_classify'] = second_classify
        tencent_class_item['evaluation_person'] = int(evaluation_person)
        tencent_class_item['evaluation_score'] = float(evaluation_score)
        tencent_class_item['evaluation_content'] = evaluation_content

        yield tencent_class_item

    def get_category_list(self, url, css_response):
        """
        获取课程目录列表
        :return:
        """
        category_list = list()
        headers = {"Accept": "application/json",
                   "Content-Type": "application/json",
                   # "Referer": "https://ke.qq.com/webcourse/frame.html?r=%d",
                   "Referer": url,
                   "User-Agent": self.ua.random
                   }
        course_id = re.findall(r'course/(\d*)$', url)[0]
        response = requests.get('https://ke.qq.com/cgi-bin/get_course_latest_liveTask?'
                         'course_id=%s&bkn=&r=%s' % (course_id, random.random()), headers=headers)
        res = json.loads(response.text, encoding='utf8')['result']
        term_id_list = list(res.keys())

        # 此处需要分两种情况，如果是通过后台json取的数据，则请求url，否则直接通过css提取即可
        if term_id_list:
            time.sleep(random.randint(1,4))
            headers['Referer'] = "https://ke.qq.com/webcourse/frame.html?r=%d" \
                                 % (round(time.time() * 1000))
            response = requests.get(url='https://ke.qq.com/cgi-bin/course/get_terms_detail?'
                                        'cid=%s&term_id_list=%%5B%s%%5D&bkn=&t=%s' % (course_id,
                                                                                      ','.join(
                                                                                          term_id_list),
                                                                                      random.random()),
                                    headers=headers)
            res_two = json.loads(response.text)['result']['terms'][0]['chapter_info'][0]['sub_info']
            for res_obj in res_two:
                category_list.append(res_obj['name'])

        else:
            category_list = css_response.css('.sub-section--tt::text').extract()
            if not category_list:

                # 此处需要使用re.s来做标记，使.运算符可以匹配任意字符包括换符
                unhandle_list = re.findall(r'var metaData = (.*),"isNodeEnv":', css_response.text, re.S)
                if unhandle_list:

                    # 需要将匹配到的js代码转换为json后进行遍历解析
                    json_str = unhandle_list[0].replace('\n', '').replace('\t', '').strip() + '}'
                    json_list = json.loads(json_str)
                    charpter_info_list = json_list['terms'][0]['chapter_info']
                    for charpter_info_obj in charpter_info_list:
                        sub_info_list = charpter_info_obj['sub_info']
                        for sub_info_obj in sub_info_list:
                            category_list.append(sub_info_obj['name'])

        return category_list

    def get_evaluation_sum_and_score(self, url):
        """
        获取评价总数，以及好评率
        :param url: 目前爬取的课程url连接 eg:    https://ke.qq.com/course/185189
        :return:
        """
        cookie_dict = dict()
        content_model_url = 'https://ke.qq.com/cgi-bin/comment_new/course_comment_stat' \
                            '?cid=%s&bkn=&r=%s'
        # 必须要referer才可以
        headers = {"Accept": "application/json",
                   "Content-Type": "application/json",
                   "Referer": url,
                   "User-Agent": self.ua.random
                   }

        # 声明一个CookieJar对象实例来保存cookie
        cookie = cookiejar.CookieJar()
        # 利用urllib.request库的HTTPCookieProcessor对象来创建cookie处理器,也就CookieHandler
        handler = request.HTTPCookieProcessor(cookie)
        # 通过CookieHandler创建opener
        opener = request.build_opener(handler)
        # 此处的open方法打开网页
        response = opener.open(url)

        for item in cookie:
            cookie_dict[item.name] = item.value

        course_id = re.findall(r'course/(\d*)$', url)[0]
        request_url = content_model_url % (course_id, random.random())
        res = json.loads(requests.get(request_url, headers=headers, cookies=cookie_dict).text,
                         encoding='utf8')['result']

        all_num = (int(res['all_num']) if 'all_num' in res.keys() else 0)
        good_percentage = (int(res['good_percentage']) if 'good_percentage' in res.keys() else 0)

        return all_num, good_percentage

    def get_evaluation_content(self, url):
        """
        获取评价主题内容信息，返回以\t分割的list组成的string,list中的内容其实是一个字典类型，将其转化为字符串即可
        :param url: 目前爬取的课程url连接 eg:    https://ke.qq.com/course/185189
        :return:
        """
        result_list = list()
        content_model_url = 'https://ke.qq.com/cgi-bin/comment_new/course_comment_list?' \
                        'cid=%s&count=10&page=%d&filter_rating=0&bkn=&r=%s'
        # 必须要referer才可以
        headers = {"Accept": "application/json",
                   "Content-Type": "application/json",
                   "Referer": url,
                   "User-Agent": self.ua.random
                   }

        # end_flag = 1表示到最后一页了，但此页还有数据，爬完后break
        course_id = re.findall(r'course/(\d*)$', url)[0]
        page = 0
        while True:
            time.sleep(random.randint(1, 3))
            request_url = content_model_url % (course_id, page, random.random())
            res = json.loads(requests.get(request_url, headers=headers).text)['result']
            content_list = res['items']

            # 如果有追加评论就与第一次的评论做一个merge
            for content_obj in content_list:
                content_dict = dict()
                comment = content_obj['first_comment']
                comment_score = content_obj['first_comment_score']
                if 'second_comment' in content_obj.keys():
                    comment = comment + ';' + content_obj['second_comment']
                if 'second_comment_score' in content_obj.keys():
                    comment_score = float(float(comment_score) + float(content_obj['second_comment_score'])) / 2

                content_dict[comment.replace('"', '')] = comment_score * 2

                result_list.append(json.dumps(content_dict, ensure_ascii=False))

            if res['end_flag'] == 1:
                break
            page += 1

        return '\t'.join(result_list)
