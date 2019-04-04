# -*- coding: utf-8 -*-
import scrapy
import time
import requests

from selenium import webdriver

class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['cnblogs.com']
    start_urls = []

    def __init__(self):
        """
        init构造start_urls
        """
        real_content = self.get_real_content()
        # res = requests.post(url='https://www.cnblogs.com/')
        print(real_content)

    def get_real_content(self):
        """
        获取博客园cookie信息
        :return:
        """
        url = 'https://www.cnblogs.com/'
        browser = webdriver.Chrome('/Users/hanyuzhou/Downloads/chromedriver')
        browser.get(url)
        # 等待browser运行js，
        time.sleep(30)
        real_content = browser.page_source
        cate_node = browser.find_elements_by_css_selector('.cate_content_block li')
        # 等待1s后退出chromedriver
        time.sleep(1)
        browser.quit()
        return real_content


    def parse(self, response):
        """
        提取每一页的url并交给解析函数进一步解析
        :param response:
        :return:
        """
        response.css('.cate_content_block')
        pass

    def parse_detail(self, response):
        """
        解析具体网页
        :param response:
        :return:
        """
        pass