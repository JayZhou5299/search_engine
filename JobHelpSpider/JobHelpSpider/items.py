# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobhelpspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobWantedInformation(scrapy.Item):
    url_object_id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    publish_time = scrapy.Field()
    content = scrapy.Field()
    data_source = scrapy.Field()
    abstract = scrapy.Field()
