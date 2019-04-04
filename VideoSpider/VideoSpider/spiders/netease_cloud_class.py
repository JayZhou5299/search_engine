# -*- coding: utf-8 -*-
import scrapy
import json

from scrapy import Request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector


from VideoSpider import settings


class NeteaseCloudClassSpider(scrapy.Spider):
    """
    网易云课堂爬虫
    """
    name = 'netease_cloud_class'
    allowed_domains = ['study.163.com']
    start_urls = ['https://study.163.com/']

    def __init__(self):
        pass

    def start_requests(self):
        """
        修改逻辑让其成为post请求并携带相关参数
        :return:
        """
        data = {
         'activityId': 0,
         'frontCategoryId': '',
         'keyword': '',
         'orderType': 50,
         'pageIndex': 1,
         'pageSize': 50,
         'priceType': -1,
         'relativeOffset': 0,
         'searchTimeType': -1,
         'activityId': 0,
         }
        headers = {
            "Accept": "application/json",
            "Host": "study.163.com",
            "Origin": "https://study.163.com",
            "Content-Type": "application/json",
            # "Referer": "https://study.163.com/category/480000003129019",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
        }
        headers = {
            'Host': 'study.163.com',
        }
        start_urls_dict = settings.NETEASE_CLOUD_CLASS
        for category in start_urls_dict.keys():
            data['frontCategoryId'] = category
            request = Request(self.start_urls[0], dont_filter=True, method='POST', body=json.dumps(data), headers=headers)
            yield request

    def parse(self, response):
        """
        通过chrome自动化加载js执行完后的网页
        :param response:
        :return:
        """
        category_list = settings.NETEASE_CLOUD_CLASS
        browser = webdriver.Chrome('/Users/hanyuzhou/Downloads/chromedriver')

        # 获取抓取目录列表
        for category_obj in category_list:
            browser.get('%s%s' % ('https://study.163.com/category/', category_obj))
            selector = Selector(text=browser.page_source)
            class_node_list = selector.css('.mc-search-coures-pool  .uc-course-list_itm')

            # 获取课程的item对象
            for class_node_obj in class_node_list:
                relevate_url = class_node_obj.css('.j-href::attr(href)').extract_first()
                yield Request(url='https:%s' % relevate_url, callback=self.parse_detail)

            next_url = selector.css('.ux-pager_btn__next .th-bk-main-gh')

        browser.quit()

    def parse_crawl_urls(self, response):
        """
        解析待爬取url的列表
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
        pass
