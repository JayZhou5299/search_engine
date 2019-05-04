# -*- coding: utf-8 -*-
import scrapy
import time
import redis
import re
import datetime

from w3lib.html import remove_tags
from scrapy.http import Request
from urllib import parse
from scrapy_redis.spiders import RedisSpider

from ArticleSpider import settings
from ArticleSpider.utils.common import get_md5
from ArticleSpider.items import TechnicalArticleItem


class ImportnewSpider(RedisSpider):
    name = 'importnew'
    allowed_domains = ['importnew.com']
    # start_urls = ['http://www.importnew.com/all-posts/']
    redis_key = 'importnew:start_urls'

    def __init__(self):
        """
        初始化start_urls到redis
        """
        redis_cli = redis.Redis(host=settings.REDIS_ADDRESS, port=6379)
        # master端需要将这个打开
        # redis_cli.lpush(self.redis_key, 'http://www.importnew.com/all-posts/')

    def parse(self, response):
        """
        提取每一页的url并交给解析函数进一步解析
        :param response:
        :return:
        """
        crawl_urls = response.css('.post.floated-thumb .post-thumb a::attr(href)').extract()
        crawl_abstracts = response.css('.excerpt p::text').extract()
        # 做一遍过滤，将'每周10道 '的过滤掉
        for crawl_abstract in crawl_abstracts:
            if crawl_abstract == '每周10道 ':
                crawl_abstracts.remove('每周10道 ')
        time.sleep(5)
        for crawl_url in crawl_urls:
            time.sleep(1)
            yield Request(url=parse.urljoin(response.url, crawl_url), callback=self.parse_detail,
                          meta={'index': crawl_urls.index(crawl_url), 'crawl_abstracts': crawl_abstracts}, dont_filter=True)

        next_url = response.css('.next::attr(href)').extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        """
        解析具体网页
        :param response:
        :return:
        """
        importnew_article_item = TechnicalArticleItem()
        index = response.meta['index']
        abstract = response.meta['crawl_abstracts'][index]
        title = response.css('.entry-header h1::text').extract_first()
        # 临时dom树节点信息，需要提取publish_time和tags两个字段
        temp_node = response.css('.entry-meta-hide-on-mobile')
        publish_time = temp_node.css('::text').extract_first().strip()
        publish_time = re.findall(r'(\d*/\d*/\d*)', publish_time)[0]
        temp_tags = temp_node.css('a::text').extract()
        # 需要对tags进行处理，因为里面包含评论的信息，将其过滤掉后再拼接
        tags = ''
        if temp_tags and len(temp_tags) > 0:
            for temp_tags_obj in temp_tags:
                if '评论' not in temp_tags_obj:
                    tags = tags + temp_tags_obj + ','
            tags = tags[0: -1]
        try:
            publish_time = datetime.datetime.strptime(publish_time, '%Y/%m/%d').date()
        except Exception as e:
            publish_time = datetime.datetime.now().date()

        url = response.url

        # 第一个参数表示被替换的，第二个参数表示用什么替换，第三个是打算替换的字符串
        # content = re.sub(r'<div class="copyright-area">.*</div>', '', response.css('.entry').extract_first())
        # content = re.sub(r'[\t\r\n\s]', '', remove_tags(content))
        # content = re.sub(r"""[;"']""", '', content)

        # 全部拼接成字符串，然后用正则提取出评论数
        comment_num = ''.join(temp_node.css(' a::text').extract())
        comment_num = re.findall(r'(\d)*( )*条评论', comment_num)[0][0]
        comment_num = 0 if (comment_num == '') else int(comment_num)

        importnew_article_item['url_object_id'] = get_md5(url)
        importnew_article_item['url'] = url
        importnew_article_item['title'] = title
        importnew_article_item['article_type'] = 'java'
        importnew_article_item['data_source'] = 'importnew'
        importnew_article_item['read_num'] = 0
        importnew_article_item['comment_num'] = comment_num
        importnew_article_item['praise_num'] = 0
        importnew_article_item['collection_num'] = 0
        importnew_article_item['publish_time'] = publish_time
        importnew_article_item['abstract'] = abstract
        importnew_article_item['tags'] = tags
        # pass
        yield importnew_article_item

