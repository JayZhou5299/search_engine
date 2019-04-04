# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class TechnicalArticleItem(scrapy.Item):
    url_object_id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    article_type = scrapy.Field()
    data_source = scrapy.Field()
    read_num = scrapy.Field()
    comment_num = scrapy.Field()
    praise_num = scrapy.Field()
    collection_num = scrapy.Field()
    publish_time = scrapy.Field()
    abstract = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field()

