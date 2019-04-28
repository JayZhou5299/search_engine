# -*- coding: utf-8 -*-
import scrapy
import re
import redis
import json
import requests
from scrapy.http import Request
from scrapy.selector import Selector
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy_redis.spiders import RedisSpider

from VideoSpider.items import VideoItem
from VideoSpider.utils.common import get_md5
from VideoSpider import settings


class ImoocSpider(RedisSpider):
    name = 'imooc'
    allowed_domains = ['www.imooc.com', 'coding.imooc.com']
    # start_urls = []
    redis_key = 'imooc:start_urls'

    def __init__(self):
        """
        初始化类别与url字典,key为url地址,value为一级分类,二级分类
        """
        # 实战课程的分类列表与url相对路径需要初始化，免费课程可以在detail页面抓取
        redis_cli = redis.Redis(host=settings.REDIS_ADDRESS, port=6379)
        self.imooc_fee_class_map = settings.IMOOC_MAP
        res = requests.get('https://www.imooc.com')
        selector = Selector(text=res.text)
        second_classify_node_list = selector.css('.clearfix .tag-box')

        # 添加免费课程的url到start_url
        for i in range(len(second_classify_node_list)):
            href_list = second_classify_node_list[i].css('a::attr(href)').extract()

            for j in range(len(href_list)):
                key_url = urljoin('http://www.imooc.com', href_list[j])
                # slave节点需要将下面的push操作注释掉，否则将会重复添加start_urls
                # redis_cli.lpush(self.redis_key, key_url)
                # self.start_urls.append(key_url)

        # 添加实战课程的url到start_url
        for url in self.imooc_fee_class_map.keys():
            key_url = 'https://coding.imooc.com/?c=%s' % url
            # slave节点需要将下面的push操作注释掉，否则将会重复添加start_urls
            # redis_cli.lpush(self.redis_key, key_url)
            # self.start_urls.append(key_url)

    def parse(self, response):
        """
        解析待爬取的url，根据url来判断是实战课程还是免费课程的列表页，实战课程的url包含coding字符串
        :param response:
        :return:
        """
        #对实战课程的处理
        if 'coding' in response.url:
            # 没有课程的标记，如果这个不为空，代表本页为空，直接跳过即可
            no_course_tag = response.css('.no-course::text').extract_first()
            if no_course_tag:
                return
            # key = re.findall(r'c=(.*)[$&]', response.url)[0]

            # 有两种url需要提取出来
            # eg:https://coding.imooc.com/?c=java&sort=2&unlearn=0&page=1
            # eg:https://coding.imooc.com/?c=java
            key = re.findall(r'c=(.*?)&', response.url)
            if key:
                key = key[0]
            else:
                key = re.findall(r'c=(.*)$', response.url)[0]

            classify_list = self.imooc_fee_class_map[key].split('\t')
            first_classify = classify_list[0]
            second_classify = classify_list[1]

            crawl_urls = response.css('.shizhan-course-wrap a::attr(href)').extract()
            for crawl_url in crawl_urls:
                crawl_url = urljoin('https://coding.imooc.com', crawl_url)

                # meta中的tag字段标志是收费还是免费的课程，fee表示收费，free表示免费
                yield Request(url=crawl_url, meta={'first_classify': first_classify,
                                                   'second_classify': second_classify,
                                                   'tag': 'fee'},
                              callback=self.parse_detail)

            page_num = re.findall(r'page=(\d*)', response.url)
            if page_num:
                page_num = int(page_num[0])
            else:
                page_num = 1

            next_url = 'https://coding.imooc.com/?c=%s&page=%d' % (key, page_num+1)
            yield Request(url=next_url, callback=self.parse)

        # 对免费课程的处理
        else:
            # 没有课程的标记，如果这个不为空，代表本页为空，直接跳过即可
            no_course_tag = response.css('.errorwarp').extract_first()
            if no_course_tag:
                return

            crawl_urls = response.css('.course-card::attr(href)').extract()
            for crawl_url in crawl_urls:
                yield Request(url=urljoin('https://www.imooc.com', crawl_url),
                              callback=self.parse_detail, meta={'tag': 'free'})

            # 根据不同的url进行相应的翻页处理
            if 'page' in response.url:
                page_num = int(re.findall(r'page=(\d*)', response.url)[0])
                next_url = re.sub(r'page=(\d*)', 'page=%s' % str(page_num+1), response.url)
            else:
                next_url = '%s&page=%d' % (response.url, 2)

            yield Request(url=next_url, callback=self.parse)

    def parse_detail(self, response):
        """
        解析网页细节,需要根据url来判断是实战课程还是免费课程
        :param response:
        :return:
        """
        imooc_item = VideoItem()
        url = response.url

        # 收费的课程处理
        if response.meta['tag'] == 'fee':
            price = response.css('.ori-price::text').extract_first()
            if price:
                price = price.replace('\t', '').replace('\n', '').replace('\r', '').replace('￥', '').replace('原价', '').strip()
            class_name = response.css('.title-box h1').extract_first()
            temp_list = response.css('.nodistance::text').extract()
            learner_nums = temp_list[2]
            category_list = self.get_category_list(url)
            class_nums = len(category_list)
            category = '\t'.join(category_list)
            abstract = response.css('.info-desc::text').extract_first()
            institution = response.css('.nickname::text').extract_first()
            first_classify = response.meta['first_classify']
            second_classify = response.meta['second_classify']
            evaluation_score = temp_list[3].replace('分', '').replace('%', '')

            class_id = re.findall(r'class/(\d*)', response.url)
            if class_id:
                class_id = class_id[0]
            evaluation_content = self.get_evaluation_content_fee(class_id)
            evaluation_person = response.css('.comp-tab-item span::text').extract()
            if evaluation_person:
                evaluation_person = evaluation_person[1]

        # 免费的课程处理
        else:
            price = 0
            category_list = list()
            class_name = response.css('.hd .l::text').extract_first()
            id = re.findall(r'learn/(\d*)', response.url)[0]
            learner_nums = self.get_learner_nums(id)
            category_temp_list = response.css('.chapter h3::text').extract()
            for category_temp_obj in category_temp_list:
                category_list.append(category_temp_obj.replace('\n', '').replace('\t', '').strip())
            category = '\t'.join(category_list)
            class_nums = len(category_list)
            abstract = response.css('.course-description::text').extract_first()
            if abstract:
                abstract = abstract.replace('\n', '').strip()
            institution = response.css('.tit a::text').extract_first()
            classify_list = response.css('.path a::text').extract()
            first_classify = classify_list[1]
            second_classify = classify_list[2]
            evaluation_person = response.css('.course-menu li span::text').extract()

            # 提取出来的只是一个列表
            if evaluation_person:
                evaluation_person = evaluation_person[1]

            class_id = re.findall(r'learn/(\d*)', response.url)[0]
            evaluation_score = response.css('.meta-value::text').extract()
            if evaluation_score:
                evaluation_score = evaluation_score[2]
            evaluation_content = self.get_evaluation_and_content(class_id)

        # 赋值item相应属性
        imooc_item['url_object_id'] = get_md5(url)
        imooc_item['url'] = url
        imooc_item['price'] = float(price)
        imooc_item['class_name'] = class_name
        imooc_item['learner_nums'] = int(learner_nums)
        imooc_item['class_nums'] = class_nums
        imooc_item['category'] = category
        imooc_item['abstract'] = abstract[:300]
        imooc_item['data_source'] = 'imooc'
        imooc_item['institution'] = institution
        imooc_item['fit_people'] = ''
        imooc_item['first_classify'] = first_classify
        imooc_item['second_classify'] = second_classify
        imooc_item['evaluation_person'] = int(evaluation_person)
        imooc_item['evaluation_score'] = float(evaluation_score) / 10
        imooc_item['evaluation_content'] = evaluation_content

        yield imooc_item

    def get_category_list(self, url):
        """
        获取目录列表
        :return:
        """
        # 现在：https://coding.imooc.com/class/chapter/104.html
        # 原来：https://coding.imooc.com/class/104.html
        class_id = re.findall(r'class/(.*)', url)
        if class_id:
            get_url = 'https://coding.imooc.com/class/chapter/%s' % class_id[0]
            res = requests.get(get_url)
            selector = Selector(text=res.content)
            category_list = selector.css('.chapter-bd h5::text').extract()
            if category_list:
                return category_list
            else:
                return []

    def get_learner_nums(self, id):
        """
        获取学习人数
        :return:
        """
        res = requests.get('http://www.imooc.com/course/AjaxCourseMembers?ids=%s' % id)
        if res:
            res = json.loads(res.text)
            if res['msg'] == '成功':
                learner_nums = res['data'][0]['numbers']
                if learner_nums:
                    return int(learner_nums)

        return 0

    def get_evaluation_content_fee(self, class_id):
        """
        针对实战课程，获取用户评价分数与评价内容
        :return:
        """
        request_url_model = 'https://coding.imooc.com/class/evaluation/%s.html?page=%d'
        res_list = list()
        page_num = 1

        while True:
            request_url = request_url_model % (class_id, page_num)
            result_list = self.formated_evaluation_content_fee(request_url)

            # 如果不是最后一页就继续翻页，并且将已经得到的字符串加到列表中
            if result_list:
                page_num += 1
                res_list.extend(result_list)
            else:
                break

        return '\t'.join(res_list)

    def formated_evaluation_content_fee(self, url):
        """
        格式化评价内容，针对实战课程
        :return:
        """
        res = requests.get(url)
        resulst_list = list()
        selector = Selector(text=res.content)
        content_list = selector.css('.cmt-txt::text').extract()

        # 如果有这个列表代表有数据，如果没有该数据直接返回空
        if content_list:
            score_node_list = selector.css('.stars')

            # 根据星星的数量判断评价
            for i in range(len(content_list)):
                score = len(score_node_list[i].css('.on').extract())
                resulst_list.append(json.dumps({content_list[i].replace('"', ''): score * 20},
                                               ensure_ascii=False))

            return resulst_list
        else:
            return None

    def get_evaluation_and_content(self, class_id):
        """
        获取免费课程的评价分数与主体内容
        :return:
        """
        request_url_model = 'https://www.imooc.com/course/coursescore/id/%s?page=%d'
        res_list = list()
        page_num = 1
        while True:
            request_url = request_url_model % (class_id, page_num)
            result_list = self.formated_evaluation_content(request_url)
            # 如果不是最后一页就继续翻页，并且将已经得到的字符串加到列表中
            if result_list:
                page_num += 1
                res_list.extend(result_list)
            else:
                break

        return '\t'.join(res_list)

    def formated_evaluation_content(self, url):
        """
        格式化评价内容，针对免费课程
        :return:返回一个字符串，该字符串由字典转化过来，key为评论，value为该条评论对应的分数
        """
        res = requests.get(url)
        result_list = list()
        selector = Selector(text=res.text)
        no_data_tag = selector.css('.no-data')

        # 如果有这个标记代表已经最后一页了，直接返回
        if no_data_tag:
            return None
        else:
            evaluation_node_list = selector.css('.evaluation')

            # 构造相应的评价字典
            for i in range(len(evaluation_node_list)):
                content = evaluation_node_list[i].css('.content::text').extract_first()
                if not content:
                    content = ''
                score = evaluation_node_list[i].css('.star-box span::text').extract_first().replace('分', '')
                result_list.append(json.dumps({content.replace('"', ''): int(score)}, ensure_ascii=False))

            return result_list
