# -*- coding: utf-8 -*-
import scrapy
import re
import datetime

from scrapy.http import Request
from w3lib.html import remove_tags

from ArticleSpider.items import TechnicalArticleItem
from ArticleSpider.utils.common import get_md5

class LinuxCnSpider(scrapy.Spider):
    """
    linux中国的爬虫
    """
    name = 'linux_cn'
    allowed_domains = ['linux.cn/']
    start_urls = ['https://linux.cn/tech/']

    def parse(self, response):
        """
        解析具体网页
        :param response:
        :return:
        """
        # 这个地方需要看网页的源代码，不能看f12给出的DOM树
        crawl_urls = response.css('.article-list .title a::attr(href)').extract()
        # 对摘要信息进行处理
        abstract_list = list()
        temp_abstract_list = response.css('.article-list p::text').extract()
        for i in range(0, 30, 3):
            abstract_list.append(temp_abstract_list[i])

        for crawl_url in crawl_urls:
            yield Request(url=crawl_url, callback=self.parse_detail, dont_filter=True,
                          meta={'abstract_list': abstract_list, 'index':crawl_urls.index(crawl_url)})

        # 爬取下一页的地址
        next_url = response.css('.nxt::attr(href)').extract_first()
        if next_url:
            yield Request(url=next_url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        """
        解析网页细节
        :param response:
        :return:
        """
        linux_cn_article_item = TechnicalArticleItem()
        index = response.meta['index']
        abstract = response.meta['abstract_list'][index]
        title = response.css('#article_title::text').extract_first()
        publish_time = response.css('#article_date::text').extract_first()
        publish_time = re.findall(r'.*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}).*', publish_time)[0].strip()

        try:
            publish_time = datetime.datetime.strptime(publish_time, '%Y-%m-%d %H:%M').date()
        except Exception as e:
            publish_time = datetime.datetime.now().date()

        url = response.url

        content = response.css('.d #article_content').extract_first()
        # 第一个参数表示被替换的，第二个参数表示用什么替换，第三个是打算替换的字符串
        content = re.sub(r'[\t\r\n\s]', '', remove_tags(content))
        content = re.sub(r"""[;"']""", '', content)

        collection_num = response.css('#_favtimes::text').extract_first()
        praise_num = response.css('#_sharetimes::text').extract_first()
        comment_num = response.css('#_commentnum::text').extract_first()
        collection_num = 0 if (not collection_num) else int(collection_num)
        comment_num = 0 if (not comment_num) else int(comment_num)
        praise_num = 0 if (not praise_num) else int(praise_num)

        linux_cn_article_item['url_object_id'] = get_md5(url)
        linux_cn_article_item['url'] = url
        linux_cn_article_item['title'] = title
        linux_cn_article_item['article_type'] = 'linux'
        linux_cn_article_item['data_source'] = 'linux_cn'
        linux_cn_article_item['read_num'] = -1
        linux_cn_article_item['comment_num'] = comment_num
        linux_cn_article_item['praise_num'] = praise_num
        linux_cn_article_item['collection_num'] = collection_num
        linux_cn_article_item['publish_time'] = publish_time
        linux_cn_article_item['abstract'] = abstract
        linux_cn_article_item['content'] = content
        linux_cn_article_item['tags'] = ''

        yield linux_cn_article_item
