# -*- coding: utf-8 -*-
import scrapy
import datetime
import requests
import re

from scrapy.selector import Selector
from scrapy import Request
from urllib import parse
from w3lib.html import remove_tags

from ArticleSpider.items import TechnicalArticleItem
from ArticleSpider.utils.common import get_md5


class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['www.cnblogs.com']
    start_urls = ['https://www.cnblogs.com/']

    def parse(self, response):
        """
        获取文章分类
        :param response:
        :return:
        """
        # 获取文章分类html列表
        res = requests.post(url='https://www.cnblogs.com/aggsite/SubCategories',
                            data={"cateIds": "108698,2,108701,108703,108704,108705,108709,108712,108724,4"})
        selector = Selector(text=res.text)
        article_type_node_list = selector.css('.cate_content_block a')

        # 解析分类起始url和分类名称
        for article_type_node_obj in article_type_node_list:
            article_type = article_type_node_obj.css('::text').extract_first()
            article_type = re.findall(r'(.*)\(', article_type)[0]
            relative_url = article_type_node_obj.css('::attr(href)').extract_first()
            yield Request(url=parse.urljoin('https://www.cnblogs.com/', relative_url),
                          meta={'article_type': article_type},
                          callback=self.parse_crawl_urls)

    def parse_crawl_urls(self, response):
        """
        获取待爬取的url
        :param response:
        :return:
        """
        article_type = response.meta['article_type']
        crawl_urls = response.css('h3 a::attr(href)').extract()
        for crawl_url in crawl_urls:
            yield Request(url=crawl_url, callback=self.parse_detail,
                          meta={'article_type': article_type})
        next_node = response.css('.pager a')
        if next_node:
            next_node = next_node[-1]
            next_tag = next_node.css('::text').extract_first()
            if 'Next' in next_tag:
                next_url = next_node.css('::attr(href)').extract_first()
                yield Request(url=parse.urljoin('https://www.cnblogs.com/', next_url),
                              callback=self.parse_crawl_urls)

    def parse_detail(self, response):
        """
        解析具体网页
        :param response:
        :return:
        """
        url = response.url
        cnblogs_item = TechnicalArticleItem()
        title = response.css('#cb_post_title_url::text').extract_first()
        read_num = response.css('#post_view_count::text').extract_first()
        if not read_num:
            read_num = 0
        comment_num = response.css('#post_comment_count::text').extract_first()
        if not comment_num:
            comment_num = 0

        publish_time = response.css('#post-date::text').extract_first()
        if publish_time:
            publish_time = datetime.datetime.strptime(publish_time, '%Y-%m-%d %H:%M')

        abstract = response.css('#cnblogs_post_body').extract_first()
        if abstract:
            abstract = remove_tags(abstract)[:300]

        cnblogs_item['url_object_id'] = get_md5(url)
        cnblogs_item['url'] = url
        cnblogs_item['title'] = title
        cnblogs_item['article_type'] = response.meta['article_type']
        cnblogs_item['data_source'] = '博客园'
        cnblogs_item['read_num'] = int(read_num)
        cnblogs_item['comment_num'] = int(comment_num)
        cnblogs_item['praise_num'] = -1
        cnblogs_item['collection_num'] = -1

        cnblogs_item['publish_time'] = publish_time
        cnblogs_item['abstract'] = abstract
        cnblogs_item['tags'] = ''

        yield cnblogs_item

    def get_read_num(self):
        """
        获取阅读数量
        :return:
        """
        pass

    def get_comment_num(self):
        """
        获取评论数量
        :return:
        """
        pass

