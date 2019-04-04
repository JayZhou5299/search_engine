# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VideospiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class VideoItem(scrapy.Item):
    url_object_id = scrapy.Field()
    url = scrapy.Field()
    class_name = scrapy.Field()
    price = scrapy.Field()
    learner_nums = scrapy.Field()
    class_nums = scrapy.Field()
    # 目录存储以\t分隔
    category = scrapy.Field()
    abstract = scrapy.Field()
    data_source = scrapy.Field()
    institution = scrapy.Field()
    second_classify = scrapy.Field()
    evaluation_score = scrapy.Field()
    evaluation_person = scrapy.Field()
    fit_people = scrapy.Field()
    first_classify = scrapy.Field()
    evaluation_content = scrapy.Field()