# -*- coding: utf-8 -*-
import redis
import re
import time
import scrapy
import datetime

from urllib import parse
from scrapy.http import Request
from w3lib.html import remove_tags
from urllib.request import unquote
from scrapy_redis.spiders import RedisSpider
from selenium import webdriver
#scarpy信号相关的包
# from scrapy.xlib.pydispatch import dispatcher
# from scrapy import signals


from ArticleSpider.items import TechnicalArticleItem
from ArticleSpider.utils.common import get_md5
from ArticleSpider import settings


class JobboleSpider(RedisSpider):
    name = 'jobbole'
    allowed_domains = ['jobbole.com']
    # 不同域名的地址只需要改配置即可，目前有三类
    # start_urls = settings.JOBBOLE_LIST_ONE[0]
    reg_exp = settings.JOBBOLE_LIST_ONE[1]
    redis_key = 'jobbole:start_urls'

    def __init__(self):
        """
        初始化start_urls到redis
        """
        redis_cli = redis.Redis(host=settings.REDIS_ADDRESS, port=6379)
        urls = settings.JOBBOLE_LIST_ONE[0]
        for url in urls:
            # master端需要将这个打开
            # redis_cli.lpush(self.redis_key, url)
            pass

    # def __init__(self):
    #     self.browser = webdriver.Chrome('/Users/hanyuzhou/Downloads/chromedriver')
    #     super(JobboleSpider, self).__init__()
    #     #通过信号量判断，如果spider关掉了，那么就调用spider_close这个函数去关闭chromedriver
    #     dispatcher.connect(self.spider_close, signals.spider_closed)

    # def spider_close(self, spider):
    #     """
    #     当爬虫退出的时候关闭chromedriver
    #     :param spider:
    #     :return:
    #     """
    #     print('spider closed')
    #     spider.browser.quit()

    def parse(self, response):
        """
        提取每一页的url并交给解析函数进一步解析
        :param response:
        :return:
        """
        article_type = unquote(re.findall(self.reg_exp, response.url)[0], encoding='utf-8')
        crawl_urls = response.css('.post.floated-thumb .post-thumb a::attr(href)').extract()
        crawl_abstracts = response.css('.excerpt p::text').extract()
        time.sleep(2)
        for crawl_url in crawl_urls:
            yield Request(url=parse.urljoin(response.url, crawl_url), callback=self.parse_detail,
                          meta={'index': crawl_urls.index(crawl_url), 'crawl_abstracts': crawl_abstracts,
                                'article_type': article_type}, dont_filter=True)

        next_url = response.css('.next::attr(href)').extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        """
        解析具体网页
        :param response:
        :return:
        """
        jobbole_article_item = TechnicalArticleItem()
        index = response.meta['index']
        abstract = response.meta['crawl_abstracts'][index]
        title = response.css('.entry-header h1::text').extract_first()
        # temp_node用来提取tags和publish_time两个字段
        temp_node = response.css('.entry-meta-hide-on-mobile')
        publish_time = temp_node.css('::text').extract_first().split('|')[0].replace('·', '').strip()
        temp_tags = temp_node.css('p a::text').extract()
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

        collection_num = response.css('.bookmark-btn::text').extract_first().replace('收藏', '').strip()
        comment_num = response.css('.btn-bluet-bigger.hide-on-480::text').extract_first().replace('评论', '').strip()
        praise_num = response.css('.vote-post-up h10::text').extract_first()
        if praise_num:
            praise_num = praise_num.replace('赞', '').strip()
        else:
            praise_num = ''
        collection_num = 0 if (collection_num == '') else int(collection_num)
        comment_num = 0 if (comment_num == '') else int(comment_num)
        praise_num = 0 if (praise_num == '') else int(praise_num)

        jobbole_article_item['url_object_id'] = get_md5(url)
        jobbole_article_item['url'] = url
        jobbole_article_item['title'] = title
        jobbole_article_item['article_type'] = response.meta['article_type']
        jobbole_article_item['data_source'] = '伯乐在线'
        jobbole_article_item['read_num'] = 0
        jobbole_article_item['comment_num'] = comment_num
        jobbole_article_item['praise_num'] = praise_num
        jobbole_article_item['collection_num'] = collection_num
        jobbole_article_item['publish_time'] = publish_time
        jobbole_article_item['abstract'] = abstract
        jobbole_article_item['tags'] = tags

        yield jobbole_article_item
