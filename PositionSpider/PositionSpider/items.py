# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PositionspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class PositionItem(scrapy.Item):
    url_object_id = scrapy.Field()
    url = scrapy.Field()
    position_name = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    welfare = scrapy.Field()
    working_place = scrapy.Field()
    working_exp = scrapy.Field()
    education = scrapy.Field()
    working_type = scrapy.Field()
    position_num = scrapy.Field()
    responsibility = scrapy.Field()
    data_source = scrapy.Field()
    publish_time = scrapy.Field()
    other_message = scrapy.Field()