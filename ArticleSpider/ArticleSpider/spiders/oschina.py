# -*- coding: utf-8 -*-
import re
import time
import scrapy
import requests
import datetime

from urllib import parse
from scrapy.http import Request
from w3lib.html import remove_tags
from urllib.request import unquote
from selenium import webdriver


from ArticleSpider.items import TechnicalArticleItem
from ArticleSpider.utils.common import get_md5
from ArticleSpider import settings


class OschinaSpider(scrapy.Spider):
    """
    开源中国爬虫
    """
    name = 'oschina'
    allowed_domains = ['www.oschina.net']
    start_urls = []

    def __init__(self):
        """
        构造函数
        """
        # 用来存储classification与类别的对应关系
        self.classify_map = dict()
        headers = {
            "Host": 'www.oschina.net',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
        }
        response = requests.get(url='https://www.oschina.net/blog', headers=headers)
        classify_list = re.findall(r'https://www.oschina.net/blog\?classification=(\d*)"><span>·</span> (.*)</a>.*', response.text)
        for classify_obj in classify_list:
            self.start_urls.append('https://www.oschina.net/blog/widgets/_blog_index_recommend_list?'
                                   'classification={0}&p=1&type=ajax'.format(classify_obj[0]))
            self.classify_map[classify_obj[0]] = classify_obj[1]
        # print(classify_map)

    def parse(self, response):
        """
        开始解析网页
        :param response:
        :return:
        """
        crawl_urls = re.findall(r'class="header" href="(.*)" target.*', response.text)
        classify_id = re.findall(r'.*classification=(\d*)&.*', response.url)[0]
        article_type = self.classify_map[classify_id]
        abstract_list = response.css('.description p::text').extract()
        time.sleep(3)
        for crawl_url in crawl_urls:
            yield Request(url=crawl_url, callback=self.parse_detail,
                          meta={'article_type': article_type, 'crawl_abstracts': abstract_list, 'index': crawl_urls.index(crawl_url)},
                          dont_filter=True)
        # print(response.text)
        if '暂无文章' in response.text:
            print('终于结束了')

        if '暂无文章' not in response.text:
            next_page_num = int(re.findall(r'.*p=(\d*)&.*', response.url)[0]) + 1
            # print (page_num)
            next_url = re.sub(r'p=(\d*)&', 'p={0}&'.format(next_page_num), response.url)
            print(next_url)
            yield Request(url=next_url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        """
        解析网页细节
        :param response:
        :return:
        """
        oschina_article_item = TechnicalArticleItem()
        title = response.css('.article-detail .header::text').extract_first().strip()
        index = response.meta['index']
        abstract = response.meta['crawl_abstracts'][index]
        publish_time = response.css('.extra.horizontal .item::text').extract()[1].replace('发布于', '').strip()

        # 由于该网站时间数据的格式不同，所以需要分别处理
        try:
            if len(re.findall(r'\d{4}/\d{2}/\d{2}', publish_time)) > 0:
                publish_time = datetime.datetime.strptime(re.findall(r'\d{4}/\d{2}/\d{2}', publish_time)[0], '%Y/%m/%d').date()
            elif len(re.findall(r'\d{2}/\d{2}', publish_time)) > 0:
                publish_time = datetime.datetime.strptime('2019/' + re.findall(r'\d{2}/\d{2}', publish_time)[0], '%Y/%m/%d').date()
            elif '前天' in publish_time:
                publish_time = datetime.date.today() - datetime.timedelta(days=2)
            elif '昨天' in publish_time:
                publish_time = datetime.date.today() - datetime.timedelta(days=1)
            elif '今天' in publish_time:
                publish_time = datetime.datetime.now().date()
        except Exception as e:
            publish_time = datetime.datetime.now().date()

        tags = response.css('.tags a::text').extract()
        url = response.url
        content = response.css('#articleContent').extract_first()

        # 第一个参数表示被替换的，第二个参数表示用什么替换，第三个是打算替换的字符串
        content = re.sub(r'[\t\r\n\s]', '', remove_tags(content))
        content = re.sub(r"""[;"']""", '', content)
        read_num = response.css('.extra.horizontal .item::text').extract()[3].replace('阅读','').strip()
        collection_num = response.css('.extra .collect-btn span::text').extract_first()
        comment_num = response.css('.extra.horizontal .normal span::text').extract()[1]
        praise_num = response.css('.normal.article-like span::text').extract_first()

        if praise_num:
            praise_num = praise_num.replace('赞', '').strip()
        else:
            praise_num = ''
        collection_num = 0 if (collection_num == '') else int(collection_num)
        comment_num = 0 if (comment_num == '') else int(comment_num)
        praise_num = 0 if (praise_num == '') else int(praise_num)
        read_num = 0 if (read_num == '') else int(read_num)

        oschina_article_item['url_object_id'] = get_md5(url)
        oschina_article_item['url'] = url
        oschina_article_item['title'] = title
        oschina_article_item['article_type'] = response.meta['article_type']
        oschina_article_item['data_source'] = '开源中国'
        oschina_article_item['read_num'] = read_num
        oschina_article_item['comment_num'] = comment_num
        oschina_article_item['praise_num'] = praise_num
        oschina_article_item['collection_num'] = collection_num
        oschina_article_item['publish_time'] = publish_time
        oschina_article_item['abstract'] = abstract
        oschina_article_item['content'] = content
        oschina_article_item['tags'] = ','.join(tags)

        yield oschina_article_item
